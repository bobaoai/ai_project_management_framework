---
name: the-review-authoring
description: 为指定 Reviewer 编写或修订 prompt source，将授权目标和目标 Design 的判断要求落实为专用指令，与既有通用规则、checklist 组成完整候选。
metadata:
  skill_class: primary_agent_development
  primary_agent_entry_role: authoring
  primary_agent_entry_subject: reviewer_prompt_source
  first_authority_ref: designDoc/the_review_contract.md
---

# Reviewer Prompt 编写

## 0. AI-facing Authoring Rules

<!-- embedded-resource:soul:bestpractice_ai_facing_writing:start -->
## 核心原则

### 原则一：先明确结果要求，再确定必要方法（结果确定性优先于过程确定性）

AI 开始写作前，应明确文稿要完成什么、服务什么读者，以及怎样判断内容已经正确、充分、可用。依据这些结果要求，确定需要交代的内容和采用的写作方法。

写作任务至少应明确四件事：

1. **目标**：文稿用于什么，读者需要从中获得什么理解、判断或执行能力。
2. **验收依据**：哪些要求决定文稿是否正确、充分并符合用途，如何核对这些要求。
3. **依据与方法**：使用哪些材料、知识和工具，哪些步骤或先后关系会影响结果。
4. **交付要求**：文稿需要达到什么深度，采用什么形式；已有明确的格式、路径或 schema 要求时，遵守相应要求。

凡步骤、顺序、工具或执行身份会影响正确性、授权边界或证据有效性的要求，应明确规定。例如，独立审核需要针对准确候选执行，审核结论需要与该候选对应。

其余方法由 AI 根据任务选择。步骤式指导、例子和经验，只要能帮助完成任务，就可以保留；避免强制执行与结果无关的过程，也避免只给目标而缺少必要方法。

### 原则二：支持 AI 自主判断，排斥 SOP

AI 具备推理能力。它的上下文容量有限。写入的内容应帮助它完成任务，减少无效的注意力消耗。

方法指导应提供建议和约束，保留 AI 选择执行路径的空间。避免将指导写成固定的标准操作流程（SOP）。

例如，市场分析可以按行业板块组织。如果当天的市场变化主要由一个宏观冲击驱动，AI 应能够选择全局分析。

已知陷阱应当写清楚。AI 可能无法仅凭当前上下文识别这些问题。真实的失败经验通常比泛泛的建议更有用。

保留一段内容前，检查两点：

1. 删除它是否会降低任务质量或成功率。
2. 它是在说明预期结果，还是在规定操作方法。

**优先保留预期结果的说明。操作方法只有在确实能提高任务成功率时才保留。**

---

### 原则三：先写清 AI-facing 文档的契约，再压缩表达

Skill 是 AI 执行任务时使用的契约文档。写作应先保证执行所需的信息完整，再优化篇幅和版面。

这条原则适用于主要供 AI 使用的稳定文档，包括顶层设计文档、路由文档、规则、公理和入口文档，如 `CLAUDE.md`、`AGENTS.md`。

#### 必须回答的六个问题

编写或评审任何 AI-facing 文档时，先确保文档能直接回答以下问题：

1. **这一层负责什么？** 说明这一层的用途。
2. **什么时候进入这一层？** 说明进入条件和触发信号。
3. **进入后先读什么？** 明确应优先遵循的权威依据（first authority），以及承载当前事实的来源（truth surface）。
4. **应该产出什么？** 说明输出形式，以及读者读完后应能理解、判断或完成什么（reader-end-state）。
5. **怎样与相邻层交接？** 说明上游期望什么、下游使用什么，以及失败时如何回退。
6. **哪些相邻概念容易混淆？** 说明它们的区别，以及什么时候应使用其他概念或入口。

**六个问题都写清后，再考虑如何缩短和整理文档。**

#### 契约完整优先于视觉简洁

文档应让 AI 在执行时找到完整的契约。压缩篇幅或调整版面时，必须保留关键边界。

避免以下四类写法：

- **合并不同的任务主线。** 不要为了减少路由表的行数，合并不同的重复性任务主线。实际产出形式不同的主线，应各占一行。
- **混淆层级。** 明确区分任务主线（task mainline）、Skill 层、写作网关层（writer gateway layer），以及确定性构建器与数据包层（deterministic builder / package layer）。名称相近的层尤其容易被误用。
- **只靠名称表达职责。** 名称可能有多种含义。例如，`manager` 可能指角色，也可能指模块。文档应直接说明对象负责什么、不负责什么。
- **先写摘要，后补契约。** 先写清详细契约，再写摘要。

