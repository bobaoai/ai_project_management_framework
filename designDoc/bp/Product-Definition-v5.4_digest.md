# V5.4 Product Definition · 结构化阅读笔记

来源：[`designDoc/bp/Product-Definition-v5.4_1.pdf`](Product-Definition-v5.4_1.pdf)（69 页，2026-04，"面向主题投资的 AI 原生研究基础设施 · v5.4 Canonical"）。

本笔记目的：把 V5.4 全文的**设计思路**（不是商业叙事）高密度结构化成 AI 可直接消费的索引；与已有的 [`forks_mvp_relation_to_trading_platform.md`](forks_mvp_relation_to_trading_platform.md) 配合使用——后者专注 V5.4 §10（Forks MVP 入口）与 trading_platform 的概念映射，本笔记覆盖完整 V5.4 §1–§13。

写作风格遵循 `.cursor/rules/30_ai_facing_docs_detail_first.mdc`：详略均衡、不为了人类 skim 牺牲设计契约的细节。

---

## 0. 元信息

### 0.1 版本演化链

| 版本 | 状态 |
|---|---|
| v5.0 – v5.2 | 早期 canonical（4 primitive + 5 workflow 并列结构）。已被 v5.3-concept loop 重构替代 |
| v5.3（旧版） | "Overshoot 版"，把 Thesis 抬成 loop 唯一主角 + 引入 thesis library 比喻。已明确否决，作对照档归档 |
| v5.3-concept | "Rebalance 版"（1275 行 markdown）。Loop 结构 + Thesis 独立段 + Scenario 降为 Thesis 分叉 + Monitor 分两腿 |
| **v5.4 canonical** | 本文档前身。融合 v5.3-concept 主体 + v5.4 delta spec 两大决策 |

### 0.2 v5.4 相对 v5.3-concept 的 delta

新增 4 处：
1. §5.4 Scenario Probability 三阶段路径（MVP qualitative + Phase 1 market-implied + Phase 2 historical）
2. §4.6 Theme/Thesis 交叉状态矩阵 + 4 条 invariant
3. §4.7 状态转移级联规则（双向）
4. §10 Forks MVP 入口章节（90 天 MVP，独立 Spec 文档）

锁定原 v5.3-concept 未决 2 处：
- **Thesis invalidated 可复活**（§4.6.5）：允许 invalidated → evolving → active(vN+1)，lineage 完整保留
- **Theme peaking/decaying 阈值归 PM 手标**（§4.6.4）：MVP 不做自动状态转移

Schema 修订 1 处：
- Scenario object：删除单一 `probability` 字段 → 改为 `pm_personal_score` + `market_implied_probability` 两个显式字段（§4.5）

### 0.3 一句话产品定位

V5.4 是一套 **thematic research loop infrastructure**——把"定位主题 → 形成论点 → 构建篮子 → 监控 → 推演 scenarios → 反哺论点"这条循环研究链路整条搬上 agent 辅助平台，**服务机构团队**。

### 0.4 客户买的是什么（差异化三句话）

1. Loop 被 agent 串起来后每段都提速 + 留痕——PM 不再在 Slack/PDF/Excel 之间手工搬运状态
2. Thesis 段的"辅导"本身就是核心价值——agent 在 PM 写 Thesis 时反问、给 rewrite 候选、把模糊陈述切成可证伪子陈述
3. Monitor → Scenarios → Evolve 闭环别人做不了——市面上有独立的 factor backtest、独立的 narrative velocity dashboard、独立的 scenario planner，但没人把"Monitor 异常 → 衍生 scenarios → basket 调整 → 反馈回 thesis 下一版"做成原生闭环

### 0.5 显式不做（首页清单）

- 不做 thesis library
- 不做研究内容发布平台（不与 Substack / Seeking Alpha 竞争；tenant 默认无公开发布路径）
- 不做订单执行 / 交易（产品到 basket + adjustment recommendation 为止）
- 不做完整投管系统（不与 Aladdin / Charles River 竞争）
- 不做通用 quant backtest 框架（backtest 是 monitor + validation 的辅助工具，不是对外产品；V4 教训）
- 不做散户产品（MiroFish 决策档已否决）
- 不做通用 LLM 对话窗口
- 不做自动市场预测（不输出系统级自动 probability）

---

## 1. Loop 五段心智模型（§3）

### 1.1 闭环骨架

```
Theme ──► Thesis ──► Basket ──► Monitor ──► Scenarios & Evolve
  ▲                                              │
  └──────── (反馈回流到下一版 Thesis) ◄──────────┘
```

每段固定 4 个槽位：
- **业务目的**（为什么需要这一段）
- **PM 要完成的判断**
- **Agent 动作清单**（动词级，不是抽象能力）
- **生命周期状态**（state machine）

### 1.2 段落速查

| 段 | 业务目的（一句话） | 产出 object | Agent 编排形态 |
|---|---|---|---|
| §3.1 Theme | 把模糊直觉收敛成有边界、有 universe 的 Theme | Theme | 后台常驻 + on-demand |
| §3.2 Thesis | 把 Theme 里的一条直觉打磨成可证伪 directional bet | Thesis | 会话式，与 PM 交替 |
| §3.3 Basket | 把 Thesis 落成可交易 basket（标的+权重+约束） | Basket | on-demand，长任务 |
| §3.4 Monitor | 对 live basket 做 7×24 持续追踪（quant + qualitative） | Monitor Event | 后台常驻 7×24 |
| §3.5 Scenarios & Evolve | 主动衍生未来路径 + 把 monitor 反馈吸收回 Thesis 下一版 | Scenario / Thesis vN+1 | on-demand + 事件触发 |

---

## 2. Loop 五段详解（§3.1–3.5）

### 2.1 §3.1 Theme 段

**业务目的**：PM 在浮出水面的趋势上正式立项——把"制造业回流美国"、"reasoning 模型压缩 SaaS 利润"这种模糊直觉收敛成明确边界 + 可投资 universe。

**PM 要完成的判断**：
- 业务边界（hyperscaler vs IaaS/PaaS/SaaS 全部？美国 onshore vs 全球回流？）
- 时间窗（12/24/36 月）
- universe 初始候选（100–500 只量级，不是精选 20 只——那是 Basket 段的事）
- "为什么现在"+"为什么不是已经 priced in"

**Agent 6 个动作**：
1. 扫 universe 按共现关系聚类提候选 Theme（每日跑 embedding + clustering）
2. 对 PM 提出的 Theme 做反证清单检查（与过去 10 年相似 Theme 重合？跑赢/跑输 SPY？）
3. 推候选 universe（factor + 行业分类 + 文本相似度三路召回 + 主题纯度预打分）
4. 拒绝模糊 Theme（"AI 会改变一切"→ 给 3 种切分方案）
5. 与 tenant 内现有 Theme 做重叠检查（避免两个 PM 各自立项 datacenter 耗电）
6. （可选）与 extended network 历史 Theme 做匿名相似度检查（tenant admin opt-in）

**Theme 状态机**：`draft → active → monitoring → peaking → decaying → archived`

### 2.2 §3.2 Thesis 段

> **本段是 loop 里 agent 辅助价值最密集的一段，但它不是唯一主角**。

**Thesis ≠ Theme**：
- Theme 是命名层（"AI 基础设施"）
- Thesis 是具体断言（"在 hyperscaler capex 2025–2026 同比 30%+ 前提下，第二梯队的电力 + 散热 + 光模块供应商在 12–18 个月跑赢 SPX 15%+"）

**为什么 agent 重要**：PM 的 Thesis 通常以"口头 + Slack 长信息 + 一封邮件 + 几张图"形态存在，永远停留在"我心里已经想清楚了"。落不到结构化文本就无法 backtest、无法 monitor、无法被 teammate challenge、无法在 12 个月后回溯"我当时怎么想的"。

#### 2.2.1 Agent 三个核心动作（V5.4 最重要的产品差异化之一）

**动作 1 · 辅导（proactively 提问引导）**

不是等 PM 写完才批改，而是在写作过程中主动提问把隐含假设逼出来。

例：PM 草写 "AI 利好云计算"，agent 逐条弹出反问：
1. "利好"是指股价 outperform SPY 多少 %？还是收入增速超过 20%？还是毛利率扩张？
2. "AI" 是终端用户对 AI 应用的需求，还是企业内部 AI workload？训练 vs 推理？
3. "云计算"指 hyperscaler，还是 IaaS/PaaS/SaaS 全部？
4. 时间窗：12/24/36 个月？
5. 最强 counterfactual 是什么——什么情况会让你说"我错了"？

