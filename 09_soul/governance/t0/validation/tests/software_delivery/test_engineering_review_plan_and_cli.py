from __future__ import annotations

import hashlib
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from jsonschema import Draft202012Validator, ValidationError

from software_delivery import engineering_review_input as inputs
from software_delivery.engineering_review import prepare_review, review_engineering
from software_delivery.engineering_review_output import EngineeringReviewOutputError, validate_engineering_review_output
from tests.runtime_review_real import REAL_GATE, assert_real_review, run_cli

CLI = Path(inputs.__file__).with_name("engineering_review.py")


def output():
    return {"verdict":"passed", "check_results":[
                {"check_id":str(i), "disposition":"passed", "assessment":"Evidence supports the requirement",
                 "finding_ids":[]} for i in range(1, 10)],
            "findings":[], "safe_next_step":"Return to the owner"}


def plan_input(**changes):
    values = dict(code_design_basis=inputs.hashed_body("plan", "A complete engineering plan"),
                  sandbox_command_plan=inputs.command_plan("commands", []), acceptance_criteria=["Expected result"])
    values.update(changes)
    return inputs.build_code_design_review_input(**values)


def plan_record():
    return {"status":"completed", "module_id":"engineering_change_reviewer", "review_purpose":"code_design",
            "semantic_input":plan_input(), "output":output(), "semantic_validation":{"status":"passed"}}


def plan_review_evidence(record=None):
    """The complete plan review a caller keeps; the input builder accepts only this form."""
    return inputs.hashed_body("review", json.dumps(plan_record() if record is None else record))


def implementation(tmp_path, **changes):
    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True).stdout.strip()
    git("init", "-q")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Test")
    (tmp_path/"code.py").write_text("x = 1\n")
    git("add", "code.py")
    git("commit", "-qm", "base")
    (tmp_path/"code.py").write_text("x = 2\n")
    git("add", "code.py")
    git("commit", "-qm", "change")
    values = dict(repository_root=tmp_path, commit_ref="HEAD",
        code_design_basis=plan_input()["code_design_basis"],
        code_design_review=plan_review_evidence(),
        sandbox_command_plan=inputs.command_plan("commands", []), acceptance_criteria=["Expected result"])
    values.update(changes)
    return inputs.build_engineering_review_input(**values)


def test_plan_needs_no_git_or_system_change(monkeypatch):
    monkeypatch.setattr(inputs, "_run_git", lambda *a: pytest.fail("Plan must not resolve Git"))
    payload = plan_input()
    assert payload["subject"] is None and payload["system_change_plan_step"] is None
    assert payload["code_design_review"] is None
    assert payload["review_purpose"] == "code_design"
    assert payload["code_design_basis"]["body"] == "A complete engineering plan"


@pytest.mark.parametrize("mutation", ["missing", "blank", "hash", "command_hash", "duplicate_context", "duplicate_command"])
def test_invalid_plan_input_fails(mutation):
    kwargs = {}
    if mutation == "missing": kwargs["code_design_basis"] = None
    if mutation == "blank": kwargs["code_design_basis"] = {"ref":"p", "body":" ", "sha256":"0"*64}
    if mutation == "hash": kwargs["code_design_basis"] = {**plan_input()["code_design_basis"], "sha256":"0"*64}
    if mutation == "command_hash": kwargs["sandbox_command_plan"] = {**inputs.command_plan("c", []), "sha256":"0"*64}
    if mutation == "duplicate_context": kwargs["context_documents"] = [inputs.hashed_body("c", "a"), inputs.hashed_body("c", "b")]
    if mutation == "duplicate_command": kwargs["sandbox_command_plan"] = inputs.command_plan("c", [command(), command()])
    with pytest.raises(inputs.EngineeringReviewInputError): plan_input(**kwargs)


def test_implementation_requires_reviewed_plan_but_not_system_change(tmp_path):
    payload = implementation(tmp_path)
    assert payload["review_purpose"] == "implementation" and payload["subject"]["commit_ref"]
    assert payload["system_change_plan_step"] is None


@pytest.mark.parametrize("mutation", ["missing", "purpose", "source_purpose", "module", "conflicting_release", "source_module", "failed", "validation", "other_plan", "criteria", "verdict", "hash", "malformed"])
def test_implementation_rejects_wrong_plan_evidence(tmp_path, mutation):
    record = plan_record()
    if mutation == "purpose": record["review_purpose"] = "implementation"
    if mutation == "source_purpose": record["semantic_input"]["review_purpose"] = "implementation"
    if mutation == "module": record["module_id"] = "other_reviewer"
    if mutation == "conflicting_release": record["module_release_ref"] = "runtime-module:design_contract_reviewer@v1"
    if mutation == "source_module": record["semantic_input"]["module_id"] = "other_reviewer"
    if mutation == "failed": record["status"] = "failed"
    if mutation == "validation": record["semantic_validation"]["status"] = "failed"
    if mutation == "other_plan": record["semantic_input"]["code_design_basis"] = inputs.hashed_body("other", "Another plan")
    if mutation == "criteria": record["semantic_input"]["acceptance_criteria"] = ["Another result"]
    if mutation == "verdict": record["output"]["verdict"] = "non_pass"
    wrapped = inputs.hashed_body("review", "not JSON" if mutation == "malformed" else json.dumps(record))
    if mutation == "hash": wrapped["sha256"] = "0"*64
    with pytest.raises(inputs.EngineeringReviewInputError):
        implementation(tmp_path, code_design_review=None if mutation == "missing" else wrapped)


def test_schema_does_not_mix_plan_and_commit():
    schema = json.loads(inputs.INPUT_SCHEMA_PATH.read_text())
    validator = Draft202012Validator(schema)
    payload = plan_input()
    validator.validate(payload)
    payload["review_purpose"] = "implementation"
    with pytest.raises(ValidationError): validator.validate(payload)


def command(required=True):
    return {"command_id":"unit", "argv":["python", "-m", "pytest"], "cwd":"/declared",
            "timeout_seconds":60, "network_policy":"denied", "expected_result":"passed", "required":required}


def with_finding(result, severity="fix", check="7", source="plan"):
    result = copy.deepcopy(result)
    result["verdict"] = {"fix": "non_pass", "block": "blocked", "note": "passed"}[severity]
    result["findings"] = [{
        "finding_id": "finding_1", "severity": severity,
        "evidence": {"source_ref": source, "locator": "§1", "observation": "Exact evidence"},
        "requirement": "Declared result", "impact": "Impact on intended result",
        "accountable_owner_ref": "owner", "required_change": "Restore the declared result",
    }]
    row = next(row for row in result["check_results"] if row["check_id"] == check)
    row.update(disposition="passed" if severity == "note" else "finding", finding_ids=["finding_1"])
    if severity != "note" and check != "8":
        result["check_results"][7].update(disposition="not_run", assessment="Await semantic closure")
    return result


def command_record(payload, *, returncode=0, unavailable=False):
    """Test double for the Runtime-owned CLI log returned by an explicit executor."""
    request = {"command_id": "unit"}
    response = (
        {"error_type": "PermissionError", "message": "Isolation unavailable"} if unavailable else
        {"command_id": "unit", "allowed": True, "returncode": returncode, "stdout": "Test output", "stderr": ""}
    )
    return executor(payload) | {
        "managed_runtime": False,
        "execution_log": {"schema_version": "runtime_cli_log_v1", "complete": True, "tool_calls": [{
            "tool_call_id": "call_1", "tool_name": "sandbox_command_execute",
            "request": request, "response": response,
            "status": "failed" if unavailable else "completed",
        }]},
    }


