"""Prepare and validate a Design review using an already available executor."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Callable, Mapping

from jsonschema import Draft202012Validator, ValidationError


def _local_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


artifact_contract = _local_module("ddm_review_artifact_contract", "design_artifact_contract.py")
output_contract = _local_module("ddm_review_output_contract", "design_review_output.py")
GOVERNANCE_ROOT = Path(__file__).resolve().parents[3]
DDM_PATH = GOVERNANCE_ROOT / "t0/the_design_doc_management.md"
MODULE_ROOT = GOVERNANCE_ROOT / "skills/the-design-authoring/runtime_modules/design_contract_reviewer"
INPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/input.schema.json"


def _frontmatter(body: str) -> dict[str, str]:
    """Read the existing scalar identity fields; never infer domain meaning."""
    if not body.startswith("---\n"):
        return {}
    end = body.find("\n---\n", 3)
    if end < 0:
        raise ValueError("Design frontmatter is not closed")
    result = {}
    for line in body[4:end].splitlines():
        if not line or line[0].isspace() or line.startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if separator and value.strip():
            if key in result:
                raise ValueError(f"duplicate frontmatter field: {key}")
            result[key] = value.strip().strip("\"'")
    return result


def _read_document(path: Path, snapshot=None) -> tuple[str, dict[str, str]]:
    # read_bytes preserves line endings and the exact reviewed content.
    body = (path.read_bytes() if snapshot is None else snapshot[path]).decode("utf-8")
    if not body.strip():
        raise ValueError(f"empty review document: {path}")
    return body, _frontmatter(body)


def build_design_review_input(
    *, candidate_paths, context_bindings=(), review_purpose="owner_design_decision",
    candidate_revision_class="materially_revised_surface", intended_result: str,
    architecture_change_summary: str, prior_findings=(), ddm_path: Path = DDM_PATH, _snapshot=None,
) -> dict[str, object]:
    """Load explicit files and derive the existing Reviewer's input object."""
    if not intended_result.strip() or not architecture_change_summary.strip():
        raise ValueError("review goal and change scope must be non-empty")
    candidates = []
    for index, path in enumerate(candidate_paths, 1):
        path = Path(path)
        body, metadata = _read_document(path, _snapshot)
        layer = metadata.get("layer")
        if layer is None:
            declarations = re.findall(r"^layer:[ \t]*(Charter|T0|T1|T2)[ \t]*$", body, re.MULTILINE)
            if len(declarations) == 1:
                layer = declarations[0]
        if layer not in {"Charter", "T0", "T1", "T2"}:
            raise ValueError(f"missing or invalid layer: {path}")
        artifact_contract.validate_artifact(body.encode("utf-8"), layer=layer)
        title = metadata.get("title")
        if not title:
            headings = re.findall(r"^# (.+)$", body, re.MULTILINE)
            title = headings[0] if headings else None
        owned_object = metadata.get("owned_system_object")
        if not owned_object:
            section = re.search(r"^## \d+\. Owned System Object\s*\n(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL)
            owned_object = section.group(1).strip() if section else None
        if not title or not owned_object:
            raise ValueError(f"Design review requires title and an explicit owned system object: {path}")
        candidates.append({
            "document_id": f"candidate_{index}", "layer": layer, "title": title,
            "owner_ref": metadata.get("canonical_owner", path.as_posix()),
            "parent_ref": metadata.get("parent"), "owned_object": owned_object, "body": body,
        })
    layers = {document["layer"] for document in candidates}
    if len(layers) != 1:
        raise ValueError("one Design review needs candidates from one layer")
    layer = layers.pop()
    ddm_body, ddm_metadata = _read_document(ddm_path, _snapshot)
    contexts = []
    if all(document["body"] != ddm_body for document in candidates):
        contexts.append({
            "document_id": "ddm_authority", "context_role": "governing_contract",
            "owner_ref": ddm_metadata.get("canonical_owner", ddm_path.as_posix()),
            "title": ddm_metadata.get("title", "Design Doc Management"), "body": ddm_body,
        })
    contexts.append({
        "document_id": "requested_change", "context_role": "prior_decision",
        "owner_ref": "user_request", "title": "本次授权目标与修改范围",
        "body": f"目标：{intended_result}\n修改范围：{architecture_change_summary}",
    })
    for index, (role, owner, path) in enumerate(context_bindings, 1):
        path = Path(path)
        body, metadata = _read_document(path, _snapshot)
        contexts.append({
            "document_id": f"context_{index}", "context_role": role,
            "owner_ref": owner or metadata.get("canonical_owner", path.as_posix()),
            "title": metadata.get("title", path.stem), "body": body,
        })
    schema = json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = {
        "schema_version": schema["properties"]["schema_version"]["const"],
        "module_id": schema["properties"]["module_id"]["const"],
        "review_request": {
            "reviewed_subject_kind": f"{layer.lower()}_design", "review_purpose": review_purpose,
            "candidate_revision_class": candidate_revision_class,
            "intended_result": intended_result, "architecture_change_summary": architecture_change_summary,
        },
        "candidate_documents": candidates, "context_documents": contexts,
        "required_check_ids": list(output_contract.REQUIRED_CHECK_IDS),
        "prior_findings": list(prior_findings),
    }
    Draft202012Validator(schema).validate(payload)
    return payload


def review_documents(*, executor: Callable, candidate_paths, context_bindings=(), **kwargs):
    """Run explicit frozen inputs; registration and source edits stay outside."""
    paths = tuple(Path(p) for p in candidate_paths)
    bindings = tuple((role, owner, Path(path)) for role, owner, path in context_bindings)
    watched = (*paths, *(item[2] for item in bindings), Path(kwargs.get("ddm_path", DDM_PATH)))
    before = {path: path.read_bytes() for path in watched}
    payload = build_design_review_input(candidate_paths=paths, context_bindings=bindings, _snapshot=before, **kwargs)
    # Refuse concurrent edits while inputs are being assembled, before dispatch.
    if any(path.read_bytes() != value for path, value in before.items()):
        raise ValueError("review input changed during preparation")
    record = dict(executor(payload))
    validation = {"status": "not_run", "message": None}
    try:
        if not str(record.get("module_release_ref", "")).startswith("runtime-module:design_contract_reviewer@"):
            raise ValueError("execution result is not from design_contract_reviewer")
        if any(path.read_bytes() != value for path, value in before.items()):
            raise ValueError("review input changed after dispatch")
        if record.get("status") == "completed":
            output_contract.validate_design_contract_review_output(record.get("output"), payload)
            validation = {"status": "passed", "message": None}
        else:
            validation = {"status": "not_run", "message": "Runtime execution did not complete"}
    except (OSError, ValueError, TypeError, KeyError, ValidationError) as exc:
        validation = {"status": "failed", "message": str(exc)}
    record["semantic_input"] = payload
    record["semantic_validation"] = validation
    record["candidate_sha256_by_document_id"] = {
        document["document_id"]: hashlib.sha256(document["body"].encode()).hexdigest()
        for document in payload["candidate_documents"]
    }
    return record


def _runtime_review():
    """Load the shared Runtime Test Run binding by path, so this file also runs as a script."""
    name = "portable_runtime_review"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / "runtime_review.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _context(value: str):
    identity, separator, path = value.partition("=")
    role, _, owner = identity.partition("@")
    if not separator or not path or role not in output_contract.CONTEXT_ROLES:
        raise argparse.ArgumentTypeError("context must use ROLE[@OWNER_REF]=PATH")
    return role, owner or None, Path(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="经 Agent Runtime Test Run 独立审核 Design 文档；不注册 Module、不修改文稿。")
    parser.add_argument("--candidate", action="append", type=Path, required=True)
    parser.add_argument("--goal", required=True, help="本次修改目标")
    parser.add_argument("--change", required=True, help="本次修改范围和要点")
    parser.add_argument("--context", action="append", type=_context, default=[], metavar="ROLE[@OWNER]=PATH",
                        help="可选背景；ROLE 使用 " + ", ".join(output_contract.CONTEXT_ROLES))
    parser.add_argument("--new", action="store_true", help="新建文档；默认审核已有文档修订")
    parser.add_argument("--prior-findings", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="新的结果文件，禁止覆盖")
    runtime = _runtime_review()
    runtime.add_runtime_arguments(parser)
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("output already exists; choose a new result path")
    if not args.output.parent.is_dir():
        parser.error("output directory does not exist")
    try:
        fields = runtime.runtime_kwargs(args)
    except ValueError as exc:
        parser.error(str(exc))
    def executor(payload):
        return runtime.run_review_test(payload, runtime_kwargs=fields)
    prior = [] if args.prior_findings is None else json.loads(args.prior_findings.read_text())
    record = review_documents(
        executor=executor, candidate_paths=args.candidate, context_bindings=args.context,
        intended_result=args.goal, architecture_change_summary=args.change,
        candidate_revision_class="new_document" if args.new else "materially_revised_surface",
        prior_findings=prior,
    )
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    valid = record["semantic_validation"]["status"] == "passed"
    verdict = record["output"]["verdict"] if valid else None
    print(json.dumps({"execution": record.get("status"), "output_validation": record["semantic_validation"], "verdict": verdict, "output": str(args.output)},ensure_ascii=False))
    return 0 if valid and verdict == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
