"""Check current Skill source or review it with an already configured executor.

Candidate text must match current declared canonical sources, not their older
published digests. Publication manifests and installations remain unchanged;
release validation is a separate operation. Source, adapter and frozen-input
checks still apply before the independently configured executor is called.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, ValidationError


def _local_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[4]
GOVERNANCE_ROOT = HERE.parents[2]
MODULE_ROOT = GOVERNANCE_ROOT / "skills/the-skill-authoring/runtime_modules/skill_candidate_reviewer"
INPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/input.schema.json"
artifact = _local_module("skill_review_artifact_contract", HERE / "skill_artifact_contract.py")
output_contract = _local_module("skill_review_output_contract", HERE / "skill_review_output.py")
release = _local_module("skill_review_release_resources", HERE.parent / "skill_release.py")


def _instruction_payloads(project_root, resource_ids, read, resource_bindings=()):
    if not resource_ids:
        return {}
    governance = project_root / "09_soul/governance"
    read(governance / "governance_skill_manifest.json")
    read(governance / "governance_t0_manifest.json")
    manifest = release.load_governance_skill_manifest(project_root)
    available = {item.resource_id: item for item in manifest.instruction_resources}
    extra = dict(resource_bindings)
    if len(extra) != len(resource_bindings) or set(extra) & set(available):
        raise ValueError("Extra resources cannot duplicate or override canonical package resources")
    if set(extra) - set(resource_ids):
        raise ValueError("Extra resource is not declared by this Skill")
    if set(resource_ids) - set(available) - set(extra):
        raise ValueError("Skill declares an instruction resource absent from the manifest")
    contracts = release._known_t0_artifact_contracts(project_root)
    result = {}
    for identity in resource_ids:
        if identity in extra:
            payload = read(Path(extra[identity]))
            release._instruction_source_lines(payload, source=str(extra[identity]))
            if not payload.strip():
                raise ValueError("Extra instruction resource is empty")
            result[identity] = payload
            continue
        resource = available[identity]
        path = release._resolve_without_symlink_escape(project_root, resource.source)
        payload = read(path)
        if resource.source in contracts:
            read(release._resolve_without_symlink_escape(project_root, contracts[resource.source].adapter))
        result[identity] = release.select_candidate_instruction_resource_bytes(
            resource, payload, project_root=project_root, artifact_contracts_by_source=contracts,
        )
    return result


def check_skill(candidate_path, *, project_root=PROJECT_ROOT, checklist_resource=None, resource_bindings=(), read=None):
    """Validate exact candidate bytes against current sources under project_root.

    Manifest entries locate canonical resources; their published text digests
    do not gate authoring. Registered adapter code and resource ownership remain
    checked. Extra resources cannot replace existing canonical resources.
    """
    read = read or (lambda path: Path(path).read_bytes())
    payload = read(Path(candidate_path))
    identities = tuple(item.decode("utf-8") for item in re.findall(
        rb"^<!-- embedded-resource:([^\n]+):start -->$", payload, re.MULTILINE,
    ))
    if resource_bindings and not identities:
        raise ValueError("Extra resource is not declared by this Skill")
    resources = _instruction_payloads(Path(project_root), identities, read, resource_bindings)
    composed = release.compose_governance_skill_package_file(payload, identities, resources)
    if composed != payload:
        raise ValueError("Skill instruction bytes differ from their canonical sources")
    bindings = None
    if checklist_resource is not None:
        name = artifact._frontmatter_scalars(payload.decode("utf-8"))[0].get("name")
        if checklist_resource not in resources:
            raise ValueError("Selected checklist is not an embedded, validated resource")
        bindings = {name: checklist_resource}
    result = artifact.validate_artifact(
        payload, embedded_resource_ids=identities, checklist_resource_by_skill_id=bindings,
    )
    report = asdict(result)
    report["resource_sha256"] = {key: hashlib.sha256(value).hexdigest() for key, value in resources.items()}
    report["review_required_check_ids"] = [item["check_id"] for item in artifact.load_contract()["reviewer_checklist"]["checks"]]
    return report


def _assert_frozen(frozen):
    for path, (resolved, data) in frozen.items():
        # Reject a changed binding before reading any newly selected target.
        if path.resolve(strict=True) != resolved:
            raise ValueError("Skill input or path binding changed")
        # Resolution can erase components that the OS cannot actually traverse.
        path.stat()
        if resolved.read_bytes() != data:
            raise ValueError("Skill input or path binding changed")


def _prepare(*, candidate_path, goal, change, self_check_path, design_paths=(), context_bindings=(), prompt_bindings=(),
             prior_findings=(), project_root=PROJECT_ROOT, checklist_resource=None, resource_bindings=()):
    if not goal.strip() or not change.strip():
        raise ValueError("Skill review requires a non-empty authorized goal and change scope")
    project_root = Path(project_root)
    frozen = {}
    def read(path):
        path = Path(path).absolute()
        resolved = path.resolve(strict=True)
        if path in frozen and frozen[path][0] != resolved:
            raise ValueError("Skill input path binding changed during preparation")
        path.stat()
        data = resolved.read_bytes()
        state = (resolved, data)
        if path in frozen and frozen[path] != state:
            raise ValueError("Skill input changed during preparation")
        frozen[path] = state
        return data
    read(artifact.CONTRACT_PATH)
    read(output_contract.OUTPUT_SCHEMA_PATH)
    report = check_skill(candidate_path, project_root=project_root, checklist_resource=checklist_resource,
                         resource_bindings=resource_bindings, read=read)
    body = read(candidate_path).decode("utf-8")
    check_ids = report["review_required_check_ids"]
    self_check = json.loads(read(self_check_path))
    if not isinstance(self_check, dict) or set(self_check) != {"candidate_sha256", "rows"} or not isinstance(self_check["rows"], list):
        raise ValueError("Self-check must contain candidate_sha256 and rows")
    artifact.validate_author_self_check_submission(
        body.encode(), declared_candidate_sha256=self_check["candidate_sha256"],
        required_check_ids=tuple(check_ids), rows=tuple(self_check["rows"]),
    )
    def document(identity, kind, path):
        text = read(path).decode("utf-8")
        if not text.strip():
            raise ValueError(f"Empty Skill review context: {path}")
        return {"document_id": identity, "document_kind": kind, "body": text}
    governance = project_root / "09_soul/governance"
    designs = [document("skill_management", "design_contract", governance / "t0/the_skill_management.md")]
    designs += [document(f"design_{index}", "design_contract", path) for index, path in enumerate(design_paths, 1)]
    designs.append({"document_id": "user_request", "document_kind": "design_contract", "body": f"本次授权目标：{goal}\n本次修改范围：{change}"})
    contexts = [document(f"context_{index}", kind, path) for index, (kind, path) in enumerate(context_bindings, 1)]
    contexts.append({"document_id": "candidate_checks", "document_kind": "registration_inspection",
                     "body": json.dumps({**report, "author_self_check": self_check["rows"]}, ensure_ascii=False)})
    prompts = [{"prompt_id": identity, "prompt_body": read(path).decode("utf-8")} for identity, path in prompt_bindings]
    if len({item["prompt_id"] for item in prompts}) != len(prompts):
        raise ValueError("Skill prompt identities must be unique")
    schema = json.loads(read(INPUT_SCHEMA_PATH))
    payload = {
        "schema_version": schema["properties"]["schema_version"]["const"], "module_id": "skill_candidate_reviewer",
        "skill_candidate": {"skill_id": report["skill_id"], "candidate_revision": 1,
                            "candidate_body": body, "runtime_ready_prompts": prompts},
        "owning_design_closure": designs, "source_and_projection_closure": contexts,
        "required_check_ids": check_ids, "prior_findings": list(prior_findings),
    }
    Draft202012Validator(schema).validate(payload)
    # These code-owned contracts also belong to the stable input used by this call.
    read(artifact.CONTRACT_PATH)
    read(output_contract.OUTPUT_SCHEMA_PATH)
    _assert_frozen(frozen)
    return payload, frozen


def review_skill(*, executor, **kwargs):
    payload, frozen = _prepare(**kwargs)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    original = json.loads(encoded)
    subject_sha256 = hashlib.sha256(original["skill_candidate"]["candidate_body"].encode()).hexdigest()
    _assert_frozen(frozen)
    record = dict(executor(payload))
    validation = {"status": "not_run", "message": "Reviewer execution did not complete"}
    try:
        if "semantic_validation" in record:
            previous = record["semantic_validation"]
            if not isinstance(previous, dict) or previous.get("status") != "passed":
                raise ValueError("Previously invalid execution record: " + json.dumps(previous, ensure_ascii=False))
        if "semantic_input" in record and json.dumps(record["semantic_input"], ensure_ascii=False, sort_keys=True) != encoded:
            raise ValueError("Execution record belongs to a different Skill review input")
        if "subject_sha256" in record and record["subject_sha256"] != subject_sha256:
            raise ValueError("Execution record belongs to a different Skill candidate")
        if not str(record.get("module_release_ref", "")).startswith("runtime-module:skill_candidate_reviewer@"):
            raise ValueError("Execution record is not from skill_candidate_reviewer")
        if json.dumps(payload, ensure_ascii=False, sort_keys=True) != encoded:
            raise ValueError("Executor changed the Skill review input")
        _assert_frozen(frozen)
        if record.get("status") == "completed":
            output_contract.validate_skill_review_output(record.get("output"), payload)
            validation = {"status": "passed", "message": None}
    except (ValueError, OSError, RuntimeError, TypeError, KeyError, ValidationError) as exc:
        validation = {"status": "failed", "message": str(exc)}
    record.setdefault("semantic_input", original)
    record["semantic_validation"] = validation
    record.setdefault("subject_sha256", subject_sha256)
    return record


def _binding(value):
    identity, separator, path = value.partition("=")
    if not separator or not identity.strip() or not path:
        raise argparse.ArgumentTypeError("Use ID=PATH or document_kind=PATH")
    return identity, Path(path)


def _runtime_review():
    """Load the shared Runtime Test Run binding by path, so this file also runs as a script."""
    name = "portable_runtime_review"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / "runtime_review.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="检查完整 Skill；经 Agent Runtime Test Run 由独立 Reviewer 审核，不注册或部署。",
        epilog="候选须与当前声明的 canonical 来源一致，不要求文字仍等于旧发布 hash；"
               "不会更新 manifest 或安装投影。发布校验另行执行，来源、adapter 和输入冻结检查仍保留。",
    )
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true", help="只检查候选及其声明资源，不调用 Reviewer")
    parser.add_argument("--self-check-template", type=Path, help="随 --check-only 生成临时自检表；hash 和 check_id 由代码填写")
    parser.add_argument("--checklist-resource", help="新 Skill 明确使用的 canonical checklist resource_id")
    parser.add_argument("--resource", type=_binding, action="append", default=[], help="补充资源 ID=PATH；不能覆盖随包 canonical 资源")
    parser.add_argument("--goal")
    parser.add_argument("--change")
    parser.add_argument("--self-check", type=Path, help="临时 JSON：candidate_sha256 与逐项 rows")
    parser.add_argument("--design", type=Path, action="append", default=[])
    parser.add_argument("--context", type=_binding, action="append", default=[])
    parser.add_argument("--prompt", type=_binding, action="append", default=[])
    parser.add_argument("--prior-findings", type=Path)
    parser.add_argument("--output", type=Path)
    runtime = _runtime_review()
    runtime.add_runtime_arguments(parser)
    args = parser.parse_args(argv)
    try:
        if args.check_only:
            report = check_skill(args.candidate, checklist_resource=args.checklist_resource, resource_bindings=args.resource)
            if args.self_check_template is not None:
                target = args.self_check_template
                if target.exists() or target.is_symlink() or not target.parent.is_dir():
                    parser.error("self-check template must be a new file in an existing directory")
                template = {"candidate_sha256": report["subject_sha256"], "rows": [
                    {"check_id": identity, "exact_evidence": "", "local_result": "", "unresolved_finding": None}
                    for identity in report["review_required_check_ids"]
                ]}
                with target.open("x", encoding="utf-8") as stream:
                    json.dump(template, stream, ensure_ascii=False, indent=2)
                    stream.write("\n")
            print(json.dumps(report, ensure_ascii=False))
            return 0
        if args.self_check_template is not None:
            parser.error("--self-check-template requires --check-only")
        if not all((args.goal, args.change, args.self_check, args.output)):
            parser.error("review requires --goal, --change, --self-check and --output")
        try:
            fields = runtime.runtime_kwargs(args)
        except ValueError as exc:
            parser.error(str(exc))
        if args.output.exists() or args.output.is_symlink() or not args.output.parent.is_dir():
            parser.error("output must be a new file in an existing directory")
        inputs = [args.candidate, args.self_check, *args.design, *(path for _, path in args.context),
                  *(path for _, path in args.prompt), *(path for _, path in args.resource)]
        if args.prior_findings:
            inputs.append(args.prior_findings)
        if args.output.resolve() in {path.resolve() for path in inputs}:
            parser.error("output must not replace an input")
        def executor(payload):
            return runtime.run_review_test(payload, runtime_kwargs=fields)
        prior = [] if args.prior_findings is None else json.loads(args.prior_findings.read_text(encoding="utf-8"))
        record = review_skill(
            executor=executor, candidate_path=args.candidate, goal=args.goal, change=args.change,
            self_check_path=args.self_check, design_paths=args.design, context_bindings=args.context,
            prompt_bindings=args.prompt, prior_findings=prior, checklist_resource=args.checklist_resource,
            resource_bindings=args.resource,
        )
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        valid = record["semantic_validation"]["status"] == "passed"
        verdict = record["output"]["verdict"] if valid else None
        print(json.dumps({"execution": record.get("status"), "validation": record["semantic_validation"], "verdict": verdict, "output": str(args.output)}, ensure_ascii=False))
        return 0 if valid and verdict == "passed" else 1
    except Exception as exc:
        # Runtime and validation failures use the CLI diagnostic; control exceptions propagate.
        print(json.dumps({"error": str(exc), "error_type": type(exc).__name__,
                          "error_code": getattr(exc, "error_code", None)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
