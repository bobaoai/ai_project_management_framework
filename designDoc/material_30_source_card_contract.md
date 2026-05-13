---
title: Source Card Material Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - Domain Expert Maintainer
  - Research Architect
  - Source Card Writer
  - Design Doc Reviewer
---

# Source Card Material Contract

## 1. Purpose

`Source Card` is the source-understanding handoff after route selection.

It records what a source says, what it does not say, how it may be used, and which Expertise lens or domain route shaped the read.

## 2. Boundary

Source Card owns:

- source identity and source refs
- voice / source class
- source permission and cannot-support grammar
- epistemic mode
- time semantics and freshness posture
- allowed use
- source spans or excerpt anchors
- optional resource-card / angle-card split
- link to Typed Claims or claim candidates
- link to Expertise Application when applicable

Source Card does not own belief delta, Thesis, Scenario, PM action, or cross-source conviction.

## 3. Resource Card / Angle Card

A single source can contain multiple independently consumable reasoning units.

| Card type | Boundary |
|---|---|
| `resource_card` | Resource-level pre-read: what the source is, what angles it contains, and whether it should be split. |
| `angle_card` | Independently consumable reasoning unit with its own allowed use, horizon, salience, source spans, and downstream route. |

The split is optional by domain, but the contract allows it. A domain must not force unrelated angles into one card when doing so would blur allowed use.

## 4. Allowed Use

Source Card allowed-use values should be closed and domain-owned. Minimum portable vocabulary:

```text
trigger
current_state
background
structural_only
candidate_only
blocked
```

A downstream workflow must not upgrade `allowed_use`.

## 5. Allowed Handoffs

Source Card may feed:

- Typed Claim
- Expertise Application route
- Expert Artifact
- Evidence drafting
- Thesis review
- Scenario input
- writer package excerpting

Source Card may not directly activate belief or authorize action.

## 6. Failure Signatures

- Source Card says "therefore we believe" without Evidence or Thesis handoff.
- Source Card is generated before domain route selection.
- A single card mixes unrelated angles with different horizons or allowed uses.
- Source Card hides source limitations, source class, or cannot-support boundaries.
- Downstream synthesis cites raw source when an admitted Source Card exists.

## 7. Adjacent Owners

| Owner | Relationship |
|---|---|
| Ingestion | Produces canonical source read content. |
| Expertise | Owns reusable card patterns, source-class firewall, and route grammar. |
| Digestion | Executes Source Card production after route selection. |
| Material Catalog | Owns Source Card material boundary. |

## 8. Open Decisions

1. Which domains must formally split resource cards and angle cards?
2. Should pre-route source briefs exist as a separate object that is explicitly not a Source Card?
3. Should Source Card allowed-use vocabulary be global, domain-local, or global with domain extensions?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[Digestion-Structure]` [Digestion Structure Contract](digestion_10_structure_contract.md)
- `[T1-Digestion]` [Digestion Layer Overview](digestion_00_overview.md)
