---
name: engineering-change-review
description: 组织代码修改方案或准确代码提交的独立工程审核，提供对应设计依据和必要验证材料，核验审核结论与受审对象、执行证据的一致性。
metadata:
  skill_class: primary_agent_development
  primary_agent_entry_role: review
  primary_agent_entry_subject: engineering_change_candidate
  first_authority_ref: designDoc/the_software_delivery.md
---

# 独立工程审核

## 1. Task

帮助 Primary Agent 准备和组织 Software Delivery 的独立审核。实现前审完整 CodeDesignBasis/plan doc，
实现后审有唯一 parent 的 exact commit，两种结果准确绑定各自对象。

本 Skill Package 携带 engineering_change_reviewer 的固定 prompt、schema、fixtures 和 registration
source。Reviewer 以独立执行身份作判断；Primary Agent 组织调用，不因此取得作者自审或部署权限。

## 2. Reader Gain

Primary Agent 能确定本次审的是计划还是实现，准备足够材料，使用现成工具调用独立 Reviewer；能区分
需要修方案或代码、缺少依据，以及工具执行失败，不把一个 passed 用到另一个对象上。

## 3. Entry and Exit

工程计划需要实施前外审，或代码已经形成可复现的 exact commit 时进入。先取得本次授权目标、范围
和验收要求。计划审核不要求未来代码；实现审核必须提供准确对应的已审计划及通过结果。

设计含义缺失时返回 Design owner；需要跨职责重新拆分时返回 System Change；不能在审核中补设计。
尚未提交的实现先由实现负责人冻结，脏工作树不成为审核对象。具体 branch 名称不是审核要求。

完成时交付准确绑定的独立结果及验证记录。失败时保留真实问题，不声称已经审核通过。Reviewer 或
所需工具不可用时返回执行环境负责人；不换相似 Reviewer，也不由作者直接代审。

## 4. Execution Contract

### 4.1 Inputs and Authority

- designDoc/the_software_delivery.md：本次工程判断与完成标准。
- 完整 CodeDesignBasis、授权目标、修改范围、验收要求及必要的 Design/code context。
- 审实现时的 commit、仓库和计划外审记录；另有 SystemChangePlan 时提供相应步骤。相关计划的本批完成条件、排除项和后续边界一并作为审核依据。
- 明确允许的命令、工作目录、超时、网络范围和预期结果；需要重新判断的 prior_findings。
- 已配置的独立 engineering_change_reviewer 执行入口与必要工具。

代码固定文件、Git 内容、hash、schema 和调用范围。Reviewer 判断计划与实现的含义；背景不是额外
subject。实际涉及时间或机器引用时按 Software Delivery 的对应 T0 引用取得依据，不加载无关材料。

### 4.2 Output and Completion

返回代码核验过的工程结果：verdict、check_results、findings 和 safe_next_step。具体字段以同包
Runtime Module 的 output schema 为准。check_results 覆盖 Software Delivery 的九项检查，
第 8 项承载表达检查；代码核对受审计划或 commit，以及 Runtime 实际记录的命令证据。

passed 表示当前对象满足要求；non_pass 表示存在可修复缺陷；blocked 表示缺少必要判断条件。
计划通过不证明代码完成，实现通过也不自动授权发布。执行或输出校验失败没有有效 verdict。
修改候选后重新审核，旧结果不覆盖新内容。
历史七字段结果保留原样；需要继续用作当前实施依据的计划，按新合同重新审核，不直接转换成通过。

## 5. Boundaries

| 边界 | 可观察的越界 |
| --- | --- |
| 对象明确 | 要求计划提供未来 commit，或把计划通过结果用于实现交付 |
| 主责设计在上游 | Reviewer 根据代码反推产品目标，或要求重审未改的有效 Design |
| 候选准确且只读 | 修改受审文件，混入脏工作树、未声明文件或其他项目 |
| 按本次范围验证 | 把明确延期的集成当作当前缺陷，或将额外探索写成作者声明的 gate |
| 作者与 Reviewer 分开 | 只阅读同包 prompt 或自行核对一遍就宣称完成独立审核 |
| 审查不增加权限 | 根据 passed 自动注册 Module、发布或部署 |

## 6. Method

### 6.1 通用审核规则

