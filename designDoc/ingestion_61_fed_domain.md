---
title: "Ingestion Domain: Fed"
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
  - Analysis Platform Builder
---

# Ingestion Domain: Fed

## 1. 这份文档负责什么

本文件定义 Fed 信息域的 ingestion 边界：哪些 Fed 来源在 scope 内、每个来源的 connector 模式、tagging 规则、archive 策略、freshness 规则、已知 gap 与 fallback、以及数据质量边界。

本文件不负责：

- 从 Fed data 生成 thesis / claim / cognitive layer（那是 digestion expert 的事）
- 决定哪个 expert 消费哪份材料（那是 digestion_31 routing 的事）
- 定义 macro dashboard 的展示逻辑（那是 AnalysisPlatform）

Fed 域与 Information Pool 的关系：ingestion 完成 → 输出进入 pool → digestion expert 从 pool 按标签取用。

---

## 2. Sources in Scope

| # | Source | 数据性质 | 接入验证 |
|---|--------|---------|---------|
| 1 | Fed Board speeches（governors + chair） | 叙事 T1 | ✓ WebFetch 全量 |
| 2 | Reserve Bank president speeches | 叙事 T1 / T1-adjacent | 部分 403，Perplexity fallback |
| 3 | FOMC statements | 叙事 T1 | ✓ WebFetch |
| 4 | FOMC minutes | 叙事 T1 | ✓ WebFetch |
| 5 | FOMC press conference transcripts | 叙事 T1 | gap（PDF 未展开） |
| 6 | FOMC calendar & SEP | 结构化 meta | ✓ WebFetch |
| 7 | FRED series（rates, spreads, employment） | 时间序列 | ✓ API |
| 8 | NY Fed rates（SOFR, EFFR, RRP） | 时间序列 | ✓ API |
| 9 | Treasury yields（daily curve） | 时间序列 | ✓ XML feed |
| 10 | Fed H.4.1（balance sheet） | 时间序列 | ✓ ZIP download |
| 11 | Treasury TGA（operating cash balance） | 时间序列 | ✓ FiscalData API |
| 12 | CME FedWatch（rate probabilities） | 结构化 snapshot | gap（JS 渲染） |

---

## 3. Connector per Source

### 3.1 Fed Board speeches

```yaml
connector: WebFetch
url_pattern: federalreserve.gov/newsevents/speech/<speaker_id><yyyymmdd>a.htm
index_url: federalreserve.gov/newsevents/speech/<yyyy>-speeches.htm
auth: none
parse: HTML → plain text extraction
status: ✓ operational
```

### 3.2 Reserve Bank president speeches

```yaml
connector: WebFetch (primary) / Perplexity agent (fallback)
url_pattern: varies per bank (see SOURCING.md §1-3)
auth: none
parse: HTML → plain text / Perplexity → verbatim passages
status: partial — Board works; most Reserve Bank sites 403
fallback_trigger: WebFetch returns 403
fallback_method: src/tools/perplexity_search.py --api agent --preset fast-search
```

Working Reserve Bank paths:
- NY Fed: `tellerwindow.newyorkfed.org/<yyyy>/<mm>/<dd>/<slug>`
- SF Fed: `frbsf.org/research-and-insights/blog/sf-fed-blog/<yyyy>/<mm>/<dd>/<slug>/`

403-blocked: Atlanta, St Louis, Philadelphia, Boston, Chicago, Cleveland, Dallas, Richmond, KC, Minneapolis.

### 3.3 FOMC statements

```yaml
connector: WebFetch
url_pattern: federalreserve.gov/newsevents/pressreleases/monetary<yyyymmdd>a.htm
auth: none
parse: HTML → plain text
status: ✓ operational
```

### 3.4 FOMC minutes

```yaml
connector: WebFetch
url_pattern: federalreserve.gov/monetarypolicy/fomcminutes<yyyymmdd>.htm
auth: none
parse: HTML → plain text
status: ✓ operational
```

### 3.5 Press conference transcripts

```yaml
connector: PDF download + pdftotext
url_pattern: federalreserve.gov/monetarypolicy/fomcpresconf<yyyymmdd>.htm → PDF link
auth: none
parse: PDF → plain text
status: gap — HTML page only links to PDF; PDF extraction not yet automated
next_step: curl + pdftotext pipeline, or Perplexity agent fallback
```

