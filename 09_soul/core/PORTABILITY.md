# PORTABILITY

Use this file to decide what the soul can carry into another project.

## Moves Unchanged

- `core/SOUL.md`
- durable parts of `core/USER.md`
- `axioms/`
- reusable `skills/`
- lessons in `memory/` that reflect stable cross-project behavior

## Must Be Adapted

- `core/PROJECT_ADAPTER_bokan_assistant.md`
- any rule that refers to local folders, filenames, or repo-specific workflows
- runtime projections in `AGENTS.md` and `.cursor/rules/`

## Should Usually Stay Local

- one-off operating conventions
- historical cleanup decisions
- temporary folder structures
- project-specific task templates that do not generalize

## Migration Recipe

1. Copy `09_soul/` into the new repo.
2. Read the new repo's actual structure before assuming anything.
3. Write a new project adapter for that repo.
4. Project only the minimal active behavior into its `AGENTS.md` and `.cursor/rules/`.
5. Keep deep context in `09_soul/` and load it on demand.
