# Contract Audit Rebuild Tracker

追踪 designDoc + skill system 向三 surface 模型迁移的进度。

## Prerequisites

| # | 条件 | 状态 | 阻塞 | 说明 |
|---|---|---|---|---|
| P1 | `shared_contracts.py` | 未开始 | **是** | 跨模块共享对象唯一来源。没有它 60 个 registry 各自重复定义 upstream Design ref |
| P2 | 第 3 个 dogfood（形态不同的模块） | 未开始 | **是** | 目前只验证了数据流水线型和元/基础设施型。需要 skill-heavy 型 |
| P3 | `the_design_doc_management.md` 同步 | **done** | **是** | §2.1 registry_path, §5.4.1 四 surface ownership, §5.4.2 Check Registry Alignment |
| P4 | 代码永久位置 | 未开始 | **是** | `designDoc/temp/smoke/` 是临时试验场。60 个模块的 registry 不能在 temp 下 |
| P5 | `manifest.py` 跨模块依赖图 | 未开始 | 否 | 回答 "改了 shared object 哪些模块需要重新审计" |
| P6 | Finding classification 实战验证 | 未开始 | 否 | 分类机制设计了但没跑过真实 round |
| P7 | Design doc 写作 guidelines | 未开始 | 否 | 模块作者需要知道三 surface 模型下 design doc 写什么、不写什么 |

## Done

| 模块 | Registry | 审计 | 说明 |
|---|---|---|---|
| `research_technical` | `modules/research_technical/registry.py` | L1+L2 pass, L3 3-round | 数据流水线型。smoke dogfood 模块 |
| `the_contract_audit` | `modules/the_contract_audit/registry.py` | L1+L2 pass | 元/基础设施型。审计系统自身 |

## Module Inventory

分类标准：
- **需要 registry**：定义或拥有 8 种 class 实例（Tool, Agent, Workflow 等）的模块
- **skip**：概述/哲学文档，不拥有 typed objects
- **needs_doc**：skill 存在但无 design doc

### T0 System (`the_*`)

| Design Doc | 需要 registry | Skills | 说明 |
|---|---|---|---|
| `the_charter` | skip | — | 宪法层，不拥有 typed objects |
| `the_task_routing` | 待定 | `routing-task-mode-router`, `routing-current-macro-priority-router` | 拥有 routing 逻辑，可能有 Tool |
| `the_artifact_graph` | 待定 | — | 定义 artifact 准入规则 |
| `the_timestamp_semantic` | skip | — | 语义约定，不拥有 typed objects |
| `the_design_doc_management` | 待定 | — | 拥有 review gate 流程 |
| `the_tradecli_code_management` | 待定 | `engineering-project-review` | 拥有 code admission 流程 |
| `the_external_agent_management` | 待定 | `support-external-agent-builder`, `writer-handoff` | 拥有 external writer execution |
| `the_contract_audit` | **done** | `agent-the-contract-audit` | — |

### Ingestion

| Design Doc | 需要 registry | Skills | 说明 |
|---|---|---|---|
| `ingestion_00_overview` | skip | — | 概述 |
| `ingestion_10_source_connector_contract` | 是 | `ingestion-source-connector-designer`, `ingestion-source-family-operator` | connector 定义 |
| `ingestion_20_archive_message_contract` | 是 | `ingestion-agentmail-inbox-triage`, `ingestion-research-archive-operator` | inbox + archive |
| `ingestion_30_ai_read_content_contract` | 是 | `ingestion-image-review-reader` | AI 阅读 |
| `ingestion_33_company_fundamentals_data_architecture` | 待定 | — | 数据架构 |
| `ingestion_40_error_and_blocker_contract` | 待定 | — | 错误处理 |
| `ingestion_50_source_family_playbook` | skip | — | playbook 参考 |
| `ingestion_6*` (domain specific) | 待定 | — | fed, company, newsletter, market data |

### Digestion

| Design Doc | 需要 registry | Skills | 说明 |
|---|---|---|---|
| `digestion_00_overview` | skip | — | 概述 |
| `digestion_10_structure_contract` | 是 | — | 结构消化 |
| `digestion_11_report_package_contract` | 是 | — | report package |
| `digestion_12_private_company_report_package_contract` | 是 | — | 私有公司 report package |
| `digestion_20_independent_researcher` | 是 | `digestion-independent-researcher` | 独立研究员 |
| `digestion_30_expert_factory` | 是 | `digestion-expert-factory` | 专家工厂 |
| `digestion_31_expert_runtime` | 是 | — | 专家运行时 |
| `digestion_35_claim_taxonomy_and_source_authority` | 待定 | — | claim 分类学 |
| `digestion_4*` (entity/company/crypto experts) | 是 | `digestion-company-expert` | 各类专家模块 |
| `digestion_5*` (transmission/industry experts) | 是 | — | 传导/行业专家 |

