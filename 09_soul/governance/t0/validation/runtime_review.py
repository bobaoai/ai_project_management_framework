"""One Runtime Test Run binding shared by every portable review object.

Each object tool keeps its own material preparation and owning validator. This
module only turns declarative CLI arguments into the public Agent Runtime
Test Run API fields, runs the exact Reviewer and checks that the returned record
belongs to that Reviewer and to the frozen input. It never opens a DSN or a
resource file, never builds a store, Profile, Variant or Adapter, and has no
executor, import locator or environment-variable selection. Runtime is imported
only when a review actually runs, so installation checks and --check-only work
without Runtime, credentials or a Provider.

Run as a command, it is also the common entry for an input already prepared
under a Reviewer's registered schema:

    python runtime_review.py --input INPUT.json --output NEW_RESULT.json --root ROOT [Runtime arguments]
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Callable, Mapping


GOVERNANCE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
SKILL_MANIFEST_PATH = GOVERNANCE_ROOT / "governance_skill_manifest.json"
VALIDATION_ROOT = Path(__file__).resolve().parent
_INPUT_SCHEMA = re.compile(r"/runtime_modules/([a-z][a-z0-9_]*)/schemas/input\.schema\.json$")
# Reviewer ID -> (validator file under this directory, function, whether it needs the execution record).
_VALIDATORS = {
    "design_contract_reviewer": ("artifact_contracts/design_review_output.py", "validate_design_contract_review_output", False),
    "skill_candidate_reviewer": ("artifact_contracts/skill_review_output.py", "validate_skill_review_output", False),
    "experiment_reviewer": ("experiment_design/review.py", "validate_output", False),
    "engineering_change_reviewer": ("software_delivery/engineering_review_output.py", "validate_engineering_review_output", True),
    "system_change_plan_reviewer": ("system_change/model_output_validation.py", "validate_system_change_review_output", False),
    "reviewer_reviewer": ("review_contract/reviewer_output_validation.py", "validate_reviewer_prompt_review_output", False),
    "project_documentation_reviewer": ("project_documentation/project_documentation_review_output.py",
                                       "validate_project_documentation_review_output", False),
}
# CLI destination -> public run_local_workflow_test field.
_RUNTIME_FIELDS = {
    "root": "root", "workflow": "workflow_id", "version": "version",
    "workflow_ref": "workflow_release_ref", "workflow_sha256": "workflow_release_sha256",
    "release_database_url_env": "release_database_url_env", "release_schema": "release_schema",
    "resources": "resources_path", "transport": "transport_kind", "model": "model_id",
    "effort": "reasoning_profile", "run_timeout_seconds": "run_timeout_seconds", "cli_path": "cli_path",
}
_POSTGRES_FIELDS = ("workflow_release_ref", "workflow_release_sha256", "release_database_url_env", "release_schema")


def reviewer_input_versions(manifest_path: Path = SKILL_MANIFEST_PATH) -> dict[str, str]:
    """Map each shipped Reviewer ID to the schema_version const of its registered input schema.

    Reviewer identity comes from the input schemas the portable Skill manifest
    ships, so an input that carries no module_id field (project documentation)
    is still identified by its registered schema version.
    """
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    versions = {}
    for skill in manifest["portable_governance_skills"]:
        for entry in skill["package_files"]:
            match = _INPUT_SCHEMA.search(entry["source"])
            if match:
                schema = json.loads((PROJECT_ROOT / entry["source"]).read_text(encoding="utf-8"))
                versions[match.group(1)] = schema["properties"]["schema_version"]["const"]
    if len(set(versions.values())) != len(versions):
        raise ValueError("shipped Reviewer input schemas repeat a schema_version")
    return versions


def reviewer_module_ids(manifest_path: Path = SKILL_MANIFEST_PATH) -> frozenset[str]:
    """Reviewer IDs whose registered input schema the portable Skill manifest ships."""
    return frozenset(reviewer_input_versions(manifest_path))


def reviewer_for_input(semantic_input: Mapping[str, object]) -> str:
    """Identify the Reviewer from the input's schema_version; a module_id field must agree."""
    if not isinstance(semantic_input, Mapping):
        raise ValueError("review input must be a JSON object")
    by_version = {version: module_id for module_id, version in reviewer_input_versions().items()}
    module_id = by_version.get(semantic_input.get("schema_version"))
    if module_id is None:
        raise ValueError(f"input schema_version is not a shipped Reviewer input: {semantic_input.get('schema_version')!r}")
    if "module_id" in semantic_input and semantic_input["module_id"] != module_id:
        raise ValueError(f"input module_id {semantic_input['module_id']!r} disagrees with its schema_version")
    return module_id


