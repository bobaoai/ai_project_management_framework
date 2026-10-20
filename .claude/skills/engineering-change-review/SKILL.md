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

## 1. Task Summary

使用本 Skill，为完整工程计划或已经冻结的代码提交组织独立工程审核。实施前审核完整 CodeDesignBasis，实施后审核有唯一 parent 的 exact commit。Primary Agent 准备准确材料、调用独立 engineering_change_reviewer，并核验和交付结果。

需要编写或修改工程计划时，使用 engineering-code-design；实现尚未冻结时，先交实现负责人形成准确候选。

## 2. Intended Outcomes

为 Primary Agent 取得并交付准确计划或代码提交的有效独立判断，以及足以支持该判断的实际证据。

1. **受审对象和材料准确。** 计划审核使用完整当前计划及必要依据；实现审核使用有唯一 parent 的准确 commit、对应已审计划和验证材料。背景只服务本次判断，脏工作区及未声明文件不混入受审内容。
2. **专业判断完整且保持独立。** 指定 Reviewer 覆盖 Software Delivery 的九项检查及适用阶段要求。问题有具体证据、依据、当前影响和负责人，Primary Agent 能据此安排修订、补件或争议重判，不能用自检代替独立结论。
3. **实际验证能够支持结论。** 审核使用获准的只读材料和受限工具，必需测试有真实执行证据。命令、范围和结果可核对；确定性与真实运行分别报告。未执行、失败或尚无法验证的事项如实保留，不被改成通过。
4. **返回结果与当前内容一致。** 输出格式、完整检查覆盖、问题与结论的一致性，以及候选、执行身份和命令证据的对应关系经代码核验。旧结果不覆盖修改后的候选，计划通过与实现通过分别表达。
5. **交接说明支持下一步处理。** 有效 passed、non_pass、blocked 与执行或校验失败明确区分。Primary Agent 取得准确结果入口、实际证据、缺口及继续条件，并知道哪些工作可以继续。审核结果交付不代替工程完成，也不增加实施、注册、发布或部署授权。

## 3. Boundaries

Software Delivery 定义工程判断和完成标准，Review Contract 提供共同审核规则。Reviewer 以独立执行身份判断，Primary Agent 负责组织调用和后续处理，不因此取得作者自审资格。

代码固定文件、Git 内容、哈希、schema 和调用范围。Reviewer 判断含义与专业符合性；必要背景只服务当前判断。缺少设计决定时交回 Design 负责人，不能在审核中补定。需要重新统筹跨职责工作时，按 System Change Governance 的适用条件选择入口，不额外强加统一计划前置。

| 分工 | 可观察的越界 |
| --- | --- |
| 计划和实现各审准确对象 | 要求计划提供未来 commit，或把计划通过用于声称实现已完成。 |
| 专业目标由所属 Design 决定 | Reviewer 从代码反推产品要求，或要求重审未改变且仍有效的 Design。 |
| 受审材料只读且范围明确 | 编辑候选，混入脏工作区、未声明文件或其他项目。 |
| 验证服从本次结果 | 把明确延期且不影响当前结果的集成当作缺陷，或把额外探索改成作者声明的必需检查。 |
| 独立判断由实际执行产生 | 作者只阅读同包 prompt 或自行检查一遍，就声称已独立审核。 |
| 审核结果不增加操作权限 | 根据 passed 自动注册 Module、发布或部署。 |

## 4. Inputs and Completion

### 4.1 Inputs

本包的 `runtime_modules/engineering_change_reviewer/` 提供固定 prompt、input/output schema、样例和 registration source。实际调用还须有已配置的独立执行入口及本次需要的受限工具。

共同输入包括 `designDoc/the_software_delivery.md`、授权目标、修改范围、验收要求、完整工程计划和必要 Design/code context。另有 SystemChangePlan 时，提供相关步骤及本批完成条件、排除项和后续边界。历史 finding 只作为本次重新判断的依据。

| 审核对象 | 额外材料与条件 |
| --- | --- |
| 完整工程计划 | 提供准确 CodeDesignBasis。按判断方案的需要取得现有代码和设计，不要求未来实现或未来测试已完成。 |
| 准确代码提交 | 提供仓库、唯一 parent 的 commit、准确对应的已审工程计划及通过记录，以及理解和验证修改所需的代码、声明命令和实际证据。 |

