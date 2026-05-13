---
title: Healthcare / Life Sciences Expert
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Independent Research Orchestrator
---

# Healthcare / Life Sciences Expert

## 1. Purpose

`Healthcare Expert` 是 Digestion 层的独立行业 expert，负责 digest healthcare/life sciences 行业的 source material：drug discovery pipeline dynamics、clinical development、CRO economics、testing infrastructure demand、biotech capital cycle。

AI 是影响本行业的重要力量（加速 R&D、改变瓶颈分布、降低 discovery 成本），但 expert 的组织原则是 **healthcare domain knowledge**，不是 AI。判断一个 AI-discovered candidate 是否有意义，需要理解临床试验分期、FDA 审批路径、CRO 经济学——这些是 pharma 行业知识，不是 AI 行业知识。

本 expert **不属于** AI Industry Expert Family (51)。51 的 transmission chain 终止于 AI platform/enterprise 层面。当 AI 的影响进入 healthcare 价值链后，证据评估所需的 domain knowledge 从 AI 转为 pharma。

## 2. Reader End-State

读完本 expert 产出后，PM 应该能说清：

- drug discovery pipeline 处于什么阶段：哪些 AI-assisted candidates 真正进入了临床开发，哪些还在 narrative 阶段；
- CRO 行业的 volume/margin 实际数据是什么（book-to-bill, cancellation, RFP tone），而非 stock price 信号；
- 行业瓶颈在哪：AI 加速了 discovery 后，约束转移到了什么节点（wet-lab、patient recruitment、regulatory）；
- enabling infrastructure（lab automation、QC、data tools）的需求是 proven 还是 anticipated；
- biotech 资本周期处于什么位置，对 CRO 和 testing 需求的传导 lag 是多少；
- 什么 signal 出现会改变判断（AI drug fails Phase 1、CRO cancellation spike、biotech funding freeze）。

Silent violation:

```text
"AI drug discovery 很热" 但读者分不清 "Eli Lilly CEO 说 AI 在帮助发现新化合物（narrative heat）"
和 "Insilico Medicine 的 ISM001-055 已完成 Phase 2a 临床试验（pipeline milestone）"。
```

## 3. Source Classes

> **Canonical references**:
> - Source class 定义和 authority 等级：[`digestion_35_claim_taxonomy_and_source_authority.md`](digestion_35_claim_taxonomy_and_source_authority.md) §5
> - Routing matrix：同文 §6
> - Machine-readable：`data/runtime/schemas/claim_type_taxonomy.yaml`
> - 本 expert 的 subtypes 和 firewall supplements：`data/digestion/expert_subsystems/healthcare_expert/expert_contract.yaml`

### 3.1 `company_primary_disclosure`

典型来源：Pharma earnings（LLY AI R&D disclosure）、CRO earnings（IQV, MEDP bookings）、lab infrastructure earnings（TMO, DHR）

Allowed claim support:

- AI-discovered candidate entering development → `pipeline_milestone` at `publicly_observable`；
- CRO booking/revenue/margin data → `cro_margin_dynamics` at `publicly_observable`；
- R&D partnership signed → `partnership_execution` at `publicly_observable`；
- management commentary on AI impact → `proxy_inferable` when forward-looking。

Blocked support:

- "AI is transforming our R&D" = pipeline proof；
- disclosed AI partnership ≠ confirmed therapeutic output；
- CRO revenue growth without AI attribution = AI demand proof。

### 3.2 `specialized_infrastructure_research`

典型来源：Citrini Research（AI drug discovery / CRO picks-and-shovels thesis）

Allowed claim support:

- bottleneck shift identification（compute → wet-lab/trials）；
- enabling infrastructure vendor identification；
- cross-company demand direction signals；
- capital cycle framing。

Blocked support:

- confirmed CRO revenue impact without disclosed data；
- pipeline acceleration certainty without clinical milestone；
- industry-wide adoption from single analyst observation。

### 3.3 `industry_data_surface`

典型来源：ClinicalTrials.gov, FDA approval pipeline, biotech funding trackers

Allowed claim support:

- trial starts/completions → `pipeline_stage_progression` at `proxy_inferable`；
- FDA pathway designations → `policy_catalyst` at `publicly_observable`；
- biotech IPO/funding data → `biotech_capital_cycle` context。

