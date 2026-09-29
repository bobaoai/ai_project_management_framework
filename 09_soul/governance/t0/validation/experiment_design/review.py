"""实验方案的确定性输入、结构和 Reviewer 返回检查。"""
from __future__ import annotations

import hashlib
import argparse
from copy import deepcopy
from dataclasses import dataclass
import importlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import sys

from jsonschema import Draft202012Validator


MODULE_ROOT = Path(__file__).resolve().parents[3] / "skills/experiment-authoring/runtime_modules/experiment_reviewer"
PROSE_CHECK = "prose_and_meaning_preservation"
CHECKS = ("experiment_sections", "experiment_environment_sections", "experiment_declared_inputs")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _nonblank(value) -> None:
    if isinstance(value, str) and not value.strip():
        raise ValueError("必填文本不能只有空白")
    if isinstance(value, dict):
        for item in value.values():
            _nonblank(item)
    elif isinstance(value, list):
        for item in value:
            _nonblank(item)


def _read(path: Path) -> tuple[Path, bytes]:
    path = Path(path).absolute()
    info = path.stat()
    if path.is_symlink() or not stat.S_ISREG(info.st_mode):
        raise ValueError(f"输入必须是普通文件：{path}")
    resolved = path.resolve(strict=True)
    data = resolved.read_bytes()
    text = data.decode("utf-8")
    if not text.strip():
        raise ValueError(f"输入必须是非空 UTF-8 文本：{path}")
    return resolved, data


def _schema(name: str, module_root: Path) -> dict:
    _, raw = _read(Path(module_root) / "schemas" / f"{name}.schema.json")
    result = json.loads(raw)
    Draft202012Validator.check_schema(result)
    return result


def _visible_lines(text: str) -> list[str]:
    """保留行位置；代码块计作内容，但其中的标题不参与结构检查。"""
    lines = []
    fence = None
    comment = False
    for line in text.splitlines():
        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*", line):
                fence = None
                lines.append("")
            else:
                lines.append("    " + line)
            continue
        visible = ""
        rest = line
        while rest:
            if comment:
                end = rest.find("-->")
                if end < 0:
                    rest = ""
                else:
                    comment, rest = False, rest[end + 3:]
            else:
                start = rest.find("<!--")
                if start < 0:
                    visible += rest
                    rest = ""
                else:
                    visible += rest[:start]
                    comment, rest = True, rest[start + 4:]
        opening = re.match(r" {0,3}(`{3,}|~{3,})(.*)$", visible)
        if opening and not (opening[1][0] == "`" and "`" in opening[2]):
            fence = (opening[1][0], len(opening[1]))
            visible = ""
        lines.append(visible)
    if fence or comment:
        raise ValueError("文稿存在未闭合的代码围栏或 HTML comment")
    return lines


def _contract(design_body: str) -> tuple[list[str], list[str], list[str]]:
    parts, environment = [], []
    for line in _visible_lines(design_body):
        if not line.startswith("|"):
            continue
        first = line.split("|")[1].strip().strip("` ")
        if re.fullmatch(r"[1-6]\. .+", first):
            parts.append(first)
        if re.fullmatch(r"3\.[1-6] .+", first):
            environment.append(first)
    start, end = "<!-- experiment-review-checklist:start -->", "<!-- experiment-review-checklist:end -->"
    if design_body.count(start) != 1 or design_body.count(end) != 1:
        raise ValueError("实验 T0 必须提供唯一 checklist source")
    if design_body.index(start) >= design_body.index(end):
        raise ValueError("实验 checklist source 边界次序错误")
    section = design_body.split(start, 1)[1].split(end, 1)[0]
    ids = re.findall(r"^\|\s*`([a-z][a-z0-9_]*)`\s*\|", section, re.M)
    if (len(parts) != 6 or [x.split(".", 1)[0] for x in parts] != list("123456")
            or len(environment) != 6 or [x.split(" ", 1)[0] for x in environment] != [f"3.{i}" for i in range(1, 7)]
            or len(ids) != 9 or len(set(ids)) != 9 or ids[-1] != PROSE_CHECK):
        raise ValueError("实验 T0 的结构表或 checklist 不完整")
    return parts, environment, ids


