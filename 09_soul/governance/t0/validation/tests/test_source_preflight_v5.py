from pathlib import Path
import hashlib
import json
import shutil
import pytest
from test_t0_release import _write_fixture_project, release, _valid_t0
from test_governance_install import installer, source

pytestmark = pytest.mark.deterministic


def _snapshot(root):
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and not {"__pycache__", ".pytest_cache"}.intersection(p.parts)
    }


def _change_source(root, mutation):
    manifest = root / "09_soul/governance/governance_t0_manifest.json"
    data = json.loads(manifest.read_text())
    row = data["portable_t0_contracts"][0]
    p = root / row["source"]
    body = p.read_bytes()
    if mutation == "module":
        body = body.replace(b"## 1. Intended Outcomes", b"## 1. Made-up Module")
    elif mutation == "identity":
        body = body.replace(b"title: the_example\n", b"")
    elif mutation == "reference":
        body += b"\n[Missing file](missing.md)\n"
    else:
        raise AssertionError(mutation)
    p.write_bytes(body)
    row["sha256"] = hashlib.sha256(body).hexdigest()
    manifest.write_text(json.dumps(data))


@pytest.mark.parametrize("mutation", ["module", "identity", "reference"])
def test_t0_check_and_apply_share_strict_admission_before_any_write(tmp_path, mutation):
    _write_fixture_project(
        tmp_path, target_payload=_valid_t0("the_example", b"# Portable T0\n")
    )
    _change_source(tmp_path, mutation)
    before = _snapshot(tmp_path)
    for run in [
        release.check_governance_t0_release,
        release.apply_governance_t0_release,
    ]:
        with pytest.raises(ValueError, match="DDM source check failed"):
            run(tmp_path)
        assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("mutation", ["module", "identity", "reference"])
@pytest.mark.parametrize("update", [False, True])
def test_installer_rejects_valid_hash_but_invalid_design_before_writing(
    source, tmp_path, mutation, update
):
    target = tmp_path / "target"
    if update:
        installer.install_governance(source, target)
    before = _snapshot(target) if update else None
    _change_source(source, mutation)
    with pytest.raises(ValueError, match="DDM source check failed"):
        installer.install_governance(source, target, update=update)
    assert (_snapshot(target) == before) if update else not target.exists()


def test_source_only_install_never_borrows_project_projections_policy_or_bindings(
    source, tmp_path
):
    shutil.rmtree(source / "designDoc")
    for name in [".claude", ".agents"]:
        if (source / name).exists():
            shutil.rmtree(source / name)
    bindings = source / "governance_bindings"
    bindings.mkdir(exist_ok=True)
    (bindings / "governance_skill_binding_manifest.json").write_text(
        "invalid source-host binding"
    )
    (bindings / "governance_release_policy.json").write_text(
        "invalid source-host policy"
    )
    report = installer.install_governance(source, tmp_path / "target")
    assert (
        report["package_checks_passed"]
        and report["project_requirements"][0]["code"] == "project_charter_missing"
    )
    assert not (tmp_path / "target/governance_bindings").exists()


def test_target_binding_error_is_zero_write_for_the_whole_update(source, tmp_path):
    target = tmp_path / "target"
    installer.install_governance(source, target)
    bindings = target / "governance_bindings"
    bindings.mkdir()
    (bindings / "governance_skill_binding_manifest.json").write_text(
        "invalid target binding"
    )
    before = _snapshot(target)
    with pytest.raises(
        ValueError, match="cannot read Governance Skill binding manifest"
    ):
        installer.install_governance(source, target, update=True)
    assert _snapshot(target) == before


def test_target_charter_keeps_its_project_contract_and_is_not_migrated_to_v5(
    source, tmp_path
):
    target = tmp_path / "target"
    target.mkdir()
    (target / "designDoc").mkdir()
    charter = target / "designDoc/the_charter.md"
    body = b"# Existing project Charter without new Design metadata\n"
    charter.write_bytes(body)
    report = installer.install_governance(source, target, update=True)
    assert report["package_checks_passed"] and not report["project_requirements"]
    assert charter.read_bytes() == body


def test_validation_and_projections_use_captured_source_during_aba_change(
    source, tmp_path, monkeypatch
):
    manifest_path = source / installer.skills.MANIFEST_RELATIVE_PATH
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    row = manifest["portable_governance_skills"][0]["package_files"][0]
    path = source / row["source"]
    original = path.read_bytes()
    changed = original + b"\n<!-- parallel source revision -->\n"
    real_validate = installer.skills.validate_governance_skill_sources

    def inspect_snapshot(frozen):
        assert frozen != source
        path.write_bytes(changed)
        row["sha256"] = hashlib.sha256(changed).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        try:
            result = real_validate(frozen)
            assert (frozen / row["source"]).read_bytes() == original
            return result
        finally:
            path.write_bytes(original)
            manifest_path.write_bytes(manifest_bytes)

    monkeypatch.setattr(
        installer.skills, "validate_governance_skill_sources", inspect_snapshot
    )
    prepared = installer.prepare_governance_install(source, tmp_path / "target")
    assert not prepared.target_root.exists()
    assert prepared.payloads[row["source"]] == original
    for projection in row["projections"]:
        assert prepared.payloads[projection["target"]] == original
