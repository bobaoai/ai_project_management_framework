# research_07 — Theme Report Canonical Structure

## Doc metadata

- version: v0.4 (major framing revision after Phase 2 pilot)
- authored_at: 2026-04-22
- prior related docs:
  - `designDoc/research_50_thesis_and_theme_agent_cluster.md` — thesis / theme agent cluster
  - `designDoc/research_40_thesis_note_schema_v1_5.md` — thesis_note schema
  - `designDoc/research_00_report_reviewer_pattern.md` — review pattern
  - `designDoc/research_10_thematic_workflow.md` — thematic workflow
- downstream artifacts defined:
  - `data/research/themes/reports/<theme_id>.md` — canonical theme report output
  - （可选）v1.6 `themes/metadata` schema extension — 承载 §4 / §5 / §6 的部分结构化字段
- v0.1 → v0.2 → v0.3 diff：按 reviewer pass-1 + pass-2 findings revise。10 条 issue closed。语言 convention 去数字编号避免与 §3 冲突。§2.3-§2.6 合并为 theme-specific hybrid modules slot。§1.1 拆 stable/dynamic 两半。补 glossary / asset-class allow-disallow / scenario_triggers SoT 硬约束。
- **v0.3 → v0.4 diff（major framing revision）**：Phase 2 first pilot 暴露 canonical structure 的核心 framing 错了 —— 把 theme report 当 schema template 设计，产出像 operations manual 而不是战略报告。PM push-back："每段话读完之后能让 PM 得到什么"才是写作标准。本版重写：(i) 语言 convention "这里放什么"规则反过来，改为"每段 prose 的 reader-gain articulation"；(ii) §5 canonical outline 每个 section / sub-section 的描述全部按"读完 PM 得到什么 concrete insight"重写；(iii) §3.0 / §4.0 field list 降级为作者 self-check checklist，不是写作骨架；(iv) 明确 theme report 默认是 continuous prose，tables / diagrams 只用在真正 schema 性质的 4 个位置（observable snapshot / state diagram / thesis freshness map / event calendar）。

## Scope

读完本节，你知道这份 doc 要解决什么、不解决什么。

这份 doc 定义 theme report markdown 的写作 canonical standard。它回答三个问题：每个 theme report 读起来应该有什么形状、每 section 读完读者得到什么 concrete insight、什么东西属于 theme report scope 什么东西不属于。

它不定义：任何具体 theme 的 report 内容（内容由 `research-theme-report-owner` 按本 doc 标准写）、任何 portfolio / 调仓 / trade execution 建议（归 operation-portfolio-decision 层）、每日 refresh 的 automation / pipeline 细节（后续 scope）。

## Why canonical structure

读完本节，你理解本 doc 要存在是为了解决什么现实问题。

之前有三个具体问题：federal_rate_cycle 上一轮按 handoff 的"短 summary"写了 placeholder 被 PM 退回；已有 8 个 theme report 结构各异不能横向对照；每个 theme 都重复决定该放什么 section。

一个 canonical standard 能让 owner 拿到模板就知道每 section 该回答什么具体问题、reader 跨 theme 比较时 section 含义对齐、stable / dynamic 分类让 refresh 成本可控。更重要的是，让每段 prose 服务于 reader 的 specific insight 而非 field schema 填空。

## Language convention

读完本节，你拿到 3 条硬规则，之后写 theme report（和 review theme report）时照这三条检查。本 doc 自身 prose 也遵守这三条。

### 一句一事

每句话给一个 fact。不嵌套从句。不用 "path-dependent such that X would cascade"、"asymmetric"、"conditional on" 这种连环套从句。

反例：
> The STIR curve is path-dependent on the joint evolution of factor (a) supply-side look-through doctrine and factor (c) market-anchored inflation expectations, such that any asymmetric move in 1y1y swap could reprice the forced-pause regime into either a hawkish pivot or a cuts-pulled-forward trajectory depending on which leg fails first.

正例：
> STIR 曲线能持续 price forced-pause，依赖两条。第一条是 Fed look-through doctrine 不倒。第二条是 1y1y inflation swap 不跳升。1y1y swap 先跳升，市场会 price 通胀失锚。look-through 先倒，市场会 price Fed 转鹰。两种失败结果不同。

### 背景信息 inline，一次，简短

每个专业名词第一次出现，inline 一句话解释它是什么。后面直接用。解释不超过一个从句，超过就砍。

示例：
- `SFRH7（3-month SOFR March 2027 期货合约，其价格隐含市场对 2027 年 3 月前后短期利率的预期）`
- `OBBBA（One Big Beautiful Bill Act，2025 年 7 月签署的税收法案，核心是恢复 100% 设备折旧）`
- `1y1y inflation swap（一年后起算的 1 年期通胀互换，即市场认为一年后起算的那一年里平均 CPI 会是多少）`

### 每段 prose 的 reader-gain articulation

每段 prose 读完必须能回答"读者得到什么 concrete insight / 判断 / 决策支持"。这是每段（不只是 section 级）的写作标准。

原因：theme report 是战略报告 / 教材质地的 narrative，不是 schema template。PM 读 theme report 不是为了 verify 字段都填全，而是为了在某个 decision 面前获得 concrete reasoning 与 judgment。Section 是 narrative 的地标，每段是 narrative 的原子单元。

