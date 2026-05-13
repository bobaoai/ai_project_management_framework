---
title: AI Application Expert
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Independent Research Orchestrator
---

# AI Application Expert

## 1. Purpose

`AI Application Expert` 是 AI Industry Expert Family 的 child expert，负责 digest AI **horizontal platform 和 enterprise** 需求侧的 source material：enterprise adoption、monetization proof、model-to-commercial-value conversion、demand quality signals。

它把 platform/enterprise-focused sources 消化为 typed claims 和 domain artifacts，供 family umbrella 组装 AI Industry State Map。

本 expert 覆盖 AI Transmission Chain 的 **Steps 5–9 horizontal branch**（Cloud Capacity Available → Model Serving → Platform Pricing → Enterprise Adoption → End-User Monetization），以及 Step 5 的 cost-to-serve 视角。

> **Vertical AI 不属于本 expert**: AI 改造垂直行业（drug discovery、autonomous、industrial）的 source digestion 由各行业自己的 expert family 负责（如 [`digestion_52_healthcare_expert.md`](digestion_52_healthcare_expert.md)），不属于 51 AI Industry family。原因：垂直行业的价值链、瓶颈节点、evidence permission 与 SaaS/enterprise 完全不同（capture 测试确认 ≈ 25-50%），且评估这些信号需要行业 domain knowledge（临床试验分期、FDA 路径、CRO 经济学），不是 AI 行业知识。

## 2. Reader End-State

读完本 expert 产出后，PM 应该能说清：

- enterprise AI adoption 处于什么阶段，evidence tier 是什么（announced > pilot > production > scaled revenue）；
- 哪些 monetization signal 是 real（有 disclosed revenue/ARR），哪些仅是 narrative（CEO 提到 AI、survey intent）；
- demand quality：usage 是否在增长、churn 高不高、pricing power 如何；
- model capability improvement 如何 translate 到 commercial value（inference cost 下降 → adoption 加速 → revenue）；
- 哪些判断来自 primary company disclosure，哪些来自 practitioner observation；
- 什么 signal 出现会改变 adoption read（usage plateau、pricing pressure、churn spike）。

Silent violation:

```text
Adoption read 很乐观，但读者分不清 "公司 CEO 说 AI 是优先级" 和 "公司 AI 产品有 disclosed revenue growth"。
```

## 3. Source Classes

> **Canonical references**:
> - Source class 定义和 authority 等级：[`digestion_35_claim_taxonomy_and_source_authority.md`](digestion_35_claim_taxonomy_and_source_authority.md) §5
> - Routing matrix（source_class × umbrella_claim_type）：同文 §6
> - Machine-readable：`data/runtime/schemas/claim_type_taxonomy.yaml`
> - 本 expert 的 subtypes 和 firewall supplements：`data/digestion/expert_subsystems/ai_application_expert/expert_contract.yaml`
>
> 以下保留 domain-specific 的 allowed/blocked support 细节，作为 expert_contract.yaml 中 `firewall_supplements` 的 human-readable 展开。
> source_class 名称已统一为 taxonomy 中的 canonical 名称（`curated_practitioner_application_analysis` → `sell_side_practitioner_analysis`）。

### 3.1 `sell_side_practitioner_analysis`

典型来源：TMT Breakout（AI application breakouts、SaaS adoption signals）

Allowed claim support:

- cross-company adoption pattern signals（多家 AI-enabled SaaS 同时 breakout/breakdown）；
- application-layer competitive dynamics；
- user behavior shifts visible in market structure；
- event catalysts for adoption inflection。

Blocked support:

- monetization certainty without disclosed revenue；
- demand proof from market momentum alone；
- usage metrics without primary source；
- single newsletter observation = structural adoption change。

### 3.2 `company_primary_disclosure`

典型来源：SaaS/platform earnings（MSFT Azure AI, CRM Einstein, SNOW Cortex）、product announcements with metrics

Allowed claim support:

- AI-attributed revenue / ARR → `publicly_observable`；
- disclosed usage metrics（seats, API calls, tokens consumed）；
- customer count for AI products；
- pricing changes and tier structure；
- pilot-to-production conversion when disclosed；
- management commentary on AI monetization（as `proxy_inferable` when forward-looking）。

