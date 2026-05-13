---
title: AI Data Center Expert
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Independent Research Orchestrator
---

# AI Data Center Expert

## 1. Purpose

`AI Data Center Expert` 是 AI Industry Expert Family 的 child expert，负责 digest 数据中心物理基础设施侧的 source material：电力供应、冷却技术、光互连/网络、机房建设和站点扩展。

数据中心不等于半导体。半导体决定计算密度，数据中心决定计算密度能否被物理世界承载。两者的 source surface、bottleneck 逻辑和 timeline 完全不同。

本 expert 覆盖 AI Transmission Chain 的 **Step 4**（Power & Physical Infrastructure），以及 Step 5 Capacity Available 的 delivery 视角。

## 2. Reader End-State

读完本 expert 产出后，PM 应该能说清：

- 当前 DC 建设 pipeline 处于什么阶段，evidence 来自哪里；
- power procurement / interconnection queue 的实际约束和 lead time；
- optical interconnect bandwidth 是否匹配 GPU cluster scale-out 需求；
- cooling 技术演进（air → liquid → immersion）的 adoption 和 constraint；
- 哪些判断来自 utility/operator primary disclosure，哪些来自 analyst inference；
- 什么 signal 出现会改变当前 infrastructure read（permit acceleration、efficiency jump、demand below projection）。

Silent violation:

```text
DC buildout 听起来 bullish，但读者分不清 "有 X MW 在 queue" 和 "有 X MW 已通电可用"。
```

## 3. Source Classes

> **Canonical references**:
> - Source class 定义和 authority 等级：[`digestion_35_claim_taxonomy_and_source_authority.md`](digestion_35_claim_taxonomy_and_source_authority.md) §5
> - Routing matrix（source_class × umbrella_claim_type）：同文 §6
> - Machine-readable：`data/runtime/schemas/claim_type_taxonomy.yaml`
> - 本 expert 的 subtypes 和 firewall supplements：`data/digestion/expert_subsystems/ai_datacenter_expert/expert_contract.yaml`
>
> 以下保留 domain-specific 的 allowed/blocked support 细节，作为 expert_contract.yaml 中 `firewall_supplements` 的 human-readable 展开。
> source_class 名称已统一为 taxonomy 中的 canonical 名称（`specialized_datacenter_research` → `specialized_infrastructure_research`）。

### 3.1 `specialized_infrastructure_research`

典型来源：Citrini（Let There Be Light、Power Struggle、Stargate Field Trip）

Allowed claim support:

- DC buildout pipeline 分析（引用 public permit/queue data）；
- power constraint identification and timeline analysis；
- optical/networking capacity mapping；
- cooling technology comparison and adoption trajectory；
- site selection and geographic distribution analysis。

Blocked support:

- utility internal capacity without operator data；
- power delivery confirmation without primary source；
- construction completion without permit/operator data；
- exact MW online without utility/operator disclosure。

Confidence cap: permission_level 上限 `proxy_inferable`（除非引用 primary disclosure）。

### 3.2 `company_primary_disclosure`

典型来源：utility filings (VST, CEG, GEV)、DC REIT earnings (EQIX, DLR)、hyperscaler capacity disclosures

Allowed claim support:

- power contract MW and price → `publicly_observable`；
- interconnection agreements disclosed in filings；
- construction timeline when operator announces；
- cooling/efficiency metrics when disclosed；
- capacity online when operator confirms。

Blocked support:

- single operator capacity as industry-wide conclusion；
- announced timeline as confirmed delivery；
- management optimism as execution certainty。

### 3.3 `industry_data_surface`

典型来源：utility interconnection queue databases、building permit trackers、power pricing data、fiber capacity reports

Allowed claim support:

- queue position and waitlist data（as `proxy_inferable`）；
- permit approval rates and timelines；
- power pricing by region；
- fiber/optical capacity metrics；
- construction activity indicators。

Blocked support:

- company-specific revenue unless from filings；
- demand certainty from capacity planning data alone；
- individual site delivery from aggregate queue data。

### 3.4 `curated_practitioner_datacenter_analysis`

典型来源：TMT Breakout DC/power observations、BofA optical TAM reports (如 GLW sizing)

Allowed claim support:

- cross-operator buildout pattern signals；
- optical TAM and bottleneck identification（引用 framework + data）；
- sector rotation signal relevant to DC infra names；
- technology adoption catalysts。

Blocked support:

- MW capacity claims without utility/operator data；
- construction timeline without permit/filing source；
- demand proof from stock performance。