需要执行命令时，明确允许的 argv、工作目录、超时、网络范围、预期结果及其是否必需。时间或机器引用规则只在实际涉及对应语义时，按 Software Delivery 的专业依据条件读取。

未提交实现由实现负责人先冻结，具体 branch 名称不是审核要求。输入、执行条件或授权缺口按第 4.3 节处理，不以附近文件或相似 Reviewer 补齐。

### 4.2 Output

向 Primary Agent 交付经代码校验的独立审核结果、准确对象与执行方式说明、实际验证证据及结果文件入口。缺陷交给相应作者，缺少的决定或条件交给其负责人，交付说明列明本次判断允许继续什么以及仍缺什么。

结果使用同包 Module 的 output schema：`verdict` 表达整体判断，`check_results` 覆盖九项检查，`findings` 给出问题证据与负责人，`safe_next_step` 说明后续处理。第 8 项承载表达检查。受审计划或 commit、调用身份和实际命令证据由代码核对，不能由模型补写。

使用新的结果文件保存本次输出，入口由 `--output` 指定；请求未指定时，组织者选择项目适用的证据位置并报告准确路径。保留已有结果及必要失败材料，不覆盖源文件或历史审核。调用失败时仍交出已完成的材料、真实错误、影响及继续条件，不伪造专业结论。

### 4.3 Completion Contract

本次审核组织工作完成，要求独立结果有效、准确绑定当前对象，所需执行证据经代码核验，并已交给 Primary Agent。有效 non_pass 或 blocked 也是本次审核的可交付结果；工程计划或代码能否继续交付，仍按 Software Delivery 的完成条件判断。

passed 只表示当前受审对象满足要求。计划通过不证明代码完成，实现通过不自动授权发布。候选改变后按所属规则重新审核，旧结果不能覆盖新内容。历史结果保留原样，包括旧七字段格式；需要继续用作当前实施依据的计划，按当前合同重新审核，不直接转换成通过记录。

执行、认证、超时或输出校验失败，没有有效 Reviewer verdict。保留准确候选、已有结果和实际错误，交给接口或执行环境负责人；缺少 Design 或权限决定时交给有权决定者。必要条件修复后重试相应步骤。不能替换为相似 Reviewer 或由作者代审，也不能把停止等待当作原工程任务已完成。

## 5. Method

### 5.1 使用共同审核规则

以下内容来自本 Skill 声明的 Review Contract 共享资源。它约束审核范围、问题判断和多轮处理；工程专业标准使用 Software Delivery 的 checklist。

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

### 5.2 准备准确内容和工具边界

先确定本次审计划还是审实现，再按第 4.1 节收齐材料。计划审核固定完整正文和必要依据；实现审核固定 commit 及其唯一 parent，并保留已经通过的准确计划审核记录。

Portable Governance 的工程审核工具从 Git 对象取得变更文件两侧版本及准确 diff。理解上下文或运行测试需要的未变更文件和目录，通过 `--read` 声明；未提交工作区内容不会进入。补充材料先加入本次准确输入，不允许 Reviewer 自由读取整个工作区。

命令计划使用 JSON 数组。每项字段采用当前 input schema 的 `command_id`、`argv`、`cwd`、`timeout_seconds`、`network_policy`、`expected_result` 和 `required`。`required` 默认 true，只有明确的补充探针设为 false。声明命令同时成为 Runtime 可执行范围，未实际运行的命令不能报告 passed。

命令在受审代码中运行时，cwd 使用 `source/commit/子目录`；临时草稿或补充测试使用 `scratch`。额外只读依赖目录用 `--dependency` 声明。受审代码始终只读，Engineering 入口不接受 `--resources`。

### 5.3 调用工程审核入口

在项目根目录使用项目配置的 Python。完整计划外审：

```sh
python -B 09_soul/governance/t0/validation/software_delivery/engineering_review.py \
  --plan path/to/plan.md --goal "授权目标" --change "本次范围" \
  --criterion "验收要求" --context path/to/needed_design.md \
  --output path/to/new_plan_review.json --root path/to/runtime_root
```

实现审核增加 `--repository`、`--commit` 和 `--plan-review`，仍使用相同计划与验收要求：

```sh
python -B 09_soul/governance/t0/validation/software_delivery/engineering_review.py \
  --plan path/to/plan.md --repository . --commit COMMIT \
  --plan-review path/to/passed_plan_review.json \
  --goal "授权目标" --change "本次范围" --criterion "验收要求" \
  --commands path/to/commands.json --read path/in/commit \
  --output path/to/new_code_review.json --root path/to/runtime_root
```

