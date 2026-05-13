---
title: Material Support Surfaces
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - System Builder
  - Research Architect
  - Data Infrastructure Maintainer
---

# Material Support Surfaces

## 1. Purpose

This document admits support surfaces used by material assets without promoting them to top-level material assets.

Support surfaces carry intermediate state, access, lifecycle, or route information. They do not own final authority.

## 2. Canonical Input

`Canonical Input` is an AI-readable or tool-readable projection produced from Raw Data.

Examples:

- `read_content.md`
- normalized provider snapshot
- signal input table
- cleaned transcript
- selected image evidence block

Canonical Input can feed Source Card, Operating Cycle Artifact, Technical Report, or feature extraction. It is not Evidence, Thesis, Scenario, or report prose.

## 3. Feature

`Feature` is a typed intermediate field extracted from another surface.

Primary subtypes:

| Feature subtype | Input | Meaning |
|---|---|---|
| `source_feature` | Source Card / Typed Claim / route | Semantic fact, mechanism, permission, caveat, or channel marker. |
| `market_feature` | bars / market data / chart vision / technical packet | Market state or setup extracted from price, volume, volatility, or chart structure. |
| `scenario_feature` | Scenario | Expected path marker, trigger, falsifier, lead-lag relation, or observable delta. |

Optional later subtypes:

- `portfolio_feature`
- `fundamental_feature`
- `behavioral_feature`

Rule:

```text
Feature owns intermediate state, not authority.
Authority comes from its source surface plus downstream consumer contract.
```

## 4. Path Observation

`Path Observation` is an early signal upstream of Scenario.

It can exist before a Thesis or Scenario is fully admitted, but before entering decision workflow it must bind to a Thesis, Scenario, or belief object.

Path Observation is not a first-class material object and must not become floating decision evidence.

## 5. Freshness Event

`Freshness Event` records lifecycle / freshness changes.

It is not Evidence by itself.

It becomes relevant to Evidence only when a stale object is revived or reused in a new decision and a belief_delta is recorded.

## 6. Support Surface Rules

Support surfaces must:

- name their source surface
- name their owner layer
- name their consumer contract
- avoid upgrading authority
- preserve audit path when derived from Raw Data or Canonical Input

Support surfaces must not:

- replace material assets
- create belief transitions
- hide source limitations
- authorize PM action

## 7. Open Decisions

1. Which Feature subtypes need runtime schemas first?
2. Should Path Observation become a formal Scenario child object?
3. Should Freshness Event remain only under Artifact Graph / lifecycle docs or also get material sidecar conventions?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[Raw-Data]` [Raw Data Material Contract](material_10_raw_data_contract.md)
- `[Scenario]` [Scenario Material Contract](material_80_scenario_contract.md)
- `[T0-Artifact-Graph]` [Artifact Dependency Closure](the_artifact_graph.md)
