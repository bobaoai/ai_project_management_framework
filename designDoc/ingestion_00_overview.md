---
title: Ingestion Family Overview
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
  - Analysis Platform Builder
---

# Ingestion Family Overview

## 1. 这组文档解决什么

`ingestion_*` family 定义外部材料从 connector 接入到 canonical source read content 的路径：如何接入、如何保真归档、如何生成可重放的 archive projection、以及如何给下游 AI agent 提供一份可直接阅读的 source surface。

这组文档不负责 theme synthesis、thesis approval、PM judgment、portfolio action，也不替代 `research_*` workflow。它的边界停在：

```text
source connector / raw import
  -> archive object
  -> archive projection objects
  -> canonical source read content
  -> downstream research / analysis consumers
```

读完本 overview，读者应该能够：

- 判断新需求属于 connector、archive object、archive projection objects、canonical source read content，还是下游 research promotion。
- 知道下游 task agent 默认读取 `read_content.md`，archive internals 由 ingestion builder 收束。
- 知道每份 `ingestion_*` 子文档的责任边界。
- 知道 ingestion 输出停在 `read_content.md`，后续 snapshot / thesis / theme promotion 由 research family 继续。

核心目标：archive 保留多文件结构供 audit / replay；下游 AI 一律读 `read_content.md` 这一份 canonical content。检测式：如果下游 prompt 里出现 `message.json` / `content.txt` / `content.md` / `agent_evidence.json` / `image_reviews.jsonl` 等 archive internals，而不是单独 `read_content.md`，就是 silent violation。

## 2. 关键分层

### 2.1 Connector / raw import

Connector 负责接入边界：

- 连接外部来源
- 拉取 source payload
- 保存 raw artifacts
- 写入 minimal metadata
- 记录 sync status 和 connector error
- 保留 `observed_at_utc`（外部 source 发生 / 发布时刻）与 `recorded_at_utc`（系统写入归档时刻）的语义边界

Connector 不负责：

- 深层摘要
- theme / thesis 判断
- PM 建议
- portfolio action
- 下游 prompt 的文件选择策略

### 2.2 Archive object

Archive object 负责可审计、可重放、可修复。对 research-style message，canonical root 是：

```text
data/research/messages/<research_id>/
```

这个目录可以保留多个文件，因为 replay 和 audit 需要看到原始材料、投影选择 ledger、AI first-pass、image review、image placement、evidence units 等不同层次。正文清洗中间文件不再是核心契约；如果 raw artifact 能稳定重放，`content.md` / `content.txt` / `content_main.txt` / `content_normalized.txt` / `chunks.jsonl` / `links.json` 这类文件应视为 legacy/cache。

Archive 多文件是合理的；下游 AI 默认面对的是 `read_content.md` 这一份整理后产物，由 `ingestion_30` 收束 archive internals。

### 2.3 Archive Projection Objects

Archive projection objects 是从 archive 原始材料生成的可重算对象。完整列表与 stable-vs-derived 分类见 `ingestion_20_archive_message_contract.md`。

- `content_selection.json`
- `image_reads.jsonl`
- `image_reviews.jsonl`

它们让 archive 可修复、可追踪、可 replay。它们也是 canonical source read content builder 的输入，但不是下游 task agent 的默认输入列表。`agent_evidence.json` 是 downstream research-promotion surface，由 `message derive-agent-evidence` 从 `read_content.md` 生成，不反过来决定 `read_content.md`。

### 2.4 Canonical Source Read Content

Canonical source read content 是给下游 AI agent 读的一份整理后 source surface。默认目标路径：

```text
data/research/messages/<research_id>/read_content.md
```

按任务面生成不同版本时，使用：

```text
data/research/messages/<research_id>/read_content/<task_surface>.md
```

这份文件承载 source card、清洗后的正文、嵌入在正文相应位置的 reviewed image evidence，以及供 stop / audit / provenance 使用的机器可读 frontmatter。完整 file shape 与 frontmatter 字段契约见 `ingestion_30_ai_read_content_contract.md`。

下游默认只读这份 content。只有 `audit_paths[]` 明确指向 archive internals 时，才打开底层文件。

## 3. 文档族

### 3.1 Shared Contract Layer（跨域通用规则）

```text
designDoc/ingestion_00_overview.md
designDoc/ingestion_10_source_connector_contract.md
designDoc/ingestion_20_archive_message_contract.md
designDoc/ingestion_30_ai_read_content_contract.md
designDoc/ingestion_40_error_and_blocker_contract.md
designDoc/ingestion_50_source_family_playbook.md
```

| Doc | 责任 |
| --- | --- |
| `ingestion_00_overview.md` | 总入口、分层、相邻文档关系、ownership 规则。 |
| `ingestion_10_source_connector_contract.md` | connector / raw import 边界，保存什么，不做什么。 |
| `ingestion_20_archive_message_contract.md` | `messages/<research_id>/` archive object，多文件内部结构，stable vs derived。 |
| `ingestion_30_ai_read_content_contract.md` | 下游 AI 默认读取的一份 canonical source read content。 |
| `ingestion_40_error_and_blocker_contract.md` | blocker / partial / failed read / readiness contract。 |
| `ingestion_33_company_fundamentals_data_architecture.md` | fundamentals 的 canonical schema、provider 优先级、point-in-time 规则。 |
| `ingestion_50_source_family_playbook.md` | 不同 source family 的读取策略、图片 review 策略、agent orchestration 入口。 |

