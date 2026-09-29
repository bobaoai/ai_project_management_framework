from __future__ import annotations

import hashlib
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
from types import ModuleType

import pytest

from .test_artifact_contract import _candidate
from tests.runtime_review_real import REAL_GATE, assert_real_review, run_cli, run_cli_interrupted


ENTRY_PATH = Path(__file__).resolve().parents[2] / "artifact_contracts/skill_review.py"
SPEC = importlib.util.spec_from_file_location("portable_skill_review_entry", ENTRY_PATH)
entry = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = entry
SPEC.loader.exec_module(entry)


def check_ids():
    return [item["check_id"] for item in entry.artifact.load_contract()["reviewer_checklist"]["checks"]]


def passed_output(*, prompts=False):
    ids = check_ids()
    return {
        "verdict": "passed",
        "check_results": [{"check_id": identity, "disposition": "not_applicable" if identity == ids[-1] and not prompts else "passed",
                           "assessment": "Current candidate evidence.", "finding_ids": []} for identity in ids]
                         + [{"check_id": "prose_and_meaning_preservation", "disposition": "passed", "assessment": "Meaning preserved.", "finding_ids": []}],
        "findings": [], "safe_next_step": "Use the reviewed Skill source.",
    }


def record(output=None, status="completed"):
    return {"module_release_ref": "runtime-module:skill_candidate_reviewer@test", "status": status,
            "output": passed_output() if output is None else output}


@pytest.fixture
def args(tmp_path):
    candidate = tmp_path / "SKILL.md"
    candidate.write_bytes(_candidate())
    self_check = tmp_path / "self-check.json"
    self_check.write_text(json.dumps({
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "rows": [{"check_id": identity, "exact_evidence": "Candidate section.", "local_result": "Locally checked.", "unresolved_finding": None}
                 for identity in check_ids()],
    }), encoding="utf-8")
    authority = tmp_path / "09_soul/governance/t0/the_skill_management.md"
    authority.parent.mkdir(parents=True)
    authority.write_text("Skill Management fixture authority.", encoding="utf-8")
    return dict(candidate_path=candidate, goal="明确任务", change="修改方法", self_check_path=self_check, project_root=tmp_path)


def test_success_uses_exact_candidate_goal_and_existing_schema(args):
    before = args["candidate_path"].read_bytes()
    received = []
    result = entry.review_skill(executor=lambda value: received.append(value) or record(), **args)

    assert result["semantic_validation"]["status"] == "passed"
    assert received[0]["skill_candidate"]["candidate_body"].encode() == before
    request = next(row for row in received[0]["owning_design_closure"] if row["document_id"] == "user_request")
    assert args["goal"] in request["body"] and args["change"] in request["body"]
    assert args["candidate_path"].read_bytes() == before
    assert result["subject_sha256"] == hashlib.sha256(before).hexdigest()


@pytest.mark.parametrize("problem", ["goal", "scope", "self_check_hash", "self_check_open", "self_check_coverage", "schema", "missing_context"])
def test_invalid_inputs_never_invoke_executor(args, problem):
    if problem == "goal": args["goal"] = " "
    if problem == "scope": args["change"] = " "
    if problem.startswith("self_check"):
        value = json.loads(args["self_check_path"].read_text())
        if problem == "self_check_hash": value["candidate_sha256"] = "0" * 64
        if problem == "self_check_open": value["rows"][0]["unresolved_finding"] = "still missing input"
        if problem == "self_check_coverage": value["rows"].pop()
        args["self_check_path"].write_text(json.dumps(value), encoding="utf-8")
    if problem == "schema":
        args["candidate_path"].write_bytes(_candidate().replace(b"## 2. Reader Gain", b"## 2. Wrong"))
    if problem == "missing_context": args["context_bindings"] = [("skill", args["candidate_path"].parent / "missing.md")]

    with pytest.raises((ValueError, OSError)):
        entry.review_skill(executor=lambda value: pytest.fail("executor must not run"), **args)


def test_context_and_declared_prompt_are_loaded_without_discovery(args, tmp_path):
    design = tmp_path / "design.md"; design.write_text("Exact task Design.", encoding="utf-8")
    context = tmp_path / "peer.md"; context.write_text("Related Skill only.", encoding="utf-8")
    prompt = tmp_path / "prompt.md"; prompt.write_text("Complete declared instruction.", encoding="utf-8")
    result = entry.review_skill(executor=lambda value: record(passed_output(prompts=True)), **args,
                               design_paths=[design], context_bindings=[("skill", context)], prompt_bindings=[("example", prompt)])
    value = result["semantic_input"]
    assert value["skill_candidate"]["runtime_ready_prompts"] == [{"prompt_id": "example", "prompt_body": prompt.read_text()}]
    assert any(row["body"] == design.read_text() for row in value["owning_design_closure"])
    assert any(row["body"] == context.read_text() for row in value["source_and_projection_closure"])
    assert result["semantic_validation"]["status"] == "passed"


