# Belief Revision System — World Model · Evidence-to-Belief · Pricing · Adversary · Cadence（T0）

> Status: idea / proposal（未实现，未 canonical）
> First written: 2026-04-26
> Last revised: 2026-04-26（吸收同事 review 的 7 点反馈）
> Owner: trading_platform / research memory layer
> 触发对话: PM 在评审 V5.5-Product-Definition 后提出三层论断 ——
> "Theme / Thesis / Scenario 是世界模型；Evidence Ledger 是学习机制；Market Pricing Layer 才是交易接口。"
> 同事 review 把它进一步升维为：本 doc 不只是"对象模型升级"，而是一套 **belief revision system**——
> 真正的强度不在加字段，而在 review / staleness 这条硬约束。
> Sibling specs:
> - [`research_50_thesis_and_theme_agent_cluster.md`](../research_50_thesis_and_theme_agent_cluster.md) — 当前 cluster 边界（drafter / verifier / adversary / scanner / bootstrapper）
> - [`research_40_thesis_note_schema_v1_5.md`](../research_40_thesis_note_schema_v1_5.md) — 当前对象模型 v1.5
> - [`bp/V5.5-Product-Definition.pdf`](../bp/V5.5-Product-Definition.pdf) — 外部 Forge 团队的 framework 蓝本

---

## 0. Reader End-State

读完本 doc，PM 应当能：

- (a) 把当前结构（`themes/metadata/` + `thesis_notes/v1.5` + `theme_update_drafts/` + `messages_index.jsonl`）按"世界模型 / 学习机制 / 交易接口 / 对抗审查 / 时效纪律"五维重新对位，看清各自缺什么；
- (b) 知道为什么我们**不**直接搬 V5.5 的强字段（`pm_probability: float` / `threshold: numeric`）—— 我们的因果链是宏观 / 半宏观，强数字会变成伪精度；
- (c) 知道五项升级的优先级排序及理由——**Evidence-to-Belief 先连，Staleness 紧跟硬约束，再补 Scenario / Pricing / Adversary**——以及"为什么不先做 scenario"的具体理由；
- (d) 知道每一项升级要碰哪些 schema / 哪些 skill / 哪些 builder / 哪些下游消费方；
- (e) 知道哪些**不做 / 推后**：不引入 numeric probability、不让 AI 自动改 lineage、不为每条 message 强制建 evidence record、不在 v0.1 把 thesis causal_chain 拍成结构化 nodes（推到 Open Questions Q5 等 dogfood 数据）。

---

## 1. 当前结构 vs 五维框架

### 1.1 把现状拍到五维上

| 维度 | 我们当前对应物 | 状态 |
|---|---|---|
| **世界模型**（Theme / Thesis / Scenario） | `themes/metadata/<id>.json` + `thesis_notes/<id>.json` (v1.5) | Theme + Thesis 已结构化；**Scenario 仍是 thesis 内的扁平 prose 列表（`scenario_triggers[]`）**，不是一等对象 |
| **学习机制**（Evidence-to-Belief Ledger） | `messages_index.jsonl` + `image_reviews.jsonl` + `theme_update_drafts/` | 原始素材层存在；**素材 → belief 状态变化 的连接缺失**（archive 与 thesis lineage 之间没有显式 link，更没有 prior→posterior 的 belief delta 记录） |
| **交易接口**（Market Pricing） | 散在 operation-portfolio-decision skill prose / theme report 文末 / PM 头脑里 | 完全没有结构化对应物；`pm_belief − market_consensus` 的 mispricing 维度只在 PM 直觉里，**且没有时间序列** |
| **对抗审查**（Adversarial Review） | `research-thesis-adversary` SKILL 跑过就跑过，输出散在 thesis prose | **没有 per-version 的 adversarial review log**；PM 看不出 thesis vN 是否真的被挑战过、unresolved objection 在哪 |
| **时效纪律**（Review Cadence / Staleness） | 没有任何机制 | 完全空白；active thesis / scenario 可以无限期"还活着"，事实早已腐烂 |

### 1.2 五维之间的真正失配点

我们目前的失配不是字段少，而是**层与层之间没有可追踪的 join key + 没有时间维度的强约束**：

