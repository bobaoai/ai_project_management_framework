# Report Reviewer Pattern

For the family-level position of this doc, see
[`research_00_overview.md`](research_00_overview.md).

## Why This Doc Exists

L4 PM-facing 报告（theme report、market observation、single-stock note、portfolio decision）目前在写完之后没有一个独立、结构化的 review 步骤。`writer-handoff` 是 **写之前** 的 package readiness gate，不是写之后的 draft 复核。

实际工作中我们已经看到几类持续出现的失败：

- DS 文里把单日价格行为升级成 regime 切换，但 package 并没有这种证据
- DS 文 silently 改了主线（mainline drift），与 `theme.owner_decision` 描述的 pass 类型不一致
- DS 文把跨资产 mismatch 平掉，因此 PM 看到的判断比 evidence 实际允许的更强
- 时间口径错配：`session_as_of` / `report_date` / 研究证据窗口 没在 DS 文里区分清楚
- 需要外部事实校验的关键 leg（政策原文、事件时间、官方价格）被 DS 当成已知

我们需要给每一类 L4 报告配一个 reviewer，它的核心职责是：

- 在 DS 文写完之后、合并回 standing report 之前
- 用 package + owner_decision 复核 draft
- 在 hard-trigger 命中时用 Perplexity 做窄口径外部事实补强
- 输出一份带 severity 的 review note + 二元化 verdict
- 不重写主稿，不改主线，不抢 owner 权限

本文档先定下 **reviewer 通用原则**，再把第一份具体实现 —— `research-theme-report-reviewer` —— 写完整。后续 `current-market`、`single-stock`、`portfolio decision` 的 reviewer 沿用同样形状，但有各自的 truth surface 和 verdict 维度。

## Reviewer 通用原则

任何 L4 reviewer 都必须遵守这些边界：

- reviewer 不写主稿，只输出 review note + verdict
- reviewer 不改主线，所有结论必须基于 draft 当前主线，不允许「我觉得另一条主线更好所以改了」
- reviewer 不抢 owner 权限，发现 package 有问题应回到 `*-report-owner` 重新决定 pass
- reviewer 输出必须是「可决断」结构，不是 narrative 评论
- reviewer 使用外部事实（如 Perplexity）时必须分 `confirmed / not confirmed / contradicted`，外部事实不能成为 verdict 的最终依据

每个 reviewer 都强制三层 pipeline：

1. `Self-audit against package`：draft 与 package + owner_decision 的逐项对照
2. `External verification (narrow)`：仅在 hard trigger 命中时调用 Perplexity，按 leg 拆 query
3. `Adversarial review`：mismatch、cherry-pick、over-attribution、silent mainline drift 四问

每个 reviewer 都返回三档 verdict 之一：

- `accept_as_is`
- `accept_with_revisions`（必须列 must-fix）
- `needs_rewrite`（必须说清是 package 问题还是写法问题）

## Theme Report Reviewer (first concrete instance)

### 在 Artifact Graph 中的位置

当前链路：

```
theme.knowledge (L2)
  -> theme.owner_decision (L3, research-theme-report-owner)
  -> theme.package (L3, research-theme-knowledge-and-package-curator report mode)
  -> theme.report.ds (L4, writer gateway)
  -> [merge back into theme.knowledge]
```

加入 reviewer 后：

```
theme.report.ds (L4)
  -> theme.report.review (L4, research-theme-report-reviewer)   <-- 新节点
  -> [accept => merge back into theme.knowledge]
  -> [revise => 回 research-theme-knowledge-and-package-curator]
  -> [rewrite => 回 research-theme-report-owner]
```

### 新增 Artifact Graph 节点（提案）

待 `data/runtime/artifact_graph.yaml` 落地时按这个 shape 添加：

- `id`: `theme.report.review`
- `layer`: `L4`
- `canonical_path`: `data/research/theme_update_drafts/<theme_id>.review.md`
- `sidecar`: `data/research/theme_update_drafts/<theme_id>.review.json`（结构化 verdict）
- `report_date_scoped`: `true`
- `builder.kind`: `ai_writer`
- `builder.command`: `research-theme-report-reviewer`
- `owner_skill`: `research-theme-report-reviewer`
- `depends_on`:
  - `theme.report.ds` (must_be_fresh, theme_id: same)
  - `theme.package` (must_be_fresh, theme_id: same)
  - `theme.owner_decision` (must_be_fresh, theme_id: same)
- 下游 merge edge：`theme.knowledge` 在 `verdict in {accept_as_is, accept_with_revisions(已应用)}` 时才允许 overwrite。

### Primary Truth Surface

reviewer 第一阶段必须完整读完这四个：

- `data/research/theme_update_drafts/<theme_id>.ds.md`（被复核的 DS 文）
- `data/research/theme_update_drafts/<theme_id>.package.md`（package）
- `data/research/theme_update_drafts/<theme_id>.owner.json`（owner_decision，决定 pass 类型）
- 当前 standing report：`data/research/themes/reports/<theme_id>.md`（用于判断 mainline drift）