def add_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the shared Test Run arguments with the same spelling in every review CLI."""
    group = parser.add_argument_group(
        "Agent Runtime Test Run",
        "Values pass unchanged to agent_runtime.run_local_workflow_test. --root is required to run a review. "
        "Select a local definition with --workflow/--version (default workflow: the Reviewer ID) or an exact "
        "PostgreSQL definition with --workflow-ref, --workflow-sha256, --release-database-url-env and "
        "--release-schema. Omitted --transport/--model/--effort come from the root's execution parameter files, "
        "then the Runtime default.")
    group.add_argument("--root", type=Path, help="Runtime root: setup, definitions and execution parameter files")
    group.add_argument("--workflow", help="local registered Workflow ID; defaults to the Reviewer ID")
    group.add_argument("--version", help="local exact version; omit for the latest registered version")
    group.add_argument("--workflow-ref", help="PostgreSQL exact Workflow release_ref")
    group.add_argument("--workflow-sha256", help="PostgreSQL exact Workflow release_sha256")
    group.add_argument("--release-database-url-env", help="name of the environment variable holding the DSN; Runtime reads it")
    group.add_argument("--release-schema", help="existing PostgreSQL release schema")
    group.add_argument("--resources", type=Path, help="resource JSON file; Runtime parses it")
    group.add_argument("--transport", help="this call's transport, for example claude_cli")
    group.add_argument("--model", help="this call's model ID")
    group.add_argument("--effort", help="this call's reasoning effort")
    group.add_argument("--run-timeout-seconds", type=int, help="this synchronous run budget in seconds; Runtime resolves defaults and parent limits")
    group.add_argument("--cli-path", type=Path, help="installed Provider CLI executable")


def runtime_kwargs(args: argparse.Namespace) -> dict:
    """Map parsed shared arguments to run_local_workflow_test fields; Runtime validates them."""
    values = {field: getattr(args, destination) for destination, field in _RUNTIME_FIELDS.items()}
    if values["root"] is None:
        raise ValueError("running a review requires --root")
    return {field: value for field, value in values.items() if value is not None or field == "root"}


def _canonical_sha256(value) -> str:
    body = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def review_run_fields(semantic_input: Mapping[str, object],
                      runtime_kwargs: Mapping[str, object]) -> tuple[str, dict]:
    """Return the Reviewer ID and the Test Run fields for one review.

    runtime_kwargs come only from trusted CLI or host arguments, never from the
    review input. The Reviewer ID comes from the input's shipped schema version
    (and its module_id field, when the schema has one); input_payload and
    expected_module_id are fixed by the review, so no general argument can
    select another Reviewer. A local definition defaults to the Workflow named
    after the Reviewer; a PostgreSQL locator is passed unchanged.
    """
    module_id = reviewer_for_input(semantic_input)
    fields = dict(runtime_kwargs)
    for reserved in ("input_payload", "expected_module_id"):
        if reserved in fields:
            raise ValueError(f"{reserved} is fixed by the review object, not by Runtime arguments")
    if fields.get("workflow_id") is None and not any(fields.get(name) is not None for name in _POSTGRES_FIELDS):
        fields["workflow_id"] = module_id
    return module_id, fields


def bind_review_record(record: Mapping[str, object], *, module_id: str,
                       semantic_input: Mapping[str, object]) -> dict:
    """Accept a Test Run record only from this Reviewer and for exactly this input.

    The record must name the Reviewer's Module release and bind the canonical
    SHA-256 of the input as its task_input. The returned copy carries module_id,
    semantic_input and, when the input has one, review_purpose for the owning
    validator.
    """
    record = dict(record)
    release = record.get("module_release_ref")
    if not isinstance(release, str) or not release.startswith(f"runtime-module:{module_id}@"):
        raise ValueError(f"Runtime record does not come from {module_id}: {release!r}")
    bound = [row.get("input_sha256") for row in record.get("input_bindings") or () if row.get("logical_name") == "task_input"]
    if bound != [_canonical_sha256(semantic_input)]:
        raise ValueError("Runtime record does not bind the frozen review input")
    record["module_id"] = module_id
    record["semantic_input"] = copy.deepcopy(dict(semantic_input))
    if "review_purpose" in semantic_input:
        record["review_purpose"] = semantic_input["review_purpose"]
    return record


def run_review_test(semantic_input: Mapping[str, object], *, runtime_kwargs: Mapping[str, object]) -> dict:
    """Run the Reviewer that the input's registered schema identifies through Runtime Test Run."""
    module_id, fields = review_run_fields(semantic_input, runtime_kwargs)
    frozen = copy.deepcopy(dict(semantic_input))
    from agent_runtime import run_local_workflow_test
    record = run_local_workflow_test(input_payload=copy.deepcopy(frozen), expected_module_id=module_id, **fields)
    return bind_review_record(record, module_id=module_id, semantic_input=frozen)


