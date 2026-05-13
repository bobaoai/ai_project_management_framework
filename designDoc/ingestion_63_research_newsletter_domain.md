---
title: "Ingestion Domain: Research Newsletter"
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
  - Analysis Platform Builder
---

# Ingestion Domain: Research Newsletter

## 1. 这份文档负责什么

本文件定义 Research Newsletter 信息域的 ingestion 边界。这个域覆盖所有通过 email / newsletter 渠道进入系统的外部 research material。

本域已经 fully operational（AgentMail pipeline 完整运行中）。本文件的目的是：

1. 把 `ingestion_50_source_family_playbook.md` 中 per-family policy 提升到域级统一视角
2. 定义本域与其他域（Fed、Company、Market Data）的边界
3. 为 Information Pool 统一索引提供本域的 tagging 规则

本文件不负责：

- image review 的详细 step-by-step（仍由 `ingestion_50` 管）
- archive object 的 file contract（由 `ingestion_20` 管）
- read_content.md 的 frontmatter schema（由 `ingestion_30` 管）

---

## 2. Sources in Scope

| # | Source | Family ID | Connector | Status |
|---|--------|-----------|-----------|--------|
| 1 | Citrini Research | `citrini` | AgentMail | ✓ active |
| 2 | TMT Breakout | `tmt_breakout` | AgentMail | ✓ active |
| 3 | Capital Flows | `capitalflows` | AgentMail (Substack) | ✓ active |
| 4 | Citrindex | `citrindex` | AgentMail | ✓ active |
| 5 | Conks | `conks` | AgentMail (Substack) | ✓ active |
| 6 | Generic Substack | `generic_newsletter` | AgentMail | ✓ catch-all |

---

## 3. Connector: AgentMail

所有 Research Newsletter 域的来源共用同一个 connector：

```yaml
connector: AgentMail
implementation: src/connectors/agentmail.py
auth: AgentMail API key (env: AGENTMAIL_API_KEY)
transport: email → AgentMail mailbox → API poll → local archive
parse: email HTML/text → content extraction → image download → archive object
status: ✓ fully operational
```

Connector 的运行方式：

1. AgentMail 提供邮箱地址，订阅 newsletter
2. 系统通过 AgentMail API 轮询新邮件
3. 邮件 payload → `data/research/messages/<research_id>/`
4. 后续由 `ingestion_20` archive contract + `ingestion_30` read content contract 处理

---

## 4. Per-Family Identity & Content Shape

### 4.1 Citrini Research

```yaml
family: citrini
collection_ids: [citrini_research]
content_shape: Long-form PDF / memo / field-trip report / deck-like research
read_mode: text_led (fallback hybrid when charts/diagrams present)
typical_topics: AI infrastructure, datacenter, semiconductor, vertical AI adoption
```

### 4.2 TMT Breakout

```yaml
family: tmt_breakout
collection_ids: []
content_shape: Newsletter / earnings wrap / Slack AMA recap
read_mode: text_led (fallback hybrid when KPI charts present)
typical_topics: TMT earnings, app metrics, platform economics, digital advertising
```

### 4.3 Capital Flows

```yaml
family: capitalflows
collection_ids: [capitalflows_rates_fx]
content_shape: Substack with embedded Bloomberg/TV screenshots, rates/FX charts
read_mode: hybrid (charts carry primary evidence)
typical_topics: rates, FX, inflation, STIR, cross-asset overlays, Fed transmission
```

### 4.4 Citrindex

```yaml
family: citrindex
collection_ids: []
content_shape: EOD performance snapshot, basket/portfolio updates
read_mode: text_led (fallback hybrid when allocation images present)
typical_topics: portfolio performance, basket composition changes
```

### 4.5 Conks

```yaml
family: conks
collection_ids: [conks_index, conks_money_markets]
content_shape: Substack money-market / funding-plumbing research, infographics, chat-thread notices
read_mode: hybrid for plumbing / infographic posts; text_led for thread notices
typical_topics: rates, liquidity, repo, reserves, TGA, RRP, SOFR, Fed balance sheet
```

### 4.6 Generic Substack / Newsletter

```yaml
family: unknown | generic_newsletter | substack
collection_ids: []
content_shape: varies — text-led by default
read_mode: text_led (fallback hybrid when data-bearing images present)
typical_topics: catch-all for unclassified newsletter sources
```

---

## 5. Tagging Rules

```yaml
domain: research_newsletter
source_class: newsletter_research
source_collection:
  family: <family_id>
  collection_id: <collection_id or empty>
```

| Family | source_class | typical ticker/theme tags |
|--------|-------------|--------------------------|
| citrini | `newsletter_research` | AI infrastructure tickers, datacenter, semiconductor |
| tmt_breakout | `newsletter_research` | TMT earnings, FANG+, digital ads |
| capitalflows | `newsletter_research` | rates, FX pairs, macro indicators |
| citrindex | `newsletter_portfolio` | basket tickers, index performance |
| conks | `newsletter_research` | rates, liquidity, repo, reserves, Treasury plumbing |
| generic | `newsletter_research` | varies |

