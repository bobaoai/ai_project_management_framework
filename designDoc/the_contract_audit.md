---
title: Contract Audit Architecture
status: active_draft
layer: T0
t0_layer_id: the_contract_audit
canonical_owner: designDoc/the_contract_audit.md
reader_persona:
  - System Builder
  - Design Doc Author
  - Design Doc Reviewer
  - Runtime Projection Maintainer
---

# Contract Audit Architecture

## 0. Contract Capsule

```yaml
title: Contract Audit Architecture
layer: T0
t0_layer_id: the_contract_audit
status: active_draft
canonical_owner: designDoc/the_contract_audit.md
registry_path: src/audit/modules/the_contract_audit/registry.py
scope: three-surface model, typed registry architecture, Design Doc / Registry / SKILL.md synchronization discipline, three-layer audit mechanism, registry inheritance model for ~60 modules
non_goals:
  - Design Doc writing freedom and review gate procedure (the_design_doc_management)
  - artifact node identity, dependency edges, freshness predicates (the_artifact_graph)
  - TradeCLI code-admission discipline (the_tradecli_code_management)
  - external agent management (the_external_agent_management)
  - domain-specific material semantics or T1 workflow behavior
  - PM belief, investment judgment, or report prose quality
inputs:
  - Design Doc drafts and materially updated active Design Docs
  - A18 class hierarchy (Tool < Skill < Workflow < Agent)
outputs:
  - three-surface-per-module standard (Design Doc / Registry / SKILL.md)
  - registry inheritance model (base.py -> shared_contracts.py -> modules/<X>/registry.py)
  - three-layer audit mechanism (capsule recovery + structural validation + semantic audit)
  - Design Doc / Registry synchronization discipline
truth_surfaces:
  - src/audit/base.py
  - src/audit/modules/the_contract_audit/registry.py
  - src/audit/modules/the_skill_management/registry.py
  - src/audit/modules/research_technical/registry.py
  - .claude/skills/agent-the-contract-audit/SKILL.md
  - .claude/skills/agent-the-skill-management/SKILL.md
  - .claude/skills/agent-research-technical-analysis/SKILL.md
downstream_consumers:
  - all T1 module Design Docs with typed registries
  - the_design_doc_management (capsule field additions, review procedure additions)
open_decisions:
  - whether ContractFamilySpec belongs in base.py or shared_contracts.py
  - manifest.py cross-module dependency graph schema
review_gate: design-doc-reviewer
```

## 1. Scope

~60 个功能模块的 design intent（Design Doc prose）、typed contract（Python registry）、AI runtime behavior（SKILL.md）需要保持同步。

本文档定义同步架构：三 surface 模型、registry 继承结构、同步纪律、三层审计机制。

本文档不干涉 Design Doc 写作方式（[T0-DDM] 的职责），不定义具体模块的 registry 内容（各模块 Design Doc + registry 的职责）。

## 2. Non-scope

| 职责 | 归属 |
|---|---|
| Design Doc 写作自由、review gate 流程、Contract Capsule recovery | the_design_doc_management [T0-DDM] |
| Artifact node identity、dependency edges、freshness predicates | the_artifact_graph [T0-AG] |
| TradeCLI code-admission discipline | the_tradecli_code_management [T0-TCM] |
| External agent management | the_external_agent_management [T0-EAM] |
| Domain-specific material semantics、T1 workflow behavior | 各 T1 domain owner |
| PM belief、investment judgment、report prose quality | PM / domain reviewer |

## 3. 三 Surface 模型

### 3.1 每模块三种 surface

| Surface | 数量 | 承载什么 |
|---|---|---|
| **Module Design Doc** | 1 | design intent, class assignment reasoning, boundary prose, authority direction, failure signatures |
| **Python Registry** | 1 | 全部 typed objects (Design, Material, Artifact, Tool, Skill, Agent, Workflow, Validator), structural validation |
| **Production SKILL.md** | 1 per Agent/Skill with runtime behavior | AI runtime execution instructions, behavior prose, completion standard |

No surface duplicates another's authority.

### 3.2 Surface ownership

```text
DesignDoc → what / why / boundary / authority / class assignment reasoning
Registry  → typed refs / class definitions / structural validation
SKILL.md  → runtime behavior instructions for AI execution
Code      → deterministic execution
```

### 3.3 Design Doc 写什么

