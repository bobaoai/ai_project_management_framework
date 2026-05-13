---
title: Claim Type Taxonomy & Source Class Authority
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Expert Factory Maintainer
  - PM
---

# Claim Type Taxonomy & Source Class Authority

## 1. Purpose

本文定义 Digestion 层的两个跨 expert 共享分类体系：

- **Claim Type Taxonomy**：typed claim 的语义分类，两层结构（umbrella + industry subtype）
- **Source Class Authority**：source voice 的权威等级和分类

以及它们之间的约束关系：

- **Routing Matrix**：source_class × umbrella_claim_type 的合法组合

这三个东西组合在一起构成 Digestion 的 evidence permission 基础设施。所有 expert（entity、transmission、macro）共用同一套 umbrella 和 routing matrix。

本文不定义具体 expert 的 channel、artifact 或 skill projection。那些在各 expert design doc 中维护，引用本文的 umbrella 和 routing matrix。

## 2. Reader End-State

读完本文后，system builder 应该能判断：

- 任意一条 claim 的 claim_type 应该归入哪个 umbrella，挂哪个 industry subtype；
- 任意一个 source 的 source_class 是什么，authority 等级多高；
- 一个 source_class 能否 emit 一个 umbrella_claim_type（routing matrix lookup）；
- 新增 expert 时如何扩展 taxonomy（加 industry subtype）而不改 umbrella 和 matrix；
- 什么时候需要修改 umbrella 或 matrix（极少，需要本文 review）。

Silent violation:

```text
一条 claim 的 claim_type 写了 industry subtype 但没有标 umbrella，导致 routing matrix 无法 enforce。
```

## 3. Design Rationale

### 3.1 为什么 Claim Type 需要两层

单层方案的问题：

- **如果只有 umbrella（太粗）**：`supply_constraint` 不区分电力瓶颈和光学瓶颈，downstream synthesis 无法按 channel 筛选
- **如果只有 industry subtype（太细）**：每个 expert 各自定义 claim type，routing matrix 爆炸，跨 expert 分析无法对齐

两层方案：umbrella 管 epistemic permission（routing matrix 在这层运作），industry subtype 管 domain precision（各 expert 按需扩展）。

### 3.2 为什么 Source Class 需要 Authority 等级

同一条 claim 从不同 source_class 来，downstream synthesis 的 weight 不同。Authority 等级是 synthesis weight 的输入之一（不是唯一输入）。

Authority 等级和 routing matrix 是两条独立的线：
- **Authority** 决定 synthesis weight（这个 voice 说话的分量多大）
- **Routing matrix** 决定 epistemic permission（这个 voice 有没有资格说这类话）

高 authority 的 source 仍然可能被 routing matrix 阻止 emit 某些 claim_type。例如 Citrini（authority 高）不能 emit `delivery_evidence` at `publicly_observable`，因为确认"已交付"需要 operator 一手记录。

---

## 4. Claim Type Taxonomy

### 4.1 Umbrella Claim Types

8 个 umbrella，按 epistemic nature 分类，跨行业通用。

| Umbrella | 语义 | 回答的核心问题 |
|---|---|---|
| `supply_constraint` | 瓶颈识别 | 什么资源供应不足，约束在哪？ |
| `delivery_evidence` | 确认已交付/可用 | 这个东西真的上线/到位了吗？ |
| `technology_adoption` | 新技术达到部署规模 | 这个技术从实验室到产线走到哪了？ |
| `cost_dynamics` | 定价机制/经济性变化 | 价格/成本结构在怎么变？ |
| `lead_time_signal` | 供应链交期数据 | 从下单到交货要多久？趋势如何？ |
| `buildout_progress` | 建设/部署/采用进度 | 建到哪了？计划 vs 实际？ |
| `competitive_position` | 供应商份额/技术领先/护城河 | 谁在赢？格局在怎么变？ |
| `cannot_know_boundary` | 不可知边界 | 这个问题 matters，但当前 public source 无法回答 |

