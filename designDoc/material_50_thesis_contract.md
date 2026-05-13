---
title: Thesis Material Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - Research Architect
  - Portfolio Manager
  - Thesis Reviewer
---

# Thesis Material Contract

## 1. Purpose

`Thesis` is a falsifiable belief container.

It explains why a mechanism should hold, what evidence supports it, what would falsify it, and when it must be reviewed.

## 2. Boundary

Thesis owns:

- belief statement
- mechanism
- scope
- parent Theme ref when applicable
- supporting Evidence refs
- counter-evidence refs
- falsifiers
- lifecycle state
- review cadence
- assumptions and dependencies

Thesis does not own source summary, Source Card, Operating Cycle Artifact, Technical Report, PM decision, or Scenario path by itself.

## 3. Reader Gain

After reading a Thesis, the reader should know:

- what we currently believe
- why we believe it
- what would change our belief
- which Evidence supports or challenges it
- which Scenario paths depend on it
- what the next review trigger is

## 4. Allowed Handoffs

Thesis may feed:

- Scenario generation
- Theme organization
- PM belief review
- Evidence review
- writer packages
- portfolio decision context

Thesis may not be consumed directly as portfolio decision authority without Scenario / PM workflow where required by Charter.

## 5. Scenario Relation

```text
Thesis + Expertise Application -> Scenario
```

A Scenario must name its Thesis anchor. A Thesis can have multiple Scenarios, but a Scenario should not silently replace or mutate its Thesis.

## 6. Failure Signatures

- Thesis is a source summary.
- Thesis has no falsifier.
- Thesis has no Evidence refs or only raw source refs.
- Thesis lifecycle changes without PM acknowledgement where required.
- Portfolio decision bypasses Scenario layer and reads Thesis prose directly.

## 7. Adjacent Owners

| Owner | Relationship |
|---|---|
| Charter | Defines Thesis as first-class belief object. |
| Research | Owns thesis drafting, review, and lifecycle workflow. |
| Evidence | Supplies belief-change support or challenge. |
| Scenario | Builds forward paths from Thesis anchors. |

## 8. Open Decisions

1. Should all Thesis objects require a parent Theme?
2. Which lifecycle fields are material contract vs research schema detail?
3. How should Thesis represent unresolved objections distinct from falsifiers?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[T0-Charter]` [Charter](the_charter.md)
- `[Evidence]` [Evidence Material Contract](material_40_evidence_contract.md)
