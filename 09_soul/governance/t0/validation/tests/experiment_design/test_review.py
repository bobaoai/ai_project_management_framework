from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest
from jsonschema import ValidationError

from tests.runtime_review_real import REAL_GATE, assert_real_review, run_cli


ROOT = Path(__file__).resolve().parents[6]
MODULE = ROOT / "09_soul/governance/skills/experiment-authoring/runtime_modules/experiment_reviewer"
FIXTURES = Path(__file__).with_name("fixtures")
DESIGN = FIXTURES / "design.md"
SPEC = importlib.util.spec_from_file_location("experiment_review", ROOT / "09_soul/governance/t0/validation/experiment_design/review.py")
review = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = review
SPEC.loader.exec_module(review)

BODY = """# 结构单元测试材料

## 1. 验证目标与任务
核对一次只读任务的动作与结果。
## 2. 输入与初始条件
提供明确材料，保留原文件。
## 3. 环境与独立性
### 3.1 项目与规则
提供目标项目的准确入口。
### 3.2 模型与运行配置
由已选配置取得模型信息。
### 3.3 工具与审核入口
使用明确提供的读取与审核函数。
### 3.4 权限与副作用
只读所给文件。
### 3.5 平台通用条件
记录实际提供的通用指令。
### 3.6 启动与核验依据
保留真实初始化证据。
## 4. 预期动作与完成
读取目标、返回核对结果。
## 5. 证据与评价
从实际文件和工具返回判断。
## 6. 复测与比较
这是单次结构用例，不支持模型优劣结论。
"""


@pytest.fixture
def candidate(tmp_path):
    p = tmp_path / "candidate.md"
    p.write_text(BODY)
    return p


@pytest.fixture
def payload(candidate):
    return review.build_input(candidate, "检查实验方案", "本次明确范围", DESIGN)


def good_output():
    return json.loads((FIXTURES / "positive_case.json").read_text())["output"]


def with_finding(payload, severity="fix"):
    result = good_output()
    key = result["check_results"][0]["check_id"]
    result["findings"] = [{"finding_id": "F1", "check_id": key, "severity": severity,
        "evidence": {"source_ref": "experiment_design", "locator": "§1", "observation": "示例证据"},
        "requirement": "任务目标", "impact": "示例影响", "required_change": "明确结果",
        "accountable_owner_ref": payload["experiment_design"]["owner_ref"]}]
    result["check_results"][0]["finding_ids"] = ["F1"]
    if severity != "note":
        result["check_results"][0]["disposition"] = "finding"
        result["check_results"][-1]["disposition"] = "not_run"
        result["verdict"] = "blocked" if severity == "block" else "non_pass"
    return result


def test_structure_and_input_use_exact_design(candidate, payload):
    report = review.check_experiment(candidate, DESIGN)
    assert report["candidate_body"] == BODY
    assert report["candidate_sha256"] == hashlib.sha256(candidate.read_bytes()).hexdigest()
    assert report["required_check_ids"] == payload["required_check_ids"]
    assert payload["required_check_ids"][-1] == "prose_and_meaning_preservation"
    assert payload["context_documents"][0]["document_id"] == "review_request"
    review.validate_input(payload)


@pytest.mark.parametrize("number", range(1, 7))
def test_every_required_section_is_required(candidate, number):
    heading = next(x for x in BODY.splitlines() if x.startswith(f"## {number}."))
    candidate.write_text(BODY.replace(heading, heading.replace("##", "#", 1)))
    with pytest.raises(ValueError, match="六个部分"):
        review.check_experiment(candidate, DESIGN)


@pytest.mark.parametrize("number", range(1, 7))
def test_every_environment_subsection_is_required(candidate, number):
    heading = next(x for x in BODY.splitlines() if x.startswith(f"### 3.{number} "))
    candidate.write_text(BODY.replace(heading, heading.replace("###", "####", 1)))
    with pytest.raises(ValueError, match="六个小节"):
        review.check_experiment(candidate, DESIGN)


