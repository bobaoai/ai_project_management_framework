"""Real Agent Runtime entry for portable review tests.

real_run tests install this Portable checkout into a temporary host with
install.py, register every shipped Reviewer there with
agent_runtime.register_reviewer, and run reviews through Agent Runtime Test Run
and the installed Provider CLI. Nothing is substituted.

Run them with PORTABLE_REVIEW_REAL_RUN=1 and the candidate Agent Runtime
importable (for example PYTHONPATH=<the_agent_runtime>/src). The Claude cases
require an authenticated Claude CLI. The Codex budget case requires
AGENT_RUNTIME_CODEX_BIN to name an executable, authenticated Codex CLI; when
unset, that case is skipped
as unverified. The host has no execution parameter file, so Claude reviews run
with the Runtime default model and effort, the configuration reviews use in
practice; each result must pass its owning validator.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

import pytest


VALIDATION_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = VALIDATION_ROOT.parents[3]
REAL_RUN = os.environ.get("PORTABLE_REVIEW_REAL_RUN") == "1"
REAL_GATE = pytest.mark.skipif(not REAL_RUN, reason="unverified: set PORTABLE_REVIEW_REAL_RUN=1 with the candidate "
                               "Agent Runtime importable and an authenticated Claude CLI")
RETIRED_EXECUTOR_VARIABLES = ("DDM_REVIEW_EXECUTOR", "SKILL_REVIEW_EXECUTOR", "EXPERIMENT_REVIEW_EXECUTOR",
                              "ENGINEERING_REVIEW_EXECUTOR")
CLI_TIMEOUT_SECONDS = 1500


def install_reviewer_host(target: Path) -> Path:
    """Install this checkout into a new host and register every shipped Reviewer there."""
    import install
    from agent_runtime import register_reviewer
    install.install_governance(PROJECT_ROOT, target)
    manifest = json.loads((PROJECT_ROOT / "09_soul/governance/governance_skill_manifest.json").read_text(encoding="utf-8"))
    for skill in manifest["portable_governance_skills"]:
        for entry in skill["package_files"]:
            match = re.search(r"/runtime_modules/([a-z][a-z0-9_]*)/module_registration\.json$", entry["source"])
            if match:
                register_reviewer(target, skill_id=skill["skill_id"], module_id=match.group(1), module_version="v1")
    return target


def run_cli(script: Path, *arguments) -> subprocess.CompletedProcess:
    """Run a review CLI as its own process with every retired executor variable set."""
    environment = dict(os.environ, **{name: "retired_module:review" for name in RETIRED_EXECUTOR_VARIABLES})
    return subprocess.run([sys.executable, "-B", str(script), *map(str, arguments)], capture_output=True, text=True,
                          timeout=CLI_TIMEOUT_SECONDS, env=environment)


def run_cli_interrupted(script: Path, *arguments) -> subprocess.CompletedProcess:
    """Run a review CLI and send it SIGINT once its Claude CLI model process is running."""
    environment = dict(os.environ, **{name: "retired_module:review" for name in RETIRED_EXECUTOR_VARIABLES})
    process = subprocess.Popen([sys.executable, "-B", str(script), *map(str, arguments)], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, env=environment)
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline and process.poll() is None:
        children = subprocess.run(["pgrep", "-P", str(process.pid)], capture_output=True, text=True).stdout.split()
        commands = [subprocess.run(["ps", "-o", "command=", "-p", child], capture_output=True, text=True).stdout
                    for child in children]
        if any(" -p " in command for command in commands):  # the model call, not the --version/--help preflight
            time.sleep(2)
            process.send_signal(signal.SIGINT)
            break
        time.sleep(0.2)
    else:
        process.kill()
        raise AssertionError("the Claude CLI model process never started")
    stdout, stderr = process.communicate(timeout=CLI_TIMEOUT_SECONDS)
    return subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)


def assert_real_review(record: dict, module_id: str, summary: dict, *, record_key: str = "semantic_validation",
                       summary_key: str = "output_validation") -> str:
    """Check that a saved record is a completed Runtime run of this Reviewer with a valid result.

    The owning validator must have accepted the output; the verdict may be any
    valid passed, non_pass or blocked. Returns the verdict for the caller's
    exit-code check. With PORTABLE_REVIEW_EVIDENCE_DIR set, the record is also
    saved there under the current test's name for the evidence report.
    """
    evidence = os.environ.get("PORTABLE_REVIEW_EVIDENCE_DIR")
    if evidence:
        test = os.environ["PYTEST_CURRENT_TEST"].split(" ")[0]
        name = re.sub(r"[^A-Za-z0-9_.-]+", "_", test.split("::", 1)[1]) + f".{module_id}.json"
        (Path(evidence) / name).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    assert record["status"] == "completed", record.get("failure_detail")
    assert record["managed_runtime"] is True and record["execution"] == "run_workflow_module"
    assert record["module_release_ref"].startswith(f"runtime-module:{module_id}@")
    assert record["workflow_release_ref"].startswith(f"runtime-workflow:{module_id}@")
    assert {source["layer"] for source in record["execution_parameter_sources"].values()} == {"runtime_default"}
    validation = record[record_key]
    assert validation["status"] == "passed", validation
    assert summary[summary_key]["status"] == "passed"
    verdict = record["output"]["verdict"]
    assert verdict in {"passed", "non_pass", "blocked"} and summary["verdict"] == verdict
    return verdict
