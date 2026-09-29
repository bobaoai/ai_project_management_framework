from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest
from jsonschema import Draft202012Validator, ValidationError

VALIDATION = Path(__file__).resolve().parents[2]
ROOT = VALIDATION.parents[3]
PROSE = "prose_and_meaning_preservation"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _artifact(ref):
    body = "Frozen body for " + ref
    return {"artifact_ref": ref, "sha256": hashlib.sha256(body.encode()).hexdigest(), "body": body}


@pytest.fixture(params=["system_change", "reviewer_prompt"])
def review_case(request):
    if request.param == "system_change":
        module = _load("sgc_output_test", VALIDATION / "system_change/model_output_validation.py")
        schema = json.loads(module.INPUT_SCHEMA_PATH.read_text())
        ids = [row["const"] for row in schema["properties"]["required_check_ids"]["prefixItems"]]
        payload = {
            "schema_version": schema["properties"]["schema_version"]["const"], "module_id": "system_change_plan_reviewer",
            "system_change_plan": {"document_id": "plan", "owner_ref": "plan_owner", "title": "Plan", "body": "Plan body"},
            "governing_contract_closure": [{"document_id": "authority", "owner_ref": "authority_owner", "title": "Authority", "body": "Authority body"}],
            "required_check_ids": ids, "prior_findings": [],
        }
        validator = module.validate_system_change_review_output
        candidate_ref, context_ref = "plan", "authority"
    else:
        module = _load("prompt_output_test", VALIDATION / "review_contract/reviewer_output_validation.py")
        schema = json.loads(module.INPUT_SCHEMA_PATH.read_text())
        ids = [row["const"] for row in schema["properties"]["required_check_ids"]["prefixItems"]]
        candidate = _artifact("artifact:prompt")
        payload = {
            "schema_version": schema["properties"]["schema_version"]["const"], "module_id": "reviewer_reviewer",
            "review_request": {"target_reviewer_module_id": "example_reviewer", "reviewed_subject_kind": "reviewer_prompt_source", "target_design_authority_ref": "designDoc/example.md", "intended_result": "Clear review instructions"},
            "prompt_candidate": candidate, "target_design_contract": _artifact("artifact:design"),
            "target_reviewer_input_schema": _artifact("artifact:input_schema"), "target_reviewer_output_schema": _artifact("artifact:output_schema"),
            "fixtures": [{"fixture_ref": "fixture:" + kind, "sha256": hashlib.sha256(b"{}").hexdigest(), "case_kind": kind, "body": "{}"} for kind in ("positive", "negative", "schema_drift")],
            "deterministic_evidence": {"disposition": "passed", "subject_sha256": candidate["sha256"], "universal_resource_id": "t0:review_contract_universal_review_style", "universal_resource_sha256": "1" * 64, "checklist_resource_id": "example_checklist", "checklist_resource_sha256": "2" * 64},
            "required_check_ids": ids, "prior_findings": [],
        }
        validator = module.validate_reviewer_prompt_review_output
        candidate_ref, context_ref = "artifact:prompt", "artifact:design"
    output = {"verdict": "passed", "check_results": [{"check_id": check, "disposition": "passed", "assessment": "Supplied evidence supports this check.", "finding_ids": []} for check in [*ids, PROSE]], "findings": [], "safe_next_step": "Use the reviewed candidate."}
    return request.param, validator, payload, output, candidate_ref, context_ref


def _finding(case, severity="fix"):
    kind, _, payload, _, candidate, context = case
    result = {"finding_id": "gap", "severity": severity, "evidence": {"source_ref": context if severity == "block" else candidate, "locator": "Task", "observation": "Required result is unclear."}, "requirement": "The declared result must be clear.", "impact": "The reader cannot proceed.", "accountable_owner_ref": "authority_owner" if severity == "block" else "candidate_owner", "required_change": "Clarify the required result."}
    if kind == "system_change": result["check_id"] = payload["required_check_ids"][0]
    else: result["finding_class"] = "input_decision_or_output_gap"
    return result