### Research

| Design Doc | 需要 registry | Skills | 说明 |
|---|---|---|---|
| `research_00_overview` | skip | — | 概述 |
| `research_00_writer_package_contract` | 是 | `writer-handoff` | writer package |
| `research_00_report_reviewer_pattern` | 是 | `research-evidence-reviewer` | reviewer 模式 |
| `research_00_report_polish_framework` | skip | — | framework 参考 |
| `research_00_information_gathering_guideline` | skip | — | guideline |
| `research_10_thematic_workflow` | 是 | `research-theme-report-owner`, `research-theme-discovery-scanner`, `research-theme-bootstrapper`, `research-theme-content-maintainer`, `research-theme-priority-updater`, `research-theme-report-debater`, `research-theme-report-reviewer`, `research-theme-staleness-sweeper`, `research-theme-knowledge-and-package-curator` | **最大模块族** — 9 个 skill |
| `research_11_theme_report_canonical_structure` | skip | — | report 结构参考 |
| `research_20_technical_*` | **done** | `agent-research-technical-analysis`, `writer-asset-technical` | smoke dogfood |
| `research_30_company_report_instruction` | 是 | `research-company-financial-analysis` | 公司报告 |
| `research_31_private_company_report_instruction` | 是 | — | 私有公司报告 |
| `research_40_thesis_note_schema` | 是 | `research-thesis-drafter`, `research-thesis-adversary`, `research-thesis-verifier` | thesis 系统 |
| `research_50_thesis_and_theme_agent_cluster` | 是 | — | thesis+theme 协作 |

### Material

| Design Doc | 需要 registry | Skills | 说明 |
|---|---|---|---|
| `material_00_overview` | skip | — | 概述 |
| `material_10_raw_data_contract` | 待定 | — | 原始数据 |
| `material_20_operating_cycle_artifact_contract` | 待定 | — | 操作周期 artifact |
| `material_30_source_card_contract` | 待定 | — | source card |
| `material_32_typed_claim_contract` | 待定 | — | typed claim |
| `material_35_expert_artifact_contract` | 待定 | — | expert artifact |
| `material_40_evidence_contract` | 待定 | — | evidence |
| `material_50_thesis_contract` | 待定 | — | thesis |
| `material_60_theme_contract` | 待定 | — | theme |
| `material_70_technical_report_contract` | 是 | — | technical report（smoke 已覆盖） |
| `material_80_scenario_contract` | 待定 | — | scenario |
| `material_90_support_surfaces` | skip | — | support 参考 |

### Operation / Analysis / Other

| Design Doc | 需要 registry | Skills | 说明 |
|---|---|---|---|
| `operation_00_operating_framework_governance` | 待定 | `operation-portfolio-decision` | 操作框架 |
| `operation_10_interpretation_framework_governance` | 待定 | `digestion-interpretation-metaskill` | 解读框架 |
| `analysis_platform_and_pm_workspace` | 待定 | `pm-cursor-workspace-guide` | PM workspace |
| `expertise_00_overview` | skip | — | 概述 |
| `expertise_20_application_contract` | 待定 | — | expertise 应用 |
| `expertise_60_prediction_framework_contract` | 待定 | — | 预测框架 |
| `knowledge_base_and_memory_system` | 待定 | — | KB |
| `market_data_architecture` | 待定 | — | 市场数据 |
| `price_data_architecture` | 待定 | — | 价格数据 |

### Skills without design doc (`needs_doc`)

| Skill | 候选 Design Doc | 说明 |
|---|---|---|
| `research-current-market-reporter` | 无 | market recap |
| `research-single-stock-analysis` | 无 | 单股分析 |
| `research-external-learning` | 无 | 外部学习 |
| `support-compaction-handoff` | 无 | compaction |
| `support-deep-research-survey` | 无 | deep research |

## Migration Phases

### Phase 0: Prerequisites (当前)
- [ ] P1: 建 `shared_contracts.py`
- [ ] P4: 确定永久代码位置（从 `temp/smoke/` 搬出）
- [ ] P3: 更新 `the_design_doc_management.md`

### Phase 1: Dogfood 扩展
- [ ] P2: 选 1 个 skill-heavy 模块做第 3 个 dogfood（候选：`research_10_thematic_workflow`）
- [ ] P6: Finding classification 实战验证

### Phase 2: Pilot（5-8 个模块）
- [ ] 每个 domain family 至少 1 个模块有 registry
- [ ] ingestion: `ingestion_20`
- [ ] digestion: `digestion_20`
- [ ] research: `research_10_thematic_workflow`
- [ ] material: `material_70`（已被 smoke 覆盖）
- [ ] operation: `operation_00`

### Phase 3: Scale
- [ ] P5: 建 `manifest.py`
- [ ] 全部 "需要 registry" 的模块
- [ ] 全部 `needs_doc` 的 skill 补 design doc
