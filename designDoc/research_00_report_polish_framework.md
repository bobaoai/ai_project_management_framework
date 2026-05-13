# Report Polish Framework: ReviewEdit Two-Mode Protocol

For the family-level position of this doc, see
[`research_00_overview.md`](research_00_overview.md).

Related:
- [`research_00_report_reviewer_pattern.md`](research_00_report_reviewer_pattern.md) — agent-level verdict loop (accept / revise / rewrite)
- [`research_11_theme_report_canonical_structure.md`](research_11_theme_report_canonical_structure.md) — structure contract for the report being polished

## Why This Doc Exists

L4 PM-facing 报告写完之后，除了 reviewer agent 的 verdict gate，还存在一段**人工 + LLM 协作的 draft polish 阶段**。这一阶段的典型场景：

- DS / Claude 首轮产出在结构和证据层达标，但 surface compliance、译文腔、内部逻辑 bug 需要逐段清理
- 外部 reviewer（鸭哥这类）交回的 draft 风格与我方 LANGUAGE_CONVENTION 不完全对齐
- reviewer agent 给出 `accept_with_revisions` verdict 后，作者按 must-fix 清单逐项改

这些场景都有同一个失败模式：人工复盘和单段修改混在一起做，作者/PM 同时在扮演「审查员」和「copyedit 助手」两个角色，review 标准、改法、compliance 检查互相干扰。

本文档定义 **ReviewEdit Two-Mode Protocol**，把 review 和 edit 拆成两个显式状态，用一套固定协议在两者之间切换。reviewer pattern 管「要不要合并这份 draft」的 yes/no 决定；本 framework 管「决定要改之后、具体怎么改」的交互协议。

## Scope

**用于**：
- 任何已有 draft 的定稿前 polish（theme report、market observation、single-stock note 等 L4 报告）
- 改写任务（rewrite pass，如 DS 基于 Claude draft 做中文化）
- reviewer agent `accept_with_revisions` 后的 must-fix 循环
- 人 + LLM 交互式 copyedit（作者口述改法、LLM 执行）

**不用于**：
- 初稿生成（writer layer 的职责）
- reviewer agent 的 verdict 决策（那是 [`research_00_report_reviewer_pattern.md`](research_00_report_reviewer_pattern.md) 的职责）
- 一次性小修（单个 typo、单句替换不需要 protocol）

## Two-Mode Protocol

两个显式状态，用户批准是唯一的 transition 信号：

```
┌─────────────┐   user "可以"    ┌─────────────┐
│  REVIEW     │ ────────────────▶│   EDIT      │
│             │                  │             │
│ 诊断不动文件  │ ◀────────────── │ 只改一段    │
│             │    自动回返      │             │
└─────────────┘                  └─────────────┘
```

**关键不变量**：
- 两态边界必须显式（每轮输出头部标明 `REVIEW 模式` 或 `EDIT 模式`）
- Edit 只改一个 atomic unit（见下文），改完自动回 Review
- 用户的 `可以 / 批准 / next` 是唯一的 Review → Edit 触发信号
- 拒绝或补充要求后退回 Review，不得抢跑进 Edit

## Review Mode

### 扫描维度：Reader-Impact Taxonomy（五类）

以 **「读者读完这一段会被害到什么」** 作为分类轴，而不是按规则来源分类。五个独立失败模式，按严重度递减排列：

| 优先级 | 类别 | 读者症状 | 典型表现 |
|---|---|---|---|
| 1（最严重）| **误解** | 读完得出错误结论 | 事实错、逻辑错、forward reference、scope 越界、evidence tier 被错误升级（conditional → confirmed）|
| 2 | **困惑** | 读完不知道作者想说什么 | 术语未定义、代号未解释、前后不一致、多套编号冲突、层级不清 |
| 3 | **错位** | 读完位置感不对 | 对称展开该不对称的列表、schema-fill 该 prose 的论述、单信号收尾不够具体、asymmetric emphasis 缺失 |
| 4 | **阻塞** | 读得慢、读得累 | 译文腔、破折号、长句连环从句、中英 hybrid、主宾倒置 |
| 5（最轻）| **噪声** | 读完记不住主线 | meta-commentary、restate 重复、workflow-speak attribution、hedging 堆砌 |

