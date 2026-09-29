from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from .test_artifact_contract import MODULE_PATH, _candidate


def run_cli(cwd: Path, *args: str, script: Path = MODULE_PATH):
    return subprocess.run(
        [sys.executable, "-I", "-B", str(script), *args],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=10,
    )


@pytest.mark.parametrize("layer", ["charter", "t0", "t1", "t2"])
def test_cli_checks_file_using_existing_contract(tmp_path, layer):
    payload = _candidate(layer)
    path = tmp_path / "candidate.md"
    path.write_bytes(payload)
    result = run_cli(tmp_path, "candidate.md", "--layer", layer.upper() if layer != "charter" else "Charter", "--json")
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == 1
    assert rows[0]["valid"] is True
    assert rows[0]["layer"] == layer
    assert rows[0]["subject_sha256"] == hashlib.sha256(payload).hexdigest()
    assert "design_required_section_schema" in rows[0]["validator_ids"]
    assert "verdict" not in rows[0]
    assert path.read_bytes() == payload
    assert set(tmp_path.iterdir()) == {path}


@pytest.mark.parametrize("payload, expected", [
    (b"# Empty design\n", "no numbered level-two sections"),
    (b"\xff", "UTF-8"),
    (_candidate("t0").replace(b"Reader Gain", b"Wrong Heading"), "Reader Gain"),
])
def test_cli_returns_actual_validation_failure(tmp_path, payload, expected):
    path = tmp_path / "bad.md"
    path.write_bytes(payload)
    result = run_cli(tmp_path, "bad.md", "--layer", "t0", "--json")
    assert result.returncode == 1
    row, = json.loads(result.stdout)
    assert row["valid"] is False
    assert row["error_code"] == "DESIGN_REPRESENTATION_INCOMPLETE"
    assert expected in row["message"]
    assert path.read_bytes() == payload


def test_cli_reports_missing_file_and_still_checks_other_files(tmp_path):
    (tmp_path / "valid.md").write_bytes(_candidate("t0"))
    result = run_cli(tmp_path, "missing.md", "valid.md", "--layer", "t0", "--json")
    assert result.returncode == 1
    missing, valid = json.loads(result.stdout)
    assert missing["file"] == "missing.md"
    assert missing["error_code"] == "FileNotFoundError"
    assert missing["valid"] is False
    assert valid["valid"] is True


@pytest.mark.parametrize("arguments", [(), ("--layer", "t0"), ("file.md",), ("file.md", "--layer", "t3")])
def test_cli_usage_errors_are_nonzero(tmp_path, arguments):
    result = run_cli(tmp_path, *arguments)
    assert result.returncode == 2
    assert "usage:" in result.stderr


def test_cli_help_and_human_output(tmp_path):
    result = run_cli(tmp_path, "--help")
    assert result.returncode == 0
    assert "--json" in result.stdout
    assert "不修改文件" in result.stdout
    (tmp_path / "valid.md").write_bytes(_candidate("t0"))
    result = run_cli(tmp_path, "valid.md", "--layer", "t0")
    assert result.returncode == 0
    assert "通过结构检查" in result.stdout
    assert "不代表语义审核通过" in result.stdout


def test_cli_is_portable_with_only_its_contract_json(tmp_path):
    isolated = tmp_path / "portable"
    isolated.mkdir()
    script = isolated / MODULE_PATH.name
    shutil.copyfile(MODULE_PATH, script)
    shutil.copyfile(MODULE_PATH.with_suffix(".json"), script.with_suffix(".json"))
    (tmp_path / "candidate.md").write_bytes(_candidate("t0"))
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    result = run_cli(tmp_path, "candidate.md", "--layer", "t0", "--json", script=script)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)[0]["valid"] is True
    after = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert before == after
