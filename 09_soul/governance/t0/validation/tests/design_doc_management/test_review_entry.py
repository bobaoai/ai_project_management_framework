from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from .test_artifact_contract import _candidate
from .test_review_output import passed_output, output_with_finding
from tests.runtime_review_real import REAL_GATE, assert_real_review, run_cli


SPEC = importlib.util.spec_from_file_location(
    "portable_ddm_review_entry", Path(__file__).resolve().parents[2] / "artifact_contracts/design_review.py"
)
entry = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = entry
SPEC.loader.exec_module(entry)


@pytest.fixture
def candidate(tmp_path):
    path = tmp_path / "设计.md"
    body = _candidate("t0").replace(
        b"---\nlayer: T0\n",
        b"---\nlayer: T0\ntitle: Example\nowned_system_object: Example decision\ncanonical_owner: designDoc/example.md\n",
        1,
    )
    path.write_bytes(body)
    return path


def args_for(candidate):
    return dict(candidate_paths=[candidate], intended_result="明确本次职责", architecture_change_summary="修改文档边界")


def good_executor(payload):
    return runtime_record(passed_output())


def runtime_record(output, status="completed"):
    return {"status": status, "output": output, "module_release_ref":"runtime-module:design_contract_reviewer@test"}


def test_build_uses_exact_input_and_does_not_require_old_process_records(candidate):
    value = entry.build_design_review_input(**args_for(candidate))
    assert value["candidate_documents"][0]["body"].encode() == candidate.read_bytes()
    assert value["candidate_documents"][0]["document_id"] == "candidate_1"
    assert value["review_request"]["candidate_revision_class"] == "materially_revised_surface"
    assert {x["context_role"] for x in value["context_documents"]} == {"governing_contract", "prior_decision"}
    assert "迁移清单" not in json.dumps(value["review_request"],ensure_ascii=False)
    assert len(value["required_check_ids"]) == 11


def test_build_loads_only_declared_context_and_its_existing_owner(candidate, tmp_path):
    peer = tmp_path / "peer.md"
    peer.write_text("---\ncanonical_owner: designDoc/peer.md\n---\nOnly relevant peer.\n")
    value = entry.build_design_review_input(**args_for(candidate), context_bindings=[("peer_contract",None,peer)])
    assert value["context_documents"][-1]["owner_ref"] == "designDoc/peer.md"
    assert value["context_documents"][-1]["body"] == peer.read_text()


