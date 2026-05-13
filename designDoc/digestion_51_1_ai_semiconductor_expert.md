---
title: AI Semiconductor Expert
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Independent Research Orchestrator
---

# AI Semiconductor Expert

## 1. Purpose

`AI Semiconductor Expert` 是 AI Industry Expert Family 的 child expert，负责 digest AI 半导体供应链侧的 source material：chip design and procurement、foundry capacity and utilization、advanced packaging (CoWoS/HBM)、memory cycle (HBM/DRAM/NAND)、chip architecture transitions (GPU/ASIC/custom silicon)、equipment and EDA。

数据中心物理基础设施（电力、冷却、光互连、网络、机房建设）由 sibling `ai_datacenter_expert` 负责。

本 expert 覆盖 AI Transmission Chain 的 **Steps 2–3**（Chip Order → Foundry & Packaging），以及 chip architecture transitions 作为 cross-cutting concern。

## 2. Reader End-State

读完本 expert 产出后，PM 应该能说清：

- semiconductor supply chain 的当前 bottleneck 在哪里（foundry capacity、advanced packaging CoWoS、HBM allocation、leading-edge yield）；
- memory cycle（HBM/DRAM/NAND）处于什么阶段，pricing power 在哪里；
- chip architecture transition（GPU vs ASIC vs custom silicon）的实际进度 vs 叙事；
- equipment 和 EDA 层的 capacity constraint 和 lead time；
- 哪些判断来自 primary company disclosure（TSM、NVDA filing），哪些来自 specialized research inference（SemiAnalysis）；
- 什么 signal 出现会改变当前 semiconductor state read（capacity expansion、yield improvement、ASIC design win cancellation）。

Silent violation:

```text
Semis read 听起来 bullish，但读者不知道 "供应紧张" 的证据是 foundry utilization data 还是 newsletter 信念。
```

## 3. Source Classes

> **Canonical references**:
> - Source class 定义和 authority 等级：[`digestion_35_claim_taxonomy_and_source_authority.md`](digestion_35_claim_taxonomy_and_source_authority.md) §5
> - Routing matrix（source_class × umbrella_claim_type）：同文 §6
> - Machine-readable：`data/runtime/schemas/claim_type_taxonomy.yaml`
> - 本 expert 的 subtypes 和 firewall supplements：`data/digestion/expert_subsystems/ai_semiconductor_expert/expert_contract.yaml`
>
> 以下保留 domain-specific 的 allowed/blocked support 细节，作为 expert_contract.yaml 中 `firewall_supplements` 的 human-readable 展开。

### 3.1 `specialized_infrastructure_research`

典型来源：Citrini（AI infrastructure focused）、SemiAnalysis

Allowed claim support:

- capex cycle position analysis（引用 public data 的 spending trend）；
- semiconductor supply chain mapping（foundry、packaging、HBM capacity analysis）；
- power/DC bottleneck identification；
- chip architecture comparison and transition thesis；
- competitive dynamics analysis（引用公开 specs 和 benchmarks）。

Blocked support:

- undisclosed company commitments；
- demand certainty without primary-source confirmation；
- author conviction as evidence tier upgrade（"I believe X" ≠ `publicly_observable`）；
- precise market share without data source attribution。

Confidence cap: 即使分析质量高，permission_level 上限是 `proxy_inferable`（除非引用了 primary disclosure 原文）。

### 3.2 `company_primary_disclosure`

典型来源：hyperscaler earnings（MSFT, GOOG, AMZN, META capex guidance）、semis filings（NVDA, AMD, TSM, AVGO）

Allowed claim support:

- capex guidance 数字 → `publicly_observable`；
- revenue segment data directly relevant to AI infra；
- capacity plans and delivery timelines when disclosed；
- supply constraints acknowledged in filings/earnings。

Blocked support:

- promotional language as demand certainty；
- single-company capex as industry-wide structural proof（需要 cross-company）；
- management optimism as confirmed delivery。

