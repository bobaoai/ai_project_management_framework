from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE_PATH = (
    REPO_ROOT
    / "09_soul/governance/t0/validation/artifact_contracts/skill_artifact_contract.py"
)
SPEC = importlib.util.spec_from_file_location(
    "skill_artifact_contract", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
contract = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = contract
SPEC.loader.exec_module(contract)


def _candidate(
    *,
    skill_class: str = "primary_agent_development",
    authoring_section: bool = False,
) -> bytes:
    metadata = [f"  skill_class: {skill_class}"]
    if skill_class == "primary_agent_development":
        metadata.extend(
            (
                "  primary_agent_entry_role: authoring",
                "  primary_agent_entry_subject: system_change_plan_step",
                "  first_authority_ref: designDoc/the_example.md",
            )
        )
    body = (
        "---\n"
        "name: example-skill\n"
        "description: Complete one stable example task.\n"
        "metadata:\n"
        + "\n".join(metadata)
        + "\n---\n\n"
        "# Example Skill\n\n"
    )
    if authoring_section:
        body += (
            "## 0. AI-facing Authoring Rules\n\n"
            "Use the registered common authoring instruction.\n\n"
        )
    return (
        body
        + "## 1. Task\n\nComplete the stable task.\n\n"
        "## 2. Reader Gain\n\nThe Agent can decide whether the task is complete.\n\n"
        "## 3. Entry and Exit\n\nEnter with the required request and return blockers to the owner.\n\n"
        "## 4. Execution Contract\n\nThe contract fixes inputs and completion.\n\n"
        "### 4.1 Inputs and Authority\n\nUse the reviewed request and owning Design.\n\n"
        "### 4.2 Output and Completion\n\nReturn one complete candidate.\n\n"
        "## 5. Boundaries\n\nDo not claim Runtime or release authority.\n\n"
        "## 6. Method\n\nChoose the shortest path that satisfies the result.\n"
    ).encode("utf-8")


@pytest.mark.parametrize(
    "skill_class",
    [
        "primary_agent_development",
        "product_agentic",
        "product_hybrid",
        "projection_only",
    ],
)
def test_each_skill_class_uses_one_code_owned_artifact_contract(
    skill_class: str,
) -> None:
    payload = _candidate(skill_class=skill_class)

    result = contract.validate_artifact(payload)

    assert result.subject_sha256 == hashlib.sha256(payload).hexdigest()
    assert result.skill_id == "example-skill"
    assert result.skill_class == skill_class
    assert "skill_required_section_schema" in result.validator_ids


def test_primary_agent_skill_requires_entry_metadata() -> None:
    payload = _candidate().replace(
        b"  first_authority_ref: designDoc/the_example.md\n", b""
    )

    with pytest.raises(
        contract.SkillArtifactContractError,
        match="metadata is incomplete",
    ) as caught:
        contract.validate_artifact(payload)

    assert caught.value.code == "GOVERNANCE_SKILL_SOURCE_CLOSURE_INVALID"


def test_required_skill_section_rename_is_rejected() -> None:
    payload = _candidate().replace(b"## 2. Reader Gain", b"## 2. Benefits", 1)

    with pytest.raises(
        contract.SkillArtifactContractError,
        match="required sections",
    ):
        contract.validate_artifact(payload)


def test_skill_section_number_gap_is_rejected() -> None:
    payload = _candidate().replace(b"## 5. Boundaries", b"## 7. Boundaries", 1)

    with pytest.raises(
        contract.SkillArtifactContractError,
        match="numbering must be continuous",
    ):
        contract.validate_artifact(payload)


def test_declared_authoring_common_resource_requires_and_accepts_section_zero() -> None:
    payload = _candidate(authoring_section=True)

    result = contract.validate_artifact(
        payload,
        embedded_resource_ids=("soul:bestpractice_ai_facing_writing",),
    )

    assert result.headings[0] == "AI-facing Authoring Rules"
    assert result.headings[1:] == (
        "Task",
        "Reader Gain",
        "Entry and Exit",
        "Execution Contract",
        "Boundaries",
        "Method",
    )


def test_undeclared_authoring_section_zero_is_rejected() -> None:
    with pytest.raises(
        contract.SkillArtifactContractError,
        match="continuous from one",
    ):
        contract.validate_artifact(_candidate(authoring_section=True))


def test_declared_authoring_common_resource_without_section_zero_is_rejected() -> None:
    with pytest.raises(
        contract.SkillArtifactContractError,
        match="continuous from zero",
    ):
        contract.validate_artifact(
            _candidate(),
            embedded_resource_ids=("soul:bestpractice_ai_facing_writing",),
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda payload: payload.replace(
            b"## 0. AI-facing Authoring Rules",
            b"## 0. Shared Writing Rules",
            1,
        ),
        lambda payload: payload.replace(
            b"Use the registered common authoring instruction.",
            b"",
            1,
        ),
        lambda payload: payload.replace(
            b"## 1. Task",
            b"## 0. AI-facing Authoring Rules\n\nDuplicate.\n\n## 1. Task",
            1,
        ),
        lambda payload: payload.replace(
            b"## 0. AI-facing Authoring Rules\n\n"
            b"Use the registered common authoring instruction.\n\n",
            b"",
            1,
        ).replace(
            b"## 2. Reader Gain",
            b"## 2. Reader Gain\n\n"
            b"## 0. AI-facing Authoring Rules\n\nLate.\n\n",
            1,
        ),
    ],
)
def test_declared_authoring_section_zero_must_be_exact_and_first(mutation) -> None:
    with pytest.raises(contract.SkillArtifactContractError):
        contract.validate_artifact(
            mutation(_candidate(authoring_section=True)),
            embedded_resource_ids=("soul:bestpractice_ai_facing_writing",),
        )


def test_execution_contract_subsections_are_required() -> None:
    payload = _candidate().replace(
        b"### 4.2 Output and Completion", b"### 4.2 Completion", 1
    )

    with pytest.raises(
        contract.SkillArtifactContractError,
        match="must occur exactly once",
    ):
        contract.validate_artifact(payload)


def test_skill_reviewer_prompt_contains_exact_projected_checklist() -> None:
    prompt = (
        REPO_ROOT
        / "09_soul/governance/skills/the-skill-authoring/runtime_modules/"
        "skill_candidate_reviewer/prompt.md"
    ).read_bytes()
    resource_id = "t0:skill_candidate_review_checklist"
    start = f"<!-- embedded-resource:{resource_id}:start -->\n".encode()
    end = f"<!-- embedded-resource:{resource_id}:end -->".encode()

    projected = prompt.split(start, 1)[1].split(end, 1)[0]

    assert projected == contract.render_reviewer_checklist()


def test_skill_authoring_keeps_method_without_a_reviewer_checklist_copy() -> None:
    authoring = (
        REPO_ROOT / "09_soul/governance/skills/the-skill-authoring/SKILL.md"
    ).read_text(encoding="utf-8")

    assert "t0:skill_candidate_review_checklist" not in authoring
    assert "identity_discovery_class_and_source" not in authoring
