---
built_at_utc: "2026-04-27T00:00:00Z"
market_day_at_utc: null
title: trading_platform vs Forks V5.5 — Comparison + Mutual Learning
audience: Forks team（CEO + engineers）+ Bokan PM
sources:
  - designDoc/bp/V5.5-Product-Definition.pdf
  - designDoc/bp/Product-Definition-v5.4_digest.md
  - designDoc/bp/forks_can_use_from_trading_platform.md
  - designDoc/bp/forks_mvp_relation_to_trading_platform.md
  - designDoc/bp/trading_platform_t0_tech_brief_20260427.md
  - designDoc/ideas/world_model_evidence_pricing_three_layer_upgrade.md
  - 09_soul/axioms/a17_reader_persona_primacy.md
  - 09_soul/axioms/t10_index_first_ai_for_gaps.md
companion: trading_platform_t0_tech_brief_20260427.md（standalone tech brief）
---

# trading_platform vs Forks V5.5 · 对照 + Mutual Learning

## §0 这份 doc 的性质 + 读者

**这是 pitch + 互学 framing**，不是 standalone 介绍。standalone 介绍见 [`trading_platform_t0_tech_brief_20260427.md`](trading_platform_t0_tech_brief_20260427.md)。

读者：Forks CEO Bowen + Forks engineers + 任何想理解 trading_platform 跟 V5.5 关系的内部 reviewer。

framing 立场：**两边都在 build "AI-native thematic research loop infrastructure"** 这个 genre。两边的差异是 audience（multi-PM hedge fund product vs single-PM internal cognitive infra）+ specific design choice，不是 genre。

---

## §1 V5.5 的 self-positioning + thematic research loop infra 是什么

V5.5 PDF §1.1 自我定义（直引）：

> 面向 thematic investment research 的 AI-native loop infrastructure。它**不是市场预测引擎，不是 quant signal generator，不是 portfolio optimizer**。它的 job 是 structure / track / replay PM 的思考。

**5-stage loop**（V5.5 §1.4）：

```
Theme → Thesis → Scenarios ↔(N:M)↔ Baskets → Monitor & Evolve ──▶ Thesis vN+1
```

5 段含义：
1. **Theme**：长期值得追踪的结构性议题（macro / sector / policy / consumer）。Container 不是 thesis
2. **Thesis**：theme 下可证伪论断（claim + 因果链 + 证伪条件）。Commodity（任何 sharp PM 都能得出，alpha 不在这）
3. **Scenarios**：thesis 的多条 realization path。**Center of gravity** —— alpha 来自 scenarios 分叉，AI 在这里最 active
4. **Baskets**：scenarios 的可执行 quant 表达（instruments + weights + rules）。唯一可量化对象（PnL / Sharpe / attribution / factor exposure）
5. **Monitor & Evolve**：双层后台（scenario 层 qualitative 追 trigger / basket 层 quantitative 追 PnL），触发 thesis vN+1 evolve

**trading_platform 也是 thematic research loop infra**。我们的 [3-layer 框架](../ideas/world_model_evidence_pricing_three_layer_upgrade.md)（World Model / Evidence Ledger / Market Pricing）是同一 genre 在 single-PM context 下的另一种切片：World Model ≈ Theme/Thesis/Scenarios/Path_observation，Evidence Ledger 显式提为 first-class learning layer，Market Pricing 是 scenario 上的 mispricing dimension。**genre 同 / 切片不同**。

下面对照具体维度。

---

## §2 5-stage loop map：V5.5 vs trading_platform

逐 stage 对照实现，看每段哪些 align / 哪些 diverge：

### §2.1 Theme stage
| 维度 | V5.5 | trading_platform |
|---|---|---|
| 对象 schema | `themes` table（PostgreSQL DDL §9.1）：name / description / state / trigger_context / related_themes / author_id / timestamps | [`themes_metadata_v1_6.schema.json`](../../data/runtime/schemas/themes_metadata_v1_6.schema.json)：lifecycle_stage / priority_bucket / scope_boundary / scenario_map / linked_thesis_ids / linked_asset_tickers / freshness_state / review_policy / evidence_status |
| State machine | 5 状态（emerging / active / peaking / decaying / dormant，PDF §2.3） | lifecycle_stage 字段存在但 state 集合不同（PM 维护，4-5 档跟 V5.5 align） |
| AI function | Theme Radar（7×24 扫描提议 emerging）+ Sanity Check | [`research-theme-discovery-scanner`](../../.claude/skills/research-theme-discovery-scanner/) skill + [`research-theme-bootstrapper`](../../.claude/skills/research-theme-bootstrapper/) Stage A & B negotiation pattern |
| 同 / 异 | concept align；V5.5 5-state 状态机比 trading_platform priority_bucket 更系统化 | trading_platform bootstrapper 5 outcome enum（admit_new / merge_into_existing / narrow_existing_then_admit / carve_out_from_existing / subordinate_to_existing）V5.5 没有 |

