# Portfolio Decision Engine

## Purpose

`PortfolioDecisionEngine` 是 `trading_platform` 里的半自动组合决策层。

它负责把：

- 最新市场数据
- 本地 research / theme intelligence
- 当前技术状态
- 当前持仓与账户复盘
- 明确的政策约束

压成短而稳定的按账户决策包，然后交给并行 specialist agents、chair、AI-ready debate prompt/package builder，以及执行预览编译器。

## Boundary

它不是：

- broker connector
- raw market-data loader
- knowledge archive
- final execution layer

它位于：

- `KnowledgeBase` / deterministic package builders
- `OrderExecution`

之间。

## Core Objects

第一版使用 5 类稳定对象：

- `PolicyEnvelope`
- `PortfolioDecisionPackage`
- `TargetBookProposal`
- `DebatePromptArtifact`
- `ExecutionPreviewPlan`

这些对象都应有 JSON truth artifact，并可附带 markdown projection 供 PM/operator 阅读。
主链 artifact 默认都是 `per-account`。

`DebatePromptArtifact` 不是最终辩论正文。
它只负责：

- 固化 AI writer 的 system prompt / user prompt template
- 组装给 AI 的事实型 debate package
- 明确 output section 和证据边界

最终辩论正文应交给 AI writer 生成，而不是在 Python 里硬编码 prose。
`debate package` 不应提前塞入 `Chair Recommendation`、`target weights`、`action table` 这类 rebalance 结论。

## Agent Roles

第一版固定 5 个 specialist roles：

- `MacroRegimeAgent`
- `IntelSynthesisAgent`
- `TechnicalTapeAgent`
- `PortfolioFitAgent`
- `RiskChallengeAgent`

再由一个 `ChairSynthesizer` 做统一裁决。

关键点不是 agent 数量，而是：

- 每个 agent 只吃自己的 projection
- 输出结构化 schema，而不是长篇散文
- chair 只做统一配置与冲突裁决

## Current V1 Policy

在完整风险预算系统完成前，第一版先依赖 `PolicyEnvelope`。

默认要覆盖：

- 最大 gross / net 暴露
- 最小现金比例
- 单标的上限
- 单主题上限
- 单日换手上限
- 新开仓数量上限
- blocked / watch-only 资产

没有政策层时，agent 可以写出结论，但不能给出可控的仓位方案。

## Candidate Universe

第一版候选池来自三个来源：

- 当前持仓
- 当前 active themes 的 `linked_asset_tickers`
- 当前 technical coverage universe

这让系统即使没有完整 optimizer，也能在现有 repo 事实上做一版账户级统一分配与执行衔接。

## Execution Boundary

`PortfolioDecisionEngine` 不直接下 live 单。

它只产出：

- `TargetBookProposal`
- `DebatePromptArtifact`
- `ExecutionPreviewPlan`

其中执行预览应尽量编译成与 `src/portfolio/order_models.py` 兼容的 intent 形态，并明确给出：

- 目标账户
- 当前股数
- 目标股数
- 需要买卖的整股数量
- 默认 `MARKET preview`

当前执行层只支持 `equity / ETF`。
因此 futures、macro proxies、或其他未被 execution layer 支持的资产在第一版里只能：

- 作为 regime / evidence 输入
- 或作为 `watch` / `blocked` 输出

而不应伪装成可直接下单的标的。

## Artifact Paths

第一版落盘到：

- `data/analysis/policy/`
- `data/analysis/decision_packages/`
- `data/analysis/debate_reports/`
- `data/analysis/decisions/`
- `data/analysis/execution_previews/`

这些是 PM/operator truth 和 replay surface，不是 archive plumbing 的替代品。
文件命名应包含 `account_number`，避免多账户结果互相覆盖。

## CLI Surface

建议的第一版 CLI：

- `tradectl portfolio policy-init`
- `tradectl portfolio policy-show`
- `tradectl portfolio package`
- `tradectl portfolio debate`
- `tradectl portfolio draft-debate-ds`
- `tradectl portfolio decide`
- `tradectl portfolio preview`

建议顺序：

1. `package`
2. `debate`
3. `draft-debate-ds`
4. `decide`
5. `preview`

其中 `debate` 负责先把当前 package 压成 AI-ready 的 per-account debate package 与 prompt scaffold，只提供市场、持仓、cash、delta exposure、政策约束、theme、technical、risk flags 等事实和约束；`draft-debate-ds` 负责生成每个账户的最终 PM-facing 辩论正文；`decide` 再根据 debate 后的判断生成 rebalance proposal；`preview` 最后把同一轮决策编译成每个账户自己的执行预览。

`draft-debate-ds` 负责消费：

- `debate_reports/*.json`
- `debate_reports/*.package.md`

并调用外部 writer model 生成最终 PM-facing 辩论正文 markdown。默认会对最新日期下的每个账户 artifact 各写一份 `debate_<date>.<account_number>.ds.md`。

同一份 debate artifact 也可以喂给本地独立的 Cursor GPT-5.4 writer。
此时应沿用来自 `09_soul` 的 system posture：

- direct
- pragmatic
- restrained
- evidence-first
- no editorial meta

## Evaluation Loop

如果没有评估闭环，这一层会退化成“看起来很像 PM 的文本系统”。

后续版本应补：

- 输入快照留档
- 最终建议留档
- 是否被采纳
- 后续表现
- 错误归因

这样才能逐步从工作台助手进化为可校准的决策系统。
