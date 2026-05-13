# Forks MVP 与 trading_platform 的关系

Source: `04_areas/work/due_diligent/forks/Forks-MVP-Product-Spec.pdf`（V1.0, 2026-04, 27 页）

本文目的：先说清 Forks MVP 在产品意义上是什么，再把它每一段映射回当前 trading_platform 的现有抽象（artifact graph、theme report、thesis_note、current_priority_tree、技术报告、PM 报告等），最后给出可借鉴点和应避免的边界。

读完这份文档，读者应能区分：

- Forks 的核心 IP 和真正的差异化层在哪里
- trading_platform 的哪些既有对象天然就是 Forks 概念的同义词
- Forks 有而我们没做的对象（Scenario tree、Trigger state machine、Vindication card、Convergence、Living feed、KOL 病毒层）
- 如果未来要把两者打通，哪些是免费 leverage、哪些会污染当前 PM-facing 的设计语言

---

## 1. Forks 是什么（一句话还原）

Forks 把"投资观点"从一段长文压缩成一个**结构化的多分支 scenario tree**，让用户公开发布并获得分享，同时让后台 agent 持续替用户监测 trigger、起草新子分支、并发现与他人 scenarios 的交集。

它的两个产品灵魂决定了 Forks 不是一个"AI 投研助手"：

1. **Scenario 是 expression，不是 AI 输出**。AI 帮用户扩张 option space，最终 scenario 的取舍是用户的视角（用户的 ego 投入 = 自豪分享 = 自然流量）。
2. **Living scenario evolution 是 retention 核心**。Trigger 命中、AI Draft 子分支、跨用户 convergence 三类事件持续推送到用户首页 living feed；trigger 命中时自动出 vindication card，这是 organic re-share 的引擎。

它显式 not-是：

- 不是 chatbot（Claude/ChatGPT 给的是 wall of text）
- 不是 PMS（不跟 Composer / Atom / Alphalens 竞争）
- 不是 stock picker（不替用户做 buy/sell）
- 不是 Substack（结构化多分支，不是无结构长文）

定位陈述：Forks 是 **v5.4 Thematic Research Loop Infrastructure 的 90 天 MVP 入口产品**，专门覆盖 v5.4 的 `Scenarios → Monitor → Evolve` 这三段；`Theme / Thesis-agent 三动作 / Basket / PIT 数据栈` 推到 9-24 个月之后再上。

---

## 2. 用一张表把 Forks 的核心对象映射到 trading_platform


| Forks 对象 / 概念                       | trading_platform 现存对应                                                                                             | 对应关系         |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------ |
| `Thesis`（一句话观点 + your view）         | `data/research/thesis_notes/<id>.json`（`title` + `claim_bullets` + `key_dependencies` + `disconfirming_evidence`） | **强同义**      |
| `Scenario`（branch，含 narrative）      | `themes/reports/<theme_id>.md` 内部的"情景/路径"段；ThesisNote 的 `scenario_triggers`                                       | **概念同源、形态弱** |
| `trigger_signals[]` + state machine | `thesis_note.scenario_triggers`（自由文本，无 status 状态机）                                                                | **概念有，机制无**  |
| `key_tickers[]` long/short          | `thesis_note.linked_asset_tickers` / `expected_winners` / `expected_losers`                                       | **强同义**      |
| `parent_scenario_id`（树形子分支）         | 没有；当前 ThesisNote 是单层 flat 对象                                                                                      | **缺失**       |
| `Forward-Cast agent`（候选 5-7 条）      | 没有专门 agent；`single-stock-analysis` 与 `research-theme-knowledge-and-package-curator` 在做相邻工作                                            | **部分**       |
| `Monitor agent`（trigger 监测）         | 没有 trigger-aware monitor；`research-current-market-reporter` 在做近因 narrative，不是 per-scenario trigger evaluator               | **缺失**       |
| `Evolve agent`（AI Draft 子分支）        | `research-theme-report-owner / research-theme-knowledge-and-package-curator` 在维护 theme report 的"新发展"，但不是子分支起草                                  | **形态不同**     |
| `Convergence detector`（embedding）   | 没有                                                                                                                | **缺失**       |
| `Vindication card`（trigger 命中后）     | 没有；artifact graph 有 `must_exist_unchanged_since` 这种内审契约，但不会输出"我两个月前预测对了"卡片                                        | **缺失**       |
| `Living feed`（用户主页）                 | `current_priority_tree.json` + `themes/reports/*` 的人工浏览路径，没有事件流主页                                                 | **形态不同**     |
| `Scenario card 1080×1080`（社交）       | 没有；我们所有输出都是 PM-facing 报告（reader-state-first，不是 social card）                                                       | **缺失（且故意）**  |
| `MonitorEvent`（事件流对象）               | 没有专门的 event stream；artifact graph 里有 sidecar/freshness 状态但不是面向用户的事件                                               | **缺失**       |
| Tier / 付费 / K 因子 / KOL seeding      | 完全无对应，trading_platform 是单 PM operating system                                                                     | **N/A**      |


