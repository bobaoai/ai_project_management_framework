"""Host-checked rules for project_documentation_reviewer results."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

import pytest

SPEC = importlib.util.spec_from_file_location(
    "portable_project_documentation_review_output",
    Path(__file__).resolve().parents[2] / "project_documentation/project_documentation_review_output.py")
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

CHECKS = ["reader_task_and_stage", "problem_scope_and_outcome", "business_meaning_and_evidence",
          "solution_reasoning_and_tradeoffs", "behavior_flow_and_handoff", "technical_and_cross_document_coherence",
          "project_adaptation_and_actual_state", "completion_failure_and_next_action", "prose_and_meaning_preservation"]


def pd_input(purpose="solution_design", formal_design=False):
    return {"schema_version": "project_documentation_reviewer_input_v1",
            "review_request": {"goal": "Decide the next project step", "change_scope": "First solution draft"},
            "candidate_documents": [{"document_ref": "candidate:plan", "owner_ref": "project_owner", "title": "Plan",
                                     "body": "The plan body.", "purpose": purpose,
                                     "reader_action": "approve the design", "project_stage": "design",
                                     "formal_design": formal_design}],
            "context_documents": [{"document_ref": "context:brief", "owner_ref": "business_owner",
                                   "title": "Brief", "body": "Business context."}],
            "prior_findings": [], "required_check_ids": list(CHECKS)}


def passed_output():
    return {"verdict": "passed", "findings": [], "safe_next_step": "Use the reviewed document.",
            "check_results": [{"check_id": check, "disposition": "passed",
                               "assessment": "Checked at the cited section.", "finding_ids": []} for check in CHECKS]}


def finding(finding_id, severity, check_id, source="candidate:plan"):
    return {"finding_id": finding_id, "severity": severity, "check_id": check_id,
            "evidence": {"source_ref": source, "locator": "section 2", "observation": "What the reader sees."},
            "requirement": "The applicable requirement.", "impact": "The wrong action a reader takes.",
            "accountable_owner_ref": "project_owner", "required_change": "The result to restore."}


def with_finding(severity="fix", check_index=2, verdict=None):
    output = passed_output()
    check = CHECKS[check_index]
    output["findings"] = [finding("F1", severity, check)]
    row = output["check_results"][check_index]
    if severity in {"fix", "block"}:
        row["disposition"] = "finding"
        output["check_results"][-1].update(disposition="not_run", finding_ids=[])
    row["finding_ids"] = ["F1"]
    output["verdict"] = verdict or {"fix": "non_pass", "block": "blocked", "note": "passed"}[severity]
    return output


def check(output, semantic_input=None):
    validator.validate_project_documentation_review_output(output, semantic_input or pd_input())


@pytest.mark.deterministic
@pytest.mark.parametrize("output", [passed_output(), with_finding("fix"), with_finding("block"), with_finding("note")],
                         ids=["passed", "non_pass", "blocked", "note_on_passed_check"])
def test_consistent_results_pass(output):
    check(output)


@pytest.mark.deterministic
@pytest.mark.parametrize("purpose", ["business_proposal", "project_update", "operating_instruction"])
def test_the_technical_check_may_be_not_applicable_for_one_non_technical_candidate(purpose):
    """Whether the document is pure business is left to the Reviewer; the host does not reject it."""
    output = passed_output()
    output["check_results"][5]["disposition"] = "not_applicable"
    check(output, pd_input(purpose=purpose))


@pytest.mark.deterministic
@pytest.mark.parametrize("semantic_input", [
    pd_input(purpose="technical_design"), pd_input(purpose="solution_design"),
    pd_input(purpose="business_proposal", formal_design=True),
    {**pd_input(purpose="business_proposal"), "candidate_documents": [
        pd_input(purpose="business_proposal")["candidate_documents"][0],
        {**pd_input(purpose="business_proposal")["candidate_documents"][0], "document_ref": "candidate:second"}]},
], ids=["technical_design", "solution_design", "formal_design", "two_candidates"])
def test_the_technical_check_cannot_be_skipped_when_the_input_shows_technical_or_group_content(semantic_input):
    output = passed_output()
    output["check_results"][5]["disposition"] = "not_applicable"
    with pytest.raises(ValueError, match="can be not_applicable only for one non-Design candidate"):
        check(output, semantic_input)


@pytest.mark.deterministic
def test_a_fix_must_cite_a_candidate_while_a_block_may_cite_background():
    fix = with_finding("fix")
    fix["findings"][0]["evidence"]["source_ref"] = "context:brief"
    with pytest.raises(ValueError, match="must cite a candidate document"):
        check(fix)
    block = with_finding("block")
    block["findings"][0]["evidence"]["source_ref"] = "context:brief"
    check(block)


@pytest.mark.deterministic
@pytest.mark.parametrize("mutate,message", [
    (lambda o, i: o["check_results"].reverse(), "coverage or order"),
    (lambda o, i: o["check_results"][0].update(disposition="not_applicable"), "cannot be not_applicable"),
    (lambda o, i: o["check_results"][3].update(disposition="not_run"), "cannot be not_run"),
    (lambda o, i: o["check_results"][-1].update(disposition="not_run"), "must run after completed semantic checks"),
    (lambda o, i: o["check_results"][0].update(finding_ids=["missing"]), "unknown finding"),
    (lambda o, i: o["check_results"][0].update(disposition="finding"), "disposition and findings disagree"),
    (lambda o, i: o.update(verdict="non_pass"), "verdict and findings disagree"),
    (lambda o, i: i["context_documents"].append(
        {"document_ref": "candidate:plan", "owner_ref": "o", "title": "t", "body": "b"}), "repeats a document_ref"),
])
def test_inconsistent_results_are_rejected(mutate, message):
    output, semantic_input = passed_output(), pd_input()
    mutate(output, semantic_input)
    with pytest.raises(ValueError, match=message):
        check(output, semantic_input)


@pytest.mark.deterministic
def test_prose_must_wait_while_a_semantic_check_has_a_finding():
    output = with_finding("fix")
    output["check_results"][-1].update(disposition="passed")
    with pytest.raises(ValueError, match="must be not_run without findings"):
        check(output)


@pytest.mark.deterministic
def test_a_note_alone_cannot_make_a_check_a_finding():
    output = with_finding("note")
    output["check_results"][2]["disposition"] = "finding"
    with pytest.raises(ValueError, match="disposition and findings disagree"):
        check(output)


@pytest.mark.deterministic
def test_a_finding_must_be_cited_by_its_own_check():
    output = with_finding("fix", check_index=2)
    output["findings"][0]["check_id"] = CHECKS[4]
    with pytest.raises(ValueError, match="not cited by its own check"):
        check(output)


@pytest.mark.deterministic
def test_a_finding_must_cite_declared_material():
    output = with_finding("fix")
    output["findings"][0]["evidence"]["source_ref"] = "undeclared:note"
    with pytest.raises(ValueError, match="undeclared material"):
        check(output)


@pytest.mark.deterministic
def test_a_fixed_verdict_cannot_hide_a_block():
    output = with_finding("block")
    output["verdict"] = "non_pass"
    with pytest.raises(ValueError, match="verdict and findings disagree"):
        check(output)
