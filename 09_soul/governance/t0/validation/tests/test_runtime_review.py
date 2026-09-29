"""Shared Runtime Test Run binding and the retirement of executor selection."""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path
import uuid

import pytest

import runtime_review
from tests.project_documentation.test_review_output import pd_input
from tests.runtime_review_real import REAL_GATE, assert_real_review, run_cli


VALIDATION_ROOT = Path(runtime_review.__file__).resolve().parent
CLI = VALIDATION_ROOT / "runtime_review.py"
REVIEWERS = {"design_contract_reviewer", "skill_candidate_reviewer", "experiment_reviewer", "engineering_change_reviewer",
             "system_change_plan_reviewer", "reviewer_reviewer", "project_documentation_reviewer"}
PD = "project_documentation_reviewer"
DSN_VARIABLE = "AGENT_RUNTIME_TEST_DATABASE_URL"


def _args(*extra):
    parser = argparse.ArgumentParser()
    runtime_review.add_runtime_arguments(parser)
    return parser.parse_args(list(extra))


def _schema(module_id):
    relative, _, _ = runtime_review._VALIDATORS[module_id]
    return json.loads(runtime_review._validator_module(relative).INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))


def _check_ids(schema):
    return [row["const"] for row in schema["properties"]["required_check_ids"]["prefixItems"]]


def system_change_input():
    """A small but complete SystemChangePlan under its governing rule."""
    schema = _schema("system_change_plan_reviewer")
    plan = ("# Rename the nightly export job\n\n## Goal\nOperators find the nightly export under the name the runbook uses:"
            " rename the scheduler job export_daily to export_nightly.\n\n## Steps\n1. Data platform (owner) renames the"
            " scheduler entry and job module and keeps export_daily as a disabled entry for one release. Verification:"
            " the scheduler lists export_nightly and its next run completes.\n2. Operations (owner) updates the runbook and"
            " alert routing to the new name. Verification: a test alert reaches the on-call channel under the new name.\n\n"
            "## Rollback\nRe-enable export_daily and disable export_nightly. No data or schema changes are involved.\n")
    rule = ("# System change rule\n\nA SystemChangePlan states its goal, orders its steps, names one owner per step, and gives"
            " each step a verification and the plan a rollback. A step that changes another owner's surface is handed to"
            " that owner.\n")
    return {"schema_version": schema["properties"]["schema_version"]["const"], "module_id": "system_change_plan_reviewer",
            "system_change_plan": {"document_id": "plan", "owner_ref": "data_platform", "title": "Rename the nightly export job",
                                   "body": plan},
            "governing_contract_closure": [{"document_id": "system_change_rule", "owner_ref": "governance",
                                            "title": "System change rule", "body": rule}],
            "required_check_ids": _check_ids(schema), "prior_findings": []}


def _artifact(ref, body):
    return {"artifact_ref": ref, "sha256": hashlib.sha256(body.encode()).hexdigest(), "body": body}


def reviewer_prompt_input():
    """A small Reviewer prompt with its Design, schemas and fixtures."""
    schema = _schema("reviewer_reviewer")
    prompt = _artifact("artifact:meeting_note_reviewer_prompt", (
        "# Meeting note reviewer\n\nInput: one meeting note as `note` text. Check that every action item names one owner"
        " and one due date. Return `passed` when all action items have both. Otherwise return `non_pass` with one finding"
        " per missing owner or due date that quotes the action item. Do not judge anything else in the note.\n"))
    design = _artifact("artifact:meeting_note_design", (
        "# Meeting notes\n\nEvery action item in a meeting note names one owner and one due date. The meeting note"
        " reviewer checks only this rule; the note's author fixes any gap.\n"))
    input_schema = _artifact("artifact:input_schema", json.dumps({
        "type": "object", "additionalProperties": False, "required": ["note"],
        "properties": {"note": {"type": "string", "minLength": 1}}}))
    output_schema = _artifact("artifact:output_schema", json.dumps({
        "type": "object", "additionalProperties": False, "required": ["verdict", "findings"],
        "properties": {"verdict": {"enum": ["passed", "non_pass"]},
                       "findings": {"type": "array", "items": {"type": "object", "required": ["action_item", "missing"],
                                    "properties": {"action_item": {"type": "string"},
                                                   "missing": {"enum": ["owner", "due_date"]}}}}}}))
    bodies = {"positive": {"note": "Action: Ana sends the budget by 2026-10-02."},
              "negative": {"note": "Action: send the budget."},
              "schema_drift": {"text": "Action: Ana sends the budget by 2026-10-02."}}
    fixtures = [{"fixture_ref": f"fixture:{kind}", "sha256": hashlib.sha256(json.dumps(body).encode()).hexdigest(),
                 "case_kind": kind, "body": json.dumps(body)} for kind, body in bodies.items()]
    return {"schema_version": schema["properties"]["schema_version"]["const"], "module_id": "reviewer_reviewer",
            "review_request": {"target_reviewer_module_id": "meeting_note_reviewer",
                               "reviewed_subject_kind": "reviewer_prompt_source",
                               "target_design_authority_ref": "designDoc/meeting_notes.md",
                               "intended_result": "The reviewer checks owners and due dates of action items only"},
            "prompt_candidate": prompt, "target_design_contract": design,
            "target_reviewer_input_schema": input_schema, "target_reviewer_output_schema": output_schema,
            "fixtures": fixtures,
            "deterministic_evidence": {"disposition": "passed", "subject_sha256": prompt["sha256"],
                                       "universal_resource_id": "t0:review_contract_universal_review_style",
                                       "universal_resource_sha256": "1" * 64,
                                       "checklist_resource_id": "meeting_note_checklist",
                                       "checklist_resource_sha256": "2" * 64},
            "required_check_ids": _check_ids(schema), "prior_findings": []}