Design intent、class assignment reasoning（为什么 writer 是 Tool 而不是 Skill）、Material/Artifact boundary reasoning、Agent boundary prose（objective, policy, stop condition 的设计意图）、failure signatures、authority direction。

Design Doc 可以 mention 具体的 class id，但不维护 ref id 完整列表。Ref lists 只在 registry 维护一份。

### 3.4 Design Doc 不写什么

- Ref id 完整列表（registry 权威）
- Step-level input/output tables（registry WorkflowStep 权威）
- Runtime behavior instructions（SKILL.md 权威）
- Typed field values（registry class 权威）

### 3.5 Registry 写什么

所有 class id、typed ref lists、class field values、structural validation logic。

### 3.6 Registry 不写什么

Design reasoning、boundary justification、failure signatures（prose）、runtime behavior instructions。

### 3.7 SKILL.md 写什么

AI runtime behavior、completion standard、boundary rules（给 AI 执行时参考）。

### 3.8 SKILL.md 不写什么

Design reasoning（为什么 writer 是 Tool）、typed refs（在 registry 里）。

## 4. Class Hierarchy

### 4.1 A18：Tool < Skill < Workflow < Agent

Registry class hierarchy 来自 A18 [Axiom:A18]。

```text
Tool < Skill < Workflow < Agent
```

Tool 是手脚。Skill 是手艺。Workflow 是流水线。Agent 是有判断权的执行主体。

每个 registry object 的 class assignment 必须通过 A18 §7 四句判定：

1. 它只是执行原子动作吗？→ Tool。
2. 它把定义好的输入变成定义好的输出，有稳定方法吗？→ Skill。
3. 它按固定步骤推进吗？→ Workflow。
4. 它根据目标、状态和反馈决定下一步吗？→ Agent。

如果第四句不成立，不要叫 Agent。如果一个 Skill 开始决定多步调度，它在侵占 Workflow。如果一个 Tool 封装了稳定方法、输出契约和检查规则，它应该是 Skill。

### 4.2 Class assignment 是设计决策

Class assignment 决定审计含义：

- Tool 的输出是"执行结果"——不需要检查 objective 或 stop condition
- Skill 的输出是"能力产出"——需要检查 input/output contract 和 failure boundary
- Workflow 的输出是"流程完成"——需要检查 step order 和 gate assertions
- Agent 的输出是"目标完成或升级"——需要检查 objective、state、policy、stop condition

Registry 的 class assignment 必须和 Design Doc 的声明一致。Design Doc 说"writer 是 Tool"（因为 judgment 在 external model），registry 里 writer 必须是 `Tool` class。

### 4.3 Axiom 锚定

**A05 文档即长期记忆** [Axiom:A05]：Design Doc prose 是 design intent 的上游权威。Registry 是 prose 的 typed 投影，不是反过来。

**V02 可验证性是信任的地基** [Axiom:V02]：审计让变更可检测，不是消灭自由度。三层审计是分层可验证的设计。

**T10 Index 优先，AI 填补语义缺口** [Axiom:T10]：Code audit（deterministic）处理 ID 存在性、type safety、naming grammar。AI audit 只在语义级联处介入：class assignment 变更、Agent boundary 变更。

## 5. Registry 继承模型

### 5.1 三层结构

```
src/audit/base.py                     — mother classes, type aliases, support classes, shared validation
src/audit/shared_contracts.py         — cross-module shared objects (upstream constraint refs, shared Materials)
src/audit/modules/<module>/registry.py — per-module instances only
src/audit/manifest.py                 — cross-module dependency graph
```

**base.py**：定义一次、全局共享。8 种 mother class、type aliases、CodeBinding、Gate、HistoryRef、MaterialFileSpec、ContractFamilySpec、DogfoodFixtureSpec、参数化 validation。

**shared_contracts.py**：跨模块共享对象。模块 A 引用模块 B 的对象必须通过 shared_contracts，不能直接 import 模块 B 的 registry。

**modules/\<module\>/registry.py**：只放该模块自己的实例。没有 class 定义、type aliases。

**manifest.py**：跨模块 dependency graph。哪个模块引用了哪些 shared objects，哪些模块之间有上下游关系。

### 5.2 8 种 Mother Classes

