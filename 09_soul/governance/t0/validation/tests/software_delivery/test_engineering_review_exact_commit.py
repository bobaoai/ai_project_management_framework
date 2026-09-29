from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from software_delivery.engineering_review_input import (
    ENGINEERING_REVIEW_SUBJECT_INVALID,
    EngineeringReviewInputError,
    build_code_design_review_input,
    build_engineering_review_input,
)
from software_delivery.engineering_review_output import (
    EngineeringReviewOutputError,
    validate_engineering_review_output,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _repository(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "Test User")
    (root / "modified.txt").write_text("before\n", encoding="utf-8")
    (root / "deleted.txt").write_text("deleted\n", encoding="utf-8")
    _git(root, "add", "modified.txt", "deleted.txt")
    _git(root, "commit", "-q", "-m", "base")
    (root / "modified.txt").write_text("after\n", encoding="utf-8")
    (root / "added.txt").write_text("added\n", encoding="utf-8")
    (root / "deleted.txt").unlink()
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "candidate")
    return root, _git(root, "rev-parse", "HEAD")


def _hashed_body(ref: str, body: str) -> dict[str, str]:
    return {
        "ref": ref,
        "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "body": body,
    }


def _build(root: Path, commit_ref: str) -> dict[str, object]:
    command_plan_body = "[]"
    plan_input = build_code_design_review_input(
        code_design_basis=_hashed_body("basis", "basis body"),
        sandbox_command_plan={"ref":"commands", "sha256":hashlib.sha256(b"[]").hexdigest(), "commands":[]},
        acceptance_criteria=("exact commit closure passes",),
    )
    # A declared test double, not an independent-review claim.
    record = {"status":"completed", "module_id":"engineering_change_reviewer", "review_purpose":"code_design",
              "semantic_input":plan_input, "output":_valid_output("passed"),
              "semantic_validation":{"status":"passed"}}
    return build_engineering_review_input(
        repository_root=root,
        commit_ref=commit_ref,
        system_change_plan_step=_hashed_body("plan", "plan body"),
        code_design_basis=_hashed_body("basis", "basis body"),
        sandbox_command_plan={
            "ref": "commands",
            "sha256": hashlib.sha256(command_plan_body.encode("utf-8")).hexdigest(),
            "commands": [],
        },
        acceptance_criteria=("exact commit closure passes",),
        code_design_review=_hashed_body("plan-review", json.dumps(record)),
    )


def _valid_output(verdict: str) -> dict[str, object]:
    findings = []
    rows = [{"check_id": str(i), "disposition": "passed", "assessment": "Evidence supports the requirement",
             "finding_ids": []} for i in range(1, 10)]
    if verdict != "passed":
        findings = [{
            "finding_id": "f1", "severity": "block" if verdict == "blocked" else "fix",
            "evidence": {"source_ref": "basis", "locator": "§1", "observation": "Exact subject evidence"},
            "requirement": "Declared requirement", "impact": "The intended result is not established",
            "accountable_owner_ref": "owner", "required_change": "Restore the declared result",
        }]
        rows[0].update(disposition="finding", finding_ids=["f1"])
        rows[7].update(disposition="not_run", assessment="Await semantic closure")
    return {"verdict": verdict, "check_results": rows, "findings": findings,
            "safe_next_step": "Return to the declared owner"}


def test_builder_derives_exact_commit_paths_and_hashes(tmp_path: Path) -> None:
    root, commit_ref = _repository(tmp_path)

    payload = _build(root, commit_ref)

    subject = payload["subject"]
    assert isinstance(subject, dict)
    assert subject["commit_ref"] == commit_ref
    assert subject["parent_ref"] == _git(root, "rev-parse", "HEAD^")
    assert [(row["path"], row["state"]) for row in subject["paths"]] == [
        ("added.txt", "added"),
        ("deleted.txt", "deleted"),
        ("modified.txt", "modified"),
    ]
    assert all(len(row["content_sha256"]) == 64 for row in subject["paths"])
    assert "change_set_manifest" not in payload
    assert "subject_mode" not in subject


