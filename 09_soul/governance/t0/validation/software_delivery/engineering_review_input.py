"""Build Engineering Reviewer input for a plan or one exact Git commit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Mapping, Sequence

from jsonschema import Draft202012Validator, SchemaError, ValidationError

from .engineering_review_output import (
    engineering_check_ids, validate_engineering_review_output, validate_engineering_reviewer_identity,
)


ENGINEERING_REVIEW_SUBJECT_INVALID = "ENGINEERING_REVIEW_SUBJECT_INVALID"
ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE = (
    "ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE"
)
INPUT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[5]
    / "09_soul/governance/skills/engineering-change-review/runtime_modules"
    / "engineering_change_reviewer/schemas/input.schema.json"
)


class EngineeringReviewInputError(ValueError):
    """One deterministic Engineering Review input failure."""

    def __init__(self, error_code: str, detail: str) -> None:
        self.error_code = error_code
        super().__init__(f"{error_code}: {detail}")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _run_git(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ("git", *args),
            cwd=root,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = (
            exc.stderr.decode("utf-8", errors="replace").strip()
            if isinstance(exc, subprocess.CalledProcessError)
            else str(exc)
        )
        raise EngineeringReviewInputError(
            ENGINEERING_REVIEW_SUBJECT_INVALID,
            detail or f"git {' '.join(args)} failed",
        ) from exc
    return result.stdout


def _full_commit_oid(root: Path, commit_ref: str) -> str:
    if not isinstance(commit_ref, str) or not commit_ref.strip():
        raise EngineeringReviewInputError(
            ENGINEERING_REVIEW_SUBJECT_INVALID,
            "commit_ref must be non-empty",
        )
    oid = _run_git(root, "rev-parse", "--verify", f"{commit_ref}^{{commit}}").decode(
        "ascii"
    ).strip()
    if len(oid) not in {40, 64} or any(char not in "0123456789abcdef" for char in oid):
        raise EngineeringReviewInputError(
            ENGINEERING_REVIEW_SUBJECT_INVALID,
            "resolved commit object ID is invalid",
        )
    return oid


def _single_parent(root: Path, commit_oid: str) -> str:
    row = _run_git(root, "rev-list", "--parents", "-n", "1", commit_oid).decode(
        "ascii"
    ).strip().split()
    if len(row) != 2:
        raise EngineeringReviewInputError(
            ENGINEERING_REVIEW_SUBJECT_INVALID,
            "Engineering Review requires one commit with exactly one parent",
        )
    return row[1]


def _changed_path_rows(root: Path, parent_oid: str, commit_oid: str) -> list[dict[str, str]]:
    raw = _run_git(
        root,
        "diff",
        "--name-status",
        "--no-renames",
        "-z",
        parent_oid,
        commit_oid,
        "--",
    )
    fields = raw.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    if len(fields) % 2:
        raise EngineeringReviewInputError(
            ENGINEERING_REVIEW_SUBJECT_INVALID,
            "Git name-status output is incomplete",
        )
    state_by_status = {b"A": "added", b"M": "modified", b"D": "deleted"}
    rows: list[dict[str, str]] = []
    for index in range(0, len(fields), 2):
        status = fields[index]
        path_bytes = fields[index + 1]
        state = state_by_status.get(status)
        if state is None:
            raise EngineeringReviewInputError(
                ENGINEERING_REVIEW_SUBJECT_INVALID,
                f"unsupported Git path state: {status!r}",
            )
        try:
            path = path_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise EngineeringReviewInputError(
                ENGINEERING_REVIEW_SUBJECT_INVALID,
                "changed path is not UTF-8",
            ) from exc
        source_oid = parent_oid if state == "deleted" else commit_oid
        content = _run_git(root, "show", f"{source_oid}:{path}")
        rows.append(
            {
                "path": path,
                "state": state,
                "content_sha256": _sha256_bytes(content),
            }
        )
    if not rows:
        raise EngineeringReviewInputError(
            ENGINEERING_REVIEW_SUBJECT_INVALID,
            "exact commit has no changed path relative to its parent",
        )
    return sorted(rows, key=lambda row: row["path"].encode("utf-8"))


def _require_hashed_body(value: Mapping[str, object], name: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != {"ref", "sha256", "body"}:
        raise EngineeringReviewInputError(
            ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE,
            f"{name} must contain ref, sha256 and body",
        )
    ref, declared_sha256, body = value["ref"], value["sha256"], value["body"]
    if not all(isinstance(item, str) and item.strip() for item in (ref, declared_sha256, body)):
        raise EngineeringReviewInputError(
            ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE,
            f"{name} fields must be non-empty strings",
        )
    actual_sha256 = _sha256_bytes(body.encode("utf-8"))
    if declared_sha256 != actual_sha256:
        raise EngineeringReviewInputError(
            ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE,
            f"{name} body hash mismatch",
        )
    return {"ref": ref, "sha256": declared_sha256, "body": body}


def hashed_body(ref: str, body: str) -> dict[str, str]:
    """Bind an explicit material reference to its exact UTF-8 body bytes."""
    return _require_hashed_body(
        {"ref": ref, "sha256": _sha256_bytes(body.encode("utf-8")), "body": body}, "material"
    )


def command_plan(ref: str, commands: Sequence[Mapping[str, object]]) -> dict[str, object]:
    """Hash the commands value as sorted-key, compact, UTF-8 JSON."""
    rows = [dict(row) for row in commands]
    encoded = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return {"ref": ref, "sha256": _sha256_bytes(encoded), "commands": rows}


def _validate_plan_review(evidence, basis, criteria, schema_path):
    wrapped = _require_hashed_body(evidence, "code_design_review")
    try:
        record = json.loads(wrapped["body"])
        validate_engineering_reviewer_identity(record)
        source = record["semantic_input"]
        if (record["status"] != "completed"
                or record["module_id"] != "engineering_change_reviewer"
                or record["review_purpose"] != "code_design"
                or record["semantic_validation"]["status"] != "passed"
                or source["review_purpose"] != "code_design"
                or source["module_id"] != "engineering_change_reviewer"
                or source["subject"] is not None):
            raise ValueError("record is not a completed independent engineering plan review")
        previous = _require_hashed_body(source["code_design_basis"], "reviewed code_design_basis")
        # A material locator may move; matching content still does not grant implementation authority.
        if previous["sha256"] != basis["sha256"] or previous["body"] != basis["body"]:
            raise ValueError("reviewed plan content differs from the implementation basis")
        if source["acceptance_criteria"] != criteria:
            raise ValueError("implementation acceptance criteria differ from the reviewed plan")
        if source.get("schema_version") != "engineering_change_reviewer_input_v6":
            raise ValueError("Historical plan evidence is retained but needs a new-format review before reuse")
        commands = source["sandbox_command_plan"]
        checked = build_code_design_review_input(
            code_design_basis=source["code_design_basis"], sandbox_command_plan=commands,
            acceptance_criteria=source["acceptance_criteria"],
            system_change_plan_step=source.get("system_change_plan_step"),
            context_documents=source.get("context_documents", ()),
            prior_findings=source.get("prior_findings", ()), schema_path=schema_path,
        )
        if checked != source:
            raise ValueError("reviewed plan input contradicts its declared protocol")
        if source.get("code_design_review") is not None:
            raise ValueError("plan review cannot consume its own future review result")
        validate_engineering_review_output(record["output"], review_input=source, execution_record=record)
        if record["output"]["verdict"] != "passed":
            raise ValueError("engineering plan review has not passed")
    except (KeyError, TypeError, ValueError) as exc:
        raise EngineeringReviewInputError(ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE,
                                          f"invalid code_design_review: {exc}") from exc
    return wrapped


def _finish_input(*, purpose, subject, code_design_basis, sandbox_command_plan, acceptance_criteria,
                  system_change_plan_step, code_design_review, context_documents, prior_findings, schema_path):
    basis = _require_hashed_body(code_design_basis, "code_design_basis")
    if not isinstance(sandbox_command_plan, Mapping) or isinstance(acceptance_criteria, (str, bytes)):
        raise EngineeringReviewInputError(ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE,
                                          "commands must be an object and acceptance criteria a list")
    criteria = list(acceptance_criteria)
    payload = {
        "schema_version": "engineering_change_reviewer_input_v6",
        "required_check_ids": list(engineering_check_ids()),
        "module_id": "engineering_change_reviewer", "review_purpose": purpose,
        "system_change_plan_step": None if system_change_plan_step is None else _require_hashed_body(
            system_change_plan_step, "system_change_plan_step"),
        "subject": subject, "code_design_basis": basis,
        "code_design_review": None if purpose == "code_design" else _validate_plan_review(
            code_design_review, basis, criteria, schema_path),
        "context_documents": [_require_hashed_body(row, "context document") for row in context_documents],
        "sandbox_command_plan": dict(sandbox_command_plan),
        "acceptance_criteria": criteria, "prior_findings": [dict(row) for row in prior_findings],
    }
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
        commands = payload["sandbox_command_plan"]
        expected = command_plan(commands["ref"], commands["commands"])
        if commands != expected:
            raise ValueError("sandbox_command_plan content hash mismatch")
        ids = [row["command_id"] for row in commands["commands"]]
        if len(ids) != len(set(ids)):
            raise ValueError("sandbox_command_plan command_id values must be unique")
        refs = [row["ref"] for row in payload["context_documents"]]
        if len(refs) != len(set(refs)):
            raise ValueError("context document references must be unique")
    except (OSError, UnicodeError, ValueError, ValidationError, SchemaError) as exc:
        raise EngineeringReviewInputError(ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE, str(exc)) from exc
    return payload


def build_code_design_review_input(*, code_design_basis, sandbox_command_plan, acceptance_criteria,
                                  system_change_plan_step=None, context_documents=(), prior_findings=(),
                                  schema_path=INPUT_SCHEMA_PATH):
    """Review a complete engineering plan without fabricating a future commit."""
    return _finish_input(purpose="code_design", subject=None, code_design_basis=code_design_basis,
        sandbox_command_plan=sandbox_command_plan, acceptance_criteria=acceptance_criteria,
        system_change_plan_step=system_change_plan_step, code_design_review=None,
        context_documents=context_documents, prior_findings=prior_findings, schema_path=schema_path)


def build_engineering_review_input(
    *,
    repository_root: Path,
    commit_ref: str,
    system_change_plan_step: Mapping[str, object] | None = None,
    code_design_basis: Mapping[str, object],
    sandbox_command_plan: Mapping[str, object],
    acceptance_criteria: Sequence[str],
    code_design_review: Mapping[str, object] | None = None,
    context_documents: Sequence[Mapping[str, object]] = (),
    prior_findings: Sequence[Mapping[str, object]] = (),
    schema_path: Path = INPUT_SCHEMA_PATH,
) -> dict[str, object]:
    """Return one schema-valid successor Reviewer input object."""

    try:
        repository_root.stat()
        root = repository_root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise EngineeringReviewInputError(ENGINEERING_REVIEW_SUBJECT_INVALID, str(exc)) from exc
    commit_oid = _full_commit_oid(root, commit_ref)
    parent_oid = _single_parent(root, commit_oid)
    paths = _changed_path_rows(root, parent_oid, commit_oid)
    diff = _run_git(
        root,
        "diff",
        "--binary",
        "--no-ext-diff",
        "--no-renames",
        parent_oid,
        commit_oid,
        "--",
    )
    diff_sha256 = _sha256_bytes(diff)
    subject_identity = json.dumps(
        {
            "commit_ref": commit_oid,
            "parent_ref": parent_oid,
            "diff_sha256": diff_sha256,
            "paths": paths,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    subject = {
            "commit_ref": commit_oid,
            "parent_ref": parent_oid,
            "subject_sha256": _sha256_bytes(subject_identity),
            "diff_sha256": diff_sha256,
            "paths": paths,
    }
    return _finish_input(purpose="implementation", subject=subject, code_design_basis=code_design_basis,
        sandbox_command_plan=sandbox_command_plan, acceptance_criteria=acceptance_criteria,
        system_change_plan_step=system_change_plan_step, code_design_review=code_design_review,
        context_documents=context_documents, prior_findings=prior_findings, schema_path=schema_path)


__all__ = [
    "ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE",
    "ENGINEERING_REVIEW_SUBJECT_INVALID",
    "EngineeringReviewInputError",
    "INPUT_SCHEMA_PATH",
    "build_engineering_review_input",
]
