"""Current structural test doubles, not independently reviewed Design content."""

from pathlib import Path
import hashlib
import shutil


def valid_t0(identity, body=b"Fixture content.", target=None):
    target = target or f"designDoc/{identity}.md"
    return (
        f"---\ntitle: {identity}\nlayer: T0\ncanonical_owner: {target}\nowned_system_object: Fixture-owned operation\nt0_layer_id: {identity}\n---\n\n# Fixture\n\n## 1. Intended Outcomes\n\nExercise one bounded validation or installation outcome.\n\n## 2. References\n\nThe test declares the required fixture inputs.\n\n".encode()
        + body
        + b"\n"
    )


def add_design_contract(root, manifest):
    repo = Path(__file__).resolve().parents[5]
    identity = "the_design_doc_management"
    source = f"09_soul/governance/t0/{identity}.md"
    target = f"designDoc/{identity}.md"
    payload = valid_t0(
        identity, b"Test-only DDM source for deterministic source validation."
    )
    for rel in [source, target]:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(payload)
    manifest["portable_t0_contracts"].append(
        {
            "t0_layer_id": identity,
            "source": source,
            "target": target,
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    )
    prefix = "09_soul/governance/t0/validation/artifact_contracts/"
    for name in ["design_artifact_contract.json", "design_artifact_contract.py"]:
        target_path = root / prefix / name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / prefix / name, target_path)
    manifest["artifact_contracts"].append(
        {
            "artifact_contract_id": "design_document_artifact_contract",
            "owner_t0_layer_id": identity,
            "source": prefix + "design_artifact_contract.json",
            "source_sha256": hashlib.sha256(
                (root / prefix / "design_artifact_contract.json").read_bytes()
            ).hexdigest(),
            "adapter": prefix + "design_artifact_contract.py",
            "adapter_sha256": hashlib.sha256(
                (root / prefix / "design_artifact_contract.py").read_bytes()
            ).hexdigest(),
        }
    )
