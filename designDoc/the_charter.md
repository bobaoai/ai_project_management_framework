---
title: Analyst Billie Charter
status: active
layer: T0
t0_layer_id: the_charter
canonical_owner: designDoc/the_charter.md
language: zh-CN
---

# Analyst Billie Charter

**Version 1.7.1 — 2026-09-28**

## 0. Contract Capsule

Machine-audit block. Keep paths, ids, aliases, commands, and ledger pointers plain; use citation ids only in body prose and `References`.

```yaml
layer: T0
t0_layer_id: the_charter
status: active
canonical_owner: designDoc/the_charter.md
scope: supreme Analyst Billie constitutional constraints for object ontology, authority layering, system surface split, archive truth, canonical paths, false-precision refusal, belief-delta evidence, freshness, decision grounding, no-orphan structure, and amendment thresholds
non_goals:
  - runtime command discipline
  - schema implementation details and field-version listings
  - task inventories, external runner mechanics, or Design Doc review procedure
inputs:
  - principal manager constitutional commitments
outputs:
  - supreme T0 constraints for all lower Design Docs, skills, schemas, runtime commands, and artifacts
truth_surfaces:
  - designDoc/the_charter.md
runtime_triggers: none
downstream_consumers:
  - all T0 and T1 Design Docs
  - runtime projections and skills that consume Hoveath authority
open_decisions: none
review_gate: owner / principal-manager amendment threshold
runtime_surface_ledger: none
verification_hooks:
  - ./.venv/bin/python -m pytest tests/test_design_doc_t0_layer_ids.py -q
```

---

## 序言

Analyst Billie 是一个将市场信息持续蒸馏为信念状态变化的认知系统。

它所识别的核心瓶颈，不在信息的获取，而在信念状态的可审计更新。

它由一名主理人 (principal manager) 主理，以 Theme、Thesis、Scenario、Evidence 四类对象为骨架，组织其记忆、判断、时效与决策。

本章程是 Analyst Billie 的最高约束。其下所有设计、协议、契约、技能与产物，均以本章程为前提。下层文档与本章程冲突的，应撤回或修订。本章程不退让。

---

## 第一条 · 对象本体

Analyst Billie 的世界由四类一等对象构成：

- **Theme** —— 值得长期追踪的结构性议题。
- **Thesis** —— Theme 之下的可证伪论断，包含因果链与证伪条件。
- **Scenario** —— Thesis 之下的可能现实路径，包含触发信号 (trigger signal) 与因果链节。
- **Evidence** —— 一次外部信息或内部判定，引发某一信念状态的变化，并记录其前态、后态与所改维度。

四者分工清晰：Theme 划定关注范围，Thesis 解释为什么会发生，Scenario 描述如何发生，Evidence 记录我们为何改变看法。

四类对象之外另设旁路对象 path observation，用于承接早期路径信号，归 Scenario 上游管辖，不属于一等对象。

observation 可以在 Thesis 之前存在，但进入决策之前必须绑定到某个 Thesis、Scenario 或信念对象。游离的 observation 不进入决策。

每类对象都必须可被上溯：Theme 为顶层；Thesis、Scenario 各属唯一父对象；Evidence 至少绑定一个明确对象。游离对象不被承认。

---

## 第二条 · 权威分层

信念层的决定权在 PM。
事实层的执行权在系统。

**信念层**包括：Thesis 与 Scenario 的生命周期转换、`pm_conviction` 赋值、`scenario_role` 赋值、`market_state` 赋值、辖域边界裁定。此层的所有动作都必须由 PM 显式确认 (acknowledge)。

**事实层**包括：数字校验、字段一致性、时间戳归一、引用完整性、客观可验证的触发信号 `signal_status` 命中、账本起草、时效巡检。此层的所有动作由系统自主执行并入账。

但是，触发信号的命中只到 `signal_status` 这一层。一个信号命中并不等同于一个 Scenario 被验证；Scenario 与 Thesis 的生命周期不能由系统自动推进。

判断准则：仅靠查证事实即可定夺的，归系统；需要解释、权衡或主观信心的，归 PM。本条以 schema 强制：未经 PM 确认的 Evidence 不能驱动信念层的转换。