@pytest.mark.parametrize("kind", ["duplicate", "reorder", "code_only_heading", "comment_heading"])
def test_false_or_wrong_top_level_structure(candidate, kind):
    if kind == "duplicate":
        body = BODY + "\n## 6. 复测与比较\n重复。\n"
    elif kind == "reorder":
        body = BODY.replace("## 1. 验证目标与任务", "## 2. 输入与初始条件", 1).replace("## 2. 输入与初始条件\n提供", "## 1. 验证目标与任务\n提供")
    elif kind == "code_only_heading":
        body = BODY.replace("## 1. 验证目标与任务", "```md\n## 1. 验证目标与任务\n```", 1)
    else:
        body = BODY.replace("## 1. 验证目标与任务", "<!--\n## 1. 验证目标与任务\n-->", 1)
    candidate.write_text(body)
    with pytest.raises(ValueError):
        review.check_experiment(candidate, DESIGN)


def test_code_counts_as_content_but_not_headings(candidate):
    body = BODY.replace("提供明确材料，保留原文件。", "````md\n## 7. 数据中的标题\n```\n````")
    candidate.write_text(body)
    assert review.check_experiment(candidate, DESIGN)["candidate_body"] == body


@pytest.mark.parametrize("text", ["\n```\n", "\n<!--未闭合"])
def test_bad_text_structure(candidate, text):
    candidate.write_bytes((BODY + text).encode())
    with pytest.raises(ValueError):
        review.check_experiment(candidate, DESIGN)


def test_empty_section_body(candidate):
    candidate.write_text(BODY.replace("核对一次只读任务的动作与结果。", "<!-- 空正文 -->"))
    with pytest.raises(ValueError, match="章节缺少内容"):
        review.check_experiment(candidate, DESIGN)


def test_empty_environment_body(candidate):
    candidate.write_text(BODY.replace("只读所给文件。", ""))
    with pytest.raises(ValueError, match="环境小节缺少"):
        review.check_experiment(candidate, DESIGN)


@pytest.mark.parametrize("kind", ["duplicate", "reorder", "wrong_parent", "fenced"])
def test_environment_order_and_parent_are_checked(candidate, kind):
    heading = "### 3.2 模型与运行配置"
    if kind == "duplicate": body = BODY.replace(heading, heading + "\n重复内容\n" + heading)
    elif kind == "reorder": body = BODY.replace("### 3.1 项目与规则", heading, 1).replace(heading + "\n由已选", "### 3.1 项目与规则\n由已选", 1)
    elif kind == "wrong_parent": body = BODY.replace(heading, "### 4.2 模型与运行配置")
    else: body = BODY.replace(heading, "```md\n" + heading + "\n```")
    candidate.write_text(body)
    with pytest.raises(ValueError, match="六个小节"):
        review.check_experiment(candidate, DESIGN)


@pytest.mark.parametrize("number", range(1, 7))
def test_environment_heading_cannot_repeat_outside_its_parent(candidate, number):
    heading = next(x for x in BODY.splitlines() if x.startswith(f"### 3.{number} "))
    candidate.write_text(BODY + "\n" + heading + "\n放在错误位置的填写内容。\n")
    with pytest.raises(ValueError, match="跨章节重复"):
        review.check_experiment(candidate, DESIGN)


def test_fenced_environment_example_outside_parent_is_data(candidate):
    candidate.write_text(BODY + "\n```md\n### 3.1 项目与规则\n数据示例\n```\n")
    review.check_experiment(candidate, DESIGN)


