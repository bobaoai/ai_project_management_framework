---
title: Thematic Research Promotion Workflow
status: active_draft
reader_persona:
  - Research Architect
  - Theme Owner
  - Archive Analyst
  - Package Builder
---

# Thematic Research Promotion Workflow

## 1. 这份文档负责什么

本文定义 thematic research 在 ingestion 之后如何进入 snapshot、thesis、theme、writer package 和 final theme report。

本文不定义 source connector、archive object、`read_content.md`、image review policy、message file layout 或 ingestion blocker vocabulary。这些属于 ingestion family：

- `ingestion_00_overview.md`
- `ingestion_20_archive_message_contract.md`
- `ingestion_30_ai_read_content_contract.md`
- `ingestion_40_error_and_blocker_contract.md`
- `ingestion_50_source_family_playbook.md`

Thematic workflow 的起点是：

```text
data/research/messages/<research_id>/read_content.md
```

如果这份 source 需要进入可复用研究记忆，显式运行 research-promotion 派生：

```text
read_content.md
  -> message derive-agent-evidence
  -> agent_evidence.json
  -> snapshots / thesis candidates / theme_update_drafts
```

## 2. 边界句

```text
ingestion owns source readability.
research owns promotion and judgment.
```

`read_content.md` 是 source-level readable surface。它让下游 AI 不必打开 archive internals。

`agent_evidence.json` 是 promotion surface。它由 AI 读取 `read_content.md` 后生成，包含 `document_read`、`image_reads` 和 `evidence_units`，用于 snapshot / thesis / theme routing。

`theme_update_drafts/*.package.md` 是 writer package。它是 task-level input，不是 source archive，也不是 canonical source read content。

## 3. Thematic promotion chain

Thematic research 的默认 promotion chain：

```text
read_content.md
  -> agent_evidence.json
  -> ResearchSnapshot
  -> ThemeUpdateDraft
  -> writer package
  -> writer draft
  -> review gate
  -> ThemeObject / ThemeAnalyticReport / ThesisNote
```

各层职责：

- `read_content.md`：source 内容。由 ingestion 生成和维护。
- `agent_evidence.json`：AI first-pass research evidence。Derived / recomputable。
- `ResearchSnapshot`：从一份或多份 source 中提炼出来的原子研究快照。
- `ThemeUpdateDraft`：尚未 merge 的主题工作层，承接新材料对某个 theme 的潜在影响。
- `theme_context_index`：package 前的显式 selection contract，只回答应该选哪些对象、对象在哪里。
- `theme_update_drafts/<theme_id>.package.md`：writer-facing package，消费 context index 和 canonical objects。
- `theme_update_drafts/<theme_id>.ds.md`：writer draft / review-stage output。
- `themes/reports/<theme_id>.md`：final human-readable theme report。
- `thesis_notes/<thesis_id>.json`：approved durable judgment。
- `themes/metadata/<theme_id>.json`：formal theme object 的 machine-readable routing surface。

## 4. Canonical paths

Research promotion 层使用以下路径：

```text
data/research/snapshots/<snapshot_id>.json
data/research/snapshots/<snapshot_id>.md
data/research/snapshots_index.jsonl
data/research/theme_update_drafts/<theme_id>.json
data/research/theme_update_drafts/<theme_id>.package.md
data/research/theme_update_drafts/<theme_id>.ds.md
data/research/theme_context_indexes/<theme_id>.json
data/research/theme_candidate_queue.json
data/research/themes/metadata/<theme_id>.json
data/research/themes/hierarchy_index.json
data/research/themes/reports/<theme_id>.md
data/research/thesis_notes/<thesis_id>.json
data/research/thesis_index.jsonl
data/research/derived_surfaces_audit.json
```

`messages/<research_id>/` 仍然是 upstream source reference，但它的 file contract 不属于本文。

## 5. Source collection as routing hint

`source_collection` 是 ingestion/source identity 层字段。Research promotion 可以消费它，但不能把它当作最终 theme assignment。

Promotion routing 可读取：

- `source_collection.preferred_output_layer`
- `source_collection.default_theme_tags`
- `source_collection.snapshot_bias`
- `source_collection.theme_bias`
- `source_collection.thesis_bias`

解释规则：

- `preferred_output_layer = snapshot`：默认先生成 snapshot。
- `preferred_output_layer = theme_update`：可作为 theme update candidate，但仍需 owner gate。
- `preferred_output_layer = thesis_candidate`：只能进入 thesis candidate / theme draft review path，不能直接成为 approved thesis。
- `default_theme_tags` 是 retrieval / routing hint，不是 finalized linked theme。
- `theme_bias` 和 `thesis_bias` 帮助缩小候选范围，不替代 AI / owner judgment。

## 6. Snapshot rule

Snapshot 是 thematic research 的原子证据层。

适合进入 snapshot 的材料：

- 单个关键事实；
- 一组关键数字；
- 一个图表证据；
- 一个事件或 regime 观察；
- 一个尚不足以成为 thesis、但未来可能复用的 interpretation。

Snapshot 应保留：

- source research id；
- evidence unit refs；
- source timestamp / observed time；
- source_collection；
- semantic tags；
- related tickers / entities；
- confidence / freshness fields；
- downstream candidate links。

Snapshot 不应承担：

- final PM conclusion；
- full theme report prose；
- portfolio action；
- approved thesis lifecycle。

## 7. ThesisNote rule

`ThesisNote` 是 approved durable judgment，不是 source summary。

它应回答：

