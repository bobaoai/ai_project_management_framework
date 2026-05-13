---
built_at_utc: "2026-04-27T00:00:00Z"
market_day_at_utc: null
title: trading_platform — T0 技术摘要
audience: 外部技术读者（partner team / engineer / cofounder / informed reviewer）
status: standalone tech brief，非 pitch、非 comparison。Pitch 与 comparison 见 sibling docs（forks_can_use_from_trading_platform.md / 待写 vs_v5_5 doc）
sources:
  - designDoc/ai_native_trading_operating_system.md
  - designDoc/ideas/world_model_evidence_pricing_three_layer_upgrade.md
  - 09_soul/axioms/a17_reader_persona_primacy.md
  - data/runtime/schemas/
---

# trading_platform · T0 技术摘要 · 2026-04-27

## 0. 一句话定位

**trading_platform 是一个为单一 PM（portfolio manager，组合经理）服务的 buy-side internal cognitive operating system。** 它把"PM 一周读 50 篇资料"和"PM 做了 3 个 portfolio decision"之间的认知层（worldview tracking + lineage + evidence + market mispricing）做成 schema-validated 的 structured object store + AI cluster + PM gate 三件套，目的是让 PM 6 个月后能 audit "我当时为什么相信 X / 现在为什么不再相信"。

这是 LLM wiki 这个 genre 在 financial vertical 上的深度适配。我们承认 LLM wiki 是必要基础设施；我们 build 的是 wiki + 7 条金融特异性扩展，而不是又一个通用 wiki。

---

## 1. 这是什么 / 不是什么

### 是
- 单 PM operating system（**single-tenant by design**）
- Audit-grade 认知 archive：所有 thesis / scenario / evidence 入 git，schema 校验，lineage preserved
- ~27 个 AI skill 协作 cluster，每段 hand-off 有显式 lifecycle_stage gate
- 10 份 canonical jsonschema 在 [`data/runtime/schemas/`](../../data/runtime/schemas/) 强制 write-time enforce
- 真实 corpus：56 thesis_notes / 9 active macro themes（10 theme reports）/ 90 asset_technicals reports + 70 signal_packets
- IDE-as-application：Cursor + Claude Code 直接读 markdown / JSON，没有独立 backend / frontend

### 不是
- 多 PM 产品（multi-tenant features 完全不存在）
- 公开发布平台（no public-facing render，no shareable card）
- AI autonomy 系统（所有 lifecycle transition 必须 PM acknowledge）
- 量化决策引擎（no numeric probability / no float threshold）
- 可商业化的 SaaS（research-grade，scale validation pending）
- 通用 LLM wiki（domain-specialized，generic ingest 弱）

---

## 2. Charter

### 服务谁
**一个 PM**（buy-side 内部 decision maker），通过 [a17 axiom](../../09_soul/axioms/a17_reader_persona_primacy.md)（Reader Persona Primacy 公理，本 repo 全局 reader 切分）拆成 6 个 decision shape：

| Persona | 一句话 decision |
|---|---|
| System Builder | 建 harness / skill / schema |
| Regime Analyst | 判 regime + path tree + cross-theme coupling |
| Allocation Decision-Maker | regime → instrument / level / size |
| Exposure Auditor | book 脆弱性 + hedge gap |
| Execution Trader | 当日挂单 / stop（scope-bound，未 active） |
| Thesis Researcher | 写 / 验证 / 攻击 single thesis |

每条 thesis_note / scenario_note / evidence_record 在生产时显式声明它服务哪个 persona 的什么 decision。**不存在 "通用读者"**。

### 解决什么
PM 每周面对：
- 50+ 条 inbound research / earnings / news
- 9 个 active macro theme（每个含多 thesis）
- 5-10 个 portfolio decision（add / reduce / hedge / rebalance）
- 6 个月后 retro 时的 "我当时为什么这么想" audit 需求

通用 wiki / Notion / Bloomberg 各解决一部分，没人解决"把 worldview / evidence / market_state 三层一起 audit"。trading_platform 是这个空隙。

---

## 3. 三层框架

整个项目的 macro narrative 来自 [`world_model_evidence_pricing_three_layer_upgrade.md`](../ideas/world_model_evidence_pricing_three_layer_upgrade.md) 的论断：