Blocked support:

- "AI is a priority" = demand proof；
- disclosed AI feature ≠ confirmed adoption；
- TAM claims as validated market size；
- customer satisfaction without retention data。

### 3.3 `usage_and_adoption_data`

典型来源：app store data、API usage trackers、developer activity metrics、enterprise survey data

Allowed claim support:

- usage growth trajectory（as `proxy_inferable`）；
- developer adoption velocity；
- enterprise survey intent（as weak signal, not adoption fact）；
- app store ranking / download trends for AI products。

Blocked support:

- exact revenue from usage proxy；
- retention/churn without disclosed data；
- enterprise intent = confirmed procurement。

### 3.4 `specialized_application_research`

典型来源：focused AI application analysts、enterprise technology research

Allowed claim support:

- adoption framework and maturity assessment；
- monetization model analysis；
- competitive positioning in AI application layer；
- cost-to-value ratio analysis。

Blocked support:

- undisclosed company internals；
- precise revenue attribution without filing source；
- demand certainty from framework alone。

### 3.5 `market_data_surface`

Allowed claim support:

- AI SaaS cohort relative strength and rotation；
- valuation premium/discount for AI-enabled vs traditional SaaS；
- market expectations for AI monetization。

Blocked support:

- business quality；
- demand certainty；
- adoption proof。

## 4. Channel Registry

### 4.1 `model_to_commercial_value`

- **定义**: frontier model capability improvement 如何 translate 到 commercial product improvement 和 cost reduction
- **transmission_step**: Steps 5–6
- **native_horizon**: 1–3 quarters（model release → product integration）
- **observables**: inference cost per token trend、model capability on commercial tasks、latency reduction、new modality launch
- **typical_misuse**: benchmark improvement on academic tasks = commercial value creation
- **falsifiers**: cost not declining、capability plateau on real tasks、latency still too high for production

### 4.2 `platform_pricing_and_economics`

- **定义**: AI platform/API pricing, unit economics, gross margin for AI services
- **transmission_step**: Step 7
- **native_horizon**: 2–4 quarters（pricing cycle）
- **observables**: API pricing tiers、inference cost trends、gross margin on AI services、consumption-based vs seat-based mix
- **typical_misuse**: pricing cut = demand acceleration（可能是 competitive pressure）
- **falsifiers**: gross margin deterioration、pricing war、consumption growth 不补足 price decline

### 4.3 `enterprise_adoption_progression`

- **定义**: enterprise 从 awareness → evaluation → pilot → production → scaled deployment 的进度
- **transmission_step**: Step 8
- **native_horizon**: 2–6 quarters（enterprise procurement cycle）
- **observables**: pilot count、production deployment count、seats/users、customer logos、land-and-expand metrics、enterprise survey data
- **typical_misuse**: pilot count = production certainty；CEO mention = budget commitment；survey intent = procurement decision
- **falsifiers**: high pilot churn、pilot-to-prod conversion stagnation、budget freezes、security/compliance blocks

### 4.4 `monetization_and_revenue_proof`

- **定义**: AI-specific revenue attribution, margin contribution, growth rate 的 hard evidence
- **transmission_step**: Step 9
- **native_horizon**: 1–4 quarters（quarterly disclosure cycle）
- **observables**: AI-attributed ARR/revenue（如 GitHub Copilot, Azure AI consumption）、AI revenue growth rate、AI gross margin、AI revenue % of total
- **typical_misuse**: "AI is contributing to growth" without disclosed quantum = confirmed monetization
- **falsifiers**: AI revenue growth deceleration、AI margin below company average、customer pushback on AI pricing

### 4.5 `demand_quality`

- **定义**: demand 是 durable/sticky 还是 trial/hype-driven 的判断
- **transmission_step**: cross-cutting（影响 Steps 8–9）
- **native_horizon**: 2–4 quarters
- **observables**: retention/churn for AI products、net revenue retention、usage frequency、workflow integration depth
- **typical_misuse**: initial adoption spike = durable demand；free-tier usage = willingness-to-pay
- **falsifiers**: usage decline after initial spike、churn above cohort norms、downgrade to lower tier