- 核心判断是什么；
- 依赖条件是什么；
- 反证条件是什么；
- 哪些 source / snapshots 支撑它；
- 它服务哪些 theme / scenario / asset interpretation；
- freshness 与 review trigger 如何管理。

Promotion 到 thesis 前必须经过 review gate。`agent_evidence.json` 和 snapshots 可以生成 thesis candidate，但不能自动写成 approved thesis。

## 8. ThemeUpdateDraft rule

`ThemeUpdateDraft` 是 review queue。它保存新 research 对某个 theme 的潜在影响，并把 writer draft 与 finalized theme report 分开。

Canonical draft path：

```text
data/research/theme_update_drafts/<theme_id>.json
data/research/theme_update_drafts/<theme_id>.package.md
data/research/theme_update_drafts/<theme_id>.ds.md
```

Theme update owner 必须先判断目标对象是哪一层：

- `top_level`
- `regional_economic`
- `industry`

默认判断顺序：

1. 先问材料是否更适合形成 regional / industry theme。
2. 只有明显统领多个中层主题时，才考虑 top-level theme。
3. 证据不稳定时，保留为 thesis cluster 或 candidate queue。

`themes/index.json`、`themes/current_priority_tree.json`、`themes/hierarchy_index.json` 只能反映 approved theme state。`draft_candidate` 可以有 metadata / report draft 文件，但不能成为正式 routing authority。

## 9. Context index before package

`theme_context_index` 是 package 前的显式 selection contract。

推荐 bucket：

- `backbone_paths`
- `migration_reference_paths`
- `primary_research_ids`
- `update_snapshot_ids`
- `technical_paths`
- `adjacent_context_ids`
- `boundary_context_paths`
- `selected_thesis_ids`

Index 收束要求：

- context index 只回答“选哪些对象、这些对象在哪里”；
- assembler 真正读取内容时必须回 canonical objects；
- index 中的 preview / summary / linked fields 不能当 package 正文；
- bucket 为空只能表示上游明确判定当前无需提供材料；
- 关键信息缺失时应停下补 index，不能从隐式默认值、旧 draft 或 heuristic logic 另开第二条路径。

如果需要额外上下文，先写进 context index，再进入 package assembler。

## 10. Writer package boundary

The full writer-package contract lives in:

```text
research_00_writer_package_contract.md
```

Theme package 的顺序：

```text
owner scope
  -> context index
  -> deterministic package assembly
  -> writer draft
  -> reviewer gate
  -> merge / reject / rewrite
```

Writer package 不应直接让 writer 面对 archive internals。Assembler 应消费 `read_content.md`、`agent_evidence.json`、snapshots、thesis notes、theme metadata、technical reports 等 canonical objects，并按 owner scope 组装。

不要维护多套长期并行 package contract。一旦 canonical bucket contract 确认，收敛到单一路径。

## 11. Review gates

Thematic promotion 需要 review gate：

1. `agent_evidence.json` 生成后：确认 evidence units 没有越过 source boundary。
2. Snapshot 创建后：确认 snapshot 是 atomic evidence，不是 premature thesis。
3. ThemeUpdateDraft 创建后：确认目标 theme level 与 candidate scope。
4. Writer package 生成后：确认 package 完整、不过量、没有 archive plumbing dump。
5. Writer draft 生成后：运行 report reviewer。
6. Merge 前：确认 finalized theme report、thesis notes、metadata、indexes 同步。

正式 theme / thesis changes 是 review-gated。新 research 不应直接 overwrite final theme report 或 thesis note。

## 12. Standard research entry points

Research promotion 入口：

```text
tradectl message derive-agent-evidence
tradectl research draft-snapshot
tradectl research draft-theme-update
tradectl research build-theme-context-index
tradectl research build-theme-candidate-queue
tradectl research build-theme-writer-package
tradectl research audit-derived-surfaces
tradectl research draft-theme-report-ds
```

Upstream ingestion 入口不属于本文 ownership，但常见前置步骤包括：

```text
tradectl message fetch-agentmail
tradectl message import-report
tradectl message import-screenshot
tradectl message review-images-claude
tradectl message refresh
```

## 13. Agent vs deterministic split

Deterministic code 负责：

- 读取 canonical indexes；
- 生成 stable IDs；
- 写 snapshot / thesis / theme index projections；
- 根据 context index 组装 package；
- 维护 freshness / sidecar / manifest；
- 检查 file existence、hash、schema、frontmatter。

AI / owner judgment 负责：

- 判断 source evidence 的 semantic meaning；
- 提炼 evidence units；
- 判断 snapshot vs thesis candidate vs theme update；
- 选择 context index scope；
- 判断 thesis 是否可 approved；
- 写 PM-facing theme prose；
- review writer draft 的 reasoning quality。

边界检测：如果 deterministic code 开始决定 theme thesis meaning，说明越界；如果 AI prompt 直接自己找 archive internals、猜路径、补 missing buckets，说明 package / context index 上游没有完成。

## 14. 相邻文档关系

- `ingestion_00_overview.md`：source intake 到 canonical source read content 的总入口。
- `ingestion_20_archive_message_contract.md`：message archive object file contract。
- `ingestion_30_ai_read_content_contract.md`：`read_content.md` contract。
- `research_00_writer_package_contract.md`：writer-facing package contract。
- `research_00_report_reviewer_pattern.md`：post-writing report reviewer pattern。
- `theme_report_owner` / `theme_knowledge_and_package_curator` skills：执行 owner scope、package assembly、writer draft、review / merge。

