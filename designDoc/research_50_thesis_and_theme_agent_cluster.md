# Thesis & Theme Analyst Agent Cluster

**Status**: active main design doc for the thesis/theme writing pipeline (Plan B §2.1 spec)
**First written**: 2026-04-19
**Owner**: trading_platform / research memory layer
**Sibling spec**: [`research_40_thesis_note_schema_v1_5.md`](research_40_thesis_note_schema_v1_5.md) — the shared object model the cluster reads/writes
**Plan source**: [`designDoc/ideas/thesis_and_theme_writing_pipeline_reorg.md`](ideas/thesis_and_theme_writing_pipeline_reorg.md)（Plan B §1, §2.1, §3）

---

## 0. 文档地位与读者引导

### 0.1 这是什么

仓库里所有「**建立** thesis / **建立** theme」类工作过去由 ad-hoc Cursor 对话完成。本 doc 把这条线规范成 **5 个独立 SKILL agent + 1 套共享 object model**，称为 `thesis-and-theme analyst cluster`。

它**不是**：

- 一个常驻的 Python orchestrator（不引入 AutoGen / LangGraph 引擎）
- 一个新的报告生成器（报告生成仍由 `research-theme-knowledge-and-package-curator` + DS writer + `research-theme-report-reviewer` 闭环负责）
- 一个 thesis library 服务（不做对外发布；不做 thesis 排行榜；不做激励机制）

它**是**：

- 一组 SKILL.md（5 份），每份独立 system prompt + 独立 tool 集合
- 一份共享 schema（`thesis_note v1.5`，见 [`research_06_*`](research_40_thesis_note_schema_v1_5.md)）
- agent 之间通过 v1.5 JSON 字段交接，**不传 chat 上下文**
- 由现有 controller skill（`routing-task-mode-router` + `research-theme-report-owner`）按需触发，**非常驻**

### 0.2 读者使用方式

