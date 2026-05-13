# Hoveath 治理架构

Hoveath 是一套 AI agent 治理系统。它解决的核心问题是：当多个 AI agent 持续产出 skill、report、schema、evidence、thesis 等相互依赖的 artifact 时，如何让这些产出之间保持一致性、freshness 可审计、authority 边界清晰。

治理靠结构，不靠人盯。

---

## 端到端：一个模块从创建到审计通过的完整流程

以创建一个新的 Digestion 模块为例，看整个系统怎么运转：

**第一步：写 Design Doc。** 在 `designDoc/` 下创建模块文档，定义模块的意图、边界、class assignment、failure signature。文档头部有 Contract Capsule YAML，声明 status、layer、canonical_owner。

**第二步：写 Registry。** 在 `src/audit/modules/<module>/registry.py` 下实例化 typed contract，继承 base.py 的母类（比如一个 Skill + 两个 Material + 一个 Artifact）。每个实例的 owner_ref 指回 Design Doc。

**第三步：写 SKILL.md。** 在 `.claude/skills/<skill-name>/SKILL.md` 下写 AI 运行时行为文本，定义 persona、task、truth surface、output artifact、completion standard、boundary。

**第四步：T0 Skill Management Agent 接管。** 调用 `agent-the-skill-management`，它编排外部 writer 和 reviewer：writer 产出 SKILL.md 初稿，reviewer 做 S1-S10 alignment 检查（Design Doc authority、registry class assignment、runtime behavior prose 之间的一致性），需要修改时 fix 后重新提交，最多 3 轮。

**第五步：T0 Contract Audit Agent 接管。** 调用 `agent-the-contract-audit`，它跑三层验证：Layer 1 capsule recovery（必填字段、status、canonical_owner 匹配）→ Layer 2 structural validation（ID 命名语法、type safety、A18 要求）→ Layer 3 semantic review（由外部 Opus 4.7 session 独立判断 Design Doc、Registry、SKILL.md 三表面的语义一致性）。finding 分类为 surface_fix（可修）、type_system_gap（base.py 层面问题，不在本循环修）、accepted_note（观察记录）。最多 3 轮。

**结果：** 模块的三个表面经过机器校验和独立 AI 审阅，一致性有审计记录。

---

## 分层架构

```
T0 治理层        agent-the-skill-management / agent-the-contract-audit
                 编排流程，不拥有内容

T1 内容契约层    Material Catalog / Artifact Graph / Expertise
                 定义 object boundary、dependency、freshness 传播

执行层           具体 skill + writer/reviewer gate
                 产出内容，受 T0 和 T1 约束
```

T0 只编排，不产出内容。T1 只定义边界，不执行流程。执行层在 T0 和 T1 的约束下产出实际 artifact。

---

## T0 治理层

### 三表面模型

每个模块有三个表面，各自有不同的作者和消费者：

| 表面 | 位置 | 拥有什么 | 作者 | 消费者 |
|---|---|---|---|---|
| Design Doc | `designDoc/` | 意图、边界、class assignment、authority 方向、failure signature | 人类或 AI（design session） | 审计、routing、下游设计决策 |
| Registry | `src/audit/modules/<X>/registry.py` | typed contract 实例、structural validation、ref integrity | 人类或 T0 agent | 审计、code binding、schema lint |
| SKILL.md | `.claude/skills/<X>/SKILL.md` | AI 运行时行为文本、completion standard、boundary | Skill Management Agent 的 writer | AI agent 运行时 |

Authority 方向：Design Doc > Registry > SKILL.md。当三者冲突时，Design Doc 的意图优先；Registry 的 typed ref 服从 Design Doc；SKILL.md 的行为文本服从前两者。

规则：作者可以省略 registry object，但不能引用不存在的 object。Design Doc 永远不从 registry 自动生成。

### Contract Audit：三层验证

`agent-the-contract-audit`（T0 Contract Audit Agent）对目标模块执行三层验证：