def test_plain_pass_and_note_are_accepted(review_case):
    _, validate, payload, output, _, _ = review_case
    validate(output, payload)
    output["findings"] = [_finding(review_case, "note")]
    output["check_results"][0]["finding_ids"] = ["gap"]
    validate(output, payload)


@pytest.mark.parametrize("severity", ["fix", "block"])
def test_actionable_result_keeps_covered_findings_and_defers_prose(review_case, severity):
    _, validate, payload, output, _, _ = review_case
    output["verdict"] = "blocked" if severity == "block" else "non_pass"
    output["findings"] = [_finding(review_case, severity)]
    output["check_results"][0].update(disposition="finding", finding_ids=["gap"])
    output["check_results"][1].update(disposition="finding", finding_ids=["gap"])
    output["check_results"][-1]["disposition"] = "not_run"
    before = deepcopy(output)
    validate(output, payload)
    assert output == before
    if severity == "block":
        output["check_results"][1].update(disposition="not_run", finding_ids=[])
        validate(output, payload)


@pytest.mark.parametrize("problem", ["legacy", "order", "duplicate_check", "unknown_finding", "duplicate_finding", "undeclared_evidence", "fix_in_context", "false_pass", "false_block", "uncited", "not_applicable", "premature_prose", "evidence_array"])
def test_invalid_output_is_rejected_by_the_owning_validator(review_case, problem):
    _, validate, payload, output, _, context = review_case
    if problem in {"legacy", "order", "duplicate_check", "unknown_finding", "false_block", "not_applicable"}:
        if problem == "legacy": output["layer_disposition"] = output.pop("verdict")
        if problem == "order": output["check_results"][0], output["check_results"][1] = output["check_results"][1], output["check_results"][0]
        if problem == "duplicate_check": output["check_results"][1] = dict(output["check_results"][0])
        if problem == "unknown_finding": output["check_results"][0].update(disposition="finding", finding_ids=["absent"])
        if problem == "false_block": output["verdict"] = "blocked"
        if problem == "not_applicable": output["check_results"][0]["disposition"] = "not_applicable"
    else:
        output["verdict"] = "non_pass"
        output["findings"] = [_finding(review_case)]
        output["check_results"][0].update(disposition="finding", finding_ids=["gap"])
        output["check_results"][-1]["disposition"] = "not_run"
        if problem == "duplicate_finding": output["findings"].append(dict(output["findings"][0]))
        if problem == "undeclared_evidence": output["findings"][0]["evidence"]["source_ref"] = "not-supplied"
        if problem == "fix_in_context": output["findings"][0]["evidence"]["source_ref"] = context
        if problem == "false_pass": output["verdict"] = "passed"
        if problem == "uncited": output["findings"].append({**output["findings"][0], "finding_id": "uncited"})
        if problem == "premature_prose": output["check_results"][-1]["disposition"] = "passed"
        if problem == "evidence_array": output["findings"][0]["evidence"] = [output["findings"][0]["evidence"]]
    with pytest.raises((ValueError, ValidationError)):
        validate(output, payload)


def test_four_declarations_export_with_runtime_common_format():
    from agent_runtime import ModuleReviewer
    from agent_runtime.registry import (BehaviorPolicyReleaseCandidate, EvaluationPolicyReleaseCandidate,
        RetryPolicyReleaseCandidate, compile_behavior_policy_release, compile_evaluation_policy_release,
        compile_retry_policy_release)
    behavior = compile_behavior_policy_release(BehaviorPolicyReleaseCandidate(policy_id="workflow_execution_isolated", policy_version="v1", context_isolation="workflow_execution_isolated"))
    evaluation = compile_evaluation_policy_release(EvaluationPolicyReleaseCandidate(policy_id="module_candidate", policy_version="v1", evaluation_mode="module_candidate"))
    retry = compile_retry_policy_release(RetryPolicyReleaseCandidate(policy_id="bounded_candidate", policy_version="v1", max_attempts=3))
    for skill, module_id in (("the-design-authoring", "design_contract_reviewer"), ("the-skill-authoring", "skill_candidate_reviewer"), ("the-system-change", "system_change_plan_reviewer"), ("the-review-authoring", "reviewer_reviewer")):
        reviewer = ModuleReviewer.from_registration(ROOT, skill_id=skill, module_id=module_id)
        first = reviewer.export(module_version="format_test", behavior_policy=behavior, evaluation_policy=evaluation, retry_policy=retry, execution_profile=None)
        second = reviewer.export(module_version="format_test", behavior_policy=behavior, evaluation_policy=evaluation, retry_policy=retry, execution_profile=None)
        assert first.module_release.release_sha256 == second.module_release.release_sha256
        assert first.execution_profile is None
        assert first.execution_blocker_code is not None