### 3.3 `industry_data_surface`

典型来源：foundry utilization reports、HBM shipment trackers、power pricing data、DC construction databases

Allowed claim support:

- utilization and capacity metrics（as `proxy_inferable` unless directly from operator）；
- shipment / delivery volume estimates；
- pricing trends（wafer、HBM、power）；
- lead time data。

Blocked support:

- company-specific revenue unless sourced from filings；
- demand certainty from capacity data alone。

### 3.4 `curated_practitioner_industry_analysis`

典型来源：TMT Breakout 的 infrastructure observations

Allowed claim support:

- cross-company infra pattern signals（多家同时 breakout/breakdown）；
- sector rotation signal relevant to infra names；
- event catalysts mapping。

Blocked support:

- supply chain structural claims without foundry/company data；
- capacity numbers without data source；
- demand proof。

## 4. Channel Registry

### 4.1 `semiconductor_supply_chain`

- **定义**: chip design → foundry → advanced packaging → testing → delivery
- **transmission_step**: Steps 2–3
- **native_horizon**: 2–6 quarters（foundry lead time）
- **observables**: foundry utilization、CoWoS/advanced packaging slots、wafer starts、chip ASP、inventory channel、lead times、equipment orders
- **typical_misuse**: supply shortage narrative = durable pricing power（忽略 capacity ramp timeline）
- **falsifiers**: capacity expansion on schedule、inventory build visible、ASP decline、alternative architectures mature

### 4.2 `memory_cycle`

- **定义**: HBM / DRAM / NAND 周期位置、capacity allocation、pricing power
- **transmission_step**: Step 2–3（memory 是 AI chip 的关键组件）
- **native_horizon**: 2–4 quarters（memory pricing cycle）
- **observables**: HBM shipment volume and allocation、DRAM ASP trend、bit growth vs demand、inventory days、contract vs spot pricing gap、HBM vendor concentration (SK Hynix / Samsung / Micron)
- **typical_misuse**: HBM shortage = DRAM shortage（不同产品线有不同周期）；single quarter pricing = structural trend
- **falsifiers**: capacity ramp faster than demand、inventory build at customer level、alternative memory architecture、demand below projection

### 4.3 `chip_architecture_transition`

- **定义**: GPU / ASIC / custom silicon architecture shifts and their supply chain implications
- **transmission_step**: cross-cutting（影响 Steps 2–3）
- **native_horizon**: 4–8 quarters（design-to-production cycle）
- **observables**: new chip launches、benchmark data、customer adoption of alternative architectures、ASIC design wins、TCO comparison data、inference optimization
- **typical_misuse**: benchmark improvement = production readiness；single-customer ASIC = industry displacement；Jensen quote about TCO = proven moat
- **falsifiers**: ASIC programs cancelled、new architecture delayed、incumbent maintains ecosystem lock-in、customer actually migrating at scale

### 4.4 `equipment_and_eda`

- **定义**: semiconductor equipment and EDA tool chain — foundry capacity 的上游约束
- **transmission_step**: Step 2 upstream constraint
- **native_horizon**: 4–8 quarters（equipment delivery lead time）
- **observables**: equipment orders (ASML, AMAT, LRCX, KLA)、EDA license growth、advanced node tool availability、EUV/high-NA adoption
- **typical_misuse**: equipment order = capacity online（忽略 install + qualification cycle）
- **falsifiers**: order cancellation、tool delivery acceleration、yield improvement reducing need for additional capacity

## 5. Typed Claim Pattern

```yaml
object_type: AISemiTypedClaim
claim_id:
source_card_id:
expert_id: ai_semiconductor_expert
channel_id: semiconductor_supply_chain | memory_cycle | chip_architecture_transition | equipment_and_eda
source_class:
claim_type:
permission_level: publicly_observable | proxy_inferable | not_knowable_from_public_data
claim:
elaboration:
time_validity:
confidence:
confidence_cap_reason:
transmission_step: 2 | 3
affected_tickers: []
falsifiers: []
source_span_refs: []
downstream_allowed_use: []
downstream_blocked_use: []
```