**Layer 1 Capsule Recovery。** 从 Design Doc 头部提取 Contract Capsule YAML。检查项：
- 必填字段存在（title、status、layer、canonical_owner）
- status 合法（proposal / active_draft / active / smoke_design / deprecated / archived）
- canonical_owner 匹配文件路径
- truth_surfaces 路径存在

**Layer 2 Structural Validation。** 对 registry 做自动校验。检查项：
- ID 命名语法（`design_*` / `material_*` / `artifact_*` / `tool_*` / `skill_*` / `workflow_*` / `agent_*` / `validator_*`）
- ref list 的 type safety
- owner_ref 路径存在
- code binding 路径存在
- A18 completeness：Agent 必须有 objective、policy、stop_condition；Skill 必须有 projection_path 且以 SKILL.md 结尾
- blocked name 检查

**Layer 3 Semantic Review。** 由外部 Opus 4.7 session 独立执行。reviewer 读取自包含的 audit package（本模块 Design Doc + Registry + base.py + SKILL.md），输出 YAML findings：
- `block`：两个表面矛盾
- `fix`：不一致但无矛盾
- `note`：观察，无需动作

Finding 分类和修复方向：
- `surface_fix`：问题在 Design Doc / Registry / SKILL.md 某一个表面，修该表面
- `type_system_gap`：问题在 base.py 母类层面，记录但不在本循环修
- `accepted_note`：边界重复但各表面均在自身 authority 内，记录后继续

通过条件：最近一轮 reviewer 返回 0 block + 0 actionable fix。Hard cap 3 轮。

### Skill Management：写作审阅循环

`agent-the-skill-management`（T0 Skill Management Agent）编排 SKILL.md 的写作和审阅：

1. 调用 `tool_skill_writer`（外部 worker）产出 SKILL.md 初稿
2. 调用 `tool_skill_reviewer` 做 S1-S10 alignment 检查
3. 解析 verdict，路由到修改或升级

Verdict 路由：
- `accept_as_is`：写入目标路径，结束
- `accept_with_notes`：做 surface fix，写入，结束
- `needs_author_revision`：编辑初稿，回到步骤 2
- `needs_registry_sync`：升级到用户（registry 变更超出本循环权限）
- 3 轮用尽：升级到用户，附 unresolved findings

每轮产出 `artifact_skill_review_log` YAML，记录 reviewer 的完整 verdict。

外部 worker 使用 `support-external-agent-builder` 的 assembled runner 架构：stable prefix + GENERAL_MODULE + CUSTOMIZE_MODULE + DATA_DEPENDENT_MODULE + dynamic suffix。worker 在独立 context 中运行，避免 context 污染，保证审计可追溯。

---

## 八母类型系统

`src/audit/base.py` 定义 8 个 frozen dataclass 母类，所有模块的 registry 通过实例化这些类来声明 typed contract。

| 母类 | A18 层级 | 核心字段 | 角色 |
|---|---|---|---|
| Design | - | design_id, owner_ref, purpose, role, scope, 各类 ref list, gates | 设计意图容器 |
| Material | - | material_id, owner_ref, scope, file_parts（role/meaning/required）, gates | 持久多文件内容资产 |
| Artifact | - | artifact_id, owner_ref, artifact_kind | 单个生成文件或运行时输出 |
| Tool | Layer 1 | tool_id, owner_ref, purpose, code_bindings | 原子执行句柄，judgment 在别处 |
| Skill | Layer 2 | skill_id, runtime, projection_path, purpose, input/output refs, tool_refs, gates | 可复用能力，有本地方法 |
| Workflow | Layer 3 | workflow_id, owner_ref, steps（WorkflowStep list）, input/output refs, gates | 固定执行序列，有步骤和门控 |
| Agent | Layer 4 | agent_id, owner_ref, role, objective, policy, stop_condition, skill/tool refs, gates | 目标导向运行时 actor，有自适应策略 |
| Validator | - | validator_id, owner_ref, input/output refs, code_bindings, gates | 校验句柄，有显式门控 |