反例（schema slot framing —— 段落只罗列"该放什么字段"，读完 reader 不知道得到了什么判断）：

> §2 放：dominant scenario 的成立要素、每条 factor 当前 reading、已观察到的反向证据。

正例（reader-gain framing —— 段落承诺一个 concrete take，之后可以 verify 自己有没有交付）：

> 读完 §2，PM 能独立回答三个问题：当前 dominant path 为什么成立、三条因素哪条最脆弱、已经观察到哪些反向信号。等任何下一个 event 发生，PM 知道要重新验证的是哪一条。

写作层面的具体要求：

- 每段 lead with insight / judgment / decision-relevant takeaway（Pyramid Principle / 顶判断-后支撑 结构）。
- 后续句子支持这个 insight —— 给 mechanism、给 evidence、给 buffer、给 reverse path。
- 段末指向下一段的 implication，保持 narrative flow。
- Tables / diagrams / bullet list 只在"用 prose 表达不清楚"时用。默认 continuous prose。Theme report 只有 4 处推荐用 table —— §6.3 observable live snapshot、§5.1 state diagram、§8.1 thesis freshness map、§10.2 event calendar。其余 section 默认 prose 主导。

## Section 类型 label

读完本节，你拿到 stable / dynamic / hybrid 三个 label 的定义以及什么时候该标什么 label。

- **[stable]**：mechanism / framework / mapping / structure。跨时间基本不变。写一次。mechanism 定义本身变化才 revise。
- **[dynamic]**：readings / events / dates / stances / proximity。每次 report refresh 重写。
- **[hybrid]**：structure 稳定，填充 content 动态。

顶层 `§N` section 默认不直接标 label。其 label 由下属 sub-section 的 label 组合推导：sub-section 全 stable 则该 §N 是 stable；全 dynamic 则 dynamic；混合则 hybrid。当顶层 section 无 sub-section（如 Meta-Header、§0）或所有 sub-section label 一致时，可显式标 label 作为读者快捷提示。

`research-theme-report-owner` refresh 时只动 dynamic 和 hybrid 的 content 部分。stable 部分锁死。

## Glossary

读完本节，你知道 theme report 反复使用的术语定义，owner 第一次 inline 引一句后沿用，不必重复完整定义。

- **regime**：theme 当前所处的宏观 / market state。federal_rate_cycle 的 regime 例子 = forced-pause / hawkish-pivot / cuts-pulled-forward / stagflation / return-to-cutting。
- **dominant path**：当前 evidence weight 最大的一条 scenario。对应 `themes/metadata/*.json` 的 `scenario_map.dominant`。
- **alt path**：当前 evidence weight 低于 dominant 但不可忽略的 scenario。对应 `scenario_map.alternative_paths[]`。
- **scenario_map**：theme metadata 里的字段，列 dominant + alt paths。见 research_05 §4.5。
- **scenario_triggers**：thesis_note 里的 machine-readable trigger 字段（observable_data / threshold / direction / status / observed_at_utc / hit_evidence）。见 research_06 §5.3。
- **scope_boundary**：theme metadata 里的 `{IS, IS_NOT}` 字段，说 theme 管什么、不管什么。见 research_05 §4.5。
- **dwell state / dwell duration**：regime 已持续多久。dwell 原意"停留"。
- **composite regime scorecard**：由多个底层 observable 合成的 0-100 regime 健康打分。每 theme 按 §6.1 自己定义合成公式。
- **anchor thesis**：某条论述背后的 thesis_note。report 的 claim 必须 pointer 到具体 thesis_id。
- **transmission chain**：regime 从 cause 传递到最终资产价格的 layer-by-layer 机制链。
- **live snapshot**：report 生成时刻的数据 reading。与 stable framework 对立。
- **priority_rank**：theme metadata 字段，整数，表示 theme 在当前 theme 池里的排名。1 = 最重要。
- **baseline**：observable 的参考值。可以是某 snapshot date 的 reading，也可以是长期平均。每 observable 单独定义。
- **5y percentile**：observable 当前值在过去 5 年分布中的分位数。50 = 中位，95 = 历史上位。

## Canonical outline

读完本节，你知道每个 theme report 应该覆盖哪 11 个 narrative 区块，以及每个区块 PM 读完应该得到什么 concrete insight。这 11 区块是 narrative scaffold，不是 schema slot。每个区块内部用 continuous prose 展开，除非在明确标记的位置才用 table / diagram。

共 11 个 section：Meta-Header + §0 到 §9 + §10。

---

### Meta-Header [hybrid]

读完 Meta-Header，PM 得到本 report 的时效边界 —— 具体是：report 生成时间戳、各类数据源的最新可得时间（以及哪些已过期需要警惕）、最近一次 regime-moving 事件、下一个计划内的决策节点、一旦发生即 invalidate 整个 report 的 staleness 条件 list、本版相对上版的核心变化摘要。这让 PM 打开 report 第一眼就知道"这份 report 的 evidence 截止到什么时候、什么时候需要找我重看"。

字段 schema 固定，字段值 dynamic：

