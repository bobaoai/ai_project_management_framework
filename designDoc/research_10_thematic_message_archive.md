---
title: Thematic Message Archive Compatibility Pointer
status: deprecated_pointer
reader_persona:
  - System Builder
  - Archive Analyst
  - Research Architect
---

# Thematic Message Archive Compatibility Pointer

## 1. Canonical ownership

本文是旧 thematic message archive contract 的兼容指针，不再拥有新的 archive 规则。

Canonical ownership 现在属于 ingestion family：

- `ingestion_20_archive_message_contract.md` 拥有 `data/research/messages/<research_id>/`、archive object shape、stable vs derived surfaces、tag taxonomy、source identity、mutable links。
- `ingestion_30_ai_read_content_contract.md` 拥有 `read_content.md`，也就是 downstream AI agent 默认读取的唯一 source surface。
- `ingestion_40_error_and_blocker_contract.md` 拥有 readiness、blocker、partial、failed-source behavior。
- `ingestion_50_source_family_playbook.md` 拥有 source-family-specific read mode、image policy、source_collection normalization。

Thematic research workflow 从 ingestion 产出 ready source surface 之后开始；需要进入 promotion 时，先由 `message derive-agent-evidence` 生成 `agent_evidence.json`。

## 2. Boundary

不要在本文新增 archive-object rules。

Source intake、archive layout、canonical content、image-read policy 读取：

1. `ingestion_00_overview.md`
2. `ingestion_20_archive_message_contract.md`
3. `ingestion_30_ai_read_content_contract.md`
4. `ingestion_50_source_family_playbook.md`

Source content 已存在后的 thematic promotion 读取：

1. `research_10_thematic_workflow.md`
2. `research_00_writer_package_contract.md`
3. `research_00_report_reviewer_pattern.md`

## 3. Preserved relationship

原对象路径仍然有效：

```text
data/research/messages/<research_id>/
```

Ownership 边界如下：

```text
connector / raw import
  -> ingestion archive object
  -> ingestion canonical source read content
  -> research promotion objects
```

`message` identity 必须独立于当前 theme / thesis interpretation。Linked snapshots、themes、theses、routing status、reconcile state 是 mutable research relationships，不是 source identity。

## 4. Detection-side boundary

如果改动对象是以下内容，应该进入 ingestion，而不是本文：

- `message.json`
- raw artifact storage
- `content_selection.json`
- `image_reads.jsonl`
- `image_reviews.jsonl`
- `read_content.md`
- `messages_index.jsonl`
- source_collection normalization
- image review policy
- ingestion blocker vocabulary

如果改动对象是以下内容，应该进入 research：

- `agent_evidence.json` consumption for promotion
- snapshot creation
- theme_update_draft routing
- thesis_note promotion
- theme context index selection
- theme writer package assembly
- theme report review and merge

