---
title: Expertise Overview
status: active_draft
layer: T1
created_date: 2026-05-07
reader_persona:
  - System Builder
  - Research Architect
  - Domain Expert Maintainer
  - Portfolio Manager
---

# Expertise Overview

## 1. Purpose

`Expertise` is the T1 capability-contract layer. T1 means a domain-family authority layer that downstream Design Docs, skills, packages, and runtime projections should defer to inside its scope.

It owns reusable analytical capabilities: how a domain is read, routed, inferred, aggregated, validated, and predicted.

It does not own the materialized outputs created by applying those capabilities. Materialized outputs belong to Material Catalog contracts, Digestion execution, Research belief admission, or Operation / PM workflows depending on the object.

This document admits the minimal active Expertise T1 boundary so later Expertise expansion has a canonical home. It does not migrate existing files, schemas, runtime rows, expert contracts, or skill projections.

## 2. Boundary Sentence

```text
Expertise owns reusable capability contracts.
Material Catalog owns material object contracts.
Digestion applies Expertise to source material and emits materialized outputs.
Research admits Evidence, Thesis, Scenario, and Theme belief use.
Operation / PM consumes materialized outputs for decisions.
```

PM consumes materialized outputs, not bare Expertise.

## 3. Capability Authority

Expertise owns durable capability rules such as:

- expert identity and lifecycle
- framework, lens, ontology, taxonomy, and reusable method
- source-card pattern
- source-class / claim-type firewall
- route and application grammar
- expert artifact schema
- scenario prediction framework
- validation and review policy
- generated skill projection contract

Expertise does not own:

- Raw Data
- Source Card instances
- Typed Claim instances
- Expert Artifact instances
- Evidence records
- Thesis / Theme / Scenario lifecycle admission
- Technical Report prose
- Operating Cycle Artifacts
- PM decisions or portfolio actions
- runtime code behavior
- source ingestion

## 4. Active Admission Scope

This admission is intentionally narrow:

```text
Admit Expertise as the T1 owner for reusable capability boundaries.
Do not yet split every existing Digestion expert document into expertise_* child contracts.
```

Current Digestion expert docs remain the active local projection for execution and existing schema detail. Future work may migrate durable capability content into child Expertise contracts.

Admitted child contracts:

| Contract | Purpose |
|---|---|
| [expertise_20_application_contract.md](expertise_20_application_contract.md) | Expertise Application relation: input materials, output materials, route semantics, allowed-use preservation |
| [expertise_60_prediction_framework_contract.md](expertise_60_prediction_framework_contract.md) | Thesis-anchored Scenario prediction grammar |

Remaining child-contract candidates:

| Candidate path | Purpose |
|---|---|
| `expertise_10_capability_contract.md` | reusable capability identity, lifecycle, owner, validation policy |
| `expertise_30_source_understanding_patterns.md` | source-card pattern, resource-card / angle-card pattern, source-class taxonomy |
| `expertise_40_claim_firewall_contract.md` | source-class x claim-type permission and confidence caps |
| `expertise_50_expert_artifact_schema_contract.md` | dossier / state-map / transmission-chain / impact-pool schema authority |
| `expertise_90_skill_projection_contract.md` | generated skill projection and stale projection rules |

These remaining child paths are not admitted by this overview.

## 5. Capability To Material Flow

Core equations:

```text
Expertise + source material -> Source Card
Expertise + Source Card / Typed Claim set -> Expert Artifact
Expertise + Thesis -> Scenario
Expertise + Theme / Thesis / Portfolio Context + material refs -> Decision Brief / Portfolio Decision support
```

Boundary constraints:

- Expertise shapes outputs; it does not become the output.
- Material Catalog defines the output object contract.
- Artifact Graph [T0-Artifact-Graph] defines node identity, dependency, provenance, freshness, and builder handles when the output is persisted or consumed as a graph-admitted artifact.
- Digestion applies selected capabilities and stores current execution artifacts.
- Research / PM admits belief use.
- PM decisions require PM-facing materialized output.

## 6. Expertise Application

`Expertise Application` is the relation between a reusable capability and a materialized output.

Minimum boundary:

```text
Expertise Application names the capability used, input materials, output materials, route/application semantics, and the allowed-use constraint that survived the application.
```

It must not:

- upgrade allowed use
- repair a source-class / claim-type firewall violation
- turn a Typed Claim into Evidence without belief_delta
- turn a technical_scenario into canonical Scenario without Thesis anchor
- authorize PM action

Admitted child contract: Expertise Application Contract [Expertise-Application].

Runtime persistence remains deferred. The child contract owns the relation boundary and bounded metadata / reasoning prose split; it does not create a runtime schema by itself. The older candidate field family in `designDoc/temp/material_layer_boundary_redefinition_plan_2026_05_06.md` is now historical planning context.

