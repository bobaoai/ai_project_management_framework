---
title: Task Routing
layer: T0
t0_layer_id: the_task_routing
canonical_owner: designDoc/the_task_routing.md
owned_system_object: RoutingDecision
---

# 任务路由（Task Routing）

Task Routing 帮助 Primary Agent 从用户要取得的结果找到下一步：该读哪份依据、使用哪个现有方法，
或者先问清哪个问题。它提供 Portable T0 的意图导航；具体项目工作流和本地入口由项目自己的工作导航
提供，项目 Charter 指明它的位置。路由本身不执行任务，也不要求先建立 Registry 或运行记录。

## 1. Primary System Flow

```mermaid
flowchart TD
    R["当前请求"] --> C{"是否继续已确定的工作"}
    C -->|是，目标与范围未变| W["Primary Agent 从原工作继续"]
    C -->|新请求或目标改变| I["判断所需结果<br/>找到所属 authority 与入口条件"]
    I -->|目标或职责不能确定| Q["提出具体问题或交给相应负责人决定"]
    I -->|项目业务任务| G["读取项目 Charter 指明的工作导航<br/>定位本地工作入口"]
    I -->|治理工作| B{"用户是否明确指定起点？"}
    B -->|指定文档、Skill 或代码| A["直接进入所属方法"]
    B -->|要求统一规划，或未指定起点| P{"明确要求规划<br/>或需要跨层统筹？"}
    P -->|需要| S["目标 · 授权 · 现有依据<br/>System Change Governance · the-system-change"]
    S --> E["Primary Agent 按已审核计划<br/>进入各步骤所属方法"]
    P -->|不需要| A
    A -->|Design 编写| D["DDM · the-design-authoring"]
    A -->|其他工作| O["按该 authority 的方法处理"]
```

路由判断从当前请求和依据出发，不依赖前一轮对话才能成立。“继续”且任务没有改变时沿用已经明确的
工作；新证据改变目标、范围或负责人时再判断入口，不凭一个相同文件名强行沿用原路径。进入入口之后，
执行可以由 Primary Agent 自己完成，也可以交给受委派的执行会话，双方的分工见第 5.4 节。

### 1.1 从 Portable T0 找到工作方法

下面是各 authority 已声明的入口导航。先读取对应 Design，再使用其中的方法；表格不替代该方法的
进入条件、检查要求或独立审核。

| 用户要取得的结果 | 先读的 authority | 从哪里开始 |
| --- | --- | --- |
| 确定一次修改涉及什么、由谁处理、按什么顺序完成 | [System Change Governance](the_system_change_governance.md) | `the-system-change` 形成计划；计划使用 `system_change_plan_reviewer` 审核后，由 Primary Agent 按步骤推进 |
| 编写或修改 Design Doc | [Design Doc Management](the_design_doc_management.md) | `the-design-authoring`；目标、范围、负责人已明确的授权请求可直接开始，重要含义变更仍须 `design_contract_reviewer` |
| 编写或修改可重复使用的 Skill | [Skill Management](the_skill_management.md) | `the-skill-authoring`；按该 authority 的现行进入条件准备输入，独立审核使用 `skill_candidate_reviewer` |
| 编写或修改 Reviewer prompt | [Review Contract](the_review_contract.md) | `the-review-authoring`；通用规则、目标指令与 checklist 按其要求组成候选，独立审核使用 `reviewer_reviewer` |
| 设计或实现代码、schema、migration，或处理发布部署 | [Software Delivery](the_software_delivery.md) | 从其规定的 Code Design、实现或操作方法进入；工程审核使用 `engineering_change_reviewer` |
| 注册或执行已有 Module、Workflow | [Agent Runtime](the_agent_runtime.md) | 读取当前 Runtime 的随包 client 文档和 runbook，按已有授权使用公开入口 |
| 审查一份已有候选 | 被审对象所属 authority | 使用该对象的指定 Reviewer；Review Contract 只提供共同规则，不是通用审核入口 |
| 执行项目业务、查询或项目工作流 | 项目 Charter 指明的工作导航及其指向的领域依据 | 使用项目已有入口，不在 Portable T0 维护业务路由表 |

`system_change_intake` 表示把目标、授权和现有依据交给 System Change，不要求先有计划或调用机器路由器。
计划通过后，Primary Agent 从每一步取得负责人、方法、输入依赖、审核要求和完成条件；不为每一步
重新做顶层路由。目标方法缺少的实际输入或执行配置由其负责人提供，不靠换一个相似方法绕过。

## 2. Intended Outcomes