PM 回答后，agent 把答案自动拼回 Thesis 正文草稿。

**动作 2 · fine-tune（识别歧义并给多个 rewrite 候选）**

Agent 在 PM 的 thesis 文本里**标红歧义段落**，并同时给 2–3 个 rewrite 候选让 PM 选或改。

例：PM 写 "GLP-1 主题会 rerate 整个医药板块"，agent 标红 "rerate 整个医药板块"：
- 歧义 1：rerate 方向？（估值扩张 vs 收缩）
- 歧义 2：范围？（肥胖药相关 vs 全医药板块）
- 歧义 3：时效？（一次性 vs multi-year）

给 3 个 rewrite 候选 A/B/C，PM 选或改写成第四种。

**动作 3 · 打碎模糊概念（把大而空陈述切成可证伪子陈述）**

Agent 把"太高维"的陈述自动切成一串可单独证伪的子陈述，作为 thesis 的 body structure。

例：PM 写 "AI 会改变零售"，agent 拒绝直接入库，切成 4 条子陈述：
- 子陈述 1（需求侧）："AI 驱动的个性化推荐将使头部电商 GMV/MAU 在 18 个月内提升 15%"（用 AMZN/MELI/PDD 验证）
- 子陈述 2（供应链）："AI 库存优化将使大型连锁零售（WMT/TGT/COST）24 个月内 inventory turnover 提升 0.5 turns"
- 子陈述 3（劳动力）："AI 客服 + 仓储自动化将使零售行业 labor cost / revenue 比率 36 个月内下降 150bp"
- 子陈述 4（新进入者）："AI-native 零售初创将在 24 个月内占据 >2% 的 US 线上零售份额"

PM 选 1–4 条作为 body；每条子陈述都可以独立 backtest、被 monitor、被证伪。Thesis 整体 confidence = 子陈述加权（PM 设权重）。

#### 2.2.2 其他 agent 动作

7. 反证清单生成（自动列 3–5 条会让 thesis 错误的历史先例或近似反例）
8. Catalyst 挖掘（earnings calendar / FDA PDUFA / 政策日历提取未来 6–12 个月相关 catalyst）
9. PIT backtest 触发（thesis v0 一定版立刻触发——用立项日之前的数据构造 prototype basket 跑回放，是 Validation 的一部分，**内嵌在 Thesis 段末尾**——v5.4 把 v5.2 独立的 Validation 工作流合并到这里）

#### 2.2.3 Thesis 状态机（v5.4 新版）

```
draft → under_review → active → stress_tested
                          │           │
                          ↓           │
                       evolving ──────┘
                          │
                          ↓ (定版新版本)
                      active (vN+1)
                          │
              ┌───────────┴───────────┐
              ↓           ↓           ↓
        invalidated   archived  (back to monitor)
              │
              │ (PM 触发复活 + rationale ≥ 100 字)
              └─────► evolving → active(vN+1)
```

**状态转换硬规则**：
- `draft → under_review`：PM 认为写完了；触发 agent 完整 fine-tune + 子陈述切分 + PIT backtest
- `under_review → active`：PM 定版，下挂第一个 Basket
- `active → stress_tested`：至少经历过一轮 Scenario 推演
- `active → evolving`：monitor 反馈触发重写；产生 vN+1
- `active → invalidated`：至少**两条核心子陈述**被 monitor 明确证伪
- `invalidated → evolving`（**v5.4 复活路径**）：PM 触发，要求 `resurrection_rationale ≥ 100 字`（合规要求）

> v5.4 重要决策（§4.6.5）：Thesis invalidated **不是终态**。允许复活到 vN+1，完整 lineage 保留。这支持"thesis 短期被证伪、后期市场反转"的现实场景（例："AI 利好云计算" 被 2024 Q3 短期调整证伪，但 2025 Q2 重新成立）。

### 2.3 §3.3 Basket 段

**业务目的**：把一份 Thesis 落成可交易 basket——决定标的、权重、约束、benchmark。

**PM 判断**：集中 10 只 vs 分散 40 只？等权 vs cap-weight vs 主题纯度加权？是否 benchmark neutral？是否保留现金？

**Agent 7 个动作**：
1. 筛候选标的（基于 Thesis 子陈述映射 universe 到对该子陈述有暴露的候选池）
2. 跑纯度打分（"这只股票对该 Thesis 的业绩敏感度"模型 = 文本相关性 + 历史 factor 载荷 + revenue exposure）
3. **给 3–5 套权重方案**（不要只给一套）：Equal / Cap / Purity Weighted / Risk Parity / Optimizer (Max Sharpe under 约束)，每套附 PIT backtest 曲线
4. 约束执行（单票上限、行业分散、流动性 ADV 天数、beta 中性、tracking error 上限）
5. 风险分解（factor exposure：growth/value/momentum/quality/low-vol + 行业 beta，让 PM 看到 basket 除了 thesis 还暴露了什么）
6. 交易成本估算（按 ADV + 预估换手率）
7. Rebalance 建议（basket live 后每次 monitor 触发告警，agent 给"要不要 rebal、rebal 幅度多少"）

**Basket 状态机**：`draft → proposed → active → rebalancing → retired`

### 2.4 §3.4 Monitor 段（双腿设计是 V5.4 的关键）

> **关键设计**：Monitor 段是 loop 里 agent 最"常驻"的一段。Theme/Thesis/Basket 段的 agent 是"被 PM 召唤时启动"，Monitor 段的 agent 是"7×24 背景跑"。这也是为什么 Monitor 段的数据管道（L0）**直接决定产品可用性**——新鲜度、延迟、吞吐都是 Monitor 段的硬约束。

**业务目的**：对已经上线的 Basket 做持续追踪，**两条腿并行**：
- **quant 腿** = 组合自身的统计属性（漂移、attribution、benchmark、风险暴露）
- **qualitative 腿** = thesis 所依赖的叙事/事件/catalyst（narrative velocity、新闻 catalyst 命中、行业对手盘移动）

**PM 判断的 fork**：当前 basket 还在"tracking the thesis" 吗？
- 如果 drift 了：是 basket 自身漂移（→ rebalance），还是 thesis 本身在 monitor 阶段被新事实动摇（→ Thesis evolve）

#### 2.4.1 Quant 腿 7 个动作

1. 持仓漂移追踪（相对 basket v0 holdings，当前权重漂移多少）
2. Attribution 分解（过去 N 日 basket 收益中多少来自 market beta / sector beta / 主题纯度 / alpha）
3. Benchmark 对比（excess return + tracking error）
4. Risk 监测（factor exposure 变化、波动率、drawdown、sharpe 滑动窗口）
5. Rebalance 信号（drift > 阈值 或 factor exposure 超约束 → 自动触发"建议 rebal"）
6. PIT backtest 持续回放（thesis v0 的 PIT backtest 在每个新 bar 上滚动，live vs 历史是否偏离）
7. 组合级上下文（把这个 basket 放到 PM 全部 active basket 里看 total exposure——不是为了投管，而是为了 monitor 决策时考虑 crowding）

#### 2.4.2 Qualitative 腿 5 个动作

1. **Narrative velocity 追踪**（新闻 + transcript + SEC filing 里 Thesis 关键词的提及速率；周环比 + 情绪分）
2. **Catalyst 命中监测**（thesis 段挂的 catalyst 到期时，agent 从财报/新闻/政府公告抓相关信号，判断"命中/未命中/部分命中"）
3. 新闻事件 alert（与 thesis 高相关的 M&A、政策、监管、重大产品发布）
4. 竞品 / 对手盘移动（13F / insider trading / ETF 流入流出）
5. **子陈述级 quant 验证**（thesis 打碎出来的每条子陈述，定期用可观测数据重新验证；e.g. "hyperscaler capex YoY > 30%"——每季 capex 财报出来后重算）

**Monitor Event lifecycle**：`raised → acknowledged → action_taken | dismissed → archived`（**append-only**，不允许删除——合规要求）

### 2.5 §3.5 Scenarios & Evolve 段（loop 闭环段，V5 defensibility 关键）

> 独立工具能做 narrative velocity，独立工具能做 backtest，但"Monitor → Scenarios → Basket 调整 → Thesis 版本"整条闭环，**需要四个环节共享同一套 object model + agent 编排**。

#### 2.5.1 两件事同时发生

- **Scenarios 衍生**：active Thesis 在 Monitor 阶段会受到外部冲击。PM 不是等"事情真的发生了"再反应，而是主动让 agent 生成"未来 3–6 个月可能发生的多条路径"，并对每条路径**提前想好"我要怎么调 basket"**
- **Thesis evolve**：Monitor 反馈 + Scenarios 推演的结果吸收回 thesis，产生 vN+1。**没有这一段，thesis 永远停在 v0，产品就退化成"一次性 research 工具"**