### 3.6 FOMC calendar & SEP

```yaml
connector: WebFetch
url_pattern: federalreserve.gov/monetarypolicy/fomccalendars.htm
auth: none
parse: HTML → structured JSON (meeting dates, SEP release nodes)
status: ✓ operational
```

### 3.7 FRED series

```yaml
connector: FRED CSV endpoint / FRED API (for credit spreads)
implementation: src/macro_data/public_sources.py → PublicMacroSourceClient
url: fred.stlouisfed.org/graph/fredgraph.csv?id=<series>
auth: FRED API key (env: FRED_API_KEY) for API endpoint; CSV endpoint is public
status: ✓ operational
```

### 3.8 NY Fed rates

```yaml
connector: NY Fed Markets API
implementation: src/macro_data/public_sources.py
url: markets.newyorkfed.org/api/rates/<type>
auth: none
status: ✓ operational
series: SOFR, EFFR, OBFR, TGCR, BGCR, RRP
```

### 3.9 Treasury yields

```yaml
connector: Treasury XML feed
implementation: src/macro_data/public_sources.py
url: home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml
auth: none
status: ✓ operational
```

### 3.10 Fed H.4.1

```yaml
connector: ZIP download + CSV parse
implementation: src/macro_data/public_sources.py
url: federalreserve.gov/datadownload/Output.aspx?rel=H41&filetype=zip
auth: none
status: ✓ operational
```

### 3.11 Treasury TGA

```yaml
connector: FiscalData API
implementation: src/macro_data/public_sources.py
url: api.fiscaldata.treasury.gov/.../operating_cash_balance
auth: none
status: ✓ operational
```

### 3.12 CME FedWatch

```yaml
connector: not built
challenge: requires JS rendering; CME site blocks automated access
status: gap
next_step: evaluate headless scraper or third-party snapshot service
```

---

## 4. Tagging Rules

所有 Fed 域 output 使用以下标签：

```yaml
domain: fed
source_class: <per source below>
```

| Source | source_class | additional tags |
|--------|-------------|----------------|
| Board speeches | `fed_speech` | `speaker_id` |
| Reserve Bank speeches | `fed_speech` | `speaker_id`, `bank_id` |
| FOMC statements | `fomc_statement` | — |
| FOMC minutes | `fomc_minutes` | — |
| Press conferences | `fomc_pressconf` | — |
| Calendar | `fomc_calendar` | `year` |
| FRED series | `macro_series` | `series_id`, `frequency` |
| NY Fed rates | `macro_series` | `rate_type` |
| Treasury yields | `macro_series` | `curve_type` |
| H.4.1 | `macro_series` | `report_type=h41` |
| TGA | `macro_series` | `report_type=tga` |
| FedWatch | `rate_expectations` | — |

### 4.1 Timestamp semantics compliance

所有时间相关值遵守 `the_timestamp_semantic.md`。不引入裸日期 tag——时间锚从 record 本身的 canonical time fields 获取：

| source_class | 时间锚来源 | 对应 §4 matrix class |
|---|---|---|
| `fed_speech` | record 的 `observed_at_utc`（speech delivery instant） | `fed_speech` |
| `fomc_statement` | record 的 `observed_at_utc`（publication instant） | `fed_statement` |
| `fomc_minutes` | record 的 `observed_at_utc`（release instant） | archive_message variant |
| `fomc_pressconf` | record 的 `observed_at_utc`（press conf start） | archive_message variant |
| `macro_series` | observation 的 `observed_at_utc` 或 `period_end_at_utc` | `tick`（point）/ `kbar_1d`（bar） |
| `rate_expectations` | record 的 `observed_at_utc`（snapshot instant） | 需 §4 登记 |

**待登记**：`rate_expectations`（CME FedWatch snapshot）尚未在 timestamp contract §4 矩阵注册。实现时需先添加行再写 schema。

---

## 5. Archive Policy

Fed 域 output 按数据性质分流到两个存储位置：

### 5.1 叙事类（speeches, statements, minutes, transcripts）

```
data/knowledge/fed/raw/speeches/<speaker_id>/<yyyymmdd>.json
data/knowledge/fed/raw/statements/<yyyymmdd>.json
data/knowledge/fed/raw/minutes/<yyyymmdd>.json
data/knowledge/fed/raw/pressconf/<yyyymmdd>.json
data/knowledge/fed/raw/calendar.json
data/knowledge/fed/raw/speakers/index.jsonl
```

