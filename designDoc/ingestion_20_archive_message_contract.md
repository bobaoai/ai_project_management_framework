---
title: Archive Message Contract
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
  - Analysis Platform Builder
---

# Archive Message Contract

## 1. 这份文档负责什么

本文件定义 research-style `message` archive object。它回答：

- `data/research/messages/<research_id>/` 里应该有哪些 surface
- 哪些是 raw / stable
- 哪些是 cleaned / normalized
- 哪些是 derived / recomputable
- 哪些文件供 builder 使用，哪些文件供 audit / replay 使用

本文件不定义 theme promotion、thesis lifecycle、writer package，也不定义 downstream AI prompt。下游 AI 默认读取 `ingestion_30` 定义的 `read_content.md`。

## 2. Object center

Archive object 的中心是 `message`，不是 `email`。

`message` 指一份可归档的 research-style input：

- newsletter
- report
- PDF
- screenshot
- chart
- manual memo
- connector news item
- future web / RSS item

Canonical root:

```text
data/research/messages/<research_id>/
```

设计原则：

- connector 只负责送入 archive。
- archive 保存 full-fidelity source 与可重放派生层。
- canonical read content 给下游 AI 使用。
- theme / thesis / PM judgment 不反向污染 message identity。

## 3. Directory shape

标准目录形态：

```text
data/research/messages/<research_id>/
  message.json
  raw.eml | raw_payload.*
  body.html                  # when the raw source contains an HTML body that builders need for replay / placement
  attachments/
  content_selection.json
  page_texts.jsonl
  image_placements.jsonl
  image_reads.jsonl
  image_reviews.jsonl
  agent_evidence.json
  read_content.md
```

并非每个 message 都必须拥有所有文件。缺失文件必须能解释：不适用、尚未生成、生成失败、或被 blocker 阻断。

正文缓存文件不属于新契约的核心层。`content.md`、`content.txt`、`content_main.txt`、`content_normalized.txt`、`chunks.jsonl`、`links.json` 可以作为 legacy / cache 出现，但不应成为下游默认读取面，也不应成为可重放性的唯一证据。只要存在 raw replay source（例如 `raw.eml` + `body.html`）和 `content_selection.json` ledger，builder 应能重建 `read_content.md`。

## 4. Surface responsibilities

### 4.1 `message.json`

`message.json` 保存稳定身份与 source provenance。

推荐内容：

- `research_id`
- `source_type`
- `source_collection`
- `source_uri`
- `sender` / `publisher` / `provider`
- `title`
- `document_type`
- `language`
- `observed_at_utc`
- `recorded_at_utc`
- `raw_artifact_paths[]`
- `attachment_inventory[]`
- `connector_status`
- `connector_errors[]`

规则：

- `observed_at_utc` 表示 source 在外部世界发生、发布、出现的时刻；对 `archive_message` 是 optional。
- `recorded_at_utc` 表示我方系统把 `message.json` 写下来的时刻；对 `archive_message` 必填。
- Archive 层禁止 `updated_at_utc`。
- 不使用对象类目前缀或旧 role 字段来表达时间语义；新增字段必须遵守 `<role>_<storage>`。
- 不把 `theme_id` 当作 source identity。
- 不把 PM-facing conclusion 写进 message identity。
- 如果保留 body preview，只能作为 preview，不作为 canonical body。

### 4.1.1 Tag taxonomy and source identity

`message.json` 可以暴露 tag / identity fields，但必须分层。不要把 source identity、semantic topic、event tag、derived research link 混成一个 `tags[]`。

Identity / source fields 回答“这份材料是什么、从哪来、主要在讲谁”。这些字段通常只在 ingest、backfill、或明确修正 source identity 时改变：

- `document_type`
- `source_type`
- `source_collection`
- `source`
- `sender` / `publisher` / `provider`
- `primary_entities`
- `related_tickers`
- `time_horizon`
- `language`
- `observed_at_utc`
- `recorded_at_utc`

Semantic fields 回答“这份材料长期属于什么问题域”。它们可以低频修订，但不应被日常 event noise 覆盖：

- `macro_topics`
- `market_structure_topics`
- `sector_topics`
- `geography_topics`
- `thesis_family`

Event / regime fields 回答“这份材料和当前哪件事或哪段 regime 强相关”。它们可以持续追加、降权、归档：

- `event_tags`
- `regime_tags`
- `catalyst_tags`
- `watchpoint_tags`

Derived links 是当前 research graph 的解释结果，不是 source identity：

- `linked_snapshot_ids`
- `linked_theme_ids`
- `linked_thesis_ids`
- `routing_status`
- `last_reconciled_at`
- `ai_read_status`

`source_collection` 是 identity-layer field，同时也是 downstream routing hint。Canonical registry 是 `data/research/source_collections.json`。Registry 可以提供 `default_theme_tags`、`preferred_output_layer`、`snapshot_bias`、`theme_bias`、`thesis_bias`，但这些字段只帮助 research promotion 缩小候选范围，不能直接写成 finalized theme / thesis assignment。

Detection-side boundary:

- 如果 `message.json` 把 current `theme_id` 当作基础 tag，archive identity 被污染。
- 如果 `event_tags` 和 `macro_topics` 使用同一批值，stable topic 与 temporary event 被混淆。
- 如果 `linked_theme_ids` 被当作 source identity 字段维护，derived relationship 被伪装成 raw metadata。

### 4.2 Raw artifact / extracted raw body

原始获取物是 archive object 的保真基础。

示例：

- `raw.eml`：email / AgentMail source 的完整原始邮件。
- `raw_payload.json`：API connector 的原始 payload。
- `attachments/`：下载后的附件、图片、PDF 页面图等本地二进制。
- `body.html`：从 raw email / payload 中抽出的 HTML body。它是 replay / image placement 的便利 raw-adjacent surface，不是下游读取面。

规则：

- 如果 `raw.eml` 足以重建 `body.html`，`body.html` 可以被视为 cache；但当前 HTML newsletter image placement 依赖它，所以可以保留。
- 如果某类 source 没有 raw replay artifact，`content_main.txt` 可临时作为 legacy raw text surface 保留，直到该 connector 写入更明确的 raw artifact。
- Raw artifact 可以脏，可以包含广告、footer、tracking residue；它的职责是保真，不是漂亮。

### 4.3 `content_selection.json`

`content_selection.json` 是投影 ledger，不是正文副本。它记录系统如何从 raw / extracted body 得到 `read_content.md` 的正文选择。

推荐字段：

```json
{
  "schema_version": "minimal_content_selection_v1",
  "preferred_variant": "normalized",
  "content_mode": "text_led|image_led|hybrid",
  "selected_body_source": "body.html",
  "selected_body_sha256": "<sha256 of selected body text>",
  "main_body_sha256": "<sha256 of raw/extracted main body>",
  "normalized_body_sha256": "<sha256 of normalized body>",
  "body_cache_policy": "raw_replay_source_plus_read_content",
  "review": {
    "review_mode": "heuristic_v1",
    "main_char_count": 0,
    "normalized_char_count": 0,
    "removed_ratio": 0.0,
    "degradation_flags": []
  }
}
```

Ledger 的价值不是让下游 AI 多读一个文件，而是让人和系统能证明：

- `read_content.md` 使用了哪个 body source。
- normalized / selected body 是否相对 raw body 有异常长度变化。
- builder 为什么选择当前 content mode。
- 后续如果 `read_content.md` 可疑，可以回到 raw artifact 重建并比对 hash / length。

### 4.4 Legacy text cache files

以下文件可以存在，但属于 cache / compatibility，不属于新 archive contract 的核心层：

- `content_main.txt`
- `content_normalized.txt`
- `content.txt`
- `content.md`
- `chunks.jsonl`
- `links.json`

它们的允许用途：

- 支持旧命令或旧 package builder 的过渡期读取。
- 临时保存没有 raw replay artifact 的手工文本 source。
- 本地调试时快速查看 builder 中间结果。

它们的限制：

- 不能作为下游 task prompt 的默认输入。
- 不能成为唯一可审计证据；如果一个 file 不能从 raw artifact / `message.json` / builder deterministic logic 重建，就不应被称为 cache。
- 对 HTML/email source，有 `raw.eml` / `body.html` 时，新的写入路径可以不再生成这些文件。

### 4.5 Light body normalization policy

正文清洗可以在 builder 内存中发生，不要求长期保存 `content_normalized.txt`。

允许的轻处理：

- 把明显一词一行 / 短语碎行压回可读段落。
- 删除完全不可见 filler / 控制字符。
- 修复显而易见的换行和段落断裂。

不允许的处理：

- 改写观点。
- 改写数字。
- 删除看似重复但可能代表不同表格行 / chart label 的内容。
- 为了简洁而删掉关键 quote、page reference、table label、image caption。
- 删除广告、CTA、footer、preview、disclaimer 等“看起来多余”的内容。最多在 `read_content.md` warning 中说明它们可能是 source chrome，但正文应保留。

### 4.6 `page_texts.jsonl`

`page_texts.jsonl` 保存 PDF / paged source 的 page-level text extraction。

默认用途：

- OCR audit
- page attribution
- repair extraction
- builder 引用 page-level source

下游 AI 不默认直接读它。

### 4.7 `agent_evidence.json`

`agent_evidence.json` 是 research promotion 使用的单一 AI-derived 证据索引。它消费 `read_content.md`，不反过来决定 canonical source text。

推荐结构：

```json
{
  "schema_version": "agent_evidence_v1",
  "source_research_id": "<research_id>",
  "source_read_content_path": "messages/<research_id>/read_content.md",
  "document_read": {
    "primary_summary": "...",
    "claim_clusters": [],
    "semantic_hints": {},
    "open_questions": []
  },
  "image_reads": [],
  "evidence_units": []
}
```

职责：

- `document_read` 保存 AI 对 `read_content.md` 的一阶阅读结果：summary、claim clusters、semantic hints、open questions、source structure notes。
- `evidence_units` 把 text / image first-pass 收束成可复用证据单元，供 snapshot / thesis / theme routing 使用。
- `image_reads` 是 reviewed image rows 的一阶 projection，帮助 evidence units 与 visual evidence 对齐。

