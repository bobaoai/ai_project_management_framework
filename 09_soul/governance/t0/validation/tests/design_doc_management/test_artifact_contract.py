from __future__ import annotations
import hashlib, importlib.util, json, re, sys
from pathlib import Path
import pytest

pytestmark = pytest.mark.deterministic
REPO_ROOT = Path(__file__).resolve().parents[6]
MODULE_PATH = (
    REPO_ROOT
    / "09_soul/governance/t0/validation/artifact_contracts/design_artifact_contract.py"
)
SPEC = importlib.util.spec_from_file_location("design_artifact_contract", MODULE_PATH)
contract = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = contract
SPEC.loader.exec_module(contract)


def _candidate(
    layer, *, extra_heading=None, extra_headings=(), outside_heading=None, headings=None
):
    value = "Charter" if layer.lower() == "charter" else layer.upper()
    if headings is None:
        opening = (
            "Constitutional Authority Map"
            if value == "Charter"
            else "Primary System Flow"
        )
        headings = [
            opening,
            "Intended Outcomes",
            "Owned System Object",
            "Authority",
            "Capability and Operation",
            "Architecture and Lifecycle",
            "Public Interface and Effects",
            "System-wide Invariants",
            "Peer Boundaries",
            "Completion, Failure, and Recovery",
            "Dependencies and Verification",
            "References",
        ]
    headings = list(headings)
    headings[-1:-1] = [*extra_headings, *([extra_heading] if extra_heading else [])]
    if outside_heading:
        headings.insert(1, outside_heading)
    rows = [
        "---",
        f"layer: {value}",
        "title: Example",
        "canonical_owner: designDoc/example.md",
        "owned_system_object: Example decision",
        "---",
        "",
        "# Candidate",
        "",
        "The selected capability serves a declared request.",
    ]
    for index, heading in enumerate(headings, 1):
        rows += ["", f"## {index}. {heading}", "", f"Complete meaning for {heading}."]
    return ("\n".join(rows) + "\n").encode()


def _replace_once(payload, old, new):
    text = payload.decode()
    assert text.count(old) == 1
    return text.replace(old, new, 1).encode()


@pytest.mark.parametrize("layer", ["charter", "t0", "t1", "t2"])
def test_each_layer_uses_current_contract(layer):
    payload = _candidate(layer)
    result = contract.validate_artifact(payload, layer=layer)
    assert result.subject_sha256 == hashlib.sha256(payload).hexdigest()
    assert result.contract_version == "design_artifact_contract_v5"
    assert (
        result.contract_sha256
        == hashlib.sha256(contract.CONTRACT_PATH.read_bytes()).hexdigest()
    )
    assert result.layer == layer and not result.references_checked
    assert result.validation_scope == "structure_and_identity_only"
    assert "design_modular_section_selection" in result.validator_ids


@pytest.mark.parametrize("fence", ["```", "~~~", "````"])
def test_fenced_examples_are_not_sections_or_forbidden_headings(fence):
    payload = _candidate("t0").replace(
        b"Complete meaning for Authority.",
        (
            f"Authority applies to this operation.\n{fence}md\n## 99. User Intent\n## Hidden\n{fence}\n"
        ).encode(),
    )
    result = contract.validate_artifact(payload, layer="t0")
    assert "Hidden" not in result.headings and "User Intent" not in result.headings


def test_comments_cannot_supply_sections_or_content():
    payload = _candidate("t0").replace(
        b"Complete meaning for Authority.", b"<!-- text\n## 55. User Intent\n-->"
    )
    with pytest.raises(
        contract.DesignArtifactContractError, match="empty or placeholder"
    ):
        contract.validate_artifact(payload, layer="t0")
    payload = _candidate("t0").replace(
        b"Complete meaning for Authority.",
        b"Actual authority.\n<!-- ``` ignored fence -->",
    )
    assert contract.validate_artifact(payload, layer="t0")


def test_fenced_example_cannot_supply_the_document():
    with pytest.raises(contract.DesignArtifactContractError):
        contract.validate_artifact(b"````md\n" + _candidate("t0") + b"````", layer="t0")


@pytest.mark.parametrize("value", ['"T0"', "'T0'"])
def test_quoted_layer_is_supported(value):
    assert contract.validate_artifact(
        _candidate("t0").replace(b"layer: T0", f"layer: {value}".encode()), layer="t0"
    )


@pytest.mark.parametrize("old_heading", ["User Intent", "Reader Gain"])
@pytest.mark.parametrize("layer", ["charter", "t0", "t1", "t2"])
def test_retired_outcome_names_are_rejected(layer, old_heading):
    for payload in [
        _candidate(layer, extra_heading=old_heading),
        _candidate(layer).replace(
            b"## 2. Intended Outcomes", f"## 2. {old_heading}".encode()
        ),
    ]:
        with pytest.raises(
            contract.DesignArtifactContractError, match="forbidden Design heading"
        ):
            contract.validate_artifact(payload, layer=layer)


