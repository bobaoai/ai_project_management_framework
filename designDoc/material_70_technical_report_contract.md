---
title: Technical Report Material Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - Research Architect
  - Technical Report Writer
  - Portfolio Manager
---

# Technical Report Material Contract

## 1. Purpose

`Technical Report` is a PM-readable expression of current market state from technical inputs.

It can explain market structure, setup conditions, risk levels, and conditional technical paths. It does not own raw market data truth or belief-layer Scenario authority.

## 2. Boundary

Technical Report owns:

- current market-state interpretation
- signal packet refs
- market data refs
- chart vision refs when used
- setup conditions
- risk levels
- invalidation / confirmation conditions
- technical_scenario prose when present
- report time and freshness context

Technical Report does not own Source Card, Thesis, Theme, Evidence, or Scenario.

## 3. Technical Scenario

`technical_scenario` is a conditional technical path inside a report or signal packet.

It is not an Expertise Scenario by default.

Promotion rule:

```text
technical_scenario -> scenario_note or Scenario only through explicit Research / Expertise promotion workflow.
```

## 4. Allowed Handoffs

Technical Report may feed:

- PM read
- single-stock package
- current-market package
- Operating Cycle Artifact
- Evidence drafting when belief_delta is attached
- Theme or Thesis review context

It may not create Evidence without belief_delta or create Scenario without Thesis anchor and Expertise Application.

## 5. Must Not Do

Technical Report must not:

- invent numeric market truth outside deterministic packet inputs
- treat chart pattern prose as deterministic numeric truth
- activate Thesis or Scenario lifecycle
- become a Source Card
- bypass PM decision workflow

## 6. Adjacent Owners

| Owner | Relationship |
|---|---|
| Research technical pipeline | Executes signal packet and report workflow. |
| Market data infrastructure | Owns price / volume / provider truth. |
| Material Catalog | Owns Technical Report material boundary. |
| Scenario | Owns Expertise-driven forward prediction, not report setup prose. |

## 7. Open Decisions

1. Which technical_scenario fields should become structured versus prose?
2. When should a technical setup promote into Evidence?
3. Should Technical Report have separate contracts for asset, current-market, and portfolio-level reports?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[Research-Technical]` [Technical Signal Pipeline](research_20_technical_signal_pipeline_v2.md)
- `[Scenario]` [Scenario Material Contract](material_80_scenario_contract.md)