- `as_of_utc`：report 生成时间戳。
- `data freshness`：每类数据源的最新可得时间（Fed speeches / FOMC minutes / BLS / BEA / market pricing / research feed），超阈值标红。
- `last decisive event before snapshot`：snapshot 之前最近能改变 regime 的事件。
- `next decisive event after snapshot`：snapshot 之后计划内的下一个关键事件。
- `staleness triggers`：触发后 report 整体失效的条件 list。
- `report version + prior version diff`：相对上一版的核心变化摘要。

---

### §0 Executive Framing [dynamic]

读完 §0，PM 得到：一句话当前 regime / phase 判断、60 秒可读的现状（起点、已持续多久、何时结束、最关键驱动力）、未来几天要盯的 3 个 observable 及其阈值与触发影响、对本 report 各区块 evidence 强度的 upfront 预期、一句话 load-bearing take。这让 PM 在不读下文的情况下已经有 actionable mental model。

§0 以 prose 为主。Top-3 observables 可以用简短 table 列示（因为是多维数据点的 anchor）。Confidence posture 用 prose 或简短 bullet list。

---

### §1 The Regime We're In

读完 §1，PM 得到对当前 theme 所处 regime 的精确 location —— 具体是：识别 theme 所有可能 regime 的字典、当前锚定在哪个 regime 以及 confidence level、regime 的 transmission chain layer by layer、chain 每一跳当下 status。这让 PM 在后续 section 读 dominant / alt path 论述时知道"这些论述成立的 regime 前提是什么"。

§1 拆 5 个 sub-section。§1.1a / §1.3 以 prose 为主 articulate mechanism。§1.1b / §1.2 / §1.4 用 prose 为主 articulate 当下证据，可辅以简短 bullet list 锚具体 data point，**不用大 table**。

#### §1.1a Regime 定义库 [stable]

读完 §1.1a，PM 得到本 theme 所有可能 regime 的精确定义库 —— 每个 regime 配"它是什么 / 怎么触发 / 怎么持续 / 怎么终止 / 与相邻 regime 如何区分" 五个维度的 prose articulation。读完 PM 能在不看下文的情况下独立判断任一 market state 是哪个 regime。

以 continuous prose 写，每个 regime 一段到几段，不堆 table / bullet。

#### §1.1b Current regime anchor [dynamic]

读完 §1.1b，PM 得到"当前锚定在哪个 regime、confidence 多高、关键识别条件的当下证据" —— 以 prose 展开而非纯 checklist。如果 checklist table 对读者 navigate 有帮助，可在段末加一个小 table 做 anchor，但段内论述用 prose。

#### §1.2 当前 regime 下的 factor-level 证据 [dynamic]

读完 §1.2，PM 得到"当前 regime 的 cause 侧 / market 侧 / communication 侧证据分别是什么状态、具体数字是什么、距阈值的 buffer 多大" —— 以 prose 展开，数字 inline 或在段末小 table 汇总。不把整 section 做成 snapshot table（那是 §6.3 的位置）。

#### §1.3 Transmission chain [stable]

读完 §1.3，PM 得到本 theme regime 的作用机制 layer-by-layer 展开，每一跳 PM 都能独立 articulate 机制本身与关键 friction。以 prose 为主 articulate，每层一段。

#### §1.4 Transmission chain 当下各跳状态 [dynamic]

读完 §1.4，PM 得到"每层当下 flowing / stressed / broken" —— prose 论述每层当前 status 与依据。如果层数多可用一个小 table 做结尾 anchor，但展开论述用 prose。

---

### §2 Dominant Path

读完 §2，PM 得到"当前 dominant path 为什么成立" 的完整 narrative argument —— 具体是：多因素成立结构、每条 factor 的 current evidence 与 buffer、theme-specific 论证模块（如果有）、已观察到的反向证据。让 PM 相信 dominant path 站得住，同时知道它脆弱的边缘在哪里。

§2 整节以 prose 为主展开 argument。Thesis anchor 引用关系的 single source of truth 在 §8.1，§2 不本地记录 thesis_id，需要引用具体论述时 prose 内 inline 引用 thesis_id。

#### §2.1 多因素结构 [stable]

读完 §2.1，PM 得到 dominant path 成立要几条 factor 同时 hold、每条 factor 的精确定义、factor 间的逻辑关系（AND / weighted / 层级）。以 prose 写，每条 factor 一段。

#### §2.2 每条 factor 当前证据 [dynamic]

读完 §2.2，PM 对 §2.1 每条 factor 得到 current reading、距失效阈值的 buffer、下一决定性数据点。以 prose 展开论述每条 factor，数字 inline。段末可选一个小 summary table 作 anchor。

#### §2.3 Theme-specific hybrid modules [hybrid, 0 或多个 module]

读完 §2.3，PM 得到本 theme 特有的论证模块（每个 module 独立 articulate 一个 mechanism），module 之间不 overlap。

每个 module 的 prose articulation 覆盖：module 名称、mechanism 机制（stable）、current reading 与 status（dynamic）。用 prose 写，不 field-by-field 填空。Module 数量典型 3-5 个，>5 需 consolidate，<2 可直接省略 §2.3 整节。

不适用的 slot 不写。Module 选择由 owner 按 theme 内容决定。

#### §2.4 已观察到的反向证据 [dynamic]