def _headings(lines: list[str], level: int) -> list[tuple[int, str]]:
    pattern = re.compile(r" {0,3}" + "#" * level + r"[ \t]+(.+?)\s*$")
    return [(i, re.sub(r"\s+#+\s*$", "", match[1]))
            for i, line in enumerate(lines) if (match := pattern.fullmatch(line))]


def _check_body(body: str, design_body: str) -> list[str]:
    parts, environment, ids = _contract(design_body)
    lines = _visible_lines(body)
    headings = _headings(lines, 2)
    if [text for _, text in headings] != parts:
        raise ValueError("实验方案必须按 T0 的六个部分完整排列，标题不得重复或缺失")
    for pos, (index, title) in enumerate(headings):
        end = headings[pos + 1][0] if pos + 1 < len(headings) else len(lines)
        content = lines[index + 1:end]
        if not any(line.strip() and not re.match(r" {0,3}#{1,6}(?:\s|$)", line) for line in content):
            raise ValueError(f"章节缺少内容：{title}")
    begin, end = headings[2][0], headings[3][0]
    all_sub = _headings(lines, 3)
    sub = [(i, title) for i, title in all_sub if begin < i < end]
    if [title for _, title in sub] != environment:
        raise ValueError("环境与独立性必须完整包含 T0 规定的六个小节")
    if [(i, title) for i, title in all_sub if re.match(r"3\.\d+(?:\s|$)", title)] != sub:
        raise ValueError("环境小节必须在第三部分内唯一出现，不能跨章节重复")
    for pos, (index, title) in enumerate(sub):
        limit = sub[pos + 1][0] if pos + 1 < len(sub) else end
        if not any(line.strip() and not re.match(r" {0,3}#{1,6}(?:\s|$)", line) for line in lines[index + 1:limit]):
            raise ValueError(f"环境小节缺少填写内容：{title}")
    return ids


def check_experiment(candidate, design, *, module_root=MODULE_ROOT) -> dict:
    candidate_path, raw = _read(Path(candidate))
    design_path, authority = _read(Path(design))
    if candidate_path.samefile(design_path):
        raise ValueError("实验候选与 governing contract 不能是同一文件")
    schema = _schema("input", Path(module_root))
    expected = schema["$defs"]["governing_document"]["properties"]["sha256"]["const"]
    if _sha(authority) != expected:
        raise ValueError("实验 T0 与本 Reviewer source 绑定的版本不同")
    body, design_body = raw.decode(), authority.decode()
    ids = _check_body(body, design_body)
    return {"candidate_body": body, "candidate_sha256": _sha(raw),
            "design_body": design_body, "design_sha256": _sha(authority),
            "required_check_ids": ids, "checks": list(CHECKS)}


def _document(identity: str, owner: str, title: str, body: str) -> dict:
    return {"document_id": identity, "owner_ref": owner, "title": title,
            "body": body, "sha256": _sha(body.encode())}


