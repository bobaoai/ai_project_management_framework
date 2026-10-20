from __future__ import annotations
import json
from pathlib import Path
import pytest
from .test_artifact_contract import _candidate, contract
from .test_artifact_cli import run_cli
from .test_review_entry import entry, args_for

pytestmark = pytest.mark.deterministic


def _reference_candidate(reference):
    return _candidate("t0").replace(
        b"Complete meaning for References.", reference.encode()
    )


def _root(tmp_path):
    root = tmp_path / "project"
    (root / "designDoc").mkdir(parents=True)
    (root / "designDoc/example.md").write_text("Previous canonical version.")
    return root


@pytest.mark.parametrize(
    "key", ["title", "layer", "canonical_owner", "owned_system_object"]
)
def test_candidate_required_fields_cannot_be_inferred_from_body_or_path(tmp_path, key):
    payload = _candidate("t0")
    lines = payload.decode().splitlines(keepends=True)
    payload = "".join(line for line in lines if not line.startswith(key + ":")).encode()
    with pytest.raises(contract.DesignArtifactContractError):
        contract.validate_artifact(payload, layer="T0")
    path = tmp_path / "example.md"
    path.write_bytes(payload)
    with pytest.raises(ValueError):
        entry.build_design_review_input(**args_for(path))


@pytest.mark.parametrize(
    "key", contract.load_contract()["identity_fields"]["forbidden"]
)
def test_known_forbidden_metadata_keys_are_rejected(key):
    payload = _candidate("t0").replace(b"---\n", f"---\n{key}: value\n".encode(), 1)
    with pytest.raises(
        contract.DesignArtifactContractError, match="forbidden Design metadata"
    ):
        contract.validate_artifact(payload, layer="T0")


@pytest.mark.parametrize(
    "value",
    [
        "",
        "# comment only",
        "null",
        "~",
        "''",
        '"   "',
        "|\n  multiple lines",
        "[one, two]",
        "{name: object}",
        "&reference object",
    ],
)
def test_empty_or_unsupported_identity_is_not_silently_coerced(value):
    payload = _candidate("t0").replace(
        b"owned_system_object: Example decision",
        f"owned_system_object: {value}".encode(),
    )
    with pytest.raises(contract.DesignArtifactContractError):
        contract.validate_artifact(payload, layer="T0")


def test_duplicate_and_unclosed_identity_are_rejected():
    with pytest.raises(contract.DesignArtifactContractError, match="duplicate"):
        contract.validate_artifact(
            _candidate("t0").replace(b"layer: T0", b"layer: T0\nlayer: T0"), layer="T0"
        )
    with pytest.raises(contract.DesignArtifactContractError, match="not closed"):
        contract.validate_artifact(
            _candidate("t0").replace(b"\n---\n", b"\n", 1), layer="T0"
        )


@pytest.mark.parametrize("layer", ["charter", "t0", "t1", "t2"])
def test_parent_depends_on_actual_inheritance_not_the_layer_alone(layer):
    assert contract.validate_artifact(_candidate(layer), layer=layer)
    parent = _candidate(layer).replace(
        b"---\n", b"---\nparent: designDoc/parent.md\n", 1
    )
    if layer in {"charter", "t0"}:
        with pytest.raises(
            contract.DesignArtifactContractError, match="parent is forbidden"
        ):
            contract.validate_artifact(parent, layer=layer)
    else:
        assert contract.validate_artifact(parent, layer=layer)
        for value in ["null", "''", '" "']:
            with pytest.raises(contract.DesignArtifactContractError):
                contract.validate_artifact(
                    parent.replace(b"designDoc/parent.md", value.encode()), layer=layer
                )


@pytest.mark.parametrize(
    "background",
    [
        "A background note without frontmatter.",
        "---\ntitle: Older Design\nstatus: candidate\nreader_persona:\n  - Author\n---\nLegacy body.",
        "---\nname: sample\nmetadata:\n  skill_class: primary_agent_development\n---\nSkill body.",
        "---\ntitle: |\n  A multiline title\n---\nThe whole text remains available.",
    ],
)
def test_background_and_governing_material_keep_their_own_representation(
    tmp_path, background
):
    path = tmp_path / "candidate.md"
    path.write_bytes(_candidate("t0"))
    context = tmp_path / "context.md"
    context.write_text(background)
    result = entry.build_design_review_input(
        **args_for(path),
        context_bindings=[("dependency_contract", "explicit_owner", context)],
        ddm_path=context,
    )
    row = next(
        x
        for x in result["context_documents"]
        if x["context_role"] == "dependency_contract"
    )
    assert row["body"] == background and row["owner_ref"] == "explicit_owner"
    assert (
        next(
            x
            for x in result["context_documents"]
            if x["context_role"] == "governing_contract"
        )["body"]
        == background
    )
    inspection = next(
        x
        for x in result["context_documents"]
        if x["document_id"] == "deterministic_design_validation"
    )
    assert json.loads(inspection["body"])["checks"][0]["references_checked"] is False


def test_explicit_root_resolves_from_canonical_owner_not_temporary_candidate(tmp_path):
    root = _root(tmp_path)
    (root / "designDoc/peer.md").write_text("peer")
    payload = _reference_candidate("[Peer](peer.md)")
    candidate = tmp_path / "outside/candidate.md"
    candidate.parent.mkdir()
    candidate.write_bytes(payload)
    result = run_cli(
        tmp_path, str(candidate), "--layer", "T0", "--project-root", str(root), "--json"
    )
    assert result.returncode == 0, result.stdout
    (row,) = json.loads(result.stdout)
    assert (
        row["references_checked"]
        and row["validation_scope"] == "structure_identity_and_local_files"
    )
    value = entry.build_design_review_input(**args_for(candidate), project_root=root)
    assert (
        json.loads(
            next(
                x
                for x in value["context_documents"]
                if x["document_id"] == "deterministic_design_validation"
            )["body"]
        )["checks"][0]["references_checked"]
        is True
    )
    (root / "designDoc/peer.md").unlink()
    (candidate.parent / "peer.md").write_text("Do not borrow this file.")
    with pytest.raises(
        contract.DesignArtifactContractError, match="unresolved local reference"
    ):
        contract.validate_artifact(
            payload, layer="T0", reference_resolver=contract.local_file_resolver(root)
        )