- thesis evolve 出 v2 时，记 `predecessor_id` 但**不记是哪条 evidence 触发了 evolve、belief 从什么 prior 变到什么 posterior**；
- scenario 散在 thesis prose 里，**没法独立追踪"哪条路径先发生"**；
- portfolio 决策时凭印象判断"市场已经 price in 了哪条路径"，**没有结构字段记录这个判断**，更没有"市场 pricing 如何从 unclear 变到 consensus"的路径；
- adversary 跑过就跑过，**没有 per-version 留底**，PM 容易陷入 confirmation machine；
- 最致命：**没有 cadence 约束**——一条半年没人动的 active scenario 仍然显示 active，对 operation-portfolio-decision 而言它跟昨天刚 verified 的 scenario 一样有效。

五个失配点对应五项升级，本 doc 提案按"修连接 → 装时效硬约束 → 补对象 → 补维度 → 装对抗审查"的顺序推进。

---

## 2. 设计原则（取自 V5.5 但有意降维 + 同事 review 升维）

### 2.1 保留

- **三层强制父子链**：scenario.parent_thesis_id / thesis.parent_theme_id / evidence.linked_object_id 都必须存在，不允许游离对象。
- **lineage 只读保留**：invalidated / superseded 的 thesis / scenario 不删除，archive-first 纪律不变。
- **AI candidate / PM decision 边界写进对象**：沿用 v1.5 的 `lifecycle_stage` 思路，扩到 evidence、scenario、adversarial review 三个新表面。

### 2.2 显式拒绝

- **不引入 `pm_probability: float (0–1)`**。改用 `pm_conviction: enum { high / medium / low / exploratory }` + `narrative_role: enum { leading_path / parallel_path / tail_path / counterfactual }` 两个独立维度（拆开"belief 强度"和"在 thesis 叙事中的位置"两件事）。
- **不要求 `threshold: numeric`**。允许 prose threshold（"若 H20 出口禁令延期超过一个 quarter"），但**强制标注 `breaks_chain_node`**——靠因果链节点（demand / supply / pricing / policy / adoption / margin）证伪，不靠表面阈值。
- **不为每条 archive 入库的 message 强制建 evidence record**。Evidence 只在"PM / cluster 主动判定它影响了某个 thesis / scenario / theme 的 belief 状态"时创建——是**判定的副产品**，不是入库副作用。
- **不让 AI 自动 evolve lineage**。Evidence record 可以由 verifier / adversary 起草，但 thesis / scenario 的 state transition 仍必须 PM 显式 acknowledge。
- **不在 v0.1 把 thesis causal_chain 拍成结构化 nodes**（同事 review 的第 5 点）。理由见 §9 Open Questions Q5：v1.5 prose causal chain 自带"顺序 / 让步 / 副词时效 / 段落连贯"四种机器扔不掉的信号，强行拍成对象数组会让 author 排序判断被 schema 对齐压力扭曲；先用 inline tag + evidence.affected_chain_node 跑 3 个月再决定。
- **不在 scenario 上加 `scenario_origin` enum**（同事 review 第 2 点的反提议路径）。bottom-up path 信号走 §5 的 `path_observation` 旁路对象，scenario 仍强制 parent_thesis_id；这避免下游 reviewer / operation-portfolio-decision 撞到"无家可归"的 scenario。

### 2.3 五维之间的 join key（最关键）

引入一组轻量约定：

- thesis evolve / scenario state transition 时，**必须**在新对象上写 `evolved_from_evidence: [<evidence_id>, ...]`；
- evidence record 反向写 `belief_delta: { prior_state, posterior_state, changed_dimension, rationale }` + `caused_transitions: [{object_type, object_id, from_state, to_state}]`；
- operation-portfolio-decision skill 在写 decision rationale 时，**必须**引用至少一条 scenario 的 `pricing_snapshots[-1].market_state` + `pricing_anchor`；
- adversarial_review_log 的 `unresolved_objections` 必须**指回 evidence_id**——一条 unresolved objection 就是一条 belief_delta 还没 resolved 的 evidence；
- staleness sweeper 改 `lifecycle_stage = stale` 时**必须写一条 belief_delta**（changed_dimension = `scenario_lifecycle` 或 `thesis_lifecycle`），让所有状态变更都进 belief 账本。

这五个 join 是把"世界模型变化 / belief 学习 / 交易决策 / 对抗审查 / 时效推进"串起来的最小约定，是本 T0 升级的核心。

---

## 3. 升级 #1 · Evidence-to-Belief Ledger（学习机制层）

### 3.1 Why（为什么放第一）