叙事类进入 Information Pool 时，同时生成：

```
data/knowledge/fed/raw/speakers/<speaker_id>/speeches/<yyyymmdd>.json
  → verbatim passages + metadata (source_url, venue, observed_at_utc, T1/aggregated tag)
```

文件名 `<yyyymmdd>` 是 file-system slug（human-readable locator），不是 schema 时间字段。JSON 内部时间字段遵守 timestamp contract：`observed_at_utc`（speech delivery）+ `recorded_at_utc`（archive write）。

### 5.2 时间序列类（FRED, NY Fed, Treasury, H.4.1, TGA）

```
data/macro/<series_group>/<series_id>.json
```

时间序列由 `src/macro_data/` 现有 pipeline 管理。Snapshot 按日期追加，保留 point-in-time audit trail。

---

## 6. Freshness Rules

| Source | Refresh cadence | Staleness threshold |
|--------|----------------|---------------------|
| Board speeches | On FOMC meeting / speech event | 7 days after speech |
| Reserve Bank speeches | On speech event | 14 days after speech |
| FOMC statements | On FOMC decision day | 1 day |
| FOMC minutes | 3 weeks post-meeting（scheduled release） | 1 day after release |
| Press conferences | On FOMC decision day | 7 days (pending PDF extraction) |
| FRED series | Daily for rates; weekly for credit | 1 business day |
| NY Fed rates | Daily | 1 business day |
| Treasury yields | Daily | 1 business day |
| H.4.1 | Weekly (Thursday release) | 2 business days |
| TGA | Daily | 1 business day |
| FedWatch | Pre-FOMC snapshot | 1 day pre-meeting |

---

## 7. Known Gaps & Fallbacks

| Gap | Impact | Fallback | Priority |
|-----|--------|----------|----------|
| Reserve Bank speeches 403 | 50%+ of regional Fed views inaccessible via WebFetch | Perplexity agent → T1-adjacent verbatim | 高 |
| Press conference PDF | Powell Q&A context missing | PDF download + pdftotext (not automated) | 高 |
| CME FedWatch | Rate expectations path missing | Manual snapshot or third-party | 中 |
| archive.org blocked | No Wayback fallback for 403 pages | Accept Perplexity aggregated | 低 |
| Perplexity truncation | Long speeches only get first 400-600 tokens | Multi-query sectional fetch | 中 |

详细 URL 模式、403 列表、已验证 fallback 路径见 `data/knowledge/fed/SOURCING.md`。

---

## 8. Quality Boundary

Fed 域数据的可信度分级：

| Level | 条件 | 下游 permission_level |
|-------|------|----------------------|
| **T1** | WebFetch 直接从 federalreserve.gov / Treasury.gov 获取 full text | `publicly_observable` |
| **T1-adjacent** | Reserve Bank blog 子域引用（如 Teller Window）；或 FOMC 文件中 verbatim section | `publicly_observable` |
| **Aggregated** | Perplexity agent 返回 verbatim passages（标注 `[aggregated]`） | `publicly_observable` 但标注来源路径 |
| **Derived** | FRED / NY Fed / Treasury 时间序列 via API | `publicly_observable`（official data） |

质量边界的核心约束：

1. aggregated 来源不应被下游 expert 当作 full T1 使用——verbatim 段可引，整体完整性不保证。
2. 时间序列数据是 official 发布，point-in-time value 可信，但 series 可能 revised（尤其就业数据）。
3. FedWatch 是 derived market pricing，不是 Fed 的 official forward guidance。

---

## 9. 与相邻文档的关系

| Doc | 关系 |
|-----|------|
| `ingestion_00_overview.md` | 本文是其下的域子文档 |
| `ingestion_10_source_connector_contract.md` | connector 通用规则，本文遵守 |
| `data/knowledge/fed/SOURCING.md` | 本文引用的运营级 URL playbook |
| `src/macro_data/public_sources.py` | 时间序列 connector 的实现 |
| `ingestion_64_market_data_domain.md` | VIX / credit spread 等在 64（market data）域，不在本域 |
| `digestion_31_expert_runtime.md` | 消费者不知道本文档；routing 基于 pool 标签 |