## 4. Channel Registry

### 4.1 `power_and_utility`

- **定义**: 数据中心电力供应、utility 协议、interconnection queue、power cost
- **transmission_step**: Step 4a
- **native_horizon**: 4–12 quarters（power procurement lead time）
- **observables**: utility interconnection queue depth、power contract MW、price per kWh、generation buildout、nuclear/gas/renewable mix、grid upgrade timeline
- **typical_misuse**: queue depth = permanent bottleneck（忽略 queue processing rate and buildout）
- **falsifiers**: accelerated interconnection、behind-the-meter solutions、demand reduction、efficiency gains reducing power per GPU

### 4.2 `optical_and_networking`

- **定义**: 光互连、网络 fabric、scale-out bandwidth — GPU cluster 之间的连接约束
- **transmission_step**: Step 4b
- **native_horizon**: 2–6 quarters（optical supply chain）
- **observables**: transceiver shipment volume、fiber deployment、switch bandwidth、co-packaged optics adoption、InfiniBand vs Ethernet mix
- **typical_misuse**: TAM 增长 narrative = 所有光学公司受益（忽略 vendor concentration and margin pressure）
- **falsifiers**: alternative interconnect technology、bandwidth sufficient for current scale、vendor diversification reducing ASP

### 4.3 `dc_construction_and_cooling`

- **定义**: 机房物理建设、site selection、冷却技术、mechanical/electrical infrastructure
- **transmission_step**: Step 4c
- **native_horizon**: 4–8 quarters（construction cycle）
- **observables**: permit approvals、construction starts、facility square footage、PUE trends、liquid cooling adoption rate、immersion cooling deployments
- **typical_misuse**: 公告的建设计划 = 已完成容量；air cooling constraint = all DC delayed
- **falsifiers**: modular construction reducing timeline、liquid cooling removing thermal bottleneck、demand below projected capacity need

## 5. Typed Claim Pattern

```yaml
object_type: AIDatacenterTypedClaim
claim_id:
source_card_id:
expert_id: ai_datacenter_expert
channel_id: power_and_utility | optical_and_networking | dc_construction_and_cooling
source_class:
claim_type:
permission_level: publicly_observable | proxy_inferable | not_knowable_from_public_data
claim:
elaboration:
time_validity:
confidence:
confidence_cap_reason:
transmission_step: 4
affected_tickers: []
falsifiers: []
source_span_refs: []
downstream_allowed_use: []
downstream_blocked_use: []
```

Claim type families:

- `power_constraint_signal` — 电力供应 bottleneck identification
- `power_delivery_evidence` — 电力实际可用 confirmation
- `interconnection_queue_state` — utility queue position and processing
- `optical_capacity_signal` — 光互连 bandwidth supply/demand
- `optical_technology_shift` — co-packaged optics、new transceiver generation
- `construction_progress` — DC 建设 timeline and delivery
- `cooling_technology_adoption` — liquid/immersion cooling deployment
- `capacity_online` — 确认可用的 MW/rack 容量
- `geographic_distribution` — site selection and regional concentration
- `cost_structure_change` — power/construction/cooling cost shifts
- `cannot_know_boundary`
- `falsifier`

## 6. Source Card Pattern

```yaml
object_type: AIDatacenterSourceCard
expert_id: ai_datacenter_expert
expert_version: v0
source_ref: data/research/messages/<research_id>/read_content.md
source_class:
source_authority: utility_operator | dc_operator | industry_data_provider | specialized_researcher | curated_practitioner
time_semantics:
  observation_period:
  published_at:
  data_freshness:
channel_relevance: []
transmission_steps_covered: []
key_observations: []
infrastructure_claims: []
missing_context: []
affected_tickers: []
blocked_uses: []
source_span_refs: []
```

## 7. Domain Artifacts

### 7.1 DC Infrastructure State Map

回答 "AI 数据中心物理基础设施当前状态和约束在哪"。

Sections:

1. **Power Supply State** — available MW, contracted MW, queue pipeline, regional distribution
2. **Optical/Networking State** — transceiver supply, bandwidth adequacy, technology transition
3. **Construction Pipeline** — permits, starts, completions, geographic spread
4. **Cooling State** — liquid cooling adoption, PUE trends, thermal constraint assessment
5. **Key Bottlenecks** — ranked by impact on capacity delivery
6. **Timeline Assessment** — when does constraint ease, evidence tier for each
7. **Falsifier Watch** — signals that would change the infrastructure read

### 7.2 Power Pipeline Dashboard