def build_input(candidate, goal, change, design, contexts=(), prior_findings=(), *,
                candidate_owner_ref="experiment-authoring", module_root=MODULE_ROOT) -> dict:
    report = check_experiment(candidate, design, module_root=module_root)
    seen = [Path(candidate).resolve(strict=True), Path(design).resolve(strict=True)]
    documents = [_document("review_request", "requester", "本次请求", f"目标：{goal}\n范围：{change}")]
    for index, (owner, path) in enumerate(contexts, 1):
        resolved, data = _read(Path(path))
        if any(resolved.samefile(prior) for prior in seen):
            raise ValueError("声明材料重复或把候选再次作为背景")
        seen.append(resolved)
        documents.append(_document(f"context_{index}", owner, Path(path).stem, data.decode()))
    payload = {
        "schema_version": "experiment_reviewer_input_v1", "module_id": "experiment_reviewer",
        "review_request": {"goal": goal, "change": change},
        "experiment_design": _document("experiment_design", candidate_owner_ref, "实验方案", report["candidate_body"]),
        "governing_contract": _document("experiment_contract", "designDoc/the_agent_experiment_design.md", "Agent 实验设计", report["design_body"]),
        "context_documents": documents,
        "deterministic_evidence": {"candidate_sha256": report["candidate_sha256"], "checks": report["checks"]},
        "required_check_ids": report["required_check_ids"], "prior_findings": list(prior_findings),
    }
    validate_input(payload, module_root=module_root)
    return payload


def validate_input(payload: dict, *, module_root=MODULE_ROOT) -> None:
    Draft202012Validator(_schema("input", Path(module_root))).validate(payload)
    _nonblank(payload)
    docs = [payload["experiment_design"], payload["governing_contract"], *payload["context_documents"]]
    if len({doc["document_id"] for doc in docs}) != len(docs):
        raise ValueError("输入中的 document_id 必须唯一")
    for doc in docs:
        if not doc["body"].strip() or _sha(doc["body"].encode()) != doc["sha256"]:
            raise ValueError("输入文稿内容与声明 hash 不一致")
    if payload["experiment_design"]["sha256"] != payload["deterministic_evidence"]["candidate_sha256"]:
        raise ValueError("确定性证据未绑定本次实验候选")
    request = next((doc for doc in payload["context_documents"] if doc["document_id"] == "review_request"), None)
    expected_request = f"目标：{payload['review_request']['goal']}\n范围：{payload['review_request']['change']}"
    if request is None or request["owner_ref"] != "requester" or request["body"] != expected_request:
        raise ValueError("请求背景必须与本次目标、范围和请求方一致")
    if len({row["finding_id"] for row in payload["prior_findings"]}) != len(payload["prior_findings"]):
        raise ValueError("历史 finding_id 重复")
    ids = _check_body(payload["experiment_design"]["body"], payload["governing_contract"]["body"])
    if payload["required_check_ids"] != ids:
        raise ValueError("要求的检查项与 governing contract 不一致")
    if any(not payload["review_request"][key].strip() for key in ("goal", "change")):
        raise ValueError("审核目标和范围不能为空")


def validate_output(output: dict, payload: dict, *, module_root=MODULE_ROOT) -> None:
    validate_input(payload, module_root=module_root)
    Draft202012Validator(_schema("output", Path(module_root))).validate(output)
    _nonblank(output)
    rows = output["check_results"]
    if [row["check_id"] for row in rows] != payload["required_check_ids"]:
        raise ValueError("Reviewer 检查项覆盖或顺序错误")
    findings = {f["finding_id"]: f for f in output["findings"]}
    if len(findings) != len(output["findings"]):
        raise ValueError("finding_id 重复")
    actionable = {key for key, f in findings.items() if f["severity"] in {"fix", "block"}}
    cited = set()
    for row in rows:
        refs = set(row["finding_ids"])
        if not refs <= set(findings):
            raise ValueError("检查项引用了不存在的 finding")
        if row["disposition"] == "not_applicable":
            raise ValueError("实验检查不使用 not_applicable，应判断本次适用情形")
        if (row["disposition"] == "finding") != bool(refs & actionable):
            raise ValueError("检查项 disposition 与问题标签不一致")
        if row["disposition"] == "not_run" and (refs or (row["check_id"] != PROSE_CHECK and output["verdict"] != "blocked")):
            raise ValueError("未完成检查的返回不合法")
        cited.update(refs & actionable)
    if cited != actionable:
        raise ValueError("必修问题没有对应检查项")
    candidate = payload["experiment_design"]
    docs = {d["document_id"]: d for d in [candidate, payload["governing_contract"], *payload["context_documents"]]}
    owners = {d["owner_ref"] for d in docs.values()}
    for finding in findings.values():
        if finding["evidence"]["source_ref"] not in docs:
            raise ValueError("finding 引用了未声明材料")
        if finding["accountable_owner_ref"] not in owners:
            raise ValueError("finding 使用了未声明的负责人")
        if finding["severity"] == "fix" and (finding["evidence"]["source_ref"] != candidate["document_id"] or finding["accountable_owner_ref"] != candidate["owner_ref"]):
            raise ValueError("fix 必须指向本次实验候选及其负责人")
        if finding["severity"] in {"fix", "block"} and not any(row["check_id"] == finding["check_id"] and finding["finding_id"] in row["finding_ids"] for row in rows):
            raise ValueError("必修问题未被其所属检查项引用")
    incomplete = any(row["disposition"] != "passed" for row in rows[:-1])
    if incomplete != (rows[-1]["disposition"] == "not_run"):
        raise ValueError("表达检查必须在全部语义检查通过后执行")
    verdict = "blocked" if any(f["severity"] == "block" for f in findings.values()) else "non_pass" if actionable else "passed"
    if output["verdict"] != verdict:
        raise ValueError("整体结论与 findings 不一致")