### §2.2 Thesis stage
| 维度 | V5.5 | trading_platform |
|---|---|---|
| 对象 schema | `theses` table：claim / causal_chain (TEXT) / falsification_conditions (JSONB) / version / predecessor_id / state / pm_confidence | [`thesis_note_v1_6.schema.json`](../../data/runtime/schemas/thesis_note_v1_6.schema.json)：claims (≥3 prose) / key_dependencies / falsifiers / scenario_triggers / counter_evidence_observed / cross_theme_links / lifecycle_stage / adversarial_review_log / pm_acknowledged_by / freshness_state / review_policy |
| State machine | 4 状态（active / evolving / invalidated / superseded） | lifecycle_stage 集 align（draft / active / invalidated / superseded） |
| Lineage | version + predecessor_id + lineage[] 完整保留 | predecessor_id + cross_theme_links + evolved_from_evidence + freshness_event 状态机 emit log |
| AI function | Falsifiability Coach + Cross-Thesis Conflict Detector + Thesis Evolution Drafter（PDF §3.4）+ "AI 不做什么" block | [`research-thesis-drafter`](../../.claude/skills/research-thesis-drafter/) → [`research-thesis-verifier`](../../.claude/skills/research-thesis-verifier/) → [`research-thesis-adversary`](../../.claude/skills/research-thesis-adversary/) 三段式 cluster + lifecycle gate 显式 |
| 同 / 异 | concept align；他们三个 AI function 是单 agent 边界；我们三段式 cluster + 显式 hand-off + PM gate |

### §2.3 Scenarios stage（V5.5 center of gravity）
| 维度 | V5.5 | trading_platform |
|---|---|---|
| 对象 schema | `scenarios` table：narrative / trigger_signals (JSONB) / pm_probability float / state / ai_generated / adopted_from_draft | [`scenario_note_v0_1.schema.json`](../../data/runtime/schemas/scenario_note_v0_1.schema.json)：parent_thesis_id / trigger_signals / pm_conviction enum / scenario_role / **market_state enum 4 档** / **pricing_snapshots[] append-only** / pricing_anchor / evolved_from_evidence / lifecycle_stage / freshness_state / review_policy |
| Probability | `pm_probability: float (0-1)`，**显式说"多条 scenarios 概率之和不必等于 1（可有 overlap 或 gap）"**（PDF §4.1） | `pm_conviction: enum {primary / plausible / tail}` —— 同 intent（避真概率假设）不同 representation |
| Trigger threshold | `trigger_signals[].threshold: string` + `current_status: enum {pending / triggered / disproved}`（PDF §4.2） | `trigger_signals[].breaks_chain_node: enum {demand / supply / pricing / policy / adoption / margin}` + status enum —— 同 prose threshold pattern，不同 enum 切片维度 |
| State machine | 4 状态（draft / active / triggered / invalidated / obsolete） | lifecycle_stage 集 align |
| AI function | Scenario Candidate Generation（5-8 条）+ Blind Spot Detector + Cross-Thesis Linkage + Scenario Stress Tester + Tree Navigator（PDF §4.4）+ explicit "AI 不做什么" 4 红线 | [`research-thesis-adversary`](../../.claude/skills/research-thesis-adversary/) skill 写 scenario_triggers + scenario 一等对象升级（per [3-layer upgrade](../ideas/world_model_evidence_pricing_three_layer_upgrade.md)） + [`research-evidence-reviewer`](../../.claude/skills/research-evidence-reviewer/) 独立 reviewer 跨 cut |
| **关键差异 1** | V5.5 **无 market_state pricing dimension**（factor_exposure 在 basket 层不在 scenario 层） | trading_platform market_state 4 档 + pricing_snapshots time-series 是独有的 alpha mispricing layer |
| **关键差异 2** | V5.5 scenario 通过 ExpressionLink 跟 basket N:M（V5.5 schema-level 创新） | trading_platform scenario 跟 basket 是 1:N 隐式 prose |