读完 §2.4，PM 得到已经观察到的 counter-evidence 清单，每条标明与哪条 factor 冲突、当前是否 decisive。以 prose 论述每条反向证据，段末可选 summary table。

---

### §3 Alternative Paths — Positive Articulation

读完 §3，PM 对 dominant path 以外的每条 alt path 能独立 articulate "如果这条 path fire 了，mechanism 是什么、我相信它发生的 prior 是什么、fire 后对资产类别的 framing 怎么重构、距 fire 的 buffer 多大、未来几天哪些 event 可能 fire 它、市场当前是否已部分 priced"。这让 PM 在任一 alt path 真的 fire 时能快速切换 mental model，而不是临时重构 narrative。

§3 每条 alt path 用 continuous prose articulate。不用 field-by-field 填空模板。

#### §3.0 Writer self-check checklist [stable]

§3.0 不是 section 写作 template。它是 writer 起草每条 alt path 前的 self-check checklist，确保 prose 覆盖到关键维度。不把 checklist 直接搬进 prose 里做 schema 填空。

每条 alt path prose 至少回答以下 8 个问题：
1. Mechanism —— 如果这条 path fire，具体怎么运作（正向陈述，不是 falsifier 反向）。
2. Cause triggers —— 哪些具体 event 会 fire。
3. Winners —— asset class 级别的 framing。
4. Losers —— asset class 级别的 framing。
5. Current proximity —— 当前距 fire 的 buffer。
6. Catalyst calendar —— 未来 7 / 30 / 90 天内可能 fire 的 event。
7. Market positioning —— 市场当前对这条 path 的 pricing 状态。
8. Anchor thesis status —— 对应 thesis_id / 或"缺，建议 id = X"。

writer 起草后 self-check 这 8 个问题在 prose 里都有 concrete answer。prose 是 continuous argument，不是 form fields。

**winners/losers 的边界**：见 "边界 — asset-class framing allow / disallow 清单"。

#### §3.1 / §3.2 / §3.3 / §3.4 / ... [sub-section label 继承 writer checklist 的 field-level label]

每条 alt path 一个 sub-section。数量等于 `scenario_map.alternative_paths[]` 长度。以 continuous prose 写，覆盖 §3.0 self-check 的 8 个问题。

---

### §4 Cross-Theme Coupling Map

读完 §4，PM 得到本 theme 与每个相邻 theme 的双向耦合画像 —— 每对 coupling 读完 PM 能独立回答 "本 theme 怎么影响邻居、邻居怎么反向影响本 theme、结构性耦合强度、当前是否 active、共享的观察指标是什么"。这让 PM 在处理 cross-theme insight 时知道该去哪家 theme 下读具体 mechanism。

§4 每对 coupling 用 continuous prose articulate，不 field-by-field 填空。Low-coupling 邻居显式写出（"不耦合"也要说清楚 why）。§4 结尾可用一个 summary grid table 做 anchor 全景。

#### §4.0 Writer self-check checklist [stable]

§4.0 是 writer 起草每对 coupling 前的 self-check checklist，不是段落 schema。

每对 coupling prose 至少回答以下 7 个问题：
1. Forward mechanism —— 本 theme 怎么影响邻居。
2. Reverse mechanism —— 邻居怎么反向影响本 theme。
3. 结构性 coupling strength —— high / medium / low。
4. Shared observables —— 跨 theme 共用的关键指标。
5. Current activation state —— active / dormant / stressed。
6. Current shared-observable readings —— observable 当前值。
7. Next coupling shift catalyst —— 下个可能改变 coupling state 的 event。

writer 起草后 self-check prose 覆盖这 7 维度。

#### §4.1 / §4.2 / ...

每对 high / medium coupling 邻居一个 sub-section。Prose 论述。

#### §4.n Low-coupling 邻居 [stable]

读完 §4.n，PM 对每个低耦合邻居得到 "当前为什么 low coupling、在什么 condition 下会 activate"。每个邻居一段 prose。不省略。

#### §4.end Coupling activation grid [dynamic]

§4.end 用一个 summary grid table 做全景 anchor。一行一对 coupling，列 = theme pair / current state / last activation / next shift catalyst。这是 §4 唯一推荐用 table 的地方 —— 之前 §4.1 / §4.2 / §4.n 以 prose 展开，这里汇总成 table 方便 PM 一眼 scan。

---

### §5 Regime State Machine

读完 §5，PM 得到本 theme 的 regime 转移地图 —— 具体是：所有可能 state 的 visual state diagram、每条 transition edge 的精确 trigger 条件、当前 dwell 在哪个 state 多久、每条 transition edge 的当前压力 gauge、当前 probability posture。这让 PM 知道"现在离哪个 transition 最近、下一个决策点在哪"。

§5.1 必须用 mermaid state diagram（这是 §5 推荐用 diagram 的地方）。§5.2 / §5.3 / §5.4 / §5.5 用 prose 为主，data 点 inline 或辅以 small anchor table。

Trigger definition single source of truth 规则：见本 doc 下方"与 scenario_triggers"条目。§5.2 trigger 必须 round-trip 到具体 `thesis_id.scenario_triggers[]`，report 不得新增 trigger。§5.1 所有 node 必须在 §1.1a regime 库有定义 —— 超出 theme scope 的 node（如 "recession" 这种下游宏观状态）须 inline annotate `out-of-scope downstream`。

