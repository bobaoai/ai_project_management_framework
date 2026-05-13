# Opportunity Ranking

## Purpose

`OpportunityRanking` 负责把“很多可能有意思的东西”压缩为“现在最值得优先处理的少数机会”。

## Responsibilities

- 生成候选机会集
- 基于催化、赔率、风险、组合适配度排序
- 过滤不满足 mandate 或 execution quality 的候选
- 记录 reject reasons
- 为 PM 决策准备优先级列表

## Inputs

- classified research
- market context
- technical setups
- event awareness
- portfolio exposure context

## Outputs

- ranked candidates
- conviction hints
- reject reasons
- priority queues
- watchlists

## Core Entities

- candidate
- setup
- catalyst
- conviction score
- reject reason
- watchlist entry

## Agent Roles

适合的 agent：

- screener
- ranking engine
- debate or committee agent
- risk gate

## Human-In-The-Loop Boundary

人主要负责：

- 决定哪些机会值得进入正式讨论
- 覆核排序是否符合当前 regime 与 mandate

系统主要负责：

- 快速筛选
- 排序
- 保存被拒绝原因

## Dependencies

- `InfoClassification`
- `PortfolioExposure`
- `StructuredAdvice`

## Notes

- 这一模块不只是选股，还包括 trade expression 与 timing priority
- 好的排序系统必须同时知道 “这是不是好机会” 和 “这是不是对当前组合最合适的机会”