@pytest.mark.parametrize(
    "heading", ["## Reader Gain", "### 5.1 User Intent", "## 99. Reader Gain ###"]
)
def test_retired_name_cannot_hide_unnumbered_or_nested(heading):
    with pytest.raises(
        contract.DesignArtifactContractError, match="forbidden Design heading"
    ):
        contract.validate_artifact(
            _candidate("t0") + f"\n{heading}\nLegacy content.\n".encode(), layer="t0"
        )


@pytest.mark.parametrize("version", ["v1", "v2", "v3", "v4", "v99"])
def test_previous_or_unknown_contract_is_not_a_compatibility_selector(
    tmp_path, version
):
    data = contract.load_contract()
    data["contract_version"] = "design_artifact_contract_" + version
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(data))
    with pytest.raises(
        contract.DesignArtifactContractError, match="unsupported.*version"
    ):
        contract.load_contract(path)


def test_design_reviewer_prompt_contains_exact_projected_checklist() -> None:
    prompt = (
        REPO_ROOT / "09_soul/governance/skills/the-design-authoring/runtime_modules/"
        "design_contract_reviewer/prompt.md"
    ).read_bytes()
    resource_id = "t0:design_contract_review_checklist"
    start = f"<!-- embedded-resource:{resource_id}:start -->\n".encode()
    end = f"<!-- embedded-resource:{resource_id}:end -->".encode()

    projected = prompt.split(start, 1)[1].split(end, 1)[0]

    assert projected == contract.render_reviewer_checklist()


def test_code_checklist_matches_the_ddm_authority_table() -> None:
    source = (
        REPO_ROOT / "09_soul/governance/t0/the_design_doc_management.md"
    ).read_bytes()
    table = source.split(b"<!-- design-contract-review-checklist:start -->", 1)[
        1
    ].split(b"<!-- design-contract-review-checklist:end -->", 1)[0]
    assert contract.render_reviewer_checklist().strip() == table.strip()


def test_design_authoring_skill_does_not_duplicate_reviewer_checklist() -> None:
    authoring = (
        REPO_ROOT / "09_soul/governance/skills/the-design-authoring/SKILL.md"
    ).read_text(encoding="utf-8")

    assert "skill-specific-review-checklist:design_contract_reviewer" not in authoring
    assert "## 7. Design Reviewer Checklist Source" not in authoring


def test_checklist_identity_is_stable_and_authority_text_is_exact(tmp_path):
    definition = contract.load_contract()
    check = definition["reviewer_checklist"]["checks"][0]
    assert check["check_id"] == "intent_and_reader_result"
    authority = (
        REPO_ROOT / "09_soul/governance/t0/the_design_doc_management.md"
    ).read_text()
    assert check["required_result"] in authority
    schema_root = (
        REPO_ROOT
        / "09_soul/governance/skills/the-design-authoring/runtime_modules/design_contract_reviewer/schemas"
    )
    schema = json.loads((schema_root / "input.schema.json").read_text())
    assert (
        schema["properties"]["required_check_ids"]["prefixItems"][0]["const"]
        == check["check_id"]
    )
    assert check["check_id"] in (schema_root / "output.schema.json").read_text()
    check["required_result"] = "Candidate owner-defined checklist wording."
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(definition))
    assert check["required_result"] in contract.render_reviewer_checklist(path).decode()


def test_module_catalog_matches_the_actual_ddm_module_library():
    authority = (
        REPO_ROOT / "09_soul/governance/t0/the_design_doc_management.md"
    ).read_text()
    names = set(re.findall(r"^#### ([A-Za-z][^：\n]+)：", authority, re.M)) - {
        "Intent Capsule"
    }
    supplement = authority.split("#### T1 常用的补充标题", 1)[1].split("### 5.3", 1)[0]
    rows = re.findall(r"^\| `([^`]+)` \| ([^|]+) \|", supplement, re.M)
    names.update(name for name, _ in rows)
    definition = contract.load_contract()
    assert set(definition["modules"]) == names and len(names) == 23
    for name, layers in rows:
        assert set(definition["modules"][name]["layers"]) == {
            x.strip().lower() for x in layers.split("、")
        }
    assert definition["modules"]["Primary System Flow"]["layers"] == ["t0", "t1", "t2"]
    assert "protected_headings" not in json.dumps(
        definition
    ) and "extension_slot" not in json.dumps(definition)