**A18 层级要求（Tool < Skill < Workflow < Agent）：**
- Tool：原子执行，judgment 在别处
- Skill：可复用能力，有 input/output contract，有稳定方法
- Workflow：固定执行序列，有步骤和门控，无自适应策略
- Agent：目标导向，有 objective、state、policy、stop_condition，有自适应决策

Layer 2 及以上必须有 projection_path（SKILL.md）。Layer 4 必须有 objective、policy、stop_condition。

**Registry 继承关系：**
```
src/audit/base.py              母类定义 + type alias + validation
  → src/audit/shared_contracts.py   跨模块共享对象
    → src/audit/modules/<X>/registry.py   模块级实例
      → src/audit/manifest.py            跨模块依赖图
```

**Artifact 种类：** config_artifact / runtime_artifact / prompt_input_artifact / sidecar_artifact / index_artifact / audit_artifact。

**Material 文件角色：** read_content / raw_content / image / metadata / archive_snapshot。每个 MaterialFileSpec 声明 role、meaning、required。

---

## T1 内容契约层

### Material Catalog：内容对象边界

Material Catalog 定义内容对象的边界、允许的内容、禁止的升级、handoff 语义。它继承 Artifact Graph 的 node/edge/freshness 基础设施，在上面加内容层规则。

**内容资产垂直语法（从原始到 PM 决策）：**

```
Raw Data（原始/provider-normalized，无解读）
  → Operating Cycle Artifact（按周期 recap/decision）
  → Source Card（source 理解 + 权限 + 时间语义 + 允许用途）
  → Expert Artifact（从 material input 的结构化解读：Dossier / State Map 等）
  → Evidence（belief-change record，链接 material 到 Thesis/Scenario/Theme delta）
  → Thesis（可证伪的信念容器）
  → Scenario（基于 Expertise + Thesis 锚点的前瞻预测路径）
  → Theme（持久研究记忆组织器）
  → Technical Report / Report / Package / Portfolio Decision
```

**高风险边界转换（需要显式 gate）：**
1. Source Card → Typed Claim：必须通过 Expertise firewall
2. Typed Claim → Evidence：需要 belief_delta + target refs
3. Source Card/Claim set → Expert Artifact：需要 named schema + material refs
4. Expert Artifact → Decision Brief：需要 PM compression + decision_use
5. Thesis → Scenario：需要 Expertise Application；Research admits
6. Scenario → scenario_note：需要 Research/PM admission

每种转换有对应的 child contract（`material_10_raw_data_contract.md` 到 `material_90_support_surfaces.md`，共 10+ 份）定义具体规则。

### Artifact Graph：依赖和 freshness

Artifact Graph 解决的核心问题：防止 agent 绕过 freshness contract 找捷径。通过显式声明 artifact 之间的依赖关系，让 freshness 可机器检查。

**Artifact Node 定义（所有字段必须）：**
- stable ID
- canonical local path
- layer label（L0 原始数据 → L1 确定性衍生 → L2 AI 解读 → L3 judgment → L4 PM-facing）
- session_date_market（日期锚点）
- one explicit builder
- one explicit owner skill
- freshness contract（predicate 决定 FRESH / STALE / MISSING / UNKNOWN）
- upstream dependencies（每条有 edge type）

**Edge 类型：**
- `must_be_fresh(D)`：上游 node 在同一日期 D 必须 FRESH
- `must_exist_unchanged_since(D)`：下游产出时记录的上游 hash 必须与当前 hash 一致
- `must_be_referenced_in_output`：必须在 sidecar 中被引用
- `optional_overlay`：提供信息但不强制要求

**Freshness Predicate 类型：**
- `date_anchor`：report_date == 请求日期
- `source_state_hash`：上游文件 hash 未变
- `blocking_flag`：daily_update_status.json 各层 flag 全 false
- `monotonic_at_least`：数据库 bar timestamp >= session anchor
- `series_recency_per_category`：宏观指标在 category-specific lag 内
- `recency_within_days`：文件在 age window 内
- `referenced_existence`：peer artifact 必须存在
- `composite`：虚拟聚合器，所有 children FRESH 才 FRESH

