"""Review Contract-owned checks for one Reviewer prompt review result."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator

MODULE_ROOT = Path(__file__).resolve().parents[3] / "skills/the-review-authoring/runtime_modules/reviewer_reviewer"
INPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/input.schema.json"
OUTPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/output.schema.json"
PROSE_CHECK_ID = "prose_and_meaning_preservation"


def validate_reviewer_prompt_review_output(output: Mapping[str, object], semantic_input: Mapping[str, object]) -> None:
    Draft202012Validator(json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))).validate(dict(semantic_input))
    Draft202012Validator(json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))).validate(dict(output))
    required = [*semantic_input["required_check_ids"], PROSE_CHECK_ID]
    rows = output["check_results"]
    if [row["check_id"] for row in rows] != required:
        raise ValueError("Reviewer prompt check coverage or order differs from the input")
    findings = {finding["finding_id"]: finding for finding in output["findings"]}
    if len(findings) != len(output["findings"]):
        raise ValueError("Reviewer prompt findings repeat finding_id")
    actionable = {key for key, finding in findings.items() if finding["severity"] in {"block", "fix"}}
    candidate_ref = semantic_input["prompt_candidate"]["artifact_ref"]
    evidence_refs = {semantic_input[name]["artifact_ref"] for name in (
        "prompt_candidate", "target_design_contract", "target_reviewer_input_schema", "target_reviewer_output_schema",
    )} | {fixture["fixture_ref"] for fixture in semantic_input["fixtures"]}
    cited = set()
    for row in rows:
        refs = set(row["finding_ids"])
        if not refs <= set(findings):
            raise ValueError("Reviewer prompt check cites an unknown finding")
        if bool(refs & actionable) != (row["disposition"] == "finding"):
            raise ValueError("Reviewer prompt check disposition and findings disagree")
        if row["disposition"] == "not_applicable":
            raise ValueError("Reviewer prompt checks cannot be not_applicable")
        if row["disposition"] == "not_run" and refs:
            raise ValueError("Unperformed Reviewer prompt checks cannot cite findings")
        if row["disposition"] == "not_run" and row["check_id"] != PROSE_CHECK_ID and output["verdict"] != "blocked":
            raise ValueError("Unperformed Reviewer prompt semantics require blocked")
        cited.update(refs & actionable)
    if cited != actionable:
        raise ValueError("Every actionable Reviewer prompt finding must be covered")
    for finding in findings.values():
        if finding["evidence"]["source_ref"] not in evidence_refs:
            raise ValueError("Reviewer prompt finding cites undeclared evidence")
        if finding["severity"] == "fix" and finding["evidence"]["source_ref"] != candidate_ref:
            raise ValueError("Reviewer prompt fix must cite the current prompt")
    semantic_incomplete = any(row["disposition"] != "passed" for row in rows[:-1])
    if semantic_incomplete != (rows[-1]["disposition"] == "not_run"):
        raise ValueError("Reviewer prompt prose must follow completed semantic checks")
    expected = "blocked" if any(row["severity"] == "block" for row in findings.values()) else "non_pass" if actionable else "passed"
    if output["verdict"] != expected:
        raise ValueError("Reviewer prompt verdict and findings disagree")


__all__ = ["validate_reviewer_prompt_review_output"]
