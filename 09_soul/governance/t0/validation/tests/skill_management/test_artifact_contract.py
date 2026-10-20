from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest


pytestmark = pytest.mark.deterministic


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
    name: str = "example-skill",
    skill_class: str = "primary_agent_development",
    authoring_section: bool = False,
    author_self_check: bool = False,
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
        f"name: {name}\n"
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
    candidate = (
        body
        + "## 1. Task Summary\n\nComplete the stable task.\n\n"
        "## 2. Intended Outcomes\n\nDeliver one complete candidate for the recipient to review against its owning Design.\n\n"
        "## 3. Boundaries\n\nDo not claim Runtime or release authority.\n\n"
        "## 4. Inputs and Completion\n\nThe contract fixes inputs and completion.\n\n"
        "### 4.1 Inputs\n\nUse the reviewed request and owning Design.\n\n"
        "### 4.2 Output\n\nReturn one complete candidate or the actual missing inputs to their owner.\n\n"
        "### 4.3 Completion Contract\n\nThe result meets the agreed criteria.\n\n"
        "## 5. Method\n\nChoose the shortest path that satisfies the result.\n"
    )
    if author_self_check:
        candidate += (
            "\n### 5.1 Author Self-Check\n\n"
            "Use the registered Author Self-Check and canonical checklist.\n"
        )
    return candidate.encode("utf-8")


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
    payload = _candidate().replace(b"## 2. Intended Outcomes", b"## 2. Benefits", 1)

    with pytest.raises(
        contract.SkillArtifactContractError,
        match="required sections",
    ):
        contract.validate_artifact(payload)


def test_skill_section_number_gap_is_rejected() -> None:
    payload = _candidate().replace(b"## 3. Boundaries", b"## 7. Boundaries", 1)

    with pytest.raises(
        contract.SkillArtifactContractError,
        match="numbering must be continuous",
    ):
        contract.validate_artifact(payload)


def test_continuous_extension_sections_are_allowed() -> None:
    payload = _candidate() + b"\n## 6. Examples\n\nOne useful example.\n\n## 7. Resources\n\nAvailable tools.\n"

    result = contract.validate_artifact(payload)

    assert result.headings[-2:] == ("Examples", "Resources")
    assert result.subject_sha256 == hashlib.sha256(payload).hexdigest()


@pytest.mark.parametrize("fence", [b"```markdown", b"~~~~markdown", b"   ```markdown"])
def test_fenced_headings_are_examples_not_skill_sections(fence: bytes) -> None:
    closer = fence.replace(b"markdown", b"")
    payload = _candidate() + b"\n" + fence + b"\n## 1. Task Summary\n### 9.8 Inputs and Authority\nExample.\n" + closer + b"\n"

    result = contract.validate_artifact(payload)

    assert len(result.headings) == 5
    assert result.subject_sha256 == hashlib.sha256(payload).hexdigest()


def test_sections_only_inside_a_fence_do_not_form_a_skill() -> None:
    payload = _candidate().replace(b"## 1. Task Summary", b"```markdown\n## 1. Task Summary", 1) + b"\n```\n"

    with pytest.raises(contract.SkillArtifactContractError, match="no numbered"):
        contract.validate_artifact(payload)


@pytest.mark.parametrize("replacement", [b"### 4.3 Output and Completion", b"### 3.2 Output and Completion"])
def test_required_subsection_number_is_not_inferred(replacement: bytes) -> None:
    payload = _candidate().replace(b"### 4.2 Output", replacement)

    with pytest.raises(contract.SkillArtifactContractError, match="exactly once"):
        contract.validate_artifact(payload)


def test_execution_contract_subsections_must_have_the_correct_parent() -> None:
    payload = _candidate().replace(
        b"### 4.1 Inputs", b"## 5. Method\n\n### 4.1 Inputs"
    ).replace(b"## 5. Method\n\nChoose the shortest path that satisfies the result.", b"Choose the shortest path that satisfies the result.")

    with pytest.raises(contract.SkillArtifactContractError, match="match its parent"):
        contract.validate_artifact(payload)


def test_duplicate_optional_subsection_number_is_rejected() -> None:
    payload = _candidate() + b"\n### 5.1 Read\n\nRead inputs.\n\n### 5.1 Write\n\nWrite output.\n"

    with pytest.raises(contract.SkillArtifactContractError, match="continuous"):
        contract.validate_artifact(payload)


def test_new_skill_can_use_an_explicit_checklist_binding() -> None:
    payload = _candidate(name="example-authoring", author_self_check=True)
    resource = "skill:example_review_checklist"

    result = contract.validate_artifact(
        payload,
        embedded_resource_ids=("t0:skill_author_self_check", resource),
        checklist_resource_by_skill_id={"example-authoring": resource},
    )

    assert result.skill_id == "example-authoring"


