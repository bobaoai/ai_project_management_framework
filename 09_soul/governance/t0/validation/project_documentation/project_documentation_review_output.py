"""Project Documentation-owned checks for one project_documentation_reviewer result.

The Reviewer judges the documents; this code checks what the prompt assigns to
the host: schema validity, exact check coverage and order, which dispositions
each check may use, finding references and coverage, cited material and the
verdict that the findings imply.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator

MODULE_ROOT = (Path(__file__).resolve().parents[3]
               / "skills/project-documentation-authoring/runtime_modules/project_documentation_reviewer")
INPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/input.schema.json"
OUTPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/output.schema.json"
PROSE_CHECK_ID = "prose_and_meaning_preservation"
# The only semantic check that may be not_applicable, under the prompt's section 4 condition.
OPTIONAL_CHECK_ID = "technical_and_cross_document_coherence"
ACTIONABLE = frozenset({"block", "fix"})
# Purposes whose documents are technical by definition; the check always applies to them.
TECHNICAL_PURPOSES = frozenset({"solution_design", "technical_design"})


def validate_project_documentation_review_output(output: Mapping[str, object],
                                                  semantic_input: Mapping[str, object]) -> None:
    """Raise ValueError (or a jsonschema error) when the result breaks the host-checked contract."""
    Draft202012Validator(json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))).validate(dict(semantic_input))
    Draft202012Validator(json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))).validate(dict(output))
    candidates = semantic_input["candidate_documents"]
    documents = [*candidates, *semantic_input["context_documents"]]
    declared = [document["document_ref"] for document in documents]
    candidate_refs = {document["document_ref"] for document in candidates}
    # Decidable part of the prompt's condition: a group always has cross-document content, and a formal
    # Design or a technical purpose always has technical content. Whether any other single document is
    # pure business without such content is the Reviewer's judgment.
    technical_check_may_be_skipped = (len(candidates) == 1 and not candidates[0]["formal_design"]
                                      and candidates[0]["purpose"] not in TECHNICAL_PURPOSES)
    if len(set(declared)) != len(declared):
        raise ValueError("Project Documentation input repeats a document_ref")
    rows = output["check_results"]
    if [row["check_id"] for row in rows] != list(semantic_input["required_check_ids"]):
        raise ValueError("Project Documentation check coverage or order differs from the input")
    findings = {finding["finding_id"]: finding for finding in output["findings"]}
    if len(findings) != len(output["findings"]):
        raise ValueError("Project Documentation findings repeat finding_id")
    actionable = {key for key, finding in findings.items() if finding["severity"] in ACTIONABLE}
    rows_by_check = {row["check_id"]: row for row in rows}
    semantic_rows, prose_row = rows[:-1], rows[-1]
    if prose_row["check_id"] != PROSE_CHECK_ID:
        raise ValueError("Project Documentation prose check must be last")
    cited = set()
    for row in rows:
        refs = set(row["finding_ids"])
        if not refs <= set(findings):
            raise ValueError(f"Project Documentation check {row['check_id']} cites an unknown finding")
        if (row["disposition"] == "finding") != bool(refs & actionable):
            raise ValueError(f"Project Documentation check {row['check_id']} disposition and findings disagree")
        cited.update(refs)
    for row in semantic_rows:
        allowed = {"passed", "finding"} | ({"not_applicable"} if row["check_id"] == OPTIONAL_CHECK_ID else set())
        if row["disposition"] not in allowed:
            raise ValueError(f"Project Documentation semantic check {row['check_id']} cannot be {row['disposition']}")
        if row["disposition"] == "not_applicable" and not technical_check_may_be_skipped:
            raise ValueError(f"{OPTIONAL_CHECK_ID} can be not_applicable only for one non-Design candidate "
                             "without a technical purpose")
    semantic_complete = all(row["disposition"] in {"passed", "not_applicable"} for row in semantic_rows)
    if semantic_complete:
        if prose_row["disposition"] not in {"passed", "finding"}:
            raise ValueError("Project Documentation prose check must run after completed semantic checks")
    elif prose_row["disposition"] != "not_run" or prose_row["finding_ids"]:
        raise ValueError("Project Documentation prose check must be not_run without findings until semantics pass")
    if not actionable <= cited:
        raise ValueError("Every actionable Project Documentation finding must be covered by a check")
    for finding_id, finding in findings.items():
        if finding_id not in rows_by_check[finding["check_id"]]["finding_ids"]:
            raise ValueError(f"Finding {finding_id} is not cited by its own check {finding['check_id']}")
        if finding["evidence"]["source_ref"] not in declared:
            raise ValueError(f"Finding {finding_id} cites undeclared material")
        if finding["severity"] == "fix" and finding["evidence"]["source_ref"] not in candidate_refs:
            raise ValueError(f"Fix {finding_id} must cite a candidate document, not only background")
    expected = ("blocked" if any(finding["severity"] == "block" for finding in findings.values())
                else "non_pass" if actionable else "passed")
    if output["verdict"] != expected:
        raise ValueError("Project Documentation verdict and findings disagree")


__all__ = ["validate_project_documentation_review_output"]