def _freeze(paths) -> dict:
    result = {}
    for value in paths:
        path = Path(value).absolute()
        resolved, data = _read(path)
        result[path] = (resolved, data)
    return result


def _assert_frozen(snapshot) -> None:
    for path, (resolved, data) in snapshot.items():
        current, raw = _read(path)
        if current != resolved or raw != data:
            raise ValueError(f"审核输入在调用期间发生变化：{path}")


@dataclass(frozen=True)
class _PreparedSnapshot:
    files: dict
    payload_json: str


def _encoded(payload) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def prepare_review(candidate, goal, change, design, contexts=(), prior_findings_path=None, *,
                   candidate_owner_ref="experiment-authoring", module_root=MODULE_ROOT):
    paths = [candidate, design, *(path for _, path in contexts),
             Path(module_root) / "schemas/input.schema.json", Path(module_root) / "schemas/output.schema.json"]
    if prior_findings_path is not None:
        paths.append(prior_findings_path)
    snapshot = _freeze(paths)
    prior = [] if prior_findings_path is None else json.loads(snapshot[Path(prior_findings_path).absolute()][1])
    payload = build_input(candidate, goal, change, design, contexts, prior,
                          candidate_owner_ref=candidate_owner_ref, module_root=module_root)
    documents = [payload["experiment_design"], payload["governing_contract"], *payload["context_documents"][1:]]
    document_paths = [candidate, design, *(path for _, path in contexts)]
    if len(documents) != len(document_paths):
        raise ValueError("构建出的输入与冻结材料数量不同")
    for document, path in zip(documents, document_paths):
        frozen = snapshot[Path(path).absolute()][1]
        if document["body"].encode("utf-8") != frozen or document["sha256"] != _sha(frozen):
            raise ValueError(f"构建出的输入与冻结正文不同：{path}")
    if payload["prior_findings"] != prior:
        raise ValueError("构建出的历史问题与冻结输入不同")
    _assert_frozen(snapshot)
    return payload, _PreparedSnapshot(snapshot, _encoded(payload))