当前最大的结构盲区。我们能看到一篇 research 被 archive 进 `messages_index.jsonl`，能看到某条 thesis 从 v1 evolve 到 v2，**但看不到二者之间的因果连接，更看不到 belief 状态的 prior→posterior 路径**。结果：

- thesis lineage 知其然不知其所以然——团队交接 / regulator audit / 半年复盘都无法 replay；
- 长材料蒸馏（PM 主诉求场景：访谈 / 政策讲话 / 长 sell-side note）的输出无处落——目前只能写在 theme_update_drafts 里，散文形式；
- AI cluster 跑一次 verifier / adversary 后，外部验证证据没有结构化承接；
- **更关键**：没有 belief_delta 字段时，evidence record 退化为索引层；有 belief_delta 才让 ledger 真正成为"学习机制"。

### 3.2 What

新建一等对象 `evidence_record v0.1`，放在 `data/research/evidence_ledger/<YYYY-WNN>/<id>.json`（按周分目录，与 progress 周报对齐）：

```jsonc
{
  "id": "...",
  "source_type": "earnings_call | transcript | policy | expert_call | sell_side | research_note | price_action | image_review | perplexity_verify",
  "source_quality": "primary | secondary | inferred",
  "source_refs": [                       // 必须挂回 archive，不允许游离
    {"system": "messages_index", "id": "<rid>"},
    {"system": "image_reviews", "id": "<image_review_id>"},
    {"system": "perplexity_log", "id": "<verifier_call_id>"}
  ],
  "evidence_summary": "...",             // 50–200 字 prose；标注哪段事实对哪条因果链节点起作用
  "linked_objects": [                    // 一条 evidence 可影响多个对象
    {
      "object_type": "theme | thesis | scenario",
      "object_id": "...",
      "update_direction": "support | weaken | open_new_path | close_path | ambiguous",
      "affected_chain_node": "demand | supply | pricing | policy | adoption | margin | scope_boundary",
      "magnitude": "minor | moderate | major",   // 不是 float；三档够用
      "confidence": "high | medium | exploratory"
    }
  ],
  "belief_delta": {                      // 同事 review 第 1 点：让 ledger 成为学习机制
    "prior_state": "...",                // prose 描述变化前 belief 状态
    "posterior_state": "...",            // prose 描述变化后
    "changed_dimension": "causal_chain_node | scenario_rank | scenario_lifecycle | thesis_lifecycle | market_state | scope_boundary | conviction | adversarial_resolution",
    "rationale": "..."                   // 为什么这条 evidence 触发这个 delta
  },
  "caused_transitions": [                // 反向 join，状态机推进时回填
    {"object_type": "thesis", "object_id": "...", "from_state": "active", "to_state": "evolving"}
  ],
  "author_persona": "drafter | verifier | adversary | pm | scanner | sweeper",
  "ai_generated": true,
  "pm_acknowledged": false,              // PM 看过且接受才置 true；驱动 lineage transition
  "created_at": "...", "updated_at": "..."
}
```

`changed_dimension` 的 8 个值覆盖：因果链节点修订、scenario 间相对排序、scenario / thesis 的 lifecycle 变化（含 active→stale）、市场定价感知、theme scope 边界变化、PM conviction 调整、对抗 objection 关闭。这把后面所有四项升级的状态变更都收口到 belief ledger，无一例外。

### 3.3 触发规则（不是入库副作用，是判定副产品）

evidence_record 在以下时机创建：

1. **verifier 跑完外部三角验证** → 自动起草 1 条 evidence（author_persona=verifier, pm_acknowledged=false, belief_delta.changed_dimension 由 verifier 自填）；
2. **adversary 找到 counter_evidence** → 自动起草 1 条 evidence（author_persona=adversary）；
3. **PM 在 review 长材料时手动 flag** → 用一个轻量 CLI / skill 接口写入（author_persona=pm, pm_acknowledged=true）；
4. **scanner 在 bottom-up 扫到簇但还没成 theme** → 写 evidence linked_objects=[] + 一条 candidate ref，等待 bootstrapper Stage A 决策；
5. **sweeper 把 active 对象改为 stale** → 自动写一条 evidence（author_persona=sweeper, changed_dimension=scenario_lifecycle / thesis_lifecycle, pm_acknowledged=false 等待 PM review）。

