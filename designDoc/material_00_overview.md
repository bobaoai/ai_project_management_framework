---
title: Material Catalog Overview
status: active_draft
layer: T1
created_date: 2026-05-07
reader_persona:
  - System Builder
  - Research Architect
  - Domain Expert Maintainer
  - Portfolio Manager
---

# Material Catalog Overview

## 1. Purpose

`Material Catalog` is the T1 material-object boundary layer. T1 means a domain-family authority layer that downstream Design Docs, skills, packages, and runtime projections should defer to inside its scope.

It owns the asset grammar: what recognized material objects are, what each object may contain, which handoffs are allowed, and which adjacent layer is allowed to execute or admit it.

It does not own domain truth, source ingestion, reusable expert frameworks, belief admission, PM decisions, report prose, runtime code, or schema migration.

This document promotes the material boundary plan into an active DesignDoc entry. Its child contracts are admitted as active_draft DesignDocs; no runtime schemas or data migrations are changed by this admission.

## 1.5 T0 Artifact Graph Inheritance

Material Catalog is the T1 material-object specialization under Artifact Graph [T0-Artifact-Graph].

Inheritance rule:

```text
Artifact Graph owns artifact node identity, dependency edges, producer / consumer handles, freshness predicates, provenance, and graph-admitted builder rules.
Material Catalog owns material object boundary, allowed content, forbidden upgrades, handoff semantics, and child material contracts.
```

Therefore every material asset may become an Artifact Graph node when it needs production, freshness, provenance, or dependency closure. Becoming a graph node does not change what the material object is allowed to mean.

Material contracts should name the minimum metadata needed for object identity and audit, then leave writing prose enough room to carry mechanism, source voice, cannot-support nuance, examples, and reader judgment. The bounded metadata / reasoning prose split is governed by the Design Doc Review Gate Contract [T0-Doc-Review].

## 2. Boundary Sentence

```text
Material Catalog owns what a material asset is.
Ingestion owns source capture and canonical read surfaces.
Expertise owns reusable capability and projection rules.
Digestion applies Expertise to source material and emits source-understanding / expert artifacts.
Research admits Evidence, Thesis, Scenario, and Theme belief use.
Operation / PM consumes materialized outputs for decisions.
```

## 3. Asset Grammar

Use a vertical grammar instead of a flat list:

```text
Raw Data
  -> Canonical Input / Operating Cycle Artifact
  -> Source Card
  -> Expert Artifact / Evidence
  -> Thesis
  -> Scenario
  -> Theme memory / Technical Report / PM Decision
  -> Report / Package / Portfolio Decision
```

The chain is not always linear. Raw market data can feed a Data Recap, Weekly Recap, Snapshot, Portfolio Decision, or Technical Report without passing through a Source Card. A Source Card can feed Evidence without becoming Evidence. Evidence can change Thesis state without becoming the Thesis.

## 4. Top-Level Material Assets

| Asset | Boundary | Execution / domain owner | Must not do |
|---|---|---|---|
| Raw Data | Original or provider-normalized material before interpretation. | Ingestion / data infrastructure | No investment meaning, belief, or report prose. |
| Operating Cycle Artifact | Cadence-bound recap / decision material. Subtypes include `data_recap`, `weekly_recap`, `snapshot`, `decision_brief`, and `portfolio_decision`. | Data pipeline, Research reporter, Operation / PM workflow | No durable Thesis, no source-understanding card, no unanchored report prose. |
| Source Card | Source-level understanding after route selection, including source permission, cannot-support grammar, voice / source class, time semantics, allowed use, and optional resource-card / angle-card split. | Digestion executes; Expertise owns reusable card pattern / firewall | No belief delta, cross-source conviction, PM action, Thesis, or Scenario. |
| Expert Artifact | Structured expert read assembled from material inputs. Subtypes include Dossier, State Map, Regime Map, Trigger Chain, Transmission Chain, Impact Pool, and Portfolio Impact Map. | Expertise owns reusable schema / lens; Digestion or expert subsystem executes | No reusable framework ownership, raw-source authority, thesis authority, or PM decision by itself. |
| Evidence | Belief-change record linking material inputs to a Thesis / Scenario / Theme delta. | Research / PM belief workflow | No raw observation by itself, no generic source summary, no unowned belief claim. |
| Thesis | Falsifiable belief container with evidence, falsifiers, lifecycle, and review trigger. | Research | No raw-source summary, no operating-cycle recap, no report prose by itself. |
| Scenario | Forward prediction produced by applying an Expertise lens to one or more Thesis anchors. | Expertise owns prediction framework; Research / PM owns belief admission | No generic possibility prose, no unanchored narrative, no PM decision. |
| Theme | Durable research-memory object grouping mechanism, question family, assets, evidence, theses, scenarios, and update cadence. | Research | Not a source summary, immediate trade, or prediction asset itself. |
| Technical Report | PM-readable expression of current market state from signal packets, market data, chart vision, and technical setup conditions. | Research / writer pipeline | Does not own raw data truth, Source Cards, Thesis authority, Theme belief, or Scenario. |