Claim type families:

- `supply_constraint_signal` — foundry/packaging/HBM bottleneck identification
- `capacity_ramp_evidence` — expansion timeline and progress
- `utilization_state` — current foundry/packaging capacity usage
- `lead_time_signal` — delivery timeline evidence
- `memory_cycle_position` — HBM/DRAM/NAND cycle phase (expansion / peak / contraction)
- `memory_pricing_signal` — ASP direction and contract/spot gap
- `architecture_shift` — chip/platform transition evidence (GPU vs ASIC vs custom)
- `competitive_position_shift` — vendor market share change (NVDA vs ASIC, TSM vs Samsung, SK vs MU)
- `equipment_constraint` — tool availability and delivery timeline
- `cost_structure_change` — wafer/packaging cost shifts
- `semiconductor_leading_indicator` — forward-looking signal (orders, backlog, inventory)
- `cannot_know_boundary`
- `falsifier`

## 6. Source Card Pattern

```yaml
object_type: AISemiSourceCard
expert_id: ai_semiconductor_expert
expert_version: v0
source_ref: data/research/messages/<research_id>/read_content.md
source_class:
source_authority: primary_company | foundry_operator | industry_data_provider | specialized_researcher | curated_practitioner
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

### 7.1 Semiconductor Supply Chain Map

回答 "AI 半导体供应链当前状态和约束在哪"。

Sections:

1. **Foundry Utilization & Packaging** — advanced node utilization、CoWoS capacity、packaging lead time
2. **Memory State** — HBM allocation、DRAM cycle phase、pricing direction、inventory
3. **Architecture Transition** — GPU/ASIC/custom silicon progress vs narrative
4. **Equipment & Capacity Expansion** — tool orders、new capacity timeline、yield state
5. **Key Bottlenecks** — ranked by impact on chip delivery
6. **Competitive Dynamics** — vendor concentration, moat durability, displacement risk
7. **Falsifier Watch** — signals that would change the semiconductor read

### 7.2 Memory Cycle Dashboard

```yaml
memory_data_points:
  - segment: HBM | DRAM | NAND
    vendor:
    metric_type: shipment_volume | asp | inventory_days | capacity_utilization
    value:
    period:
    trend: rising | flat | declining
    source_ref:
    permission_level:
cycle_phase_assessment:
  hbm:
  dram:
  nand:
evidence_tier:
```

## 8. Firewall Rules

```text
specialized_infrastructure_research CAN support:
  - supply_constraint_signal (foundry/packaging bottleneck)
  - capacity_ramp_evidence (when citing foundry/industry data)
  - architecture_shift
  - memory_cycle_position
  - semiconductor_leading_indicator
  - cost_structure_change
  - competitive_position_shift
  - equipment_constraint

specialized_infrastructure_research CANNOT support:
  - utilization_state at publicly_observable (needs foundry/operator data)
  - memory_pricing_signal at publicly_observable (needs vendor/channel data)
  - demand proof (that's application expert's territory)
  - DC power/construction claims (that's datacenter expert's territory)

company_primary_disclosure CAN support:
  - ALL semiconductor claim types at publicly_observable when directly stated
  - capacity_ramp_evidence (foundry announces expansion)
  - supply_constraint_signal (acknowledged in filing/earnings)
  - utilization_state (when foundry/memory vendor discloses)
  - memory_pricing_signal (when vendor discloses contract terms)

company_primary_disclosure CANNOT support:
  - industry-wide supply conclusion from single company
  - future delivery certainty from management optimism
  - competitor analysis from one vendor's claims

industry_data_surface CAN support:
  - utilization_state
  - lead_time_signal
  - memory_pricing_signal
  - cost_structure_change
  - capacity_ramp_evidence
  - equipment_constraint