观察：

- **Thesis 抽象高度重叠**。Forks 的 `Thesis = title + your_view`，我们的 `thesis_note = title + claim_bullets + key_dependencies + disconfirming_evidence`。我们的 schema 还更厚一些（已经隐含 your_view 拆得更细）。
- **Scenario 抽象同源但形态不同**。我们目前把"路径/情景"嵌在 `themes/reports/*.md` 里作为段落，没有把 Scenario 拆成可独立 CRUD 的一等公民对象。Forks 把 Scenario 提到一等公民，并加了 `parent_scenario_id` 形成 tree。
- **Trigger 状态机我们没有**。`scenario_triggers` 现在是自由文本数组（"Agentic trading APIs gain developer adoption"），既不带 `observable_data + threshold + direction`，也不带 `pending / triggered / reverse_triggered / obsolete` 状态。这恰好是 Forks 让 Living feed 能跑起来的最小机制。
- **Living/事件流 vs 报告**。trading_platform 最终交付物是 PM-facing 报告（`current-market.md`、theme report、single-stock note、portfolio decision），是"读后 PM 能判断什么"。Forks 最终交付物是事件流（feed）和可分享卡片，是"用户被反复召回 + 自然分享"。两者本质不同。

---

## 3. 关键差异（不要一上来就想合并）


| 维度             | trading_platform                                             | Forks                                                    |
| -------------- | ------------------------------------------------------------ | -------------------------------------------------------- |
| 目标用户           | 单 PM（Bowen 本人）；内部 operating system                           | fintwit / aspiring buyside / semi-pro / 学生；公开产品          |
| 输出形态           | PM-facing markdown 报告 + sidecar + freshness 状态               | Scenario tree + 1080×1080 social card + vindication card |
| 阅读契约           | reader-state-first；删除编辑性元话语                                  | "一眼 get 到" social card；watermark + 病毒回流                  |
| Loop 终点        | 帮 PM 形成下一轮判断 / 调仓决定                                          | 帮用户拿到 social proof + 让 retention 闭环跑起来                   |
| 数据深度           | 强：artifact graph、freshness contract、writer sidecar           | 浅：Postgres + S3 + Redis + Claude API；trigger 60-70% 覆盖   |
| 自动化重心          | deterministic builder + AI gap-filling，强可审计                  | LLM-heavy、Claude prompt + cron monitor                   |
| Backtest / PIT | 不做                                                           | 不做（一致）                                                   |
| 商业层            | 无                                                            | Free / Pro $12 / Team $49；K1+K2 病毒系数                     |
| 边界硬规则          | `42_artifact_graph_admission` / `35_pm_reader_state_first` 等 | "MVP 必须覆盖完整 loop 的差异化环节"（v5.4 §10.1）                     |


注意：trading_platform 的 `35_pm_reader_state_first.mdc` 和 `32_pm_report_prose_no_editorial_meta.mdc` 是为给一个具体 PM 写报告服务的；Forks 的 social card 的写作语言（"我两个月前说"、"今天发生了"）与之**故意**不同。这两套话术不应互相借鉴 prose 风格，否则两边都会被破坏。

