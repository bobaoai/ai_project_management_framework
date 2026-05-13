# Source Connectors And Knowledge Ingestion

**Version 0.1 — 2026-03-21**

> Status: legacy boundary note. New connector and ingestion-family work should start from [`ingestion_00_overview.md`](ingestion_00_overview.md) and [`ingestion_10_source_connector_contract.md`](ingestion_10_source_connector_contract.md). This file remains as historical context until the connector sections are fully absorbed.

本文档描述 `SourceConnectorLayer` 与知识摄入边界，重点解释为什么 Gmail 应从 `research` 主体语义中剥离出来。

---

## 1. Purpose

系统不应把某个 connector 误建模为研究系统本身。

正确分层应是：

- connectors 负责接入外部输入
- archive / data layer 负责可靠落盘
- knowledge layer 负责组织为可检索对象
- agents / workflows 负责理解、排序、建议

---

## 2. What Counts As A Source Connector

典型 connectors 包括：

- Gmail
- RSS
- broker APIs
- market data APIs
- web fetchers
- manual file drops

它们的共性不是“研究”，而是“接入边界”。

---

## 3. Connector Responsibilities

connector 只做以下几件事：

- connect and authenticate
- fetch source content
- save raw artifacts
- emit minimal metadata
- track sync status and errors

connector 不应默认负责：

- 深层摘要
- thesis 生成
- ticker/macro 的完整推断
- 机会排序
- PM 建议输出

这些属于后续模块。

---

## 4. Gmail Reframing

Gmail 的正确定位：

- 它是 research/newsletters/documents 的一种运输通道
- 它不是知识库本身
- 它也不是 analysis platform 本身

因此 Gmail connector 的目标是：

- 把邮件及其附件、链接、元数据保存到本地
- 让后续模块能读取这些内容

而不是在接入阶段一次性把所有分析都做完。

---

## 5. Minimal Ingestion Philosophy

当前阶段更适合采用：

- `minimal ingest parsing`
- `retrieval-time interpretation`

也就是：

- 接入时保存 raw files + small metadata index
- 真正需要分析时，再让 Cursor/agents 读取原文件并花 token 做理解

这样做的好处：

- ingest pipeline 更稳
- source-specific parser 压力更小
- 未来更容易扩展到网页、PDF、RSS、手工导入文件

---

## 6. Recommended Connector Output Contract

每个 connector 输出至少应包括：

- raw artifact path
- source type
- source id
- `observed_at_utc` / `recorded_at_utc`
- sender / publisher / domain
- mime or content type
- minimal text preview
- sync metadata

如果成本低，可以补：

- extracted links
- attachment list
- normalized title

但不要求每个 connector 都做完整知识抽取。

---

## 7. Relationship To Knowledge Base

connector 输出进入 archive 后，才逐步转化为 knowledge objects。

路径应当是：

`connector output -> archive object -> normalized knowledge record -> retrieved analysis context`

这意味着：

- connector 是输入边界
- knowledge base 是组织层
- analysis platform 是消费层

对 research-style sources，推荐进一步理解为：

`connector output -> messages archive -> snapshot and/or theme draft -> reviewed thesis note`

这条链路意味着：

- connector 负责把 source material 安全送到 canonical archive
- connector 可以补充 minimal metadata，但不应直接把单条输入升级成 thesis
- thesis promotion 必须发生在 knowledge workflow 内，而不是发生在 connector 层

---

## 8. Research Connector Promotion Rule

对 newsletter、report、manual import、screenshot 这类 research inputs，connector 之后的默认流程应是：

1. 保存 raw artifact 和 canonical archive path
2. 保留 sender / publisher / headers / timestamps / source metadata
3. 如有必要补充 links、attachments、cleaned text
4. 交由 knowledge layer 决定它更像：
   - `messages/` long-form source
   - `snapshots/` atomic evidence
   - `theme_update_drafts/` synthesis under review
5. 只有在 review gate 之后，才允许 promotion 到 `thesis_notes/`

也就是说：

- connector 不负责最终 judgment
- connector 不负责 thesis approval
- connector 只负责把后续 thesis workflow 所需的 provenance 保留下来

---

## 9. Gmail In This Repo

就 `trading_platform` 而言，Gmail 适合作为：

- research/newsletter connector
- file delivery connector
- event memo connector

不适合作为：

- 整个 research 模块的命名中心
- 总设计文档的主角

---

## 10. Current Design Direction

因此当前 repo 的文档语义调整为：

- 总纲：[`ai_native_trading_operating_system.md`](ai_native_trading_operating_system.md)
- 模块：`DataCollection -> InfoClassification -> PortfolioExposure -> OpportunityRanking -> StructuredAdvice`
- connector 专题：本文件
- market data 总纲：[`market_data_architecture.md`](market_data_architecture.md)
- price 规则：[`price_data_architecture.md`](price_data_architecture.md)
- fundamentals 规则：[`research_33_company_fundamentals_data_architecture.md`](research_33_company_fundamentals_data_architecture.md)

后续若扩展 RSS、web、manual imports，也沿用同一 connector 语义即可。

需要注意：

- 本文件只定义 connector 通用边界
- 不重复定义具体的 `price` 或 `fundamentals` provider 规则
- market data 相关的字段级规则与对象模型应以下游专用文档为准
