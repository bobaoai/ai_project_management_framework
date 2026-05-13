---
title: Company Fundamentals Data Architecture
status: active_draft
reader_persona:
  - System Builder
  - Analysis Platform Builder
---

# Fundamentals Data Architecture

**Version 0.2 — 2026-05-05 (migrated from research_33 to ingestion_33; timestamp contract aligned)**

本文档是 `trading_platform` 中 `fundamentals` 这一类数据的唯一 schema contract。

它负责：

- company / security profile
- key stats
- financial statements
- point-in-time semantics
- provider roles and precedence
- fundamentals freshness and revision handling

它不负责 intraday quotes、bars 或 futures contract 规则。

归属：ingestion shared contract layer。被 `ingestion_62_company_domain.md`（connector / source 管理）引用为 schema authority。

---

## 1. Purpose

`fundamentals` 与 `price` 的根本区别，不在于数据源不同，而在于对象语义不同。

fundamentals 的核心问题是：

- statement period（fiscal quarter / year）
- filing date（公开可见时刻）
- reported vs restated values
- point-in-time truth
- company / security reference metadata
- refresh cadence

这些都与 `price` 的 freshness、roll、连续合约问题不同，因此必须单独成文。

---

## 2. Scope

本文件覆盖：

- issuer / security profile
- key stats snapshot
- quarterly / annual statements
- filing-linked metadata
- normalized reference fields
- fundamentals provider precedence
- revision and point-in-time handling

本文件不覆盖：

- intraday prices / bars / futures contracts → [`price_data_architecture.md`](price_data_architecture.md)
- connector 层（从哪拉、怎么拉）→ [`ingestion_62_company_domain.md`](ingestion_62_company_domain.md)
- earnings transcripts / qualitative signals → `ingestion_62` §3.2

---

## 3. Canonical Fundamentals Objects

### Timestamp semantics alignment

所有时间字段遵守 [`the_timestamp_semantic.md`](the_timestamp_semantic.md)。对应 §4 matrix class: `fundamentals_snapshot`（period_start_at REQ, period_end_at REQ, recorded_at REQ）。

裸字段名映射：

| 旧名（v0.1） | 新名（v0.2 合规） | role | storage |
|---|---|---|---|
| `as_of` | `recorded_at_utc` | recorded_at | at_utc |
| `snapshot_date` | `recorded_at_utc` | recorded_at | at_utc |
| `retrieved_at` | `recorded_at_utc` | recorded_at | at_utc |
| `filing_date` | `observed_at_utc` + `observed_precision: "date"` | observed_at | at_utc |
| `accepted_date` | `observed_at_utc`（SEC acceptance instant） | observed_at | at_utc |
| `period_end` / `fiscal_period_end` | `period_end_at_utc` | period_end_at | at_utc |
| — | `period_start_at_utc` | period_start_at | at_utc |

### 3.1 SecurityProfile

```yaml
class: fundamentals_snapshot (variant: profile)
fields:
  - symbol
  - security_name
  - issuer_name
  - exchange
  - country
  - sector
  - industry
  - currency
  - is_active
  - provider
  - provider_symbol
  - recorded_at_utc          # R1 mandatory
  - metadata
```

### 3.2 KeyStatsSnapshot

```yaml
class: fundamentals_snapshot (variant: key_stats)
fields:
  - symbol
  - provider
  - market_cap
  - enterprise_value
  - shares_outstanding
  - pe_ratio
  - pb_ratio
  - dividend_yield
  - beta
  - recorded_at_utc          # when connector wrote this snapshot
  - metadata
```

### 3.3 FinancialStatementSet

```yaml
class: fundamentals_snapshot
fields:
  - symbol
  - provider
  - statement_type           # income / balance_sheet / cashflow
  - period_type              # quarterly / annual
  - period_start_at_utc      # fiscal period start
  - period_end_at_utc        # fiscal period end
  - observed_at_utc          # filing date (when publicly visible)
  - observed_precision       # "date" for SEC filings (no intraday instant)
  - reported_currency
  - line_items               # dict of metric → value
  - recorded_at_utc          # R1 mandatory
  - metadata
```

### 3.4 FundamentalsResolution

用于回答"系统最终采用哪组 fundamentals"。

```yaml
class: fundamentals_snapshot (variant: resolution)
fields:
  - symbol
  - object_type
  - resolved_from_provider
  - period_end_at_utc
  - observed_at_utc          # filing date
  - point_in_time_valid      # boolean: was this the known-at-the-time value?
  - confidence
  - recorded_at_utc
  - notes
```

---

## 4. Point-In-Time Rule

fundamentals 系统必须显式区分：

- `period_end_at_utc` — 这是哪个 fiscal period 的值
- `observed_at_utc` — 它是在什么时候公开可见的（filing date / acceptance date）
- `recorded_at_utc` — 系统何时写下这条 record

如果没有这三个字段分离，系统就很容易把"今天知道的值"误写成"当时已知的值"。

### Required rule

所有 statements / key stats 的后续分析消费，必须能够回答：

- 这是哪个 period 的值 → `period_end_at_utc`
- 它是在什么时候公开可见的 → `observed_at_utc`
- 它是初始版本还是修订版 → `revision_type` (first_reported / restated)

### yfinance limitation

yfinance 不提供 filing date 或 point-in-time audit trail。它只给 latest restated values。因此：

