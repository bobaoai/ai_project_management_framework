# AGENTS.md — Hoveath 母仓库

> Runtime 状态表 + 非 Cursor/Claude 入口指针。Cursor 的 canonical entry 是 [`.cursor/rules/00_hoveath_always.mdc`](.cursor/rules/00_hoveath_always.mdc)，Claude Code 的 canonical entry 是 [`CLAUDE.md`](CLAUDE.md)。

## Mission

Maintain `Hoveath` as a portable digital self that can be cloned into other repos.

This repo is the **source framework / 母仓库**, not a host project's operational workspace.

## Current Agent Runtime

| Runtime | Status | Entry |
|---|---|---|
| Claude Code | **active**（主投影） | [`CLAUDE.md`](CLAUDE.md) + [`09_claude/`](09_claude/) + [`.claude/`](.claude/) |
| Cursor | **active secondary**（本地模板 dogfood） | [`.cursor/rules/00_hoveath_always.mdc`](.cursor/rules/00_hoveath_always.mdc) + [`09_cursor/`](09_cursor/) + [`.cursor/skills/`](.cursor/skills/) |
| OpenCode / Codex / 其他 | 未实施 | 按 [`09_soul/handoff/add_new_agent_projection.md`](09_soul/handoff/add_new_agent_projection.md)（待补）协议建立 |

非 Claude-Code / Cursor 的 agent runtime 打开本仓时，先读本文件判断当前主投影，再按对应 runtime 入口进入。

## Repo Purpose

- 维护 portable 层 source-of-truth：[`09_soul/`](09_soul/)
- 接收 host 项目的反向蒸馏：[`09_soul/handoff/distillation_protocol.md`](09_soul/handoff/distillation_protocol.md)
- 作为新 workspace 的 bootstrap 源：[`09_soul/handoff/installation_guide.md`](09_soul/handoff/installation_guide.md)
- 维护 Claude Code 主投影自身（dogfood 框架在它自己的母仓库里）

## Working Rule

When editing this repo, prefer improving portability over optimizing for one host project.

母仓库本身的 runtime 投影是例外：`09_claude/` / `CLAUDE.md` / `.claude/` 用于 Claude Code dogfood，`09_cursor/` / `.cursor/` 用于 Cursor runtime dogfood。

## Safety

- Do not embed nested git repos
- Keep deprecated imported materials clearly marked rather than silently deleting them
- 不要把 host 项目的业务 overlay 提升进母仓 runtime。Cursor runtime 可吸收的是通用运行层，不是 billie_workspace 的 EB1-B / PIM / Nathan persona。