## 7. Theme, Thesis, And Scenario

Expertise is especially important for forward prediction.

```text
Scenario = Thesis anchor + Expertise Application + forward prediction.
```

Examples:

- `Fed Regime Transfer`: a Fed / liquidity / rates regime capability generates path predictions against a Thesis about reaction-function transfer.
- `AI industry development`: an AI industry transmission capability generates path predictions against a Thesis about capex diffusion, bottlenecks, monetization, and adoption.

Research owns whether those predictions are admitted into belief use. Theme owns durable organization and review cadence. PM owns portfolio decision.

Expertise may also produce PM-readable support through materialized outputs such as Dossiers, State Maps, Transmission Chains, Decision Brief support, and Portfolio Impact Maps. Those outputs remain Material Catalog objects or Operating Cycle Artifacts.

## 8. Current Migration Candidates

These existing docs contain Expertise material but are not moved by this admission:

| Current doc | Current role | Future Expertise treatment |
|---|---|---|
| `digestion_30_expert_factory.md` | Digestion home for expert admission / projection | Split durable capability authority into Expertise; keep Digestion execution / projection adapter details |
| `digestion_31_expert_runtime.md` | expert runtime, routing, prompt context, `expert_contract.yaml` projection | Keep runtime mechanics outside Expertise; `expert_contract.yaml` may remain a derived routing / validation index |
| `digestion_40_entity_expert.md` | entity expert abstraction | Candidate Expertise child capability contract |
| `digestion_50_transmission_expert.md` | transmission expert abstraction | Candidate Expertise child capability contract |
| `digestion_51_*_expert.md` | AI transmission-chain experts | Candidate Expertise child contracts; Digestion execution remains local |
| `digestion_41_*_expert.md` | company expert family | Candidate Expertise child contracts; report package and research consumption remain elsewhere |
| `research_20_technical_signal_pipeline_v2.md` `technical_expert_lens` | local technical lens | Candidate future Expertise capability; current packet execution stays Research technical pipeline |

## 9. Adjacent Owners

| Adjacent layer | Relationship |
|---|---|
| Charter | Defines first-class belief objects and PM/system authority split. Expertise must not override it. |
| Material Catalog | Owns material object contracts and instance boundaries for outputs shaped by Expertise. |
| Ingestion | Produces Raw Data and Canonical Input surfaces. |
| Digestion | Applies selected Expertise capabilities to source material and owns current execution / schema detail. |
| Research | Owns Evidence admission, Thesis / Scenario / Theme belief use, and PM-facing research outputs. |
| Operation / PM | Owns PM acknowledgement, decision authority, role gates, and action workflow. |
| Artifact Graph | Owns artifact node identity, dependency closure, freshness predicates, and canonical builder admission. |

## 10. Non-Goals

- Do not migrate runtime schemas or data.
- Do not rename existing Digestion expert files in this admission.
- Do not move source ingestion into Expertise.
- Do not let Expertise own material instances.
- Do not let Expertise directly admit Evidence, Thesis, Scenario, Theme, or PM action.
- Do not make Source Card generic before domain route selection.
- Do not require a persisted Expertise Application schema before one runtime builder needs it.

## 11. Open Decisions

1. Which child Expertise contract should be admitted next: capability identity, source-understanding patterns, claim firewall, expert artifact schema, or skill projection?
2. Should `Framework Card` move from Digestion to Expertise while `Framework Route` remains Digestion execution / Expertise Application?
3. Should `expert_contract.yaml` be renamed, or remain a derived routing index?
4. Should technical expert lenses enter the same capability lifecycle as source-reading experts?
5. Should persisted Scenario require a named `prediction_framework_id` before runtime admission?
6. How should generated skills declare stale projection when the underlying capability changes?

## References

- `[T1-Material-Catalog]` [Material Catalog Overview](material_00_overview.md)
- `[Expertise-Application]` [Expertise Application Contract](expertise_20_application_contract.md)
- `[Expertise-Prediction]` [Expertise Prediction Framework Contract](expertise_60_prediction_framework_contract.md)
- `[T1-Digestion]` [Digestion Layer Overview](digestion_00_overview.md)
- `[Digestion-Expert-Factory]` [Digestion Expert Factory](digestion_30_expert_factory.md)
- `[Digestion-Structure]` [Digestion Structure Contract](digestion_10_structure_contract.md)
- `[T1-Research]` [Research Family Overview](research_00_overview.md)
- `[T0-Charter]` [Charter](the_charter.md)
- `[T0-Artifact-Graph]` [Artifact Dependency Closure Contract](the_artifact_graph.md)