```yaml
power_data_points:
  - operator:
    region:
    contracted_mw:
    online_mw:
    queue_position:
    estimated_delivery:
    source_ref:
    permission_level:
regional_summary:
  - region:
    total_queue_mw:
    processing_rate:
    constraint_type:
```

## 8. Firewall Rules

```text
specialized_datacenter_research CAN support:
  - power_constraint_signal
  - optical_capacity_signal
  - optical_technology_shift
  - construction_progress (when citing permit/public data)
  - cooling_technology_adoption
  - geographic_distribution
  - cost_structure_change

specialized_datacenter_research CANNOT support:
  - power_delivery_evidence at publicly_observable (needs utility/operator)
  - capacity_online at publicly_observable (needs operator confirmation)
  - exact MW numbers without data source

company_primary_disclosure CAN support:
  - power_delivery_evidence (operator confirms capacity online)
  - capacity_online (operator/utility confirms)
  - construction_progress (operator announces timeline)
  - interconnection_queue_state (utility filing data)
  - optical_capacity_signal (if vendor discloses shipment data)

company_primary_disclosure CANNOT support:
  - industry-wide DC capacity from single operator
  - future delivery certainty from current construction start
  - regional conclusion from one site

industry_data_surface CAN support:
  - interconnection_queue_state
  - geographic_distribution
  - cost_structure_change
  - construction_progress (aggregate permit data)

industry_data_surface CANNOT support:
  - operator-specific delivery timeline
  - capacity_online without operator confirmation

curated_practitioner_datacenter_analysis CAN support:
  - optical_technology_shift (cross-company pattern)
  - cooling_technology_adoption (market trend)
  - geographic_distribution (cross-operator pattern)

curated_practitioner_datacenter_analysis CANNOT support:
  - power MW claims without utility data
  - construction timeline without permit source
  - capacity_online claims
```

## 9. Validation Gates

AI Data Center Expert output is invalid if:

- queue pipeline 被等同于 permanent bottleneck（忽略 processing rate 和 alternative paths）；
- announced construction 被标为 `capacity_online`；
- 单一 operator disclosure 被概括为 industry-wide DC state；
- optical TAM growth 被等同于所有 optical vendor 受益；
- market price momentum 被当作 power/capacity constraint proof；
- cooling technology announcement 被当作 deployment at scale；
- "power is tight" 无具体 region、MW gap、timeline evidence；
- 产出 portfolio action 或 semiconductor supply claims（那是 semiconductor expert 领域）；
- 混淆 "contracted MW" 和 "available MW"。

## 10. Dogfood Source Shape

### Citrini as Primary Source

| Source type | Source class | What it supports | What it cannot support alone |
|---|---|---|---|
| Citrini "Let There Be Light" (optical) | `specialized_datacenter_research` | optical capacity mapping, technology transition | exact shipment numbers without vendor filing |
| Citrini "Power Struggle: Natural Gas" | `specialized_datacenter_research` | power constraint identification, energy source analysis | utility-specific delivery timeline |
| Citrini "Stargate" field trip | `specialized_datacenter_research` | DC buildout pattern, geographic strategy | single site ≠ industry buildout state |

### TMT Breakout Observations

| Source type | Source class | What it supports | What it cannot support alone |
|---|---|---|---|
| BofA GLW optical TAM sizing | `curated_practitioner_datacenter_analysis` | optical TAM framework, scale-out sizing | vendor-specific revenue, exact capacity |
| TMTB DC/power/optical sector signals | `curated_practitioner_datacenter_analysis` | cross-company pattern, rotation signal | MW capacity claims, construction timeline |

### Ticker Coverage

Primary affected tickers:

- **Power/Utility**: VST, CEG, GEV, NRG
- **Optical**: GLW, ALAB, COHR, LITE, CIEN
- **Networking**: ANET, AVGO (networking division)
- **DC REIT/Operator**: EQIX, DLR, AMT
- **Cooling**: VRT, GNRC

## 11. Adjacent Docs

| Doc | Relationship |
|---|---|
| `digestion_51_ai_industry_expert.md` | Family umbrella / orchestrator |
| `digestion_51_1_ai_semiconductor_expert.md` | Sibling: AI Semiconductor child expert |
| `digestion_51_3_ai_application_expert.md` | Sibling: AI Application child expert |
| `digestion_41_2_listed_company_expert.md` | Handoff target when DC signal feeds single-ticker analysis |
| `digestion_30_expert_factory.md` | Expert lifecycle and admission |
| `digestion_10_structure_contract.md` | Object schema |