### §2.4 Baskets stage（V5.5 first-class，trading_platform 不做）
| 维度 | V5.5 | trading_platform |
|---|---|---|
| 是否一等对象 | **First-class**（PDF §1.3 原则 3）：唯一可量化对象，PnL / Sharpe / attribution / factor exposure 全挂这 | **不做**（per [tech brief §8 显式 NOT doing](trading_platform_t0_tech_brief_20260427.md)）：basket 是 hedge fund 产品形态需要；single-PM 用 [`operation-portfolio-decision`](../../.claude/skills/operation-portfolio-decision/) skill prose 输出已足够 |
| ExpressionLink N:M | 独立 linking table：scenario_id / basket_id / weight_contribution。一 basket 表达多 scenarios，一 scenario 多 basket 表达 | **无对应** |
| AI function | Candidate Instrument Recommender + Historical Analog Finder + Factor Exposure Analyzer + Cross-Basket Correlation Monitor + Attribution Engine | 不适用（无 basket 对象） |

**这是 V5.5 vs trading_platform 最大的对象差异**：basket layer 不存在我们这边，是 single-PM design choice 不是 gap。

### §2.5 Monitor & Evolve stage
| 维度 | V5.5 | trading_platform |
|---|---|---|
| 双层 monitor | scenario qualitative + basket quantitative 双层（PDF §6.2） | scenario / thesis / theme freshness 单层（无 basket 层） |
| Trigger event 模型 | `TriggerEvent` first-class object：scenario_id / signal_matched (JSONB) / severity / confidence / pm_acknowledged | [`evidence_record_v0_2.schema.json`](../../data/runtime/schemas/evidence_record_v0_2.schema.json) first-class：source_quality / source_refs / linked_objects / **belief_delta** / caused_transitions / author_persona / ai_generated / ai_verified / pm_acknowledged / **ai_review_log[]** |
| Performance attribution | `PerformanceRecord` first-class：basket_id / pnl / attribution (alpha / beta / factor / execution) | **不做**（无 basket 层） |
| AI function | Trigger Watcher + Signal Quality Evaluator + Cross-Scenario Correlation Detector + Thesis Evolution Drafter + Performance Attribution Engine + Retroactive Signal Discovery | [`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/) freshness sweeper + freshness_event v0.1 状态机 + [`research-thesis-adversary`](../../.claude/skills/research-thesis-adversary/) writes counter_evidence_observed / next_review_trigger |
| **关键差异 1** | V5.5 **TriggerEvent 是 event log**（pm_acknowledged 字段）；trading_platform evidence_record **加 belief_delta + trust_tier (source_quality) + ai_review_log 三件套**形成 learning ledger | 不同 shape：V5.5 trigger event 闭环 vs trading_platform evidence ledger 闭环 |
| **关键差异 2** | V5.5 Attribution 是 quant PnL breakdown | trading_platform 没有 basket 不做 PnL attribution；attribution 是 lineage walk-back（caused_transitions / evolved_from_evidence） |

---

## §3 7 条 financial adaptation：在 loop infra 之上加什么

**thematic research loop infra 之上的 7 条具体加层**。每条说"V5.5 也是 loop infra 但没这条 / 有但不同 shape" + "trading_platform 独有什么":

### §3.1 Causal chain node 显式 enum（vs trigger signal type 切片）
- V5.5：`trigger_signals[].signal_type: enum {earnings / macro / industry / sentiment}` —— 按"信号来源"切（PDF §4.2）
- trading_platform：`thesis.breaks_chain_node: enum {demand / supply / pricing / policy / adoption / margin}` —— 按"因果链节点"切
- 同 / 异：**两边都把 typed enum 引入**。差异在 enum 取值的切片维度（信号源 vs 因果节点）。**互补不竞争**：可以合并成 2D 标签（来源 × 节点）

### §3.2 Lineage 是 graph 不是 linear，加 evidence join
- V5.5：thesis.predecessor_id + lineage[] 链表式版本（PDF §3.2 + DDL §9.1）+ 4 状态机
- trading_platform：predecessor_id + evolved_from_evidence + caused_transitions + freshness_event 状态机
- 关键差异：trading_platform 加了 evidence join（thesis 的 evolve 必须 reference 触发它的 evidence_id；evidence 反向写 caused_transitions 形成双向闭环）。**V5.5 thesis lineage 系统化程度比 trading_platform 高（state 集合更细），但缺 evidence join**

### §3.3 Non-monotonic 知识 + invalidate 不删除
- V5.5：thesis.state = `invalidated` 保留 lineage；invalidated 可 revive 为 v2（PDF §3.3）
- trading_platform：lifecycle_stage = `draft / active / invalidated / superseded / obsolete` 多 version 并存
- **高 align**。差异小

### §3.4 Persona-segmented 消费（entry-level vs product-tier）
- V5.5：persona 切在 product-tier 层（Framework / Forks Pro / Forks Retail，PDF §1.2 + §8）。entry 内字段不分 persona
- trading_platform：[a17 axiom](../../09_soul/axioms/a17_reader_persona_primacy.md) 6-persona canonical 在 entry 层强制 declare reader_persona
- 差异：V5.5 不是"缺 persona 概念"，是"persona 切割点不同"。trading_platform entry-level projection 更细粒度

### §3.5 Market Pricing dimension（V5.5 没有，trading_platform 独有）
- V5.5：factor_exposure 在 basket 层（quant beta / sector tilt 等），**scenario 层无 mispricing 维度**
- trading_platform：scenario_note.market_state enum 4 档（underpriced / consensus / overpriced / unclear）+ pricing_snapshots[] time-series + pricing_anchor prose
- **trading_platform 独有的 alpha 维度**：alpha = `pm_conviction − market_state`。V5.5 alpha 在 PnL 出来后 attribute；trading_platform alpha 在 scenario 标 market_state 时 ex-ante surface

### §3.6 State-machine freshness with review_trigger（V5.5 已有 thesis 层，trading_platform 扩到全对象）
- V5.5：thesis 4-state + scenario 4-state + theme 5-state + basket 5-state（已系统化）
- trading_platform：freshness_state + review_policy（cadence + stale_after_days + review_trigger[]）+ freshness_event v0.1 状态机 emit log
- **align 但 surface 不同**：V5.5 是 entity state machine；trading_platform 加 review_trigger 事件订阅 + 独立 sweeper 周扫 + freshness_event log。V5.5 state machine 由 PM 触发；trading_platform freshness 由 sweeper 主动 emit

### §3.7 AI cluster + 独立 reviewer 网（vs V5.5 contract-based per-stage AI governance）
- V5.5：每 stage 显式 "AI 不做什么"列表 + 5 原则（A-E：Candidates not Decisions / Proactive / Structured / Explainable / Grounded）+ 6 红线（PDF §7.2-§7.3）。**强 contract-based AI governance**
- trading_platform：cluster pattern（drafter→verifier→adversary thesis 三段式 + owner→curator→debater→reviewer theme 四段式）+ 独立 reviewer 网（[`research-evidence-reviewer`](../../.claude/skills/research-evidence-reviewer/) / [`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/) / [`engineering-project-review`](../../.claude/skills/engineering-project-review/)）。**强 process-based AI governance**
- **contract-based vs process-based 两条路径**：V5.5 把约束写在每 endpoint contract（必须 grounded / 必须 explainable / 必须 candidate-only）；trading_platform 把约束写在 cluster hand-off + 独立 reviewer cross-cut。两种路径都合理，可互补