---

## 4. 假设 Forks 是 Bowen 的下一个产品，trading_platform 在其中扮演什么

如果 Forks 真的进入 90 天 build，trading_platform 与 Forks 之间最自然的角色分工是：

- **trading_platform = Bowen 自己的 high-fidelity research workshop**
  - 出 high-conviction theses
  - 在 theme report、single-stock note、portfolio decision 里做最深一层的判断
  - 拥有 deterministic 数据、freshness contract、writer sidecar 这些机构级审计资产
- **Forks = Bowen 的对外发布层 + 社区/付费产品**
  - 把 trading_platform 内部产出里"适合公开"的那部分 thesis + scenarios 拍平成一棵 Scenario tree
  - 由 Forks 的 Forward-Cast / Monitor / Evolve / Convergence 四个 agent 去跑公开侧的 retention loop
  - vindication card 给 Bowen 自己也提供了一个"track record 自动归档"的副作用，这对 Citrini network 的冷启动 seeding 是正向

这意味着两个产品**不需要、也不应该**直接共享运行时：

- 不要把 trading_platform 的 `data/research/` 直接挂到 Forks 后端
- 不要让 Forks 的 social card prose 风格回流污染 PM-facing 报告
- 但可以共享 **schema 直觉**（Thesis / Scenario / Trigger 的字段命名和语义），这是"免费的设计 leverage"

---

## 5. 双向可借鉴的点

### 5.1 trading_platform 可以从 Forks 借鉴的（按性价比排序）

1. **Trigger state machine**
  把 `thesis_note.scenario_triggers` 从自由文本升级成结构化对象：
   `{ observable_data, threshold, direction, status: pending|triggered|reverse_triggered|obsolete, observed_at_utc, hit_evidence }`。
   这件事对我们自己也有用——artifact graph 已经能追踪"数据新鲜度"，但还不能追踪"thesis 的某个 trigger 是否已经命中"。补上之后，PM 报告里"还在等什么 / 已经发生了什么 / 已经被反向证伪"的判断会更可机审、不全靠人脑。
  - 注意符合 `13_index_first_ai_for_gaps.mdc`：trigger status 是结构化字段，不要做成 AI 重新猜的中间层。
2. **Scenario 作为一等公民对象**
  现在 ThesisNote 内部隐含多个 scenario，但没有独立 CRUD。考虑在 `data/research/thesis_notes/` 旁加一层 `scenarios/<id>.json`，包含 `parent_thesis_id` + `parent_scenario_id`，让 theme report / single-stock note 都可以**引用**而不是**重写**这些 scenario。
  - 这件事和 artifact graph 是一致的——多一类节点、有 canonical_path、有 freshness 契约。
3. **Trigger 命中后的"事后回顾"自动化**（Vindication 的 internal 版本）
  不需要 social card。需要的是：当某个 thesis_note 的 trigger 命中或被反向证伪，自动在 `data/research/thesis_notes/<id>.history.md` 追加一行"哪个 trigger / 在什么时候 / 用什么证据"。这是 trading_platform 自己的 lessons-learned 自动化，跟 Forks 的 vindication card 同源、不同形态。
4. **Convergence/divergence 检测**
  embedding similarity 找跨 thesis_note 的交集，在 trading_platform 这边的价值是"提醒 PM 自己有没有同一观点写在两个 thesis_note 里、互相 contradict"，不是社区互动。这件事可以晚一点做。

### 5.2 Forks 可以从 trading_platform 借鉴的

1. **Writer sidecar / freshness contract** 的最小子集
  每张 vindication card / scenario card 渲染时把"基于哪几个 trigger event id、哪几个数据源"写进 sidecar；用户和 KOL 之后翻旧帖时不会失真。这是 trading_platform 的 `<canonical_path>.writer.json` 在 social 层的最简版本。
2. `**reader-state-first`** 的语言
  即便 Forks 的输出是 social card，"读完这张卡片用户被允许相信什么 / 不能相信什么"也是核心。trading_platform 已经把这件事抽象成可执行的 rule，可以直接借用做 card design 评审清单。
