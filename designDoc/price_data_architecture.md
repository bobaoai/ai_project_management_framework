# Price Data Architecture

**Version 0.1 — 2026-03-26**

本文档是 `trading_platform` 中 `price` 这一类市场数据的唯一主规则文档。

它负责：

- quotes / bars / mark / close 的对象定义
- freshness、coverage、provenance
- provider precedence for price
- futures contract selection and roll policy
- 价格数据的运行时消费边界

它不负责 fundamentals 对象与 statement 语义。

---

## 1. Purpose

价格数据和基本面数据不应混写。

`price` 的核心问题是：

- 时序
- 频率
- freshness
- continuity
- futures 合约切换
- intraday 与 end-of-day 的差异

这些问题与 fundamentals 的 statement date / filing date / point-in-time 语义完全不同，因此必须单独成文。

---

## 2. Scope

本文件覆盖：

- latest quote
- end-of-day price
- historical bars
- intraday bars
- normalized mark / close surfaces
- futures contract identity
- roll windows
- price-source precedence
- price coverage status

本文件不覆盖：

- company profile
- key stats
- financial statements
- filing metadata

这些交给 [`research_33_company_fundamentals_data_architecture.md`](research_33_company_fundamentals_data_architecture.md)。

---

## 3. Canonical Price Objects

## 3A. Time Contract

Price data time semantics must stay split into distinct layers.

### Raw UTC instant (canonical data-layer rule)

Persist these as precise UTC instants:

- `quote_time`
- `as_of`
- `bar_start`
- provider-native timestamps
- ingest timestamps

Normative rule:

- the data layer keeps exact UTC instants
- ET/PT/local session wording is downstream render logic
- do not wash ingestion rows into ET-first storage just to make daily labels look easier

### Session-semantic field

Price objects may additionally carry or feed derived fields such as:

- `session_as_of`
- `session_date_utc`
- exchange/session policy ids

These are not replacements for raw UTC timestamps.
They are market-semantic interpretations built from UTC instants plus session policy.

### Human/render labels

`report_date`, “post-close”, “上一交易日”, ET/PT-local labels, and similar wording belong to report or dashboard surfaces.

They may summarize a data object for readers, but they are not canonical time truth for ingestion or storage.

### 3.1 QuoteSnapshot

用于当前价格观察。

最小字段建议：

- `symbol`
- `asset_type`
- `provider`
- `provider_symbol`
- `price_kind`
- `price`
- `bid`
- `ask`
- `mark`
- `quote_time`
- `as_of`
- `session_type`
- `is_realtime`
- `metadata`

Time rule:

- `quote_time` and `as_of` should remain UTC instants in storage
- if a consumer needs an ET/PT-local display, derive it at render time
- if a consumer needs “which completed market session does this quote belong to,” derive that separately instead of overloading `quote_time`

### 3.2 BarSeries

用于历史时间序列。

最小字段建议：

- `symbol`
- `provider`
- `provider_symbol`
- `interval`
- `bar_start`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `trades`
- `as_of`

Time rule:

- `bar_start` and `as_of` remain precise UTC instants in storage
- daily bars may additionally expose a derived `session_date_utc` or session-policy field
- downstream consumers must not infer a bar's semantic session solely from a display label when the raw UTC instant is already present

### 3.3 PriceResolution

用于回答“这个时点系统最终采用哪个价格”。

最小字段建议：

- `symbol`
- `field_name`
- `resolved_value`
- `resolved_from_provider`
- `resolved_from_object`
- `resolved_at`
- `freshness_bucket`
- `confidence`
- `notes`

### 3.4 FuturesContractSpec

用于期货合约解析与 roll。

最小字段建议：

- `contract_root`
- `canonical_symbol`
- `provider_symbol`
- `month_code`
- `year_code`
- `expiry_date`
- `last_trade_date`
- `first_notice_date`
- `contract_family`
- `is_active_contract`
- `roll_priority`

---

## 4. Provider Roles For Price

当前建议：

- `Schwab`：优先承担 broker-adjacent quotes / bars / account-linked market context
- 未来其他 price provider：承担 Schwab 不支持或质量不足的价格面
- futures price path：单独建模，不强行假设与 current `Schwab REST quote/history` 同构

### Provider precedence principle

