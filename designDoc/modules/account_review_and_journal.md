# Account Review And Journal

## Purpose

`AccountReviewAndJournal` 负责把 broker truth surfaces 组织成可复盘的日度/周度工作面。

它不是 connector 本身，也不是 portfolio exposure 的替代品。

## Main Boundary

这一模块需要严格区分两层：

- `truth/static archive`
- `analytic report/editable draft`

建议的第一版路径：

- truth:
  - `data/account/snapshots/`
  - `data/account/activity/raw/`
  - `data/account/activity/by_date/`
  - `data/account/journals/`
  - `data/account/weekly_review_packages/`
- editable reports:
  - `data/account/reports/daily/`
  - `data/account/reports/weekly/`

也就是说：

- `json` truth files 负责回答“到底发生了什么”
- `md` report files 负责承载“我怎么看、我怎么复盘、我之后怎么改进”

## Responsibilities

- 拉取并保存 broker orders / transactions / account snapshots
- 归一化为 stable local objects
- 形成日度 account journal
- 聚合为周度 review package
- 生成可持续编辑的日报和周报工作稿

## Inputs

- Schwab account snapshots
- Schwab orders
- Schwab transactions
- local position history
- operator-triggered review commands

## Outputs

- raw broker activity archives
- normalized activity-by-date files
- daily account journals
- weekly review packages
- editable markdown daily / weekly reports

## Shared Update Gate

`AccountReviewAndJournal` 现在不应只依赖“本地刚好有文件”这种弱判断。

在进入:

- `daily`
- `weekly`
- `weekly-ds`

这些下游生成动作前，应先读取 shared daily update status surface:

- `data/dashboard/daily_update_status.json`

当前 account-layer gate 重点看两件事:

- 当日 position snapshot 是否已刷新
- 当日 raw activity refresh 是否已刷新

如果这两项没有到位，weekly / daily review 不应继续生成一个看起来完整但实际基于旧 broker truth 的复盘稿。

## Truth Rule

truth layer 应尽量稳定、少改 schema、避免夹带写作语气。

例如：

- order rows
- transaction rows
- position changes
- account value deltas
- machine notes with explicit provenance

这些可以随着 parser 变强而重算，但不应该被人工润色稿反向覆盖。

## Editable Report Rule

日报和周报 markdown 可以被持续修改、改标题、改结构、补主观判断。

但它们不应成为：

- transaction truth source
- position truth source
- account delta truth source

也不应驱动回写 broker facts。

## Relationship To Other Modules

- `DataCollection` 负责 fetch 和 raw archive
- `PortfolioExposure` 消费 snapshots 和 journals 形成组合上下文
- `StructuredAdvice` 可以再消费 weekly review package 形成更正式 memo

## Human-In-The-Loop Boundary

人主要负责：

- 解释自己的交易意图
- 写反思
- 判断哪些操作是纪律问题、哪些是正确试错

系统主要负责：

- fetch
- normalize
- diff
- aggregate
- 起草 report skeleton

## Notes

- 第一版允许 attribution 近似，不必假装精确 realized/unrealized decomposition 已完全解决
- 重点先做到：可追溯、可周度复盘、可持续积累行为样本