Primary Agent 应取得足以继续工作的入口判断。结果应满足以下要求。

1. **任务归属与下一步明确。** 判断说明当前要取得的结果、主责规范、应读取的依据、可使用的方法及选择理由。Design、Skill、Reviewer 指令、工程、Runtime 和项目业务按各自实际对象区分，不凭文件名、模型或相似名称选入口。
2. **已定工作能够持续推进。** 目标和范围未变时沿原路径继续。用户指定文档、Skill 或代码起点时保留该起点；确需统一规划或尚缺决定时，准确保留这些条件。直接进入不会免除所属方法的设计依据、权限、检查和独立审核，也不会自动授权其他层的修改。
3. **Portable 与项目导航各有准确入口。** 共同治理工作可以从本 T0 找到负责规范。具体业务从项目 Charter 指明的工作导航取得本地流程、路径和依赖。项目采用自己的文档、索引或 Registry，不被要求统一机器路由实现；项目 Registry 缺失也不阻止使用 Portable 写作方法。
4. **无法选择时有可处理的缺口。** 目标歧义、职责冲突、缺少引用或工具不可用有具体说明、影响和提供方。候选问题、计划问题与执行故障按真实归属处理，不因调用失败改变任务主线，也不以创建角色或基础设施掩盖缺口。
5. **委派后仍有明确的整体责任。** Primary Agent 继续承担目标、用户沟通、必要决定、协调、结果核对和最终交付。受委派会话在既定范围使用所属方法，缺件时回报，不再次委派同一工作；适用独立审核仍由指定 Reviewer 完成。
6. **交接反映实际完成程度。** 路由判断只证明入口已明确或缺口已交出，不证明下游已经审核、注册、执行或部署，不增加权限。provider、模型、执行配置及委派方式由对应方法、宿主和用户指示决定。导航源更新与安装分别报告结果。

## 3. Owned System Object

Task Routing 拥有任务入口判断，名称为 `RoutingDecision`。输入是当前请求、已有授权，以及判断所需的相关依据。结果说明要取得什么、由哪项规范负责、下一步读哪里或进入什么方法，以及选择理由；不能确定时说明具体缺口。

这项判断可以直接写在当前工作说明中。不要求先建立项目 Registry，也不要求另建持久对象、固定 schema、request ID、hash、审批状态或版本记录。

## 4. Authority

Task Routing 按所需结果与用户指定起点识别入口，并引用各 authority 的实际输入、检查和审核要求。
用户指定从文档、Skill 或代码开始时，不追加 SystemChangePlan 前置；这不取消所属方法自己的
设计依据、授权或独立审核，也不自动授权后续其他层的修改。

System Change 决定需要规划的修改如何拆分和排序；DDM 等 subject authority 决定自己的写作、检查、
独立 Reviewer 和完成要求。具体产品取舍留给用户或其明确委派的负责人。导航到一个入口不授予执行权限。

## 5. Capability and Operation

### 5.1 按指定起点或实际统筹需求进入

先按用户要取得的结果确定负责规范。文件名、模型名和已经打开的工具只能帮助定位，不能替代任务含义。继续同一目标且已有明确路径时沿原工作推进；新请求或实质变化才需要重新选择。

用户指定“先改文档”“先改 Skill”或“先改代码”时，直接进入对应方法，先处理该项已授权工作。
请求整体涉及其他层，不会撤销已经指定的起点；说明后续依赖，在需要扩大范围、改变顺序或补足
实际产品决定时提出具体问题，不自动退回“必须先有 SystemChangePlan”。

用户明确要求统一规划，或没有指定起点且修改需要跨层统筹范围、职责与依赖时，使用
`the-system-change`。输入是目标、授权和现有依据；计划由该方法产生，不是进入它的条件。
未指定起点且无需这种统筹时，直接使用负责所需结果的方法。

直接进入仍须满足实际工作条件。例如文档需要明确的修订目标，Skill 需要明确的重复任务，代码
实现保留 Software Delivery 的 Code Design 与工程审核。缺少这些材料时说明具体缺件；不能把
该方法的工程方案要求解释为必须另有一份 System Change 计划。

### 5.2 找不到或出现冲突时

请求不足以区分不同结果时，问清会改变选择的具体问题。没有可用入口、引用缺失或 authority 相互冲突时，
指出所缺内容及负责方；不能擅自建立 Registry、创造新角色或用名字相近的 Skill 顶替。

已选方法中的候选缺陷返回作者；已有计划漏项或依赖变化返回 System Change；Reviewer、工具或执行配置
不可用则返回对应负责人。执行失败本身不改变任务的逻辑归属，也不意味着设计内容需要改写。