@pytest.mark.parametrize("change", ["candidate", "context", "input_object", "wrong_reviewer"])
def test_moved_or_wrong_subject_cannot_receive_a_valid_result(args, tmp_path, change):
    context = tmp_path / "context.md"; context.write_text("Original context.", encoding="utf-8")
    def executor(value):
        if change == "candidate": args["candidate_path"].write_text("Changed.", encoding="utf-8")
        if change == "context": context.write_text("Changed.", encoding="utf-8")
        if change == "input_object": value["skill_candidate"]["candidate_body"] = "Replaced by executor."
        result = record()
        if change == "wrong_reviewer": result["module_release_ref"] = "runtime-module:design_contract_reviewer@test"
        return result
    result = entry.review_skill(executor=executor, **args, context_bindings=[("skill", context)])
    assert result["semantic_validation"]["status"] == "failed"
    assert result["semantic_input"]["skill_candidate"]["candidate_body"] != "Replaced by executor."


def test_execution_failure_is_not_a_reviewer_verdict(args):
    result = entry.review_skill(executor=lambda value: record(status="failed"), **args)
    assert result["semantic_validation"]["status"] == "not_run"


def _linked_input(args, tmp_path, kind):
    if kind == "directory":
        target = tmp_path / "original"
        target.mkdir()
        (target / "SKILL.md").write_bytes(args["candidate_path"].read_bytes())
        alias = tmp_path / "candidate_directory"
        alias.symlink_to(target, target_is_directory=True)
        args["candidate_path"] = alias / "SKILL.md"
        return alias, target / "SKILL.md"
    target = args["candidate_path"]
    alias = tmp_path / "candidate_link.md"
    if kind == "context":
        target = tmp_path / "context.md"
        target.write_text("Original context.", encoding="utf-8")
        alias = tmp_path / "context_link.md"
        args["context_bindings"] = [("skill", alias)]
    else:
        args["candidate_path"] = alias
    alias.symlink_to(target)
    return alias, target


@pytest.mark.parametrize("kind", ["candidate", "context", "directory"])
def test_stable_input_symlinks_remain_supported(args, tmp_path, kind):
    _linked_input(args, tmp_path, kind)
    result = entry.review_skill(executor=lambda _: record(), **args)
    assert result["semantic_validation"]["status"] == "passed"


@pytest.mark.parametrize("kind", ["candidate", "context", "directory"])
@pytest.mark.parametrize("same_bytes", [False, True])
def test_retargeted_input_is_rejected_without_reading_new_target(args, tmp_path, monkeypatch, kind, same_bytes):
    alias, original = _linked_input(args, tmp_path, kind)
    replacement = tmp_path / "replacement" / original.name
    replacement.parent.mkdir()
    replacement.write_bytes(original.read_bytes() if same_bytes else b"Different input.\n")
    read_bytes = Path.read_bytes
    observed = []
    def guarded_read(path):
        observed.append(path)
        assert path != replacement, "The new target is not an authorized frozen input"
        return read_bytes(path)
    def executor(_):
        alias.unlink()
        alias.symlink_to(replacement.parent if kind == "directory" else replacement,
                         target_is_directory=kind == "directory")
        monkeypatch.setattr(Path, "read_bytes", guarded_read)
        return record()
    result = entry.review_skill(executor=executor, **args)
    assert result["semantic_validation"]["status"] == "failed"
    assert replacement not in observed


def test_retargeting_before_dispatch_does_not_call_executor(args, tmp_path, monkeypatch):
    alias, original = _linked_input(args, tmp_path, "candidate")
    replacement = tmp_path / "replacement.md"
    replacement.write_bytes(original.read_bytes())
    prepare = entry._prepare
    def moved_after_prepare(**kwargs):
        prepared = prepare(**kwargs)
        alias.unlink()
        alias.symlink_to(replacement)
        return prepared
    monkeypatch.setattr(entry, "_prepare", moved_after_prepare)
    with pytest.raises(ValueError, match="changed"):
        entry.review_skill(executor=lambda _: pytest.fail("must not dispatch"), **args)


