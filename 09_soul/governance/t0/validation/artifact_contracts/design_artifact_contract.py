#!/usr/bin/env python3
"""DDM v5 structural and identity checks, with explicit local-reference scope."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import unquote, urlsplit

ERROR_CODE = "DESIGN_REPRESENTATION_INCOMPLETE"
CONTRACT_PATH = Path(__file__).with_suffix(".json")
_H2_PATTERN = re.compile(r"^ {0,3}##[ \t]+(\d+)\.[ \t]+(.+?)[ \t]*$", re.MULTILINE)
_PLACEHOLDERS = {"todo", "tbd", "placeholder", "待补充", "待定"}


class DesignArtifactContractError(ValueError):
    code = ERROR_CODE


@dataclass(frozen=True)
class DesignArtifactValidationResult:
    subject_sha256: str
    layer: str
    headings: tuple[str, ...]
    validator_ids: tuple[str, ...]
    contract_version: str
    contract_sha256: str
    references_checked: bool
    validation_scope: str
    external_references_unverified: tuple[str, ...]


def _require_exact_keys(value, expected, context):
    if not isinstance(value, dict) or set(value) != expected:
        raise DesignArtifactContractError(
            f"{context} keys mismatch; expected={sorted(expected)}"
        )


def _read_contract(path: Path = CONTRACT_PATH):
    try:
        raw = Path(path).read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeError, ValueError) as exc:
        raise DesignArtifactContractError(
            f"cannot read Design artifact contract: {path}"
        ) from exc
    _require_exact_keys(
        value,
        {
            "$id",
            "contract_version",
            "artifact_contract_id",
            "owner_t0_layer_id",
            "artifact_kind",
            "layers",
            "modules",
            "section_rules",
            "identity_fields",
            "reviewer_checklist",
            "forbidden_headings",
        },
        "contract",
    )
    if (
        value["contract_version"] != "design_artifact_contract_v5"
        or value["$id"] != "hoveath://governance/design-artifact-contract/v5"
    ):
        raise DesignArtifactContractError(
            "unsupported Design artifact contract version"
        )
    if (
        value["artifact_contract_id"],
        value["owner_t0_layer_id"],
        value["artifact_kind"],
    ) != (
        "design_document_artifact_contract",
        "the_design_doc_management",
        "design_document",
    ):
        raise DesignArtifactContractError("Design artifact contract identity mismatch")
    if not isinstance(value["layers"], dict) or set(value["layers"]) != {
        "charter",
        "t0",
        "t1",
        "t2",
    }:
        raise DesignArtifactContractError("Design contract layers are invalid")
    for key, row in value["layers"].items():
        _require_exact_keys(row, {"layer_value"}, f"layers.{key}")
        if row["layer_value"] != ("Charter" if key == "charter" else key.upper()):
            raise DesignArtifactContractError(f"layers.{key} value is invalid")
    modules = value["modules"]
    if not isinstance(modules, dict) or not modules:
        raise DesignArtifactContractError("Design modules must be a nonempty catalog")
    for name, row in modules.items():
        _require_exact_keys(row, {"layers"}, f"modules.{name}")
        allowed = row["layers"]
        if (
            not isinstance(name, str)
            or not name.strip()
            or not isinstance(allowed, list)
            or not allowed
            or any(x not in value["layers"] for x in allowed)
            or len(allowed) != len(set(allowed))
        ):
            raise DesignArtifactContractError(f"invalid module declaration: {name}")
    rules = value["section_rules"]
    _require_exact_keys(
        rules,
        {
            "numbering_start",
            "required_headings",
            "opening_headings",
            "final_heading",
            "exclusive_groups",
        },
        "section_rules",
    )
    if (
        type(rules["numbering_start"]) is not int
        or rules["numbering_start"] != 1
        or rules["required_headings"] != ["Intended Outcomes", "References"]
        or rules["opening_headings"]
        != ["Primary System Flow", "Constitutional Authority Map"]
        or rules["final_heading"] != "References"
    ):
        raise DesignArtifactContractError(
            "section_rules opening, required or numbering rules are invalid"
        )
    if rules["exclusive_groups"] != [
        ["Primary System Flow", "Constitutional Authority Map"],
        ["Owned System Object", "Domain Outcome and Owned Objects"],
        ["Completion and Failure", "Completion, Failure, and Recovery"],
    ]:
        raise DesignArtifactContractError("section_rules exclusive groups are invalid")
    if any(
        n not in modules
        for n in rules["required_headings"]
        + rules["opening_headings"]
        + [n for g in rules["exclusive_groups"] for n in g]
    ):
        raise DesignArtifactContractError("section_rules refers to an unknown module")
    identity = value["identity_fields"]
    _require_exact_keys(
        identity, {"required", "optional", "forbidden"}, "identity_fields"
    )
    if identity["required"] != [
        "title",
        "layer",
        "canonical_owner",
        "owned_system_object",
    ] or identity["optional"] != ["parent", "t0_layer_id"]:
        raise DesignArtifactContractError(
            "identity_fields required or optional fields are invalid"
        )
    for label, entries in [
        ("forbidden identity fields", identity["forbidden"]),
        ("forbidden headings", value["forbidden_headings"]),
    ]:
        if (
            not isinstance(entries, list)
            or not entries
            or any(not isinstance(x, str) or not x for x in entries)
            or len(set(entries)) != len(entries)
        ):
            raise DesignArtifactContractError(
                f"{label} must be unique nonempty strings"
            )
    if set(identity["forbidden"]) & set(identity["required"] + identity["optional"]):
        raise DesignArtifactContractError("identity_fields forbid an identity field")
    _validated_checklist(value["reviewer_checklist"])
    return value, hashlib.sha256(raw).hexdigest()


def load_contract(path: Path = CONTRACT_PATH):
    return _read_contract(path)[0]


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
        if not isinstance(lines, list) or any(
            not isinstance(line, str) or not line for line in lines
        ):
            raise DesignArtifactContractError(f"reviewer_checklist.{field} is invalid")
    checks = value["checks"]
    if not isinstance(checks, list) or len(checks) != 11:
        raise DesignArtifactContractError(
            "Design checklist must contain exactly eleven checks"
        )
    check_ids: list[str] = []
    finding_classes: list[str] = []
    for index, check in enumerate(checks, start=1):
        if not isinstance(check, dict):
            raise DesignArtifactContractError(
                f"reviewer_checklist.checks[{index - 1}] must be an object"
            )
        _require_exact_keys(
            check,
            {"order", "check_id", "required_result", "finding_class", "stage"},
            f"reviewer_checklist.checks[{index - 1}]",
        )
        if check["order"] != index:
            raise DesignArtifactContractError(
                "Design checklist order is not continuous"
            )
        if check["stage"] != ("prose" if index == 11 else "semantic"):
            raise DesignArtifactContractError(
                "Design checklist stage boundary is invalid"
            )
        for field in ("check_id", "required_result", "finding_class"):
            if not isinstance(check[field], str) or not check[field]:
                raise DesignArtifactContractError(
                    f"Design checklist {field} must be non-empty"
                )
        check_ids.append(check["check_id"])
        finding_classes.append(check["finding_class"])
    if len(set(check_ids)) != len(check_ids) or len(set(finding_classes)) != len(
        finding_classes
    ):
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


def _blank(text):
    return "".join("\n" if c == "\n" else " " for c in text)


def _structural_text(text: str, *, mask_fences: bool = True) -> str:
    """Mask comments and optionally fences, keeping every character offset."""
    fence = None
    comment = False
    result = []
    for line in text.splitlines(keepends=True):
        if fence is not None:
            result.append(_blank(line) if mask_fences else line)
            if re.fullmatch(
                r" {0,3}"
                + re.escape(fence[0])
                + "{"
                + str(len(fence))
                + r",}[ \t]*\n?",
                line,
            ):
                fence = None
            continue
        raw_opening = (
            re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\n"))
            if not comment
            else None
        )
        if raw_opening and not (raw_opening[1][0] == "`" and "`" in raw_opening[2]):
            fence = raw_opening[1]
            result.append(_blank(line) if mask_fences else line)
            continue
        output = ""
        offset = 0
        while offset < len(line):
            if comment:
                end = line.find("-->", offset)
                stop = len(line) if end < 0 else end + 3
                output += _blank(line[offset:stop])
                offset = stop
                if end >= 0:
                    comment = False
            else:
                start = line.find("<!--", offset)
                code = re.search(r"`+", line[offset:])
                if code and (start < 0 or offset + code.start() < start):
                    code_start = offset + code.start()
                    tail_start = offset + code.end()
                    closing = re.search(
                        r"(?<!`)" + re.escape(code[0]) + r"(?!`)", line[tail_start:]
                    )
                    if closing:
                        stop = tail_start + closing.end()
                        output += line[offset:stop]
                        offset = stop
                        continue
                if start < 0:
                    output += line[offset:]
                    break
                output += line[offset:start]
                offset = start
                comment = True
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", output.rstrip("\n"))
        if opening and not (opening[1][0] == "`" and "`" in opening[2]):
            fence = opening[1]
            result.append(_blank(line) if mask_fences else output)
        else:
            result.append(output)
    return "".join(result)


def _scalar(raw: str, key: str) -> str:
    raw = raw.strip()
    if raw.startswith('"'):
        try:
            value, end = json.JSONDecoder().raw_decode(raw)
        except ValueError as exc:
            raise DesignArtifactContractError(
                f"unsupported quoted scalar for {key}"
            ) from exc
        if not isinstance(value, str) or (
            raw[end:].strip() and not raw[end:].lstrip().startswith("#")
        ):
            raise DesignArtifactContractError(f"unsupported scalar for {key}")
        return value
    if raw.startswith("'"):
        match = re.fullmatch(r"'((?:[^']|'')*)'(?:[ \t]+#.*)?", raw)
        if not match:
            raise DesignArtifactContractError(f"unsupported quoted scalar for {key}")
        return match[1].replace("''", "'")
    value = (
        "" if raw.startswith("#") else re.split(r"[ \t]+#", raw, maxsplit=1)[0].strip()
    )
    if not value or value.casefold() in {"null", "~", "true", "false"}:
        raise DesignArtifactContractError(
            f"frontmatter {key} must be a nonempty string; null/boolean is not a string"
        )
    if (
        value[0] in "|>[{&*!"
        or ": " in value
        or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value)
    ):
        raise DesignArtifactContractError(
            f"unsupported scalar or multiline YAML for {key}; use a single-line string"
        )
    return value


def parse_frontmatter(text: str, *, candidate: bool = True) -> dict[str, str]:
    """Strict candidate scalars; optional display labels never gate background."""
    if not text.startswith("---\n"):
        if candidate:
            raise DesignArtifactContractError("Design frontmatter is required")
        return {}
    end = text.find("\n---\n", 3)
    if end < 0:
        if candidate:
            raise DesignArtifactContractError("Design frontmatter is not closed")
        return {}
    values = {}
    for number, line in enumerate(text[4:end].splitlines(), 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z_0-9-]*)[ \t]*:[ \t]*(.*)", line)
        if not match:
            if candidate:
                raise DesignArtifactContractError(
                    f"unsupported frontmatter YAML at line {number}; only top-level single-line scalars are supported"
                )
            continue
        key, raw = match.groups()
        if not candidate and key not in {"title", "canonical_owner"}:
            continue
        if key in values:
            if candidate:
                raise DesignArtifactContractError(f"duplicate frontmatter field: {key}")
            return {}
        try:
            values[key] = _scalar(raw, key)
        except DesignArtifactContractError:
            if candidate:
                raise
    return values


def _validate_identity(text, layer, definition):
    fields = parse_frontmatter(text)
    for key in definition["identity_fields"]["required"]:
        if not fields.get(key, "").strip():
            raise DesignArtifactContractError(
                f"Design frontmatter requires nonempty {key}"
            )
    for key in definition["identity_fields"]["optional"]:
        if key in fields and not fields[key].strip():
            raise DesignArtifactContractError(
                f"Design frontmatter {key} must be a nonempty string when present"
            )
    forbidden = set(fields) & set(definition["identity_fields"]["forbidden"])
    if forbidden:
        raise DesignArtifactContractError(
            f"forbidden Design metadata: {sorted(forbidden)}"
        )
    expected = definition["layers"][layer]["layer_value"]
    if fields["layer"] != expected:
        raise DesignArtifactContractError(
            f"Design layer conflicts with requested {expected!r}"
        )
    if layer in {"charter", "t0"} and "parent" in fields:
        raise DesignArtifactContractError(f"parent is forbidden for {expected}")
    return fields


def _has_content(body, heading):
    clean = _structural_text(body, mask_fences=False)
    structure = _structural_text(body)
    for match in reversed(
        list(re.finditer(r"^ {0,3}#{1,6}[ \t]+.*$", structure, re.MULTILINE))
    ):
        clean = (
            clean[: match.start()]
            + _blank(clean[match.start() : match.end()])
            + clean[match.end() :]
        )
    clean = re.sub(r"^ {0,3}(?:`{3,}|~{3,}).*$", "", clean, flags=re.MULTILINE)
    lines = [line.strip(" \t\r\n#*_|>-.`") for line in clean.splitlines()]
    lines = [x.casefold() for x in lines if x]
    return bool(lines) and not all(
        x in _PLACEHOLDERS or x == heading.casefold() for x in lines
    )


def local_file_resolver(
    project_root: Path, *, overrides: Mapping[str, str] | None = None
) -> Callable[[str, str], Path]:
    """Resolve only project files, with caller-declared exact canonical overlays."""
    root = Path(project_root).resolve(strict=True)
    if not root.is_dir():
        raise DesignArtifactContractError("reference project root must be a directory")
    overlay = dict(overrides or {})

    def normalized(reference, owner):
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc or parsed.query:
            raise DesignArtifactContractError(
                f"unsupported local reference: {reference}"
            )
        path = unquote(parsed.path)
        if "\\" in path or path.startswith("/"):
            raise DesignArtifactContractError(
                f"absolute or non-portable local reference: {reference}"
            )
        if not path:
            if not owner:
                raise DesignArtifactContractError("empty identity reference")
            path = owner
        elif owner:
            path = posixpath.join(posixpath.dirname(owner), path)
        path = posixpath.normpath(path)
        if path in {".", ".."} or path.startswith("../"):
            raise DesignArtifactContractError(
                f"reference escapes project root: {reference}"
            )
        return path

    for key, value in overlay.items():
        if normalized(key, "") != key or normalized(value, "") != value:
            raise DesignArtifactContractError(
                "reference overlays must use normalized project-relative paths"
            )

    def resolve(reference, owner):
        rel = normalized(reference, owner)
        target = root / overlay.get(rel, rel)
        resolved = target.resolve()
        if not resolved.is_relative_to(root):
            raise DesignArtifactContractError(
                f"reference symlink escapes project root: {reference}"
            )
        if not resolved.is_file():
            raise DesignArtifactContractError(
                f'unresolved local reference: {reference} (canonical owner={owner or "project root"})'
            )
        return resolved

    return resolve


def _destination(contents):
    """Read one Markdown destination and optional title; no content evaluation."""
    contents = contents.strip()
    if contents.startswith("<"):
        stop = contents.find(">")
        if stop < 0:
            raise DesignArtifactContractError("unclosed Markdown link destination")
        target, rest = contents[1:stop], contents[stop + 1 :].strip()
    else:
        stop = 0
        while stop < len(contents):
            if contents[stop] == "\\" and stop + 1 < len(contents):
                stop += 2
                continue
            if contents[stop].isspace():
                break
            stop += 1
        target, rest = contents[:stop], contents[stop:].strip()
    if rest and not (
        len(rest) >= 2
        and (
            (rest[0] == rest[-1] and rest[0] in "\"'")
            or (rest[0], rest[-1]) == ("(", ")")
        )
    ):
        raise DesignArtifactContractError(
            "unsupported Markdown link title or destination"
        )
    if not target:
        raise DesignArtifactContractError("empty Markdown link destination")
    return re.sub(r"\\(.)", r"\1", target)


def _markdown_references(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end >= 0:
            text = _blank(text[: end + 5]) + text[end + 5 :]
    structure = _structural_text(text)
    structure = re.sub(
        r"(`+)(.*?)(?<!`)\1(?!`)", lambda m: _blank(m[0]), structure, flags=re.DOTALL
    )
    definitions = {}
    refs = []
    for match in re.finditer(
        r"^ {0,3}\[([^]\n]+)\]:[ \t]*(.+)$", structure, re.MULTILINE
    ):
        key = " ".join(match[1].split()).casefold()
        if key in definitions:
            raise DesignArtifactContractError(
                f"duplicate Markdown reference label: {match[1]}"
            )
        definitions[key] = _destination(match[2])
        refs.append(definitions[key])
    # Definitions are data for the link scanner, not shortcut links themselves.
    structure = re.sub(
        r"^ {0,3}\[([^]\n]+)\]:[ \t]*(.+)$",
        lambda m: _blank(m[0]),
        structure,
        flags=re.MULTILINE,
    )
    index = 0
    while index < len(structure):
        if structure[index] == "\\":
            index += 2
            continue
        if structure[index] != "[":
            index += 1
            continue
        start = index + 1
        end = start
        depth = 1
        while end < len(structure) and depth:
            if structure[end] == "\\":
                end += 2
                continue
            if structure[end] == "[":
                depth += 1
            elif structure[end] == "]":
                depth -= 1
            if depth:
                end += 1
        if depth:
            break  # Unmatched brackets are ordinary prose.
        label = structure[start:end]
        index = end + 1
        if structure[index : index + 1] == "(":
            start = index + 1
            index = start
            depth = 1
            angle = False
            quote = None
            while index < len(structure):
                char = structure[index]
                if char == "\\":
                    index += 2
                    continue
                if quote:
                    if char == quote:
                        quote = None
                elif angle:
                    if char == ">":
                        angle = False
                elif char == "<":
                    angle = True
                elif char in "\"'" and index > start and structure[index - 1].isspace():
                    quote = char
                elif char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        break
                index += 1
            if depth:
                raise DesignArtifactContractError("unclosed Markdown inline link")
            refs.append(_destination(structure[start:index]))
            index += 1
            continue
        explicit = structure[index : index + 1] == "["
        if explicit:
            close = structure.find("]", index + 1)
            if close < 0:
                raise DesignArtifactContractError("unclosed Markdown reference label")
            label = structure[index + 1 : close] or label
            index = close + 1
        key = " ".join(label.split()).casefold()
        if key in definitions:
            refs.append(definitions[key])
        elif explicit:
            raise DesignArtifactContractError(
                f"unresolved Markdown reference label: {label}"
            )
    return tuple(dict.fromkeys(refs))


def validate_artifact(
    payload: bytes, *, layer: str, reference_resolver=None
) -> DesignArtifactValidationResult:
    definition, contract_hash = _read_contract()
    normalized_layer = layer.lower()
    if normalized_layer not in definition["layers"]:
        raise DesignArtifactContractError(f"unsupported Design layer: {layer}")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DesignArtifactContractError("Design candidate must be UTF-8") from exc
    if "\r" in text:
        raise DesignArtifactContractError("Design candidate must use LF line endings")
    identity = _validate_identity(text, normalized_layer, definition)
    body_start = text.index("\n---\n", 3) + 5
    structure = _blank(text[:body_start]) + _structural_text(text[body_start:])
    for heading in definition["forbidden_headings"]:
        if re.search(
            r"^ {0,3}#{2,6}[ \t]+(?:\d+(?:\.\d+)*\.?[ \t]+)?"
            + re.escape(heading)
            + r"(?:[ \t]+#+)?[ \t]*$",
            structure,
            re.MULTILINE,
        ):
            raise DesignArtifactContractError(f"forbidden Design heading: {heading}")
    matches = list(_H2_PATTERN.finditer(structure))
    if not matches:
        raise DesignArtifactContractError(
            "Design candidate has no numbered level-two sections"
        )
    if len(re.findall(r"^ {0,3}##[ \t]+", structure, re.MULTILINE)) != len(matches):
        raise DesignArtifactContractError(
            "every level-two Design section must be numbered"
        )
    numbers = [int(x[1]) for x in matches]
    if numbers != list(range(1, len(matches) + 1)) or any(
        x[1] != str(int(x[1])) for x in matches
    ):
        raise DesignArtifactContractError(
            "Design section numbering must be continuous from one"
        )
    headings = [x[2] for x in matches]
    if len(set(headings)) != len(headings):
        raise DesignArtifactContractError("Design section headings must be unique")
    rules = definition["section_rules"]
    for name in rules["required_headings"]:
        if name not in headings:
            raise DesignArtifactContractError(
                f"required Design heading is missing: {name}"
            )
    for group in rules["exclusive_groups"]:
        if len(set(group) & set(headings)) > 1:
            raise DesignArtifactContractError(
                f"only one module may be selected from exclusive group: {group}"
            )
    for name in headings:
        if name not in definition["modules"]:
            raise DesignArtifactContractError(f"unknown Design module: {name}")
        if normalized_layer not in definition["modules"][name]["layers"]:
            raise DesignArtifactContractError(
                f"Design module {name} is not allowed for {layer}"
            )
    opening = [x for x in headings if x in rules["opening_headings"]]
    prefix = opening + ["Intended Outcomes"]
    if headings[: len(prefix)] != prefix:
        raise DesignArtifactContractError(
            "Design opening modules and Intended Outcomes are out of order"
        )
    if headings[-1] != rules["final_heading"]:
        raise DesignArtifactContractError("References must be the final Design section")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if not _has_content(text[match.end() : end], headings[index]):
            line = text.count("\n", 0, match.start()) + 1
            raise DesignArtifactContractError(
                f"Design section is empty or placeholder-only: {headings[index]} (line {line})"
            )
    external = []
    checked = reference_resolver is not None
    if checked:

        def resolve(reference, owner):
            try:
                path = reference_resolver(reference, owner)
                if not isinstance(path, (str, Path)) or not Path(path).is_file():
                    raise DesignArtifactContractError(
                        f"resolver did not return an existing file: {reference}"
                    )
            except (OSError, TypeError, ValueError) as exc:
                if isinstance(exc, DesignArtifactContractError):
                    raise
                raise DesignArtifactContractError(
                    f"cannot resolve reference: {reference}: {exc}"
                ) from exc

        for key in ["canonical_owner", "parent"]:
            if key in identity:
                resolve(identity[key], "")
        for ref in _markdown_references(text):
            if urlsplit(ref).scheme.casefold() in {"http", "https", "mailto"}:
                external.append(ref)
            else:
                resolve(ref, identity["canonical_owner"])
    ids = [
        "design_utf8_and_line_endings",
        "design_numbered_section_sequence",
        "design_required_section_schema",
        "design_section_content",
        "design_identity_metadata",
        "design_modular_section_selection",
    ]
    if checked:
        ids.append("design_local_file_references")
    return DesignArtifactValidationResult(
        hashlib.sha256(payload).hexdigest(),
        normalized_layer,
        tuple(headings),
        tuple(ids),
        definition["contract_version"],
        contract_hash,
        checked,
        (
            "structure_identity_and_local_files"
            if checked
            else "structure_and_identity_only"
        ),
        tuple(external),
    )


def main(argv: list[str] | None = None) -> int:
    """Expose the existing read-only validator without host dependencies."""
    parser = argparse.ArgumentParser(
        description="检查当前 Design v5 结构和身份；--project-root 启用本地引用检查，省略时仅检查结构和身份。不执行语义审核，不修改文件。"
    )
    parser.add_argument("files", type=Path, nargs="+", help="待检查的 Design 文档")
    parser.add_argument(
        "--layer",
        type=str.lower,
        choices=("charter", "t0", "t1", "t2"),
        required=True,
        help="本次文件的目标层级",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON 检查结果")
    parser.add_argument(
        "--project-root",
        type=Path,
        help="本地引用的准确项目根；省略则明确报告引用未检查",
    )
    args = parser.parse_args(argv)
    results: list[dict[str, Any]] = []
    for path in args.files:
        try:
            checked = validate_artifact(
                path.read_bytes(),
                layer=args.layer,
                reference_resolver=(
                    local_file_resolver(args.project_root)
                    if args.project_root is not None
                    else None
                ),
            )
        except (OSError, DesignArtifactContractError) as exc:
            results.append(
                {
                    "file": str(path),
                    "valid": False,
                    "error_code": (
                        exc.code
                        if isinstance(exc, DesignArtifactContractError)
                        else type(exc).__name__
                    ),
                    "message": str(exc),
                }
            )
        else:
            results.append({"file": str(path), "valid": True, **asdict(checked)})
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            if result["valid"]:
                print(
                    f"通过结构检查：{result['file']}（{len(result['validator_ids'])} 项；不代表语义审核通过）"
                )
            else:
                print(
                    f"检查失败：{result['file']} [{result['error_code']}] {result['message']}"
                )
    return 0 if all(result["valid"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
