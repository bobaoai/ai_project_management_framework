---
title: Theme Material Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - Research Architect
  - Portfolio Manager
  - Theme Owner
---

# Theme Material Contract

## 1. Purpose

`Theme` is a durable research-memory container.

It defines a persistent question space, mechanism cluster, or opportunity domain, and organizes Thesis, Scenario, Evidence, assets, reports, and update cadence.

## 2. Boundary

Theme owns:

- scope and non-scope
- mechanism / question family
- related assets or entities
- Thesis refs
- Scenario refs or scenario-note refs
- Evidence refs
- update cadence
- open questions
- stale / active / deprecated posture
- report and package lineage

Theme does not own source summary, immediate trade action, raw data truth, or Scenario prediction by itself.

## 3. Reader Gain

After reading a Theme, the reader should know:

- what durable question is being tracked
- which beliefs and scenarios belong inside it
- what evidence has mattered
- what is currently unresolved
- when it should be revisited
- which adjacent themes or assets should not be conflated

## 4. Allowed Handoffs

Theme may feed:

- Theme report
- Thesis routing
- Scenario review
- Evidence collection tasks
- PM context
- portfolio context
- research backlog

Theme may not directly authorize portfolio action.

## 5. Scenario Relation

Theme may organize Scenario refs or scenario_note refs. It does not own Scenario lifecycle by itself unless a child contract later admits Theme-owned Scenario Map as a subtype.

## 6. Failure Signatures

- Theme is a folder of source summaries.
- Theme has no scope boundary.
- Theme silently changes Thesis or Scenario belief state.
- Theme report introduces new belief without Evidence / Thesis handoff.
- Theme absorbs adjacent theme boundaries without explicit scope decision.

## 7. Adjacent Owners

| Owner | Relationship |
|---|---|
| Charter | Defines Theme as first-class top-level memory object. |
| Research | Owns theme workflow, reports, and memory curation. |
| Thesis | Supplies belief containers inside the Theme. |
| Scenario | Supplies forward path objects or scenario notes referenced by the Theme. |

## 8. Open Decisions

1. Should Theme own Scenario Map, or only reference Scenario / scenario_note objects?
2. Should Theme have a standard scope / non-scope field contract?
3. Which Theme update events require PM acknowledgement?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[T0-Charter]` [Charter](the_charter.md)
- `[Thesis]` [Thesis Material Contract](material_50_thesis_contract.md)
- `[Scenario]` [Scenario Material Contract](material_80_scenario_contract.md)