- 想知道 cluster 里有哪些 agent / 各自责任：读 §2
- 想知道 agent 之间怎么交接 / 失败了怎么处理：读 §3 + §4
- 想知道 cluster 与上游 / 下游 controller 的边界：读 §5
- 想知道哪些事 cluster **不**做（避免误用）：读 §6
- 想跑测试：读 [Plan B §4](ideas/thesis_and_theme_writing_pipeline_reorg.md#4-phase-b-05-per-agent-独立测试generic-fixtures--golden-file-live-diff)

### 0.3 为什么要 cluster 化

旧 ad-hoc 路径有三个反复出现的 fail mode：

- **persona 混杂**：同一段 chat 里既起草、又验证、又找反例 → 自我审查偏弱（adversary 不彻底）、外部数字不查（verifier 缺位）、概率 inflation（drafter 写「高确信」自己却没列 falsifier）
- **schema 漂移**：每次手写 thesis_note 字段集略不同；下游 builder / reviewer 拿到不一致的字段集
- **theme bootstrap 没有结构**：新主题在 chat 里被随手命名，scope_boundary 经常缺失，导致后续主题间相互蹭 thesis（典型：AI capex thesis 错挂在 Hormuz 下）

cluster 化用「**persona 独立 + 共享 object 不共享 prompt**」直接修这三件事。

---

## 1. Cluster 边界

### 1.1 Cluster 内（5 个 agent）

- `research-thesis-drafter` — researcher persona，把 raw research 拆成 thesis_note v1.5 主体 prose
- `research-thesis-verifier` — external fact checker persona，对 drafter 写的关键数字 / 因果做外部三角验证
- `research-thesis-adversary` — critic / pre-mortem persona，写 falsifiers + scenario_triggers + counter_evidence_observed
- `research-theme-discovery-scanner` — archive scanner persona，bottom-up 扫 `data/research/messages_index.jsonl`，按 window / source_collection / theme_tag 聚类，把成簇但**未被现有 theme admit** 的 message group 提成 theme candidate 清单（≥3 message 才算簇），handoff 给 PM 审
- `research-theme-bootstrapper` — similarity-and-negotiation orchestrator + executor 双段 persona。**接收**第一次 owner 决策（"值不值得开"），统一对全 themes 库做相似度仲裁，给出 5 种 negotiation 方案（admit_as_independent / merge_into / narrow_self / carve_out_from / subordinate_to），写 proposal 让 owner 做**第二次决策**；按二次决策走 5 条互斥执行分支落盘并触发 seed thesis cluster。**任何 theme 创建意图都必经 Stage A 仲裁**（即便 PM 在 chat 里说"直接开吧"也不可跳过）

### 1.1.1 三个 theme 入口与 cluster 路径映射

| 入口 | 来源 | 入口 controller | 路径 |
|---|---|---|---|
| **#1 PM-driven** | PM 明确「开个新 theme X」 | `routing-task-mode-router` → `research-theme-report-owner` (`pass_type = seed_theme_brief`) | owner round-1 写「值不值得开」+ framing brief → `research-theme-bootstrapper` Stage A 全库仲裁写 proposal → owner round-2 选 negotiation 方案 → `research-theme-bootstrapper` Stage B 按方案落盘 + 触发 seed thesis cluster |
| **#2 AI bottom-up** | AI / PM 触发对 archive 做扫描 | `routing-task-mode-router` → `research-theme-discovery-scanner` | scanner 输出 candidate 清单（不直接落 theme 文件）→ PM 审 → 选某条 → 转 `research-theme-report-owner` (`pass_type = seed_theme_brief`) → 同 #1 后段（同样必经 bootstrapper Stage A 仲裁，scanner 的 nearest_existing_themes 只是初筛 sanity check，不替代 Stage A 细仲裁） |
| **#3 update existing** | PM 拿已有 theme 来更新 | `routing-task-mode-router` → `research-theme-report-owner` (`report_refresh / report_delta_scan / report_gap_review / theme_candidate_discovery`) | owner → `research-theme-knowledge-and-package-curator` → `writer-handoff` → `research-theme-report-reviewer` → `research-theme-priority-updater`，**不**进 cluster（除非该 update pass 决定要新建 thesis，再调 thesis 子 cluster；新建 thesis 不经 bootstrapper，因为 theme 已存在不是 theme-level 操作） |

> **责任边界**：
> - `research-theme-discovery-scanner` 不决定 theme 是否要开，只产 candidate（PM 审）；nearest_existing_themes 是粗筛 sanity check
> - `research-theme-report-owner` round-1 决定 theme 是否值得开（high-level "yes/no"）+ 写 framing brief；round-2 在看完 bootstrapper proposal 后做 informed 选择（5 种 negotiation 方案之一）
> - `research-theme-bootstrapper` 是 orchestrator + executor：Stage A 全库相似度仲裁 + 写 proposal（**必经，对所有 #1 #2 入口统一执行**）；Stage B 按 owner round-2 决策走 5 条互斥执行分支
> - 三类决策的责任被显式分离，避免「owner 要既扫库又决策」或「bootstrapper 自作主张」

每个 agent 一个 `.cursor/skills/<agent_id>/SKILL.md`，独立的 `Current persona / Current task / Primary truth surface / Output artifact / Self-test` 段（按 [`rule 20`](../.cursor/rules/20_daily_task_router_and_skill_persona.mdc)）。

### 1.2 Cluster 外（不属于本 doc）

- `routing-task-mode-router` — 上游路由，决定何时进入 cluster
- `research-theme-report-owner` — 上游 controller，决定本轮 theme 是否需要新建 thesis / 新建 theme，触发对应 cluster agent
- `research-theme-knowledge-and-package-curator` — 下游 controller，把 cluster 产出的 thesis 引用进报告
- `writer-handoff` — 下游 package 评审 gate
- `research-theme-report-reviewer` — 下游 review gate（[`Plan B §5.2`](ideas/thesis_and_theme_writing_pipeline_reorg.md#52-reviewer-最小升级) 给它加一节 thesis structural readiness 节，**真消费** v1.5 新字段）
- `research-theme-priority-updater` — 平行 controller，处理优先级路由（[`Plan B §3.5`](ideas/thesis_and_theme_writing_pipeline_reorg.md#35-升级最小改动) 给它加 `cross-theme thesis link role` 节）

### 1.3 共享 object model

- `thesis_note v1.5` schema（见 [`research_06`](research_40_thesis_note_schema_v1_5.md)）—— cluster 所有 agent 读写的核心对象
- `data/research/themes/metadata/<theme_id>.json` —— theme metadata，bootstrapper 写、其它 agent 通过 `cross_theme_links[].theme_id` 引用
- `data/research/source_collections.json` —— source-family 路由，bootstrapper 在 source-collection routing 步骤读它
- [`data/runtime/artifact_graph.yaml`](../data/runtime/artifact_graph.yaml) `theme.*` 节点 —— 下游消费侧的入账点（cluster 产出 thesis 后，包装/审报告通过 graph 入账）

---

## 2. Agent Roster（详细责任 / 输入 / 输出）

### 2.1 research-thesis-drafter

| 维度 | 内容 |
|---|---|
| persona | 拆 claim 的 researcher |
| 输入 | raw research 段落（来自 `data/research/messages/<rid>/`）/ 1 个 `theme_id` 或 `theme_intent` prose / 上游 `routing-task-mode-router` 给的写作目标 |
| 工具 | 文件读、grep、本地索引；**不**调外部 API |
| 必填输出（v1.5 prose 主体） | `claims[]` 按重要性排序 / `key_dependencies[]` / `probability_view` / `cross_theme_links[]` 含 role / `lifecycle_stage = "draft"` / `source_research_ids[]` ≥2（三角依据） |
| **不**允许 | 写 `falsifiers[]` / `scenario_triggers[].status` / 在 `notes` 写 `external verification:` 行（这些留给下游 agent）/ 写 `confidence_estimate: float`（v1.5 显式撤销） |
| 失败模式 | 输入只有 1 个 source_research_id → drafter 在 `notes` 写 `single source – verifier 必须扩源`，标记 lifecycle 仍是 draft |

### 2.2 research-thesis-verifier

| 维度 | 内容 |
|---|---|
| persona | external fact checker |
| 输入 | drafter 写完的 thesis_note v1.5 JSON（只读） |
| 工具 | Perplexity（首选） / web fetch / 本地数据库（如已有 series 可对照） |
| 必填输出 | 在 `notes` 末尾追加一行 `external verification: <verified \| partial \| pending> – <一句>`；在 `source_research_ids[]` 追加外部验证到的 source_id；**不**新增 enum 字段 |
| **不**允许 | 改 drafter 写的 prose；改 `lifecycle_stage`；写 falsifiers |
| 失败模式 | 外部数据全拿不到 → 写 `external verification: pending – <reason>`，**不**阻塞下游 adversary；reviewer 后续会列 minor finding |

> **为什么不引入 `evidence_strength` enum**：[`Plan B §1.2`](ideas/thesis_and_theme_writing_pipeline_reorg.md#12-上一轮外部-macro-analyst-skill-调研) 决定用一句 prose 替代 enum。enum 会被 LLM 学成「都标 verified」的均值塌陷；prose 强迫写「verified what / pending what」，自带 hedging。

### 2.3 research-thesis-adversary

| 维度 | 内容 |
|---|---|
| persona | critic / pre-mortem |
| 输入 | drafter + verifier 写完的 thesis_note v1.5 |
| 工具 | 文件读 / grep / 必要时调 Perplexity 找反例 |
| 必填输出 | `counter_evidence_observed[]` prose（与 drafter 的 `claims[]` 对应反位） / `falsifiers[]` ≥1 / `scenario_triggers[]` 含 `status: pending` / `next_review_trigger: {kind, value}` |
| 强制 | `falsifiers[].length >= 1`，空 → raise 让 PM 补 |
| Lifecycle 升级 | `draft → active`（adversary 是唯一升 lifecycle 到 active 的 agent） |
| **不**允许 | 写 `confidence_estimate: float`；改 drafter 的 prose；改 verifier 的 notes 行 |
| 失败模式 | 找不到反例 → 强制声明 `single-perspective risk: <一句>` 到 `notes`，禁止留空 falsifiers |

### 2.4 research-theme-discovery-scanner

| 维度 | 内容 |
|---|---|
| persona | archive scanner / candidate proposer |
| 输入 | `time_window` 必须含**显式时间锚**：`{anchor_kind: "wall_clock" \| "as_of_utc", as_of_utc: "<ISO8601 UTC>", lookback_days: int}`（F6 / V04，**不**允许 PM 只说"最近一个月"，PM 必须明确 `as_of_utc` 是 wall clock 还是某个固定基准）+ 可选 `source_collection_filter` + 现有 `data/research/themes/metadata/*.json` 全集（用作去重） |
| 工具 | 读 `data/research/messages_index.jsonl` 全扫 / grep / 文件读；**不**调外部 API |
| 步骤 | 1) Window scan：截 `[as_of_utc - lookback_days, as_of_utc]` 内所有 message 候选 → 2) Cluster：按 `theme_tag` / `sender_name` / `source_collection` / 关键 ticker 多维聚类 → 3) 去重：剔除已被任一现有 `themes/metadata/*.linked_research_ids[]` admit 的 message → 4) 候选筛选：保留 ≥3 message 且 ≥2 个独立 source 的簇 → 5) 对每个候选写 candidate brief：proposed_id_suggestion / proposed_scope_one_line / evidence_cluster (含 message_id 列表) / nearest_existing_themes (≥2) / recommended_candidate_level (`adjacent / thesis_only / regional / industry / top_level`) / why_not_existing_theme → 6) handoff 给 PM 审 |
| 必填输出 | `data/research/theme_candidates/<scan_id>.json`（含顶层 `scanned_window_utc: {as_of_utc, lookback_days, anchor_kind, scanner_invoked_at_utc}` 字段，F6 / V04 / T11，scan_id = `discovery_<as_of_utc>`）+ `data/research/theme_candidates/<scan_id>.md`（PM-readable summary） |
| **不**允许 | 直接写 `themes/metadata/*.json`（不建 theme 文件）；直接调 `research-theme-bootstrapper`（必须 PM 审过）；把候选数膨胀（一次 scan 输出 ≤5 候选）；省略 `scanned_window_utc`（若 PM 没给 `as_of_utc` → raise `missing_temporal_anchor`，**不**默认用 wall clock，F6 / V04） |
| 失败模式 | window 内 ≥3 message 簇不存在 → 输出空清单 + 一句 `no eligible cluster found in window <as_of_utc - lookback_days .. as_of_utc>`，**不**强行造候选；`as_of_utc` 缺失 → raise `missing_temporal_anchor` |
| 触发频率 | 本轮**不做**定期 cron；由 PM 在 chat 里手动触发并显式给 `as_of_utc`（典型："以 2026-04-19T00:00:00Z 为基准回看 30 天"） |

### 2.5 research-theme-bootstrapper