**关键约束**：thesis / scenario 的 lifecycle_stage transition 必须引用至少一条 `pm_acknowledged=true` 的 evidence，否则 cluster reviewer 拦下。这是把"AI candidate / PM decision"边界写到 schema 里的具体兑现。

### 3.4 与 archive-first 纪律的关系

evidence_record 不复制 archive 内容——只引用 `source_refs`。它是**判定层**，不是存储层。
archive 仍是 single source of truth；evidence ledger 是 archive 的索引视图 + belief revision overlay。

---

## 4. 升级 #2 · Review Cadence / Staleness Discipline（时效纪律）

### 4.1 Why（为什么紧跟在 #1 后面而不是放最后）

同事 review 第 7 点：**市场情报对象最大的问题不是错，而是 stale**。

把 staleness 提到第二位的三条理由：

- **最便宜**：一个 sweeper skill + 三个对象加 `review_policy` 字段；
- **乘数效应**：belief ledger 没 cadence → 退化为日志垃圾；scenario 没 stale → alpha 追踪退化为废墟巡游；market pricing 没 cadence → 一周后脱锚；adversarial review 没 cadence → confirmation machine。**其他每一项升级的 ROI 都依赖 staleness 这条硬约束**。
- **ROI 远高于 scenario 一等对象**：scenario 升级是 cluster 级别改动面，staleness 是单 sweeper。

光加字段没用——必须配 enforcement。

### 4.2 What

#### 4.2.1 三个对象上加 `review_policy` 字段

适用于 theme（active / peaking 状态）、thesis（active / evolving 状态）、scenario（active / triggered 状态）：

```jsonc
"review_policy": {
  "cadence": "weekly | monthly | event_driven",
  "next_review_at": "ISO8601",
  "stale_after_days": 30,                // 超过此天数无 review 自动转 stale
  "review_trigger": ["earnings | policy_update | price_dislocation | scheduled"]
}
```

#### 4.2.2 默认 cadence（schema 里硬编码，不每个对象单独填）

| 对象类型 | 默认 cadence | stale_after_days | event-driven trigger |
|---|---|---|---|
| theme | monthly | 60 | scope_breach / cross_theme_overlap |
| thesis | monthly + event_driven | 45 | earnings / policy_update |
| scenario | bi-weekly + event_driven | 21 | price_dislocation / sell_side_revision |

PM 可以在单个对象上 override default，但 override 必须在 review_policy 里 inline 写明 `override_reason`。

#### 4.2.3 新增 sweeper skill `research-theme-staleness-sweeper`

每周扫一次所有 active object：

- 命中 `next_review_at < now()` 或 `last_updated_at + stale_after_days < now()` 的对象，**自动改 `lifecycle_stage = stale`** 并写一条 evidence_record（author_persona=sweeper, changed_dimension=scenario_lifecycle / thesis_lifecycle, pm_acknowledged=false）；
- 输出一份 `data/runtime/staleness_sweep/<YYYY-WNN>.md` 报告，列出本次刷下来的所有对象 + 触发原因，给 PM 周末 review。

#### 4.2.4 硬门控（最关键的一条）

**stale 的对象不进 operation-portfolio-decision skill 的 candidate set。** 这是 schema 里**强制**的：

- operation-portfolio-decision 读 active scenario 时，自动过滤 `lifecycle_stage = stale`；
- 想用 stale scenario 必须先走 revive 流程（PM 写一条 evidence_record + belief_delta，把 lifecycle 改回 active）；
- 这把"stale = 死信号"从约定升级为系统级 enforcement，杜绝"反正 stale 我也能用"的退化。

### 4.3 触动到的 skill

- 新增 `research-theme-staleness-sweeper`（独立 skill，不挂在现有 priority-updater 上——理由：sweeper 是无状态的扫描器，priority-updater 是有意图的 PM-driven 重排序，两者职责正交）；
- `operation-portfolio-decision` SKILL：读 candidate set 时强制过滤 stale；
- `research-thesis-drafter` / `research-thesis-adversary`：起草 / 修订时必须填 `review_policy`，default 由 schema 兜底但不能省。

---

## 5. 升级 #3 · Scenario 一等对象（世界模型层）+ Path Observation 旁路

### 5.1 Why

当前 `thesis_note v1.5` 的 `scenario_triggers[]` 是 thesis 内嵌字段（research_06 §1.2 + §2），扁平 prose 数组，没有 parent 关系、没有独立状态机、不能跨 thesis link。结果：

