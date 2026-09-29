"""Engineering review materials: reviewed code frozen from Git and declared commands as Runtime resources."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from software_delivery import engineering_review_input as inputs
from software_delivery.engineering_review_materials import verify_materials, write_review_resources
from tests.runtime_review_real import REAL_GATE, assert_real_review, run_cli
from tests.software_delivery.test_engineering_review_plan_and_cli import plan_input, plan_record

CLI = Path(inputs.__file__).with_name("engineering_review.py")
COMMAND = {"command_id": "unit_tests", "argv": ["python", "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                                                "test_calc.py"],
           "cwd": "source/commit", "timeout_seconds": 300, "network_policy": "denied",
           "expected_result": "passed", "required": True}


def _repository(root: Path) -> Path:
    def git(*args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
    root.mkdir()
    git("init", "-q")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Test")
    (root / "calc.py").write_text("def add(a, b):\n    return a - b\n")
    (root / "test_calc.py").write_text("from calc import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n")
    (root / "gone.py").write_text("OLD = True\n")
    (root / "run.sh").write_text("#!/bin/sh\necho base\n")
    (root / "run.sh").chmod(0o755)
    (root / "docs").mkdir()
    (root / "docs" / "notes.md").write_text("notes\n")
    git("add", "-A")
    git("commit", "-qm", "base")
    (root / "calc.py").write_text("def add(a, b):\n    return a + b\n")
    (root / "gone.py").unlink()
    (root / "new.py").write_text("NEW = True\n")
    (root / "run.sh").write_text("#!/bin/sh\necho changed\n")
    git("add", "-A")
    git("commit", "-qm", "fix add")
    (root / "calc.py").write_text("UNCOMMITTED = True\n")  # working tree change must never be reviewed
    return root


def _implementation(repo: Path, commands=()):
    return inputs.build_engineering_review_input(
        repository_root=repo, commit_ref="HEAD", code_design_basis=plan_input()["code_design_basis"],
        code_design_review=inputs.hashed_body("review", json.dumps(plan_record())),
        sandbox_command_plan=inputs.command_plan("commands", list(commands)), acceptance_criteria=["Expected result"])


def _git_blob(repo: Path, spec: str) -> bytes:
    return subprocess.run(["git", "show", spec], cwd=repo, check=True, capture_output=True).stdout


@pytest.mark.deterministic
def test_implementation_materials_bind_both_sides_the_diff_and_read_files(tmp_path):
    repo = _repository(tmp_path / "repo")
    payload = _implementation(repo, [COMMAND])
    path = write_review_resources(payload=payload, repository_root=repo, read_paths=["test_calc.py", "docs"],
                                  commands=payload["sandbox_command_plan"]["commands"],
                                  dependencies=[Path("/usr")], target=tmp_path / "out")
    resource = json.loads(path.read_text())
    materials = tmp_path / "out" / "materials"
    listed = {row["relative_path"]: row for row in resource["material_files"]}
    assert set(listed) == {"commit/calc.py", "parent/calc.py", "parent/gone.py", "commit/new.py", "commit/run.sh",
                           "parent/run.sh", "commit/test_calc.py", "commit/docs/notes.md", "candidate.diff"}
    rows = {row["path"]: row for row in payload["subject"]["paths"]}
    assert hashlib.sha256((materials / "commit/calc.py").read_bytes()).hexdigest() == rows["calc.py"]["content_sha256"]
    assert (materials / "parent/calc.py").read_bytes() == _git_blob(repo, "HEAD^:calc.py")
    assert (materials / "commit/calc.py").read_bytes() != (materials / "parent/calc.py").read_bytes()
    assert b"UNCOMMITTED" not in (materials / "commit/calc.py").read_bytes()
    assert hashlib.sha256((materials / "parent/gone.py").read_bytes()).hexdigest() == rows["gone.py"]["content_sha256"]
    assert hashlib.sha256((materials / "candidate.diff").read_bytes()).hexdigest() == payload["subject"]["diff_sha256"]
    assert listed["commit/run.sh"]["executable"] and listed["parent/run.sh"]["executable"]
    assert not listed["commit/calc.py"]["executable"]
    for name, row in listed.items():
        assert hashlib.sha256((materials / name).read_bytes()).hexdigest() == row["sha256"]
        assert bool((materials / name).stat().st_mode & 0o111) == row["executable"], name  # Runtime checks the mode
    assert resource["material_root"] == "materials"
    assert resource["commands"] == [{key: COMMAND[key] for key in ("command_id", "argv", "cwd", "timeout_seconds")}]
    assert resource["read_only_dependencies"] == ["/usr"]


@pytest.mark.deterministic
@pytest.mark.parametrize("target", ["commit/calc.py", "parent/calc.py", "commit/test_calc.py", "candidate.diff"])
def test_changed_material_bytes_are_refused(tmp_path, target):
    repo = _repository(tmp_path / "repo")
    payload = _implementation(repo)
    write_review_resources(payload=payload, repository_root=repo, read_paths=["test_calc.py"], commands=[],
                           dependencies=[], target=tmp_path / "out")
    materials = tmp_path / "out" / "materials"
    (materials / target).write_bytes((materials / target).read_bytes() + b"# changed\n")
    with pytest.raises(ValueError, match="differs"):
        verify_materials(repo, payload["subject"], materials, ["test_calc.py"])


@pytest.mark.deterministic
@pytest.mark.parametrize("read", ["missing.py", "../outside.py", "/abs/path.py"])
def test_read_paths_must_be_in_the_reviewed_commit(tmp_path, read):
    repo = _repository(tmp_path / "repo")
    with pytest.raises(ValueError, match="--read"):
        write_review_resources(payload=_implementation(repo), repository_root=repo, read_paths=[read], commands=[],
                               dependencies=[], target=tmp_path / "out")


def _git(repo, *args, body=None):
    return subprocess.run(["git", *args], cwd=repo, input=body, check=True, capture_output=True).stdout.strip()


def _special_entry(repo, mode, *, target=b"notes.md", path="docs/special"):
    """Create real Git symlink/gitlink entries without a network or a submodule checkout."""
    oid = (_git(repo, "hash-object", "-w", "--stdin", body=target) if mode == "120000"
           else _git(repo, "rev-parse", "HEAD"))
    _git(repo, "update-index", "--add", "--cacheinfo", f"{mode},{oid.decode()},{path}")
    _git(repo, "commit", "-qm", "record special entry")


@pytest.mark.deterministic
@pytest.mark.parametrize("mode", ["120000", "160000"])
@pytest.mark.parametrize("change", ["added", "modified", "deleted"])
def test_changed_special_entries_are_refused_before_writing_materials(tmp_path, mode, change):
    repo = _repository(tmp_path / "repo")
    _special_entry(repo, mode)
    if change == "modified":
        _special_entry(repo, mode, target=b"another.md")
    elif change == "deleted":
        _git(repo, "update-index", "--force-remove", "docs/special")
        _git(repo, "commit", "-qm", "remove special entry")
    payload = _implementation(repo)
    assert payload["subject"]["paths"][0]["state"] == change
    target = tmp_path / "out"
    with pytest.raises(ValueError, match=f"unsupported Git mode {mode}"):
        write_review_resources(payload=payload, repository_root=repo, read_paths=[], commands=[],
                               dependencies=[], target=target)
    assert not target.exists()


@pytest.mark.deterministic
@pytest.mark.parametrize("mode", ["120000", "160000"])
@pytest.mark.parametrize("read", ["docs/special", "docs"])
def test_read_selection_refuses_special_entries_including_inside_directories(tmp_path, mode, read):
    repo = _repository(tmp_path / "repo")
    _special_entry(repo, mode)
    # The special entry is unchanged; the directory also contains a regular file.
    (repo / "docs/notes.md").write_text("updated notes\n")
    _git(repo, "add", "docs/notes.md")
    _git(repo, "commit", "-qm", "update ordinary file")
    target = tmp_path / "out"
    with pytest.raises(ValueError, match=f"unsupported Git mode {mode}"):
        write_review_resources(payload=_implementation(repo), repository_root=repo, read_paths=[read], commands=[],
                               dependencies=[], target=target)
    assert not target.exists()


@pytest.mark.deterministic
@pytest.mark.parametrize("mode", ["120000", "160000"])
def test_unselected_special_entries_do_not_block_regular_file_review(tmp_path, mode):
    repo = _repository(tmp_path / "repo")
    _special_entry(repo, mode)
    (repo / "docs/notes.md").write_text("updated notes\n")
    _git(repo, "add", "docs/notes.md")
    _git(repo, "commit", "-qm", "update ordinary file")
    path = write_review_resources(payload=_implementation(repo), repository_root=repo, read_paths=["run.sh"],
                                  commands=[], dependencies=[], target=tmp_path / "out")
    names = {row["relative_path"] for row in json.loads(path.read_text())["material_files"]}
    assert names == {"commit/docs/notes.md", "parent/docs/notes.md", "commit/run.sh", "candidate.diff"}


@pytest.mark.deterministic
def test_verify_materials_also_refuses_flattened_symlink_bytes(tmp_path):
    repo = _repository(tmp_path / "repo")
    _special_entry(repo, "120000")
    materials = tmp_path / "materials"
    (materials / "commit/docs").mkdir(parents=True)
    (materials / "commit/docs/special").write_bytes(_git_blob(repo, "HEAD:docs/special"))
    with pytest.raises(ValueError, match="unsupported Git mode 120000"):
        verify_materials(repo, _implementation(repo)["subject"], materials, [])


@pytest.mark.deterministic
@pytest.mark.parametrize("mutation", ["executable", "symlink"])
@pytest.mark.parametrize("relative", ["commit/calc.py", "parent/calc.py", "commit/test_calc.py"])
def test_verify_materials_refuses_changed_file_types_or_modes(tmp_path, mutation, relative):
    repo = _repository(tmp_path / "repo")
    payload = _implementation(repo)
    write_review_resources(payload=payload, repository_root=repo, read_paths=["test_calc.py"], commands=[],
                           dependencies=[], target=tmp_path / "out")
    materials = tmp_path / "out/materials"
    target = materials / relative
    if mutation == "executable":
        target.chmod(0o755)
    else:
        original = tmp_path / "same_bytes.py"
        original.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(original)
    with pytest.raises(ValueError, match="file type or executable mode differs"):
        verify_materials(repo, payload["subject"], materials, ["test_calc.py"])


@pytest.mark.deterministic
@pytest.mark.parametrize("from_mode,to_mode", [("100644", "100755"), ("100755", "100644")])
def test_regular_executable_mode_changes_preserve_both_sides(tmp_path, from_mode, to_mode):
    repo = _repository(tmp_path / "repo")
    path = "calc.py" if from_mode == "100644" else "run.sh"
    _git(repo, "update-index", "--chmod=" + ("+x" if to_mode == "100755" else "-x"), path)
    _git(repo, "commit", "-qm", "change executable mode")
    resource = write_review_resources(payload=_implementation(repo), repository_root=repo, read_paths=[], commands=[],
                                      dependencies=[], target=tmp_path / "out")
    files = {r["relative_path"]: r for r in json.loads(resource.read_text())["material_files"]}
    assert files["commit/" + path]["executable"] == (to_mode == "100755")
    assert files["parent/" + path]["executable"] == (from_mode == "100755")


@pytest.mark.deterministic
@pytest.mark.parametrize("from_mode,to_mode", [("100644", "120000"), ("120000", "100644")])
def test_file_type_changes_remain_rejected_by_the_subject_builder(tmp_path, from_mode, to_mode):
    repo = _repository(tmp_path / "repo")
    path = "docs/special"
    for mode in (from_mode, to_mode):
        oid = _git(repo, "hash-object", "-w", "--stdin", body=b"notes.md")
        _git(repo, "update-index", "--add", "--cacheinfo", f"{mode},{oid.decode()},{path}")
        _git(repo, "commit", "-qm", "record file type")
    with pytest.raises(inputs.EngineeringReviewInputError, match="unsupported Git path state"):
        _implementation(repo)


def _add_non_utf8_path(repo: Path, name: bytes) -> None:
    """Commit a tree entry whose path is not UTF-8, without needing such a file on disk."""
    oid = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=repo, input=b"legacy\n", check=True,
                         capture_output=True).stdout.strip()
    subprocess.run([b"git", b"update-index", b"--add", b"--cacheinfo", b"100644," + oid + b"," + name], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "legacy name"], cwd=repo, check=True)


@pytest.mark.deterministic
def test_unselected_non_utf8_paths_do_not_block_the_review(tmp_path):
    repo = _repository(tmp_path / "repo")
    subprocess.run(["git", "checkout", "--", "calc.py"], cwd=repo, check=True)
    _add_non_utf8_path(repo, b"legacy/caf\xe9.txt")
    (repo / "calc.py").write_text("def add(a, b):\n    return b + a\n")
    subprocess.run(["git", "add", "calc.py"], cwd=repo, check=True)  # the legacy entry exists only in Git
    subprocess.run(["git", "commit", "-qm", "reorder"], cwd=repo, check=True)
    payload = _implementation(repo)
    path = write_review_resources(payload=payload, repository_root=repo, read_paths=["test_calc.py"], commands=[],
                                  dependencies=[], target=tmp_path / "out")
    assert "commit/calc.py" in {row["relative_path"] for row in json.loads(path.read_text())["material_files"]}
    with pytest.raises(ValueError, match="not UTF-8"):
        write_review_resources(payload=payload, repository_root=repo, read_paths=["legacy"], commands=[],
                               dependencies=[], target=tmp_path / "legacy")


@pytest.mark.deterministic
def test_plan_review_resources_carry_only_declared_commands(tmp_path):
    payload = plan_input(sandbox_command_plan=inputs.command_plan("commands", [COMMAND]))
    path = write_review_resources(payload=payload, repository_root=None, read_paths=[],
                                  commands=payload["sandbox_command_plan"]["commands"], dependencies=[],
                                  target=tmp_path / "out")
    resource = json.loads(path.read_text())
    assert (resource["material_root"], resource["material_files"]) == (None, [])
    assert [row["command_id"] for row in resource["commands"]] == ["unit_tests"]
    assert write_review_resources(payload=plan_input(), repository_root=None, read_paths=[], commands=[],
                                  dependencies=[], target=tmp_path / "none") is None
    with pytest.raises(ValueError, match="implementation review"):
        write_review_resources(payload=plan_input(), repository_root=None, read_paths=["x.py"], commands=[],
                               dependencies=[], target=tmp_path / "read")


def _cli_implementation_files(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(plan_input()["code_design_basis"]["body"])
    review = tmp_path / "plan_review.json"
    review.write_text(json.dumps(plan_record()))
    return plan, review


@pytest.mark.deterministic
def test_cli_refuses_caller_resources(tmp_path):
    plan, _ = _cli_implementation_files(tmp_path)
    done = subprocess.run([sys.executable, "-B", str(CLI), "--plan", str(plan), "--goal", "g", "--change", "c",
                           "--criterion", "Expected result", "--resources", str(tmp_path / "r.json"), "--check-only"],
                          capture_output=True, text=True)
    assert done.returncode == 2 and "--resources is not accepted" in done.stderr


@pytest.mark.deterministic
def test_cli_check_only_reports_a_read_path_outside_the_commit(tmp_path):
    repo = _repository(tmp_path / "repo")
    plan, review = _cli_implementation_files(tmp_path)
    done = subprocess.run([sys.executable, "-B", str(CLI), "--plan", str(plan), "--goal", "g", "--change", "c",
                           "--criterion", "Expected result", "--repository", str(repo), "--commit", "HEAD",
                           "--plan-review", str(review), "--read", "missing.py", "--check-only"],
                          capture_output=True, text=True)
    assert done.returncode == 2 and "--read path is not in the reviewed commit" in done.stderr


@pytest.mark.deterministic
@pytest.mark.parametrize("mode", ["120000", "160000"])
def test_cli_check_only_reports_an_unsupported_selected_git_mode(tmp_path, mode):
    repo = _repository(tmp_path / "repo")
    _special_entry(repo, mode)
    (repo / "docs/notes.md").write_text("updated notes\n")
    _git(repo, "add", "docs/notes.md")
    _git(repo, "commit", "-qm", "update ordinary file")
    plan, review = _cli_implementation_files(tmp_path)
    done = subprocess.run([sys.executable, "-B", str(CLI), "--plan", str(plan), "--goal", "g", "--change", "c",
                           "--criterion", "Expected result", "--repository", str(repo), "--commit", "HEAD",
                           "--plan-review", str(review), "--read", "docs", "--check-only"],
                          capture_output=True, text=True)
    assert done.returncode == 2 and f"unsupported Git mode {mode}" in done.stderr


@pytest.mark.real_run
@REAL_GATE
def test_real_implementation_review_reads_the_frozen_commit_and_runs_its_tests(tmp_path, reviewer_host):
    """Real entry: the Engineering CLI freezes the commit, Runtime Test Run runs the Reviewer and its declared command."""
    # The working tree keeps an uncommitted calc.py that breaks the test; passing proves the frozen commit ran.
    repo = _repository(tmp_path / "repo")
    plan, review = _cli_implementation_files(tmp_path)
    commands = tmp_path / "commands.json"
    commands.write_text(json.dumps([COMMAND]))
    target = tmp_path / "result.json"
    result = run_cli(CLI, "--plan", plan, "--goal", "Fix add so the unit test passes",
                     "--change", "calc.add returns the sum", "--criterion", "Expected result",
                     "--repository", repo, "--commit", "HEAD", "--plan-review", review,
                     "--commands", commands, "--read", "test_calc.py", "--output", target, "--root", reviewer_host)
    record = json.loads(target.read_text())
    assert_real_review(record, "engineering_change_reviewer", json.loads(result.stdout))
    attempt, = (row for row in record["execution_log"]["attempts"] if row["attempt_id"] == record["attempt_id"])
    call, = (row for row in attempt["tool_calls"] if row["tool_name"] == "sandbox_command_execute")
    assert call["request"] == {"command_id": "unit_tests"} and call["status"] == "completed"
    assert call["response"]["returncode"] == 0 and call["response"]["cwd"].endswith("materials/source/commit")
