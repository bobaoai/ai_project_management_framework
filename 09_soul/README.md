# 09_soul

`09_soul/` is the portable operator layer packaged by this repo.

The digital self carried by this layer is named `Hoveath`.

It represents the assistant as a reusable persona or project manager with:
- stable work style
- stable judgment patterns
- portable heuristics
- memory that can be refined over time

This directory is not the repo's day-to-day working state. It is the source layer that can be projected into local Cursor runtime files and adapted to future projects.

It now contains a copy-first manager baseline imported from the reference `context-infrastructure` system:
- 44 axioms
- 25 skills
- core persona and communication material
- memory and automation scaffolding

## Model

- `09_soul/` is the source of portable identity and learned style.
- `AGENTS.md` and `.cursor/rules/` are the local runtime projection for Cursor.
- host repo `AGENTS.md` and `.cursor/rules/` become the local runtime projection.
- host repo operational files remain local truth.

## Structure

- `core/`: persona, user preferences, project adapter, portability rules
- `docs/`: imported setup and cron references
- `memory/`: observations and reflections that may later be promoted
- `axioms/`: stable principles worth carrying across repos
- `skills/`: reusable work patterns
- `contexts/`: imported context scaffolding from the reference manager
- `periodic_jobs/`: imported heartbeat automation scaffold
- `tools/`: imported helper tools and utilities
- `reference/`: external reference material used to shape this framework
- `core/LOCALIZATION_GUIDE.md`: what to rewrite first when bringing Hoveath into a new repo

## Promotion Rule

Use this path for learning:

1. A lesson appears during project work.
2. Keep it local first.
3. If it repeats and feels stable, write it into `memory/`.
4. If it looks portable across contexts, promote it into `axioms/` or `skills/`.
5. Only project the minimal active subset into `AGENTS.md` or `.cursor/rules/`.

## Portability

The goal is that `09_soul/` can later be summoned by another repo with a new project adapter rather than rebuilt from scratch.

## Copy-First Policy

The current approach is intentionally copy-first:
- import strong existing manager materials
- localize `USER.md` first
- adapt routing and project behavior through local runtime files
- refine or replace imported axioms and skills only after real usage