## 5. Bridge Objects And Support Surfaces

These objects are recognized but are not promoted to top-level material assets in this pass.

| Object | Status | Boundary |
|---|---|---|
| Typed Claim | bridge contract admitted | Atomic semantic claim projected from source material into a domain claim taxonomy. It remains a bridge object, not a top-level material asset. |
| Expertise Application | relation contract admitted under Expertise | Records which Expertise capability was applied to which input materials to produce which output materials. It remains a relation, not a top-level material asset. |
| Canonical Input | support surface admitted | AI-readable / tool-readable projection of Raw Data, such as `read_content.md`, signal input tables, or canonical provider snapshots. |
| Feature | support surface admitted | Typed intermediate field extracted from Raw Data, Source Cards, Operating Cycle Artifacts, Technical Reports, Scenarios, or market packets. |
| Path Observation | Scenario-side support object admitted | Early path signal upstream of Scenario. It is not a first-class material object. |
| Freshness Event | lifecycle support object admitted | Time / freshness lifecycle event. It is not Evidence unless later reused with belief delta. |

## 6. Expertise Relation

Working decision:

```text
Expertise owns capability contract.
Material Catalog owns artifact contract.
Expertise Application links capability to materialized output.
```

Expertise carries reusable ways of seeing:

- framework
- lens
- ontology
- source-card pattern
- source-class / claim-type firewall
- route grammar
- expert artifact schema
- scenario prediction model
- validation rule

Material Catalog carries materialized instances created from those capabilities.

Key materialization paths:

```text
Expertise + source material -> Source Card
Expertise + Source Card / Typed Claim set -> Expert Artifact
Expertise + Thesis -> Scenario
Expertise + Theme / Thesis / Portfolio Context + material refs -> Decision Brief / Portfolio Decision support
```

PM consumes materialized outputs, not bare Expertise.

## 7. Expertise Application

`Expertise Application` is the relation between reusable capability and material output. It is not a top-level material asset in this phase. Its active relation contract is owned by Expertise Application Contract [Expertise-Application].

At overview level, it only needs to preserve the boundary:

```text
Expertise Application names the capability used, the input materials, the output materials, and the allowed-use constraint that survived the application.
```

Detailed relation fields belong to the Expertise child contract. Runtime relation schema remains deferred until a builder or persistent store needs it.

Rule:

```text
Expertise Application must never upgrade the allowed use of its input material.
```

If an input Source Card is `structural_only`, the application can only be background or structural. If an input source voice cannot emit a claim type under its Expertise firewall, downstream Evidence, Thesis, Scenario, or PM artifacts cannot silently repair that violation.

## 8. High-Risk Boundary Compression

Full asset boundaries are in §4 and the admitted child contracts. This section keeps only the short equations and conversion rules for objects that most often swallow each other.

Boundary equations:

```text
Source Card = source permission and source-understanding handoff.
Typed Claim = source-understanding atom projected into domain semantics.
Expert Artifact = expert-level structured read assembled from material inputs.
Evidence = material input + belief_delta + target belief object.
Scenario = Thesis anchor + Expertise Application + forward prediction.
```

Conversion rules:

1. `Source Card -> Typed Claim` is allowed only through the owning Expertise claim firewall.
2. `Typed Claim -> Evidence` requires explicit belief delta and target Thesis / Scenario / Theme refs.
3. `Source Card / Typed Claim set -> Expert Artifact` requires a named expert schema and material refs.
4. `Expert Artifact -> Decision Brief / Portfolio Decision support` requires PM-facing compression and `decision_use`.
5. `Thesis -> Scenario` requires an Expertise Application; Research can admit or reject belief use afterward.
6. `Scenario -> scenario_note` requires Research / PM admission and must not overwrite the original Scenario.

