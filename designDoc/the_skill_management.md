---
title: Skill Writing Governance
status: active_draft
layer: T0
t0_layer_id: the_skill_management
reader_persona:
  - System Builder
  - Skill Author
  - Skill Reviewer
---

# Skill Writing Governance

## 0. Contract Capsule

```yaml
title: Skill Writing Governance
layer: T0
t0_layer_id: the_skill_management
status: active_draft
canonical_owner: designDoc/the_skill_management.md
registry_path: src/audit/modules/the_skill_management/registry.py
scope: SKILL.md surface governance — writing principles, required content areas, reviewer contract, registry alignment, style rules
non_goals:
  - Design Doc writing freedom and review gate (the_design_doc_management)
  - Registry structure and structural validation (the_contract_audit)
  - External agent execution mechanics (the_external_agent_management)
  - Domain-specific skill content and behavior
  - Portable bestpractice definitions (09_soul/skills/bestpractice_skill_writing.md owns those)
inputs:
  - SKILL.md drafts (new or materially updated)
  - module Design Doc (upstream design intent)
  - module registry (typed object set)
outputs:
  - SKILL.md writing standard for this project
  - skill-reviewer verdict and findings
truth_surfaces:
  - 09_soul/skills/bestpractice_skill_writing.md
  - 09_claude/core/COMMUNICATION.md
  - designDoc/the_contract_audit.md
  - 09_soul/skills/bestpractice_doc_self_review.md
  - 09_soul/skills/bestpractice_reader_state_and_judgment_gain.md
  - 09_soul/skills/bestpractice_prose_without_editorial_meta.md
  - 09_soul/skills/bestpractice_prompt_boundary.md
downstream_consumers:
  - all SKILL.md authors and agents
  - skill-reviewer
open_decisions:
  - whether skill-reviewer runs as external AI or in-session sub-reviewer
review_gate: design-doc-reviewer
```

## 1. Scope

本文档管 SKILL.md surface：三 surface 模型里的第三面。

```text
DesignDoc → what / why / boundary / authority / class assignment reasoning
Registry  → typed refs / class definitions / structural validation
SKILL.md  → runtime behavior instructions for AI execution   ← 本文档管这里
```

核心立场：

```text
Skill 作者按写作原则自由写 prose。
Skill Reviewer 负责加 audit 结构、检查 surface alignment。
```

作者不被要求在初稿就写出 registry id 或 audit 结构。Reviewer 在 review gate 补上或提出缺口。

## 2. Non-scope

| 职责 | 归属 |
|---|---|
| Design Doc 写作自由、review gate、Contract Capsule | the_design_doc_management [T0-DDM] |
| Registry class 定义、structural validation、三层审计 | the_contract_audit [T0-CA] |
| External agent 执行机制（model/CLI identity） | the_external_agent_management [T0-EAM] |
| Portable 写作方法论（5 原则、验收标准、陷阱表） | bestpractice_skill_writing [Portable-Skill-Writing] |
| 沟通风格（语言、label 注解、pre-response gate） | COMMUNICATION.md [COMM] |
| Domain-specific skill 内容（分析框架、领域知识） | 各 domain owner |

## 3. 写作原则

本节从 [Portable-Skill-Writing] 提取本项目适用的 standing rules。原则的完整推导、例子和 anti-pattern 见源文件。

### 3.1 结果确定性优先于过程确定性

SKILL.md 回答四个核心问题：

1. **目标**：一句话说清楚
2. **验收标准**：agent 能自行判断"做完了没有"
3. **可用资源**：工具、文件、边界
4. **输出规格**：产物的格式、路径、schema

其他内容围绕这四项展开。步骤式流程只在顺序本身会改变结果时保留。

### 3.2 Enabling guidance, not SOP

SKILL.md 的读者是有推理能力的 agent。每一段文字增加 agent 成功完成任务的概率。

- 方法论建议以"建议"和"约束"形式出现，不硬编码为唯一过程
- 已知陷阱只记录真实发生过的失败模式，不预测
- 删掉一段后 agent 完成任务的质量不下降 → 这段是 padding，删

### 3.3 Contract first, compression second

SKILL.md 是 AI-facing contract。6 个必须能回答的问题：

