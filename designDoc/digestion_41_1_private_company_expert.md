---
title: Private Company Expert
status: active_draft
reader_persona:
  - System Builder
  - Research Architect
  - Private Company Analyst
  - Independent Research Orchestrator
---

# Private Company Expert

## 1. Purpose

`Private Company Expert` is the Digestion-layer expert for one private operating company, pre-IPO issuer, or private-company exposure.

It turns a routed private-company `source_packet` into private-company Source Cards, typed claims, and a `private_company_dossier`. It is not the same object as `research-single-stock-analysis`, `operation-portfolio-decision`, private-market trading advice, or portfolio allocation.

Private-company research has a different semantic problem from listed-company research:

- there may be no audited public filing package;
- operating-company value and instrument-specific security price are different objects;
- primary-round valuation, common-share secondary price, SPV all-in price, platform indicative price, tender price, and fund mark are not interchangeable;
- secondary-market prices stale quickly and may not represent completed transfers;
- transfer restrictions, ROFR, share-class rights, fees, and liquidity constraints can change the claim being made;
- valuation requires public-comp calibration, private-round calibration, and explicit confidence caps.

## 2. Reader End-State

After reading a `private_company_dossier`, the downstream analyst should be able to state:

- what operating company is being researched;
- what exact security, instrument, exposure, or pricing surface is being interpreted;
- which facts are issuer-disclosed, which are third-party research, which are platform pricing surfaces, and which are not knowable from public data;
- whether a quoted private price refers to enterprise value, preferred-round valuation, common-share PPS, SPV all-in price, indicative platform price, tender price, or fund mark;
- how public comps and private rounds calibrate the possible valuation range;
- which assumptions are blocked because the source packet lacks audited financials, cap table, liquidation preferences, transfer approval information, or real matched transaction detail;
- what may be handed to PM-facing workflows and what must stay blocked.

Silent violation:

```text
The dossier says a private company is "down" or "cheap" but does not name the pricing surface, share class, all-in fee treatment, timestamp, liquidity, and comp basis.
```

That is price-label laundering, not research.

## 3. Layer Boundary

The route is:

```text
Independent Research Orchestrator
  -> canonical message archive
  -> asset source packet
  -> domain_route:
       default: private_company_expert
       compatibility: company_expert:private_company_dossier
  -> PrivateCompanySourceCard
  -> PrivateCompanyTypedClaim
  -> private_company_dossier
  -> optional downstream handoff
```

The independent researcher owns source collection, archiving, linking, packet assembly, run logs, and route selection. The private company expert owns private-company interpretation objects and evidence firewalls.

Method learning is a separate path:

```text
routing-task-mode-router
  -> research-external-learning
```

Use it only when the private-company method is missing, stale, or being updated. A concrete private-company run should enter `digestion-independent-researcher` directly once this method exists.

Blocked outputs:

- buy / sell / hold instruction;
- position sizing;
- private-share transaction recommendation;
- claim that a secondary-market price proves business quality;
- claim that a preferred-round valuation equals current common-share fair value;
- thesis activation;
- theme priority update;
- public ticker recommendation for a comp.

Allowed downstream handoff:

- `research-single-stock-analysis` only for public comp ticker interpretation;
- `operation-portfolio-decision` only when the user asks about book action and the asset is actually investable in the user's mandate;
- `research-theme-report-owner` only when the private-company claim becomes evidence for a broader theme;
- `Digestion Expert Factory` when the template needs runtime/schema work.

## 4. Source Classes

### 4.1 `issuer_voluntary_disclosure`

Examples:

- issuer press release;
- investor update;
- company blog with financial metrics;
- founder / executive interview with operating metrics.

Allowed claim support:

- stated revenue / ARR / run-rate;
- stated growth rate;
- stated NRR / NDR;
- stated FCF status;
- stated customer count or product run-rate;
- stated financing round details.

Blocked support:

- audited financial quality unless audited;
- full margin structure unless disclosed;
- current common-share fair value;
- cap table and liquidation stack unless disclosed.

Confidence cap:

- issuer voluntary disclosure is `publicly_observable` for what the issuer stated;
- downstream business-quality claims remain capped when metrics are unaudited, non-GAAP, or unreconciled.

### 4.2 `primary_round_disclosure`

Examples:

- company funding announcement;
- credible news report of priced round;
- investor announcement;
- filed certificate / financing document when available.

Allowed claim support:

- round size;
- post-money valuation;
- lead investors;
- preferred-round price when disclosed;
- approximate valuation timestamp.

Blocked support:

- common-share fair value without share-class adjustment;
- current fair value after market movement without calibration;
- liquidation preference economics unless terms are disclosed.

### 4.3 `secondary_market_surface`

Examples:

- Forge Price;
- Hiive Price;
- highest bid;
- lowest ask;
- last matched;
- platform indicative price;
- SPV all-in price;
- tender price.

Allowed claim support:

- observed pricing surface;
- signal type and timestamp;
- platform liquidity context;
- bid / ask / listing / match distinction when provided.

Blocked support:

- business quality;
- completed transfer certainty;
- final settlement price when only indicative;
- universal company valuation without share-class and fee normalization.

### 4.4 `fund_mark_surface`

Examples:

- mutual fund / crossover fund mark;
- private fund NAV disclosure;
- holding value in a public fund report;
- valuation committee mark.

Allowed claim support:

- one holder's mark or implied exposure value;
- mark direction and timing;
- calibration point for valuation range.

Blocked support:

- public-market clearing price;
- definitive company-wide fair value;
- current transaction price.

### 4.5 `public_comp_surface`

Examples:

- public comp earnings release;
- 10-K / 10-Q;
- public market EV / revenue;
- public SaaS multiple benchmark;
- market-data feed for comp valuation.

Allowed claim support:

- public-comp revenue, growth, NRR / NDR, margin, FCF, and valuation context;
- calibration baseline;
- multiple compression or expansion context.

Blocked support:

- private-subject fundamentals;
- private-subject share-class value;
- direct cheap / expensive conclusion without private-subject evidence.

### 4.6 `third_party_private_research`

Examples:

- Sacra;
- private-market data vendor writeup;
- industry research note;
- credible financial press with private-company estimates.

Allowed claim support:

- proxy operating estimate;
- source-disclosed methodology;
- cross-check against issuer data;
- product mix or market context when sourced.

Blocked support:

- primary-source certainty;
- audited financial claims;
- portfolio action.

### 4.7 `company_filing:private_issuer_voluntary`

Use this subtype when a private company provides filing-like disclosure without the legal status of public-company SEC filings.

Allowed support is source-specific. The dossier must preserve whether the document is audited, unaudited, management-prepared, lender-facing, investor-facing, or regulatory.

## 5. Evidence Permission Layer

Every private-company claim must carry one permission level.

```text
publicly_observable
  The source directly reports the fact or visible pricing surface.

proxy_inferable
  The source does not directly prove the fact, but a bounded proxy supports a directional read.

not_knowable_from_public_data
  The question matters, but the current public source packet cannot answer it.
```

Examples:

- Databricks stated it crossed a `$4.8B` revenue run-rate in Q3 2025: `publicly_observable` for issuer statement, confidence-capped for audited revenue quality.
- A Forge Price is `$196.31` on a given retrieval date: `publicly_observable` for platform-displayed pricing surface, blocked for business quality.
- Employee selling pressure explains secondary-market softness: `not_knowable_from_public_data` unless sourced.

## 6. Claim-Type Firewall

Core claim families:

- `company_identity`;
- `unit_of_account`;
- `instrument_or_share_class`;
- `issuer_operating_metric`;
- `revenue_growth_quality`;
- `retention_quality`;
- `margin_or_cash_conversion`;
- `product_mix`;
- `primary_round_valuation`;
- `secondary_pricing_surface`;
- `fund_mark_context`;
- `public_comp_calibration`;
- `valuation_bridge`;
- `liquidity_constraint`;
- `transfer_restriction`;
- `transaction_close_risk`;
- `cap_table_boundary`;
- `cannot_know_boundary`;
- `downstream_handoff`.

Firewall rules:

- `issuer_voluntary_disclosure` can support stated operating metrics but needs confidence caps when unaudited.
- `primary_round_disclosure` can support funding-round valuation, not common-share fair value without calibration.
- `secondary_market_surface` can support observed pricing-surface claims, not business-quality claims.
- `fund_mark_surface` can support one holder's mark, not a public-market clearing price.
- `public_comp_surface` can support valuation context and calibration, not private-subject operating facts.
- `third_party_private_research` supports `proxy_inferable` claims unless it quotes or links primary data.

## 7. Source Card Pattern

`PrivateCompanySourceCard` should be generated only after route selection.

Minimum fields:

```yaml
object_type: PrivateCompanySourceCard
expert_id: private_company_expert
expert_version: v0
asset_key: private_<company_slug>
source_ref: data/research/messages/<research_id>/read_content.md
source_class: issuer_voluntary_disclosure | primary_round_disclosure | secondary_market_surface | fund_mark_surface | public_comp_surface | third_party_private_research | company_filing:private_issuer_voluntary
source_authority: issuer | regulator | platform | third_party_research | fund_holder | public_comp | financial_press
time_semantics:
  reported_period:
  measurement_date:
  observed_at_utc:
  source_publication_date:
  retrieved_at_utc:
company_scope:
  legal_name:
  aliases: []
  private_public_status: private
unit_of_account:
  object_type: enterprise_value | preferred_round_valuation | common_share_pps | spv_all_in_price | indicative_platform_price | tender_price | fund_mark
  share_class:
  fee_treatment:
  transfer_constraints:
key_facts: []
pricing_signals: []
operating_metrics: []
public_comp_context: []
missing_context: []
claim_candidates: []
blocked_uses: []
source_span_refs: []
```

## 8. Typed Claim Pattern

Minimum fields:

```yaml
object_type: PrivateCompanyTypedClaim
claim_id:
source_card_id:
asset_key:
source_class:
claim_type:
allowed_use: evidence | background | trigger | candidate_only | blocked
package_use_override: evidence | background | trigger | candidate_only | blocked
permission_level: publicly_observable | proxy_inferable | not_knowable_from_public_data
claim:
elaboration:
time_validity:
confidence:
confidence_cap_reason:
unit_of_account:
metrics:
  period:
  value:
  unit:
  source_basis:
calibration_refs: []
counterevidence_needed: []
falsifiers: []
source_span_refs: []
downstream_allowed_use: []
downstream_blocked_use: []
why_it_matters_for_pm:
must_not_say:
```

`confidence_cap_reason` is mandatory for third-party estimates, management-prepared metrics, platform-derived prices, fund marks, and any claim that translates one unit of account into another.
`allowed_use` is the upstream eligibility field consumed by downstream report-package builders. It must be authored by the expert output and must not be invented by the package layer. `package_use_override` may only preserve or narrow `allowed_use`; it cannot turn a `background`, `candidate_only`, or `blocked` claim into `evidence`.

## 9. `private_company_dossier`

The dossier is a structured expert artifact, not a final PM instruction.

Minimum sections:

1. `Identity And Unit Of Account`
   - legal name, aliases, private status, asset key, exposure or instrument, share class, fee treatment, and transfer restrictions.
2. `Source And Pricing Surface Map`
   - issuer disclosures, primary rounds, secondary-market surfaces, fund marks, public comps, third-party research, and source freshness.
3. `Operating Evidence`
   - revenue / ARR / run-rate, growth, NRR / NDR, gross margin, FCF, customer count, product mix, runway, cash, debt, and explicit blocked fields.
4. `Public Comp Calibration`
   - selected public comps, comparability rationale, revenue scale, growth, retention, margin, FCF, EV / revenue, and multiple trend.
5. `Valuation Bridge`
   - primary-round valuation, public-comp multiple, premium / discount adjustments, liquidity and information asymmetry, share-class adjustment, and confidence caps.
6. `Liquidity And Transfer Constraints`
   - ROFR, approval, lock-up, settlement risk, bid / ask / match status, and whether a displayed price can close.
7. `Evidence Permission Summary`
   - public facts, proxy-inferable reads, cannot-know boundaries.
8. `Cannot-Know Boundaries`
   - cap table, liquidation preferences, common-vs-preferred fair value, employee selling pressure, transfer approval probability, undisclosed customer concentration, audited margin.
9. `Downstream Handoff`
   - what can be handed to public comp single-stock analysis, theme work, PM decision, or further source collection.

Required artifact metadata:

```yaml
object_type: private_company_dossier
expert_id: private_company_expert
route_template: private_company_dossier
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

## 10. Public-Comp Calibration Template

Private-company research should use public comps as a calibration surface, not as a shortcut to a conclusion.

1. Public comp baseline
   - Capture closest public comps with revenue, YoY growth, NRR / NDR, gross margin, free-cash-flow margin, share count, enterprise value, EV / revenue, and EV / forward revenue.
   - Source class: `public_comp_surface`.

2. Private subject scope
   - Capture disclosed or externally estimated revenue / ARR, growth, period, product mix, profitability status, and confidence cap.
   - Issuer disclosure is strongest; third-party research stays `proxy_inferable` until primary-source support exists.

3. Premium / discount bridge
   - Start from the public comp multiple.
   - Adjust for growth-quality premium, retention gap, profitability gap, scale, information asymmetry, liquidity discount, and share-class / unit-of-account differences.
   - Each adjustment carries a `permission_level` and `confidence_cap_reason`.

4. Cross-check against private pricing surfaces
   - Compare the bridge-implied range with latest primary round, secondary-market surfaces, tender prices, fund marks, and SPV all-in prices.
   - Reconcile signal type, timestamp, share class, fees, and transfer restrictions before comparing numbers.

5. Output gate
   - If the bridge and observed pricing surfaces overlap, the dossier may state that observed private pricing is directionally consistent with the documented assumptions.
   - If they diverge, the dossier states which side moved: public multiple compression, operating momentum, liquidity discount, share-class discount, information gap, or stale source.
   - The dossier does not output buy / sell / position-size language.

## 11. Local Workflow Contract

Concrete private-company research path:

```text
routing-task-mode-router
  -> digestion-independent-researcher
       step a: archive_message_create -> data/research/messages/<research_id>/{message.json, raw_payload.*, content_selection.json, read_content.md}
       step b: asset_source_link -> sources.jsonl rows resolve through messages_index.jsonl
       step c: asset_source_packet_build + domain_route_select
  -> private_company_expert or company_expert:private_company_dossier
  -> private_company_dossier
  -> research-single-stock-analysis (public-comp ticker interpretation only)
  -> operation-portfolio-decision (only on PM request)
```

Minimum artifact path:

```text
data/research/messages/<research_id>/
  message.json
  raw_payload.*
  content_selection.json
  read_content.md

data/digestion/independent_research/assets/private_<company_slug>/
  asset.json
  sources.jsonl
  source_packet.md
  source_packet.json
  domain_route.json
  run_log.jsonl
  expert_outputs/private_company_expert/
    source_cards/
    claims/
    artifacts/private_company_dossier.md
```

Raw secondary-market quotes, primary-round disclosures, public-comp snapshots, and issuer / third-party research first become canonical message archives under `data/research/messages/<research_id>/`. The asset workspace links those sources and builds packets; it does not become a second raw archive root.

Compatibility does not change the semantic output path. Even when runtime invocation uses `selected_route: company_expert` with `template_id: private_company_dossier`, private-company expert artifacts should project under `expert_outputs/private_company_expert/`. Record the compatibility execution surface in metadata, for example `invoked_route: company_expert`, `template_id: private_company_dossier`, and `contract_expert_id: private_company_expert`.

Every current runtime operation such as `archive_message_create`, `asset_source_link`, `asset_source_packet_build`, and `domain_expert_invoke` writes a `run_log.jsonl` row. `domain_route_select` is a design-level operation; current runtime may emit route selection inside `asset_source_packet_build`.

## 12. Relationship To Company Expert

`digestion_41_company_expert.md` owns the company expert family boundary. `digestion_41_2_listed_company_expert.md` owns listed-company research where filings, earnings, market data, and public equity context dominate.

This document owns private-company research where unit of account, secondary pricing surface, transfer restriction, private-round calibration, and cannot-know fields dominate.

Runtime should use `selected_route: private_company_expert` with `template_id: private_company_dossier`. Compatibility packets may still use `selected_route: company_expert` with `template_id: private_company_dossier`; the design responsibility lives here so private-company behavior does not overload the listed-company expert.

## 13. Dogfood Project

The concrete Databricks / Snowflake dogfood project lives in:

```text
designDoc/learning_library/projects/databricks_private_company_research/README.md
```

That project tests this expert contract. It is not the identity of the expert.

## 14. Validation Gates

A private-company expert output is invalid if:

- it skips the canonical message archive and stores raw source only in the asset workspace;
- it lacks a `domain_route`;
- it does not identify the unit of account;
- it compares preferred-round valuation, common-share PPS, SPV all-in price, and platform indicative price as if they were the same object;
- it treats a secondary-market surface as proof of business quality;
- it treats issuer voluntary disclosure as audited public-company filing evidence;
- it omits transfer restrictions, share-class caveats, or fee treatment when interpreting price;
- it omits evidence permission levels;
- it omits confidence caps for third-party estimates, platform prices, and issuer voluntary metrics;
- it assigns portfolio action or position sizing;
- it cannot point each claim back to source spans.

## 15. Source Notes

Method provenance:

- `designDoc/learning_library/topics/private_company_research.md`
- IPEV 2025 Valuation Guidelines.
- KPMG IPEV 2025 clarification note.
- Forge private-market pricing education.
- EquityZen secondary deal pricing education.
- Carta and ESO Fund secondary transaction explainers.
- SaaS Capital private SaaS valuation framework.
- Jarsy private-company operating metric primer.
