---
name: hoveath-doc-self-review
description: Review plans, design docs, proposals, methodologies, retrospectives, and multi-section handoffs before delivery.
---

# Doc Self-Review（交付前自审 doc）

## 元数据

- **类型**: BestPractice
- **适用场景**: 在交付任何 Proposal 前（Plan、Design Doc、Methodology Doc、Framing Doc、Retrospective、给用户消费的 inline 回复或多 section 长 response）执行 self-review
- **创建日期**: 2026-04-25
- **来源**: 多次 doc 交付后被用户当场指出 reader-state 结构性失败的实战经验，加上 R13 Self-Review Before Handoff 的 protocol 化需求

---

## 这个文件是干什么的

R13 规定交付 Proposal 前必须 self-review。COMMUNICATION.md 第一性原理 #7 定义了 review 时要查的四份参考。但 "查什么" 不等于 "按什么顺序查、每步产出什么、什么时候判定 review 通过"。这个 skill 把 review 从 principle 落到 procedure，是 R13 的 canonical 执行路径。

它解决的具体问题：Doc self-review 经常退化成 "再读一遍找错别字"，结构性 reader-state 失败（重复段、缺 priority、缺执行序、abstract 没传达核心收益）漏掉。这种漏掉只有在用户当场指出时才被发现，每次都是事后修补。

---

## 基础公理（详见 axioms）

- **T02**：结果确定性优于过程确定性（self-review 的结果是 doc 满足验收，不是 review 流程跑完）
- **A08**：提示质量是主要杠杆（doc 是给用户的 prompt，质量决定下游决策质量）
- **A16**：先揭示隐藏假设（review 的核心是把 doc 里的隐藏 weakness 显式化）

---

## 触发条件

下列任一情况触发：

- 即将交付 Plan、Design Doc、Methodology Doc、Framing Doc、Retrospective 给用户
- 即将给用户回一段多 section 长 response（>3 段且涉及 framing / 决策 / 推荐）
- 修改了 R13 涵盖的 doc 后再次交付（即使是小改也要重跑相关 stage）
- 用户问 "review 一下" / "自己看看" / "你 review 过了吗"

不触发：

- 单轮事实问答
- 单文件 trivial 改动（错别字、单行修复）
- 纯执行类回复（"已经跑完，结果是 X"）

---

## 目标、边界、验收

**目标**：交付前对 Proposal 完成结构 + 内容 + 风格三层 review，输出明确的 "改了 X 处 + 保留 Y 处及理由" 报告。

**边界**：

- 只 review 即将交付的 Proposal 本身，不顺手扩 scope 改其他 doc
- 只跑 4 份参考定义的 review 维度，不引入临时新维度
- 跳过任何 stage 必须显式声明，禁止静默跳过

**验收**（review 通过判定）：

- Stage 1-3 全部跑过，每个 stage 有 explicit pass/fix 记录
- 4 份参考全部对照过（或显式声明跳过及理由）
- Reader-state 5 问全部跑过且都过
- 输出 self-review 报告包含：改动 list（每条带 §引用 + 修法）+ 保留 list（每条带理由）+ 跳过 list（每条带理由）

---

## 三阶段执行序

按顺序跑，前一 stage 出的 fix 全部应用后再进下一 stage。否则风格审改了一处 prose，结构审又把这段删了，浪费两次工作。

### Stage 1：结构审（最重要）

**输入**：草稿 doc 全文 + Reader State and Judgment Gain skill

**操作**：跑 reader-state 5 问，每问产生 0-N 个 fix item。

| # | 自检问 | fix 信号 |
|---|---|---|
| Q1 | 读完后会更清楚什么？ | Abstract 没传达核心收益 / 主线被埋在第 N 节 |
| Q2 | 会更能区分什么？ | 概念对比模糊 / 应当用 table 但用了 prose |
| Q3 | 哪种误读现在更容易被拒绝？ | 已知误读没被显式 reject / 缺 disclaimer |
| Q4 | 下一步判断或决策会被怎样 sharpen？ | Action list 缺执行序 / 缺优先级 / 缺依赖图 |
| Q5 | 删掉某段读者判断能力是否真的下降？ | dead section / 重复段 / status table 重复 actions list |

**额外结构检查**（reader-state 之外）：

- 同级 section 对称性：同 level 标题下的内容长度 / 深度是否平衡。一节 12 行嵌表格、其他节 1 行，就是失衡（典型例子：COMMUNICATION.md 第一性原理 #7 曾经 12 行打破其他 6 条 1 行的平衡）
- Cross-ref 完整性：doc 里引的 §X / 文件路径 / 表格是否真的存在

**输出**：Stage 1 fix list。每条 `[§X.Y] 问题 → 修法`。

**Stage 1 必须先全部应用完，再进 Stage 2。**

### Stage 2：内容审

**输入**：Stage 1 修过的 doc + 4 份参考中按场景适用的 (skill writing / AI product design)

**操作**：

- 论证链完整性：每个主张是否有 evidence / 引用 / 推理链支撑
- 例子有效性：例子是否带 confound（如想说明 authority 但例子里 freshness 也变了）
- 引用准确性：cite 的 paper / 文件 / 数据是否真实存在且数字对
- 重复段：前后是否说同一件事（即使措辞不同）
- Skill / contract 段落：用 Skill Writing Best Practice 检查（结果导向 / 不变量 / 检测式 boundary）
- AI-facing artifact 段落：用 AI Product Design Best Practice 检查（contract 字段完整 / 边界明确 / handoff 清楚）

**输出**：Stage 2 fix list。

**Stage 2 必须先全部应用完，再进 Stage 3。**

