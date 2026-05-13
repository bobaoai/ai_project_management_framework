---
title: Error And Blocker Contract
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
  - Analysis Platform Builder
---

# Error And Blocker Contract

## 1. 这份文档负责什么

本文件定义 ingestion family 中的错误、partial state、blocker、warning、audit note 如何表达，以及下游看到这些状态时应该怎么处理。

核心规则：

```text
如果 read_content.md 的 upstream_blockers[] 非空，下游停止并报告 blocker。
```

系统应该把上游未完成说清楚，而不是让下游 AI 用更复杂的 prompt 猜测缺失材料。

## 2. 状态分类

### 2.1 Blocker

`blocker` 表示下游不能可靠继续。

典型情况：

- raw artifact 缺失
- attachment 下载失败
- PDF text extraction 完全失败
- raw artifact / selected body source 不存在，且无法生成可用正文
- source 是 `image_led`，但 image review 失败
- required page texts 缺失
- email / newsletter source 有多张有效 reviewed image evidence，但没有可匹配的 HTML image anchor
- `read_content.md` 正文为空
- source 太大且没有 section/chunk selection
- `observed_at_utc` / provenance 缺失到影响引用或审计

下游行为：

```text
stop and report blocker
```

### 2.2 Warning

`warning` 表示下游可以继续，但需要知道材料不完美。

典型情况：

- OCR 有噪声但主线可读
- 少量图片被跳过但不是核心证据
- 部分 page text 缺失但正文完整
- cleanup 删除了重复页眉页脚
- evidence units 未生成，但正文和 image evidence 已足够
- source_collection 未识别，但 source metadata 足够

下游行为：

```text
continue, but carry the caveat if it affects judgment
```

### 2.3 Audit note

`audit note` 表示对 replay / debug 有用，但不影响下游阅读。

典型情况：

- raw file path
- parser version
- extraction command
- recorded_at_utc
- image ids processed
- omitted empty surfaces
- legacy compatibility file used

下游行为：

```text
ignore by default, open only when debugging or audit_paths[] asks for it
```

## 3. Canonical fields

`read_content.md` frontmatter 至少应支持：

```yaml
readiness_status: ready|ready_with_warnings|blocked|partial_needs_selection|failed
upstream_blockers: []
warnings: []
audit_paths: []
omitted_surfaces: []
recorded_at_utc: <ISO-8601 UTC instant>
```

完整 canonical frontmatter 由 `ingestion_30_ai_read_content_contract.md` 定义；本文件只定义 readiness / blocker / warning 的 shape 与行为。

推荐 blocker shape：

```yaml
upstream_blockers:
  - blocker_id: pdf_text_extraction_failed
    severity: blocking
    source_surface: page_texts.jsonl
    message: "PDF text extraction failed for all pages."
    recommended_fix: "rerun ingestion text extraction for this research_id"
    audit_paths:
      - data/research/messages/<research_id>/attachments/<file>.pdf
```

推荐 warning shape：

```yaml
warnings:
  - warning_id: ocr_noise_detected
    severity: warning
    source_surface: content_selection.json
    message: "Cleanup collapsed obvious fragmented lines, but OCR quality remains uneven."
```

## 4. Error sources

### 4.1 Connector errors

Connector errors 来自 `ingestion_10`。

Examples:

- auth failure
- fetch timeout
- partial download
- missing attachment
- unsupported MIME type
- invalid provider response

Blocker 判定：

- 如果 raw artifact 没有可靠保存，blocking。
- 如果 raw artifact 保存成功，但部分 optional metadata 缺失，多数是 warning。

### 4.2 Archive extraction errors

Archive extraction errors 来自 `ingestion_20`。

Examples:

- text extraction failed
- OCR failed
- page count mismatch
- duplicate raw data not safely cleanable
- malformed table extraction
- attachment inventory mismatch

Blocker 判定：

- 没有任何可用正文且 source 不是 image-led，blocking。
- 关键表格或 chart 无法恢复且 source 依赖它，blocking。
- 只有 minor layout noise，warning。

### 4.3 Image read / review errors

Image errors 来自 image first-pass 或 reviewed image evidence。

Examples:

- image file missing
- model timeout
- invalid JSON from image reader
- model quota / monthly usage limit / hard 429
- no reviewed image rows
- page role unknown
- visual evidence expected but absent

Blocker 判定：

- `content_mode: image_led` 且 image review 失败，blocking。
- `content_mode: hybrid` 且图片承载核心结论，blocking 或 warning，由 builder 判断。
- `content_mode: text_led` 且图片只是装饰，warning 或 audit note。
- Claude / image model 返回 quota、monthly usage limit、或 hard 429 时，当前 image-review run 必须 hard stop。不能把这些 rows 标成 failed / reviewed，也不能继续对同一批 pending rows 空转重试；保留 `status: pending`，等待额度恢复后从 pending ledger 继续。
- email / newsletter source 已经 review 出多张有判断增量的图片，但 `image_placements.jsonl` 无法把它们定位回 `body.html` 的正文位置，blocking；这表示 archive placement surface 还没收口，下游不能把末尾堆叠的 fallback 当成完整上下文。

### 4.4 Read-content builder errors

Read-content builder errors 来自 `ingestion_30`。

Examples:

- no canonical body selected
- cleanup uncertainty too high
- source too large without section plan
- contradictory content surfaces
- frontmatter invalid
- generated body empty

Blocker 判定：

- 不能生成可信 `read_content.md`，blocking。
- 能生成但有局部 omitted material，warning。

## 5. Downstream behavior

Downstream AI consumer 必须遵守：

```text
if upstream_blockers[] is non-empty:
  stop
  report blocker_id, message, recommended_fix
  do not continue source interpretation
```

允许继续的情况：

```text
if warnings[] is non-empty and upstream_blockers[] is empty:
  continue
  mention caveat only if it affects the task result
```

禁止：

- 用 prompt 自己补缺失正文
- 直接打开 archive internals 绕过 blocker
- 把 warning 当成 source conclusion
- 把 failed image review 当成“图片没有信息”
- 在 blocker 存在时生成 thesis、evidence verdict、PM action 或正式 report prose

## 6. Readiness status

推荐状态：

```text
ready
ready_with_warnings
blocked
partial_needs_selection
failed
```

含义：

- `ready`：下游可直接读。
- `ready_with_warnings`：下游可读，但 caveat 存在。
- `blocked`：下游停止。
- `partial_needs_selection`：source 太大或分区未选，需上游 section/chunk selection。
- `failed`：builder 或 extraction 失败，需重跑上游。

这个 status 可以进入 `read_content.md` frontmatter，也可以进入 `messages_index.jsonl` 的 readiness 字段。

## 7. 与相邻文档的关系

- `ingestion_10_source_connector_contract.md`：产生 connector-level errors。
- `ingestion_20_archive_message_contract.md`：产生 archive extraction / derived object errors。
- `ingestion_30_ai_read_content_contract.md`：消费这些错误，并在 `read_content.md` 中暴露 `upstream_blockers[]` / `warnings[]`。
- Downstream research / analysis skills：只消费 readiness，不重新判断 archive internals。