#### 2.5.2 Scenario 不是独立 primitive——它是 Thesis 的分叉

数据层面 `Scenario.parent_thesis_id` 指回 Thesis；生命周期上 Scenario 不能脱离 Thesis 存在。

#### 2.5.3 Scenarios 衍生侧 5 个动作

1. 从 thesis + monitor signals 生成 3–5 条 scenarios（典型 base/bull/bear/tail，可非对称数量）
2. 为每条 scenario 产出 **narrative + trigger signals + basket adjustment plan**（三件套，MVP 核心产出）；probability 字段按 §5.4 规则——MVP 不由系统自动生成
3. 每条 scenario 映射到具体 basket 调整方案（加仓哪几只、减仓哪几只、是否增减 beta 对冲）
4. 识别每条 scenario 的 trigger signal（什么数据点出现会把 probability 抬起来，e.g. "AWS 季度 capex YoY 突破 35%"）
5. 持续监测 trigger 到来（新 monitor event 到来时按 trigger signal 标记"已触发"或"未触发"；Phase 1 后自动重算 market-implied probability）

#### 2.5.4 Thesis evolve 侧 4 个动作

1. 识别触发条件（至少一条子陈述被 monitor 明确证伪/命中/时效过期 → 触发版本更新）
2. 起草 vN+1（基于 vN + monitor 收集的证据 + PM note，agent 起草，PM 审阅后定版）
3. 版本 diff 高亮（vN vs vN+1 的子陈述、catalyst、证伪条件变化）
4. 回写 basket 衔接（vN+1 定版后 agent 提示"当前挂在 vN 下的 basket 要不要 re-associate 到 vN+1"——**默认保留原关联，PM 显式批准才切换**）

**Scenario 状态机**：`proposed → active → triggered | obsolete → archived`

> **闭环表达**：`Thesis vN → Monitor → Scenarios → Basket 调整 → 观测 → Monitor → Thesis evolve → Thesis vN+1`。这个闭环是 V5 与"在研究工作流上加一个 chatbot"的根本区别——不是单点工具的堆叠，是四个环节共享同一套 object model + agent 编排。

---

## 3. 数据模型与状态机（§4）

### 3.1 五个主 object

#### Theme

| 字段 | 说明 |
|---|---|
| `id` | UUID |
| `tenant_id` | 所属机构 |
| `name` | 名称 |
| `boundary` | 业务边界（text + 结构化 facet：geo、industry、time_window） |
| `universe_ids` | 预筛候选股票 ID 数组 |
| `base_state` | `draft / active / archived`（系统维护） |
| **`pm_manual_state`** | nullable；PM 手标的 peaking/decaying（**v5.4 新增**） |
| `pm_manual_state_reason` | nullable；audit 用 |
| `pm_manual_state_at` | nullable |
| `created_by`, `created_at`, `updated_at` | — |

**Theme `current_state` 的 derived 计算**（v5.4 锁定）——不是 DB 直接字段：

```sql
CASE
  WHEN base_state = 'archived' THEN 'archived'                      -- P1: 终态
  WHEN pm_manual_state IN ('peaking','decaying')                    -- P2: PM 手标优先
       THEN pm_manual_state
  WHEN EXISTS (active Thesis 下挂) THEN 'monitoring'                -- P3: 派生
  WHEN base_state = 'active' THEN 'active'                          -- P4
  ELSE 'draft'
END
```

设计好处：**消除 Theme/Thesis state 同步不一致风险**；PM 手标能 override 系统计算（PM 看到市场信号比系统早）。

#### Thesis

| 字段 | 说明 |
|---|---|
| `id`, `theme_id`, `version`, `author_id` | — |
| `body.sub_assertions[]` | `{text, falsification_condition, verification_data_source, confidence}` |
| `catalysts[]` | `{event, expected_date, impact_direction}` |
| `falsification_conditions_global[]` | thesis 整体级证伪条件 |
| `time_window` | 开始/结束 |
| `confidence` | 0–1，自子陈述加权 |
| `state` | `draft / under_review / active / stress_tested / evolving / invalidated / archived` |
| `parent_thesis_id` | nullable；evolve/fork 时的父 thesis |
| `evolved_from_version` | 自我 evolve 时上一版本号 |
| **`resurrected_from_invalidated`** | bool；**v5.4 新增**——是否由 invalidated 复活而来 |
| **`resurrection_rationale`** | nullable text；**v5.4 新增**——PM 触发复活时必填 ≥ 100 字（SEC 204-2） |
| `signed_hash` | finalized 时 body 的 SHA-256 |
| `created_at, updated_at, finalized_at` | — |

> `author_id / version / signed_hash / resurrection_rationale` 等字段的存在理由是合规与审计（SEC Rule 204-2 + RIA fiduciary duty），**不是因为"署名是产品卖点"**。

#### Basket

| 字段 | 说明 |
|---|---|
| `id`, `version` | — |
| `thesis_id`, `thesis_version` | **不可变**——挂在哪一版 thesis 上是固定的 |
| `holdings[]` | `{ticker, weight, rationale}` |
| `weighting_method` | `equal / cap / purity / risk_parity / optimizer` |
| `constraints` | `{max_single_name, max_sector, min_liquidity_days, tracking_error_cap, ...}` |
| `benchmark` | ticker 或 custom index |
| `state` | `draft / proposed / active / rebalancing / retired` |
| `PIT_backtest_ref` | 指向 backtest 结果对象 |

#### Monitor Event

| 字段 | 说明 |
|---|---|
| `id`, `affected_thesis_id`, `affected_basket_id` | — |
| `event_type` | `drift / attribution_shift / catalyst_hit / catalyst_miss / narrative_spike / news_shock / exposure_breach / sub_assertion_verified / sub_assertion_invalidated / ...` |
| `severity` | `info / warn / critical` |
| `evidence_refs[]` | 数据点 / 新闻 / 财报段落引用 |
| `suggested_next_action` | `rebalance / spawn_scenarios / evolve_thesis / dismiss` |
| `state` | `raised / acknowledged / action_taken / dismissed / archived` |

> Monitor Event **append-only**，不允许删除（合规要求）。

#### Scenario（v5.4 修订版）

| 字段 | 说明 |
|---|---|
| `id`, `parent_thesis_id`, `parent_thesis_version` | — |
| `narrative` | scenario 描述（**MVP 核心产出**） |
| `trigger_signals[]` | `{observable_data, threshold, direction}`（**MVP 核心产出**） |
| `basket_adjustment_plan` | `{holdings_delta[], weight_changes, rationale}`（**MVP 核心产出**） |
| **`pm_personal_score`** | nullable float 0-1；PM 个人判断，**非系统推导**；v5.4 新增 |
| **`pm_score_rationale`** | nullable text |
| **`market_implied_probability`** | nullable float 0-1；Phase 1 从 options data 反推；**risk-neutral** |
| `market_implied_snapshot_time` | nullable timestamp |
| `market_implied_instruments[]` | 追溯用——哪些 options 组合反推的 |
| `state` | `proposed / active / triggered / obsolete / archived` |

**v5.4 关键修订**：删除 v5.3-concept 的单一 `probability` 字段，改为两个**显式标注来源**的字段。

### 3.2 §4.6 Theme/Thesis State 交叉约束（v5.4 新增章节）

#### 4.6.1 问题背景

v5.3-concept 把 Theme 和 Thesis 的 state 分别定义，但**没说一条线转移时另一条线的合法状态是什么**。会导致逻辑上不可能的组合出现在 DB 里——比如"Theme 已 archived 但下面还有 active Thesis"。v5.4 补上这个空白。

#### 4.6.3 完整交叉矩阵

| Thesis →<br>Theme ↓ | draft | under_review | active | stress_tested | evolving | invalid / archived |
|---|---|---|---|---|---|---|
| **draft** | 合法 | 非法 | 非法 | 非法 | 非法 | 非法 |
| **active** | 合法 | 合法 | 合法 | 合法 | 合法 | 合法 |
| **monitoring** | 合法 | 合法 | 合法 | 合法 | 合法 | 合法 |
| **peaking** | 合法 | 合法 | 合法 | 合法 | 合法 | 合法 |
| **decaying** | ⚠️警告 | ⚠️警告 | 合法 | 合法 | 合法 | 合法 |
| **archived** | 非法 | 非法 | 非法 | 非法 | 非法 | 合法 |

#### 4.6.4 四条 invariant