设计约束：

- umbrella 数量应保持在 10 以内。新增 umbrella 需要同步更新 routing matrix，属于 schema-level 变更
- `falsifier` 不是 claim_type，而是每条 claim 的必填字段 `falsifiers[]`

### 4.2 Industry Subtypes

每个 expert domain 在 umbrella 下定义自己的 subtype。Subtype 的命名遵循 `<umbrella>.<domain>.<specific>` 的逻辑，但在 claim 中只需填写 subtype 名称，umbrella 由 taxonomy lookup 确定。

#### AI Semiconductor Expert (51_1)

| Umbrella | Subtype | 说明 |
|---|---|---|
| supply_constraint | `foundry_capacity_constraint` | 代工产能瓶颈（utilization、slot availability） |
| supply_constraint | `hbm_allocation_constraint` | HBM 分配/产能 |
| supply_constraint | `equipment_lead_time_constraint` | 半导体设备交期约束 |
| supply_constraint | `wafer_supply_constraint` | 晶圆供应（含 advanced node） |
| delivery_evidence | `fab_capacity_online` | 新产能/新制程量产确认 |
| delivery_evidence | `packaging_line_qualified` | 封装产线认证通过 |
| delivery_evidence | `memory_volume_shipping` | 存储器大规模出货确认 |
| technology_adoption | `architecture_transition` | GPU → ASIC → custom silicon |
| technology_adoption | `packaging_generation` | CoWoS → SoIC → 下一代封装 |
| technology_adoption | `memory_generation` | HBM3 → HBM4 / DDR5 → DDR6 |
| cost_dynamics | `wafer_pricing_shift` | 晶圆代工价格变化 |
| cost_dynamics | `memory_pricing_cycle` | 存储器价格周期位置 |
| lead_time_signal | `foundry_slot_lead_time` | 代工排产交期 |
| lead_time_signal | `equipment_delivery_lead_time` | 光刻机、CVD 等设备交期 |
| buildout_progress | `fab_construction_milestone` | 晶圆厂建设里程碑 |
| buildout_progress | `packaging_expansion` | 封装产能扩张进度 |
| competitive_position | `foundry_share_shift` | 代工市场份额变化 |
| competitive_position | `architecture_design_win` | ASIC/custom silicon design win |

#### AI Data Center Expert (51_2)

| Umbrella | Subtype | 说明 |
|---|---|---|
| supply_constraint | `power_grid_constraint` | 电网互联/并网瓶颈 |
| supply_constraint | `optical_bandwidth_constraint` | 光互连带宽供需 |
| supply_constraint | `cooling_capacity_constraint` | 冷却系统容量瓶颈 |
| supply_constraint | `construction_labor_constraint` | 施工劳动力/技术工人短缺 |
| supply_constraint | `gas_supply_constraint` | 天然气供应瓶颈（上游分子供给） |
| delivery_evidence | `power_mw_online` | 电力容量确认通电可用 |
| delivery_evidence | `construction_complete` | 数据中心建筑完工 |
| delivery_evidence | `fiber_lit` | 光纤点亮/互联生效 |
| technology_adoption | `cooling_technology` | air → D2C liquid → immersion |
| technology_adoption | `co_packaged_optics` | co-packaged optics 部署 |
| technology_adoption | `modular_construction` | 模块化/预制化 DC 建设 |
| cost_dynamics | `power_pricing_shift` | 电力价格/PPA 定价变化 |
| cost_dynamics | `construction_cost_change` | DC 建设成本变化 |
| cost_dynamics | `equipment_premium_signal` | 设备供应商 lead time 导致的溢价（Tier2/3 接单） |
| cost_dynamics | `gas_pricing_shift` | 天然气价格结构性变化 |
| lead_time_signal | `turbine_delivery_lead_time` | 燃气轮机交期 |
| lead_time_signal | `ups_factory_slot_lead_time` | UPS 工厂排产交期 |
| lead_time_signal | `interconnection_queue_wait` | utility interconnection queue 等待时间 |
| buildout_progress | `site_permit_approved` | 站点许可审批 |
| buildout_progress | `building_phase_complete` | 单栋建筑阶段完工 |
| buildout_progress | `geographic_expansion` | 新站点/新区域扩张 |
| competitive_position | `vendor_concentration_change` | 供应商集中度变化 |
| competitive_position | `operator_market_share` | DC 运营商份额 |