#### §5.1 State diagram [stable]

读完 §5.1，PM 一眼看清本 theme 所有可能 state 及它们之间的 transition edges。用 mermaid 画。

节点列：当前 regime、上游 regime（若本 theme 有有意义的历史 regime）、下游 regime（所有 alt path 对应的 state）、recovery path（若本 theme 有 fall-back）。渐变型 theme 可省略上游和 recovery path。

#### §5.2 每条 edge 的 trigger precise 定义 [stable]

读完 §5.2，PM 对 state diagram 每条 edge 都知道精确 trigger 条件以及这个 trigger 的 round-trip source（哪个 thesis 的 scenario_triggers 条目）。Prose 或 table 皆可，关键是每条 edge 都有 round-trip pointer。

#### §5.3 Current dwell state [dynamic]

读完 §5.3，PM 得到 "current regime 从什么时候开始、已 dwell 多久、预期还会 dwell 多久"。Prose 一到两段。

#### §5.4 Transition pressure gauge [dynamic]

读完 §5.4，PM 对每条 transition edge 得到当前压力评级（low / medium / high）+ 依据。Prose + 可选小 summary table。

#### §5.5 当前 probability posture [dynamic]

读完 §5.5，PM 得到对所有可能 state 的当前 weight 分布（prose 表述不给假精度百分数）+ 一句话指出哪条 transition 压力最高。纯 prose，无 table。

不写前瞻行动建议。"压力最高"是 observation，不是 "应该提前 position"。

---

### §6 Quantitative Observable Framework

读完 §6，PM 得到本 theme 的完整观察框架 —— 具体是：observable 分 layer 的定义、每层 observable 清单与 series code、当前 live snapshot table、composite regime scorecard 当前输出、未来 30 天决策者 communication 排期与近期发言 digest。这让 PM 在 report 时效边界内知道该盯哪些数、现在 reading 是什么、哪些偏离基线需要警惕。

§6.3 live snapshot 是推荐用 table 的地方（多维数据点的密集 anchor）。其他 sub-section 以 prose 为主。

Trigger definition single source of truth 规则同 §5 —— §6.2 observable + threshold 必须 round-trip 到对应 `thesis_id.scenario_triggers[]`。

#### §6.1 Observable layer 定义 [stable]

读完 §6.1，PM 对本 theme 的 observable 如何分 layer 有清晰 mental model。每 theme 按需选择 layer 划分，推荐从以下三个 prototype 起手：

- **Prototype 1 — "pricing + composite + mechanism + communication"**（适合 macro / rate / FX / commodity theme）。Layer 1 primary pricing；Layer 2 composite regime scorecard；Layer 3 mechanism observables；Layer 4 decision-maker communication pulse。
- **Prototype 2 — "physical + contract + sentiment"**（适合 supply-chain / commodity-physical theme）。Layer 1 physical；Layer 2 contract；Layer 3 sentiment / positioning。
- **Prototype 3 — "signal + event + positioning"**（适合 geopolitical / event-driven theme）。Layer 1 event signal；Layer 2 event proxy；Layer 3 positioning。

以 prose 为主 articulate 每层的定义与作用。

#### §6.2 每层 observable 清单 + series code [stable]

读完 §6.2，PM 对每 observable 得到 series code、baseline 定义、阈值、refresh cadence、automation hook。这里 observable 密集，推荐用 table 组织（每层一个 table）。

#### §6.3 Live snapshot table [dynamic]

读完 §6.3，PM 一眼看到所有 observable 的 as-of-now reading、与 baseline 的 Δ、关联到哪条 scenario。这是 §6 最核心的 live component，用一个完整 table 展示。

列分三 tier：
- **Mandatory v1**：name / series / current / scenario link。
- **Recommended v1**：baseline / Δ。
- **Optional v1.1（需 5y daily history pipeline 才能填）**：5y percentile。

percentile 列不强制，若未搭 history pipeline 可整列省略或标 `[optional, requires 5y daily history]`。

Placeholder 规范：暂无 live data 的行用 `[TBD: source=<FRED/CME/BLS/...>, series=<series code>, needed_by=<date>]` 明示来源与时间，不用粗糙的 `[TBD live pull]`。

#### §6.4 Composite regime scorecard 当前值 [dynamic]

读完 §6.4，PM 得到 composite score 的当前输出值、所处分段、一句话解释。Prose 一段。

#### §6.5 决策者 communication pulse [dynamic]

读完 §6.5，PM 得到未来 30 天 Fed / 相关决策者 speech calendar + 最近 14 天发言 digest。可 prose 为主 + 小 table 列发言 entry。

---

### §7 Open Research Agenda

读完 §7，PM 得到未解决的 research 问题清单（每条标 priority / owner / next decisive data point / horizon）以及 upstream dependency 跟踪（哪些外部事件如发生会 re-rate 整个 theme）。这让 PM 知道下一轮 research 该优先补什么、哪些事件他要自己盯而不等 owner 提醒。

以 prose + table 混合。

#### §7.1 Agenda priority matrix [hybrid：column schema stable, rows dynamic]

一个 priority matrix table 做全景。列 schema：# / question / priority / owner / next decisive data point / horizon。每次 refresh：rows 动态更新，列 schema 不动。

