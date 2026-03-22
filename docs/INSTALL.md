# Install Hoveath Into A Host Repo

This guide shows how to install `Hoveath` into another repository.

## Copy These Pieces

From this repo, copy:
- `09_soul/`
- `.cursor/rules/00_hoveath_always.mdc`
- `.cursor/rules/05_soul_router.mdc`

Then adapt them to the host repo.

## Host Repo Changes

### 1. Add `09_soul/`

Copy the whole `09_soul/` directory into the host repo.

### 2. Add Cursor Runtime Rules

Copy the rule templates into the host repo's `.cursor/rules/`.

Suggested filenames:
- `.cursor/rules/00_hoveath_always.mdc`
- `.cursor/rules/05_soul_router.mdc`

### 3. Update Host `AGENTS.md`

Add Hoveath to the host repo's guidance layers and routing logic.

Minimum idea:
- `09_soul/` is the portable source layer
- host repo operational files remain local truth
- runtime rules stay short

### 4. Localize The User

Edit:
- `09_soul/core/USER.md`

This is the first file that should reflect the real user and working style.

### 5. Create A Project Adapter

Duplicate:
- `09_soul/core/PROJECT_ADAPTER_TEMPLATE.md`

Rename it for the host repo, for example:
- `PROJECT_ADAPTER_app_repo.md`
- `PROJECT_ADAPTER_personal_workspace.md`

### 6. Localize Only The Skills You Need

Many imported skills are already portable.

Some still depend on:
- missing side projects
- external credentials
- host-specific paths

If a skill is not locally usable yet, keep it and mark it deprecated rather than deleting it.

## Recommended Order

1. copy framework
2. copy runtime templates
3. update host `AGENTS.md`
4. localize `USER.md`
5. create project adapter
6. localize path-heavy skills only when needed

## Optional Next Step

If the host repo starts teaching Hoveath stable lessons, promote them back into:
- `09_soul/memory/`
- `09_soul/axioms/`
- `09_soul/skills/`
