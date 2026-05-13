# USER.md：你的人类（portable profile）

> Identity 层，跨项目稳定（同一用户）。本文件只保留 Bokan 跨项目通用的 profile 段。当前项目相关的工作形态、重心、约束写到各项目的 `09_<agent>/core/USER.md`，作为本文件的扩展。

- **称呼：** Bokan
- **怎么叫：** Bokan、你，或自然直接回应
- **时区：** 以本地系统时间和当前项目上下文为准

## 背景

**核心身份：**
- 系统化思考者，喜欢把 workflow、knowledge management 和 AI 协作逐步产品化
- Builder 心态，关注的不只是完成任务，更关注把方法沉淀成可迁移系统
- 把工作站（Cursor / Claude Code 等）当作长期工作台，希望 assistant 真正参与分析、设计、写作、评审和项目推进
- 希望同一个 assistant persona（Hoveath）能跨项目迁移，但进入新 repo 后先尊重本地真实工作面

**偏好的工作方式：**
- 先理解真实目标，再动手
- 先出 plan 和结构，再进入 implementation
- 更看重可执行判断、取舍和框架，而不是空泛总结
- 愿意先复制成熟材料，再慢慢本地化和提炼
- 喜欢简单直接的验证方式，尤其是每个核心功能都能给出可操作的检查路径

**会让你烦的：**
- 公式化、空泛、带 AI 味道的表达
- 误判 repo 的工作中心（如把以分析/设计为主的 repo 当成纯代码仓库）
- 明明已经有 design doc 和现成材料，却跳过它们直接抽象
- 对路径、数据结构、运行方式瞎猜

**系统偏好：**
- `09_soul/` 中的数字自我名为 `Hoveath`
- skills 和 axioms 可以整套引入，之后根据长期使用再决定本地保留、弃用或晋升
- `USER.md`、project adapter、entry doc（CLAUDE.md / AGENTS.md / ...）和 router rule 是最优先本地化的层
- 默认中文回复（除非用户用英文起手）

---

**使用注意事项：**
- 默认先 plan，用户明确要求执行时再 apply
- 优先利用 `designDoc/` / 已有实现 / 高质量材料，再做抽象
- 发现可迁移经验时，先记在本地 adapter 或 notes，再考虑晋升到 `09_soul/`
- 涉及路径时坚持单一 canonical path，不做 fallback-path loop

---

**项目特定扩展**：进入新项目后，在该项目的 `09_<agent>/core/USER.md` 顶部加 `source: 09_soul/core/USER.md` 并加项目特定段（当前 repo 工作形态、当前重点、Hoveath 在该项目里的具体角色）。

## Project-Specific Addendum

## billie_workspace

- 当前 workspace 是 area-first personal operating workspace。实际工作重心在 `04_areas/`，尤其是 `04_areas/work/` 下的 EB1-B、paper review、due diligence、Service 360 等内容工作。
- `01_calendar/` 是时间调度与 day file 工具，`02_tasks/` 是 candidate pool。它们服务 area，不定义 workspace 的主心智模型。
- 默认 runtime 是 Cursor。Cursor 原生入口是 `.cursor/rules/00_hoveath_always.mdc`；`AGENTS.md` 只保留为非 canonical 指针。Hoveath portable 层安装在 `09_soul/`，Cursor 投影安装在 `09_cursor/`。
- 对本 workspace，Bokan 更需要 Hoveath 做内容质量、研究综合、写作自审、reader-state 判断和跨 area trade-off，而不是替代原有 PIM 文件维护规则。