- 一条 thesis 下的多条实现路径全压在 prose 里，PM 没法单独追踪"哪条 path 先发生"；
- 两个不同 theme 下的 thesis 即使共享同一条 realization path，也无法在结构上 link；
- adversary 写 scenario_trigger 阈值时缺一个独立对象承接，trigger 命中后没有规范的"scenario 状态推进"动作。

### 5.2 What — `scenario_note v0.1`

新建一等对象，放在 `data/research/scenario_notes/<id>.json`：

```jsonc
{
  "id": "ai_inference_capex_shifts_to_custom_silicon",
  "parent_thesis_ids": ["..."],          // v0.1 先 1:1，v0.2 再开放多 parent（见 §9 Q1）
  "parent_theme_ids": ["..."],           // 冗余字段，便于反查；由 cluster 自动填充
  "narrative": "...",                    // prose，描述路径
  "trigger_signals": [                   // 沿用 v1.5 内嵌结构，不要 numeric threshold
    {
      "signal_type": "earnings | macro | industry | sentiment | policy",
      "description": "...",
      "threshold_prose": "...",          // 允许 prose；不强制 numeric
      "breaks_chain_node": "demand | supply | pricing | policy | adoption | margin",
      "current_status": "pending | triggered | disproved | stale",
      "last_checked_at": "ISO8601"
    }
  ],
  "pm_conviction": "high | medium | low | exploratory",  // belief 强度
  "narrative_role": "leading_path | parallel_path | tail_path | counterfactual",  // 在 thesis 叙事中的位置
  "rank_within_thesis": 1,               // 同 thesis 下 scenarios 的相对排序（与 narrative_role 互补，不冗余）
  "lifecycle_stage": "draft | active | triggered | invalidated | obsolete | stale",
  "ai_generated": true,
  "adopted_from_draft": true,
  "lineage_predecessor_id": null,        // sub-scenario 分叉时填
  "evolved_from_evidence": ["<evidence_id>", ...],
  "review_policy": { ... },              // 见 §4.2.1，default bi-weekly
  "linked_baskets": [],                  // 留 placeholder，由后续 portfolio 升级填
  "pricing_snapshots": [...],            // 见 §6
  "graduated_from_path_observation": null,  // 若由 §5.4 path_observation 升上来则填
  "created_at": "...", "updated_at": "...", "author_id": "..."
}
```

注意 `pm_conviction` 与 `narrative_role` 是**两个独立维度**（同事 review 第 3 点）：一条 tail_path 可以有 high conviction（低概率但高破坏力），一条 leading_path 也可以 exploratory conviction（结构上是主线但 PM 还没看清楚）。两者**不**互推。

`narrative_role` 故意**不**用 sell-side 的 base/upside/downside 三分——我们处理的多数宏观叙事是几条互斥 path 抢主导，没有"对称分布的中间 base"。`hedge_case` 不进 scenario schema（它是 portfolio expression 层属性），由 operation-portfolio-decision 在读取 (pm_conviction, narrative_role) 时自行映射。

### 5.3 与 v1.5 的兼容

- `thesis_note v1.5` 的 `scenario_triggers[]` 字段**保留为 fallback**，但新建 thesis 起 cluster 必须把每条 trigger 抽成独立 `scenario_note`，原字段降级为 prose summary。
- lazy migration：旧 thesis 不强制回填 scenario_note；当某条 thesis evolve 到 v2 时，cluster 同步把它的 scenario 抽出。

### 5.4 Path Observation 旁路（同事 review 第 2 点的安置点）

bottom-up 信号"先看到路径迹象、再回头形成 thesis"是真问题。但**不**通过给 scenario 加 `scenario_origin` enum 解决——理由：scenario 强制 parent_thesis 是为了下游 reviewer / operation-portfolio-decision 不撞 null pointer。

新建轻量旁路对象 `path_observation v0.1`，放在 `data/research/path_observations/<YYYY-WNN>/<id>.json`：

```jsonc
{
  "id": "...",
  "discovered_at": "...",
  "narrative": "...",                    // 早期路径迹象的 prose 描述
  "supporting_evidence_ids": [...],      // 必须 ≥1 条 evidence_record
  "tentative_themes": [...],             // 可能挂在哪些 theme 下（多对多，模糊）
  "lifecycle_stage": "observed | cluster_formed | graduated_to_scenario | dismissed",
  "graduation_target_scenario_id": null, // graduate 时填，反向写入 scenario.graduated_from_path_observation
  "review_policy": { "cadence": "weekly", "stale_after_days": 14 },  // 旁路对象 stale 阈值更短
  "created_at": "...", "updated_at": "..."
}
```

