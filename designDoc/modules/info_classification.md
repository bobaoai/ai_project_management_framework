# Info Classification

## Purpose

`InfoClassification` 负责把原始材料整理成系统可复用的知识对象，而不是让每次分析都从原始噪音开始。

## Responsibilities

- 标准化文本和元数据
- 主题归类与标签化
- ticker / basket / macro topic 关联
- 组织 research objects
- 管理 summary、memo、index 等中间知识产物

## Inputs

- raw artifacts from `DataCollection`
- existing knowledge records
- portfolio context
- operator annotations

## Outputs

- normalized knowledge records
- searchable indexes
- memo-ready summaries
- entity links
- retrieval-ready context bundles

## Core Entities

- research item
- knowledge record
- topic tag
- entity link
- evidence reference
- memo excerpt

## Agent Roles

适合的 agent：

- classifier
- summarizer
- linker
- memo distiller

## Human-In-The-Loop Boundary

人主要负责：

- 定义 taxonomy 是否合理
- 审核重要材料的归类结果
- 修正误链、误标记、错误摘要

系统主要负责：

- 初步归类
- 检索组织
- 生成中间知识对象

## Dependencies

- `DataCollection`
- `KnowledgeStateLayer`
- `PortfolioExposure` for context-aware classification

## Notes

- 这一模块是知识库建设的核心
- 不必默认把所有原始内容都解析到极致
- 更适合 “minimal ingest, richer retrieval-time reasoning”
- 但 `KnowledgeBase` 已经是更高一层的正式设计对象；本模块更像知识库中的“整理与转化”工作面，而不是知识库本身
