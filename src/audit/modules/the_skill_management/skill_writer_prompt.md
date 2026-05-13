# SKILL.md Writer

Date: {{WRITE_DATE}}
Module: {{MODULE_ID}}
Target: {{SKILL_PATH}}

## Task

Write a complete SKILL.md file for the target path above.

If an existing SKILL.md is provided in §5, treat it as the current version to update.
If none exists, write from scratch.

## Writing Principles (governance §3)

These are the primary quality bar. Every section you write must satisfy these principles. They take priority over structural completeness.

1. **结果确定性优先于过程确定性**。SKILL.md 回答四个核心问题：目标（一句话）、验收标准（agent 能自行判断"做完了没有"）、可用资源（工具、文件、边界）、输出规格（产物的格式、路径、schema）。其他内容围绕这四项展开。步骤式流程只在顺序本身会改变结果时保留。
2. **Enabling guidance, not SOP**。读者是有推理能力的 agent。方法论以"建议"和"约束"形式出现，不硬编码为唯一过程。删掉一段后 agent 完成任务的质量不下降，那段是 padding。
3. **Contract first, compression second**。SKILL.md 是 AI-facing contract。6 个必须能回答的问题：这一层干什么、什么时候进入、进入后先读什么、应该产出什么、和相邻层怎么交接、哪些邻近概念容易混淆。只有 6 个都清楚时再考虑能不能更短。
4. **钉不变量，不钉实现路径**。必须钉死：canonical 路径与命名、identity 字段、上游依赖身份与新鲜度契约、canonical builder、相邻 surface 的接口形状。留开给 agent：具体 prose 怎么写、判断路径与权衡、中间过程组织、证据展开深度。
5. **边界有两面**。每条关键边界同时给出：禁止式（不要做 X）和检测式（无声违反时长什么样）。只有禁止式没有检测式 = agent 走捷径时无人察觉。
6. **先定义读者读完后的判断增益**。每段文字应该提升 agent 的判断能力。写之前先回答：agent 读完后应该更清楚什么、更能区分什么、哪种误判应该更容易被排除。
7. **下游 prompt 只放 task-plane**。如果 SKILL.md 包含发给 subagent 的 prompt 模板，只放 worker 完成任务必须知道的信息。编排细节、persona 来源标签、内部 routing rationale 留在 caller 上游。

## Reader-State 5 Questions

Before writing each major section, answer these questions. If none of them has an answer, that section only adds volume, not value.

1. Agent 读完后应该更清楚什么？
2. Agent 应该更能区分什么？
3. 哪种误判现在应该更容易被排除？
4. Agent 接下来应该更容易做什么判断或决定什么下一步？
5. 如果答不出来，这段文字是 padding，删。

## Style Contract (governance §6)

1. **务实、理性、克制**。不堆砌宏大词藻，不用文学性比喻。
2. **不用破折号**（em dash / en dash / double hyphen）。拆成两句或用冒号。
3. **正向陈述**。与其说 X 不是 Y，不如直接说 X 是什么。
4. **Label 注解**。任何编号标签（tool id、artifact id、gate id）首次出现必须 inline 注明它是什么。
5. **No process leak**。不出现"上一轮讨论"、"本次 dogfood"、"我们刚才决定"之类对话归因。SKILL.md 是稳定 artifact，读者无对话上下文。
6. **No editorial meta**。不出现"本次更新"、"相比上一版"、"这次补充了"。写关于任务和世界，不写关于稿件本身。

## Surface Authority (governance §4)

SKILL.md writes: AI runtime behavior instructions, trigger conditions, required inputs, objective, policy, stop condition, completion standard, tool/validator refs (by id), workflow steps, boundary, known traps.

SKILL.md does not write: design reasoning (Design Doc owns that), typed ref lists (Registry owns that), class definitions (base.py owns that), code implementation.

## Required Content Areas (governance §5)

**Agent SKILL.md** has 4 top-level areas and 3 Workflow sub-areas:

Top-level: Identity, Objective, Owned Workflow, Boundary.

Owned Workflow sub-areas (Agent's judgment gains on the execution backbone):

| Sub-area | Question it answers |
|---|---|
| Steps & Gates | What steps in what order, which tool/validator at each step, what gate conditions between steps |
| Policy | At branching points, what signal drives which path |
| Stop Condition | What conditions terminate execution (success and failure) |
| Completion Standard | After termination, what observable state proves the run was complete |

Each sub-area answers exactly one question. If two sub-areas are saying the same thing, their scope definitions are wrong.

**Skill SKILL.md** must cover 5 areas: Identity, Required inputs, Output specification, Completion standard, Boundary.

Read the full governance document (§2) for complete definitions. Then read the module's design doc (§3) and registry (§4) to understand the specific skill/agent.

## §2 Governance

<governance>
{{GOVERNANCE}}
</governance>

## §3 Module Design Doc

<design_doc>
{{DESIGN_DOC}}
</design_doc>

## §4 Module Registry

<registry>
{{REGISTRY}}
</registry>

## §5 Existing SKILL.md

<existing_skill>
{{EXISTING_SKILL}}
</existing_skill>

## Output Requirements

1. Output the complete SKILL.md content (not a diff, not a summary, not commentary)
2. Include YAML frontmatter: name, type (agent or skill), description
3. Cover all required content areas per governance §5.1 (Agent) or §5.2 (Skill)
4. Respect surface authority: no design reasoning (Design Doc owns that), no typed ref lists (Registry owns that), no class definitions (base.py owns that)
5. After writing, perform self-review per governance §9.2:
   - Structure: Can the agent answer the 6 contract questions (governance §3.3)? Are all required content areas present?
   - Content: Are invariants pinned? Do boundaries have detection signatures? Is the completion standard observable and testable?
   - Style: No em dash, no process leak, no editorial meta, labels annotated on first mention?
6. Fix any self-review issues before final output
7. Output only the SKILL.md content. No wrapper, no explanation, no "here is the file" preamble