> Theme / Thesis / Scenario 是世界模型；Evidence Ledger 是学习机制；Market Pricing Layer 才是交易接口。

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1 · World Model（世界模型）                                │
│  我们对世界长什么样的当前判断 + 未来路径                            │
│                                                                 │
│  themes_metadata v1.6 ─┬─ thesis_note v1.6 ─┬─ scenario_note v0.1│
│                        │                    │                    │
│  9 active 主题          │  56 thesis         │  1 sample（在扩）   │
│  scope / priority      │  claims / falsify  │  trigger / market   │
│  scenario_map          │  cross_theme_links │  pricing_snapshots  │
│                        │                                          │
│                        └─ path_observation v0.1                  │
│                          （pre-thesis 观察，1 sample）            │
└─────────────────────────────────────────────────────────────────┘
                           ▲          │
                           │ caused   │ evolved_from
                           │ transitions │ evidence
                           │          ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2 · Evidence Ledger（学习机制）                            │
│  外部材料如何修正世界模型；非 monotonic                            │
│                                                                 │
│  evidence_record v0.2                                            │
│  按周分目录：data/research/evidence_ledger/<YYYY-WNN>/             │
│                                                                 │
│  source_quality（trust tier 3 档）                                │
│  belief_delta（对哪个对象的 update_direction + magnitude）         │
│  caused_transitions（反向 join 回 thesis / scenario）             │
│  ai_review_log（独立 reviewer append-only）                       │
│  pm_acknowledged（PM gate）                                      │
└─────────────────────────────────────────────────────────────────┘
                                      │ ack
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3 · Market Pricing（交易接口）                             │
│  alpha 来源：pm_lean − market_state                               │
│                                                                 │
│  scenario_note.market_state 4 档                                 │
│    underpriced / consensus / overpriced / unclear                │
│  scenario_note.pricing_snapshots（time-series append-only）      │
│  scenario_note.pricing_anchor（解释 prose）                       │
│                                                                 │
│  下游 operation-portfolio-decision skill 强制引用 ≥1 条 scenario           │
│  的 (pm_conviction, market_state) pair 作 decision rationale     │
└─────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                              portfolio decision
                              (PM 直接落到 instrument)