**UNKNOWN 语义（三种含义，必须区分）：**
1. Tool-gap UNKNOWN：检查工具未实现，真实 FRESH/STALE 存在但无法判定
2. Input-gap UNKNOWN：调用方参数不足（缺 report_date 等）
3. Designed UNKNOWN：虚拟聚合器，by construction 在 post-walk 才 rollup

**Writer Sidecar：** `.writer.json` 记录上游 node ID、content hash、status_at_emit、reason_at_emit、produced_for metadata。用于 `source_state_hash` 和 `must_exist_unchanged_since` 校验。

**逻辑 asof vs mtime：** 逻辑 asof（显式 task time）是 truth；文件 mtime 无意义。允许日内 judgment invalidation 而无需 touch 文件。

### Expertise：可复用分析能力

Expertise 层定义可复用的分析能力 contract，不定义具体实例。

**Expertise 拥有什么：**
- Expert identity + lifecycle
- Framework、lens、ontology、taxonomy、method
- Source-card pattern（Source Card 的必填 section）
- Source-class / claim-type firewall（哪些 source class 可以产出哪些 claim type）
- Route + application grammar
- Expert artifact schema
- Scenario prediction framework
- Validation + review policy
- Generated skill projection contract

**Expertise 不拥有什么：**
- Raw Data、Source Card 实例、Typed Claim、Expert Artifact、Evidence、Thesis/Theme/Scenario admission、Technical Report prose、PM 决策、code behavior、source ingestion

**能力到内容的流动公式：**
```
Expertise + source material        → Source Card
Expertise + Source Card / Claims   → Expert Artifact
Expertise + Thesis                 → Scenario
Expertise + context + material     → Decision Brief / Portfolio Decision support
```

**Expert Factory（`digestion-expert-factory` skill）负责生产和维护 Expert：**
- 准入判定：material 是否教了一个可复用的方法（方法/指标/信号/模式/failure mode/行业 leading indicator/选股 lens）
- 不准入：单个事实、单次价格变动、单张图表、单个 PM 意见
- 产出 Expert contract（expert_id、expert_type、source_classes、claim_types、typed_claim_firewall、outputs_allowed、outputs_blocked）
- Expert 不能直接写 active thesis、ai_verified=true 的 evidence、scenario activation、PM ack、portfolio action

---

## Gate-Based Composition 模式

整个系统用统一的 writer → reviewer → gate 模式控制质量。以下是各流程的实例：

| 流程 | 作者层 | 审阅层 | 门控逻辑 |
|---|---|---|---|
| Skill 写作 | skill writer（外部 worker） | skill reviewer（外部 worker） | S1-S10 alignment，≤3 轮 |
| Contract 审计 | 模块作者 | semantic reviewer（外部 Opus 4.7） | 0 block + 0 actionable fix |
| Evidence 审阅 | thesis-drafter / thesis-adversary | evidence-reviewer（独立 AI gate） | 五项 sub-verdict + quote provenance |
| Package 完整性 | theme-knowledge-and-package-curator | writer-handoff | 10 项 minimum package check |
| 代码审查 | 代码提交者 | engineering-project-review | severity taxonomy（BLOCKING / MEDIUM / LOW / NIT） |

**Evidence Reviewer 详细机制（`research-evidence-reviewer`）：**

独立 AI gate，对每条 evidence_record 做以下 sub-verdict：
1. source_trust_verdict：至少 1 个 T1 anchor，caller 的 tier assignment 合规
2. belief_delta_coherence：四个 prose field 有实质内容且内部一致
3. response_supports_claim：source content 直接支持/部分支持/矛盾 claim

对含引用的 evidence，额外做 quote provenance 审计（共 9 项子检查：quote 溯源、official source attempt、surface attribution、verbatim location、semantic truth、surface time、oral surface attempt、prior public use、secondary-only downgrade）。

输出：同一条 evidence_record JSON，append 一条 ai_review_log entry。ai_verified 翻转为 true 仅在所有 sub-verdict pass 且 schema R1 满足时。reviewer 不编辑 body field，只操作 ai_review_log + updated_at_utc + ai_verified flip。

