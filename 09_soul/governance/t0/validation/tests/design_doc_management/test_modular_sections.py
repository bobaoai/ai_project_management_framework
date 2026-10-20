from __future__ import annotations
import json
import pytest
from .test_artifact_cli import run_cli
from .test_artifact_contract import _candidate, contract

pytestmark = pytest.mark.deterministic


def _modular_candidate(
    layer="T0", *, capsule=False, flow=None, details=("Capability and Operation",)
):
    headings = (
        (["Intent Capsule"] if capsule else [])
        + ([flow] if flow else [])
        + ["Intended Outcomes", *details, "References"]
    )
    return _candidate(layer, headings=headings)


@pytest.mark.parametrize("layer", ["Charter", "T0", "T1", "T2"])
@pytest.mark.parametrize("flow", [False, True])
def test_modules_are_selected_without_a_fixed_middle_order(layer, flow):
    opening = (
        (
            "Constitutional Authority Map"
            if layer == "Charter"
            else "Primary System Flow"
        )
        if flow
        else None
    )
    for details in [
        ("Authority", "Capability and Operation"),
        ("Capability and Operation", "Authority"),
    ]:
        result = contract.validate_artifact(
            _modular_candidate(layer, flow=opening, details=details), layer=layer
        )
        assert result.headings[-1] == "References"
        assert result.headings.index("Intended Outcomes") == int(flow)


@pytest.mark.parametrize("layer", ["Charter", "T0", "T1", "T2"])
def test_only_required_modules_can_be_structurally_valid(layer):
    result = contract.validate_artifact(
        _modular_candidate(layer, details=()), layer=layer
    )
    assert result.headings == ("Intended Outcomes", "References") and not hasattr(
        result, "verdict"
    )


@pytest.mark.parametrize(
    "heading",
    [
        "Intent Capsule",
        "审查与完成",
        "Owner-specific Detail",
        "Authority：边界",
        "capability and operation",
        "Authority / Rules",
    ],
)
def test_unknown_or_retired_top_modules_are_rejected(heading):
    with pytest.raises(
        contract.DesignArtifactContractError, match="unknown Design module"
    ):
        contract.validate_artifact(_modular_candidate(details=(heading,)), layer="T0")


@pytest.mark.parametrize(
    "heading",
    [
        "Domain Outcome and Owned Objects",
        "Public Boundaries and Quality Rules",
        "T2 Partition and Dependencies",
    ],
)
@pytest.mark.parametrize("layer", ["Charter", "T0", "T1", "T2"])
def test_t1_supplements_follow_layer_applicability(heading, layer):
    payload = _modular_candidate(layer, details=(heading,))
    if layer == "T1":
        assert contract.validate_artifact(payload, layer=layer)
    else:
        with pytest.raises(contract.DesignArtifactContractError, match="not allowed"):
            contract.validate_artifact(payload, layer=layer)


@pytest.mark.parametrize(
    "heading",
    [
        "Product Identity and Scope",
        "Human Authority",
        "Constitutional Invariants",
        "Amendment Authority",
        "T0 Topology Reference",
    ],
)
def test_charter_supplements_do_not_expand_t0_authority(heading):
    assert contract.validate_artifact(
        _modular_candidate("Charter", details=(heading,)), layer="Charter"
    )
    with pytest.raises(contract.DesignArtifactContractError, match="not allowed"):
        contract.validate_artifact(_modular_candidate(details=(heading,)), layer="T0")


@pytest.mark.parametrize("layer", ["Charter", "T0", "T1", "T2"])
def test_shared_supplements_and_unnumbered_subsections(layer):
    payload = _modular_candidate(
        layer, details=("Design and Code Boundary", "Completion and Failure")
    )
    payload = payload.replace(
        b"Complete meaning for Completion and Failure.",
        b"### End of operation\n\nAn actual result is returned.\n### Recovery\n\nPreserve earlier valid results.",
    )
    assert contract.validate_artifact(payload, layer=layer)


def test_authority_and_human_authority_are_not_mechanically_exclusive():
    assert contract.validate_artifact(
        _modular_candidate("Charter", details=("Authority", "Human Authority")),
        layer="Charter",
    )


