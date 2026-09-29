# Project Documentation Reviewer source

Runtime Module 目录包含固定 Reviewer prompt、输入输出 schema、注册源和用例声明；完整输入输出 fixtures 保存在包根目录的 fixtures 子目录。它们是待独立审核的任务定义，文件存在不表示已经注册、已执行或已通过。

## 输入和引用

`review_request` 给出授权目标与修改范围。`candidate_documents` 是唯一受审集合，每份文稿同时说明用途、读者行动、阶段和是否按正式 Design 交付。`context_documents` 提供必要背景，不能自动成为修改目标。`prior_findings` 是当前内容上需重新判断的历史意见。

`document_ref` 由调用方分配，在一次输入的候选与背景联合集合内唯一，按准确字符串判等。它指向本次随输入提供的正文，不是文件读取许可，也不表示持久对象身份。`owner_ref` 说明相应决定或修订的负责人，调用材料需使该角色可理解。缺件通过结果返回负责人，不由 Reviewer 从名称猜测真实授权。

输入和输出 schema 中的版本引用标识协议定义；不表示候选文稿的采用版本。schema 无时间字段。执行绑定与内容摘要由现有宿主工具记录，不要求模型生成。

## 结果使用

输出继承 Runtime 共同的四个字段。`check_id` 的取值来自 T0 中的专用 checklist；finding 中的同名字段表示主要根因归类，其他检查可以引用同一 finding。

格式校验之外，采用环境还必须核对：

- 输入文档引用在联合集合内唯一；候选与背景可区分。
- 检查项恰好按 T0 列出的九项出现一次；finding_id 唯一，引用无悬空。
- 仅技术与跨文档一致性项允许按 T0 条件使用 `not_applicable`。语义项缺必要依据时使用 `finding` 并关联 `block`。
- 语义未全部通过时，表达项为 `not_run`；通过时完成表达判断。
- `finding` 项至少关联一条 `fix` 或 `block`；`note` 可以关联 `passed` 项。所有必修问题均被检查项引用。
- `fix` 的证据指向准确候选，`block` 可以指出声明背景中的必要缺件。证据位置的有效性和主张支持程度分别由代码与 Reviewer 按实际能力检查。
- 有 `block` 时 verdict 为 `blocked`；无 block 且有 fix 时为 `non_pass`；全部适用检查完成且没有必修问题时为 `passed`。
- 返回结果确实对应本次候选、固定指令与独立执行。源内容改变后不能套用旧结果。

本目录未提供或安装新的宿主执行适配器、专业输出校验器或持久结果服务。上述专用校验接入是运行采用的必要条件，当前确定性记录仅证明 schema 与固定 source 的相容性。注册、执行和完整输出校验应由采用环境沿现有 Runtime 和对象 owner 入口落实。

## Fixtures

`fixtures/project_documentation_reviewer/positive_case.json` 包含格式合格的输入与作者编写的预期输出。同目录的 `negative_extra_field_case.json` 和 `schema_drift_case.json` 验证额外输出字段与未知检查项被 schema 拒绝。它们均不是模型执行结果。tests 子目录 保留安装器要求的五字段用例声明，具体输入输出放在 `fixtures/`，两者都属于同包资源。

专业判断场景见 `../review_cases.md`；实际测试时预期只交给结果评价者，不能混入被测 Reviewer 的输入。