| Class | Meaning | Owns | Does not own |
|---|---|---|---|
| Design | Module-level design doc pointer | design_id, owner_ref, purpose, role, scope, ref lists | runtime execution, material content |
| Material | Durable multi-file content asset | material_id, scope, file_parts, gates | input/output flow |
| Artifact | Single generated file or runtime output | artifact_id, artifact_kind | multi-file meaning |
| Tool | Atomic execution handle (A18 Layer 1) | tool_id, purpose, code_bindings | judgment, orchestration |
| Skill | Reusable capability with local method (A18 Layer 2) | skill_id, projection_path, input/output refs, tool_refs, gates | autonomous objective, state |
| Workflow | Fixed execution sequence (A18 Layer 3) | workflow_id, steps, input/output refs, tool/validator refs, gates | adaptive policy, PM belief |
| Agent | Goal-directed runtime actor (A18 Layer 4) | agent_id, objective, state_refs, policy, stop_condition, skill/tool refs | material schema, raw data truth |
| Validator | Validation handle with explicit gate | validator_id, input/output refs, code_bindings, gates | workflow order |

### 5.3 设计原则

1. **Typed Python**：所有 ref list 是 typed dataclass list，不是 string list。
2. **显式共享**：shared_contracts.py 是唯一的跨模块共享点。
3. **独立验证**：每个模块的 registry 可以独立 validate。Shared objects 是 frozen dataclass，import 不触发 side effect。
4. **计算图**：manifest.py 记录依赖关系，支持"模块 A 的 registry 变了，哪些下游模块需要检查"。

## 6. 同步纪律

### 6.1 同步方向

```text
Design Doc prose → (人/AI 判断) → Registry → (code validation) → Code / SKILL.md
```

Design Doc 是上游权威。Design Doc 改变 class assignment，registry 必须跟着改。反方向不成立。

Registry 里出现了 Design Doc 没有提到的 class instance，这是审计 finding。

### 6.2 Prose 自由原则

Design Doc 作者保持自由写作（[T0-DDM] §1 核心立场）。审计框架下四条规则：

1. Design Doc **可以**省略 registry 中存在的对象。作者不被强制 mention 每个 artifact id。
2. Design Doc **不可以**引用 registry 中不存在的 class id。
3. Design Doc **可以**用任何叙事结构。不强制 section layout。
4. Design Doc **不可以**从 registry 自动生成。

### 6.3 Prose 三种内容性质

| 性质 | 例子 | Cascade 到 registry |
|---|---|---|
| Structural decision | "writer 是 Tool，不是 Skill" | 是。Registry class assignment 必须匹配 |
| Boundary declaration | "这个模块不生产 Evidence" | 可能。检查 registry 是否反映该边界 |
| Rationale/context | "我们选择 Tool 是因为 judgment 在 external model" | 否。解释，不触发 registry 变更 |

审计检查前两种。第三种是写作自由。

## 7. 三层审计

### 7.1 第一层：Capsule Recovery

**执行者**：[T0-DDM] design-doc-reviewer
**触发**：Design Doc finalization, promotion, or material update
**内容**：从 Design Doc 恢复 Contract Capsule（recoverable fields + registry_path）

检查 Design Doc 作为文档的可审计性。与 registry 无关。

### 7.2 第二层：Registry Structural Validation

**执行者**：自动（Python validation function）
**触发**：registry file 变更

检查项：

1. **ID 命名语法**：`tool_*`, `skill_*`, `agent_*`, `workflow_*`, `material_*`, `artifact_*`, `validator_*`, `design_*`
2. **Type safety**：所有 ref list 包含正确类型的 typed objects
3. **Code binding path 存在性**
4. **A18 层级完整性**：Agent 必须有非空的 `objective`, `policy`, `stop_condition`；Skill 必须有 `projection_path`
5. **Blocked names**：废弃 id 不能复活
6. **Material file part validation**：MaterialFileSpec roles 在 allowed list 里

确定性，零 AI 成本。

### 7.3 第三层：语义对齐（独立审计）

**执行者**：独立 AI reviewer（单独进程，无对话上下文，`claude -p --model claude-opus-4-7`）
**触发**：核心文件变更且第二层通过后
**输入**：本文档（审计方法论）+ Design Doc + Registry + base.py + SKILL.md，自动组装为 self-contained prompt

七项检查：

1. **Class assignment 一致性**：Design Doc 声明的 class type 和 registry 的 class type 匹配
2. **Agent boundary 完整性**：objective, policy, stop condition 跨 surface 语义等价
3. **Skill 层一致性**：Design Doc Skill 声明和 registry Skill 实例数匹配
4. **Workflow step 对齐**：步骤数、描述、顺序匹配
5. **Material / Artifact boundary**：boundary reasoning 和实际 class assignment 匹配
6. **三 surface separation**：Design Doc 不含 ref lists，registry 不含 prose
7. **SKILL.md 对齐**：runtime behavior 与 Design Doc boundary 和 registry refs 一致