Blocked support:

- trial count = trial success；
- regulatory filing = regulatory approval；
- biotech funding = CRO demand certainty（2-4 quarter lag）。

### 3.4 `sell_side_practitioner_analysis`

Allowed: cross-company pattern signals, competitive dynamics. Blocked: confirmed demand/revenue claims.

## 4. Channel Registry

### 4.1 `drug_discovery_pipeline`

- **定义**: 从 target identification 到 IND filing 的 discovery 管线状态
- **native_horizon**: 4-12 quarters
- **observables**: AI-discovered candidate count and stage, discovery-to-IND timeline, pharma R&D partnerships, domain model milestones
- **typical_misuse**: model benchmark improvement = commercial drug discovery success
- **falsifiers**: AI-discovered candidates fail preclinical at higher rate than traditional, no major pharma adopts AI-first discovery workflow

### 4.2 `clinical_development`

- **定义**: IND 之后的临床开发（Phase 1/2/3, approval, post-market）
- **native_horizon**: 4-16 quarters
- **observables**: trial starts, enrollment rates, completion rates, FDA designations, approval/rejection
- **typical_misuse**: Phase 1 entry = drug will succeed; fast track designation = guaranteed approval
- **falsifiers**: AI-discovered drugs show no better phase transition rate than traditional compounds

### 4.3 `cro_and_service_economics`

- **定义**: CRO / CDMO 的 volume、pricing、backlog、margin dynamics
- **native_horizon**: 2-6 quarters
- **observables**: book-to-bill, booking growth, cancellation rate, RFP volume, margin, sponsor concentration
- **typical_misuse**: biotech funding up = CRO demand up (lag!); CRO stock up = demand confirmed
- **falsifiers**: CRO book-to-bill stays <1.0 despite biotech funding recovery; elevated cancellations persist

### 4.4 `testing_and_qc_infrastructure`

- **定义**: 检测、质控、实验室自动化设备和服务需求
- **native_horizon**: 2-8 quarters
- **observables**: lab automation orders, QC deployments, sample volume, testing throughput
- **typical_misuse**: "AI drug discovery = buy lab equipment" without demand transmission logic
- **falsifiers**: enabling tool demand stays flat despite AI discovery announcements

### 4.5 `biotech_capital_cycle`

- **定义**: biotech 融资环境、IPO 窗口、pharma M&A 对 downstream demand 的影响
- **native_horizon**: 2-6 quarters
- **observables**: IPO volume/proceeds, venture rounds, M&A activity/premium, biotech index
- **typical_misuse**: biotech index rally = industry health; single large deal = M&A cycle turning
- **falsifiers**: funding recovery doesn't translate to CRO bookings within 3 quarters

## 5. Healthcare Value Chain

本 expert 的价值链是 pharma/biotech 自身的 R&D-to-commercial 链，不是 AI Transmission Chain：

```text
1. Target/Lead Identification (computational + wet-lab screening)
   ↓
2. Preclinical Development (toxicology, pharmacology, formulation)
   ↓
3. IND Filing & Regulatory Interaction
   ↓
4. Clinical Development (Phase 1 → 2 → 3)
   ↓
5. Regulatory Approval (NDA/BLA, FDA/EMA review)
   ↓
6. Commercial Launch & Post-Market
```

**Where AI enters**: primarily Step 1 (AI-assisted target identification, candidate generation), with emerging influence on Step 2 (predictive toxicology) and Step 4 (AI-assisted patient recruitment, adaptive trial design).

**Service provider overlay**: CROs serve Steps 2-5. Lab automation/QC serves Steps 1-2. CDMO serves Steps 2-6.

## 6. Typed Claim Pattern

```yaml
object_type: HealthcareTypedClaim
claim_id:
source_card_id:
expert_id: healthcare_expert
channel_id: drug_discovery_pipeline | clinical_development | cro_and_service_economics | testing_and_qc_infrastructure | biotech_capital_cycle
source_class:
claim_type:
permission_level: publicly_observable | proxy_inferable | not_knowable_from_public_data
claim:
elaboration:
time_validity:
confidence:
confidence_cap_reason:
affected_tickers: []
falsifiers: []
source_span_refs: []
downstream_allowed_use: []
downstream_blocked_use: []
```

