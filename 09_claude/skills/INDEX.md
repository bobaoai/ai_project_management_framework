# Skills INDEX — 09_claude（母仓库 baseline）

本目录是 [`09_soul/skills/`](../../09_soul/skills/) 的 **baseline 子集 mirror**。完整 skill 清单（含业务工具与弃用 skill）见 [`09_soul/skills/INDEX.md`](../../09_soul/skills/INDEX.md)。

## Baseline 边界

09_claude/skills/ 只 mirror **跨项目通用、领域无关**的 skill：
- 不依赖外部 API 凭据（无需 Gmail / Google OAuth / GA4 token）
- 不依赖项目业务术语（Trading / Fed / Marketing 都用得上）
- 不在 INDEX 中标记弃用

业务 skill（gemini_image / send_email / google_docs / typefully_metrics 等）与已弃用 skill（workflow_bilibili / share_report 等）只在 09_soul/skills/ 保留，不进 mirror。host 项目按需自行添加。

## Baseline 清单（14 个）

### Doc / Skill 写作

- [bestpractice_doc_self_review.md](bestpractice_doc_self_review.md) — FP7 / R11 canonical 路径：交付 Proposal 前三阶段 self-review
- [bestpractice_skill_writing.md](bestpractice_skill_writing.md) — meta-skill：怎么写 skill（含原则四五 + AI-facing detail-first 6 问）
- [bestpractice_retrospective_writing.md](bestpractice_retrospective_writing.md) — R12：dogfood 周期完成后的复盘协议（含 Item schema + validation kind + trigger placement）
- [bestpractice_reader_state_and_judgment_gain.md](bestpractice_reader_state_and_judgment_gain.md) — 先定义读者读完获得的判断能力，再决定结构（含 multi-agent handoff reader-gain 化）
- [bestpractice_prose_without_editorial_meta.md](bestpractice_prose_without_editorial_meta.md) — sentence-level 守门：写关于世界，不写关于稿件
- [bestpractice_prompt_boundary.md](bestpractice_prompt_boundary.md) — A14 canonical 操作路径：下游 prompt 只放 task-plane

### Bridging / 系统卫生

- [bestpractice_mirror_sync.md](bestpractice_mirror_sync.md) — 09_soul/core ↔ 09_\<agent\>/core 同步触发条件与协议
- [bestpractice_staged_approach.md](bestpractice_staged_approach.md) — 隔离-处理-验证（T07）的实操形态；破坏性操作前 dry-run
- [bestpractice_temporal_info_verification.md](bestpractice_temporal_info_verification.md) — V04：验证 knowledge cutoff 之后的时效性信息

### AI 工程心智

- [bestpractice_ai_programming_mindset.md](bestpractice_ai_programming_mindset.md) — 70% 问题、成功标准、可验证性
- [bestpractice_ai_debugging_diagnosis.md](bestpractice_ai_debugging_diagnosis.md) — 「代码改不好」的根因诊断决策树
- [bestpractice_multi_agent_analysis.md](bestpractice_multi_agent_analysis.md) — Topic 分割 50% overlap、交叉验证

### Workflow（多 agent）

- [workflow_parallel_subagents.md](workflow_parallel_subagents.md) — 后台 agent + 并行 subagent 调用规则；初次使用前必读
- [workflow_deep_research_survey.md](workflow_deep_research_survey.md) — 多 agent 并行 + 交叉验证的深度调研

## Mirror 维护

所有 baseline skill 都在 [`09_soul/bridging/mirror_manifest.json`](../../09_soul/bridging/mirror_manifest.json) 登记。改 09_soul/skills/\<name\>.md 后跑：

```
python3 09_soul/bridging/mirror_sync.py --check
python3 09_soul/bridging/mirror_sync.py --apply
```

新增 baseline skill 时：
1. 在 09_soul/skills/ 写源文件
2. 在 09_soul/skills/INDEX.md 同步登记
3. `python3 09_soul/bridging/mirror_sync.py --register --source 09_soul/skills/<name>.md --target 09_claude/skills/<name>.md`
4. 在本 INDEX.md 加条目