五类互斥、穷举。同一处问题可以命中多类（例如一处 forward reference 既是「误解」又是「困惑」），标**优先级更高**（数字更小）的那一类。严重度递减的内在逻辑：**影响判断 > 影响认知 > 影响结构感 > 影响阅读速度 > 影响纯净度**。

### Review 输出格式

按五类分 bucket，每条 issue 包含：

- **位置定位**：优先用 `章节标题 + grep 关键词 + 原文片段`；避免绝对 line 号（多轮 edit 后会漂移）
- **类别 tag**：`误解` / `困惑` / `错位` / `阻塞` / `噪声`
- **严重度色标**（optional 视觉辅助）：🔴 = `误解` / 🟡 = `困惑`+`错位` / 🟠 = `阻塞`+`噪声`。色标是严重度轴、类别 tag 是失败模式轴，两轴正交。可以 "🔴 误解 + forward reference"
- **规则来源**（optional）：如果对应具体 rule 文档（COMMUNICATION、LANGUAGE_CONVENTION、CRITIQUE 某项），注出
- **修改方向**（可留开）：一句话提 fix 思路

Review 末尾给出 **priority ordering**，按 cascade 依赖排序：upstream 定义先修，downstream 引用自动解决。例如 factor (a)(b)(c) 在开头定义好，后面 10 处 forward reference 自动 resolve。

**Line cite drift 约定**：每次 Review 开始时重新 grep 定位，不信任上一轮的 line 号。多轮 Edit 会使绝对行号持续漂移，以 `章节 H2 标题 + grep 关键词` 定位最稳。

### Review 不做的事

- 不动文件
- 不预判作者采纳哪些修改（列出、不 rank 是否必改）
- 不混入 edit suggestion 的细节（那是 edit mode 的事）

## Edit Mode

### Atomic Unit = 一个 H2 Section

一次 Edit 只改一个 H2 section 或一组紧耦合段落。理由：
- 一个 H2 对作者来说是一个完整语义单元，脑子里能保持一致改写意图
- 作者在 30 秒内能审完一次改动
- 改完即返回 review mode，避免多段耦合产生 review 死锁

**禁止**：
- 一次改多个 H2 section
- 一次只改一行（用 edit mode 杀鸡用牛刀，直接 suggestion + 作者自改即可）

### Edit 前的 announce

Edit 动手前，先输出：

```
# EDIT 模式 — 第 N 段
改「章节 H2 标题」节（line A-B，以当前 state grep 为准）。
- 🔴 误解: fix 1
- 🟡 困惑/错位: fix 2
- 🟠 阻塞/噪声: fix 3
顺手修: ...
```

作者看到后可以在 edit 落下前喊停。

**Edit 前的 Read 纪律**：如果要替换的 `old_string` 超过 3 行或含全角/半角混合标点（`:`/`：`、`""`/`""`、`—`/`-`），**先 Read 精确匹配一次**，不凭记忆构造 old_string。LLM Edit 对全半角字符不做 normalization，`:` 和 `：` 是 literal 不等价，容易导致 Edit tool 返回 `String to replace not found`。一次 Read + 一次 Edit 比两次 Edit 失败更省时间。

### Edit 后的 present

改完必须按顺序给出四件事：

0. **Grep 先行（硬要求）**：announce 任何 Before/After 或合规数字之前，先跑一遍该段的 grep 硬指标（`——` / `—` / `不是.+而是` / `而非` / workflow-speak 黑名单 / 中英 hybrid 抽象名词）。发现自引入违规就**立即回到 Edit 态补修**，修完再 announce。不允许"announce 完才 grep 发现问题"这种顺序——那等于把未经验证的合规结论交给用户。
1. **Before/After 表**：每条改动一行，旧 → 新，对应到 review 里的哪一条 issue
2. **合规 check**：grep 后的硬指标 count（全部 0）
3. **下段候选**：预告下一段的 review 主要 fix 点