1. 这一层干什么
2. 什么时候进入
3. 进入后先读什么
4. 应该产出什么
5. 和相邻层怎么交接
6. 哪些邻近概念容易混淆

只有 1-6 都清楚时再考虑能不能更短。不为视觉清爽牺牲 contract。

### 3.4 钉不变量，不钉实现路径

必须钉死：canonical 路径与命名、identity 字段、上游依赖身份与新鲜度契约、canonical builder、相邻 surface 的接口形状。

留开给 agent：具体 prose 怎么写、判断路径与权衡、中间过程组织、证据展开深度。

### 3.5 边界有两面

每条关键边界同时给出：

- **禁止式**：不要做 X
- **检测式**：无声违反时长什么样（一个 agent 在产出后能自己回头检查的可观察特征）

只有禁止式没有检测式 = agent 走捷径时无人察觉。

### 3.6 先定义读者读完后的判断增益

SKILL.md 的每一段文字应该提升 agent 的判断能力，不只是增加信息体积。

写之前先回答：agent 读完后应该更清楚什么、更能区分什么、哪种误判应该更容易被排除。如果答不出来，这段文字通常只增加体积不增加价值。

完整推导见 [Reader-State]。

### 3.7 下游 prompt 只放 task-plane

Agent SKILL.md 如果包含发给 subagent 或 external worker 的 prompt 模板，只放 worker 完成任务必须知道的信息（task-plane）。编排细节、组装逻辑、persona 来源标签、内部 routing rationale 留在 caller 上游，不进 prompt。

检测式：worker 输出在 hedge 一些 caller 已经保证的事、或在描述自己怎么工作。这是 control-plane 漏进 prompt 的副产品。

完整推导见 [Prompt-Boundary]。

## 4. Surface Authority

### 4.1 SKILL.md 写什么

共有（Agent 和 Skill）：

- AI runtime behavior instructions
- 触发条件和进入条件
- Completion standard（可观察的完成标准）
- Boundary（does / does not own）
- Known traps（真实失败模式）

Agent 追加（A18 Layer 4 叠加在 Workflow 上）：

- Objective（一句话目标）
- Owned Workflow（步骤序列、gate 条件、每步的 tool/validator refs）
- Policy、stop condition（Workflow 上的判断增益）

Skill 追加（A18 Layer 2）：

- Required inputs（先读什么、读取顺序）
- Output specification（产物格式、路径、schema）

### 4.2 SKILL.md 不写什么

- **Design reasoning**（为什么 writer 是 Tool 而不是 Skill → Design Doc 权威）
- **Typed ref lists**（完整的 class instance 列表 → Registry 权威）
- **Class definitions**（母类定义 → base.py 权威）
- **Code implementation**（函数逻辑 → Code surface 权威）
- **Design Doc 的 boundary justification**（只引用结论，不重复推理）

SKILL.md 可以 mention Design Doc 的结论（如"writer 是 Tool"），但不承载推理过程。推理变了 → 先改 Design Doc → 然后 SKILL.md 跟着改。

## 5. Required Content Areas

以下不是固定模板，是成熟 SKILL.md 需要覆盖的内容区域。Section 名和顺序由作者决定。

### 5.1 Agent SKILL.md

Agent 是有判断权的执行主体（A18 Layer 4）。Agent 拥有一个 Workflow（A18 Layer 3），并在 Workflow 上叠加 objective、state、policy、stop condition。SKILL.md 的内容结构反映这个叠加关系。

**顶级区域**

| 区域 | 说明 | 缺失后果 |
|---|---|---|
| **Identity** | 做什么、不做什么、什么时候进入、先读什么 | Agent 边界不清，侵占相邻 skill 或被相邻 skill 替代 |
| **Objective** | 一句话目标 | 无法判断 Agent 是否完成 |
| **Owned Workflow** | 执行层容器（A18 Layer 3），下含步骤序列和三个判断增益子区域 | Agent 不知道手里有什么工具，不知道执行顺序 |
| **Boundary** | 不拥有什么，每项配检测签名 | 侵占相邻 surface 的权威 |

**Owned Workflow 子区域**

Workflow 是 Agent 的执行骨架。以下子区域是 Agent（Layer 4）在骨架上叠加的判断增益。