## 7. Domain Artifacts

### 7.1 Drug Discovery Pipeline Map

Per-stage tracking of AI-assisted vs traditional pipeline：

```yaml
pipeline:
  - company:
    candidate:
    discovery_method: ai_assisted | traditional | hybrid
    current_stage: target_id | lead_opt | preclinical | phase_1 | phase_2 | phase_3 | approved
    evidence_source:
    confidence:
```

### 7.2 CRO Economics Dashboard

```yaml
cro_metrics:
  - company:
    period:
    book_to_bill:
    booking_growth_yoy:
    cancellation_rate:
    margin:
    rfp_tone: improving | stable | deteriorating
    ai_attribution: none | mentioned | quantified
    source_ref:
```

### 7.3 Testing Infrastructure Demand Matrix

```yaml
testing_demand:
  - category: lab_automation | qc | sample_management | genomic_data
    companies: []
    demand_signal:
    evidence_tier: confirmed_orders | management_commentary | analyst_inference
    source_ref:
```

## 8. Relationship With AI Industry Expert (51)

```text
AI Industry Expert (51)              Healthcare Expert (52)
  └── Transmission Chain               └── Pharma Value Chain
        Steps 1-9                           Steps 1-6
        (capex → semis → DC →              (discovery → preclinical →
         platform → enterprise)              clinical → approval)

  Boundary: when AI's impact enters a specific industry value chain,
  evidence evaluation requires INDUSTRY domain knowledge, not AI knowledge.
  
  Edge: 51's "model capability" claims can inform 52's "ai_rd_integration"
  assessment, but 52 makes its own judgment using pharma context.
```

跨 expert edge 不在一个 expert 内部混合。51 可以告诉 52 "frontier model X has improved accuracy on protein structure prediction"，但 52 独立判断这对 drug discovery pipeline 意味着什么。

## 9. Validation Gates

Healthcare Expert output is invalid if:

- academic model benchmark 被标为 `pipeline_milestone`（需要 drug candidate 进入具体阶段）；
- CEO "AI is transforming our R&D" 被标为 `pipeline_milestone` 或 `rd_cycle_compression`；
- CRO stock performance 被当作 `cro_margin_dynamics` proof（需要 disclosed financials）；
- biotech funding recovery 被直接等同于 CRO demand（2-4 quarter lag）；
- 单一 AI drug 成功被概括为行业范围 pipeline acceleration；
- picks-and-shovels thesis 没有 demand transmission 逻辑；
- 产出 portfolio action、thesis、AI platform adoption claims（属于其他 expert）。

## 10. Dogfood Source Shape

### Citrini AI Drug Discovery (2026-01-16)

| Source type | Source class | What it supports | What it cannot support alone |
|---|---|---|---|
| Citrini AI drug discovery / CRO picks-and-shovels | `specialized_infrastructure_research` | wet_lab_capacity_constraint, enabling_tool_position, cro_margin_dynamics (directional) | pipeline_milestone (needs clinical data), trial_cost_shift (needs CRO financials) |
| Evo 2 / AlphaFold model data | `industry_data_surface` | ai_rd_integration at proxy_inferable | commercial drug discovery success |
| Genesis Mission EO | `industry_data_surface` | policy_catalyst at publicly_observable | demand acceleration certainty |
| Eli Lilly CEO interview | `company_primary_disclosure` | ai_rd_integration at proxy_inferable | pipeline_milestone without disclosed candidate |

## 11. Adjacent Docs

| Doc | Relationship |
|---|---|
| `digestion_51_ai_industry_expert.md` | Adjacent: AI industry（51 的 model capability claims 可以 inform 52 的 ai_rd_integration） |
| `digestion_51_3_ai_application_expert.md` | Boundary: horizontal AI platform adoption 留在 51_3 |
| `digestion_35_claim_taxonomy_and_source_authority.md` | Shared taxonomy |
| `digestion_41_2_listed_company_expert.md` | Handoff target for single-ticker analysis |
| `digestion_30_expert_factory.md` | Expert lifecycle and admission |
| `digestion_10_structure_contract.md` | Object schema |