```

三层之间的 **join key 强制**：
- thesis evolve → 必须写 `evolved_from_evidence: [<evidence_id>, ...]`
- evidence_record → 必须写 `caused_transitions: [{object_type, object_id, from_state, to_state}]`
- operation-portfolio-decision skill → 必须引用 `(pm_conviction, market_state)` 二元对

不允许游离对象。每条 lineage 都能 walk back 到具体 evidence。

---

## 4. Object 模型 + 10 schema 关系

10 份 canonical jsonschema 在 [`data/runtime/schemas/`](../../data/runtime/schemas/)：

| Schema | 角色 | 关键字段（节选） |
|---|---|---|
| `themes_metadata_v1_6.schema.json` | 主题元数据（世界模型顶层） | lifecycle_stage / priority_bucket / scope_boundary / scenario_map / linked_thesis_ids / freshness_state / review_policy |
| `thesis_note_v1_6.schema.json` | 单 thesis 对象（世界模型中层） | claims（≥3 条 prose）/ key_dependencies / falsifiers（≥1）/ scenario_triggers / counter_evidence_observed / cross_theme_links / lifecycle_stage / adversarial_review_log / pm_acknowledged_by |
| `scenario_note_v0.1.schema.json` | 实现路径一等对象（世界模型底层 + Market Pricing 接口） | parent_thesis_id / trigger_signals / pm_conviction / scenario_role / **market_state** / **pricing_snapshots[]** / **pricing_anchor** / evolved_from_evidence / lifecycle_stage / freshness_state |
| `evidence_record_v0_2.schema.json` | Evidence Ledger 一等对象 | source_type / source_quality（trust tier）/ source_refs / linked_objects[] / **belief_delta** / caused_transitions / author_persona / ai_generated / ai_verified / pm_acknowledged / **ai_review_log[]** |
| `path_observation_v0_1.schema.json` | pre-thesis 观察对象 | supporting_evidence_ids / tentative_themes / graduation_target_scenario_id / lifecycle_stage |
| `freshness_event_v0_1.schema.json` | 状态机转换日志 | object_type / object_id / from_state / to_state / trigger_kind / trigger_evidence_id / supersedes_event_id |
| `bootstrapper_proposal.schema.json` | theme 创建 Stage A 输出 | dimension_scores / synthesis_narrative_per_theme / recommended_outcome（5 enum） |
| `owner_round_2_decision.schema.json` | theme 创建 PM gate decision | chosen_outcome / pm_explicit_confirm / rationale |
| `theme_candidate.schema.json` | scanner 输出（候选 theme） | scanned_window_utc / candidates[] |
| `perplexity_log_v0_1.schema.json` | LLM 外部 verification call log | caller_persona / purpose / query / response_summary / source_urls |

**Lineage join 图**（Mermaid，对象级 + cross-layer join key 标注）：

```mermaid
flowchart LR
    %% ===== Raw / external sources =====
    subgraph RAW["Raw layer · external sources"]
        direction TB
        MI["messages_index<br/>(archive-first)"]
        IR["image_reviews"]
        PL["perplexity_log v0.1"]
    end

    %% ===== Layer 1: World Model =====
    subgraph WM["Layer 1 · World Model（世界模型）"]
        direction TB
        TM["themes_metadata v1.6<br/>9 active themes"]
        TN["thesis_note v1.6<br/>56 theses"]
        SN["scenario_note v0.1<br/>1 sample"]
        PO["path_observation v0.1<br/>1 sample (pre-thesis)"]
    end

    %% ===== Layer 2: Evidence Ledger =====
    subgraph EL["Layer 2 · Evidence Ledger（学习机制）"]
        direction TB
        ER["evidence_record v0.2<br/>evidence_ledger/&lt;YYYY-WNN&gt;/"]
        FE["freshness_event v0.1<br/>staleness_sweep/&lt;YYYY-WNN&gt;.jsonl"]
    end

    %% ===== Layer 3: Market Pricing =====
    subgraph MP["Layer 3 · Market Pricing（交易接口）"]
        direction TB
        PS["scenario_note.pricing_snapshots[]<br/>append-only time-series"]
        PD["operation-portfolio-decision skill<br/>强制引用 (pm_conviction, market_state)"]
    end

    %% ===== World Model 内部 =====
    TM -->|linked_thesis_ids| TN
    TN -->|scenario_triggers + parent_thesis_id| SN
    PO -->|graduation_target_scenario_id| SN

    %% ===== Evidence ↔ World Model 双向 join =====
    ER -->|linked_objects| TM
    ER -->|linked_objects| TN
    ER -->|linked_objects| SN
    TN -.->|evolved_from_evidence| ER
    SN -.->|evolved_from_evidence| ER
    ER -->|caused_transitions<br/>(lifecycle gate)| TN
    ER -->|caused_transitions<br/>(lifecycle gate)| SN

    %% ===== Evidence ↔ Raw =====
    ER -->|source_refs| MI
    ER -->|source_refs| IR
    ER -->|source_refs| PL

    %% ===== Freshness ↔ World Model =====
    FE -->|object_id<br/>active → stale_warning → stale → needs_relabel| TM
    FE -->|object_id| TN
    FE -->|object_id| SN
    FE -->|object_id| PO
    FE -.->|trigger_evidence_id| ER

    %% ===== Layer 3 接口 =====
    SN -->|"pricing_snapshots[-1]"| PS
    PS -->|consumed by| PD

    %% ===== 颜色按 layer 分 =====
    classDef wmStyle fill:#e6f3ff,stroke:#4a90d9,stroke-width:2px,color:#000
    classDef elStyle fill:#fff4e6,stroke:#d97f00,stroke-width:2px,color:#000
    classDef mpStyle fill:#e6ffe6,stroke:#2d8c2d,stroke-width:2px,color:#000
    classDef rawStyle fill:#f0f0f0,stroke:#888,stroke-width:1px,stroke-dasharray: 5 3,color:#333
    class TM,TN,SN,PO wmStyle
    class ER,FE elStyle
    class PS,PD mpStyle
    class MI,IR,PL rawStyle