### 3.2 Information Domain Layer（按信息域管理）

```text
designDoc/ingestion_61_fed_domain.md
designDoc/ingestion_62_company_domain.md
designDoc/ingestion_63_research_newsletter_domain.md
designDoc/ingestion_64_market_data_domain.md
```

| Doc | 域 | 责任 |
| --- | --- | --- |
| `ingestion_61_fed_domain.md` | Fed | Fed speeches, FOMC materials, macro time-series (FRED/NY Fed/Treasury) |
| `ingestion_62_company_domain.md` | Company | SEC filings, earnings transcripts, quarterly financials, IR releases |
| `ingestion_63_research_newsletter_domain.md` | Research Newsletter | Citrini, TMT Breakout, Capital Flows, Citrindex, generic Substack |
| `ingestion_64_market_data_domain.md` | Market Data | Price history, economic events, VIX, TradingView news, MCP connectors |

每个域 doc 定义 7 个标准 slot：Sources in Scope、Connector per Source、Tagging Rules、Archive Policy、Freshness Rules、Known Gaps & Fallbacks、Quality Boundary。

### 3.3 层级关系

```text
ingestion_00 (overview)
├── ingestion_10 ~ 50 (shared contracts: connector / archive / read / error / playbook)
└── ingestion_61 ~ 64 (information domains)
      ↓ 所有 output 汇入
    Information Pool
      ↓
    Digestion Layer (experts consume from pool via tags)
```

Shared Contract Layer 定义"所有 connector 和 archive 必须遵守的规则"。
Information Domain Layer 定义"每个信息域有哪些来源、怎么获取、标什么签"。
两层正交——域 doc 遵守 shared contract，但各自独立管理自己的来源和质量边界。

## 4. 相邻 truth surfaces

- `source_connectors_and_knowledge_ingestion.md`：legacy connector boundary note；新 connector contract 以 `ingestion_10` 为准。
- `research_10_thematic_message_archive.md`：deprecated compatibility pointer；archive-object、tag taxonomy、source identity、mutable links 以 `ingestion_20` 为准。
- `research_10_thematic_workflow.md`：定义 `read_content.md` / `agent_evidence.json` 之后的 snapshot / thesis / theme promotion，不定义 ingestion file contract。
- `research_00_writer_package_contract.md`：定义 writer-facing package，不定义 source-level read content。
- `last_session_truth_and_ingestion_boundary.md`：定义时间语义与 ingestion/read boundary；时间字段命名仍以 `the_timestamp_semantic.md` 为 authority。

## 5. 与 research family 的边界

`ingestion` 负责 source material 进入系统和形成 canonical source read content。

`research` 负责把材料进一步变成：

- `snapshot`
- `thesis_note`
- `theme_update_draft`
- `theme report`
- writer-facing package

边界句：

```text
ingestion read content != writer package
```

`read_content.md` 是 source-level 的可读材料。Writer package 是 task-level 的写作包，只有在 owner scope、selected evidence、writer direction 已经决定后才生成。

## 6. Ownership 规则

1. `ingestion_10` owns connector / raw import 边界。
2. `ingestion_20` owns `data/research/messages/<research_id>/` 的 archive-object file contract。
3. `ingestion_30` owns `read_content.md` 的 canonical source read surface。
4. `ingestion_30` owns `read_content.md` frontmatter / file shape；`ingestion_40` owns `readiness_status`、`upstream_blockers[]`、`warnings[]` 的 value vocabulary 与 downstream stop / continue behavior。
5. 下游 consumer 默认读 `read_content.md`。

## 7. Downstream consumer rules

1. 如果 `read_content.md` 声明 `upstream_blockers[]` 非空，下游停止并报告 blocker。
2. 如果下游需要打开 archive internals，必须由 `read_content.md` 的 `audit_paths[]` 明确授权。

## 8. Information Pool

Ingestion 所有 output 汇入 Information Pool。Pool 不是一个单独的 store，而是以下位置的带标签聚合：

| 存储位置 | 数据类型 | 域 |
|----------|---------|-----|
| `data/research/messages/<id>/read_content.md` | 叙事（newsletters, filings, transcripts） | 63 Research, 62 Company, 61 Fed |
| `data/knowledge/fed/` | Fed 结构化文本 + verbatim passages | 61 Fed |
| `data/knowledge/company_fundamentals/` | 公司财务结构化数据 | 62 Company |
| `data/macro/` | 宏观时间序列 | 61 Fed / 64 Market |
| `data/hist/` | 价格历史 | 64 Market |

**隔离原则：**

- Ingestion 不知道谁消费。它只管 acquire → normalize → tag → pool。
- Digestion expert 不知道数据从哪来。它只看 Information Pool 里带标签的 source material。
- Router（`digestion_31_expert_runtime.md` §5）基于标签做确定性匹配，连接两层。

**统一索引：** `data/runtime/information_pool_index.yaml` 记录 pool 中所有 source 的 metadata（source_class, domain, tickers, observed_at, freshness_status），供 digestion router 做确定性匹配。

---

## 9. 非目标

Ingestion family 不负责：

- theme priority
- thesis lifecycle
- evidence verification
- PM-facing report prose
- portfolio action
- writer package 的完整结构
- artifact graph 的 node registry

这些属于 research、operation、AnalysisPlatform、artifact graph 或 PM workflow。
