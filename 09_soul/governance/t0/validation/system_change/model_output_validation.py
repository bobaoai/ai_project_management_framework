"""System Change-owned output checks, reusable without a project planner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator

MODULE_ROOT = Path(__file__).resolve().parents[3] / "skills/the-system-change/runtime_modules/system_change_plan_reviewer"
INPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/input.schema.json"
OUTPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/output.schema.json"
PROSE_CHECK_ID = "prose_and_meaning_preservation"


def validate_system_change_review_output(output: Mapping[str, object], semantic_input: Mapping[str, object]) -> None:
    Draft202012Validator(json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))).validate(dict(semantic_input))
    Draft202012Validator(json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))).validate(dict(output))
    required = [*semantic_input["required_check_ids"], PROSE_CHECK_ID]
    rows = output["check_results"]
    if [row["check_id"] for row in rows] != required:
        raise ValueError("System Change check coverage or order differs from the input")
    findings = {finding["finding_id"]: finding for finding in output["findings"]}
    if len(findings) != len(output["findings"]):
        raise ValueError("System Change findings repeat finding_id")
    actionable = {key for key, finding in findings.items() if finding["severity"] in {"block", "fix"}}
    candidate_ref = semantic_input["system_change_plan"]["document_id"]
    evidence_refs = {candidate_ref} | {row["document_id"] for row in semantic_input["governing_contract_closure"]}
    cited = set()
    for row in rows:
        refs = set(row["finding_ids"])
        if not refs <= set(findings):
            raise ValueError("System Change check cites an unknown finding")
        if bool(refs & actionable) != (row["disposition"] == "finding"):
            raise ValueError("System Change check disposition and findings disagree")
        if row["disposition"] == "not_applicable":
            raise ValueError("System Change checks cannot be not_applicable")
        if row["disposition"] == "not_run" and refs:
            raise ValueError("Unperformed System Change checks cannot cite findings")
        if row["disposition"] == "not_run" and row["check_id"] != PROSE_CHECK_ID and output["verdict"] != "blocked":
            raise ValueError("Unperformed System Change semantics require blocked")
        cited.update(refs & actionable)
    if cited != actionable:
        raise ValueError("Every actionable System Change finding must be covered")
    for finding in findings.values():
        if finding["evidence"]["source_ref"] not in evidence_refs:
            raise ValueError("System Change finding cites undeclared evidence")
        if finding["severity"] == "fix" and finding["evidence"]["source_ref"] != candidate_ref:
            raise ValueError("System Change fix must cite the current plan")
        if finding["severity"] in {"block", "fix"} and not any(
            row["check_id"] == finding["check_id"] and finding["finding_id"] in row["finding_ids"] for row in rows
        ):
            raise ValueError("System Change finding is not cited by its own check")
    semantic_incomplete = any(row["disposition"] != "passed" for row in rows[:-1])
    if semantic_incomplete != (rows[-1]["disposition"] == "not_run"):
        raise ValueError("System Change prose must follow completed semantic checks")
    expected = "blocked" if any(row["severity"] == "block" for row in findings.values()) else "non_pass" if actionable else "passed"
    if output["verdict"] != expected:
        raise ValueError("System Change verdict and findings disagree")


__all__ = ["validate_system_change_review_output"]
