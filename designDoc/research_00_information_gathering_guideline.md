# Information Gathering Guideline: Source Tiering + Agent Placeholder

For the family-level position of this doc, see
[`research_00_overview.md`](research_00_overview.md).

Related:
- [`ingestion_20_archive_message_contract.md`](ingestion_20_archive_message_contract.md) — where fetched materials persist as archive messages
- [`ingestion_30_ai_read_content_contract.md`](ingestion_30_ai_read_content_contract.md) — canonical source surface consumed by downstream AI agents
- [`research_10_thematic_workflow.md`](research_10_thematic_workflow.md) — promotion path after archived material has a readable source surface
- [`research_50_thesis_and_theme_agent_cluster.md`](research_50_thesis_and_theme_agent_cluster.md) — thesis cluster that consumes archived research
- [`research_00_report_reviewer_pattern.md`](research_00_report_reviewer_pattern.md) — reviewer agent with external-verify phase
- [`research_00_report_polish_framework.md`](research_00_report_polish_framework.md) — polish loop that may request external evidence
- [`source_connectors_and_knowledge_ingestion.md`](source_connectors_and_knowledge_ingestion.md) — existing push-style connectors

## Why This Doc Exists

Research pipelines (thesis drafting / debate / review / polish) regularly need **external facts not yet in the local archive**: Fed speeches fresh off `federalreserve.gov`, market data from today's close, breaking news from the last 24 hours, specific primary-source quotes.

Today these pull-style fetches are done ad hoc via Web Search / Perplexity, then the results live only in one conversation's context. Two problems:

- **Not auditable**：downstream agents can't tell which external fact backed which claim
- **Not reusable**：next week the same Fed speech needs to be re-fetched because it never landed in `data/research/messages/`

This doc fixes two things：

1. **Source caliber taxonomy（T1–T5）**：how to grade external material so downstream agents know what's verdict-quality vs background color
2. **`information-gatherer` agent placeholder**：spec for a future agent that turns one-shot web fetches into archived, tiered, reusable research_messages

The agent itself is not built yet. This doc establishes the contract so when it's built, the stages that invoke it（thesis / debate / review / polish）already have the interface defined.

## Source Caliber Taxonomy

External material carries very different audit weight depending on how close to the original source it is.

| Tier | 类型 | Example | 适合作为 |
|---|---|---|---|
| **T1 — 主 primary** | 原发机构官方文档 / 讲话 / 统计发布 | `federalreserve.gov/newsevents/speech/...` / FOMC 声明 / BLS Employment Situation / BEA PCE / SEC EDGAR filing / 央行 decision 原文 | Verdict-level evidence，可以独立支撑 thesis claim |
| **T2 — 近主 near-primary** | 权威媒体带 direct quote + URL 指向 primary | CNBC / Bloomberg / WSJ / Reuters / Fed 官员媒体采访文本 | 引语可信，支撑 thesis 需要 2 条 T2 交叉或 1 条 T1 补 |
| **T3 — 市场数据 data** | 标准 market data feed / 官方发布机构 | FRED series / Treasury daily rates / 交易所 daily close / CME settle / Bloomberg terminal snapshot | 数据锚点，time-stamped，可以量化 reference |
| **T4 — 聚合 aggregator** | 二手媒体叙事 / 百科 / 综合 recap | Wikipedia / 综合 news recap / analyst 整理 timeline | 事件轮廓可信，数字 / 引语要回 check T1/T2 |
| **T5 — 预测 speculative** | 第三方 forecasts / model projections / unverified commentary | longforecast.com / analyst price target / Twitter speculation | 不作 evidence 用。可作为 "市场共识 snapshot" 的一部分 tag |

### Tier 使用规则

- **Thesis 级别的 claim**（影响 regime identification / asset mapping）至少要 1 条 T1 或 2 条 T2 交叉背书
- **Debate / adversary 的 falsifier** 可以用 T3 market data 或 T2 counter-evidence
- **Review 的外部事实校验** 优先 T1 > T2 > T3
- **T4 仅作 context filler**，数字 / 引语必须回指 T1/T2
- **T5 永远不是 verdict 的最终依据**

### 源口径元数据

