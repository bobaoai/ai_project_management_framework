---
title: Evidence Material Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - Research Architect
  - Portfolio Manager
  - Evidence Reviewer
---

# Evidence Material Contract

## 1. Purpose

`Evidence` is a belief-change record.

It links material inputs to a Thesis, Scenario, Theme, or other admitted belief object, and records why belief changed, held, weakened, or became contested.

## 2. Charter Binding

Evidence follows the Charter: Evidence is not a log. A record that only says "what was seen" without saying "what changed in belief" is archive or source material, not Evidence.

Evidence must be able to express:

- prior belief state
- posterior belief state
- changed dimension
- reason for change
- material refs
- target belief refs
- counter-evidence or unresolved objections when present

## 3. Boundary

Evidence owns:

- belief_delta
- target Thesis / Scenario / Theme refs
- material inputs causing the belief delta
- support / weaken / falsify / hold posture
- source trust or verification refs when applicable
- PM acknowledgement state when belief-layer transition is involved

Evidence does not own source summary, Typed Claim, raw observation, reusable framework, Scenario prediction, or PM decision by itself.

## 4. Conversion Rule

```text
material input + belief_delta + target belief object -> Evidence
```

Material input can be Source Card, Typed Claim, Expert Artifact, Operating Cycle Artifact, Technical Report, Raw Data reference, or other admitted material. The input alone is not Evidence.

## 5. Allowed Handoffs

Evidence may feed:

- Thesis support / falsifier
- Scenario review
- Theme memory
- PM belief review
- audit trail
- revive of stale belief objects

Evidence may not drive belief-layer transitions without the PM acknowledgement required by Charter.

## 6. Failure Signatures

- Evidence is just a quote.
- Evidence has no target belief object.
- Evidence records "seen" but not "belief changed".
- Evidence only records supporting material and omits known counter-evidence.
- Evidence repairs an upstream source-class / claim-type firewall violation.

## 7. Adjacent Owners

| Owner | Relationship |
|---|---|
| Charter | Defines Evidence as first-class object and PM belief-layer authority. |
| Evidence Source Trust | Owns trust tier / AI-verified gate for source refs. |
| Research | Drafts and admits Evidence into belief workflows. |
| Material Catalog | Owns Evidence material boundary. |

## 8. Open Decisions

1. Should Evidence object fields be split into system-drafted and PM-acknowledged sections?
2. How should Evidence refs represent multi-target belief deltas?
3. Which existing evidence_record schemas need alignment after this contract is admitted?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[T0-Charter]` [Charter](the_charter.md)
- `[Evidence-Trust]` [Evidence Source Trust Contract](evidence_source_trust_contract.md)