Before/After 表的作用是**让 over-correction 立刻可见**。典型 over-correction：DS 为「中文流畅」把 Fed 原话英文也翻译了——这种规则冲突在表格里一摆就暴露。

Grep 先行的作用是**让自引入的违规立刻可见**。Edit 过程中 LLM 自己可能打出新的 `——` / `而非` / 中英 hybrid 结构（实战中已发生过多次），不 grep 验证就 announce 等于把错误结论交给用户。这一条是 v0.3 新增的硬要求。

### 保留纪律（non-negotiable）

Edit 时以下维度零损失：

- **数字锚点**：所有价位、阈值、日期、identifier（SFRH7 / DFII10 / specific levels）
- **结构骨架**：H2 章节数、顺序、推荐的 13 条 PM-memo writing moves 显式覆盖
- **Evidence 密度**：每段 load-bearing 判断 + 支撑证据全保留
- **Mermaid / table / code block**：内部 label 可改，结构不动

**能动的只有**：措辞顺序、句式结构、术语中英选择、段首 insight 呈现。把 polish 与 rewrite 严格分开。

### Cross-section Consistency Check

改一个 section 时，顺带 check 它引用的 upstream 定义和被 downstream 引用的位置是否一致。例如改第 3 段的 hawkish pivot 触发条件 (a)+(c)，必须同时核对第 5 段的 chain-dependent 例子、第 7 段 state machine 的 mermaid label 是否对齐。

这一 check 用 grep，不用肉眼扫。

**Canonical-source rule**：任何术语 / 编号 / regime 定义的 canonical 源 = 文件中**第一次完整列出**的位置（通常是开头的「核心判断」或「读者画像」节）。后续章节都是引用，不得重复定义或偷偷改义。改 canonical 定义时必须 grep 所有引用处并同步。反之改下游引用时，先确认它和 canonical 源一致，不一致的话回去改 canonical 源或改引用，不能两边都改形成新的冲突。

同一术语的两套编号（例如 regime 内部的 (a)(b)(c) vs thesis A3-i 内部的 sub-factor a/b）是 anti-pattern，应在 review 阶段标为 🔴 `困惑`，强制合并到单套或显式区分命名。

## Why It Works

这个 protocol 对以下 anti-pattern 有效：

1. **Review / Edit 混做** → 两态显式分离，作者只做一件事
2. **Over-correction 悄悄发生** → Before/After 表让冲突规则显性化
3. **Edit 改动过大 / 改到无关段落** → H2 atomic unit + 用户 gate 限制 scope
4. **Forward reference / cross-section inconsistency** → cascade-aware priority + grep check
5. **规则爆炸（10+ 条 rule anchor）** → Reader-impact 五类收敛扫描维度，减少遗漏
6. **过度细致（pattern-matching 每条 COMM 规则）** → 五类是读者视角，不是 doc anchor 视角，粒度适配

## When Not To Use

- 单文件 < 3 段的小 draft：走 inline suggestion 即可，不用 protocol
- 结构性 rewrite（改骨架 / 合并章节 / 重排段落）：那是 owner 级决定，先回 `*-report-owner` 调整 `owner_decision`，不是 polish 阶段的事
- 作者对 draft 的主线判断有异议：退回 `*-report-owner` 层重新 pass，不做 polish
- 已在 reviewer agent 的 `needs_rewrite` verdict 下：需要走 writer 重出，polish 救不了

## 与 Reviewer Pattern 的协作

两个 framework 串起来的完整 lifecycle：

```
writer 出 draft
   ↓
reviewer agent 给 verdict
   ↓
   ├── accept_as_is → merge
   ├── accept_with_revisions → ReviewEdit Polish Loop（本文档） → merge
   └── needs_rewrite → 回 writer 或 owner
```

Polish loop 的输入是 reviewer 的 must-fix 清单（如果有）+ 人工复读发现的 surface issue。输出是定稿可 merge 的 draft。

## Concrete Example

一次完整 polish loop 的实例：

