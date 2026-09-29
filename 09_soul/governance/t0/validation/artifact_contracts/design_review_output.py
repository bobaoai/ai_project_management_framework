"""DDM-owned consistency checks for one Design Reviewer output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from jsonschema import Draft202012Validator

MODULE_ROOT = (
    Path(__file__).resolve().parents[3]
    / "skills/the-design-authoring/runtime_modules/design_contract_reviewer"
)
OUTPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/output.schema.json"
INPUT_SCHEMA_PATH = MODULE_ROOT / "schemas/input.schema.json"
_CONTRACT_PATH = Path(__file__).with_name("design_artifact_contract.json")
REQUIRED_CHECK_IDS = tuple(
    item["check_id"]
    for item in json.loads(_CONTRACT_PATH.read_text(encoding="utf-8"))["reviewer_checklist"]["checks"]
)
CONTEXT_ROLES = tuple(
    json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))["$defs"]["context_document"]["properties"]["context_role"]["enum"]
)
EVIDENCE_ONLY_CONTEXT_ROLES = frozenset(
    {"code_projection", "current_inspection", "design_migration_inventory"}
)
ALLOWED_CONTEXT_CORRECTION_ROLES = frozenset(CONTEXT_ROLES) - EVIDENCE_ONLY_CONTEXT_ROLES
VERDICT_PASSED = "passed"
VERDICT_NON_PASS = "non_pass"
VERDICT_BLOCKED = "blocked"


def validate_design_contract_review_output(
    output: Mapping[str, object],
    semantic_input: Mapping[str, object],
    *,
    schema_path: Path = OUTPUT_SCHEMA_PATH,
) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(dict(output))

    findings = output["findings"]
    check_results = output["check_results"]
    required_checks = semantic_input.get("required_check_ids")
    candidate_documents = semantic_input.get("candidate_documents")
    if not isinstance(findings, list) or not isinstance(check_results, list):
        raise ValueError("design review output collections must be arrays")
    if not isinstance(required_checks, list) or not required_checks:
        raise ValueError("design review input lacks required checks")
    if tuple(required_checks) != REQUIRED_CHECK_IDS:
        raise ValueError(
            "design review input lacks the complete ordered v6 checks"
        )
    if not isinstance(candidate_documents, list) or not candidate_documents:
        raise ValueError("design review input lacks candidate documents")

    finding_by_id = {
        finding["finding_id"]: finding
        for finding in findings
        if isinstance(finding, dict)
    }
    if len(finding_by_id) != len(findings):
        raise ValueError("design review findings repeat finding_id")

    candidate_owner_by_id = {
        document["document_id"]: document["owner_ref"]
        for document in candidate_documents
        if isinstance(document, dict)
    }
    context_documents = semantic_input.get("context_documents")
    if not isinstance(context_documents, list) or not context_documents:
        raise ValueError("design review input lacks context documents")
    context_owner_by_id = {
        document["document_id"]: document["owner_ref"]
        for document in context_documents
        if isinstance(document, dict)
    }
    context_role_by_id = {
        document["document_id"]: document.get("context_role")
        for document in context_documents
        if isinstance(document, dict)
    }
    candidate_ids = set(candidate_owner_by_id)
    evidence_ids = candidate_ids | set(context_owner_by_id)
    if any(finding["evidence"]["source_ref"] not in evidence_ids for finding in finding_by_id.values()):
        raise ValueError("design finding cites an undeclared evidence source")
    correction_owner_by_id = {
        **candidate_owner_by_id,
        **context_owner_by_id,
    }
    if any(
        finding["affected_candidate_document_id"] not in candidate_ids
        for finding in finding_by_id.values()
    ):
        raise ValueError(
            "design review finding affects a non-candidate document"
        )
    if any(
        finding["correction_target_document_id"] not in correction_owner_by_id
        for finding in finding_by_id.values()
    ):
        raise ValueError(
            "design review finding names an unknown correction target"
        )
    if any(
        target_id in context_role_by_id
        and context_role_by_id[target_id]
        not in ALLOWED_CONTEXT_CORRECTION_ROLES
        for target_id in (
            finding["correction_target_document_id"]
            for finding in finding_by_id.values()
        )
    ):
        raise ValueError(
            "design review finding targets a non-authoritative context role"
        )
    if any(
        finding["accountable_owner_ref"]
        != correction_owner_by_id[finding["correction_target_document_id"]]
        for finding in finding_by_id.values()
    ):
        raise ValueError("design review finding crossed the correction owner route")

    result_by_id = {
        result["check_id"]: result
        for result in check_results
        if isinstance(result, dict)
    }
    if len(result_by_id) != len(check_results):
        raise ValueError("design review check_results repeat check_id")
    observed_check_order = tuple(
        result["check_id"]
        for result in check_results
        if isinstance(result, dict)
    )
    if observed_check_order != tuple(required_checks):
        raise ValueError("design review check_results order differs from the profile")

    cited_actionable_findings: set[str] = set()
    for result in result_by_id.values():
        finding_ids = result["finding_ids"]
        if result["disposition"] == "not_applicable":
            raise ValueError("Design checks cannot be marked not_applicable")
        if result["disposition"] == "not_run":
            if result["check_id"] != "prose_and_meaning_preservation":
                raise ValueError("only the prose design check may be not_run")
            if finding_ids:
                raise ValueError("not_run prose check cannot cite findings")
        unknown = set(finding_ids) - set(finding_by_id)
        if unknown:
            raise ValueError("design check cites unknown finding_ids")
        actionable = {
            finding_id for finding_id in finding_ids
            if finding_by_id[finding_id]["severity"] in {"block", "fix"}
        }
        if result["disposition"] == "finding" and not actionable:
            raise ValueError("failed design check requires actionable findings")
        for finding_id in finding_ids:
            severity = finding_by_id[finding_id]["severity"]
            if result["disposition"] == "passed":
                if severity != "note":
                    raise ValueError("passed design check can only cite note findings")
            elif severity in {"block", "fix"}:
                cited_actionable_findings.add(finding_id)

    for finding in finding_by_id.values():
        if (
            finding["severity"] == "fix"
            and finding["correction_target_document_id"] not in candidate_ids
        ):
            raise ValueError("fix must target a candidate in the reviewed scope")

    prose_result = result_by_id["prose_and_meaning_preservation"]
    semantic_results = tuple(
        result_by_id[check_id]
        for check_id in REQUIRED_CHECK_IDS[:-1]
    )
    semantic_failed = any(
        result["disposition"] == "finding" for result in semantic_results
    )
    if semantic_failed and prose_result["disposition"] != "not_run":
        raise ValueError("failed semantic checks require prose check not_run")
    if not semantic_failed and prose_result["disposition"] == "not_run":
        raise ValueError("prose check cannot be not_run after semantics pass")

    actionable_findings = {
        finding_id
        for finding_id, finding in finding_by_id.items()
        if finding["severity"] in {"block", "fix"}
    }
    if cited_actionable_findings != actionable_findings:
        raise ValueError("every actionable design finding must map to a required check")

    severities = {finding["severity"] for finding in finding_by_id.values()}
    verdict = output["verdict"]
    if verdict == VERDICT_PASSED and severities.intersection({"block", "fix"}):
        raise ValueError("passed verdict cannot carry block or fix findings")
    if verdict == VERDICT_PASSED and any(
        result["disposition"] != "passed" for result in result_by_id.values()
    ):
        raise ValueError("passed verdict requires every design check to pass")
    if verdict == VERDICT_NON_PASS and not severities.intersection(
        {"block", "fix"}
    ):
        raise ValueError("non_pass verdict requires an actionable finding")
    if "block" in severities and verdict != VERDICT_BLOCKED:
        raise ValueError("block finding requires blocked verdict")
    if verdict == VERDICT_BLOCKED and "block" not in severities:
        raise ValueError("blocked verdict requires a block finding")