### Stage 3：风格审

**输入**：Stage 1+2 修过的 doc + COMMUNICATION.md 语言风格 section

**操作**：扫这些 violations：

- 破折号 ——/—/-- （prohibited per COMMUNICATION.md 语言风格）
- 否定句式（X 不是 Y → X 是 Z）
- 华丽辞藻、营销词（"惊喜"、"卓越"、"赋能"）
- AI 味比喻（"在虚空里相遇" / "leaves your mouth"）
- 「主句——插入——主句」结构
- 「长出来 / 长出了」用法
- 多余的 "下面"、"接下来"、"总之" filler
- 客套话、废话（"这是一个非常好的问题"）
- meta-mention 例外：如果文档自身在举例展示禁用对象（line 53 「主句——插入——主句」这种结构尤其要避免），保留破折号是合理的

**输出**：Stage 3 fix list。

### 最终输出：Self-review 报告

格式（直接交付给用户）：

```
## Self-Review 报告

改了 N 处：
| # | 问题 | 修法 |
|---|---|---|
| 1 | [§X.Y] ... | ... |
...

跳过的 stage / 参考（必须声明）：
- 跳过了 X 因为 Y（按 R13 跳过协议）

保留未改的（评估后保留）：
- §X.Y ... 因为 ...
```

报告里禁止说 "感觉 OK" / "整体没问题" / "review 通过" 这种 vague 表述。

---

## 不允许的捷径（禁止式 + 检测式）

每条 boundary 都配一句 "无声违反时长什么样"。这是 agent 自己回头能检查的可观察特征。

| 禁止式 | 检测式（无声违反时长什么样） |
|---|---|
| 不允许跳过 reader-state 5 问而声称 review 通过 | 交付的 doc 有结构性 reader-state 失败（重复段 / 缺 priority / 缺执行序 / abstract 没传达核心收益），但 review 报告里没提到这些维度 |
| 不允许把 Stage 3 风格审当成 self-review 全部 | review 报告通篇都是 em dash / negation 这种局部 fix，没有 reader-state 维度的 fix 或 explicit pass |
| 不允许跳过 4 份参考中任一条而不显式声明 | review 报告只引用 3 份参考的 finding，第 4 份既没出现 finding 也没出现 "skipped because Y" |
| 不允许在 review 报告里用 "感觉 OK" / "整体没问题" | 报告没具体列出 Stage 1/2/3 各自的 fix list 和 explicit pass，只有结论性陈述 |
| 不允许 review 后再加新内容不重 review | doc final 版本比 review 报告基于的版本字数更多，新加的段没被任何 stage 检查覆盖 |
| 不允许把 "已应用 fix" 和 "保留未改" 混在一个 list | 用户读完不知道哪些是改过的 / 哪些是评估后保留 / 哪些是被忽略的 |

---

## 跳过协议

R13 允许在具体 Proposal 上下文不涉及某条参考时跳过那一条（如纯改 source code 时跳过 AI Product Design）。本 skill 的跳过协议：

- **可以跳过整个 stage**：如 Stage 2 内容审在纯 framing doc 上没有可论证的 claim，跳过 Stage 2 (内容审)，但必须在最终报告写 "跳过 Stage 2 因为本 doc 不含可证伪 claim"
- **可以跳过单条参考**：如 doc 不涉及 skill / contract 设计，跳过 Skill Writing Best Practice 检查
- **不可以跳过 Stage 1**：reader-state 5 问对所有 Proposal 适用，没有跳过场景
- **不可以跳过 Stage 3**：风格审对所有 Proposal 适用
- **不可以静默跳过**：任何跳过必须在最终报告显式声明

---

## 常见陷阱

| 陷阱 | 表现 | 应对 |
|---|---|---|
| 把手工挑刺当 self-review 全部 | 通篇都是 em dash / negation / 重复词 这种局部 fix，没有 reader-state 维度的检查 | 强制先跑 Stage 1，Stage 1 全部应用后再进 Stage 3 |
| 加内容时破坏父结构对称性 | 在 numbered list 第 N 条下塞 12 行嵌套表格，破坏其他 N-1 条 1 行的平衡 | Stage 1 "同级 section 对称性" 检查即可 catch |
| 跳过参考不声明 | 只跑 reader-state 5 问就交付，没碰 skill writing / AI product design | 报告强制 4 份参考逐条说明 used / skipped + 理由 |
| Review 后加内容不重 review | 用户问完 follow-up，加了新段，没重新跑 Stage 1-3 | 任何 doc 改动后默认重跑 affected stage，明显不影响某 stage 才跳过 |
| 用 "感觉 OK" 替代 explicit fix list | 报告只说 "我读了一遍没问题" | 强制输出 fix list（即使是 0 条也要明示 "Stage X 跑完 0 fix"） |
| 把 fix list 和 retain list 混 | 用户读完不知道哪些改了哪些没改 | 报告分两个独立 list：改了 N 处 / 保留 M 处及理由 |
| Stage 顺序错乱 | Stage 3 改 prose，Stage 1 把这段删了，重复劳动 | 严格按 1→2→3 顺序，前 stage fix 全部应用再进下一 stage |

---

## 何时回读本文件

- 即将交付 Proposal 给用户之前
- 用户问 "review 用了什么 skill" 或 "你自己看看"
- 发现某次 review 漏掉了用户当场指出的问题，回头看是哪个 stage 没跑
- 在写新 doc 时想知道 doc 完成后该怎么 self-review
- 修改 R13 / Self-Review Protocol 时回看本 skill 是否需要同步

---

**最后更新**: 2026-04-25