> **Reader gain (F12 / Rule 36)**：读完 §2.5 + §2.5.1-§2.5.6 后 agent 应能 (a) 区分 5 种 negotiation 方案各自的判定条件与对应执行体；(b) 区分 Stage A 与 Stage B 的责任、输入、输出与隔离边界（Stage B **不**能看 Stage A proposal）；(c) 知道何时必须等 owner round-2 而非自己决定；(d) 知道哪个分支必须先 dry-run；(e) 区分哪些 5 维分数由 deterministic 工具预计算、哪些由 LLM 语义判断；(f) 知道 thesis_note 当前**不在** artifact_graph 内、本 cluster 不需要 emit-sidecar。

| 维度 | 内容 |
|---|---|
| persona | similarity-and-negotiation orchestrator + executor（双段） |
| 触发前提 | 一份**第一次 owner 决策**已就位（来自 `research-theme-report-owner` 的 `seed_theme_brief` pass），即 `data/research/theme_update_drafts/<theme_id>.owner.json` 已写好 reader_end_state + scope_intent + framing brief。Owner 第一次决策只回答 high-level "值不值得开"，**不**承担全库扫库与冲突分析。 |
| 输入（Stage A，**已预处理**） | (1) owner.json round-1 字段；(2) 拟用 `theme_id`；(3) `themes/metadata/*.json` 全集的**精简切片**（每个邻居只送 6 字段：`theme_id / scope_boundary.IS / linked_research_ids_count / source_collection / theme_tag / primary_assets`，**不**送完整 metadata 进 prompt，F2 / A14）；(4) `precomputed_overlap_scores`（5 维中 3 维由 harness 预计算好，见 §2.5.4 / F1 / T10）；(5) 若来自 #2 入口则附 candidate.evidence_cluster |
| 输入（Stage B，**严格隔离**，F4 / T03） | (1) owner.json round-2 字段（`bootstrap_arbitration_decision`）；(2) 现有 themes/metadata 全集精简切片（同 Stage A）；(3) 必要时 candidate evidence_cluster。**不送** Stage A 的 `bootstrapper_proposal.json` 全文（避免 Stage B "知道 Stage A 是怎么想的"，破坏上下文隔离） |
| 工具 | 文件读 / 文件写 / `data/research/source_collections.json` 读写 / harness 内的 deterministic 5 维分数预处理脚本 |
| **Stage A 步骤** | A1) harness 加载 `themes/metadata/*.json` 全集并切片成 6 字段精简形式（`theme_id / scope_boundary.IS / linked_research_ids_count / source_collection / theme_tag / primary_assets`，**不**送完整 metadata 进 prompt，F2 / A14） → **A2-deterministic** harness 预计算 3 维分数（`linked_research_ids_overlap` 集合交集 / `source_collection_overlap` Jaccard / `theme_tag_overlap` Jaccard）写入 `precomputed_overlap_scores`（F1 / T10 强约束，见 §2.5.4） → **A2-llm** LLM 在 invocation 内只判 2 维语义分数（`scope_is_semantic_overlap` / `asset_focus_semantic_overlap`） + 综合 5 维出推荐方案 → A3) 取 top-N 邻居（N=5，合成方式由 LLM 在 `synthesis_narrative` 字段说明，本 plan **不**预设硬合成公式） → A4) 对每个高分邻居判定**冲突类型** + 推荐 5 种 negotiation 方案之一（§2.5.1） → A5) 写 `bootstrapper_proposal.json`（schema §2.5.3）+ `bootstrapper_proposal.summary.md`（≤30 行 PM-readable 摘要） → A6) handoff 回 `research-theme-report-owner`，**block** 等 owner round-2 |
| **Stage B 步骤** | B1-B5 五条互斥分支，详见 §2.5.5。所有分支结束后统一 handoff 给 `research-theme-report-owner` + `research-theme-priority-updater`。 |
| 必填输出 | Stage A：`bootstrapper_proposal.json`（schema §2.5.3）+ `bootstrapper_proposal.summary.md`。Stage B（按决策不同）：见 §2.5.5 |
| **不**允许 | 跳过 Stage A 直接落盘（即便 PM 说"直接开吧"也必须先扫一遍写 proposal）；自己做 round-1 / round-2 决策；让 LLM 重算 3 维 deterministic 分数（F1 / T10）；送整 metadata 全文进 prompt（F2 / A14）；**Stage B 拿 Stage A proposal 当 context**（F4 / T03，Stage B input 严格只含 owner.json round-2 + themes/metadata 精简切片 + 必要时 candidate evidence）；执行 `carve_out_from` 时不写 dry-run diff；Stage B B5 subordinate 落任何 metadata 文件（F3 / M05，本轮直接 raise，见 §2.5.5 B5）；scope_boundary 不写 IS_NOT；seed thesis < 3（除 B5 raise 路径） |
| 失败模式 | owner.json round-1 未就位 → raise `missing_owner_decision_round1`；Stage A 邻居全库为空 → proposal 写「无邻居约束」并推荐 `admit_as_independent`，仍等 owner round-2 confirm（保流程一致）；Stage A 跑出 ≥3 个 high-overlap 邻居 → proposal 必须**显式推荐** merge 或 narrow 作为 primary，禁止默认推 admit_as_independent；owner round-2 缺字段 → raise `missing_owner_decision_round2`；owner round-2 缺 `pm_explicit_confirm: true` → raise `missing_pm_confirmation_round2`（F7 / V01）；Stage B `carve_out_from` PM 不 confirm dry-run → raise `pending_pm_confirmation_carve_out`；Stage B `subordinate_to` 调用 → raise `subordinate_executor_not_implemented`（F3 / M05，**不**落任何 metadata 文件，提示 PM 改 round-2 决策为 `admit_as_independent` 或 `narrow_self_to`，并在 owner.json `notes` 标 `subordinate_pending_future_plan` 留 follow-up）|

### 2.5.1 冲突类型 → 协商方案对照表（Stage A4 用）

| 冲突类型 | 判定条件（粗，dogfood 后调） | 推荐 negotiation 方案 |
|---|---|---|
| `full_overlap` | `scope_is_semantic_overlap` ≥0.70 **或** `linked_research_ids_overlap` ≥0.50 | `merge_into:<existing_theme_id>` |
| `partial_overlap_self_should_narrow` | 邻居先存在且 scope 更广，新 theme 大部分被邻居覆盖 | `narrow_self_to:<scope_subset>` |
| `partial_overlap_neighbor_should_carve_out` | 新 theme scope 集中且证据更新，邻居 scope 已含但论述薄弱 | `carve_out_from:<neighbor_theme_id>` |
| `subordinate_relationship` | 新 theme 是邻居的某条 thesis 维度 / 子叙事 / overlay | `subordinate_to:<parent_theme_id>`（**Stage B 本轮 raise 不实现**，见 §2.5.5 B5） |
| `boundary_clarification_only` | 多维分数均 < threshold，仅需互写 IS_NOT | `admit_as_independent` |

