from __future__ import annotations

import importlib.util
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from test_skill_release import _skill_payload, _write_fixture_project


MODULE_PATH = Path(__file__).resolve().parents[1] / "install.py"
SPEC = importlib.util.spec_from_file_location("governance_install_test", MODULE_PATH)
installer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = installer
SPEC.loader.exec_module(installer)


@pytest.fixture
def source(tmp_path):
    root = tmp_path / "source"
    _write_fixture_project(root)
    package = root / "09_soul/governance"
    (package / "README.md").write_text("# Governance entry\n")
    validation = package / "t0/validation"
    validation.mkdir()
    for name in ("install.py", "t0_release.py", "skill_release.py"):
        shutil.copyfile(MODULE_PATH.with_name(name), validation / name)
    (root / ".env").write_text("NOT_A_REAL_SECRET=do_not_copy\n")
    (root / "CLAUDE.md").write_text("Project-specific instructions must not be copied.\n")
    return root


def test_install_copies_exact_package_and_declared_projections(source, tmp_path):
    target = tmp_path / "installed"
    original = (source / installer.skills.MANIFEST_RELATIVE_PATH).read_bytes()
    report = installer.install_governance(source, target)
    assert report["installed"] and report["package_checks_passed"]
    assert report["t0_count"] == report["skill_count"] == 1
    assert [x["code"] for x in report["project_requirements"]] == ["project_charter_missing"]
    assert not (target / "designDoc/the_charter.md").exists()
    assert not (target / ".env").exists()
    assert not (target / "governance_bindings").exists()
    assert not (target / "src").exists()
    assert "09_soul/governance/README.md" in (target / "CLAUDE.md").read_text()
    assert "Project-specific" not in (target / "CLAUDE.md").read_text()
    assert (target / "AGENTS.md").read_text() == "Read and follow CLAUDE.md first.\n"
    for host in (".claude", ".agents"):
        assert (target / host / "skills/engineering-example/SKILL.md").read_bytes() == (source / "09_soul/governance/skills/engineering-example/SKILL.md").read_bytes()
    assert (target / "designDoc/the_example.md").read_bytes() == (source / "09_soul/governance/t0/the_example.md").read_bytes()
    assert (source / installer.skills.MANIFEST_RELATIVE_PATH).read_bytes() == original
    assert (target / installer.skills.MANIFEST_RELATIVE_PATH).read_bytes() == original


def test_same_source_has_same_fingerprint_in_two_new_directories(source, tmp_path):
    first = installer.install_governance(source, tmp_path / "first")
    second = installer.install_governance(source, tmp_path / "second")
    assert first["source_sha256"] == second["source_sha256"]
    assert first["file_count"] == second["file_count"]
    hashes = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (source / "09_soul/governance").rglob("*") if p.is_file()}
    expected = hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    assert first["source_sha256"] == expected
    (source / "09_soul/governance/README.md").write_text("# Changed entry\n")
    third = installer.install_governance(source, tmp_path / "third")
    assert third["source_sha256"] != first["source_sha256"]


@pytest.mark.parametrize("kind", ["directory", "file", "symlink"])
def test_existing_destination_is_not_overwritten(source, tmp_path, kind):
    target = tmp_path / "existing"
    if kind == "directory": target.mkdir()
    elif kind == "file": target.write_text("keep")
    else: target.symlink_to(tmp_path / "missing")
    with pytest.raises(ValueError, match="new directory"):
        installer.install_governance(source, target)
    if kind == "file": assert target.read_text() == "keep"
    elif kind == "directory": assert not list(target.iterdir())
    else: assert target.is_symlink()


def test_source_cannot_be_an_installation_destination(source):
    target = source / "09_soul/governance/new"
    with pytest.raises(ValueError, match="source package"):
        installer.install_governance(source, target)
    assert not target.exists()


def test_missing_destination_parent_is_reported(source, tmp_path):
    target = tmp_path / "missing/new"
    with pytest.raises(ValueError, match="parent directory"):
        installer.install_governance(source, target)
    assert not target.parent.exists()


