# Market Data Architecture

**Version 0.1 — 2026-03-26**

本文档是 `trading_platform` 的市场数据总纲，但它只负责定义：

- 市场数据这一层在系统里的位置
- `price` 与 `fundamentals` 的边界
- provider / connector / platform store / analysis consumer 的职责划分
- 哪个设计问题应由哪份文档负责

它不重复定义具体 `price` 规则或 `fundamentals` 规则。

---

## 1. Purpose

当前 repo 已经有：

- `Schwab` 驱动的部分市场数据代码
- `history_loader` 这类已落地的数据抓取逻辑
- `price_cache` / `options_snapshot` 这类迁移残留
- 外部 worker 驱动的 fundamentals 拉取痕迹

问题不在于“有没有市场数据功能”，而在于：

- price 与 fundamentals 还没有被正式拆成两类对象
- provider 边界还不清晰
- 旧代码残留与新设计之间没有统一真相面

因此本文件的目标，是把市场数据重新放回系统级结构里，而不是把它写成某个单一 provider 的使用说明。

---

## 2. System Position

市场数据属于 `SourceConnectorLayer` 与 `DataCollection` 的交叉工作面。

它的正确路径应是：

`provider connector -> canonical platform objects -> coverage / retrieval surfaces -> analysis consumers`

这意味着：

- provider 是接入边界
- canonical symbol / coverage / normalized objects 属于平台层
- PM/analysis 消费的是规范化后的价格与基本面对象，而不是 provider 原始 payload

---

## 3. Split The Domain

市场数据在本 repo 中应拆成两大类：

### 3.1 Price Data

包括：

- quotes
- bars
- end-of-day prices
- intraday prices
- futures contract selection
- roll policy
- freshness and provenance

详细规则由：

- [`price_data_architecture.md`](price_data_architecture.md)

负责。

### 3.2 Fundamentals Data

包括：

- security profile
- key stats
- financial statements
- point-in-time reference views
- statement / filing semantics
- fundamentals provider ownership

详细规则由：

- [`research_33_company_fundamentals_data_architecture.md`](research_33_company_fundamentals_data_architecture.md)

负责。

---

## 4. Ownership Boundaries

### 4.1 Connector / Provider Layer

provider connector 只负责：

- authenticate
- fetch raw or lightly normalized payloads
- expose provider-local symbol formats
- record sync status and errors

provider connector 不负责：

- PM-facing interpretation
- cross-provider precedence judgment
- canonical symbol truth
- final analysis artifacts

### 4.2 Platform-Owned Market Data Layer

平台层负责：

- canonical symbol identity
- asset typing
- provider mapping
- coverage status
- freshness status
- normalized price/fundamentals objects
- normalized macro series and observation history
- downstream consumer contracts

当前 price bar 路径的明确约束：

- PostgreSQL 是 canonical price-bar runtime store
- `history_loader` 应直接把规范化 bars 写入平台层 PostgreSQL 表
- parquet 仅作为导出/缓存 artifact，不是分析层主读取路径
- 不再把 SQLite 作为 technical runtime 的 bar truth surface

### 4.3 Analysis Consumption Layer

分析层负责：

- 读取 task-specific projections
- 结合价格、基本面、研究、组合做判断
- 输出 memo / recommendation / monitoring artifacts

它不应直接暴露 provider plumbing。

### 4.3A Ticker Coverage And Admission Layer

在当前系统里，`ticker` 不能继续只作为 theme metadata 的附属字段存在。

更稳的做法是把它单独视为一个 `coverage / admission layer`：

- `ticker` 是被 admission 的分析对象
- 不同上游只是 admission source，而不是 ticker 本体

当前至少要支持这些 admission source：

- `theme`
- `portfolio`
- `manual list`
- `task-scoped list`

后续也可以扩展：

- connector-derived watchlist
- screener result
- imported basket

这个层的职责应是：

- 记录哪些 ticker 进入当前 coverage universe
- 记录 admission provenance
- 记录 admission scope 是持久还是临时
- 给 downstream technical / fundamentals / timeline / profile workflows 提供统一对象入口

这意味着：

- theme 不再独占 ticker universe
- portfolio holdings 不应只作为 technical 层的临时补丁
- manual list 不应只能作为一次性 ad hoc 输入
- task-scoped ticker list 也可以进入当前工作批次的 coverage surface，而不自动升级为长期 routing authority