---

## §4 10 dimension 对照矩阵

| # | Dimension | trading_platform T0 | V5.5 |
|---|---|---|---|
| 1 | **Audience** | single PM internal cognitive infra | 专业 PM（buy-side）primary user：机构 PM / 独立 fund manager / research team lead；retail 走 Forks（V5.5 retail 实现） |
| 2 | **Object model** | 10 schema：theme + thesis v1.6 + scenario v0.1 + evidence v0.2 + path_observation + freshness_event + 4 supporting | **7 一等对象**（PDF §1.5 + DDL §9.1）：Theme + Thesis + Scenario + Basket + ExpressionLink + TriggerEvent + PerformanceRecord |
| 3 | **Probability shape** | enum `pm_conviction: primary / plausible / tail` | `pm_probability: float (0-1)` 但**显式声明"多 scenarios 之和不必等于 1（有 overlap 或 gap）"**（PDF §4.1）。两边都拒绝伪 forecast |
| 4 | **Threshold shape** | prose threshold + `breaks_chain_node` enum + `current_status` | prose threshold + `signal_type` enum + `current_status: enum {pending / triggered / disproved}`（PDF §4.2）。**高 align**，两边都没用 numeric threshold |
| 5 | **Evidence / event layer** | `evidence_record v0.2`：trust_tier + belief_delta + caused_transitions + ai_review_log + ai_verified + pm_acknowledged | `TriggerEvent`：scenario_id / signal_matched / severity / confidence / pm_acknowledged（PDF §1.5 + DDL §9.1）+ `PerformanceRecord` for quant attribution。V5.5 evidence 等价物是 TriggerEvent（event log 形态）；trading_platform 是 learning ledger 形态，**两种闭环模型** |
| 6 | **Market Pricing** | scenario.market_state enum 4 档 + pricing_snapshots[] + pricing_anchor | factor_exposure 在 basket 层（quant beta）；**scenario 层无 mispricing dimension**。trading_platform 独有 |
| 7 | **Persona model** | a17 axiom 6-persona canonical + entry 层强制 declare reader_persona | persona 切在 product tier（Framework / Forks Pro / Forks Retail，PDF §1.2 + §8）；entry 内字段不分 persona |
| 8 | **AI integration / governance** | cluster pattern（thesis 三段式 + theme 四段式）+ 独立 reviewer 网 | per-stage AI function（Theme Radar + Falsifiability Coach + Scenario Generator + Stress Tester + Trigger Watcher + Attribution Engine + 等十几个）+ 5 原则 + 6 红线（PDF §7）。**contract-based vs process-based** 两路径 |
| 9 | **Lineage / freshness** | predecessor_id + evidence join + freshness_event 状态机 + staleness sweeper | thesis 4-state + scenario 4-state + theme 5-state + basket 5-state + version + predecessor_id + lineage[]（PDF §3.2 + §2.3 + §4.3 + §5.3）。**V5.5 状态机覆盖比 trading_platform 广**（theme / basket 都有 state machine） |
| 10 | **Schema discipline** | canonical [`data/runtime/schemas/`](../../data/runtime/schemas/) jsonschema validator at write time（10 schema） | PostgreSQL CREATE TABLE DDL（§9.1）+ ~30 REST endpoint（§9.2）+ AI service response JSON schema 模板（§9.3）。jsonschema-at-file-write vs DDL-at-DB-write + REST-at-API-boundary，不同 enforcement layer |

