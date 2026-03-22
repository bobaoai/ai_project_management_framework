# Hoveath Framework Repo

## Mission

Maintain `Hoveath` as a portable digital self that can be cloned into other repos.

This repo is the source framework, not a host project's operational workspace.

## Repo Purpose

- keep the portable soul layer in `09_soul/`
- preserve imported axioms, skills, tools, and memory scaffolding
- provide reusable Cursor runtime templates
- document how to localize Hoveath into a host repo

## Guidance Layers

- `AGENTS.md`: root contract for maintaining this framework repo
- `.cursor/rules/`: reusable runtime templates for installation into host repos
- `09_soul/`: portable identity, memory, axioms, skills, and tooling
- `docs/`: installation and localization guidance

## Working Rule

When editing this repo, prefer improving portability over optimizing for one host project.

## Localization Rule

When Hoveath is installed into another repo, localize these first:
1. `09_soul/core/USER.md`
2. `09_soul/core/PROJECT_ADAPTER_TEMPLATE.md` -> rename for the host repo
3. host repo `AGENTS.md`
4. host repo `.cursor/rules/`

## Keep Stable By Default

These usually should not be heavily rewritten during installation:
- `09_soul/core/SOUL.md`
- `09_soul/core/COMMUNICATION.md`
- `09_soul/axioms/`
- `09_soul/skills/`

## Safety

- Do not embed nested git repos.
- Keep deprecated imported materials clearly marked rather than silently deleting them.
- Keep runtime templates short and adaptable.
