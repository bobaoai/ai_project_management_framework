#!/usr/bin/env python3
"""DDM-owned Design artifact validation and Reviewer checklist projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ERROR_CODE = "DESIGN_REPRESENTATION_INCOMPLETE"
CONTRACT_PATH = Path(__file__).with_suffix(".json")
_H2_PATTERN = re.compile(r"^##[ \t]+(\d+)\.[ \t]+(.+?)[ \t]*$", re.MULTILINE)
_H3_PATTERN = re.compile(r"^###[ \t]+(\d+\.\d+)[ \t]+(.+?)[ \t]*$", re.MULTILINE)
_PLACEHOLDERS = {"todo", "tbd", "placeholder", "待补充", "待定"}


class DesignArtifactContractError(ValueError):
    """Raised when a Design artifact cannot satisfy the DDM representation."""

    code = ERROR_CODE


@dataclass(frozen=True)
class DesignArtifactValidationResult:
    subject_sha256: str
    layer: str
    headings: tuple[str, ...]
    validator_ids: tuple[str, ...]


def _require_exact_keys(value: dict[str, Any], expected: set[str], context: str) -> None:
    actual = set(value)
    if actual != expected:
        raise DesignArtifactContractError(
            f"{context} keys mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DesignArtifactContractError(f"cannot read Design artifact contract: {path}") from exc
    if not isinstance(contract, dict):
        raise DesignArtifactContractError("Design artifact contract root must be an object")
    _require_exact_keys(
        contract,
        {
            "$id",
            "contract_version",
            "artifact_contract_id",
            "owner_t0_layer_id",
            "artifact_kind",
            "layers",
            "optional_sections",
            "reviewer_checklist",
        },
        "contract",
    )
    if contract["contract_version"] != "design_artifact_contract_v2":
        raise DesignArtifactContractError("unsupported Design artifact contract version")
    if contract["owner_t0_layer_id"] != "the_design_doc_management":
        raise DesignArtifactContractError("Design artifact contract owner mismatch")
    layers = contract["layers"]
    if not isinstance(layers, dict) or set(layers) != {"charter", "t0", "t1", "t2"}:
        raise DesignArtifactContractError("Design artifact contract must define charter, t0, t1, and t2")
    for layer_id, layer in layers.items():
        if not isinstance(layer, dict):
            raise DesignArtifactContractError(f"layers.{layer_id} must be an object")
        _require_exact_keys(
            layer,
            {"layer_value", "protected_headings", "extension_slot"},
            f"layers.{layer_id}",
        )
        headings = layer["protected_headings"]
        if (
            not isinstance(headings, list)
            or not headings
            or any(not isinstance(item, str) or not item for item in headings)
            or len(set(headings)) != len(headings)
        ):
            raise DesignArtifactContractError(f"layers.{layer_id}.protected_headings is invalid")
        slot = layer["extension_slot"]
        if not isinstance(slot, dict):
            raise DesignArtifactContractError(f"layers.{layer_id}.extension_slot must be an object")
        _require_exact_keys(slot, {"after", "before"}, f"layers.{layer_id}.extension_slot")
        if slot["after"] not in headings or slot["before"] not in headings:
            raise DesignArtifactContractError(f"layers.{layer_id}.extension_slot is unresolved")
        if headings.index(slot["after"]) + 1 != headings.index(slot["before"]):
            raise DesignArtifactContractError(f"layers.{layer_id}.extension_slot bounds must be adjacent")
    optional_sections = contract["optional_sections"]
    if not isinstance(optional_sections, list) or len(optional_sections) != 1:
        raise DesignArtifactContractError(
            "Design artifact contract must define one optional section"
        )
    optional = optional_sections[0]
    if not isinstance(optional, dict):
        raise DesignArtifactContractError("optional_sections[0] must be an object")
    _require_exact_keys(
        optional,
        {"heading", "placement", "required_subsections"},
        "optional_sections[0]",
    )
    if optional["heading"] != "审查与完成" or optional["placement"] != "extension_slot_last":
        raise DesignArtifactContractError("optional review-completion section identity is invalid")
    if optional["required_subsections"] != [
        "确定性检查",
        "语义审查",
        "表达审查",
        "完成条件",
    ]:
        raise DesignArtifactContractError(
            "optional review-completion subsection contract is invalid"
        )
    _validated_checklist(contract["reviewer_checklist"])
    return contract


def _validated_checklist(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesignArtifactContractError("reviewer_checklist must be an object")
    _require_exact_keys(
        value,
        {"resource_id", "intro_lines", "columns", "checks", "outro_lines"},
        "reviewer_checklist",
    )
    if value["resource_id"] != "t0:design_contract_review_checklist":
        raise DesignArtifactContractError("Design checklist resource identity mismatch")
    columns = value["columns"]
    if columns != ["顺序", "`check_id`", "必须确定的结果", "`finding_class`"]:
        raise DesignArtifactContractError("Design checklist columns mismatch")
    for field in ("intro_lines", "outro_lines"):
        lines = value[field]
        if not isinstance(lines, list) or any(not isinstance(line, str) or not line for line in lines):
            raise DesignArtifactContractError(f"reviewer_checklist.{field} is invalid")
    checks = value["checks"]
    if not isinstance(checks, list) or len(checks) != 11:
        raise DesignArtifactContractError("Design checklist must contain exactly eleven checks")
    check_ids: list[str] = []
    finding_classes: list[str] = []
    for index, check in enumerate(checks, start=1):
        if not isinstance(check, dict):
            raise DesignArtifactContractError(f"reviewer_checklist.checks[{index - 1}] must be an object")
        _require_exact_keys(
            check,
            {"order", "check_id", "required_result", "finding_class", "stage"},
            f"reviewer_checklist.checks[{index - 1}]",
        )
        if check["order"] != index:
            raise DesignArtifactContractError("Design checklist order is not continuous")
        if check["stage"] != ("prose" if index == 11 else "semantic"):
            raise DesignArtifactContractError("Design checklist stage boundary is invalid")
        for field in ("check_id", "required_result", "finding_class"):
            if not isinstance(check[field], str) or not check[field]:
                raise DesignArtifactContractError(f"Design checklist {field} must be non-empty")
        check_ids.append(check["check_id"])
        finding_classes.append(check["finding_class"])
    if len(set(check_ids)) != len(check_ids) or len(set(finding_classes)) != len(finding_classes):
        raise DesignArtifactContractError("Design checklist identities must be unique")
    return value


def render_reviewer_checklist(contract_path: Path = CONTRACT_PATH) -> bytes:
    checklist = _validated_checklist(load_contract(contract_path)["reviewer_checklist"])
    lines = [*checklist["intro_lines"], ""]
    lines.append("| " + " | ".join(checklist["columns"]) + " |")
    lines.append("| " + " | ".join("---" for _ in checklist["columns"]) + " |")
    for check in checklist["checks"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(check["order"]),
                    f"`{check['check_id']}`",
                    check["required_result"],
                    f"`{check['finding_class']}`",
                )
            )
            + " |"
        )
    lines.extend(("", *checklist["outro_lines"]))
    return ("\n".join(lines) + "\n").encode("utf-8")


def _structural_text(text: str) -> str:
    """Mask fenced examples while preserving offsets into the original text."""
    fence: str | None = None
    lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if fence is None:
            opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\n"))
            if opening and not (opening[1][0] == "`" and "`" in opening[2]):
                fence = opening[1]
                lines.append("".join("\n" if char == "\n" else " " for char in line))
            else:
                lines.append(line)
        else:
            lines.append("".join("\n" if char == "\n" else " " for char in line))
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*", line.rstrip("\n")):
                fence = None
    return "".join(lines)


def validate_artifact(payload: bytes, *, layer: str) -> DesignArtifactValidationResult:
    contract = load_contract()
    normalized_layer = layer.lower()
    if normalized_layer not in contract["layers"]:
        raise DesignArtifactContractError(f"unsupported Design layer: {layer}")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DesignArtifactContractError("Design candidate must be UTF-8") from exc
    if "\r" in text:
        raise DesignArtifactContractError("Design candidate must use LF line endings")
    structure = _structural_text(text)
    matches = list(_H2_PATTERN.finditer(structure))
    if not matches:
        raise DesignArtifactContractError("Design candidate has no numbered level-two sections")
    numbers = [int(match.group(1)) for match in matches]
    if numbers != list(range(len(matches))):
        raise DesignArtifactContractError("Design section numbering must be continuous from zero")
    headings = [match.group(2) for match in matches]
    if len(set(headings)) != len(headings):
        raise DesignArtifactContractError("Design section headings must be unique")

    layer_contract = contract["layers"][normalized_layer]
    protected = layer_contract["protected_headings"]
    positions: list[int] = []
    for heading in protected:
        observed = [index for index, value in enumerate(headings) if value == heading]
        if len(observed) != 1:
            raise DesignArtifactContractError(
                f"protected Design heading must occur exactly once: {heading}; observed={len(observed)}"
            )
        positions.append(observed[0])
    if positions != sorted(positions):
        raise DesignArtifactContractError("protected Design headings are out of order")
    slot = layer_contract["extension_slot"]
    slot_start = headings.index(slot["after"])
    slot_end = headings.index(slot["before"])
    extras = [
        index for index, heading in enumerate(headings) if heading not in set(protected)
    ]
    if any(not slot_start < index < slot_end for index in extras):
        raise DesignArtifactContractError("Design extension section is outside its layer-owned slot")

    optional = contract["optional_sections"][0]
    optional_heading = optional["heading"]
    if optional_heading in headings:
        optional_index = headings.index(optional_heading)
        if optional_index != slot_end - 1:
            raise DesignArtifactContractError(
                "optional review-completion section must be last in the extension slot"
            )
        optional_body_start = matches[optional_index].end()
        optional_body_end = (
            matches[optional_index + 1].start()
            if optional_index + 1 < len(matches)
            else len(text)
        )
        optional_body = structure[optional_body_start:optional_body_end]
        observed_subsections = [
            (match.group(1), match.group(2))
            for match in _H3_PATTERN.finditer(optional_body)
        ]
        expected_subsections = [
            (f"{optional_index}.{index}", heading)
            for index, heading in enumerate(
                optional["required_subsections"], start=1
            )
        ]
        if observed_subsections != expected_subsections:
            raise DesignArtifactContractError(
                "optional review-completion subsections are missing, renamed, or out of order"
            )
        optional_section_validated = True
    else:
        optional_section_validated = False

    for index, match in enumerate(matches):
        body_start = match.end()
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        if not body or body.casefold() in _PLACEHOLDERS:
            raise DesignArtifactContractError(f"Design section is empty or placeholder-only: {headings[index]}")
    capsule_index = headings.index("Intent Capsule")
    capsule_start = matches[capsule_index].end()
    capsule_end = matches[capsule_index + 1].start()
    frontmatter = ""
    if text.startswith("---\n"):
        frontmatter_end = text.find("\n---\n", 3)
        if frontmatter_end == -1:
            raise DesignArtifactContractError("Design frontmatter is not closed")
        frontmatter = text[4:frontmatter_end]
    declarations: list[str] = []
    for location, body in (
        ("frontmatter", frontmatter),
        ("Intent Capsule", text[capsule_start:capsule_end]),
    ):
        values = re.findall(r"^layer:[ \t]*(.*?)[ \t]*$", body, re.MULTILINE)
        if len(values) > 1:
            raise DesignArtifactContractError(f"Design layer is repeated in {location}")
        declarations.extend(values)
    expected_layer = layer_contract["layer_value"]
    allowed_values = {expected_layer, f'"{expected_layer}"', f"'{expected_layer}'"}
    if not declarations:
        raise DesignArtifactContractError("Design layer declaration is missing")
    if any(value not in allowed_values for value in declarations):
        raise DesignArtifactContractError(
            f"Design layer declarations conflict with requested {expected_layer!r}"
        )
    validator_ids = [
        "design_utf8_and_line_endings",
        "design_numbered_section_sequence",
        "design_required_section_schema",
        "design_section_content",
        "design_layer_capsule_binding",
    ]
    if optional_section_validated:
        validator_ids.append("design_optional_review_completion_section")
    return DesignArtifactValidationResult(
        subject_sha256=hashlib.sha256(payload).hexdigest(),
        layer=normalized_layer,
        headings=tuple(headings),
        validator_ids=tuple(validator_ids),
    )


def main(argv: list[str] | None = None) -> int:
    """Expose the existing read-only validator without host dependencies."""
    parser = argparse.ArgumentParser(
        description="检查 Design 文档结构与 layer；不执行语义审核，不修改文件。"
    )
    parser.add_argument("files", type=Path, nargs="+", help="待检查的 Design 文档")
    parser.add_argument(
        "--layer", type=str.lower, choices=("charter", "t0", "t1", "t2"),
        required=True, help="本次文件的目标层级",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON 检查结果")
    args = parser.parse_args(argv)
    results: list[dict[str, Any]] = []
    for path in args.files:
        try:
            checked = validate_artifact(path.read_bytes(), layer=args.layer)
        except (OSError, DesignArtifactContractError) as exc:
            results.append({
                "file": str(path), "valid": False,
                "error_code": exc.code if isinstance(exc, DesignArtifactContractError) else type(exc).__name__,
                "message": str(exc),
            })
        else:
            results.append({"file": str(path), "valid": True, **asdict(checked)})
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            if result["valid"]:
                print(f"通过结构检查：{result['file']}（{len(result['validator_ids'])} 项；不代表语义审核通过）")
            else:
                print(f"检查失败：{result['file']} [{result['error_code']}] {result['message']}")
    return 0 if all(result["valid"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
