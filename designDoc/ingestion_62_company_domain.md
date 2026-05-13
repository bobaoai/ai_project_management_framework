---
title: "Ingestion Domain: Company"
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
  - Analysis Platform Builder
---

# Ingestion Domain: Company

## 1. 这份文档负责什么

本文件定义 Company 信息域的 ingestion 边界：SEC filings、earnings transcripts、company fundamentals、IR releases 的获取渠道、connector 模式、tagging、archive 策略、freshness、gap 与质量边界。

本文件不负责：

- 对公司财务的解读或 thesis 生成（digestion expert）
- 决定哪个 expert 消费哪份材料（digestion_31 routing）
- Fundamentals 的 canonical schema 设计（`ingestion_33_company_fundamentals_data_architecture.md`）
- Newsletter / 外部 research 对公司的讨论（那属于 ingestion_63 Research Newsletter 域）

---

## 2. Sources in Scope

| # | Source | 数据性质 | 接入验证 |
|---|--------|---------|---------|
| 1 | SEC EDGAR 10-K / 10-Q | 叙事 + 结构化 | planned（public API） |
| 2 | SEC EDGAR 8-K | 叙事 | planned（public API） |
| 3 | Earnings call transcripts | 叙事 T1 | planned（SEC exhibit → IR → Aiera MCP） |
| 4 | Quarterly / annual financials | 结构化 | prototype（yfinance verified） |
| 5 | Company profile & key stats | 结构化 | partial（yfinance / EODHD） |
| 6 | Company IR press releases | 叙事 | future |
| 7 | Proxy statements (DEF 14A) | 叙事 | future |

---

## 3. Connector per Source

### 3.1 SEC EDGAR filings (10-K / 10-Q / 8-K)

```yaml
connector: SEC EDGAR full-text API
base_url: https://efts.sec.gov/LATEST/search-index?q=*&dateRange=custom
filing_url: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<cik>&type=<form_type>
auth: none (public, rate-limited to 10 req/sec with User-Agent header)
user_agent_required: "trading_platform bb576@cornell.edu"
parse: HTML filing → section extraction (MD&A, Risk Factors, Financial Statements)
status: planned
implementation_target: src/connectors/sec_edgar.py
```

EDGAR access rules:
- Must include descriptive User-Agent with contact email
- Max 10 requests per second
- Full-text search API available for targeted filing discovery
- Filing index via company CIK lookup

### 3.2 Earnings call transcripts

```yaml
connector: multi-path with fallback chain
path_1: SEC 8-K exhibit (some companies file transcript as exhibit)
path_2: Company IR website → WebFetch
path_3: Aiera MCP connector (plugin installed, needs auth)
path_4: Manual transcript drop
auth: varies
status: planned
```

Fallback chain:
1. Check SEC EDGAR for 8-K exhibit containing transcript → free, T1
2. Check company IR page for transcript PDF/HTML → free, T1
3. Aiera MCP connector → paid subscription required
4. Manual file drop → operator-provided

### 3.3 Quarterly / annual financials

```yaml
connector: yfinance (primary free path)
implementation: src/connectors/yahoo_fundamentals.py (to build)
method: yfinance.Ticker(<symbol>).quarterly_financials / .quarterly_balance_sheet / .quarterly_cashflow
auth: none
rate_limit: informal (no hard API key, but throttled at high volume)
status: prototype verified
```

yfinance provides:
- Income statement (quarterly + annual)
- Balance sheet (quarterly + annual)
- Cash flow statement (quarterly + annual)
- Earnings history (EPS actual vs estimate)
- Key statistics (market cap, P/E, P/B, EV, etc.)

Limitations:
- No point-in-time audit trail (only latest restated values)
- No filing-date linkage
- Occasional data gaps for non-US securities
- Rate throttling under heavy use

### 3.4 Company profile & key stats

```yaml
connector: yfinance (primary) / EODHD (supplemental)
method: yfinance.Ticker(<symbol>).info
auth: EODHD requires API key (env: EODHD_API_KEY)
status: partial
```

### 3.5 Company IR press releases

