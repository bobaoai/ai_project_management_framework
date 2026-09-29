"""Validate the existing Skill Reviewer's output against its actual input."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


MODULE_ROOT = Path(__file__).resolve().parents[3] / "skills/the-skill-authoring/runtime_modules/skill_candidate_reviewer"
OUTPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/output.schema.json"
REQUIRED_CHECK_IDS = tuple(
    row["check_id"] for row in json.loads(
        Path(__file__).with_name("skill_artifact_contract.json").read_text(encoding="utf-8")
    )["reviewer_checklist"]["checks"]
)


def validate_skill_review_output(output, semantic_input, *, schema_path=OUTPUT_SCHEMA_PATH):
    if not isinstance(output, dict):
        raise ValueError("Skill Reviewer output must be one object")
    Draft202012Validator(json.loads(Path(schema_path).read_text(encoding="utf-8"))).validate(output)
    semantic_ids = semantic_input["required_check_ids"]
    if tuple(semantic_ids) != REQUIRED_CHECK_IDS:
        raise ValueError("Skill input does not contain the complete ordered semantic checks")
    required = [*semantic_ids, "prose_and_meaning_preservation"]
    rows = output["check_results"]
    if [row["check_id"] for row in rows] != required:
        raise ValueError("Skill check coverage or order differs from the input")
    findings = {finding["finding_id"]: finding for finding in output["findings"]}
    if len(findings) != len(output["findings"]):
        raise ValueError("Skill findings repeat an identity")
    actionable = {key for key, finding in findings.items() if finding["severity"] in {"block", "fix"}}
    cited = set()
    candidate_ref = semantic_input["skill_candidate"]["skill_id"]
    evidence_refs = {candidate_ref}
    for name in ("owning_design_closure", "source_and_projection_closure"):
        evidence_refs.update(document["document_id"] for document in semantic_input[name])
    for row in rows:
        references = set(row["finding_ids"])
        if not references <= set(findings):
            raise ValueError("Skill check cites an unknown finding")
        if bool(references & actionable) != (row["disposition"] == "finding"):
            raise ValueError("Skill check disposition and findings disagree")
        if row["disposition"] in {"not_applicable", "not_run"} and references:
            raise ValueError("Unperformed Skill checks cannot cite findings")
        if row["disposition"] == "not_run" and row["check_id"] != required[-1]:
            raise ValueError("Only the Skill prose check may be not_run")
        if row["disposition"] == "not_applicable" and (
            row["check_id"] != semantic_ids[-1]
            or semantic_input["skill_candidate"]["runtime_ready_prompts"]
        ):
            raise ValueError("Declared prompt cannot be marked not_applicable")
        cited.update(references & actionable)
    if cited != actionable:
        raise ValueError("An actionable Skill finding is not covered by a check")
    for finding in findings.values():
        if finding["evidence"]["source_ref"] not in evidence_refs:
            raise ValueError("Skill finding cites an undeclared evidence source")
        if finding["severity"] == "fix" and finding["evidence"]["source_ref"] != candidate_ref:
            raise ValueError("Skill fix must cite the current candidate")
        if finding["severity"] in {"block", "fix"} and not any(
            row["check_id"] == finding["check_id"] and finding["finding_id"] in row["finding_ids"]
            for row in rows
        ):
            raise ValueError("Skill finding is not cited by its own check")
    expected = (
        "blocked" if any(item["severity"] == "block" for item in findings.values())
        else "non_pass" if actionable else "passed"
    )
    semantic_failed = any(row["disposition"] == "finding" for row in rows[:-1])
    if semantic_failed and rows[-1]["disposition"] != "not_run":
        raise ValueError("Skill semantic findings require prose not_run")
    if not semantic_failed and rows[-1]["disposition"] == "not_run":
        raise ValueError("Skill prose must run after semantic checks pass")
    if rows[-1]["disposition"] == "not_applicable":
        raise ValueError("Skill prose cannot be not_applicable")
    if output["verdict"] != expected:
        raise ValueError("Skill verdict and finding labels disagree")