### 4.4 Macro Indicator Path

宏观指标在当前 repo 中应作为平台拥有的规范化时间序列对象处理：

- source fetcher 负责抓取官方或公开 source
- 平台层负责统一 `series_key`、时间戳、单位、来源元数据与入库
- 派生序列如 `SOFR_FF`、`2s10s`、后续 `net_liquidity` 由平台确定性生成
- 报告、图表、profile、theme-view 这类消费面读取的是平台存储后的标准 series，而不是 source 原始 payload
- 长历史视角与当前决策窗口应作为可复用展示模式，由平台统一生成而不是在单次分析里临时拼接

---

## 5. Provider Roles

当前默认方向：

- `Schwab`：broker/auth/account-linked context，以及任何真实可用的 market data surface
- `EODHD`：fundamentals / reference / broader market-data enrichment 的第一候选 provider
- `FuturesDataPath`：独立建模，不预设必须等同于当前 `Schwab REST quote/history`

本文件只定义 provider family，不在此处定义每个字段谁优先。

字段级 precedence 规则：

- `price` 见 [`price_data_architecture.md`](price_data_architecture.md)
- `fundamentals` 见 [`research_33_company_fundamentals_data_architecture.md`](research_33_company_fundamentals_data_architecture.md)

---

## 6. Relationship To Existing Docs

为避免文档互相覆盖，每份文档只保留一个工作：

- [`source_connectors_and_knowledge_ingestion.md`](source_connectors_and_knowledge_ingestion.md)：connector 的通用边界
- [`postgres_ticker_coverage_design_v0_1.md`](postgres_ticker_coverage_design_v0_1.md)：ticker universe / watchlist / coverage orchestration
- [`analysis_platform_and_pm_workspace.md`](analysis_platform_and_pm_workspace.md)：分析消费与 PM 工作面
- [`price_data_architecture.md`](price_data_architecture.md)：价格与期货主规则
- [`research_33_company_fundamentals_data_architecture.md`](research_33_company_fundamentals_data_architecture.md)：基本面主规则

其中：

- theme / portfolio / manual list 如何把 ticker admission 到 coverage universe，属于 `postgres_ticker_coverage_design_v0_1.md` 和相关 module docs 的细化问题
- 本文只定义 ticker coverage/admission 应存在于平台层，而不应被某个单独 theme workflow 私有化

如果一个问题已经在下游专用文档里定义，这里只放链接，不再重复。

---

## 7. Current Repo Reality

当前代码面大致是：

- `src/core/schwab_client.py`：现有 REST market data client
- `src/market_data/history_loader.py`：当前最完整的已落地 market-data path
- `src/market_data/price_cache.py`：迁移残留 stub
- `src/market_data/options_snapshot.py`：迁移残留 stub
- `src/tools/holdings_options_sync.py`：已移除，不再作为正式入口

当前状态更像：

- `bars` 有一条相对真实的路径
- `quotes` 有 client method，但缺少上层规范化消费层
- `fundamentals` 还没有正式纳入统一 provider architecture
- `futures` 很可能需要独立 connector / streaming 路线

当前已收敛的一点：

- asset technical runtime、dashboard technical pages、latest-price history fallback 都应优先读取 PostgreSQL price bars

---

## 8. Cleanup Rule

后续代码清理必须遵守：

1. 先把目标对象模型和 provider 边界写清楚
2. 再决定哪些旧代码保留、抽象、删除或标记为 deprecated
3. 不允许一边清理旧代码、一边让文档重新混成一个“大杂烩”

当前执行导向的 cleanup inventory 见：

- [`temp/market_data_cleanup_inventory_20260326.md`](temp/market_data_cleanup_inventory_20260326.md)

---

## 9. Design Routing

当后续有人问：

- “这个字段属于谁定义？”
- “这个 provider 为什么存在？”
- “futures 合约该怎么选？”
- “fundamentals 到底谁是主来源？”

应按以下顺序跳转：

1. 本文档：先判断问题属于哪一类
2. `price_data_architecture.md` 或 `research_33_company_fundamentals_data_architecture.md`
3. 如涉及 universe / coverage，再看 `postgres_ticker_coverage_design_v0_1.md`
4. 如涉及分析消费，再看 `analysis_platform_and_pm_workspace.md`