```yaml
connector: Per-company WebFetch
challenge: IR page structure varies widely; no universal API
status: future
next_step: template per coverage-list company (start with healthcare CRO/pharma)
```

### 3.6 Proxy statements (DEF 14A)

```yaml
connector: SEC EDGAR (same as 3.1)
status: future — low priority unless governance thesis active
```

---

## 4. Tagging Rules

```yaml
domain: company
source_class: <per source below>
ticker: <uppercase symbol>
```

| Source | source_class | non-time tags |
|--------|-------------|--------------|
| 10-K | `company_annual_filing` | `cik` |
| 10-Q | `company_quarterly_filing` | `cik` |
| 8-K | `company_event_filing` | `event_items[]` |
| Earnings transcript | `company_earnings_transcript` | `quarter`, `fiscal_year` |
| Quarterly financials | `company_fundamentals` | `statement_type` |
| Key stats | `company_key_stats` | — |
| IR releases | `company_ir_release` | `release_type` |
| Proxy | `company_proxy` | — |

### 4.1 Timestamp semantics compliance

所有时间相关值遵守 `the_timestamp_semantic.md`（`<role>_<storage>` 命名，禁裸日期 tag）。

| source_class | 时间锚字段 | 对应 §4 matrix class |
|---|---|---|
| `company_annual_filing` | `observed_at_utc`（filing date）+ `period_start_at_utc` / `period_end_at_utc`（fiscal year） | `archive_message` |
| `company_quarterly_filing` | `observed_at_utc`（filing date）+ `period_start_at_utc` / `period_end_at_utc`（fiscal quarter） | `archive_message` |
| `company_event_filing` | `observed_at_utc`（filing date） | `archive_message` |
| `company_earnings_transcript` | `observed_at_utc`（call date） | `archive_message` |
| `company_fundamentals` | `period_start_at_utc` / `period_end_at_utc`（fiscal period） | `fundamentals_snapshot` |
| `company_key_stats` | `observed_at_utc`（snapshot time） | `fundamentals_snapshot` variant |
| `company_ir_release` | `observed_at_utc`（release publication） | `archive_message` |
| `company_proxy` | `observed_at_utc`（filing date） | `archive_message` |

Filing 类 record 使用 `observed_at_utc` 记录 SEC filing date（事件在外部世界发生的时刻），使用 `period_start_at_utc` / `period_end_at_utc` 记录 fiscal period coverage。两者必须共存于 SEC filing record 上——filing date ≠ period end。

`recorded_at_utc` 全局必填（R1）——connector 写入 archive 的时刻。

**Date-level observed fallback**：SEC filing date 通常只精确到日（EDGAR 给 `filed` 日期不给时刻）。按 contract §3.1 date-level 规则：`observed_precision: "date"`，`observed_at_utc` 写 ET 23:59:59 投影到 UTC。

---

## 5. Archive Policy

Company 域 output 按数据性质分流：

### 5.1 叙事类（filings, transcripts, IR releases）

```
data/research/messages/sec_<ticker>_<form_type>_<yyyymmdd>/
  ├── message.json          (archive metadata)
  ├── raw_filing.html       (raw SEC HTML)
  ├── read_content.md       (canonical read surface)
  └── sections/             (optional: extracted MD&A, Risk Factors, etc.)
```

Earnings transcripts:
```
data/research/messages/earnings_<ticker>_Q<n>_FY<yy>/
  ├── message.json
  ├── raw_transcript.txt
  └── read_content.md
```

叙事类遵守 `ingestion_20` archive object contract 和 `ingestion_30` read content contract。

### 5.2 结构化类（financials, key stats）

```
data/knowledge/company_fundamentals/<ticker>/
  ├── quarterly_income.json
  ├── quarterly_balance_sheet.json
  ├── quarterly_cashflow.json
  ├── earnings_history.json
  ├── key_stats.json
  └── profile.json
```

Schema 由 `ingestion_33_company_fundamentals_data_architecture.md` 定义。

---

## 6. Freshness Rules