def _record(module_id, semantic_input):
    """The two record fields bind_review_record reads, shaped as Test Run returns them."""
    return {"module_release_ref": f"runtime-module:{module_id}@v1",
            "input_bindings": [{"logical_name": "task_input",
                                "input_sha256": runtime_review._canonical_sha256(semantic_input)}]}


@pytest.mark.deterministic
def test_every_shipped_reviewer_has_one_identity_and_one_owning_validator():
    versions = runtime_review.reviewer_input_versions()
    assert set(versions) == REVIEWERS == set(runtime_review._VALIDATORS)
    assert versions[PD] == "project_documentation_reviewer_input_v1"
    for relative, function, _ in runtime_review._VALIDATORS.values():
        assert callable(getattr(runtime_review._validator_module(relative), function))


@pytest.mark.deterministic
def test_cli_arguments_map_to_the_public_test_run_fields_unchanged(tmp_path):
    args = _args("--root", str(tmp_path), "--workflow-ref", "runtime-workflow:x@v1", "--workflow-sha256", "a" * 64,
                 "--release-database-url-env", "RUNTIME_RELEASE_DSN", "--release-schema", "agent_runtime",
                 "--resources", "resources.json", "--transport", "claude_cli", "--model", "m", "--effort", "high",
                 "--cli-path", "/bin/claude", "--run-timeout-seconds", "3600")
    assert runtime_review.runtime_kwargs(args) == {
        "root": tmp_path, "workflow_release_ref": "runtime-workflow:x@v1", "workflow_release_sha256": "a" * 64,
        "release_database_url_env": "RUNTIME_RELEASE_DSN", "release_schema": "agent_runtime",
        "resources_path": Path("resources.json"), "transport_kind": "claude_cli", "model_id": "m",
        "reasoning_profile": "high", "cli_path": Path("/bin/claude"), "run_timeout_seconds": 3600}
    with pytest.raises(ValueError, match="requires --root"):
        runtime_review.runtime_kwargs(_args())


@pytest.mark.deterministic
def test_budget_omission_is_left_to_runtime_and_invalid_integer_is_rejected(tmp_path):
    assert "run_timeout_seconds" not in runtime_review.runtime_kwargs(_args("--root", str(tmp_path)))
    with pytest.raises(SystemExit):
        _args("--root", str(tmp_path), "--run-timeout-seconds", "1.5")


@pytest.mark.deterministic
def test_reviewer_identity_comes_from_the_shipped_input_schema():
    assert runtime_review.reviewer_for_input(pd_input()) == PD
    assert runtime_review.reviewer_for_input({"schema_version": "experiment_reviewer_input_v1",
                                              "module_id": "experiment_reviewer"}) == "experiment_reviewer"
    with pytest.raises(ValueError, match="disagrees with its schema_version"):
        runtime_review.reviewer_for_input({"schema_version": "experiment_reviewer_input_v1",
                                           "module_id": "design_contract_reviewer"})
    with pytest.raises(ValueError, match="not a shipped Reviewer input"):
        runtime_review.reviewer_for_input({"schema_version": "unknown_input_v1"})


@pytest.mark.deterministic
@pytest.mark.parametrize("fields,workflow", [({"root": Path("r")}, PD),
                                              ({"root": Path("r"), "workflow_id": "custom"}, "custom"),
                                              ({"root": Path("r"), "workflow_release_ref": "x", "workflow_release_sha256": "y",
                                                "release_database_url_env": "V", "release_schema": "s"}, None)])
def test_run_fields_fix_the_reviewer_and_default_only_the_local_workflow(fields, workflow):
    module_id, sent = runtime_review.review_run_fields(pd_input(), fields)
    assert module_id == PD
    assert sent.get("workflow_id") == workflow
    assert {key: value for key, value in sent.items() if key != "workflow_id"} == {
        key: value for key, value in fields.items() if key != "workflow_id"}


