---
title: "Ingestion Domain: Market Data"
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
  - Analysis Platform Builder
---

# Ingestion Domain: Market Data

## 1. 这份文档负责什么

本文件定义 Market Data 信息域的 ingestion 边界：价格历史、经济事件、实时 connector、以及 MCP plugin data connectors 的获取渠道、tagging、archive 策略和质量边界。

本文件不负责：

- 价格数据的 canonical schema 设计（`price_data_architecture.md`）
- 技术分析或 signal 生成（那是 AnalysisPlatform）
- Macro series 归 Fed 域（ingestion_61）管辖的部分（FRED, NY Fed, Treasury）

边界划分原则：
- **Fed 域 (61)** owns 所有由 Fed / Treasury 官方发布的 rates 和 macro series
- **Market Data 域 (64)** owns 市场参与者的 price action、broker data、economic event calendars、以及 third-party data provider connectors

---

## 2. Sources in Scope

| # | Source | 数据性质 | 接入验证 |
|---|--------|---------|---------|
| 1 | Schwab price history | OHLCV bars | ✓ operational（broker API） |
| 2 | Yahoo Finance chart data | OHLCV bars | ✓ operational |
| 3 | EODHD economic events | 结构化 event calendar | ✓ operational |
| 4 | EODHD fundamentals | 结构化 (supplement) | partial |
| 5 | CBOE VIX history | 时间序列 | ✓ operational |
| 6 | TradingView News | 叙事 (market news) | ✓ operational |
| 7 | MCP: FactSet | 多种（estimates, fundamentals, news） | blocked（paid） |
| 8 | MCP: S&P / Kensho | 结构化 analytics | blocked（paid） |
| 9 | MCP: Moody's | credit / fixed income | blocked（paid） |
| 10 | MCP: PitchBook | private markets / M&A | blocked（paid） |
| 11 | MCP: Morningstar | fund / ETF analytics | blocked（paid） |
| 12 | MCP: LSEG | multi-asset analytics | blocked（paid） |
| 13 | MCP: Daloopa | structured financials | blocked（paid） |
| 14 | MCP: Aiera | earnings transcripts / events | blocked（paid） |
| 15 | MCP: MT Newswires | real-time news | blocked（paid） |
| 16 | MCP: Chronograph | PE / alternatives | blocked（paid） |
| 17 | MCP: Egnyte | document management | blocked（paid） |

---

## 3. Connector per Source

### 3.1 Schwab price history

```yaml
connector: Schwab Broker API
implementation: existing broker integration (src/)
auth: OAuth2 (Schwab developer account)
data: OHLCV daily/intraday bars, options chain
status: ✓ operational
tripwire: auth error → stop + re-authenticate (R11)
```

### 3.2 Yahoo Finance chart data

```yaml
connector: yfinance library
method: yfinance.Ticker(<symbol>).history(period=...)
auth: none
data: OHLCV daily bars, dividends, splits
status: ✓ operational
limitation: delayed quotes; no real-time; throttled at volume
```

### 3.3 EODHD economic events

```yaml
connector: EODHD API
url: https://eodhd.com/api/economic-events
auth: API key (env: EODHD_API_KEY)
data: scheduled economic releases (NFP, CPI, GDP, etc.) with actual/estimate/prior
status: ✓ operational
```

### 3.4 EODHD fundamentals (supplement)

```yaml
connector: EODHD API
url: https://eodhd.com/api/fundamentals/<symbol>
auth: API key
data: financial statements, profile, key stats
status: partial — supplements yfinance for non-US / edge cases
role: secondary to yfinance (ingestion_62 primary)
```

### 3.5 CBOE VIX history

```yaml
connector: CBOE CSV download
implementation: src/macro_data/public_sources.py
url: cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv
auth: none
data: daily VIX close
status: ✓ operational
```

### 3.6 TradingView News

```yaml
connector: TradingView worker
implementation: src/connectors/tv_news/
data: market news headlines, sentiment signals
status: ✓ operational
archive: DB + local archive
```