### 5.3 项目自己的路由

项目自己的工作导航提供具体工作流、文件、产物和本地入口，项目 Charter 指明它在哪里、由谁负责。它可以是
文档、索引或 Registry；项目若使用 Registry 或 resolver，其 schema、存储、当前版本和调用方式由项目自己的
设计与代码负责。Charter 未指明工作导航时，按 5.2 说明缺少的入口，交项目 Charter 负责人补齐。本 T0 不要求所有项目采用相同机器路由实现，
也不把项目 Registry 的可用性作为读取 Portable T0 或使用其写作方法的前提。

### 5.4 路由之后的执行分工

入口确定后，直接承接用户请求的 Primary Agent 继续对这项请求负责：确认目标与完成标准，与用户沟通并
取得需要用户作出的决定，协调各步骤，并按所属 authority 的要求核对实际结果和独立审核后向用户交付。
具体执行可以由它自己完成，也可以按项目入口文件（会话启动时读取的项目说明）或宿主提供的委派方法
交给受委派的执行会话。委派不转移上述责任，不改变任务的逻辑归属，也不减免所属方法的进入条件、检查和
独立审核。

受委派的执行会话接到的是入口已经确定的具体工作。它在交给它的授权范围内直接使用所属方法完成，遇到
缺件、冲突或授权不足时回报委派它的 Primary Agent；它不对同一工作重新做顶层路由，也不把这项工作再
委派给其他会话。按所属方法调用独立 Reviewer 是该方法的审核要求，不属于再委派。

是否委派、采用哪个委派方法，以及执行会话使用的 provider、模型和观察方式，由项目入口文件或宿主指定的
委派方法、该方法的参数和用户当次指示决定。Routing 不作这些选择，也不因为委派而维护下游执行状态。

## 6. Completion, Failure, and Recovery

本章判断入口选择和交接是否完成，不判断被路由的任务是否完成。Primary Agent 取得可使用的入口、负责规范和选择依据，或取得具体缺口、影响及提供方后，本次路由判断即可交出。目标方法能否开始、何时完成，继续按其输入、授权和验收要求判断。

目标不明时，只提出会改变入口选择的问题。引用缺失、职责冲突或入口不可用时，保留已确定的结果与依据，将缺口交给第 5.2 节的负责人。不能通过猜测、创建基础设施或换用相似方法宣称完成交接。

候选缺陷、计划缺项和工具故障各自返回所属负责人。工具失败不改变逻辑归属；补齐条件后从原工作继续。只有新证据实际改变目标、范围或责任时，才重新判断入口。委派后的整体责任与继续执行方式按第 5.4 节保持。

Portable 导航文稿的修改、审核和源更新使用 DDM。源更新不表示其他宿主已安装新内容，也不表示任一下游任务已经执行。本规范不维护下游的运行状态。

## 7. Peer Boundaries

| 交接方 | Task Routing 提供 | 对方保留 |
| --- | --- | --- |
| System Change Governance | 需要规划的请求及已知目标 | 修改范围、步骤、依赖顺序和计划审核 |
| Design Doc Management | Design 请求及已有依据 | 进入写作的条件、Design 结构、检查、独立审核和源文件更新 |
| Skill Management | 稳定 Agent 方法的编写或修改请求 | Skill 进入条件、完整性、边界及 Skill Reviewer |
| Review Contract | Reviewer prompt 编写或修改请求 | 通用审核规则、prompt 布局与 prompt Reviewer；不接管其他对象的审核 |
| Software Delivery | 工程或发布操作所需结果 | Code Design、实现、测试、工程审核和发布部署 |
| Agent Runtime | 已明确的 Module 或 Workflow 使用需求 | 注册、执行配置、独立执行与证据 |
| Product Authorization | 下游确需数据库访问时找到其规则入口 | `user_key` 的数据库访问权限；不决定意图路由 |

项目 Charter 提供项目范围和人类决策权，并指明项目工作导航；项目工作导航提供本地入口。两者都不是本 T0
生成的 Portable 业务清单。本文不复制 peer 内部流程、接口、错误码或运行记录。

## 8. References

- [System Change Governance](the_system_change_governance.md)
- [Design Doc Management](the_design_doc_management.md)
- [Skill Management](the_skill_management.md)
- [Review Contract](the_review_contract.md)
- [Software Delivery](the_software_delivery.md)
- [Agent Runtime](the_agent_runtime.md)
- [Product Authorization](the_product_authorization.md)
