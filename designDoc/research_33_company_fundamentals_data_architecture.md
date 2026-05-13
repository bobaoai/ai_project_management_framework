# Fundamentals Data Architecture

**Version 0.1 — 2026-03-26**

本文档是 `trading_platform` 中 `fundamentals` 这一类数据的唯一主规则文档。

它负责：

- company / security profile
- key stats
- financial statements
- point-in-time semantics
- provider roles for fundamentals
- fundamentals freshness and revision handling

它不负责 intraday quotes、bars 或 futures contract 规则。

---

## 1. Purpose

`fundamentals` 与 `price` 的根本区别，不在于数据源不同，而在于对象语义不同。

fundamentals 的核心问题是：

- statement period
- filing date
- reported vs restated values
- point-in-time truth
- company / security reference metadata
- refresh cadence

这些都与 `price` 的 freshness、roll、连续合约问题不同，因此必须单独成文。

---

## 2. Scope

本文件覆盖：

- issuer / security profile
- key stats
- quarterly / annual statements
- filing-linked metadata
- normalized reference fields
- fundamentals provider precedence
- revision and point-in-time handling

本文件不覆盖：

- intraday prices
- bars
- futures contracts
- quote freshness policy

这些交给 [`price_data_architecture.md`](price_data_architecture.md)。

---

## 3. Canonical Fundamentals Objects

### 3.1 SecurityProfile

最小字段建议：

- `symbol`
- `security_name`
- `issuer_name`
- `exchange`
- `country`
- `sector`
- `industry`
- `currency`
- `is_active`
- `provider`
- `provider_symbol`
- `as_of`
- `metadata`

### 3.2 KeyStatsSnapshot

最小字段建议：

- `symbol`
- `provider`
- `market_cap`
- `enterprise_value`
- `shares_outstanding`
- `pe_ratio`
- `pb_ratio`
- `dividend_yield`
- `beta`
- `snapshot_date`
- `as_of`
- `metadata`

### 3.3 FinancialStatementSet

最小字段建议：

- `symbol`
- `provider`
- `statement_type`
- `period_type`
- `fiscal_period_end`
- `filing_date`
- `accepted_date`
- `reported_currency`
- `line_items`
- `as_of`
- `metadata`

### 3.4 FundamentalsResolution

用于回答“系统最终采用哪组 fundamentals”。

最小字段建议：

- `symbol`
- `object_type`
- `resolved_from_provider`
- `resolved_as_of`
- `filing_date`
- `period_end`
- `point_in_time_valid`
- `confidence`
- `notes`

---

## 4. Point-In-Time Rule

fundamentals 系统必须显式区分：

- `period_end`
- `filing_date`
- `accepted_date`
- `retrieved_at`
- `as_of`

如果没有这些字段，系统就很容易把“今天知道的值”误写成“当时已知的值”。

### Required rule

所有 statements / key stats 的后续分析消费，必须能够回答：

- 这是哪个 period 的值
- 它是在什么时候公开可见的
- 它是初始版本还是修订版

---

## 5. Provider Roles For Fundamentals

当前默认方向：

- `EODHD`：第一候选 fundamentals / reference provider
- `Schwab`：不是 fundamentals 主 provider；即便未来提供少量 reference fields，也不应成为 fundamentals truth surface 的命名中心

### Why

fundamentals 需要：

- 更完整的 statement coverage
- 更清晰的 reference metadata
- 更明确的 historical / point-in-time semantics

这类工作更适合专门 fundamentals provider，而不是从 broker API 侧面拼凑。

---

## 6. Freshness And Revision Semantics

fundamentals 不应套用 `price` 的 freshness 语言。

更合适的分类是：

- `current_reference`
- `latest_reported`
- `historical_reported`
- `restated`
- `stale_reference`
- `missing`

### Revision rule

系统应允许同一：

- `symbol`
- `statement_type`
- `period_type`
- `period_end`

出现多个版本，但必须能识别哪个是：

- first reported
- latest restated
- point-in-time valid for a historical replay

---

## 7. Relationship To Platform Store

fundamentals 不应直接替代 ticker universe。

与 [`postgres_ticker_coverage_design_v0_1.md`](postgres_ticker_coverage_design_v0_1.md) 的关系应为：

- platform store 继续管理 canonical ticker universe / watchlists / coverage status
- fundamentals provider 管理 issuer/security/reference payloads
- 平台层再把 provider payload 规范化为 fundamentals objects

也就是说：

- universe orchestration 不是 fundamentals provider 的职责
- fundamentals provider 也不是 canonical symbol authority

---

## 8. Current Repo Implication

当前 repo 已经有一条 fundamentals 痕迹：

- `.env.example` 中已有 `EODHD_API_TOKEN`
- `tradectl` 中已有 `fetch:fundamentals` / `fetch:financials` 的 worker 调用痕迹

但这仍不等于 fundamentals architecture 已经成立。

当前缺的是：

- canonical fundamentals object model
- point-in-time / revision rule
- provider precedence rule
- 与平台层的清晰边界

---

## 9. Cleanup Targets

后续 fundamentals 相关清理重点不应放在 Schwab client，而应放在：

- 当前 ad hoc worker-driven fundamentals path
- fundamentals object normalization
- provider ownership definition

目标是把 “能抓到一些 fundamentals” 升级成 “系统知道自己在管理什么 fundamentals 对象”。

---

## 10. Consumer Rule

analysis consumer 不应直接吃 fundamentals provider 的原始字段命名。

它应消费：

- normalized profile
- normalized key stats
- normalized statements
- explicit `period_end / filing_date / as_of`

否则后续主题研究、资产卡片、memo 和 review artifact 很容易出现时间错配。