def test_retargeting_during_preparation_does_not_read_new_target(args, tmp_path, monkeypatch):
    alias, original = _linked_input(args, tmp_path, "candidate")
    replacement = tmp_path / "replacement.md"
    replacement.write_bytes(original.read_bytes())
    read_bytes = Path.read_bytes
    moved = False
    def read_and_retarget(path):
        nonlocal moved
        assert path != replacement, "Preparation must reject changed binding before reading its target"
        data = read_bytes(path)
        if path == original and not moved:
            moved = True
            alias.unlink()
            alias.symlink_to(replacement)
        return data
    monkeypatch.setattr(Path, "read_bytes", read_and_retarget)
    with pytest.raises(ValueError, match="changed"):
        entry.review_skill(executor=lambda _: pytest.fail("must not dispatch"), **args)


@pytest.mark.parametrize("kind", ["candidate", "context", "directory"])
def test_disappearing_input_target_cannot_validate(args, tmp_path, kind):
    _, original = _linked_input(args, tmp_path, kind)
    def executor(_):
        original.unlink()
        return record()
    assert entry.review_skill(executor=executor, **args)["semantic_validation"]["status"] == "failed"


@pytest.mark.parametrize("kind", ["candidate", "context", "directory"])
@pytest.mark.parametrize("component", ["missing", "not_directory"])
def test_unresolvable_retarget_cannot_be_normalized_to_old_input(args, tmp_path, kind, component):
    alias, original = _linked_input(args, tmp_path, kind)
    parent = original.parent.parent if kind == "directory" else original.parent
    intermediate = parent / "intermediate"
    if component == "not_directory":
        intermediate.write_text("Not a directory.", encoding="utf-8")
    final = original.parent.name if kind == "directory" else original.name
    destination = intermediate / ".." / final
    def executor(_):
        alias.unlink()
        alias.symlink_to(destination, target_is_directory=kind == "directory")
        with pytest.raises(OSError):
            (alias / "SKILL.md" if kind == "directory" else alias).read_bytes()
        return record()
    assert entry.review_skill(executor=executor, **args)["semantic_validation"]["status"] == "failed"


def test_disappearing_traversed_directory_invalidates_requested_path(args, tmp_path):
    traversed = tmp_path / "traversed"
    traversed.mkdir()
    args["candidate_path"] = traversed / ".." / args["candidate_path"].name
    assert args["candidate_path"].read_bytes() == _candidate()
    def executor(_):
        traversed.rmdir()
        with pytest.raises(FileNotFoundError):
            args["candidate_path"].read_bytes()
        return record()
    assert entry.review_skill(executor=executor, **args)["semantic_validation"]["status"] == "failed"


@pytest.mark.parametrize("component", ["missing", "not_directory"])
def test_unresolvable_input_is_rejected_during_preparation(args, tmp_path, component):
    intermediate = tmp_path / "intermediate"
    if component == "not_directory":
        intermediate.write_text("Not a directory.", encoding="utf-8")
    args["candidate_path"] = intermediate / ".." / args["candidate_path"].name
    with pytest.raises(OSError):
        entry.review_skill(executor=lambda _: pytest.fail("must not dispatch"), **args)


def test_equivalent_valid_link_target_remains_supported(args, tmp_path):
    alias, original = _linked_input(args, tmp_path, "candidate")
    traversed = tmp_path / "traversed"
    traversed.mkdir()
    def executor(_):
        alias.unlink()
        alias.symlink_to(traversed / ".." / original.name)
        assert alias.read_bytes() == original.read_bytes()
        return record()
    assert entry.review_skill(executor=executor, **args)["semantic_validation"]["status"] == "passed"


@pytest.mark.parametrize("error", [OSError("Unresolvable input"), RuntimeError("Symlink loop")])
def test_post_dispatch_resolution_error_is_a_failed_validation(args, monkeypatch, error):
    resolve = Path.resolve
    requested = args["candidate_path"].absolute()
    def fail_resolution(path, *positional, **options):
        if path == requested:
            raise error
        return resolve(path, *positional, **options)
    def executor(_):
        monkeypatch.setattr(Path, "resolve", fail_resolution)
        return record()
    result = entry.review_skill(executor=executor, **args)
    assert result["semantic_validation"]["status"] == "failed"
    assert str(error) in result["semantic_validation"]["message"]