def test_new_skill_cannot_guess_a_checklist_from_an_embedded_resource() -> None:
    with pytest.raises(contract.SkillArtifactContractError, match="does not match"):
        contract.validate_artifact(
            _candidate(name="example-authoring", author_self_check=True),
            embedded_resource_ids=("t0:skill_author_self_check", "t0:skill_candidate_review_checklist"),
        )


def test_invocation_cannot_rebind_an_existing_skill_checklist() -> None:
    with pytest.raises(contract.SkillArtifactContractError, match="cannot replace"):
        contract.validate_artifact(
            _candidate(name="the-skill-authoring", author_self_check=True),
            embedded_resource_ids=("t0:skill_author_self_check", "t0:design_contract_review_checklist"),
            checklist_resource_by_skill_id={"the-skill-authoring": "t0:design_contract_review_checklist"},
        )


def test_code_owned_checklist_map_can_add_skills_without_a_fixed_count(tmp_path: Path) -> None:
    import json

    value = contract.load_contract()
    value["author_self_check"]["checklist_resource_by_skill_id"]["another-authoring"] = "t0:skill_candidate_review_checklist"
    path = tmp_path / "skill_contract.json"
    path.write_text(json.dumps(value), encoding="utf-8")

    assert "another-authoring" in contract.load_contract(path)["author_self_check"]["checklist_resource_by_skill_id"]


def test_declared_authoring_common_resource_requires_and_accepts_section_zero() -> None:
    payload = _candidate(authoring_section=True)

    result = contract.validate_artifact(
        payload,
        embedded_resource_ids=("soul:bestpractice_ai_facing_writing",),
    )

    assert result.headings[0] == "AI-facing Authoring Rules"
    assert result.headings[1:] == (
        "Task Summary",
        "Intended Outcomes",
        "Boundaries",
        "Inputs and Completion",
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
            b"## 1. Task Summary",
            b"## 0. AI-facing Authoring Rules\n\nDuplicate.\n\n## 1. Task Summary",
            1,
        ),
        lambda payload: payload.replace(
            b"## 0. AI-facing Authoring Rules\n\n"
            b"Use the registered common authoring instruction.\n\n",
            b"",
            1,
        ).replace(
            b"## 2. Intended Outcomes",
            b"## 2. Intended Outcomes\n\n"
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
        b"### 4.2 Output", b"### 4.2 Completion", 1
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


def test_skill_authoring_contains_exact_projected_author_self_check_resources() -> None:
    authoring = (
        REPO_ROOT / "09_soul/governance/skills/the-skill-authoring/SKILL.md"
    ).read_bytes()

    def projected(resource_id: str) -> bytes:
        start = f"<!-- embedded-resource:{resource_id}:start -->\n".encode()
        end = f"<!-- embedded-resource:{resource_id}:end -->".encode()
        return authoring.split(start, 1)[1].split(end, 1)[0]

    assert projected("t0:skill_author_self_check") == (
        contract.render_author_self_check_instruction()
    )
    assert projected("t0:skill_candidate_review_checklist") == (
        contract.render_reviewer_checklist()
    )


def test_declared_author_self_check_requires_one_method_section_and_checklist() -> None:
    payload = _candidate(name="the-skill-authoring", author_self_check=True)

    result = contract.validate_artifact(
        payload,
        embedded_resource_ids=(
            "t0:skill_author_self_check",
            "t0:skill_candidate_review_checklist",
        ),
    )

    assert "skill_author_self_check_contract" in result.validator_ids


@pytest.mark.parametrize(
    ("payload", "resource_ids", "message"),
    [
        (
            _candidate(name="the-skill-authoring"),
            (
                "t0:skill_author_self_check",
                "t0:skill_candidate_review_checklist",
            ),
            "must occur exactly once",
        ),
        (
            _candidate(name="the-skill-authoring", author_self_check=True),
            ("t0:skill_author_self_check",),
            "does not match the registered Skill binding",
        ),
        (
            _candidate(name="the-skill-authoring", author_self_check=True),
            ("t0:skill_candidate_review_checklist",),
            "declarations must be complete",
        ),
        (
            _candidate(name="the-skill-authoring", author_self_check=True),
            (
                "t0:skill_author_self_check",
                "t0:skill_candidate_review_checklist",
                "t0:design_contract_review_checklist",
            ),
            "does not match the registered Skill binding",
        ),
    ],
)
def test_author_self_check_contract_rejects_incomplete_declarations(
    payload: bytes,
    resource_ids: tuple[str, ...],
    message: str,
) -> None:
    with pytest.raises(contract.SkillArtifactContractError, match=message):
        contract.validate_artifact(payload, embedded_resource_ids=resource_ids)


@pytest.mark.parametrize(
    ("skill_id", "wrong_checklist"),
    [
        ("the-system-change", "t0:design_contract_review_checklist"),
        ("the-design-authoring", "t0:skill_candidate_review_checklist"),
        ("the-skill-authoring", "t0:reviewer_prompt_review_checklist"),
        ("the-review-authoring", "t0:system_change_plan_review_checklist"),
    ],
)
def test_author_self_check_rejects_wrong_allowlisted_checklist(
    skill_id: str,
    wrong_checklist: str,
) -> None:
    with pytest.raises(
        contract.SkillArtifactContractError,
        match="does not match the registered Skill binding",
    ):
        contract.validate_artifact(
            _candidate(name=skill_id, author_self_check=True),
            embedded_resource_ids=(
                "t0:skill_author_self_check",
                wrong_checklist,
            ),
        )


def test_author_self_check_must_be_structurally_inside_method() -> None:
    payload = _candidate(
        name="the-skill-authoring",
        author_self_check=True,
    )
    self_check = (
        b"\n### 5.1 Author Self-Check\n\n"
        b"Use the registered Author Self-Check and canonical checklist.\n"
    )
    misplaced = payload.replace(self_check, b"").replace(
        b"## 5. Method",
        self_check + b"\n## 5. Method",
        1,
    )

    with pytest.raises(
        contract.SkillArtifactContractError,
        match="must be inside the Method section",
    ):
        contract.validate_artifact(
            misplaced,
            embedded_resource_ids=(
                "t0:skill_author_self_check",
                "t0:skill_candidate_review_checklist",
            ),
        )


def _self_check_rows(*check_ids: str) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "check_id": check_id,
            "exact_evidence": f"candidate evidence for {check_id}",
            "local_result": "locally closed",
            "unresolved_finding": None,
        }
        for check_id in check_ids
    )