**生命周期约束**：

- `observed`：单条 path 信号，scanner / PM flag 都可以创建；
- `cluster_formed`：同主题 path_observation 数 ≥3 时由 scanner 聚簇；
- `graduated_to_scenario`：PM 决定把这条 path 升为 scenario 时执行——**graduate 动作必须**：(1) 创建 scenario_note 并强制绑 parent_thesis_id；(2) 在 evidence_record 写一条 belief_delta（changed_dimension=scenario_lifecycle）；(3) path_observation 转只读保留 lineage；
- `dismissed`：14 天没 graduate 也没新支持证据，sweeper 自动 dismiss。

这样 bottom-up 信号有承接物，scenario schema 的强制父子链不破坏。

### 5.5 触动到的 cluster / skill

- `research-thesis-adversary` SKILL：原本写在 thesis 上的 `scenario_triggers[]`，改为产出独立 `scenario_note draft[]`（ai_generated=true, lifecycle_stage=draft）；
- `research-theme-discovery-scanner` SKILL：新增 path_observation 输出能力（在 candidate 之外），且其 candidate 输出可携带 path_observation_ids 作为佐证；
- `research-theme-knowledge-and-package-curator` SKILL：package 装配时增加 scenario_note slot；
- `operation-portfolio-decision` SKILL：从读 thesis prose 改为读 active scenario_notes + (pm_conviction, narrative_role, pricing_snapshots[-1])。

---

## 6. 升级 #4 · Market Pricing Snapshots（交易接口层）

### 6.1 Why

当前最弱的认知维度。PM 做 portfolio decision 时凭印象判断"市场已经 price in 哪条路径"，但这个判断没有结构字段记录，**也没有时间序列**——同事 review 第 4 点指出的问题：只能知道"现在 underpriced"，不知道它是从 unclear 变来的还是从 consensus 变来的。**复盘价值大头在路径，不在状态。**

### 6.2 What

不新建对象，在 `scenario_note`（升级 #3 已建）上加一个时间序列字段：

```jsonc
{
  "pricing_snapshots": [
    {
      "as_of": "ISO8601",
      "market_state": "underpriced | consensus | overpriced | unclear",
      "pricing_anchor": "...",           // prose；解释为什么是这个 state
      "pricing_evidence_refs": [         // 挂回 evidence_ledger
        "<evidence_id>", ...
      ],
      "review_context": "earnings | price_move | sell_side_revision | positioning | scheduled_review"
    }
  ]
}
```

读取时用 `pricing_snapshots[-1]` 取当前态；retro / drift detection 用全序列。

**显式拒绝**：

- 不加 `market_implied_probability: float`。pricing 推断在我们这里靠的是 sell-side consensus prose / options skew 观察 / valuation 比较，不靠 numeric probability extraction。enum 四档够 portfolio decision 用。
- 不加单独的 `pricing_last_reviewed_at` 字段——它退化为 `pricing_snapshots[-1].as_of`，避免冗余。
- 不要求每条 scenario 都填。只对 `lifecycle_stage = active` 且被 operation-portfolio-decision skill 引用过的 scenario 强制 ≥1 个 snapshot；其他 scenario `pricing_snapshots = []` 即默认 unclear。

### 6.3 触动到的 skill / 报告

- `operation-portfolio-decision` SKILL：原本输出 prose 决策，改为**强制引用 ≥1 条 scenario 的 (pm_conviction, narrative_role, pricing_snapshots[-1].market_state)** 三元组作为决策依据；
- `research-theme-knowledge-and-package-curator`：theme report 里 scenario 段落需展示 (pm_conviction × market_state) 矩阵，让读者一眼看清"哪条 path PM 看好但市场未 price in"；
- `research-current-market-reporter` 的当日复盘可以反向**追加** snapshot 到相关 active scenario 的 pricing_snapshots[]（不修改既有 snapshot，只 append）；
- `research-theme-staleness-sweeper`：scenario 的 stale 判定需要看 `pricing_snapshots[-1].as_of`——pricing review 也算 review，避免误把刚做完 pricing review 的 scenario 刷成 stale。