| 参数或组合 | 使用条件和作用 |
| --- | --- |
| `--criterion`、`--context` | 可以重复，分别提供验收要求和明确背景。 |
| `--read` | 可重复，指定 commit 中需要补充读取的文件或目录。 |
| `--commands`、`--dependency` | 声明命令及其额外只读依赖，边界见第 5.2 节。 |
| `--system-change` | 仅在另有相关统一计划步骤时提供。 |
| `--prior-findings` | 提供需要在当前候选上重新判断的历史意见。 |
| `--check-only` | 检查并输出准确输入，不调用模型。 |
| `--check-only --self-check-template NEW_PATH` | 生成计划作者的临时自检表，代码填入内容哈希和完整 check_id。作者填写具体证据、本地判断与未解决问题。 |
| `--self-check` | 计划作者提供已完成的临时 JSON，工具核对当前计划哈希、检查覆盖及未解决问题。已有的人类计划可以直接受审，不要求补造 Agent 自检经历。 |

该入口经 Portable Governance 的 `09_soul/governance/t0/validation/runtime_review.py` 调用 Agent Runtime Test Run，运行已注册的 engineering_change_reviewer。`--root` 必填，定义来源和执行参数见 `09_soul/governance/README.md` 的“独立审核的执行”。工具不内置模型或数据库连接，不临时注册 Module。

明确授权采用等价的非 Runtime 外审入口时，保持相同指令、准确材料、受限工具和输出校验，并如实标明执行方式。上述工程审核 CLI 不因这项授权自动改变执行路径。工具冻结输入、调用独立 Reviewer、核对完整输出与绑定，再独占创建新的结果文件，不覆盖源或既有结果。

### 5.4 观察运行并收回结果

运行中观察需要支持 `progress_observer` 的 Runtime。实际 transport 为 `claude_cli` 时，上述工程审核 CLI 自动向 stderr 输出 `runtime_process_progress` JSON 行，无需额外进度参数。它给出 PID、进程存活、耗时、接收字节数，以及初始化、模型活动、工具请求与返回、最终结果等安全摘要。Runtime 管理的声明命令还给出 `command_id` 和开始、结束状态，摘要不含正文、工具参数或工具输出。

其他 transport 不产生这类更新，通用 Test Run CLI 也没有同名进度开关。直接使用 Runtime Python API 的宿主，通过 `run_local_workflow_test(..., progress_observer=...)` 接入。

静默 10 秒后的心跳会重复最后事件。慢接收者可能丢失更新，`updates_dropped` 给出计数。字节数为零或状态暂时不变，不能证明模型已经停止。沿当前调用收回最终结果，以执行事实和语义校验判断完成，不根据进度摘要给 verdict 或重复发起审核。

这个入口只实时显示过程摘要。最终 `--output` 保存精简审核结果及必要身份、输入绑定和命令证据，不保存原始过程流或进度历史；观察进度无需额外重定向 stderr。

### 5.5 核对独立结论并交接

先确认代码接受执行记录和输出，再消费专业结论。实现审核应读取准确代码并复现必需测试；允许的补充探针在声明的工具和临时目录范围内运行。同一 Reviewer 按需要使用读取、搜索和命令工具，不要求每次用完全部工具。

测试证据按 `deterministic` 与 `real_run` 分开报告。新增或行为被修改的测试只带其中一个 marker。经过 Provider、Runtime 执行或数据库的测试必须为 real_run，使用真实路径和依赖，不接受替身；写明实际入口、版本、输入和结果，未执行的标为未验证。已有 fake_run 不能算真实链路验收，不能把各类结果合并成一句“全部通过”。

核对 Reviewer 结果是否按完整 Software Delivery checklist 覆盖当前对象，不在本 Skill 另写专业标准。必修意见先核对证据、当前后果和本批必要性：成立的缺陷交作者，缺少 Design 或权限决定交有权负责人，环境问题交执行负责人。note 默认不实施；错误或越界意见附理由请求独立重判，不能自行修改未通过结论。真实回归仍须处理；只有满足第 5.1 节规定的重开条件时，才重新打开已处理的问题。

交付时说明准确审了什么、实际执行了哪些检查、验证仍有哪些缺口，以及结论只适用于计划、某个 commit 或哪个有限范围。按第 4.3 节区分审核结果交付与整个工程任务完成。
