# Structured Advice

## Purpose

`StructuredAdvice` 负责把分析结果转化为投资经理可直接消费的结构化建议。

## Responsibilities

- 输出 thesis / evidence / risks / action framing
- 连接机会、组合上下文、风险约束
- 支持多种 trade expression
- 给出后续监控与复盘要点
- 生成 memo、brief、review artifacts

## Inputs

- ranked opportunities
- portfolio exposure context
- linked evidence
- risk flags
- human preferences and mandate

## Outputs

- structured recommendation
- investment memo
- decision brief
- monitoring checklist
- review-ready rationale

## Core Entities

- recommendation
- rationale
- evidence bundle
- action framing
- monitoring plan
- post-trade review hook

## Agent Roles

适合的 agent：

- advisor
- memo writer
- committee chair
- review assistant

## Human-In-The-Loop Boundary

人主要负责：

- 最终 capital allocation
- 最终 risk ownership
- 是否执行、何时执行、执行多大

系统主要负责：

- 提供结构化建议
- 保留证据链
- 让判断过程更可复盘

## Dependencies

- `OpportunityRanking`
- `PortfolioExposure`
- `InfoClassification`

## Notes

- 输出的重点应是结构化和可追溯，而不是“写得像聊天”
- 这一模块应优先服务 PM decision workflow，而不是服务 demo 风格的 bot 对话
- `AnalysisPlatform` 是更高一层的工作面；本模块更偏“正式输出对象”的生成与交付
