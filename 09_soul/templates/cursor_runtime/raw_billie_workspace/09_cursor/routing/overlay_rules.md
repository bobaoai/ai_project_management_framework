# Overlay Rules: billie_workspace

## Area-First Routing

When interpreting a user request, first identify the area or project it belongs to. Calendar and task files are scheduling tools unless the user explicitly asks to edit them.

## Cursor Native Rule Priority

`.cursor/rules/` remains the executable rule layer for Cursor. If a file glob rule applies, follow it together with this Hoveath routing layer.

Priority order:

1. Explicit user instruction in the current turn
2. Safety and privacy boundaries
3. File-specific `.cursor/rules/*.mdc`
4. `09_cursor/core/PROJECT_ADAPTER.md`
5. Portable Hoveath axioms and skills

## PLAN-Only Boundary

For calendar, task, and general area maintenance, default to PLAN-only. Apply edits only when the user says `apply` or ends the request with `!`.

For direct content work where the user names a target file and asks to edit, draft, rewrite, or review, editing that file is allowed after reading the relevant source materials.