#### 检查删去一段是否影响执行

写完一段后，检查：删去这段，AI 还能完成文档规定的读者目标任务吗？

- 能完成：这段是多余内容，应删除。
- 不能完成：这段属于契约，应保留。

这项检查与 FP4（删除不影响判断的信息）及 `bestpractice_prose_without_editorial_meta.md` 中的检查互为补充。它们删除无助于判断的句子，避免无效扩写；本项检查保留执行所需的契约，避免删减造成含义不清。AI-facing 文档应同时满足这两项要求。

---

### 原则四：固定不变量，保留实现选择

结果确定性优先于过程确定性。写作时还应区分：哪些结果要求必须保持一致，哪些实现选择应留给 AI。

约束所有细节会限制 AI 自主判断。缺少必要约束，会使系统反复改变同一对象的定义和做法，失去连贯性。

**必须固定的不变量**包括：

- 产物的规范路径与命名。
- 产物的身份字段，如 `report_date`、`asset_id`、`theme_id`。
- 上游依赖的身份与新鲜度契约。
- 产出此节点的唯一规范构建器（canonical builder）。不允许第二条产出路径。
- 与相邻 Skill、构建器和写作器的接口形式。

**应留给 AI 选择的内容**包括：

- 正文的具体写法。
- 判断路径与取舍。
- 中间过程的组织方式。
- 哪些证据需要重点展开，哪些只需简述。

写作时应明确区分这两类要求。固定不变量，使系统保持连贯，产物可以追踪，并能跨任务复用。保留实现选择，使 AI 能根据当前上下文作出合适判断。

如果文档只规定正文结构和写作步骤，却没有写清不变量，就会同时限制 AI 的判断空间，并允许产物偏离约定。

检查每条要求：

- 它属于不变量，还是实现细节？
- 如果属于实现细节，能否写成建议和失败信号，保留 AI 的选择空间？
- 不变量是否足以防止系统偏移，同时数量少到 AI 能记住和使用？

### 原则五：同时写清禁止事项和违规特征

仅写“不要做什么”，依赖 AI 主动注意并遵守禁令。AI 绕过禁令后，产物仍可能看似合格，禁令本身无法帮助它发现问题。

每条关键边界都应同时说明两件事：

- **禁止事项**：哪些行为或结果不被允许。
- **违规特征**：发生违规后，可以观察到什么。

例如，数据更新边界可以写成：

- **禁止事项**：数据更新完成前，不得编写投资经理（PM）报告。
- **违规特征**：已经产出报告，却没有确认 `daily_update_status.json` 中的 `blocking == false`。报告本身可能看不出问题，但上游数据的新鲜度要求尚未满足，需要通过后续复盘发现。

主题补充分析的边界可以写成：

- **禁止事项**：主题补充分析（theme overlay）不得替代任务的首要依据（first authority）。
- **违规特征**：报告的核心论述采用主题的一般结论，取代了对当前股票或当前市场的分析。读者据此判断主题，判断对象偏离了当前股票或市场。

描述违规特征时，尽量做到：

- 给出 AI 能在产出后检查的可观察特征。
- 指出缺少哪类证据或使用了哪个错误的依据来源（truth surface），不要只说“读起来不对”。
- 如果问题只能在后续环节发现，明确指出哪个环节能够发现。

这样，AI 在自主选择路径后，仍能检查自己是否越过边界。可观察的违规特征有助于发现仅凭禁令容易遗漏的偏差。

### 原则六：按陌生读者的理解顺序组织概念

执行者通常没有参与作者当时的讨论。写作顺序必须从读者已有的知识出发，使每个新概念只依赖读者已经知道、或前文已经说明的对象、任务与边界。

先明确读者的起点和目标：

- **读者起点**：进入时已经知道哪些对象、字段、工具和上游事实。
- **读者目标状态**：读完后能判断何时进入、应优先信任什么、需要产出什么、何时完成，以及何时停止或提交给有权处理的人。

引入新概念时，优先按以下顺序说明：

1. 当前对象、任务或可观察问题是什么。
2. 它与相邻对象、正常路径或读者已有认知有何关键差异。
3. 这项差异会改变什么执行、判断或交接。
4. 最后给出需要长期复用的正式名称。

Schema、协议对象或法律术语可以先定义，以保证精确。定义首次出现时，应同时说明其通俗含义、适用任务或操作影响，让读者能够理解这个名称的作用。