def test_builder_is_independent_of_dirty_worktree(tmp_path: Path) -> None:
    root, commit_ref = _repository(tmp_path)
    first = _build(root, commit_ref)
    (root / "modified.txt").write_text("dirty\n", encoding="utf-8")
    (root / "ambient.txt").write_text("ambient\n", encoding="utf-8")

    second = _build(root, commit_ref)

    assert second == first


def test_builder_rejects_root_and_empty_commits(tmp_path: Path) -> None:
    root, _commit_ref = _repository(tmp_path)
    root_commit = _git(root, "rev-list", "--max-parents=0", "HEAD")
    with pytest.raises(EngineeringReviewInputError) as root_error:
        _build(root, root_commit)
    assert root_error.value.error_code == ENGINEERING_REVIEW_SUBJECT_INVALID

    _git(root, "commit", "-q", "--allow-empty", "-m", "empty")
    with pytest.raises(EngineeringReviewInputError) as empty_error:
        _build(root, "HEAD")
    assert empty_error.value.error_code == ENGINEERING_REVIEW_SUBJECT_INVALID


def test_builder_projects_rename_as_delete_and_add(tmp_path: Path) -> None:
    root, _commit_ref = _repository(tmp_path)
    _git(root, "mv", "modified.txt", "renamed.txt")
    _git(root, "commit", "-q", "-m", "rename")

    payload = _build(root, "HEAD")

    subject = payload["subject"]
    assert isinstance(subject, dict)
    assert [(row["path"], row["state"]) for row in subject["paths"]] == [
        ("modified.txt", "deleted"),
        ("renamed.txt", "added"),
    ]


def test_builder_rejects_merge_commit(tmp_path: Path) -> None:
    root, _commit_ref = _repository(tmp_path)
    main_branch = _git(root, "branch", "--show-current")
    _git(root, "checkout", "-q", "-b", "side")
    (root / "side.txt").write_text("side\n", encoding="utf-8")
    _git(root, "add", "side.txt")
    _git(root, "commit", "-q", "-m", "side")
    _git(root, "checkout", "-q", main_branch)
    (root / "main.txt").write_text("main\n", encoding="utf-8")
    _git(root, "add", "main.txt")
    _git(root, "commit", "-q", "-m", "main")
    _git(root, "merge", "-q", "--no-ff", "side", "-m", "merge")

    with pytest.raises(EngineeringReviewInputError) as merge_error:
        _build(root, "HEAD")
    assert merge_error.value.error_code == ENGINEERING_REVIEW_SUBJECT_INVALID


@pytest.mark.parametrize("verdict", ["passed", "non_pass", "blocked"])
def test_output_validator_accepts_registered_verdicts(verdict):
    validate_engineering_review_output(_valid_output(verdict))


def test_output_validator_rejects_verdict_and_finding_conflicts():
    payload = _valid_output("non_pass")
    payload["verdict"] = "passed"
    with pytest.raises(EngineeringReviewOutputError):
        validate_engineering_review_output(payload)
    payload = _valid_output("passed")
    payload["verdict"] = "blocked"
    with pytest.raises(EngineeringReviewOutputError):
        validate_engineering_review_output(payload)


def test_successor_schema_rejects_legacy_fields() -> None:
    schema = json.loads(
        (
            Path(__file__).resolve().parents[6]
            / "09_soul/governance/skills/engineering-change-review/runtime_modules"
            / "engineering_change_reviewer/schemas/input.schema.json"
        ).read_text(encoding="utf-8")
    )
    assert schema["$id"] == "schema:engineering_change_reviewer_input@v6"
    assert "change_set_manifest" not in schema["properties"]
    assert "subject_mode" not in schema["properties"]["subject"]["properties"]
    output_schema = json.loads(
        (
            Path(__file__).resolve().parents[6]
            / "09_soul/governance/skills/engineering-change-review/runtime_modules"
            / "engineering_change_reviewer/schemas/output.schema.json"
        ).read_text(encoding="utf-8")
    )
    assert output_schema["$id"] == "schema:engineering_change_reviewer_output@v6"
    assert set(output_schema["properties"]) == {"verdict", "check_results", "findings", "safe_next_step"}