def test_invocation_local_author_self_check_accepts_exact_closed_rows() -> None:
    candidate = b"exact candidate\n"
    check_ids = ("check_a", "check_b")

    result = contract.validate_author_self_check_submission(
        candidate,
        declared_candidate_sha256=hashlib.sha256(candidate).hexdigest(),
        required_check_ids=check_ids,
        rows=_self_check_rows(*check_ids),
    )

    assert result.candidate_sha256 == hashlib.sha256(candidate).hexdigest()
    assert result.required_check_ids == check_ids
    assert result.row_count == 2


@pytest.mark.parametrize(
    ("declared_sha256", "check_ids", "rows", "error_code"),
    [
        (
            "0" * 64,
            ("check_a",),
            _self_check_rows("check_a"),
            contract.AUTHOR_SELF_CHECK_CANDIDATE_MISMATCH,
        ),
        (
            hashlib.sha256(b"exact candidate\n").hexdigest(),
            ("check_a", "check_b"),
            _self_check_rows("check_b", "check_a"),
            contract.AUTHOR_SELF_CHECK_COVERAGE_INVALID,
        ),
        (
            hashlib.sha256(b"exact candidate\n").hexdigest(),
            ("check_a",),
            (
                {
                    "check_id": "check_a",
                    "exact_evidence": "",
                    "local_result": "locally closed",
                    "unresolved_finding": None,
                },
            ),
            contract.AUTHOR_SELF_CHECK_EVIDENCE_MISSING,
        ),
        (
            hashlib.sha256(b"exact candidate\n").hexdigest(),
            ("check_a",),
            (
                {
                    "check_id": "check_a",
                    "exact_evidence": "candidate evidence",
                    "local_result": "finding remains",
                    "unresolved_finding": "fix the candidate",
                },
            ),
            contract.AUTHOR_SELF_CHECK_UNRESOLVED,
        ),
    ],
)
def test_invocation_local_author_self_check_rejects_invalid_submission(
    declared_sha256: str,
    check_ids: tuple[str, ...],
    rows: tuple[dict[str, object], ...],
    error_code: str,
) -> None:
    with pytest.raises(contract.AuthorSelfCheckValidationError) as caught:
        contract.validate_author_self_check_submission(
            b"exact candidate\n",
            declared_candidate_sha256=declared_sha256,
            required_check_ids=check_ids,
            rows=rows,
        )

    assert caught.value.code == error_code


