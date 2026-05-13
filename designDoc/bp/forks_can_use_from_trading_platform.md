# Forks 可借用的 trading_platform 资源

面向 Bowen / Forks 团队的单向资产清单 · v1.1 · 2026-04-27

源材料：[`04_areas/work/due_diligent/forks/Forks-MVP-Product-Spec.pdf`](04_areas/work/due_diligent/forks/Forks-MVP-Product-Spec.pdf)（V1.0, 27 页）+ [`designDoc/bp/V5.5-Product-Definition.pdf`](V5.5-Product-Definition.pdf)（V5.5 canonical, 29 页, 2026-04-24）

对照仓库：`bokanbao/trading_platform`

姊妹文档：
- [`designDoc/bp/forks_mvp_relation_to_trading_platform.md`](forks_mvp_relation_to_trading_platform.md) — 双向关系总览
- [`designDoc/bp/trading_platform_t0_tech_brief_20260427.md`](trading_platform_t0_tech_brief_20260427.md) — T0 standalone tech brief（架构 + object model + workflow + skill cluster + maturity）
- [`designDoc/bp/trading_platform_vs_v5_5_comparison_and_mutual_learning_20260427.md`](trading_platform_vs_v5_5_comparison_and_mutual_learning_20260427.md) — 跟 V5.5 对照 + mutual learning + collab 提议