def test_crlf_candidate_and_context_preserve_exact_bytes(candidate, tmp_path):
    raw = BODY.replace("\n", "\r\n").encode()
    candidate.write_bytes(raw)
    context = tmp_path / "basis.md"
    context.write_bytes("任务依据\r\n下一行\r\n".encode())
    value = review.build_input(candidate, "目标", "范围", DESIGN, [("task_owner", context)])
    assert value["experiment_design"]["body"].encode() == raw
    assert value["experiment_design"]["sha256"] == hashlib.sha256(raw).hexdigest()
    assert value["context_documents"][1]["body"].encode() == context.read_bytes()
    review.validate_output(good_output(), value)


def test_changed_design_is_not_silently_accepted(candidate, tmp_path):
    d = tmp_path / "other_design.md"
    d.write_bytes(DESIGN.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="绑定的版本"):
        review.check_experiment(candidate, d)


def test_missing_and_untraversable_inputs(candidate, tmp_path):
    for p in [tmp_path / "missing.md", tmp_path, tmp_path / "missing/../candidate.md", candidate / "../candidate.md"]:
        with pytest.raises((ValueError, OSError)):
            review.check_experiment(p, DESIGN)
    link = tmp_path / "link.md"
    link.symlink_to(candidate)
    with pytest.raises(ValueError, match="普通文件"):
        review.check_experiment(link, DESIGN)


def test_invalid_utf8(candidate):
    candidate.write_bytes(b"\xff")
    with pytest.raises(UnicodeDecodeError):
        review.check_experiment(candidate, DESIGN)


def test_duplicate_source_and_input_identity(candidate, payload):
    with pytest.raises(ValueError, match="声明材料重复"):
        review.build_input(candidate, "目标", "范围", DESIGN, [("owner", candidate)])
    duplicate = deepcopy(payload)
    duplicate["context_documents"][0]["document_id"] = duplicate["experiment_design"]["document_id"]
    with pytest.raises(ValueError, match="document_id"):
        review.validate_input(duplicate)


@pytest.mark.parametrize("mutation", ["body_hash", "evidence_hash", "check_ids", "wrong_version", "blank_goal"])
def test_input_binding_failures(payload, mutation):
    if mutation == "body_hash":
        payload["experiment_design"]["body"] += "\n"
    elif mutation == "evidence_hash":
        payload["deterministic_evidence"]["candidate_sha256"] = "0" * 64
    elif mutation == "check_ids":
        payload["required_check_ids"].reverse()
    elif mutation == "wrong_version":
        payload.update(json.loads((FIXTURES / "schema_drift_case.json").read_text())["input_patch"])
    else:
        payload["review_request"]["goal"] = " "
    with pytest.raises((ValueError, ValidationError)):
        review.validate_input(payload)


def test_common_format_fixture(payload):
    review.validate_output(good_output(), payload)
    bad = json.loads((FIXTURES / "negative_extra_field_case.json").read_text())["output"]
    with pytest.raises(ValidationError):
        review.validate_output(bad, payload)


@pytest.mark.parametrize("severity", ["note", "fix", "block"])
def test_valid_conclusions_and_shared_finding(payload, severity):
    output = with_finding(payload, severity)
    review.validate_output(output, payload)
    output["check_results"][1]["finding_ids"] = ["F1"]
    if severity != "note":
        output["check_results"][1]["disposition"] = "finding"
    review.validate_output(output, payload)


@pytest.mark.parametrize("mutation", ["missing_check", "duplicate_check", "wrong_order", "dangling", "duplicate_finding", "background_fix", "wrong_owner", "uncovered", "false_pass", "early_prose", "unknown_source", "not_applicable"])
def test_invalid_outputs_are_rejected(payload, mutation):
    output = with_finding(payload)
    if mutation == "missing_check": output["check_results"].pop()
    elif mutation == "duplicate_check": output["check_results"][1] = deepcopy(output["check_results"][0])
    elif mutation == "wrong_order": output["check_results"].reverse()
    elif mutation == "dangling": output["check_results"][0]["finding_ids"] = ["missing"]
    elif mutation == "duplicate_finding": output["findings"].append(deepcopy(output["findings"][0]))
    elif mutation == "background_fix": output["findings"][0]["evidence"]["source_ref"] = "experiment_contract"
    elif mutation == "wrong_owner": output["findings"][0]["accountable_owner_ref"] = "unknown_owner"
    elif mutation == "uncovered": output["check_results"][0].update(disposition="passed", finding_ids=[])
    elif mutation == "false_pass": output["verdict"] = "passed"
    elif mutation == "early_prose": output["check_results"][-1]["disposition"] = "passed"
    elif mutation == "unknown_source": output["findings"][0]["evidence"]["source_ref"] = "undeclared"
    else: output["check_results"][1]["disposition"] = "not_applicable"
    with pytest.raises((ValueError, ValidationError)):
        review.validate_output(output, payload)