<!-- embedded-resource:t0:review_contract_universal_review_style:start -->
- 以本次用户授权目标、适用上游规则及已确定的计划为依据。已有计划时，使用当前步骤、完成条件、相关排除项与后续边界；所属方法无需正式计划时，使用明确授权请求，不追加计划或 Registry 前置。候选自行增加的承诺不自动成为必须补全的要求。
- 只审明确提供的候选及本次修改范围。可读取完整候选与必要背景；读取范围不等于修改范围，背景不因载入而成为新的修改目标。
- 先按目标 checklist 完成语义判断，语义通过后再检查同一份内容的表达。完整检查指在当前对象、层级和交付阶段内检查完整，不是补齐整个相关系统。只返回约定的结果对象。
- 每项必修问题说明实际适用的要求、候选证据、不修会使本步哪项结果失败或造成什么实际回归，以及为什么必须现在处理。合理留给下一层或后续步骤且不影响当前结果的选择，不是当前缺陷。
- 不为形式完整要求新增未被授权目标或适用规则需要的 object、field、workflow、state、lifecycle、policy 或 mechanism。宽泛的完整性、未来收益或最佳实践偏好本身不足以支持 fix 或 block；真正影响当前结果的多余机制仍可报告。
- 审计划时判断方案能否达到授权目标；审其下游产出时保持已确定的范围与取舍。真实依赖缺失、适用规则冲突、新证据或原处理失败，可以证明原决定需要重新判断。说明受影响结果与负责方；提出问题或挑战排除项不授予扩展工作的权限。本次修改造成的实际回归不因计划未逐字列出而获得豁免。
- 同一根因只报告一次，可以关联多个检查项。一次返回当前可判断的全部问题，不设置 finding 数量目标。
- 按下表区分具体缺陷、阻断判断的缺口和可选建议；不能用措辞强弱、个人偏好或凑数决定标签。
- 说明必须恢复的结果，不替作者指定唯一修法。其他负责人的问题说明影响并交回真实负责人，不能借本次审核扩大修改范围。
- 表达检查保持事实、数值、归因、职责、因果、不确定性、兼容性和停止条件；不能用润色改变设计或判断。审查修订后的候选时，结合受影响的完整段落、章节或接口说明，判断修改是否放在承载该职责或含义的位置，是否与上下文的术语、结构、逻辑及交接一致；检查局部修改造成的突兀插入、重复、前后矛盾或引用错位。
- 对文档、Skill、Reviewer prompt、代码注释和 docstring，按各自用途检查长期使用的正文是否混入本次讨论、修复或测试的过程信息；工作记录和变更日志可以保留相应过程。发现表达问题时，指出准确位置、上下文关系及对读者理解或操作的影响，交由作者修订。检查完整上下文不扩大本次修改范围；必修缺陷与可选润色仍按下表区分。
- 多轮审核沿用同一授权目标和完成标准。历史 finding 在当前候选上重新核对，不继承旧 verdict；允许提出此前漏掉的真实缺陷。重新打开已处理或已裁决问题时，说明新的证据、候选变化或原处理为何未解决问题。
- 审核不编辑候选，不增加用户授权。Primary Agent 先核对意见的依据、范围和实际后果，再修订成立的必修问题；note 默认不进入本轮实施。争议通过证据与范围理由交回独立 Reviewer 重判，作者不能自行把未通过结论改成通过。

审查的整体结论与单条问题标签分开使用：

| 整体结论 | 成立条件 |
| --- | --- |
| `passed` | 规定检查已经完成，产出达到本次授权目标，且没有 `block` 或 `fix`。可以包含 `note`。 |
| `non_pass` | 已有足够依据判断产出，但存在至少一项 `fix`，且没有阻断判断的 `block`。修订后重新审查。 |
| `blocked` | 至少一项必要判断因 `block` 无法成立。返回所缺依据或决定及其提供方；已经发现的 `fix` 仍可同时报告。 |

| 问题标签 | 使用条件 | 必须说明什么 |
| --- | --- | --- |
| `fix` | 有证据表明当前产出违反授权目标或实际适用的规则，影响本步完成条件或造成实际回归，且作者能在本次范围内修正 | 具体证据、实际适用的要求、当前后果、为什么必须本步处理及需要恢复的结果 |
| `block` | 缺少必要依据、存在无法自行裁决的规则冲突，或需要其他负责人先作决定，使当前必要判断无法成立 | 哪项当前判断无法完成、缺什么或冲突在哪里、为什么不能合理留给后续、为什么不能在当前范围内解决、谁能提供依据或决定 |
| `note` | 当前要求已经满足，意见只是可选改进；不采用也不会损害本次结果 | 可选改进带来的收益，并明确它不构成通过条件 |

已能确认的严重缺陷仍按 `fix` 处理；修复前不能通过。`block` 表示判断所需的前提不成立，不是
“更严重的 fix”。Reviewer 不能只因自己犹豫就写 `block`，也不能把必须修复的问题降为 `note`。
一句话不够顺但意思清楚，可以是 `note`；如果歧义会导致读者作出错误动作，则是有证据的 `fix`。
只是更喜欢另一种写法、额外机制或未授权功能，不能形成必须解决的问题。