## 9. Admitted Child Contracts

These child contracts are admitted as active_draft DesignDocs:

| Contract | Purpose |
|---|---|
| [material_10_raw_data_contract.md](material_10_raw_data_contract.md) | raw material identity, provider/origin boundary, non-interpretation rule |
| [material_20_operating_cycle_artifact_contract.md](material_20_operating_cycle_artifact_contract.md) | Data Recap, Weekly Recap, Snapshot, Decision Brief, Portfolio Decision |
| [material_30_source_card_contract.md](material_30_source_card_contract.md) | Source Card / Resource Card / Angle Card boundary |
| [material_32_typed_claim_contract.md](material_32_typed_claim_contract.md) | Typed Claim bridge contract |
| [material_35_expert_artifact_contract.md](material_35_expert_artifact_contract.md) | Dossier / State Map / Transmission Chain / Impact Pool style outputs |
| [material_40_evidence_contract.md](material_40_evidence_contract.md) | belief-change record boundary |
| [material_50_thesis_contract.md](material_50_thesis_contract.md) | falsifiable belief container boundary |
| [material_60_theme_contract.md](material_60_theme_contract.md) | durable research-memory container boundary |
| [material_70_technical_report_contract.md](material_70_technical_report_contract.md) | current market-state report boundary |
| [material_80_scenario_contract.md](material_80_scenario_contract.md) | Expertise-driven forward prediction boundary |
| [material_90_support_surfaces.md](material_90_support_surfaces.md) | Canonical Input, Feature, Path Observation, Freshness Event |

## 10. Adjacent Owners

| Adjacent layer | Relationship |
|---|---|
| Charter | Defines first-class belief objects: Theme, Thesis, Scenario, Evidence, plus PM/system authority split. Material Catalog must not override it. |
| Ingestion | Produces Raw Data and Canonical Input surfaces. |
| Digestion | Executes source-understanding, Typed Claim, route, and Expert Artifact production under selected Expertise. Existing digestion docs remain execution and current schema detail owners inside admitted Material Catalog boundaries. |
| Expertise | Active T1 owner for reusable capability contracts, not material instances. |
| Research | Owns Evidence admission, Thesis / Scenario / Theme belief use, and PM-facing research outputs. |
| Operation / PM | Owns PM acknowledgement, portfolio-decision authority, role gates, and action workflow. |
| Artifact Graph | Owns T0 graph law: artifact node identity, dependency closure, freshness predicates, provenance / sidecar handles, and canonical builder admission. Material Catalog inherits those graph handles without redefining global graph law. |

## 11. Non-Goals

- Do not treat Expertise admission as runtime schema migration.
- Do not rename existing Digestion or Research files.
- Do not migrate schemas or runtime data.
- Do not make Source Card generic before domain route selection.
- Do not allow PM-facing workflows to consume bare Expertise without materialized output.
- Do not import Fed-specific video-parser object names as generic top-level assets.

## 12. Open Decisions

1. Should `Typed Claim` ever become a top-level material asset, or remain a bridge contract?
2. Should Source Card formally split into `resource_card` and `angle_card` across all domains?
3. Which Expert Artifact subtypes deserve dedicated contracts first?
4. Which runtime surface, if any, should first persist `expertise_application_id`?
5. Should Scenario Map belong under Theme, or should Theme reference Scenario / scenario_note objects owned elsewhere?

## References

- `[T0-Charter]` [Charter](the_charter.md)
- `[T1-Digestion]` [Digestion Layer Overview](digestion_00_overview.md)
- `[Digestion-Structure]` [Digestion Structure Contract](digestion_10_structure_contract.md)
- `[T1-Research]` [Research Family Overview](research_00_overview.md)
- `[Evidence-Trust]` [Evidence Source Trust Contract](evidence_source_trust_contract.md)
- `[Expertise-Application]` [Expertise Application Contract](expertise_20_application_contract.md)
- `[T0-Artifact-Graph]` [Artifact Dependency Closure](the_artifact_graph.md)
- `[T0-Doc-Review]` [Design Doc Review Gate Contract](the_design_doc_management.md)
- `[External-Video-Parser]` sibling repo precedent, not runtime dependency: `video_parser` repo, `macro_fed_kb/design/28_source_card_schema.md`, `macro_fed_kb/design/25_claim_schema.md`, and `macro_fed_kb/design/34_angle_channel_routing.md`