def test_block_can_route_to_declared_requester(payload):
    output = with_finding(payload, "block")
    output["findings"][0].update(accountable_owner_ref="requester")
    output["findings"][0]["evidence"]["source_ref"] = "review_request"
    output["check_results"][1]["disposition"] = "not_run"
    review.validate_output(output, payload)


def test_request_context_cannot_claim_a_different_authorization(payload):
    request = payload["context_documents"][0]
    request["body"] = "声称其他目标已经授权"
    request["sha256"] = hashlib.sha256(request["body"].encode()).hexdigest()
    with pytest.raises(ValueError, match="请求背景"):
        review.validate_input(payload)


def test_duplicate_prior_finding_is_rejected(payload):
    payload["prior_findings"] = [{"finding_id": "F1", "body": "历史问题"}] * 2
    with pytest.raises(ValueError, match="历史 finding_id"):
        review.validate_input(payload)


def test_blank_assessment_is_rejected(payload):
    output = good_output()
    output["check_results"][0]["assessment"] = " \n "
    with pytest.raises(ValueError, match="空白"):
        review.validate_output(output, payload)


def test_schema_compiles_through_public_module_reviewer_without_execution():
    from agent_runtime import ModuleReviewer
    from agent_runtime.registry import (
        ModuleRegistrationSource, BehaviorPolicyReleaseCandidate, EvaluationPolicyReleaseCandidate,
        RetryPolicyReleaseCandidate, compile_behavior_policy_release,
        compile_evaluation_policy_release, compile_retry_policy_release,
    )
    from agent_runtime.contracts.registry_release_definition import ModuleEntryPolicy, OutputResolutionPolicy

    registration = json.loads((MODULE / "module_registration.json").read_text())
    authority = DESIGN.read_text()
    source = ModuleRegistrationSource(
        skill_id=registration["skill_id"], module_id=registration["module_id"],
        owner_contract_ref="owner-contract-sha256:" + hashlib.sha256(authority.encode()).hexdigest(),
        owner_contract_content=authority,
        input_schema_ref=registration["input_schema_ref"],
        input_schema_document=(MODULE / "schemas/input.schema.json").read_text(),
        output_schema_ref=registration["output_schema_ref"],
        output_schema_document=(MODULE / "schemas/output.schema.json").read_text(),
        instruction_text="格式编译测试替身；不执行模型。",
        declared_operation_ids=tuple(registration["declared_operation_ids"]),
        compatible_transport_kinds=tuple(registration["compatible_transport_kinds"]),
        behavior_policy_ref=registration["behavior_policy_ref"],
        evaluation_policy_ref=registration["evaluation_policy_ref"],
        retry_policy_ref=registration["retry_policy_ref"],
        entry_policy=ModuleEntryPolicy.STANDALONE_ALLOWED,
        output_resolution_policy=OutputResolutionPolicy.EVALUATED_SINGLE,
    )
    exported = ModuleReviewer(source).export(
        module_version="v1",
        behavior_policy=compile_behavior_policy_release(BehaviorPolicyReleaseCandidate(
            policy_id="workflow_execution_isolated", policy_version="v1", context_isolation="workflow_execution_isolated")),
        evaluation_policy=compile_evaluation_policy_release(EvaluationPolicyReleaseCandidate(
            policy_id="module_candidate", policy_version="v1", evaluation_mode="module_candidate")),
        retry_policy=compile_retry_policy_release(RetryPolicyReleaseCandidate(
            policy_id="bounded_candidate", policy_version="v1", max_attempts=3)),
        execution_profile=None,
    )
    assert exported.module_release.module_id == "experiment_reviewer"
    assert exported.execution_profile is None