每个归档进 `data/research/messages/` 的 research_message 必须带 `source_tier` 元数据（T1-T5）+ 原 URL + 抓取时间戳。消费者（research-thesis-drafter / adversary / reviewer）按 tier 决定能否 cite 到 claim 背书上。

## `information-gatherer` Agent（Placeholder）

### 定位

Pull-style 按需 ingestion agent。区别于现有 `source_connectors_and_knowledge_ingestion` 的 push 式连接器：

- **Push connector**（已有）：`agentmail` / `gmail` / `manual_import` —— 订阅式持续拉流
- **Pull gatherer**（待建）：one-shot 按 query / claim 去 Web Search 或 Perplexity 定向抓

### 调用 stage

本 agent 在三个 upstream stage 被调用：

| Stage | 触发场景 | 输入 | 输出 |
|---|---|---|---|
| **Thesis drafting** | `research-thesis-drafter` 发现 `source_research_ids[]` < 2 或缺关键 T1 支撑 | target theme_id + claim direction + 已知 research_ids gap | 新增 research_ids（入 `messages_index.jsonl`） |
| **Debate / adversary** | `research-thesis-adversary` 需要 external falsifier 或 counter-evidence | thesis_id + 待 stress-test 的 claim | 新 research_ids 作为 falsifier evidence |
| **Review** | `research-theme-report-reviewer` / polish loop 发现 claim 需要 external verify（hard-trigger 命中） | draft section + 需校验 claim 清单 | 新 research_ids + tier 分类（confirmed / not_confirmed / contradicted） |

### Process

1. **Query formulation**：基于 claim / 主题 / 待填 gap 生成 2-5 条窄口径搜索 query。时间窗约束为近期（例如最近 4 周，除非明确要历史参照）
2. **Multi-source search**：Web Search + Perplexity 并行，收集 URL 候选
3. **Tier classification**：每个候选 URL 分 T1-T5
4. **Priority filter**：T1/T2/T3 保留；T4 仅在无更高 tier 时备选；T5 丢弃或仅标为 "speculation context"
5. **Content fetch**：
   - T1 源用 WebFetch 抓原网页，full text archive
   - T2 源抓文章主体 + direct quote extraction
   - T3 源记录数据 snapshot（value + timestamp + series ID）
6. **Archive via `research import-text`**：每条带 `source_tier`、原 URL、抓取时间、stage 调用上下文作为 metadata
7. **Return research_id list**：给调用方（research-thesis-drafter / adversary / reviewer）消费

### 硬约束

- 所有 fetched 内容**必须先落盘**，再消费。不允许 in-context 使用未归档的外部 fact
- 每条归档 research_message 必须带 `source_tier` 元数据
- 外部 fact 的**抓取时间戳 ≠ source 发布时间**。两个 timestamp 都记
- **时间窗纪律**：除非明确要历史参照，搜索默认加最近时间约束（避免拿 3 个月前的 FOMC 当当前 Fed 立场）
- 对 T4（Wikipedia / aggregator）内容，不允许单独作为 thesis claim 背书；必须同时有至少一条 T1/T2 交叉验证
- 若搜索 / 抓取失败，返回结构化 `not_found` 而不是编造

### 不做的事

- 不替 research-thesis-drafter 下 claim（那是 drafter 的判断权）
- 不替 research-thesis-verifier 做 fact-check 的 verdict（verifier 基于归档结果决定 confirmed / not_confirmed / contradicted，但归档本身是 gatherer 的活）
- 不做长期订阅式 ingestion（那是 push connector）
- 不替代人工 source 选择；只在 query / stage 输入已明确时跑

### 接口契约（stage-side contract）

**Thesis-drafter → info-gatherer**：
```yaml
stage: thesis-drafting
theme_id: <snake_case>
claim_direction: <1-2 句 causal chain>
existing_research_ids: [<rid>, ...]  # 已有，避免 refetch
missing_aspects:
  - <evidence aspect 1>  # e.g., "historical Fed doctrine flip precedents"
  - <evidence aspect 2>  # e.g., "current STIR pricing vs Fed dot plot"
required_tiers: [T1, T2, T3]  # optional，默认全要
time_window: <e.g., "last 4 weeks" | "historical">
```

**Thesis-adversary → info-gatherer**：
```yaml
stage: adversary
thesis_id: <rid>
claim_to_stress: <claim[i] text>
falsifier_hypothesis: <what if the opposite were true?>
target_tiers: [T1, T2]  # falsifier 要 high tier
```