@pytest.mark.parametrize(
    "layer,details",
    [
        ("T1", ("Owned System Object", "Domain Outcome and Owned Objects")),
        ("T0", ("Completion and Failure", "Completion, Failure, and Recovery")),
        ("Charter", ("Primary System Flow", "Constitutional Authority Map")),
    ],
)
def test_exclusive_module_pairs(layer, details):
    with pytest.raises(contract.DesignArtifactContractError, match="exclusive group"):
        contract.validate_artifact(
            _modular_candidate(layer, details=details), layer=layer
        )


@pytest.mark.parametrize(
    "layer,flow",
    [("Charter", "Primary System Flow"), ("T0", "Constitutional Authority Map")],
)
def test_opening_navigation_has_the_correct_layer(layer, flow):
    with pytest.raises(contract.DesignArtifactContractError, match="not allowed"):
        contract.validate_artifact(_modular_candidate(layer, flow=flow), layer=layer)


@pytest.mark.parametrize(
    "heading", ["Primary System Flow", "Constitutional Authority Map"]
)
def test_opening_cannot_follow_outcomes(heading):
    layer = "Charter" if heading == "Constitutional Authority Map" else "T0"
    with pytest.raises(contract.DesignArtifactContractError, match="out of order"):
        contract.validate_artifact(
            _modular_candidate(layer, details=(heading,)), layer=layer
        )


@pytest.mark.parametrize("heading", ["Intended Outcomes", "References"])
def test_required_modules_cannot_be_renamed(heading):
    with pytest.raises(
        contract.DesignArtifactContractError, match="required Design heading"
    ):
        contract.validate_artifact(
            _modular_candidate().replace(heading.encode(), b"Renamed", 1), layer="T0"
        )


@pytest.mark.parametrize(
    "heading", ["Intended Outcomes", "References", "Capability and Operation"]
)
def test_duplicate_modules_cannot_hide(heading):
    with pytest.raises(
        contract.DesignArtifactContractError, match="headings must be unique"
    ):
        contract.validate_artifact(
            _modular_candidate() + f"\n## 4. {heading}\n\nDuplicate.\n".encode(),
            layer="T0",
        )


@pytest.mark.parametrize(
    "old,new",
    [
        (b"## 1.", b"## 0."),
        (b"## 2.", b"## 1."),
        (b"## 2.", b"## 9."),
        (b"## 1.", b"## 01."),
    ],
)
def test_numbering_has_one_continuous_origin(old, new):
    with pytest.raises(
        contract.DesignArtifactContractError, match="numbering must be continuous"
    ):
        contract.validate_artifact(
            _modular_candidate().replace(old, new, 1), layer="T0"
        )


def test_all_h2_sections_must_be_numbered():
    with pytest.raises(contract.DesignArtifactContractError, match="must be numbered"):
        contract.validate_artifact(
            _modular_candidate() + b"\n## Hidden section\nActual content.\n", layer="T0"
        )


def test_references_close_the_document():
    with pytest.raises(
        contract.DesignArtifactContractError, match="final Design section"
    ):
        contract.validate_artifact(
            _modular_candidate() + b"\n## 4. Authority\nActual authority.\n", layer="T0"
        )


@pytest.mark.parametrize(
    "body",
    [
        "",
        "TBD",
        "待补充",
        "Capability and Operation",
        "**Capability and Operation**",
        "### Local detail",
        "<!-- hidden content -->",
    ],
)
def test_chosen_modules_need_real_content(body):
    payload = _modular_candidate().replace(
        b"Complete meaning for Capability and Operation.", body.encode()
    )
    with pytest.raises(
        contract.DesignArtifactContractError, match="empty or placeholder"
    ):
        contract.validate_artifact(payload, layer="T0")


def test_diagram_only_content_is_not_empty():
    payload = _modular_candidate().replace(
        b"Complete meaning for Capability and Operation.",
        b"```mermaid\nflowchart LR\n A-->B\n```",
    )
    assert contract.validate_artifact(payload, layer="T0")


def test_cli_reports_the_current_rule_without_rewriting(tmp_path):
    path = tmp_path / "candidate.md"
    body = _modular_candidate(flow="Primary System Flow")
    path.write_bytes(body)
    result = run_cli(tmp_path, str(path), "--layer", "T0", "--json")
    assert result.returncode == 0, result.stderr
    (row,) = json.loads(result.stdout)
    assert (
        row["contract_version"] == "design_artifact_contract_v5"
        and row["references_checked"] is False
    )
    assert (
        row["validation_scope"] == "structure_and_identity_only"
        and path.read_bytes() == body
    )
