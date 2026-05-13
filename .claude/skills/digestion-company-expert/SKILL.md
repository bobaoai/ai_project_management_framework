---
name: digestion-company-expert
description: Generates company-owned Digestion outputs for one listed company from an independent-research source packet. Use after `digestion-independent-researcher` selects `company_expert` or `company_expert:default_company_dossier`, when the task needs CompanySourceCards, CompanyTypedClaims, a `single_asset_dossier`, company evidence permission boundaries, or a handoff into `research-single-stock-analysis`.
---

# Digestion Company Expert

## What This Skill Does

Use this skill after an independent company research run has a source packet and a company route.

Canonical shape:

```text
source_packet
  -> domain_route: company_expert:default_company_dossier
  -> CompanySourceCard
  -> CompanyTypedClaim
  -> single_asset_dossier
  -> downstream handoff
```

This is a Digestion expert. It explains company evidence before PM-facing report writing. It does not replace `research-single-stock-analysis`.

Projected expert metadata:

```yaml
projected_from_expert_id: company_expert
projected_from_expert_version: v0
projection_owner: digestion-expert-factory
governing_design: designDoc/digestion_41_company_expert.md
```

## Desired Result

The desired result is a source-grounded company dossier that a PM-facing analyst can consume without rereading every raw source.

By the end, it should be explicit:

- what the company does and which segment / product / customer channel matters most;
- which facts are `publicly_observable`, which are `proxy_inferable`, and which are `not_knowable_from_public_data`;
- which claims come from filings, earnings releases, transcripts, presentations, market data, external news, or alternative data;
- what the source packet can and cannot support;
- which assumptions are blocked;
- what can be handed to `research-single-stock-analysis`, `research-theme-report-owner`, `operation-portfolio-decision`, or Expert Factory.

If the output reads like an investment memo but does not expose source authority and evidence permissions, this skill has failed.

## Primary Truth Surfaces

Read first:

- `designDoc/digestion_41_company_expert.md`
- `designDoc/digestion_20_independent_researcher.md`
- the asset workspace under `data/digestion/independent_research/assets/<asset_key>/`
- `source_packet.md`
- `source_packet.json`
- `domain_route.json`

Read source bodies from:

- `data/research/messages/<research_id>/read_content.md`

Read downstream context only when needed:

- `.claude/skills/research-single-stock-analysis/SKILL.md`
- `designDoc/research_33_company_fundamentals_data_architecture.md` if fundamentals data architecture is relevant
- `designDoc/learning_library/projects/agentic_finance_data_stack/data_needs.md` for equity data-source requirements
- `designDoc/learning_library/repo_notes/public_trading_skills_landscape.md` for external single-stock skill comparison

## Entry Conditions

Enter this skill only when:

- the asset is a listed company or company-like equity research target;
- a source packet exists or the task explicitly asks to define company expert output from one;
- route is `company_expert`, `company_expert:default_company_dossier`, or a future `company_template:<template_id>`.

If route selection has not happened, return to `digestion-independent-researcher`.

If the company needs a new industry template before it can be read responsibly, return `blocked_missing_company_template` and hand off to `digestion-expert-factory`.

## Source Classes

Classify every source before making claims:

- `company_filing`
- `earnings_release`
- `earnings_call_transcript`
- `investor_presentation`
- `market_data_surface`
- `external_news`
- `alternative_or_channel_data`

Keep source authority visible:

- filings and regulator-hosted releases can support official facts;
- management materials can support management framing but not independent validation;
- market data can support expectation and tape context but not business quality;
- alternative data can support proxy reads, not audited facts;
- external news can support event discovery and counterevidence, not final structural judgment alone.

## Evidence Permission Layer

Every claim must carry one:

```text
publicly_observable
  The source directly reports the fact.

proxy_inferable
  A bounded proxy suggests a directional read, but the source does not directly prove the fact.

not_knowable_from_public_data
  The question matters, but public sources in the packet cannot answer it.
```

Do not hide cannot-know boundaries. They are part of the output quality.

## Claim-Type Firewall

Allowed company claim families:

- `business_model`
- `segment_mix`
- `revenue_growth_quality`
- `margin_structure`
- `operating_leverage`
- `cash_conversion`
- `balance_sheet_strength`
- `capital_allocation`
- `product_cycle`
- `customer_or_channel_signal`
- `competitive_position`
- `supply_chain_dependency`
- `regulatory_or_geopolitical_risk`
- `management_guidance`
- `expectations_gap`
- `valuation_context`
- `catalyst_path`
- `risk_factor`
- `falsifier`
- `cannot_know_boundary`