def execute_review(payload, snapshot, executor, *, module_root=MODULE_ROOT) -> dict:
    _assert_frozen(snapshot.files)
    if _encoded(payload) != snapshot.payload_json:
        raise ValueError("发送输入与准备时冻结的完整输入不同")
    validate_input(payload, module_root=module_root)
    result = {}
    try:
        raw = executor(deepcopy(payload))
        if not isinstance(raw, dict):
            result["raw_executor_result"] = raw
            raise ValueError("执行入口没有返回结构化执行记录")
        result = dict(raw)
        _assert_frozen(snapshot.files)
        if result.get("status") != "completed":
            raise ValueError("Reviewer 执行未完成；保留原执行记录")
        ref = result.get("module_release_ref")
        if not isinstance(ref, str) or ref.partition("@")[0] != "runtime-module:experiment_reviewer":
            raise ValueError("执行记录并非 experiment_reviewer")
        validate_output(result.get("output"), payload, module_root=module_root)
        result["output_validation"] = {"status": "passed", "message": None}
    except Exception as exc:
        result.setdefault("status", "execution_failed")
        result["output_validation"] = {"status": "failed", "message": str(exc), "error_type": type(exc).__name__}
    result["semantic_input"] = payload
    result["source_sha256"] = {str(path): _sha(data) for path, (_, data) in snapshot.files.items()}
    return result


def _context_binding(value):
    owner, separator, path = value.partition("=")
    if not separator or not owner.strip() or not path.strip():
        raise argparse.ArgumentTypeError("context 参数使用 OWNER=PATH")
    return owner, Path(path)


def _runtime_review():
    """Load the shared Runtime Test Run binding by path, so this file also runs as a script."""
    name = "portable_runtime_review"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / "runtime_review.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def main(argv=None, *, module_root=MODULE_ROOT) -> int:
    parser = argparse.ArgumentParser(description="实验方案结构检查，及经 Agent Runtime Test Run 的独立 experiment_reviewer 审核")
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--goal")
    parser.add_argument("--change")
    parser.add_argument("--candidate-owner", default="experiment-authoring")
    parser.add_argument("--context", action="append", type=_context_binding, default=[])
    parser.add_argument("--prior-findings", type=Path)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--output", type=Path)
    runtime = _runtime_review()
    runtime.add_runtime_arguments(parser)
    args = parser.parse_args(argv)
    try:
        if args.check_only:
            if args.output is not None:
                raise ValueError("check-only 不写审核结果；省略 --output")
            report = check_experiment(args.candidate, args.design, module_root=module_root)
            print(json.dumps({k: v for k, v in report.items() if not k.endswith("_body")}, ensure_ascii=False))
            return 0
        if not args.goal or not args.change or args.output is None:
            raise ValueError("独立审核需要 --goal、--change 和新的 --output")
        output = args.output.absolute()
        if output.exists() or output.is_symlink() or not output.parent.is_dir():
            raise ValueError("结果必须是已有目录中的新文件，不覆盖候选或已有记录")
        payload, snapshot = prepare_review(args.candidate, args.goal, args.change, args.design,
            args.context, args.prior_findings, candidate_owner_ref=args.candidate_owner, module_root=module_root)
        if output.resolve() in {path for path, _ in snapshot.files.values()}:
            raise ValueError("结果不得替换任何输入")
        fields = runtime.runtime_kwargs(args)
        def executor(payload):
            return runtime.run_review_test(payload, runtime_kwargs=fields)
        _assert_frozen(snapshot.files)
        # 先独占预留输出；同一位置并发调用不会重复进入模型。
        with output.open("x", encoding="utf-8") as stream:
            try:
                result = execute_review(payload, snapshot, executor, module_root=module_root)
            except Exception as exc:
                result = {"status": "input_validation_failed", "semantic_input": payload,
                          "output_validation": {"status": "failed", "message": str(exc), "error_type": type(exc).__name__}}
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        valid = result["output_validation"]["status"] == "passed"
        verdict = result["output"]["verdict"] if valid else None
        print(json.dumps({"execution": result["status"], "output_validation": result["output_validation"],
                          "verdict": verdict, "output": str(output)}, ensure_ascii=False))
        return 0 if valid and verdict == "passed" else 1 if valid else 2
    except Exception as exc:
        print(json.dumps({"error": str(exc), "error_type": type(exc).__name__}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
