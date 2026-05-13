---
title: Source Connector Contract
status: active_draft
reader_persona:
  - System Builder
  - Archive Analyst
---

# Source Connector Contract

## 1. 这份文档负责什么

本文件定义 `source connector / raw import` 的边界。它回答：

- 什么算 connector
- connector 必须保存什么
- connector 可以补哪些 minimal metadata
- connector 明确不负责什么
- connector 如何把材料交给 archive object

Connector 是外部世界进入系统的 intake boundary。它不是 research workflow，不是 analysis agent，也不是 PM 判断层。

## 2. Connector 的定义

Connector 指任何把外部材料拉入本地系统的入口，包括：

- AgentMail
- email / newsletter
- RSS
- web fetcher
- broker API
- market-data API
- manual file drop
- screenshot / chart import
- PDF / report import

这些入口的共同点不是“研究”，而是“接入”。Connector 的名字不应该成为整个知识系统的命名中心。

## 3. Connector 必须做的事

每个 connector 至少负责：

- connect / authenticate
- fetch source payload
- save raw artifacts
- emit minimal metadata
- track sync status
- track connector errors
- return or write canonical archive handoff information

对 research-style source，connector 的默认 handoff target 是：

```text
data/research/messages/<research_id>/
```

对 market data / broker data / fundamentals data，connector 可以写入各自专门 store，但同样需要保留 raw provider facts 和 archive audit fields。

## 4. Raw artifact preservation

Connector 必须尽量保留 source 原貌。典型 raw artifacts：

- raw email / raw message payload
- original attachment
- downloaded PDF
- source HTML
- source image / screenshot
- provider JSON payload
- broker API response
- market-data response

Raw artifact 不等于 downstream read content。Raw artifact 的目标是 replay、audit、debug、backfill。

## 5. Minimal metadata contract

Connector 立即写入的 metadata 应该尽量稳定、低解释度。

推荐字段：

```text
source_type
source_id
source_collection
source_uri
sender / publisher / provider
title
mime_type
attachment_inventory
observed_at_utc
recorded_at_utc
raw_artifact_paths[]
connector_status
connector_errors[]
```

规则：

- `observed_at_utc` 表示 source 在外部世界发生、发布、出现的时刻；没有可靠来源时允许缺失。
- `recorded_at_utc` 表示我方系统把 connector handoff / archive record 写下来的时刻；archive record 必填。
- 不使用对象类目前缀或旧 role 字段来表达时间语义；新增字段必须遵守 `<role>_<storage>`。
- connector 可以补 normalized title、attachment list、extracted links。
- connector 不应把当前 theme、thesis、portfolio judgment 写成 source identity。
- `source_collection` 是 source-family routing hint，不是最终语义判断。

## 6. Stable ID and idempotency

`research_id` 不由下游 prompt 决定，也不由 AI 生成。它由 archive admission layer 根据稳定 source key 生成或确认。

Connector handoff 应提供生成或查找 `research_id` 所需的稳定输入：

```text
source_type
source_collection
source_id
source_uri
provider_message_id
raw_artifact_hash
observed_at_utc
```

Archive admission layer 负责：

- 计算 `unique_source_key`。
- 在 `messages_index.jsonl` 或等价 index 中检查唯一性。
- 已存在同一 `unique_source_key` 时返回既有 `research_id`，不创建重复 message。
- 同一 `source_id` / `source_uri` 但 raw artifact hash 改变时，记录 collision 或 revision，不静默覆盖。
- 同一内容经不同 connector 进入时，按 hash / source provenance 进入 dedupe review，而不是让两个 `research_id` 同时成为默认事实。
- rerun / reingest 默认幂等：可补缺失 derived surfaces，不改写 immutable archive identity。

冲突策略：

- `exact_duplicate`：复用既有 `research_id`。
- `same_source_changed_payload`：保留既有 identity，记录 revision / blocker，等待 archive policy 决定是否新建 version。
- `hash_duplicate_different_source`：进入 dedupe review，可建立 cross-source link。
- `source_key_collision`：blocking，不生成 ready read content。

## 7. Connector 不负责什么

Connector 不负责：

- 深层摘要
- semantic interpretation
- thesis 生成
- evidence verification
- theme synthesis
- PM action
- opportunity ranking
- writer package assembly
- canonical source read content 的完整正文组织

如果 connector 发现材料需要后续 AI read，应只记录状态或触发后续 builder，不在 connector 内部临时拼 prompt 或直接写 PM-facing 结论。

## 8. Handoff 到 archive object

Research-style connector 成功后，应交给 archive object 层处理：

```text
connector output
  -> data/research/messages/<research_id>/
  -> ingestion_20 archive object
  -> ingestion_30 read_content.md
```

Connector handoff 应至少提供：

- stable source-key inputs
- raw artifact path
- source metadata
- attachment inventory
- connector status
- error / warning list

Archive admission layer 确认或生成 `research_id` 后，archive object 层负责后续正文抽取、图片读取、evidence units、canonical read content。

## 9. Error behavior

Connector 失败时必须显式记录，不允许静默降级。

典型错误：

- auth failure
- fetch timeout
- missing attachment
- unsupported MIME type
- partial download
- provider response invalid
- `observed_at_utc` missing when source publication time is required for downstream audit

错误应进入 `connector_errors[]` 或等价状态面，并由 `ingestion_40_error_and_blocker_contract.md` 定义它们是否阻塞下游 read content。

## 10. 与相邻文档的关系

- `ingestion_00_overview.md`：定义 ingestion family 的整体分层。
- `ingestion_20_archive_message_contract.md`：定义 connector handoff 后的 message archive object。
- `ingestion_40_error_and_blocker_contract.md`：定义 connector error 如何变成 blocker / warning / audit note。
- `source_connectors_and_knowledge_ingestion.md`：旧 connector 边界文档，后续应降级为历史参考或指向本文。