@pytest.mark.skipif(os.name != "posix", reason="This case requires POSIX directory search permissions")
@pytest.mark.parametrize("kind", ["candidate", "context"])
@pytest.mark.parametrize("timing", ["preparation", "before_dispatch", "post_dispatch"])
def test_original_path_search_permission_is_required(args, tmp_path, monkeypatch, kind, timing):
    if os.geteuid() == 0:
        pytest.skip("A privileged user bypasses the directory permission negative control")
    target = args["candidate_path"]
    if kind == "context":
        target = tmp_path / "context.md"
        target.write_text("Context content.", encoding="utf-8")
    traversal = tmp_path / "traversal"
    traversal.mkdir()
    original_mode = stat.S_IMODE(traversal.stat().st_mode)
    requested = traversal / ".." / target.name
    if kind == "candidate":
        args["candidate_path"] = requested
    else:
        args["context_bindings"] = [("skill", requested)]
    assert requested.read_bytes() == target.read_bytes()
    assert entry.review_skill(executor=lambda _: record(), **args)["semantic_validation"]["status"] == "passed"
    prepare = entry._prepare
    def deny_search():
        traversal.chmod(0o600)
        with pytest.raises(PermissionError):
            requested.read_bytes()
        with pytest.raises(PermissionError):
            requested.stat()
    try:
        if timing == "preparation":
            deny_search()
        elif timing == "before_dispatch":
            def prepared_then_denied(**kwargs):
                result = prepare(**kwargs)
                deny_search()
                return result
            monkeypatch.setattr(entry, "_prepare", prepared_then_denied)
        if timing == "post_dispatch":
            def execute(_):
                deny_search()
                return record()
            result = entry.review_skill(executor=execute, **args)
            assert result["semantic_validation"]["status"] == "failed"
        else:
            with pytest.raises(PermissionError):
                entry.review_skill(executor=lambda _: pytest.fail("must not dispatch"), **args)
    finally:
        traversal.chmod(original_mode)
        monkeypatch.setattr(entry, "_prepare", prepare)
    assert requested.read_bytes() == target.read_bytes()
    assert entry.review_skill(executor=lambda _: record(), **args)["semantic_validation"]["status"] == "passed"


def test_notes_are_accepted_without_failed_checks(args):
    output = passed_output()
    candidate_id = entry.check_skill(args["candidate_path"], project_root=args["project_root"])["skill_id"]
    output["findings"] = [{"finding_id": "note_1", "severity": "note", "check_id": check_ids()[0],
                           "evidence": {"source_ref": candidate_id, "locator": "Task", "observation": "Current name."},
                           "requirement": "Optional clarity", "impact": "May improve reading", "accountable_owner_ref": "skill_owner", "required_change": "Optional wording improvement."}]
    output["check_results"][0]["finding_ids"] = ["note_1"]
    result = entry.review_skill(executor=lambda value: record(output), **args)
    assert result["semantic_validation"]["status"] == "passed"


@pytest.mark.parametrize("problem", ["wrong_order", "extra_field", "duplicate_finding", "unknown_finding", "uncited_fix", "wrong_verdict", "not_applicable"])
def test_output_errors_do_not_become_pass(args, tmp_path, problem):
    output = passed_output()
    candidate_id = entry.check_skill(args["candidate_path"], project_root=args["project_root"])["skill_id"]
    evidence = {"source_ref": candidate_id, "locator": "Task", "observation": "Source."}
    if problem == "wrong_order": output["check_results"].reverse()
    if problem == "extra_field": output["extra"] = True
    if problem == "duplicate_finding":
        note = {"finding_id": "same", "severity": "note", "check_id": check_ids()[0], "evidence": evidence,
                "requirement": "Optional clarity", "impact": "May help reading", "accountable_owner_ref": "owner", "required_change": "Optional."}
        output["findings"] = [note, dict(note)]
    if problem == "unknown_finding": output["check_results"][0].update(disposition="finding", finding_ids=["absent"])
    if problem in {"uncited_fix", "wrong_verdict"}:
        output["verdict"] = "non_pass"
        output["check_results"][0].update(disposition="finding", finding_ids=["fix_1"])
        output["findings"] = [{"finding_id": "fix_1", "severity": "fix", "check_id": check_ids()[0], "evidence": evidence,
                               "requirement": "A complete task", "impact": "Cannot execute", "accountable_owner_ref": "owner", "required_change": "Restore task."}]
        output["check_results"][-1].update(disposition="not_run", assessment="Semantic finding first.")
        if problem == "uncited_fix": output["findings"].append({**output["findings"][0], "finding_id": "uncited"})
        if problem == "wrong_verdict": output["findings"][0]["severity"] = "block"
    if problem == "not_applicable":
        prompt = tmp_path / "prompt.md"; prompt.write_text("Declared prompt.", encoding="utf-8")
        args["prompt_bindings"] = [("prompt", prompt)]
    result = entry.review_skill(executor=lambda value: record(output), **args)
    assert result["semantic_validation"]["status"] == "failed"