---

## 7. 升级 #5 · Adversarial Review Log（对抗审查层）

### 7.1 Why

同事 review 第 6 点：adversary 跑过就跑过，输出散在 thesis prose 里，PM 看不出 thesis vN 这个**版本**是否真的被挑战过。结果系统容易退化为 confirmation machine——PM 只看到支持性 evidence，不知道 unresolved objection 还堆在哪。

关键观察：要回答的问题不是 "thesis 这个 entity 有没有被挑战"，而是 **"thesis vN 这个 version 有没有被挑战"**——挂在 thesis entity 上的 `last_challenged_at` 会让 PM 产生假安全感（"反正挑战记录在这"）。

### 7.2 What

在 `thesis_note` 上加 `adversarial_review_log[]`，每次 adversary 跑一次 append 一条记录，每条记录绑 thesis version：

```jsonc
{
  "adversarial_review_log": [
    {
      "reviewed_at": "ISO8601",
      "thesis_version": 2,                          // 必须绑当时的 version
      "adversary_run_id": "...",                    // 引用 adversary skill 的本次执行 id
      "strongest_counter_case": "...",              // prose
      "unresolved_objections": [                    // 引用 evidence_id
        "<evidence_id of unresolved counter-evidence>", ...
      ],
      "resolved_objections": [                      // 本轮 review 中被 resolve 的 objection
        {"evidence_id": "...", "resolution_rationale": "..."}
      ],
      "adversary_confidence": "weak | moderate | strong",
      "next_review_due": "ISO8601"                  // 与 review_policy.cadence 一致
    }
  ]
}
```

**关键约束**：

- `unresolved_objections` 中的 evidence_id 必须是 belief_delta.changed_dimension ≠ `adversarial_resolution` 的（否则就是已 resolved）；
- 一条 objection resolve 时**必须**写一条新 evidence_record，`changed_dimension = adversarial_resolution`，`belief_delta.posterior_state` 解释为何这条 objection 不再有效——这把第 1 点 belief_delta 的 `adversarial_resolution` dimension 跟这里闭环；
- thesis evolve 到 vN+1 时，**继承** vN 的 unresolved_objections，但 resolved_objections 不继承（每个 version 独立审计）。

scenario 上**不**单独加 adversarial_review_log——scenario 的挑战通过它 parent_thesis 的 review_log 反查（scenario 不是独立 belief subject，是 thesis 的 path realization）。

### 7.3 触动到的 skill

- `research-thesis-adversary` SKILL：每次 run 完必须 append 一条 review_log entry + 把 unresolved objections 落成 evidence_record；
- `research-theme-knowledge-and-package-curator`：theme report 必须展示当前 thesis vN 的 unresolved_objections count，> 0 时强制在报告醒目位置列出；
- `research-theme-report-reviewer`：reviewer 检查报告时把 "unresolved_objections > 3" 视为 high severity finding。

---

## 8. 推进顺序（按 ROI 排序，已吸收同事 review 重排）

| # | 升级 | 成本 | 收益 | 阻塞关系 |
|---|---|---|---|---|
| 1 | **Evidence-to-Belief Ledger**（含 belief_delta + 8 维 changed_dimension） | 中（schema + 2-3 个 SKILL 改动） | 高（让所有其他升级有 belief 落点） | 不阻塞下游 |
| 2 | **Review Cadence / Staleness Discipline**（含 sweeper skill + 硬门控） | 低（1 sweeper + 三对象加 review_policy） | **极高（其他每项升级的乘数）** | 依赖 #1（sweeper 写 belief_delta） |
| 3 | **Scenario 一等对象 + Path Observation 旁路** | 中-高（schema + cluster 改动 + builder 升级） | 高（解锁 scenario alpha 追踪 + bottom-up 信号承接） | 依赖 #1 evidence join + #2 review_policy |
| 4 | **Market Pricing Snapshots** | 低（在 #3 的 scenario_note 上加时间序列字段） | 高（operation-portfolio-decision 第一次有可 audit 依据） | 依赖 #3 |
| 5 | **Adversarial Review Log** | 低-中（thesis schema 加字段 + adversary skill 改 + reviewer 加 finding） | 高（防 confirmation machine） | 依赖 #1 evidence join |

