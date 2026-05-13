# PROJECT ADAPTER: Hoveath Mother Repo Cursor Projection

Hoveath 在自己的母仓库中通过 Cursor 工作时的本地规则。

## Current Read Of The Repo

`Hoveath/` 是 `09_soul/` 的 source-of-truth。这个仓库不是 host project，也不是业务工作区。它维护 portable digital self 框架本身。

Claude Code 仍是当前主 dogfood runtime。Cursor 现在是 active secondary runtime，用来验证 Hoveath 在 Cursor 里的 native 运行形态，并沉淀 `09_soul/templates/cursor_runtime/`。

## Practical Center Of Gravity

| 工作面 | 用途 |
|---|---|
| `09_soul/` | portable source layer: axioms, core, skills, bridging, handoff, examples |
| `09_cursor/` | Cursor projection layer: mirrored identity, axioms, skills, routing, rules |
| `.cursor/rules/` | Cursor-native executable trigger rules |
| `.cursor/skills/` | Cursor physical project skills, not wrappers |
| `09_claude/` | Claude Code primary projection, kept in sync where mirrored |
| `CLAUDE.md` | Claude Code entry doc |
| `AGENTS.md` | cross-runtime status pointer |
| `09_soul/templates/cursor_runtime/` | Cursor runtime template draft and raw distillation input |

## Local Truths

- `09_soul/` remains the upstream source-of-truth. Do not edit mirrored `09_cursor/` source sections when the intended change belongs upstream.
- `.cursor/rules/00_hoveath_always.mdc` is the Cursor canonical entry point.
- `.cursor/skills/<skill>/SKILL.md` must contain Cursor frontmatter plus the full skill body.
- `09_soul/templates/cursor_runtime/raw_billie_workspace/` is raw snapshot material from a host project. It is evidence for template distillation, not portable canonical truth.
- Mother repo must not absorb host-specific business overlays such as EB1-B, trading, Fed-watcher, or paper-review personas into portable source.

## When To Summon Hoveath

Use Hoveath in Cursor for the same mother-repo work as Claude Code:

- new or revised axioms
- skill writing and skill upgrades
- mirror sync and projection maintenance
- installation and distillation protocol changes
- Cursor runtime template distillation
- examples/ child workspace registry and message flow
- README, INDEX, handoff, and other stable AI-facing docs

## What Stays Local

- This PROJECT_ADAPTER.
- `.cursor/rules/` and `.cursor/skills/` Cursor runtime material.
- `09_cursor/routing/` and `09_cursor/rules/`.
- Template drafts under `09_soul/templates/cursor_runtime/` until they pass round-trip validation.

## Promotion Filter

Promote a Cursor runtime lesson into portable template material only if:

- it is about Cursor runtime shape, not billie_workspace business content
- it survives at least one additional workspace or a deliberate round-trip validation
- it can be expressed with placeholders for project truth surfaces and routing rows
- it improves install reliability for future Cursor workspaces