@pytest.mark.parametrize("authoring_section", [False, True])
def test_old_skill_outcomes_are_rejected_alone_and_in_appendix(authoring_section):
    candidate = _candidate(authoring_section=authoring_section)
    resources = ("soul:bestpractice_ai_facing_writing",) if authoring_section else ()
    for payload in (candidate.replace(b"## 2. Intended Outcomes", b"## 2. Reader Gain", 1),
                    candidate + b"\n## 6. Reader Gain\n\nLegacy section.\n"):
        with pytest.raises(contract.SkillArtifactContractError, match="forbidden Skill heading"):
            contract.validate_artifact(payload, embedded_resource_ids=resources)


def test_duplicate_skill_outcomes_are_rejected():
    with pytest.raises(contract.SkillArtifactContractError, match="headings must be unique"):
        contract.validate_artifact(_candidate() + b"\n## 6. Intended Outcomes\n\nDuplicate.\n")


@pytest.mark.parametrize("heading", [b"## Reader Gain", b"### 5.1 Reader Gain", b"## 6. Reader Gain ###"])
def test_old_skill_heading_cannot_hide_unnumbered_or_nested(heading):
    with pytest.raises(contract.SkillArtifactContractError, match="forbidden Skill heading"):
        contract.validate_artifact(_candidate() + b"\n" + heading + b"\n\nLegacy.\n")


@pytest.mark.parametrize("fence", [b"```", b"~~~", b"````"])
def test_old_skill_heading_in_fenced_example_is_data(fence):
    result = contract.validate_artifact(_candidate() + b"\n" + fence + b"md\n## 2. Reader Gain\n" + fence + b"\n")
    assert result.headings[1] == "Intended Outcomes"


def test_empty_skill_outcomes_are_rejected():
    payload = _candidate().replace(b"Deliver one complete candidate for the recipient to review against its owning Design.", b"")
    with pytest.raises(contract.SkillArtifactContractError, match="empty or placeholder-only"):
        contract.validate_artifact(payload)


def test_previous_skill_contract_version_is_rejected(tmp_path):
    import json
    definition = contract.load_contract()
    definition["contract_version"] = "skill_artifact_contract_v4"
    path = tmp_path / "old.json"
    path.write_text(json.dumps(definition))
    with pytest.raises(contract.SkillArtifactContractError, match="unsupported.*version"):
        contract.load_contract(path)


def test_skill_outcomes_keep_task_delivery_and_registered_check_identity(tmp_path):
    import json
    definition = contract.load_contract()
    check = definition["reviewer_checklist"]["checks"][1]
    assert definition["contract_version"] == "skill_artifact_contract_v6"
    assert check["check_id"] == "task_and_reader_gain"
    assert all(fragment in check["required_result"] for fragment in ("任务应交付的结果", "接收者的使用情境", "必要质量要求", "不保证无证据结论", "不强制统一执行路径"))
    assert check["required_result"] in contract.render_reviewer_checklist().decode()
    schema_root = REPO_ROOT / "09_soul/governance/skills/the-skill-authoring/runtime_modules/skill_candidate_reviewer/schemas"
    input_schema = json.loads((schema_root / "input.schema.json").read_text())
    assert input_schema["$defs"]["skill_candidate_required_check_ids"]["prefixItems"][1]["const"] == check["check_id"]
    assert '"task_and_reader_gain"' in (schema_root / "output.schema.json").read_text()
    check["required_result"] = "Return the requested task deliverable to its recipient."
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(definition))
    assert check["required_result"] in contract.render_reviewer_checklist(path).decode()


@pytest.mark.parametrize("authoring_section", [False, True])
def test_five_section_contract_preserves_required_inputs_and_completion(authoring_section):
    resources = ("soul:bestpractice_ai_facing_writing",) if authoring_section else ()
    result = contract.validate_artifact(_candidate(authoring_section=authoring_section), embedded_resource_ids=resources)
    assert result.headings[-5:] == ("Task Summary", "Intended Outcomes", "Boundaries", "Inputs and Completion", "Method")
    assert "skill_execution_contract_subsections" in result.validator_ids


@pytest.mark.parametrize("heading", [
    b"## 6. Entry and Exit", b"## Execution Contract", b"  ## 6. Execution Contract ###",
    b"## Entry and Exit ##", b"## 6. Entry and Exit\t", b"## 6 Execution Contract",
])
def test_legacy_top_level_sections_cannot_be_appended(heading):
    with pytest.raises(contract.SkillArtifactContractError, match="forbidden Skill top-level heading"):
        contract.validate_artifact(_candidate() + b"\n" + heading + b"\n\nLegacy body.\n")