解释性段落应让陌生读者理解三件事：正在描述什么、为什么需要这样规定、会改变什么。纯字段表、枚举、代码块和引用块无需逐项回答这三个问题，但前后必须有足够的用途说明。

交付前统一检查是否存在缺陷。以下任一问题回答“是”，都必须修改或记录为审核发现（finding）：

- 是否在说明任务或对象前引入抽象术语，迫使读者暂存尚未理解的名称？
- 是否有解释性段落无法让读者理解正在说什么、为什么需要，以及会改变什么？
- 是否存在机械编号、教科书式口吻或不自然的概念堆叠？
- 是否在过短的篇幅内引入过多独立概念？
- 是否存在段落间的契约缺口或推理断层？
- 改写是否改变了权威来源中的数字、身份、权限、因果方向、不确定性、兼容性或停止条件？

最后一项检查保护原意。作者只能改善表达的可理解性。若更自然的措辞会改变权威来源的含义，应保留原意，或交由该内容的负责人决定；不得借润色重写契约。

---

<!-- embedded-resource:soul:bestpractice_ai_facing_writing:end -->

## 1. Task

本 Skill 接收明确授权的 Reviewer prompt 编写请求，或已有已审计划中的对应步骤，为一个由目标
Design authority 定义判断标准的 Reviewer 编写或修订 prompt source。直接请求不需要另有 SystemChangePlan。

完整 Reviewer prompt 使用五个固定章节：

1. `0. review_contract_universal`；
2. `1. Review Task`；
3. `2. Inputs, Decision, and Output`；
4. `3. Boundaries and Failure Routing`；
5. `4. Subject Review Checklist`。

本 Skill 只编写第 1 至 3 节。第 0 节由 Review Contract 拥有，第 4 节由目标 Design authority
拥有；两者由 code 根据已登记的 canonical source ref 和 hash 机械注入。成功结果是一份完整、冻结、
返回 Skill Management 的 Reviewer prompt candidate。本 Skill 不执行 `reviewer_reviewer`，不审核
自己的候选，不生成 Skill package closure，不注册 Module，也不选择 provider、model 或 Runtime
profile。

Exact prompt candidate 必须使用已注册的 `reviewer_reviewer` Runtime Module 完成独立审核。Module
route 未注册、未准入或不可执行时，停止交付并返回 Runtime registration 或 execution 的真实
owner；Prompt author 不自审，Primary Agent 不直接代审。

## 2. Reader Gain

冷启动 Primary Agent 只读本 Skill、授权请求或已有计划步骤、Review Contract 和目标 Design
authority 后，可以：

1. 判断请求是否属于 Reviewer prompt source authoring；
2. 写清 Reviewer 要审什么、使用哪些输入、作出什么判断、返回什么结果；
3. 把 target-specific instruction 与 universal instruction、Design checklist 和 invocation data 分开；
4. 形成无需聊天历史或 ambient repository search 也能执行的完整 Reviewer prompt candidate；
5. 在 owner、subject、checklist、schema 或 failure route 不完整时停止，并返回真实 owner。

## 3. Entry and Exit

### 3.1 Entry

只有以下条件全部成立时才进入：

1. 用户已明确授权编写或修改 Reviewer prompt，或已有已审计划将对应步骤交给 `the-review-authoring`；
2. 请求或步骤指定唯一 Reviewer identity、目标 Design authority、被审 subject kind 和 intended result；
3. Review Contract 的 universal source 与目标 Design authority 的 checklist source 均可解析；
4. Reviewer 的 input、output、verdict meaning 和 failure owner 已由对应 authority 定义；
5. 新建任务已比较现有 Reviewer source peer set；更新任务已取得当前 accepted prompt source。

Reviewer 名字、附近 prompt、旧 review output、Runtime Module 或 provider session 不能替代上述
entry 条件。

### 3.2 Exit

- 请求范围、Reviewer identity、target Design authority 或 subject kind 不一致时，说明具体冲突并
  返回请求方；已有计划的步骤错误返回其作者，不要求直接请求先补一份计划。
- Checklist、input/output meaning、verdict meaning 或 failure owner 未由目标 Design authority
  定义时，停止并返回该 authority。
- Universal source、checklist source、current prompt 或 exact bytes 无法重现时，返回
  `blocked_reproducibility`，不创建候选。
- 请求实际改变 Review Contract、目标 Design、Skill lifecycle、Runtime registration 或 release 时，
  退出到对应 owner，不把该变更写进 Reviewer prompt。
