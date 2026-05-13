---
title: Operating Cycle Artifact Material Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - System Builder
  - Research Reporter
  - Portfolio Manager
  - Operation Maintainer
---

# Operating Cycle Artifact Material Contract

## 1. Purpose

`Operating Cycle Artifact` is cadence-bound recap or decision material.

It records what changed in a bounded data window, week, snapshot, brief, or portfolio action cycle, and what operational review state that change supports.

## 2. Admitted Subtypes

| Subtype | Boundary |
|---|---|
| `data_recap` | Bounded recap of data changes, missingness, anomalies, or source updates. |
| `weekly_recap` | Weekly operating summary across relevant themes, assets, or workflows. |
| `snapshot` | Point-in-time compression of research, market, or source state. |
| `decision_brief` | PM-facing compression of material inputs for a decision context. |
| `portfolio_decision` | Record of PM / operation decision support and resulting action state. |

These subtypes are one family because they are cadence / action-cycle objects, not durable belief objects.

## 3. Required Reader Gain

After reading an Operating Cycle Artifact, the reader should know:

- the bounded period or decision cycle
- what changed
- what remained unchanged
- which material inputs were used
- which follow-up review or action state is supported
- what is stale, blocked, or unresolved

## 4. Allowed Handoffs

Operating Cycle Artifact may feed:

- Evidence drafting
- Thesis review
- Scenario review
- Theme update
- Technical Report context
- PM situational awareness
- portfolio action log

It may cite Evidence, Thesis, Scenario, Theme, Source Cards, Technical Reports, and Expert Artifacts. It must not silently mutate them.

## 5. Must Not Do

Operating Cycle Artifact must not:

- become a Source Card
- become a durable Thesis
- create an Expertise Scenario
- replace Evidence belief_delta
- authorize portfolio action without PM / Operation gate
- present generic report prose without action or freshness context

## 6. Adjacent Owners

| Owner | Relationship |
|---|---|
| Research | Produces recap / snapshot / brief surfaces when they serve research review. |
| Operation / PM | Owns decision authority and portfolio action gates. |
| Artifact Graph | Owns freshness and dependency closure when the artifact is graph-admitted. |
| Material Catalog | Owns the family boundary and subtype list. |

## 7. Open Decisions

1. Should `decision_brief` remain in this family or receive a dedicated PM-facing child contract later?
2. Should `snapshot` split into research snapshot, market update snapshot, and operating snapshot?
3. Which subtype should own Data Recap vs Weekly Recap freshness conventions?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[T0-Artifact-Graph]` [Artifact Dependency Closure](the_artifact_graph.md)
- `[T1-Operation]` [Operating Framework Governance](operation_00_operating_framework_governance.md)