@pytest.mark.parametrize("heading", [b"### 5.1 Entry and Exit", b"### 5.1 Execution Contract", b"#### Execution Contract"])
def test_legacy_words_in_legal_subheadings_are_not_retired_main_sections(heading):
    result = contract.validate_artifact(_candidate() + b"\n" + heading + b"\n\nA task-specific explanation.\n")
    assert result.headings[-1] == "Method"


@pytest.mark.parametrize("fence", [b"```", b"~~~", b"````"])
def test_legacy_main_sections_inside_fenced_examples_remain_data(fence):
    result = contract.validate_artifact(_candidate() + b"\n" + fence + b"markdown\n## 3. Entry and Exit\n## 4. Execution Contract\n" + fence + b"\n")
    assert len(result.headings) == 5


def test_complete_old_six_section_layout_is_rejected():
    payload = _candidate()
    boundaries = b"## 3. Boundaries\n\nDo not claim Runtime or release authority.\n\n"
    payload = payload.replace(boundaries, b"").replace(b"## 2. Intended Outcomes", b"## 2. Intended Outcomes")
    payload = payload.replace(b"## 4. Inputs and Completion", b"## 3. Entry and Exit\n\nEnter or hand off.\n\n## 4. Execution Contract")
    payload = payload.replace(b"## 5. Method", boundaries.replace(b"## 2.", b"## 5.") + b"## 6. Method")
    with pytest.raises(contract.SkillArtifactContractError, match="forbidden Skill top-level heading"):
        contract.validate_artifact(payload)


@pytest.mark.parametrize("bad", [None, "Entry and Exit", [], [""], [7], ["Entry and Exit", "Entry and Exit"]])
def test_invalid_top_level_forbidden_heading_contract_is_rejected(tmp_path, bad):
    import json
    definition = contract.load_contract()
    definition["forbidden_top_level_headings"] = bad
    path = tmp_path / "bad_contract.json"
    path.write_text(json.dumps(definition))
    with pytest.raises(contract.SkillArtifactContractError, match="forbidden_top_level_headings"):
        contract.load_contract(path)


def test_top_level_forbidden_heading_is_consumed_from_the_contract(tmp_path):
    import json
    definition = contract.load_contract()
    definition["forbidden_top_level_headings"] = ["Retired Appendix"]
    path = tmp_path / "selected_contract.json"
    path.write_text(json.dumps(definition))
    with pytest.raises(contract.SkillArtifactContractError, match="forbidden Skill top-level heading"):
        contract.validate_artifact(_candidate() + b"\n## 6. Retired Appendix\n\nOld instructions.\n", contract_path=path)


@pytest.mark.parametrize("change", ["missing", "duplicate", "reversed"])
def test_completion_subsection_contract_survives_main_section_migration(change):
    payload = _candidate()
    if change == "missing":
        payload = payload.replace(b"### 4.2 Output", b"Completion text")
    elif change == "duplicate":
        payload += b"\n### 4.2 Output\n\nDuplicate.\n"
    else:
        payload = payload.replace(b"### 4.1 Inputs", b"SWAP").replace(b"### 4.2 Output", b"### 4.1 Inputs").replace(b"SWAP", b"### 4.2 Output")
    with pytest.raises(contract.SkillArtifactContractError, match="exactly once|out of order"):
        contract.validate_artifact(payload)


@pytest.mark.parametrize("missing", range(5), ids=["Task", "Boundaries", "Intended Outcomes", "Inputs and Completion", "Method"])
def test_missing_required_primary_section_is_rejected_after_renumbering(missing):
    import re
    parts = re.split(rb"(?m)(?=^## \d+\. )", _candidate())
    sections = [section for index, section in enumerate(parts[1:]) if index != missing]
    payload = parts[0] + b"".join(
        re.sub(rb"^## \d+\.", f"## {index}.".encode(), section, count=1)
        for index, section in enumerate(sections, 1)
    )
    with pytest.raises(contract.SkillArtifactContractError, match="required sections"):
        contract.validate_artifact(payload)


@pytest.mark.parametrize("order", [(0, 2, 1, 3, 4), (0, 1, 3, 2, 4)],
                         ids=["old_outcomes_before_boundaries", "completion_before_outcomes"])
def test_wrong_primary_section_order_is_rejected_with_continuous_numbers(order):
    import re
    parts = re.split(rb"(?m)(?=^## \d+\. )", _candidate())
    payload = parts[0] + b"".join(
        re.sub(rb"^## \d+\.", f"## {number}.".encode(), parts[index + 1], count=1)
        for number, index in enumerate(order, 1)
    )
    with pytest.raises(contract.SkillArtifactContractError, match="required sections"):
        contract.validate_artifact(payload)
