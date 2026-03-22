# Hoveath

`Hoveath` is a portable digital self for Cursor-centered work.

It packages a reusable soul layer that can be cloned into other repos and localized there:
- identity and communication style
- axioms and skills
- memory scaffolding
- helper tools and automation skeleton
- lightweight Cursor runtime templates

## What This Repo Is

This is the standalone source repo for Hoveath.

It is intentionally separate from any one host project's operational state. The goal is that you can clone this repo, then install `09_soul/` and the runtime templates into another workspace without dragging along unrelated project files.

## Core Layout

- `09_soul/`: portable framework
- `.cursor/rules/`: generic runtime templates
- `docs/`: install and setup guidance
- `examples/`: sample adapter material

## Quick Start

1. Clone this repo.
2. Copy `09_soul/` into the target repo.
3. Copy and adapt the runtime templates from `.cursor/rules/`.
4. Update the target repo's `AGENTS.md`.
5. Localize `09_soul/core/USER.md`.
6. Create a host-specific project adapter from `09_soul/core/PROJECT_ADAPTER_TEMPLATE.md`.

## Localize First

- `09_soul/core/USER.md`
- `09_soul/core/PROJECT_ADAPTER_TEMPLATE.md`
- host repo `AGENTS.md`
- host repo `.cursor/rules/`

## Keep Stable At First

- `09_soul/core/SOUL.md`
- `09_soul/core/COMMUNICATION.md`
- `09_soul/axioms/`
- `09_soul/skills/`

## Notes

- Some imported skills are marked deprecated but preserved. They remain as footprints for future restoration.
- The raw `context-infrastructure` nested repo is intentionally not included here.
- `Hoveath` is the name of the digital self. The portable folder remains `09_soul/` for easy installation across repos.