industry_data_surface CANNOT support:
  - company-specific revenue (needs filing)
  - competitive_position_shift as definitive (needs multi-source)

curated_practitioner_industry_analysis CAN support:
  - semiconductor_leading_indicator (sector pattern)
  - competitive_position_shift (cross-company pattern)
  - architecture_shift (practitioner assessment)
  - memory_cycle_position (cross-vendor pattern)

curated_practitioner_industry_analysis CANNOT support:
  - supply_constraint_signal as structural claim without data
  - utilization/capacity numbers without foundry data source
  - memory pricing without channel data
```

## 9. Validation Gates

AI Semiconductor Expert output is invalid if:

- claim 缺少 `channel_id` 或 `transmission_step`；
- specialized research conviction 被标为 `publicly_observable`；
- 单一 source 支撑整条 supply chain 的结论；
- market price momentum 被当作 supply/demand proof；
- "supply is tight" 无具体 bottleneck location（foundry? packaging? HBM?）和 evidence tier；
- Jensen/CEO quote about competitive moat 被当作 `publicly_observable` market share data；
- HBM shortage 被自动等同于 DRAM shortage（不同 cycle）；
- single-customer ASIC win 被概括为 industry displacement；
- 产出 portfolio action 或 demand/adoption claims（那是 application expert 的领域）；
- 产出 DC power/construction claims（那是 datacenter expert 的领域）；
- capacity ramp 被当作永远不会到来（忽略 timeline）。

## 10. Dogfood Source Shape

### Citrini as Primary Source

| Source type | Source class | What it supports | What it cannot support alone |
|---|---|---|---|
| Citrini "Semis Memo: Muscle Memory" | `specialized_infrastructure_research` | memory cycle position, HBM allocation dynamics | exact pricing without vendor data |
| Citrini "Carving Up the TPU" | `specialized_infrastructure_research` | architecture transition (ASIC analysis), competitive dynamics | production volume, customer commitment |
| Citrini "Atoms vs Bits" | `specialized_infrastructure_research` | supply chain mapping, physical constraint analysis | foundry utilization numbers without TSM data |

### TMT Breakout / SemiAnalysis

| Source type | Source class | What it supports | What it cannot support alone |
|---|---|---|---|
| Dylan Patel / SemiAnalysis AMA | `curated_practitioner_industry_analysis` | architecture shift assessment, competitive dynamics, supply chain insight | production-ready claims, exact capacity |
| TMTB semis sector rotation signals | `curated_practitioner_industry_analysis` | cross-company pattern, memory vs logic rotation | structural supply chain claims, utilization data |
| TMTB earnings first-takes (NVDA, AMD, MU, TSM) | `curated_practitioner_industry_analysis` | event interpretation, guidance contextualization | standalone demand proof |

### Ticker Coverage

Primary affected tickers:

- **GPU/Logic**: NVDA, AMD, AVGO, MRVL, QCOM
- **Foundry/Packaging**: TSM, ASX (ASML), AMKR
- **Memory**: MU, SK Hynix (000660.KS), Samsung
- **Equipment**: ASML, AMAT, LRCX, KLA, SNPS, CDNS
- **ASIC/Custom**: AVGO (custom), GOOG (TPU), AMZN (Trainium)

## 11. Adjacent Docs

| Doc | Relationship |
|---|---|
| `digestion_51_ai_industry_expert.md` | Family umbrella / orchestrator |
| `digestion_51_2_ai_datacenter_expert.md` | Sibling: AI Data Center child expert |
| `digestion_51_3_ai_application_expert.md` | Sibling: AI Application child expert |
| `digestion_41_2_listed_company_expert.md` | Handoff target when industry signal feeds single-ticker analysis |
| `digestion_30_expert_factory.md` | Expert lifecycle and admission |
| `digestion_10_structure_contract.md` | Object schema |