1. **Theme 必须先于 Thesis 存在**：Thesis `→ under_review` 之前，所属 Theme 必须已 active。`draft Thesis` 可以在 `draft Theme` 下存在
2. **Theme 必须保护所有活跃 Thesis**：Theme `→ archived` 时，下挂所有 Thesis 必须已 invalidated 或 archived。Theme archive 是级联操作，不能单独触发
3. **Theme decaying 给警告但不阻塞**：允许 Thesis 继续 active 跑到 time_window 结束，但 UI 给 warning。在 decaying Theme 下新起草 Thesis 特别要 warning（反常识，PM 可能误操作）
4. **Theme 状态来源 v5.4 锁定**：MVP 阶段 Theme 的 peaking/decaying 状态由 PM 手动标注，不做自动状态转移
   - 阈值难定（拥挤度、narrative velocity 衰减的具体数字每家机构不一样）
   - PM 的直觉比算法准（Tiger Cub PM 对"这个主题开始 peak 了"有强烈直觉）
   - 减少 MVP 工程复杂度（自动状态转移需要 crowding detector + narrative velocity + 多因子聚合，每条都是 R&D 项目，省 20+ 人·天）

#### 4.6.5 Thesis invalidated 可复活（v5.4 锁定）

设计要点：
- `invalidated → evolving` 允许——PM 显式触发"复活"，agent 起草 vN+1
- vN+1 与 invalidated vN 的关系——通过 `parent_thesis_id` + `evolved_from_version` + `resurrected_from_invalidated` 三个字段保留完整 lineage
- **复活需 explicit rationale**——`resurrection_rationale ≥ 100 字`（既是 SEC 204-2 的 decision rationale，也防止随意复活）
- UI：invalidated thesis 默认归档页显示，但有"复活"按钮

#### 4.6.6 复活操作的审计要求

| 字段 | 内容 |
|---|---|
| who | 触发复活的 PM ID |
| when | 触发时间 |
| what | 从 invalidated vN 进入 evolving，产生 vN+1 |
| why | PM 写的 rationale（≥ 100 字，强制） |
| evidence | 可选——PM 关联的 monitor events 或外部新闻链接 |

### 3.3 §4.7 状态转移级联规则

#### 4.7.1 Theme 动作触发 Thesis 级联

| Theme 动作 | 对下挂 Thesis 影响 | 级联行为 |
|---|---|---|
| Theme `draft → active` | 下挂 draft Thesis 可进入 under_review | 解锁 Thesis 状态转移 |
| Theme `→ monitoring`（derived） | 至少一个 active Thesis 存在 | 仅 indicator 变化 |
| Theme `→ peaking`（PM 手标） | 不强制转态 | UI 给下挂 Thesis 挂 "Theme peaking" badge |
| Theme `→ decaying`（PM 手标） | 收到 review reminder | active/stress_tested 推 reminder（不强转）；draft/under_review 给强警告 |
| **Theme archive 请求** | **必须所有 Thesis 已 invalidated/archived** | 拒绝并提示"请先处理这 N 个 Thesis" |

#### 4.7.2 Thesis 动作触发 Theme 级联

| Thesis 动作 | 对所属 Theme 影响 | 级联行为 |
|---|---|---|
| 首个 Thesis `→ under_review`（Theme 为 draft） | Theme 应已 active | 自动推 Theme `base_state: draft → active` |
| 首个 Thesis `→ active` | Theme derived 变为 monitoring | current_state 自动返回 monitoring |
| 最后一个 active Thesis 退出 | Theme 失去 monitoring 语义 | 退回 active；若 pm_manual_state 是 peaking/decaying 则保留 |
| Thesis `invalidated → evolving`（复活） | 无 Theme 级影响 | 审计日志记录复活事件 |
| Thesis `evolving → active(vN+1)` | 无 Theme 级影响 | 审计日志记录版本定版 |

#### 4.7.3 Basket 对 Thesis state 的依赖

| Basket 操作 | 要求 Thesis state | 约束 |
|---|---|---|
| Basket 创建 | `active / stress_tested / evolving` | 不能挂在 draft / under_review / invalidated 下 |
| Thesis invalidated 时 | 必须 N 天内处理（默认 N=30） | PM 必须 retire Basket 或 re-associate |
| Thesis archived 时 | 所有下挂 Basket 已 retired | 有 active Basket 则拒绝 archive |
| Thesis 复活时 | 原下挂 Basket 保持 retired | 复活产生 vN+1 时 PM 决定是否新建 Basket（**不自动 re-activate 原 Basket**） |

#### 4.7.4 Monitor Event 对 Thesis state 的依赖

- Thesis `active / stress_tested / evolving`：Monitor Event 正常生成
- Thesis `invalidated`：Monitor Event 继续生成（合规要求——继续记录直到 archived），但**不触发 Scenario 衍生 / Thesis evolve**
- Thesis `archived`：Monitor Event 停止生成，历史 event 保留
- Thesis 复活：Monitor sensor 重挂到 vN+1；原 vN 的 Monitor Event 归档到该 thesis lineage 但不影响 vN+1 的新 event

### 3.4 §4.9 Schema 演化约束

- Basket 的 `thesis_id + thesis_version` 组合在生命周期内**不可变**（要换 thesis 版本 → 开新 basket 版本）
- Thesis 进入 active 后**不允许原地修改 body**，必须开 vN+1
- Monitor Event 为 **append-only**，不允许删除（合规）
- 所有主 object 有软删除字段 `deleted_at`，物理删除仅在法律请求下触发
- `resurrected_from_invalidated` 字段一旦写入 `true`，**不允许改回 false**
- `Scenario.market_implied_probability` 不可 PM 编辑——**只能系统计算**

---

## 4. Scenario 段与 Probability 设计（§5，v5.4 最重要新增章节）

### 4.1 问题的重新 frame

> v5.3-concept 未决问题原本问："Scenarios 的贝叶斯更新深度是 PM 手动 + agent 建议为主，还是 agent 自动 + PM 可覆盖为主？"——**这个问题本身 frame 错了**。

v5.4 的 reframe：**Scenario 的产品价值在 qualitative 结构（narrative + trigger signals + basket adjustment），不在 probability 数字本身**。一个写得好的 scenario 本身就是完整的 playbook，不需要 probability 标签。

### 4.2 核心原则（v5.4 锁定）

> MVP **不做系统级自动 probability**。Scenario 的核心产出是 qualitative narrative + trigger signals + basket adjustment plan。PM 可选填 personal score 作为个人判断记录。Phase 1 接入 options market data 后，展示 market-implied probability 作为 reference line（明确标注 risk-neutral）。Historical analogues 路径暂不做（样本永远不够）。
>
> **产品立场：不预测市场，让 PM 的判断结构化、可追踪、可回放**。

### 4.3 为什么 MVP 不给 scenario 自动 probability

| 反对理由 | 说明 |
|---|---|
| LLM 给的 probability 是 narrative-generated 不是 derived | 客户问"这 30% 怎么算的"没有有说服力的答案——这正是早期 MiroFish 路线被否决的同一个问题，不能重蹈覆辙 |
| Small-sample historical Bayesian 比没有 prior 还危险 | Citrini 2 年 archive 约 200 个 thesis，贝叶斯会给出 confident 但错误的 prior。Thematic thesis 的分支组合数太大，样本库永远不够 |
| 机构客户对"AI 预测市场"默认警惕 | "我们不预测市场、让 PM 的预测过程结构化"比跟风做"AI probability engine"更 institutional-friendly |
| 合规更清爽 | 系统不出 probability 不承担 accuracy 责任。PM 手输的 score 归 PM 主观判断，SEC 204-2 下 fiduciary 责任链清晰 |

### 4.4 为什么 market-implied 是 Phase 1 而不是 historical

| 维度 | Market-implied (Phase 1 推荐) | Historical analogues (Phase 2 保留选项) |
|---|---|---|
| 数据 ground truth | 市场真金白银投票 | 内部统计；小样本 |
| 机构客户接受度 | 高——他们自己的语言 | 中——要解释方法论 |
| Demo 说服力 | "Options 定价这个 scenario 23%" | "历史上 23 个相似 thesis..." |
| Hallucination 风险 | **零** | 中——embedding 相似不等于情境相似 |
| 启动门槛 | 接入 options data（~$50k/年） | 需 500+ labeled thesis（5+ 年积累） |
| 覆盖率 | Liquid underliers only | 所有 thesis 理论上可覆盖 |
| 合规清爽度 | 高——非系统预测，市场数据 | 中——系统的 prior 算作预测 |

### 4.5 三阶段实现路径

