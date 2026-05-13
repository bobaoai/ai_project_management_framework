"""Contract Audit module registry.

Per-module instances for the_contract_audit T0 layer.
Mother classes and validation live in audit.base.
"""

from __future__ import annotations

from pathlib import Path

from ...base import (
    Design,
    Artifact,
    Tool,
    Agent,
    Workflow,
    WorkflowStep,
    CodeBinding,
    Gate,
    ContractFamilySpec,
    ContractRefList,
    validate_ref_integrity as _base_validate,
    validate_capsule as _base_capsule,
    unresolved_code_binding_paths as _base_unresolved,
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

MODULE_DESIGN_DOC = "designDoc/the_contract_audit.md"


# --- Upstream constraint Design refs ---

DESIGN_THE_DESIGN_DOC_MANAGEMENT = Design(
    "design_the_design_doc_management",
    "designDoc/the_design_doc_management.md",
)
DESIGN_THE_EXTERNAL_AGENT_MANAGEMENT = Design(
    "design_the_external_agent_management",
    "designDoc/the_external_agent_management.md",
)


# --- Code bindings ---

CODE_ASSEMBLE_PROMPT = CodeBinding(
    "src/audit/tools/assemble_contract_audit.py::assemble",
    "assembles self-contained audit prompt from module files",
)
CODE_PROMPT_TEMPLATE = CodeBinding(
    "src/audit/modules/the_contract_audit/contract_audit_prompt.md",
    "prompt template with 7 semantic checks and structured output format",
)
CODE_RUN_AUDIT = CodeBinding(
    "src/audit/run_audit.sh",
    "shell wrapper that invokes claude -p with assembled prompt and saves audit log",
)


# --- Artifacts ---

ARTIFACT_THE_CONTRACT_AUDIT_PROMPT_TEMPLATE = Artifact(
    "artifact_the_contract_audit_prompt_template",
    "src/audit/modules/the_contract_audit/contract_audit_prompt.md",
    "config_artifact",
)
ARTIFACT_THE_CONTRACT_AUDIT_RUN_LOG = Artifact(
    "artifact_the_contract_audit_run_log",
    "audit_log/<module_id>/<date>_round_<N>.yaml",
    "audit_artifact",
)


# --- Tools ---

TOOL_THE_CONTRACT_AUDIT_SEMANTIC_REVIEWER = Tool(
    tool_id="tool_the_contract_audit_semantic_reviewer",
    owner_ref="designDoc/the_external_agent_management.md",
    purpose=(
        "atomic external agent handle that assembles audit package "
        "and invokes independent AI reviewer for "
        "design doc / registry semantic alignment"
    ),
    code_bindings=[CODE_ASSEMBLE_PROMPT, CODE_PROMPT_TEMPLATE, CODE_RUN_AUDIT],
)


# --- Gates ---

GATE_THE_CONTRACT_AUDIT_PASSED = Gate(
    "gate_the_contract_audit_passed",
    "independent semantic reviewer returned 0 blocks and 0 fixes",
)


# --- Workflow ---

WORKFLOW_THE_CONTRACT_AUDIT_LOOP = Workflow(
    workflow_id="workflow_the_contract_audit_loop",
    owner_ref=MODULE_DESIGN_DOC,
    steps=[
        WorkflowStep(
            "capsule_recovery",
        ),
        WorkflowStep(
            "structural_validation",
        ),
        WorkflowStep(
            "semantic_review",
            tool_refs=[TOOL_THE_CONTRACT_AUDIT_SEMANTIC_REVIEWER],
            gates=[GATE_THE_CONTRACT_AUDIT_PASSED],
        ),
    ],
    tool_refs=[TOOL_THE_CONTRACT_AUDIT_SEMANTIC_REVIEWER],
    gates=[GATE_THE_CONTRACT_AUDIT_PASSED],
    code_bindings=[CODE_ASSEMBLE_PROMPT, CODE_RUN_AUDIT],
)


# --- Agent ---

AGENT_THE_CONTRACT_AUDIT = Agent(
    agent_id="agent_the_contract_audit",
    owner_ref=".claude/skills/agent-the-contract-audit/SKILL.md",
    role=(
        "independent audit agent under the_contract_audit T0 layer; "
        "ensures a module's design doc and registry are semantically aligned"
    ),
    objective=(
        "audit a module: run three-layer validation, invoke the semantic "
        "reviewer Tool, evaluate findings, fix or escalate until pass"
    ),
    policy=(
        "1. run validate_capsule() for Layer 1 capsule recovery. "
        "2. run validate() and unresolved_bindings() for Layer 2 structural check. "
        "3. invoke tool_the_contract_audit_semantic_reviewer via run_audit.sh for Layer 3. "
        "4. parse findings YAML; classify as surface_fix / type_system_gap / accepted_note. "
        "5. if surface_fix findings: fix design doc or registry, go to step 1. "
        "6. if 0 surface_fix: pass. "
        "7. max 3 rounds; if still surface_fix after 3 rounds, escalate to PM."
    ),
    tool_refs=[TOOL_THE_CONTRACT_AUDIT_SEMANTIC_REVIEWER],
    output_artifacts=[ARTIFACT_THE_CONTRACT_AUDIT_RUN_LOG],
    gates=[GATE_THE_CONTRACT_AUDIT_PASSED],
    stop_condition=(
        "reviewer returns 0 blocks and 0 fixes (pass), "
        "or 3 retry rounds exhausted (escalate to PM)"
    ),
)


# --- Module Design ---

DESIGN_THE_CONTRACT_AUDIT_MODULE = Design(
    design_id="design_the_contract_audit_module",
    owner_ref=MODULE_DESIGN_DOC,
    purpose=(
        "three-surface model, typed registry architecture, "
        "Design Doc / Registry / SKILL.md synchronization discipline, "
        "three-layer audit mechanism"
    ),
    role=(
        "T0 design for contract audit infrastructure that enforces "
        "surface consistency across ~60 modules"
    ),
    scope=(
        "three-surface model (Design Doc / Registry / SKILL.md)",
        "registry inheritance model (base -> shared_contracts -> per-module)",
        "three-layer audit (capsule recovery -> structural validation -> semantic audit)",
        "synchronization discipline (Design Doc prose -> Registry -> Code / SKILL.md)",
    ),
    artifact_refs=[
        ARTIFACT_THE_CONTRACT_AUDIT_PROMPT_TEMPLATE,
        ARTIFACT_THE_CONTRACT_AUDIT_RUN_LOG,
    ],
    tool_refs=[TOOL_THE_CONTRACT_AUDIT_SEMANTIC_REVIEWER],
    agent_refs=[AGENT_THE_CONTRACT_AUDIT],
    workflow_refs=[WORKFLOW_THE_CONTRACT_AUDIT_LOOP],
    code_bindings=[CODE_ASSEMBLE_PROMPT, CODE_PROMPT_TEMPLATE, CODE_RUN_AUDIT],
    gates=[GATE_THE_CONTRACT_AUDIT_PASSED],
)


# --- Family spec ---

CONTRACT_AUDIT_FAMILY = ContractFamilySpec(
    family_id="the_contract_audit",
    status="proposal",
    canonical_owner_candidates=[DESIGN_THE_CONTRACT_AUDIT_MODULE],
    upstream_constraints=[
        DESIGN_THE_DESIGN_DOC_MANAGEMENT,
        DESIGN_THE_EXTERNAL_AGENT_MANAGEMENT,
    ],
    core_classes=(Design, Artifact, Tool, Agent, Workflow),
    field_types=(ContractRefList,),
    blocked_names=(),
)


# --- All registered objects ---

CONTRACT_AUDIT_OBJECTS: ContractRefList = [
    DESIGN_THE_CONTRACT_AUDIT_MODULE,
    DESIGN_THE_DESIGN_DOC_MANAGEMENT,
    DESIGN_THE_EXTERNAL_AGENT_MANAGEMENT,
    ARTIFACT_THE_CONTRACT_AUDIT_PROMPT_TEMPLATE,
    ARTIFACT_THE_CONTRACT_AUDIT_RUN_LOG,
    TOOL_THE_CONTRACT_AUDIT_SEMANTIC_REVIEWER,
    AGENT_THE_CONTRACT_AUDIT,
    WORKFLOW_THE_CONTRACT_AUDIT_LOOP,
]


# --- Convenience wrappers ---

def validate() -> list[str]:
    return _base_validate(
        CONTRACT_AUDIT_OBJECTS,
        CONTRACT_AUDIT_FAMILY,
        [],
        PROJECT_ROOT,
    )


def unresolved_bindings() -> list[str]:
    return _base_unresolved(CONTRACT_AUDIT_OBJECTS, PROJECT_ROOT)


def validate_capsule() -> list[str]:
    return _base_capsule(MODULE_DESIGN_DOC, PROJECT_ROOT)


__all__ = [
    "CONTRACT_AUDIT_FAMILY",
    "CONTRACT_AUDIT_OBJECTS",
    "DESIGN_THE_CONTRACT_AUDIT_MODULE",
    "AGENT_THE_CONTRACT_AUDIT",
    "TOOL_THE_CONTRACT_AUDIT_SEMANTIC_REVIEWER",
    "WORKFLOW_THE_CONTRACT_AUDIT_LOOP",
    "validate",
    "validate_capsule",
    "unresolved_bindings",
]
