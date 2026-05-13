"""Assemble a self-contained audit prompt for an independent semantic reviewer.

Usage:
    python -m audit.tools.assemble_contract_audit research_technical
    python -m audit.tools.assemble_contract_audit --discover
    python -m audit.tools.assemble_contract_audit --diff

Outputs the assembled prompt to stdout. Pipe to claude -p for execution.
--discover prints discovered modules from the filesystem.
--diff compares discovered modules against the hardcoded MODULES dict.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULES_DIR = Path(__file__).resolve().parents[1] / "modules"
PROMPT_TEMPLATE = MODULES_DIR / "the_contract_audit" / "contract_audit_prompt.md"
BASE_REL = "src/audit/base.py"

AUDIT_DOC = "designDoc/the_contract_audit.md"

MODULES: dict[str, dict[str, str]] = {
    "research_technical": {
        "design_doc": "designDoc/temp/smoke/designDoc/research_20_technical_module_smoke_design.md",
        "registry": "src/audit/modules/research_technical/registry.py",
        "base": "src/audit/base.py",
        "skill_md": ".claude/skills/agent-research-technical-analysis/SKILL.md",
    },
    "the_contract_audit": {
        "design_doc": "designDoc/the_contract_audit.md",
        "registry": "src/audit/modules/the_contract_audit/registry.py",
        "base": "src/audit/base.py",
        "skill_md": ".claude/skills/agent-the-contract-audit/SKILL.md",
    },
}


def discover_modules() -> dict[str, dict[str, str]]:
    """Scan modules/*/registry.py and extract audit config from each registry."""
    discovered: dict[str, dict[str, str]] = {}

    for registry_path in sorted(MODULES_DIR.glob("*/registry.py")):
        module_id = registry_path.parent.name
        registry_rel = str(registry_path.relative_to(PROJECT_ROOT))
        source = registry_path.read_text(encoding="utf-8")

        design_doc = _extract_module_design_doc(source)
        skill_md = _extract_skill_md(source, registry_path, module_id)

        discovered[module_id] = {
            "design_doc": design_doc or "(not found in registry)",
            "registry": registry_rel,
            "base": BASE_REL,
            "skill_md": skill_md or "",
        }

    return discovered


def _extract_module_design_doc(source: str) -> str | None:
    """Extract MODULE_DESIGN_DOC string constant from registry source."""
    m = re.search(r'^MODULE_DESIGN_DOC\s*=\s*["\'](.+?)["\']', source, re.MULTILINE)
    return m.group(1) if m else None


def _extract_skill_md(source: str, registry_path: Path, module_id: str) -> str | None:
    """Extract SKILL.md path from Agent owner_ref in registry source."""
    for m in re.finditer(r'owner_ref\s*=\s*["\'](.+?\.md)["\']', source):
        path = m.group(1)
        if "skills/" in path and path.endswith("SKILL.md"):
            return path
    return None


def diff_modules() -> list[str]:
    """Compare hardcoded MODULES against discovered modules. Return diff lines."""
    discovered = discover_modules()
    diffs: list[str] = []

    all_ids = sorted(set(list(MODULES) + list(discovered)))
    for mid in all_ids:
        hardcoded = MODULES.get(mid)
        found = discovered.get(mid)

        if hardcoded and not found:
            diffs.append(f"  {mid}: in MODULES but not discovered (no registry.py)")
            continue
        if found and not hardcoded:
            diffs.append(f"  {mid}: discovered but not in MODULES (needs registration)")
            for k, v in found.items():
                diffs.append(f"    {k}: {v}")
            continue

        for key in ("design_doc", "registry", "base", "skill_md"):
            h = hardcoded.get(key, "")
            d = found.get(key, "")
            if h != d:
                diffs.append(f"  {mid}.{key}:")
                diffs.append(f"    hardcoded:   {h}")
                diffs.append(f"    discovered:  {d}")

    return diffs


def assemble(module_id: str) -> str:
    if module_id not in MODULES:
        available = ", ".join(sorted(MODULES))
        print(f"Unknown module: {module_id}. Available: {available}", file=sys.stderr)
        sys.exit(1)

    paths = MODULES[module_id]
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")

    audit_doc = _read_file(AUDIT_DOC)
    design_doc = _read_file(paths["design_doc"])
    registry = _read_file(paths["registry"])
    base = _read_file(paths["base"])
    skill_md = _read_file(paths.get("skill_md", ""))

    prompt = template
    prompt = prompt.replace("{{AUDIT_DOC}}", audit_doc)
    prompt = prompt.replace("{{DESIGN_DOC}}", design_doc)
    prompt = prompt.replace("{{REGISTRY}}", registry)
    prompt = prompt.replace("{{BASE}}", base)
    prompt = prompt.replace("{{SKILL_MD}}", skill_md or "(no SKILL.md for this module)")
    prompt = prompt.replace("{{MODULE_ID}}", module_id)
    prompt = prompt.replace("{{AUDIT_DATE}}", date.today().isoformat())

    return prompt


def _read_file(rel_path: str) -> str:
    if not rel_path:
        return ""
    full = PROJECT_ROOT / rel_path
    if not full.exists():
        print(f"Warning: file not found: {rel_path}", file=sys.stderr)
        return f"(file not found: {rel_path})"
    return full.read_text(encoding="utf-8")


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] == "--discover":
        discovered = discover_modules()
        if not discovered:
            print("No modules discovered.")
            return
        for mid, paths in discovered.items():
            print(f"{mid}:")
            for k, v in paths.items():
                print(f"  {k}: {v}")
        return

    if len(sys.argv) == 2 and sys.argv[1] == "--diff":
        diffs = diff_modules()
        if not diffs:
            print("MODULES dict matches discovered modules. No differences.")
        else:
            print("Differences between MODULES (hardcoded) and discovered:")
            for line in diffs:
                print(line)
        return

    if len(sys.argv) != 2 or sys.argv[1].startswith("-"):
        print(f"Usage: {sys.argv[0]} <module_id>", file=sys.stderr)
        print(f"       {sys.argv[0]} --discover", file=sys.stderr)
        print(f"       {sys.argv[0]} --diff", file=sys.stderr)
        sys.exit(1)

    print(assemble(sys.argv[1]))


if __name__ == "__main__":
    main()