@pytest.mark.parametrize("mutation", [
    "missing", "duplicate", "failed_required", "unknown", "incomplete_log", "wrong_log_version",
    "wrong_input", "wrong_purpose", "wrong_identity", "blocked_without_finding",
    "missing_response", "bad_returncode", "mismatched_command", "invalid_status", "model_gate", "false_managed",
])
def test_result_contract_rejects_false_pass(mutation):
    payload = plan_input(sandbox_command_plan=inputs.command_plan("c", [command()]))
    result = output()
    record = command_record(payload)
    observation = record["execution_log"]["tool_calls"][0]
    if mutation == "missing": record["execution_log"]["tool_calls"] = []
    if mutation == "duplicate": record["execution_log"]["tool_calls"] *= 2
    if mutation == "failed_required": record = command_record(payload, returncode=1)
    if mutation == "incomplete_log": record["execution_log"]["complete"] = False
    if mutation == "wrong_log_version": record["execution_log"]["schema_version"] = "unknown"
    if mutation == "missing_response": observation.pop("response")
    if mutation == "false_managed": record["managed_runtime"] = True
    if mutation == "wrong_input": record["semantic_input"]["acceptance_criteria"] = ["Another result"]
    if mutation == "wrong_purpose": record["review_purpose"] = "implementation"
    if mutation == "wrong_identity": record["module_id"] = "other_reviewer"
    if mutation == "invalid_status": observation["status"] = "unknown"
    if mutation == "blocked_without_finding": result["verdict"] = "blocked"
    if mutation == "model_gate":
        result["gate_results"] = [{"command_id": "unit", "disposition": "passed"}]
    if mutation in {"unknown", "bad_returncode", "mismatched_command"}:
        body = observation["request" if mutation == "unknown" else "response"]
        if mutation == "unknown": body["command_id"] = "unknown"
        if mutation == "bad_returncode": body["returncode"] = False
        if mutation == "mismatched_command": body["command_id"] = "other"
    with pytest.raises(EngineeringReviewOutputError):
        validate_engineering_review_output(result, review_input=payload, execution_record=record)


def test_optional_probe_does_not_become_required_gate():
    payload = plan_input(sandbox_command_plan=inputs.command_plan("c", [command(False)]))
    validate_engineering_review_output(output(), review_input=payload)
    # Its failure also does not promote it into a required gate.
    validate_engineering_review_output(output(), review_input=payload,
                                       execution_record=command_record(payload, returncode=1))


@pytest.mark.parametrize("returncode,verdict", [(0, "passed"), (1, "non_pass"), (1, "blocked")])
def test_actual_command_evidence_supports_the_result(returncode, verdict):
    payload = plan_input(sandbox_command_plan=inputs.command_plan("c", [command()]))
    result = output() if verdict == "passed" else with_finding(
        output(), severity="fix" if verdict == "non_pass" else "block")
    validate_engineering_review_output(result, review_input=payload,
                                       execution_record=command_record(payload, returncode=returncode))


def options(tmp_path):
    plan = tmp_path/"plan.md"
    plan.write_text("A complete engineering plan\n")
    return dict(plan_path=plan, goal="Expected result", change="Bounded change", acceptance_criteria=["Expected result"])


def executor(payload):
    return {"status":"completed", "module_id":"engineering_change_reviewer", "output":output(), "execution":"test_fixture",
            "review_purpose":payload.get("review_purpose","code_design"), "semantic_input":copy.deepcopy(payload)}


@pytest.mark.parametrize("mutation", ["plan", "context", "input", "purpose", "identity", "output", "failure"])
def test_runtime_record_and_frozen_input_are_checked(tmp_path, mutation):
    opts = options(tmp_path)
    context = tmp_path/"context.md"; context.write_text("Context")
    opts["context_paths"] = [context]
    def altered(payload):
        result = executor(payload)
        if mutation == "plan": opts["plan_path"].write_text("changed")
        if mutation == "context": context.write_text("changed")
        if mutation == "input": payload["acceptance_criteria"] = ["changed"]
        if mutation == "purpose": result["review_purpose"] = "implementation"
        if mutation == "identity": result["module_id"] = "other"
        if mutation == "output": result["output"] = {}
        if mutation == "failure": result["status"] = "failed"; result["output"] = None
        return result
    record = review_engineering(executor=altered, **opts)
    assert record["semantic_validation"]["status"] != "passed"
    assert record["semantic_input"]["acceptance_criteria"] == ["Expected result"]
    if mutation == "identity": assert record["module_id"] == "other"


def test_review_plan_is_read_only_and_self_contained(tmp_path):
    opts = options(tmp_path); before = opts["plan_path"].read_bytes()
    record = review_engineering(executor=executor, **opts)
    assert record["semantic_validation"]["status"] == "passed"
    assert record["review_purpose"] == "code_design"
    assert opts["plan_path"].read_bytes() == before
    assert record["semantic_input"]["context_documents"][0]["ref"] == "user_request"