### 3.7 MCP Plugin Connectors

```yaml
connector: MCP (Model Context Protocol) remote servers
configuration: ~/.claude/plugins/cache/claude-for-financial-services/financial-analysis/0.1.0/.mcp.json
protocol: HTTP-based tool invocation via MCP SDK
auth: per-provider subscription required
status: all blocked (installed but no active subscriptions)
```

Installed MCP servers:

| Provider | URL | Capability |
|----------|-----|------------|
| Daloopa | mcp.daloopa.com | Structured financials extraction |
| Morningstar | mcp.morningstar.com | Fund/ETF analytics, ratings |
| S&P / Kensho | kfinance.kensho.com | Market intelligence, analytics |
| FactSet | mcp.factset.com | Estimates, fundamentals, ownership |
| Moody's | api.moodys.com | Credit, fixed income research |
| MT Newswires | vast-mcp.blueskyapi.com | Real-time market news |
| Aiera | mcp-pub.aiera.com | Earnings transcripts, event monitoring |
| LSEG | api.analytics.lseg.com | Multi-asset analytics |
| PitchBook | premium.mcp.pitchbook.com | Private markets, M&A, VC |
| Chronograph | ai.chronograph.pe | PE, alternatives performance |
| Egnyte | mcp-server.egnyte.com | Document management |

Upgrade path: 当订阅激活后，MCP connectors 可直接在 Claude Code session 中通过 tool use 调用。数据通过 MCP protocol 返回结构化 JSON，可直接入 pool。

---

## 4. Tagging Rules

```yaml
domain: market_data
source_class: <per source below>
```

| Source | source_class | non-time tags |
|--------|-------------|--------------|
| Schwab bars | `price_history` | `ticker`, `timeframe`, `exchange` |
| Yahoo bars | `price_history` | `ticker`, `timeframe` |
| EODHD events | `economic_event` | `event_type`, `country` |
| EODHD fundamentals | `company_fundamentals_supplement` | `ticker` |
| VIX | `volatility_index` | `index_id=VIX` |
| TV News | `market_news` | `tickers[]` |
| MCP data | `mcp_<provider>` | `provider`, `query_type`, `tickers[]` |

### 4.1 Timestamp semantics compliance

所有时间相关值遵守 `the_timestamp_semantic.md`（`<role>_<storage>` 命名）。不引入裸 `release_date` / `headline_date` tag。

| source_class | 时间锚字段 | 对应 §4 matrix class |
|---|---|---|
| `price_history` (bar) | `period_start_at_utc` / `period_end_at_utc` | `kbar_*`（REQ + REQ） |
| `price_history` (tick) | `observed_at_utc` | `tick`（REQ） |
| `economic_event` | `observed_at_utc`（release instant）或 `scheduled_for_at_utc`（pre-release） | 需 §4 登记 |
| `volatility_index` | `period_start_at_utc` / `period_end_at_utc`（daily bar） | `kbar_1d` |
| `market_news` | `observed_at_utc`（headline publication） | 需 §4 登记 |
| `mcp_<provider>` | `observed_at_utc`（query result timestamp） | per-query class TBD |

`recorded_at_utc` 全局必填（R1）。

**待登记**：`economic_event` 和 `market_news` 尚未在 timestamp contract §4 矩阵注册。实现 connector 时需先添加 class 行再写 schema。建议 matrix 行：

```
economic_event:  observed_at REQ, scheduled_for_at OPT, recorded_at REQ, 其余 —
market_news:     observed_at REQ, recorded_at REQ, 其余 —
```

---

## 5. Archive Policy

### 5.1 Price history

```
data/hist/<ticker>/daily.json (or .csv)
data/hist/<ticker>/intraday/<date>.json
```

由 `price_data_architecture.md` 定义 schema。Append-only per day。

### 5.2 Economic events

```
data/macro/events/<yyyy>/<event_type>_<date>.json
```

或由 `src/macro_data/` 管理为统一 macro store。