| 子区域 | 回答的问题 | 缺失后果 |
|---|---|---|
| **Steps & Gates** | 按什么顺序调用哪些 tool/validator，步骤间的 gate 条件是什么 | Agent 不知道执行顺序和可用工具 |
| **Policy** | 当 Workflow 到达分叉点时，Agent 根据什么信号选择哪条路径 | Agent 退化为 Workflow，失去 adaptive decision |
| **Stop Condition** | 什么条件满足时 Workflow 终止（成功和失败各自的终止条件） | Agent 无限循环或过早退出 |
| **Completion Standard** | Workflow 终止后，哪些可观测状态能证明这次运行是完整的 | 无法自行判断"做完了" |

Policy 是 Agent 和 Workflow 的本质区别。如果 Policy 为空或只是"按步骤执行"，这不是 Agent，是 Workflow。

### 5.2 Skill SKILL.md

Skill 是有稳定方法的可复用能力（A18 Layer 2）。Skill SKILL.md 必须覆盖：

| 区域 | 说明 |
|---|---|
| **Identity** | 做什么、不做什么、什么时候触发 |
| **Required inputs** | 先读什么、读取顺序 |
| **Output specification** | 产物格式、路径、schema |
| **Completion standard** | 可观察的完成标准 |
| **Boundary** | 不拥有什么 |

Skill 不需要 objective/policy/stop_condition（那是 Agent 的）。Skill 的 method 是确定的，不需要 adaptive decision。

### 5.3 Frontmatter

```yaml
---
name: <skill directory name>
type: agent | skill
description: "<one paragraph: what it does, when to use>"
---
```

`type` 必须和 registry class assignment 一致。Design Doc 说"这是 Agent"、registry 有 Agent 实例、SKILL.md frontmatter 写 `type: agent`。

## 6. Style Rules

从 [COMM] 提取 SKILL.md 适用的 standing rules：

1. **务实、理性、克制**。不堆砌宏大词藻，不用文学性比喻。
2. **不用破折号**（em dash / en dash / double hyphen）。拆成两句或用冒号。
3. **正向陈述**。与其说 X 不是 Y，不如直接说 X 是什么。
4. **Label 注解**。任何编号标签首次出现必须 inline 注明它讲什么。
5. **No process leak**。不出现"上一轮讨论"、"本次 dogfood"、"我们刚才决定"之类对话归因。SKILL.md 是稳定 artifact，读者无对话上下文。
6. **No editorial meta**。SKILL.md 写关于任务和世界，不写关于稿件本身。不出现"本次更新"、"相比上一版"、"这次补充了"。如果出处必要，放在 frontmatter provenance 字段，不在正文里。完整反模式清单见 [No-Editorial-Meta]。

## 7. Registry Alignment

SKILL.md 和 registry 的一致性由 [T0-CA] 第三层审计的 Check 7 检查。Standing rules：

1. SKILL.md 中 mention 的每个 workflow id、tool ref、validator ref、artifact id 必须在 registry 中存在且 class type 匹配。
2. SKILL.md 中描述的 Agent boundary 必须和 Design Doc 的 boundary 一致。
3. Registry 分配给该 Agent/Skill 的 entity，SKILL.md 不应遗漏。
4. SKILL.md 不应引用 registry 中不存在的 entity。

方向：Design Doc → Registry → SKILL.md。SKILL.md 不是上游权威。

## 8. Reviewer Contract

### 8.1 何时 review

- 新建 SKILL.md 准备投入使用
- SKILL.md 被 materially updated（目标、policy、workflow、boundary 变更）
- 对应 Design Doc 或 registry 变更后需要检查 SKILL.md 是否还一致
- 审计发现 SKILL.md 和 registry 不对齐

不需要 review：初稿阶段（作者自由写）、纯 typo 修复、注释更新。

### 8.2 Review 检查项

检查项按三阶段分组（对应 reviewer 三阶段审查：结构审 → 内容审 → 风格审）。

**结构审**（结构完整性、id 对齐）

| # | 检查 | Finding |
|---|---|---|
| S10 | Frontmatter 完整（name, type, description） | `incomplete_frontmatter` |
| S2 | SKILL.md 的 type (agent/skill) 和 registry class assignment 一致 | `class_assignment_mismatch` |
| S3 | SKILL.md mention 的 id 在 registry 中存在 | `id_not_in_registry` |
| S4 | Registry 分配的 entity 在 SKILL.md 中被 mention | `missing_entity_mention` |