按需读：

- 同主题最近的 review note（如果存在）
- 相关 thesis：`data/research/thesis_notes/*.json`
- asset-centered 主题（`gold`/`oil`/`usd`/`rates`/`btc`）应顺手读一份 `asset_technical_report` 做技术状态对照
- 跨主题 sweep：仅在 owner_decision 显示有 overlap 嫌疑时才进行

### 三层 Pipeline 详细

#### Layer 1 — Self-audit Against Package

逐项核对：

- **Mainline alignment**：DS 文最终在讲的故事 vs `owner_decision.scope` 描述的故事是否一致。允许语言上的 polish，但主线、关键转折、关键 trigger 不能被静悄悄替换。
- **Evidence alignment**：DS 文里每个有数字 / 时间 / 政策措辞的 claim 是否能在 package 中找到锚点。允许 polish，但不允许引入 package 没有的事实。
- **Confirmed vs not-confirmed 分隔**：DS 文是否把 package 中标记 `not_confirmed` 的 item 当成 confirmed 来用。
- **Time discipline**：研究证据窗口、市场原始 UTC、`session_as_of`、`report_date`、`generated_at` 是否被混成「最新」一个含糊概念。
- **Block coverage**：current judgment / background / 市场在定价什么 / drivers 与传导 / confirmed anchors / not-confirmed / 关键 debate / scenario path / portfolio fit / risks 与 monitoring 是否齐全；缺哪一块要明说。

#### Layer 2 — External Verification（按需）

**Hard triggers（命中其一即必须调用 Perplexity）**：

- DS 文出现具体价格 / 收益率 / 央行决议 / 官方 statement timing 且 package 没有原始锚点
- DS 文叙事时间窗内有重大公开事件（rate decision、OPEC 公报、监管发布、地缘事件），但 package 明显早于该事件
- DS 文做了「事件 X 在 Y 时间发生」类断言，但 package 中没有 dated 锚点
- DS 文与 standing report 主线明显冲突，需要外部时间线确认是哪边正确

**不应该触发**：

- 纯 thesis / mechanism 表达
- 长期叙事
- package 中已有 confirmed anchor 的事实
- 仅是文体或 polish 改动

**调用规则**：

- 一个 leg 一次 query，不做大杂烩 prompt
- 显式 date window
- 默认 `--preset fast-search`，机制类升级 `--preset pro-search`
- 输出按 `confirmed / not confirmed / contradicted` 三栏归档
- 永远不让 Perplexity 决定 verdict；它只是 evidence

#### Layer 3 — Adversarial Review

强制四问：

1. **Mismatch handling**：DS 文是否抹平了 cross-asset mismatch、技术与叙事 mismatch、或 thesis 内部 mismatch
2. **Cherry-pick**：DS 文是否只用支持论点的资产 / 时间窗，回避了反向资产
3. **Over-attribution**：DS 文是否把单日价格升级为 regime 切换、把单一事件升级为结构性 trigger
4. **Silent mainline drift**：DS 文最终的 mainline 与 `owner_decision.scope` + standing report 是否一致；若不一致，必须以 `needs_rewrite` 提交回 owner

### Verdict Shape

每次 review 输出固定三个二元化对齐 + 一个 status：

- `mainline_alignment`: `ok` | `weak` | `fail`
- `evidence_alignment`: `ok` | `partial` | `fail`
- `mismatch_handling`: `ok` | `weak` | `fail`
- `status`: `accept_as_is` | `accept_with_revisions` | `needs_rewrite`

判定规则：

- 任一对齐 = `fail` ⇒ status 至少 `needs_rewrite`
- 任一对齐 = `weak` 且其他不为 `fail` ⇒ status 至多 `accept_with_revisions`
- 三项都 `ok` 且无 critical finding ⇒ `accept_as_is`

severity 分级：

- `critical`：影响 PM 决策正确性（mainline drift、把 not_confirmed 当 confirmed、规模性数字错误）
- `major`：影响判断稳健性（mismatch 抹平、over-attribution、缺关键 debate）
- `minor`：措辞、结构、章节顺序、editorial 语言泄漏

### Output Template

主输出 `data/research/theme_update_drafts/<theme_id>.review.md`：

```
---
theme_id: <theme_id>
report_date: <D>
draft_path: data/research/theme_update_drafts/<theme_id>.ds.md
package_path: data/research/theme_update_drafts/<theme_id>.package.md
owner_decision_path: data/research/theme_update_drafts/<theme_id>.owner.json
reviewer: research-theme-report-reviewer
generated_at: <UTC>
---

## Verdict
- status: accept_with_revisions
- mainline_alignment: ok
- evidence_alignment: partial
- mismatch_handling: weak
- external_verification_used: yes (n legs)

## Critical Findings
- [C1] ...

## Major Findings
- [M1] ...

## Minor Findings
- [m1] ...

## External Verification (Perplexity)
- query 1: "<narrow query>"
- date_window: <range>
- result: confirmed / not_confirmed / contradicted
- impact: ...

## Required Revisions
- ...

## Notes For Owner
- ...
```