**Writer-Handoff 详细机制（`writer-handoff`）：**

package 完整性门。两种结果：
- `need_more_detail`：列出缺失的 block + 为什么阻止写作
- `ready_to_write`：gate 通过

10 项 minimum package check：当前判断明确 / 背景上下文存在 / 市场定价清晰或可推断 / key driver 和传导路径存在 / confirmed anchor 和 not-confirmed item 分离 / key debate 和 uncertainty 存在 / scenario path 存在 / portfolio fit 存在 / 风险和监控项存在。

**Engineering Project Review 详细机制（`engineering-project-review`）：**

三阶段强制顺序：
1. Reproduce 校验门：逐条复现提交者声明的每个 `校验门` 命令，比对数字
2. 读 diff：`git diff` 获取独立于 commit message 的 truth
3. 跨切面检查：schema enum、SKILL.md vs runtime、mirror 一致性、contract/registry/test sync、scope bleed、time-field 语义、delta narration、aggregate-count transparency、vertical vs longitudinal frame、dirty-state attribution

---

## Freshness 和 Lifecycle 治理

Charter 的 freshness law：**active 和 fresh 是两个独立维度。** 一个 object 可以是 active 但 stale。portfolio 决策要求 active AND fresh。

### freshness_state enum

三个值：`fresh` / `due` / `stale`。

### 状态转换规则

```
if any review_trigger[] fired:
    new_state = "due"
elif now >= scheduled_for + stale_after_days:
    new_state = "stale"
elif now >= scheduled_for:
    new_state = "due"
elif prior_state == "absent":
    new_state = "fresh"
else:
    no transition
```

### 默认 cadence（当 object 无 review_policy 时）

| object_type | cadence | stale_after |
|---|---|---|
| thesis_note | monthly + event | 45 days |
| themes/metadata | monthly | 60 days |
| scenario_note | bi-weekly + event | 21 days |
| path_observation | event-only | 30 days |

### Staleness Sweeper（`research-theme-staleness-sweeper`）

每周自动扫描 canonical store。对每个 state transition emit 一行 freshness_event（append-only，不编辑已有 event）。

Sweeper 不自动 revive。Revive 条件：evidence_record 有 `pm_acknowledged=true` 且 `changed_dimension ∈ {conviction, scope_boundary}`。Sweeper emit `revived` freshness_event，但 revive 的触发必须来自 PM。

每次 sweep 产出两个 artifact：
- `data/runtime/staleness_sweep/<weekiso>.jsonl`：machine-readable event 行
- `data/runtime/staleness_sweep/<weekiso>.md`：human digest

### Portfolio Decision 的硬 freshness gate

`operation-portfolio-decision` skill 要求：
- 引用的 Scenario 必须 active + fresh
- 必须有显式的 (pm_conviction, scenario_role, market_state) 三元组
- 每个三元组元素必须能追溯到 Evidence ledger
- 必须有 pricing anchor

缺任何一项，decision 被拦截，不是降级通过。

---

## 时间语义契约

`designDoc/the_timestamp_semantic.md` 定义所有时间戳/日期字段的语义。所有 schema、API、Design Doc、code 中的时间字段都必须先通过这份 contract。

### 9 个角色（互斥）

| # | 角色 | 语义 |
|---|---|---|
| 1 | `observed_at` | 世界中的事件发生时刻（tick、讲话、投票、政策、出版） |
| 2 | `period_start_at` / `period_end_at` | 区间窗口的边界（成对使用） |
| 3 | `effective_at` / `effective_date` | 规则/政策/任命生效时刻 |
| 4 | `expiry_date` | 规则/条款/政策过期（总是与 effective_at 成对） |
| 5 | `recorded_at` | 我们系统写入该 record 的时刻（所有 record 必须有，archive 唯一写入时间） |
| 6 | `updated_at` | record 的可变字段最后变更时刻（overlay 层 required/optional，archive 层禁止） |
| 7 | `horizon_date` | 内容覆盖数据到此点（"data through X"） |
| 8 | `scheduled_for_at` | 前瞻性时点（未来 trigger、next review） |