#### AI Application Expert (51_3)

| Umbrella | Subtype | 说明 |
|---|---|---|
| supply_constraint | `cloud_capacity_constraint` | 云计算/inference 容量瓶颈 |
| supply_constraint | `inference_cost_constraint` | inference 成本阻碍 adoption |
| delivery_evidence | `product_ga_release` | AI 产品正式发布 |
| delivery_evidence | `api_publicly_available` | API 公开可用 |
| technology_adoption | `enterprise_workflow_integration` | 企业 workflow 深度集成 |
| technology_adoption | `vertical_ai_penetration` | AI 改造垂直行业（drug discovery、autonomous、marketing） |
| technology_adoption | `agentic_architecture` | agentic AI 架构部署 |
| cost_dynamics | `inference_unit_economics` | inference 单位经济性（cost per token/query） |
| cost_dynamics | `seat_pricing_power` | SaaS 提价能力 |
| lead_time_signal | — | 通常不适用于 application layer |
| buildout_progress | `adoption_stage_progression` | pilot → production → scaled revenue |
| buildout_progress | `monetization_milestone` | AI 收入里程碑（disclosed ARR、usage metric） |
| competitive_position | `platform_market_share` | AI platform 份额 |
| competitive_position | `workflow_lock_in_depth` | workflow 锁定深度 |

### 4.3 扩展规则

**新增 industry subtype（常规操作）：**
- 在对应 expert design doc 中定义
- 必须归入现有 umbrella
- 不需要修改本文
- 不需要修改 routing matrix

**新增 umbrella（schema-level 变更）：**
- 必须修改本文
- 必须同步更新 routing matrix（§6）
- 需要 review：确认现有 umbrella 无法覆盖
- 预期频率：极低（年级别）

**新增 expert domain：**
- 在新 expert design doc 中定义该 domain 的 subtype 表
- 引用本文的 umbrella 和 routing matrix
- 不需要修改本文（除非需要新 umbrella）

---

## 5. Source Class Authority

### 5.1 Source Class 定义

5 个 source_class，按 voice authority 从高到低排列。

| source_class | Authority | 定义 | 典型来源 |
|---|---|---|---|
| `regulatory_permit_record` | 最高 | 政府/监管机构一手记录，不经主观解读 | FERC filing, utility interconnection record, building permit, EPA permit, export control regulation, FOMC statement |
| `company_primary_disclosure` | 高 | 公司一手披露，受 SEC/法律约束 | earnings call transcript, 10-K/10-Q, investor day presentation, management guidance, operator press release with specific data |
| `specialized_infrastructure_research` | 高 | 原创 field research，有 investigative access 和专有分析框架 | Citrini Research, SemiAnalysis/Dylan Patel。区别于 sell-side：有 field access（drone、实地考察）、从一手数据（permit、delivery schedule）自建模型 |
| `industry_data_surface` | 中 | 第三方聚合数据，有延迟和不完整性 | foundry utilization tracker, utility interconnection queue database, equipment lead time survey, fiber capacity report, app store data |
| `sell_side_practitioner_analysis` | 中低 | 卖方/策略师基于公开信息的解读，无 field access | TMT Breakout, BofA optical TAM report, sell-side thematic note, enterprise survey report |

### 5.2 Authority 与 Permission Level 的关系