```

**图的读法约定**：
- 实线箭头 `-->` = 强 join（write-time schema 字段直接 reference 对方 id）
- 虚线箭头 `-.->` = 反向 / 派生 join（A 的字段写另一头的 id 形成 bidirectional 闭环）
- 颜色按三层分组（蓝 = World Model / 橙 = Evidence Ledger / 绿 = Market Pricing / 灰 = Raw）
- 每条 edge label 是 schema 实际字段名，可直接 grep 验

每个对象的 lifecycle_stage 状态机典型 transition：`draft → active → invalidated | superseded | obsolete`。**所有 transition 必须有 evidence_record 支撑且 PM acknowledge**，不允许 AI 自动跳。

---

## 5. 一个具体 workflow 走查（PM Monday morning）

让上面 schema 落地，下面是真实使用例（虚构但 representative）：

**08:00** PM 打开 Cursor。Inbox 有 12 封新邮件 +某 broker 转发的 earnings call transcript。

**08:05** 调用 [`ingestion-agentmail-inbox-triage`](../../.claude/skills/ingestion-agentmail-inbox-triage/) skill。skill 把 12 封拆 3 类：8 封日常 sell-side note 入 archive；3 封含新事件 flag 给 PM；1 封是 spam。Earnings transcript 用 [`ingestion-research-archive-operator`](../../.claude/skills/ingestion-research-archive-operator/) 归档到 `data/research/messages/<weekiso>/`，写 messages_index entry。

**08:20** PM 看到 transcript 提到一个未覆盖 theme（"AI inference capex 转移到 custom silicon"）。调用 [`research-theme-discovery-scanner`](../../.claude/skills/research-theme-discovery-scanner/) 扫过去 2 周 messages，clustering 找到 7 条相关 message。emit `theme_candidates/<scan_id>.json`。

**08:35** 调用 [`research-theme-bootstrapper`](../../.claude/skills/research-theme-bootstrapper/) Stage A 跑 similarity scan：跟 17 个 active theme 比，propose `narrow_existing_then_admit`（既有 "AI semiconductor" theme 缩 scope 后开新 sibling theme）。emit `bootstrapper_proposal.json`。

**08:50** PM 不同意，给 round 2 decision = `admit_new`（保留既有 theme 完整 scope，新主题独立开）。写 `owner_round_2_decision.json`。bootstrapper Stage B 执行 admit_new branch，写 `themes/metadata/ai_inference_custom_silicon.json`（schema_version 1.6）。

**09:10** 调用 [`research-thesis-drafter`](../../.claude/skills/research-thesis-drafter/) 起 thesis："AI inference workload 从 GPU 转 custom silicon 的速度被市场低估"。drafter 写 `thesis_note v1.6` 含 ≥3 条 claims + key_dependencies + falsifiers，lifecycle_stage = draft。

**09:30** 调用 [`research-thesis-verifier`](../../.claude/skills/research-thesis-verifier/)。verifier 跑 perplexity / web 三角验证，写 `perplexity_log` entry，append `external verification:` 一行到 thesis notes。同时 emit 1 条 `evidence_record v0.2`（author_persona=verifier, ai_verified=false, pm_acknowledged=false）含 belief_delta 描述 verification 对哪些 claim 是 support / weaken。

**09:50** 调用 [`research-thesis-adversary`](../../.claude/skills/research-thesis-adversary/)。adversary 写 falsifiers[] / scenario_triggers[] / counter_evidence_observed[] / next_review_trigger，emit 第 2 条 evidence_record（counter evidence）。promote thesis lifecycle_stage = draft → active 但需 PM ack。

**10:15** PM review 两条 evidence_record。调用 [`research-evidence-reviewer`](../../.claude/skills/research-evidence-reviewer/) 独立 AI gate（跟 verifier / adversary 不同 model 不同 prompt），re-judge trust_tier + belief_delta + source-content support 三 sub-verdict。两条都过，append `ai_review_log` entry，flip ai_verified=true。

**10:30** PM 在两条 evidence_record 上写 `pm_acknowledged: true`。thesis lifecycle_stage 升 active。同时 thesis 写 `evolved_from_evidence: [ev_id_1, ev_id_2]`，evidence_record 反向写 `caused_transitions: [{object: thesis_xxx, from: draft, to: active}]`。

**10:45** PM 去 `scenario_notes/` 起一条 scenario：`ai_inference_capex_shifts_to_custom_silicon.json`，parent_thesis_id 指上面 thesis。pm_conviction=plausible，rank_within_thesis=2。market_state 暂留 `unclear`。

**11:00** PM 调用 [`operation-portfolio-decision`](../../.claude/skills/operation-portfolio-decision/) skill 评估对当前 book 的影响。skill 强制引用上面 scenario 的 (pm_conviction, market_state) 二元对作 rationale 写入 decision note。

**12:00** 当周稍后，[`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/) 周扫所有 17 theme + 56 thesis + 1 scenario + 1 path_observation 的 review_policy。3 条 thesis 因为 next_review_trigger 命中 earnings 事件而 stale_warning。emit `freshness_event` 3 条 + 写 `data/runtime/staleness_sweep/2026-W17.md` digest 给 PM 周日 review 用。

**整周后**：[`engineering-project-review`](../../.claude/skills/engineering-project-review/) skill 跑 cross-cutting independent review on the week's commits（包括上面 schema-write 的所有改动），cross-check schema enums vs canonical stores、instructions vs runtime enforcement、mirror dirs 一致性。emit 严重度分级 review report。

---

## 6. Skill cluster taxonomy

27 skill 不是 flat list，是 grouped cluster：