### 5 种存储后缀

| 后缀 | 格式 | 用途 |
|---|---|---|
| `_at_utc` | ISO-8601 UTC instant | 通用时刻 |
| `_calendar_day_utc` | `YYYY-MM-DD` | 纯 UTC 日历切片（7×24 资产） |
| `_session_date_et` | `YYYY-MM-DD` | XNYS ET session day |
| `_session_date_ct` | `YYYY-MM-DD` | CMES CT session day |
| `_session_date_market` | `YYYY-MM-DD` + 兄弟 `market_tz` IANA | 通用每资产 session |

字段命名规则：`<role>_<storage>`，如 `observed_at_utc`、`period_end_session_date_et`。

### 4 条强制执行规则

- **R1**：所有进入系统的 record 必须有 `recorded_at_<storage>`（archive-first minimum）
- **R2**：新 object class 必须先在 §4 矩阵注册，再写 schema
- **R3**：双向执行。schema 有但矩阵没有的字段，linter raise；矩阵 REQ 但 schema 缺的，linter raise；字段名不符合 `<role>_<storage>` 形式，linter raise
- **R4**：archive 层禁止 `updated_at_*`（immutability）；overlay 层 required `updated_at_*`

### 比较规则

- 同 role + 同 storage 才能比较，否则 raise `TimestampSemanticsMismatch`
- UTC-first 比较（不做 astimezone 再 timedelta）
- DST 处理：只用 IANA tz，不用固定 offset
- 不使用 `datetime.now().date()` 或 `bar_start.date()` 做 freshness/idempotency 判断

### 执行工具