def test_actual_resource_selection_and_hash_drift(tmp_path):
    root = entry.PROJECT_ROOT
    governance = tmp_path / "09_soul/governance"
    (governance / "t0").mkdir(parents=True)
    for name in ("governance_skill_manifest.json", "governance_t0_manifest.json"):
        shutil.copyfile(root / "09_soul/governance" / name, governance / name)
    source = governance / "t0/the_skill_management.md"
    shutil.copyfile(root / "09_soul/governance/t0/the_skill_management.md", source)
    start = "<!-- skill-authority-input-guard:start -->\n"; end = "<!-- skill-authority-input-guard:end -->"
    selected = source.read_text().split(start)[1].split(end)[0]
    identity = "t0:skill_authority_input_guard"
    candidate = tmp_path / "candidate.md"
    candidate.write_bytes(_candidate() + f"\n<!-- embedded-resource:{identity}:start -->\n{selected}<!-- embedded-resource:{identity}:end -->\n".encode())
    report = entry.check_skill(candidate, project_root=tmp_path)
    assert report["resource_sha256"][identity] == hashlib.sha256(selected.encode()).hexdigest()
    manifests = {path: path.read_bytes() for path in governance.glob("*.json")}
    source.write_text(source.read_text().replace("machine-facing meaning", "modified authority meaning"), encoding="utf-8")
    with pytest.raises(ValueError, match="differ from their canonical sources"):
        entry.check_skill(candidate, project_root=tmp_path)
    candidate.write_bytes(candidate.read_bytes().replace(b"machine-facing meaning", b"modified authority meaning"))
    changed = entry.check_skill(candidate, project_root=tmp_path)
    assert changed["resource_sha256"][identity] != report["resource_sha256"][identity]
    assert all(path.read_bytes() == payload for path, payload in manifests.items())


def _json_resource_candidate(root):
    governance = root / "09_soul/governance"
    contracts = governance / "t0/validation/artifact_contracts"
    contracts.mkdir(parents=True)
    for name in ("governance_skill_manifest.json", "governance_t0_manifest.json"):
        shutil.copyfile(entry.PROJECT_ROOT / "09_soul/governance" / name, governance / name)
    source = contracts / "skill_artifact_contract.json"
    adapter = contracts / "skill_artifact_contract.py"
    for path in (source, adapter):
        shutil.copyfile(entry.HERE / path.name, path)
    shutil.copyfile(entry.GOVERNANCE_ROOT / "t0/the_skill_management.md", governance / "t0/the_skill_management.md")
    value = json.loads(source.read_bytes())
    value["reviewer_checklist"]["checks"][0]["required_result"] += " Current authoring text."
    source.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")
    payload = _candidate(name="the-skill-authoring", author_self_check=True)
    for identity, renderer in (
        ("t0:skill_author_self_check", entry.artifact.render_author_self_check_instruction),
        ("t0:skill_candidate_review_checklist", entry.artifact.render_reviewer_checklist),
    ):
        payload += (f"\n<!-- embedded-resource:{identity}:start -->\n".encode()
                    + renderer(source) + f"<!-- embedded-resource:{identity}:end -->\n".encode())
    candidate = root / "SKILL.md"
    candidate.write_bytes(payload)
    return candidate, source, adapter


def test_current_json_text_can_be_checked_without_updating_publication(tmp_path):
    candidate, source, _ = _json_resource_candidate(tmp_path)
    before = {path: path.read_bytes() for path in (tmp_path / "09_soul/governance").glob("*.json")}
    report = entry.check_skill(candidate, project_root=tmp_path)
    identity = "t0:skill_candidate_review_checklist"
    assert report["resource_sha256"][identity] == hashlib.sha256(entry.artifact.render_reviewer_checklist(source)).hexdigest()
    manifest = entry.release.load_governance_skill_manifest(tmp_path)
    resource = next(row for row in manifest.instruction_resources if row.resource_id == identity)
    with pytest.raises(ValueError, match="source hash mismatch"):
        entry.release._select_instruction_resource_bytes(
            resource, source.read_bytes(), project_root=tmp_path,
            artifact_contracts_by_source=entry.release._known_t0_artifact_contracts(tmp_path),
        )
    assert all(path.read_bytes() == content for path, content in before.items())


