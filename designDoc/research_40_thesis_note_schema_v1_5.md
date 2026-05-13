# thesis_note Schema v1.5

**Status**: active main schema spec for thesis_note objects under `data/research/thesis_notes/`
**First written**: 2026-04-19
**Owner**: trading_platform / research memory layer
**Cluster spec**: [`research_50_thesis_and_theme_agent_cluster.md`](research_50_thesis_and_theme_agent_cluster.md)
**Plan source**: [`designDoc/ideas/thesis_and_theme_writing_pipeline_reorg.md`](ideas/thesis_and_theme_writing_pipeline_reorg.md)（Plan B §2.2）
**Reference v1 file**: [`data/research/thesis_notes/ai_capex_is_the_real_melt_up_engine_via_real_rate_easing.json`](../data/research/thesis_notes/ai_capex_is_the_real_melt_up_engine_via_real_rate_easing.json)（90 行 v1）

---

## 0. 文档地位与读者引导

### 0.1 这是什么

仓库里 thesis_note 历史上没有显式 schema，事实标准来自 [`build_theme_writer_package.py`](../src/tools/build_theme_writer_package.py) 与若干现存 v1 文件的归纳。本 doc 把当前事实标准锁住为 **v1**，并定义一个**最小结构化升级** `v1.5`，让 cluster（[research_05](research_50_thesis_and_theme_agent_cluster.md)）的 agent 可以依赖确定的字段集。

### 0.2 读者使用方式

- 想知道现有 v1 字段集（builder 实际读取的）：读 §1
- 想知道 v1.5 加了什么 / 改了什么 / **不**做什么：读 §2 / §3 / §4
- 想知道下游谁会读哪个新字段：读 §5
- 想知道老文件怎么处置：读 §6（lazy migration）
- 想知道为什么不直接做 V5.4 全 schema 升级（v2）：读 §7
- 想知道 schema 字段之外、prose 还应承载什么（多 factor contribution / 多 path 并列 / 反向 path concurrent acknowledgement / inline source ref `[refs: i, j]`）：读 §8

### 0.3 设计原则（v1.5 的核心取舍）

prose 自带四种机器扔不掉的信号：

- **顺序 = 优先级**（`claims[0]` 比 `claims[3]` 重要）
- **句长 + 让步成分 = 信心强弱**（"high confidence X, moderate confidence Y" vs "X" 是不同状态）
- **副词 = 时效边界**（"already", "still", "near-term", "structurally" 各自不同时间窗）
- **段落连贯 = 因果链**（claim_bullets 之间不是 set，是有顺序的论证）

把 prose 数组拍成结构化对象数组（per-claim `{text, falsification_condition, verification_data_source, confidence}`）会让「每条都长得一样重」，PM 后续读时丢失原作者排序判断；LLM 后续 verify / score 也会被字段对齐压力扭曲。

→ **只在机器真正要做状态机判断 / 计数 / 路由的地方结构化，其它一律保 prose**。这是 v1.5 与原 v2 spec 的根本区别。

---

## 1. v1 事实标准（builder 当前读取的字段集）

来自 [`build_theme_writer_package.py:548-580`](../src/tools/build_theme_writer_package.py) 的实际行为。

### 1.1 顶层标识

- `id: str`（kebab-or-snake，文件名同此）
- `title: str`
- `created_at: ISO8601`
- `updated_at: ISO8601`
- `source_research_ids: [str, ...]` ≥1（指向 `data/research/messages/<rid>/`）
- `theme_tags: [str, ...]`
- `related_tickers: [str, ...]`
- `related_assets: [str, ...]`
- `linked_asset_tickers: [str, ...]`（部分 v1 文件有；与 `related_tickers` 历史重复）
- `time_horizon: str`（自由 prose："near_to_medium_term" / "medium_term" / 等）
- `status: str`（自由 prose："active" / "monitoring" / 等；非 enum）
- `notes: str`（自由 prose）

### 1.2 builder 实际渲染的「Theses (selected)」字段

按 [`build_theme_writer_package.py:548-554`](../src/tools/build_theme_writer_package.py) 顺序：

- `claim_bullets: [str, ...]` — prose 数组，顺序 = 优先级
- `key_dependencies: [str, ...]` — prose 数组
- `disconfirming_evidence: [str, ...]` — prose 数组
- `scenario_triggers: [str, ...]` — **v1 是 prose 数组**（与 V5.4 §13.4 想升的对象数组不同）
- `expected_winners: [str, ...]`
- `expected_losers: [str, ...]`
- `probability_view: str` — 单段 prose

### 1.3 v1 没有显式 schema 文件

字段名靠 builder 源码 + 现存 v1 文件归纳。本 doc §1 是**首次把 v1 事实标准写下来**。

### 1.4 v1.5 起有显式 schema 文件（L1 强制层）