`src/core/timekeeping/` 提供：
- 9 role 的 typed wrapper
- parse / compare 语义
- registry（per-class 矩阵）
- `tradectl timeaudit --scan-schemas`：schema lint，校验 data/runtime/schemas/*.json 与 §4 矩阵的一致性

---

## Portable Persona 层（09_soul/）

`09_soul/` 是跨项目可迁移的 persona 层。进入新项目时，通过 `09_soul/handoff/installation_guide.md` 安装，用 `09_soul/handoff/distillation_protocol.md` 做内容蒸馏。

### 目录结构

```
09_soul/
├── core/
│   ├── SOUL.md              # 性格和工作姿态
│   ├── USER.md              # 用户 profile（跨项目稳定段 + 项目特定扩展）
│   └── COMMUNICATION.md     # 沟通风格 contract（always-on）
├── axioms/
│   ├── INDEX.md             # 公理索引和触发词
│   └── *.md                 # 各公理文件
├── skills/
│   ├── bestpractice_*.md    # 方法论 skill（doc self-review、retrospective、external worker 等）
│   └── workflow_*.md        # 工作流 skill（deep research、parallel subagent 等）
├── bridging/
│   └── mirror_sync.py       # 09_soul → 09_claude 同步工具
└── handoff/
    ├── distillation_protocol.md   # 内容蒸馏协议
    └── installation_guide.md      # 新项目安装指南
```

### 迁移路径

1. 把 `09_soul/` 整体复制到新项目
2. 在新项目创建 `09_<agent>/`（如 `09_claude/`）作为 runtime projection
3. 用 `mirror_sync.py` 从 soul → agent projection 同步
4. 在 `09_<agent>/core/PROJECT_ADAPTER.md` 写项目特定适配
5. 在新项目的 CLAUDE.md / AGENTS.md 指向 `09_<agent>/core/` 作为 session startup protocol

### 可迁移性标签

每条 rule 标注可迁移性：
- `<portable>`：跨项目 baseline，可直接搬
- `<project>`：项目特定，留本地
- `<portable-shape>`：pattern 可搬，内容需本地化

---

## Task Routing 框架

每个新请求先跑 routing-first check，识别 task mainline、assign first authority、定位 truth surface、调用 skill。

### routing-task-mode-router

顶层路由 skill。接收用户请求，匹配 task mainline，输出：
- mainline 名称
- first authority（哪个 skill 拥有这条线）
- truth surface（读哪些 canonical 数据）
- overlay_needed（是否需要 theme / ticker overlay，但不改变 mainline）

### 路由表结构

| 信号 | Mainline | 下游 Skill |
|---|---|---|
| inbox / triage | inbox / mail triage | ingestion-agentmail-inbox-triage |
| 整理 / normalize / promote | archive / research curation | ingestion-research-archive-operator |
| 市场 / recap / observation | market recap | research-current-market-reporter |
| theme report / update | theme maintenance | research-theme-report-owner |
| 扫描 / discovery | theme discovery | research-theme-discovery-scanner |
| 公司分析 / valuation | company financial analysis | research-company-financial-analysis |
| 单股 / ticker / levels | single-stock analysis | research-single-stock-analysis |
| 调仓 / hedge / book | portfolio decision | operation-portfolio-decision |
| 外部 repo / learning | external learning | research-external-learning |
| code / bug fix | engineering | 无 skill，读 code rules |
| designDoc / architecture | design | 无 skill，读 designDoc/ |

### Overlay 规则

theme 或 ticker mention 在 portfolio 或 stock request 内部出现时，不重新路由。保持原 mainline，标注 `overlay_needed = theme`。

### Skill 层级

| 层级 | 含义 | 实例 |
|---|---|---|
| Top-level entry | 路由器 | routing-task-mode-router |
| Mainline | 拥有完整结果的主线 | research-theme-report-owner, operation-portfolio-decision 等 |
| Substep | 在 mainline 下做有用的工作 | digestion-company-expert, routing-current-macro-priority-router 等 |
| Downstream gate / writer | 在上游稳定后执行 | writer-handoff, writer-asset-technical |
| Specialist / helper | 窄领域或设计辅助 | ingestion-source-connector-designer, engineering-project-review 等 |

执行顺序：route → mainline → substep（mainline 需要时）→ downstream gate（上游稳定后）。

---

## Thesis / Theme Analyst Sub-Cluster

六个 skill 组成 analyst sub-cluster，始终在 routing-task-mode-router 或 research-theme-report-owner 下运行。

### Thesis 子集群（4 agent，严格执行顺序）

```
research-thesis-drafter
  → research-thesis-verifier
    → research-evidence-reviewer
      → research-thesis-adversary
        → research-evidence-reviewer
```

- **thesis-drafter**：写 thesis_note v1.5 prose body + claims[] + cross_theme_links[] + lifecycle_stage: draft
- **thesis-verifier**：append 外部验证行到 notes；emit perplexity_log + evidence_record（ai_verified=false）
- **thesis-adversary**：写 falsifiers[] + scenario_triggers[] + next_review_trigger；promote lifecycle 到 active；emit evidence_record per counter_evidence
- **evidence-reviewer**：独立 AI gate，验证后在 thesis-verifier 和 thesis-adversary 各产出的 evidence_record 上执行

### Theme 子集群（2 agent，条件触发）

- **research-theme-discovery-scanner**：扫 messages_index.jsonl 在显式 as_of_utc 窗口内，聚类为尚未被任何 theme 覆盖的 candidates
- **research-theme-bootstrapper**：两阶段。Stage A（仲裁）：给定 candidate，在 5 个 similarity dimension 上扫所有现有 theme，提议 admit_new / merge / narrow / carve_out / subordinate。Stage B（执行）：给定 owner 的 round-2 决策，执行选定分支。Stage B 看不到 Stage A 的 proposal，只看 owner 确认的计划

### 三条 Theme 创建路径

1. PM 驱动：routing → report-owner round-1 → bootstrapper Stage A → owner round-2 → bootstrapper Stage B
2. AI 底部向上：routing → discovery-scanner → PM 选 candidate → report-owner round-1 → bootstrapper Stage A → owner round-2 → bootstrapper Stage B
3. 更新现有 theme：routing → report-owner → knowledge-and-package-curator（无 bootstrapper）

---

## Independent Research 循环（Digestion）

`digestion-independent-researcher` 拥有跨资产独立研究的完整循环：

```
research question
  → asset identity
  → local archive search
  → optional external search
  → message archive link
  → asset source packet
  → domain route selection
  → selected domain expert
  → expert-owned digestion output
  → downstream handoff
```

核心原则：**Route BEFORE Source Card。** 先选 domain route，再把 source packet 交给匹配的 expert。Expert 拥有自己的 Source Card、Typed Claim、Expert Artifact schema。

默认路由：
- Listed company / public equity：`company_expert:default_company_dossier`
- Private company / pre-IPO：`private_company_expert:private_company_dossier`
- Crypto project：`crypto_project_expert`
- Thesis/theme lifecycle：`thesis_theme_expert`
- Missing route：`blocked_missing_expert`

Blocked outputs（researcher 不能直接写）：active thesis lifecycle state、verified evidence record、final theme report ownership、portfolio action、sizing、execution plan、order instructions。

---

## Charter：宪法级约束

`the_charter.md` 是整个系统的 supreme law。上面各层的规则都源于 Charter 的对应 section。

### 四个 first-class 对象

| 对象 | 定义 | 关键约束 |
|---|---|---|
| Theme | 值得持续跟踪的长期结构性研究问题 | 持久记忆组织器，不是 source summary，不是 trade |
| Thesis | 某 Theme 下的可证伪信念 | 含 causal chain 和 refutation condition |
| Scenario | 某 Thesis 下的前瞻预测路径 | 有 trigger signal 和 causal node |
| Evidence | belief-state change record | 不是 log；只记录实际 belief delta；必须同等记录 counter-evidence |

### Authority 分离

| 层 | 拥有者 | 内容 |
|---|---|---|
| Belief Layer | PM | Thesis/Scenario lifecycle、pm_conviction、scenario_role、market_state、boundary decision |
| Fact Layer | System | 字段验证、一致性、timestamp normalization、reference integrity、signal hitting、ledger drafting、freshness checking |

关键边界：signal hitting 是 Fact Layer；Scenario verification 是 Belief Layer。系统不能自动把 signal promote 为 validated Scenario。

### 其他宪法级规则

- **Archive Principle（§3）：** Single source of truth；append-only，不 rewrite
- **Precision Discipline（§5）：** belief strength 用 enum（high/medium/low/exploratory），threshold 用 prose，magnitude 用三级 enum（minor/moderate/major）。禁止无法审计的浮点精度
- **Fail Loud（§4）：** 不静默 fallback。timestamp 语义不匹配、必填字段缺失、authority violation，立即 raise
- **No Orphans（§9）：** 每个 PM-facing product 必须是 artifact graph node（有 path、freshness、builder、owner），被 skill 或 workflow 引用，routing 层可达

---

## 从 0 到 1 的复用路径

### 最小可用配置

1. 复制 `09_soul/core/`（SOUL.md + USER.md + COMMUNICATION.md）
2. 在新项目创建 `09_<agent>/core/PROJECT_ADAPTER.md`
3. 创建 CLAUDE.md，指向 session startup protocol
4. 复制 `routing-task-mode-router` skill，调整路由表
5. 定义第一条 task mainline 的 skill

此时你有：persona、沟通契约、routing、一条可执行的 mainline。

### 加治理

6. 复制 `src/audit/base.py`，定义项目需要的母类子集
7. 复制 `agent-the-skill-management`，为新 skill 提供写作审阅循环
8. 复制 `agent-the-contract-audit`，为模块提供三层审计
9. 复制 `support-external-agent-builder`，为外部 worker 提供 runner 架构

### 加内容层

10. 按需建 Material Catalog 子契约（从 `material_00_overview.md` 开始）
11. 按需建 Expertise 子契约（从 `expertise_00_overview.md` 开始）
12. 按需建 Artifact Graph node 定义

### 加 Freshness

13. 复制 `research-theme-staleness-sweeper`（调整 object type 和 default cadence）
14. 在需要 freshness gate 的 mainline skill 中加入硬 freshness check
15. 部署 `tradectl timeaudit --scan-schemas` 或等价 linter