@pytest.mark.parametrize("skill,module_id", [
    ("the-design-authoring", "design_contract_reviewer"),
    ("the-skill-authoring", "skill_candidate_reviewer"),
    ("the-system-change", "system_change_plan_reviewer"),
    ("the-review-authoring", "reviewer_reviewer"),
])
@pytest.mark.parametrize("provider", ["claude", "codex"])
def test_provider_projection_preserves_canonical_output_validation(skill, module_id, provider):
    from agent_runtime.invocation import invocation_schema_projection as projection

    path = ROOT / "09_soul/governance/skills" / skill / "runtime_modules" / module_id / "schemas/output.schema.json"
    canonical = json.loads(path.read_text())
    original = deepcopy(canonical)
    task_schema = projection.task_plane_output_schema(canonical)
    project = getattr(projection, provider + "_native_output_schema")
    native = project(task_schema)
    Draft202012Validator.check_schema(native)
    assert canonical == original
    ids = canonical["$defs"]["check_result"]["properties"]["check_id"]["enum"]
    output = {
        "verdict": "passed",
        "check_results": [
            {"check_id": check, "disposition": "passed", "assessment": "Evidence supports this check.", "finding_ids": []}
            for check in ids
        ],
        "findings": [],
        "safe_next_step": "Use the reviewed candidate.",
    }
    Draft202012Validator(canonical).validate(output)
    Draft202012Validator(native).validate(output)

    # Native schema projection relaxes uniqueItems. Canonical validation must
    # still reject repeated references after the provider returns an object.
    output["check_results"][0]["finding_ids"] = ["same", "same"]
    Draft202012Validator(native).validate(output)
    with pytest.raises(ValidationError, match="non-unique"):
        Draft202012Validator(canonical).validate(output)


@pytest.mark.parametrize("skill,module_id", [
    ("the-design-authoring", "design_contract_reviewer"),
    ("the-review-authoring", "reviewer_reviewer"),
])
def test_finding_identifiers_round_trip_into_existing_prior_findings(skill, module_id):
    source = ROOT / "09_soul/governance/skills" / skill / "runtime_modules" / module_id / "schemas"
    input_schema = json.loads((source / "input.schema.json").read_text())
    output_schema = json.loads((source / "output.schema.json").read_text())
    prior = input_schema["$defs"]["prior_finding"]
    identity = output_schema["$defs"]["finding"]["properties"]["finding_id"]
    reference = output_schema["$defs"]["check_result"]["properties"]["finding_ids"]["items"]
    assert identity["pattern"] == reference["pattern"] == prior["properties"]["finding_id"]["pattern"]
    for finding_id in ("f1", "boundary_gap", "peer.rule-2", "a" * 192):
        Draft202012Validator(identity).validate(finding_id)
        Draft202012Validator(reference).validate(finding_id)
        Draft202012Validator(prior).validate({
            "finding_id": finding_id, "disposition": "claimed_fixed", "body": "Current evidence for re-review.",
        })
    for finding_id in ("F1", "x", "a" * 193, "bad id"):
        with pytest.raises(ValidationError):
            Draft202012Validator(identity).validate(finding_id)
        with pytest.raises(ValidationError):
            Draft202012Validator(reference).validate(finding_id)