def test_same_names_do_not_collide_in_model_identifiers(candidate, tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    peer = other / candidate.name
    peer.write_bytes(candidate.read_bytes())
    value = entry.build_design_review_input(**args_for(candidate),context_bindings=[("peer_contract",None,peer)])
    ids = [x["document_id"] for x in value["candidate_documents"] + value["context_documents"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("mutation", ["missing_layer", "missing_object", "missing_heading", "crlf", "empty_goal"])
def test_invalid_candidate_never_reaches_executor(candidate, mutation):
    args = args_for(candidate)
    body = candidate.read_bytes()
    if mutation == "missing_layer": body = body.replace(b"layer: T0",b"unrelated: T0")
    if mutation == "missing_object":
        body = body.replace(b"owned_system_object:",b"unrelated:")
        body = body.replace(b"Complete meaning for Owned System Object.", b" ")
    if mutation == "missing_heading": body = body.replace(b"Reader Gain",b"Wrong Heading")
    if mutation == "crlf": body = body.replace(b"\n",b"\r\n")
    if mutation == "empty_goal": args["intended_result"] = " "
    candidate.write_bytes(body)
    with pytest.raises(ValueError):
        entry.review_documents(executor=lambda p:pytest.fail("must not execute"),**args)


def test_success_preserves_input_and_returns_bound_result(candidate):
    before = candidate.read_bytes()
    record = entry.review_documents(executor=good_executor, **args_for(candidate))
    assert record["semantic_validation"]["status"] == "passed"
    assert record["candidate_sha256_by_document_id"]["candidate_1"] == hashlib.sha256(before).hexdigest()
    assert candidate.read_bytes() == before


def test_owned_object_may_be_declared_in_its_required_body_section(candidate):
    candidate.write_bytes(candidate.read_bytes().replace(b"owned_system_object: Example decision\n",b""))
    value=entry.build_design_review_input(**args_for(candidate))
    assert value["candidate_documents"][0]["owned_object"] == "Complete meaning for Owned System Object."


@pytest.mark.parametrize("kind", ["schema", "false_pass", "missing_check"])
def test_invalid_reviewer_output_is_not_an_accepted_verdict(candidate, kind):
    output = passed_output()
    if kind == "schema": output["extra"] = True
    if kind == "missing_check": output["check_results"].pop()
    if kind == "false_pass": output["check_results"][-1]["disposition"] = "not_run"
    record = entry.review_documents(executor=lambda p:runtime_record(output),**args_for(candidate))
    assert record["semantic_validation"]["status"] == "failed"


def test_valid_non_pass_remains_non_pass(candidate):
    output = output_with_finding()
    output["findings"][0].update(affected_candidate_document_id="candidate_1",correction_target_document_id="candidate_1",accountable_owner_ref="designDoc/example.md")
    output["findings"][0]["evidence"]["source_ref"] = "candidate_1"
    record = entry.review_documents(executor=lambda p:runtime_record(output),**args_for(candidate))
    assert record["semantic_validation"]["status"] == "passed"
    assert record["output"]["verdict"] == "non_pass"


def test_provider_failure_does_not_become_review_verdict(candidate):
    record = entry.review_documents(executor=lambda p:runtime_record(None,status="failed"),**args_for(candidate))
    assert record["semantic_validation"]["status"] == "not_run"
    assert record["output"] is None


def test_other_reviewer_cannot_substitute_for_design_reviewer(candidate):
    value=runtime_record(passed_output())
    value["module_release_ref"]="runtime-module:skill_candidate_reviewer@test"
    record=entry.review_documents(executor=lambda p:value,**args_for(candidate))
    assert record["semantic_validation"]["status"] == "failed"


def test_post_dispatch_change_rejects_old_result(candidate):
    original = candidate.read_bytes()
    def changing_executor(payload):
        candidate.write_bytes(original + b"\nChanged after sending.\n")
        return good_executor(payload)
    record = entry.review_documents(executor=changing_executor,**args_for(candidate))
    assert record["semantic_validation"]["status"] == "failed"
    assert record["semantic_input"]["candidate_documents"][0]["body"].encode() == original


def test_changed_context_also_rejects_old_result(candidate, tmp_path):
    peer = tmp_path / "peer.md"
    peer.write_text("Original peer meaning.")
    def changing_executor(payload):
        peer.unlink()
        return good_executor(payload)
    record = entry.review_documents(executor=changing_executor,context_bindings=[("peer_contract",None,peer)],**args_for(candidate))
    assert record["semantic_validation"]["status"] == "failed"


@pytest.mark.deterministic
def test_cli_refuses_to_replace_candidate(candidate, monkeypatch):
    import agent_runtime
    monkeypatch.setattr(agent_runtime, "run_local_workflow_test", lambda **kw: pytest.fail("no dispatch"), raising=False)
    before = candidate.read_bytes()
    with pytest.raises(SystemExit):
        entry.main(["--candidate", str(candidate), "--goal", "goal", "--change", "change", "--output", str(candidate),
                    "--root", str(candidate.parent)])
    assert candidate.read_bytes() == before


@pytest.mark.real_run
@REAL_GATE
def test_real_standalone_cli_reviews_through_runtime_with_exclusive_output(candidate, tmp_path, reviewer_host):
    """Real entry: this CLI as a process, the Reviewer registered from this checkout, Runtime Test Run and Claude CLI.

    Retired executor variables are set and ignored.
    """
    output = tmp_path / "review.json"
    prior = [{"finding_id": "previous_boundary", "disposition": "claimed_fixed", "body": "核对修订后的职责。"}]
    prior_path = tmp_path / "prior.json"
    prior_path.write_text(json.dumps(prior))
    arguments = ["--candidate", candidate, "--goal", "明确职责", "--change", "新建文档", "--new",
                 "--prior-findings", prior_path, "--output", output, "--root", reviewer_host]
    process = run_cli(Path(entry.__file__), *arguments)
    record = json.loads(output.read_text())
    verdict = assert_real_review(record, "design_contract_reviewer", json.loads(process.stdout))
    assert process.returncode == (0 if verdict == "passed" else 1), process.stderr
    assert record["semantic_input"]["review_request"]["candidate_revision_class"] == "new_document"
    assert record["semantic_input"]["prior_findings"] == prior
    before = output.read_bytes()
    again = run_cli(Path(entry.__file__), *arguments)
    assert again.returncode == 2 and output.read_bytes() == before


@pytest.mark.deterministic
def test_cli_rejects_the_retired_executor_argument(candidate, tmp_path, capsys):
    with pytest.raises(SystemExit) as error:
        entry.main(["--candidate", str(candidate), "--goal", "g", "--change", "c", "--output", str(tmp_path / "r.json"),
                    "--root", str(tmp_path), "--executor", "installed_executor:review"])
    assert error.value.code == 2 and "--executor" in capsys.readouterr().err


@pytest.mark.deterministic
@pytest.mark.parametrize("problem", ["missing_root", "missing_output_directory"])
def test_cli_missing_configuration_stops_with_actionable_message(candidate, tmp_path, monkeypatch, capsys, problem):
    import agent_runtime
    monkeypatch.setattr(agent_runtime, "run_local_workflow_test", lambda **kw: pytest.fail("no dispatch"), raising=False)
    output = tmp_path / "result.json"
    argv = ["--candidate", str(candidate), "--goal", "goal", "--change", "change", "--output", str(output)]
    if problem == "missing_output_directory":
        output = tmp_path / "missing" / "result.json"
        argv = [*argv[:-1], str(output), "--root", str(tmp_path)]
    with pytest.raises(SystemExit) as error:
        entry.main(argv)
    assert error.value.code == 2
    message = capsys.readouterr().err
    assert ("running a review requires --root" if problem == "missing_root" else "output directory does not exist") in message
    assert not output.exists()


@pytest.mark.parametrize("layer", ["charter", "t1", "t2"])
def test_review_kind_follows_document_layer(tmp_path, layer):
    path = tmp_path / "candidate.md"
    body = _candidate(layer).replace(b"---\n", b"---\ntitle: Example\nowned_system_object: Example decision\n", 1)
    path.write_bytes(body)
    value = entry.build_design_review_input(**args_for(path))
    assert value["review_request"]["reviewed_subject_kind"] == layer + "_design"
