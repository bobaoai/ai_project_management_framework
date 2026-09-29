"""Run one plan or implementation review through a configured independent executor."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from software_delivery.engineering_review_input import (
    INPUT_SCHEMA_PATH, build_code_design_review_input, build_engineering_review_input,
    command_plan, hashed_body,
)
from software_delivery.engineering_review_materials import write_review_resources
from software_delivery.engineering_review_output import (
    OUTPUT_SCHEMA_PATH, engineering_check_ids, validate_engineering_review_output, validate_engineering_reviewer_identity,
)


def _assert_frozen(frozen):
    for path, (resolved, data) in frozen.items():
        # Check the binding before reading, so a retargeted link is not dereferenced for content.
        if path.resolve(strict=True) != resolved:
            raise ValueError("Engineering review material or path binding changed")
        path.stat()  # Traverse the original spelling; resolve may elide search permissions at '..'.
        if resolved.read_bytes() != data:
            raise ValueError("Engineering review material or path binding changed")


def prepare_review(*, plan_path, goal, change, acceptance_criteria, repository_root=None, commit_ref=None,
                   plan_review_path=None, system_change_path=None, context_paths=(), commands_path=None,
                   prior_findings_path=None, self_check_path=None):
    if not isinstance(goal, str) or not goal.strip() or not isinstance(change, str) or not change.strip():
        raise ValueError("Engineering review requires an authorized goal and change scope")
    if (repository_root is None) != (commit_ref is None):
        raise ValueError("Implementation review requires both repository_root and commit_ref")
    if commit_ref is None and plan_review_path is not None:
        raise ValueError("A plan review does not consume its own future review result")
    frozen = {}
    def read(path):
        path = Path(path).absolute()
        resolved = path.resolve(strict=True)
        if path in frozen and frozen[path][0] != resolved:
            raise ValueError("Engineering review path binding changed during preparation")
        path.stat()
        data = resolved.read_bytes()
        state = (resolved, data)
        if path in frozen and frozen[path] != state:
            raise ValueError("Engineering review material changed during preparation")
        frozen[path] = state
        return data
    def material(path):
        path = Path(path).absolute()
        body = read(path).decode("utf-8")
        return hashed_body(str(frozen[path][0]), body)
    read(INPUT_SCHEMA_PATH)
    read(OUTPUT_SCHEMA_PATH)
    required_ids = engineering_check_ids(read)
    commands = [] if commands_path is None else json.loads(read(commands_path))
    if not isinstance(commands, list):
        raise ValueError("Commands file must contain a JSON array")
    prior = [] if prior_findings_path is None else json.loads(read(prior_findings_path))
    if not isinstance(prior, list):
        raise ValueError("Prior findings must be a JSON array")
    basis = material(plan_path)
    if self_check_path is not None:
        if commit_ref is not None:
            raise ValueError("Plan author self-check is only used before plan review")
        row_set = json.loads(read(self_check_path))
        if not isinstance(row_set, dict) or set(row_set) != {"candidate_sha256", "rows"}:
            raise ValueError("Self-check must contain candidate_sha256 and rows")
        validation_root = Path(__file__).resolve().parents[1]
        helper = validation_root/"artifact_contracts/skill_artifact_contract.py"
        read(helper)
        spec = importlib.util.spec_from_file_location("engineering_author_self_check", helper)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.validate_author_self_check_submission(basis["body"].encode(),
            declared_candidate_sha256=row_set["candidate_sha256"], required_check_ids=required_ids,
            rows=tuple(row_set["rows"]))
    options = dict(
        code_design_basis=basis,
        system_change_plan_step=None if system_change_path is None else material(system_change_path),
        sandbox_command_plan=command_plan("review_commands", commands),
        acceptance_criteria=acceptance_criteria,
        context_documents=[hashed_body("user_request", f"本次授权目标：{goal}\n本次修改范围：{change}"),
                           *(material(path) for path in context_paths)],
        prior_findings=prior,
    )
    if commit_ref is None:
        payload = build_code_design_review_input(**options)
    else:
        payload = build_engineering_review_input(repository_root=Path(repository_root), commit_ref=commit_ref,
            code_design_review=None if plan_review_path is None else material(plan_review_path), **options)
    _assert_frozen(frozen)
    if payload["required_check_ids"] != list(required_ids):
        raise ValueError("Software Delivery checklist changed during preparation")
    return payload, frozen


def review_engineering(*, executor, **kwargs):
    """The executor returns its actual semantic_input and review_purpose with completed output.

    The caller's invocation adapter supplies these from the request it executed; a bare
    historical verdict is not sufficient evidence for the current request.
    """
    payload, frozen = prepare_review(**kwargs)
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    _assert_frozen(frozen)
    record = dict(executor(payload))
    validation = {"status": "not_run", "message": "Independent execution did not complete"}
    try:
        if "semantic_validation" in record:
            previous_validation = record["semantic_validation"]
            if not isinstance(previous_validation, dict) or previous_validation.get("status") != "passed":
                raise ValueError("Previously invalid execution record: " + json.dumps(previous_validation, ensure_ascii=False))
        validate_engineering_reviewer_identity(record)
        if (record.get("status") == "completed" or "review_purpose" in record) and record.get("review_purpose") != payload["review_purpose"]:
            raise ValueError("Execution record belongs to a different review purpose")
        if (record.get("status") == "completed" or "semantic_input" in record) and json.dumps(record.get("semantic_input"), ensure_ascii=False, sort_keys=True) != serialized:
            raise ValueError("Execution record belongs to a different review input")
        if json.dumps(payload, ensure_ascii=False, sort_keys=True) != serialized:
            raise ValueError("Executor changed the review input")
        _assert_frozen(frozen)
        if payload["review_purpose"] == "implementation":
            pinned = dict(kwargs)
            pinned["commit_ref"] = payload["subject"]["commit_ref"]
            current, _ = prepare_review(**pinned)
            if current["subject"] != payload["subject"]:
                raise ValueError("Reviewed Git subject changed after dispatch")
        if record.get("status") == "completed":
            validate_engineering_review_output(record.get("output"), review_input=payload, execution_record=record)
            validation = {"status": "passed", "message": None}
    except (ValueError, OSError, TypeError, KeyError) as exc:
        validation = {"status": "failed", "message": str(exc)}
    original = json.loads(serialized)
    if validation["status"] == "passed":
        record.setdefault("module_id", "engineering_change_reviewer")
    if record.get("status") != "completed":
        record.setdefault("semantic_input", original)
    record.update(semantic_validation=validation,
                  source_sha256={str(path):hashlib.sha256(data).hexdigest() for path, (_, data) in frozen.items()})
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


def main(argv=None):
    parser = argparse.ArgumentParser(description="经 Agent Runtime Test Run 独立审核工程计划或 exact commit，不注册、不修改候选。")
    parser.add_argument("--plan", type=Path, required=True, help="CodeDesignBasis / plan doc")
    parser.add_argument("--commit", help="实现审核的 commit；省略时审计划")
    parser.add_argument("--repository", type=Path, help="--commit 所属仓库")
    parser.add_argument("--plan-review", type=Path, help="实现审核所需的已通过计划审核记录")
    parser.add_argument("--system-change", type=Path, help="另有 SystemChangePlan 时的相关步骤")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--change", required=True)
    parser.add_argument("--criterion", action="append", required=True, help="验收要求，可重复")
    parser.add_argument("--context", type=Path, action="append", default=[])
    parser.add_argument("--commands", type=Path, help="允许的命令 JSON 数组，required 默认 true；同时成为 Runtime 可执行的命令")
    parser.add_argument("--read", action="append", default=[],
                        help="实现审核：受审 commit 中需要一并提供的未变更文件或目录（相对仓库根），可重复")
    parser.add_argument("--dependency", type=Path, action="append", default=[],
                        help="声明命令运行所需的只读依赖目录（绝对路径），可重复")
    parser.add_argument("--prior-findings", type=Path)
    parser.add_argument("--self-check", type=Path, help="计划作者的临时自检表：candidate_sha256 与 rows")
    parser.add_argument("--self-check-template", type=Path, help="随 --check-only 生成计划作者的临时自检表")
    parser.add_argument("--check-only", action="store_true", help="只检查并组装输入，不调用 Reviewer")
    parser.add_argument("--output", type=Path, help="新的结果文件，不允许覆盖")
    runtime = _runtime_review()
    runtime.add_runtime_arguments(parser)
    args = parser.parse_args(argv)
    if args.resources is not None:
        parser.error("Engineering review builds its Runtime resources from --commit, --read, --commands and "
                     "--dependency; --resources is not accepted")
    options = dict(plan_path=args.plan, goal=args.goal, change=args.change, acceptance_criteria=args.criterion,
        repository_root=args.repository, commit_ref=args.commit, plan_review_path=args.plan_review,
        system_change_path=args.system_change, context_paths=args.context, commands_path=args.commands,
        prior_findings_path=args.prior_findings, self_check_path=args.self_check)
    def resources(payload, target):
        # Runtime commands come from the frozen input declaration, never from a second read.
        return write_review_resources(payload=payload, repository_root=args.repository, read_paths=args.read,
                                      commands=payload["sandbox_command_plan"]["commands"],
                                      dependencies=args.dependency, target=Path(target))
    try:
        if args.check_only:
            payload, _ = prepare_review(**options)
            with tempfile.TemporaryDirectory(prefix="engineering-review-resources-") as directory:
                resources(payload, directory)
            if args.self_check_template is not None:
                target = args.self_check_template
                if args.commit is not None or target.exists() or target.is_symlink() or not target.parent.is_dir():
                    parser.error("plan self-check template must be a new file in an existing directory")
                template = {"candidate_sha256":payload["code_design_basis"]["sha256"], "rows":[
                    {"check_id":identity, "exact_evidence":"", "local_result":"", "unresolved_finding":None}
                    for identity in payload["required_check_ids"]]}
                with target.open("x", encoding="utf-8") as stream:
                    json.dump(template,stream,ensure_ascii=False,indent=2)
                    stream.write("\n")
            print(json.dumps(payload, ensure_ascii=False))
            return 0
        if args.self_check_template is not None:
            parser.error("self-check template requires --check-only")
        if not args.output:
            parser.error("review requires --output")
        fields = runtime.runtime_kwargs(args)
        if args.output.exists() or args.output.is_symlink() or not args.output.parent.is_dir():
            parser.error("output must be a new file in an existing directory")
        watched = [args.plan, args.plan_review, args.system_change, args.commands, args.prior_findings, args.self_check,
                   INPUT_SCHEMA_PATH, OUTPUT_SCHEMA_PATH, *args.context]
        if args.output.resolve() in {path.resolve() for path in watched if path is not None}:
            parser.error("output cannot overwrite review input")
        def runtime_executor(payload):
            with tempfile.TemporaryDirectory(prefix="engineering-review-resources-") as directory:
                path = resources(payload, directory)
                selected = fields if path is None else {**fields, "resources_path": path}
                return runtime.run_review_test(payload, runtime_kwargs=selected)
        record = review_engineering(executor=runtime_executor, **options)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        valid = record["semantic_validation"]["status"] == "passed"
        verdict = record.get("output", {}).get("verdict") if valid else None
        print(json.dumps({"execution":record.get("status"), "output_validation":record["semantic_validation"],
                          "verdict":verdict, "output":str(args.output)}, ensure_ascii=False))
        return 0 if valid and verdict == "passed" else 1
    except Exception as exc:
        # Interrupts and SystemExit still propagate; ordinary failures never become verdicts.
        print(json.dumps({"error": str(exc), "error_type": type(exc).__name__,
                          "error_code": getattr(exc, "error_code", None)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
