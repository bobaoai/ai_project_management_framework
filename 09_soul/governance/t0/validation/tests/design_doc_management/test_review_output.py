from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

import pytest


MODULE_PATH = Path(__file__).resolve().parents[2] / "artifact_contracts/design_review_output.py"
SPEC = importlib.util.spec_from_file_location("ddm_output_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def review_input() -> dict:
    return {
        "required_check_ids": list(validator.REQUIRED_CHECK_IDS),
        "candidate_documents": [{"document_id": "candidate_design", "owner_ref": "designDoc/candidate.md"}],
        "context_documents": [
            {"document_id": "peer_design", "owner_ref": "designDoc/peer.md", "context_role": "peer_contract"},
            {"document_id": "inspection", "owner_ref": "code", "context_role": "current_inspection"},
        ],
    }


def passed_output() -> dict:
    return {
        "verdict": "passed",
        "check_results": [
            {"check_id": check_id, "disposition": "passed", "assessment": "Verified against the supplied candidate.", "finding_ids": []}
            for check_id in validator.REQUIRED_CHECK_IDS
        ],
        "findings": [],
        "safe_next_step": "Use the reviewed candidate within existing authorization.",
    }


def output_with_finding(severity: str = "fix") -> dict:
    value = passed_output()
    value["verdict"] = "blocked" if severity == "block" else "non_pass"
    value["findings"] = [{
        "finding_id": "boundary_gap", "severity": severity, "finding_class": "boundary_ambiguity",
        "affected_candidate_document_id": "candidate_design",
        "correction_target_document_id": "candidate_design",
        "evidence": {"source_ref": "candidate_design", "locator": "Boundaries", "observation": "Two owners can write the same record."},
        "requirement": "The write responsibility must be unambiguous.",
        "impact": "The caller cannot identify the authorized writer.",
        "accountable_owner_ref": "designDoc/candidate.md",
        "required_change": "Make the intended writer responsibility clear.",
    }]
    for row in value["check_results"]:
        if row["check_id"] == "boundary_coherence":
            row.update(disposition="finding", finding_ids=["boundary_gap"])
        if row["check_id"] == "prose_and_meaning_preservation":
            row.update(disposition="not_run", assessment="Semantic judgment is unresolved.")
    return value


def test_passed_output_is_accepted() -> None:
    validator.validate_design_contract_review_output(passed_output(), review_input())


def test_one_root_cause_can_be_cited_by_multiple_checks() -> None:
    value = output_with_finding()
    row = next(x for x in value["check_results"] if x["check_id"] == "peer_authority_and_inheritance")
    row.update(disposition="finding", finding_ids=["boundary_gap"])
    validator.validate_design_contract_review_output(value, review_input())
    assert len(value["findings"]) == 1


def test_known_fix_cannot_target_an_unreviewed_peer() -> None:
    value = output_with_finding()
    value["findings"][0].update(correction_target_document_id="peer_design", accountable_owner_ref="designDoc/peer.md")
    with pytest.raises(ValueError, match="fix must target a candidate"):
        validator.validate_design_contract_review_output(value, review_input())


def test_missing_peer_decision_can_be_returned_as_blocked() -> None:
    value = output_with_finding("block")
    value["findings"][0].update(correction_target_document_id="peer_design", accountable_owner_ref="designDoc/peer.md")
    validator.validate_design_contract_review_output(value, review_input())


def test_block_cannot_be_reported_as_non_pass() -> None:
    value = output_with_finding("block")
    value["verdict"] = "non_pass"
    with pytest.raises(ValueError, match="block finding requires blocked verdict"):
        validator.validate_design_contract_review_output(value, review_input())


def test_passed_cannot_carry_a_fix() -> None:
    value = output_with_finding()
    value["verdict"] = "passed"
    with pytest.raises(ValueError, match="passed verdict cannot carry"):
        validator.validate_design_contract_review_output(value, review_input())


def test_note_does_not_prevent_pass() -> None:
    value = passed_output()
    note = output_with_finding()["findings"][0]
    note["severity"] = "note"
    value["findings"] = [note]
    validator.validate_design_contract_review_output(value, review_input())


@pytest.mark.parametrize("check_id", ["intent_and_reader_result", "prose_and_meaning_preservation"])
def test_passed_check_may_cite_a_note_without_rewriting_output(check_id: str) -> None:
    value = passed_output()
    note = output_with_finding()["findings"][0]
    note["severity"] = "note"
    value["findings"] = [note]
    row = next(x for x in value["check_results"] if x["check_id"] == check_id)
    row["finding_ids"] = [note["finding_id"]]
    before = deepcopy(value)
    validator.validate_design_contract_review_output(value, review_input())
    assert value == before


@pytest.mark.parametrize("severity", ["fix", "block"])
def test_passed_check_cannot_cite_actionable_findings(severity: str) -> None:
    value = output_with_finding(severity)
    value["check_results"][0]["finding_ids"] = [value["findings"][0]["finding_id"]]
    with pytest.raises(ValueError, match="passed design check can only cite note"):
        validator.validate_design_contract_review_output(value, review_input())


def test_note_on_passed_check_does_not_hide_another_checks_fix() -> None:
    value = output_with_finding()
    note = {**value["findings"][0], "finding_id": "optional_wording", "severity": "note"}
    value["findings"].append(note)
    value["check_results"][0]["finding_ids"] = [note["finding_id"]]
    validator.validate_design_contract_review_output(value, review_input())
    assert value["verdict"] == "non_pass"


def test_passed_check_cannot_cite_an_unknown_note() -> None:
    value = passed_output()
    value["check_results"][0]["finding_ids"] = ["unknown_note"]
    with pytest.raises(ValueError, match="unknown finding_ids"):
        validator.validate_design_contract_review_output(value, review_input())


def test_not_run_check_cannot_cite_a_note() -> None:
    value = output_with_finding()
    note = {**value["findings"][0], "finding_id": "optional_wording", "severity": "note"}
    value["findings"].append(note)
    value["check_results"][-1]["finding_ids"] = [note["finding_id"]]
    with pytest.raises(ValueError, match="not_run prose check cannot cite findings"):
        validator.validate_design_contract_review_output(value, review_input())


def test_note_cannot_make_a_check_fail() -> None:
    value = output_with_finding()
    value["findings"][0]["severity"] = "note"
    with pytest.raises(ValueError, match="requires actionable findings"):
        validator.validate_design_contract_review_output(value, review_input())


@pytest.mark.parametrize("mutation,match", [
    ("unknown_finding", "unknown finding_ids"),
    ("duplicate_finding", "repeat finding_id"),
    ("wrong_candidate", "non-candidate"),
    ("wrong_owner", "crossed the correction owner"),
    ("evidence_target", "non-authoritative context"),
    ("premature_prose", "require prose check not_run"),
])
def test_invalid_review_binding_is_rejected(mutation: str, match: str) -> None:
    value = output_with_finding()
    if mutation == "unknown_finding":
        next(x for x in value["check_results"] if x["disposition"] == "finding")["finding_ids"] = ["missing_id"]
    elif mutation == "duplicate_finding":
        value["findings"].append(deepcopy(value["findings"][0]))
    elif mutation == "wrong_candidate":
        value["findings"][0]["affected_candidate_document_id"] = "peer_design"
    elif mutation == "wrong_owner":
        value["findings"][0]["accountable_owner_ref"] = "designDoc/another.md"
    elif mutation == "evidence_target":
        value["findings"][0].update(correction_target_document_id="inspection", accountable_owner_ref="code")
    elif mutation == "premature_prose":
        value["check_results"][-1]["disposition"] = "passed"
    with pytest.raises(ValueError, match=match):
        validator.validate_design_contract_review_output(value, review_input())


def test_pass_requires_completed_prose_check() -> None:
    value = passed_output()
    value["check_results"][-1]["disposition"] = "not_run"
    with pytest.raises(ValueError, match="cannot be not_run after semantics pass"):
        validator.validate_design_contract_review_output(value, review_input())


def test_finding_cannot_cite_an_undeclared_evidence_source() -> None:
    value = output_with_finding()
    value["findings"][0]["evidence"]["source_ref"] = "not_supplied"
    with pytest.raises(ValueError, match="undeclared evidence source"):
        validator.validate_design_contract_review_output(value, review_input())


def test_design_check_cannot_be_skipped_as_not_applicable() -> None:
    value = passed_output()
    value["check_results"][0]["disposition"] = "not_applicable"
    with pytest.raises(ValueError, match="cannot be marked not_applicable"):
        validator.validate_design_contract_review_output(value, review_input())
