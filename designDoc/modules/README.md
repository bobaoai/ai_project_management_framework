# Modules

这些子文档按 `功能模块` 组织，而不是按技术组件或接入源组织。

对应的第一版核心 operating loop：

1. `data_collection.md`
2. `info_classification.md`
3. `portfolio_exposure.md`
4. `opportunity_ranking.md`
5. `structured_advice.md`

与当前研究工作流直接相关的补充模块说明：

- `asset_technical_signal_pipeline.md`
- `account_review_and_journal.md`
- `daily_data_update_dashboard.md`

每个文档统一回答：

- 这个模块解决什么问题
- 输入和输出是什么
- 关键对象和状态是什么
- 主要 agent / workflow 是什么
- human-in-the-loop 边界在哪里
- 与其他模块如何衔接

这些模块文档应与总纲文档 [`../ai_native_trading_operating_system.md`](../ai_native_trading_operating_system.md) 配套阅读。

另外还应与两个横切设计文档一起阅读：

- [`../knowledge_base_and_memory_system.md`](../knowledge_base_and_memory_system.md)
- [`../analysis_platform_and_pm_workspace.md`](../analysis_platform_and_pm_workspace.md)

因为从当前阶段开始：

- `KnowledgeBase` 是第一类系统对象
- `AnalysisPlatform` 是第一类工作对象
