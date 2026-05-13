# Cursor Runtime Template Draft

## Status

Experimental raw template material.

This directory holds a local copy of the Cursor-native Hoveath runtime that was dogfooded in `billie_workspace` on 2026-05-04.

It is not yet the portable canonical Cursor template. Treat it as distillation input.

## Contents

`raw_billie_workspace/` contains:

- `.cursor/rules/`: Cursor-native executable trigger rules
- `.cursor/skills/`: physical Cursor project skills, not pointer wrappers
- `09_cursor/`: Cursor projection layer with core, axioms, skills, routing, rules, and working logs
- `AGENTS.md`: non-canonical pointer for non-Cursor runtimes

## Boundary

The raw snapshot intentionally preserves local billie_workspace material, including area-first PIM assumptions and work-domain overlays such as EB1-B and paper review.

Do not copy this directory directly into a new workspace as portable truth.

## Next Step

Distill `raw_billie_workspace/` into a clean Cursor template:

- keep runtime layers: `00`, `01-03`, `30-34`, `40-42`, `50-52`, `91`
- parameterize project adapter, routing rows, and truth surfaces
- remove or placeholder billie-specific overlays: PIM area conventions, EB1-B, Nathan paper-review persona
- preserve the Cursor-specific contract that `.cursor/skills/<skill>/SKILL.md` contains the full skill body
