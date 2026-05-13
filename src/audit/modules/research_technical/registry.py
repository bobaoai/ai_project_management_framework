"""Research Technical module registry.

Per-module instances only. Mother classes and validation live in audit.base.
"""

from __future__ import annotations

from pathlib import Path

from ...base import (
    Design,
    Material,
    Artifact,
    Tool,
    Agent,
    Workflow,
    WorkflowStep,
    Validator,
    CodeBinding,
    Gate,
    HistoryRef,
    MaterialFileSpec,
    ContractFamilySpec,
    MaterialFileInstance,
    MaterialInstance,
    ArtifactInstance,
    DogfoodFixtureSpec,
    ContractRefList,
    validate_ref_integrity as _base_validate,
    validate_capsule as _base_capsule,
    unresolved_code_binding_paths as _base_unresolved,
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

MODULE_DESIGN_DOC = "designDoc/temp/smoke/designDoc/research_20_technical_module_smoke_design.md"


# --- Upstream constraint Design refs ---

DESIGN_RESEARCH_TECHNICAL_SIGNAL_PIPELINE = Design(
    "design_research_technical_signal_pipeline",
    "designDoc/research_20_technical_signal_pipeline_v2.md",
)
DESIGN_MATERIAL_TECHNICAL_REPORT_CONTRACT = Design(
    "design_material_catalog_technical_report_contract",
    "designDoc/material_70_technical_report_contract.md",
)
DESIGN_RESEARCH_WRITER_PACKAGE_CONTRACT = Design(
    "design_research_writer_package_contract",
    "designDoc/research_00_writer_package_contract.md",
)
DESIGN_TIMESTAMP_SEMANTIC = Design(
    "design_the_timestamp_semantic",
    "designDoc/the_timestamp_semantic.md",
)
DESIGN_EXTERNAL_AGENT_MANAGEMENT = Design(
    "design_the_external_agent_management",
    "designDoc/the_external_agent_management.md",
)
DESIGN_ARTIFACT_GRAPH = Design(
    "design_the_artifact_graph",
    "designDoc/the_artifact_graph.md",
)


# --- Code bindings ---

CODE_BUILD_PACKETS = CodeBinding(
    "src/tools/build_asset_technical_reports.py::build_asset_technical_reports",
    "builds current technical signal packet artifacts",
)
CODE_RUNTIME_PAYLOADS = CodeBinding(
    "src/tools/asset_technical_runtime.py::compute_runtime_asset_payloads",
    "computes deterministic technical runtime payloads",
)
CODE_DRAFT_REPORTS = CodeBinding(
    "src/tools/draft_asset_technical_reports_with_deepseek.py::draft_asset_technical_reports",
    "runs writer package, external writer, report persistence, and fidelity pass",
)
CODE_WRITE_PACKAGE = CodeBinding(
    "src/tools/draft_asset_technical_reports_with_deepseek.py::_write_asset_writer_package",
    "writes the prompt input artifact consumed by the writer agent",
)
CODE_FIDELITY_FINDINGS = CodeBinding(
    "src/tools/draft_asset_technical_reports_with_deepseek.py::_build_deterministic_fidelity_findings",
    "builds deterministic report fidelity findings",
)
CODE_PARSE_FIDELITY = CodeBinding(
    "src/tools/draft_asset_technical_reports_with_deepseek.py::_parse_fidelity_findings",
    "parses writer or deterministic fidelity findings",
)
CODE_BUILD_INDEX = CodeBinding(
    "src/tools/build_asset_technical_index.py::build_asset_technical_index",
    "builds generated technical index artifacts",
)
CODE_WRITER_REQUEST = CodeBinding(
    "src/writers/models.py::WriterRequest",
    "shared external writer request object",
)
CODE_WRITER_SERVICE = CodeBinding(
    "src/writers/service.py::ExternalWriterService",
    "shared external writer execution service",
)


# --- Tools ---

TOOL_RESEARCH_TECHNICAL_SIGNAL_PACKET_BUILDER = Tool(
    "tool_research_technical_signal_packet_builder",
    "src/tools/build_asset_technical_reports.py",
    "atomic runtime handle that builds Research Technical signal packet artifacts",
    code_bindings=[CODE_BUILD_PACKETS, CODE_RUNTIME_PAYLOADS],
)
TOOL_RESEARCH_TECHNICAL_WRITER_PACKAGE_BUILDER = Tool(
    "tool_research_technical_writer_package_builder",
    "src/tools/draft_asset_technical_reports_with_deepseek.py",
    "atomic runtime handle that assembles the single writer package artifact",
    code_bindings=[CODE_WRITE_PACKAGE],
)
TOOL_RESEARCH_TECHNICAL_WRITER = Tool(
    "tool_research_technical_writer",
    "src/writers/service.py",
    "atomic writer runtime handle that transforms a writer package into a Technical Report",
    code_bindings=[CODE_WRITER_REQUEST, CODE_WRITER_SERVICE],
)
TOOL_RESEARCH_TECHNICAL_FIDELITY_CHECKER = Tool(
    "tool_research_technical_fidelity_checker",
    "src/tools/draft_asset_technical_reports_with_deepseek.py",
    "atomic checker for deterministic fidelity and reviewer-style findings",
    code_bindings=[CODE_FIDELITY_FINDINGS, CODE_PARSE_FIDELITY],
)
TOOL_RESEARCH_TECHNICAL_REVIEWER = Tool(
    "tool_research_technical_reviewer",
    "src/tools/draft_asset_technical_reports_with_deepseek.py",
    "atomic reviewer runtime handle that compares report claims to package support",
    code_bindings=[CODE_FIDELITY_FINDINGS, CODE_PARSE_FIDELITY],
)
TOOL_RESEARCH_TECHNICAL_INDEX_BUILDER = Tool(
    "tool_research_technical_index_builder",
    "src/tools/build_asset_technical_index.py",
    "atomic index builder for admitted Technical Report surfaces",
    code_bindings=[CODE_BUILD_INDEX],
)


# --- Gates ---

GATE_RESEARCH_TECHNICAL_SIGNAL_PACKET_READY = Gate(
    "gate_research_technical_signal_packet_ready",
    "signal packet artifact exists and carries timestamp semantic fields",
)
GATE_RESEARCH_TECHNICAL_WRITER_PACKAGE_READY = Gate(
    "gate_research_technical_writer_package_ready",
    "writer package artifact is ready for writer agent consumption",
)
GATE_RESEARCH_TECHNICAL_REVIEWER_PASSED = Gate(
    "gate_research_technical_reviewer_passed",
    "reviewer agent passed the report for downstream validation and indexing",
)
GATE_RESEARCH_TECHNICAL_REPORT_VALIDATED = Gate(
    "gate_research_technical_report_validated",
    "Technical Report passed deterministic validator or carries explicit warning override",
)
GATE_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION = Gate(
    "gate_research_technical_downstream_admission",
    "downstream consumers may use the report after reviewer and validator gates",
)
GATE_PM_ACKNOWLEDGEMENT = Gate(
    "gate_pm_acknowledgement",
    "PM-only belief or operation acknowledgement gate",
)


# --- History refs ---

HISTORY_ACTIVE_PIPELINE = HistoryRef(
    "designDoc/research_20_technical_signal_pipeline_v2.md",
    "current active technical pipeline design",
)
HISTORY_MATERIAL_REPORT = HistoryRef(
    "designDoc/material_70_technical_report_contract.md",
    "Technical Report Material owner",
)
HISTORY_SMOKE_DESIGN = HistoryRef(
    MODULE_DESIGN_DOC,
    "smoke reconstruction design",
)


# --- Materials ---

MATERIAL_RESEARCH_TECHNICAL_REPORT = Material(
    material_id="material_research_technical_report",
    owner_ref="designDoc/material_70_technical_report_contract.md",
    scope=(
        "PM-readable current market-state expression from technical inputs",
        "technical setup, key levels, confirmation, and invalidation prose",
        "conditional technical paths inside the report",
    ),
    file_parts=[
        MaterialFileSpec("read_content", "canonical PM-readable Technical Report markdown"),
        MaterialFileSpec("metadata", "optional report metadata sidecar", required=False),
        MaterialFileSpec("image", "optional chart or image attachment", required=False),
        MaterialFileSpec("archive_snapshot", "optional immutable archive snapshot", required=False),
    ],
    gates=[
        GATE_RESEARCH_TECHNICAL_REVIEWER_PASSED,
        GATE_RESEARCH_TECHNICAL_REPORT_VALIDATED,
    ],
    history_refs=[HISTORY_MATERIAL_REPORT],
)


# --- Artifacts ---

ARTIFACT_RESEARCH_TECHNICAL_PROFILES_CONFIG = Artifact(
    "artifact_research_technical_profiles_config",
    "data/knowledge/asset_technicals/profiles.json",
    "config_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET = Artifact(
    "artifact_research_technical_signal_packet",
    "data/knowledge/asset_technicals/signal_packets/<report_id>.md",
    "runtime_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_PAYLOAD = Artifact(
    "artifact_research_technical_signal_packet_payload",
    "data/knowledge/asset_technicals/signal_packets/<report_id>.json",
    "runtime_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE = Artifact(
    "artifact_research_technical_writer_package",
    "data/knowledge/asset_technicals/packages/<report_id>.package.md",
    "prompt_input_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_MANIFEST = Artifact(
    "artifact_research_technical_writer_package_manifest",
    "data/knowledge/asset_technicals/packages/<report_id>.package.manifest.json",
    "prompt_input_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_WRITER_PROMPT_PROJECTION = Artifact(
    "artifact_research_technical_writer_prompt_projection",
    "data/knowledge/asset_technicals/packages/<report_id>.writer.md",
    "prompt_input_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_WRITER_SIDECAR = Artifact(
    "artifact_research_technical_writer_sidecar",
    "<report>.writer.json",
    "sidecar_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_REVIEW_RESULT = Artifact(
    "artifact_research_technical_review_result",
    "reviewer output candidate",
    "audit_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_INDEX_ROW = Artifact(
    "artifact_research_technical_index_row",
    "data/knowledge/asset_technicals/index.json",
    "index_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_VALIDATION_RESULT = Artifact(
    "artifact_research_technical_signal_packet_validation_result",
    "validator output candidate",
    "audit_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_VALIDATION_RESULT = Artifact(
    "artifact_research_technical_writer_package_validation_result",
    "validator output candidate",
    "audit_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_REPORT_VALIDATION_RESULT = Artifact(
    "artifact_research_technical_report_validation_result",
    "validator output candidate",
    "audit_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION = Artifact(
    "artifact_research_technical_downstream_admission_result",
    "validator output candidate",
    "audit_artifact",
)
ARTIFACT_RESEARCH_TECHNICAL_WORKFLOW_RUN_RESULT = Artifact(
    "artifact_research_technical_workflow_run_result",
    MODULE_DESIGN_DOC,
    "audit_artifact",
)


# --- Validators ---

VALIDATOR_RESEARCH_TECHNICAL_SIGNAL_PACKET = Validator(
    validator_id="validator_research_technical_signal_packet",
    owner_ref=MODULE_DESIGN_DOC,
    input_refs=[
        ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET,
        ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_PAYLOAD,
        DESIGN_RESEARCH_TECHNICAL_SIGNAL_PIPELINE,
        DESIGN_TIMESTAMP_SEMANTIC,
    ],
    output_refs=[ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_VALIDATION_RESULT],
    code_bindings=[CODE_BUILD_PACKETS, CODE_RUNTIME_PAYLOADS],
    gates=[GATE_RESEARCH_TECHNICAL_SIGNAL_PACKET_READY],
    tool_refs=[TOOL_RESEARCH_TECHNICAL_SIGNAL_PACKET_BUILDER],
    history_refs=[HISTORY_ACTIVE_PIPELINE],
)
VALIDATOR_RESEARCH_TECHNICAL_WRITER_PACKAGE = Validator(
    validator_id="validator_research_technical_writer_package",
    owner_ref=MODULE_DESIGN_DOC,
    input_refs=[
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_MANIFEST,
        DESIGN_RESEARCH_WRITER_PACKAGE_CONTRACT,
    ],
    output_refs=[ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_VALIDATION_RESULT],
    code_bindings=[CODE_WRITE_PACKAGE],
    gates=[GATE_RESEARCH_TECHNICAL_WRITER_PACKAGE_READY],
    tool_refs=[TOOL_RESEARCH_TECHNICAL_WRITER_PACKAGE_BUILDER],
    history_refs=[HISTORY_SMOKE_DESIGN],
)
VALIDATOR_RESEARCH_TECHNICAL_REPORT = Validator(
    validator_id="validator_research_technical_report",
    owner_ref=MODULE_DESIGN_DOC,
    input_refs=[
        MATERIAL_RESEARCH_TECHNICAL_REPORT,
        ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET,
        ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_PAYLOAD,
        ARTIFACT_RESEARCH_TECHNICAL_REVIEW_RESULT,
        DESIGN_MATERIAL_TECHNICAL_REPORT_CONTRACT,
    ],
    output_refs=[ARTIFACT_RESEARCH_TECHNICAL_REPORT_VALIDATION_RESULT],
    code_bindings=[CODE_FIDELITY_FINDINGS, CODE_PARSE_FIDELITY],
    gates=[GATE_RESEARCH_TECHNICAL_REPORT_VALIDATED],
    tool_refs=[TOOL_RESEARCH_TECHNICAL_FIDELITY_CHECKER],
    history_refs=[HISTORY_MATERIAL_REPORT],
)
VALIDATOR_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION = Validator(
    validator_id="validator_research_technical_downstream_admission",
    owner_ref=MODULE_DESIGN_DOC,
    input_refs=[
        MATERIAL_RESEARCH_TECHNICAL_REPORT,
        ARTIFACT_RESEARCH_TECHNICAL_REVIEW_RESULT,
        ARTIFACT_RESEARCH_TECHNICAL_REPORT_VALIDATION_RESULT,
        ARTIFACT_RESEARCH_TECHNICAL_INDEX_ROW,
    ],
    output_refs=[ARTIFACT_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION],
    code_bindings=[CODE_BUILD_INDEX],
    gates=[GATE_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION],
    tool_refs=[TOOL_RESEARCH_TECHNICAL_INDEX_BUILDER],
    history_refs=[HISTORY_SMOKE_DESIGN],
)


# --- Agent ---

AGENT_RESEARCH_TECHNICAL_ANALYSIS = Agent(
    agent_id="agent_research_technical_analysis",
    owner_ref=".claude/skills/agent-research-technical-analysis/SKILL.md",
    role="goal-directed runtime actor that produces a passing Technical Report for a given ticker",
    objective="produce a passing Technical Report Material for a given ticker",
    state_refs=[
        ARTIFACT_RESEARCH_TECHNICAL_REVIEW_RESULT,
    ],
    policy=(
        "revision loop: after reviewer verdict, select one of three actions: "
        "(1) retry writer with same package if transient quality problem; "
        "(2) adjust package and retry writer if data insufficient for reviewer requirements; "
        "(3) escalate to PM if data fundamentally insufficient for this ticker"
    ),
    tool_refs=[
        TOOL_RESEARCH_TECHNICAL_SIGNAL_PACKET_BUILDER,
        TOOL_RESEARCH_TECHNICAL_WRITER_PACKAGE_BUILDER,
        TOOL_RESEARCH_TECHNICAL_WRITER,
        TOOL_RESEARCH_TECHNICAL_FIDELITY_CHECKER,
        TOOL_RESEARCH_TECHNICAL_REVIEWER,
        TOOL_RESEARCH_TECHNICAL_INDEX_BUILDER,
    ],
    input_refs=[
        ARTIFACT_RESEARCH_TECHNICAL_PROFILES_CONFIG,
        DESIGN_RESEARCH_TECHNICAL_SIGNAL_PIPELINE,
        DESIGN_RESEARCH_WRITER_PACKAGE_CONTRACT,
        DESIGN_TIMESTAMP_SEMANTIC,
    ],
    output_materials=[MATERIAL_RESEARCH_TECHNICAL_REPORT],
    output_artifacts=[
        ARTIFACT_RESEARCH_TECHNICAL_WORKFLOW_RUN_RESULT,
    ],
    gates=[
        GATE_RESEARCH_TECHNICAL_REVIEWER_PASSED,
        GATE_RESEARCH_TECHNICAL_REPORT_VALIDATED,
        GATE_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
    ],
    stop_condition="report passes review (proceed to validate and index), or max retries exhausted (escalate to PM)",
    history_refs=[HISTORY_SMOKE_DESIGN],
)


# --- Workflow ---

WORKFLOW_RESEARCH_TECHNICAL_ANALYSIS = Workflow(
    workflow_id="workflow_research_technical_analysis",
    owner_ref=MODULE_DESIGN_DOC,
    steps=[
        WorkflowStep(
            "build_research_technical_signal_packet_artifact",
            input_refs=[ARTIFACT_RESEARCH_TECHNICAL_PROFILES_CONFIG],
            output_refs=[
                ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET,
                ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_PAYLOAD,
            ],
            validator_refs=[VALIDATOR_RESEARCH_TECHNICAL_SIGNAL_PACKET],
            tool_refs=[TOOL_RESEARCH_TECHNICAL_SIGNAL_PACKET_BUILDER],
            code_bindings=[CODE_BUILD_PACKETS, CODE_RUNTIME_PAYLOADS],
        ),
        WorkflowStep(
            "build_research_technical_writer_package_artifact",
            input_refs=[
                ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET,
                ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_PAYLOAD,
                ARTIFACT_RESEARCH_TECHNICAL_PROFILES_CONFIG,
            ],
            output_refs=[
                ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE,
                ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_MANIFEST,
            ],
            validator_refs=[VALIDATOR_RESEARCH_TECHNICAL_WRITER_PACKAGE],
            tool_refs=[TOOL_RESEARCH_TECHNICAL_WRITER_PACKAGE_BUILDER],
            code_bindings=[CODE_WRITE_PACKAGE],
        ),
        WorkflowStep(
            "invoke_research_technical_writer",
            input_refs=[ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE],
            output_refs=[
                MATERIAL_RESEARCH_TECHNICAL_REPORT,
                ARTIFACT_RESEARCH_TECHNICAL_WRITER_PROMPT_PROJECTION,
                ARTIFACT_RESEARCH_TECHNICAL_WRITER_SIDECAR,
            ],
            tool_refs=[TOOL_RESEARCH_TECHNICAL_WRITER],
            code_bindings=[CODE_DRAFT_REPORTS, CODE_WRITER_SERVICE],
        ),
        WorkflowStep(
            "invoke_research_technical_reviewer",
            input_refs=[
                MATERIAL_RESEARCH_TECHNICAL_REPORT,
                ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE,
            ],
            output_refs=[ARTIFACT_RESEARCH_TECHNICAL_REVIEW_RESULT],
            tool_refs=[TOOL_RESEARCH_TECHNICAL_REVIEWER],
            code_bindings=[CODE_FIDELITY_FINDINGS, CODE_PARSE_FIDELITY],
        ),
        WorkflowStep(
            "validate_and_index_research_technical_report",
            input_refs=[
                MATERIAL_RESEARCH_TECHNICAL_REPORT,
                ARTIFACT_RESEARCH_TECHNICAL_REVIEW_RESULT,
            ],
            output_refs=[
                ARTIFACT_RESEARCH_TECHNICAL_REPORT_VALIDATION_RESULT,
                ARTIFACT_RESEARCH_TECHNICAL_INDEX_ROW,
                ARTIFACT_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
            ],
            validator_refs=[
                VALIDATOR_RESEARCH_TECHNICAL_REPORT,
                VALIDATOR_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
            ],
            code_bindings=[CODE_FIDELITY_FINDINGS, CODE_BUILD_INDEX],
            tool_refs=[
                TOOL_RESEARCH_TECHNICAL_FIDELITY_CHECKER,
                TOOL_RESEARCH_TECHNICAL_INDEX_BUILDER,
            ],
        ),
    ],
    input_refs=[
        DESIGN_RESEARCH_TECHNICAL_SIGNAL_PIPELINE,
        DESIGN_RESEARCH_WRITER_PACKAGE_CONTRACT,
        DESIGN_TIMESTAMP_SEMANTIC,
    ],
    output_refs=[
        ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET,
        ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_PAYLOAD,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_MANIFEST,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_PROMPT_PROJECTION,
        MATERIAL_RESEARCH_TECHNICAL_REPORT,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_SIDECAR,
        ARTIFACT_RESEARCH_TECHNICAL_REVIEW_RESULT,
        ARTIFACT_RESEARCH_TECHNICAL_INDEX_ROW,
        ARTIFACT_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
        ARTIFACT_RESEARCH_TECHNICAL_WORKFLOW_RUN_RESULT,
    ],
    tool_refs=[
        TOOL_RESEARCH_TECHNICAL_SIGNAL_PACKET_BUILDER,
        TOOL_RESEARCH_TECHNICAL_WRITER_PACKAGE_BUILDER,
        TOOL_RESEARCH_TECHNICAL_WRITER,
        TOOL_RESEARCH_TECHNICAL_FIDELITY_CHECKER,
        TOOL_RESEARCH_TECHNICAL_REVIEWER,
        TOOL_RESEARCH_TECHNICAL_INDEX_BUILDER,
    ],
    validator_refs=[
        VALIDATOR_RESEARCH_TECHNICAL_SIGNAL_PACKET,
        VALIDATOR_RESEARCH_TECHNICAL_WRITER_PACKAGE,
        VALIDATOR_RESEARCH_TECHNICAL_REPORT,
        VALIDATOR_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
    ],
    agent_refs=[AGENT_RESEARCH_TECHNICAL_ANALYSIS],
    code_bindings=[CODE_BUILD_PACKETS, CODE_DRAFT_REPORTS, CODE_BUILD_INDEX],
    gates=[
        GATE_RESEARCH_TECHNICAL_SIGNAL_PACKET_READY,
        GATE_RESEARCH_TECHNICAL_WRITER_PACKAGE_READY,
        GATE_RESEARCH_TECHNICAL_REPORT_VALIDATED,
        GATE_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
    ],
    history_refs=[HISTORY_SMOKE_DESIGN],
)


# --- Module Design ---

DESIGN_RESEARCH_TECHNICAL_MODULE = Design(
    design_id="design_research_technical_module",
    owner_ref=MODULE_DESIGN_DOC,
    purpose="rebuild Research Technical as typed Design, Material, Artifact, Tool, Workflow, and Validator objects",
    role="smoke parent design for technical artifacts, tools, writer and reviewer tools, workflow, Technical Report, validators, and index",
    scope=(
        "technical artifact generation",
        "writer tool behavior binding",
        "reviewer gate after writer output",
        "Technical Report material handoff",
        "validator and downstream admission artifacts",
    ),
    material_refs=[MATERIAL_RESEARCH_TECHNICAL_REPORT],
    artifact_refs=[
        ARTIFACT_RESEARCH_TECHNICAL_PROFILES_CONFIG,
        ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET,
        ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_PAYLOAD,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_MANIFEST,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_PROMPT_PROJECTION,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_SIDECAR,
        ARTIFACT_RESEARCH_TECHNICAL_REVIEW_RESULT,
        ARTIFACT_RESEARCH_TECHNICAL_INDEX_ROW,
        ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_VALIDATION_RESULT,
        ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_VALIDATION_RESULT,
        ARTIFACT_RESEARCH_TECHNICAL_REPORT_VALIDATION_RESULT,
        ARTIFACT_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
        ARTIFACT_RESEARCH_TECHNICAL_WORKFLOW_RUN_RESULT,
    ],
    tool_refs=[
        TOOL_RESEARCH_TECHNICAL_SIGNAL_PACKET_BUILDER,
        TOOL_RESEARCH_TECHNICAL_WRITER_PACKAGE_BUILDER,
        TOOL_RESEARCH_TECHNICAL_WRITER,
        TOOL_RESEARCH_TECHNICAL_FIDELITY_CHECKER,
        TOOL_RESEARCH_TECHNICAL_REVIEWER,
        TOOL_RESEARCH_TECHNICAL_INDEX_BUILDER,
    ],
    agent_refs=[AGENT_RESEARCH_TECHNICAL_ANALYSIS],
    workflow_refs=[WORKFLOW_RESEARCH_TECHNICAL_ANALYSIS],
    validator_refs=[
        VALIDATOR_RESEARCH_TECHNICAL_SIGNAL_PACKET,
        VALIDATOR_RESEARCH_TECHNICAL_WRITER_PACKAGE,
        VALIDATOR_RESEARCH_TECHNICAL_REPORT,
        VALIDATOR_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
    ],
    code_bindings=[CODE_BUILD_PACKETS, CODE_DRAFT_REPORTS, CODE_BUILD_INDEX],
    gates=[
        GATE_RESEARCH_TECHNICAL_SIGNAL_PACKET_READY,
        GATE_RESEARCH_TECHNICAL_WRITER_PACKAGE_READY,
        GATE_RESEARCH_TECHNICAL_REVIEWER_PASSED,
        GATE_RESEARCH_TECHNICAL_REPORT_VALIDATED,
        GATE_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
    ],
    history_refs=[HISTORY_SMOKE_DESIGN, HISTORY_ACTIVE_PIPELINE],
)


# --- Family spec ---

TECHNICAL_SMOKE_FAMILY = ContractFamilySpec(
    family_id="research_technical_smoke",
    status="temp_smoke",
    canonical_owner_candidates=[DESIGN_RESEARCH_TECHNICAL_MODULE],
    upstream_constraints=[
        DESIGN_RESEARCH_TECHNICAL_SIGNAL_PIPELINE,
        DESIGN_MATERIAL_TECHNICAL_REPORT_CONTRACT,
        DESIGN_RESEARCH_WRITER_PACKAGE_CONTRACT,
        DESIGN_TIMESTAMP_SEMANTIC,
        DESIGN_EXTERNAL_AGENT_MANAGEMENT,
        DESIGN_ARTIFACT_GRAPH,
    ],
    core_classes=(Design, Material, Artifact, Tool, Agent, Workflow, Validator),
    field_types=(
        ContractRefList,
    ),
    blocked_names=(
        "technical_lens_contract",
        "object_model_contract",
        "runtime_surface_contract",
        "prompt_surface_contract",
        "artifact_signal_packet",
        "artifact_writer_package",
        "agent_writer_asset_technical",
        "workflow_technical_analysis",
        "tool_research_technical_external_writer_service",
    ),
)


# --- All registered objects ---

TECHNICAL_CONTRACT_OBJECTS: ContractRefList = [
    DESIGN_RESEARCH_TECHNICAL_MODULE,
    DESIGN_RESEARCH_TECHNICAL_SIGNAL_PIPELINE,
    DESIGN_MATERIAL_TECHNICAL_REPORT_CONTRACT,
    DESIGN_RESEARCH_WRITER_PACKAGE_CONTRACT,
    DESIGN_TIMESTAMP_SEMANTIC,
    DESIGN_EXTERNAL_AGENT_MANAGEMENT,
    DESIGN_ARTIFACT_GRAPH,
    MATERIAL_RESEARCH_TECHNICAL_REPORT,
    ARTIFACT_RESEARCH_TECHNICAL_PROFILES_CONFIG,
    ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET,
    ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_PAYLOAD,
    ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE,
    ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_MANIFEST,
    ARTIFACT_RESEARCH_TECHNICAL_WRITER_PROMPT_PROJECTION,
    ARTIFACT_RESEARCH_TECHNICAL_WRITER_SIDECAR,
    ARTIFACT_RESEARCH_TECHNICAL_REVIEW_RESULT,
    ARTIFACT_RESEARCH_TECHNICAL_INDEX_ROW,
    ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_VALIDATION_RESULT,
    ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_VALIDATION_RESULT,
    ARTIFACT_RESEARCH_TECHNICAL_REPORT_VALIDATION_RESULT,
    ARTIFACT_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
    ARTIFACT_RESEARCH_TECHNICAL_WORKFLOW_RUN_RESULT,
    TOOL_RESEARCH_TECHNICAL_SIGNAL_PACKET_BUILDER,
    TOOL_RESEARCH_TECHNICAL_WRITER_PACKAGE_BUILDER,
    TOOL_RESEARCH_TECHNICAL_WRITER,
    TOOL_RESEARCH_TECHNICAL_FIDELITY_CHECKER,
    TOOL_RESEARCH_TECHNICAL_REVIEWER,
    TOOL_RESEARCH_TECHNICAL_INDEX_BUILDER,
    AGENT_RESEARCH_TECHNICAL_ANALYSIS,
    WORKFLOW_RESEARCH_TECHNICAL_ANALYSIS,
    VALIDATOR_RESEARCH_TECHNICAL_SIGNAL_PACKET,
    VALIDATOR_RESEARCH_TECHNICAL_WRITER_PACKAGE,
    VALIDATOR_RESEARCH_TECHNICAL_REPORT,
    VALIDATOR_RESEARCH_TECHNICAL_DOWNSTREAM_ADMISSION,
]


# --- Dogfood fixture ---

FUTURE_ES_2026_04_20_FIXTURE = DogfoodFixtureSpec(
    fixture_id="future_es_2026_04_20",
    asset_id="/ES",
    report_id="future_es",
    session_date_market="2026-04-20",
    material_instances=[
        MaterialInstance(
            material_ref=MATERIAL_RESEARCH_TECHNICAL_REPORT,
            file_instances=[
                MaterialFileInstance("read_content", "data/knowledge/asset_technicals/reports/future_es.md"),
                MaterialFileInstance(
                    "archive_snapshot",
                    "data/archive/asset_technicals/future_es/future_es_2026-04-20.md",
                ),
            ],
        )
    ],
    artifact_instances=[
        ArtifactInstance(
            ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET,
            "data/knowledge/asset_technicals/signal_packets/future_es.md",
        ),
        ArtifactInstance(
            ARTIFACT_RESEARCH_TECHNICAL_SIGNAL_PACKET_PAYLOAD,
            "data/knowledge/asset_technicals/signal_packets/future_es.json",
        ),
        ArtifactInstance(
            ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE,
            "data/knowledge/asset_technicals/packages/future_es.package.md",
        ),
        ArtifactInstance(
            ARTIFACT_RESEARCH_TECHNICAL_WRITER_PACKAGE_MANIFEST,
            "data/knowledge/asset_technicals/packages/future_es.package.manifest.json",
        ),
        ArtifactInstance(
            ARTIFACT_RESEARCH_TECHNICAL_WRITER_PROMPT_PROJECTION,
            "data/knowledge/asset_technicals/packages/future_es.writer.md",
        ),
    ],
)


# --- Convenience wrappers ---

def validate() -> list[str]:
    return _base_validate(
        TECHNICAL_CONTRACT_OBJECTS,
        TECHNICAL_SMOKE_FAMILY,
        [FUTURE_ES_2026_04_20_FIXTURE],
        PROJECT_ROOT,
    )


def unresolved_bindings() -> list[str]:
    return _base_unresolved(TECHNICAL_CONTRACT_OBJECTS, PROJECT_ROOT)


def validate_capsule() -> list[str]:
    return _base_capsule(MODULE_DESIGN_DOC, PROJECT_ROOT)


__all__ = [
    "TECHNICAL_SMOKE_FAMILY",
    "TECHNICAL_CONTRACT_OBJECTS",
    "FUTURE_ES_2026_04_20_FIXTURE",
    "DESIGN_RESEARCH_TECHNICAL_MODULE",
    "AGENT_RESEARCH_TECHNICAL_ANALYSIS",
    "WORKFLOW_RESEARCH_TECHNICAL_ANALYSIS",
    "validate",
    "validate_capsule",
    "unresolved_bindings",
]
