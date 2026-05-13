---
title: Expert Artifact Material Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - Domain Expert Maintainer
  - Research Architect
  - Portfolio Manager
---

# Expert Artifact Material Contract

## 1. Purpose

`Expert Artifact` is a structured expert read assembled from material inputs through an Expertise capability.

It is the materialized output of expert reasoning, not the reusable Expertise itself.

## 2. Boundary

Expert Artifact owns:

- structured expert read
- input material refs
- owning expert / framework refs
- Expertise Application refs
- domain schema used
- conclusions allowed by the schema
- confidence and limits
- falsifiers or review triggers
- downstream handoff intent

Expert Artifact does not own reusable frameworks, raw-source authority, Thesis authority, PM conviction, or portfolio action by itself.

## 3. Admitted Subtypes

Current admitted subtype family:

- Dossier
- State Map
- Regime Map
- Trigger Chain
- Transmission Chain
- Impact Pool
- Portfolio Impact Map

These names are subtype examples. They should not become generic top-level T1 objects without a separate admission decision.

## 4. Input Discipline

Expert Artifact may be assembled from:

- Source Cards
- Typed Claims
- source sets or source packets
- Canonical Input when a domain contract explicitly permits direct read
- Technical Report or Operating Cycle Artifact when admitted as material input

It must cite material refs and must not invent upstream source authority.

## 5. Allowed Handoffs

Expert Artifact may feed:

- Evidence drafting
- Thesis review
- Scenario input
- Decision Brief
- Technical Report context
- PM context
- writer packages

Expert Artifact may not directly become PM action or update reusable Expertise rules inside a single run.

## 6. Failure Signatures

- Dossier or State Map changes framework rules instead of citing the framework version.
- Expert Artifact hides which Source Cards or Typed Claims shaped it.
- Expert Artifact is consumed as Evidence without belief_delta.
- Expert Artifact emits PM action without Operation / PM gate.

## 7. Adjacent Owners

| Owner | Relationship |
|---|---|
| Expertise | Owns reusable schema, lens, and validation rule. |
| Digestion | Executes expert artifact production for source-understanding families. |
| Research | Uses expert artifacts for Evidence, Thesis, Scenario, and Theme work. |
| Material Catalog | Owns artifact instance boundary. |

## 8. Open Decisions

1. Which subtypes deserve dedicated contracts first: Dossier, State Map, Transmission Chain, or Impact Pool?
2. Should Regime Map / Trigger Chain live here, under Scenario, or under a future Expertise-specific contract?
3. What minimum fields are required for PM-facing consumption?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[Typed-Claim]` [Typed Claim Bridge Contract](material_32_typed_claim_contract.md)
- `[T1-Digestion]` [Digestion Layer Overview](digestion_00_overview.md)