**为什么 staleness 从原版的 #5 提到 #2**：它是其他每项升级的 ROI 乘数。belief ledger 没 cadence → 日志垃圾；scenario 没 stale → 废墟巡游；pricing 没 cadence → 一周后脱锚；adversary 没 cadence → confirmation machine。staleness 这一条是整个 belief revision system 的"心跳"，没有它后面再优雅的字段都会 6 个月后变考古现场。

**Causal Chain Nodes 不进这次 T0**（同事 review 第 5 点），推到 §9 Q5 等 dogfood 数据。

---

## 9. 显式不做（避免 scope creep）

- **不做 `basket` 一等对象**。V5.5 把 basket 提为一等并接 ExpressionLink，是 hedge fund 产品形态；我们目前是单 PM 工作流，basket 维度由 operation-portfolio-decision 的 prose 输出承接已足够，强行结构化会变成低价值字段集。
- **不做 numeric probability / numeric threshold / numeric magnitude**。三档 enum 在我们工作流够用，过度量化是伪精度。
- **不做 AI 自动 publish / invalidate**。所有 lineage transition 必须 PM 在 evidence record 上置 `pm_acknowledged=true`。
- **不做 cron 化的 evidence 扫描器**。evidence 是判定副产品，不是入库副作用；自动化扫描会让 ledger 信噪比崩塌。staleness sweeper 是例外——它扫的是已有对象的"心跳"，不创造新认知。
- **不做跨 repo 的 ledger 同步**。evidence_ledger 是 trading_platform local 资产，不进 portable soul 层。
- **不做 `scenario_origin` enum**。bottom-up path 走 path_observation 旁路（§5.4），不污染 scenario 强制父子链。
- **不在 scenario 加 `hedge_case` narrative_role**。hedge 是 portfolio expression 层属性，不是 world-model 层 scenario 属性。

---

## 10. Open Questions（留给 PM 拍板）

- **Q1**：scenario_note 的 `parent_thesis_ids` 允许多对一（V5.5 cross-thesis linkage）。是否要在升级 #3 第一版就开放多 parent，还是 v0.1 先 1:1，v0.2 再开放？
  - 倾向：v0.1 先 1:1，避免 cluster 第一次跑就要处理冲突 parent 的 ranking。
- **Q2**：evidence_ledger 的目录粒度（按周 vs 按月 vs 按 theme）。
  - 倾向：按周（`<YYYY-WNN>`），与 progress 周报对齐，便于 PM 周末 review。
- **Q3**：Market Pricing 的 `market_state` enum 是否要细化到第 5 档（如 `gradually_pricing_in`）？
  - 倾向：先四档，半年后看 operation-portfolio-decision retro 数据再决定。
- **Q4**：thesis_note v1.5 是否同步升 v1.6 加 `evolved_from_evidence` + `review_policy` + `adversarial_review_log` 字段，还是只在 v2 时强制？
  - 倾向：v1.5 软加（optional 字段），v2 强制；避免动 active thesis lineage。但 review_policy 必须 v1.5 软加 + 兜底 default 值，否则 sweeper 跑不起来。
- **Q5**：thesis causal_chain 是否要在未来某个版本拍成结构化 nodes（`causal_chain_nodes[{node_id, claim, expected_signal, break_condition}]`）？
  - 倾向：v0.1 用 inline tag（`[node: demand_growth]`）+ evidence.affected_chain_node 跑 3 个月；如果出现 ≥5 个 case 是 prose 真的承不住的，再启动 chain_nodes 结构化（v0.2 或独立 initiative）。**不进本 T0**。
- **Q6**：sweeper 的执行频率（每周 vs 每日）+ stale 判定是否要给 PM 一个"宽限期"（例如 stale 后 7 天内不进硬门控，给 PM 救活的窗口）？
  - 倾向：每周一次扫；不给宽限期——硬门控就是硬门控，要救活就走 revive 流程写 belief_delta。

---

## 11. 与外部 V5.5 / Forge 团队的关系

本升级**不**是对 V5.5 的 fork。V5.5 是我们的镜子，它照出了我们五个具体缺口：scenario 层缺失、belief 连接缺失、market pricing 维度缺失、adversarial coverage 缺失、staleness 完全空白。我们按自己工作流的颗粒度落，不抄字段。

同事 review 把这次升级从"对象模型升级"推到了"belief revision system"——真正的强度不在多加字段，**在于 review/staleness 这条硬约束**。没有它，再优雅的 belief_delta 也会在 6 个月后变成考古现场。
