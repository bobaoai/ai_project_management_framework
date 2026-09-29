from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import ValidationError
from jsonschema.validators import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE_PATH = REPO_ROOT / "09_soul/governance/t0/validation/skill_release.py"
SPEC = importlib.util.spec_from_file_location("governance_skill_release", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
release = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = release
SPEC.loader.exec_module(release)

UNIVERSAL_RESOURCE_ID = "t0:review_contract_universal_review_style"
CHECKLIST_RESOURCE_ID = "t0:example_design_review_checklist"
RESOURCE_IDS = (UNIVERSAL_RESOURCE_ID, CHECKLIST_RESOURCE_ID)


def _resource_block(resource_id: str, body: str) -> str:
    return (
        f"<!-- embedded-resource:{resource_id}:start -->\n"
        f"{body}\n"
        f"<!-- embedded-resource:{resource_id}:end -->\n"
    )


def _prompt() -> bytes:
    return (
        "# Example Reviewer\n\n"
        "## 0. review_contract_universal\n\n"
        + _resource_block(UNIVERSAL_RESOURCE_ID, "Apply the universal rules.")
        + "\n## 1. Review Task\n\nReview one exact subject.\n\n"
        "## 2. Inputs, Decision, and Output\n\n"
        "Use the frozen subject and return the registered result.\n\n"
        "## 3. Boundaries and Failure Routing\n\n"
        "Return wrong-owner issues without expanding the subject.\n\n"
        "## 4. Subject Review Checklist\n\n"
        + _resource_block(CHECKLIST_RESOURCE_ID, "Check the declared result.")
    ).encode("utf-8")


def test_reviewer_prompt_accepts_exact_five_section_layout() -> None:
    release.validate_reviewer_prompt_artifact(
        _prompt(),
        embedded_resource_ids=RESOURCE_IDS,
    )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda payload: payload.replace(b"## 1. Review Task", b"", 1),
        lambda payload: payload.replace(
            b"## 3. Boundaries and Failure Routing",
            b"## 4. Boundaries and Failure Routing",
            1,
        ),
        lambda payload: payload.replace(
            b"## 4. Subject Review Checklist",
            b"## 5. Extra\n\nExtra.\n\n## 4. Subject Review Checklist",
            1,
        ),
        lambda payload: payload.replace(
            b"## 2. Inputs, Decision, and Output",
            b"## 2. Output",
            1,
        ),
    ],
)
def test_reviewer_prompt_rejects_incomplete_or_extra_layout(mutation) -> None:
    with pytest.raises(release.GovernanceSkillReleaseError) as caught:
        release.validate_reviewer_prompt_artifact(
            mutation(_prompt()),
            embedded_resource_ids=RESOURCE_IDS,
        )

    assert caught.value.code == "GOVERNANCE_SKILL_SOURCE_CLOSURE_INVALID"


def test_reviewer_prompt_rejects_universal_resource_outside_section_zero() -> None:
    payload = _prompt()
    universal = _resource_block(
        UNIVERSAL_RESOURCE_ID,
        "Apply the universal rules.",
    ).encode()
    payload = payload.replace(universal, b"Universal rules are declared below.\n", 1)
    payload = payload.replace(
        b"Review one exact subject.\n",
        b"Review one exact subject.\n" + universal,
        1,
    )

    with pytest.raises(release.GovernanceSkillReleaseError) as caught:
        release.validate_reviewer_prompt_artifact(
            payload,
            embedded_resource_ids=RESOURCE_IDS,
        )

    assert caught.value.code == "GOVERNANCE_SKILL_SOURCE_CLOSURE_INVALID"
    assert "wrong section" in caught.value.detail


def test_reviewer_prompt_rejects_checklist_outside_section_four() -> None:
    payload = _prompt()
    checklist = _resource_block(
        CHECKLIST_RESOURCE_ID,
        "Check the declared result.",
    ).encode()
    payload = payload.replace(checklist, b"Checklist is declared above.\n", 1)
    payload = payload.replace(
        b"Use the frozen subject and return the registered result.\n",
        b"Use the frozen subject and return the registered result.\n" + checklist,
        1,
    )

    with pytest.raises(release.GovernanceSkillReleaseError) as caught:
        release.validate_reviewer_prompt_artifact(
            payload,
            embedded_resource_ids=RESOURCE_IDS,
        )

    assert caught.value.code == "GOVERNANCE_SKILL_SOURCE_CLOSURE_INVALID"
    assert "wrong section" in caught.value.detail