v1.5 不再依赖 builder 源码归纳。canonical schema 文件如下：

- [`data/runtime/schemas/thesis_note_v1_5.schema.json`](../data/runtime/schemas/thesis_note_v1_5.schema.json) — drafter / verifier / adversary 共用；包含 `lifecycle_stage = "active"` 时 `falsifiers / scenario_triggers / next_review_trigger / counter_evidence_observed / adversary_at_utc` 必填的条件分支
- [`data/runtime/schemas/theme_candidate.schema.json`](../data/runtime/schemas/theme_candidate.schema.json) — `research-theme-discovery-scanner` 输出
- [`data/runtime/schemas/bootstrapper_proposal.schema.json`](../data/runtime/schemas/bootstrapper_proposal.schema.json) — `research-theme-bootstrapper` Stage A 输出（含 `composite_overlap_score` 加权公式 invariant）
- [`data/runtime/schemas/owner_round_2_decision.schema.json`](../data/runtime/schemas/owner_round_2_decision.schema.json) — `research-theme-report-owner` round-2 决策（强制 `pm_explicit_confirm: const true` + `pm_chat_message_id` 必填）
- [`data/runtime/schemas/themes_metadata_v1_5.schema.json`](../data/runtime/schemas/themes_metadata_v1_5.schema.json) — `research-theme-bootstrapper` Stage B 输出 / `research-theme-knowledge-and-package-curator` 写回；`oneOf` 路由 v1 lazy（历史 17 字段，新结构字段必须不存在）vs v1.5 strict（含 `schema_version: "1.5"` + `scope_boundary` + `scenario_map` + `theme_tags` + `created_at_utc` + `created_via`）。详见 [`research_05 §4.5 themes/metadata v1.5 lazy migration`](research_50_thesis_and_theme_agent_cluster.md#45-themesmetadata-v15-lazy-migrationcluster-假设字段的工程化落地)。**注意**：themes/metadata 的 `lifecycle_stage` 枚举是 `{approved, draft_candidate}`，与本 doc 主题 thesis_note 的 `{draft, active, retired}` 是**两套不同的 lifecycle**，不可混用——见 [`research_05 §4.6`](research_50_thesis_and_theme_agent_cluster.md#46-两套-lifecycle-不混用thesis_note-vs-themesmetadata)

业务层补充规则（schema 表达不了的部分）由 [`src/tools/thesis_cluster_validate.py`](../src/tools/thesis_cluster_validate.py) 兑现：notes 中 `external verification:` 行最多一条 + 单源时 notes 必须含 `single source – verifier 必须扩源` 标记 + `composite_overlap_score` 与公式 1e-6 相等 + `[OVERRIDE]` 前缀与 override flag 一致 + `theme-bootstrapper-stage-b` per-branch 强制 v1.5（admit_new / narrow_then_admit / carve_out_confirmed）vs 接受 v1 lazy（merge_into_existing）。

调用接口（统一通过 `tradectl thesis-cluster`，详见 [`research_05 §4.4`](research_50_thesis_and_theme_agent_cluster.md#44-四层强制层4-layer-enforcement-architecture)）：

```bash
./.venv/bin/python -m src.cli.tradectl thesis-cluster validate <agent_id> <artifact_path>
./.venv/bin/python -m src.cli.tradectl thesis-cluster gate <agent_id> <input_path>
```

---

## 2. v1.5 新增 5 个结构化字段

| 字段 | 类型 | 写入责任 agent | 用途 |
|---|---|---|---|
| `lifecycle_stage` | enum: `draft \| active \| stress_tested \| evolving \| invalidated \| archived` | drafter 写 `draft`；adversary 升 `active`；PM 后续可降 | 让下游 reviewer 机审「是否引用了 invalidated thesis」 |
| `cross_theme_links` | `[{theme_id: str, role: enum}]`，role ∈ `primary \| secondary \| boundary_reference` | drafter | 让 priority-updater 处理 cross-theme 引用 + reviewer 机审「boundary_reference 被当 primary 用」是 major finding |
| `falsifiers` | `[str, ...]` ≥1，纯字符串列表 | adversary | reviewer 强制 ≥1 检查；与 `disconfirming_evidence` (counter_evidence_observed) 区分：falsifiers 是「未来如果 X 发生 thesis 就 wrong」，counter 是「已经观察到的反向证据」 |
| `next_review_trigger` | `{kind: enum, value: str}`，kind ∈ `time \| event \| catalyst` | adversary | 让 PM 知道下次该回看 thesis 的触发条件 |
| `scenario_triggers` (升级) | `[{observable_data, threshold, direction, status, observed_at_utc, hit_evidence}]`，status ∈ `pending \| triggered \| reverse_triggered \| obsolete` | adversary 写初始 `pending`；事件发生后由 PM 或后续 cluster 调整 status | reviewer 机审「triggered 但没进 What to watch」是 major finding |

### 2.1 字段细节

#### `cross_theme_links[].role` 三个值

- `primary`：本 thesis 是该 theme 的主要论据之一（理应在该 theme 报告 ds.md 的「Drivers」段被展开）
- `secondary`：本 thesis 是该 theme 的辅助论据
- `boundary_reference`：本 thesis **不属于**该 theme，但需要在该 theme 报告里被显式引用以说明「这件事归隔壁主题管」（典型：AI capex thesis 在 Hormuz 报告里以 `boundary_reference` 出现）

#### `scenario_triggers[]` 对象详解

```json
{
  "observable_data": "1y US real rates",
  "threshold": "negative",
  "direction": "below",
  "status": "pending",
  "observed_at_utc": null,
  "hit_evidence": null
}
```

- `observable_data` + `threshold` + `direction` 是 trigger 的可机读三件套
- `status` 是状态机：`pending` → `triggered`（条件命中）/ `reverse_triggered`（反向命中，触发 falsifier 同侧逻辑）/ `obsolete`（条件不再相关）
- 命中后 PM / cluster 写 `observed_at_utc: ISO8601` + `hit_evidence: <一句话指向证据>`

#### `next_review_trigger` 单对象

- `kind: time` → `value: "2026-05-15"`（绝对日期）或 `"weekly"`（周期）
- `kind: event` → `value: "next FOMC"` / `"GEV Q2 earnings"`
- `kind: catalyst` → `value: "OpenAI IPO pricing window opens"`

---

## 3. v1.5 改名 2 个字段

> **注意**：本节只描述字段层（structural floor）。`claims[]` / `key_dependencies[]` / `probability_view` / `notes` / `falsifiers[]` / `counter_evidence_observed[]` 这些字段**内部 prose 应当承载的 narrative 形态**（多 factor contribution / 多 path 并列 / 反向路径 concurrent acknowledgement）见 [§8 Narrative 形态约定](#8-narrative-形态约定--schema-化触发条件v15-自由格式承载)。

| v1 字段 | v1.5 字段 | 类型不变 | 理由 |
|---|---|---|---|
| `claim_bullets` | `claims` | `[str, ...]` | builder 注释里就叫 "claim_bullets, dependencies, ..." 不一致；v1.5 收敛 |
| `disconfirming_evidence` | `counter_evidence_observed` | `[str, ...]` | 与 v1.5 新加的 `falsifiers[]` 区分：`counter_evidence_observed` = 已经观察到的反向证据；`falsifiers` = 未来什么发生会让 thesis 失效 |

### 3.1 向后兼容（reader 同时识别新旧名）

`build_theme_writer_package.py` 在 [`Plan B §5.1`](ideas/thesis_and_theme_writing_pipeline_reorg.md#51-builder-向后兼容补丁30-行-diff) 打补丁：

- 先读 `claims`，缺失才回落 `claim_bullets`
- 先读 `counter_evidence_observed`，缺失才回落 `disconfirming_evidence`

新生成的 v1.5 thesis 用新名；老 v1 thesis 不动也仍能渲染。

---

## 4. v1.5 显式撤销的字段（曾考虑过的 v2 字段）

> 下表字段是上一轮 schema v2 讨论里出现过的「全结构化」候选。v1.5 决定**不要它们**，理由是「结构化收益不抵 prose 损失」。各自原因记录在此，避免后续讨论反复。

| 字段 | v2 spec 想做什么 | v1.5 拒绝理由 |
|---|---|---|
| `sub_assertions[]`（per-claim 拆 `{text, falsification_condition, verification_data_source, confidence}`） | 让每条 claim 自带 falsifier 与 verification source | 与 §0.3 设计原则冲突；prose 顺序丢失；LLM 会被字段对齐压力压成均值 |
| `mechanism: str` 独立字段 | 把因果链拆出来 | `claims[]` 的 prose 段落连贯本身就是因果链；额外字段会让 drafter 写两遍 |
| `supporting_evidence[]` / `counter_evidence[]` per-claim object 化 | 让每条证据带结构 | source_research_ids[] 已记录证据 ID；prose 已说明哪条 claim 用哪条证据；object 化只是冗余 |
| `confidence_estimate: float ∈ [0, 1]` | 数值化概率倾向 | V5.4 §5.5 三条硬约束之一就是禁此；用 `probability_view` prose（含 hedging） |
| `evidence_strength` enum（`strong / moderate / weak`） | verifier 标证据强度 | enum 会塌陷成「都标 moderate」；用 verifier 在 `notes` 末尾写 `external verification: <verified \| partial \| pending> – <一句>` 替代 |
| `external_verification_status` enum | verifier 标外部验证状态 | 同上；用 `notes` 末尾固定行替代 |
| `auto_degrade_when[]` | 自动降级条件 | 与 `falsifiers[]` + `scenario_triggers[].status` 重叠；任何「auto」字样要求一个我们目前没有的常驻 watcher |
| `resurrection_rationale: str ≥100 字` | 复活已 archived thesis 时强制写理由 | 真复活时临时写进 `notes` 即可；常态字段是冗余 |

---

## 5. 下游消费者影响清单

### 5.1 `build_theme_writer_package.py` ([Plan B §5.1](ideas/thesis_and_theme_writing_pipeline_reorg.md#51-builder-向后兼容补丁30-行-diff))

- 读 `claims` 优先于 `claim_bullets`，读 `counter_evidence_observed` 优先于 `disconfirming_evidence`
- v1.5 新加字段（`lifecycle_stage / cross_theme_links / falsifiers / next_review_trigger / scenario_triggers` 对象数组）**本轮 builder 不渲染**；它们由 reviewer 消费
- diff ≤30 行

### 5.2 `research-theme-report-reviewer/SKILL.md` ([Plan B §5.2](ideas/thesis_and_theme_writing_pipeline_reorg.md#52-reviewer-最小升级))

verdict 加 `thesis structural readiness` 节，机审：

- `falsifiers[].length`：=0 → minor finding；≥1 → ok
- `scenario_triggers[].status`：若有 `triggered / reverse_triggered` 但 `themes/reports/<theme_id>.md` 没把这条 trigger 写进「What to watch / What changed」→ major finding
- `lifecycle_stage`：若引用了 `invalidated / archived` thesis → major finding
- `cross_theme_links[].role`：若本 theme 引用了 `boundary_reference` 角色的 thesis 但 ds 把它当 primary 论据展开 → major finding

### 5.3 `research-theme-priority-updater/SKILL.md` ([Plan B §3.5](ideas/thesis_and_theme_writing_pipeline_reorg.md#35-升级最小改动))

- 加一节 `cross-theme thesis link role`，处理 thesis 多主题出现时的 role 分配
- 不改写 thesis 文件

### 5.4 cluster 5 agent 自身

- 读 / 写边界见 [`research_05 §3.3`](research_50_thesis_and_theme_agent_cluster.md#33-字段写入约定防止-cross-write)

### 5.5 不消费 v1.5 新字段的下游

- `research-theme-knowledge-and-package-curator`：仍然按 builder 渲染的 package 写报告，不直接读 thesis JSON
- `writer-handoff`：仍然只看 package 的结构，不看 thesis JSON
- `routing-task-mode-router` / `research-theme-report-owner`：路由 / owner 决策不依赖 thesis 字段
- `research-theme-discovery-scanner`：扫的是 `messages_index.jsonl` 与 `themes/metadata/*.linked_research_ids[]`，**不**读 thesis_note JSON（discovery 早于 thesis 落地）
- `research-theme-bootstrapper`：执行层，触发 thesis cluster 后由后者写 v1.5 字段，bootstrapper 自己只读 owner.json + 写 metadata + 写占位 report

### 5.6 新出现的非 thesis 对象（关联但不属本 schema）

- `data/research/theme_candidates/<scan_id>.json` + `.md`（由 `research-theme-discovery-scanner` 产出）：candidate 清单 sidecar + PM-readable summary。**不**是 thesis_note，**不**走 v1.5 schema；含顶层 `scanned_window_utc: {as_of_utc, lookback_days, anchor_kind, scanner_invoked_at_utc}` 字段（F6 / V04 / T11）；schema 见 [`research_05 §2.4`](research_50_thesis_and_theme_agent_cluster.md#24-theme-discovery-scanner) 的「必填输出」段
- `data/research/theme_update_drafts/<theme_id>.bootstrapper_proposal.json`（由 `research-theme-bootstrapper` Stage A 产出）：完整 schema 见 [`research_05 §2.5.3`](research_50_thesis_and_theme_agent_cluster.md#253-bootstrapper_proposaljson-输出-schemaf8--x05)（含 per-dimension `dimension_score_provenance` + `synthesis_narrative`，F8 / X05）
- `data/research/theme_update_drafts/<theme_id>.bootstrapper_proposal.summary.md`（伴生 PM-readable ≤30 行摘要，F11 减负 PM 阅读 proposal.json 全文）
- `data/research/theme_update_drafts/<theme_id>.owner.json` 新增 `bootstrap_arbitration_decision` 字段（owner round-2 决策，含 `pm_explicit_confirm: true` + `pm_chat_message_id` + `decided_at_utc`，F5 / F7 / V01 / T11）：schema 见 [`research_05 §2.5.2`](research_50_thesis_and_theme_agent_cluster.md#252-owner-round-2-决策字段追加在-ownerjson)
- `data/research/theme_update_drafts/<theme_id>.bootstrapper_carve_out_diff.json`（仅 Stage B `carve_out_from` 分支产出）：dry-run 邻居 metadata diff，等 PM 在线 confirm；含 `dry_run_generated_at_utc`
- `data/research/themes/metadata/<theme_id>.json` 新增 1 个可选字段（仅 Stage B 部分分支用）：
  - `merge_audit: [{ source_owner_json, merged_at_utc, merged_keys[] }]`（仅 `merge_into` 分支写到目标 theme 的 metadata，F5 / T11）
- 此 metadata 字段的全 schema spec 不属本 doc；本轮 Plan B 只声明它在 v0.4 cluster 出现，不动现有 metadata 的其它字段
- 注：`parent_theme_id` / `is_overlay` 在 v0.3 草案曾考虑过为 `subordinate_to` 分支预备，v0.4 已**撤销**；B5 直接 raise 不落 metadata（F3 / M05），相关字段等真有 subordinate executor plan 时再加

### 5.7 thesis_note 与 artifact_graph 的关系（F13 / Rule 42）

- 当前 [`data/runtime/artifact_graph.yaml`](../data/runtime/artifact_graph.yaml) **不含** `thesis_note` 节点
- cluster 写 thesis_note 时**不**需要 emit-sidecar；Rule 42 只对 graph 里有节点的 L4 artifact 强制
- 若未来要把 thesis_note 加进 graph（属于另一个 plan），加节点之后 cluster harness 须同步加 `tradectl plan thesis_note --id <id> --emit-sidecar auto` 步骤；本 plan 不强求

---

## 6. v1 ↔ v1.5 共存与迁移

### 6.1 共存策略

- v1.5 字段都是 **additive**：v1 文件没有这些字段，下游不应当 raise；reviewer 在缺失时给 minor finding 而不是阻塞
- 改名 2 个字段（`claim_bullets / disconfirming_evidence` → `claims / counter_evidence_observed`）由 builder 兼容补丁双向识别

### 6.2 lazy migration

- 不做一次性 batch migration
- cluster **触及** v1 thesis 时（drafter 改名 + adversary 补 falsifiers 等）顺手升级到 v1.5
- 未触及的 v1 thesis 保持 v1，不动

### 6.3 升级一份 v1 → v1.5 的最小步骤

1. 改名：`claim_bullets → claims` / `disconfirming_evidence → counter_evidence_observed`
2. 加 `lifecycle_stage`：若 v1 `status` ∈ `["active", "monitoring"]` → v1.5 `lifecycle_stage = "active"`；若 `"archived"` → `"archived"`
3. 加 `cross_theme_links[]`：从 `theme_tags[]` 与 PM 知识里推 role
4. 加 `falsifiers[]`：从 v1 `disconfirming_evidence` 里挑 ≥1 条改写为「未来什么发生会让 thesis 失效」格式
5. 加 `next_review_trigger`
6. 升级 `scenario_triggers[]` 从 prose 数组到对象数组（v1 prose 一行 → v1.5 对象 `{observable_data, threshold, direction, status: pending, observed_at_utc: null, hit_evidence: null}`）

预期升级后 JSON 体量：v1 ~90 行 → v1.5 ~110-125 行。

---

## 7. 为什么不直接做 v2 全升级

上一轮讨论曾考虑过 V5.4 §13.4 风格的全 object 化 v2 schema（即 §4 表里那些字段）。最终选 v1.5 的三个主要理由：

1. **prose 信号损失**：详见 §0.3 设计原则
2. **dogfood 优先**：cluster + 测试基础设施还没建好；先把 contract 锁住、跑通一次 dogfood（[Plan A](ideas/short_term_3_themes_regime_reshuffle.md)），后续若 v1.5 不够再增量补字段，比一步到位安全
3. **下游消费侧能力有限**：没有常驻 Python watcher，所以 `auto_degrade_when[] / confidence_estimate: float` 这类「靠数值连续做调度」的字段产生不了价值
   - 当前的 reviewer + builder 只能消费 enum 与 length 检查，不能消费 float 概率
   - 等下游有真正的概率消费侧（如 operation-portfolio-decision 自动用 confidence 做权重）再加，到时也属 v1.6 / v2 的事

→ v1.5 是「**够新 cluster 跑通 + 够 reviewer 真消费 + 不做工业化全套**」的最小一步。

---

## 8. Narrative 形态约定 — schema 化触发条件（v1.5 自由格式承载）

### 8.1 这一节的位置

一份 thesis 的 effect 通常由多个因子的 contribution 共同支撑，而非单变量 1-to-1 cause；scenarios 通常**可叠加**而非互斥分叉，多条可能同时 unfold；下游 reader 与 PM 真正需要在语义关系上权衡的，是这些并行 path 的 contribution 强弱。

v1.5 schema 不为这套 framing 新增字段。承载位是已有 prose 字段（`claims[]` / `key_dependencies[]` / `probability_view` / `notes` / `falsifiers[]` / `counter_evidence_observed[]`）。schema 化升级只在出现「下游 reader 想 distinguish 但 prose 读不到」的具体落差后再补——见 §8.5 的 4 个升级 trigger。

### 8.2 三件 prose 必须承载的事（按 reader gain 排序）

按下游 reader 真正能 distinguish 的优先级：

1. **多 path 并列承载（最高 reader gain）** — `probability_view` 与（adversary 升 active 后）`falsifiers[]` 必须让 reader 看到「主线 + 同时在跑的次路径」，不强行收敛到单 base case。承载位：drafter 在 `probability_view` 里点出，adversary 在 `falsifiers[]` 把反向 path 写成 path-shaped（factors → mechanism → effect）而非一行 nitpick。
2. **多 factor contribution narrative（次高）** — `claims[]` 必须用 contribution 语言（`supports / amplifies / enables / counters`），避免 1-to-1 cause 语言（`X causes Y` / `if X then Y`）。承载位：drafter 在 `claims[]` 写 multi-factor 段落；adversary 攻击时也按 contribution 权重 rebalancing 而非 chain-topple。
3. **concurrent reverse path acknowledgement（中）** — 当反向 path 已经**部分 unfolding**（不只是未来 hypothetical），adversary 在 `notes` 末尾追加一行 `concurrent reverse path: <prose>`（在 verifier 的 `external verification:` 行之后）。reviewer Layer 0 检查 6/7 强制此行存在。

不做的部分（避免边际收益为负或为零的 over-engineering）：
- 不强 enum 化 `effect_on_thesis` / factor `role` — enum 会把 nuance 压扁成几个固定标签
- 不强制 `falsifiers[]` 至少一条带 `falsify` 类型 — 会迫使 adversary 凑数稀释质量
- 不加 `current_intensity` / `scenario_weighting_note` 等 v1.6 候选字段 — 先在 prose 里跑，按 §8.5 的 trigger 升级

### 8.3 承载位映射（v1.5 schema 字段 ↔ narrative 责任）

| 字段（v1.5 schema） | 写入 agent | 应承载的 narrative |
|---|---|---|
| `claims[]` | drafter | multi-factor contribution prose；顺序 = 优先级；句长 = 信心强弱 |
| `key_dependencies[]` | drafter | load-bearing 因子；可预先点出"if 该 dependency 反向移动" |
| `probability_view` | drafter | hedging + ≥2 forward path 并列承载（不强行 base case 化） |
| `notes`（drafter 写） | drafter | single-source flag（强制） |
| `notes`（verifier 追加） | verifier | `external verification: (verified\|partial\|pending) – <prose>` 一行 |
| `notes`（adversary 追加） | adversary | 当反向 path 已 partially unfolding：`concurrent reverse path: <prose>` 一行 |
| `falsifiers[]` | adversary | path-shaped 反向路径（factors → mechanism → effect），非一行 nitpick |
| `counter_evidence_observed[]` | adversary | 已观察到的反向证据；可点出 contribution 权重 rebalancing |
| `scenario_triggers[]` | adversary | `{observable_data, threshold, direction, status}` 6 件套；不强制 reference factor.id |
| `next_review_trigger` | adversary | 单对象；prefer `event` / `catalyst` 优先 `time` |

### 8.4 reviewer 读到 → 通过 / 不通过 的判定

reviewer Layer 0 [`research-theme-report-reviewer/SKILL.md §Layer 0`](../.cursor/skills/research-theme-report-reviewer/SKILL.md) check 6 / 7 把这套 narrative 责任落成读时检查：

- check 6（reverse path not buried）：`falsifiers[]` 全是 one-line nitpick → fail；至少一条 path-shaped → pass
- check 7（concurrent reverse path acknowledgement）：当 `scenario_triggers[*].status` ∈ `{triggered, reverse_triggered}` 或 `counter_evidence_observed[]` 非空且重要 → `notes` 必须含 `concurrent reverse path:` 行；缺 → fail

两条都路由 `root_cause: thesis_structure`，不路由 `package` / `writing`；责任 agent 多数情况是 `research-thesis-adversary`（path-shaped 反向 + concurrent acknowledgement）；少数情况是 `research-thesis-drafter`（drafter 没在 `key_dependencies[]` / `probability_view` 里点出反向 path 候选，导致 adversary 没源材料）。

### 8.5 什么时候才升 v1.6 加字段

下列任一 trigger 满足即可启动 v1.6 讨论。未达 trigger 之前，**v1.5 prose 形式即契约**；reviewer 与 maintainer 按 prose 读判，不期待新字段出现。

- **trigger A — reviewer 反复无法机审**：连续 3+ 个 review pass 中，Layer 0 check 6 / 7 因为 prose 散落在多字段里抓不到关键判据被 manual override，就考虑把 `scenarios[]` 升级为结构化对象数组（每个 scenario 自带 `narrative` + `effect_on_thesis` + `current_intensity` + `trigger_signals[]`），让 check 6 / 7 变成 schema 级 invariant。
- **trigger B — adversary 反复漏写**：连续 3+ 个 adversary pass 中，`notes` 缺 `concurrent reverse path:` 行被 reviewer 反弹，就考虑把这一行升级为顶层字段 `scenario_weighting_note: str` 让 L1 schema 强制存在 + 长度。
- **trigger C — bootstrapper 跨 thesis overlap 颗粒度不够**：bootstrapper 5-维 similarity 因为 contributing factor 散在 `claims[]` prose 里抓不到，需要把 contributing_factors 显式抽出来，那时考虑 `contributing_factors: [{factor: str, role: str}]` 顶层字段。
- **trigger D — content-maintainer 反复无法承载**：写 PM-facing 报告时多 path 并列 / concurrent reverse path 反复在 prose 里被 maintainer 误读 / 漏读，那时考虑把 v1.5 prose 形式升级为更显式的 schema 对象。

### 8.6 inline source ref convention — `[refs: i, j]`（v1.5 prose carrier）

v1.5 schema 把 `claims[]` 与 `counter_evidence_observed[]` 都定义为 `array of strings`。reader（PM、research-theme-report-reviewer、research-theme-knowledge-and-package-curator）单看一条 claim prose 时无法回答「这条 claim 站在 source_research_ids[] 的哪几条上」——必须重读全部 source 反推。这是真正的 reader gain 落差，但 v1.5 仍走 prose carrier 路径解决，理由：(a) 不动 schema 不破坏 27 fixture / validator / diff guard / builder；(b) `source_research_ids[]` 已是稳定 1-based 有序数组（verifier 只允许 append、不允许 reorder/delete）→ 在 prose 里贴 1-based index 已能精确回查；(c) 真正不够时按 §8.5 trigger 升 v1.6（候选字段 `claims[*].source_refs[]` + `counter_evidence_observed[*].source_refs[]`）。

**convention 定义**：

| 字段 | 是否必加 `[refs: …]` | 1-based 取值范围 | 责任 agent |
|---|---|---|---|
| `claims[]` | **必加** | `1..len(source_research_ids)` | drafter |
| `counter_evidence_observed[]` | **必加** | `0..len(source_research_ids)`（`0` = adversary 自有观察） | adversary |
| `key_dependencies[]` | 选加 | `1..len(source_research_ids)` | drafter |
| `falsifiers[]` | 选加（forward-looking 假设通常无单一 cite） | `1..len(source_research_ids)` | adversary |
| `probability_view` | **禁加**（综合判断字段，非 source-anchored） | — | drafter |

**写入位置**：prose 句末，单空格前导，句号在 `[` 之前，例如 `... neither alone is sufficient. [refs: 1, 4]`。

**Reader gain（PM 视角）**：PM 读一条 claim 立刻知道「此条来自 source_research_ids[1] (Capital Flows 4/10) 与 [4] (FRED DGS1)」，scroll 到 source 列表对应位置即可回查具体出处；不再需要全文重读。

**Reader gain（research-theme-knowledge-and-package-curator 视角）**：渲染报告时把 `[refs: …]` 转成 footnote 标记 `[1][4]` 并在文末加 `## Sources` 块——正文保持干净 analyst prose，PM 仍可逐句溯源。详见 [`research-theme-knowledge-and-package-curator SKILL §Inline source ref tags`](../.cursor/skills/research-theme-knowledge-and-package-curator/SKILL.md)。

**Reader gain（reviewer 视角）**：Layer 0 check 8 验证 `claims[]` 与 `counter_evidence_observed[]` 是否带 `[refs: …]`、index 是否 in-range。缺 ref / out-of-range / 非数字 → `root_cause: thesis_structure`，路由回责任 agent（drafter for claims，adversary for counter-evidence）。详见 [`research-theme-report-reviewer SKILL Layer 0 check 8`](../.cursor/skills/research-theme-report-reviewer/SKILL.md)。

**v1.6 升级 trigger（§8.5 体系内追加 trigger E）**：
- **trigger E — inline ref prose carrier 反复出错**：连续 3+ 个 review pass 中 Layer 0 check 8 因为「claim 写了 ref 但与实际 source 内容不匹配 / out-of-range / drafter 拼写错误」反弹；或 maintainer 在渲染 footnote 时反复需要 manual fix——则把 `claims[*]` 与 `counter_evidence_observed[*]` 升级为结构化对象 `{text: str, source_refs: [str]}`（`source_refs` 直接装 `source_research_ids` 中的 string id 而非 index，避免位置漂移），让 L1 schema 强制存在性 + 引用合法性。

### 8.7 与 v5.4 §3.5 Scenario object 的对账

v5.4 §3.5 把 Scenario 视作独立顶层对象，含 base / bull / bear / tail 四条 categorical 路径，每条带 `narrative` + `trigger_signals` + `basket_adjustment_plan`。v1.5 不采用这套结构，差异如下：

| v5.4 §3.5 | v1.5 + 本节 narrative 约定 |
|---|---|
| scenario 默认互斥（base / bull / bear / tail 四选一） | 多 scenario 可并列 unfold；prose 描述各自当前强度 |
| scenario 数量固定四条 categorical | 数量按 thesis 实际语义复杂度 emerge，不规定上下限 |
| `basket_adjustment_plan` 内嵌于 scenario | basket / 仓位调整属 `operation-portfolio-decision` SKILL 职责，thesis_note 不承载 |

即 v1.5 + narrative 约定**比 v5.4 更软**（不强 categorical 数量与互斥），**比 v1 更紧**（多 path / 多 factor / 反向 path 在 prose 内必须可见）。

---

## 9. Changelog

- 2026-04-19 v0.4 — §8.6 新增 inline source ref convention `[refs: i, j]`：1-based index 进 `source_research_ids[]`；`claims[]` / `counter_evidence_observed[]` 必加（counter-evidence 接受 `0` = adversary 自有观察）；`key_dependencies[]` / `falsifiers[]` 选加；`probability_view` 禁加。映射到 4 份 SKILL（[`research-thesis-drafter §Inline source ref convention`](../.cursor/skills/research-thesis-drafter/SKILL.md) / [`research-thesis-adversary §Inline source ref convention`](../.cursor/skills/research-thesis-adversary/SKILL.md) / [`research-theme-report-reviewer Layer 0 check 8`](../.cursor/skills/research-theme-report-reviewer/SKILL.md) / [`research-theme-knowledge-and-package-curator §Inline source ref tags`](../.cursor/skills/research-theme-knowledge-and-package-curator/SKILL.md)：strip 后转 footnote `[1][4]` + `## Sources` 块）；§8.5 trigger 体系追加 trigger E（连续反弹 → 升 v1.6 结构化 `claims[*].source_refs[]`）；原 §8.6 v5.4 对账下移到 §8.7。schema 文件 / 27 fixture 不动。
- 2026-04-19 v0.3 — 新增 §8 narrative 形态约定：v1.5 schema 不新增字段，已有 prose 字段（`claims[]` / `key_dependencies[]` / `probability_view` / `notes` / `falsifiers[]` / `counter_evidence_observed[]`）承载 multi-factor contribution / 多 path 并列 / concurrent reverse path 三件事；映射到 4 份 SKILL（[`research-thesis-drafter §Narrative Shape`](../.cursor/skills/research-thesis-drafter/SKILL.md) / [`research-thesis-adversary §Adversarial Shape`](../.cursor/skills/research-thesis-adversary/SKILL.md) / [`research-theme-report-reviewer §Layer 0 check 6-7`](../.cursor/skills/research-theme-report-reviewer/SKILL.md) / [`research-theme-knowledge-and-package-curator §Carrying thesis narrative shape into the report`](../.cursor/skills/research-theme-knowledge-and-package-curator/SKILL.md)）；定义 v1.6 升级的 4 个 trigger 条件；与 v5.4 §3.5 Scenario object 的对账。§0.2 reader 引导、§3 顶部加 §8 跳转。schema 文件 / 27 fixture 不动。
- 2026-04-19 v0.2 — 同步 cluster v0.4 review 修正：(F5 / T11) 时间字段统一 `_utc` 后缀；(F6 / V04) `theme_candidates/<scan_id>.json` 加 `scanned_window_utc` 顶层字段约定；(F8 / X05) `bootstrapper_proposal.json` schema 引到 [`research_05 §2.5.3`](research_50_thesis_and_theme_agent_cluster.md#253-bootstrapper_proposaljson-输出-schemaf8--x05) + 加 `bootstrapper_proposal.summary.md` 减负 PM 阅读；(F3 / M05) 撤销 `parent_theme_id` / `is_overlay` 字段（subordinate B5 已改为 raise 不落 metadata）；(F7 / V01) `bootstrap_arbitration_decision` 加 `pm_explicit_confirm` + `pm_chat_message_id`；(F13 / Rule 42) 新增 §5.7 显式声明 thesis_note 不在 artifact_graph 内、cluster 不需要 emit-sidecar。
- 2026-04-19 v0.1 — 首版。Plan B Phase B-(-1) 产物。把 v1 事实标准首次写下来；定义 v1.5 = 5 新 + 2 改名 + 8 撤销；下游影响清单 + lazy migration 步骤。
