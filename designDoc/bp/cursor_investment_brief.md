# Intelligent Trading Platform — Brief
# 智能交易平台 — 简报

---

## Platform Overview / 平台概述

A personal quantitative trading intelligence platform that covers the full workflow: **data acquisition, portfolio monitoring, risk analysis, technical signals, and intelligent advisory**.

个人量化交易智能平台，覆盖完整工作流：**数据获取、持仓监控、风险分析、技术信号、智能建议**。

---

## What the Platform Does / 平台功能

### 1. Portfolio Monitoring / 持仓监控

Direct connection to brokerage accounts via Charles Schwab API. Automatically captures daily position snapshots across all accounts — equities, options, and futures. Positions are valued at latest market prices and organized by sector/basket for clear visibility.

通过 Charles Schwab API 直连券商账户，每日自动抓取全账户持仓快照（股票、期权、期货），按板块/篮子分类展示，使用最新市场价格估值。

### 2. Risk Exposure Analysis / 风险敞口分析

Computes option Greeks (Delta, Gamma, Theta, Vega) for every position. Aggregates directional exposure by sector and basket — shows exactly where risk is concentrated. Detects expiration clustering in options positions and flags single-name overexposure.

为每个头寸计算期权 Greeks（Delta、Gamma、Theta、Vega）。按板块和篮子聚合方向性敞口，精确展示风险集中在哪里。检测期权到期聚类和单一标的过度暴露。

### 3. Multi-Timeframe Data Engine / 多周期数据引擎

Maintains a self-updating historical data warehouse covering 200+ symbols at four timeframes: 30-minute, 1-hour, 4-hour, and daily. Data is sourced from Schwab REST API, stored in optimized formats (SQLite + Parquet), and automatically gap-filled when missing bars are detected.

自维护的历史数据仓库，覆盖 200+ 标的的四个时间周期（30 分钟、1 小时、4 小时、日线）。数据从 Schwab REST API 获取，以优化格式存储（SQLite + Parquet），检测到缺口自动补填。

### 4. Technical Signal System / 技术信号系统

- **Elliott Wave Detection**: Identifies ABC correction and 5-wave impulse patterns on 30-minute and daily charts, each pattern scored 0-100 for quality
- **Trend Segmentation**: SMA-based trend direction identification with noise filtering across timeframes
- **IV Analysis**: Monitors implied volatility conditions across the options universe

- **Elliott Wave 识别**：在 30 分钟和日线级别自动识别 ABC 调整和 5 浪推动形态，每个形态 0-100 质量评分
- **趋势分割**：基于 SMA 的多周期趋势方向识别，带噪声过滤
- **IV 分析**：监控期权隐含波动率状况

### 5. Intelligent Advisory Agents / 智能顾问 Agent

Three AI-powered agents that process raw data into structured, actionable output:

三个 AI 驱动的 Agent，将原始数据加工为结构化的可执行输出：

**News & Macro Agent / 新闻宏观 Agent**
Aggregates financial news and macro research (including Citrini sector positioning, Capital Flow fund rotation data, Conk macro regime analysis). Classifies each item by relevance to current holdings and upcoming catalysts (Fed, CPI, earnings).

整合金融新闻和宏观研报（Citrini 板块持仓、Capital Flow 资金轮动、Conk 宏观分析），按持仓相关性和即将到来的催化事件分类。

**Portfolio Advisor / 组合顾问 Agent**
Reads current positions and delta exposure, compares against target risk profile, and generates specific rebalancing suggestions — which positions to reduce, where to add hedge, which expirations to roll.

读取当前持仓和 Delta 敞口，对照目标风险画像，生成具体调仓建议 — 减持什么、在哪加对冲、哪些到期需要展期。

**Screener Agent / 标的筛选 Agent**
Screens the full symbol universe against configurable trading rules: wave pattern quality, trend direction alignment, IV percentile conditions, volume/liquidity filters. Outputs a ranked candidate list.

按可配置的交易规则筛选全标的池：波浪形态质量、趋势方向一致性、IV 百分位条件、成交量/流动性。输出排序的候选名单。

### 6. Dashboard & Reporting / 看板与报告

Web-based dashboard showing portfolio overview, exposure breakdown, agent recommendations, and signal status. One-command daily report generation. Historical position tracking for review and attribution.

Web 看板展示持仓概览、敞口分解、Agent 建议和信号状态。一键生成每日报告。历史持仓追踪用于复盘和归因。

---

## Monthly Budget: $500 / 月度预算：$500

**Research & Intelligence Feeds / 研报与情报订阅 (~$200)**

Professional macro research subscriptions that serve as structured data inputs for the platform's Agent system:

- Citrini — equity sector analysis, institutional positioning, thematic baskets
- Capital Flow — fund flow tracking, sector rotation signals
- Conk — macro regime analysis, cross-asset indicators

专业宏观研报订阅，作为平台 Agent 系统的结构化数据输入：Citrini（板块分析+机构持仓）、Capital Flow（资金流向+轮动信号）、Conk（宏观体制分析）。

**AI Development Tool / AI 开发工具 (~$200)**

AI-assisted coding tool (Cursor) for ongoing platform development and maintenance. The platform consists of 50+ modules across portfolio management, data pipelines, analytics, and agent systems — maintained by a single developer.

AI 辅助编程工具（Cursor），用于平台持续开发和维护。平台由 50+ 模块组成，涵盖持仓管理、数据管道、分析引擎和 Agent 系统 — 由单人开发维护。

**Data & API / 数据与 API (~$100)**

API usage for multi-timeframe data acquisition across 200+ symbols, analytics computation, and data storage infrastructure.

200+ 标的的多周期数据获取 API 用量、分析计算和数据存储基础设施。