#### Phase 0（MVP · 0-120 天）· 纯 qualitative + optional PM score

Scenario 4 个产出字段：`narrative` / `trigger_signals[]` / `basket_adjustment_plan` / `pm_personal_score` (optional)

Agent 做前三项；**不碰 probability**。

创建流程：
```
PM 在 Monitor 段看到关键告警 → 点击"衍生 scenarios" → Agent 生成 3-5 条
  - 每条 narrative ~200 字
  - 每条 3-5 个 trigger signals
  - 每条带 basket adjustment plan
→ PM 审阅 (可编辑 narrative / 调 triggers / 改 plan / 选填 personal score)
→ 确认保存 → state: proposed → active
```

#### Phase 1（接入 options data 后）· market-implied 作为 reference line

对每个 scenario 自动找一组 market instruments（payoff 与 scenario 对应）：
- Bull → OTM call options on basket constituents
- Bear → OTM put options
- Tail → deep OTM options 或 VIX calls
- Base → 当前 forward price 对应概率

从 implied vol surface 反推 risk-neutral probability，UI 展示 `market-implied: 23% (risk-neutral)`——**明确标注 risk-neutral，不装作是 real-world probability**。

**关键产品规则**：market-implied 只作 reference line，**不作 system 的 primary probability**。Scenario object 的 primary probability field 仍是 `pm_personal_score`（optional，空也可以）。

技术实现要点：
- Options data source：CBOE / OPRA / Polygon
- Instrument matching 需 LLM 辅助（"这个 scenario 的 payoff pattern 是 OTM call at strike X"）
- Strike selection 需定义规则（"bull scenario = +10% at 3-month ATM"）
- Coverage fallback：没 liquid options 的 constituent 标 "insufficient liquidity"，**不猜数字**
- 重算频率：每日 EOD + 重大 monitor event 触发

#### Phase 2（Year 2+ 可能）· historical analogues 作为次级信号

- 只有当 library 真大到统计有意义（> 500 theses with labeled outcome、多 regime、多年份）才启用
- 永远作为 **tertiary signal**，不是主导
- **实话**：Citrini archive 可能永远达不到这个规模——2 年产生 200 个 thesis 是现实数字，500 个 labeled thesis 需要 5 年以上

### 4.6 §5.5 三条硬约束（写进 Product Principles）

无论哪个 phase：

1. **所有 probability 数字必须 attributable**——UI 上点任意数字都能打开"为什么是这个数字" drawer
2. **PM 永远可以 override**——agent 给的 prior / market-implied 只是参考，PM 最终数字算数
3. **LLM 不直接吐 probability 数字**——LLM 只负责 scenario narrative、sub-assertion mapping、retrieval。所有数字从确定性计算来（market data 或 PM 手输）

### 4.7 产品叙事上的 strategic benefit

> 市面上现在有一堆 AI 投研产品在吹"AI 给你算概率"，机构 buyer 本来就对这类 claim 警惕。V5 反着走——"我们把 scenario 做成结构化 playbook，probability 留给 market 或 PM，不由 AI 生成"——这个定位比跟风做"AI probability engine"更 defensive、更 institutional-friendly。

---

## 5. Agent 架构（§6）

### 5.1 六个 agent 一览

| loop 段 | agent 名 | 编排形态 | 核心调用栈 |
|---|---|---|---|
| §3.1 Theme | Discovery | 后台常驻 + on-demand | Claude API + text embedding + 向量聚类 + MCP data tools |
| §3.2 Thesis | Formulation | 会话式，与 PM 交替 | Claude API (multi-turn) + structured output schema + MCP data tools |
| §3.3 Basket | Construction | on-demand，长任务 | Claude API + factor model tool + optimizer + PIT backtest |
| §3.4 Monitor | Monitor | 后台常驻 7×24 | Claude API + stream processing + event generation + MCP |
| §3.5 Scenarios | Scenario | on-demand + 事件触发 | Claude API (planning) + trigger signal extractor + (Phase 1) options pricing engine |
| §3.5 Evolve | Evolve | 事件触发，低频 | Claude API + diff generator + citation extractor |

### 5.2 Context 策略

- **共享 object model，不共享 prompt context**——六个 agent 不共享完全相同的 prompt context，但共享同一套 object model（Theme / Thesis / Basket / Monitor Event / Scenario）。Formulation agent 在对话中可以调 MCP 工具 fetch Thesis 最新状态，**不必把所有状态塞进每轮 prompt**
- **独立 system prompt + 独立 tool 清单**——动作形态差异大：Formulation 是 coaching 型（提问），Construction 是 execution 型（跑参数），Monitor 是 detection 型（流处理）

### 5.3 技术选型

- **LLM 层**：Claude（Anthropic API）作为主要推理引擎；其他模型作为 fallback / 特定子任务（embedding / ranking）
- **MCP 层**：MCP 作为 agent 调用外部工具的统一接口。典型 MCP server：market data / news / factor model / PIT backtest / portfolio analytics
- **Tool layer**：MCP 背后的具体服务——自研 or wrapping 第三方（Bloomberg / FactSet / S&P Capital IQ / Quiver / AlphaSense）。**核心自研：PIT backtest、factor model、monitor stream processor**
- **Persistence**：loop 上所有 object 在 Postgres + object store；时序数据（monitor events、price panel）在 Postgres timeseries extension 或 ClickHouse
- **多租户隔离**：schema-per-tenant 或 row-level security；行情数据是共享池，PII / thesis 内容严格租户隔离

### 5.4 Thesis evolve 环节——loop 最关键的技术环节

详细序列：
```
1. Monitor agent 连续写入 Monitor Event 到 object store
2. Trigger 条件命中（例 ≥N 条子陈述证伪）→ Monitor agent 通知 Evolve agent
3. Evolve agent 读取 Thesis vN + 相关 Monitor Events + Scenarios
4. Evolve agent 起草 vN+1 候选：
   - 标记哪些子陈述要删/改/新增
   - 更新 catalyst 列表
   - 重算 confidence
5. Evolve agent 推送"Thesis 建议更新"通知给 PM（附 diff）
6. PM 进入 Formulation 会话（复用 §3.2 agent）协作打磨 vN+1
7. PM 定版 vN+1，state → active
8. Monitor sensor 重挂到 vN+1：
   - 旧 basket 关联 vN+1 的确认对话触发
   - 旧 vN 的 Monitor Event 保留在 thesis lineage
```

**关键设计**：Evolve agent **不直接产出最终版**；它产出 candidate diff + 说明，交给 Formulation agent（也就是 §3.2 agent）继续与 PM 协作定版。loop 技术上这样闭合。

### 5.5 Agent 责任边界

- Agent 提议、评分、起草：可以独立完成
- Agent 定版、签字、触发订单：**必须有 PM 显式确认**
- Agent **永远不直接修改 active 的 Thesis 或 Basket**：只能创建新 version + 请求 PM 合入

边界来源：合规（AI 不能替代 fiduciary 决策）+ 客户信任（机构客户默认不信任"AI 自动改我的仓位"）。

### 5.6 v5.4 特殊约束

无论哪个 agent，**都不允许直接写入** `Scenario.pm_personal_score`（PM 手输）或 `Scenario.market_implied_probability`（Phase 1 由 options 引擎计算，非 LLM）。LLM 只能生成 `narrative / trigger_signals / basket_adjustment_plan` 三个 qualitative 字段。这是 §5.5 三条硬约束在 agent 层面的落实。

---

## 6. PIT 时点一致性与数据栈（§7）

### 6.1 为什么 PIT 是硬约束

V5 的 backtest、validation、monitor 都依赖时点一致的数据。没有 PIT，backtest 会 leak 未来信息，产品给出的任何历史类比都不可信。

机构客户会在 bake-off 阶段就问："你们怎么处理 restatement？split-adjusted？ETF 权重变化？" V5 必须能给出有审计 trail 的答案。

### 6.2 三层数据栈

```
┌─ L0a · 行情 / 基本面 ───────────────────────────────┐
│ Market data: 开高低收成交 + 分红 / 拆分 / 重述调整     │
│ Fundamental data: 财报 + 前瞻一致预期                  │
└────────────────────────────────────────────────────┘
                       ↓
┌─ L0b · 因子与画像 ─────────────────────────────────┐
│ Factor panel: PIT 因子载荷                           │
│ Classification: GICS / 自定义主题 taxonomy            │
└────────────────────────────────────────────────────┘
                       ↓
┌─ L0c · Universe / 主题 ────────────────────────────┐
│ Universe snapshot: 每日 PIT universe                  │
│ Taxonomy snapshot: 主题 → 候选股票映射                 │
└────────────────────────────────────────────────────┘
```