---

## 第二条之一 · 系统表面分工

Analyst Billie 的系统表面分工如下：

```text
DesignDoc owns what / why / boundary / authority.
Skills own how an AI should act now.
Code owns how something can be deterministically checked or executed.
```

DesignDoc 是设计与维护的权威入口。它定义系统承认什么对象、什么工作流、什么产物、为什么如此设计、边界在哪里、谁拥有权威。任何改变系统契约、边界、工作流、产物形状、路由规则、技能责任、命令行为、schema 或 runner profile 的工作，都应先从 DesignDoc 入手，再经 review gate 投影到 Skills、Code、tests、schemas 与 artifacts。

T1 DesignDoc 可以定义 AI workflow semantics，前提是它定义的是持久的设计权威：工作流为什么存在、识别哪些状态、有哪些边界、准入哪些输入输出、何时需要人工裁定。对应 Skill 是该权威在当前 AI runtime 中的执行投影，负责告诉 AI 此刻如何行动。Skill 可以编排已准入 Code，但不拥有 deterministic command behavior、schema validation 或 executable result 的最终定义。

Skills 是已准入产品运行的执行入口。执行既有 workflow 时，应由 routing skill 或具体 task skill 进入，只读取必要的 DesignDoc capsule / ledger 作为权威上下文，不应要求每次运行重读整个设计语料。

产物、运行时状态、sidecar 与 reports 保存系统已经生成的结果；它们不单独拥有本条意义上的系统权威。Code 执行和验证可判定规则；它回答"什么可以被稳定检查或运行"。

任何表面都不得伪装成全部四种权威。无法判断归属时，先回到本条。

---

## 第三条 · 事实本源

archive 是 Analyst Billie 唯一的事实本源 (source of truth)。

archive 不可改写，只可追加 (append)。其他所有表面都是对 archive 的引用、索引或解释，本身不复制原文。

任何"仅在覆盖层 (overlay) 修改而 archive 未动"的状态，都不构成事实。

---

## 第四条 · 路径唯一

每一类资源只设一条正典路径 (canonical path)。

正典路径无法服务请求时，系统必须直接报错，使调用方立即可见。任何 fallback 结构都视为缺陷，必须移除。

系统宁可硬中断，不接受静默污染。

---

## 第五条 · 拒绝伪精度

Analyst Billie 所处理的因果链，多属宏观或半宏观范畴。其表达的默认形态为 enum 与散文。

- 信念强度以 enum 表达（high / medium / low / exploratory），不使用 0–1 浮点。
- 阈值以散文表达，并必须显式标注它所对应断裂的链节（demand / supply / pricing / policy / adoption / margin），不接受单独的数字阈值。
- 量级以三档 enum 表达（minor / moderate / major），不使用浮点。

数字不是默认形态。任何引入数字的提议都必须证明该数字确实可被审计；无法审计的数字属于伪精度，本章程不予接受。

---

## 第六条 · 学习而非日志

Evidence 不是日志。

每一条 Evidence 必须记录以下四项：

- **前态** —— 此次变化之前的信念状态。
- **后态** —— 此次变化之后的信念状态。
- **变化维度** —— 此次变化属于哪一维。
- **变化理由** —— 引发此次变化的原因。

没有信念变化的 Evidence 不被视为 Evidence。仅记录"看到了什么"而不记录"信念发生了什么变化"的内容，由 archive 收纳，账本 (ledger) 不接收。两者职责不同，不得混淆。

Evidence 不得偏倚。对抗证据 (counter-evidence) 与未决反驳 (unresolved objection) 必须以同等地位入账，不得只录支持性证据。

---

## 第七条 · 时效约束

所有 active 对象都必须配置复核策略 (review policy)。

时效与生命周期是两个独立的属性，不可混淆——时效描述对象的新旧，生命周期描述对象的存续。一条 Thesis 可以同时为 active（生命周期仍然成立）与 stale（时效已过期）。两者各自一维，互不替代。

