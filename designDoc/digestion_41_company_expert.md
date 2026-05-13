---
title: Company Expert Family
status: active_draft
reader_persona:
  - System Builder
  - Research Architect
  - Domain Expert Designer
---

# Company Expert Family

## 1. Purpose

`Company Expert` is the Digestion-layer family contract for company research.

It does not own one full company-analysis methodology by itself. It routes company-like research targets into the correct expert and keeps the shared boundaries between:

- listed-company research;
- private-company research;
- future company variants such as banks, insurers, biotech clinical-stage issuers, funds, holding companies, or SPAC / de-SPAC entities.

The family exists because "company" is a useful high-level research object but not a sufficient evidence model. A public operating company and a private company have different source surfaces, pricing semantics, disclosure reliability, and cannot-know boundaries.

## 2. Reader End-State

After reading this document, the system builder should know:

- when a request belongs to the company expert family;
- which child expert should own the actual Source Cards, typed claims, and dossier;
- which shared evidence rules apply across child experts;
- when a new child expert or template is justified;
- where not to put PM-facing portfolio decisions, theme maintenance, or generic source ingestion.

This file is intentionally an umbrella. For executable domain contracts, read the child expert docs.

## 3. Child Experts

| Target | Canonical expert doc | Primary artifact | Current runtime route |
|---|---|---|---|
| Listed public company / public equity issuer | [`digestion_41_2_listed_company_expert.md`](digestion_41_2_listed_company_expert.md) | `single_asset_dossier` | default compatibility `company_expert` with `template_id: default_company_dossier`; explicit `listed_company_expert` route accepted |
| Private company / pre-IPO company / secondary-market issuer | [`digestion_41_1_private_company_expert.md`](digestion_41_1_private_company_expert.md) | `private_company_dossier` | default `private_company_expert`; compatibility `company_expert` with `template_id: private_company_dossier` |

Future company experts should be admitted only when the default listed or private expert cannot express the source surface and claim firewall without distortion.

## 4. Routing Contract

The company family sits downstream of the Independent Research Orchestrator.

```text
Independent Research Orchestrator
  -> asset workspace
  -> archived raw sources and message links
  -> source_packet
  -> domain_route
  -> child company expert
  -> source cards / typed claims / dossier
  -> optional PM-facing analyst workflow
```

The family-level router should decide the child expert from explicit structured facts whenever possible:

- `asset_type`;
- `selected_route`;
- `template_id`;
- exchange / listing status;
- source classes present in the packet;
- requested output artifact.

Do not infer private-versus-listed status from marketing names alone. If listing status is unclear, the orchestrator should mark the route as unresolved and ask for clarification or source evidence.

Current route compatibility:

```yaml
listed_company:
  asset_type: listed_equity
  selected_route: company_expert
  template_id: default_company_dossier
  explicit_selected_route: listed_company_expert

private_company:
  asset_type: private_company
  selected_route: private_company_expert
  template_id: private_company_dossier
  compatibility_selected_route: company_expert
```

## 5. Shared Evidence Rules

All child company experts must preserve the same high-level evidence discipline.

### 5.1 Permission Levels

Each typed claim must distinguish:

```text
publicly_observable
  The source directly reports the fact.

proxy_inferable
  The source does not directly report the fact, but a bounded proxy supports a directional read.

not_knowable_from_public_data
  The question matters, but the available source packet cannot answer it.
```

Child experts may add tighter confidence caps, but they should not weaken these three levels.

### 5.2 Claim Provenance

Every operational claim should point back to:

- `source_ref`;
- source class;
- source authority;
- source span or quote where available;
- time semantics;
- confidence cap where the source cannot prove the full claim.

### 5.3 Market And Business Separation

Market price, public comparables, private marks, secondary indications, and valuation multiples can describe pricing surfaces and expectations. They do not by themselves prove operating quality.

Operating facts, product claims, customer signals, regulatory risk, and guidance need their own source support.

### 5.4 Portfolio Boundary

Company experts do not emit buy / sell / hold, target weights, hedge actions, or execution instructions. Those belong to PM-facing analyst and portfolio workflows.

## 6. Child Expert Responsibilities

Child experts own:

- source-class taxonomy;
- Source Card schema details;
- typed-claim claim families and claim firewall;
- dossier shape;
- source-specific confidence caps;
- route template defaults;
- dogfood source maps;
- validation gates.

The umbrella owns:

- the family routing contract;
- shared evidence permission semantics;
- admission criteria for new company child experts;
- cross-reference hygiene across Digestion docs.

## 7. Admission For New Company Experts

Create a new child expert only when all are true:

- the target is still company-like, not a theme, crypto protocol, macro event, or portfolio action;
- the default listed and private experts would misrepresent the source surface;
- the new expert requires materially different source classes or claim-type firewalls;
- the output artifact changes downstream judgment, not only section naming;
- the route can be expressed in `domain_route.json` and source-packet metadata.

Do not create a child expert only because:

- one company is important;
- a report should look different;
- the request needs deeper research but uses the same source classes;
- the difference can be handled by an industry template.

Use a `company_template:<template_id>` inside a child expert before creating a new expert.

## 8. Boundaries With Adjacent Workflows

### 8.1 Independent Researcher

`digestion-independent-researcher` owns external collection, raw archive, indexing, message links, source-packet assembly, and route selection.

The company family begins after route selection. It does not search the web or bypass the archive.

### 8.2 Research Single Stock Analysis

`research-single-stock-analysis` is the PM-facing analyst layer for public tickers. It may consume `single_asset_dossier` from the listed-company expert, but it owns the final ticker read, PM judgment, and portfolio relevance framing.

### 8.3 Private Company Research

Private-company methodology lives in [`digestion_41_1_private_company_expert.md`](digestion_41_1_private_company_expert.md). Do not keep private-company pricing-surface rules in the family doc or the listed-company doc.

### 8.4 Listed Company Research

Listed-company methodology lives in [`digestion_41_2_listed_company_expert.md`](digestion_41_2_listed_company_expert.md). Do not keep filings / earnings / transcript / public-market source rules in the family doc beyond shared routing summary.

### 8.5 Theme / Thesis / Portfolio

Company dossiers can feed theme, thesis, or portfolio workflows, but those workflows own their own admission gates and final outputs.

## 9. Minimum Validation

A company-family design or runtime change is invalid if it:

- routes private-company research through the listed-company claim firewall;
- routes listed-company filings into a private-company pricing-surface model;
- skips the independent researcher archive and source-packet boundary;
- emits PM action directly from a company expert;
- stores child-expert methodology only in the umbrella;
- creates a new child expert without a route, artifact, source-class delta, and validation gate.

## 10. Implementation Notes

Near-term runtime can keep `selected_route: company_expert` while using `template_id` to distinguish child behavior:

```yaml
default_company_dossier:
  child_contract: digestion_41_2_listed_company_expert

private_company_dossier:
  child_contract: digestion_41_1_private_company_expert
```

When runtime route dispatch is extended, the preferred explicit routes are:

```yaml
listed_company_expert:
  default_template_id: default_company_dossier

private_company_expert:
  default_template_id: private_company_dossier
```

The transition should preserve old packet readability by treating `company_expert + template_id` as a compatibility surface, not as a second canonical path.
