---
title: Expertise Prediction Framework Contract
status: active_draft
layer: T1
parent: expertise_00_overview
created_date: 2026-05-07
reader_persona:
  - System Builder
  - Research Architect
  - Domain Expert Maintainer
  - Portfolio Manager
---

# Expertise Prediction Framework Contract

## 1. Purpose

`Prediction Framework` is the Expertise child contract for reusable forward-prediction capability.

It owns the grammar that turns one or more Thesis anchors into a Scenario-shaped prediction through an Expertise Application.

It does not own the Scenario material instance, scenario_note admission, Thesis lifecycle, PM conviction, portfolio action, runtime schema, or source ingestion.

Boundary equation:

```text
Prediction Framework + Thesis anchor + material refs -> Scenario candidate
Scenario candidate + Research / PM admission -> scenario_note / PM use
```

## 2. Reader End-State

After reading a Prediction Framework output, a downstream reader should know:

- which Thesis anchor the prediction depends on;
- which reusable Expertise lens produced the prediction;
- which source-understanding materials and route / channel reads shaped it;
- what path is being predicted and which adjacent paths compete with it;
- which triggers would activate, weaken, or falsify the path;
- what observable deltas should appear if the path is unfolding;
- when the prediction must be refreshed;
- which parts are PM-usable only after Research / PM admission.

Silent violation:

```text
The output sounds like a plausible future, but no one can tell what Thesis it tests, what would falsify it, or which Expertise lens produced it.
```

## 3. Ownership Split

| Concern | Owner |
|---|---|
| Prediction grammar, path taxonomy, trigger / falsifier families, observable-delta map | Expertise |
| Scenario material object boundary | Material Catalog |
| Applying a selected prediction framework to material refs | Digestion / Expertise Application execution surface |
| Scenario belief admission, scenario_note, PM conviction | Research / PM |
| Freshness, dependency closure, canonical builder admission | Artifact Graph / Code when runtime exists |

## 4. Required Inputs

A Prediction Framework may only produce a Scenario candidate when it has:

- `prediction_framework_id`
- `framework_version`
- `domain`
- `thesis_anchor_refs[]`
- `input_material_refs[]`
- `expertise_application_ref` or draft application block following Expertise Application Contract [Expertise-Application]
- `state_model`
- `path_taxonomy`
- `trigger_family`
- `falsifier_family`
- `observable_delta_map`
- `horizon_policy`
- `review_policy`
- `blocked_outputs[]`

Input materials may include Source Cards, Typed Claims, Expert Artifacts, Evidence records, prior Scenarios, scenario_notes, Technical Reports, Operating Cycle Artifacts, or market packets. Each input must keep its original allowed-use constraint.

## 5. Minimum Framework Shape

Machine-auditable contract block:

```yaml
contract_id: expertise_prediction_framework_contract
schema_kind: contract_shape
owner_t1: expertise
status: active_draft
runtime_schema_status: not_admitted
required_fields:
  - prediction_framework_id
  - framework_version
  - domain
  - thesis_anchor_refs
  - input_material_refs
  - expertise_application_ref
  - state_model
  - path_taxonomy
  - trigger_family
  - falsifier_family
  - observable_delta_map
  - horizon_policy
  - review_policy
  - blocked_outputs
allowed_outputs:
  - scenario_candidate
  - scenario_review_input
  - decision_brief_support
blocked_outputs:
  - evidence_record
  - thesis_update
  - scenario_note_admission
  - pm_action
```

Machine-auditable framework template:

```yaml
prediction_framework_id: stable_id
framework_version: 0.1
owner_t1: expertise
domain: custom
purpose: what recurring forward prediction this framework produces

applicable_thesis_types:
  - thesis class or mechanism family
not_for:
  - blocked use

state_model:
  current_state_variables: []
  transition_variables: []
  regime_or_path_labels: []
  adjacent_states: []

path_taxonomy:
  leading_path: <definition>
  parallel_path: <definition>
  counterfactual_path: <definition>
  tail_path: <definition>

trigger_family:
  activation_triggers: []
  acceleration_triggers: []
  weakening_triggers: []
  invalidation_triggers: []

falsifier_family:
  mechanism_falsifiers: []
  timing_falsifiers: []
  source_authority_falsifiers: []
  market_expression_falsifiers: []

observable_delta_map:
  - observable: series / event / text surface
    expected_delta: direction / threshold / qualitative change
    horizon: example_horizon
    source_owner: data_or_source_owner

horizon_policy:
  native_horizon: months_to_quarters
  refresh_required_before: []
  stale_after_days: null

allowed_outputs:
  - scenario_candidate
  - scenario_review_input
  - decision_brief_support
blocked_outputs:
  - evidence_record
  - thesis_update
  - scenario_note_admission
  - pm_action
```

## 6. Scenario Candidate Shape

A Scenario candidate produced by a Prediction Framework should carry:

```yaml
scenario_candidate_id: <stable_id>
material_object: scenario_candidate
parent_thesis_refs: []
prediction_framework_id: <id>
framework_version: <version>
expertise_application:
  expertise_application_id: <id_or_draft_local_id>
  application_kind: scenario_generation
  capability_ref:
    expertise_id: <id>
    framework_id: <prediction_framework_id>
    framework_version: <version>
  input_material_refs: []
  output_material_refs:
    - <scenario_candidate_id>
  allowed_use_in: []
  allowed_use_out: candidate_only | background | trigger | decision_support

path_role: leading_path | parallel_path | counterfactual_path | tail_path
path_label: <human-readable path>
mechanism: <why the path would unfold>
assumptions: []
trigger_signals:
  - observable_data: <event / metric / text surface>
    threshold: <threshold or qualitative condition>
    direction: above | below | crosses | appears | absent
    status: pending | hit | missed | stale
expected_observable_deltas: []
falsifiers: []
unresolved_objections: []
review_policy: {}
pm_use_boundary: <what PM may and may not consume before admission>
```

The candidate is not a canonical `scenario_note`. It becomes PM-usable only after Research / PM admission under the Scenario material contract.

## 7. VideoParser Fed KB Calibration

The first calibration precedent is the sibling `video_parser` repo's `macro_fed_kb`.

Portable lessons:

| VideoParser pattern | Prediction Framework rule |
|---|---|
| Resource Card + Angle Card split | Prediction inputs should cite the smallest source-understanding unit that carries the reasoning. |
| `gate_status`, `freshness_verdict`, `allowed_use` | Prediction cannot consume stale or blocked material as live trigger evidence. |
| `source_class x claim_type` firewall | A source voice cannot update Fed framework / parameter / operation claims unless its class permits that claim type. |
| Angle-to-Channel Route | Prediction must preserve channel, stance, salience, mechanism, horizon, allowed use, conditions, falsifiers, and refresh triggers. |
| Transmission Channel Registry | Prediction should name the channel it expects to move, not leap from source claim to PM conclusion. |
| `reasoning_chain` | Prediction must preserve the causal path, not just the final view. |

Fed-specific calibration examples:

- `primary_policy_record` can shape Fed framework / parameter / operation state.
- `market_interpretation` can shape current market read, route salience, and some framework interpretation, but must not silently become official Fed intent.
- `buy_side_narrative` can shape market mapping, portfolio expression, and stale / background diagnostics; it cannot directly rewrite Fed reaction-function state.

## 8. Fed Regime Transfer Pattern

`Fed Regime Transfer` is the first dogfood pattern.

Definition:

```text
Fed Regime Transfer predicts whether a live Fed reaction-function regime transfers from one anchor framework to another, which path becomes leading, and which market observables should reprice first.
```

Minimum state model:

- current regime anchor;
- successor or competing framework;
- institutional transition mechanism;
- source authority map;
- market-pricing map;
- trigger / falsifier matrix;
- review cadence around FOMC, employment, inflation, and succession events.

Example transition variables:

- chair transition and statement authorship;
- FOMC statement language;
- dot plot / forward guidance treatment;
- balance sheet tool preference;
- supply-shock look-through doctrine;
- inflation-expectations anchoring;
- labor-break threshold;
- STIR pricing and front-end basis;
- long-end term premium and curve shape.

## 9. Failure Signatures

- Prediction has no Thesis anchor.
- Prediction cites raw sources where Source Cards or material refs exist.
- Prediction uses a stale current-market read as live trigger evidence.
- Prediction lets buy-side narrative update Fed internal reaction-function state.
- Prediction names triggers but no falsifiers.
- Prediction gives PM action without scenario_note / PM admission.
- Prediction collapses multiple adjacent paths into one smooth base case.
- Prediction gives numeric probability precision without a calibration basis.

## 10. Non-Goals

- Do not create runtime schema in this admission.
- Do not migrate existing scenario_notes.
- Do not rename `scenario_prediction` runtime fields yet.
- Do not require all domains to use Fed-specific channel ids.
- Do not make Prediction Framework own the Thesis or Scenario material contract.
- Do not let Prediction Framework bypass Source Card, claim firewall, allowed-use, or Research / PM admission gates.

## 11. Open Decisions

1. Should persisted Scenario require `prediction_framework_id` and `expertise_application_id`?
2. Should Fed Regime Transfer receive a dedicated child framework file after dogfood?
3. Should Scenario Map live under Theme, Scenario, or Expertise prediction review?
4. Should numeric probability ever be allowed, or should probability remain qualitative until backtest/replay exists?
5. Which runtime builder, if any, should first parse Prediction Framework contracts?

## References

- `[Expertise-Overview]` [Expertise Overview](expertise_00_overview.md)
- `[Expertise-Application]` [Expertise Application Contract](expertise_20_application_contract.md)
- `[Material-Scenario]` [Scenario Material Contract](material_80_scenario_contract.md)
- `[Material-Thesis]` [Thesis Material Contract](material_50_thesis_contract.md)
- `[Material-Source-Card]` [Source Card Material Contract](material_30_source_card_contract.md)
- `[Material-Typed-Claim]` [Typed Claim Material Contract](material_32_typed_claim_contract.md)
- `[T1-Research]` [Research Family Overview](research_00_overview.md)
- `[External-Video-Parser]` sibling repo precedent, not runtime dependency: `video_parser` repo, `macro_fed_kb/design/28_source_card_schema.md`, `macro_fed_kb/design/25_claim_schema.md`, `macro_fed_kb/design/34_angle_channel_routing.md`, `macro_fed_kb/design/32_transmission_channel_registry.md`