时效巡检器 (sweeper) 按既定节律执行巡检；逾期对象的时效自动转为 stale，并写入一条时效事件 (freshness event)。时效事件不构成 Evidence——只有当对象经 revive 流程复用、或在新决策中再次被援引时，才需要写入一条信念变化记录。生命周期不会因时效而改变。

组合决策 (portfolio decision) 的候选集合，必须同时满足生命周期为 active 与时效为 fresh。这是 schema 级别的强制规则。

复议一个 stale 对象，必须经过 revive 流程，并写入一条信念变化记录，注明复议的理由。

时效是强制约束，不是建议。

---

## 第八条 · 决策依据

组合决策必须至少引用一条 active 且 fresh 的 Scenario，并显式引用其 (`pm_conviction`, `scenario_role`, `market_state`) 三元组以及定价锚 (pricing anchor)。

`market_state` 必须保留时间序列：每次更新追加一条快照，不覆盖旧值。复盘时，定价路径与当前态同等重要。

三元组中每一项的当前值都必须能够通过 Evidence 账本上溯到其信念源头。

决策所引用的 Scenario 必须暴露其当前未决反驳；忽略未决反驳必须显式说明理由。
决策不得绕过 Scenario 层直接读取 Thesis 散文。
决策不得引用未经 PM 确认的信念变化记录。

由此，每一份组合决策都可以事后逐项审计。

---

## 第九条 · 不得游离

在 Analyst Billie 内部，任何能力、产物或动作都不得游离于系统之外。

支撑此原则的有三个结构：

- **三视角** —— Functional Modules、KnowledgeBase、AnalysisPlatform。任何能力都必须能在此三视角中定位。
- **四路由** —— 任务主线 (task mainline)、技能 (skill)、确定性装配器 (deterministic builder / package)、写入网关 (writer gateway)。四层之间不得互相穿透；任何请求都必须走完这四层。
- **一工件图** —— 每一件面向 PM 的产物都是图中的一个节点，附带正典路径、时效契约、装配器与归属技能。复合任务是若干目标节点的集合；任何产物都必须能挂入此图。

无法挂入的对象，要么是能力错位，要么是位置缺失，必须先补足再继续。游离的对象不进入系统。

---

## 第十条 · 章程修订

本章程可以修订，但修订门槛严格：

- **认知条款** —— 第一条至第八条中的某一条被持续证伪：通过若干独立案例证明它与实际工作流存在根本冲突；
- **结构条款** —— 第九条所述的结构发生根本变化：例如三视角重新切分、四路由合并或拆分、或工件图模型重构；
- **新增条款** —— 增立第十一条：出现稳定持续三个月以上、横跨多个技能与多个 schema 的新认知约束；
- **章程重启** —— 主理人明确宣告：发生重大业务方向调整。

本章程不接受以下改动：

- 写入 schema 实现细节、字段版本号或技能列表（章程仅命名宪法级承诺，不锁定具体实现）；
- 写入运行时纪律（这属于操作员守则的职责）；
- 软调措辞（措辞的改动等同于承诺的改动，必须按上述门槛执行）。

每次修订都必须在 Version 行递增。

---

## 修订记录

- **v1.7.1 (2026-09-28)** —— 移除指向已撤回英文平行版本 `the_charter.en.md` 的四处导航与重复真相面引用（frontmatter `parallel`、版本行下的英文平行链接、Contract Capsule `truth_surfaces` 条目、References 条目）及随之为空的 References 标题；宪法承诺不变。
- **v1.7 (2026-05-06)** —— 在 **第二条之一 · 系统表面分工** 中补入 refined interpretation：T1 DesignDoc 可以定义持久 AI workflow semantics；Skill 是其当前 runtime 执行投影；Skill 可编排 Code，但不拥有 deterministic command behavior、schema validation 或 executable result。
- **v1.6 (2026-05-06)** —— 新增 **第二条之一 · 系统表面分工**：明确 DesignDoc / Skills / Code 的权威分界，并区分设计维护入口与产品运行入口；产物、sidecar、reports 与运行时状态保存生成结果，但不独立拥有系统权威。
- **v1.5 (2026-04-26)** —— 第三轮评审后小修四处语义边界，结构与承诺不变：
  - **第一条** 加四类对象分工速记一行（Theme 划定范围、Thesis 解释为什么、Scenario 描述如何发生、Evidence 记录为何改变看法），降低 onboarding 门槛；
  - **第一条** 末句"唯一上溯链路"改为按对象类型分述：Theme 顶层、Thesis 与 Scenario 各属唯一父对象、Evidence 至少绑定一个明确对象。原措辞对 Evidence multi-link 设计不准确；
  - **第七条** sweeper 写入对象由 "Evidence" 改为 "时效事件 (freshness event)"，明示时效事件不构成 Evidence，避免与第六条"无 belief delta 不算 Evidence"矛盾；
  - **第七条** 候选集合过滤措辞由 "按时效过滤、不按生命周期过滤" 改为 "必须同时满足生命周期 active 与时效 fresh"，免误读。
  - 第三轮评审第 4 点（"账本起草"措辞）未采纳：现有末句"未经 PM 确认的 Evidence 不能驱动信念层的转换"已兜底，"起草"本意即 candidate-not-decision，无需修辞替换。
