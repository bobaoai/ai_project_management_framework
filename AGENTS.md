# AGENTS.md — Hoveath 母仓库

> **主投影已迁移到 Claude Code**。本文件保留为 sunset 指针 + 框架仓的 mission 简述。详细 entry 见 [`CLAUDE.md`](CLAUDE.md)。

## Mission

Maintain `Hoveath` as a portable digital self that can be cloned into other repos.

This repo is the **source framework / 母仓库**, not a host project's operational workspace.

## Current Agent Runtime

| Runtime | Status | Entry |
|---|---|---|
| Claude Code | **active**（主投影） | [`CLAUDE.md`](CLAUDE.md) + [`09_claude/`](09_claude/) + [`.claude/`](.claude/) |
| Cursor | frozen / sunset | [`.cursor/rules/`](.cursor/rules/) 仅保留 sunset 指针 |
| OpenCode / Codex / 其他 | 未实施 | 按 [`09_soul/handoff/add_new_agent_projection.md`](09_soul/handoff/add_new_agent_projection.md)（待补）协议建立 |

非 Claude-Code 的 agent runtime（含 Cursor）打开本仓时，请直接读 [`CLAUDE.md`](CLAUDE.md) 与 [`09_claude/core/PROJECT_ADAPTER.md`](09_claude/core/PROJECT_ADAPTER.md)。

## Repo Purpose

- 维护 portable 层 source-of-truth：[`09_soul/`](09_soul/)
- 接收 host 项目的反向蒸馏：[`09_soul/handoff/distillation_protocol.md`](09_soul/handoff/distillation_protocol.md)
- 作为新 workspace 的 bootstrap 源：[`09_soul/handoff/installation_guide.md`](09_soul/handoff/installation_guide.md)
- 维护 Claude Code 主投影自身（dogfood 框架在它自己的母仓库里）

## Working Rule

When editing this repo, prefer improving portability over optimizing for one host project.

母仓库本身的 `09_claude/` / `CLAUDE.md` / `.claude/` 是**唯一例外** — 它们是母仓库自己的 runtime，目的是让母仓库的 framework 维护工作能在 Claude Code 里被 dogfood。

## Safety

- Do not embed nested git repos
- Keep deprecated imported materials clearly marked rather than silently deleting them
- Cursor sunset 后不在 `.cursor/rules/` 加新 rule；新 rule 一律去 `09_claude/rules/`
