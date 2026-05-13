"""Skill Management module registry.

Per-module instances for the_skill_management T0 layer.
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

MODULE_DESIGN_DOC = "designDoc/the_skill_management.md"


# --- Upstream constraint Design refs ---

DESIGN_THE_DESIGN_DOC_MANAGEMENT = Design(
    "design_the_design_doc_management",
    "designDoc/the_design_doc_management.md",
)
DESIGN_THE_CONTRACT_AUDIT = Design(
    "design_the_contract_audit",
    "designDoc/the_contract_audit.md",
)
DESIGN_THE_EXTERNAL_AGENT_MANAGEMENT = Design(
    "design_the_external_agent_management",
    "designDoc/the_external_agent_management.md",
)


# --- Code bindings ---

CODE_ASSEMBLE_WRITER = CodeBinding(
    "src/audit/tools/assemble_skill_writer.py::assemble",
    "assembles self-contained writer prompt from governance + module files",
)
CODE_ASSEMBLE_REVIEWER = CodeBinding(
    "src/audit/tools/assemble_skill_reviewer.py::assemble",
    "assembles self-contained reviewer prompt from governance + module files + SKILL.md",
)
CODE_WRITER_PROMPT_TEMPLATE = CodeBinding(
    "src/audit/modules/the_skill_management/skill_writer_prompt.md",
    "writer prompt template with governance + module slots",
)
CODE_REVIEWER_PROMPT_TEMPLATE = CodeBinding(
    "src/audit/modules/the_skill_management/skill_reviewer_prompt.md",
    "reviewer prompt template with S1-S10 checks and YAML output format",
)
CODE_RUN_WRITER = CodeBinding(
    "src/audit/run_skill_writer.sh",
    "shell wrapper that invokes claude -p with assembled writer prompt",
)
CODE_RUN_REVIEWER = CodeBinding(
    "src/audit/run_skill_reviewer.sh",
    "shell wrapper that invokes claude -p with assembled reviewer prompt",
)


# --- Artifacts ---

ARTIFACT_SKILL_WRITER_PROMPT_TEMPLATE = Artifact(
    "artifact_skill_writer_prompt_template",
    "src/audit/modules/the_skill_management/skill_writer_prompt.md",
    "config_artifact",
)
ARTIFACT_SKILL_REVIEWER_PROMPT_TEMPLATE = Artifact(
    "artifact_skill_reviewer_prompt_template",
    "src/audit/modules/the_skill_management/skill_reviewer_prompt.md",
    "config_artifact",
)
ARTIFACT_SKILL_REVIEW_LOG = Artifact(
    "artifact_skill_review_log",
    "audit_log/<module_id>/skill_review_<skill_dir>_<date>.yaml",
    "audit_artifact",
)


# --- Tools ---

TOOL_SKILL_WRITER = Tool(
    tool_id="tool_skill_writer",
    owner_ref="designDoc/the_external_agent_management.md",
    purpose=(
        "atomic external agent handle that assembles governance + module context "
        "and invokes independent AI writer to produce SKILL.md content"
    ),
    code_bindings=[CODE_ASSEMBLE_WRITER, CODE_WRITER_PROMPT_TEMPLATE, CODE_RUN_WRITER],
)

TOOL_SKILL_REVIEWER = Tool(
    tool_id="tool_skill_reviewer",
    owner_ref="designDoc/the_external_agent_management.md",
    purpose=(
        "atomic external agent handle that assembles governance + module context + SKILL.md "
        "and invokes independent AI reviewer to check S1-S10 alignment"
    ),
    code_bindings=[CODE_ASSEMBLE_REVIEWER, CODE_REVIEWER_PROMPT_TEMPLATE, CODE_RUN_REVIEWER],
)


# --- Gates ---

GATE_SKILL_REVIEW_PASSED = Gate(
    "gate_skill_review_passed",
    "independent skill reviewer returned verdict accept_as_is or accept_with_notes",
)


# --- Workflow ---

WORKFLOW_SKILL_WRITE_REVIEW_LOOP = Workflow(
    workflow_id="workflow_skill_write_review_loop",
    owner_ref=MODULE_DESIGN_DOC,
    steps=[
        WorkflowStep(
            "invoke_writer",
            tool_refs=[TOOL_SKILL_WRITER],
        ),
        WorkflowStep(
            "invoke_reviewer",
            tool_refs=[TOOL_SKILL_REVIEWER],
            gates=[GATE_SKILL_REVIEW_PASSED],
        ),
        WorkflowStep(
            "apply_fixes",
        ),
    ],
    tool_refs=[TOOL_SKILL_WRITER, TOOL_SKILL_REVIEWER],
    gates=[GATE_SKILL_REVIEW_PASSED],
    code_bindings=[
        CODE_ASSEMBLE_WRITER, CODE_ASSEMBLE_REVIEWER,
        CODE_RUN_WRITER, CODE_RUN_REVIEWER,
    ],
)


# --- Agent ---

AGENT_SKILL_MANAGEMENT = Agent(
    agent_id="agent_skill_management",
    owner_ref=".claude/skills/agent-the-skill-management/SKILL.md",
    role=(
        "skill writing agent under the_skill_management T0 layer; "
        "orchestrates writer, reviewer, and edit loop to produce "
        "governance-compliant SKILL.md files"
    ),
    objective=(
        "produce a SKILL.md that passes the independent skill reviewer "
        "(accept_as_is or accept_with_notes) within 3 rounds"
    ),
    policy=(
        "1. invoke tool_skill_writer to produce SKILL.md draft. "
        "2. invoke tool_skill_reviewer to check S1-S10. "
        "3. parse reviewer YAML; classify verdict. "
        "4. if accept_as_is or accept_with_notes: write SKILL.md to target path, stop. "
        "5. if needs_author_revision: edit SKILL.md based on findings, go to step 2. "
        "6. if needs_registry_sync: report to user, stop. "
        "7. max 3 review-edit rounds; if still needs_author_revision after 3, escalate to user."
    ),
    tool_refs=[TOOL_SKILL_WRITER, TOOL_SKILL_REVIEWER],
    output_artifacts=[ARTIFACT_SKILL_REVIEW_LOG],
    gates=[GATE_SKILL_REVIEW_PASSED],
    stop_condition=(
        "reviewer returns accept_as_is or accept_with_notes (pass), "
        "or needs_registry_sync (escalate), "
        "or 3 review-edit rounds exhausted (escalate to user)"
    ),
)


# --- Module Design ---

DESIGN_THE_SKILL_MANAGEMENT_MODULE = Design(
    design_id="design_the_skill_management_module",
    owner_ref=MODULE_DESIGN_DOC,
    purpose=(
        "SKILL.md surface governance: writing principles, required content areas, "
        "reviewer contract, registry alignment, style rules"
    ),
    role=(
        "T0 design for SKILL.md writing governance that defines how "
        "AI-facing runtime behavior instructions are authored and reviewed"
    ),
    scope=(
        "SKILL.md writing principles (result determinism, enabling guidance, contract-first)",
        "required content areas (Agent 7 areas, Skill 5 areas, frontmatter)",
        "surface authority (what SKILL.md writes vs does not write)",
        "reviewer contract (S1-S10 checks, verdict format)",
        "writing flow (writer, self-review, reviewer, application rule)",
    ),
    artifact_refs=[
        ARTIFACT_SKILL_WRITER_PROMPT_TEMPLATE,
        ARTIFACT_SKILL_REVIEWER_PROMPT_TEMPLATE,
        ARTIFACT_SKILL_REVIEW_LOG,
    ],
    tool_refs=[TOOL_SKILL_WRITER, TOOL_SKILL_REVIEWER],
    agent_refs=[AGENT_SKILL_MANAGEMENT],
    workflow_refs=[WORKFLOW_SKILL_WRITE_REVIEW_LOOP],
    code_bindings=[
        CODE_ASSEMBLE_WRITER, CODE_ASSEMBLE_REVIEWER,
        CODE_WRITER_PROMPT_TEMPLATE, CODE_REVIEWER_PROMPT_TEMPLATE,
        CODE_RUN_WRITER, CODE_RUN_REVIEWER,
    ],
    gates=[GATE_SKILL_REVIEW_PASSED],
)


# --- Family spec ---

SKILL_MANAGEMENT_FAMILY = ContractFamilySpec(
    family_id="the_skill_management",
    status="proposal",
    canonical_owner_candidates=[DESIGN_THE_SKILL_MANAGEMENT_MODULE],
    upstream_constraints=[
        DESIGN_THE_DESIGN_DOC_MANAGEMENT,
        DESIGN_THE_CONTRACT_AUDIT,
        DESIGN_THE_EXTERNAL_AGENT_MANAGEMENT,
    ],
    core_classes=(Design, Artifact, Tool, Agent, Workflow),
    field_types=(ContractRefList,),
    blocked_names=(),
)


# --- All registered objects ---

SKILL_MANAGEMENT_OBJECTS: ContractRefList = [
    DESIGN_THE_SKILL_MANAGEMENT_MODULE,
    DESIGN_THE_DESIGN_DOC_MANAGEMENT,
    DESIGN_THE_CONTRACT_AUDIT,
    DESIGN_THE_EXTERNAL_AGENT_MANAGEMENT,
    ARTIFACT_SKILL_WRITER_PROMPT_TEMPLATE,
    ARTIFACT_SKILL_REVIEWER_PROMPT_TEMPLATE,
    ARTIFACT_SKILL_REVIEW_LOG,
    TOOL_SKILL_WRITER,
    TOOL_SKILL_REVIEWER,
    AGENT_SKILL_MANAGEMENT,
    WORKFLOW_SKILL_WRITE_REVIEW_LOOP,
]


# --- Convenience wrappers ---

def validate() -> list[str]:
    return _base_validate(
        SKILL_MANAGEMENT_OBJECTS,
        SKILL_MANAGEMENT_FAMILY,
        [],
        PROJECT_ROOT,
    )


def unresolved_bindings() -> list[str]:
    return _base_unresolved(SKILL_MANAGEMENT_OBJECTS, PROJECT_ROOT)


def validate_capsule() -> list[str]:
    return _base_capsule(MODULE_DESIGN_DOC, PROJECT_ROOT)


__all__ = [
    "SKILL_MANAGEMENT_FAMILY",
    "SKILL_MANAGEMENT_OBJECTS",
    "DESIGN_THE_SKILL_MANAGEMENT_MODULE",
    "AGENT_SKILL_MANAGEMENT",
    "TOOL_SKILL_WRITER",
    "TOOL_SKILL_REVIEWER",
    "WORKFLOW_SKILL_WRITE_REVIEW_LOOP",
    "validate",
    "validate_capsule",
    "unresolved_bindings",
]