@pytest.mark.parametrize(
    "resource_ids",
    [
        (UNIVERSAL_RESOURCE_ID,),
        (CHECKLIST_RESOURCE_ID,),
        (UNIVERSAL_RESOURCE_ID, CHECKLIST_RESOURCE_ID, "t0:another_checklist"),
    ],
)
def test_reviewer_prompt_requires_one_universal_and_one_checklist(
    resource_ids: tuple[str, ...],
) -> None:
    with pytest.raises(release.GovernanceSkillReleaseError) as caught:
        release.validate_reviewer_prompt_artifact(
            _prompt(),
            embedded_resource_ids=resource_ids,
        )

    assert caught.value.code == "GOVERNANCE_SKILL_SOURCE_CLOSURE_INVALID"


def test_reviewer_prompt_rejects_retired_universal_resource_id() -> None:
    with pytest.raises(release.GovernanceSkillReleaseError) as caught:
        release.validate_reviewer_prompt_artifact(
            _prompt(),
            embedded_resource_ids=(
                UNIVERSAL_RESOURCE_ID,
                "t0:contract_audit_universal_review_style",
            ),
        )

    assert caught.value.code == "GOVERNANCE_SKILL_EMBEDDED_RESOURCE_INVALID"


def test_reviewer_reviewer_package_contract_is_closed() -> None:
    module_root = (
        REPO_ROOT
        / "09_soul/governance/skills/the-review-authoring/runtime_modules/"
        "reviewer_reviewer"
    )
    registration = json.loads(
        (module_root / "module_registration.json").read_text(encoding="utf-8")
    )
    input_schema = json.loads(
        (module_root / "schemas/input.schema.json").read_text(encoding="utf-8")
    )
    output_schema = json.loads(
        (module_root / "schemas/output.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(input_schema)
    Draft202012Validator.check_schema(output_schema)
    assert registration["input_schema_ref"] == input_schema["$id"]
    assert registration["output_schema_ref"] == output_schema["$id"]

    check_ids = [
        item["const"]
        for item in input_schema["properties"]["required_check_ids"][
            "prefixItems"
        ]
    ]
    assert check_ids == [
        "purpose_subject_and_reader_gain",
        "inputs_decision_and_output",
        "boundaries_and_failure_routing",
        "instruction_ownership_and_nonduplication",
        "cold_start_executability_and_schema_fixture_consistency",
    ]
    output_ids = [*check_ids, "prose_and_meaning_preservation"]
    assert output_schema["$defs"]["check_result"]["properties"]["check_id"]["enum"] == output_ids
    assert output_schema["properties"]["check_results"]["items"] == {"$ref": "#/$defs/check_result"}
    passed_output = {
        "verdict": "passed",
        "check_results": [
            {"check_id": check_id, "disposition": "passed", "assessment": "Candidate evidence.", "finding_ids": []}
            for check_id in output_ids
        ],
        "findings": [], "safe_next_step": "Use the reviewed prompt.",
    }
    validator = Draft202012Validator(output_schema)
    validator.validate(passed_output)
    with pytest.raises(ValidationError):
        validator.validate(passed_output | {"reviewer_prompt_judgment": {}})
    with pytest.raises(ValidationError):
        validator.validate(passed_output | {"check_results": passed_output["check_results"][:-1]})

    fixture_schema = deepcopy(input_schema["properties"]["fixtures"])
    fixture_schema["$defs"] = {"fixture": input_schema["$defs"]["fixture"]}
    valid_fixtures = [
        {
            "fixture_ref": f"fixture:{case_kind}",
            "sha256": "0" * 64,
            "case_kind": case_kind,
            "body": "{}",
        }
        for case_kind in ("positive", "negative", "schema_drift")
    ]
    Draft202012Validator(fixture_schema).validate(valid_fixtures)
    with pytest.raises(ValidationError):
        Draft202012Validator(fixture_schema).validate(
            [valid_fixtures[0], valid_fixtures[0], valid_fixtures[2]]
        )


def test_reviewer_reviewer_prompt_matches_registered_instruction_sources() -> None:
    manifest = release.load_governance_skill_manifest(REPO_ROOT)
    resources = {item.resource_id: item for item in manifest.instruction_resources}
    resource_ids = (
        "t0:review_contract_universal_review_style",
        "t0:reviewer_prompt_review_checklist",
    )
    selected = {
        resource_id: release._select_instruction_resource_bytes(
            resources[resource_id],
            (REPO_ROOT / resources[resource_id].source).read_bytes(),
            project_root=REPO_ROOT,
            artifact_contracts_by_source=release._known_t0_artifact_contracts(
                REPO_ROOT
            ),
        )
        for resource_id in resource_ids
    }
    prompt = (
        REPO_ROOT
        / "09_soul/governance/skills/the-review-authoring/runtime_modules/"
        "reviewer_reviewer/prompt.md"
    ).read_bytes()

    assert prompt == release.compose_governance_skill_package_file(
        prompt,
        resource_ids,
        selected,
    )
    release.validate_reviewer_prompt_artifact(
        prompt,
        embedded_resource_ids=resource_ids,
    )
