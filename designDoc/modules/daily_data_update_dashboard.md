# Daily Data Update Dashboard

## Purpose

`DailyDataUpdateDashboard` 是一个跨层的 operator truth surface。

**Normative distinction:** this dashboard is a **workflow gate** (refresh completeness / blocking), not the semantic definition of “last trading session” for mixed calendars. For raw UTC timestamps, equity vs futures session boundaries, `generated_at` on artifacts, and ingestion independence from daily report, see [`../last_session_truth_and_ingestion_boundary.md`](../last_session_truth_and_ingestion_boundary.md).

它不负责写研究，不负责写 PM 结论，也不负责替代各层自己的 domain object。

它只负责回答一件事:

- 今天用于下游 package / report 的数据层，哪些已经更新
- 哪些仍然 stale / missing / error
- 这些问题是否应该直接阻断下游生成

Time rule for this layer:

- the dashboard may summarize readiness with business-date-style labels for operators
- the dashboard must not replace the underlying UTC data-layer timestamps
- the dashboard must not redefine per-asset `session_as_of`

## Why This Layer Exists

当前 repo 的 recap / package 问题不是单点缺 prompt，而是 upstream data freshness 没有统一状态面。

如果没有统一状态面，下游 builder 往往会出现三种坏行为:

- 临时重建某一层数据，但不知道其他层是否还是旧的
- 在依赖缺失时静默降级，把坏 section 写回 package
- 每个 builder 自己写一套 freshness 判断，口径越来越散

所以需要一个统一、可落盘、可被 CLI 和下游 builder 共同消费的 daily update surface。

## Canonical Artifacts

- JSON: `data/dashboard/daily_update_status.json`
- Markdown: `data/dashboard/daily_update_status.md`

这两个文件是 operator-facing surface，不是 domain truth archive。

## Place In The Overall Flow

总体流程应尽量拆成四段，而不是让一个 command 吞掉所有语义：

1. `data update`
2. `import / ingest`
3. `read / package assembly`
4. `analysis / reporting`

这里的 `DailyDataUpdateDashboard` 只服务第 1 段，并为第 3 段提供 gate。

它不是第 2 段的归档 schema，也不是第 4 段的分析输出。

## What `data update` Is

`tradectl data update` 现在应被理解为 umbrella command。

它负责：

- 驱动若干 deterministic refresh action
- 可选地触发轻量 research connector check，例如 AgentMail inbox polling
- 汇总三层 freshness / completeness / blocking
- 产出一个共享 status surface

它不负责：

- 代替完整的 research import / archive ingest workflow
- 代替 package builder 的内容拼装
- 代替 PM-facing analysis 和 report prose

这里的边界是：

- `data update` 可以顺手做轻量 connector poll，让 operator 看到当天是否有新邮件落盘
- 但 shared daily status surface 仍只把 `macro / technical / account` 作为 blocking freshness gate
- research archive 的对象语义、归档形态、以及后续 snapshot/theme/thesis routing 仍归 `research` workflow 负责

## Path Split

建议按职责理解当前 canonical path：

- update status surface:
  - `data/dashboard/daily_update_status.json`
  - `data/dashboard/daily_update_status.md`
- imported / refreshed truth artifacts:
  - `data/account/snapshots/`
  - `data/account/activity/raw/`
  - `data/account/activity/by_date/`
  - `data/macro/snapshots/`
  - `data/knowledge/asset_technicals/signal_packets/`
  - `data/knowledge/asset_technicals/reports/`
  - `data/research/messages/` and related AgentMail archive paths when email checking is enabled
- package assembly outputs:
  - `data/research/theme_update_drafts/*.package.md`
  - `data/account/weekly_review_packages/`
- analysis / report outputs:
  - `data/research/snapshots/*.ds.md`
  - `data/account/reports/daily/`
  - `data/account/reports/weekly/`

也就是说：

- `dashboard/` 管 workflow readiness
- `data/.../snapshots|raw|signal_packets` 管 truth surfaces
- `package.md` 管 writer input assembly
- `reports/` 和 `*.ds.md` 管 analysis output

其中时间语义再分三层:

- truth surfaces 保留精确 UTC 时间
- package assembly 承接 derived session semantics
- dashboard / reports 可以做 ET/PT/交易日表达

## Layer Model