def test_source_overlay_is_explicit_and_does_not_require_installed_projections(
    tmp_path,
):
    root = tmp_path / "source"
    (root / "sources").mkdir(parents=True)
    for name in ["example", "peer"]:
        (root / f"sources/{name}.md").write_text(name)
    resolve = contract.local_file_resolver(
        root,
        overrides={
            f"designDoc/{name}.md": f"sources/{name}.md" for name in ["example", "peer"]
        },
    )
    assert contract.validate_artifact(
        _reference_candidate("[Peer](peer.md)"), layer="T0", reference_resolver=resolve
    ).references_checked
    with pytest.raises(contract.DesignArtifactContractError, match="unresolved"):
        contract.validate_artifact(
            _reference_candidate("[Unlisted](other.md)"),
            layer="T0",
            reference_resolver=resolve,
        )


@pytest.mark.parametrize(
    "reference",
    [
        "../../outside.md",
        "%2Fetc/passwd",
        "file:///etc/passwd",
        "schema:unknown@v1",
        "//example.org/object",
        "peer.md?version=1",
    ],
)
def test_unsupported_or_escaping_local_references_fail(tmp_path, reference):
    root = _root(tmp_path)
    with pytest.raises(contract.DesignArtifactContractError):
        contract.validate_artifact(
            _reference_candidate(f"[Bad]({reference})"),
            layer="T0",
            reference_resolver=contract.local_file_resolver(root),
        )


def test_symlink_escape_is_not_a_local_reference(tmp_path):
    root = _root(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("outside")
    (root / "designDoc/peer.md").symlink_to(outside)
    with pytest.raises(contract.DesignArtifactContractError, match="symlink escapes"):
        contract.validate_artifact(
            _reference_candidate("[Peer](peer.md)"),
            layer="T0",
            reference_resolver=contract.local_file_resolver(root),
        )


@pytest.mark.parametrize(
    "reference",
    [
        "[Nested [label]](peer.md)",
        '[Peer](peer.md "display title")',
        "[Peer][named]\n\n[named]: peer.md",
        "[named][]\n\n[named]: peer.md",
        "[named]\n\n[named]: peer.md",
        "[Peer](<a b.md>)",
        "[Peer](peer(1).md)",
        "[Peer](a\\ b.md)",
        "[Peer](peer.md#unchecked-fragment)",
    ],
)
def test_markdown_file_link_forms_and_fragments(tmp_path, reference):
    root = _root(tmp_path)
    for name in ["peer.md", "peer(1).md", "a b.md"]:
        (root / "designDoc" / name).write_text("peer")
    assert contract.validate_artifact(
        _reference_candidate(reference),
        layer="T0",
        reference_resolver=contract.local_file_resolver(root),
    )
    for name in ["peer.md", "peer(1).md", "a b.md"]:
        (root / "designDoc" / name).unlink()
    with pytest.raises(contract.DesignArtifactContractError, match="unresolved"):
        contract.validate_artifact(
            _reference_candidate(reference),
            layer="T0",
            reference_resolver=contract.local_file_resolver(root),
        )


def test_external_links_are_reported_unverified_without_network(tmp_path, monkeypatch):
    import socket

    def no_network(*args, **kwargs):
        raise AssertionError("network access is forbidden")

    monkeypatch.setattr(socket, "socket", no_network)
    root = _root(tmp_path)
    refs = ["https://example.invalid/doc", "mailto:review@example.invalid"]
    result = contract.validate_artifact(
        _reference_candidate("\n".join(f"[External]({x})" for x in refs)),
        layer="T0",
        reference_resolver=contract.local_file_resolver(root),
    )
    assert result.external_references_unverified == tuple(refs)


def test_examples_comments_and_escaped_labels_do_not_create_file_dependencies(tmp_path):
    root = _root(tmp_path)
    example = "Actual reference scope.\n```md\n[Missing](missing.md)\n```\n<!-- [Missing](hidden.md) -->\n`[Missing](inline.md)`\n\\[literal](also-missing.md)"
    assert contract.validate_artifact(
        _reference_candidate(example),
        layer="T0",
        reference_resolver=contract.local_file_resolver(root),
    )


def test_a_resolver_must_return_an_actual_file():
    with pytest.raises(contract.DesignArtifactContractError, match="existing file"):
        contract.validate_artifact(
            _candidate("t0"), layer="T0", reference_resolver=lambda ref, owner: None
        )


def test_comment_markers_in_frontmatter_and_inline_code_are_literal(tmp_path):
    root = _root(tmp_path)
    (root / "designDoc/peer.md").write_text("peer")
    payload = _reference_candidate("A literal `<!--` marker. [Peer](peer.md)")
    payload = payload.replace(b"title: Example", b'title: "An <!-- example"')
    assert contract.validate_artifact(
        payload, layer="T0", reference_resolver=contract.local_file_resolver(root)
    )
    (root / "designDoc/peer.md").unlink()
    with pytest.raises(contract.DesignArtifactContractError, match="unresolved"):
        contract.validate_artifact(
            payload, layer="T0", reference_resolver=contract.local_file_resolver(root)
        )