def runtime_result(output=None):
    return {"status": "completed", "module_release_ref": "runtime-module:experiment_reviewer@v1",
            "workflow_execution_id": "execution_fixture", "output": good_output() if output is None else output}


def test_review_records_exact_input_and_does_not_modify_source(candidate):
    payload, snapshot = review.prepare_review(candidate, "目标", "范围", DESIGN)
    before = candidate.read_bytes()
    def executor(value):
        assert value == payload
        value["review_request"]["goal"] = "执行器对自己副本的修改"
        return runtime_result()
    result = review.execute_review(payload, snapshot, executor)
    assert result["output_validation"]["status"] == "passed"
    assert result["semantic_input"]["review_request"]["goal"] == "目标"
    assert candidate.read_bytes() == before


@pytest.mark.parametrize("kind", ["exception", "no_record", "failed", "wrong_module", "bad_output"])
def test_execution_failures_have_no_valid_verdict(candidate, kind):
    payload, snapshot = review.prepare_review(candidate, "目标", "范围", DESIGN)
    def executor(_):
        if kind == "exception": raise TimeoutError("Provider 超时")
        if kind == "no_record": return "invalid"
        if kind == "failed": return {"status": "failed", "failure_class": "provider_unavailable"}
        if kind == "wrong_module": return {**runtime_result(), "module_release_ref": "runtime-module:other@v1"}
        return runtime_result({})
    result = review.execute_review(payload, snapshot, executor)
    assert result["output_validation"]["status"] == "failed"
    if kind == "failed": assert result["failure_class"] == "provider_unavailable"
    if kind == "no_record": assert result["raw_executor_result"] == "invalid"


def test_input_change_before_call_prevents_execution(candidate):
    payload, snapshot = review.prepare_review(candidate, "目标", "范围", DESIGN)
    candidate.write_text(BODY + "修改")
    called = []
    with pytest.raises(ValueError, match="发生变化"):
        review.execute_review(payload, snapshot, lambda value: called.append(value))
    assert called == []


def test_payload_changed_after_preparation_prevents_execution(candidate):
    payload, snapshot = review.prepare_review(candidate, "目标", "范围", DESIGN)
    payload["experiment_design"]["body"] += "\n"
    payload["experiment_design"]["sha256"] = hashlib.sha256(payload["experiment_design"]["body"].encode()).hexdigest()
    payload["deterministic_evidence"]["candidate_sha256"] = payload["experiment_design"]["sha256"]
    called = []
    with pytest.raises(ValueError, match="冻结的完整输入"):
        review.execute_review(payload, snapshot, lambda value: called.append(value))
    assert called == []


def test_change_during_build_and_restore_is_rejected(candidate, monkeypatch):
    original = review.build_input
    initial = candidate.read_bytes()
    def changed_input(*args, **kwargs):
        candidate.write_bytes(initial + b"\n")
        try:
            return original(*args, **kwargs)
        finally:
            candidate.write_bytes(initial)
    monkeypatch.setattr(review, "build_input", changed_input)
    with pytest.raises(ValueError, match="冻结正文不同"):
        review.prepare_review(candidate, "目标", "范围", DESIGN)
    assert candidate.read_bytes() == initial


def test_input_change_during_call_preserves_raw_result(candidate):
    payload, snapshot = review.prepare_review(candidate, "目标", "范围", DESIGN)
    def executor(_):
        candidate.write_text(BODY + "修改")
        return runtime_result()
    result = review.execute_review(payload, snapshot, executor)
    assert result["output"]["verdict"] == "passed"
    assert result["workflow_execution_id"] == "execution_fixture"
    assert result["output_validation"]["status"] == "failed"
    assert result["semantic_input"]["experiment_design"]["body"] == BODY