- Authoring 完成后交出 exact candidate 与 deterministic composition result。只改 prompt 时直接进入
  独立 `reviewer_reviewer`；containing Skill 的 Task、方法或交接也改变时，先完成该 Skill 的独立审核。
  准确源文件的更新仍按 Skill Management 的负责人和采用规则处理。

## 4. Execution Contract

### 4.1 Inputs and Authority

本 Skill 只使用以下冻结输入：

1. 本次明确授权目标与范围，或已有已审计划及其目标步骤；
2. `designDoc/the_review_contract.md`；
3. 目标 Design authority 及其 exact Reviewer checklist source；
4. Reviewer identity、subject kind、review purpose 和 intended result；
5. allowed core context、optional supporting context 和禁止读取的 context；
6. input schema、output schema、semantic validator 和 verdict meaning；
7. Review Contract universal source 的 exact ref；
8. 更新任务的 current accepted prompt source、predecessor 和必须保留的 meaning。

授权请求或已有计划决定本次 scope。目标 Design authority 决定 Reviewer 要判断的 subject meaning、checklist、
output 和 verdict。Review Contract 决定共同审核纪律与固定 layout。Skill Management 决定 prompt
source 作为 Skill artifact 的完整性。Runtime 只在下游执行已注册 Module。

本次请求或计划步骤的目标、完成条件、相关排除项与后续边界随候选交接。Prior finding 只作为 evidence，
先核对引文、owner、scope、intended result 和本步必要性，再决定是否修订；note 默认不实施，
错误或越界意见附理由交回独立重判，不能把建议改成 authority 或自行把未通过结论改成通过。

### 4.2 Output and Completion

成功时返回：

1. Reviewer identity、目标 Design authority、subject kind 和 intended result；
2. 完整的第 1 至 3 节 source；
3. 由 code 机械加入第 0 节和第 4 节后的完整五章节 prompt candidate；
4. universal source、Design checklist source、input/output schema 和 semantic validator 的 exact refs；
5. changed surfaces、preserved meaning、明确排除项和 predecessor；
6. deterministic composition result，以及后续可交给 `reviewer_reviewer` 的 exact subject。

Candidate 只有在以下结果全部成立时才完成：

- 冷启动 Reviewer 能判断 exact subject、允许证据、判断顺序、输出对象、verdict 和 failure route；
- 第 1 至 3 节没有复制或改写第 0 节和第 4 节；
- invocation data 没有进入 fixed prompt source；
- deterministic code 可以验证五个章节各出现一次、顺序固定、两个机械注入章节逐字同源；
- prompt 没有新增目标 Design 未要求的 object、field、workflow、state、policy 或 mechanism；
- Reviewer author、独立 Reviewer、subject owner、Runtime execution identity 和 admission owner 保持分离。

本 Skill 不计算或手改 hash，不写 manifest/schema/fixture，不生成 host projection，不返回 review verdict，
不注册、执行、发布或部署 Reviewer Module。

## 5. Boundaries

| Boundary | 本 Skill 的职责 | 无声违反时的可观察结果 |
| --- | --- | --- |
| 请求与 authoring | 按直接授权或已有计划步骤编写指定 prompt | Prompt 超出本次范围，或明确授权请求因缺少 SystemChangePlan 被拒绝 |
| Review Contract 与 target Design | 保留 universal 规则和 target checklist 的独立权责 | 第 1 至 3 节重复、概括或改写第 0 节或第 4 节 |
| Authoring 与 review | Prompt 完成机械检查后独立审核；containing Skill 的 Task、方法或交接改变时先审该 Skill | 作者自行返回 `passed`、跳过实际适用的审核，或仅因同目录而重复审核未变 Skill |
| Prompt source 与 invocation data | 固定 instruction 只描述稳定任务 | Candidate 包含本次 subject bytes、临时路径、prior output、credential 或 execution record |
| Skill 与 Runtime | 交付完整 prompt source 和 handoff | Candidate 声称 Module 已 registered、provider 已绑定或 release 已 admitted |
| Deterministic 与 semantic | Code 检查 layout、source、hash 和 schema；Reviewer 判断意义闭包 | 模型被要求核对 byte equality，或 code 被要求推断 checklist 是否充分 |
| Subject 与 context | Core context 只帮助判断 exact subject | Reviewer 获准把辅助材料变成新的 review subject 或修改 peer contract |

## 6. Method

### 6.1 冻结 Reviewer 边界

