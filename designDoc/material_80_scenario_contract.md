---
title: Scenario Material Contract
status: active_draft
layer: T1
parent: material_00_overview
created_date: 2026-05-07
reader_persona:
  - Research Architect
  - Domain Expert Maintainer
  - Portfolio Manager
---

# Scenario Material Contract

## 1. Purpose

`Scenario` is a forward prediction generated from a Thesis anchor through an Expertise Application.

It describes how a possible reality path may unfold, including assumptions, triggers, falsifiers, horizons, expected observable deltas, and review cadence.

## 2. Boundary

Scenario owns:

- Thesis anchor refs
- Expertise Application refs
- path structure
- assumptions
- trigger signals
- falsifiers
- horizon
- expected observables
- review cadence
- unresolved objections
- replay / review hooks

Scenario does not own Thesis itself, generic possibility prose, technical setup narrative, Evidence, PM decision, or portfolio action.

## 3. Scenario Equation

```text
Scenario = Thesis anchor + Expertise Application + forward prediction.
```

Without Thesis anchor, it is unanchored future prose.

Without Expertise Application, it lacks a reusable prediction grammar.

Without triggers, falsifiers, horizon, and observables, it cannot be reviewed.

## 4. Related Objects

| Object | Boundary |
|---|---|
| `scenario` | Materialized forward prediction. |
| `scenario_note` | Research / PM admission record for belief use of a Scenario. |
| `technical_scenario` | Conditional technical path inside a Technical Report; not an Expertise Scenario by default. |
| `path_observation` | Early signal upstream of Scenario; not first-class material object. |

## 5. Allowed Handoffs

Scenario may feed:

- Theme memory
- Thesis review
- PM decision context
- scenario_note
- replay / backtest library
- Evidence review when observables hit or fail

Scenario may not by itself update PM conviction, scenario_role, market_state, or portfolio action without PM / Research admission workflow.

## 6. Failure Signatures

- Scenario has no Thesis anchor.
- Scenario has no Expertise Application.
- Scenario is generic future narrative.
- Scenario lacks falsifiers or review cadence.
- Trigger signal match is treated as Scenario verification without Evidence / PM workflow.
- Portfolio decision bypasses Scenario unresolved objections.

## 7. Adjacent Owners

| Owner | Relationship |
|---|---|
| Charter | Defines Scenario as first-class object and PM belief-layer authority. |
| Expertise Application | Owns the capability-to-material relation that records which prediction capability shaped the Scenario. |
| Expertise | Owns reusable prediction model and path grammar; see `expertise_60_prediction_framework_contract.md`. |
| Research | Admits Scenario belief use through scenario_note / review workflow. |
| Theme | Organizes Scenario refs inside durable memory. |

## 8. Open Decisions

1. Should scenario_note receive its own child contract?
2. Should Scenario Map live under Theme or Scenario?
3. Which fields must be structured before runtime persistence?

## References

- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[Expertise-Application]` [Expertise Application Contract](expertise_20_application_contract.md)
- `[Expertise-Prediction]` [Expertise Prediction Framework Contract](expertise_60_prediction_framework_contract.md)
- `[T0-Charter]` [Charter](the_charter.md)
- `[Thesis]` [Thesis Material Contract](material_50_thesis_contract.md)
- `[Theme]` [Theme Material Contract](material_60_theme_contract.md)