- **v1.4 (2026-04-26)** —— 回看两轮评审，补三处此前弱化或丢失的承诺：
  - **第六条** 加 "Evidence 不得偏倚"：对抗证据与未决反驳必须以同等地位入账，不得只录支持性证据。回应首轮评审第 6 点关于 confirmation machine 的告诫。
  - **第八条** 加 "`market_state` 必须保留时间序列"：每次更新追加一条快照，不覆盖旧值；复盘看路径而非当前态。回应首轮评审第 4 点关于 pricing snapshots 的建议。
  - **第八条** 加 "决策所引用的 Scenario 必须暴露其当前未决反驳"：忽略须显式说明理由。与第六条对抗审查条款形成闭环。
- **v1.3 (2026-04-26)** —— 全文行文风格调整：从仿古文体改为现代克制权威汉语。条款语义不变，章程结构不变；移除"凡 / 之 / 乃 / 然 / 者 / 也"等古汉语虚词与四字宣言式句法（如"宁愿挂掉，不愿污染"、"时效非建议，乃法"），改写为陈述式现代汉语；序"序"改为"序言"；多条标题去古化（"真之所在"→"事实本源"、"颗粒拒伪"→"拒绝伪精度"、"学习，而非记账"→"学习而非日志"、"时效之法"→"时效约束"、"决策之据"→"决策依据"、"不容游离"→"不得游离"、"修宪"→"章程修订"）。
- **v1.2 (2026-04-26)** —— 七处条款修订加全文中文化。
  - 内部一致性：第二条 `pm_conviction` / `market_state` 字段名与第八条对齐；
  - 自相矛盾：第七条 "周扫一次" 改为 "以法定节律巡检"，避免运行时频率渗入章程；
  - 隐含承诺显化：第八条加 "三元组每一项可经 Evidence 账本上溯至其信念源头"，使审计承诺成立；
  - 删冗：第八条三禁删去 "不可基于 stale 对象"（已被主句覆盖）；
  - 拒绝伪精度反例：第十条 "至少三次 case" 改为 "若干独立案例"，免犯第五条；
  - 修订门槛分层：第十条认知条款 / 结构条款 / 新增条款 / 章程重启四类分行列示；
  - schema 边界澄清：第十条 "不接受写入 schema 字段" 改为 "不接受 schema 实现细节、字段版本号"，承认 charter 命名宪法级字段并非禁忌；
  - 全文中文化：除四类核心对象 (Theme / Thesis / Scenario / Evidence)、enum、schema 字段名、架构专名 (Functional Modules / KnowledgeBase / AnalysisPlatform) 等之外，其余英文术语均译为中文，首次出现处以括号附原英文。
- **v1.1 (2026-04-26)** —— 序补可审计性北极星；第一条增 observation 入决策须先绑定；第二条澄清信号命中止于事实层；第六条强调 archive 与账本职分有别；第七条引入时效与生命周期二维分离；第八条 narrative_role 改名 scenario_role；第九条易名"不容游离"。
- **v1.0 (2026-04-26)** —— 第一次成章。
