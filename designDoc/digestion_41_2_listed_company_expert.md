---
title: Listed Company Expert
status: active_draft
reader_persona:
  - System Builder
  - Research Architect
  - Company Analyst
  - Independent Research Orchestrator
---

# Listed Company Expert

## 1. Purpose

`Listed Company Expert` is the Digestion-layer expert for one public operating company.

It turns a routed listed-company `source_packet` into company-owned Source Cards, company typed claims, and a `single_asset_dossier`. It is not the same object as `research-single-stock-analysis`, `research-theme-report-owner`, thesis drafting, or portfolio decision.

Listed-company research has a different semantic problem from theme, thesis, private-company, or crypto work:

- filings and earnings materials contain operating facts, accounting facts, guidance, segment data, risks, and management language;
- market data and technical packets describe price behavior but do not prove business quality;
- external news can reveal catalysts and disputes but often cannot support structural claims alone;
- valuation requires separating observed multiples, expectation gaps, and forward assumptions;
- portfolio action requires PM authority and should not be emitted directly by the expert.

## 2. Reader End-State

After reading a `single_asset_dossier`, the PM or downstream analyst should be able to state:

- what the company actually does and which segment or product line matters most now;
- which source-backed facts are public, which are proxy-inferable, and which are not knowable from public data;
- whether recent performance is driven by volume, price, margin, mix, accounting, one-time events, or market expectation;
- what management claims, filings, market data, and external evidence each can and cannot prove;
- which business questions matter before promoting the asset into `research-single-stock-analysis`, `operation-portfolio-decision`, or a thesis/theme workflow;
- which assumptions are blocked because the source packet lacks filings, transcripts, market data, peer data, or customer / channel evidence.

Silent violation:

```text
The dossier sounds like an investment memo, but the reader cannot tell which claims came from filings, which came from market price, and which came from analyst inference.
```

## 3. Layer Boundary

The route is:

```text
Independent Research Orchestrator
  -> source_packet
  -> domain_route: listed_company_expert or company_expert:default_company_dossier
  -> CompanySourceCard
  -> CompanyTypedClaim
  -> single_asset_dossier
  -> optional company_research_report_draft
```

The independent researcher owns source collection, archiving, linking, package assembly, and route selection. The listed company expert owns listed-company interpretation objects.

Blocked outputs:

- direct portfolio action;
- position sizing;
- thesis activation;
- theme priority updates;
- generic source cards before company route selection;
- crypto project decision briefs;
- private-company pricing-surface interpretation;
- market recap or macro regime reports.

Allowed downstream handoff:

- `research-single-stock-analysis` for ticker-first PM analysis;
- `operation-portfolio-decision` when the user asks about book action;
- `research-theme-report-owner` only when a company claim becomes theme evidence;
- `Digestion Expert Factory` when the company requires a new industry template.

## 4. Source Classes

### 4.1 `company_filing`

Examples:

- 10-K;
- 10-Q;
- 8-K;
- S-1 / F-1;
- proxy statement;
- Form 4;
- 13D / 13G;
- 13F when the question is ownership rather than company operations.

Allowed claim support:

- audited or filed financial statements;
- segment disclosure;
- stated risk factors;
- legal and regulatory disclosures;
- accounting policies;
- share count and capital structure;
- official business description.

Blocked support:

- management credibility by itself;
- future demand certainty;
- valuation attractiveness;
- customer intent beyond disclosed evidence.

### 4.2 `earnings_release`

Allowed claim support:

- current-quarter headline metrics;
- company-provided segment revenue;
- GAAP / non-GAAP bridge when disclosed;
- guidance and outlook;
- disclosed one-time charges;
- official management quote.

Blocked support:

- full historical business quality without filing context;
- durable margin assumption without multi-period evidence;
- customer economics unless disclosed.

### 4.3 `earnings_call_transcript`

Allowed claim support:

- management explanation of drivers;
- analyst Q&A pressure points;
- changes in tone and emphasis;
- guidance color;
- customer / product / channel commentary.

Blocked support:

- factual certainty when management uses promotional or forward-looking language;
- unquoted inference about customer behavior;
- numerical claims not stated or reconciled elsewhere.

### 4.4 `investor_presentation`

Allowed claim support:

- official market framing;
- product roadmap framing;
- segment strategy;
- disclosed KPI snapshots;
- management-defined TAM and long-term narrative.

Blocked support:

- independent validation of TAM;
- proof that customers will adopt at the claimed rate;
- proof that economics will accrue to shareholders.

### 4.5 `market_data_surface`

Examples:

- price / volume;
- relative strength;
- implied volatility;
- options skew;
- valuation multiples;
- market cap and enterprise value;
- consensus snapshot when the source is structured.

Allowed claim support:

- market behavior;
- positioning pressure;
- volatility and expectation regime;
- observed valuation context.

Blocked support:

- business quality;
- future fundamentals;
- management execution;
- customer demand without separate evidence.

### 4.6 `external_news`

Allowed claim support:

- event discovery;
- public controversy;
- regulator, customer, supplier, or competitor statements;
- industry context;
- timeline reconstruction.

Blocked support:

- durable business judgment without official or primary-source corroboration;
- numerical operating claims unless the article cites primary data;
- portfolio action.

### 4.7 `alternative_or_channel_data`

Examples:

- app downloads;
- web traffic;
- job postings;
- credit-card or receipt aggregates;
- cloud spend proxies;
- supply-chain checks;
- customer checks;
- developer activity.

Allowed claim support:

- proxy-inferable direction;
- channel momentum;
- product adoption clue;
- early warning signal.

Blocked support:

- reported revenue;
- exact market share;
- audited margin;
- undisclosed customer commitments.

## 5. Evidence Permission Layer

Each listed-company claim must carry one permission level.

```text
publicly_observable
  The source directly reports the fact.

proxy_inferable
  The source does not directly report the fact, but a bounded proxy suggests a directional read.

not_knowable_from_public_data
  The question matters, but the current public source packet cannot answer it.
```

Permission examples:

- `NVIDIA Q1 FY2026 revenue was $44.1B` from the company earnings release: `publicly_observable`.
- `NVIDIA's H20 export restriction pressured reported gross margin in Q1 FY2026` from the same release: `publicly_observable`.
- `Blackwell demand is strong enough to offset all China export loss`: not directly proven; at most `proxy_inferable` with guidance, order commentary, and hyperscaler capex support.
- `A specific hyperscaler has committed to an undisclosed multi-year volume`: `not_knowable_from_public_data` unless disclosed by a primary source.

## 6. Claim-Type Firewall

Listed-company typed claims use domain-specific `claim_type`.

Core claim families:

- `business_model`;
- `segment_mix`;
- `revenue_growth_quality`;
- `margin_structure`;
- `operating_leverage`;
- `cash_conversion`;
- `balance_sheet_strength`;
- `capital_allocation`;
- `product_cycle`;
- `customer_or_channel_signal`;
- `competitive_position`;
- `supply_chain_dependency`;
- `regulatory_or_geopolitical_risk`;
- `management_guidance`;
- `expectations_gap`;
- `valuation_context`;
- `catalyst_path`;
- `risk_factor`;
- `falsifier`;
- `cannot_know_boundary`.

Firewall rules:

- `company_filing` can support `business_model`, `segment_mix`, `risk_factor`, `cash_conversion`, `balance_sheet_strength`, and `capital_allocation`.
- `earnings_release` can support `revenue_growth_quality`, `margin_structure`, `management_guidance`, `segment_mix`, and disclosed `catalyst_path`.
- `earnings_call_transcript` can support `management_guidance`, `product_cycle`, `customer_or_channel_signal`, and `competitive_position`, but promotional statements require lower confidence unless corroborated.
- `investor_presentation` can support management framing and product roadmap claims, but not independent TAM validation.
- `market_data_surface` can support `valuation_context`, `expectations_gap`, and market-implied risk, but not operating facts.
- `external_news` can support event timeline and counter-evidence; structural claims need primary-source support.
- `alternative_or_channel_data` can support `proxy_inferable` claims only unless the source has audited or primary status.

## 7. Source Card Pattern

`CompanySourceCard` should be generated only after `domain_route` selects the listed company expert.

Minimum fields:

```yaml
object_type: CompanySourceCard
expert_id: listed_company_expert
expert_version: v0
asset_key: equity_<ticker_or_company_slug>
source_ref: data/research/messages/<research_id>/read_content.md
source_class: company_filing | earnings_release | earnings_call_transcript | investor_presentation | market_data_surface | external_news | alternative_or_channel_data
source_authority: primary_company | primary_regulator | market_data | third_party_reporter | alternative_proxy
time_semantics:
  reported_period:
  published_at:
  filed_at:
  observed_at:
company_scope:
  ticker:
  issuer_name:
  cik:
  exchange:
  fiscal_period:
  segment_scope:
key_facts: []
management_claims: []
market_claims: []
external_claims: []
missing_context: []
claim_candidates: []
blocked_uses: []
source_span_refs: []
```

The source card should preserve what the source can prove and what it cannot prove before synthesis begins.

## 8. Typed Claim Pattern

Minimum fields:

```yaml
object_type: CompanyTypedClaim
claim_id:
source_card_id:
asset_key:
source_class:
claim_type:
permission_level: publicly_observable | proxy_inferable | not_knowable_from_public_data
claim:
elaboration:
time_validity:
confidence:
confidence_cap_reason:
metrics:
  period:
  value:
  unit:
  comparator:
  source_basis:
counterevidence_needed: []
falsifiers: []
source_span_refs: []
downstream_allowed_use: []
downstream_blocked_use: []
```

`confidence_cap_reason` is mandatory when a claim comes from management framing, alternative data, sell-side commentary, or market-implied interpretation.

## 9. `single_asset_dossier`

The dossier is a structured expert artifact, not a final PM instruction.

Minimum sections:

1. `Identity And Scope`
   - issuer, ticker, exchange, CIK where available, fiscal calendar, asset workspace path, route template.
2. `Business Shape`
   - business model, segment mix, unit economics if available, customer/channel exposure.
3. `Recent Operating Evidence`
   - revenue, margins, cash flow, guidance, one-time items, segment deltas, product-cycle facts.
4. `Market And Expectation Context`
   - price behavior, valuation multiples, relative strength, IV/skew when available, consensus/guidance gap when available.
5. `Catalyst Path`
   - earnings, product launches, regulatory events, customer events, capital allocation, investor day.
6. `Risk And Falsifier Map`
   - source-backed risks, blocked assumptions, measurable falsifiers.
7. `Evidence Permission Summary`
   - public facts, proxy-inferable reads, cannot-know boundaries.
8. `Downstream Handoff`
   - what can be handed to `research-single-stock-analysis`, `operation-portfolio-decision`, `research-theme-report-owner`, or Expert Factory.

Required artifact metadata:

```yaml
object_type: single_asset_dossier
expert_id: listed_company_expert
route_template: default_company_dossier
asset_key:
generated_at_utc:
source_packet_id:
included_source_card_ids: []
included_claim_ids: []
key_uncertainties: []
blocked_assumptions: []
downstream_allowed_use: []
downstream_blocked_use: []
```

## 10. Template Extensions

The default listed company expert should be conservative and cross-sector.

Industry or business-model templates belong under:

```text
company_template:<template_id>
```

Candidate templates:

- `company_template:ai_infrastructure_platform`;
- `company_template:semiconductor_cycle`;
- `company_template:consumer_brand`;
- `company_template:financial_institution`;
- `company_template:biotech_clinical_stage`;
- `company_template:commodity_producer`;
- `company_template:marketplace_or_platform`;
- `company_template:software_saas`.

Template admission requires:

- repeated use across more than one company or one durable coverage need;
- source classes that differ materially from the default listed-company expert;
- claim types or confidence caps that the default expert cannot express cleanly;
- a dossier section that changes PM judgment rather than only changing formatting.

## 11. NVIDIA Dogfood Source Shape

NVIDIA is a useful dogfood case because it stresses the listed-company expert in four ways:

- official company materials contain both hard operating facts and promotional AI-infrastructure framing;
- segment mix is dominated by Data Center, so the expert must not overweight older Gaming identity;
- export controls and supply commitments create regulatory and supply-chain claims that need filing-level support;
- market expectations can be far ahead of reported fundamentals, so market data and valuation context must stay separate from business facts.

Source classes:

| Source | Source class | What it can support | What it cannot support alone |
|---|---|---|---|
| NVIDIA FY2025 Annual Report / Form 10-K | `company_filing` | FY2025 revenue, segment mix, risk factors, supply chain, export-control risk | near-term demand certainty |
| NVIDIA Q1 FY2026 earnings release | `earnings_release` | Q1 revenue, Data Center revenue, H20 charge, gross margin bridge, Q2 guide | durable margin normalization |
| NVIDIA earnings call transcript | `earnings_call_transcript` | management explanation and analyst pressure points | audited operating facts not in filings |
| NVIDIA investor company overview | `investor_presentation` | platform framing, CUDA / Blackwell / AI factory narrative, product roadmap | independent TAM validation |
| Price / valuation / technical packet | `market_data_surface` | market expectations, trend, volatility, valuation context | business quality |
| Customer, hyperscaler, export-control, and supply-chain reports | `external_news` | event timeline and corroboration pressure | definitive customer volume or margin impact |

Example claims:

```yaml
- claim_type: revenue_growth_quality
  permission_level: publicly_observable
  claim: NVIDIA reported Q1 FY2026 revenue of $44.1B, up 69% year over year.
  source_class: earnings_release
  allowed_use: recent operating evidence

- claim_type: segment_mix
  permission_level: publicly_observable
  claim: Data Center revenue was $39.1B in Q1 FY2026, far larger than Gaming and other reported segments.
  source_class: earnings_release
  allowed_use: business shape and segment priority

- claim_type: regulatory_or_geopolitical_risk
  permission_level: publicly_observable
  claim: The H20 export licensing requirement created a $4.5B Q1 FY2026 charge and blocked additional H20 shipments.
  source_class: earnings_release
  allowed_use: risk and margin normalization analysis

- claim_type: product_cycle
  permission_level: proxy_inferable
  claim: Blackwell full-scale production and cloud availability indicate a major product-cycle transition.
  source_class: earnings_release
  confidence_cap_reason: management and launch data show transition, but customer-level economics require corroboration.
  allowed_use: catalyst path

- claim_type: cannot_know_boundary
  permission_level: not_knowable_from_public_data
  claim: Public materials do not reveal undisclosed customer-specific purchase commitments or actual hyperscaler deployment economics.
  source_class: investor_presentation
  allowed_use: blocked assumption
```

## 12. Relationship To Existing Workflows

### 12.1 `research-single-stock-analysis`

`research-single-stock-analysis` remains the PM-facing ticker-first analysis workflow. It may consume `single_asset_dossier` as a structured source of company facts, operating questions, and evidence gaps.

The listed company expert does not replace ticker analysis because it does not decide:

- whether the stock should be bought, held, reduced, or avoided;
- how the position fits the current book;
- whether technical state confirms or rejects entry;
- whether a macro or theme overlay should dominate the read.

### 12.2 Theme / Thesis

A listed-company dossier can feed theme or thesis work when the company is evidence for a broader mechanism. The listed company expert should emit promotion candidates, not activate lifecycle state.

Example:

```text
NVDA Data Center margin normalization
  -> possible AI infrastructure theme evidence
  -> theme owner decides whether to consume
```

### 12.3 Private Company Expert

The listed company expert and private company expert share evidence-permission discipline but diverge after routing.

Listed-company research centers on filings, earnings, public market data, transcripts, guidance, and public equity expectations. Private-company research centers on unit of account, private pricing surfaces, primary rounds, fund marks, transfer constraints, and public-comp calibration.

### 12.4 Crypto Project Expert

The crypto expert and listed company expert share the evidence permission layer but diverge after routing.

Listed-company research centers on filings, accounting, segments, management guidance, and market expectations. Crypto research centers on token supply, protocol usage, exchange/liquidity structure, reflexive market behavior, and public-data limitations.

## 13. Validation Gates

A listed company expert output is invalid if:

- it lacks a `domain_route`;
- it produces Source Cards before listed-company route selection;
- it mixes market price action into operating facts;
- it treats management TAM claims as independently validated facts;
- it assigns portfolio action or position sizing;
- it omits evidence permission levels;
- it omits confidence caps for proxy or management-framed claims;
- it cannot point each claim back to source spans;
- it forces thesis/theme output for a single-company research request;
- it handles private-company pricing surfaces instead of routing to `digestion_41_1_private_company_expert.md`.

Minimum dogfood:

```text
./.venv/bin/python -m src.cli.tradectl digestion independent-research init --asset-key equity_nvda --asset-type listed_equity --display-name "NVIDIA" --primary-symbol NVDA
./.venv/bin/python -m src.cli.tradectl digestion independent-research link --asset-key equity_nvda --research-id <message_id>
./.venv/bin/python -m src.cli.tradectl digestion independent-research build-source-packet --asset-key equity_nvda --research-question "Assess NVIDIA as a single-company research target" --selected-route company_expert --template-id default_company_dossier
```

The deterministic loop only creates the workspace, source links, source packet, and route. A future listed-company expert writer generates `CompanySourceCard`, `CompanyTypedClaim`, and `single_asset_dossier` from that packet.

## 14. Source Notes

External and local references used by this design:

- NVIDIA FY2025 Annual Report / Form 10-K, official investor PDF and SEC filing.
- NVIDIA Q1 FY2026 earnings release, official NVIDIA newsroom and SEC-filed press release.
- NVIDIA investor company overview presentation.
- `designDoc/learning_library/repo_notes/public_trading_skills_landscape.md`, especially `us-stock-analysis` as a public single-stock skill counterpart.
- `designDoc/learning_library/projects/agentic_finance_data_stack/data_needs.md`, especially equity fundamentals, filings/news, estimates/transcripts/guidance.
- `data/analysis/interpretation_frameworks/consumer_demand_sensing_expert.md`, especially the evidence ladder that separates taste signal, proxy support, and issuer / retailer / external corroboration.