### 5.3 VIX / volatility indices

```
data/macro/vix/daily.json
```

### 5.4 Market news

```
DB (TradingView worker)
Archive: periodic dump to data/knowledge/market_news/ (if needed for replay)
```

### 5.5 MCP connector data

MCP 数据是 session-level 查询结果。Archive policy：

- 如果查询结果用于 report 或 thesis，persist 到对应的 research archive
- 如果是 ad-hoc lookup，不强制 archive（tool result 在 conversation 中已 captured）
- 重要 snapshot（如 earnings estimates pre-report）应 persist 到 `data/knowledge/`

---

## 6. Freshness Rules

| Source | Refresh cadence | Staleness threshold |
|--------|----------------|---------------------|
| Schwab bars | Daily after market close | 1 business day |
| Yahoo bars | Daily (delayed 15-20 min) | 1 business day |
| EODHD events | Pre-release (1 day before scheduled event) | Event day |
| VIX | Daily | 1 business day |
| TV News | Continuous (worker-based) | Real-time |
| MCP queries | On-demand (no scheduled refresh) | Session-scoped |

---

## 7. Known Gaps & Fallbacks

| Gap | Impact | Fallback | Priority |
|-----|--------|----------|----------|
| MCP connectors all blocked | 无法获取 institutional-grade estimates, credit, PE data | yfinance + SEC filings + manual | 中 |
| Yahoo delayed quotes | 无 real-time intraday | Schwab API for real-time（auth required） | 低 |
| Options data limited | Yahoo options chain incomplete | Schwab options chain | 低 |
| Futures continuous contract | Roll logic not automated | Manual or Schwab futures | 低 |
| News sentiment scoring | TV News 有 headlines 但无 systematic sentiment | Future: LLM-based sentiment pipeline | 低 |

MCP connector upgrade path:
1. Identify highest-value provider for current coverage (likely FactSet for estimates, Aiera for transcripts)
2. Subscribe → auth → MCP connector auto-activates
3. Data flows directly through Claude Code tool use into session

---

## 8. Quality Boundary

Market Data 域的可信度分级：

| Level | 条件 | 下游 permission_level |
|-------|------|----------------------|
| **Exchange official** | Schwab / exchange-sourced OHLCV | `publicly_observable` |
| **Delayed official** | Yahoo Finance delayed quotes | `publicly_observable`（15-20min delay noted） |
| **Scheduled release** | EODHD economic events (NFP, CPI) | `publicly_observable` post-release |
| **Third-party derived** | VIX (CBOE calculated), EODHD analytics | `publicly_observable` |
| **News / sentiment** | TV News headlines | `market_intelligence`（not primary source） |
| **MCP provider** | FactSet / S&P / Moody's data | `institutional_data`（provider-sourced, auditable） |

核心约束：

1. Price data 是 factual（exchange-cleared）——它不需要 interpretation 就可以作为 evidence。
2. Economic events 在 release 后是 `publicly_observable`；release 前的 estimates 是 consensus forecast，不是 fact。
3. MCP provider data 的质量取决于 provider methodology。FactSet estimates 是 consensus aggregation；Moody's ratings 是 opinion。下游 expert 需区分 data fact vs provider opinion。
4. News headlines 是 signal，不是 evidence。不能用 headline 作为 thesis 的 sole support。

---

## 9. 与相邻文档的关系

| Doc | 关系 |
|-----|------|
| `ingestion_00_overview.md` | 本文是其下的域子文档 |
| `ingestion_61_fed_domain.md` | Fed official rates/series 归 61 域；本域不重复 |
| `ingestion_62_company_domain.md` | Company fundamentals 归 62 域；EODHD fundamentals 在本域仅作 supplement |
| `price_data_architecture.md` | 价格数据 schema authority |
| `src/macro_data/public_sources.py` | VIX 实现在这里 |
| `src/connectors/tv_news/` | TV News connector 实现 |
| MCP plugin config | `~/.claude/plugins/cache/.../financial-analysis/.mcp.json` |