Authority 等级影响 synthesis weight，但 claim 的 `permission_level` 由 source_class + claim_type 的组合决定：

| permission_level | 含义 | 谁能达到 |
|---|---|---|
| `publicly_observable` | source 直接报告的事实 | `regulatory_permit_record`, `company_primary_disclosure`, `industry_data_surface`（其发布的数据本身） |
| `proxy_inferable` | source 未直接报告，但有限 proxy 支持 directional read | `specialized_infrastructure_research`, `sell_side_practitioner_analysis`；以及 `company_primary_disclosure` 的推断性判断 |
| `not_knowable_from_public_data` | 问题 matters，但当前 public source 无法回答 | 所有 source_class 均可 emit（作为 `cannot_know_boundary`） |

关键约束：`specialized_infrastructure_research` 即使 authority 为高，其 permission_level 上限仍是 `proxy_inferable`。除非它引用了 primary disclosure 原文（此时 claim 应标注双重 source_class）。

### 5.3 跨行业适用性

本节定义的 5 个 source_class 设计为跨行业通用。但不同行业的同一 source_class 对应不同的具体 source。例如：

| source_class | AI Industry (51) | Fed/Macro (52) |
|---|---|---|
| `regulatory_permit_record` | FERC filing, building permit | FOMC statement, Fed minutes |
| `company_primary_disclosure` | NVDA earnings, utility filing | — (Fed 不是 company) |
| `specialized_infrastructure_research` | Citrini, SemiAnalysis | — |
| `industry_data_surface` | foundry utilization tracker | FRED data, Treasury auction |
| `sell_side_practitioner_analysis` | TMT Breakout, BofA | Joseph Wang, Sahm, Tooze |

Fed/Macro domain 可能需要额外的 source_class（如 `academic_framework`, `buy_side_narrative`）。届时在本文增加，同步更新 routing matrix。

### 5.4 扩展规则

**新增 source_class（schema-level 变更）：**
- 必须修改本文
- 必须同步更新 routing matrix
- 需要 review：确认现有 source_class 无法覆盖
- 同时定义 authority 等级和 permission_level 约束

---

## 6. Routing Matrix

### 6.1 Matrix 定义

Routing matrix 控制哪个 source_class 可以 emit 哪个 umbrella claim_type。所有 expert 共用同一份 matrix。

```
                              supply   delivery  technology  cost      lead_time  buildout  competitive  cannot_know
                              constr.  evidence  adoption    dynamics  signal     progress  position     boundary
regulatory_permit_record        ✅        ✅        ·          ·         ✅          ✅         ·            ✅
company_primary_disclosure      ✅        ✅        ✅          ✅         ✅          ✅         ✅            ✅
specialized_infra_research      ✅        ⚠️        ✅          ✅         ✅          ✅         ✅            ✅
industry_data_surface           ✅        ·         ·          ✅         ✅          ✅         ·            ✅
sell_side_practitioner          ·         ·         ✅          ✅         ·          ·         ✅            ✅
```

图例：
- ✅ = 允许 emit
- ⚠️ = 允许 emit 但 permission_level 上限 `proxy_inferable`（不能达到 `publicly_observable`）
- · = 不允许 emit

### 6.2 Matrix 解读

**`regulatory_permit_record`** — 可以确认事实（supply_constraint, delivery_evidence, buildout_progress），可以提供交期数据（lead_time_signal from queue records），但不做技术判断或竞争分析。

**`company_primary_disclosure`** — 最宽的 emit 权限。公司自己说的，涵盖所有 claim type。但 single-company disclosure 不能直接概括为 industry-wide conclusion。

**`specialized_infrastructure_research`** — 几乎全开，但 `delivery_evidence` 带 ⚠️。Citrini 可以说"看到 turbine 已安装"（proxy_inferable），但"已通电可用"需要 operator 确认。