def _validator_module(relative: str):
    name = "portable_review_validator_" + relative.replace("/", "_").removesuffix(".py")
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, VALIDATION_ROOT / relative)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _validator(module_id: str) -> tuple[Callable, bool]:
    relative, function, needs_record = _VALIDATORS[module_id]
    return getattr(_validator_module(relative), function), needs_record


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a shipped Reviewer on an input already prepared under its registered schema, "
                    "through Agent Runtime Test Run, and validate the result with its owning validator.")
    parser.add_argument("--input", type=Path, required=True, help="JSON input under the Reviewer's registered schema")
    parser.add_argument("--output", type=Path, required=True, help="new result file; never overwritten")
    add_runtime_arguments(parser)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink() or not args.output.parent.is_dir():
        parser.error("output must be a new file in an existing directory")
    if args.output.resolve() == args.input.resolve():
        parser.error("output must not replace the input")
    try:
        fields = runtime_kwargs(args)
    except ValueError as exc:
        parser.error(str(exc))
    try:
        semantic_input = json.loads(args.input.read_text(encoding="utf-8"))
        module_id = reviewer_for_input(semantic_input)
        if module_id not in _VALIDATORS:
            raise ValueError(f"no owning validator is declared for Reviewer {module_id}")
        validate, needs_record = _validator(module_id)
        record = run_review_test(semantic_input, runtime_kwargs=fields)
        validation = {"status": "not_run", "message": "Runtime execution did not complete"}
        if record.get("status") == "completed":
            try:
                if needs_record:
                    validate(record.get("output"), review_input=record["semantic_input"], execution_record=record)
                else:
                    validate(record.get("output"), record["semantic_input"])
                validation = {"status": "passed", "message": None}
            except Exception as exc:  # validator families raise different error types
                validation = {"status": "failed", "message": str(exc), "error_type": type(exc).__name__}
        record["semantic_validation"] = validation
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(json.dumps({"error": str(exc), "error_type": type(exc).__name__}, ensure_ascii=False), file=sys.stderr)
        return 2
    valid = validation["status"] == "passed"
    verdict = record["output"]["verdict"] if valid else None
    print(json.dumps({"execution": record.get("status"), "output_validation": validation, "verdict": verdict,
                      "output": str(args.output)}, ensure_ascii=False))
    return 0 if valid and verdict == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
