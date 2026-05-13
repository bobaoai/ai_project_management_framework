---
title: Typed Claim Bridge Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - Domain Expert Maintainer
  - Research Architect
  - Claim Reviewer
---

# Typed Claim Bridge Contract

## 1. Purpose

`Typed Claim` is the bridge object between Source Card understanding and downstream expert / research consumption.

It is not promoted to a top-level material asset in this pass. It is admitted as a Material Catalog bridge contract because persisted claims need a clear boundary.

## 2. Boundary

Typed Claim owns:

- an atomic semantic claim
- source ref and Source Card ref
- source span or quote anchor
- source class
- claim type
- permission level
- confidence and confidence reason
- time validity
- falsifiers
- blocked-output / cannot-know boundary

Typed Claim does not own belief delta, Thesis support, Scenario path, or PM decision by itself.

## 3. Source-Class Firewall

A Typed Claim can only exist inside an owning Expertise claim firewall.

The firewall controls:

- allowed source classes
- allowed claim types
- confidence caps
- permission levels
- blocked outputs
- source-class to claim-type routing matrix

If the firewall does not allow a source class to emit a claim type, downstream Evidence, Thesis, Scenario, or PM artifacts cannot silently repair that violation.

## 4. Conversion Rule

```text
Typed Claim + belief_delta + target belief object -> Evidence
```

A Typed Claim can become Evidence only when a Research / PM workflow attaches:

- target Thesis / Scenario / Theme refs
- prior belief state
- posterior belief state
- changed dimension
- PM acknowledgement state when belief-layer transition is involved

## 5. Allowed Handoffs

Typed Claim may feed:

- Expert Artifact
- Expertise Application route
- Evidence drafting
- Thesis review
- Scenario review
- writer package evidence list

Typed Claim may not directly activate or falsify a Thesis without Evidence admission.

## 6. Failure Signatures

- Claim is used as proof of a Thesis without belief_delta.
- Claim type is inferred from prose style rather than owning Expertise firewall.
- Buy-side / practitioner voice modifies framework state when the firewall forbids it.
- Claim lacks source span or source-card lineage.

## 7. Adjacent Owners

| Owner | Relationship |
|---|---|
| Source Card | Supplies source-understanding and source spans. |
| Expertise | Owns claim taxonomy and firewall. |
| Digestion | Executes claim extraction / generation. |
| Research | Admits claims into Evidence only with belief_delta. |

## 8. Open Decisions

1. Should Typed Claim ever become a top-level material asset, or remain a bridge object?
2. Which child Expertise contract should own claim firewall rules before runtime projection?
3. Which persisted runtime tables need to defer to this bridge contract?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[Source-Card]` [Source Card Material Contract](material_30_source_card_contract.md)
- `[Digestion-Structure]` [Digestion Structure Contract](digestion_10_structure_contract.md)
