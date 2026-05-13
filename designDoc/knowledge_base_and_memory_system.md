# Knowledge Base And Memory System

**Version 0.1 — 2026-03-21**

本文档把 `KnowledgeBase` 作为正式设计对象单独展开。它不是学习笔记，而是面向本仓库的系统设计说明。

## Table Of Contents

- [1. Purpose](#1-purpose)
- [2. Scope](#2-scope)
- [3. Internal Layers](#3-internal-layers)
- [4. Core Design Principles](#4-core-design-principles)
- [5. Core Object Set](#5-core-object-set)
- [6. Retrieval Model](#6-retrieval-model)
- [7. Relationship To Analysis Platform](#7-relationship-to-analysis-platform)
- [8. Current Repo Direction](#8-current-repo-direction)
- [9. Theme Horizon As A First-Class Research Field](#9-theme-horizon-as-a-first-class-research-field)

Detailed companion docs:

- [`ingestion_00_overview.md`](ingestion_00_overview.md): source intake, archive object, canonical source read content, and ingestion/read boundary
- [`ingestion_20_archive_message_contract.md`](ingestion_20_archive_message_contract.md): canonical message archive, tag taxonomy, source identity, and mutable links
- [`research_10_thematic_workflow.md`](research_10_thematic_workflow.md): `read_content.md` / `agent_evidence.json` 之后的 snapshot / theme / thesis promotion workflow
- [`temp/research_mail_workflow_handoff.md`](temp/research_mail_workflow_handoff.md): short operational handoff for a new context window

---

## 1. Purpose

`KnowledgeBase` 是 `trading_platform` 的长期记忆面。

它的目标不是“存资料”，而是让系统能持续积累：

- 研究材料
- 组合状态
- 决策依据
- 结果反馈

并让这些内容在未来分析中可被可靠检索与复用。

---

## 2. Scope

知识库应覆盖三类核心对象：

### 2.1 Research Memory

- newsletters
- reports
- notes
- links
- attachments
- normalized research records

### 2.2 Operating Memory

- account snapshots
- exposure states
- ranked opportunities
- recommendations
- monitoring records

### 2.3 Decision Memory

- memos
- PM decisions
- rejected ideas
- post-trade reviews
- review outcomes

---

## 3. Internal Layers

知识库内部建议分四层：

### 3.1 Raw Artifacts

原始邮件、网页、PDF、附件、截图、原始文本。

### 3.2 Normalized Records

对原始内容做最小但稳定的结构化，形成统一对象。

### 3.3 Searchable Indexes

面向 retrieval 和快速定位的索引层。

### 3.4 Memo And Review Archive

历史判断、正式建议、执行前后复盘的长期存储层。

对 research memory，推荐把 promotion path 理解为 `branching graph`，而不是单一线性流水线：

`messages/ -> snapshots/ -> thesis_notes/`

同时：

`messages/ / snapshots/ / thesis_notes/ -> theme_update_drafts/ -> reviewed theme objects`

其中：

- `messages/` 保留完整 source context
- `snapshots/` 保留原子证据
- `thesis_notes/` 保存 approved durable judgment
- `theme_update_drafts/` 保留待审核的主题维护综合层
- reviewed `theme objects` 保存正式主题层，包括少量 top-level theme 与更多 regional/industry theme

其中 `messages/` 的正文协议建议再区分：

- `main content`：尽量保留 source 原始主体文本
- `normalized content`：去除 CTA、tracking URL、newsletter footer 等噪音后的版本
- `effective content`：通过自动 review 选择后默认暴露给下游的单一正文接口

内部 review 不应只回答 `main` 还是 `normalized`，还应回答当前 source 更适合哪种阅读模式：

- `text_led`：正文文本已经足够，默认直接暴露所选文本版本
- `image_led`：图片 review 才是主证据，默认外部正文应以 reviewed image evidence 为主
- `hybrid`：正文文本和图片 review 都重要，默认外部正文应合并两者
- `needs_image_review`：系统判断该 source 很可能是 image-led，但图片还未 review；此时应明确暴露 `pending/failed image review` 状态，而不是静默回退到低质量 fallback 文本

外部调用方默认只应消费 `effective content`，而不应自己决定 `main` 还是 `normalized`，也不应再额外判断该 source 是 text-led 还是 image-led。

对图片证据，建议再明确一层 `image review` 协议：

- `image_reviews.jsonl` 是 archive 内部的局部证据层，不是最终报告层
- 兼容保留基础字段：`image_type`、`summary`、`ocr_text`、`key_numbers`、`claims_supported`、`confidence`
- richer review 可继续补充：`page_role`、`evidence_value`、`main_takeaway`、`visible_facts`、`inference`、`uncertainties`、`pm_relevance`、`incremental_evidence`、`visuals`
- `visible_facts` 和 `inference` 必须分开，避免把看见的内容和推断混成一句话
- 对 multi-page research PDF，要允许 `page_role=disclosure` / `appendix` 之类的低价值页面被自动降权，而不是让它们和核心分析页同等进入 downstream surface

---

## 4. Core Design Principles

- raw capture 优先于过度预处理
- 最小整理优先于一次性深解析
- 重要的是对象关系，而不是某个具体数据库
- source provenance 必须保留
- 组合状态和研究材料必须能互相链接
- memo 和 review 不能只是附属文本，应是正式知识对象

### 4.1 Projection Boundary Rule

不要让某一个下游格式变成整个知识库的万能承载物。

对 research memory，建议明确区分四类 surface：

- `archive format`：保存 full-fidelity source，包括正文、附件、links、抓取与路由元信息
- `semantic objects`：从 archive 提炼出的稳定对象，例如 `ResearchSnapshot`、`ThemeUpdateDraft`、`ThesisNote`
- `task projections`：面向某一个下游任务的临时投影，例如 writer package、verification packet、ranking packet
- `final artifacts`：最终给人阅读和使用的正式产物，例如 theme report、memo、review

规则：

- `archive format` 应优先保证完整保存，而不是优先适配某个写作任务
- `task projection` 不应原样继承 archive 中的全部技术字段、link exhaust、抓取痕迹或 sync metadata
- 同一份 source 可以同时支持多个 projection，但每个 projection 只应携带对该任务直接有语义价值的信息
- `ThemeUpdateDraft` 的 `.package.md` 应被视为 `writer projection`，而不是 archive dump
- 若未来需要 verification、ranking、asset mapping 等任务输入，应优先新增对应 projection，而不是不断膨胀 writer package

对 writer projection，推荐的默认方向是：

- full text in
- operational metadata out
- provenance preserved in thin form

也就是说，writer package 可以保留完整清洗原文，但应去掉与写作判断无直接关系的 `id`、索引行、抓取日志、技术性 links dump 和 connector plumbing。

---

## 5. Core Object Set

当前建议作为正式对象对待的至少包括：

- `SourceArtifact`
- `ResearchRecord`
- `PortfolioStateRecord`
- `RecommendationRecord`
- `MemoRecord`
- `ReviewRecord`

这些对象之间应能通过如下线索互相连接：

- ticker
- basket
- macro topic
- date / time window
- decision reference

对 research-related objects，至少还应保留以下关系：

- `message -> snapshot`
- `message -> theme_update_draft`
- `message -> thesis_note`
- `snapshot -> thesis_note`
- `theme_update_draft -> theme object`
- `theme object -> linked thesis ids`
- `theme object -> parent theme ids`
- `theme object -> child theme ids`
- `thesis_note -> source message ids`
- `thesis_note -> supporting snapshot ids`

---

## 6. Retrieval Model

当前阶段更适合采用：

- minimal ingest parsing
- retrieval-time interpretation

即：

- 接入阶段保存 raw files 和小型索引
- 真正分析时让 Cursor 或 agent 读取原文件和相关记录

但 retrieval-time interpretation 并不代表“无结构”。

最少仍需要：

- stable IDs
- file paths
- source metadata
- compact indexes
- links to memo / review history

但这些 retrieval 结构并不意味着每个下游 surface 都要直接暴露它们。

推荐 contract：

- retrieval layer 保留 `stable IDs`、`paths`、`source metadata`、`link graph`
- semantic layer 保留可复用的判断对象与证据对象
- task projection 只提取当前任务所需的最小 traceability 和完整语义材料

因此：

- `links` 在知识库里是重要的 provenance 结构
- 但全量 `links.json`、`links index rows` 通常不属于 writer projection 的默认正文

---

## 7. Relationship To Analysis Platform

`KnowledgeBase` 不是分析平台。

它负责：

- remember
- organize
- retrieve
- preserve

`AnalysisPlatform` 负责：

- compare
- synthesize
- decide
- present

两者必须分开设计，但必须严密联通。

---

## 8. Current Repo Direction

就 `trading_platform` 而言，知识库演进方向应是：

- source connector archives
- normalized research records
- portfolio state history
- memo archive
- review archive

未来如果需要再引入：

- vector retrieval
- semantic memory
- richer entity graph

也应建立在上述对象体系稳定之后。

Detailed research-memory workflow has been split into:

- [`research_10_thematic_workflow.md`](research_10_thematic_workflow.md)

That companion doc now owns the long-form design for:

- canonical research inbox layers
- snapshot vs long-form rules
- source collection classification
- theme update routing
- theme draft review queue
- thesis promotion gate
- multimodal archive and image workflow
- standard ingestion entry points
- agent vs deterministic coding split

This top-level document keeps only the knowledge-base overview and the downstream theme / asset architecture.

Top-level operating rule:

- new source material should not become `thesis_notes/` directly
- single-source input should first remain in `messages/`
- reusable evidence can be distilled into `snapshots/`
- multi-source synthesis should pass through `theme_update_drafts/`
- only review-approved stable judgment should enter `thesis_notes/`

Unified ingestion artifact rule:

- reusable current-state products such as `news`, `macro`, and `technical_report` should not live only inside one downstream builder like `market observation`
- they should be written into one shared ingestion/state layer with stable type, scope, timestamp, and body fields so multiple tasks can consume the same refreshed object
- examples of intended shared objects:
  - current news / event window selections
  - daily macro report surfaces
  - per-asset canonical technical reports
- task builders such as `market observation`, `theme`, `thesis`, or mail-driven synthesis should prefer consuming that shared artifact layer instead of each one silently redefining refresh policy
- refresh policy belongs to the ingestion/coordinator layer; task builders should mainly declare what artifact freshness they require

---

## 9. Theme Horizon As A First-Class Research Field

研究对象不应只记录“ticker + thesis”，还应记录该 thesis 所属的时间框架。

### 9.1 Why It Matters

同一个标的可能同时满足：

- `structural long`
- `tactical risk asset`

例如：

- `TSLA` 可因机器人、储能、制造平台而成为长期结构性多头
- `OUST` 可因供应链关键位置而成为中长期主题仓位
- `FLNC` 可因北美储能逻辑而成为长期主题表达

但若未来 `1-2 months` 存在伊朗战争、霍尔木兹海峡、油价与供应短缺的战术风险窗口，上述标的也可能同时需要：

- lower net exposure
- hedge overlay
- explicit reentry criteria

### 9.2 Suggested Research Fields

对 `ResearchRecord`，建议增加至少以下语义字段：

- `document_type`
- `stance`
- `time_horizon`
- `primary_entities`
- `thesis_family`
- `theme_horizon`
- `tactical_window`
- `structural_thesis`
- `tactical_risk`
- `hedge_overlay`
- `dehedge_or_reentry_condition`

### 9.3 Bilingual Interpretation Rule

**中文**

- research 不是只回答“这个票好不好”
- research 需要回答“这个票在哪个时间框架上成立”
- 如果长期逻辑成立、短期风险升高，系统应允许 `core long + hedge overlay`

**English**

- Research should not only answer whether a ticker is good or bad.
- Research should answer which time horizon the thesis belongs to.
- If the structural thesis is intact but the tactical risk window is elevated, the system should allow `core long + hedge overlay`.

### 9.4 Retrieval Implication

未来 retrieval 不应只按：

- ticker
- macro topic
- date

还应支持按以下问题召回：

- 哪些标的是 `structural long but tactical hedge now`
- 哪些主题属于 `1-8 weeks`
- 哪些建议要求 `index put` 或 `industry put`
- 哪些判断是在事件结束后允许恢复净多头

这样知识库才能真正支持 PM workflow，而不是只做资料仓库。

### 9.4A Theme Report Layer

除了 `ResearchItem` / `ThesisNote` / `AssetLogicCard` 外，建议增加一层专门用于“当前主题组织与优先级”的对象：

- `ThemeAnalyticReport`
- `ThemeIndex`
- `CurrentPriorityTree`

其中：

- `ThemeAnalyticReport` 是给人读的完整 macro theme 文档
- `ThemeIndex` 是给机器读的结构化主题注册表
- `CurrentPriorityTree` 是从 `ThemeIndex` 派生出来的当前排序视图

它们不是长期单资产记忆，也不是单条 thesis。

它们的职责是：

- 表示当前值得优先处理的 top-level themes
- 表示更多真正承接 thesis 的 `regional economic themes` 与 `industry themes`
- 把人读的完整逻辑与机器读的结构化字段分开
- 指出每个主题当前更适合调用哪个 skill / workflow
- 把“当前优先级”与“长期可复用判断”分开
- 记录该主题如何随 source materials 和时间演进

Theme hierarchy rule:

- `theme` 不是一个扁平层
- top-level themes 应该很少
- 系统里应当更多是 `regional economic themes` 和 `industry themes`
- thesis 是这些主题之下更细的 durable judgment layer

推荐把三层理解为：

- `top_level`:
  - 跨资产、跨地区、跨多个行业支路的 regime layer
  - 例如 AI industrialization、global liquidity plumbing、modern warfare / rearmament
- `regional_economic`:
  - 以国家、地区、政策-经济结构为中心的主题对象
  - 例如 Japan normalization、Europe gas-cost relief、China property-credit transition
- `industry`:
  - 以行业、价值链、capability stack、business model 结构为中心的主题对象
  - 例如 datacenter power stack、counter-UAS stack、autonomy platform economics

默认 promotion rule：

- 不要把一组相关 thesis 默认直接升成新的 top-level theme
- 先判断它是否更自然地构成 `regional_economic` 或 `industry` theme
- 只有当它明显统领多个地区/行业主题时，才升级成新的 top-level theme

推荐 canonical paths：

- `data/research/themes/index.json`
- `data/research/themes/current_priority_tree.json`
- `data/research/themes/hierarchy_index.json`
- `data/research/themes/reports/<theme_id>.md`
- `data/research/themes/metadata/<theme_id>.json`

其中 canonical rule 应该明确为：

- `reports/*.md` 是人读主文档
- `metadata/<theme_id>.json` 是机器读主文档
- `index.json` 只是自动生成的轻量入口
- `current_priority_tree.json` 只是自动生成的排序视图
- `hierarchy_index.json` 只是自动生成的父子关系与 layer 视图

不应手写维护：

- `index.json`
- `current_priority_tree.json`
- `hierarchy_index.json`

不建议把“当前热点排序”混进：

- `ThesisNote`
- `AssetLogicCard`

因为：

- `ThesisNote` 更像可复用判断
- `AssetLogicCard` 更像资产级长期记忆
- 主题排序和 skill 路由是一个高时效、可快速变更的 PM routing layer

### 9.4B Why Theme Reports Beat Flat Hotspot Lists

单条 `hotspot` 往往不足以表达复杂宏观主题。

例如 `Iran / Hormuz` 不只是一个 trade idea，而是多个冲击链的组合：

- oil supply shock
- shipping / supply-chain disruption
- LNG / gas tightness
- Japan imported energy shock
- inflation persistence
- real-rates surge
- defense and security complex

这些链条：

- 影响不同板块
- 作用在不同时间尺度
- 有时甚至会对同一资产给出相反方向的压力

因此主题层更适合拆成：

- 少量 top-level themes
- 其下若干 first-class `regional economic themes` 或 `industry themes`
- 每个主题对象内部再允许保留 report-local sections

而不是只维护一个扁平 `top ideas` 列表。

### 9.4C Suggested Theme Directory Shape

建议 `themes/` 至少包含：

- `index.json`
- `current_priority_tree.json`
- `hierarchy_index.json`
- `reports/`
- `metadata/`

其中：

- `index.json` 是自动生成的主题目录入口
- `current_priority_tree.json` 是自动生成的当前排序视图
- `hierarchy_index.json` 是自动生成的主题层级视图
- `reports/*.md` 是每个主题对象的正式人读报告
- `metadata/*.json` 是每个主题对象的机器读结构化文档

推荐 `index.json` 只保留轻量字段：

- `schema_version`
- `updated_at`
- `generation_rule`
- `themes`

其中每个 `theme` 推荐字段：

- `id`
- `title`
- `status`
- `theme_level`
- `priority_bucket`
- `priority_rank`
- `parent_theme_ids`
- `child_theme_ids`
- `top_level_theme_id`
- `theme_path`
- `metadata_path`

推荐 `metadata/<theme_id>.json` 至少包含：

- `id`
- `title`
- `status`
- `theme_level`
- `theme_kind`
- `time_horizon`
- `summary`
- `why_now`
- `preferred_skill`
- `priority_bucket`
- `priority_rank`
- `last_reviewed_at`
- `evidence_status`
- `open_questions`
- `parent_theme_ids`
- `child_theme_ids`
- `top_level_theme_id`
- `region_tags`
- `industry_tags`
- `linked_research_ids`
- `linked_thesis_ids`
- `linked_asset_tickers`
- `sections`

其中：

- `theme_level` 固定回答当前对象是 `top_level`、`regional_economic` 还是 `industry`
- `theme_kind` 用于更细粒度描述对象主语义，例如 `policy_regime`、`country_macro`、`value_chain`、`capability_stack`
- `sections` 只表示该 report 内部的人读分节，不默认承担 first-class middle-layer theme object 的责任

推荐新增 `hierarchy_index.json`：

- `schema_version`
- `updated_at`
- `roots`
- `nodes`

其中每个 `node` 推荐字段：

- `id`
- `title`
- `theme_level`
- `status`
- `parent_theme_ids`
- `child_theme_ids`
- `top_level_theme_id`
- `priority_bucket`
- `priority_rank`
- `linked_asset_tickers`

推荐每个 `ThemeAnalyticReport` 至少包含：

- title
- summary
- scope and market structure
- current logic / framework
- main article
- why it matters now
- child themes or report sections
- affected baskets / assets
- linked thesis notes
- linked research items
- development log
- monitoring triggers
- upgrade / downgrade conditions

### 9.4D Operating Rule

建议 agent 处理当前 PM 请求时按以下顺序：

1. 先判断当前请求属于哪个 `task mode`
2. 若该请求确实是 `macro / theme-oriented`，再读 `themes/index.json`
3. 再读对应 `metadata/<theme_id>.json`
4. 再读 `reports/<theme_id>.md`，把它当作 `theme_path` 指向的 canonical 人读 surface
5. 再读 `current_priority_tree.json` 作为当前排序视图和 fallback chooser
6. 判断当前请求属于哪个 `theme` / `child theme` / `mainline`
7. 调用对应 `preferred_skill`，默认应优先落到 `research-theme-report-owner` 这个上游 owner
8. 最后再回到：
   - `ResearchItem`
   - `ThesisNote`
   - `AssetLogicCard`

项目内可以进一步通过 router skill 固化这一步，例如：

- 先用 `routing-task-mode-router` 判断当前请求属于哪条 `task mainline`
- 若该请求已经明确属于 `macro/theme` 路径，或其他主线只需要 `theme overlay`，再用 `routing-current-macro-priority-router`
- 若目标是更新 theme 内容、证据、subtheme、thesis，则先转给 `research-theme-report-owner`，再由其路由到 `research-theme-knowledge-and-package-curator`
- 若目标是更新优先级、排序、routing、priority tree，则转给 `research-theme-priority-updater`
- 若两者都要做，先通过 `research-theme-report-owner` 跑内容更新，再跑 `research-theme-priority-updater`
- 再把请求转发给：
  - `writer-handoff`
  - 或其他后续新增的主题 skill

换句话说：

- `task mode` 负责顶层入口分类
- `routing-task-mode-router` 负责把真实请求先落到正确主线，而不是让某个 theme/router 名称静默充当所有对话的入口
- `CurrentPriorityTree` 负责分析层里的 theme / mainline fallback
- `ThesisNote` 负责可复用判断单元
- `AssetLogicCard` 负责资产记忆

### 9.4D0 Theme / Scenario / Thesis

当前推荐不要把 `theme` 简化成“thesis 的唯一主容器”。

更准确的关系应是：

- `top-level theme` = 更高阶的 regime 或 umbrella
- `regional/industry theme` = 真正常驻承接 thesis 的中间主题对象
- `scenario` = 某个 theme 下的情景分支
- `thesis` = 可复用判断单元

因此：

- 一个 top-level theme 可以覆盖多个 regional/industry themes
- 一个 regional/industry theme 在不同 scenario 下可以激活不同 thesis 组合
- thesis 可以被多个 theme 或 scenario 复用
- thesis 可以出现在多个 theme 里；它有结构关系，但默认不是 mutually exclusive container membership
- theme 可以收束 thesis，但不应独占 thesis 的归属

这能更好支持：

- 同一大框架下的情景切换
- 宏观主题与行业 beta thesis 的交叉复用
- 单票、行业、宏观判断之间的层次拆分

### 9.4D2 Index Boundary

`index` 在这一层应被严格视为 `selection / lookup / routing layer`，而不是正文事实层。

固定原则：

- `themes/index.json`、`current_priority_tree.json` 与 `hierarchy_index.json` 只负责定位、排序、轻量选择
- `messages_index.jsonl`、`snapshots_index.jsonl`、`thesis_index.jsonl` 也只负责对象收束与路径指引
- 真正 payload truth 仍在 canonical objects：
  - `messages/<research_id>/...`
  - `snapshots/<snapshot_id>.json|md`
  - `thesis_notes/<thesis_id>.json`
  - `themes/metadata/<theme_id>.json`
  - `themes/reports/<theme_id>.md`

这意味着 package 或 analysis workflow 可以通过 index 选对象，但读取内容时必须回 canonical objects，而不是直接把 index preview 当正文事实源。

### 9.4D1 Theme Update Approval Gate

当一份新 research 可能改变现有 `theme` / `subtheme` 所依赖的 thesis 时，建议 workflow 固定为：

1. 先归档 research 到 `messages/`
2. 读取 `metadata.source_collection`，结合 `default_theme_tags`、`theme_bias`、`preferred_output_layer` 判断它是否应先落到 `snapshot` 还是直接进入 theme draft
3. 生成 `summary`
4. 若该输入已形成 theme 级证据，再生成或更新 `theme_update_drafts/` 中该 main theme 的候选草案
5. 由 PM 人工审核 draft
6. 审核通过后才：
   - merge 到 `themes/reports/<theme_id>.md`
   - promote 到 `thesis_notes/`
   - 修改 `themes/metadata/<theme_id>.json` 中的 `linked_research_ids`
   - 修改 `themes/metadata/<theme_id>.json` 中的 `linked_thesis_ids`
   - 必要时修改 `subthemes`
7. 最后运行 deterministic builders，刷新：
   - `thesis_index.jsonl`
   - `themes/index.json`
   - `themes/current_priority_tree.json`

这样可以避免：

- 新 report 直接改坏现有 thesis
- 未确认结论过早进入 theme routing
- `current_priority_tree.json` 反映未批准状态
- theme 证据层和 thesis 正式层脱节

### 9.4F Theme-Derived Watchlists And PostgreSQL Mirror

`themes/metadata/*.json` 仍然是 theme 语义层的 canonical authoring source。

但当系统进入 market coverage / watchlist orchestration 阶段时，建议增加一个 Postgres middle layer，把 theme 信息投影成可执行对象。

建议把以下对象视为 Postgres 中的 operational mirror：

- `tickers`
- `ticker_sources`
- `watchlists`
- `watchlist_members`
- `coverage_status`

其中：

- `linked_asset_tickers` 决定 theme / subtheme 对哪些资产有操作意义
- `current_priority_tree.json` 提供当前 `priority_bucket` / `priority_rank`
- Postgres watchlist 负责给 coverage job、connector sync、read API 提供统一入口

推荐生成规则：

1. 每个 theme 生成一个 watchlist：`theme:<theme_id>`
2. 每个有 ticker 的 subtheme 生成一个 watchlist：`subtheme:<theme_id>:<subtheme_id>`
3. 每个成员同时写入 provenance，说明它来自：
   - `theme`
   - `subtheme`
   - `tv_watchlist`
   - `thesis`

换句话说：

- JSON files 负责语义编辑
- Postgres 负责 operational orchestration
- coverage job 默认只从 Postgres ticker universe 取待更新对象

这能避免：

- theme 改了但 coverage universe 没更新
- connector 加了 ticker 但 theme/router 看不到
- 不同 runtime surface 各自维护一套 watchlist

### 9.4E Dedicated Skill Admission Rule

不是每个 theme 都应该升级为专门 skill。

推荐门槛：

- 只有当某个 theme 会系统性影响：
  - portfolio routing
  - holdings review
  - rebalance framing
  - cross-asset risk interpretation
  才值得做 dedicated skill

适合 dedicated skill 的通常是：

- `Iran / Hormuz / oil-gas-rates shock`
- `Fed rate cycle`
- 其他会影响整个组合风险框架的 regime 级主题

不适合 dedicated skill、但仍应保留在系统中的通常是：

- 学习型主题
- 区域型主题
- 只影响少数板块或小仓位的主题

这些对象更适合停留在：

- `CurrentPriorityTree`
- `ThesisNote`
- `AssetLogicCard`
- 通用 skill，如 `writer-handoff`

判断时可问三个问题：

1. 这个 theme 影响的是整个组合，还是只有一小部分暴露？
2. 它是否真的需要一个独立 workflow，而不是 generic synthesis 就够了？
3. 它是否会被反复作为 routing layer 使用？

若答案大多是否，则不应创建 dedicated skill。

### 9.5 AssetLogicCard JSON Shape

为了让 AI 更稳定地理解每个资产的逻辑，建议把单资产研究对象标准化为 `AssetLogicCard`。

它应当：

- 可以直接作为 JSON 存储
- 字段稳定，方便 SQLite / Postgres / document DB 整理
- 同时保留当前状态与编辑历史

当前建议的 canonical file path：

- `data/knowledge/asset_logic_cards/<TICKER>.json`
- `data/knowledge/asset_logic_cards/index.jsonl`

推荐字段：

- `id`
- `ticker`
- `name`
- `asset_type`
- `theme_tags`
- `position_role`
- `theme_horizon`
- `structural_thesis`
- `tactical_risk`
- `technical_framework`
- `hedge_overlay`
- `invalidations`
- `monitoring_signals`
- `intelligence_watchlist`
- `source_thesis_ids`
- `source_research_ids`
- `created_at`
- `updated_at`
- `last_reviewed_at`
- `edit_log`

其中时间字段统一建议：

- ISO 8601 UTC
- 例如：`2026-03-23T18:05:00Z`

### 9.6 Database-Friendly JSON Example

```json
{
  "id": "asset_logic_tsla",
  "ticker": "TSLA",
  "name": "Tesla",
  "asset_type": "equity",
  "theme_tags": [
    "robotics",
    "energy_storage",
    "manufacturing_platform"
  ],
  "position_role": "core_long_with_tactical_hedge",
  "theme_horizon": {
    "tactical": {
      "window": "1-8 weeks",
      "state": "elevated_risk"
    },
    "intermediate": {
      "window": "1-3 quarters",
      "state": "positive"
    },
    "structural": {
      "window": "1-3 years",
      "state": "positive"
    }
  },
  "structural_thesis": "Global leader in robotics scale-up, energy storage, and manufacturing platform leverage.",
  "tactical_risk": "In an Iran-war and oil-spike window, TSLA may face supply-chain stress, multiple compression, and short-term risk-off pressure.",
  "technical_framework": {
    "timeframe": "1d",
    "trend_state": "uptrend",
    "trend_basis": {
      "structure": "higher_highs_higher_lows",
      "moving_averages": [
        "20d",
        "50d",
        "200d"
      ]
    },
    "risk_levels": {
      "stop_loss": 312.0,
      "trend_invalidation": 298.0
    },
    "take_profit_levels": [
      {
        "level": 365.0,
        "action": "trim_25"
      }
    ],
    "add_zones": [
      {
        "zone_low": 320.0,
        "zone_high": 330.0,
        "condition": "pullback_holds_20d_or_prior_breakout"
      }
    ],
    "breakdown_condition": "daily_close_below_key_support_for_2_sessions",
    "reentry_condition": "reclaims_support_with_volume_and_structure",
    "notes": "Daily rhythm only."
  },
  "hedge_overlay": {
    "needed": true,
    "methods": [
      "QQQ put",
      "TSLA put",
      "semiconductor hedge"
    ]
  },
  "invalidations": [
    "robotics scale-up stalls materially",
    "energy storage growth decelerates structurally",
    "manufacturing execution deteriorates beyond base-case"
  ],
  "monitoring_signals": [
    "oil price",
    "shipping disruption",
    "battery supply headlines",
    "robotics production milestones"
  ],
  "intelligence_watchlist": [
    {
      "signal": "macro_or_industry_data",
      "why_it_matters": "Explains whether the thesis is strengthening or weakening."
    }
  ],
  "created_at": "2026-03-23T18:00:00Z",
  "updated_at": "2026-03-23T18:05:00Z",
  "last_reviewed_at": "2026-03-23T18:05:00Z",
  "edit_log": [
    {
      "edited_at": "2026-03-23T18:00:00Z",
      "editor": "pm",
      "change_type": "create",
      "summary": "Created initial structural thesis card."
    },
    {
      "edited_at": "2026-03-23T18:05:00Z",
      "editor": "pm",
      "change_type": "risk_update",
      "summary": "Raised tactical risk due to Iran-war and supply-chain scenario."
    }
  ]
}
```

### 9.7 Logging Rule

最少应保留以下三个时间/日志字段：

- `updated_at`: 最近一次编辑时间
- `last_reviewed_at`: 最近一次人工或 agent 审核时间
- `edit_log`: 结构化变更日志

`edit_log` 建议至少包含：

- `edited_at`
- `editor`
- `change_type`
- `summary`

这样未来无论落在 SQLite、Postgres 还是 JSON 文件，都能较稳定地支持：

- 最近更新排序
- 变更审计
- AI 按最近逻辑变化做优先检索

`technical_framework` 的详细设计见：

- [`research_20_technical_framework_v0_1.md`](research_20_technical_framework_v0_1.md)

### 9.8 AssetLogicCard Index Contract

`index.jsonl` 的目标不是复制完整卡片，而是提供一个轻量、稳定、可排序、可过滤的入口层。

建议遵循以下原则：

- `index.jsonl` 只放高频检索字段
- 详情解释、长文本、复杂结构保留在 `<TICKER>.json`
- index 记录必须能独立完成：
  - ticker 查找
  - role 过滤
  - horizon / risk 状态过滤
  - 最近更新时间排序
  - 跳转到完整卡片

#### Required In `index.jsonl`

以下字段建议为索引层必填：

- `id`
- `ticker`
- `name`
- `asset_type`
- `position_role`
- `theme_tags`
- `tactical_state`
- `intermediate_state`
- `structural_state`
- `technical_timeframe`
- `trend_state`
- `updated_at`
- `last_reviewed_at`
- `card_path`

#### Keep Only In Full Card

以下字段建议只保留在完整卡片中：

- `structural_thesis`
- `tactical_risk`
- `technical_framework` 的完整细节
- `hedge_overlay`
- `invalidations`
- `monitoring_signals`
- `intelligence_watchlist`
- `source_thesis_ids`
- `source_research_ids`
- `edit_log`

#### Why The Split Matters

这样拆分之后：

- `index.jsonl` 适合快速扫描与批量检索
- `<TICKER>.json` 适合深度阅读与 AI 推理
- 后续若迁移到 SQLite / Postgres，也能直接映射为：
  - index table
  - full object table / JSON column

#### Suggested Usage Pattern

推荐工作流：

1. 编辑或新增 `<TICKER>.json`
2. 运行 index builder 重建 `index.jsonl`
3. 先读取 `index.jsonl`
4. 根据 `ticker`、`position_role`、`tactical_state`、`updated_at` 做过滤
5. 再根据 `card_path` 打开完整资产卡

这样可以避免每次让 AI 一上来就读所有长卡片。

#### Index Build Rule

`index.jsonl` 不应被长期手工维护。

建议通过一个 deterministic builder 脚本，从 canonical path：

- `data/knowledge/asset_logic_cards/*.json`

自动抽取索引字段并重建：

- `data/knowledge/asset_logic_cards/index.jsonl`

`ThesisNote` 也建议采用同样原则：

- 编辑或新增 `data/research/thesis_notes/*.json`
- 运行 deterministic builder 重建 `data/research/thesis_index.jsonl`

这样可以减少：

- index 与详情卡不一致
- 新卡漏入索引
- 人工维护重复劳动

### 9.9 Example AssetLogicCards

以下样例不是自动生成信号，而是为了验证 schema 是否能承载真实 PM 思维。

#### Example 1: `TSLA`

```json
{
  "id": "asset_logic_tsla",
  "ticker": "TSLA",
  "name": "Tesla",
  "asset_type": "equity",
  "theme_tags": [
    "robotics",
    "energy_storage",
    "manufacturing_platform",
    "high_beta_growth"
  ],
  "position_role": "core_long_with_tactical_hedge",
  "theme_horizon": {
    "tactical": {
      "window": "1-8 weeks",
      "state": "elevated_risk"
    },
    "intermediate": {
      "window": "1-3 quarters",
      "state": "positive"
    },
    "structural": {
      "window": "1-3 years",
      "state": "positive"
    }
  },
  "structural_thesis": "Tesla is a structural long through robotics scale-up, global manufacturing leverage, and energy storage deployment.",
  "tactical_risk": "In an Iran-war and oil-spike window, TSLA may face supply-chain disruption, growth-multiple compression, and broad risk-off pressure.",
  "technical_framework": {
    "timeframe": "1d",
    "trend_state": "transition",
    "trend_basis": {
      "structure": "watch_for_higher_low_vs_recent_swing",
      "moving_averages": [
        "20d",
        "50d",
        "200d"
      ],
      "momentum_check": "prefer_price_above_20d_before_adding"
    },
    "risk_levels": {
      "stop_loss": null,
      "trend_invalidation": null
    },
    "take_profit_levels": [
      {
        "level": null,
        "action": "trim_into_sharp_event_rally",
        "reason": "reduce_tactical_beta"
      }
    ],
    "add_zones": [
      {
        "zone_low": null,
        "zone_high": null,
        "condition": "pullback_holds_key_support_and_reclaims_20d",
        "priority": "high"
      }
    ],
    "breakdown_condition": "loses_key_daily_support_and_fails_to_reclaim_it",
    "reentry_condition": "daily_trend_rebuilds_with_higher_low_and_support_reclaim",
    "notes": "Keep the long-term thesis separate from the event-risk hedge decision."
  },
  "hedge_overlay": {
    "needed": true,
    "methods": [
      "QQQ put",
      "TSLA put",
      "semiconductor or growth hedge"
    ]
  },
  "invalidations": [
    "robotics commercialization stalls materially",
    "energy storage growth loses scale advantage",
    "manufacturing execution deteriorates structurally"
  ],
  "monitoring_signals": [
    "robotics deployment milestones",
    "Megapack growth",
    "oil price shock",
    "shipping and component-supply headlines"
  ],
  "created_at": "2026-03-23T18:20:00Z",
  "updated_at": "2026-03-23T18:20:00Z",
  "last_reviewed_at": "2026-03-23T18:20:00Z",
  "edit_log": [
    {
      "edited_at": "2026-03-23T18:20:00Z",
      "editor": "pm",
      "change_type": "create",
      "summary": "Created TSLA example card with structural long plus tactical hedge framing."
    }
  ]
}
```

#### Example 2: `OUST`

```json
{
  "id": "asset_logic_oust",
  "ticker": "OUST",
  "name": "Ouster",
  "asset_type": "equity",
  "theme_tags": [
    "sensors",
    "autonomy_supply_chain",
    "industrial_automation",
    "high_beta_growth"
  ],
  "position_role": "satellite_long_with_tactical_hedge",
  "theme_horizon": {
    "tactical": {
      "window": "1-8 weeks",
      "state": "high_risk"
    },
    "intermediate": {
      "window": "1-3 quarters",
      "state": "positive"
    },
    "structural": {
      "window": "1-3 years",
      "state": "positive"
    }
  },
  "structural_thesis": "Ouster is a thematic supply-chain enabler for autonomy, industrial sensing, and next-wave machine perception.",
  "tactical_risk": "OUST is vulnerable to short-term liquidity stress, event-driven de-risking, and multiple compression during a war-driven risk-off window.",
  "technical_framework": {
    "timeframe": "1d",
    "trend_state": "transition",
    "trend_basis": {
      "structure": "respect_recent_breakout_only_if_pullback_holds",
      "moving_averages": [
        "20d",
        "50d"
      ],
      "momentum_check": "avoid_adding_if_daily_structure_rolls_over"
    },
    "risk_levels": {
      "stop_loss": null,
      "trend_invalidation": null
    },
    "take_profit_levels": [
      {
        "level": null,
        "action": "trim_on_failed_breakout_or_event_spike",
        "reason": "high_beta_name"
      }
    ],
    "add_zones": [
      {
        "zone_low": null,
        "zone_high": null,
        "condition": "pullback_to_support_holds_and_volume_contracts",
        "priority": "medium"
      }
    ],
    "breakdown_condition": "fails_support_and_breaks_prior_swing_low_on_daily_close",
    "reentry_condition": "rebuilds_base_and_reclaims_breakout_level",
    "notes": "Treat as a smaller thematic expression, not a benchmark-like core."
  },
  "hedge_overlay": {
    "needed": true,
    "methods": [
      "QQQ put",
      "small_position_size",
      "trim_into_strength"
    ]
  },
  "invalidations": [
    "sensor platform loses adoption momentum",
    "end-market demand weakens structurally",
    "competitive moat does not scale as expected"
  ],
  "monitoring_signals": [
    "new design wins",
    "gross margin trend",
    "industrial demand",
    "daily liquidity and volatility"
  ],
  "created_at": "2026-03-23T18:22:00Z",
  "updated_at": "2026-03-23T18:22:00Z",
  "last_reviewed_at": "2026-03-23T18:22:00Z",
  "edit_log": [
    {
      "edited_at": "2026-03-23T18:22:00Z",
      "editor": "pm",
      "change_type": "create",
      "summary": "Created OUST example card as a structural satellite long with higher tactical beta risk."
    }
  ]
}
```

#### Example 3: `FLNC`

```json
{
  "id": "asset_logic_flnc",
  "ticker": "FLNC",
  "name": "Fluence Energy",
  "asset_type": "equity",
  "theme_tags": [
    "energy_storage",
    "grid_infrastructure",
    "north_america_power_theme",
    "high_beta_growth"
  ],
  "position_role": "core_theme_long_with_tactical_hedge",
  "theme_horizon": {
    "tactical": {
      "window": "1-8 weeks",
      "state": "elevated_risk"
    },
    "intermediate": {
      "window": "1-3 quarters",
      "state": "positive"
    },
    "structural": {
      "window": "1-3 years",
      "state": "positive"
    }
  },
  "structural_thesis": "Fluence is a leading listed expression of North American energy storage and grid modernization demand.",
  "tactical_risk": "In a war-driven inflation and supply-shortage window, FLNC may see growth-multiple pressure and near-term supply-chain sensitivity despite a favorable long-run thesis.",
  "technical_framework": {
    "timeframe": "1d",
    "trend_state": "transition",
    "trend_basis": {
      "structure": "watch_if_daily_base_holds_after_event_volatility",
      "moving_averages": [
        "20d",
        "50d",
        "200d"
      ],
      "momentum_check": "prefer_adds_only_after_support_reclaim"
    },
    "risk_levels": {
      "stop_loss": null,
      "trend_invalidation": null
    },
    "take_profit_levels": [
      {
        "level": null,
        "action": "trim_partial_on_failed_retest_of_resistance",
        "reason": "protect_against_event_volatility"
      }
    ],
    "add_zones": [
      {
        "zone_low": null,
        "zone_high": null,
        "condition": "daily_pullback_holds_base_and_reclaims_short_term_trend",
        "priority": "high"
      }
    ],
    "breakdown_condition": "breaks_base_support_and remains below it on daily closes",
    "reentry_condition": "base_rebuild plus reclaim of prior support with improving momentum",
    "notes": "Best treated as a medium-term theme long with tactical discipline."
  },
  "hedge_overlay": {
    "needed": true,
    "methods": [
      "QQQ put",
      "clean-energy basket hedge",
      "event-window position reduction"
    ]
  },
  "invalidations": [
    "storage backlog quality weakens materially",
    "grid storage deployment stalls structurally",
    "execution issues overwhelm demand tailwind"
  ],
  "monitoring_signals": [
    "storage backlog",
    "North America deployment wins",
    "battery supply constraints",
    "daily support and resistance behavior"
  ],
  "created_at": "2026-03-23T18:24:00Z",
  "updated_at": "2026-03-23T18:24:00Z",
  "last_reviewed_at": "2026-03-23T18:24:00Z",
  "edit_log": [
    {
      "edited_at": "2026-03-23T18:24:00Z",
      "editor": "pm",
      "change_type": "create",
      "summary": "Created FLNC example card with structural storage thesis and tactical macro hedge overlay."
    }
  ]
}
```