- `observed_at_utc` 不可填（yfinance 不告诉我们何时公开可见）
- `recorded_at_utc` 填 connector 写入时刻
- `point_in_time_valid` = false（无法证明这是 originally reported value）

当 SEC EDGAR connector（`ingestion_62` §3.1）上线后，可从 filing 中获取真实 `observed_at_utc`，形成 point-in-time 完整链。

---

## 5. Provider Roles For Fundamentals

### 当前 provider 优先级

| Priority | Provider | 角色 | Status |
|---|---|---|---|
| 1 | **yfinance** | 免费 primary path：quarterly/annual statements, key stats, earnings surprise | ✓ operational |
| 2 | **EODHD** | 补充 provider：non-US, economic events, edge cases | partial |
| 3 | **SEC EDGAR** | T1 filing authority：point-in-time truth, `observed_at_utc` 来源 | planned |
| 4 | **MCP connectors** (FactSet, S&P, Moody's) | 机构级 point-in-time data | blocked（paid） |
| — | Schwab | 不是 fundamentals provider；broker API 不作为 fundamentals truth surface | excluded |

### Provider precedence for same data point

```
SEC filing > MCP (FactSet/S&P) > yfinance > EODHD
```

SEC filing 是 legal document（audited/reviewed），其他都是 derived。当 multiple providers 给出同一 `period_end_at_utc` 的不同 value 时，SEC filing 为准。

---

## 6. Freshness And Revision Semantics

fundamentals 不应套用 `price` 的 freshness 语言。

分类：

| Status | 含义 |
|---|---|
| `current_reference` | latest period, from latest provider pull |
| `latest_reported` | period is the most recent fiscal quarter/year |
| `historical_reported` | older period, value as originally reported |
| `restated` | period value updated by company (restatement) |
| `stale_reference` | provider pull > staleness threshold old |
| `missing` | period expected but data not available |

### Revision rule

系统应允许同一 `(symbol, statement_type, period_type, period_end_at_utc)` 出现多个版本，但必须能识别哪个是：

- first reported（`revision_type: first_reported`）
- latest restated（`revision_type: restated`）
- point-in-time valid for a historical replay

yfinance 只给 latest restated。真正的 revision tracking 需要 SEC EDGAR 或 MCP provider。

---

## 7. Relationship To Platform Store

fundamentals 不应直接替代 ticker universe。

- platform store 继续管理 canonical ticker universe / watchlists / coverage status
- fundamentals connector 管理 issuer/security/reference payloads
- 平台层再把 provider payload 规范化为 fundamentals objects

也就是说：

- universe orchestration 不是 fundamentals provider 的职责
- fundamentals provider 也不是 canonical symbol authority

---

## 8. Current Implementation State

| 组件 | Status |
|------|--------|
| `src/connectors/yahoo_fundamentals.py` | ✓ operational — quarterly statements, earnings, key stats, profile |
| `data/knowledge/company_fundamentals/<TICKER>/` | ✓ created — MEDP, CRL, IQV verified |
| SEC EDGAR connector | planned |
| EODHD connector | partial（`src/macro_data/` 有部分 EODHD 调用） |
| MCP connectors (FactSet etc.) | blocked（paid subscription） |
| Point-in-time tracking | gap — yfinance 不提供 filing date；需 SEC EDGAR 补 |
| Revision history | gap — 只有 latest restated；需 append-on-pull tracking |

---

## 9. Storage Contract

```
data/knowledge/company_fundamentals/<TICKER>/
  ├── quarterly_income.json
  ├── quarterly_balance_sheet.json
  ├── quarterly_cashflow.json
  ├── annual_income.json          (optional)
  ├── annual_balance_sheet.json   (optional)
  ├── annual_cashflow.json        (optional)
  ├── earnings_history.json
  ├── key_stats.json
  └── profile.json
```

每个 JSON 文件包含 `recorded_at_utc`（R1）。Statement 文件包含 `periods[]`，每个 period 有 `period_end_at_utc`。

---

## 10. Consumer Rule

Analysis consumer 不应直接吃 fundamentals provider 的原始字段命名。

它应消费：

- normalized profile（company identity）
- normalized key stats（valuation multiples, margins）
- normalized statements（line_items keyed by standard metric names）
- explicit `period_end_at_utc` / `observed_at_utc` / `recorded_at_utc` 三级时间锚

否则后续主题研究、资产卡片、memo 和 review artifact 很容易出现时间错配。

---

## 11. Cross-references

| Doc | 关系 |
|-----|------|
| [`ingestion_62_company_domain.md`](ingestion_62_company_domain.md) | 引用本文为 schema authority |
| [`the_timestamp_semantic.md`](the_timestamp_semantic.md) | 时间字段命名与 class registration |
| [`price_data_architecture.md`](price_data_architecture.md) | 价格数据独立 architecture |
| [`ingestion_10_source_connector_contract.md`](ingestion_10_source_connector_contract.md) | connector 边界规则 |
| `src/connectors/yahoo_fundamentals.py` | yfinance connector 实现 |

---

## 12. Changelog

- **v0.2 (2026-05-05)** — 从 `research_33` 迁移到 `ingestion_33`。Timestamp 字段全部合规（`as_of` → `recorded_at_utc`，`filing_date` → `observed_at_utc`，`period_end` → `period_end_at_utc`）。Provider §5 更新（yfinance 成为 working primary free path）。§8 更新实际实现状态。添加 §9 Storage Contract。
- **v0.1 (2026-03-26)** — 初始版本，定义 fundamentals 与 price 的对象语义区分。