**`industry_data_surface`** — 只能报告数据事实（constraint, cost, lead_time, buildout progress）。不能做技术判断或竞争分析。

**`sell_side_practitioner_analysis`** — 最窄。只能做技术趋势判断（technology_adoption）、竞争格局分析（competitive_position）、成本分析（cost_dynamics）。不能报告 supply constraint（缺 field access 验证）、delivery evidence（缺一手数据）、lead time（缺供应链数据）、buildout progress（缺 permit/site 数据）。

### 6.3 Firewall Enforcement

当前阶段 routing matrix 在 skill/prompt 层 enforce（angel card 写作时 reviewer 检查）。

未来可提升为 Python 硬编码（参考 `video_parser/macro_fed_kb/extractor/routing.py`），实现 claim 提取时的自动化校验。

### 6.4 Matrix 变更规则

修改 routing matrix 属于 schema-level 变更：
- 需要同步更新本文
- 需要 review 确认不会 break 现有 expert 的 claim 产出
- 新增 ✅ 相对安全（放宽权限）
- 移除 ✅ 或新增 · 需要检查现有 claims 是否会被 invalidate

---

## 7. Claim Schema 要求

每条 typed claim 必须包含：

```yaml
claim_id: <stable id>
source_card_id: <parent source card>
expert_id: <owning expert>
channel_id: <expert-defined channel>
source_class: <one of §5.1>
umbrella_claim_type: <one of §4.1>
claim_subtype: <industry subtype from §4.2, optional if umbrella sufficient>
permission_level: publicly_observable | proxy_inferable | not_knowable_from_public_data
claim: <one-line assertion>
elaboration: <mechanism / boundary / counterfactual, 2-4 sentences>
confidence: low | medium | high
confidence_reason: <why this confidence level>
time_validity: event_specific | cycle_specific | structural
affected_tickers: []
falsifiers: []              # 必填，至少 1 条
source_span_refs: []
```

与之前 flat YAML 的主要变化：
- `confidence` 从 cardinal（0.70）改为 ordinal（low / medium / high）
- 新增 `umbrella_claim_type` 和 `claim_subtype` 双层分类
- `falsifiers` 从独立 claim_type 改为每条 claim 的必填字段
- `transmission_step` 移到 source card 层面（claim 不重复）

---

## 8. 与其他 Design Docs 的关系

| Doc | 关系 |
|---|---|
| `digestion_00_overview.md` | 本文是 overview 中 "evidence permission" 层的 canonical 定义 |
| `digestion_30_expert_factory.md` | Factory 产出的 expert contract 中 `source_classes[]` 和 `claim_types[]` 引用本文 |
| `digestion_51_ai_industry_expert.md` | Umbrella expert 引用本文的 routing matrix 做 family-level enforcement |
| `digestion_51_1_*.md` / `51_2` / `51_3` | Child experts 引用本文的 umbrella，定义各自的 industry subtype |
| `digestion_50_transmission_expert.md` | Transmission expert 抽象基类可引用本文的 umbrella 作为最小要求 |
| `data/runtime/schemas/` | 未来可生成 JSON Schema 做 runtime validation |

---

## 9. Migration Path

当前 51 family design docs 中的 claim type 和 source class 定义需要迁移到本文：

1. 各 child expert doc 中的 `claim_type` 列表 → 本文 §4.2 industry subtype（已完成初始映射）
2. 各 child expert doc 中的 `source_class` 定义 → 本文 §5.1 统一定义
3. 各 child expert doc 中的 firewall rules → 本文 §6 routing matrix + expert doc 中保留 subtype-level 补充约束
4. 各 child expert doc 引用本文，不再内联定义 umbrella 和 routing matrix

迁移原则：expert doc 保留 subtype 定义和 subtype-level 的补充约束（如 "Citrini 不能单独支持 single site = industry-wide conclusion"）。Umbrella 和 routing matrix 统一在本文维护。