@pytest.mark.parametrize("problem", ["json", "adapter", "owner", "source_escape"])
def test_current_candidate_selection_preserves_resource_boundaries(tmp_path, problem):
    root = tmp_path / "project"
    candidate, source, adapter = _json_resource_candidate(root)
    if problem == "json":
        source.write_text('{}\n', encoding="utf-8")
    elif problem == "adapter":
        adapter.write_text("raise AssertionError('changed adapter must not execute')\n", encoding="utf-8")
    elif problem == "owner":
        path = root / "09_soul/governance/governance_skill_manifest.json"
        manifest = json.loads(path.read_bytes())
        row = next(row for row in manifest["instruction_resources"] if row["resource_id"] == "t0:skill_author_self_check")
        row["parent_dependency_id"] = "the_review_contract"
        path.write_text(json.dumps(manifest), encoding="utf-8")
    else:
        outside = tmp_path / "outside.json"
        outside.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(outside)
    with pytest.raises(ValueError):
        entry.check_skill(candidate, project_root=root)


@pytest.mark.parametrize("timing", ["before_dispatch", "after_dispatch"])
def test_current_json_source_remains_frozen_for_review(tmp_path, monkeypatch, timing):
    candidate, source, _ = _json_resource_candidate(tmp_path)
    check = tmp_path / "self-check.json"
    check.write_text(json.dumps({"candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "rows": [{"check_id": identity, "exact_evidence": "Current candidate section.",
                  "local_result": "Locally checked.", "unresolved_finding": None} for identity in check_ids()]}), encoding="utf-8")
    options = dict(candidate_path=candidate, self_check_path=check, project_root=tmp_path,
                   goal="Current text", change="Text-only candidate")
    calls = []
    def mutate():
        source.write_text(source.read_text().replace("Current authoring text.", "Changed after preparation."), encoding="utf-8")
    if timing == "before_dispatch":
        prepare = entry._prepare
        def moved(**kwargs):
            result = prepare(**kwargs)
            mutate()
            return result
        monkeypatch.setattr(entry, "_prepare", moved)
        with pytest.raises(ValueError, match="changed"):
            entry.review_skill(executor=lambda value: calls.append(value) or record(), **options)
        assert not calls
    else:
        def execute(value):
            calls.append(value)
            mutate()
            return record()
        result = entry.review_skill(executor=execute, **options)
        assert len(calls) == 1
        assert result["semantic_validation"]["status"] == "failed"


@pytest.mark.real_run
@REAL_GATE
def test_real_cli_supports_check_and_runtime_review_without_overwrites(args, tmp_path, reviewer_host):
    """Real entry: this CLI as a process, the Reviewer registered from this checkout, Runtime Test Run and Claude CLI.

    Retired executor variables are set and ignored.
    """
    checked = run_cli(ENTRY_PATH, "--candidate", args["candidate_path"], "--check-only")
    assert checked.returncode == 0, checked.stderr
    assert json.loads(checked.stdout)["subject_sha256"] == hashlib.sha256(args["candidate_path"].read_bytes()).hexdigest()
    output = tmp_path / "result.json"
    review = _review_cli_args(args, output, reviewer_host)
    result = run_cli(ENTRY_PATH, *review)
    saved = json.loads(output.read_text())
    verdict = assert_real_review(saved, "skill_candidate_reviewer", json.loads(result.stdout), summary_key="validation")
    assert result.returncode == (0 if verdict == "passed" else 1), result.stderr
    old = output.read_bytes()
    repeated = run_cli(ENTRY_PATH, *review)
    assert repeated.returncode != 0 and output.read_bytes() == old


def test_missing_executor_does_not_create_result(args, tmp_path, monkeypatch):
    monkeypatch.delenv("SKILL_REVIEW_EXECUTOR", raising=False)
    output = tmp_path / "absent.json"
    with pytest.raises(SystemExit):
        entry.main(["--candidate", str(args["candidate_path"]), "--goal", "Goal", "--change", "Change", "--self-check", str(args["self_check_path"]), "--output", str(output)])
    assert not output.exists()


def _review_cli_args(args, output, root):
    return ["--candidate", str(args["candidate_path"]), "--goal", args["goal"], "--change", args["change"],
            "--self-check", str(args["self_check_path"]), "--output", str(output), "--root", str(root)]


@pytest.mark.real_run
@REAL_GATE
@pytest.mark.parametrize("failure,error_type", [("unregistered_root", "FileNotFoundError"),
                                                ("mixed_transport", "ValueError")])
def test_real_runtime_failure_has_diagnostic_and_no_result(args, tmp_path, reviewer_host, failure, error_type):
    """Real entry: Runtime Test Run failing before any Provider call; nothing is substituted."""
    output = tmp_path / "result.json"
    if failure == "unregistered_root":
        result = run_cli(ENTRY_PATH, *_review_cli_args(args, output, tmp_path / "empty_root"))
    else:
        result = run_cli(ENTRY_PATH, *_review_cli_args(args, output, reviewer_host), "--transport", "codex_cli")
    assert result.returncode == 2 and result.stdout == "" and not output.exists()
    error = json.loads(result.stderr)
    assert set(error) == {"error", "error_type", "error_code"} and error["error_type"] == error_type and error["error"]