## 5. Typed Claim Pattern

```yaml
object_type: AIAppTypedClaim
claim_id:
source_card_id:
expert_id: ai_application_expert
channel_id: model_to_commercial_value | platform_pricing_and_economics | enterprise_adoption_progression | monetization_and_revenue_proof | demand_quality
source_class:
claim_type:
permission_level: publicly_observable | proxy_inferable | not_knowable_from_public_data
claim:
elaboration:
time_validity:
confidence:
confidence_cap_reason:
transmission_step: 5 | 6 | 7 | 8 | 9
affected_tickers: []
falsifiers: []
source_span_refs: []
downstream_allowed_use: []
downstream_blocked_use: []
```

Claim type families:

- `adoption_stage` — where on the adoption ladder (announced / pilot / production / scaled)
- `adoption_proof` — concrete adoption metric with source
- `monetization_evidence` — disclosed AI-specific revenue or margin
- `monetization_signal` — weaker monetization indicator (management commentary, partial data)
- `demand_quality_signal` — retention, usage frequency, stickiness evidence
- `pricing_power` — ability to maintain/raise AI pricing
- `cost_to_serve` — inference/serving cost trajectory
- `competitive_position_shift` — application-layer market share or moat change
- `workflow_integration_depth` — how embedded AI is in customer workflow
- `cannot_know_boundary`
- `falsifier`

## 6. Source Card Pattern

```yaml
object_type: AIAppSourceCard
expert_id: ai_application_expert
expert_version: v0
source_ref: data/research/messages/<research_id>/read_content.md
source_class:
source_authority: primary_company | usage_data_provider | curated_practitioner | specialized_researcher | market_data
time_semantics:
  observation_period:
  published_at:
  data_freshness:
channel_relevance: []
transmission_steps_covered: []
key_observations: []
adoption_claims: []
monetization_claims: []
missing_context: []
affected_tickers: []
blocked_uses: []
source_span_refs: []
```

## 7. Domain Artifacts

### 7.1 Adoption Ladder

回答 "AI adoption 现在在哪一步，evidence 是什么"。

```text
Tier 5 — Scaled Revenue (disclosed, growing, material % of total)
Tier 4 — Production Revenue (disclosed AI revenue but early/small)
Tier 3 — Production Deployment (customers in production, usage metrics)
Tier 2 — Pilot / POC (announced pilots, evaluations)
Tier 1 — Announced / Intent (CEO statements, feature launches, surveys)
Tier 0 — No Signal
```

每家受关注公司标注当前 tier + evidence source + confidence cap。

### 7.2 Monetization Evidence Matrix

Structured view of which companies have disclosed AI-specific revenue/metrics：

```yaml
monetization_data_points:
  - company:
    product:
    metric_type: revenue | ARR | seats | usage | growth_rate
    value:
    period:
    yoy_or_qoq:
    source_ref:
    permission_level:
    confidence_cap_reason:
```

### 7.3 Demand Quality Assessment

Per-product or per-company demand quality scoring：

- usage trajectory (growing / flat / declining)
- retention signal (disclosed NRR, churn, or inferred from cohort)
- pricing power (raising prices / stable / cutting)
- workflow integration (standalone tool / embedded / core workflow)

## 8. Firewall Rules

```text
curated_practitioner_application_analysis CAN support:
  - adoption_stage (cross-company pattern)
  - competitive_position_shift (market structure observation)
  - demand_quality_signal (behavioral pattern)

curated_practitioner_application_analysis CANNOT support:
  - monetization_evidence (needs primary disclosure)
  - adoption_proof with specific metrics (needs primary source)
  - pricing_power claim without pricing data

company_primary_disclosure CAN support:
  - ALL claim types at publicly_observable when directly stated
  - monetization_evidence (disclosed AI revenue)
  - adoption_proof (disclosed metrics)
  - pricing_power (disclosed pricing changes)

company_primary_disclosure CANNOT support:
  - industry-wide adoption conclusion from single company
  - demand_quality for market segment from one company's data
  - future monetization certainty from current revenue (guidance ≠ fact)

usage_and_adoption_data CAN support:
  - adoption_proof at proxy_inferable (usage metrics)
  - demand_quality_signal (usage patterns)
  - competitive_position_shift (market share proxy)

usage_and_adoption_data CANNOT support:
  - monetization_evidence (usage ≠ revenue)
  - retention as definitive without churn data
  - enterprise intent as procurement fact

market_data_surface CAN support:
  - competitive_position_shift (relative performance)
  - market expectations context

market_data_surface CANNOT support:
  - adoption_proof
  - monetization_evidence
  - demand_quality
```