三层职责：
1. **行情 + 基本面**：vendor 数据（Bloomberg / FactSet / S&P Capital IQ），落盘为 PIT-safe——任何 restatement 都附带有效日，**不覆盖历史**
2. **因子与画像**：基于第一层计算的 factor panel；每个因子每只股票每日一点，带 as-of 日
3. **Universe / 主题**：把第二层切成可查询的 universe 快照——"2023-03-15 当日 Russell 3000 的成分股 + 每只股票的因子载荷 + 属于哪些主题 taxonomy 节点"

### 6.3 PIT 在 backtest 与 monitor 之间共享（关键设计）

> Backtest 与 live monitor **用同一套 universe 快照服务**。当 backtest 问"2023-03-15 某 Theme 的 universe 是什么"，与 live monitor 问"2026-04-19 某 Theme 的 universe 是什么"走完全同一个 API，只是 as-of 日不同。
>
> 这消除了"backtest 跑出来好看，live 却跑不赢"的常见陷阱——**训练与 production 同源**。

### 6.4 数据新鲜度 SLA

| 数据 | SLA |
|---|---|
| 行情 | < 15 分钟（日内），EOD 当晚入库 |
| 文本（新闻 / transcript / filing） | < 5 分钟触发 monitor sensor |
| 因子 panel | T+1 EOD 更新 |
| Universe 快照 | 每日一次 |

### 6.5 多租户隔离

- 行情 / 文本原始数据 = 共享池（vendor 授权允许）
- Thesis 内容 / PM 操作 log / basket holdings / scenarios / comments = **严格租户隔离**（schema-per-tenant 或行级隔离 + KMS 密钥租户化）
- 审计 log：按 tenant 分区，客户可独立取证

---

## 7. 团队工作流（§8，刻意写薄）

> 本章篇幅短、语气平淡——这是产品的**卫生要求，不是差异化卖点**。

### 7.1 能力清单

| 能力 | 粒度 | 默认开关 |
|---|---|---|
| Thesis 在 tenant 内可读 | 对象级 | 开 |
| Thesis fork（创建 parent_thesis_id 链接） | 操作级 | 开，可 tenant admin 关 |
| Thesis cite（显式引用） | 操作级 | 开 |
| @ 提及 + Slack/Teams 通知 | 操作级 | 开，用户级可关 |
| 行级 comment（在某段子陈述上留言） | 操作级 | 开 |
| IC review checklist（轻流程） | 流程级 | 选配 |
| Extended（跨 tenant 白名单）visibility | 对象级 | tenant admin opt-in |
| Public 发布（写到公开网络） | 对象级 | tenant admin opt-in，**产品默认不推** |

### 7.2 为什么不写厚

早期 v5.3 旧版有独立的"Thesis Formulation workflow" + "Thesis Collaboration workflow" + "Visibility 模型与 Tenant Admin 控制"三大章节，用了近 80 页概念篇幅——这是 overshoot。v5.4 用 1 页讲清楚：协作能力以"随产品附带"的形态存在，**不做单独的产品叙事**。

### 7.3 跨 tenant / 公开发布的刻意保守

- 默认 tenant admin 不允许 extended 可见性
- 即使 tenant admin 打开 public，产品 UI 也不给"一等入口"。这不是"Substack for PMs"
- Compliance review 流程必须挂在公开发布前

---

## 8. 合规与审计（§9）

### 8.1 法规基线

| 法规 | V5 的对应措施 |
|---|---|
| **SEC Rule 204-2**（RIA 记录保存 ≥5 年） | Thesis 版本历史 + audit trail + monitor event log 原生满足 |
| **FINRA Rule 2210**（如适用） | comment audit + version lineage 满足 supervision 工作流基本需求 |
| **SEC Rule 10b-5 / Reg FD** | 默认关 + 打开时插入显式 disclaimer 流程 |
| **SEC Marketing Rule (Rule 206(4)-1)** | 产品不输出"保证收益"、"必赚"、"最优秀"这类字样 |

### 8.2 实现要点

- Thesis `finalized_at` 对应的 body snapshot 写入 **append-only** 存储，含 SHA-256 hash
- 任意编辑视为"从 vN 创建 vN+1 草稿"，**不得覆盖 vN**
- Monitor Event **append-only**
- 所有操作 log 在 tenant audit log 中保留 **7 年**（超出 204-2 的 5 年，给 FINRA 冗余）
- 一键导出完整的 thesis lineage + monitor history 作为合规取证材料

### 8.3 v5.4 新增 · Thesis 复活的审计要求

1. `resurrection_rationale` 必填，≥ 100 字
2. 审计日志记录 who / when / what / why / evidence
3. 合规报告导出时**复活事件 highlight 展示**（SEC 204-2 关心 decision rationale）
4. Compliance officer 可按 thesis lineage 查询完整状态历史（含 vN 的 invalidation + vN+1 的复活）

### 8.4 SOC 2 路径

- SOC 2 Type II：Y1 必须（机构客户 bake-off blocker）
- ISO 27001：Y2（扩展国际客户）
- GDPR：从 day 1 对 EU tenant 合规
- Penetration test：Y1 上半年完成首轮

### 8.5 合规不是 wedge 但是 blocker

V4 教训：compliance 是 tie-breaker 不是 wedge。
- **差异化（赢单子）**：loop + agent 辅助 + monitor/scenarios 闭环
- **Blocker（输单子）**：SOC 2 没拿下、数据隔离不干净、audit trail 无法导出

合规做到"大家都有的水平"即可，不追求在合规层做卖点。

---

## 9. Forks MVP 入口（§10）

> 本节内容已在 [`forks_mvp_relation_to_trading_platform.md`](forks_mvp_relation_to_trading_platform.md) 详细展开（包含与 trading_platform 的概念映射、不应跨过的边界、双向可借鉴点）。本笔记只补 V5.4 §10 在 V5 整体设计里的**承上启下**位置。

### 9.1 核心立场

- Forks 是 V5.4 终态的 **90 天 MVP 入口**，不是 V5.4 的完整实现，也不是被砍版的 V5.4
- 客群：fintwit / aspiring buyside / semi-pro / 学生
- 覆盖 V5.4 最有差异化价值的三段：**Scenarios + Monitor + Evolve**
- 未覆盖：Theme / Thesis-agent 三动作 / Basket / PIT 数据栈

### 9.2 关键洞察：Thesis 是 commodity，Scenario 是 alpha

> 多个聪明 PM 看同样的市场会得出相似 thesis（"AI 利好 hyperscaler" 是共识）。真正区分不同 PM 的 alpha 是 scenarios——同样的 thesis 下，谁能想到某条 supply chain 重构、谁能识别出 bear scenario 里的非对称机会。

所以 Forks MVP 不做 V5.4 §3.2 的 Thesis 段 agent 三动作——那是文本润色，不改变 thesis 本身的 insight。**MVP 聚焦在 Scenario 段**。

### 9.3 是否违反 V5.4 §11.1 的"MVP 必须覆盖完整 loop"

V5.4 自己的解释：
- §11.1 硬规则原本针对**机构客户 MVP**——当 MVP 面向 Tiger Cub PM 时确实必须覆盖完整 loop（因为他们的工作流是完整 loop）
- Forks 面向 fintwit / semi-pro，他们的工作流只需 Scenarios + Monitor 两段就能 deliver 核心价值
- 所以 Forks MVP 的 scope 决策**不是对规则的例外**，是对规则适用对象的合理区分

### 9.4 24 个月演化路径

| 阶段 | 时间 | 加什么 | 客户 | 对应 V5.4 章节 |
|---|---|---|---|---|
| Forks MVP | 0-3 月 | Scenarios + Monitor + Evolve 闭环 | fintwit / semi-pro | §3.4 / §3.5 |
| Forks v1.x · 深化 | 3-9 月 | Trigger 自动化 + 付费数据源 | + 机构 PM 个人沉默用户 | §5 Probability Phase 1 |
| + Basket | 9-15 月 | PIT backtest + basket construction | Family office / RIA / 小型 hedge fund | §3.3 |
| **v5.4 Canonical** | 15-24 月 | Theme + Thesis 段 + 多人协作 + 合规 | Tiger Cub / multi-strat / Theme ETF | §3.1 / §3.2 / §9 |

---

## 10. MVP 范围与价值链完整性（§11）

### 10.1 MVP 纪律

> MVP 必须覆盖完整 loop 的每一段。**不是"先做 theme + basket，thesis/monitor/scenarios 后面再说"——那不叫 MVP，那是砍环节**。客户在 bake-off 上看不到 monitor + scenarios 的原型，不会相信你能交付"闭环 loop"的价值主张。