def test_malformed_prior_json_is_rejected_before_call(candidate, tmp_path):
    path = tmp_path / "prior.json"
    path.write_text("{")
    with pytest.raises(json.JSONDecodeError):
        review.prepare_review(candidate, "目标", "范围", DESIGN, prior_findings_path=path)


def test_cli_check_only_does_not_need_executor(candidate, capsys):
    assert review.main(["--candidate", str(candidate), "--design", str(DESIGN), "--check-only"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert "candidate_body" not in output
    assert output["candidate_sha256"] == hashlib.sha256(candidate.read_bytes()).hexdigest()


@pytest.mark.deterministic
@pytest.mark.parametrize("target_kind", ["existing_result", "candidate", "symlink", "hardlink"])
def test_cli_output_refusal_never_reaches_runtime(candidate, tmp_path, monkeypatch, target_kind):
    import agent_runtime
    monkeypatch.setattr(agent_runtime, "run_local_workflow_test", lambda **kw: pytest.fail("no Runtime call"), raising=False)
    output = tmp_path / "result.json"
    if target_kind == "candidate": output = candidate
    elif target_kind == "symlink": output.symlink_to(candidate)
    elif target_kind == "hardlink": output.hardlink_to(candidate)
    else: output.write_text("原结果")
    before = output.read_bytes()
    code = review.main(["--candidate", str(candidate), "--design", str(DESIGN), "--goal", "目标",
        "--change", "范围", "--output", str(output), "--root", str(tmp_path / "root")])
    assert code == 2 and output.read_bytes() == before and not (tmp_path / "root").exists()


@pytest.mark.real_run
@REAL_GATE
def test_real_cli_exit_code_follows_the_saved_record(candidate, tmp_path, reviewer_host):
    """Real entry: this CLI as a process, the Reviewer registered from this checkout, Runtime Test Run and Claude CLI.

    Retired executor variables are set and ignored. The exit code is 0 for a
    valid passed result and 1 for another valid verdict.
    """
    target = tmp_path / "result.json"
    process = run_cli(SPEC.origin, "--candidate", candidate, "--design", DESIGN, "--goal", "目标", "--change", "范围",
                      "--output", target, "--root", reviewer_host)
    saved = json.loads(target.read_text())
    verdict = assert_real_review(saved, "experiment_reviewer", json.loads(process.stdout), record_key="output_validation")
    assert process.returncode == (0 if verdict == "passed" else 1), process.stderr
    assert saved["semantic_input"]["experiment_design"]["body"] == BODY


@pytest.mark.real_run
@REAL_GATE
def test_real_runtime_failure_is_saved_as_a_failure(candidate, tmp_path):
    """Real entry: Runtime Test Run on a root where experiment_reviewer is not registered; no Provider is reached."""
    target = tmp_path / "failed.json"
    process = run_cli(SPEC.origin, "--candidate", candidate, "--design", DESIGN, "--goal", "目标", "--change", "范围",
                      "--output", target, "--root", tmp_path / "empty_root")
    assert process.returncode == 2, process.stderr
    saved = json.loads(target.read_text())
    assert saved["output_validation"]["error_type"] == "FileNotFoundError"
    assert "No registered workflow: experiment_reviewer" in saved["output_validation"]["message"]
    assert "output" not in saved


@pytest.mark.deterministic
def test_cli_rejects_the_retired_executor_argument(candidate, tmp_path, capsys):
    with pytest.raises(SystemExit) as error:
        review.main(["--candidate", str(candidate), "--design", str(DESIGN), "--root", str(tmp_path),
                     "--executor", "module:function"])
    assert error.value.code == 2 and "--executor" in capsys.readouterr().err
