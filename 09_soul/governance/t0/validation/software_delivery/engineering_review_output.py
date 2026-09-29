"""Validate Engineering Reviewer output against Software Delivery meaning."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Mapping

from jsonschema import Draft202012Validator, SchemaError, ValidationError


ENGINEERING_REVIEW_RESULT_INVALID = "ENGINEERING_REVIEW_RESULT_INVALID"
OUTPUT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[5]
    / "09_soul/governance/skills/engineering-change-review/runtime_modules"
    / "engineering_change_reviewer/schemas/output.schema.json"
)


class EngineeringReviewOutputError(ValueError):
    """One invalid Engineering Reviewer result."""

    error_code = ENGINEERING_REVIEW_RESULT_INVALID


def engineering_check_ids(read=Path.read_bytes) -> tuple[str, ...]:
    """Read the existing numbered checklist from its Portable authority."""
    authority = read(Path(__file__).resolve().parents[2] / "the_software_delivery.md").decode("utf-8")
    start = "<!-- engineering-change-review-checklist:start -->"
    end = "<!-- engineering-change-review-checklist:end -->"
    if authority.count(start) != 1 or authority.count(end) != 1 or authority.index(start) >= authority.index(end):
        raise EngineeringReviewOutputError("Software Delivery checklist is unavailable or ambiguous")
    checklist = authority.split(start, 1)[1].split(end, 1)[0]
    ids = tuple(re.findall(r"^(\d+)\. ", checklist, re.MULTILINE))
    if not ids or ids != tuple(str(i) for i in range(1, len(ids) + 1)):
        raise EngineeringReviewOutputError("Software Delivery checklist numbering is invalid")
    return ids


def validate_engineering_reviewer_identity(record: Mapping[str, object]) -> None:
    """Accept either execution identity form, but reject contradictory evidence."""
    if not isinstance(record, Mapping):
        raise EngineeringReviewOutputError("Execution record must be an object")
    identity = record.get("module_id")
    release = record.get("module_release_ref")
    prefix = "runtime-module:engineering_change_reviewer@"
    if identity is not None and identity != "engineering_change_reviewer":
        raise EngineeringReviewOutputError("Execution record belongs to another Reviewer")
    if release is not None and (
        not isinstance(release, str) or not release.startswith(prefix) or not release[len(prefix):].strip()
    ):
        raise EngineeringReviewOutputError("Execution record has a conflicting Reviewer release")
    if identity is None and release is None:
        raise EngineeringReviewOutputError("Execution record has no Engineering Reviewer identity")


def _validate_command_evidence(verdict, review_input, execution_record):
    """Consume Runtime's log view, never model-reported test results.

    Runtime owns Provider parsing, content integrity and log representation.
    This consumer only checks the selected review Attempt's declared commands.
    Explicit independent-CLI bootstrap may use Runtime's parse_cli_log view;
    it remains non-managed and cannot stand in for Runtime execution lineage.
    """
    try:
        commands = review_input["sandbox_command_plan"]["commands"]
        declared = {row["command_id"]: row for row in commands}
        if len(declared) != len(commands) or any(type(row.get("required", True)) is not bool for row in commands):
            raise ValueError("Invalid command identities or required flags")
        required = {key for key, row in declared.items() if row.get("required", True)}
        record = {} if execution_record is None else execution_record
        if not isinstance(record, Mapping):
            raise ValueError("Runtime execution record must be an object")
        if record:
            validate_engineering_reviewer_identity(record)
            if record.get("status") != "completed" or record.get("semantic_input") != review_input:
                raise ValueError("Command evidence belongs to another invocation input")
            if record.get("review_purpose") != review_input["review_purpose"]:
                raise ValueError("Command evidence belongs to another review purpose")
        log = record.get("execution_log")
        if log is None:
            if required:
                raise ValueError("Required commands have no actual execution evidence")
            return
        if not isinstance(log, Mapping):
            raise ValueError("Runtime execution log must be an object")
        if log.get("schema_version") == "runtime_execution_log_v1":
            attempts = log.get("attempts")
            if (not isinstance(attempts, list) or any(not isinstance(item, Mapping) for item in attempts)
                    or not isinstance(record.get("attempt_id"), str) or not record["attempt_id"]
                    or not isinstance(record.get("module_run_id"), str) or not record["module_run_id"]
                    or record.get("managed_runtime") is not True):
                raise ValueError("Runtime log requires the exact selected review Attempt")
            if log.get("workflow_execution_id") != record.get("workflow_execution_id"):
                raise ValueError("Runtime log belongs to another workflow execution")
            selected = [item for item in attempts if item.get("attempt_id") == record["attempt_id"]]
            if (len(selected) != 1 or selected[0].get("module_run_id") != record.get("module_run_id")
                    or selected[0].get("status") != "completed"):
                raise ValueError("Runtime log belongs to another review Attempt")
            log = selected[0]
        elif log.get("schema_version") == "runtime_cli_log_v1":
            if record.get("managed_runtime") is not False:
                raise ValueError("A CLI-only log cannot claim managed Runtime execution")
        else:
            raise ValueError("Unsupported Runtime execution-log version")
        if required and log.get("complete") is not True:
            raise ValueError("Required command evidence is in an incomplete Runtime log")
        observations = log.get("tool_calls")
        if not isinstance(observations, list):
            raise ValueError("Runtime log tool_calls must be a list")
        seen, executed, failed, unavailable = set(), set(), set(), set()
        for row in observations:
            call_id = row["tool_call_id"]
            if not isinstance(call_id, str) or not call_id.strip() or call_id in seen:
                raise ValueError("Runtime tool_call_id is missing or duplicated")
            seen.add(call_id)
            if not isinstance(row["tool_name"], str) or not row["tool_name"].strip():
                raise ValueError("Runtime tool name is missing")
            if row["tool_name"] != "sandbox_command_execute":
                continue
            request, response = row["request"], row["response"]
            if not isinstance(request, dict) or not isinstance(response, dict):
                raise ValueError("Runtime command request/response must be objects")
            if set(request) != {"command_id"} or request["command_id"] not in declared:
                raise ValueError("Runtime executed an unknown command")
            identity = request["command_id"]
            status = row.get("status", "completed")
            if status == "failed":
                if not response:
                    raise ValueError("Unavailable command lacks actual Runtime failure evidence")
                unavailable.add(identity)
            elif status == "completed":
                if (response.get("command_id") != identity or response.get("allowed") is not True
                        or type(response.get("returncode")) is not int
                        or not isinstance(response.get("stdout"), str)
                        or not isinstance(response.get("stderr"), str)):
                    raise ValueError("Runtime command result is incomplete or mismatched")
                executed.add(identity)
                if response["returncode"] != 0:
                    failed.add(identity)
            else:
                raise ValueError("Unknown Runtime tool status")
        if required - executed - unavailable:
            raise ValueError("Required commands have no actual execution evidence")
        if unavailable & required and verdict != "blocked":
            raise ValueError("An unavailable required command requires blocked and a block finding")
        if failed & required and verdict == "passed":
            raise ValueError("A failed required command cannot produce passed")
    except (KeyError, TypeError, ValueError) as exc:
        raise EngineeringReviewOutputError(str(exc)) from exc


def validate_engineering_review_output(
    payload: Mapping[str, object],
    *,
    schema_path: Path = OUTPUT_SCHEMA_PATH,
    review_input: Mapping[str, object] | None = None,
    execution_record: Mapping[str, object] | None = None,
) -> None:
    """Validate common output, engineering checklist and executor-owned evidence."""
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(dict(payload))
    except (OSError, UnicodeError, ValueError, TypeError, ValidationError, SchemaError) as exc:
        raise EngineeringReviewOutputError(str(exc)) from exc

    required = list(engineering_check_ids())
    if review_input is not None:
        if review_input.get("schema_version") != "engineering_change_reviewer_input_v6":
            raise EngineeringReviewOutputError("A new-format output requires a v6 review input")
        if review_input.get("required_check_ids") != required:
            raise EngineeringReviewOutputError("Input must carry the complete canonical checklist")
    rows, findings = payload["check_results"], payload["findings"]
    if [row["check_id"] for row in rows] != required:
        raise EngineeringReviewOutputError("check_results must cover the canonical checklist once, in order")
    by_id = {item["finding_id"]: item for item in findings}
    if len(by_id) != len(findings):
        raise EngineeringReviewOutputError("finding_id values must be unique")
    levels = {item["severity"] for item in findings}
    expected = "blocked" if "block" in levels else "non_pass" if "fix" in levels else "passed"
    if payload["verdict"] != expected:
        raise EngineeringReviewOutputError("Finding severities and verdict disagree")
    referenced = set()
    for row in rows:
        ids = set(row["finding_ids"])
        if not ids <= by_id.keys():
            raise EngineeringReviewOutputError("check_result references an unknown finding")
        referenced.update(ids)
        actionable = any(by_id[identity]["severity"] != "note" for identity in ids)
        disposition = row["disposition"]
        if disposition == "finding" and not actionable:
            raise EngineeringReviewOutputError("finding row must reference an actionable finding")
        if disposition == "passed" and actionable:
            raise EngineeringReviewOutputError("passed row cannot contain block or fix")
        if disposition == "not_applicable":
            raise EngineeringReviewOutputError("Engineering checklist requires a judgment for each item")
        if disposition == "not_run" and (row["check_id"] != "8" or ids):
            raise EngineeringReviewOutputError("Only deferred prose check 8 may be not_run, without findings")
    if referenced != by_id.keys():
        raise EngineeringReviewOutputError("Every finding must be linked to a check_result")
    semantic_open = any(row["disposition"] == "finding" for row in rows if row["check_id"] != "8")
    prose = next(row for row in rows if row["check_id"] == "8")
    if (prose["disposition"] == "not_run") != semantic_open:
        raise EngineeringReviewOutputError("Prose check 8 runs after semantic checks pass")
    if review_input is not None:
        try:
            subject_refs = {review_input["code_design_basis"]["ref"]}
            subject = review_input["subject"]
            if subject is not None:
                subject_refs = {subject["commit_ref"], *(row["path"] for row in subject["paths"])}
            context_refs = {row["ref"] for row in review_input["context_documents"]}
            context_refs.add(review_input["code_design_basis"]["ref"])
            for key in ("system_change_plan_step", "code_design_review"):
                if review_input.get(key) is not None:
                    context_refs.add(review_input[key]["ref"])
            context_refs.add(review_input["sandbox_command_plan"]["ref"])
            for finding in findings:
                source = finding["evidence"]["source_ref"]
                if source not in subject_refs | context_refs:
                    raise ValueError("Finding cites undeclared evidence")
                if finding["severity"] == "fix" and source not in subject_refs:
                    raise ValueError("A fix must cite the current subject, not a background document")
        except (KeyError, TypeError, ValueError) as exc:
            raise EngineeringReviewOutputError(str(exc)) from exc
        _validate_command_evidence(payload["verdict"], review_input, execution_record)


__all__ = [
    "ENGINEERING_REVIEW_RESULT_INVALID",
    "EngineeringReviewOutputError",
    "OUTPUT_SCHEMA_PATH",
    "engineering_check_ids",
    "validate_engineering_review_output",
    "validate_engineering_reviewer_identity",
]