## 9. The "Narrative Heat" Problem

本 expert 的核心 firewall 挑战是区分 narrative heat 和 real demand：

| Source signal | What it IS | What it is NOT |
|---|---|---|
| CEO says "AI is our top priority" | `adoption_stage: announced` | `adoption_proof` |
| Company launches AI feature | `adoption_stage: announced` | `monetization_evidence` |
| Survey says 60% of enterprises plan to use AI | `adoption_stage: intent` (weak) | `enterprise_adoption_progression: production` |
| AI product has 1M free users | `adoption_proof: trial` | `monetization_evidence` or `demand_quality: sticky` |
| AI ARR grew 50% QoQ to $X00M (disclosed) | `monetization_evidence` ✓ | — |
| GitHub Copilot has 1.8M paid subscribers (disclosed) | `adoption_proof: scaled` ✓ | — |

只有 company 主动 disclose 的 AI-specific revenue/usage metric 才能标为 `publicly_observable` monetization or adoption proof。

## 10. Validation Gates

AI Application Expert output is invalid if:

- narrative heat（CEO mention、feature launch、survey intent）被标为 `adoption_proof` 或 `monetization_evidence`；
- free-tier usage 被当作 willingness-to-pay proof；
- 单一公司 AI revenue 被概括为 industry adoption trend（需要 cross-company evidence）；
- market momentum 被当作 demand quality proof；
- "AI is growing" 无具体 metric、company、period；
- 产出 portfolio action 或 supply chain claims（那是 infrastructure expert 的领域）；
- adoption_stage 标注没有 evidence source mapping；
- inference cost 下降被自动等同于 adoption acceleration（中间还有 pricing、integration、procurement 等步骤）。

## 11. Dogfood Source Shape

### TMT Breakout as Primary Source

| Source type | Source class | What it supports | What it cannot support alone |
|---|---|---|---|
| TMT Breakout AI SaaS breakout signals | `curated_practitioner_application_analysis` | cross-company adoption pattern, competitive shift | monetization numbers, specific usage metrics |
| TMT Breakout enterprise AI observations | `curated_practitioner_application_analysis` | demand direction signal, workflow integration patterns | retention data, revenue attribution |

### Company Earnings (Application Layer)

| Source type | Source class | What it supports | What it cannot support alone |
|---|---|---|---|
| MSFT Azure AI / Copilot metrics | `company_primary_disclosure` | monetization_evidence, adoption_proof (when disclosed) | industry-wide adoption from one company |
| CRM Einstein AI / Agentforce | `company_primary_disclosure` | monetization_evidence if disclosed, adoption_stage | proof that enterprise is broadly adopting |
| GitHub Copilot subscriber data | `company_primary_disclosure` | adoption_proof: scaled (publicly disclosed) | quality of usage, retention depth |

## 12. Adjacent Docs

| Doc | Relationship |
|---|---|
| `digestion_51_ai_industry_expert.md` | Family umbrella / orchestrator |
| `digestion_51_1_ai_semiconductor_expert.md` | Sibling: AI Semiconductor child expert |
| `digestion_51_2_ai_datacenter_expert.md` | Sibling: AI Data Center child expert |
| `digestion_52_healthcare_expert.md` | Adjacent: Healthcare expert（vertical AI signals route here, not to 51） |
| `digestion_41_2_listed_company_expert.md` | Handoff target for single-ticker analysis |
| `digestion_30_expert_factory.md` | Expert lifecycle and admission |
| `digestion_10_structure_contract.md` | Object schema |