每项 finding 带 severity：`block`（surface 矛盾）、`fix`（不一致但不阻塞）、`note`（观察）。

模块通过 = 0 blocks + 0 fixes。

### 7.4 触发链

```text
核心文件修改 → 第二层 structural validation（自动）
             → 第三层语义对齐（独立 reviewer）
             → blocks/fixes → fix → 重新审计直到通过
```

`shared_contracts.py` 变更 cascade 到所有引用该 shared object 的模块。

### 7.5 审计工具链

Prompt 自动组装：`audit.tools.assemble_contract_audit` 从 registry 文件自动发现模块配置（`MODULE_DESIGN_DOC` 常量 + Agent `owner_ref`），读取 5 个文件，替换模板占位符，输出 self-contained prompt。

```bash
# 运行审计
designDoc/temp/smoke/run_audit.sh <module_id>

# 发现已注册模块
python -m audit.tools.assemble_contract_audit --discover

# 对比硬编码 vs 发现
python -m audit.tools.assemble_contract_audit --diff
```

审计 Agent（`agent_the_contract_audit`）拥有审计循环：调用 reviewer Tool → 解析 findings → 修复 → 重新审计 → 直到通过或 3 轮后升级到 PM。

## 8. 对 DDM 的贡献

### 8.1 新增 registry_path 字段

```yaml
registry_path: <path to per-module Python registry file>
```

Recoverable field。没有 registry 的 Design Doc 不需要填。

### 8.2 新增 Check Registry Alignment 审计步骤

当 Design Doc 声明了 `registry_path`：

1. Registry file 存在且可 import
2. Design Doc prose 中 mention 的 class ids 在 registry 中存在
3. Class assignment 声明和 registry class type 匹配
4. Skill 层声明和 registry Skill 实例数匹配

### 8.3 新增 Surface Ownership 审计

Design Doc 维护了完整 ref id 列表 → flag `ref_list_belongs_in_registry`。

## 9. 相邻 T0 边界

| T0 层 | 本文档贡献 | 分界 |
|---|---|---|
| **the_design_doc_management** | registry_path 字段、Check Registry Alignment 步骤、surface ownership 更新 | 本文档不修改 [T0-DDM] 的写作自由核心立场 |
| **the_artifact_graph** | 无 | Registry `Artifact` 是 audit-time class assignment；[T0-AG] artifact node 是 runtime dependency closure |
| **the_tradecli_code_management** | 无 | Registry 检查 code binding path 存在性；[T0-TCM] 定义 code quality 和 admission 标准 |
| **the_external_agent_management** | 无 | Registry 记录 Tool identity；[T0-EAM] 定义 external agent prompt boundary 和 runtime mechanics |

## References

- `[T0-DDM]` [Design Doc Review Gate Contract](the_design_doc_management.md)
- `[T0-AG]` [Artifact Dependency Closure Contract](the_artifact_graph.md)
- `[T0-TCM]` [TradeCLI Code Management](the_tradecli_code_management.md)
- `[T0-EAM]` [External Agent Management](the_external_agent_management.md)
- `[Axiom:A18]` [Skill / Agent 边界不可混淆](../09_claude/axioms/a18_skill_agent_boundary.md)
- `[Axiom:A05]` [文档即长期记忆](../09_claude/axioms/a05_docs_long_term_memory.md)
- `[Axiom:V02]` [可验证性是信任的地基](../09_claude/axioms/v02_verifiability.md)
- `[Axiom:T10]` [Index 优先，AI 填补语义缺口](../09_claude/axioms/t10_index_first_ai_for_gaps.md)
- `[Smoke-Design]` [Research Technical Module Smoke Design](temp/smoke/designDoc/research_20_technical_module_smoke_design.md)
- `[Smoke-Registry-Base]` [Audit Base Classes](temp/smoke/src/audit/base.py)
- `[Smoke-Registry-RT]` [Research Technical Registry](temp/smoke/src/audit/modules/research_technical/registry.py)
- `[Agent-RTA]` [Agent Research Technical Analysis SKILL.md](../.claude/skills/agent-research-technical-analysis/SKILL.md)