当前统一三层:

- `macro`
- `technical`
- `account`

research email checks may run during `data update`, but they stay outside the three-layer blocking model above.

每层都输出:

- `status`
- `blocking`
- `summary`
- `artifacts`
- `details`
- `issues`

## Status Semantics

- `ok`: 当前层可直接用于下游
- `partial`: 有缺口，但不是当前下游的硬阻断
- `stale`: 数据老了，通常不应继续生成依赖它的下游结果
- `missing`: 必要 artifact 或输入不存在
- `error`: 更新或检查过程本身失败

`blocking` 比 `status` 更接近 workflow 决策。

因为:

- 某些 `partial` 可以继续，例如 technical 中已知的单资产 `data_status != ok`
- 某些 `stale` 必须阻断，例如 broker snapshot/activity 没有刷新到今天

## Current Policy

### Macro

- 缺 Postgres 依赖或核心 series 缺失: `blocking = true`
- 存在 stale inputs 但 snapshot 仍可读: `blocking = false`

### Technical

- `core assets` 若未 runtime-enable、缺 signal packet、或 signal packet 未到 expected date: `blocking = true`
- theme coverage 中没有 manual profile 的资产，应先自动生成 minimal runtime profile，再进入 daily refresh；manual profile 仍优先于 generated profile
- 最新账户持仓里的底层标的也应自动进入 coverage；期权持仓只纳入其 underlying，不把期权合约本身塞进 technical runtime
- dashboard 应区分 `manual profiles`、`generated profiles`、和 `not runtime-enabled`，而不是把所有长尾 theme 资产都表述成刷新失败
- operator-facing `technical tunnel` / `composition` 应进一步区分 admission 来源，至少看得出 `theme admitted`、`account holding admitted`、以及二者重叠
- 对已经进入 runtime 的非核心资产，AI summary 缺失或 `data_status != ok` 先记为 `partial`
- 也就是说，technical layer 的阻断应主要由核心资产和已启用 runtime 的资产驱动，而不是由整个 coverage universe 一票否决
- operator dashboard 还应产出一个 `technical index` 静态页，并为每个 runtime asset 生成可点击的单资产图页；核心资产应能从主 dashboard 直接点入
- `data update` 内的 technical refresh 不能只重建 signal packets。它应先按 runtime-enabled technical universe 刷新底层 price history（至少 `30m` 与 `1d` 原始 bars），再重建 signal packets / technical index，最后才可选刷新 AI-written summaries。
- 如果 signal packet 的 `report_date` 已进入当前 live session，但底层 raw price bars 仍停在更早日期，这应被视为 technical-refresh implementation drift，而不是下游 package / report 层的问题。
- `strict_time_check` 必须跟随真实的 session policy。`fx_proxy`、`macro_proxy`、`commodity_spot` 在专门 policy 落地前，不能默认套用 XNYS equity 的 `14:00/14:30 ET` 30m bar 要求。
- provider-specific 的 intraday API 边界也必须在 loader 层被显式尊重；例如 Yahoo `30m` 只能回看有限窗口，不能继续沿用通用的 400 天请求范围。

### Account

- 当日 snapshot 未刷新: `blocking = true`
- 当日 raw activity 未刷新: `blocking = true`

## CLI Surface

- `tradectl data status`
- `tradectl data update`

`data update` 的目标不是写最终 report，而是先把底层 refresh 和状态面收敛好。

## Downstream Gate Rule

下游 package / report pipeline 应先消费 shared status，再决定是否继续。

当前已接入:

- `assemble-market-observation-package`
- `build_theme_writer_package`
- `tradectl account-review daily`
- `tradectl account-review weekly`
- `tradectl account-review weekly-ds`

## Boundary Rule

`DailyDataUpdateDashboard` 是 workflow control surface，不是业务内容 surface。

它应该:

- 描述 freshness / completeness / blocking
- 提供 artifact path
- 给下游 deterministic gate
- 保留“这是 gate，不是时间真相”的边界

它不应该:

- 直接写 PM prose
- 直接代替 macro snapshot / signal packet / account journal 自己的 domain schema
- 在 builder 内偷偷做最终判断然后不留下状态痕迹
- 混入 import / package assembly / analysis 的对象语义
- 用 ET/PT/local wording 取代底层 UTC 时间字段