Additional tags extracted during ingestion:
- `tickers[]` — 正文中提到的 ticker symbols
- `themes[]` — 匹配现有 theme registry 的 theme slugs

### 5.1 Timestamp semantics compliance

所有 Research Newsletter record 进入 archive 时遵守 `the_timestamp_semantic.md`：

| 字段 | 含义 | 来源 |
|------|------|------|
| `observed_at_utc` | newsletter 发布时间 | email Date header（OPT per `archive_message` matrix row） |
| `recorded_at_utc` | connector 写入 archive 的时刻 | 系统生成（REQ per R1） |

不引入裸 `publish_date` / `email_date` tag。时间锚统一从 `archive_message` 的 canonical fields 获取。

对应 §4 matrix class：`archive_message`（observed_at OPT, recorded_at REQ, updated_at —）。

---

## 6. Archive Policy

所有 Research Newsletter 域 output 进入：

```
data/research/messages/<research_id>/
  ├── message.json          (metadata + source identity)
  ├── raw artifacts         (raw email, body.html, attachments, downloaded images)
  ├── content_selection.json (body selection / assembly ledger)
  ├── content.txt / content.md  (legacy/cache only when present)
  ├── attachments/          (PDF, images)
  ├── image_reviews.jsonl   (image review ledger)
  ├── image_placements.jsonl (HTML image anchors when available)
  └── read_content.md       (canonical read surface)
```

遵守 `ingestion_20_archive_message_contract.md` 完整 file contract。

---

## 7. Freshness Rules

| Family | Typical cadence | Staleness threshold |
|--------|----------------|---------------------|
| Citrini | 2-5 per week | N/A（event-driven research） |
| TMT Breakout | 3-5 per week | N/A（event-driven） |
| Capital Flows | Daily-ish during active macro | 3 days during active rate moves |
| Citrindex | Daily EOD | 1 day (for latest performance) |
| Conks | Weekly-ish / event-driven | N/A（event-driven money-market research） |
| Generic | Varies | N/A |

Freshness 对 newsletter 域意义不大——newsletter 是 event-driven，不是 scheduled data feed。Staleness 只在"已知有新邮件但尚未 ingest"时触发。

---

## 8. Known Gaps & Fallbacks

| Gap | Impact | Fallback | Priority |
|-----|--------|----------|----------|
| Image review queue backlog | read_content.md 停在 `image_reviewed=false` | 按 family policy 优先处理 evidence-bearing images | 中 |
| Source family misclassification | 新 newsletter 落入 generic catch-all | 稳定后添加专属 family section | 低 |
| Attachment PDF 未解析 | Citrini PDF 内 chart/table 不在 read_content | PDF page rendering + image review | 中 |
| AgentMail downtime | 邮件堆积，ingest 延迟 | AgentMail 有 mailbox buffer；恢复后 backfill | 低 |

---

## 9. Quality Boundary

Research Newsletter 域的可信度定位：

| Level | 条件 | 下游 permission_level |
|-------|------|----------------------|
| **Expert interpretation** | 外部 analyst 的 interpretation、thesis、recommendation | `expert_interpretation`（不能作为 T1 primary source） |
| **Data pass-through** | Newsletter 引用的 official data（如 Citrini 引 NVDA 10-Q 数字） | 需追溯原始 filing；newsletter 本身不升级可信度 |
| **Chart evidence** | Bloomberg/TV chart screenshots embedded in newsletter | `expert_interpretation`（图表可信，解读是 analyst 的） |
| **Portfolio signal** | Citrindex basket changes, position sizing | `expert_interpretation`（Citrini 的 portfolio 信号） |

核心约束：

1. Newsletter research 永远不能作为 `publicly_observable` fact 的唯一来源——如果 claim 需要 T1 grounding，必须追溯到 SEC filing / official data / company disclosure。
2. Newsletter 的价值是 interpretation + pattern recognition + timing signal，不是 factual authority。
3. 当 newsletter 报道的数字与 official filing 矛盾时，以 filing 为准。

---

## 10. 与 ingestion_50 的关系

`ingestion_50_source_family_playbook.md` 继续作为 operational-level 的 image review policy reference。本文件（63）是域级 overview，定义边界和标签；50 定义具体 image policy 的 step-by-step。

分工：
- 63 owns: 域定义、tagging、archive policy、quality boundary
- 50 owns: per-family image review policy、operational verification checklist

---

## 11. 与相邻文档的关系

| Doc | 关系 |
|-----|------|
| `ingestion_00_overview.md` | 本文是其下的域子文档 |
| `ingestion_50_source_family_playbook.md` | operational image policy 的详细执行 |
| `ingestion_20_archive_message_contract.md` | archive object 文件结构 |
| `ingestion_30_ai_read_content_contract.md` | read_content.md 形态 |
| `ingestion_62_company_domain.md` | 公司 primary disclosure 归 62 域 |
| `ingestion_61_fed_domain.md` | Fed speech / minutes 归 61 域 |
| `src/connectors/agentmail.py` | connector 实现 |