@pytest.mark.real_run
@REAL_GATE
def test_real_interrupt_during_the_model_call_never_becomes_a_verdict(args, tmp_path, reviewer_host):
    """Real entry: SIGINT to this CLI while the Claude CLI model process runs.

    Runtime owns the interrupt during Provider execution: it stops the model
    process and returns a cancelled record, which the CLI saves without a verdict.
    """
    output = tmp_path / "result.json"
    result = run_cli_interrupted(ENTRY_PATH, *_review_cli_args(args, output, reviewer_host))
    saved = json.loads(output.read_text())
    assert saved["status"] == "cancelled" and saved["failure_class"] == "cancelled"
    assert saved["semantic_validation"]["status"] != "passed"
    assert json.loads(result.stdout)["verdict"] is None and result.returncode == 1, result.stderr


def test_python_api_keeps_executor_exception(args):
    class ExecutorUnavailable(Exception):
        pass
    def execute(_):
        raise ExecutorUnavailable("Provider unavailable")
    with pytest.raises(ExecutorUnavailable, match="Provider unavailable"):
        entry.review_skill(executor=execute, **args)


@pytest.mark.parametrize("change", ["goal", "candidate", "context"])
def test_historical_record_cannot_bind_to_different_input(args, tmp_path, change):
    previous = entry.review_skill(executor=lambda _: record(), **args)
    preserved = copy.deepcopy(previous)
    if change == "goal":
        args["goal"] = "Different authorized goal"
    if change == "candidate":
        args["candidate_path"].write_bytes(args["candidate_path"].read_bytes() + b"\nUpdated method.\n")
        check = json.loads(args["self_check_path"].read_text())
        check["candidate_sha256"] = hashlib.sha256(args["candidate_path"].read_bytes()).hexdigest()
        args["self_check_path"].write_text(json.dumps(check), encoding="utf-8")
    if change == "context":
        context = tmp_path / "another-context.md"
        context.write_text("Additional input.", encoding="utf-8")
        args["context_bindings"] = [("skill", context)]
    result = entry.review_skill(executor=lambda _: previous, **args)
    assert result["semantic_validation"]["status"] == "failed"
    assert result["semantic_input"] == preserved["semantic_input"]
    assert result["subject_sha256"] == preserved["subject_sha256"]
    assert previous == preserved


@pytest.mark.parametrize("previous_validation", [
    {"status": "failed", "message": "Original rejection evidence"},
    {"status": "not_run", "message": "Original incomplete execution"},
    None,
    "invalid validation",
])
def test_rejected_record_is_not_revalidated_into_pass(args, previous_validation):
    previous = entry.review_skill(executor=lambda _: record(), **args)
    previous["semantic_validation"] = previous_validation
    preserved = copy.deepcopy(previous)
    result = entry.review_skill(executor=lambda _: previous, **args)
    assert result["semantic_validation"]["status"] == "failed"
    assert json.dumps(previous_validation, ensure_ascii=False) in result["semantic_validation"]["message"]
    assert result["semantic_input"] == preserved["semantic_input"]
    assert previous == preserved


def test_provided_candidate_hash_cannot_be_silently_replaced(args):
    previous = entry.review_skill(executor=lambda _: record(), **args)
    previous["subject_sha256"] = "0" * 64
    result = entry.review_skill(executor=lambda _: previous, **args)
    assert result["semantic_validation"]["status"] == "failed"
    assert result["subject_sha256"] == previous["subject_sha256"] == "0" * 64


def test_same_input_valid_record_can_be_checked_without_mutation(args):
    previous = entry.review_skill(executor=lambda _: record(), **args)
    preserved = copy.deepcopy(previous)
    result = entry.review_skill(executor=lambda _: previous, **args)
    assert result["semantic_validation"]["status"] == "passed"
    assert result["semantic_input"] == previous["semantic_input"]
    assert result["subject_sha256"] == previous["subject_sha256"]
    assert previous == preserved


def test_fresh_execution_after_rejection_remains_usable(args):
    invalid = record()
    invalid["module_release_ref"] = "runtime-module:another_reviewer@test"
    rejected = entry.review_skill(executor=lambda _: invalid, **args)
    assert rejected["semantic_validation"]["status"] == "failed"
    fresh = entry.review_skill(executor=lambda _: record(), **args)
    assert fresh["semantic_validation"]["status"] == "passed"


