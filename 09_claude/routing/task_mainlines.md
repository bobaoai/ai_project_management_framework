# Task Mainlines — Hoveath 母仓库

母仓库工作的主线 → first authority → truth surface → downstream skill 路由表。
本文件被 [`CLAUDE.md`](../../CLAUDE.md) 的 Routing Table 摘要 section 指向，CLAUDE.md 只放摘要、详细路由在这里。

## 主线表

| Signal（中英文触发词） | Mainline | First Authority | Truth Surface | Downstream Skill |
|---|---|---|---|---|
| 「新 axiom」「修订 axiom」「公理」「propose new axiom」 | axiom 维护 | [`09_soul/axioms/INDEX.md`](../../09_soul/axioms/INDEX.md) | [`09_soul/axioms/`](../../09_soul/axioms/) | self_review + 编号 reconciliation（见 [`09_soul/axioms/a20_*.md`](../../09_soul/axioms/a20_reader_persona_primacy.md) frontmatter 范例） |
| 「新 skill」「skill 升级」「写技能」「meta-skill」 | skill 维护 | [`09_soul/skills/INDEX.md`](../../09_soul/skills/INDEX.md) | [`09_soul/skills/`](../../09_soul/skills/) | [`bestpractice_skill_writing.md`](../../09_soul/skills/bestpractice_skill_writing.md) |
| 「sync」「mirror」「core 改了」「drift」 | mirror 同步 | [`09_soul/bridging/`](../../09_soul/bridging/) | [`09_soul/bridging/mirror_manifest.json`](../../09_soul/bridging/mirror_manifest.json) | [`bestpractice_mirror_sync.md`](../../09_soul/skills/bestpractice_mirror_sync.md) |
| 「装 Hoveath」「bootstrap」「Phase 1-7」「install」 | installation | [`09_soul/handoff/installation_guide.md`](../../09_soul/handoff/installation_guide.md) | [`09_soul/examples/`](../../09_soul/examples/) | n/a |
| 「蒸馏」「distill」「promote」「lesson 回流」「fork drift 治理」 | distillation | [`09_soul/handoff/distillation_protocol.md`](../../09_soul/handoff/distillation_protocol.md) | [`09_soul/`](../../09_soul/) + host 项目 | self_review |
| 「retrospective」「复盘」「下次怎么改」「lesson」 | retrospective | n/a | n/a | [`bestpractice_retrospective_writing.md`](../../09_soul/skills/bestpractice_retrospective_writing.md) |
| 「persona」「读者」「服务谁」「reader」「为谁写」 | reader-persona 锁定 | [`09_soul/axioms/a20_reader_persona_primacy.md`](../../09_soul/axioms/a20_reader_persona_primacy.md) | [`09_soul/personas/`](../../09_soul/personas/) | self_review |
| 「parallel agent」「并行 subagent」「多 agent」 | 并行调研 / 多 agent | n/a | n/a | [`workflow_parallel_subagents.md`](../../09_soul/skills/workflow_parallel_subagents.md) |
| 「调研」「research」「deep survey」「topic 调查」 | 深度调研 | n/a | n/a | [`workflow_deep_research_survey.md`](../../09_soul/skills/workflow_deep_research_survey.md) |
| 「debug」「不稳定」「错了」「为什么 fail」 | 调试诊断 | A15 通路层诊断 + A19 概率性面积 | 报错日志 / 通路层 | [`bestpractice_ai_debugging_diagnosis.md`](../../09_soul/skills/bestpractice_ai_debugging_diagnosis.md) |
| 「README 重写」「INDEX 重写」「顶层 doc」 | 顶层 doc 重写 | n/a | 当前 doc 本身 | [`bestpractice_doc_self_review.md`](../../09_soul/skills/bestpractice_doc_self_review.md)（强制） |
| 「temporal」「日期」「now」「latest」 | 时间锚定 | V04 + T11 | n/a | [`bestpractice_temporal_info_verification.md`](../../09_soul/skills/bestpractice_temporal_info_verification.md) |

## Overlay Rules

某些 signal 不是独立主线，而是叠加在主线之上的修饰。**Overlay 不重定向主线**，只增加额外 contract。

| Overlay Signal | 修饰行为 |
|---|---|
| 文件位于 `09_soul/core/*` | 改完后必须 `python 09_soul/bridging/mirror_sync.py --check`；drift 时 `--apply` |
| 文件位于 `09_soul/axioms/*` | 必须同步更新 [`09_soul/axioms/INDEX.md`](../../09_soul/axioms/INDEX.md) 条目 + 触发词 |
| 文件位于 `09_soul/skills/*` | 必须同步更新 [`09_soul/skills/INDEX.md`](../../09_soul/skills/INDEX.md) 条目 |
| 任务输出是 Proposal / Plan / Design / 多 section 长 response | 触发 R11 doc-self-review（FP7 canonical 路径） |
| 任务跨 ≥3 轮推进 | 尾部加 R13 全局进展快照 |
| 输出引用某个 host 项目（trading_platform / 未来项目） | 同步检查是否应促成 promotion 候选写入 `examples/<project>/` 的 retrospective notes |

## Package-Review Rule

当一次任务涉及 ≥2 个 mainline 时（如「修一条 axiom 同时升级一个 skill」），按下面顺序处理：

1. 先识别所有命中 mainline，列出
2. 按依赖序处理：axiom 改动 → 影响 skill → 影响 routing / rules → 影响 doc
3. 处理完所有 mainline 后做一次跨主线一致性 check（INDEX 是否同步、skill frontmatter 是否反映新 axiom、CLAUDE.md routing 是否要更新）
4. 整体作为一个 Proposal 走 self-review

不要在 mainline 之间来回跳，会污染 doc-level coherence。

## 未命中处理

未命中任何 signal 时，按这个顺序自行判断：
1. First Principles 7 条
2. [`09_claude/core/PROJECT_ADAPTER.md`](../core/PROJECT_ADAPTER.md) 的 promotion filter / 角色定义
3. 主动反问用户 framing（FP1）
