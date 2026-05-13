# Analysis Platform And PM Workspace

**Version 0.1 — 2026-03-21**

本文档把 `AnalysisPlatform` 作为正式设计对象单独展开。它描述的不是知识库，而是人和 agent 共同工作的当前工作台。

---

## 1. Purpose

`AnalysisPlatform` 的目标是把：

- 当前研究材料
- 当前组合状态
- 当前风险边界
- 当前候选机会
- 历史 memo 与历史判断

组织成投资经理可消费的当前判断。

本工作台不替代顶层 task routing。真实请求应先经过 `designDoc/the_task_routing.md` 所定义的 `task mainline` / `first authority` 判断，再进入本文件所描述的 synthesis、PM decision、memo / review surfaces。

---

## 2. Core Work Surfaces

分析平台至少应包含四个工作面：

### 2.1 Analysis Inbox

待看的新材料、待处理风险变化、待复核机会。

### 2.2 Synthesis Workspace

把研究、市场、组合、风险、主题放到一起形成判断。

它消费的应主要是 task-specific projections，而不是 archive layer 的原样导出。

对 theme/report 写作，默认应消费：

- full-text but metadata-thin writer package
- relevant snapshots
- relevant thesis notes

而不是：

- connector sync 痕迹
- full links dump
- archive plumbing metadata

当 package-driven writer 需要调用外部模型 API 时，边界应固定为：

- upstream 仍由本地 deterministic/tooling 负责组装 package
- external writer API 只消费 package 并返回成稿
- provider client 应作为稳定边界对象存在于 `src/core/`
- 不要让外部 writer API 反向定义 package shape 或 archive routing

### 2.3 PM Decision Surface

让 PM 看到：

- thesis
- evidence
- risks
- exposure fit
- action framing

### 2.4 Memo And Review Surface

把当前判断变成：

- recommendation
- memo
- monitoring checklist
- post-mortem input

---

## 3. Interaction Model

如果 Cursor 是主交互端，那么第一版分析平台更像：

- Cursor + local files + local state + deterministic CLI

而不是：

- 一个纯聊天机器人
- 一个完全没有状态的问答器

推荐交互方式：

1. refresh or load current state
2. retrieve relevant research and portfolio context
3. synthesize a current view
4. output structured recommendation or memo

---

## 4. Relationship To Functional Modules

分析平台不是独立替代功能模块，而是这些模块汇流后的工作面。

它主要消费：

- `InfoClassification`
- `PortfolioExposure`
- `OpportunityRanking`

并把结果转化为：

- `StructuredAdvice`
- `MemoRecord`
- `ReviewRecord`

---

## 5. Relationship To Agents

分析平台应容纳多种 agent 工作模式：

- specialist analysis
- synthesis
- risk review
- committee or chair review
- memo writing

关键不是 agent 数量，而是：

- 角色边界是否清晰
- 谁负责 synthesis
- 谁负责 risk gate
- 谁负责最终 artifact

对 research-to-report workflow，边界建议固定为：

- `KnowledgeBase` 保存 full-fidelity archive 和 stable semantic objects
- upstream updater / packager 负责把 source 整理成 writer projection
- writer agent 负责从 projection 生成 PM-facing artifact
- PM decision surface 不应直接暴露 archive plumbing

---

## 6. What It Should Avoid

分析平台应避免退化成：

- 纯 prompt engineering playground
- 只有聊天记录、没有正式产物
- 每次分析不看本地 archive
- 只给观点，不给证据和风险边界

---

## 7. Current Repo Direction

对 `trading_platform`，分析平台第一版最合理的落地方式是：

- Cursor 作为 operator endpoint
- canonical CLI 作为 deterministic actions
- local archives / state / memos 作为 ground truth
- structured recommendations and memos 作为正式输出

未来如果再发展 UI，也应建立在这套工作面已经清晰之后。