> 阈值（0.70 / 0.50）首版用启发式默认值；calibration trigger 见 [`Plan B §10`](ideas/thesis_and_theme_writing_pipeline_reorg.md#10-风险与缓解)（F10 / M01）。

### 2.5.2 owner round-2 决策字段（追加在 owner.json）

```json
{
  "bootstrap_arbitration_decision": {
    "kind": "admit_as_independent | merge_into | narrow_self_to | carve_out_from | subordinate_to",
    "target_theme_id": "<existing_theme_id>",         // merge / carve_out / subordinate 必填；其余 null
    "narrowed_scope_is": ["...", "..."],              // narrow_self_to 必填；其余 null
    "rationale": "<owner 一句话解释；若推翻 bootstrapper 推荐方案则以 [OVERRIDE] 前缀开头 (F10 calibration grep)>",
    "decided_at_utc": "<ISO8601 UTC>",                 // F5 / T11 时间字段统一 _utc 后缀
    "pm_explicit_confirm": true,                       // F7 / V01 责任不可委派；false / 缺失 → raise
    "pm_chat_message_id": "<chat msg id 或 PM 短描述>"  // F7 / V01 audit trail
  }
}
```

### 2.5.3 `bootstrapper_proposal.json` 输出 schema（F8 / X05）

```json
{
  "scan_target_theme_id": "<拟用 theme_id>",
  "scan_at_utc": "<ISO8601 UTC>",
  "neighbors_considered_count": 12,
  "per_neighbor": [
    {
      "neighbor_theme_id": "us-dollar-liquidity-plumbing",
      "dimension_scores": {
        "scope_is_semantic_overlap": 0.62,
        "linked_research_ids_overlap": 0.18,
        "source_collection_overlap": 0.40,
        "theme_tag_overlap": 0.33,
        "asset_focus_semantic_overlap": 0.25
      },
      "dimension_score_provenance": {
        "scope_is_semantic_overlap": "llm",
        "linked_research_ids_overlap": "deterministic",
        "source_collection_overlap": "deterministic",
        "theme_tag_overlap": "deterministic",
        "asset_focus_semantic_overlap": "llm"
      },
      "conflict_type": "partial_overlap_self_should_narrow",
      "recommended_negotiation_kind": "narrow_self_to",
      "narration": "<一句解释为什么本邻居判定为该冲突类型>"
    }
  ],
  "recommended_primary": {
    "kind": "narrow_self_to",
    "target_theme_id": "us-dollar-liquidity-plumbing",
    "synthesis_narrative": "<LLM 解释如何综合 5 维分数得到本推荐>"
  },
  "alternatives": [
    { "kind": "admit_as_independent", "rationale_one_line": "..." }
  ]
}
```

### 2.5.4 5 维分数 deterministic vs LLM 划分（F1 / T10 强约束）

| 维度 | 计算方 | 说明 |
|---|---|---|
| `linked_research_ids_overlap` | **harness 预计算** | Python set: `\| A ∩ B \| / max(\| A \|, \| B \|)`，全结构化 fact，禁止 LLM 重算 |
| `source_collection_overlap` | **harness 预计算** | tag set Jaccard，全结构化 fact |
| `theme_tag_overlap` | **harness 预计算** | tag set Jaccard，全结构化 fact |
| `scope_is_semantic_overlap` | LLM | 语义判断，不可 deterministic |
| `asset_focus_semantic_overlap` | LLM | 语义判断（"Mag7" vs "AI hyperscalers" 是否同义），不可 deterministic |

> 这是 [t10_index_first_ai_for_gaps](../09_soul/axioms/t10_index_first_ai_for_gaps.md) 的强落地：结构化 fact 由 deterministic 算，AI 只补语义缺口。harness 在 invoke LLM 前必须把 3 维分数算好写进 input；LLM 拿到的 input 已含 `precomputed_overlap_scores` 字段，**不许用 LLM 自己算这 3 维**。

### 2.5.5 Stage B 五条执行分支

- **B1 `admit_as_independent`**：抄 owner.reader_end_state / scope 落 `metadata/<theme_id>.json` → 邻居 IS_NOT referee（含 Stage A 已识别的 top-N 邻居，每个写一条「这件事归隔壁主题 X」）→ source-collection routing → 占位 report → 补完 owner.json `writer_direction[]` ≥6 条 → 触发 thesis cluster 建 ≥3 seed thesis
- **B2 `merge_into:<existing>`**：**不**建新 metadata；把 owner.json 的 reader_end_state / scope_intent 关键句作为 `merge_audit[]` 项（含 `merged_at_utc`）追加到现有 metadata；把 candidate evidence_cluster（来自 #2 入口）作为 raw 喂给 thesis cluster，**触发 ≥1 seed thesis** link 到现有 theme（"否则 candidate 的 evidence 没人接"）；归档 `theme_candidates/<scan_id>.json` 标 `consumed_by: <existing>` + `consumed_at_utc`
- **B3 `narrow_self_to:<scope>`**：用 owner round-2 给的 `narrowed_scope_is[]` 替换 owner.json 原 scope_intent 中冲突项 → 走 B1 流程；同时在被让出的邻居 metadata 写一条 `explicit_IS` 项（"这部分归我，因为新 theme 已让出"）
- **B4 `carve_out_from:<neighbor>`**：先**写 dry-run diff**（具体邻居 metadata 的哪些 IS 项要搬到新 theme / 哪些 linked_research_id 要重新归属），存 `bootstrapper_carve_out_diff.json` → handoff PM **在线 confirm**（block）→ confirm 后改邻居 metadata（含 `audit_trail[].changed_at_utc` + 反向 IS_NOT）→ 走 B1 流程
- **B5 `subordinate_to:<parent>`**：**raise `subordinate_executor_not_implemented`**（F3 / M05），**不**落任何 metadata 文件；返回提示给 owner："本轮 subordinate 执行体未实现，请改 round-2 决策为 `admit_as_independent`（独立开但 metadata `notes` 标 `subordinate_to_intent: <parent_theme_id>` 备忘）或 `narrow_self_to`（缩 scope 后独立）"；在 owner.json 加 `notes: "subordinate_pending_future_plan"` 留 follow-up

### 2.5.6 thesis_note 是否需要 graph emit-sidecar（F13 / Rule 42）

- 当前 [`data/runtime/artifact_graph.yaml`](../data/runtime/artifact_graph.yaml) **不含** `thesis_note` 节点
- 因此 cluster B1/B2/B3/B4 写 thesis_note 时**不**需要 emit-sidecar；Rule 42 只对 graph 里有节点的 L4 artifact 强制
- 若未来把 `thesis_note` 加进 graph（建议作为后续 plan 的事），cluster harness 必须同步加 `tradectl plan thesis_note --id <id> --emit-sidecar auto` 步骤；当前 spec 不强求

---

## 3. Message Contract（agent 之间怎么交接）

### 3.1 通过 JSON 字段交接，不传 chat 上下文

每个 agent 的输入是上游 agent 写完的 thesis_note v1.5 JSON 文件（或 raw research 段落），输出是同一个 JSON 文件的 in-place 写入。**不**通过 chat 上下文传递隐式约定。

理由：

- 让每个 agent 独立可测（[`Plan B §4`](ideas/thesis_and_theme_writing_pipeline_reorg.md#4-phase-b-05-per-agent-独立测试generic-fixtures--golden-file-live-diff) 的 fixture 就是手写一份「上游 agent 应当输出的样子」当作 input）
- 让 agent 失败时只重跑该 agent，不必重跑整条链
- 让 cluster 升级（替换某个 agent 的 SKILL prompt）时，下游 agent 的契约不破

### 3.2 Cluster 内顺序

- thesis 子 cluster：`drafter → verifier → adversary`（顺序不可调换；adversary 必须看到 verifier 的 notes 行才能判定 falsifier 强度）
- discovery-scanner 独立调度（不进 thesis 子 cluster），输出 candidate 清单后停在 PM 审这一步
- bootstrapper 独立调度但**自带 round-trip**：Stage A 写 proposal → block 等 owner round-2 → Stage B 落盘；Stage B 触发 thesis cluster（`drafter → verifier → adversary`）作为 callback
- bootstrapper 的 **Stage A 和 Stage B 输入严格隔离**（F4 / T03）：Stage B 的 input **不**包含 Stage A 的 `bootstrapper_proposal.json` 全文；Stage B 只看 owner round-2 决策 + themes/metadata 精简切片 + 必要时 candidate evidence_cluster。理由：避免 Stage B 因看到 Stage A 推荐而锚定，让 owner round-2 决策成为唯一权威输入
- 入口 → bootstrapper 的两条路径（#1 PM-driven / #2 PM 审过的 discovery candidate）最终都收敛到 owner_decision_round1，bootstrapper 只认 owner.json round-1 字段作为 Stage A 触发契约 + owner.json round-2 字段作为 Stage B 触发契约

### 3.3 字段写入约定（防止 cross-write）

下表说明每个字段的**写入责任 agent**，其它 agent 只读：

| 字段 | 写入 agent | 备注 |
|---|---|---|
| `claims[]` | drafter | adversary / verifier 不得改 |
| `key_dependencies[]` | drafter | 同上 |
| `probability_view` | drafter | 同上 |
| `cross_theme_links[]` | drafter（或 PM 后续手调） | 含 role |
| `lifecycle_stage` | drafter 写 `draft`；adversary 升 `active`；PM 后续可降 `evolving / invalidated / archived` |
| `source_research_ids[]` | drafter 初值；verifier 追加；adversary 追加（如查到反例 source） |
| `notes` | 三个 agent 都可追加，但 verifier 的 `external verification:` 行格式固定 |
| `counter_evidence_observed[]` | adversary | drafter / verifier 不得写 |
| `falsifiers[]` | adversary | 强制 ≥1 |
| `scenario_triggers[]` | adversary | drafter 不得写 |
| `next_review_trigger` | adversary | 单对象 |
| `expected_winners[] / expected_losers[]` | drafter 初值；adversary 可追加 hedge / 反位 ticker |

---

## 4. 运行时形态 + 失败模式

### 4.1 运行时形态

- cluster **非常驻**。PM 或 `research-theme-report-owner` 在需要时由 controller 触发对应 agent
- 顺序触发，不并发（共享 JSON 文件并发写有冲突风险）
- 每次触发一个 agent = 一次 Cursor SKILL invocation，独立 system prompt
- 不引入 Python 编排引擎；调度本身是 PM + controller 的人工 / SKILL 路由

### 4.2 失败模式与处置

| 失败 | 触发条件 | 处置 |
|---|---|---|
| drafter 输入只有 1 个 source | 数 `source_research_ids[].length` | drafter 标 `single source` 进 notes，verifier 必须扩源 |
| verifier 拿不到外部数据 | Perplexity / web 全失败 | notes 写 `external verification: pending`，不阻塞 adversary，reviewer 后续 minor finding |
| adversary 找不到反例 | adversary 自检 | 强制写 `single-perspective risk: <一句>` 到 notes；禁止留空 `falsifiers[]` |
| discovery-scanner window 内无 ≥3 message 簇 | scanner 自检 | 输出空清单 + 一句 `no eligible cluster found`，禁止强行造候选 |
| discovery-scanner 候选数 >5 | scanner 自检 | raise `cluster threshold too low`，要求 PM 收紧 source_collection_filter 或 window 重跑 |
| bootstrapper Stage A 被调用但 owner.json round-1 未就位 | bootstrapper 第一步 | raise `missing_owner_decision_round1`，不向后跑（路由错了，应当先去 owner） |
| bootstrapper Stage A 邻居主题为空（首个 theme） | 检查 themes/metadata 全集 | proposal 写「无邻居约束」+ 推荐 `admit_as_independent`，**仍然**等 owner round-2 confirm（保流程一致；不允许跳 round-2） |
| bootstrapper Stage A ≥3 个 high-overlap 邻居 | similarity 多 ≥3 个 hit threshold 邻居 | proposal 必须**显式推荐** `merge_into` 或 `narrow_self_to` 之一作为 primary，禁止默认推 `admit_as_independent` |
| bootstrapper Stage A LLM 试图自己计算 deterministic 三维分数 | harness self-check：input 已含 `precomputed_overlap_scores` 但 LLM 输出的对应 `dimension_score_provenance` 不是 "deterministic" | raise `llm_overrode_deterministic_score`（F1 / T10），让 SKILL prompt 收紧 |
| bootstrapper Stage B 被调用但 owner.json round-2 决策缺字段 | Stage B 第一步 | raise `missing_owner_decision_round2`，不向后跑 |
| bootstrapper Stage B 被调用但 owner.json round-2 缺 `pm_explicit_confirm: true` | Stage B 第一步 | raise `missing_pm_confirmation_round2`（F7 / V01），不向后跑 |
| bootstrapper Stage B input 含 `bootstrapper_proposal.json` 内容 | harness pre-flight check | raise `stage_b_context_leak`（F4 / T03），让 harness 收紧 input 边界 |
| bootstrapper Stage B `carve_out_from` 已写 dry-run diff 但 PM 未 confirm | Stage B B4 第二步 | raise `pending_pm_confirmation_carve_out`，不改邻居 metadata |
| bootstrapper Stage B `subordinate_to` 调用 | Stage B B5 | raise `subordinate_executor_not_implemented`（F3 / M05），**不**落任何 metadata 文件；提示 owner 改 round-2 决策为 `admit_as_independent` 或 `narrow_self_to`；在 owner.json 加 `notes: "subordinate_pending_future_plan"` |
| agent 想改不属于自己的字段 | SKILL 末尾 self-test assertion 强制 | 测试 fail，回 SKILL.md 收紧 prompt |
| cluster 内字段集与 v1.5 schema 漂移 | reviewer 加的 thesis structural readiness 节会查 | major finding，必须回 cluster 修 |

### 4.3 Agent 责任边界（继承 V5.4 §6.5）

- agent **永不**直接修改已被 theme metadata 引用的 thesis；只能产 vN+1 文件 + 请求 PM 合入
- agent **永不**改 `themes/reports/<theme_id>.md` 主报告（那是 `research-theme-knowledge-and-package-curator` 的领域）
- agent **永不**改 `data/runtime/artifact_graph.yaml`

### 4.4 四层强制层（4-layer enforcement architecture）

§4.2 把所有失败模式列了一张大表，但表里很多模式不该靠 agent 自检兑现。Cluster 的稳定性来自把硬规则**搬出 SKILL prose、搬进 deterministic code**。四层划分如下：

- **L1 — JSON Schema 强制**（已落地）
 - 文件：`data/runtime/schemas/*.schema.json`（4 份：`thesis_note_v1_5` / `bootstrapper_proposal` / `owner_round_2_decision` / `theme_candidate`）
 - 工具：`src/tools/thesis_cluster_validate.py`
 - CLI：`./.venv/bin/python -m src.cli.tradectl thesis-cluster validate <agent_id> <artifact_path>`
 - 兑现 §4.2 中："字段类型 / 枚举 / 正则 / 必填字段缺失 / lifecycle 派生字段必填 / `pm_explicit_confirm` 必须为 boolean true / `scan_id` 命名 / `composite_overlap_score` 与公式相等" 等
 - validator 还做 schema 表达不了的 business-extras："notes 中 `external verification:` 行最多一条 + 单源时 notes 必须含 `single source – verifier 必须扩源` 标记 + composite 五维加权与公式 1e-6 相等 + override 标志与 `[OVERRIDE]` 前缀一致"
- **L2 — Diff Guard**（与 L4 同一工具，待 Phase B-0.5 接入 fixture harness 后激活）
 - 用途：保证 verifier / adversary / Stage B 改动只动允许字段，其余字节相等
 - 现状：尚未独立成模块；harness 跑 fixture 时通过 `golden_output.json` 与 `last_run.json` 字节比较实现
- **L3 — Prompt Construction Harness**（部分待落地）
 - 用途：在工具侧物理过滤 LLM input 字段，避免 cluster 内任何 agent 误读它不该看的内容
 - 关键守护：
 - bootstrapper Stage A 邻居主题 input 必须只有 6 字段 slim slice（避免 A14 prompt 边界违例）
 - bootstrapper Stage A 三维 deterministic 分数必须由 harness 预计算后注入，LLM 不能自行赋值（T10）
 - bootstrapper Stage B input 必须**不**含 Stage A `bootstrapper_proposal.json` 任何字段（防 `stage_b_context_leak` / T03）
 - 现状：harness 设计在 §3 Message Contract 已定义；具体 Python 实现随 Phase B-0.5 fixture harness 一并交付
- **L4 — Pre-condition Gate**（已落地）
 - 文件：`src/tools/thesis_cluster_router.py::can_run(agent_id, input_payload, *, context=None)`
 - CLI：`./.venv/bin/python -m src.cli.tradectl thesis-cluster gate <agent_id> <input_path>`
 - 兑现 §4.2 中："verifier 输入 lifecycle 必须为 draft 且 notes 不含已有 verification 行 / adversary 输入 lifecycle 必须为 draft 且 notes 已含 verification 行 / scanner 必须显式 `as_of_utc` 不允许默认 now() / Stage A 必须 `round_1_verdict = worth_arbitrating_via_bootstrapper` / Stage B 必须 `pm_explicit_confirm: true` 且 `pm_chat_message_id` / Stage B `subordinate_to_existing` 直接 raise / Stage B `carve_out` 两阶段约束（已有 diff 文件就强制走 `_confirmed`）"

#### 4.4.1 强制层 vs SKILL 自检的分工

每份 cluster SKILL 在 `## Failure Signals` 段都改写为两栏：

- **Caught deterministically (do not waste tokens self-checking)**：列举具体哪些规则被 L1 / L4 拦下、并给出对应 CLI 命令；agent 不需要自检这些
- **Self-check (LLM judgment, not catchable by validator)**：剩下 LLM 必须自我判断的语义层（"是 IS_NOT 边界写得清楚吗" / "是 falsifier 真的可证伪还是循环论证" / "scenario_trigger 的 observable_data 是真机器可观测还是包了一层主观词"）

这套分工把 SKILL prose 从「写齐所有硬规则」松开成「写齐语义判断」，硬规则迁到 schema + router；schema + router 失败时直接 exit non-zero、CLI 输出可读 reason，attribution 也比 LLM 自检失败清晰得多。

#### 4.4.2 与 §4.2 失败模式表的映射

§4.2 表里仍保留所有失败模式的人类可读描述，但每条已可在工程层面定位到 L1 / L2 / L3 / L4 中的某一层：

- L1（schema + business extras）覆盖：lifecycle 派生字段缺失 / 字段类型 / 正则 / `composite` 公式 / `[OVERRIDE]` 一致性 / 单源 notes 标志 / 验证行重复
- L4（pre-condition gate）覆盖：verifier on non-draft / adversary 在 verifier 之前跑 / scanner 缺时间锚 / Stage A 没有 owner round-1 verdict / Stage B 缺 pm_confirm / Stage B 收到 subordinate / Stage B carve_out 两阶段错位
- L3（harness）覆盖：A14 prompt 边界（slim slice）/ T10 deterministic 分数注入 / T03 Stage B 上下文隔离
- L2（diff guard）覆盖：verifier / adversary / Stage B 越权改动上游字段（在 Phase B-0.5 fixture harness 阶段统一兑现）
- 仅 SKILL self-check：scenario_trigger 是否真机器可观测、falsifier 是否真可证伪、命名 slug 是否描述性、邻居 IS_NOT 实际语义贴合度、theme_id 文件是否已存在（collision check）

### 4.5 themes/metadata v1.5 lazy migration（cluster 假设字段的工程化落地）

cluster 设计依赖 `research-theme-bootstrapper` Stage A 在 5 个相似性维度上做评分，其中 3 个维度（`linked_research_ids_overlap` / `theme_tags_overlap` / `source_collection_overlap`）由 harness 直接对 `themes/metadata/<id>.json` 取字段做 Jaccard，2 个维度（`scope_boundary_semantic_overlap` / `scenario_map_semantic_overlap`）由 LLM 读 `themes/metadata` 的 prose 字段评分。

**实事归纳问题（2026-04-19 反查）**：现有 8 份 `themes/metadata/*.json` 历史文件**没有** `scope_boundary` / `scenario_map` / `theme_tags` 这 3 个 cluster 假设字段。8 份文件统一带的是 17 个 v1 字段（`id` / `title` / `lifecycle_stage` / `status` / `time_horizon` / `priority_bucket` / `priority_rank` / `summary` / `why_now` / `preferred_skill` / `last_reviewed_at` / `evidence_status` / `open_questions` / `linked_research_ids` / `linked_thesis_ids` / `linked_asset_tickers` / `subthemes`），其中 `linked_asset_tickers` 即 cluster 设计早期讨论里所说的 `key_assets`（用事实名，不另起字段）。

**决策（option A，PM 已确认）**：正式扩 `themes/metadata` schema 到 v1.5，把 cluster 设计假设的字段写进 schema，但对历史 8 份采取 lazy migration——历史 v1 文件可继续 pass、不强制改写；新建文件（bootstrapper Branch 1 / 3 / 4b 写 admit / narrow_then_admit / carve_out_confirmed 时）必须是 v1.5 strict。后续由 PM 主动重写历史文件填上 v1.5 字段。

**v1.5 schema 路由结构**（`data/runtime/schemas/themes_metadata_v1_5.schema.json`，oneOf 分支）：

| 分支 | 触发条件 | 必含字段 | 写入者 |
|---|---|---|---|
| **v1 lazy** | 文件不含 `schema_version` 字段 | 17 个 v1 基础字段；**禁止**含任一 v1.5 新结构字段（防 partial migration 灰色态） | 历史 / 不动 |
| **v1.5 strict** | 文件含 `schema_version: "1.5"` | 17 个 v1 字段 + `schema_version` + `scope_boundary` + `scenario_map` + `theme_tags` + `created_at_utc` + `created_via` | bootstrapper Stage B / `research-theme-knowledge-and-package-curator` |

**Stage A 过渡期退化行为**（v1.5 字段未 backfill 的相似性维度）：

- `theme_tags_overlap`: 历史邻居 `theme_tags` 缺失 → 该维度对该邻居赋 0.0（harness 直接判 absent → 0.0，不让 LLM 猜）。Composite 加权后该邻居整体得分会偏低，可能在 `merge_into_existing` 触发阈值下不触发 → 这是过渡期偏向"宁开新主题、不强制 merge"的合理失真，PM 重写历史文件后会自然恢复
- `scope_boundary_semantic_overlap`: 历史邻居 `scope_boundary` 缺失 → harness 跳过该邻居的 LLM scope 评分，赋 0.0，并在 `dimension_score_provenance.scope_boundary_semantic_overlap[<theme_id>]` 标 `harness_skipped_v1_legacy`（而不是 `llm_estimated`），让 PM round-2 看得见
- `scenario_map_semantic_overlap`: 同上，缺失 → 0.0 + `harness_skipped_v1_legacy`
- `linked_research_ids_overlap` / `source_collection_overlap`: v1 已有，无退化

bootstrapper Stage A 在合成 narrative 时必须把 `harness_skipped_v1_legacy` 标记反映出来（例如 `synthesis_narrative_per_theme[<theme_id>]: "邻居 metadata 仍为 v1 legacy，scope/scenario 维度未参与计算，仅以 linked_research_ids 重叠 = 0.X 估算"`），让 owner round-2 能判断是否要先回填邻居的 v1.5 字段再决策。

**强制层兑现**：
- L1：`themes_metadata_v1_5.schema.json` 的 `oneOf` 分支结构 + `_check_themes_metadata_stage_b_extras()` 的 per-branch policy（admit_new / narrow_then_admit / carve_out_confirmed 必须 v1.5；merge_into_existing 接受 v1）
- L2（待 Phase B-0.5 兑现）：merge_into_existing 写回时 diff guard 必须确认只动 `linked_research_ids` + `merge_audit`，不能顺手"升级"既有 v1 文件到 v1.5（升级是 PM 主动行为，不是 merge 副产物）
- CLI: `tradectl thesis-cluster validate theme-bootstrapper-stage-b <metadata_path> --branch <branch_name>`

### 4.7 命名约定 — 读宽 写严（read wide, write strict）

cluster schema 在 theme_id 命名上采用过渡期的「读宽 写严」分层规则，避免 8 份历史 hyphen-case `themes/metadata/*.json` 文件被强制迁移：

**Read-side（引用既有 theme 的字段，schema pattern 用 transitional `[a-z0-9_-]`）**

| Schema | 字段 |
|---|---|
| `thesis_note_v1_5.schema.json` | `cross_theme_links[].theme_id` |
| `bootstrapper_proposal.schema.json` | `neighbor_themes_evaluated[]`、`dimension_scores` keys、`dimension_score_provenance` keys、`synthesis_narrative_per_theme` keys |
| `theme_candidate.schema.json` | `closest_existing_themes[].theme_id`、`recommended_action: already_covered_by_theme_<id>` 中 `<id>` 子串 |
| `themes_metadata_v1_5.schema.json` | `id`、`subthemes[].id` |

**Write-side（新生成的 identifier，snake_case-only）**

| Schema | 字段 | 强制层 |
|---|---|---|
| `thesis_note_v1_5.schema.json` | `thesis_id` | schema pattern `^[a-z0-9][a-z0-9_]{2,79}$` |
| `bootstrapper_proposal.schema.json` | `candidate_slug` | schema pattern `^[a-z0-9][a-z0-9_]{2,79}$` |
| `theme_candidate.schema.json` | `candidate_slug` | schema pattern `^[a-z0-9][a-z0-9_]{2,79}$` |
| `owner_round_2_decision.schema.json` | `candidate_slug` | schema pattern `^[a-z0-9][a-z0-9_]{2,79}$` |
| `themes_metadata_v1_5.schema.json` | Stage B `admit_new` / `narrow_then_admit` / `carve_out_confirmed` 写出的 `id`、`subthemes[].id` | schema pattern transitional + `_check_themes_metadata_stage_b_extras()` 拒 hyphen |

**为什么这么分层。** `themes_metadata.id` 既是历史 read 字段又是未来 write 字段，无法在 JSON Schema 单一 pattern 同时表达两条规则。schema 用 transitional pattern 让历史文件继续 valid（read），write-side 强制走 validator extra check（拒 hyphen）。同样 `cross_theme_links[].theme_id` 必须接 hyphen 才能让 thesis cluster 立即引用现存 8 份 hyphen-case theme，否则整个 cluster 在 PM 重建 metadata 之前不可用。

**自然 deprecation。** 我们不写"主动迁移 8 份文件"phase。后续 PM 重建 priority_tree / thesis_notes / themes/metadata 的过程会自然把 hyphen-case 文件用 snake_case 版本替换；transitional schema 容许这个过渡期持续任意长。当所有现存 metadata 都迁完后，可以把 read-side pattern 收紧到 snake_case-only `[a-z0-9_]`，并删除 validator 的 `_check_themes_metadata_stage_b_extras` 中 hyphen 检查（因为 schema 已经禁止）。

**fixture 演示**：

- `tests/thesis_cluster_fixtures/research-thesis-drafter/02_links_to_legacy_hyphen_theme/`：thesis 引用 `ai-datacenter-power-and-balance-of-plant`，schema 接受 → cluster 不被历史 metadata 阻塞
- `tests/thesis_cluster_fixtures/theme-bootstrapper-stage-b/02_admit_new_with_hyphen_id_rejected/`：Stage B `admit_new` 试图写 hyphen-case 新 id，validator 拒绝 → 写出来的新 theme 强制 snake_case

### 4.6 两套 lifecycle 不混用（thesis_note vs themes/metadata）

cluster 内部存在两个独立的 lifecycle 概念，名字相近但语义完全不同。SKILL / 设计 doc 中过往讨论曾出现混用，此节固定区分：

| 字段 | 所属对象 | 枚举 | 触发对象 | 含义 |
|---|---|---|---|---|
| `lifecycle_stage` | `thesis_note.<thesis_id>.json` | `{draft, active, retired}` | `research-thesis-drafter` 写 draft；adversary 通过后 owner / drafter 推进到 active；后续证伪后 adversary / owner 推进到 retired | thesis 命题在 adversary-validation pipeline 中的成熟度。`active` 才允许写 adversary 字段 (`falsifiers` / `scenario_triggers` / 等)，draft 不可 |
| `lifecycle_stage` | `themes/metadata/<id>.json` | `{approved, draft_candidate}` | `research-theme-bootstrapper` 创建时写 `draft_candidate`；首份 PM-confirmed 报告产出后 `research-theme-priority-updater` / `research-theme-report-owner` 推进到 `approved` | theme 治理状态。`draft_candidate` 表示 metadata 已落但尚未经 PM 确认作为长期研究主题；`approved` 表示进入正式 priority pool |

误用风险：cluster doc 早期把 thesis_note 的 `{draft, active, retired}` 误用到 themes/metadata 上下文。**今后只允许**：

- "thesis 进入 active 状态" 必然指 thesis_note.lifecycle_stage = active（adversary 通过门）
- "theme 进入 approved 状态" 必然指 themes/metadata.lifecycle_stage = approved（PM 治理门）
- **不可** 写 "theme 进入 active" 或 "thesis 进入 approved"，前者会与 themes/metadata.status (`{active, candidate}`) 混淆，后者根本不是合法状态

L1 schema 的 enum 已经把这两套写死、互不接受对方枚举值；任何混用会被 jsonschema 直接拒。

---

## 5. 与上游 / 下游 controller 的边界

### 5.1 上游

- `routing-task-mode-router` 把 PM 的输入路由到 thesis 或 theme 任务线 → 触发对应 cluster agent
  - "建新 thesis" → `research-thesis-drafter`
  - "扫资料找 theme candidate" / "最近一个月有什么 candidate 吗" → `research-theme-discovery-scanner`
  - "我想开个新 theme X" → `research-theme-report-owner` (`pass_type = seed_theme_brief`)
  - "PM 审过的 candidate Y 现在开了" → `research-theme-report-owner` (`pass_type = seed_theme_brief`，把 candidate 转为 owner_decision)
- `research-theme-report-owner` 在 `seed_theme_brief` round-1 决策完成后调 `research-theme-bootstrapper` Stage A 仲裁；Stage A 写完 proposal 后回到 owner 做 round-2 决策；owner 写完 round-2 后再次调 `research-theme-bootstrapper` Stage B 执行
- `research-theme-report-owner` 在 `report_*` pass 中决定要新建 thesis 时，直接调 `research-thesis-drafter`（不走 bootstrapper，因为 theme 已存在不是 theme-level 操作）

### 5.2 下游

- `writer-handoff`：cluster 产出后被装进 package 时，由它做 pre-writing 闸门
- `research-theme-report-reviewer`：写完 ds.md 后由它做 post-writing 闸门，**含**对 cluster 写出的 v1.5 字段做结构审计 + 对 cluster 跑出来的判定结果做**外部独立验证**（F9 / T02：reviewer 是 cluster 之外的"裁判"，必须能 raise major finding 推翻 cluster 判定，不只是格式 check；详见 [`Plan B §5.2`](ideas/thesis_and_theme_writing_pipeline_reorg.md#52-reviewer-最小升级)）
- `research-theme-priority-updater`：cluster 写完后跑它重建 priority view + index，含 `cross_theme_links[].role` 处理

### 5.3 平行（不通过 cluster）

- 旧 v1 thesis_note 在 cluster **触及**时升级到 v1.5；不触及不动（lazy migration）

---

## 6. 显式不做（避免误用）

- 不做 cluster orchestrator（AutoGen / LangGraph 风格）
- 不引入 MCP / Anthropic-only 技术栈
- 不做 thesis library / GitHub for thesis 类外部叙事
- 不在本 doc 把 `scenario` 提为一等公民对象（留 Phase 3 / 后续 plan）
- 不把 v1 老 thesis 全部一次性 migrate 到 v1.5
- cluster agent 不写 PM-facing 报告主体（那是 `research-theme-knowledge-and-package-curator` + DS writer 的事）
- cluster agent **不**作为 controller，不能自己决定路由（路由仍归 `routing-task-mode-router` / `research-theme-report-owner`）
- `research-theme-discovery-scanner` 不做定期 cron（本轮）；不直接落 `themes/metadata/*.json`；不调 `research-theme-bootstrapper`（必须 PM 审过 → owner round-1 → bootstrapper）；scanner 的 nearest_existing_themes 是粗筛，**不替代** bootstrapper Stage A 细仲裁
- `research-theme-bootstrapper` 不做"值不值得开"决策（owner round-1 责任）也不做"走哪条 negotiation 方案"决策（owner round-2 责任）；自己的责任是 Stage A 跑全库相似度仲裁 + 写 proposal，以及 Stage B 按 owner round-2 决策走 5 条互斥执行分支
- `research-theme-bootstrapper` **不允许跳过 Stage A** 直接落盘，即便 PM 在 chat 里说"直接开吧"也必须先扫一遍写 proposal（否则 cluster 失去去重责任，第二天就会出现重复主题）
- `research-theme-bootstrapper` **不允许**让 LLM 自己计算 deterministic 三维分数（`linked_research_ids_overlap` / `source_collection_overlap` / `theme_tag_overlap`），harness 必须先预计算（F1 / T10）
- `research-theme-bootstrapper` Stage A 的 prompt **不允许**含完整 themes/metadata 全文，只能含 6 字段精简切片（F2 / A14）
- `research-theme-bootstrapper` Stage B 的 input **不允许**含 Stage A `bootstrapper_proposal.json` 全文（F4 / T03，避免 Stage B 锚定 Stage A 推荐）
- `research-theme-bootstrapper` Stage B `carve_out_from` 分支**不允许**不写 dry-run diff 直接改邻居 metadata
- `research-theme-bootstrapper` Stage B `subordinate_to` 分支本轮**不允许**落任何 metadata 文件（F3 / M05，直接 raise `subordinate_executor_not_implemented`，让 owner 改决策）
- `research-theme-discovery-scanner` **不允许**省略 `as_of_utc` 锚（F6 / V04，PM 必须显式给基准时间，scanner 不默认用 wall clock）

---

## 7. Changelog

- 2026-04-19 v0.4 — 落地 13 条 review 修正：(F1 / T10) `research-theme-bootstrapper` Stage A 5 维分数显式拆 deterministic vs LLM（§2.5.4），harness 预计算 3 维结构化分数；(F2 / A14) Stage A prompt 输入收紧到 6 字段精简切片，禁止送完整 metadata 全文；(F3 / M05) Stage B B5 `subordinate_to` 不落 metadata，直接 raise `subordinate_executor_not_implemented`；(F4 / T03) Stage A 与 Stage B input 严格隔离，Stage B 不送 proposal.json 全文；(F5 / T11) 时间字段统一 `_utc` 后缀（`decided_at_utc / scan_at_utc / merged_at_utc / consumed_at_utc / changed_at_utc / as_of_utc / scanner_invoked_at_utc`）；(F6 / V04) `research-theme-discovery-scanner` 强制 `as_of_utc` 显式锚 + `scanned_window_utc` 顶层字段；(F7 / V01) `bootstrap_arbitration_decision` 加 `pm_explicit_confirm: true` + `pm_chat_message_id`，缺失 raise `missing_pm_confirmation_round2`；(F8 / X05) §2.5.3 给 `bootstrapper_proposal.json` 完整 schema 含 per-dimension `dimension_score_provenance` + `synthesis_narrative`；(F9 / T02) §5.2 reviewer 显式定位为"cluster 之外的独立验证 + 可推翻 cluster 判定"；(F10 / M01) `rationale` 加 `[OVERRIDE]` 前缀约定 + 阈值 calibration trigger 引 Plan B §10；(F12 / Rule 36) §2.5 加 reader gain 一句；(F13 / Rule 42) §2.5.6 显式声明 `thesis_note` 当前**不在** artifact_graph 内、cluster 不需要 emit-sidecar。同步更新 §0.1 / §3.2 / §4.2 / §5.2 / §6 / §1.1.1 周边描述。
- 2026-04-19 v0.3 — `research-theme-bootstrapper` 升级为 orchestrator + executor 双段 persona：Stage A 全库相似度仲裁 + 5 维分数 + 5 种 negotiation 方案对照表（§2.5.1）+ owner round-2 决策字段（§2.5.2）+ Stage B 五条互斥执行分支（§2.5.3，含 `carve_out_from` dry-run + `subordinate_to` placeholder）；强制规定**任何 theme 创建意图都必经 Stage A**，无论入口是 PM-driven 还是 PM 审过的 discovery candidate。§1.1 / §1.1.1 / §3.2 / §4.2 / §5.1 / §6 同步。`carve_out` 与 `subordinate` 涉及的 metadata 新字段（`is_overlay` / `parent_theme_id` / `merge_audit`）见 [`research_06 §5.6`](research_40_thesis_note_schema_v1_5.md#56-新出现的非-thesis-对象关联但不属本-schema)。
- 2026-04-19 v0.2 — 把 cluster 从 4 agent 扩到 5：加 `research-theme-discovery-scanner` 覆盖 #2 AI bottom-up 入口；把 `research-theme-bootstrapper` 收紧成 executor persona（决策 / framing brief 归 `research-theme-report-owner`，bootstrapper 只落文件）；§1.1.1 加三入口路径映射表；§4.2 / §5.1 / §6 同步。
- 2026-04-19 v0.1 — 首版。Plan B Phase B-(-1) 产物。覆盖 cluster 边界 / 4 agent roster / message contract / 运行时形态 / 失败模式 / 上下游边界。