先写出 Reviewer identity、target Design authority、subject kind、intended result、allowed context、
output、verdict meaning 和 failure owner。任何一项缺失时停止 authoring，不用通用措辞掩盖空缺。

### 6.2 编写第 1 节 Review Task

第 1 节说明 Reviewer 的目的、Reader Gain、exact frozen subject 和 intended result。它必须让执行者
知道自己的判断会帮助哪个 owner 作出什么决定，同时不把辅助 context 或未来 implementation 当成
被审对象。

### 6.3 编写第 2 节 Inputs, Decision, and Output

第 2 节逐项列出 required core input、可按需读取的 supporting context、禁止读取的 context、判断顺序、
output schema、semantic validator 和 verdict meaning。Required input 必须足以完成判断；supporting
context 只能解释 subject，不能扩大 subject。

### 6.4 编写第 3 节 Boundaries and Failure Routing

第 3 节明确 Reviewer 不得编辑、批准、注册、执行或发布 subject。Peer、parent、child 或 implementation
只作为背景；其缺口确实阻止当前判断时说明依赖与真实负责人，不将邻接改进作为 prompt 修订义务。
信息不足、具体缺陷与满足要求按 Review Contract 的既有含义返回；不要在专用部分再写一套通用规则。

### 6.5 机械组装与交接

由 code 把 Review Contract 的第 0 节和目标 Design authority 的第 4 节注入候选，并检查章节 identity、
唯一性、顺序、source bytes、hash、schema 和 projection closure。Primary Agent 只消费检查结果，不手改
机械章节或生成 hash。

冻结后的 exact prompt candidate 在机械检查完成后进入独立 `reviewer_reviewer`。Containing Skill
的 Task、方法或交接同时改变时，先完成其 `skill_candidate_reviewer`，再审核 prompt；仅修改 prompt
时不重复审核未变 Skill。源文件更新由 Skill Management 规定的负责人按准确审核结果完成。Finding 作为
evidence 返回 author，按本次目标与当前必要性处理；实际修订形成新的 exact candidate，并重新经过
适用的 deterministic checks。重开已处理问题说明新证据、候选变化或原处理失败，不逐轮改变完成标准。

### 6.6 Author Self-Check

<!-- embedded-resource:t0:skill_author_self_check:start -->
调用外部 Reviewer 前，author 必须直接消费本 Skill 声明的、由 subject authority 拥有的 canonical checklist，不能手抄第二份 checklist。每次调用只形成临时结果表：

| `check_id` | `exact evidence` | `local result` | `unresolved finding` |
| --- | --- | --- | --- |

每个 required `check_id` 恰好出现一次，并绑定当前 exact candidate 的证据。依据本次授权目标、适用计划步骤、完成条件与排除项判断当前必要性；历史 `prior_findings` 在当前候选上重新核对，不能继承旧 verdict。经核对成立且影响本步完成的必修问题列为 unresolved finding，先在本 Skill 内修订；note 不列入该栏，也不自动实施。对证据错误或越界的历史意见，在 exact evidence 中说明理由并交回独立 Reviewer 重判，不能自行改写原结论。只有没有已知未解决的必修问题时，才冻结候选并调用独立 Reviewer。

Author Self-Check 只防止作者把自己已经看见的缺口交给 Reviewer。它不产生 `passed`、approval、admission 或任何可替代独立审核的结果，也不创建持久化 record、Registry 或跨系统 schema。
<!-- embedded-resource:t0:skill_author_self_check:end -->

Canonical subject checklist：

<!-- embedded-resource:t0:reviewer_prompt_review_checklist:start -->
1. Prompt 清楚说明任务、读者需要的判断、受审对象、必要输入、输出和完成条件。
2. 专用指令保留目标 Design 的判断标准，并与注入的通用规则和 checklist 一致。
3. 模型只承担语义和表达判断，schema、hash、引用和投影等确定性检查交给代码。
4. Prompt 按授权结果、当前层级与计划步骤解释 checklist，要求必修意见说明当前必要性；不把形式完整、未授权机制或合理下层选择变成强制缺陷，也不豁免实际回归。
5. 冷启动 Reviewer 只读完整 prompt 和声明的输入即可工作，能区分候选与背景、缺陷与建议，知道信息不足和计划需要重新判断时交给谁，并保持多轮审核依据稳定。
6. 前五项通过后，检查表达清楚且保持任务、职责、证据要求、输出含义和停止条件。
<!-- embedded-resource:t0:reviewer_prompt_review_checklist:end -->