3. `**source_collection` / 标签优先于关键字**
  trading_platform 的 `13_index_first_ai_for_gaps` 经验适用于 Forks 的 Monitor agent：先消费已有 tag/registry，AI 只补语义空白。Forks 早期容易把 Monitor 直接做成"Claude 7×24 全部跑一遍"，成本和噪音都会失控。

---

## 6. 不应该跨过去的边界

- **不要让 Forks 的 K-factor / 病毒层概念进入 trading_platform 的设计语言**。trading_platform 没有"分享"这一终点，引入这层会把 PM-facing 报告的 reader 错位。
- **不要把 trading_platform 的 artifact graph 强加到 Forks MVP**。Forks v0 的 schema 应保持轻；artifact graph 是 trading_platform 长出来的产物，不是先验工程要求。Forks 可在 9-24 月演化到 v5.4 canonical 时再考虑。
- **不要把 Forks 的 Scenario tree 倒推回我们的 theme report**。我们的 theme report 是 PM-facing 的"现在该怎么读这个 theme"，不是给读者一棵可点开的 flowchart。Scenario tree 应当作为 ThesisNote 的旁路结构存在，不替代 theme report 的叙事。
- **不要拿 Forks v5.4 §10.1 的"MVP 必须覆盖完整 loop"硬规则来约束 trading_platform**。trading_platform 不是 MVP，是已经运行的内部系统，loop 完整性的判定标准不同。

---

## 7. 我现在能给的判断

- Forks 在产品上是清晰、定位收敛的 MVP，灵魂 1 / 灵魂 2 是真有差异化的洞察，特别是"Scenario 是 expression，不是 AI 输出"这条——它直接决定了产品不会滑进又一个 AI chatbot。
- Forks 与 trading_platform 不是竞品，也不是简单上下游，更像是**同一组研究 schema 直觉的两种产品形态**：一个对内做 high-fidelity PM workshop，一个对外做 fintwit-级 social/retention loop。
- 最有价值的交叉点不是把两个 codebase 合并，而是让 ThesisNote / Scenario / Trigger 三个核心 schema 在两边保持**字段级语义一致**，这样未来 Bowen 在 trading_platform 里写好的某个 thesis 可以低成本"剥一层壳"作为 Forks 上的种子 scenario，反向 vindication 数据也能回流成 trading_platform 的 lessons-learned。
- 短期对 trading_platform 自己最值钱的借鉴是 **Trigger state machine** 和 **Scenario 提为一等公民对象**这两件事；其余的（vindication card、convergence、living feed、social card、KOL seeding、tier 定价）都属于 Forks 那一侧的产品资产，trading_platform 不需要现在去复刻。

---

## 附录：Forks MVP 90 天里程碑速览（仅供对照，不作我们排期）


| 周次        | 关键交付                                                                                                  |
| --------- | ----------------------------------------------------------------------------------------------------- |
| Week 1-2  | Next.js + Postgres + Claude + auth + Stripe + visual design system                                    |
| Week 3-4  | Forward-cast agent v0；Thesis + Scenario schema 可写                                                     |
| Week 5-6  | Scenario editor（flowchart）、节点状态编码、子分支手动添加                                                             |
| Week 7-8  | Scenario card renderer（PNG 1080×1080 + 1080×1920）、Twitter 分享、profile                                  |
| Week 9-10 | Monitor agent v0、earnings + SEC ingestion、半自动 trigger 检测                                              |
| Week 11   | Vindication card 自动生成、AI Draft agent、Living feed 主页                                                   |
| Week 12   | Convergence detector、Team tier、QA、KOL seed outreach                                                   |
| Week 13   | Private launch（20-30 KOL + 50 个高质量 seed scenarios）                                                    |
| 关键风险      | (1) scenario 生成质量；(2) trigger 自动覆盖率 60-70%；(3) flowchart UX 学习曲线；(4) disclaimer 与视觉冲突；(5) KOL seed 失败 |
| 验证指标      | K1 > 0.3；signup 转化 > 3%；30 天 retention > 25%；Free→Pro > 3%；K2 > 1.5 × K1                              |