- **输入**：`ds_rewrite_v2_from_claude.md`（DS reasoner 基于 Claude Opus 4.7 xhigh v2 的 rewrite pass，197 行 / 28KB）
- **Review 1**：sweep 出 3 处 🔴 结构性 bug（两套 a/b/c 编号冲突、A3-i/A3-ii 未定义、line 27/45 逻辑错 a+b→ 应为 a+c）+ 2 处 🟡 合规违规（`——`、`而非`）+ 若干 🟠 译文腔
- **Priority**：upstream 先修（line 5 当前判断节定义 (a)(b)(c)），downstream 10+ 处 forward reference 自动 resolve
- **Edit 1**：改 line 3-9「当前判断 + 置信度声明」。Before/After 7 行，compliance 0/0/0
- **Edit 2-5**：依次改 Regime 识别 / 联合排序 / 传导链 / Dominant Path 资产映射
- **Review 2**：五类重扫，确认残留问题

整个过程在两态之间切换，每次 Edit 是 atomic，每次 Review 用五类扫描收敛。

## Status

- **Version 0.3 — 2026-04-23**
- 首次落地：`federal_rate_cycle` theme report polish（DS rewrite v2 → final，[复盘](../share/federal_rate_cycle_external_review/04_ds_rewrite/polish_loop_retrospective.md)）
- v0.3 变更：
  - `Edit 后的 present` 增加 0 号硬要求：announce 前必须 grep 先行，自引入违规立即回 Edit 态修
- v0.2 变更：
  - 五类严重度排序显式化（误解 > 困惑 > 错位 > 阻塞 > 噪声）
  - 色标 × 类别 的两轴正交关系写清
  - Line cite drift 纪律：用 `章节标题 + grep 关键词` 替代绝对 line 号
  - Edit 前 Read 纪律：长 old_string 或含全半角混合标点必须先 Read
  - Canonical-source rule：术语定义权威位 = 第一次完整列出的位置
- 待沉淀：
  - 后续 report family（market observation / single-stock / portfolio decision）的 reader-impact 五类是否需要针对性扩展
  - 自动化：`compliance check` 这步能不能在 lint 层跑（grep `——` / 否定反结构 / workflow-speak 黑名单）
  - reviewer agent 的 `accept_with_revisions` 输出 format 是否直接对齐本 framework 的 review 输出
  - Edit tool 是否在 wrapper 层加一层字符 normalization，让 `:`/`：` 等全半角等价匹配（非必需、tool 层改动）

## Debater 未来演进 Roadmap

Debater v0.1 的 skill 定义见 `.cursor/skills/research-theme-report-debater/SKILL.md`。其核心是 D1-D7（七个逻辑维度）× L1-L6（六个 persona 透镜）两轴正交的 attack log。

**v0.1（now）—— 单 Debater 内嵌 6 透镜 checklist**
- 单一 attacker 角色，内部依次跑 L1 macro / L2 technical / L3 fundamental / L4 flow / L5 catalyst / L6 scenario 六个 lens 的静态 checklist
- 所有 attack 带 `dimension` + `lens` 双标签，末尾附透镜覆盖矩阵
- 优先起草 L1 / L2 / L3 三份 checklist，L4-L6 后补

**v0.2（条件触发）—— 拆成 6 个独立 per-lens agent**

触发条件（任一满足）：
1. 单 lens checklist 超 50 行，prompt attention 被稀释
2. 某 lens 需接外部 data source（L2 读真实 chart、L4 读 13F / positioning），不能再 fully static
3. 多 lens 之间出现系统性冲突，需要显式 cross-lens debate（v0.1 单 agent 内部难以承载）

拆分后结构：Dispatcher + L1-L6 六个 attacker + Aggregator。attacker 仍只 attack draft，不 produce opinion（和 writer persona 的 bull/bear 独立观点区分开）。

**外部参考**：`tradermonty/claude-trading-skills` 把 writer 按 persona 切成 7 个独立 skill（见 `learning_library/repo_notes/public_trading_skills_landscape.md`）。我们在 attacker 侧做同构切分，但保留攻击者的职责边界。

**先决条件**（拆分前必须达成）：
- v0.1 单 Debater 已跑过至少 3 份完整 theme report
- Attack log 累积能回答"哪个 lens 最常产出 block 级 issue"
- 6 份 checklist 稳定到可作为独立 agent 硬 spec