def test_previous_pass_does_not_skip_current_output_validation(args):
    previous = entry.review_skill(executor=lambda _: record(), **args)
    previous["output"]["check_results"].pop()
    result = entry.review_skill(executor=lambda _: previous, **args)
    assert result["semantic_validation"]["status"] == "failed"


@pytest.mark.deterministic
def test_invalid_input_is_rejected_before_runtime_is_called(args, tmp_path, monkeypatch):
    import agent_runtime
    monkeypatch.setattr(agent_runtime, "run_local_workflow_test", lambda **kw: pytest.fail("no Runtime call"), raising=False)
    result = entry.main(["--candidate", str(args["candidate_path"]), "--goal", " ", "--change", "Change",
                         "--self-check", str(args["self_check_path"]), "--output", str(tmp_path / "result.json"),
                         "--root", str(tmp_path / "root")])
    assert result == 2


@pytest.mark.deterministic
def test_cli_rejects_the_retired_executor_argument(args, tmp_path, capsys):
    with pytest.raises(SystemExit) as error:
        entry.main([*_review_cli_args(args, tmp_path / "result.json", tmp_path), "--executor", "module:function"])
    assert error.value.code == 2 and "--executor" in capsys.readouterr().err


def test_explicit_new_skill_checklist_does_not_require_editing_portable_manifest(tmp_path):
    governance = tmp_path / "09_soul/governance"
    governance.mkdir(parents=True)
    for name in ("governance_skill_manifest.json", "governance_t0_manifest.json"):
        shutil.copyfile(entry.PROJECT_ROOT / "09_soul/governance" / name, governance / name)
    identity = "skill:example_checklist"
    source = tmp_path / "checklist.md"; source.write_text("Check the declared example outcome.\n", encoding="utf-8")
    candidate = tmp_path / "candidate.md"
    candidate.write_bytes(_candidate(name="new-skill") + f"\n<!-- embedded-resource:{identity}:start -->\n{source.read_text()}<!-- embedded-resource:{identity}:end -->\n".encode())
    before = {path: path.read_bytes() for path in governance.glob("*.json")}
    report = entry.check_skill(candidate, project_root=tmp_path, resource_bindings=[(identity, source)])
    assert report["resource_sha256"][identity] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert all(path.read_bytes() == data for path, data in before.items())
    source.write_text("Changed canonical input.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="differ"):
        entry.check_skill(candidate, project_root=tmp_path, resource_bindings=[(identity, source)])


def test_extra_resource_cannot_override_registered_common_instructions(tmp_path):
    governance = tmp_path / "09_soul/governance"; governance.mkdir(parents=True)
    for name in ("governance_skill_manifest.json", "governance_t0_manifest.json"):
        shutil.copyfile(entry.PROJECT_ROOT / "09_soul/governance" / name, governance / name)
    identity = "t0:skill_authority_input_guard"
    source = tmp_path / "fake.md"; source.write_text("Other meaning.\n", encoding="utf-8")
    candidate = tmp_path / "candidate.md"
    candidate.write_bytes(_candidate() + f"\n<!-- embedded-resource:{identity}:start -->\nOther meaning.\n<!-- embedded-resource:{identity}:end -->\n".encode())
    with pytest.raises(ValueError, match="override"):
        entry.check_skill(candidate, project_root=tmp_path, resource_bindings=[(identity, source)])


def test_dangling_output_symlink_is_rejected_before_review(args, tmp_path):
    output = tmp_path / "link.json"; output.symlink_to(tmp_path / "not_created.json")
    with pytest.raises(SystemExit):
        entry.main(["--candidate", str(args["candidate_path"]), "--goal", "Goal", "--change", "Change",
                    "--self-check", str(args["self_check_path"]), "--executor", "must_not_import:execute", "--output", str(output)])
    assert not (tmp_path / "not_created.json").exists()


def test_self_check_template_is_code_bound_and_cannot_be_submitted_unfilled(args, tmp_path):
    target = tmp_path / "template.json"
    command = ["--candidate", str(args["candidate_path"]), "--check-only", "--self-check-template", str(target)]
    assert entry.main(command) == 0
    value = json.loads(target.read_text())
    assert value["candidate_sha256"] == hashlib.sha256(args["candidate_path"].read_bytes()).hexdigest()
    assert [row["check_id"] for row in value["rows"]] == check_ids()
    with pytest.raises(ValueError, match="empty exact evidence"):
        entry.review_skill(executor=lambda payload: pytest.fail("must not execute"), **{**args, "self_check_path": target})
    before = target.read_bytes()
    with pytest.raises(SystemExit):
        entry.main(command)
    assert target.read_bytes() == before