### 10.2 P0 最简实现

| 段 | P0 范围 |
|---|---|
| Theme | PM 手输 + agent 反证清单；universe 基于 GICS + 3 个 factor |
| Thesis | agent 三动作全做；子陈述 3 种 pattern；catalyst 手挂；PIT backtest 单一 prototype basket |
| Basket | 3 种权重方案 equal/cap/purity；5 个标准约束；PIT backtest + factor exposure |
| Monitor | quant 腿全做；qualitative 腿做 narrative velocity + catalyst hit；告警中心 + Slack integration |
| Scenarios | agent 生成 3 条（narrative + trigger + adjustment）；不做自动 probability；pm_personal_score 选填；Evolve 支持手动升版 + 复活路径 |

**P0 合格判据**：每段都能让 PM 端到端走通；agent 在这段做至少 2 个动词级动作；PM 能感知到 agent 的"帮助"而非"chatbot 摆设"。

### 10.3 时间线推荐选项 A（120 天 + 维持完整 loop）

```
0–30 天：object model + L0 数据栈骨架 + Thesis/Basket/Theme 三段 P0 前端
30–60 天：Monitor P0（quant 腿优先）+ 首个 Thesis formulation agent
60–90 天：Monitor qualitative 腿 + Scenarios & Evolve P0
90–120 天：内部 dogfood（Citrini）+ 至少 1 个外部 design partner 上线
```
团队：2 FE + 3 BE + 1 quant + 1 PM（兼任产品 owner）

### 10.4 不允许的 MVP 裁剪（护栏）

- ❌ "先做 Theme + Basket，Thesis / Monitor / Scenarios 后面再说"
- ❌ "Monitor 先只做日度 EOD 看板，live alert 后做"——live alert 是产品可信度 anchor
- ❌ "Scenarios 交给用户手建"——那就不是"agent 辅助的 loop"
- ❌ "Evolve 功能 v2 再做"——loop 不闭环，defensibility 不成立
- ❌ "MVP 加上自动 probability 算法"——v5.4 明确不做（§5.2）

---

## 11. 与前版的关系（§12 浓缩）

| 与 | 关系要点 |
|---|---|
| v5.2 | loop 结构基本沿用；工作流名字从动词型 → 名词型 loop stage；Validation 合并进 Thesis 段；Scenario 从独立 primitive 降为 Thesis 分叉 |
| v5.3（旧版） | 删除"Thesis 是 loop 唯一主角""GitHub for thesis library""Substack for PMs""viral growth loop"等 framing；Thesis Formulation/Collaboration 两个独立 workflow 拆分合并 |
| v5.3-concept | 直接上游，新增 §4.6/§4.7/§5/§10 四章；锁定 Thesis 复活 + Theme 手标两个未决；删除单一 probability 字段 |

---

## 12. 剩余未决问题（§13）

v5.3-concept 6 个未决，v5.4 解决其中 2 个；剩 4 个保留到 v5.5 或实际 build 时处理：

| 未决 | 问题 | 何时必须回答 |
|---|---|---|
| 1 | Monitor qualitative 腿数据源——自建 scraper (~$50k/年) vs 买 AlphaSense/RavenPack/Prattle ($500k+/年) | MVP 开始后 30 天内 |
| 2 | 跨 tenant extended 可见性的 IP 模型（显式 cite？Non-cite fork 是否允许？） | extended 档功能上线之前（P1 之前） |
| 3 | Monitor 段订阅模式与价格（按 basket 数 / 按 seat / 按 compute 单位） | 首批商业合同落地之前 |
| 4 | Thesis evolve 的量化触发门槛（≥2 条子陈述被证伪 vs confidence 下降 >20% vs PM 手动 only） | MVP launch 前 2 周（可调参） |
| 5 | Extended/Public 通道的刻意限制会否影响"想用 V5 做 thought leadership"的头部 PM 获取 | GA 之前 |

---

## 13. 与 trading_platform 的对照与启发

> 本节**只补** [`forks_mvp_relation_to_trading_platform.md`](forks_mvp_relation_to_trading_platform.md) 还没覆盖的部分。已映射的 Thesis/Scenario/Trigger schema、Forks MVP 90 天里程碑、双向借鉴清单等，都在那份 bridge 文档里，这里不重复。

### 13.1 V5.4 设计语言 vs trading_platform 概念（loop 全段对照）

