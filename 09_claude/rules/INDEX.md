# Rules INDEX — Hoveath 母仓库

R-rules 的优先级、加载时机与分组。CLAUDE.md 的「Core Rules」section 引用本 INDEX；具体 rule 详细解释（如果 inline 写不下）落到独立文件。

## 优先级（高 → 低）

1. **First Principles**（[`09_soul/axioms/FP_first_principles.md`](../../09_soul/axioms/FP_first_principles.md)） — Philosophy 层最高优先级，跨项目跨 agent，先于所有 R-rule
2. **R-rules `<portable>`** — 跨项目稳定的工作约束（多数）
3. **R-rules `<portable-shape>`** — 形状稳定但项目可能调参（如 mirror_sync 路径在所有项目都用，但具体 marker 文本可项目特化）
4. **R-rules `<project>`** — 母仓库特定 tripwire（如「不写业务 skill」「不动 .cursor/」）
5. **Task-scoped rules** — 进入特定任务模式时按 INDEX lazy-load（暂未拆分独立文件，先 inline 在 CLAUDE.md）
6. **Routing Table** — [`../routing/task_mainlines.md`](../routing/task_mainlines.md) 决定主线落点

冲突时：高层覆盖低层；R-rule 之间冲突时按编号小者优先（编号是分组顺序，不是绝对优先级）。

## 加载时机

| 时机 | 加载内容 |
|---|---|
| Session 启动 | First Principles + 全部 R01-R13（已 inline 在 CLAUDE.md） |
| 命中 mainline | mainline 对应的 first authority + downstream skill |
| 编辑 09_soul/core/* 后 | mirror_sync overlay |
| 交付 Proposal 类输出前 | doc_self_review skill |
| 走完完整 dogfood 周期且用户问 retrospective 时 | retrospective_writing skill |

## R-rules 分组

### 系统结构（R01-R03） `<portable>`

约束工作姿态本身。

- **R01** plan-first：非 trivial 改动先出 plan / 结构再 implement
- **R02** 单一 canonical path：路径、数据结构坚持单一来源，不做 fallback-path loop
- **R03** 默认中文回复（用户用英文起手才用英文）

### 交付质量（R04-R06） `<portable>`

约束输出形态。

- **R04** 不假装完成：跑不通的、半成品都要明说
- **R05** 不替用户决策：高 leverage 决策先 propose 再 apply
- **R06** 引用用相对路径 markdown 链接（方便点击跳转）

### Source-of-truth 卫生（R07-R08） `<portable-shape>`

约束跨投影 / 跨编号一致性。

- **R07** mirror_sync 是 09_soul/core 唯一同步路径（手抄禁止）
- **R08** 编号守则：新增前先扫 INDEX；冲突按时间序处理

### 母仓库 tripwire（R09-R10） `<project>`

母仓库特有，host 项目不继承（host 项目应有自己的 tripwire）。

- **R09** 母仓库不写业务 skill：trading / Fed-watcher 等领域 skill 属于 host 项目，本仓库 `.claude/skills/` 只放跨项目 baseline
- **R10** examples/ 是验证集：host 项目蒸馏来的内容是参考，不能反向定义协议

### 协议触发（R11-R13） `<portable>`

约束什么时候自动调 skill / 加 section。

- **R11** doc-self-review 触发：交付 Proposal 类输出前调用 doc_self_review skill（FP7 canonical 路径）
- **R12** retrospective 触发：完整 dogfood 周期走完且用户问"下次怎么改进 / lesson"时调用 retrospective_writing skill
- **R13** 全局进展快照：跨多轮推进的项目 / 重构 / 迁移在尾部加 2-5 句进展快照；单轮一次性问答不加

## 标签语义

- **`<portable>`**：母仓库与所有 host 项目共用，蒸馏时直接拷
- **`<portable-shape>`**：结构跨项目通用，具体参数项目特化（如路径 / 命令 / marker 文本）
- **`<project>`**：母仓库特有 tripwire，蒸馏到 host 项目时改为各自特化版本（host 项目要有自己的 R09/R10 等价物，但内容不同）

蒸馏时只回吐 `<portable>` 与 `<portable-shape>` 的骨架；`<project>` 留 examples 作 tripwire 范例。

## 后续拆分时机

当某条 R-rule inline 在 CLAUDE.md 写不下（需要超过 2 行解释、需要范例、需要"违反时长什么样"的检测式描述）时，独立成文件 `R<NN>_<slug>.md`，CLAUDE.md 改为指针。

当前 R01-R13 都还能 inline，未拆分。
