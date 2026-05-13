# Portfolio Exposure

## Purpose

`PortfolioExposure` 负责把账户与持仓信息转换成真正可用于判断的组合上下文。

## Responsibilities

- 聚合持仓与现金状态
- 计算 delta / notional / concentration context
- 按 basket、theme、sector、expiry 组织暴露
- 识别风险标记和约束边界
- 为机会评估提供组合适配上下文

## Inputs

- account snapshots
- account journals and broker activity records
- positions
- option greeks
- basket mappings
- market prices

## Outputs

- exposure summaries
- concentration flags
- hedge gaps
- basket-level views
- daily and weekly account-change context
- reusable portfolio context for agents

## Core Entities

- account snapshot
- daily account journal
- position snapshot
- exposure summary
- basket exposure
- risk flag

## Agent Roles

适合的 agent / system roles：

- exposure calculator
- risk watcher
- portfolio context builder

## Human-In-The-Loop Boundary

人主要负责：

- 定义组合目标和风险偏好
- 审核关键暴露与对冲边界

系统主要负责：

- 计算
- 聚合
- 标记异常
- 输出可复用组合上下文

## Dependencies

- account and broker data inputs
- market data and pricing context
- `OpportunityRanking`
- `StructuredAdvice`

## Notes

- 没有组合上下文，任何机会排序都容易失真
- 这一模块是 AI-native discretionary system 与一般选股器的关键区别之一
- PM-facing scenario analysis should consume saved account snapshots plus exposure summaries through theme routing and asset memory, rather than through a standalone `scenario_report` module
- account review/report markdown 不是事实源；可修改的日报和周报应建立在 saved snapshots、orders、transactions、daily journals 这些 truth surfaces 之上