@pytest.mark.deterministic
def test_cli_check_and_failure_paths(tmp_path):
    opts = options(tmp_path)
    cmd = [sys.executable, "-B", str(CLI), "--plan", str(opts["plan_path"]), "--goal", "Expected result",
           "--change", "Bounded change", "--criterion", "Expected result"]
    env = {k:v for k,v in os.environ.items() if k not in ("ENGINEERING_REVIEW_EXECUTOR", "PYTHONPATH")}
    checked = subprocess.run([*cmd,"--check-only"],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert checked.returncode == 0, checked.stderr
    assert json.loads(checked.stdout)["subject"] is None
    failed = subprocess.run(cmd,cwd=tmp_path,env=env,text=True,capture_output=True)
    assert failed.returncode == 2 and "review requires --output" in failed.stderr
    missing_root = subprocess.run([*cmd,"--output",str(tmp_path/"new.json")],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert missing_root.returncode == 2 and "running a review requires --root" in missing_root.stderr
    target=tmp_path/"result.json"; target.write_text("preserve")
    failed = subprocess.run([*cmd,"--root",str(tmp_path),"--output",str(target)],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert failed.returncode == 2 and target.read_text() == "preserve"
    retired = subprocess.run([*cmd,"--executor","missing:run","--output",str(tmp_path/"other.json")],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert retired.returncode == 2 and "--executor" in retired.stderr


def _cli_review(opts, target, root, *extra):
    return ["--plan", opts["plan_path"], "--goal", "Expected result", "--change", "Bounded change",
            "--criterion", "Expected result", "--output", target, "--root", root, *extra]


@pytest.mark.real_run
@REAL_GATE
def test_real_cli_plan_review_runs_through_runtime(tmp_path, reviewer_host):
    """Real entry: this CLI as a process, the Reviewer registered from this checkout, Runtime Test Run and Claude CLI.

    Retired executor variables are set and ignored.
    """
    opts = options(tmp_path)
    target = tmp_path / "result.json"
    result = run_cli(CLI, *_cli_review(opts, target, reviewer_host))
    record = json.loads(target.read_text())
    verdict = assert_real_review(record, "engineering_change_reviewer", json.loads(result.stdout))
    assert result.returncode == (0 if verdict == "passed" else 1), result.stderr
    assert record["review_purpose"] == "code_design" and record["semantic_input"]["subject"] is None


@pytest.mark.real_run
@REAL_GATE
def test_real_declared_command_evidence_reaches_the_validator_from_the_same_run(tmp_path, reviewer_host):
    """Real entry: the Runtime executes the declared command through its local command tool during a real review.

    The command is declared once (--commands); the Engineering entry makes it
    both part of the Reviewer input and a Runtime command. The owning validator
    accepts the record from that run; the same record without its command call,
    or bound to another Attempt, is rejected.
    """
    opts = options(tmp_path)
    opts["plan_path"].write_text("# Unit check plan\n\nThe declared command `unit_check` runs `/bin/echo evidence`"
                                 " and exits 0. Acceptance: the command runs in the review and exits 0.\n")
    argv = ["/bin/echo", "evidence"]
    commands = tmp_path / "commands.json"
    commands.write_text(json.dumps([{"command_id": "unit_check", "argv": argv, "cwd": "scratch", "timeout_seconds": 60,
                                     "network_policy": "denied", "expected_result": "passed", "required": True}]))
    target = tmp_path / "result.json"
    result = run_cli(CLI, "--plan", opts["plan_path"], "--goal", "Keep the unit check green",
                     "--change", "Plan for one unit check", "--criterion", "The declared unit_check command runs and exits 0",
                     "--commands", commands, "--output", target, "--root", reviewer_host)
    record = json.loads(target.read_text())
    assert_real_review(record, "engineering_change_reviewer", json.loads(result.stdout))
    attempt, = (row for row in record["execution_log"]["attempts"] if row["attempt_id"] == record["attempt_id"])
    call, = (row for row in attempt["tool_calls"] if row["tool_name"] == "sandbox_command_execute")
    assert call["request"] == {"command_id": "unit_check"} and call["status"] == "completed"
    assert (call["response"]["returncode"], call["response"]["stdout"], call["response"]["declared_argv"]) == (
        0, "evidence\n", argv)
    arguments = dict(review_input=record["semantic_input"], execution_record=record)
    validate_engineering_review_output(record["output"], **arguments)
    without_call = copy.deepcopy(record)
    for row in without_call["execution_log"]["attempts"]:
        row["tool_calls"] = [item for item in row["tool_calls"] if item["tool_name"] != "sandbox_command_execute"]
    with pytest.raises(EngineeringReviewOutputError, match="no actual execution evidence"):
        validate_engineering_review_output(record["output"], review_input=record["semantic_input"],
                                           execution_record=without_call)
    other_attempt = copy.deepcopy(record) | {"attempt_id": "module_attempt_other"}
    with pytest.raises(EngineeringReviewOutputError, match="another review Attempt"):
        validate_engineering_review_output(record["output"], review_input=record["semantic_input"],
                                           execution_record=other_attempt)


def test_plan_self_check_template_and_validation(tmp_path):
    opts=options(tmp_path)
    template=tmp_path/"self.json"
    cmd=[sys.executable,"-B",str(CLI),"--plan",str(opts["plan_path"]),"--goal","g","--change","c",
         "--criterion","Expected result","--check-only","--self-check-template",str(template)]
    result=subprocess.run(cmd,cwd=tmp_path,text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    rows=json.loads(template.read_text())
    assert rows["candidate_sha256"]==hashlib.sha256(opts["plan_path"].read_bytes()).hexdigest()
    assert [r["check_id"] for r in rows["rows"]]==list(map(str,range(1,10)))
    with pytest.raises(ValueError): prepare_review(**opts,self_check_path=template)
    for row in rows["rows"]:
        row.update(exact_evidence="A complete engineering plan",local_result="The declared requirement is covered.")
    template.write_text(json.dumps(rows))
    payload,_=prepare_review(**opts,self_check_path=template)
    assert payload["review_purpose"]=="code_design"
    rows["rows"][0]["unresolved_finding"]="Missing a decision"
    template.write_text(json.dumps(rows))
    with pytest.raises(ValueError): prepare_review(**opts,self_check_path=template)
    failed=subprocess.run(cmd,cwd=tmp_path,text=True,capture_output=True)
    assert failed.returncode==2
    assert json.loads(template.read_text())["rows"][0]["unresolved_finding"]=="Missing a decision"


def test_invalid_input_does_not_import_executor(tmp_path):
    opts=options(tmp_path)
    marker=tmp_path/"imported"
    (tmp_path/"bad_executor.py").write_text('from pathlib import Path\nPath('+repr(str(marker))+').touch()\n')
    env={**os.environ,"PYTHONPATH":str(tmp_path)}
    cmd=[sys.executable,"-B",str(CLI),"--plan",str(opts["plan_path"]),"--goal"," ","--change","c",
         "--criterion","a","--executor","bad_executor:run","--output",str(tmp_path/"out.json")]
    result=subprocess.run(cmd,cwd=tmp_path,env=env,text=True,capture_output=True)
    assert result.returncode==2 and not marker.exists()


def test_execution_failure_creates_no_verdict(tmp_path):
    record=review_engineering(executor=lambda p:{"status":"failed","module_id":"engineering_change_reviewer",
        "output":None,"failure_detail":"Execution unavailable"},**options(tmp_path))
    assert record["semantic_validation"]["status"]=="not_run" and record["output"] is None


@pytest.mark.real_run
@REAL_GATE
@pytest.mark.parametrize("failure,error_type", [("unregistered_root", "FileNotFoundError"),
                                                ("mixed_transport", "ValueError")])
def test_real_runtime_failure_is_reported_without_a_verdict(tmp_path, reviewer_host, failure, error_type):
    """Real entry: Runtime Test Run failing before any Provider call; nothing is substituted."""
    opts = options(tmp_path)
    target = tmp_path / "result.json"
    if failure == "unregistered_root":
        result = run_cli(CLI, *_cli_review(opts, target, tmp_path / "empty_root"))
    else:
        result = run_cli(CLI, *_cli_review(opts, target, reviewer_host, "--transport", "codex_cli"))
    assert result.returncode == 2 and not target.exists()
    error = json.loads(result.stderr)
    assert set(error) == {"error", "error_type", "error_code"} and error["error_type"] == error_type
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("material", ["plan", "context", "goal"])
def test_previous_request_record_cannot_be_rebound(tmp_path, material):
    opts=options(tmp_path)
    context=tmp_path/"context.md"; context.write_text("Design A")
    opts["context_paths"]=[context]
    previous=review_engineering(executor=executor,**opts)
    unchanged=review_engineering(executor=lambda payload:copy.deepcopy(previous),**opts)
    assert unchanged["semantic_validation"]["status"]=="passed"
    if material=="plan": opts["plan_path"].write_text("Different plan")
    if material=="context": context.write_text("Design B")
    if material=="goal": opts["goal"]="Different goal"
    rejected=review_engineering(executor=lambda payload:copy.deepcopy(previous),**opts)
    assert rejected["semantic_validation"]["status"]=="failed"
    assert rejected["semantic_input"]==previous["semantic_input"]


def test_previous_commit_record_cannot_be_rebound(tmp_path):
    opts=options(tmp_path)
    plan=review_engineering(executor=executor,**opts)
    evidence=tmp_path/"plan-review.json";evidence.write_text(json.dumps(plan))
    repo=tmp_path/"repo";repo.mkdir();implementation(repo)
    opts.update(repository_root=repo,commit_ref="HEAD",plan_review_path=evidence)
    previous=review_engineering(executor=executor,**opts)
    assert previous["semantic_validation"]["status"]=="passed"
    (repo/"code.py").write_text("x=3\n")
    for args in (("add","code.py"),("commit","-qm","next")):
        subprocess.run(["git",*args],cwd=repo,check=True,capture_output=True)
    rejected=review_engineering(executor=lambda payload:copy.deepcopy(previous),**opts)
    assert rejected["semantic_validation"]["status"]=="failed"
    assert rejected["semantic_input"]["subject"]==previous["semantic_input"]["subject"]


def test_conflicting_reviewer_identity_is_rejected(tmp_path):
    def inconsistent(payload):
        return executor(payload)|{"module_release_ref":"runtime-module:design_contract_reviewer@v1"}
    result=review_engineering(executor=inconsistent,**options(tmp_path))
    assert result["semantic_validation"]["status"]=="failed"
    assert result["module_release_ref"]=="runtime-module:design_contract_reviewer@v1"


@pytest.mark.parametrize("missing", ["semantic_input", "review_purpose"])
def test_completed_record_requires_actual_input_and_purpose(tmp_path, missing):
    def incomplete(payload):
        record=executor(payload);record.pop(missing);return record
    rejected=review_engineering(executor=incomplete,**options(tmp_path))
    assert rejected["semantic_validation"]["status"]=="failed"
    assert missing not in rejected


def test_legacy_input_record_is_not_upgraded(tmp_path):
    def legacy(payload):
        record=executor(payload)
        record["semantic_input"].pop("review_purpose")
        record["semantic_input"]["schema_version"]="engineering_change_reviewer_input_v4"
        return record
    rejected=review_engineering(executor=legacy,**options(tmp_path))
    assert rejected["semantic_validation"]["status"]=="failed"
    assert rejected["semantic_input"]["schema_version"].endswith("v4")


def test_required_blocked_gate_cannot_be_hidden_by_a_fix():
    payload = plan_input(sandbox_command_plan=inputs.command_plan("commands", [command()]))
    record = command_record(payload, unavailable=True)
    with pytest.raises(EngineeringReviewOutputError, match="unavailable required"):
        validate_engineering_review_output(with_finding(output()), review_input=payload, execution_record=record)
    validate_engineering_review_output(with_finding(output(), severity="block"),
                                       review_input=payload, execution_record=record)


def test_previously_rejected_execution_cannot_be_revalidated(tmp_path):
    opts=options(tmp_path); original=opts["plan_path"].read_bytes()
    def changing_input(payload):
        record=executor(payload)
        opts["plan_path"].write_text("Changed during execution")
        return record
    rejected=review_engineering(executor=changing_input,**opts)
    assert rejected["semantic_validation"]["status"]=="failed"
    original_failure=rejected["semantic_validation"]["message"]
    opts["plan_path"].write_bytes(original)
    replay=review_engineering(executor=lambda payload:copy.deepcopy(rejected),**opts)
    assert replay["semantic_validation"]["status"]=="failed"
    assert original_failure in replay["semantic_validation"]["message"]
    evidence=tmp_path/"invalid-plan-review.json";evidence.write_text(json.dumps(replay))
    repo=tmp_path/"repo";repo.mkdir();implementation(repo)
    with pytest.raises(inputs.EngineeringReviewInputError):
        prepare_review(**opts,repository_root=repo,commit_ref="HEAD",plan_review_path=evidence)


@pytest.mark.parametrize("mutation", ["v4", "v5", "command_hash", "context_hash", "missing_field", "checklist"])
def test_imported_plan_input_must_match_its_declared_protocol(tmp_path, mutation):
    record=plan_record()
    if mutation=="v4": record["semantic_input"]["schema_version"]="engineering_change_reviewer_input_v4"
    if mutation=="v5": record["semantic_input"]["schema_version"]="engineering_change_reviewer_input_v5"
    if mutation=="command_hash":
        record["semantic_input"]["sandbox_command_plan"]=inputs.command_plan("commands",[command()])
        record["semantic_input"]["sandbox_command_plan"]["commands"]=[]
    if mutation=="context_hash":
        record["semantic_input"]["context_documents"]=[inputs.hashed_body("design","Design")|{"sha256":"0"*64}]
    if mutation=="missing_field": record["semantic_input"].pop("context_documents")
    if mutation=="checklist": record["semantic_input"]["required_check_ids"].pop()
    with pytest.raises(inputs.EngineeringReviewInputError):
        implementation(tmp_path,code_design_review=inputs.hashed_body("review",json.dumps(record)))


def test_historical_cli_plan_evidence_requires_rereview_without_rewriting_it(tmp_path):
    record=plan_record()
    record["semantic_input"].pop("schema_version")
    record["semantic_input"]["sandbox_command_plan"]={"commands":[]}
    before = copy.deepcopy(record)
    with pytest.raises(inputs.EngineeringReviewInputError, match="new-format review"):
        implementation(tmp_path,code_design_review=inputs.hashed_body("review",json.dumps(record)))
    assert record == before


@pytest.mark.parametrize("wrapped_commands", [True, False])
def test_unversioned_input_still_requires_executable_command_shape(tmp_path, wrapped_commands):
    record=plan_record();record["semantic_input"].pop("schema_version")
    invalid=command()|{"argv":[]}
    record["semantic_input"]["sandbox_command_plan"]=inputs.command_plan("commands",[invalid]) if wrapped_commands else {"commands":[invalid]}
    record["output"]["gate_results"]=[{"command_id":"unit","disposition":"passed","observation":"claimed"}]
    with pytest.raises(inputs.EngineeringReviewInputError):
        implementation(tmp_path,code_design_review=inputs.hashed_body("review",json.dumps(record)))


VIEW_KEYS = {"source_record", "code_design_basis", "acceptance_criteria", "status", "module_id",
             "review_purpose", "semantic_validation", "runtime_identity", "output"}


def traced_plan_record(calls=1):
    """A complete plan review carrying Runtime identity and `calls` unrelated tool calls in its CLI log."""
    record = plan_record() | {"managed_runtime": False, "model": "claude-opus-5-5", "effort": "xhigh",
                              "module_release_ref": "runtime-module:engineering_change_reviewer@v1",
                              "runtime_version": None, "usage": {"input_tokens": calls}}
    record["execution_log"] = {"schema_version": "runtime_cli_log_v1", "complete": True, "tool_calls": [
        {"tool_call_id": f"call_{i}", "tool_name": "read_file", "request": {"path": f"file_{i}"},
         "response": {"text": "trace " * 50}} for i in range(calls)]}
    record["provider_trace"] = [{"event": "delta", "text": "x" * 100} for _ in range(calls)]
    return record


@pytest.mark.deterministic
def test_validated_plan_review_reaches_the_reviewer_as_a_compact_view(tmp_path):
    record = traced_plan_record()
    evidence = plan_review_evidence(record)
    derived = implementation(tmp_path, code_design_review=evidence)["code_design_review"]
    view = json.loads(derived["body"])
    assert derived["ref"] == "review#validated-plan-review"
    assert derived["sha256"] == hashlib.sha256(derived["body"].encode("utf-8")).hexdigest()
    assert derived["sha256"] != evidence["sha256"]
    assert derived["body"] == json.dumps(view, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    assert set(view) == VIEW_KEYS
    assert view["source_record"] == {"ref": "review", "sha256": evidence["sha256"]}
    basis = record["semantic_input"]["code_design_basis"]
    assert view["code_design_basis"] == {"ref": basis["ref"], "sha256": basis["sha256"]}
    assert view["acceptance_criteria"] == record["semantic_input"]["acceptance_criteria"]
    assert (view["status"], view["module_id"], view["review_purpose"], view["semantic_validation"]) == (
        "completed", "engineering_change_reviewer", "code_design", {"status": "passed"})
    assert view["runtime_identity"] == {
        "managed_runtime": False, "model": "claude-opus-5-5", "effort": "xhigh",
        "module_release_ref": "runtime-module:engineering_change_reviewer@v1", "runtime_version": None}
    assert view["output"] == record["output"]
    # A record without Runtime identity fields gets none invented.
    bare = tmp_path/"bare"; bare.mkdir()
    assert json.loads(implementation(bare)["code_design_review"]["body"])["runtime_identity"] == {}


@pytest.mark.deterministic
def test_plan_review_trace_growth_does_not_reach_the_reviewer(tmp_path):
    views = {}
    for calls in (1, 400):
        repo = tmp_path/str(calls); repo.mkdir()
        evidence = plan_review_evidence(traced_plan_record(calls))
        derived = implementation(repo, code_design_review=evidence)["code_design_review"]
        views[calls] = (len(evidence["body"].encode("utf-8")), derived["body"])
    (small_source, small_body), (large_source, large_body) = views[1], views[400]
    small, large = json.loads(small_body), json.loads(large_body)
    assert large_source > 100 * len(large_body.encode("utf-8"))
    assert len(large_body.encode("utf-8")) == len(small_body.encode("utf-8"))
    assert small["source_record"]["sha256"] != large["source_record"]["sha256"]
    assert {key: small[key] for key in VIEW_KEYS - {"source_record"}} == {
        key: large[key] for key in VIEW_KEYS - {"source_record"}}
    assert "trace" not in large_body


@pytest.mark.deterministic
@pytest.mark.parametrize("field,value", [("model", {"provider_trace": ["nested"]}), ("attempt_id", ["call_1"]),
                                         ("effort", 3), ("managed_runtime", "false"), ("managed_runtime", None)])
def test_plan_review_identity_fields_cannot_carry_trace(tmp_path, field, value):
    record = plan_record() | {field: value}
    with pytest.raises(inputs.EngineeringReviewInputError, match="scalar identity") as caught:
        implementation(tmp_path, code_design_review=plan_review_evidence(record))
    assert caught.value.error_code == inputs.ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE


@pytest.mark.deterministic
def test_plan_review_checks_and_findings_survive_the_view(tmp_path):
    result = with_finding(output(), severity="note", check="2")
    second = copy.deepcopy(result["findings"][0]) | {"finding_id": "finding_2", "required_change": "Optional wording"}
    second["evidence"]["observation"] = "The provider_trace field stays in the complete record"
    result["findings"].append(second)
    result["check_results"][6]["finding_ids"] = ["finding_2"]
    result["check_results"][0]["assessment"] = "Code checked execution_log and semantic_input before the view"
    result["safe_next_step"] = "Implement the reviewed plan; both notes are optional"
    record = plan_record() | {"output": result}
    payload = implementation(tmp_path, code_design_review=plan_review_evidence(record))
    view = json.loads(payload["code_design_review"]["body"])
    assert view["output"] == result
    assert [row["finding_id"] for row in view["output"]["findings"]] == ["finding_1", "finding_2"]
    # Prior plan notes stay inside the plan review result; they are not current findings.
    assert payload["prior_findings"] == []


@pytest.mark.deterministic
@pytest.mark.parametrize("evidence", ["replayed_view", "forged_summary"])
def test_validated_view_is_not_plan_review_evidence(tmp_path, evidence):
    source = tmp_path/"plan-review.json"; source.write_text(json.dumps(plan_record()))
    first = tmp_path/"first"; first.mkdir()
    derived = implementation(first, code_design_review=inputs.hashed_body(str(source), source.read_text()))
    submitted = derived["code_design_review"]
    if evidence == "forged_summary":
        view = json.loads(submitted["body"])
        submitted = inputs.hashed_body(str(source), json.dumps({key: view[key] for key in VIEW_KEYS - {"source_record"}}))
    second = tmp_path/"second"; second.mkdir()
    # The complete record is readable at source_record.ref; the builder still does not open it.
    with pytest.raises(inputs.EngineeringReviewInputError) as caught:
        implementation(second, code_design_review=submitted)
    assert caught.value.error_code == inputs.ENGINEERING_REVIEW_INPUT_CLOSURE_INCOMPLETE


def full_plan_review_file(tmp_path, opts):
    """A complete plan review from the real entry, with trace the Reviewer view leaves out."""
    evidence = tmp_path/"plan-review.json"
    evidence.write_text(json.dumps(review_engineering(executor=executor, **opts) | {"provider_trace": ["trace"] * 1000}))
    repo = tmp_path/"repo"; repo.mkdir(); implementation(repo)
    return evidence, repo


@pytest.mark.deterministic
def test_complete_plan_review_file_stays_frozen_and_unchanged(tmp_path):
    opts = options(tmp_path)
    evidence, repo = full_plan_review_file(tmp_path, opts)
    original = evidence.read_bytes()
    opts.update(repository_root=repo, commit_ref="HEAD", plan_review_path=evidence)
    payload, frozen = prepare_review(**opts)
    resolved = evidence.resolve()
    assert frozen[evidence.absolute()] == (resolved, original)
    derived = payload["code_design_review"]
    assert derived["ref"] == f"{resolved}#validated-plan-review"
    assert json.loads(derived["body"])["source_record"] == {"ref": str(resolved),
                                                            "sha256": hashlib.sha256(original).hexdigest()}
    record = review_engineering(executor=executor, **opts)
    assert record["semantic_validation"]["status"] == "passed"
    assert record["source_sha256"][str(evidence.absolute())] == hashlib.sha256(original).hexdigest()
    assert derived["sha256"] not in record["source_sha256"].values()
    assert evidence.read_bytes() == original
    def rewrite(payload):
        evidence.write_bytes(original + b"\n")
        return executor(payload)
    rejected = review_engineering(executor=rewrite, **opts)
    assert rejected["semantic_validation"]["status"] == "failed"
    assert "binding changed" in rejected["semantic_validation"]["message"]


@pytest.mark.deterministic
def test_check_only_sends_only_the_validated_view(tmp_path):
    opts = options(tmp_path)
    evidence, repo = full_plan_review_file(tmp_path, opts)
    original, full = evidence.read_bytes(), json.loads(evidence.read_text())
    cmd = [sys.executable, "-B", str(CLI), "--plan", str(opts["plan_path"]), "--goal", "Expected result",
           "--change", "Bounded change", "--criterion", "Expected result", "--plan-review", str(evidence)]
    env = {k:v for k,v in os.environ.items() if k not in ("ENGINEERING_REVIEW_EXECUTOR", "PYTHONPATH")}
    checked = subprocess.run([*cmd, "--repository", str(repo), "--commit", "HEAD", "--check-only"],
                             cwd=tmp_path, env=env, text=True, capture_output=True)
    assert checked.returncode == 0, checked.stderr
    payload = json.loads(checked.stdout)
    view = json.loads(payload["code_design_review"]["body"])
    assert set(view) == VIEW_KEYS and view["output"] == full["output"]
    assert "provider_trace" not in checked.stdout and len(checked.stdout.encode("utf-8")) < len(original)
    assert evidence.read_bytes() == original
    # A plan review still consumes no historical review result.
    plan_only = subprocess.run([*cmd, "--check-only"], cwd=tmp_path, env=env, text=True, capture_output=True)
    assert plan_only.returncode == 2 and "future review result" in plan_only.stderr
    # The output validator accepts the declared view ref; the source locator is not declared evidence.
    cited = with_finding(output(), severity="note", source=payload["code_design_review"]["ref"])
    validate_engineering_review_output(cited, review_input=payload, execution_record=executor(payload))
    cited["findings"][0]["evidence"]["source_ref"] = view["source_record"]["ref"]
    with pytest.raises(EngineeringReviewOutputError, match="undeclared evidence"):
        validate_engineering_review_output(cited, review_input=payload, execution_record=executor(payload))


def inaccessible_path(path, kind):
    prefix=path.parent/("traversal_"+kind)
    if kind=="file": prefix.write_text("Not a directory")
    if kind=="link": prefix.symlink_to(path.parent/"missing_directory",target_is_directory=True)
    return prefix/".."/path.name


@pytest.mark.parametrize("kind", ["missing", "file", "link"])
@pytest.mark.parametrize("field", ["plan", "context", "commands"])
def test_unreadable_input_path_is_not_lexically_repaired(tmp_path, kind, field):
    opts=options(tmp_path)
    if field=="plan":
        wrong=inaccessible_path(opts["plan_path"],kind);opts["plan_path"]=wrong
    else:
        source=tmp_path/(field+".json");source.write_text("[]" if field=="commands" else "Context")
        wrong=inaccessible_path(source,kind)
        if field=="context":opts["context_paths"]=[wrong]
        else:opts["commands_path"]=wrong
    with pytest.raises(OSError):wrong.read_bytes()
    with pytest.raises((OSError,ValueError)):
        review_engineering(executor=lambda payload:pytest.fail("Invalid input reached executor"),**opts)


@pytest.mark.parametrize("field", ["plan", "context"])
@pytest.mark.parametrize("linked", [False, True])
def test_disappearing_traversal_directory_invalidates_review(tmp_path, field, linked):
    opts=options(tmp_path)
    directory=tmp_path/"traversal";directory.mkdir()
    prefix=directory
    if linked:
        prefix=tmp_path/"link";prefix.symlink_to(directory,target_is_directory=True)
    if field=="plan":opts["plan_path"]=prefix/".."/opts["plan_path"].name
    else:
        source=tmp_path/"context.md";source.write_text("Context")
        opts["context_paths"]=[prefix/".."/source.name]
    control=review_engineering(executor=executor,**opts)
    assert control["semantic_validation"]["status"]=="passed"
    def remove_directory(payload):
        result=executor(payload);directory.rmdir();return result
    rejected=review_engineering(executor=remove_directory,**opts)
    assert rejected["semantic_validation"]["status"]=="failed"


@pytest.mark.deterministic
@pytest.mark.parametrize("kind", ["missing", "file", "link"])
def test_repository_path_must_really_resolve(tmp_path, kind):
    repo=tmp_path/"repo";repo.mkdir();original=implementation(repo)
    # The payload carries a validated view; a direct caller passes its complete plan review again.
    values={key:original[key] for key in ("code_design_basis","sandbox_command_plan","acceptance_criteria")}
    values["code_design_review"]=plan_review_evidence()
    valid=repo/"traversal";valid.mkdir()
    control=inputs.build_engineering_review_input(repository_root=valid/"..",commit_ref="HEAD",**values)
    assert control["subject"]==original["subject"]
    assert control["code_design_review"]==original["code_design_review"]
    # Produce an invalid path ending at the same repository after lexical normalization.
    prefix=repo/("traversal_"+kind)
    if kind=="file":prefix.write_text("Not a directory")
    if kind=="link":prefix.symlink_to(repo/"missing_directory",target_is_directory=True)
    with pytest.raises(inputs.EngineeringReviewInputError):
        inputs.build_engineering_review_input(repository_root=prefix/"..",commit_ref="HEAD",**values)


@pytest.mark.skipif(os.name!="posix" or getattr(os,"geteuid",lambda:0)()==0,reason="Requires ordinary POSIX traversal permissions")
@pytest.mark.parametrize("field", ["plan", "context"])
@pytest.mark.parametrize("during_review", [False, True])
def test_original_path_search_permissions_are_required(tmp_path, field, during_review):
    opts=options(tmp_path);directory=tmp_path/"traversal";directory.mkdir()
    if field=="plan":
        requested=directory/".."/opts["plan_path"].name;opts["plan_path"]=requested
    else:
        source=tmp_path/"context.md";source.write_text("Context")
        requested=directory/".."/source.name;opts["context_paths"]=[requested]
    assert review_engineering(executor=executor,**opts)["semantic_validation"]["status"]=="passed"
    def revoke(payload):
        result=executor(payload);directory.chmod(0o600)
        with pytest.raises(PermissionError):requested.read_bytes()
        return result
    try:
        if during_review:
            assert review_engineering(executor=revoke,**opts)["semantic_validation"]["status"]=="failed"
        else:
            directory.chmod(0o600)
            with pytest.raises(PermissionError):requested.read_bytes()
            with pytest.raises(PermissionError):
                review_engineering(executor=lambda p:pytest.fail("Unreadable path reached executor"),**opts)
    finally:
        directory.chmod(0o700)


@pytest.mark.deterministic
@pytest.mark.skipif(os.name!="posix" or getattr(os,"geteuid",lambda:0)()==0,reason="Requires ordinary POSIX traversal permissions")
def test_repository_original_path_search_permission_is_required(tmp_path):
    repo=tmp_path/"repo";repo.mkdir();source=implementation(repo)
    values={key:source[key] for key in ("code_design_basis","sandbox_command_plan","acceptance_criteria")}
    values["code_design_review"]=plan_review_evidence()
    directory=repo/"traversal";directory.mkdir();requested=directory/".."
    assert inputs.build_engineering_review_input(repository_root=repo,commit_ref="HEAD",**values)["subject"]==source["subject"]
    try:
        directory.chmod(0o600)
        with pytest.raises(PermissionError):requested.stat()
        with pytest.raises(inputs.EngineeringReviewInputError):
            inputs.build_engineering_review_input(repository_root=requested,commit_ref="HEAD",**values)
    finally:
        directory.chmod(0o700)


def test_repeated_input_retarget_is_rejected_before_reading_replacement(tmp_path, monkeypatch):
    opts=options(tmp_path);original=opts["plan_path"]
    alias=tmp_path/"alias.md";alias.symlink_to(original)
    other=tmp_path/"other.md";other.write_text("Unselected replacement")
    opts.update(plan_path=alias,context_paths=[alias])
    read_bytes=Path.read_bytes
    def retarget_after_first_read(path):
        assert path!=other,"Must not read a retargeted input"
        data=read_bytes(path)
        if path==original:
            alias.unlink();alias.symlink_to(other)
        return data
    monkeypatch.setattr(Path,"read_bytes",retarget_after_first_read)
    with pytest.raises(ValueError,match="binding changed"):
        review_engineering(executor=lambda p:pytest.fail("Changed input reached executor"),**opts)


@pytest.mark.parametrize("same_bytes", [False, True])
def test_retargeted_input_link_is_rejected(tmp_path, same_bytes):
    first=tmp_path/"first.md"; first.write_text("Plan")
    second=tmp_path/"second.md"; second.write_text("Plan" if same_bytes else "Different plan")
    link=tmp_path/"plan.md"; link.symlink_to(first)
    def retarget(payload):
        link.unlink(); link.symlink_to(second)
        return executor(payload)
    result=review_engineering(executor=retarget,plan_path=link,goal="g",change="c",acceptance_criteria=["r"])
    assert result["semantic_validation"]["status"]=="failed"
    assert "path binding" in result["semantic_validation"]["message"]

@pytest.mark.parametrize("mutation", [
    "missing_check", "duplicate_check", "reordered", "unknown_check", "unknown_finding",
    "unlinked_finding", "duplicate_finding", "finding_without_defect", "passed_with_fix",
    "semantic_not_run", "not_applicable", "prose_too_early", "prose_missing", "missing_requirement",
    "undeclared_evidence", "background_fix", "input_checklist",
])
def test_common_format_and_engineering_coverage_reject_gaps(mutation):
    payload = plan_input(context_documents=[inputs.hashed_body("peer", "Background Design")])
    result = output()
    if mutation == "missing_check": result["check_results"].pop()
    if mutation == "duplicate_check": result["check_results"][1] = result["check_results"][0]
    if mutation == "reordered": result["check_results"].reverse()
    if mutation == "unknown_check": result["check_results"][0]["check_id"] = "unknown"
    if mutation == "unknown_finding": result["check_results"][0]["finding_ids"] = ["unknown"]
    if mutation == "finding_without_defect": result["check_results"][0]["disposition"] = "finding"
    if mutation == "semantic_not_run": result["check_results"][0]["disposition"] = "not_run"
    if mutation == "not_applicable": result["check_results"][0]["disposition"] = "not_applicable"
    if mutation == "prose_missing": result["check_results"][7]["disposition"] = "not_run"
    if mutation == "input_checklist": payload["required_check_ids"].pop()
    if mutation in {"unlinked_finding", "duplicate_finding", "passed_with_fix", "prose_too_early",
                    "missing_requirement", "undeclared_evidence", "background_fix"}:
        result = with_finding(result)
        if mutation == "unlinked_finding": result["check_results"][6]["finding_ids"] = []
        if mutation == "duplicate_finding": result["findings"] *= 2
        if mutation == "passed_with_fix": result["check_results"][6]["disposition"] = "passed"
        if mutation == "prose_too_early": result["check_results"][7]["disposition"] = "passed"
        if mutation == "missing_requirement": result["findings"][0].pop("requirement")
        if mutation == "undeclared_evidence": result["findings"][0]["evidence"]["source_ref"] = "invented"
        if mutation == "background_fix": result["findings"][0]["evidence"]["source_ref"] = "peer"
    with pytest.raises(EngineeringReviewOutputError):
        validate_engineering_review_output(result, review_input=payload)


def test_note_and_prose_only_fix_are_supported():
    validate_engineering_review_output(with_finding(output(), severity="note"), review_input=plan_input())
    validate_engineering_review_output(with_finding(output(), check="8"), review_input=plan_input())
    payload = plan_input(context_documents=[inputs.hashed_body("peer", "Needed prerequisite")])
    validate_engineering_review_output(with_finding(output(), severity="block", source="peer"),
                                       review_input=payload)


def test_required_commands_without_trusted_record_cannot_pass():
    payload = plan_input(sandbox_command_plan=inputs.command_plan("c", [command()]))
    with pytest.raises(EngineeringReviewOutputError, match="actual execution evidence"):
        validate_engineering_review_output(output(), review_input=payload)


def test_command_evidence_is_checked_on_actual_entry_and_plan_reuse(tmp_path):
    opts = options(tmp_path)
    commands = tmp_path/"commands.json"
    commands.write_text(json.dumps([command()]))
    opts["commands_path"] = commands
    record = review_engineering(executor=command_record, **opts)
    assert record["semantic_validation"]["status"] == "passed"
    # A model saying passed, without the trusted observations, fails at the normal entry.
    missing = review_engineering(executor=executor, **opts)
    assert missing["semantic_validation"]["status"] == "failed"
    repo = tmp_path/"repo"; repo.mkdir()
    values = dict(code_design_basis=record["semantic_input"]["code_design_basis"],
                  code_design_review=inputs.hashed_body("review", json.dumps(record)))
    implementation(repo, **values)
    record["execution_log"]["complete"] = False
    values["code_design_review"] = inputs.hashed_body("review", json.dumps(record))
    with pytest.raises(inputs.EngineeringReviewInputError, match="incomplete"):
        inputs.build_engineering_review_input(
            repository_root=repo, commit_ref="HEAD", **values,
            acceptance_criteria=["Expected result"], sandbox_command_plan=inputs.command_plan("none", []))


@pytest.mark.parametrize("exit_code", [0, 3])
def test_command_evidence_with_real_local_subprocess(tmp_path, exit_code):
    # This tests evidence consumption, not a live Reviewer or Runtime registration.
    declared = command() | {"argv": [sys.executable, "-B", "-c", f"print('evidence'); raise SystemExit({exit_code})"],
                            "cwd": str(tmp_path)}
    payload = plan_input(sandbox_command_plan=inputs.command_plan("c", [declared]))
    actual = subprocess.run(declared["argv"], cwd=declared["cwd"], capture_output=True,
                            text=True, timeout=declared["timeout_seconds"])
    record = command_record(payload, returncode=actual.returncode)
    response = {
        "command_id": "unit", "allowed": True, "returncode": actual.returncode,
        "stdout": actual.stdout, "stderr": actual.stderr,
    }
    record["execution_log"]["tool_calls"][0]["response"] = response
    result = output() if exit_code == 0 else with_finding(output())
    validate_engineering_review_output(result, review_input=payload, execution_record=record)
    if exit_code:
        with pytest.raises(EngineeringReviewOutputError, match="failed required"):
            validate_engineering_review_output(output(), review_input=payload, execution_record=record)


@pytest.mark.skipif(os.environ.get("AGENT_RUNTIME_LOGGING_INTEGRATION") != "1",
                    reason="explicit integration with the upgraded Runtime package")
@pytest.mark.parametrize("exit_code", [0, 3])
def test_actual_runtime_cli_log_reaches_portable_without_a_host_artifact_map(tmp_path, exit_code):
    from agent_runtime import parse_cli_log
    from agent_runtime.invocation.invocation_cli_logging import captured_cli_streams
    from agent_runtime.invocation.invocation_process_execution import run_cli_process
    command_argv = [sys.executable, "-c", f"print('runtime evidence');raise SystemExit({exit_code})"]
    producer = "\n".join([
        "import json,subprocess",
        "item={'id':'real_call','type':'mcp_tool_call','tool':'sandbox_command_execute','arguments':{'command_id':'unit'}}",
        "print(json.dumps({'type':'item.started','item':item}),flush=True)",
        f"actual=subprocess.run({command_argv!r},capture_output=True,text=True)",
        "body={'command_id':'unit','allowed':True,'returncode':actual.returncode,'stdout':actual.stdout,'stderr':actual.stderr}",
        "print(json.dumps({'type':'item.completed','item':{**item,'status':'completed','error':None,'result':{'structured_content':body}}}),flush=True)",
        "print(json.dumps({'type':'turn.completed'}),flush=True)",
    ])
    actual = run_cli_process(argv=[sys.executable, "-u", "-c", producer], cwd=tmp_path,
        prompt="", timeout_seconds=10, environment=dict(os.environ))
    log = parse_cli_log({"transport":"codex_cli", "process_output_complete":True,
                         **captured_cli_streams(actual)})
    assert log["complete"] and log["tool_calls"][0]["response"]["stdout"] == "runtime evidence\n"
    payload = plan_input(sandbox_command_plan=inputs.command_plan("c", [command() | {"argv":command_argv,"cwd":str(tmp_path)}]))
    record = executor(payload) | {"managed_runtime":False,"execution_log":log}
    assert "tool_observations" not in record and "tool_artifacts" not in record
    result = output() if exit_code == 0 else with_finding(output())
    validate_engineering_review_output(result, review_input=payload, execution_record=record)
    if exit_code:
        with pytest.raises(EngineeringReviewOutputError, match="failed required"):
            validate_engineering_review_output(output(), review_input=payload, execution_record=record)


def test_managed_log_only_credits_the_selected_attempt():
    payload = plan_input(sandbox_command_plan=inputs.command_plan("c", [command()]))
    call = command_record(payload)["execution_log"]["tool_calls"][0]
    record = executor(payload) | {"managed_runtime":True,"module_run_id":"run_1","attempt_id":"attempt_2",
        "execution_log":{"schema_version":"runtime_execution_log_v1", "attempts":[
            {"module_run_id":"run_1","attempt_id":"attempt_1","status":"completed","complete":True,"tool_calls":[call]},
            {"module_run_id":"run_1","attempt_id":"attempt_2","status":"completed","complete":True,"tool_calls":[]}]}}
    with pytest.raises(EngineeringReviewOutputError, match="actual execution evidence"):
        validate_engineering_review_output(output(), review_input=payload, execution_record=record)
    record["execution_log"]["attempts"][1]["tool_calls"] = [call]
    validate_engineering_review_output(output(), review_input=payload, execution_record=record)
    record["module_run_id"] = "other"
    with pytest.raises(EngineeringReviewOutputError, match="another review Attempt"):
        validate_engineering_review_output(output(), review_input=payload, execution_record=record)


@pytest.mark.skipif(os.environ.get("AGENT_RUNTIME_LOGGING_INTEGRATION") != "1",
                    reason="explicit integration with the upgraded Runtime package")
def test_actual_runtime_failed_mcp_event_preserves_unavailable_command_evidence():
    from agent_runtime import parse_cli_log
    from agent_runtime.invocation.invocation_cli_logging import captured_cli_streams
    item = {"id": "denied_call", "type": "mcp_tool_call", "tool": "sandbox_command_execute",
            "arguments": {"command_id": "unit"}}
    error = {"message": "sandbox process launch denied"}
    events = [{"type": "item.started", "item": item},
              {"type": "item.completed", "item": {**item, "status": "failed", "result": None, "error": error}},
              {"type": "turn.completed"}]
    raw = b"\n".join(json.dumps(event).encode() for event in events)
    process = subprocess.CompletedProcess([], 0, raw.decode(), "")
    process.stdout_bytes, process.stderr_bytes = raw, b""
    log = parse_cli_log({"transport": "codex_cli", "process_output_complete": True,
                         **captured_cli_streams(process)})
    call = log["tool_calls"][0]
    assert log["complete"] and call["status"] == "failed"
    assert call["response"] == {"result": None, "error": error}
    assert "returncode" not in call["response"]
    payload = plan_input(sandbox_command_plan=inputs.command_plan("commands", [command()]))
    record = executor(payload) | {"managed_runtime": False, "execution_log": log}
    validate_engineering_review_output(with_finding(output(), severity="block"),
                                       review_input=payload, execution_record=record)
    for rejected in (output(), with_finding(output())):
        with pytest.raises(EngineeringReviewOutputError, match="unavailable required"):
            validate_engineering_review_output(rejected, review_input=payload, execution_record=record)


def test_checklist_has_one_source_and_is_frozen_by_entry(tmp_path):
    from software_delivery.engineering_review_output import engineering_check_ids
    payload, frozen = prepare_review(**options(tmp_path))
    assert payload["required_check_ids"] == list(engineering_check_ids())
    assert any(path.name == "the_software_delivery.md" for path in frozen)
    start, end = "<!-- engineering-change-review-checklist:start -->", "<!-- engineering-change-review-checklist:end -->"
    for body in (b"", f"{end}\n1. first\n{start}".encode(),
                 f"{start}\n1. first\n3. skipped\n{end}".encode()):
        with pytest.raises(EngineeringReviewOutputError):
            engineering_check_ids(lambda path: body)

@pytest.mark.parametrize("fixture_name", ["positive_case.json", "negative_extra_field_case.json", "schema_drift_case.json"])
def test_registered_engineering_fixture_against_current_sources(fixture_name):
    from types import SimpleNamespace
    import skill_release as release

    root = Path(inputs.__file__).resolve().parents[5]
    prefix = "09_soul/governance/skills/engineering-change-review/runtime_modules/engineering_change_reviewer"
    module_root = root / prefix
    fixture = json.loads((module_root / "tests" / fixture_name).read_text())
    assert fixture["module_id"] == "engineering_change_reviewer"
    payloads = {str(path.relative_to(root)): path.read_bytes() for path in module_root.rglob("*") if path.is_file()}
    skill = SimpleNamespace(skill_id="engineering-change-review")
    release._validate_runtime_module_registration_closure(skill, payloads)
    if fixture["case_kind"] == "positive":
        assert fixture["mutation"] == "none"
        validate_engineering_review_output(output(), review_input=plan_input())
    elif fixture["case_kind"] == "negative":
        assert fixture["mutation"] == "additional_model_output_field"
        with pytest.raises(EngineeringReviewOutputError):
            validate_engineering_review_output(output() | {"extra": "not in the contract"})
    else:
        assert fixture["mutation"] == "output_schema_ref_hash_mismatch"
        registration_path = prefix + "/module_registration.json"
        registration = json.loads(payloads[registration_path])
        registration["output_schema_ref"] = "schema:engineering_change_reviewer_output@v5"
        payloads[registration_path] = json.dumps(registration).encode()
        with pytest.raises(release.GovernanceSkillReleaseError, match="schema ref"):
            release._validate_runtime_module_registration_closure(skill, payloads)


def test_engineering_prompt_keeps_canonical_universal_and_checklist():
    import skill_release as release

    root = Path(inputs.__file__).resolve().parents[5]
    manifest = release.load_governance_skill_manifest(root)
    resources = {row.resource_id: row for row in manifest.instruction_resources}
    ids = ("t0:review_contract_universal_review_style", "t0:engineering_change_review_checklist")
    selected = {key: release._select_instruction_resource_bytes(
        resources[key], (root / resources[key].source).read_bytes()) for key in ids}
    prompt = (inputs.INPUT_SCHEMA_PATH.parent.parent / "prompt.md").read_bytes()
    assert release.compose_governance_skill_package_file(prompt, ids, selected) == prompt
    release.validate_reviewer_prompt_artifact(prompt, embedded_resource_ids=ids)