**内容审**（与 Design Doc / Registry 一致性，写作原则）

| # | 检查 | Finding |
|---|---|---|
| S1 | SKILL.md 的 objective/policy/stop_condition 和 Design Doc 语义等价 | `agent_boundary_drift` |
| S5 | SKILL.md 不含 design reasoning（属于 Design Doc） | `design_reasoning_in_skill` |
| S6 | SKILL.md 不含 typed ref lists（属于 Registry） | `ref_list_in_skill` |
| S7 | Completion standard 可观察、可测试 | `vague_completion_standard` |
| S8 | Policy 区分了 Agent 和 Workflow（非空 adaptive decision） | `agent_without_policy` |

**风格审**（§6 style rules）

| # | 检查 | Finding |
|---|---|---|
| S9 | Style rules 遵守（no em dash, no process leak, label annotation, no editorial meta） | `style_violation` |

### 8.3 Verdict

```text
accept_as_is
accept_with_notes
needs_author_revision
needs_registry_sync
```

`needs_registry_sync`：SKILL.md 描述了 registry 中不存在的 entity，或 registry 有而 SKILL.md 遗漏。需要决定是改 SKILL.md 还是改 registry。决策依据：Design Doc 是上游权威。

## 9. 写作流程

### 9.1 Writer

Writer 是 Tool（A18 Layer 1，`tool_skill_writer`），由 the_external_agent_management 管理的 atomic external agent handle。Writer 的输入：

1. 本文档（写作原则 + surface authority）
2. [Portable-Skill-Writing]（详细原则、验收标准、陷阱表）
3. [COMM]（风格约束）
4. [Reader-State]（读者判断增益优先）
5. [No-Editorial-Meta]（stable artifact 不含 editorial meta）
6. [Prompt-Boundary]（subagent prompt 只含 task-plane）
7. Module Design Doc（design intent, class assignment, boundary）
8. Module registry（typed object set, tool/validator refs）

Writer 按原则自由写 prose。不被要求在初稿就对齐 registry id。初稿可以是叙事、探索、或 proposal 形态。写完后执行 self-review（§9.2）再提交 reviewer。

### 9.2 Self-Review（交付前自审）

Writer 完成初稿后、提交 Reviewer 之前，执行 self-review。Self-review 不是"再读一遍找错别字"，而是结构性检查：reader-state 是否达标、边界是否可检测、是否有 editorial meta 或 process leak。

Self-review 三阶段（从 [Self-Review] 提取）：

1. **结构审**：reader-state 5 问全部跑过。Agent 读完后能更清楚什么？能更区分什么？哪种误判更容易排除？缺少的 required content area（§5）是否有意省略？
2. **内容审**：不变量是否钉死（§3.4）？边界是否有检测式（§3.5）？下游 prompt 是否只含 task-plane（§3.7）？completion standard 是否可观察（§5）？
3. **风格审**：对照 §6 style rules 逐条检查。重点关注 no process leak 和 no editorial meta。

Self-review 发现的问题由 writer 自行修复后再提交 reviewer。如果跳过 self-review，必须在提交时声明跳过原因。

完整 self-review 执行路径见 [Self-Review]。

### 9.3 Reviewer

Reviewer 是 Tool（A18 Layer 1，`tool_skill_reviewer`），由 the_external_agent_management 管理的 atomic external agent handle。Reviewer 在 SKILL.md 准备投入使用时运行。检查 §8.2 的 10 项。Reviewer 可以：

- 补 frontmatter
- 补遗漏的 registry id
- 标注 surface authority violation
- 标注 style violation

Reviewer 不可以：

- 改写 agent 的 policy 或 objective（那是 Design Doc 权威）
- 把 enabling guidance 改写成 SOP
- 删掉 known traps（那是真实经验）
- 为了 audit completeness 压缩 prose

### 9.4 Application Rule

1. 作者自由写初稿
2. 初稿可以不含 frontmatter、不对齐 registry id
3. Writer 完成初稿后执行 self-review（§9.2）
4. Self-review 修复后提交 reviewer
5. Reviewer 在 finalization 前运行（§9.3）
6. Reviewer 补 audit 结构或提出 findings
7. Author 修改后 reviewer 重新检查
8. 通过后 SKILL.md 可投入使用

