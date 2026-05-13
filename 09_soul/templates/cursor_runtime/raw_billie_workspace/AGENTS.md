# AGENTS.md: Non-Canonical Pointer

This workspace runs primarily in Cursor.

The canonical agent entry point is `.cursor/rules/00_hoveath_always.mdc`, not this file. Do not treat `AGENTS.md` as the source of truth for Cursor behavior.

Hoveath is installed as:

- `09_soul/`: portable source layer
- `09_cursor/`: Cursor mirror projection
- `.cursor/rules/`: Cursor-native executable rules
- `.cursor/skills/`: Cursor skill wrappers

If an agent runtime reads this file, immediately route to `.cursor/rules/00_hoveath_always.mdc`.