@pytest.mark.parametrize("kind", ["file", "directory"])
def test_source_symlinks_are_rejected_before_copy(source, tmp_path, kind):
    link = source / "09_soul/governance/linked"
    link.symlink_to(source / (".env" if kind == "file" else "designDoc"))
    target = tmp_path / "installed"
    with pytest.raises(ValueError, match="symlink"):
        installer.install_governance(source, target)
    assert not target.exists()


def test_escaping_projection_is_rejected_before_copy(source, tmp_path):
    path = source / installer.skills.MANIFEST_RELATIVE_PATH
    manifest = json.loads(path.read_text())
    manifest["portable_governance_skills"][0]["package_files"][0]["projections"][1]["target"] = "../escaped/SKILL.md"
    path.write_text(json.dumps(manifest))
    target = tmp_path / "installed"
    with pytest.raises(ValueError): installer.install_governance(source, target)
    assert not target.exists() and not (tmp_path / "escaped").exists()


def test_missing_declared_dependency_stops_before_copy(source, tmp_path):
    path = source / installer.skills.MANIFEST_RELATIVE_PATH
    manifest = json.loads(path.read_text())
    manifest["portable_governance_skills"][0]["required_soul_resource_ids"] = ["soul:communication"]
    path.write_text(json.dumps(manifest))
    target = tmp_path / "installed"
    with pytest.raises(FileNotFoundError): installer.install_governance(source, target)
    assert not target.exists()


def test_declared_soul_dependency_is_copied_and_fingerprinted(source, tmp_path):
    path = source / installer.skills.MANIFEST_RELATIVE_PATH
    manifest = json.loads(path.read_text())
    manifest["portable_governance_skills"][0]["required_soul_resource_ids"] = ["soul:communication"]
    path.write_text(json.dumps(manifest))
    dependency = source / "09_soul/core/COMMUNICATION.md"
    dependency.parent.mkdir()
    dependency.write_text("# Communication\nKeep the task boundary clear.\n")
    first = installer.install_governance(source, tmp_path / "first")
    assert first["package_checks_passed"]
    assert (tmp_path / "first/09_soul/core/COMMUNICATION.md").read_bytes() == dependency.read_bytes()
    dependency.write_text("# Communication\nReport observable results.\n")
    second = installer.install_governance(source, tmp_path / "second")
    assert first["source_sha256"] != second["source_sha256"]


def test_stale_hash_is_reported_without_rewriting_source_or_copy(source, tmp_path, capsys):
    path = source / installer.skills.MANIFEST_RELATIVE_PATH
    manifest = json.loads(path.read_text())
    manifest["portable_governance_skills"][0]["package_files"][0]["sha256"] = "0" * 64
    path.write_text(json.dumps(manifest))
    original = path.read_bytes()
    target = tmp_path / "installed"
    report = installer.install_governance(source, target)
    assert report["installed"] and not report["package_checks_passed"]
    assert report["checks"]["t0"]["passed"]
    assert "source hash mismatch" in report["checks"]["skill"]["error"]
    assert path.read_bytes() == (target / installer.skills.MANIFEST_RELATIVE_PATH).read_bytes() == original
    assert installer.main(["--source-root", str(source), "--target-root", str(tmp_path / "cli_copy")]) == 1
    assert json.loads(capsys.readouterr().out)["package_checks_passed"] is False


def test_undeclared_package_content_is_not_hidden_from_checker(source, tmp_path):
    (source / "09_soul/governance/EXTRA.md").write_text("Undeclared package material.\n")
    report = installer.install_governance(source, tmp_path / "installed")
    assert not report["package_checks_passed"]
    assert "governance_package_undeclared_root_member" in [x["code"] for x in report["checks"]["t0"]["issues"]]


def test_source_change_during_capture_stops_before_writing(source, tmp_path, monkeypatch):
    file = source / "09_soul/governance/t0/the_example.md"
    original_read = Path.read_bytes
    changed = False
    def read(path):
        nonlocal changed
        content = original_read(path)
        if path == file and not changed:
            changed = True
            path.write_bytes(content + b"changed\n")
        return content
    monkeypatch.setattr(Path, "read_bytes", read)
    target = tmp_path / "installed"
    with pytest.raises(ValueError, match="source changed"):
        installer.install_governance(source, target)
    assert not target.exists()