价格 precedence 应按字段和 use case 决定，而不是按 provider 一刀切。

示例：

- intraday equity quote：可优先 `Schwab`
- daily bars：可优先当前最稳定 provider
- futures live quote：若 `Schwab REST` 不通，应切到专用 futures path
- PM-facing snapshot close：优先采用最可验证的 close source，而不是最新但不稳定的 mark

---

## 5. Freshness And Coverage

价格系统必须显式区分：

- `live`
- `delayed`
- `eod`
- `historical_backfill`
- `stale`
- `missing`

不能只回答“有没有价格”，还要回答：

- 这个价格是哪一类价格
- 这个价格来自哪个 provider
- 这个价格是不是当前 use case 可接受的 freshness

### Coverage split

coverage 至少要按：

- `symbol`
- `interval`
- `provider`
- `status`

记录，而不是只记录一个笼统的 “ok / error”。

这与 [`postgres_ticker_coverage_design_v0_1.md`](postgres_ticker_coverage_design_v0_1.md) 一起工作，但 provider-specific price rules 以本文件为准。

---

## 6. Futures Contract Policy

期货不能被当作普通 spot/equity symbol。

系统必须显式维护：

- root symbol
- contract month
- year code
- active contract rule
- roll buffer
- provider symbol mapping

### Default contract-family rules

#### Equity index and rates

适用于：

- `ES`
- `NQ`
- `ZN`

默认规则：

- 使用季度合约 `H/M/U/Z`
- 默认选择当前最活跃的 nearby quarter
- 接近到期或明显流动性切换时滚到下一季度

#### Monthly energy

适用于：

- `CL`
- `BZ`

默认规则：

- 按月合约维护
- 不把“front month”与“分析主力合约”简单等同
- 默认在 expiry 前约 `5-7` 个交易日开始滚动

#### Metals

适用于：

- `GC`

默认规则：

- 选择活跃流动性月份
- 不假设每个月都应追最前月
- 分析序列和交易观察窗可允许不同 contract preference

#### Volatility futures

适用于：

- `VX`

默认规则：

- 保留 front month 与 second month 观察窗
- 不把单一 front month 直接当作完整 risk proxy

### Key principle

系统最终应保存两层符号：

- canonical contract identity
- provider-local tradable symbol

不能把 provider symbol 直接当成平台永久主键。

---

## 7. Current Repo Implication

当前 repo 的现实状态是：

- `src/core/schwab_client.py` 提供 REST quote/history methods
- `src/market_data/history_loader.py` 是当前最完整的 price ingestion 路线
- `src/market_data/price_cache.py` 还停留在迁移 stub
- plain root `ES` 这类 symbol 仍会误命中股票 `ES / EVERSOURCE ENERGY`，因此不能把非 slash root 当作 futures path
- `Schwab REST` 对 slash-root futures symbol 已证明可用，例如 `'/ES'`、`'/NQ'`、`'/CL'`、`'/GC'` 可返回 `FUTURE` quote 和约一年 `1d` history
- 当前 `'/ES'` 与 `'/ESM26'` 返回的 `1d` history 表现接近 provider-managed front-contract / continuation path，而不是完整已验证的逐合约历史库
- `/ESH25`、`/ESU25` 这类非当前季度 contract-specific history 仍未被当前 Schwab path 证明可用

因此下一步不应是继续在旧 price cache 上堆 patch，而应先建立：

- canonical price abstraction
- futures contract resolver
- provider precedence rules
- slash-root continuation history 与 contract-specific history 的明确分层
- futures family profile 与 root-specific profile 的两层配置
- non-slash root-history candidate 的 asset-class guardrail

---

## 8. Cleanup Targets

后续 price-related 清理优先看：

- `src/market_data/price_cache.py`
- `src/market_data/history_loader.py`
- `src/core/schwab_client.py`

目标不是“删旧代码”，而是让这些文件重新对齐到同一 price truth surface。

---

## 9. Consumer Rule

analysis consumer 不应直接依赖：

- provider raw payload shape
- provider-local symbol formatting
- connector sync state

它应依赖：

- normalized quote view
- normalized bar view
- explicit freshness / provenance metadata
- explicit futures contract resolution result
- raw UTC timestamps plus separate session-semantic fields when market-session interpretation matters