它是 derived / recomputable，不是 source truth。新写入路径不再并列生成 `text_read.json` 和 `evidence_units.jsonl`；旧文件如存在，只属于 legacy / audit。

### 4.8 `image_reads.jsonl`

`image_reads.jsonl` 保存 AI 对图片 / PDF 页面的一阶视觉读取。

规则：

- 每行应指向 `image_id` / `image_path` / `page_number`。
- 应区分纯文字页、封面、logo、页眉页脚、真实 visual evidence。
- 只有真实 chart / table / diagram / infographic 等目标对象才应进入 `visuals[]`。

### 4.9 `image_reviews.jsonl`

`image_reviews.jsonl` 是 reviewed image evidence surface。

它比 `image_reads.jsonl` 更适合作为 downstream read content builder 的输入，但仍然不是下游 agent 默认读取文件。Builder 应把其中有用内容嵌入 `read_content.md` 的正文相应位置。

Image review 不是“所有图片都送模型”。它有两层：

1. deterministic prefilter / dismissal
2. model review for remaining evidence-bearing images

Prefilter 可以直接终结明显无判断增量的图片，例如：

- logo / branding
- avatar / author photo
- CTA / subscribe / publish button
- tracking pixel / spacer / separator
- generic video thumbnail
- repeated footer / legal / disclosure decoration

这类 row 应保留在 `image_reviews.jsonl`，因为 archive 仍要能解释为什么某张图没有进入正文。但它不应继续占用 image model quota，也不应让 `image_reviewed` 长期保持 false。当前 persistence 规则是：dismissed row 写成 terminal reviewed row，`has_visual_evidence=false`、`evidence_value=none`、`incremental_evidence=false`，`review_model` 标明 deterministic prefilter / local gate，`summary` 简短说明 dismissal 原因。

只有 prefilter 后仍可能含有 chart、table、dashboard、screenshot、diagram、infographic、PDF page evidence 的 pending rows，才进入 canonical image model review。已 `status: reviewed` 的 row 不重跑，除非人工明确要求覆盖或修复错误 review。

### 4.10 `image_placements.jsonl`

`image_placements.jsonl` 保存 HTML / newsletter source 中 external image 的原文位置线索。

它不是图片判断结果，只是 placement anchor。典型字段包括 `image_id`、`image_path`、`source: body_html`、`html_ordinal`、`anchor_before`、`anchor_after`。Builder 用它把 `image_reviews.jsonl` 中有价值的 visual evidence 放回原文段落附近；如果 anchor 匹配失败，再降级到 `Reviewed Image Evidence` fallback 区。

### 4.11 `read_content.md`

`read_content.md` 是下游 AI 默认读取的一份完整材料。详细 contract 见 `ingestion_30_ai_read_content_contract.md`。

## 5. Stable vs derived

Stable / source identity:

- `message.json`
- raw artifacts
- attachments
- `observed_at_utc`
- `recorded_at_utc`

Projection ledger / placement audit:

- `content_selection.json`
- `image_placements.jsonl`

Legacy / cache:

- `content_main.txt`
- `content_normalized.txt`
- `content.txt`
- `content.md`
- `chunks.jsonl`
- `links.json`

Derived / recomputable:

- `agent_evidence.json`
- `image_reads.jsonl`
- `image_reviews.jsonl`
- `read_content.md`

Corpus indexes:

- `messages_index.jsonl`
- `links_index.jsonl`

Index rows are projections of `messages/<research_id>/message.json` plus current generated surface paths / hashes. Any canonical archive writer that creates or refreshes `read_content.md` must update the corresponding message index row in the same operation, so external programs that read only `messages_index.jsonl` do not miss newly ingested material. Direct file-level external writes that bypass the canonical writer must run `tradectl message rebuild-index` before downstream selection.

Mutable links:

- linked snapshots
- linked themes
- linked theses
- routing status
- reconcile status / latest reconcile record reference

Mutable links 可以出现在 index 或 derived metadata 中，不应伪装成 source identity。

## 6. Downstream rule

下游 AI agent 的默认读法：

```text
Read data/research/messages/<research_id>/read_content.md
```

下游不默认打开：

- `message.json`
- `content.txt`
- `content.md`
- `page_texts.jsonl`
- `agent_evidence.json`
- `image_reads.jsonl`
- `image_reviews.jsonl`

只有 `read_content.md` 的 `audit_paths[]` 明确要求时，才打开 archive internals。

## 7. 与相邻文档的关系

- `ingestion_10_source_connector_contract.md`：定义 message archive 的上游 handoff。
- `ingestion_30_ai_read_content_contract.md`：定义 `read_content.md` 的下游可读形态。
- `ingestion_40_error_and_blocker_contract.md`：定义缺失、失败、partial、blocker 如何表达。
- `research_10_thematic_message_archive.md`：deprecated compatibility pointer。Archive object、tag taxonomy、source identity、mutable links 以本文为准。