Rules:

- `company_filing` can support official business, segment, risk, cash-flow, balance-sheet, share-count, and capital-structure claims.
- `earnings_release` can support current-quarter metrics, segment revenue, GAAP / non-GAAP bridges, disclosed charges, and guidance.
- `earnings_call_transcript` can support management explanations and analyst pressure points, but promotional statements need confidence caps.
- `investor_presentation` can support official framing and roadmap, not independent TAM validation.
- `market_data_surface` can support `valuation_context`, `expectations_gap`, and tape / volatility context, not operating facts.
- `external_news` can support event timelines and corroboration pressure; primary-source support is needed for structural claims.
- `alternative_or_channel_data` can support `proxy_inferable` claims only unless it has primary or audited status.

## Output Artifacts

### `CompanySourceCard`

Create one source card per important source or source cluster. Preserve:

- `asset_key`
- `source_ref`
- `source_class`
- `source_authority`
- `time_semantics`
- `company_scope`
- `key_facts`
- `management_claims`
- `market_claims`
- `external_claims`
- `missing_context`
- `claim_candidates`
- `blocked_uses`
- `source_span_refs`

### `CompanyTypedClaim`

Each claim should include:

- `claim_id`
- `source_card_id`
- `asset_key`
- `source_class`
- `claim_type`
- `permission_level`
- `claim`
- `elaboration`
- `time_validity`
- `confidence`
- `confidence_cap_reason`
- `metrics` where relevant
- `counterevidence_needed`
- `falsifiers`
- `source_span_refs`
- `downstream_allowed_use`
- `downstream_blocked_use`

`confidence_cap_reason` is required for management-framed, proxy, sell-side, alternative-data, or market-implied claims.

### `single_asset_dossier`

The dossier should contain:

- `Identity And Scope`
- `Business Shape`
- `Recent Operating Evidence`
- `Market And Expectation Context`
- `Catalyst Path`
- `Risk And Falsifier Map`
- `Evidence Permission Summary`
- `Downstream Handoff`

The dossier is an expert artifact. It is not final PM action.

## Downstream Boundary

Use the two-step company research architecture:

```text
Digestion company expert
  -> company evidence and dossier

PM-facing analyst
  -> single-stock report, action framing, or portfolio handoff
```

Hand off to:

- `research-single-stock-analysis` for ticker-first report writing and action framing;
- `operation-portfolio-decision` only when the user asks about book action, sizing, hedge, reduce/add/hold, or execution preview;
- `research-theme-report-owner` only when company evidence becomes theme evidence;
- `digestion-expert-factory` when a reusable company template is missing.

## Blocked Outputs

This skill must not directly produce:

- portfolio action;
- position sizing;
- execution plan;
- active thesis lifecycle state;
- theme priority update;
- final PM-facing single-stock report as the owning analyst;
- crypto decision brief;
- macro market recap.

It may produce a `company_research_report_draft` only when explicitly requested, and it must mark the draft as company-evidence-first, not portfolio action.

## Completion Standard

A run is complete when it leaves one of:

- `single_asset_dossier`;
- `CompanySourceCard` and `CompanyTypedClaim` set ready for dossier assembly;
- `blocked_missing_source`;
- `blocked_missing_company_template`;
- `blocked_insufficient_public_data`;
- downstream handoff payload.

Minimum handoff:

```yaml
asset_key: <asset>
selected_route: company_expert:default_company_dossier
source_packet: <path>
source_cards: []
typed_claims: []
dossier: <path or none>
permission_summary:
  publicly_observable: []
  proxy_inferable: []
  not_knowable_from_public_data: []
blocked_outputs: []
downstream_next_step: <research-single-stock-analysis | operation-portfolio-decision | research-theme-report-owner | digestion-expert-factory | none>
```

## Failure Signals

Treat these as failures:

- Source Cards are generated before route selection.
- The output cites external web results that are not archived as message objects.
- Market price action is used as proof of business quality.
- Management TAM or roadmap language is treated as independently validated fact.
- Proxy data is treated as audited operating data.
- Public-data limits are omitted.
- The dossier silently becomes a buy / sell / sizing recommendation.
- The company is forced through thesis/theme when the request is single-company research.