def test_copied_cli_can_install_same_package_again_without_project_imports(source, tmp_path):
    first = installer.install_governance(source, tmp_path / "first")
    command = Path(first["target_root"]) / "09_soul/governance/t0/validation/install.py"
    second = tmp_path / "second"
    run = subprocess.run([sys.executable, "-I", "-B", str(command), "--target-root", str(second)], cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr + run.stdout
    report = json.loads(run.stdout)
    assert report["source_sha256"] == first["source_sha256"]
    assert report["package_checks_passed"]
    run = subprocess.run([sys.executable, "-I", "-B", str(command), "--target-root", str(second)], cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert run.returncode == 2
    assert json.loads(run.stdout)["installed"] is False


def _file_bytes(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


def _revise_source(root):
    for relative, manifest_relative, section in [
        ("09_soul/governance/t0/the_example.md", installer.t0.MANIFEST_RELATIVE_PATH, "portable_t0_contracts"),
        ("09_soul/governance/skills/engineering-example/SKILL.md", installer.skills.MANIFEST_RELATIVE_PATH, "portable_governance_skills"),
    ]:
        path = root / relative
        path.write_bytes(path.read_bytes() + b"\nUpdated portable content.\n")
        manifest_path = root / manifest_relative
        manifest = json.loads(manifest_path.read_bytes())
        row = manifest[section][0]
        if section == "portable_governance_skills":
            row = row["package_files"][0]
        row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest))


def test_update_replaces_portable_content_and_preserves_host_files(source, tmp_path):
    target = tmp_path / "installed"
    installer.install_governance(source, target)
    binding = b"## Project Runtime Bindings\n\nModule: `example_module`.\n"
    _write_fixture_project(target, binding_payload=binding)
    installer.skills.apply_governance_skill_release(target)
    host_files = {
        "CLAUDE.md": b"Host entry\n", "AGENTS.md": b"Host agent entry\n",
        "designDoc/the_charter.md": b"# Project Charter\n",
        ".env": b"FAKE_CREDENTIAL=preserve\n", "src/business.py": b"business = True\n",
        ".runtime/module/example/v1.json": b"{}\n",
        ".agents/skills/host-only/SKILL.md": b"# Host-only method\n",
    }
    for name, body in host_files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    bindings_before = _file_bytes(target / "governance_bindings")
    _revise_source(source)
    source_before = _file_bytes(source)
    report = installer.install_governance(source, target, update=True)
    assert report["installed"] and report["package_checks_passed"]
    for name, body in host_files.items():
        assert (target / name).read_bytes() == body
    assert _file_bytes(target / "governance_bindings") == bindings_before
    assert _file_bytes(source) == source_before
    for name, body in source_before.items():
        if name.startswith("09_soul/governance/"):
            assert (target / name).read_bytes() == body
    assert (target / "designDoc/the_example.md").read_bytes() == (source / "09_soul/governance/t0/the_example.md").read_bytes()
    instruction = (source / "09_soul/governance/skills/engineering-example/SKILL.md").read_bytes()
    for host in (".claude", ".agents"):
        assert (target / host / "skills/engineering-example/SKILL.md").read_bytes() == instruction + b"\n" + binding
    first = _file_bytes(target)
    repeated = installer.install_governance(source, target, update=True)
    assert repeated["package_checks_passed"] and repeated["source_sha256"] == report["source_sha256"]
    assert _file_bytes(target) == first


@pytest.mark.parametrize("kind", ["missing", "file", "symlink"])
def test_update_requires_existing_real_directory(source, tmp_path, kind):
    target = tmp_path / "target"
    if kind == "file":
        target.write_text("keep")
    elif kind == "symlink":
        target.symlink_to(source, target_is_directory=True)
    before = _file_bytes(source)
    with pytest.raises(ValueError):
        installer.install_governance(source, target, update=True)
    assert _file_bytes(source) == before
    if kind == "missing":
        assert not target.exists()
    elif kind == "file":
        assert target.read_text() == "keep"
    else:
        assert target.is_symlink()


@pytest.mark.parametrize("kind", ["directory", "symlink", "broken_symlink", "fifo", "parent_file"])
def test_update_checks_all_managed_paths_before_overwrite(source, tmp_path, kind):
    target = tmp_path / "target"
    installer.install_governance(source, target)
    _revise_source(source)
    occupied = target / ".agents/skills/engineering-example/SKILL.md"
    occupied.unlink()
    if kind == "directory":
        occupied.mkdir()
    elif kind == "symlink":
        occupied.symlink_to(source / ".env")
    elif kind == "broken_symlink":
        occupied.symlink_to(target / "unrelated")
    elif kind == "fifo":
        os.mkfifo(occupied)
    else:
        occupied.parent.rmdir()
        occupied.parent.write_text("keep parent file")
    before = _file_bytes(target)
    with pytest.raises((ValueError, OSError)):
        installer.install_governance(source, target, update=True)
    assert _file_bytes(target) == before
    assert (source / ".env").read_text() == "NOT_A_REAL_SECRET=do_not_copy\n"


def test_update_source_change_stops_before_overwrite(source, tmp_path, monkeypatch):
    target = tmp_path / "target"
    installer.install_governance(source, target)
    before = _file_bytes(target)
    changed_path = source / "09_soul/governance/t0/the_example.md"
    original = Path.read_bytes
    changed = False
    def read(path):
        nonlocal changed
        data = original(path)
        if path == changed_path and not changed:
            changed = True
            path.write_bytes(data + b"changed\n")
        return data
    monkeypatch.setattr(Path, "read_bytes", read)
    with pytest.raises(ValueError, match="source changed"):
        installer.install_governance(source, target, update=True)
    assert _file_bytes(target) == before


def test_update_can_resume_after_interrupted_copy(source, tmp_path, monkeypatch, capsys):
    target = tmp_path / "target"
    installer.install_governance(source, target)
    _revise_source(source)
    original = installer.skills._write_bytes_atomically
    calls = 0
    def interrupted(path, body):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated copy interruption")
        original(path, body)
    monkeypatch.setattr(installer.skills, "_write_bytes_atomically", interrupted)
    args = ["--source-root", str(source), "--target-root", str(target), "--update"]
    assert installer.main(args) == 2
    failure = json.loads(capsys.readouterr().out)
    assert failure["installed"] is False and "simulated" in failure["error"]
    assert "部分" in failure["message"]
    monkeypatch.setattr(installer.skills, "_write_bytes_atomically", original)
    assert installer.main(args) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["package_checks_passed"]
    assert (target / "designDoc/the_example.md").read_bytes() == (source / "09_soul/governance/t0/the_example.md").read_bytes()


@pytest.mark.parametrize("kind", ["hash", "leftover"])
def test_update_never_hides_bad_package_or_deletes_leftovers(source, tmp_path, capsys, kind):
    target = tmp_path / "target"
    installer.install_governance(source, target)
    if kind == "hash":
        path = source / "09_soul/governance/skills/engineering-example/SKILL.md"
        path.write_bytes(path.read_bytes() + b"\nUnreleased change.\n")
    else:
        (target / "09_soul/governance/EXTRA.md").write_text("Keep for inspection.\n")
    code = installer.main(["--source-root", str(source), "--target-root", str(target), "--update"])
    result = json.loads(capsys.readouterr().out)
    assert code in (1, 2) and result.get("package_checks_passed") is not True
    if kind == "leftover":
        assert code == 1
        assert (target / "09_soul/governance/EXTRA.md").read_text() == "Keep for inspection.\n"


def test_update_invalid_binding_preserves_existing_skill_projection(source, tmp_path, capsys):
    target = tmp_path / "target"
    installer.install_governance(source, target)
    binding = b"## Project Runtime Bindings\n\nModule: `example_module`.\n"
    _write_fixture_project(target, binding_payload=binding)
    installer.skills.apply_governance_skill_release(target)
    projected = target / ".claude/skills/engineering-example/SKILL.md"
    before = projected.read_bytes()
    (target / "governance_bindings/skills/engineering-example.md").write_bytes(binding + b"changed\n")
    _revise_source(source)
    assert installer.main(["--source-root", str(source), "--target-root", str(target), "--update"]) == 2
    failure = json.loads(capsys.readouterr().out)
    assert "binding" in failure["error"] and projected.read_bytes() == before


def test_copied_cli_updates_existing_target_with_default_source(source, tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    installer.install_governance(source, first)
    installer.install_governance(source, second)
    _revise_source(first)
    command = first / "09_soul/governance/t0/validation/install.py"
    run = subprocess.run([sys.executable, "-I", "-B", str(command), "--target-root", str(second), "--update"],
                         cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stdout + run.stderr
    result = json.loads(run.stdout)
    assert result["package_checks_passed"]
    assert (second / "designDoc/the_example.md").read_bytes() == (first / "09_soul/governance/t0/the_example.md").read_bytes()


def test_update_copies_new_declared_dependency_and_missing_dependency_is_read_only(source, tmp_path):
    target = tmp_path / "target"
    installer.install_governance(source, target)
    manifest_path = source / installer.skills.MANIFEST_RELATIVE_PATH
    manifest = json.loads(manifest_path.read_bytes())
    manifest["portable_governance_skills"][0]["required_soul_resource_ids"] = ["soul:communication"]
    manifest_path.write_text(json.dumps(manifest))
    before = _file_bytes(target)
    with pytest.raises(FileNotFoundError):
        installer.install_governance(source, target, update=True)
    assert _file_bytes(target) == before
    dependency = source / "09_soul/core/COMMUNICATION.md"
    dependency.parent.mkdir()
    dependency.write_text("# Communication\nPreserve the agreed scope.\n")
    assert installer.install_governance(source, target, update=True)["package_checks_passed"]
    assert (target / "09_soul/core/COMMUNICATION.md").read_bytes() == dependency.read_bytes()


def test_update_atomic_replacement_does_not_modify_host_hardlink(source, tmp_path):
    target = tmp_path / "target"
    installer.install_governance(source, target)
    portable = target / "09_soul/governance/README.md"
    host_file = target / "host-note.txt"
    os.link(portable, host_file)
    original_host = host_file.read_bytes()
    (source / "09_soul/governance/README.md").write_text("# New portable entry\n")
    report = installer.install_governance(source, target, update=True)
    assert report["package_checks_passed"]
    assert portable.read_text() == "# New portable entry\n"
    assert host_file.read_bytes() == original_host


def test_update_keeps_missing_host_entries_missing(source, tmp_path):
    target = tmp_path / "existing-project"
    target.mkdir()
    (target / "business.txt").write_text("keep\n")
    report = installer.install_governance(source, target, update=True)
    assert report["package_checks_passed"]
    assert not (target / "CLAUDE.md").exists() and not (target / "AGENTS.md").exists()
    assert (target / "business.txt").read_text() == "keep\n"


ORCHESTRATION = "paseo-orchestrator"


def _add_orchestration_skill(root):
    package = f"09_soul/governance/skills/{ORCHESTRATION}"
    files = {
        "SKILL.md": _skill_payload(name=ORCHESTRATION, role="operator")
        + b"\nDefaults live in [launch defaults](references/launch-defaults.json).\n",
        "references/launch-defaults.json": b"{}\n",
    }
    for relative, body in files.items():
        path = root / package / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    manifest_path = root / installer.skills.MANIFEST_RELATIVE_PATH
    manifest = json.loads(manifest_path.read_bytes())
    manifest["portable_governance_skills"].append({
        "skill_id": ORCHESTRATION, "required_t0_layer_ids": ["the_example"],
        "required_soul_resource_ids": [], "primary_agent_entry_role": "operator",
        "primary_agent_entry_subject": "engineering_change_candidate",
        "accountable_owner_ref": "designDoc/the_example.md", "lifecycle_state": "developing",
        "managed_target_ref": None, "direct_entry_disposition": "active",
        "predecessor_skill_id": None, "retirement_tombstone": None,
        "package_files": [
            {"source": f"{package}/{relative}", "sha256": hashlib.sha256(body).hexdigest(),
             "embedded_resource_ids": [],
             "projections": [{"host_id": host, "target": f"{prefix}/{ORCHESTRATION}/{relative}"}
                             for host, prefix in (("claude", ".claude/skills"), ("codex", ".agents/skills"))]}
            for relative, body in files.items()
        ],
    })
    manifest_path.write_text(json.dumps(manifest))
    return files


@pytest.mark.deterministic
def test_fresh_install_entry_points_to_projected_orchestration_skill(source, tmp_path):
    files = _add_orchestration_skill(source)
    target = tmp_path / "installed"
    report = installer.install_governance(source, target)
    assert report["package_checks_passed"] and report["skill_count"] == 2
    entry = (target / "CLAUDE.md").read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", entry)
    assert links == [f".claude/skills/{ORCHESTRATION}/SKILL.md", f".agents/skills/{ORCHESTRATION}/SKILL.md"]
    for link in links:
        skill = target / link
        assert skill.read_bytes() == files["SKILL.md"]
        for resource in re.findall(rb"\]\(([^)]+)\)", skill.read_bytes()):
            assert (skill.parent / resource.decode()).read_bytes() == files[resource.decode()]
    assert "直接承接用户完整项目任务的 Primary Agent" in entry
    assert "受委派执行任务的会话直接完成交给它的任务，不再委派。" in entry
    assert (target / "AGENTS.md").read_text() == "Read and follow CLAUDE.md first.\n"


@pytest.mark.deterministic
def test_fresh_install_entry_links_package_root_skill_not_nested_skill_resource(source, tmp_path):
    files = _add_orchestration_skill(source)
    package = f"09_soul/governance/skills/{ORCHESTRATION}"
    nested = b"# Nested resource named SKILL.md\n"
    (source / package / "references/SKILL.md").write_bytes(nested)
    manifest_path = source / installer.skills.MANIFEST_RELATIVE_PATH
    manifest = json.loads(manifest_path.read_bytes())
    manifest["portable_governance_skills"][-1]["package_files"].append({
        "source": f"{package}/references/SKILL.md", "sha256": hashlib.sha256(nested).hexdigest(),
        "embedded_resource_ids": [],
        "projections": [{"host_id": "claude", "target": f".claude/skills/{ORCHESTRATION}/references/SKILL.md"}],
    })
    manifest_path.write_text(json.dumps(manifest))
    target = tmp_path / "installed"
    report = installer.install_governance(source, target)
    assert report["package_checks_passed"]
    entry = (target / "CLAUDE.md").read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", entry)
    assert links == [f".claude/skills/{ORCHESTRATION}/SKILL.md", f".agents/skills/{ORCHESTRATION}/SKILL.md"]
    for link in links:
        assert (target / link).read_bytes() == files["SKILL.md"]
    assert (target / f".claude/skills/{ORCHESTRATION}/references/SKILL.md").read_bytes() == nested


@pytest.mark.deterministic
def test_fresh_install_entry_omits_orchestration_when_package_lacks_it(source, tmp_path):
    target = tmp_path / "installed"
    installer.install_governance(source, target)
    entry = (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert ORCHESTRATION not in entry and "](" not in entry


@pytest.mark.deterministic
def test_update_keeps_existing_entries_and_projects_orchestration_to_both_hosts(source, tmp_path):
    target = tmp_path / "installed"
    installer.install_governance(source, target)
    entries = {"CLAUDE.md": b"Host entry\n", "AGENTS.md": b"Host agent entry\n"}
    for name, body in entries.items():
        (target / name).write_bytes(body)
    files = _add_orchestration_skill(source)
    report = installer.install_governance(source, target, update=True)
    assert report["package_checks_passed"] and report["skill_count"] == 2
    for name, body in entries.items():
        assert (target / name).read_bytes() == body
    for host in (".claude", ".agents"):
        for relative, body in files.items():
            assert (target / host / "skills" / ORCHESTRATION / relative).read_bytes() == body