#### §7.2 Upstream dependency tracking [dynamic]

Prose list 哪些外部事件如果发生会触发整个 theme report re-rate。

---

### §8 Evidence Base

读完 §8，PM 得到本 report 所有论证的 anchor 溯源地图 —— 具体是：每条 linked thesis 的 freshness status 与 anchor 位置、linked research 源的 timestamp 与 relevance、gap register（哪里缺 thesis-level backing）。这让 PM 在质疑任一论述时知道该去哪个 thesis / source 复核。

§8 是 thesis anchor 关系的 single source of truth。§2 / §3 / §4 / §5 不重复记录 thesis_id，需引用时 prose inline 引 thesis_id，但结构化 anchor 关系只在这里。

#### §8.1 Linked thesis freshness map [dynamic]

一个完整 thesis freshness table。列 = thesis_id / schema version / last updated / age / 在哪些 section 做 anchor / freshness status（✅ fresh / ⚠️ stale / ❌ broken）。这是 §8 核心 component，用 table 展示。

"在哪些 section 做 anchor" 列是 §2 / §3 / §4 thesis anchor 的唯一结构化记录。一个 cell pointer >5 个时按 §N 分组竖排增强可读性。

#### §8.2 Linked research freshness [dynamic]

区分 current event sources / decision-maker communication sources / 底层数据源。Prose + 小 table 混合。

#### §8.3 Gap register [dynamic]

哪些 factor / transition / coupling / layer 当前没有 thesis-level backing。Prose list 或 table，每条标是否建议补 + 建议 thesis id。

---

### §9 Scope Boundary & Cross-Reference

读完 §9，PM 得到本 theme 的管辖边界 —— IS / IS_NOT、相邻 theme priority 对照、当前 boundary pressure（哪条 thesis 跨两个 theme 归属不清）。让 PM 在判断某个 insight 该去哪家 theme 下读时能快速定位，也知道当前哪些 boundary 需要 reconcile。

#### §9.1 IS / IS_NOT [stable]

完整 IS / IS_NOT prose，从 metadata `scope_boundary` 同步。以 prose 展开，不是 bullet list。

#### §9.2 Neighbor theme priority 对照 [dynamic]

一个小 table 列相邻 theme 当前 priority_rank 和 coupling strength。priority_rank 由 `build_theme_indexes` 从 `themes/metadata/*.json.priority_rank` 自动同步，owner 不手填。

#### §9.3 当前 boundary pressure [dynamic]

Prose list 哪些 boundary 当前最接近"模糊"。每条一段 prose 说清楚具体争议。

---

### §10 Near-Term Event Calendar

读完 §10，PM 得到未来 90 天里所有 decisive event 的时间轴 —— 具体是：horizon 分层（7 / 14 / 30 / 90 天）、每层具体 event 清单与预期对 regime 的 impact。让 PM 开会、度假、决策时知道哪天不能错过、哪个 event 对哪条 path 是 decisive。

不包含任何 pre-position recommendation / trade action / 具体仓位动作。

#### §10.1 Calendar structure [stable]

Prose 一段说明 horizon 分层定义（7d / 14d / 30d / 90d）与每层收纳什么类型 event。14d horizon 典型 3-5 个 event，否则易退化成 7d 的镜像。

#### §10.2 当前 7 / 14 / 30 / 90 天 calendar [dynamic]

每层用一个 table 列具体 event。列 = 日期 / event 名称 / expected 对 regime 的 impact。

---

## Section 类型 roll-up 表

读完本表，你对每 section 的 refresh 成本与触发条件有 quick reference。

| Section | Stable 占比 | Dynamic 占比 | Refresh cost | Refresh trigger |
|---|---|---|---|---|
| Meta-Header | 10% schema | 90% values | 低 | 每次 refresh |
| §0 Executive | 0% | 100% | 低 | 每次 refresh |
| §1 Regime | 50% (1.1a, 1.3) | 50% (1.1b, 1.2, 1.4) | 中 | regime 定义变或当前证据变 |
| §2 Dominant | 30% (2.1, 2.3 module 定义) | 70% (2.2, 2.3 readings, 2.4) | 中-高（取决于 §2.3 module 数） | factor reading 变 |
| §3 Alt Paths | 50% (模板 self-check + mechanism + winners/losers) | 50% (proximity + calendar + positioning + anchor status) | 很高 | proximity 变 / 新 thesis 补齐时 |
| §4 Coupling | 55% (mechanism + strength + observables) | 45% (activation + reading + catalyst) | 中 | activation state 变 |
| §5 State Machine | 40% (diagram + triggers) | 60% (dwell + pressure + posture) | 中 | pressure 变 / transition fire |
| §6 Observable Framework | 40% (layer 定义 + series code) | 60% (snapshot + scorecard + pulse) | 高 | 每次 refresh |
| §7 Research Agenda | 20% (column schema) | 80% (rows + dependency) | 中 | open question 状态变 |
| §8 Evidence Base | 0% | 100% | 中 | linked thesis 或 source 变 |
| §9 Scope Boundary | 60% (IS/IS_NOT) | 40% (priority + boundary pressure) | 低 | metadata scope 变 |
| §10 Event Calendar | 10% (structure) | 90% (具体 event) | 高 | 每次 refresh |