### 9.5 Automated Workflow

§9.4 是作者视角的完整流程（8 步，包含人工初稿和 self-review）。自动化编排是其中的子集。

`workflow_skill_write_review_loop`（Workflow，A18 Layer 3）是 3 步自动化循环：

| 步骤 | 工具 | Gate |
|---|---|---|
| invoke_writer | `tool_skill_writer` | — |
| invoke_reviewer | `tool_skill_reviewer` | `gate_skill_review_passed` |
| apply_fixes | — | — |

Workflow 不包含 §9.4 步骤 1-3（作者初稿和 self-review），只覆盖步骤 4-7 的自动化部分。

### 9.6 Agent

`agent_skill_management`（Agent，A18 Layer 4）拥有 `workflow_skill_write_review_loop`，在 Workflow 骨架上叠加判断增益。

**Objective**：produce a SKILL.md that passes the independent skill reviewer（accept_as_is 或 accept_with_notes）within 3 rounds。

**Policy**：invoke writer → invoke reviewer → parse verdict → if accept: write SKILL.md, stop。If needs_author_revision: edit SKILL.md based on findings, re-invoke reviewer。If needs_registry_sync: report to user, stop。Max 3 review-edit rounds; if still needs_author_revision after 3, escalate to user。

**Stop condition**：reviewer returns accept_as_is 或 accept_with_notes（pass），或 needs_registry_sync（escalate），或 3 rounds exhausted（escalate to user）。

### 9.7 Artifacts

| Artifact | Kind | 路径 | 设计意图 |
|---|---|---|---|
| `artifact_skill_writer_prompt_template` | config_artifact | `src/audit/modules/the_skill_management/skill_writer_prompt.md` | 组装 writer prompt 的模板，含 governance + module 插槽。单文件模板，非 multi-part content asset，分类为 Artifact 而非 Material。 |
| `artifact_skill_reviewer_prompt_template` | config_artifact | `src/audit/modules/the_skill_management/skill_reviewer_prompt.md` | 组装 reviewer prompt 的模板，含 S1-S10 检查项和 YAML 输出格式。同上分类逻辑。 |
| `artifact_skill_review_log` | audit_artifact | `audit_log/<module_id>/skill_review_<skill_dir>_<date>.yaml` | reviewer verdict 和 findings 的持久化记录。每次 review 生成一个文件，是 audit 输出而非持久内容资产。 |

## 10. Adjacent T0 Boundaries

| T0 层 | 本文档贡献 | 分界 |
|---|---|---|
| **the_design_doc_management** | SKILL.md 不承载 design reasoning | DDM 管 Design Doc 写什么；本文档管 SKILL.md 写什么 |
| **the_contract_audit** | SKILL.md alignment 是三层审计 Check 7 的检查对象 | T0-CA 定义检查机制；本文档定义写作标准 |
| **the_external_agent_management** | SKILL.md 不承载 model/CLI execution metadata | EAM 管执行机制；SKILL.md 只管 task lens |

## References

- `[T0-DDM]` [Design Doc Review Gate Contract](the_design_doc_management.md)
- `[T0-CA]` [Contract Audit Architecture](the_contract_audit.md)
- `[T0-EAM]` [External Agent Management](the_external_agent_management.md)
- `[Portable-Skill-Writing]` [Skill 写作指南](../09_soul/skills/bestpractice_skill_writing.md)
- `[COMM]` [沟通风格指南](../09_claude/core/COMMUNICATION.md)
- `[Axiom:A18]` [Skill / Agent 边界不可混淆](../09_claude/axioms/a18_skill_agent_boundary.md)
- `[Self-Review]` [Doc Self-Review 交付前自审](../09_soul/skills/bestpractice_doc_self_review.md)
- `[Reader-State]` [读者状态与判断增益优先](../09_soul/skills/bestpractice_reader_state_and_judgment_gain.md)
- `[No-Editorial-Meta]` [Prose Without Editorial Meta](../09_soul/skills/bestpractice_prose_without_editorial_meta.md)
- `[Prompt-Boundary]` [Prompt Boundary: Task-Plane vs Control-Plane](../09_soul/skills/bestpractice_prompt_boundary.md)