| V5.4 概念 | trading_platform 现有对应 | 对应程度 | 说明 |
|---|---|---|---|
| Loop 五段（Theme→Thesis→Basket→Monitor→Scenarios） | `the_task_routing.md` 里的 task 主线（current-market / theme / single-stock / operation-portfolio-decision / theme-priority） | **结构同源、切分不同** | 我们按"PM 日常任务"切；V5.4 按"研究对象的状态机"切。两边可以互补 |
| Theme 段（Discovery agent 扫 universe 聚类） | 没有自动 Discovery agent；`current_priority_tree.json` 是 PM 手维护的 theme 池 | **形态不同** | 我们没做"每日浮现 3 个候选 Theme"。如果做，要遵 `13_index_first_ai_for_gaps`：先建 source_collection 标签，再让 AI 补语义聚类 |
| Theme `boundary` 结构化（geo/industry/time_window facet） | `themes/reports/<id>.md` 里的边界是自由文本 | **缺结构化** | 可以把 boundary facet 升级为 frontmatter 字段，让 PM 报告/portfolio 决策都可以查询 |
| Theme `derived current_state` 计算（base_state + pm_manual_state + 下挂 Thesis） | 我们有 `priority_bucket / priority_rank` 但没"下挂 thesis 数量"的 derived 状态 | **可借鉴** | 这个 derived state 模式可以套到我们的 theme 元数据上 |
| **Thesis agent 三动作（辅导/fine-tune/打碎）** | `single-stock-analysis` 和 `research-theme-knowledge-and-package-curator` 主要做"基于 package 写报告"；不做"提问引导 + 标红歧义 + 切子陈述" | **缺失** | 这是 V5.4 最有差异化的一段。**对我们的价值有限**——单 PM 操作系统不需要"逼出隐含假设"，因为 PM 自己就是 author。但"打碎模糊概念为可证伪子陈述"对 ThesisNote schema 是真升级 |
| Thesis `body.sub_assertions[]` schema（每条带 falsification_condition + verification_data_source + confidence） | `thesis_note.claim_bullets / key_dependencies / disconfirming_evidence` 是平铺字段 | **schema 升级机会** | 把 ThesisNote 的 claim 升级为带 `falsification_condition` + `verification_data_source` 的对象数组，能让我们的 monitor 自动 trace 子陈述命中状态 |
| Thesis 状态机 + invalidated 复活 | ThesisNote 没有显式状态机；过期/失效靠人工判断 | **缺机制** | "复活"是个有趣的 lineage 设计——`parent_thesis_id` + `evolved_from_version` + `resurrected_from_invalidated` 三字段能保留完整 thesis 历史。对长 horizon 主题（"美元霸权衰减"这类 5 年主题）有价值 |
| Basket 段（5 套权重方案 + factor exposure + tracking error） | 我们的 operation-portfolio-decision skill 做"加减仓建议"，没有 5 套权重 ABC 比较 | **范围不同** | trading_platform 是单 PM 实盘（Schwab + Crypto），不是 basket modeling 工具。Basket 段的 deterministic 部分（factor exposure / ADV / 约束执行）我们也用得上——属于 operation-portfolio-decision 的下游升级 |
| **Monitor 双腿（quant + qualitative）** | quant 腿：`asset_technicals` 信号包 + 每日 signal_packets/*.md（部分覆盖）<br>qualitative 腿：`research-current-market-reporter` + 研究归档（弱 trigger 化） | **quant 腿强、qualitative 腿弱** | 我们已经有 deterministic 的 quant 腿（`signal_packets` + `reports/listed_*.md`），但没把它和"thesis 命中状态"绑定。qualitative 腿基本上是"PM 自己读研究"，没有 trigger state machine |
| Monitor `子陈述级 quant 验证`（每季 capex 财报后重算 sub_assertion） | 没有；fundamental 数据是 ad hoc 查询，不挂在 thesis sub-assertion 上 | **缺机制** | 与上面 sub_assertions schema 升级一起做，能形成"thesis 子陈述 → 数据源 → 自动验证"的链路 |
| Monitor Event lifecycle + append-only | artifact_graph 有 freshness/sidecar，但没"事件流"对象 | **形态不同** | 我们的 freshness 是"数据/报告新鲜度"，V5.4 的 Monitor Event 是"thesis 相关的世界变化"。两者**正交**，可以叠加 |
| Scenario probability 三阶段路径 | 我们 PM 报告里完全不出 probability 数字 | **立场一致** | V5.4 §5 的"产品立场：不预测市场，让 PM 判断结构化"和我们 `35_pm_writing_contract.mdc` 的"reader state first / 让 PM 能区分什么已确认/什么未确认"立场**完全一致**——两边可以互相印证 |
| Scenario `narrative + trigger_signals + basket_adjustment_plan` 三件套 | `themes/reports/*.md` 里写"路径/情景"段落（自由 prose）；没有结构化 trigger | **schema gap** | 这是 forks_mvp_relation 已经详细列过的——把 scenario 提为一等公民对象 + trigger state machine。**对 trading_platform 是 high-leverage 升级** |
| Agent 责任边界（agent 不直接修改 active 对象，只创建新 version） | 我们的 ai_writer 节点也是这样——产出 draft 到 `theme_update_drafts/<id>.ds.md`，不直接覆盖 `themes/reports/<id>.md`（要 reviewer + PM 合入） | **设计已对齐** | 这条是 V5.4 和 trading_platform 不约而同的——证明这是好设计。**可以反向写进我们的 axiom**（"AI 永不直接修改 active 对象，只创建新版本 + 请求合入"）|
| MCP 作为 agent 调用外部工具的统一接口 | 我们目前是 Python tool 直接调用，没有 MCP 抽象 | **架构选型差异** | 单 PM 系统不需要 MCP；机构产品需要。**不是借鉴对象** |
| PIT 三层数据栈（行情/因子/universe） | 我们有 L0a（asset_technicals + Schwab data + crypto），但没有显式的 L0b 因子 panel + L0c universe 快照 | **L0a 强、L0b/L0c 弱** | trading_platform 现在不需要 backtest，所以 universe-as-of-date API 不是必需。但如果将来要做 thesis 历史回放，这个三层栈是参照系 |
| 合规章节（SEC 204-2 / FINRA 2210 / Marketing Rule） | trading_platform 是单 PM 内部 OS，不是 RIA SaaS | **N/A** | 但 V5.4 的"复活需 100 字 rationale"模式可以借鉴——任何对历史 thesis_note 的"复活/重新激活"操作都该带 rationale 字段 |
| 团队工作流（fork/cite/comment） | 单 PM，无团队 | **N/A** | — |

### 13.2 V5.4 哪些设计原则与本仓 axioms 互相印证

下列 V5.4 立场与我们 [`09_soul/axioms/`](../../09_soul/axioms/) 的 axioms / `.cursor/rules/` 的规则**结构一致**，互为印证：

| V5.4 立场 | 本仓对应 axiom / rule |
|---|---|
| MVP 不做系统级自动 probability，让 PM 判断结构化（§5.2） | `35_pm_writing_contract` 的"reader state first / 让 PM 能区分已确认 vs 未确认" |
| LLM 不直接吐 probability，所有数字从确定性计算来（§5.5） | `13_index_first_ai_for_gaps`（先消费结构化字段，AI 只补语义空白） |
| Agent 永远不直接修改 active 对象，只创建新 version（§6.5） | 我们的 ai_writer 产出 draft + reviewer gate 模式 |
| Monitor Event append-only，不允许删除 | `42_artifact_graph_admission`（artifact graph 节点的 sidecar/freshness 永久记录） |
| Theme `current_state` 是 derived，避免 Theme/Thesis state 同步不一致（§4.1.1） | `13_index_first_ai_for_gaps`（结构化推导优先于猜测） |
| 协作能力是"卫生要求不是卖点"（§8） | `41_dedicated_skill_admission`（不为了"看起来更全"造 skill） |
| Compliance 是 tie-breaker 不是 wedge（§9.6） | 同上——基础设施必须做到位但不是差异化叙事 |

### 13.3 V5.4 哪些设计**不应该**借鉴到 trading_platform

- **不要把 V5.4 的"机构客户 + 多 PM + 多 tenant + bake-off + SOC 2"叙事框架搬过来**——trading_platform 是单 PM 内部系统，loop 完整性的判定标准、agent 编排的成本约束、合规深度都不同
- **不要把 V5.4 的"Thesis 段 agent 辅导/fine-tune"做成主角**——单 PM 操作系统下，PM 自己就是 author，不需要 agent 反问"你说的'利好'是指什么"。这部分价值在多 PM 协作场景才显现
- **不要为了对齐 V5.4 引入 MCP / Anthropic-only 技术栈**——我们的 Python tool 直调和 LiteLLM 选择是单 PM 场景的合理工程选型
- **不要把 V5.4 的"loop 必须完整"硬规则套到我们的 task mainline 上**——我们的 task mainline（`routing-task-mode-router` 等）是按"PM 日常使用场景"切，不是按"研究对象状态机"切，两套切法的完整性判定标准不同
- **Forks 的社交层（K-factor / 病毒层 / vindication card / KOL seeding）已在 forks_mvp_relation §6 列为"不应跨过去的边界"**，本笔记不再重复

### 13.4 最值钱的三条具体借鉴（按性价比排序）

> 这是 forks_mvp_relation §5.1 已经列过的三件事的**收敛复述**，方便从本笔记跳过去。

1. **Trigger state machine**：把 `thesis_note.scenario_triggers` 从自由文本升级成 `{observable_data, threshold, direction, status: pending|triggered|reverse_triggered|obsolete, observed_at_utc, hit_evidence}`
2. **Scenario 提为一等公民对象**：`data/research/thesis_notes/` 旁加一层 `scenarios/<id>.json`，让 theme report / single-stock note / portfolio decision 都**引用**而不是**重写**
3. **Thesis sub-assertion schema 升级**：把 `claim_bullets` 升级为 `[{text, falsification_condition, verification_data_source, confidence}]`，配合 trigger state machine 形成"子陈述 → 数据源 → 命中状态"的可机审链路

详细操作建议见 [`forks_mvp_relation_to_trading_platform.md §5`](forks_mvp_relation_to_trading_platform.md)。

---

## 14. V5.4 关键决策速查表

> 任何时候要对比 V5.4 立场或回忆 v5.4 相对前版的改动，从这张表入口。

| 决策 | 内容 | 章节 |
|---|---|---|
| Loop 主角 | 不是 Thesis library，是 5 段 loop 闭环 | §1.4 / §3 |
| Thesis 段 agent 三动作 | 辅导（提问） / fine-tune（rewrite 候选） / 打碎模糊概念（切子陈述） | §3.2 |
| Monitor 双腿 | quant（drift/attribution/benchmark/risk）+ qualitative（narrative velocity / catalyst / 子陈述验证） | §3.4 |
| Scenario 不是独立 primitive | 是 Thesis 的分叉（`parent_thesis_id`） | §3.5 |
| Validation 不再独立 | 合并进 Thesis 段末尾的 PIT backtest | §3.2 / §12.1 |
| Theme `current_state` derived | base_state + pm_manual_state + 下挂 Thesis 集合三层优先级派生 | §4.1.1 |
| Theme peaking/decaying | MVP 由 PM 手标，不做自动状态转移 | §4.6.4 |
| Thesis invalidated 可复活 | invalidated → evolving → active(vN+1)，需 ≥100 字 rationale | §4.6.5 |
| Scenario probability 不自动生成 | MVP 纯 qualitative + 选填 PM personal score；Phase 1 接入 options 算 market-implied (risk-neutral)；Phase 2 historical 保留 | §5.4 |
| 三条 probability 硬约束 | attributable / PM 永远可 override / LLM 不直接吐数字 | §5.5 |
| Agent 责任边界 | 提议/起草独立完成，定版/签字/触发订单需 PM 显式确认；永不直接改 active 对象 | §6.5 |
| PIT 三层栈共享 | backtest 与 live monitor 走同一套 universe-as-of-date API | §7.3 |
| 协作能力定位 | 卫生要求不是卖点；1 页讲完，不写厚 | §8 |
| 合规定位 | tie-breaker 不是 wedge；做到 industry standard 即可，不在合规层做卖点 | §9.6 |
| Forks MVP 覆盖范围 | Scenarios + Monitor + Evolve 三段；不做 Theme / Thesis-agent三动作 / Basket | §10.3 |
| MVP 不允许的裁剪 | 砍 Monitor live alert / 砍 Scenarios / 砍 Evolve / 加自动 probability 算法 | §11.5 |

---

— End of V5.4 Canonical 阅读笔记 —