## 边界 — asset-class framing allow / disallow 清单

读完本节，你拿到 §3 winners/losers 的 asset class 判定标尺，灰色 case 查这里。

### Allow（属于 theme report scope）

- "long-duration USTs 会涨"（asset class framing）
- "AI capex basket 受益"（basket 名称，不到具体 ticker）
- "rate cut fire 时 2s10s curve 会 steepen"（曲线结构判断）
- "gold outperforms equity in stagflation path"（asset class 对比）
- "short-end dominates long-end if hawkish pivot fires"（期限结构判断）
- "commodity curve backwardation 加深"（结构判断）

### Disallow（归 operation-portfolio-decision 层，不写在 theme report）

- "买 TLT"（具体 ticker）
- "long SFRH7 paired with short ES，sizing 5% of NAV"（具体合约 + sizing）
- "在 96.40 入场，stop 96.20"（entry / stop）
- "reduce AI capex exposure by 30%"（具体仓位动作 + 幅度）
- "PM 当前 long XLF，建议 rebalance 到 XLU"（对比 PM 当前 portfolio）
- "VIX put spread strike 15-18，maturity 30 days"（具体 option 结构）

### 灰色 → 默认 disallow

不确定时默认 disallow。owner 把它写到对应 operation-portfolio-decision 层 artifact，不写在 theme report。

## 与其他 artifact / skill 的关系

读完本节，你知道 theme report 与 metadata / thesis_notes / scenario_triggers / operation-portfolio-decision 层各自的责任分工，避免 overlap 与重复记录。

### 与 `themes/metadata/<id>.json`

Metadata 是 structured summary。Report 是完整论证 + 当前 snapshot。

Metadata 里的 `scope_boundary` / `scenario_map` / `theme_tags` / `linked_thesis_ids` / `linked_asset_tickers` 是 report 的子集，machine-readable 形式。Report §9.1 IS/IS_NOT 从 metadata `scope_boundary` 同步。Report §3 / §5 structure 基于 metadata `scenario_map` 展开。Report §8.1 thesis list 基于 metadata `linked_thesis_ids`。

单向依赖：metadata 变 → report 需 refresh。Report 变（仅 dynamic 部分）不一定动 metadata。

### 与 linked thesis_notes

Thesis 是 anchor。Report 是 synthesis。

每个 thesis 负责一个具体 cause→effect 单跳论证。Report 把多个 thesis 串起来 articulate 跨 thesis narrative。

Anchor 关系 single source of truth 在 report §8.1。§2 / §3 / §4 本地不重复记录 thesis_id，只 prose inline 引用。§8.3 gap register 显式列没有 thesis anchor 的地方 —— 是 report 下一轮 research priority。

### 与 scenario_triggers

`scenario_triggers`（thesis 层字段，见 research_06 §5.3）是 machine-readable trigger 的 single source of truth。

Report 内部有 4 个地方碰 trigger 数据：§3 alt path cause triggers + proximity + catalyst、§5.2 每条 edge 的 trigger、§5.4 transition pressure gauge、§6.2 observable + threshold + §6.3 snapshot。

**硬约束**：
- Report 不得新增 trigger。§5.2 / §6.2 所有 trigger 条目必须 round-trip 到某条 `thesis_id.scenario_triggers[]`。
- Report refresh 时如发现需要新 trigger，先回到 thesis 层补写（走 research-thesis-adversary 流程），再在 report 引用。
- `research-theme-report-reviewer` L0 check 列入 trigger round-trip 验证。
- 推荐在 §5.2 / §6.2 的 table 加一列 "round-trip source: `<thesis_id>.scenario_triggers[<idx>]`" 让 reviewer 能 verify。

### 与 operation-portfolio-decision 层

严格边界：theme report 止于 §3 scenario-level asset-class framing（见 allow / disallow 清单）。

Portfolio-decision 层的独立 artifact（具体 ticker / sizing / entry / exit / stop / PM 当前 portfolio gap / 调仓动作）consume theme report 作为 input，叠加 PM portfolio state 产出具体动作。不写在 theme report 里。

## 开放问题

读完本节，你知道本 doc sign-off 之后 first pilot / 后续 round 里要拍板的真实分歧点，不凑数。

### Stable section 的 revise 频率

stable section 什么情况 revise？至少三种触发：regime 定义本身变化（新 paradigm，例如 look-through doctrine 被 Fed 正式 deprecate）；`scenario_map` 新增 / 删除 alt path；`scope_boundary` 调整（与邻居 theme 分工改变）。

每次 revise 需要 bump report 的 "stable version" counter，与 dynamic refresh 分开管理。**待定**：stable version counter 具体实现（report frontmatter / meta-header 字段 / git tag）。first pilot 后拍板。

### Refresh cadence 是否进 skill spec

三级 refresh cadence 提议：每周 refresh §6 observable snapshot / §0 top-3 / Meta-Header；每 major event refresh §2.2 / §3 proximity / §5 pressure；每 FOMC / 关键数据发布 refresh 全 dynamic 部分。

**待定**：这三级是否写进 `research-theme-report-owner` SKILL spec 作为硬性 refresh obligation，还是留给 theme 各自的 owner 按需。first pilot 后拍板。