**Reviewer → info-gatherer**：
```yaml
stage: review
report_path: <draft md path>
claims_to_verify:
  - text: <claim>
    section: <H2 header>
    expected_tier: T1
```

### 未来 integration 点

当这个 agent 建出来后，下面几个 flow 要改：

- `research-thesis-drafter` 的 entry check："是否 ≥2 source_research_ids 且 ≥1 条 T1/T2"；不满足则先走 info-gatherer
- `research-theme-report-reviewer` 的 "External verification" 阶段：封装成对 info-gatherer 的一次调用
- `research_00_report_polish_framework` v0.3 polish loop：Review mode 里如果 catch 到 "误解 = 事实错 / 逻辑错 / evidence tier 被错误升级"，可以触发 info-gatherer 补证
- reviewer verdict `accept_with_revisions` must-fix 列表可以带 "需要 info-gatherer 补 T1 源" 作为 action item

## 实例：本次 federal_rate_cycle polish loop 的 external verify

（作为未来 agent 落地的参照样本）

本轮 polish 过程中，为 verify `ds_rewrite_v2_from_claude.md` 的 scenario 数字与现实是否对齐，手动跑了 15 条 Web Search query，分 9 条主轴 + 6 条 recent window 校正。发现：

- Scenario 时间线偏差（4 月初 vs 实际 2 月 28 日开战）
- Brent 价格锚点偏差（$109/$67 vs 实际 $101.73/$72）
- Jefferson 原话 `complicated by energy disruption` **找不到 T1 源**，可能是 paraphrase
- 关键事件遗漏：Khamenei 被杀 / Powell 任期 5 月结束 / 4/8 ceasefire / 4/13 blockade
- 关键 Fed 讲话遗漏：Waller "One Transitory Shock After Another"（governor 级质疑 look-through）/ Barr 3/26（governor 级 hawkish flag）

15 条搜索结果需要归档成 ~11 条 research_messages 才能让未来 research-thesis-drafter / reviewer 复用。**这种手工重复劳动正是 `information-gatherer` agent 要自动化的部分**。

## 信息的时间属性最小 schema

**每条进入 writer-facing package 的 message 只带两个时间字段，其它时间字段一律不进 writer view。**

### 两个保留字段

| 字段 | 含义 | 来源示例 |
|---|---|---|
| `data_observed_at` / `data_as_of` | 这条信息所描述的**事实或数据本身发生 / 被测量的时刻** | Brent 收盘价对应 2026-04-22；Jefferson Dallas speech delivery 2026-03-26；NFP revision data 所属期 2026-02 |
| `message_produced_at` | 这条 message 作为一条记录**被表达 / 写下的时刻** | Fed speech transcript 产出日；BLS release 公告日；thesis drafter 写下 claim 的日期 |

### 明确排除的字段

以下字段不进 writer-facing package（可保留在 DB / owner.json / thesis_note 内部作运维字段）：

- `ingested_at` / `archived_at` — 归档到 DB 的时刻，纯运维
- `created_at` / `updated_at` — record ORM 字段
- `drafted_at` / `last_reviewed_at` / `last_reconciled_at` — 生产管理字段
- `schema_version` / `lifecycle_stage` — 框架维护字段
- `audit_trail` / `verified_at` / `adversary_at` — thesis 生产管理字段

理由：这些字段对 writer reasoning 无贡献，仅增加噪声并让 reader 误将"归档日期"当"事实日期"。

### 典型落地情形

大多数情况 `data_observed_at` ≈ `message_produced_at`：
- Fed speech：speech delivery = transcript 产出，同一天
- BLS NFP release：数据公告 = message 产出，同一天
- Market snapshot report：snapshot as-of = report 发布日，差 0-1 天

两者会明显不同的情形（writer 应当心）：
- **下修 / revision**：data_observed_at = 2026-02（数据所属期），message_produced_at = 2026-03-07（修订公告日）
- **Retrospective / historical analysis**：data_observed_at = 2024-Q3，message_produced_at = 2026-04-15
- **Thesis claim**：data_observed_at = claim 覆盖的数据集时间区间，message_produced_at = drafter 写下的日期

