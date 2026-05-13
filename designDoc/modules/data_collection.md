# Data Collection

## Purpose

`DataCollection` 负责把外部世界的输入可靠送入本地系统，并形成后续模块可以消费的原始材料与最小索引。

## Responsibilities

- 对接 source connectors
- 拉取 market / research / portfolio / event inputs
- 保存 raw artifacts
- 记录最小元数据和同步状态
- 维持 source health visibility

## Boundary With `data update`

`DataCollection` 是上游职责。

`tradectl data update` 可以作为 umbrella refresh command 去触发某些已确定的日更动作，但这不改变模块边界：

- `DataCollection` 负责 fetch / import / save / sync bookkeeping
- `DailyDataUpdateDashboard` 负责汇总 refresh 后的 readiness / freshness / blocking
- package builders 负责读取 truth artifacts 并做 deterministic assembly
- analysis/report writers 负责形成 judgment 和 prose

不要因为有了 `data update`，就把导入、读取、打包、分析视为同一个层。

## Inputs

- Gmail / RSS / web pages
- broker and account APIs
- market data APIs
- manually dropped files
- operator-triggered refresh commands

## Outputs

- raw files
- snapshots
- broker activity archives
- metadata rows
- sync logs
- source freshness status

## Core Entities

- source connector
- raw artifact
- source record
- broker activity fetch
- sync checkpoint
- ingestion status

## Agent Roles

这一模块尽量少依赖“深度思考 agent”。

更适合的角色：

- connector operator
- fetch scheduler
- ingestion validator

## Human-In-The-Loop Boundary

人主要负责：

- 决定接入哪些数据源
- 管理 credentials 和 connector scope
- 审核 source quality

系统主要负责：

- fetch
- save
- index
- report failures
- support simple local scheduling for repeatable daily refresh jobs when the workflow is already deterministic

## Dependencies

- `SourceConnectorLayer`
- `DataLayer`

## Notes

- Gmail 只是一个 connector，不是本模块的命名中心
- ingest 时优先保证稳定性和可追溯性
- 不要在采集阶段过早做重型理解
- 对 broker/account inputs，`orders`、`transactions`、position snapshots 应先进入 static archive / truth layer，再由下游 journal 和 report workflow 消费
- `data update` 可以调度某些 deterministic refresh，但它不应成为所有导入对象的命名中心