---

## §5 互相可学：mutual learning matrix

每条标 cross-link 到 §3 对应章节。

### §5.1 trading_platform 能从 V5.5 学（L 列）

| # | 项 | 我们弱在哪 | 学他们什么具体 pattern | 对应 §X |
|---|---|---|---|---|
| L1 | **Multi-source ingest 广度** | single-PM design 假设 PM 自带 source curation；corpus 主要 Gmail + AgentMail | V5.5 Trigger Watcher 7×24 ingest（earnings / macro / industry / sentiment / news API） | — |
| L2 | **Multi-user collaboration features** | 单 PM 不需要 | Forks Pro 即将 expose 的 multi-PM permission / visibility scope | — |
| L3 | **Public-facing render layer** | internal markdown 已足够 | Forks scenario card / vindication card visual 渲染 | — |
| L4 | **Distribution / KOL seed 路径** | 无 distribution channel | Forks Week 12-13 KOL outreach + private launch 模式 | — |
| L5 | **Convergence detector / cross-PM theme matching** | single-PM 不需要 | Forks Week 12 convergence detector embedding + theme tag 优先策略 | — |
| L6 | **ExpressionLink N:M（scenario ↔ basket）一等 linking table** | trading_platform 没 basket 层；scenario→portfolio 是 1:N 隐式 prose | V5.5 ExpressionLink (scenario_id, basket_id, weight_contribution) 独立表设计模式 —— 一基金多 thesis 共享同 basket 表达，或一 thesis 多种 basket 表达 | §2.3 / §3.5 |
| L7 | **State machine 系统化覆盖**（theme / thesis / scenario / basket 都有完整 state 集） | trading_platform thesis / scenario 有 lifecycle_stage，但 theme 只 priority_bucket 没 lifecycle 状态机 | V5.5 theme 5-state（emerging / active / peaking / decaying / dormant）+ 自动 transition 触发条件（"3+ 月无新 thesis → peaking" 等） | §3.6 |
| L8 | **PostgreSQL DDL ready** | trading_platform file-based JSON in git，scale 上限低 | V5.5 §9.1 7 张 CREATE TABLE 已 spec；scale 路径 clear。如要 scale beyond 当前 corpus，可 reference V5.5 DDL 作为 migration target | §4 D10 |
| L9 | **AI service endpoint 已 specced** | trading_platform AI 调用是 skill / Claude IDE inline，没 REST API expose | V5.5 §9.2 暴露 POST /ai/scenarios/generate / POST /ai/baskets/recommend / POST /ai/theses/falsifiability / GET /ai/blind-spots / GET /ai/correlations 等。**外部系统 wrap trading_platform AI cluster 时可以参考 V5.5 endpoint 命名 + response schema** | §6 |

### §5.2 V5.5 能从 trading_platform 学（F 列）

