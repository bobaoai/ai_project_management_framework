# PROJECT ADAPTER — Hoveath（母仓库自身）

Hoveath 在它自己的母仓库中如何工作。

## Current Read Of The Repo

`Hoveath/` 是 09_soul 的母版本 / source-of-truth。

它**不是**一个产品 repo，也**不是**某个 host 项目的工作区。它是 Hoveath portable digital self 框架本身的源仓库，承担：
- 维护 portable 层的 canonical 版本（axioms / core / skills / bridging / handoff）
- 接收来自其他 host 项目（如 trading_platform）的反向蒸馏 lesson
- 作为新 workspace 的 bootstrap 源

母仓库自带一份 Claude Code 主投影（`09_claude/` + `CLAUDE.md` + `.claude/`），用于在母仓库内迭代和验证 portable 层的修改。这份投影**也是一份示范**：让任何看到 Hoveath 母仓库的人立即知道「Claude Code 投影长什么样」。

## Practical Center Of Gravity

按重要性排序：

| 工作面 | 用途 |
|---|---|
| [`09_soul/axioms/`](../../09_soul/axioms/) | Philosophy 层 source-of-truth；新 axiom / axiom 修订首先在这里发生 |
| [`09_soul/core/`](../../09_soul/core/) | Identity 层 source-of-truth；改完 host 项目要 mirror_sync --apply |
| [`09_soul/skills/`](../../09_soul/skills/) | 跨项目 best-practice skill 库 |
| [`09_soul/bridging/`](../../09_soul/bridging/) | 投影同步工具 + manifest |
| [`09_soul/handoff/`](../../09_soul/handoff/) | installation / distillation 协议 |
| [`09_soul/examples/`](../../09_soul/examples/) | 真实项目的参考实现 |
| [`09_claude/`](../../09_claude/) | 本 Claude Code 投影；Identity 层是 09_soul/core/ 的物理 mirror |
| [`.claude/`](../../.claude/) | Claude Code runtime config（settings / skills / hooks） |

## Local Truths

- **母仓库不绑定具体业务**。任何特定项目的术语、路径、agent 行为约束都不应进 09_soul/ 或 09_claude/，应进它们各自的 host 项目
- **改 09_soul/core/* 后必须 sync**：跑 `python 09_soul/bridging/mirror_sync.py --apply` 把改动同步到 09_claude/core/*。不要手抄
- **axiom 编号先到先得**：新 axiom 审核入仓前先扫一遍 INDEX.md 确认编号未占；冲突时按时间序处理（参见 a20 的 frontmatter 解释）
- **examples/ 是验证集，不是规范**：从 trading_platform 蒸馏来的内容只能作为参考，不能反向定义协议
- **未提交的工作面**：`handoff/add_new_agent_projection.md`、`templates/` 仍待建，分别属于 distillation backlog 与 templates v0.1 验收门
- **不要在母仓库写业务 skill**：业务 skill（trading 的 portfolio analysis、Fed-watcher 等）属于 host 项目的 `.<agent>/skills/`，母仓库的 `.claude/skills/` 只放跨项目通用的 best-practice baseline

## When To Summon Hoveath

母仓库内的工作大多需要 Hoveath 全程在场，因为这些工作本身就是在维护 Hoveath：

- 新 axiom 提案 / 现有 axiom 修订（高频）
- Skill 写作与升级（高频）
- handoff 协议演化（installation / distillation / add_new_agent）
- bridging 层工具维护（mirror_sync 升级、新增 sync 类型）
- 反向蒸馏窗口：从 host 项目接收 promotion candidates
- README / INDEX / 顶层 doc 重写（需要严格 self-review）

## What Stays Local

母仓库本身已经是 Hoveath 的 portable 层，所以"local"在这里的语义是「母仓库特有但不该跨项目继承的内容」：

- 本 PROJECT_ADAPTER.md（描述母仓库自己；其他项目要写自己的）
- 本仓库的 `CLAUDE.md`（描述母仓库自己的工作面与 routing；其他项目要写自己的）
- 本仓库的 `.claude/settings.json`（runtime config 项目特化）
- `examples/<project>/` 下的项目特定材料
- 任何尚未通过 distillation 验收门的实验性 skill / axiom 草稿

## Promotion Filter

母仓库本身不接收 promotion（它就是 promotion 的终点），但它内部会发生**升级类决策**：

| 决策 | 标准 |
|---|---|
| host 项目 lesson → 09_soul/ | 至少 ≥3 项目重复出现，且 portable（不依赖某个 repo 的路径 / 工具栈） |
| 实验 axiom 草稿 → INDEX 正式入仓 | dogfood ≥1 周稳定 + self-review 通过 + 与现有 axiom 无冲突 |
| 跨项目 skill 升级 / 拆分 | 在 ≥2 host 项目里被 dogfood 过，且当前形态阻碍迭代 |
| handoff 协议改版 | round-trip validation 在至少一个 example 项目通过 |

## Hoveath 在母仓库内的具体角色

- **Architect**：维护 09_soul/ 的层归属边界（Philosophy / Identity / Working Environment / Execution）
- **Editor**：所有公开 doc（README、INDEX、handoff/*）的写作 + self-review
- **Migrator**：把 host 项目蒸馏来的 lesson 整合进母仓库时做编号 reconciliation 与 portability 提纯
- **Validator**：每次大改后跑 mirror_sync --check / handoff round-trip / INDEX consistency 验收