### v1.6 metadata schema 扩展

以下结构化字段是否进 v1.6 `themes/metadata` schema 作为 first-class field：`cross_theme_coupling_map`（承载 §4 forward / reverse / strength / shared observables）；`regime_state_machine`（承载 §5.1 mermaid + edge trigger schema）；`observable_framework`（承载 §6.1 + §6.2 layer 定义 + series code 清单）。

优点：machine-readable，可以 cross-theme query。成本：schema 复杂度上升，write-side 规则要扩展。

**待定**：federal_rate_cycle first pilot 写完后评估。Pilot 过程中如果多次需要在 markdown 里重复 metadata 数据（破坏 single source of truth），优先推 v1.6。

### Report skeleton generator

是否写一个 subroutine，把 stable section 从 metadata + linked thesis 自动生成，只留 dynamic 部分让 owner 填？

优点：降低 owner 重复工作量，stable section 永远与 metadata 一致。成本：generator 是新 code，维护成本。

**待定**：first pilot 之后。先手工 seed 沉淀几份经验再自动化。

### Live data pull subroutine 优先级

Phase 2 first pilot 暴露了一个未预期的 blocker：没有 live data pull subroutine 的话，§6.3 snapshot table / §6.5 Fed pulse / §9.2 priority 对照 / §1.2 / §2.2 / §3.X proximity 大量字段只能 `[TBD]`。

**待定**：live data pull subroutine 是否应升为 Phase 3 前置 blocker（先搭再做其他 theme report），还是允许 "partial pilot with honest TBD"。first pilot 之后拍板。

## Upgrade plan

读完本节，你知道本 doc 从 approved 到其他 7 theme 全部 refresh 的 3 阶段路径与每阶段退出条件。

三阶段。每阶段有 exit branch。

### Phase 1 — 模板 sign-off（本 doc）

PM review 本 doc → reviewer 走一遍 → PM sign-off。

Done 条件：本 doc 进 `designDoc/research_07_*`，status marked `approved`。

### Phase 2 — federal_rate_cycle first pilot

按本 doc 模板重写 `data/research/themes/reports/federal_rate_cycle.md`。同时补 §8.3 gap register 里标 "must" 的 thesis（至少 §3.3 stagflation positive thesis）。

Done 条件：PM review pilot report → 符合模板 → confirm 模板本身不需再改 → pilot report 进 canonical 位置。

**Exit branch**：pilot 过程中发现模板结构需要改，回退 Phase 1 revise 本 doc，再进 Phase 2。v0.4 本版就是 Phase 2 触发 exit branch 后的 revise 结果。

### Phase 3 — 其他 7 theme refresh

按模板 refresh 现有 8 个 theme reports 中的其他 7 个。

Done 条件：每个 theme report 符合 canonical structure + reviewer 走一遍 + PM sign-off。

**Review gate**：每个 theme 单独走 reviewer，不批量 rubber-stamp。每 theme review 时间预算 ~30 分钟。

**Exit branch**：如果多数 theme refresh 时发现模板需要改（例如某类 theme 的 §5 state machine 根本不适用），回退 Phase 1 revise。

## Reviewer self-check list

读完本节，你作为 reviewer / owner 提交 sign-off 前拿到一份 verification checklist。

- [ ] 所有 sub-section 都标 [stable] / [dynamic] / [hybrid] label。顶层 `§N` 不标（由 sub-section 推导），除非 §N 无 sub-section 或 sub-section label 全一致。
- [ ] 每段 prose 都能回答"读完 reader 得到什么 concrete insight"。不是 schema slot 填空。
- [ ] Section 顶层描述用 "读完 §N，PM 得到 X、Y、Z" 句式，不是 "§N 放：..." 或 "§N 做 X" 句式。
- [ ] Tables / diagrams 只出现在 4 个推荐位置（§6.3 snapshot / §5.1 state diagram / §8.1 thesis freshness map / §10.2 event calendar）以及 §6.2 series code / §4.end coupling grid / §9.2 neighbor priority 这些本质 schema 性质的小 table。其他地方默认 continuous prose。
- [ ] 语言 convention 三条（一句一事 / 背景 inline / 每段 reader gain）在整份 report 自身 prose 中遵守。
- [ ] Portfolio-decision 层所有内容（具体 trade action / sizing / portfolio gap / ticker）100% 排除，对灰色 case 查 allow-disallow 清单。
- [ ] 与 research_05 / research_06 引用 link 正确。
- [ ] 与 metadata / thesis / scenario_triggers 边界说清楚，"report 不得新增 trigger" 硬约束 round-trip source 在 §5.2 / §6.2 标出。
- [ ] §5.1 所有 state node 在 §1.1a regime 库有定义。超出 theme scope 的 node 须 inline annotate `out-of-scope downstream`。
- [ ] §6.3 `[TBD]` 占位符遵守 `[TBD: source=X, series=Y, needed_by=Z]` 规范，不用粗糙 `[TBD live pull]`。
- [ ] §9.2 priority_rank 列由 `build_theme_indexes` 自动同步，owner 不手填。
- [ ] Open questions 不虚设，每条都是 first pilot 之后真实决策点。
- [ ] Glossary 术语覆盖 doc 反复使用的词。