| Source | Refresh cadence | Staleness threshold |
|--------|----------------|---------------------|
| 10-K | Annual（filing season: Feb-Apr） | 30 days after expected filing |
| 10-Q | Quarterly（~40 days post-period-end） | 14 days after expected filing |
| 8-K | Event-driven | 3 days after filing |
| Earnings transcript | Quarterly（earnings day + 1-2 days） | 7 days after earnings date |
| Quarterly financials | Quarterly（after 10-Q/10-K filing） | 14 days after filing |
| Key stats | Weekly or on-demand | 7 days |
| IR releases | Event-driven | 3 days |

---

## 7. Known Gaps & Fallbacks

| Gap | Impact | Fallback | Priority |
|-----|--------|----------|----------|
| Earnings transcript 无免费统一 API | 覆盖面受限于 SEC 8-K exhibit availability | IR page WebFetch → Aiera MCP (paid) | 高 |
| yfinance 无 point-in-time | 无法判断何时数据被 restated | 用 filing_date 做 proxy 时间锚 | 中 |
| SEC EDGAR rate limit | 大批量 backfill 受限 | 分时段 backfill + CIK 预缓存 | 低 |
| IR page 结构非标 | 无法写通用 parser | Per-company template（coverage list 小） | 中 |
| Non-US companies | yfinance 数据可能缺失 | EODHD 补充 | 低 |
| MCP connectors (FactSet, S&P, Moody's) | 高质量 point-in-time data | 需付费订阅；当前 blocked | 中（升级路径） |

---

## 8. Quality Boundary

Company 域数据的可信度分级：

| Level | 条件 | 下游 permission_level |
|-------|------|----------------------|
| **T1 — Primary disclosure** | SEC filing (10-K/10-Q/8-K) 或 official earnings release | `publicly_observable` |
| **T1 — Official transcript** | 公司 IR 发布的 earnings call transcript | `publicly_observable` |
| **T1-adjacent** | Third-party transcript (Aiera, SeekingAlpha) 与 filing 数字一致 | `publicly_observable` 但标注来源 |
| **Derived — Provider** | yfinance / EODHD 聚合的 quarterly financials | `publicly_observable`（数字源头是 filing） |
| **Derived — Calculated** | Key stats (P/E, EV/EBITDA) 含 market price component | `publicly_observable` 但 point-in-time 不稳定 |

质量边界的核心约束：

1. yfinance financials 是 restated values——如果 company 后续修正了数字，yfinance 反映的是最新版本，不是 originally reported。对需要 point-in-time 判断的场景（如 earnings surprise calculation），应额外引用 `earnings_history` 中的 surprise 数据。
2. Earnings transcripts 是 management 口述，含 forward-looking statements。下游 expert 应区分 reported fact vs management outlook。
3. SEC filings 是 legal documents，数字是 audited（10-K）或 reviewed（10-Q）。这是 fundamentals 的最终 authority。
4. yfinance 不提供 qualitative signals（book-to-bill commentary, RFP pipeline tone, AI attribution claims）——这些只能从 earnings transcripts 或 IR materials 获取。

---

## 9. Provider Precedence

当多个来源提供同一数据点时：

```
SEC filing > yfinance financials > EODHD > MCP connector snapshot
```

对 earnings surprise：
```
earnings_history (yfinance) > manually computed from filing vs consensus
```

对 qualitative signals：
```
earnings transcript > IR press release > news aggregation
```

---

## 10. 与相邻文档的关系

| Doc | 关系 |
|-----|------|
| `ingestion_00_overview.md` | 本文是其下的域子文档 |
| `ingestion_10_source_connector_contract.md` | connector 通用规则，本文遵守 |
| `ingestion_33_company_fundamentals_data_architecture.md` | 结构化数据的 schema authority |
| `ingestion_63_research_newsletter_domain.md` | 外部 research 讨论公司归 63 域，不在本域 |
| `ingestion_64_market_data_domain.md` | 价格数据归 64 域 |
| `digestion_31_expert_runtime.md` | 消费者从 pool 按标签取用，不知道本文档 |