代码校验结论与标签、检查覆盖和候选绑定是否一致；是否真正违反要求仍由 Reviewer 给出证据。
调用超时、认证失败或输出格式无效是执行或校验失败，没有有效 Reviewer verdict，不能伪装成
`passed`、`non_pass` 或 `blocked`。
<!-- embedded-resource:t0:review_contract_universal_review_style:end -->

### 6.2 使用随包入口

在项目根目录，使用当前项目 Python。完整计划外审：

```sh
python -B 09_soul/governance/t0/validation/software_delivery/engineering_review.py \
  --plan path/to/plan.md --goal "授权目标" --change "本次范围" \
  --criterion "验收要求" --context path/to/needed_design.md \
  --output path/to/new_plan_review.json --root path/to/runtime_root
```

实现审核在同一命令上增加 --repository、--commit 和 --plan-review，仍使用相同计划和验收要求：

```sh
python -B 09_soul/governance/t0/validation/software_delivery/engineering_review.py \
  --plan path/to/plan.md --repository . --commit COMMIT \
  --plan-review path/to/passed_plan_review.json \
  --goal "授权目标" --change "本次范围" --criterion "验收要求" \
  --commands path/to/commands.json --read path/in/commit --output path/to/new_code_review.json \
  --root path/to/runtime_root
```

实现审核时，工具从 Git 对象冻结受审 commit 交给 Reviewer：变更文件在 commit 与 parent 两侧的版本及准确 diff，
以及 --read 指定的 commit 中未变更文件或目录（理解上下文或运行测试所需，可重复）；工作区中未提交的内容不会进入。
--commands 中的命令同时成为 Runtime 可执行的命令：cwd 写 source/commit/子目录（在受审代码中运行）或 scratch，
命令需要的额外只读目录用 --dependency 提供。Engineering 入口不接受 --resources。

--criterion 和 --context 可以重复；--system-change 仅在另有相关计划步骤时提供，--prior-findings
接收需要重判的意见。--check-only 只检查并输出输入，不调用模型。命令文件是 JSON 数组，每项使用
当前 input schema 的 command_id、argv、cwd、timeout_seconds、network_policy、expected_result；
required 默认为 true，只有明确的补充探针设为 false。实际未运行的命令不能报告 passed。
同一个 Reviewer 默认具备声明的读取、搜索和授权命令能力，按本次任务需要调用；不要求每次使用全部工具。
--check-only 可配 --self-check-template NEW_PATH 生成计划作者的临时自检表；代码填写 hash 与完整
check_id，作者填写具体证据、本地判断和未解决问题。
计划作者提供 Author Self-Check 时，用 --self-check 传入其临时 JSON；工具核对当前计划 hash、
check_id 覆盖与未解决问题。已有的人类计划可直接受审，不要求补一份 Agent 自检经历。

审核经随包 runtime_review.py 调用 Agent Runtime Test Run 运行已注册的 engineering_change_reviewer；
--root 必填，定义来源、执行参数与资源参数见 Portable README“独立审核的执行”。Portable 工具不内置
模型或数据库连接，不临时注册 Module；未经 Runtime 的明确授权外审要如实记录实际执行方式。工具冻结
输入、调用独立 Reviewer、检查完整输出与绑定，独占创建新结果文件，不覆盖源或既有结果。

实现审核的测试证据按 deterministic 与 real_run 分别提供和核对：每个新增或行为被修改的测试只带其中一个
marker，经过 Provider、Runtime 执行或数据库的测试必须是 real_run，不接受替身；real_run 写明实际入口、
版本、输入和结果，未执行的标为未验证；已有 fake_run 测试不计为真实链路验收。各类结果不合并成一句
“全部通过”。

### 6.3 核对结果与下一步

先看代码是否接受执行记录和输出，再消费语义结论。按完整 Software Delivery checklist 判断当前对象，
不在本 Skill 重写检查标准。实现审核应读取准确代码并复现所需测试；补充探针只在明确允许的工具与
临时目录中运行，不把代码风格偏好当成语义缺陷。

必修意见先核对证据、当前后果和本批必要性；成立的缺陷返回作者，缺少 Design 或权限决定返回
负责人，环境失败返回执行负责人。note 默认不实施；错误或越界意见说明理由并请求独立重判，不自行
改写未通过结论。真实回归仍须处理，已经解决的问题按第 6.1 节的同一依据重判。
完成后明确说明审了什么、实际运行了哪些检查，
以及当前结果是否只针对计划、某个 commit 或某个有限范围。