| 组 | 角色 | 成员 |
|---|---|---|
| **Discovery** | 候选 theme 找出来 | [`research-theme-discovery-scanner`](../../.claude/skills/research-theme-discovery-scanner/) → [`research-theme-bootstrapper`](../../.claude/skills/research-theme-bootstrapper/) Stage A & B |
| **Thesis 三段式** | single thesis 起草 → 验证 → 攻击 | [`research-thesis-drafter`](../../.claude/skills/research-thesis-drafter/) → [`research-thesis-verifier`](../../.claude/skills/research-thesis-verifier/) → [`research-thesis-adversary`](../../.claude/skills/research-thesis-adversary/) |
| **Theme 四段式** | macro theme report 写作流 | [`research-theme-report-owner`](../../.claude/skills/research-theme-report-owner/) → [`research-theme-knowledge-and-package-curator`](../../.claude/skills/research-theme-knowledge-and-package-curator/) → [`research-theme-report-debater`](../../.claude/skills/research-theme-report-debater/) → [`research-theme-report-reviewer`](../../.claude/skills/research-theme-report-reviewer/) |
| **独立 Reviewer 网** | cross-cutting，不 mutate body 只 emit append-only review log | [`research-evidence-reviewer`](../../.claude/skills/research-evidence-reviewer/) / [`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/) / [`engineering-project-review`](../../.claude/skills/engineering-project-review/) |
| **Consumer** | 下游用 worldview 做实际 decision | [`operation-portfolio-decision`](../../.claude/skills/operation-portfolio-decision/) / [`single-stock-analysis`](../../.claude/skills/single-stock-analysis/) / [`research-current-market-reporter`](../../.claude/skills/research-current-market-reporter/) / [`writer-asset-technical`](../../.claude/skills/writer-asset-technical/) |
| **Ingestion** | 外部 source 入库边界 | [`ingestion-agentmail-inbox-triage`](../../.claude/skills/ingestion-agentmail-inbox-triage/) / [`ingestion-research-archive-operator`](../../.claude/skills/ingestion-research-archive-operator/) / [`ingestion-source-connector-designer`](../../.claude/skills/ingestion-source-connector-designer/) / [`ingestion-image-review-reader`](../../.claude/skills/ingestion-image-review-reader/) |
| **Router** | 任务到达时的顶层 routing | [`routing-task-mode-router`](../../.claude/skills/routing-task-mode-router/) / [`routing-current-macro-priority-router`](../../.claude/skills/routing-current-macro-priority-router/) |
| **Gateway** | 跨 cluster 的 hand-off 闸门 | [`writer-handoff`](../../.claude/skills/writer-handoff/) / [`research-theme-priority-updater`](../../.claude/skills/research-theme-priority-updater/) |

**Cluster pattern 的关键 insight**：单 agent 写 + 自审 = AI hallucination 没人 catch。Cluster + 显式 hand-off + 独立 reviewer = 每段 hand-off 是 gate，每个 reviewer 是 cross-cutting check。这是 "audit-grade AI output" 的 architectural answer。

---

## 7. 7 条 design discipline

让我们在 LLM wiki 这个 genre 内深度适配 financial vertical 的 7 条原则。每条都 baked into schema 或 skill：

### 7.1 Archive-first
任何外部 source 入库前先 archive raw 到 `data/research/messages/<weekiso>/` 或 `data/knowledge/<domain>/raw/`。Cognitive 层只引用 archive 不复制内容。Audit 时永远能回到 single source of truth。

### 7.2 [a17 Reader Persona Primacy](../../09_soul/axioms/a17_reader_persona_primacy.md)
6-persona canonical 表全 repo 全局固定。每条 doc / artifact 显式声明服务哪个 persona 的什么 decision。**没有"通用读者"**。

### 7.3 AI candidate vs PM decision boundary
所有 AI 起草的 entry 必须 `ai_generated=true` + `pm_acknowledged=false`。Lifecycle_stage transition 必须有 PM ack。AI 永远不 auto-publish。

### 7.4 Lineage preservation
Invalidated / superseded thesis / scenario 不删除。`predecessor_id` + `caused_transitions` + `evolved_from_evidence` 三组 join key 强制。6 个月后能 walk back 任一 active 对象到原始 evidence。

### 7.5 [T10 Index First, AI for Gaps](../../09_soul/axioms/t10_index_first_ai_for_gaps.md)
deterministic 能做的事 hardcode 做（registry / canonical path / tag / schema validation）；AI 只填 semantic gap（claim 抽取 / sentiment / belief_delta 判断）。**无 fallback chain**（不写"先 regex 试，不行再 LLM 兜底"）。

### 7.6 Schema-validated at write-time
write 任何 entry 必经 jsonschema validate。Bad shape 不进 canonical store。这把"AI 自由生成的 enum 词汇会跨 run 漂移"这条 risk 关在门外。

### 7.7 独立 reviewer 网（cross-cutting）
[`research-evidence-reviewer`](../../.claude/skills/research-evidence-reviewer/) / [`research-theme-staleness-sweeper`](../../.claude/skills/research-theme-staleness-sweeper/) / [`engineering-project-review`](../../.claude/skills/engineering-project-review/) 三个 reviewer 不属于任何 cluster，cross-cut 所有 cluster 的 output。**只 append review log，不 mutate body**。Audit 永远 traceable。

---

## 8. 显式 NOT doing（边界声明）

诚实 surface 让读者不误判 scope：

| 不做 | 为什么 |
|---|---|
| Numeric `pm_probability: float (0-1)` | 宏观因果链强数字 = 伪精度。用 `pm_conviction: enum{primary/plausible/tail}` |
| Numeric `threshold: float` | trigger 用 prose + `breaks_chain_node` enum，靠因果节点证伪 |
| AI auto-publish / auto-invalidate | 所有 lifecycle transition 必须 PM ack |
| Multi-tenant / multi-PM | 单 PM design，schema 假设 single source of truth gate |
| 公开 render（PNG card / shareable image） | internal-only，markdown / JSON 已足够 PM 消费 |
| Semantic search / RAG / vector store | T10 Index First 选择，retrieval 用 canonical path + tag |
| Collaboration features（comment / mention / notify） | 单 PM 不需要 |
| Cron-driven evidence 扫描 | Evidence 是判定副产品不是入库副作用，自动化扫描会让 ledger 信噪比崩塌 |
| `basket` 一等对象 | hedge fund 产品形态需要；单 PM 用 operation-portfolio-decision prose 输出已足够 |
| 跨 repo evidence_ledger 同步 | local 资产，不进 portable soul 层 |

---

## 9. AI-native paradigm + tech stack

### Paradigm
**No backend / no frontend。IDE is the application。**

PM 操作系统的方式：
- 打开 Cursor 或 Claude Code（IDE）
- IDE 读 markdown / JSON / Python source
- 调用 skill（`.claude/skills/*/SKILL.md` 是 prompt + workflow spec）
- skill 调用 underlying tool（python script / curl / git）
- 输出落 markdown / JSON 入 git

整个系统 = git repo + AI runtime（Claude / Cursor）。没有部署、没有 server、没有 web UI。

### Tech stack
| 层 | 选择 |
|---|---|
| 数据 | JSON files in git，jsonschema validated。无 DB |
| 存储 | git repo。Diff-able / portable / auditable |
| AI runtime | Anthropic Claude（Opus 4.7 / Sonnet 4.6 / Haiku 4.5）via Cursor IDE 或 Claude Code CLI |
| Skill 定义 | Markdown 在 `.claude/skills/<name>/SKILL.md`（也镜像到 `.cursor/skills/`） |
| Validator / loader | Python 3 + jsonschema 4.26 + pyyaml 6.0 |
| 时间契约 | [`src/tools/time_semantics.py`](../../src/tools/time_semantics.py)（T11 时间语义公理） |
| Source ingestion | AgentMail（[`src/research/agentmail.py`](../../src/research/agentmail.py)）/ Gmail routing / web fetch |
| Archive 工具 | [`src/research/archive.py`](../../src/research/archive.py) |
| Export | [`src/tools/export_markdown_document.py`](../../src/tools/export_markdown_document.py) markdown → DOCX → PDF |
| External AI verification | Perplexity API + 自定义 verifier prompts |

### Why JSON-files-in-git over DB
- **Audit-able**：每条 entry 的每次改动是 git commit，blame 可用
- **Diff-able**：任何 schema 演进 / lineage 变化都是 PR 级别可读
- **Portable**：clone repo 即获完整系统，无 server dependency
- **AI-friendly**：LLM 直接读 markdown / JSON 比读 DB schema + run query 高效
- **Cost**：单 PM 数据量 file-based 完全可承
- 代价：scale 上限低（10x 我们 corpus 还行，100x 未验证）

---

## 10. Persona / voice 层

跟数据层 orthogonal。

### Hoveath identity layer
Claude 在本 repo 操作时戴的 identity（per [`09_claude/core/SOUL.md`](../../09_claude/core/SOUL.md)）。是 trading_platform 内 AI 工作执行体的人格底色：真正有用而不是表演有用 / 通过能力赢得信任 / 有观点 / 不破折号 / 否定改正向。

### Domain voice carrier
针对特定 domain 的写作 voice。例：
- [`09_soul/personas/fed_watcher.md`](../../09_soul/personas/fed_watcher.md) —— Fed-watcher 20 年观察经验 voice，用于 Fed cognitive 层 prose 写作（**Fed Domain 已 paused 在本 repo 测试**）
- 未来其他 domain（ECB-watcher / commodity-desk-watcher / geopolitics-watcher）按同模板可建

### a17 Reader Persona（消费者层）
Hoveath 写完后**给谁读**。a17 axiom 6-persona canonical（§2 Charter 已列）。

三层 orthogonal：identity（谁写）/ voice（怎么写）/ reader（给谁读）。schema 强制每条 entry 显式 reader_persona。

---

## 11. Communication discipline as feature

不只是 style 偏好，是 PM-AI loop signal-rich 的工程选择。写在 [`09_claude/core/COMMUNICATION.md`](../../09_claude/core/COMMUNICATION.md)：

- **务实理性克制**：不堆华丽词藻 / 不用"惊喜"营销词 / 用数据和逻辑说话
- **不用破折号**：能拆两句的拆开，能用冒号分句的用冒号
- **避免否定句式**：与其说 "X 不是 Y" 直接说 "X 是 Z"
- **任何编号标签每条回复内首次出现都必须 inline 注明它讲什么**：a17（Reader Persona Primacy 公理）/ R07（KB-AP boundary rule）/ T10（Index First, AI for Gaps）等所有 letter+digit identifier 在每条回复 first appearance 强制 inline 解释。理由：用户可能从中间某条读起，每条必须 self-contained
- **Self-Review Protocol**：交付任何 Proposal 前调用 [`09_soul/skills/bestpractice_doc_self_review.md`](../../09_soul/skills/bestpractice_doc_self_review.md) 三阶段审

这些 rule 不是装饰；它们让 PM 6 个月后回看 doc 不需要重新 mental dictionary 翻 label。低 friction = 长期 retention。

---

## 12. 当前 maturity & scale

| 维度 | 当前 |
|---|---|
| Active themes（themes/metadata/*.json） | 9 |
| Theme reports（themes/reports/*.md） | 10（含已存档 / 跨版本） |
| Thesis_notes | 56（部分 v1.5 待升 v1.6） |
| Scenario_notes | 1 sample（T0 周末新落） |
| Evidence_records | 数条（按 ISO 周分目录，2026-W17 已开始填） |
| Path_observations | 1 sample |
| Asset technicals reports（.md，每 asset 一份最新 snapshot） | 90 |
| Asset technicals signal_packets（deterministic JSON） | 70 |
| Skills | 27 |
| Canonical schemas | 10 |
| Build pace | 单 PM weekend / weeknight craft project，不是 VC sprint |
| Scale validation | 跑过 ~10x 当前 corpus；100x 未验证 |
| Multi-PM 适配 | 0（design choice，not roadmap） |
| 公开发布版本 | 无 |

**Stage 描述**：research-grade for single user。production for me（Bokan PM 用）。not packaged for resale, not API'd, not multi-tenant ready。

---

## 13. 路线图（next 3-6 月）

| 优先 | 工作 | Status |
|---|---|---|
| 1 | Market Pricing Layer C 字段在 scenario_note 真实 populate | schema ✓ / data 待填 |
| 2 | scenario_note v0.2 加 cross-thesis linkage（many:many parent_thesis_ids） | propose 中 |
| 3 | thesis_notes 全 corpus 升 v1.6 | 部分完成 |
| 4 | Fed Domain 三层架构（Hardcode / Mining / Eval）build 在独立 project（已 paused 在本 repo） | external project 进行 |
| 5 | context_infra_evaluation framework 横向扩到非 Fed surface | propose 中 |
| 6 | path_observation → scenario graduation workflow 跑通 | schema ✓ / workflow 待 |
| 7 | Multi-source ingest 广度（news / earnings / SEC EDGAR） | 弱项，pending |

**显式不做**：multi-tenant / RAG / public render / collaboration features / numeric prob upgrade。这些是 LLM wiki / hedge fund product 方向，跟我们 single-PM cognitive infra 方向 orthogonal。

---

## 14. Pointer：读者要看实际 substance 去哪

| 想看什么 | 去哪 |
|---|---|
| 全部 canonical schema | [`data/runtime/schemas/`](../../data/runtime/schemas/) |
| Skill 定义（27 个） | [`.claude/skills/`](../../.claude/skills/) |
| 真实 thesis 样本 | [`data/research/thesis_notes/`](../../data/research/thesis_notes/) |
| 真实 theme report | [`data/research/themes/reports/`](../../data/research/themes/reports/) |
| Scenario 一等对象 sample | [`data/research/scenario_notes/`](../../data/research/scenario_notes/) |
| Evidence Ledger sample | [`data/research/evidence_ledger/2026-W17/`](../../data/research/evidence_ledger/2026-W17/) |
| Asset technicals reports | [`data/knowledge/asset_technicals/reports/`](../../data/knowledge/asset_technicals/reports/) |
| 系统级架构 truth | [`designDoc/ai_native_trading_operating_system.md`](../ai_native_trading_operating_system.md) |
| 三层框架 idea doc | [`designDoc/ideas/world_model_evidence_pricing_three_layer_upgrade.md`](../ideas/world_model_evidence_pricing_three_layer_upgrade.md) |
| Reader Persona axiom | [`09_soul/axioms/a17_reader_persona_primacy.md`](../../09_soul/axioms/a17_reader_persona_primacy.md) |
| 50+ axioms 索引 | [`09_soul/axioms/INDEX.md`](../../09_soul/axioms/INDEX.md) |
| Communication 风格 | [`09_claude/core/COMMUNICATION.md`](../../09_claude/core/COMMUNICATION.md) |
| Hoveath identity | [`09_claude/core/SOUL.md`](../../09_claude/core/SOUL.md) |
| 用户 profile | [`09_claude/core/USER.md`](../../09_claude/core/USER.md) |
| Project 主仓约定 | [`CLAUDE.md`](../../CLAUDE.md) |

---

## Appendix A · 8 generic LLM wiki function 我们 map

LLM wiki genre 通常含 8 个 core function。我们每个都有，但 financially adapted：

| LLM wiki function | 我们的实现 | 适配点 |
|---|---|---|
| 1. Source ingestion + archive | [`ingestion-agentmail-inbox-triage`](../../.claude/skills/ingestion-agentmail-inbox-triage/) + [`ingestion-research-archive-operator`](../../.claude/skills/ingestion-research-archive-operator/) + `messages_index.jsonl` | archive-first 纪律：raw 永久保留，cognitive 层只引用 |
| 2. Structured authoring | AI cluster + PM gate | typed entries（thesis / scenario / evidence 各自 schema），不是 prose-only |
| 3. Retrieval | canonical path + tag + linked_*_ids | T10 Index First：deterministic 索引 first，无 RAG |
| 4. Citation + provenance | source_refs + linked_objects + 五标签 citation discipline（[T1] / [raw] / [aggregated] / [pending T1] / [cognitive]） | trust_tier 3 档（primary / secondary / inferred） |
| 5. Versioning + history | predecessor_id + lifecycle_stage + freshness_event 状态机 | Non-monotonic：invalidate 不删除；branching graph 不是 linear edit |
| 6. Linked references | evolved_from_evidence + caused_transitions + cross_theme_links | bidirectional join key 强制；audit walk-back |
| 7. AI consumption interface | Skill 协议 + canonical path direct read | persona-segmented：每条 entry 显式 reader_persona |
| 8. Audit + governance | 独立 reviewer 网 + ai_review_log append-only + pm_acknowledged gate | "AI candidate vs PM decision" 边界写在 schema |

我们做的 = generic LLM wiki + 7 条 financial vertical adaptation：
1. Causal chain object model（key_dependencies / breaks_chain_node / falsifiers）
2. Lineage 是 graph 不是 linear edit history
3. Non-monotonic supersession
4. Persona-segmented consumption（a17 6-persona）
5. Market Pricing dimension（market_state / pricing_snapshots）
6. State-machine freshness（review_policy + review_trigger[]）
7. AI cluster + PM gate（不是 single-agent edit）

---

## Appendix B · 跟外部 framework 的关系

### Forks / Forge V5.5（Thematic Research Loop Infrastructure）
我们与 Forks 都在 LLM wiki genre 内 build。差异：
- **scope**：他们 multi-PM hedge fund product；我们 single-PM internal cognitive infra
- **优势侧**：他们广（multi-source ingest / multi-tenant / social distribution / public render）；我们深（typed schemas / lineage join / 独立 reviewer / persona primacy）
- **mutual learning**：我们想学他们的 ingest 广度 + multi-user collaboration；他们可考虑 take in 我们的 7 条 financial adaptation 作为 financial vertical extension
- 详细对照见 sibling docs：[`forks_can_use_from_trading_platform.md`](forks_can_use_from_trading_platform.md)（v1.0 stale，待 v1.1 升级）/ 待写 vs_v5_5 comparison doc

### 通用 LLM wiki product（Notion AI / Glean / Mem 等）
解决 broad org knowledge retrieval。我们是 narrow domain（single-PM financial decision）+ deep schema。互补不竞争：通用 wiki 给企业，我们给 PM 做 deep cognitive 工作。

### Hedge fund 内部工具（Bloomberg / FactSet / 自建 IDB / Notion vault）
Bloomberg 给 market data + execution，没 worldview tracking。Notion vault 给 doc 但无 lineage / audit / schema。我们填这两端中间空隙：worldview + evidence + market_state 三层 audit-grade structured store。

---

## 一句话结尾

trading_platform = 给单 PM 做 worldview audit + evidence learning + market mispricing 三层 cognitive infra。LLM wiki genre 内的 financial vertical 深度适配。Single-PM by design，schema-validated，audit-grade。Build 在 git + AI IDE 之上，无 backend 无 frontend，IDE is the application。

**这是 substance 性 deliverable 不是 product pitch**。需要的话见 sibling pitch doc / vs comparison doc。
