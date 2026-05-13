"""Assemble a self-contained review prompt for an independent SKILL.md reviewer.

Usage:
    python -m audit.tools.assemble_skill_reviewer <module_id> <skill_dir>
    python -m audit.tools.assemble_skill_reviewer <module_id>
    python -m audit.tools.assemble_skill_reviewer --list

Outputs the assembled prompt to stdout. Pipe to claude -p for execution.
<module_id> alone lists available skills for that module.
--list shows all modules and their skills.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULES_DIR = Path(__file__).resolve().parents[1] / "modules"
PROMPT_TEMPLATE = MODULES_DIR / "the_skill_management" / "skill_reviewer_prompt.md"
GOVERNANCE_DOC = "designDoc/the_skill_management.md"


def discover_skills() -> dict[str, list[dict[str, str]]]:
    """Scan registries and extract Agent/Skill instances with owner_ref."""
    result: dict[str, list[dict[str, str]]] = {}

    for registry_path in sorted(MODULES_DIR.glob("*/registry.py")):
        module_id = registry_path.parent.name
        source = registry_path.read_text(encoding="utf-8")

        design_doc = _extract_module_design_doc(source)
        registry_rel = str(registry_path.relative_to(PROJECT_ROOT))

        skills: list[dict[str, str]] = []
        for m in re.finditer(r'owner_ref\s*=\s*["\'](.+?SKILL\.md)["\']', source):
            skill_path = m.group(1)
            skill_dir = _skill_dir_from_path(skill_path)
            if skill_dir:
                skills.append({
                    "skill_dir": skill_dir,
                    "skill_path": skill_path,
                    "design_doc": design_doc or "(not found in registry)",
                    "registry": registry_rel,
                })

        if skills:
            result[module_id] = skills

    return result


def _extract_module_design_doc(source: str) -> str | None:
    m = re.search(r'^MODULE_DESIGN_DOC\s*=\s*["\'](.+?)["\']', source, re.MULTILINE)
    return m.group(1) if m else None


def _skill_dir_from_path(skill_path: str) -> str | None:
    parts = skill_path.split("/")
    for i, p in enumerate(parts):
        if p == "skills" and i + 1 < len(parts):
            return parts[i + 1]
    return None


def assemble(module_id: str, skill_dir: str) -> str:
    all_skills = discover_skills()
    module_skills = all_skills.get(module_id, [])

    target = None
    for s in module_skills:
        if s["skill_dir"] == skill_dir:
            target = s
            break

    if not target:
        print(f"Skill '{skill_dir}' not found in module '{module_id}'.", file=sys.stderr)
        if module_skills:
            available = ", ".join(s["skill_dir"] for s in module_skills)
            print(f"Available skills for {module_id}: {available}", file=sys.stderr)
        else:
            available_modules = ", ".join(sorted(all_skills))
            print(f"No skills found for module '{module_id}'. Modules with skills: {available_modules}", file=sys.stderr)
        sys.exit(1)

    skill_full = PROJECT_ROOT / target["skill_path"]
    if not skill_full.exists():
        print(f"SKILL.md not found: {target['skill_path']}", file=sys.stderr)
        print("Cannot review a SKILL.md that does not exist. Run the writer first.", file=sys.stderr)
        sys.exit(1)

    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    governance = _read_file(GOVERNANCE_DOC)
    design_doc = _read_file(target["design_doc"])
    registry = _read_file(target["registry"])
    skill_md = _read_file(target["skill_path"])

    prompt = template
    prompt = prompt.replace("{{GOVERNANCE}}", governance)
    prompt = prompt.replace("{{DESIGN_DOC}}", design_doc)
    prompt = prompt.replace("{{REGISTRY}}", registry)
    prompt = prompt.replace("{{SKILL_MD}}", skill_md)
    prompt = prompt.replace("{{MODULE_ID}}", module_id)
    prompt = prompt.replace("{{SKILL_DIR}}", skill_dir)
    prompt = prompt.replace("{{SKILL_PATH}}", target["skill_path"])
    prompt = prompt.replace("{{REVIEW_DATE}}", date.today().isoformat())

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
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        all_skills = discover_skills()
        if not all_skills:
            print("No modules with skills discovered.")
            return
        for mid, skills in sorted(all_skills.items()):
            print(f"{mid}:")
            for s in skills:
                marker = "exists" if (PROJECT_ROOT / s["skill_path"]).exists() else "missing"
                print(f"  [{marker}] {s['skill_dir']}")
                print(f"          {s['skill_path']}")
        return

    if len(sys.argv) == 2 and not sys.argv[1].startswith("-"):
        module_id = sys.argv[1]
        all_skills = discover_skills()
        module_skills = all_skills.get(module_id, [])
        if not module_skills:
            print(f"No skills found for module '{module_id}'.", file=sys.stderr)
            available = ", ".join(sorted(all_skills))
            if available:
                print(f"Modules with skills: {available}", file=sys.stderr)
            sys.exit(1)
        print(f"{module_id}:")
        for s in module_skills:
            marker = "exists" if (PROJECT_ROOT / s["skill_path"]).exists() else "missing"
            print(f"  [{marker}] {s['skill_dir']}")
            print(f"          {s['skill_path']}")
        return

    if len(sys.argv) == 3 and not sys.argv[1].startswith("-"):
        print(assemble(sys.argv[1], sys.argv[2]))
        return

    print(f"Usage: {sys.argv[0]} <module_id> <skill_dir>", file=sys.stderr)
    print(f"       {sys.argv[0]} <module_id>  (list skills)", file=sys.stderr)
    print(f"       {sys.argv[0]} --list", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