@pytest.mark.deterministic
@pytest.mark.parametrize("reserved", ["expected_module_id", "input_payload"])
def test_the_review_fixes_the_reviewer_and_its_input(reserved):
    with pytest.raises(ValueError, match="fixed by the review object"):
        runtime_review.review_run_fields(pd_input(), {"root": Path("r"), reserved: "design_contract_reviewer"})


@pytest.mark.deterministic
@pytest.mark.parametrize("problem,message", [
    ("other_reviewer", "does not come from project_documentation_reviewer"),
    ("prefix_only", "does not come from project_documentation_reviewer"),
    ("other_input", "does not bind the frozen review input"),
    ("no_binding", "does not bind the frozen review input"),
    ("two_bindings", "does not bind the frozen review input"),
])
def test_a_record_from_another_reviewer_or_input_is_rejected(problem, message):
    semantic_input = pd_input()
    record = _record(PD, semantic_input)
    if problem == "other_reviewer":
        record = _record("design_contract_reviewer", semantic_input)
    if problem == "prefix_only":
        record["module_release_ref"] = f"runtime-module:{PD}_extra@v1"
    if problem == "other_input":
        record = _record(PD, {**semantic_input, "prior_findings": [{"finding_id": "x"}]})
    if problem == "no_binding":
        record["input_bindings"] = []
    if problem == "two_bindings":
        record["input_bindings"] = record["input_bindings"] * 2
    with pytest.raises(ValueError, match=message):
        runtime_review.bind_review_record(record, module_id=PD, semantic_input=semantic_input)


@pytest.mark.deterministic
def test_a_bound_record_carries_its_own_copy_of_the_input():
    semantic_input = pd_input()
    bound = runtime_review.bind_review_record(_record(PD, semantic_input), module_id=PD, semantic_input=semantic_input)
    assert bound["module_id"] == PD and bound["semantic_input"] == semantic_input and "review_purpose" not in bound
    semantic_input["review_request"]["goal"] = "changed later"
    assert bound["semantic_input"] == pd_input()


@pytest.mark.deterministic
def test_executor_selection_is_gone_from_review_code(tmp_path, capsys):
    """Source scan: no executor variable, --executor option, string import or private run seam in validation code."""
    offenders = []
    for path in VALIDATION_ROOT.rglob("*.py"):
        relative = path.relative_to(VALIDATION_ROOT)
        if relative.parts[0] == "tests" or "__pycache__" in relative.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for token in ("_REVIEW_EXECUTOR", '"--executor"', "import_module(", "_invoke"):
            if token in text:
                offenders.append(f"{relative}: {token}")
    assert offenders == []
    assert list(inspect.signature(runtime_review.run_review_test).parameters) == ["semantic_input", "runtime_kwargs"]
    with pytest.raises(SystemExit) as error:
        runtime_review.main(["--input", "i.json", "--output", str(tmp_path / "r.json"), "--root", str(tmp_path),
                             "--executor", "module:function"])
    assert error.value.code == 2 and "--executor" in capsys.readouterr().err


@pytest.mark.real_run
@REAL_GATE
@pytest.mark.parametrize("build", [pd_input, system_change_input, reviewer_prompt_input],
                         ids=[PD, "system_change_plan_reviewer", "reviewer_reviewer"])
def test_real_raw_input_review_runs_the_reviewer_and_its_owning_validator(tmp_path, reviewer_host, build):
    """Real entry: this CLI as a process, the Reviewer registered from this checkout, Runtime Test Run and Claude CLI.

    Retired executor variables are set and ignored.
    """
    semantic_input = build()
    module_id = runtime_review.reviewer_for_input(semantic_input)
    source = tmp_path / "input.json"
    source.write_text(json.dumps(semantic_input))
    result = tmp_path / "result.json"
    process = run_cli(CLI, "--input", source, "--output", result, "--root", reviewer_host)
    record = json.loads(result.read_text())
    verdict = assert_real_review(record, module_id, json.loads(process.stdout))
    assert record["semantic_input"] == semantic_input
    assert process.returncode == (0 if verdict == "passed" else 1), process.stderr
    # The actual record from this run is rejected for another Reviewer or another input.
    other = "design_contract_reviewer"
    for claimed, claimed_input in ((module_id, {**semantic_input, "prior_findings": [{"finding_id": "x"}]}),
                                   (other, semantic_input)):
        with pytest.raises(ValueError):
            runtime_review.bind_review_record(record, module_id=claimed, semantic_input=claimed_input)
    before = result.read_bytes()
    again = run_cli(CLI, "--input", source, "--output", result, "--root", reviewer_host)
    assert again.returncode == 2 and "new file" in again.stderr and result.read_bytes() == before