**v1.0 → v1.1 主要变化**（2026-04-27 T0 周末升级 + V5.5 PDF 全文 read 后）：
- 数字校准：thesis_notes 43 → 56；asset_technicals 90 → 90 .md（v1.0 已对，v0.1 doc 1 错算 163 已修）；skills 18 → 27
- 新 schema：`scenario_note v0.1` / `evidence_record v0.2` / `path_observation v0.1` / `freshness_event v0.1` / `themes_metadata v1.6` / `thesis_note v1.6`（升级 from v1.5）+ 4 supporting schema 全 in [`data/runtime/schemas/`](../../data/runtime/schemas/)
- 新 skill：[`research-evidence-reviewer`](../../.claude/skills/research-evidence-reviewer/) / [`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/) / [`engineering-project-review`](../../.claude/skills/engineering-project-review/) / [`research-theme-report-debater`](../../.claude/skills/research-theme-report-debater/)
- 重命名：`research-theme-content-maintainer` → [`research-theme-knowledge-and-package-curator`](../../.claude/skills/research-theme-knowledge-and-package-curator/)（2026-04-27 重命名，旧名暗示 janitorial 实际是 active drafting + assembly）
- 三层架构 framing 加入：World Model / Evidence Ledger / Market Pricing（per [`world_model_evidence_pricing_three_layer_upgrade.md`](../ideas/world_model_evidence_pricing_three_layer_upgrade.md)）
- §2.1 ThesisNote 字段表升级到 v1.6 字段集
- §6 cursor rules 路径校准（35_pm_writing_contract.mdc 不是 _reader_state_first；36_ 已删）
- V5.5 self-positioning 校准为 "AI-native thematic research loop infrastructure"（不是 LLM wiki）

## 0. 这份文档要回答的问题

Forks 是 V5.5 "AI-native thematic research loop infrastructure" 的 90 天 MVP 入口（[`Forks-MVP-Product-Spec.pdf`](04_areas/work/due_diligent/forks/Forks-MVP-Product-Spec.pdf) V1.0 起 V5.4，现 V5.5 framework 已 supersede），聚焦 `Scenarios → Monitor → Evolve` 三段。trading_platform 是 Bokan 在做的单 PM operating system，已经在相邻问题上跑了较长时间。

本文回答一件事：**Forks 在不改变其产品定位的前提下，能从 trading_platform 直接拿走、复用、或借鉴哪些资产，以及哪些不该照搬。**

## 1. 总览地图：4 类资产 × Forks 5 个阶段

把 Forks 的 90 天里程碑（Week 1-2 基建 / Week 3-4 Forward-Cast / Week 5-8 Editor + Card / Week 9-11 Monitor + Vindication / Week 12-13 Convergence + Launch）摆在横轴，trading_platform 已有资产摆在纵轴，能立刻看出免费 leverage 落点。

| 资产类别 | Forks 受益最多的阶段 | Forks 能省的事 |
| --- | --- | --- |
| Schema 直觉（Theme / Thesis / Scenario / Evidence / Trigger） | Week 3-6 | 字段命名、必填项、可选项已被 56 份真实 ThesisNote + 1 sample scenario_note + 数条 evidence_record 验证过，少 1-2 周拍脑袋 |
| 数据 seed（56 thesis / 10 theme reports / 9 active themes / 90 asset technical reports + 70 signal_packets） | Week 12-13 launch seed | Forks 原计划 Week 13 由 Bowen + Citrini 团队手写 50 个高质量 seed；已现成 |
| 10 canonical jsonschema（含新增 4 个 first-class object schema） | Week 3 Schema RFC | scenario_note / evidence_record / path_observation / freshness_event 直接借 |
| Prompt / skill 设计哲学（27 skill cluster + 独立 reviewer 网） | Week 3-4 Forward-Cast / Week 11 Evolve | 每个 agent 的"什么必须 deterministic / 什么交给 AI"已有可抄的 rule；3 段式 + 4 段式 hand-off pattern + 独立 reviewer 网（research-evidence-reviewer / staleness-sweeper / engineering-project-review）作为 multi-agent governance reference |
| 代码模块（时间语义 / 数据连接器 / 索引构建） | Week 1-2, Week 9-10 | DST / 多市场 session / source connector 边界等坑已经踩过 |
| 操作守则（`.cursor/rules`） | 全程 | 团队协作的 written norms，直接 fork 一份当 contributing guide 用 |
| **三层架构 framing**（World Model / Evidence Ledger / Market Pricing） | 全程 architecture 决策 | per [`world_model_evidence_pricing_three_layer_upgrade.md`](../ideas/world_model_evidence_pricing_three_layer_upgrade.md)，可作为 V5.5 5-stage loop infra 的 hedge fund-vs-single-PM 切片对照 |

## 2. Schema 资产：6 类一等对象 schema，直接对应 V5.5 7 对象的子集

V5.5 PDF §1.5 + DDL §9.1 列了 7 个一等对象：Theme / Thesis / Scenario / Basket / ExpressionLink / TriggerEvent / PerformanceRecord。trading_platform 侧 6 类一等对象 schema 直接对应前 5 个（Basket / PerformanceRecord 我们 single-PM 不做），且**多了 Evidence + PathObservation + FreshnessEvent 三层 V5.5 没有的 learning ledger 对象**。

### 2.1 ThesisNote v1.6 字段（已生产 56 份）

[`thesis_note_v1_6.schema.json`](../../data/runtime/schemas/thesis_note_v1_6.schema.json) 全 schema 校对：

| trading_platform 字段（v1.6） | V5.5 对应字段 | 对 Forks 的价值 |
| --- | --- | --- |
| `thesis_id` / `schema_version` / `drafted_at_utc` | `id` / 无 versioning metadata | schema_version 字段强制让 thesis schema 升级时不破老 thesis |
| `claims[]`（≥3 prose sentences）| `claim: string`（单 string） | claims 拆 ≥3 条独立子断言，比 V5.5 单 string claim 更可证伪、更可单条 evolve |
| `key_dependencies[]` | causal_chain 内嵌 prose | 显式拆出 dependencies 让 trigger_signals 的语义父类清晰，Forward-Cast prompt 更聚焦 |
| `falsifiers[]`（≥1 required） | `falsification_conditions[]` | 概念高 align；我们用 enum + prose mix；V5.5 用 JSONB |
| `scenario_triggers[]` + `breaks_chain_node` enum | `trigger_signals[]` + `signal_type` enum (earnings/macro/industry/sentiment) | **不同切片维度互补**：V5.5 按"信号来源"切，我们按"因果链节点"（demand/supply/pricing/policy/adoption/margin）切。可合并 2D 标签 |
| `counter_evidence_observed[]` | 无显式字段（散在 evolve narrative） | 显式记观察到的反证 evidence_id list，让"thesis evolve 时哪些反证累积"可 audit |
| `cross_theme_links[]` | 无（V5.5 thesis 是单 theme child） | 跨 theme 的 thesis 关联可表达 |
| `lifecycle_stage` enum（draft / active / invalidated / superseded / obsolete） | `state` enum (active / evolving / invalidated / superseded) | **集合接近全 align** |
| `pm_acknowledged_by: string` + `adversarial_review_log[]` | 无显式 ack 字段 | "AI candidate vs PM decision" 边界写在 schema |
| `freshness_state` + `review_policy` + `next_review_trigger` | 无显式 freshness 字段 | event-driven freshness（per F7 in [`vs_v5_5 doc`](trading_platform_vs_v5_5_comparison_and_mutual_learning_20260427.md)） |
| `probability_view: enum {primary / plausible / tail}`（在 v1.6 字段） | `pm_confidence: float (0-1)` | **不同 representation 同 intent**（双方都拒绝伪 forecast；V5.5 PDF §4.1 显式说"sum 不必等于 1"） |
| `expected_winners` / `expected_losers` | `key_tickers` long/short | — |

### 2.2 直接可拿的真实样本（节选）

- `agentic_finance_drives_onchain_execution.json` — 完整 ThesisNote，标的 HYPE/COIN/ETH/SOL
- `ai_power_demand_can_pull_us_natural_gas_into_a_structurally_tighter_regime.json` — 跨资产 macro thesis
- `advanced_packaging_can_become_the_true_ai_scaling_bottleneck.json` — semi/AI 主题，fintwit 高匹配
- `ai_reshoring_and_labor_disruption_can_weaken_the_marginal_bid_for_us_equities.json` — bear scenario 范例
- `agent_stablecoin_default_settlement.json` — agentic finance 子线
- `auto_insurance_profit_cycles_can_recycle_excess_returns_into_marketing_spend.json` — 单行业 alpha 类
- 共 56 份（v1.0 时 43 份，T0 周末扩到 56），完整列表在 [`data/research/thesis_notes/`](../../data/research/thesis_notes/)

建议处理：Bowen 在 launch seed 阶段，可用脚本把这 56 份 ThesisNote 转成"Forks Thesis + 4 条候选 Scenario"的种子，替代 Week 13"Bowen + Citrini 团队手写 50 个"的人工成本。脚本工作量约 1-2 天，远低于人工撰写。

### 2.3 Scenario / Evidence / FreshnessEvent / PathObservation 4 个新 first-class object schema（T0 周末新落）

V5.5 PDF 显示 V5.5 已有 Scenario + TriggerEvent，但 trading_platform 这边把 TriggerEvent 升级为 Evidence Ledger（含 trust_tier + belief_delta + ai_review_log 三件套），并加了 PathObservation（pre-thesis 观察）+ FreshnessEvent（状态机转换日志）两个 V5.5 没有的 learning ledger 对象。

| schema | 路径 | 对 Forks 的价值 |
| --- | --- | --- |
| `scenario_note v0.1` | [`data/runtime/schemas/scenario_note_v0_1.schema.json`](../../data/runtime/schemas/scenario_note_v0_1.schema.json) | trigger_signals + pm_conviction + scenario_role + **market_state 4 档 enum + pricing_snapshots[] append-only time-series**（Market Pricing dimension V5.5 无）+ evolved_from_evidence + lifecycle_stage 4 状态。**直接给 V5.5 Scenario schema 加 market_state + pricing_snapshots 字段即可补 mispricing layer** |
| `evidence_record v0.2` | [`data/runtime/schemas/evidence_record_v0_2.schema.json`](../../data/runtime/schemas/evidence_record_v0_2.schema.json) | source_quality (trust_tier) + linked_objects + **belief_delta** + caused_transitions + **ai_review_log[]** + ai_verified + pm_acknowledged。**V5.5 TriggerEvent 升级到 Evidence Ledger 的完整 schema reference**（per F1 in [`vs_v5_5 doc`](trading_platform_vs_v5_5_comparison_and_mutual_learning_20260427.md)） |
| `path_observation v0.1` | [`data/runtime/schemas/path_observation_v0_1.schema.json`](../../data/runtime/schemas/path_observation_v0_1.schema.json) | supporting_evidence_ids + tentative_themes + graduation_target_scenario_id + lifecycle_stage。**pre-thesis 观察对象**（Forks scanner / Theme Radar 找到信号但还没成 thesis 时承接的 schema） |
| `freshness_event v0.1` | [`data/runtime/schemas/freshness_event_v0_1.schema.json`](../../data/runtime/schemas/freshness_event_v0_1.schema.json) | object_type + object_id + from_state + to_state + trigger_kind + trigger_evidence_id + supersedes_event_id。**event-driven freshness 状态机 emit log**（V5.5 thesis state machine 已系统化但没 freshness event log 这层） |
| `themes_metadata v1.6` | [`data/runtime/schemas/themes_metadata_v1_6.schema.json`](../../data/runtime/schemas/themes_metadata_v1_6.schema.json) | lifecycle_stage + priority_bucket + **scenario_map** + linked_thesis_ids + linked_asset_tickers + scope_boundary + freshness_state + review_policy。比 V5.5 Theme（id / name / description / state / trigger_context）多 priority + scope_boundary + freshness 三层 |
| `thesis_note v1.6` | [`data/runtime/schemas/thesis_note_v1_6.schema.json`](../../data/runtime/schemas/thesis_note_v1_6.schema.json) | 见 §2.1 |

## 3. 真实数据资产：可作为 Forks seed 的内容池

| 资产 | 数量 | Forks 的用法 |
| --- | --- | --- |
| [`data/research/thesis_notes/*.json`](../../data/research/thesis_notes/) | 56（v1.0 时 43，T0 周末扩） | Forward-Cast 的 few-shot 训练集 + launch seed 的 thesis 池 |
| [`data/research/themes/reports/*.md`](../../data/research/themes/reports/) | 10 | 现成的"macro theme 长文"，可拍平为 Forks 上的"theme-level scenario tree" |
| [`data/research/themes/metadata/*.json`](../../data/research/themes/metadata/) | 9 active themes | themes_metadata v1.6 schema 的真实 instance |
| [`data/research/themes/current_priority_tree.json`](../../data/research/themes/current_priority_tree.json) | 1 | 已有 short-term / medium-term 主题排序，可作为 Forks 默认 trending 排序的冷启动权重 |
| [`data/research/themes/index.json`](../../data/research/themes/index.json) | 1 | theme 字典 + tag 分类，可直接喂 Convergence detector 做主题匹配 |
| [`data/research/scenario_notes/*.json`](../../data/research/scenario_notes/) | 1 sample（T0 周末新落） | scenario_note v0.1 schema 的真实 instance（[`warsh_succession_leading_path_framework_substitution.json`](../../data/research/scenario_notes/warsh_succession_leading_path_framework_substitution.json)） |
| [`data/research/evidence_ledger/<YYYY-WNN>/*.json`](../../data/research/evidence_ledger/) | 数条（按 ISO 周分目录，2026-W17 已开始填） | evidence_record v0.2 schema 的真实 instance + Evidence Ledger 工作流 reference |
| [`data/research/path_observations/<YYYY-WNN>/*.json`](../../data/research/path_observations/) | 1 sample | path_observation v0.1 schema 的真实 instance |
| [`data/knowledge/asset_technicals/reports/*.md`](../../data/knowledge/asset_technicals/reports/) | 90 .md（每 asset 一份最新 snapshot，不 per-date 累积） | Forks scenario card 的 `key_tickers` 段可借这层做技术状态背书；也可作为 Monitor agent 判定"price-side trigger"的 ground truth 文本 |
| [`data/knowledge/asset_technicals/signal_packets/*.json`](../../data/knowledge/asset_technicals/signal_packets/) | 70 | deterministic 价格信号包，Forks 的"price 类 trigger 自动监测"可直接消费 |
| [`data/research/source_collections.json`](../../data/research/source_collections.json) | 1 | source 家族注册表，Forks 的 Monitor agent ingestion routing 直接借 |
| `data/research/messages/` + `snapshots/` | 数百 | Forward-Cast prompt 的 few-shot 真实研究语料，比 Citrini 历史 theses 更新更杂 |

**授权与隐私边界**：这些数据是 Bokan 的内部研究产出，给 Forks 使用前需要明确两件事：

1. 公开发布权限（有些 thesis 含未公开 view）
2. 哪些段落可作为 AI prompt 上下文 vs 可直接发布

建议建立一份 "releasable subset" 的过滤清单，而不是整库给。

## 4. Skill / Prompt 设计资产：27 个 skill cluster 映射到 Forks 4 个 agent + 独立 reviewer 网

Forks 的 4 个 agent（`Forward-Cast / Monitor / Evolve / Convergence`）在 trading_platform 侧都有相邻 skill，可直接读 [`.claude/skills/<name>/SKILL.md`](../../.claude/skills/) 做参考（`.cursor/skills/` 是镜像）。

### 4.1 Forks 4 agent 映射

| Forks 的 agent | trading_platform 可参考的 skill | 可直接抄的部分 |
| --- | --- | --- |
| Forward-Cast（生成 5-7 候选） | [`single-stock-analysis`](../../.claude/skills/single-stock-analysis/), [`research-theme-knowledge-and-package-curator`](../../.claude/skills/research-theme-knowledge-and-package-curator/) | ticker-first authority, "completion standard" 写法, 输出 frontmatter 字段 |
| Monitor（trigger 监测） | [`research-current-market-reporter`](../../.claude/skills/research-current-market-reporter/), [`ingestion-source-connector-designer`](../../.claude/skills/ingestion-source-connector-designer/), [`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/)（**T0 新增 freshness sweeper**） | session_freshness 的市场日定义, source connector 边界（`40_systemic_mismatch` 经验）+ freshness_event 状态机 emit log pattern |
| Evolve（AI Draft 子分支） | [`research-theme-report-owner`](../../.claude/skills/research-theme-report-owner/), [`research-theme-knowledge-and-package-curator`](../../.claude/skills/research-theme-knowledge-and-package-curator/) | owner 决定 pass / writer 执行 pass 的拆分模型（Forks 的 "AI 起草, 用户 adopt" 同源） |
| Convergence detector | [`research-theme-priority-updater`](../../.claude/skills/research-theme-priority-updater/), [`research-theme-report-reviewer`](../../.claude/skills/research-theme-report-reviewer/) | embedding 之外，theme-tag 优先消费（`13_index_first_ai_for_gaps`），减 Claude API 烧量 |
| （横向）Writer gateway | [`writer-handoff`](../../.claude/skills/writer-handoff/) | package 不够时返回 `need_more_detail` 的形态，Forks scenario editor 可借同样模式 |
| （横向）Inbox triage | [`ingestion-agentmail-inbox-triage`](../../.claude/skills/ingestion-agentmail-inbox-triage/) | 邮件 / 新闻 ingest 的分类规则；Forks 的 news scraper 入站 buffer 可借 |

### 4.2 Thesis 三段式 cluster（T0 新增显式列出）

Forks Forward-Cast / Evolve agent 内部如果要做 single-thesis 完整生命周期，trading_platform 已有完整三段式 cluster pattern：

- [`research-thesis-drafter`](../../.claude/skills/research-thesis-drafter/) → [`research-thesis-verifier`](../../.claude/skills/research-thesis-verifier/) → [`research-thesis-adversary`](../../.claude/skills/research-thesis-adversary/)
- 每段 hand-off 有显式 lifecycle_stage gate（draft → verifier appended → adversary promoted to active 但需 PM ack）
- 配合 [`research-theme-discovery-scanner`](../../.claude/skills/research-theme-discovery-scanner/) → [`research-theme-bootstrapper`](../../.claude/skills/research-theme-bootstrapper/) Stage A & B 做 bottom-up theme discovery 时的 thesis 起步

### 4.3 独立 reviewer 网（T0 新增，process-based AI governance pattern）

V5.5 走 contract-based AI governance（5 原则 + 6 红线 per stage）；trading_platform 走 process-based 独立 reviewer 网。两者互补，Forks 可同时采纳两层：

- [`research-evidence-reviewer`](../../.claude/skills/research-evidence-reviewer/) — 独立 AI 评审 evidence_record 的 trust_tier + belief_delta + ai_review_log
- [`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/) — 独立 freshness sweeper，周扫 emit freshness_event；不 mutate body
- [`engineering-project-review`](../../.claude/skills/engineering-project-review/) — 独立 review engineering commits

3 个 reviewer 都 cross-cutting（不属于任何主 cluster）+ 都 append-only（不改 body 字段），是 audit-grade AI output 的 architectural answer。Forks 多 agent 协作如果想避免 single-agent 自审 hallucination，这层必加。

### 4.4 Theme 四段式 cluster（T0 新增显式列出）

Forks Convergence detector + Evolve 上游需要的 macro theme 报告生命周期：

- [`research-theme-report-owner`](../../.claude/skills/research-theme-report-owner/) → [`research-theme-knowledge-and-package-curator`](../../.claude/skills/research-theme-knowledge-and-package-curator/)（**T0 重命名 from `research-theme-content-maintainer`**，旧名暗示 janitorial 实际是 active drafting + assembly）→ [`research-theme-report-debater`](../../.claude/skills/research-theme-report-debater/)（T0 新加，content-logic adversary）→ [`research-theme-report-reviewer`](../../.claude/skills/research-theme-report-reviewer/)

## 5. 代码模块：直接可移植的 Python 资产

下面这些模块在 trading_platform 已经投产，接口稳定，跟产品定位无强耦合，Forks 后端（Postgres + Claude + cron）直接搬过去即用。

- `src/tools/time_semantics.py` — T11 时间契约（`MarketDay` vs `CalendarDayUTC`, `assert_same_semantics`, IANA tz 校验）；Forks scenario card 跨时区渲染必踩的坑
- `src/data_update/session_freshness.py` — XNYS / CMES / `24_7` session anchor；Forks Monitor 判 trigger 命中时的"今天是不是交易日"判定
- `src/tools/build_theme_indexes.py` — 从 metadata 派生 priority tree；Forks 的 "trending scenarios / hot themes" 排行榜可借同样思路
- `src/research/agentmail.py` — AgentMail intake 边界 + 去重 + 标签结构；Forks 接 RSS / Twitter scrape 时的边界 boilerplate
- `src/research/archive.py` — "archive-first" 的研究归档模式；Forks Monitor ingest 的事件流如果要做可审计 history，应优先复用这层而不是自己造
- `src/tools/artifact_graph.py` 的 freshness probe 思路（不是整套 graph）— Forks 的 trigger "是否还新鲜可信" 判定可借这种 deterministic + `UNKNOWN` 标签的写法
- `src/tools/export_markdown_document.py` — `markdown → DOCX → PDF` 的 canonical 工具（macOS 走 Pages.app, Windows 走 Word, Linux 走 docx2pdf），Forks 后续如果要给付费用户出"我的 Scenario Set 月度报告 PDF"，直接用

## 6. 操作守则与已踩过的坑

trading_platform 在 [`.cursor/rules/`](../../.cursor/rules/) 下沉淀了一组 always-on 规则，多数是"AI 协作下不返工"的硬经验。Forks 团队 contributing guide 可直接 fork 下面这几条。**v1.1 verified actual paths（v1.0 时部分 rule 已重命名 / 删除）**：

- [`13_index_first_ai_for_gaps.mdc`](../../.cursor/rules/13_index_first_ai_for_gaps.mdc) — "已存在的 tag/index 不要用 AI 重猜"，Forks Monitor agent 必踩，否则 Claude API 月成本会爆
- [`31_prompt_boundary_task_vs_control_plane.mdc`](../../.cursor/rules/31_prompt_boundary_task_vs_control_plane.mdc) — 给 LLM 的 prompt 只放任务，不放调度信息；Forks Forward-Cast / Evolve prompt 直接受益
- [`33_clickable_links_for_user_paths.mdc`](../../.cursor/rules/33_clickable_links_for_user_paths.mdc) — 任何工具 / agent 输出里，文件 / URL 用可点链接；Forks 的 admin 控制台、内部 dashboard 也适用
- [`34_hidden_assumption_and_better_question.mdc`](../../.cursor/rules/34_hidden_assumption_and_better_question.mdc) — 用户给的问题先判断隐藏假设是否成立；Forks PM 输入 thesis 时 AI Coach 阶段可借
- [`35_pm_writing_contract.mdc`](../../.cursor/rules/35_pm_writing_contract.mdc)（**v1.0 错引为 `35_pm_reader_state_first`，已修**）— PM-facing 写作契约；对应 Forks "scenario card / vindication card 让用户读完应该能判断什么"
- [`40_systemic_mismatch_second_order_check.mdc`](../../.cursor/rules/40_systemic_mismatch_second_order_check.mdc) — 修一个 bug 时，顺手判断同一类 bug 会不会在邻近场景再发；对 Forks 的多 agent 协作很关键
- [`42_artifact_graph_admission.mdc`](../../.cursor/rules/42_artifact_graph_admission.mdc) — Forks v0 可不用整套 graph，但"L4 必须经 canonical builder，不能旁路写"的精神适用于 vindication card / scenario card 的生成路径
- [`53_docx_pdf_via_export_markdown_document.mdc`](../../.cursor/rules/53_docx_pdf_via_export_markdown_document.mdc)（v1.1 新加） — DOCX / PDF 导出走 canonical 工具不直接 markdown→PDF；Forks 月度报告 export 直接复用 [`src/tools/export_markdown_document.py`](../../src/tools/export_markdown_document.py)

**v1.0 引用但已删除的 rule**：原 `36_reader_gain_before_instruction_detail` 已合并入 35 / 删除。

### 6.1 已经付过学费的坑（直接告诉 Forks 团队避开）

- DST / fixed-offset 时间字符串不要用（`-04:00` / `FixedOffset(-300)`）；scenario card / vindication card 跨 ET 夏令时切换会错一天
- "N business days ago" 不能用 `timedelta(days=N)`；必须走 exchange calendar
- AI 写报告时如果直接覆盖正本，必然丢 provenance；用 sidecar（`writer.json`）记上游 hash，比事后做 git 考古便宜 10 倍
- Source connector 不要做成"同时知道 ranking + interpretation"的层（`12_connector_boundary`），Forks Monitor agent 也别这么做
- AgentMail / 任何 inbox 类入口，不要把 wrapper 邮件当成研究内容本身；先 triage 再 archive

## 7. 90 天里程碑对照：Forks 每周可立刻拿走的东西

| Forks 周次 | 原 spec 的交付 | trading_platform 这边的免费 leverage |
| --- | --- | --- |
| Week 1-2 | Next.js + Postgres + Claude + auth + Stripe + design system | [`time_semantics.py`](../../src/tools/time_semantics.py) + [`session_freshness.py`](../../src/data_update/session_freshness.py) 直接放进 backend；`.cursor/rules` 7 条 fork 进 `contributing.md`（v1.1 verified） |
| Week 3-4 | Forward-cast agent v0; Thesis + Scenario schema 可写 | ThesisNote v1.6 schema 字段对照表（本文 §2.1）直接当 schema RFC；**56 份 thesis_notes** 作为 prompt few-shot；scenario_note v0.1 schema（本文 §2.3）直接抄；trading_platform 的 [`research-thesis-drafter`](../../.claude/skills/research-thesis-drafter/) → [`research-thesis-verifier`](../../.claude/skills/research-thesis-verifier/) → [`research-thesis-adversary`](../../.claude/skills/research-thesis-adversary/) 三段式 cluster 直接作为 Forward-Cast agent 多段式实现 reference |
| Week 5-6 | Scenario editor (flowchart) + 节点状态编码 | 10 份 [`themes/reports/*.md`](../../data/research/themes/reports/) 的"路径 / 情景"段，是 flowchart 节点的真实样本；**1 sample scenario_note**（[`warsh_succession_leading_path_framework_substitution.json`](../../data/research/scenario_notes/warsh_succession_leading_path_framework_substitution.json)）作为 lifecycle_stage 状态机的真实 instance |
| Week 7-8 | Scenario card renderer (PNG) + Twitter 分享 | [`asset_technicals/reports/*.md`](../../data/knowledge/asset_technicals/reports/) 的"frontmatter + 段落结构"可启发 card 分区设计（Asset State / Why It Matters Now / Trade Framing） |
| Week 9-10 | Monitor agent v0 + earnings/SEC ingestion + 半自动 trigger | [`agentmail.py`](../../src/research/agentmail.py) + [`source_collections.json`](../../data/research/source_collections.json) 是 ingest router 的 v0；[`signal_packets/*.json`](../../data/knowledge/asset_technicals/signal_packets/)（70 个）是 price-side trigger 的真值源；**evidence_record v0.2 schema**（本文 §2.3）作为 Monitor agent 输出 trigger event 的 schema RFC（trust_tier + belief_delta + ai_review_log 三件套） |
| Week 11 | Vindication card 自动生成；AI Draft agent；Living feed | [`writer-handoff`](../../.claude/skills/writer-handoff/) + [`research-theme-report-owner`](../../.claude/skills/research-theme-report-owner/) 拆分模型 = AI Draft 起草 + adopt 的同构；**[`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/) skill** 作为 Living feed 的 freshness event emit pattern；**freshness_event v0.1 schema**（本文 §2.3）作为 Living feed event log schema |
| Week 12 | Convergence detector; Team tier; QA; KOL seed outreach | [`themes/index.json`](../../data/research/themes/index.json) 的 theme tag 分类直接作为 convergence 第一层粗筛；**[`research-evidence-reviewer`](../../.claude/skills/research-evidence-reviewer/) + [`engineering-project-review`](../../.claude/skills/engineering-project-review/)** 独立 reviewer 网作为 QA pattern reference |
| Week 13 | Private launch + 50 高质量 seed scenarios（人工） | **56 ThesisNote → ~200 候选 Scenario** 的脚本式转换（V5.5 PDF §9.3 已 spec AI scenario generation response format，schema-to-API mapping 一周可 prototype），替代人工撰写 |

## 8. 不建议 Forks 照搬的部分（避免互相污染）

- 整套 artifact graph 的 `must_be_fresh` / `must_exist_unchanged_since` 契约 — 对 v0 MVP 太重，Forks 应保持 schema-light
- PM-facing 报告的 `reader-state-first` prose（`35`）— 服务对象是单 PM，跟 social card 不同；借"先定义 reader gain"的方法论，不借 prose 风格
- writer sidecar 的 5 字段全套（T11 完整版）— Forks 只需 `event_id` + `source_url` + `rendered_at_utc` 这种最小子集
- `routing-task-mode-router` / `routing-current-macro-priority-router` 的多层路由 — Forks 用户场景单一，不需要先做 task 分类再做 theme 分类的双层

## 9. 合作模型建议

假设双方愿意正式协作，建议三件具体事（v1.1 增至 5 件，cost 排序）：

### 9.1 短期（本周可启动，cost <2 day）

1. **"releasable subset" 过滤清单** — Bokan 这边明确 56 ThesisNote / 10 theme reports / 9 active themes / 1 sample scenario_note 里哪些可以作为 Forks 公开种子，哪些只能作为 Forks AI prompt 上下文（不公开）。建议 1-2 天内出第一版
2. **Schema cheatsheet 对齐** — trading_platform [`thesis_note v1.6`](../../data/runtime/schemas/thesis_note_v1_6.schema.json) / [`scenario_note v0.1`](../../data/runtime/schemas/scenario_note_v0_1.schema.json) / [`evidence_record v0.2`](../../data/runtime/schemas/evidence_record_v0_2.schema.json) 字段命名对齐 V5.5 Thesis / Scenario / TriggerEvent 命名。让未来 conversion cost 趋零
3. **`.cursor/rules` 7 条 fork 进 Forks `contributing.md`**（per §6 verified paths）+ §6.1 "已踩过的坑" list 直接 fork。一次性投入，节省 Forks 团队 2-4 周踩坑时间

### 9.2 中期（本月内，cost 1-2 week）

4. **3 个 high-leverage schema 移植到 V5.5**（per [`vs_v5_5 doc`](trading_platform_vs_v5_5_comparison_and_mutual_learning_20260427.md) §9.2）：
   - `evidence_record v0.2` → V5.5 TriggerEvent 升级（加 trust_tier + belief_delta + ai_review_log 三件套）
   - `scenario_note v0.1` 的 market_state + pricing_snapshots 字段 → V5.5 Scenario 字段加 H6（Market Pricing dimension）
   - `freshness_event v0.1` + review_policy → V5.5 4 对象 lifecycle 补 review_trigger 事件订阅
5. **AI cluster + 独立 reviewer 网 pattern 给 V5.5 team**：thesis 三段式 / theme 四段式 / 独立 reviewer 网 spec。补 V5.5 contract-based AI governance 的 process-based reviewer cross-cut

### 9.3 长期（季度，需双方 architect commit）

6. **AI 自动 conversion build**：V5.5 `POST /ai/scenarios/generate` → trading_platform `scenario_note v0.1 draft` ingest pipeline；trading_platform schema 反向 → V5.5 endpoint mapping（V5.5 PDF §9.3 已 spec response format，friction 比想象低）
7. **7 native extension hook**（per [`vs_v5_5 doc`](trading_platform_vs_v5_5_comparison_and_mutual_learning_20260427.md) §7）作为 V5.5 schema 升级 RFC

## 10. 一句话结论

Forks 不需要也不应该融合 trading_platform 的运行时，但可以在 **schema（10 canonical jsonschema 含 4 个 first-class object schema）/ AI cluster pattern（27 skill cluster + 独立 reviewer 网 process-based governance）/ 数据 seed（56 thesis + 10 theme reports + 90 asset technicals + 70 signal packets）/ 三层 framing（World Model / Evidence Ledger / Market Pricing）/ 时间和 ingest 模块** 五个层面拿走至少 4-6 周的工程量，并避开 trading_platform 已经付过学费的坑。

**最高 ROI 三件事**（v1.1 增至 3，原 2）：

1. 用 [`thesis_note v1.6 schema`](../../data/runtime/schemas/thesis_note_v1_6.schema.json) 字段 + 56 份样本作为 Forward-Cast 的 schema RFC 与 few-shot
2. 用 [`evidence_record v0.2 schema`](../../data/runtime/schemas/evidence_record_v0_2.schema.json) 三件套（trust_tier + belief_delta + ai_review_log）升级 V5.5 TriggerEvent → Evidence Ledger（V5.5 当前最大 structural blindspot，[`world_model_evidence_pricing_three_layer_upgrade.md`](../ideas/world_model_evidence_pricing_three_layer_upgrade.md) §1.2 已 identified）
3. 把 [`.cursor/rules`](../../.cursor/rules/) 里 7 条规则 fork 进 Forks `contributing.md`，让 Forks 多 agent 协作从第一天起就对齐

详细 mutual learning matrix（trading_platform 能学 V5.5 的 9 项 + V5.5 能学 trading_platform 的 7 项）见 [`vs_v5_5 doc`](trading_platform_vs_v5_5_comparison_and_mutual_learning_20260427.md) §5。