| # | 项 | 为什么 V5.5 该学 | trading_platform 提供什么具体 pattern | 对应 §X |
|---|---|---|---|---|
| F1 | **Evidence Ledger 三件套**（trust_tier + belief_delta + ai_review_log）—— 跟 TriggerEvent 互补不替代 | V5.5 TriggerEvent 是 event log（signal matched / severity / confidence / pm_ack），但**没记 belief_delta**（这条 evidence 对哪个对象 update_direction = support / weaken / open_path / close_path 多大 magnitude）+ 没 trust_tier 分级（primary / secondary / inferred）+ 没 ai_review_log（独立 reviewer append-only review）。三件套加上去，TriggerEvent → Evidence Ledger learning loop | [`evidence_record_v0_2.schema.json`](../../data/runtime/schemas/evidence_record_v0_2.schema.json) 完整 schema + [`research-evidence-reviewer`](../../.claude/skills/research-evidence-reviewer/) skill spec | §2.5 / §3.2 |
| F2 | **Market Pricing layer enum design** —— V5.5 完全没有 | V5.5 alpha 在 PnL 出来后 attribute（reactive）；scenario 层加 market_state enum 4 档 + pricing_snapshots time-series 让 alpha = (pm_lean − market_state) ex-ante surface（proactive） | scenario_note.market_state 4 档 + pricing_snapshots time-series 设计 | §2.3 / §3.5 |
| F3 | **a17 Reader Persona Primacy entry-level** —— V5.5 在 product tier 切，可下放到 entry | V5.5 product tier 切割已经存在（Framework / Forks Pro / Forks Retail），但同 tier 内 entry 字段不分 persona。entry 加 `served_personas: []` 字段后，每条 thesis / scenario 可声明给哪个 sub-persona consumed，更细粒度 projection | a17 axiom 6-persona 表 + entry-level reader_persona declaration | §3.4 |
| F4 | **AI cluster + 独立 reviewer 网（process-based）补 contract-based 缺口** | V5.5 5 原则 + 6 红线 是每 endpoint 的 contract，缺 cross-cutting independent reviewer 跨 stage 复审。trading_platform 独立 reviewer 网（research-evidence-reviewer / staleness-sweeper / engineering-project-review）补此层 | thesis 三段式 + theme 四段式 + 独立 reviewer 网 spec | §3.7 |
| F5 | **canonical schema + jsonschema validator at file-write** —— 跟 V5.5 DDL 互补 | V5.5 PostgreSQL DDL 在 DB-write 时 enforce + REST API 在 boundary expose。文件级 jsonschema 在 git commit / file-write 时 enforce 是另一层。**对 git-based / file-based deployment 形态特别有用**（如 Forks 内部 dev workflow / config-as-code 场景） | [`data/runtime/schemas/`](../../data/runtime/schemas/) 10 schema + write-time enforce pattern | §4 D10 |
| F6 | **breaks_chain_node enum 跟 V5.5 signal_type enum 是不同切片，可合并 2D** | V5.5 signal_type（earnings / macro / industry / sentiment）按"信号来源"切；trading_platform breaks_chain_node（demand / supply / pricing / policy / adoption / margin）按"因果链节点"切。**两个不同维度互补**，trigger_signals 加二维 tag（source × node）信息密度翻倍 | breaks_chain_node enum + thesis_note v1.6 字段设计 | §3.1 |
| F7 | **review_trigger event 订阅 + sweeper 主动 emit** | V5.5 thesis 4-state + scenario 4-state 是 PM 触发为主；review_policy review_trigger[] event 订阅 + 独立 sweeper 周扫主动 emit freshness_event 是 V5.5 没有的。Forks Pro 多 PM 后 freshness 漏掉风险更大，sweeper 模式更 critical | freshness_event v0.1 schema + [`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/) skill | §3.6 |

---

## §6 AI 自动 conversion 评估

### §6.1 方向 1：V5.5 → trading_platform（bottom-up suggestion）
**可行**。V5.5 已 expose 结构化 endpoint（PDF §9.2-§9.3），response 含 reasoning + grounded references。LLM 可消费：
- `POST /ai/scenarios/generate` response → trading_platform `scenario_note v0.1 draft`
- V5.5 thesis evolve draft → trading_platform `thesis_note v1.6 v2 candidate`
- V5.5 TriggerEvent → trading_platform `evidence_record v0.2 draft`（需补 belief_delta + trust_tier 字段）

约束：所有 transform 输出 `lifecycle_stage=draft` + `ai_generated=true` + `pm_acknowledged=false`，PM gate 后才 promote。

### §6.2 方向 2：trading_platform → V5.5（renderer projection）
V5.5 PDF §9.3 已 spec AI service response format。trading_platform schema → V5.5 endpoint 几乎是 plug-in：
- `thesis_note v1.6` → `POST /theses/v5.5` direct map（claim / causal_chain / falsification_conditions 字段对齐）
- `scenario_note v0.1` → `POST /scenarios` direct map（narrative / trigger_signals / pm_probability 字段对齐）
- `evidence_record v0.2` → `POST /triggers` partial map（signal_matched 部分；belief_delta + trust_tier + ai_review_log 在 V5.5 schema 里 missing，需 V5.5 加 §7 hook）

**实际工程现实**：schema-to-API mapping 一周内能 prototype。

### §6.3 双向 sync 是 danger zone，不要做
lineage drift / authority 模糊 / trust tier 跨系统不可移植。正确模型：单向主从。

---

## §7 给 V5.5 的 7 个 native extension hook

每个 hook 是 V5.5 schema 可加的 optional field，default null，generic 用户不感知。financial vertical instance 启用后 enforce：

| # | Hook | 字段形态 | 对应 F | 痛点 |
|---|---|---|---|---|
| H2 | `chain_nodes_affected` causal tagging（跟 signal_type 二维） | `[demand, supply, pricing, policy, adoption, margin]` enum 多选 | F6 | 二维切片信息密度翻倍 |
| H3 | lineage join keys：`evolved_from_evidence` + `caused_transitions` | array of evidence_id + array of {object_type, object_id, from_state, to_state} | F1 | TriggerEvent 升 Evidence Ledger 必需 |
| H5 | `served_personas: []` projection metadata | array of persona enum | F3 | entry-level persona projection |
| H6 | `market_state` decision-relevant 字段 | `underpriced \| consensus \| overpriced \| unclear`（仅 scenario 类） | F2 | 金融决策核心 alpha |
| H7 | `review_policy` 事件订阅 freshness | `{cadence, stale_after_days, review_trigger: []}` | F7 | event-driven freshness |
| H9 | `trust_tier` evidence-only + sub-verdicts | `primary \| secondary \| inferred` + `{coverage, claim_alignment, source_authority}` 三 sub-verdict | F1 | evidence 必须分级 |
| H10 | `ai_review_log: []` append-only review hook | array of `{reviewer_persona, verdict, rationale, at_utc}` | F1 / F4 | 独立 reviewer 网必需 |

设计原则：
- All optional default null —— V5.5 现 7 对象不动
- Validation by entry type —— 启用某 type 后该 type 的 required hook 才 enforce
- 通过 V5.5 §9.3 AI service response schema 模板自然 carry

H 编号从 H2 开始（H1 / H4 / H8 砍掉因为 V5.5 现有设计已涵盖：H1 entry_type → V5.5 7 对象天然 typed；H4 lifecycle_stage → V5.5 4 对象都有 state；H8 author_persona → V5.5 已有 ai_generated + pm_acknowledged）。

---

## §8 trading_platform 已知 gap

诚实 surface 让 V5.5 team 不误判 scope：

| # | Gap | 影响 | Mitigation |
|---|---|---|---|
| G1 | **Single PM 假设硬绑** | schema 假设 single PM as gate（pm_acknowledged: bool）；无 user_id / 无 permission layer / 无 multi-PM ack resolver | V5.5 multi-PM 要 wrap user-identity + permission；schema 至少加 `acknowledged_by_user_id` + `visibility_scope` |
| G2 | **No semantic search / RAG 基础设施** | retrieval 全 canonical-path + tag（per [t10 axiom](../../09_soul/axioms/t10_index_first_ai_for_gaps.md) Index First, AI for Gaps 公理） | 定位 "structured object store"；RAG 是 V5.5 在 trading_platform 之上加层 |
| G3 | **Persona projection 在 entry 层缺失对 V5.5 应用** | a17 是 doc-level 约定 + prompt 写法；entry schema 没 `served_personas: []` 字段（待 H5 加） | propose H5 |
| G4 | **Causal chain node 显式 tagging 不全** | thesis_note v1.6 有 claims / key_dependencies prose，但 `chain_nodes_affected` enum array 字段 schema 还没显式（在 prose 里 implicit） | 可补 schema 字段 |
| G5 | **No public-facing render layer** | 没 PNG card / vindication card / Twitter image | 定位 "purely internal markdown"；V5.5 retail 实现层做 |
| G6 | **Event-driven trigger runtime 不完整** | freshness_event 是 manual trigger（sweeper 周扫）；earnings 自动 cascade runtime 没 build | schema ready / runtime pending |
| G7 | **Multi-source ingest 广度不足** | raw 主要 Gmail + AgentMail + 90 asset_technicals；缺 news API / SEC EDGAR / X / Reddit | 想从 V5.5 学的方向（L1） |
| G8 | **No collaboration features** | 单 PM 不需要 comment / mention / notify | out of scope，V5.5 自建 |
| G9 | **No incremental API** | file-based JSON in git；无 REST / GraphQL / webhook | pitch schema + pattern + data，runtime 要 V5.5 自己 wrap |
| G10 | **Scale 不验证** | 最多 56 thesis + 9 active themes + 数条 evidence；10x / 100x 未跑 | 定位 research-grade，scale validation pending |
| G11 | **数据隐私 / releasable subset 没定** | 56 thesis 含 PM 私有 view | pitch doc 显式 separate "可分享 schema + pattern + 已踩坑" vs "data seed 待授权" |

---

## §9 具体 collaboration 提议

### §9.1 短期（本周可启动，cost 各方 <2 day）
1. **Schema cheatsheet 对齐**：trading_platform [`thesis_note v1.6`](../../data/runtime/schemas/thesis_note_v1_6.schema.json) / [`scenario_note v0.1`](../../data/runtime/schemas/scenario_note_v0_1.schema.json) / [`evidence_record v0.2`](../../data/runtime/schemas/evidence_record_v0_2.schema.json) 字段命名对齐 V5.5 Thesis / Scenario / TriggerEvent 命名。免费但让未来 conversion cost 趋零
2. **`.cursor/rules` 5 条 fork 进 V5.5 团队 contributing.md**：
   - [`13_index_first_ai_for_gaps.mdc`](../../.cursor/rules/13_index_first_ai_for_gaps.mdc)
   - [`31_prompt_boundary_task_vs_control_plane.mdc`](../../.cursor/rules/31_prompt_boundary_task_vs_control_plane.mdc)
   - [`33_clickable_links_for_user_paths.mdc`](../../.cursor/rules/33_clickable_links_for_user_paths.mdc)
   - [`35_pm_writing_contract.mdc`](../../.cursor/rules/35_pm_writing_contract.mdc)
   - [`40_systemic_mismatch_second_order_check.mdc`](../../.cursor/rules/40_systemic_mismatch_second_order_check.mdc)
3. **"已踩过的坑" list 直接 fork**（[`forks_can_use_from_trading_platform.md` §6.1](forks_can_use_from_trading_platform.md)）：DST 时间字符串 / business days 必走 exchange calendar / writer sidecar 模式 / source connector 边界 / AgentMail wrapper 邮件 triage 等

### §9.2 中期（本月内，cost 1-2 week）
1. **Releasable subset 过滤清单**：56 thesis / 10 theme reports / 90 asset_technicals 中明确 publicly releasable / AI prompt 上下文可用 / 内部仅读 三档分类
2. **3 个 high-leverage schema 移植到 V5.5**：
   - evidence_record v0.2 → V5.5 TriggerEvent 升级（per F1）：加 trust_tier + belief_delta + ai_review_log
   - scenario_note v0.1 market_state + pricing_snapshots → V5.5 Scenario 字段加 H6（per F2）
   - freshness_event v0.1 + review_policy → V5.5 4 对象 lifecycle 补 review_trigger 事件订阅（per F7）
3. **AI cluster + 独立 reviewer 网 pattern 给 V5.5 team**：3 套 spec（thesis 三段式 / theme 四段式 / 独立 reviewer 网），V5.5 既有 5 原则 + 6 红线 contract 补 process-based reviewer cross-cut（per F4）

### §9.3 长期（季度，需双方 architect commit）
1. **AI 自动 conversion build**（per §6.2 方向 b）：V5.5 `POST /ai/scenarios/generate` → trading_platform `scenario_note v0.1 draft` ingest pipeline；trading_platform schema 反向 → V5.5 endpoint mapping
2. **7 native extension hook**（per §7）作为 V5.5 schema 升级 RFC：V5.5 engineering team 评估 H2-H10 哪些 v0 进 / 哪些延后

---

## §10 一句话结论

**两边都在 build "AI-native thematic research loop infrastructure"** 这个 genre。V5.5 = multi-tenant hedge fund product 形态，trading_platform = single-PM internal cognitive infra 形态。**互补不竞争**：

- V5.5 借 trading_platform：F1-F7 详见 §5.2（重点 F1 Evidence Ledger 三件套 / F2 Market Pricing dimension / F4 独立 reviewer 网 process-based 补 contract-based）
- trading_platform 借 V5.5：L1-L9 详见 §5.1（重点 L6 ExpressionLink N:M / L7 state machine 系统化覆盖 / L8 PostgreSQL DDL ready / L9 AI service endpoint already specced）
- AI 自动 conversion 走单向 hand-off（V5.5 → trading_platform = bottom-up suggestion；trading_platform → V5.5 = renderer projection 几乎 plug-in），双向 sync 不做

最高 ROI 是 §9.1 短期 3 件（schema cheatsheet + 5 cursor rules fork + 已踩坑 list），cost 极低收益高。中长期看 §9.2 / §9.3 取决于 architect-level commit。