并写一份结构化 sidecar `<theme_id>.review.json`：

```
{
  "theme_id": "...",
  "report_date": "...",
  "verdict": {
    "status": "accept_with_revisions",
    "mainline_alignment": "ok",
    "evidence_alignment": "partial",
    "mismatch_handling": "weak"
  },
  "findings": {
    "critical": [...],
    "major": [...],
    "minor": [...]
  },
  "external_verification": [
    {
      "query": "...",
      "date_window": "...",
      "preset": "fast-search",
      "result": "confirmed",
      "impact": "..."
    }
  ],
  "required_revisions": [...]
}
```

### Routing 回流

- `accept_as_is` ⇒ `research-theme-knowledge-and-package-curator` 执行 merge：覆盖 `themes/reports/<theme_id>.md`，更新 metadata，删除 `theme_update_drafts/<theme_id>.package.md`，重建 indexes
- `accept_with_revisions` ⇒ 回 `research-theme-knowledge-and-package-curator`（report mode），按 `Required Revisions` 修改 DS 文 → 再走一次 reviewer
- `needs_rewrite` ⇒ 回 `research-theme-report-owner`，重新决定 `pass_type / scope / writer_direction`，必要时回到 `research-theme-knowledge-and-package-curator` knowledge mode 先补结构

`writer-handoff` 不动。`writer-handoff` 仍然是写之前的 package readiness gate；`research-theme-report-reviewer` 是写之后的 draft 复核 gate。两个 gate 不重复。

### Failure Signals（reviewer 自身失败的迹象）

- reviewer 自己重写了 DS 文，而不是返回 verdict
- reviewer 静悄悄改了主线
- Perplexity 输出被当作 verdict 结论
- mismatch 在 review note 里被「圆」掉
- review note 用 PM 主稿语气写市场分析
- review note 出现 `这次 package`、`这版`、`本次更新` 等 editorial 语言
- review note 缺三项对齐 + status，只写 narrative 评论
- review 没记录 sidecar，下游无法机器化判断 verdict

## 后续 Reviewer（占位）

后续在同一形状下增加：

- `current-market.report.review`：复核 `current-market.ds.md`，重点 cross-asset mismatch、session_as_of 一致性、intraday vs close 标签
- `single_stock.report.review`：复核 `single_stock.ds.md`，重点 ticker-first 主线、技术状态 vs 叙事一致性、theme overlay 是否合理
- `portfolio_decision.review`：复核 portfolio decision，重点 policy limits、状态一致性、reduce/add/hold 对应 evidence

每一类沿用：三层 pipeline + 三档 verdict + 二元化对齐 + severity 分级 + sidecar JSON。差异只在 truth surface 与对齐维度。

## Follow-up 集成清单

实施时需要顺带做的事：

- 在 `data/runtime/artifact_graph.yaml` 增加 `theme.report.review` 节点
- 在 `research-theme-report-owner` SKILL.md 的 `Downstream Routing Contract` 中加入：DS 写完后默认走 `research-theme-report-reviewer`，根据 verdict 决定回流
- 在 `research-theme-knowledge-and-package-curator` SKILL.md 的 `report mode` 完成标准里加入：merge 前必须存在对应 `<theme_id>.review.md` 且 verdict ∈ {`accept_as_is`, `accept_with_revisions`(已应用)}
- 在 `.cursor/skills/research-theme-report-reviewer/SKILL.md` 落实本文档对应的 reviewer skill
- 在 `designDoc/learning_library/repo_notes/public_trading_skills_landscape.md` 末尾追加一节，标注本 reviewer 借鉴了 `scenario-analyzer` / `skill-reviewer` / `academic-paper-reviewer` / `doublecheck.agent.md` / `perplexity-web-research` 的哪些设计

参考外部样本：

- [tradermonty/claude-trading-skills - scenario-analyzer](https://github.com/tradermonty/claude-trading-skills/blob/main/skills/scenario-analyzer/SKILL.md)（dual-agent: analyst + reviewer）
- [anthropics/claude-plugins-official - skill-reviewer](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/plugin-dev/agents/skill-reviewer.md)（severity 分级 + 三档 verdict）
- [Imbad0202/academic-research-skills - academic-paper-reviewer](https://github.com/Imbad0202/academic-research-skills/blob/main/academic-paper-reviewer/SKILL.md)（多视角非重叠 lens）
- [github/awesome-copilot - doublecheck.agent.md](https://github.com/github/awesome-copilot/blob/main/agents/doublecheck.agent.md)（self-audit + source verification + adversarial review 三层）
- [xpepper/perplexity-agent-skill](https://github.com/xpepper/perplexity-agent-skill)（Perplexity 仅作 second opinion，不替代主推理）
