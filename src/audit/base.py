"""Contract audit base classes and validation.

Defines the eight mother classes, type aliases, support classes,
and parametrized structural validation shared across all modules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias

import yaml


ArtifactKind: TypeAlias = Literal[
    "config_artifact",
    "runtime_artifact",
    "prompt_input_artifact",
    "sidecar_artifact",
    "index_artifact",
    "audit_artifact",
]
MaterialFileRole: TypeAlias = Literal[
    "read_content",
    "raw_content",
    "image",
    "metadata",
    "archive_snapshot",
]
ALLOWED_MATERIAL_FILE_ROLES: tuple[str, ...] = (
    "read_content",
    "raw_content",
    "image",
    "metadata",
    "archive_snapshot",
)


@dataclass(frozen=True)
class CodeBinding:
    ref: str
    meaning: str


@dataclass(frozen=True)
class Gate:
    gate_id: str
    meaning: str


@dataclass(frozen=True)
class HistoryRef:
    ref: str
    meaning: str = ""


@dataclass(frozen=True)
class MaterialFileSpec:
    role: MaterialFileRole
    meaning: str
    required: bool = True


MaterialFileSpecList: TypeAlias = list[MaterialFileSpec]


@dataclass(frozen=True)
class Design:
    design_id: str
    owner_ref: str
    purpose: str = ""
    role: str = ""
    scope: tuple[str, ...] = ()
    core_design_principle: str = ""
    material_refs: MaterialRefList = field(default_factory=list)
    artifact_refs: ArtifactRefList = field(default_factory=list)
    tool_refs: ToolRefList = field(default_factory=list)
    skill_refs: SkillRefList = field(default_factory=list)
    agent_refs: AgentRefList = field(default_factory=list)
    workflow_refs: WorkflowRefList = field(default_factory=list)
    validator_refs: ValidatorRefList = field(default_factory=list)
    code_bindings: CodeBindingList = field(default_factory=list)
    gates: GateRefList = field(default_factory=list)
    history_refs: HistoryRefList = field(default_factory=list)


@dataclass(frozen=True)
class Material:
    material_id: str
    owner_ref: str
    scope: tuple[str, ...]
    file_parts: MaterialFileSpecList = field(default_factory=list)
    gates: GateRefList = field(default_factory=list)
    history_refs: HistoryRefList = field(default_factory=list)


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    owner_ref: str
    artifact_kind: ArtifactKind
    history_refs: HistoryRefList = field(default_factory=list)


@dataclass(frozen=True)
class Tool:
    tool_id: str
    owner_ref: str
    purpose: str
    code_bindings: CodeBindingList = field(default_factory=list)
    history_refs: HistoryRefList = field(default_factory=list)


@dataclass(frozen=True)
class Skill:
    skill_id: str
    runtime: str
    projection_path: str
    purpose: str = ""
    input_refs: ContractRefList = field(default_factory=list)
    output_materials: MaterialRefList = field(default_factory=list)
    output_artifacts: ArtifactRefList = field(default_factory=list)
    tool_refs: ToolRefList = field(default_factory=list)
    required_contract_refs: DesignRefList = field(default_factory=list)
    gates: GateRefList = field(default_factory=list)


@dataclass(frozen=True)
class Agent:
    agent_id: str
    owner_ref: str
    role: str
    objective: str = ""
    state_refs: ContractRefList = field(default_factory=list)
    policy: str = ""
    skill_refs: SkillRefList = field(default_factory=list)
    tool_refs: ToolRefList = field(default_factory=list)
    input_refs: ContractRefList = field(default_factory=list)
    output_materials: MaterialRefList = field(default_factory=list)
    output_artifacts: ArtifactRefList = field(default_factory=list)
    code_bindings: CodeBindingList = field(default_factory=list)
    gates: GateRefList = field(default_factory=list)
    stop_condition: str = ""
    history_refs: HistoryRefList = field(default_factory=list)


@dataclass(frozen=True)
class WorkflowStep:
    step_id: str
    input_refs: ContractRefList = field(default_factory=list)
    output_refs: ContractRefList = field(default_factory=list)
    agent_refs: AgentRefList = field(default_factory=list)
    tool_refs: ToolRefList = field(default_factory=list)
    validator_refs: ValidatorRefList = field(default_factory=list)
    gates: GateRefList = field(default_factory=list)
    code_bindings: CodeBindingList = field(default_factory=list)


@dataclass(frozen=True)
class Workflow:
    workflow_id: str
    owner_ref: str
    steps: WorkflowStepList = field(default_factory=list)
    input_refs: ContractRefList = field(default_factory=list)
    output_refs: ContractRefList = field(default_factory=list)
    agent_refs: AgentRefList = field(default_factory=list)
    tool_refs: ToolRefList = field(default_factory=list)
    validator_refs: ValidatorRefList = field(default_factory=list)
    code_bindings: CodeBindingList = field(default_factory=list)
    gates: GateRefList = field(default_factory=list)
    history_refs: HistoryRefList = field(default_factory=list)


@dataclass(frozen=True)
class Validator:
    validator_id: str
    owner_ref: str
    input_refs: ContractRefList
    output_refs: ArtifactRefList
    code_bindings: CodeBindingList
    gates: GateRefList
    agent_refs: AgentRefList = field(default_factory=list)
    tool_refs: ToolRefList = field(default_factory=list)
    history_refs: HistoryRefList = field(default_factory=list)


ContractRef: TypeAlias = Design | Material | Artifact | Tool | Skill | Agent | Workflow | Validator
ContractRefList: TypeAlias = list[ContractRef]
DesignRefList: TypeAlias = list[Design]
MaterialRefList: TypeAlias = list[Material]
ArtifactRefList: TypeAlias = list[Artifact]
ToolRefList: TypeAlias = list[Tool]
SkillRefList: TypeAlias = list[Skill]
AgentRefList: TypeAlias = list[Agent]
WorkflowRefList: TypeAlias = list[Workflow]
ValidatorRefList: TypeAlias = list[Validator]
CodeBindingList: TypeAlias = list[CodeBinding]
GateRefList: TypeAlias = list[Gate]
HistoryRefList: TypeAlias = list[HistoryRef]
WorkflowStepList: TypeAlias = list[WorkflowStep]


@dataclass(frozen=True)
class ContractFamilySpec:
    family_id: str
    status: str
    canonical_owner_candidates: DesignRefList
    upstream_constraints: DesignRefList
    core_classes: tuple[type, ...]
    field_types: tuple[object, ...]
    blocked_names: tuple[str, ...]


@dataclass(frozen=True)
class MaterialFileInstance:
    role: MaterialFileRole
    instance_ref: str


@dataclass(frozen=True)
class MaterialInstance:
    material_ref: Material
    file_instances: list[MaterialFileInstance]


@dataclass(frozen=True)
class ArtifactInstance:
    artifact_ref: Artifact
    instance_ref: str


@dataclass(frozen=True)
class DogfoodFixtureSpec:
    fixture_id: str
    asset_id: str
    report_id: str
    session_date_market: str
    material_instances: list[MaterialInstance]
    artifact_instances: list[ArtifactInstance]


CAPSULE_REQUIRED_FIELDS: tuple[str, ...] = (
    "title",
    "status",
    "layer",
    "canonical_owner",
)

CAPSULE_RECOVERABLE_FIELDS: tuple[str, ...] = (
    "title",
    "status",
    "layer",
    "canonical_owner",
    "registry_path",
    "reader_persona",
    "reader_decision",
    "upstream_refs",
    "downstream_refs",
)

CAPSULE_PATH_FIELDS: tuple[str, ...] = (
    "canonical_owner",
    "registry_path",
)

CAPSULE_PATH_LIST_FIELDS: tuple[str, ...] = (
    "upstream_refs",
    "downstream_refs",
)

CAPSULE_VALID_STATUSES: tuple[str, ...] = (
    "proposal",
    "active_draft",
    "active",
    "smoke_design",
    "deprecated",
    "archived",
)


def _extract_capsule_yaml(doc_text: str) -> dict | None:
    """Extract the first YAML code block from a markdown design doc."""
    pattern = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL)
    for m in pattern.finditer(doc_text):
        block = m.group(1)
        lines = [ln for ln in block.splitlines() if not ln.strip().startswith("#")]
        cleaned = "\n".join(lines)
        try:
            parsed = yaml.safe_load(cleaned)
            if isinstance(parsed, dict) and "canonical_owner" in parsed:
                return parsed
        except yaml.YAMLError:
            continue
    return None


def validate_capsule(
    design_doc_path: str,
    project_root: Path,
) -> list[str]:
    """Layer 1: validate Contract Capsule in a design doc. Returns list of errors."""
    errors: list[str] = []
    full_path = project_root / design_doc_path

    if not full_path.exists():
        errors.append(f"design doc not found: {design_doc_path}")
        return errors

    doc_text = full_path.read_text(encoding="utf-8")
    capsule = _extract_capsule_yaml(doc_text)

    if capsule is None:
        errors.append(f"no Contract Capsule YAML block found in {design_doc_path}")
        return errors

    for field_name in CAPSULE_REQUIRED_FIELDS:
        if field_name not in capsule or not capsule[field_name]:
            errors.append(f"capsule missing required field: {field_name}")

    status = capsule.get("status", "")
    if status and status not in CAPSULE_VALID_STATUSES:
        errors.append(f"capsule status '{status}' not in valid set: {CAPSULE_VALID_STATUSES}")

    canonical = capsule.get("canonical_owner", "")
    if canonical and canonical != design_doc_path:
        errors.append(
            f"capsule canonical_owner '{canonical}' does not match "
            f"actual path '{design_doc_path}'"
        )

    for field_name in CAPSULE_PATH_FIELDS:
        path_val = capsule.get(field_name, "")
        if path_val and not (project_root / path_val).exists():
            errors.append(f"capsule {field_name} path not found: {path_val}")

    for field_name in CAPSULE_PATH_LIST_FIELDS:
        path_list = capsule.get(field_name, []) or []
        if not isinstance(path_list, list):
            errors.append(f"capsule {field_name}: expected list, got {type(path_list).__name__}")
            continue
        for path_val in path_list:
            if path_val and not (project_root / path_val).exists():
                errors.append(f"capsule {field_name} path not found: {path_val}")

    return errors


def validate_ref_integrity(
    objects: ContractRefList,
    family: ContractFamilySpec,
    fixtures: list[DogfoodFixtureSpec],
    project_root: Path,
) -> list[str]:
    """Return registry shape errors without touching production files."""
    errors: list[str] = []

    for obj in objects:
        if isinstance(obj, Design):
            _check_class_id("Design.design_id", obj.design_id, "design_", errors)
            _check_owner_ref("Design.owner_ref", obj.owner_ref, project_root, errors)
            _check_list("Design.material_refs", obj.material_refs, Material, errors)
            _check_list("Design.artifact_refs", obj.artifact_refs, Artifact, errors)
            _check_list("Design.tool_refs", obj.tool_refs, Tool, errors)
            _check_list("Design.skill_refs", obj.skill_refs, Skill, errors)
            _check_list("Design.agent_refs", obj.agent_refs, Agent, errors)
            _check_list("Design.workflow_refs", obj.workflow_refs, Workflow, errors)
            _check_list("Design.validator_refs", obj.validator_refs, Validator, errors)
        elif isinstance(obj, Agent):
            _check_class_id("Agent.agent_id", obj.agent_id, "agent_", errors)
            _check_owner_ref("Agent.owner_ref", obj.owner_ref, project_root, errors)
            _check_list("Agent.state_refs", obj.state_refs, (Design, Material, Artifact, Skill, Agent, Workflow, Validator), errors)
            _check_list("Agent.skill_refs", obj.skill_refs, Skill, errors)
            _check_list("Agent.tool_refs", obj.tool_refs, Tool, errors)
            _check_list("Agent.input_refs", obj.input_refs, (Design, Material, Artifact, Skill, Agent, Workflow, Validator), errors)
            _check_list("Agent.output_materials", obj.output_materials, Material, errors)
            _check_list("Agent.output_artifacts", obj.output_artifacts, Artifact, errors)
        elif isinstance(obj, Workflow):
            _check_class_id("Workflow.workflow_id", obj.workflow_id, "workflow_", errors)
            _check_owner_ref("Workflow.owner_ref", obj.owner_ref, project_root, errors)
            _check_list("Workflow.steps", obj.steps, WorkflowStep, errors)
            _check_list("Workflow.agent_refs", obj.agent_refs, Agent, errors)
            _check_list("Workflow.tool_refs", obj.tool_refs, Tool, errors)
            _check_list("Workflow.validator_refs", obj.validator_refs, Validator, errors)
            for step in obj.steps:
                _check_list(f"WorkflowStep[{step.step_id}].agent_refs", step.agent_refs, Agent, errors)
                _check_list(f"WorkflowStep[{step.step_id}].tool_refs", step.tool_refs, Tool, errors)
                _check_list(f"WorkflowStep[{step.step_id}].validator_refs", step.validator_refs, Validator, errors)
                _check_list(f"WorkflowStep[{step.step_id}].gates", step.gates, Gate, errors)
        elif isinstance(obj, Validator):
            _check_class_id("Validator.validator_id", obj.validator_id, "validator_", errors)
            _check_owner_ref("Validator.owner_ref", obj.owner_ref, project_root, errors)
            _check_list("Validator.output_refs", obj.output_refs, Artifact, errors)
            _check_list("Validator.agent_refs", obj.agent_refs, Agent, errors)
            _check_list("Validator.tool_refs", obj.tool_refs, Tool, errors)
        elif isinstance(obj, Material):
            _check_class_id("Material.material_id", obj.material_id, "material_", errors)
            _check_list("Material.file_parts", obj.file_parts, MaterialFileSpec, errors)
            for part in obj.file_parts:
                if part.role not in ALLOWED_MATERIAL_FILE_ROLES:
                    errors.append(f"{obj.material_id}: unknown material file part role {part.role}")
            if hasattr(obj, "input_refs") or hasattr(obj, "output_refs"):
                errors.append(f"{obj.material_id}: Material must not define input_refs or output_refs")
        elif isinstance(obj, Artifact):
            _check_class_id("Artifact.artifact_id", obj.artifact_id, "artifact_", errors)
        elif isinstance(obj, Tool):
            _check_class_id("Tool.tool_id", obj.tool_id, "tool_", errors)
            _check_owner_ref("Tool.owner_ref", obj.owner_ref, project_root, errors)
            _check_list("Tool.code_bindings", obj.code_bindings, CodeBinding, errors)
        elif isinstance(obj, Skill):
            _check_class_id("Skill.skill_id", obj.skill_id, "skill_", errors)
            if not obj.projection_path.endswith("SKILL.md"):
                errors.append(f"{obj.skill_id}: Skill projection must point to SKILL.md")
            _check_owner_ref("Skill.projection_path", obj.projection_path, project_root, errors)
            _check_list("Skill.input_refs", obj.input_refs, (Design, Material, Artifact, Skill, Agent, Workflow, Validator), errors)
            _check_list("Skill.output_materials", obj.output_materials, Material, errors)
            _check_list("Skill.output_artifacts", obj.output_artifacts, Artifact, errors)
            _check_list("Skill.tool_refs", obj.tool_refs, Tool, errors)
            _check_list("Skill.required_contract_refs", obj.required_contract_refs, Design, errors)
            _check_list("Skill.gates", obj.gates, Gate, errors)
            for ref in obj.required_contract_refs:
                _check_owner_ref(
                    f"Skill.required_contract_refs[{ref.design_id}]",
                    ref.owner_ref,
                    project_root,
                    errors,
                )
        else:
            errors.append(f"Unknown contract object type: {type(obj).__name__}")

    _check_blocked_names(objects, family, errors)
    for fixture in fixtures:
        _check_fixture_material_parts(fixture, errors)
    return errors


def unresolved_code_binding_paths(
    objects: ContractRefList,
    project_root: Path,
) -> list[str]:
    """Return file paths from CodeBinding refs that do not exist."""
    missing: list[str] = []
    for binding in _all_code_bindings(objects):
        path_part = binding.ref.split("::", 1)[0]
        if not (project_root / path_part).exists():
            missing.append(binding.ref)
    return sorted(set(missing))


def _check_owner_ref(name: str, value: str, project_root: Path, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{name}: expected non-empty path string")
        return
    if not (project_root / value).exists():
        errors.append(f"{name}: missing path {value}")


def _check_class_id(name: str, value: str, prefix: str, errors: list[str]) -> None:
    if not value.startswith(prefix):
        errors.append(f"{name}: expected {prefix}* id, got {value}")


def _check_blocked_names(
    objects: ContractRefList,
    family: ContractFamilySpec,
    errors: list[str],
) -> None:
    object_ids = [
        getattr(obj, "design_id", None)
        or getattr(obj, "material_id", None)
        or getattr(obj, "artifact_id", None)
        or getattr(obj, "skill_id", None)
        or getattr(obj, "agent_id", None)
        or getattr(obj, "workflow_id", None)
        or getattr(obj, "validator_id", None)
        for obj in objects
    ]
    for blocked_name in family.blocked_names:
        if blocked_name in object_ids:
            errors.append(f"{blocked_name}: blocked ad hoc or superseded class id is still registered")


def _check_fixture_material_parts(fixture: DogfoodFixtureSpec, errors: list[str]) -> None:
    for material_instance in fixture.material_instances:
        declared_roles = {part.role for part in material_instance.material_ref.file_parts}
        instance_roles = {file_instance.role for file_instance in material_instance.file_instances}
        for file_instance in material_instance.file_instances:
            if file_instance.role not in declared_roles:
                errors.append(
                    f"{fixture.fixture_id}: {material_instance.material_ref.material_id} "
                    f"uses undeclared file part role {file_instance.role}"
                )
        required_roles = {
            part.role for part in material_instance.material_ref.file_parts if part.required
        }
        missing_roles = sorted(required_roles - instance_roles)
        if missing_roles:
            errors.append(
                f"{fixture.fixture_id}: {material_instance.material_ref.material_id} "
                f"missing required file parts {missing_roles}"
            )


def contract_ref_ids(refs: list[object]) -> list[str]:
    result: list[str] = []
    for ref in refs:
        for attr in (
            "design_id",
            "material_id",
            "artifact_id",
            "tool_id",
            "skill_id",
            "agent_id",
            "workflow_id",
            "validator_id",
            "gate_id",
        ):
            value = getattr(ref, attr, None)
            if value:
                result.append(value)
                break
    return result


def _check_list(name: str, values: object, expected_type: type | tuple[type, ...], errors: list[str]) -> None:
    if not isinstance(values, list):
        errors.append(f"{name}: expected list, got {type(values).__name__}")
        return
    expected_name = _type_name(expected_type)
    for value in values:
        if not isinstance(value, expected_type):
            errors.append(f"{name}: expected {expected_name}, got {type(value).__name__}")


def _type_name(expected_type: type | tuple[type, ...]) -> str:
    if isinstance(expected_type, tuple):
        return " | ".join(item.__name__ for item in expected_type)
    return expected_type.__name__


def _all_code_bindings(objects: ContractRefList) -> list[CodeBinding]:
    seen: dict[str, CodeBinding] = {}
    for obj in objects:
        for binding in getattr(obj, "code_bindings", []):
            seen[binding.ref] = binding
        if isinstance(obj, Workflow):
            for step in obj.steps:
                for binding in step.code_bindings:
                    seen[binding.ref] = binding
    return list(seen.values())
