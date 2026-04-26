# .claude/skills/

本目录留给 **Claude Code native invocable skill**（带 YAML frontmatter、可被 Claude Code 自动发现并通过触发词调用的 skill）。

母仓库当前**没有** invocable skill 需求 — 工作几乎都是 doc 维护 / framework 演化，通过 CLAUDE.md 的 routing table 直接指向 [`09_claude/skills/`](../../09_claude/skills/) 中的 reference skill 即可。

## 与 09_claude/skills/ 的边界

| 目录 | 性质 | 加载方式 | frontmatter |
|---|---|---|---|
| [`09_claude/skills/`](../../09_claude/skills/) | 文档型 reference skill（baseline mirror） | CLAUDE.md routing 引导 / 主动 Read | 无（保留 09_soul 原 markdown 格式） |
| `.claude/skills/`（本目录） | Claude Code native invocable skill | Claude Code 自动 discover | YAML frontmatter 必填（`name` + `description`） |

## 何时该往这里加 skill

- 某个流程触发条件能用一句话描述、且希望 Claude Code 自动识别并调用
- 该流程在母仓库内部反复出现，每次手动指引浪费 token
- frontmatter `description` 能写得让 Claude Code 准确判断何时该用

不满足时，把 skill 留在 `09_claude/skills/`（或新增到 `09_soul/skills/` 后 mirror），用 CLAUDE.md routing 显式指引。

## 加 skill 的格式

```markdown
---
name: skill-name
description: When this skill should be used. Triggers, scope, and what it produces.
---

# Skill body
...
```

文件名可以是 `<name>.md` 或子目录 `<name>/SKILL.md`。