@pytest.mark.real_run
@REAL_GATE
@pytest.mark.parametrize("failure,error_type", [("unregistered_root", "FileNotFoundError"),
                                                ("mixed_transport", "ValueError")])
def test_real_runtime_failure_is_a_diagnostic_without_a_result(tmp_path, reviewer_host, failure, error_type):
    """Real entry: Runtime Test Run failing before any Provider call; nothing is substituted."""
    source = tmp_path / "input.json"
    source.write_text(json.dumps(pd_input()))
    result = tmp_path / "result.json"
    arguments = (["--root", tmp_path / "empty_root"] if failure == "unregistered_root"
                 else ["--root", reviewer_host, "--transport", "codex_cli"])
    process = run_cli(CLI, "--input", source, "--output", result, *arguments)
    assert process.returncode == 2 and not result.exists()
    error = json.loads(process.stderr)
    assert error["error_type"] == error_type and error["error"] and "Traceback" not in process.stderr


@pytest.mark.real_run
@REAL_GATE
@pytest.mark.skipif(not os.environ.get(DSN_VARIABLE), reason=f"unverified: requires {DSN_VARIABLE}")
def test_real_pg_review_uses_the_exact_release_and_passes_the_locator_unchanged(tmp_path, reviewer_host):
    """Real entry: the Reviewer published to the PostgreSQL test database, Runtime Test Run and Claude CLI."""
    from dataclasses import fields
    import psycopg
    from agent_runtime import RuntimeReleaseBundle, load_runtime_registration
    from agent_runtime.registry import PostgresRuntimeReleaseStore
    saved = load_runtime_registration(reviewer_host, "workflow", PD)
    snapshot = saved.registry.snapshot()
    schema = f"portable_review_{uuid.uuid4().hex[:16]}"
    store = PostgresRuntimeReleaseStore.from_dsn(os.environ[DSN_VARIABLE], schema=schema)
    store.create_schema(installed_at_utc="2026-09-26T00:00:00Z")
    try:
        store.register_bundle(RuntimeReleaseBundle(**{field.name: getattr(snapshot, field.name)
                                                     for field in fields(RuntimeReleaseBundle)}))
        consumer = tmp_path / "consumer"  # an empty root; the definition comes from PostgreSQL
        source = tmp_path / "input.json"
        source.write_text(json.dumps(pd_input()))
        result = tmp_path / "result.json"
        process = run_cli(CLI, "--input", source, "--output", result, "--root", consumer,
                          "--workflow-ref", saved.release.release_ref, "--workflow-sha256", saved.release.release_sha256,
                          "--release-database-url-env", DSN_VARIABLE, "--release-schema", schema)
        record = json.loads(result.read_text())
        assert_real_review(record, PD, json.loads(process.stdout))
        assert (record["workflow_release_ref"], record["workflow_release_sha256"]) == (
            saved.release.release_ref, saved.release.release_sha256)
        assert os.environ[DSN_VARIABLE] not in result.read_text()
    finally:
        with psycopg.connect(os.environ[DSN_VARIABLE]) as connection:
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")


@pytest.mark.real_run
@REAL_GATE
@pytest.mark.skipif("AGENT_RUNTIME_CODEX_BIN" not in os.environ,
                    reason="unverified: set AGENT_RUNTIME_CODEX_BIN to an authenticated Codex CLI executable")
def test_real_shared_entry_passes_single_run_budget_to_runtime(tmp_path, reviewer_host):
    cli_path = Path(os.environ["AGENT_RUNTIME_CODEX_BIN"])
    if not cli_path.is_file() or not os.access(cli_path, os.X_OK):
        pytest.fail(f"AGENT_RUNTIME_CODEX_BIN must name an executable Codex CLI file: {cli_path}")
    source = tmp_path / "input.json"
    source.write_text(json.dumps(pd_input()))
    target = tmp_path / "result.json"
    process = run_cli(CLI, "--input", source, "--output", target, "--root", reviewer_host,
                      "--transport", "codex_cli", "--model", "gpt-6-astra", "--effort", "xhigh",
                      "--cli-path", cli_path, "--run-timeout-seconds", "3600")
    assert target.exists(), process.stderr
    record = json.loads(target.read_text())
    evidence = os.environ.get("PORTABLE_REVIEW_EVIDENCE_DIR")
    if evidence:
        with (Path(evidence) / "portable_budget_record.json").open("x") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
    assert record["status"] == "completed", record.get("failure_detail")
    assert record["semantic_validation"]["status"] == "passed"
    assert record["execution_budget"]["requested_timeout_seconds"] == 3600
    assert record["execution_parameter_sources"]["run_timeout_seconds"]["layer"] == "call"
    assert record["provider_trace"]["timeout_seconds"] == 3600
    assert process.returncode == (0 if record["output"]["verdict"] == "passed" else 1)
