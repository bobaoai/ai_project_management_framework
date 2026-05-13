# Task Mainlines: Hoveath Mother Repo Cursor Projection

Cursor 默认先读 `.cursor/rules/00_hoveath_always.mdc`。本表用于把母仓库请求路由到 truth surface、first authority 和 Cursor skill。

| Signal | Mainline | First Authority | Truth Surface | Downstream Skill |
|---|---|---|---|---|
| 新 axiom、修订 axiom、公理 | Axiom maintenance | `09_cursor/axioms/INDEX.md` | `09_soul/axioms/` | `hoveath-doc-self-review`, `hoveath-skill-writing` |
| 新 skill、skill 升级、写技能 | Skill maintenance | `09_cursor/skills/INDEX.md` | `09_soul/skills/` | `hoveath-skill-writing` |
| sync、mirror、core 改了、drift | Mirror sync | `09_soul/bridging/mirror_manifest.json` | `09_soul/bridging/`, `09_claude/`, `09_cursor/` | `hoveath-mirror-sync` |
| 装 Hoveath、bootstrap、install | Installation | `09_soul/handoff/installation_guide.md` | `09_soul/handoff/`, `09_soul/templates/` | `hoveath-staged-approach` |
| 蒸馏、distill、promote、lesson 回流 | Distillation | `09_soul/handoff/distillation_protocol.md` | `09_soul/`, `09_soul/examples/`, `09_soul/templates/` | `hoveath-doc-self-review` |
| Cursor template、Cursor runtime、.cursor/rules、.cursor/skills | Cursor runtime template | `.cursor/rules/00_hoveath_always.mdc` | `.cursor/`, `09_cursor/`, `09_soul/templates/cursor_runtime/` | `hoveath-skill-writing`, `hoveath-mirror-sync` |
| retrospective、复盘、lesson | Retrospective | `09_cursor/core/PROJECT_ADAPTER.md` | relevant local notes or examples | `hoveath-retrospective-writing` |
| reader、persona、为谁写、读者状态 | Reader / persona | `09_cursor/axioms/a20_reader_persona_primacy.md` | `09_soul/personas/`, target doc | `hoveath-reader-state` |
| prompt、subagent brief、boundary | Prompt boundary | `.cursor/rules/31_prompt_boundary_task_vs_control_plane.mdc` | target prompt or brief | `hoveath-prompt-boundary` |
| 调研、research、deep survey | Research | `09_cursor/core/PROJECT_ADAPTER.md` | source materials named by task | `hoveath-deep-research-survey` |
| debug、不稳定、为什么 fail | Debug diagnosis | `.cursor/rules/40_temporal_verification_tripwire.mdc` when time-sensitive, otherwise task logs | logs, error output, changed files | `hoveath-ai-debugging-diagnosis` |
| README、INDEX、handoff doc、stable docs | Stable doc writing | target doc | target doc + related INDEX | `hoveath-reader-state`, `hoveath-doc-self-review` |

## Overlay Rules

- If a change touches `09_soul/core/*`, run mirror sync so `09_claude/` and `09_cursor/` stay aligned.
- If a change touches `09_soul/axioms/*`, update `09_soul/axioms/INDEX.md`.
- If a change touches `09_soul/skills/*`, update `09_soul/skills/INDEX.md`.
- If a change touches `.cursor/rules/` or `.cursor/skills/`, update `09_cursor/rules/INDEX.md` or `09_cursor/skills/INDEX.md`.
- If a task references a host-project example, treat the example as evidence until a promotion decision is explicit.