两者差距越大，reader 越应警惕"这条陈述是基于过时的 data surface 作出的当前判断"。

### 衰减模型（reader-side heuristic）

两字段足以支撑两种衰减模型，不需要额外的 `superseded_by` 链。Package builder 不做硬分类，让 reader 按信息类别自行判断：

**Causal / observation anchor — time-decay**
- `now - data_observed_at < 2 weeks` → fresh，全权重
- 2-6 weeks → reference
- \> 6 weeks → stale，非 mechanism 支撑则降权
- 判断主轴：data_observed_at 本身与 now 的距离

**Mechanism anchor — replacement-based**
- 同一 speaker / 同一 topic 后续未出现更新 message → load-bearing 保持
- 出现同 speaker 更晚 message（message_produced_at 更新）且 stance 反向 → 旧的 instantly 降级
- 判断主轴：有无后续 message supersede，与 data_observed_at 距离无关

### 与 source_tier 的关系

`source_tier`（T1-T5）与时间字段正交。Tier 决定**证据权重**，时间字段决定**当前有效性**。两者联合使用：
- T1 mechanism anchor（Jefferson Dallas speech）保持 load-bearing，直到同 speaker 出现更晚 T1 反向 message
- T3 market data（Brent $101.73）随 data_observed_at time-decay，2 周后需要新 snapshot

## Package Rebuild Gotcha: owner.json vs metadata linked_*

**Pitfall discovered 2026-04-24**：`build_theme_writer_package` CLI reads material selection **ONLY from the canonical `data/research/theme_update_drafts/<theme_id>.owner.json`** under `selected_materials.{core_recent_research_ids, still_relevant_backbone_research_ids, selected_thesis_note_ids}`.

The theme metadata file `data/research/themes/metadata/<theme_id>.json` fields `linked_research_ids` / `linked_thesis_ids` are **cross-reference registries**, not builder input. Patching metadata alone will NOT flow new theses or research into the next package build. Writer builder checks R2 (owner.json must exist) and then pulls from owner's selected_materials exclusively.

**Correct rebuild sequence**：

1. Confirm or refresh **canonical owner.json** at `data/research/theme_update_drafts/<theme_id>.owner.json`:
   - Extend `selected_materials.core_recent_research_ids` with new research_message IDs intended for current-session priority
   - Extend `selected_materials.still_relevant_backbone_research_ids` with structural / reference-layer sources
   - Extend `selected_materials.selected_thesis_note_ids` with newly-active thesis IDs
   - Update `session_date_market` / `report_date` / `generated_at` / `pass_type`
   - Append new `writer_direction` bullets for any scenario-level corrections the writer must enforce
   - Append new file paths to `reviewed_artifacts`
2. Optionally also refresh metadata `linked_*_ids` so the cross-reference registry stays in sync with owner.json truth — but this is documentation, not builder input.
3. Rebuild via `./.venv/bin/python -m src.cli.tradectl research build-theme-writer-package --theme-id <id> --output <path> --report-date <YYYY-MM-DD>`
4. Verify the new package pulls the expected theses + research cards by grep of the generated markdown.

**Rule**: canonical owner_decision is the builder's single source of truth. Metadata linked_* is a discoverability registry. Future `information-gatherer` agent implementation should automatically update owner.json when a thesis-drafting or verifier-triggered research message lands, not only metadata.

## Status

- **Version 0.3 — 2026-04-23 晚** (add 信息的时间属性最小 schema: `data_observed_at` + `message_produced_at`, exclude ops timestamps)
- **Version 0.2 — 2026-04-24** (add owner.json vs metadata linked_* pitfall + correct rebuild sequence)
- **Version 0.1 — 2026-04-23**
- Placeholder：agent 未实现，接口契约先定
- 下一步：
  - 决定 agent 位置（`.cursor/skills/information-gatherer/SKILL.md`）
  - 实现 Query formulation + tier classification 启发式
  - 批量 import pipeline（目前 `research import-text` 是单条 CLI，批量场景要包装）
  - Perplexity integration（当前 Web Search 已有，Perplexity 需要 API key + client）
  - 与 thesis cluster 的实际 plumbing（research-thesis-drafter entry check 自动路由到 gatherer）
  - 对 T5 speculation 的显式处理路径（是否允许作为 "市场共识" 标签 but 不作 evidence）
