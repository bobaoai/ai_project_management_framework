---
title: Expertise Application Contract
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

# Expertise Application Contract

## 1. Purpose

`Expertise Application` is the relation contract for applying a reusable Expertise capability to material inputs in order to produce or shape material outputs.

It owns the hinge:

```text
Expertise capability + input material refs + application semantics
-> output material refs + allowed-use boundary
```

It does not own the reusable capability itself, the material output instance, Digestion execution, Research belief admission, scenario_note admission, PM conviction, portfolio action, runtime schema, or graph node freshness under Artifact Graph [T0-Artifact-Graph].

The application relation exists so downstream readers can answer four questions:

- Which capability was used?
- Which materials were consumed?
- What route / method / permission boundary survived the application?
- What output was produced or shaped, and how may it be consumed?

## 2. Boundary Sentence

```text
Expertise owns capability.
Material Catalog owns material object.
Expertise Application owns the relation between capability and materialized output.
Digestion or another execution owner applies the capability.
Research / PM admits belief use when the output enters Evidence, Scenario, Theme, or decision workflow.
```

PM consumes materialized outputs and admitted application traces, not bare Expertise.

## 3. Ownership Split

| Concern | Owner |
|---|---|
| Reusable framework, lens, ontology, source-card pattern, claim firewall, prediction grammar | Expertise capability contract |
| Material output boundary, such as Source Card, Expert Artifact, Scenario, Evidence, Theme, or Operating Cycle Artifact | Material Catalog [Material-Overview] |
| Which capability was applied to which inputs, with what route semantics and allowed use | Expertise Application |
| Actual run, storage, prompts, generated artifacts, and current schema detail | Digestion / runtime owner / selected execution surface |
| Belief admission, scenario_note, Evidence use, PM conviction, portfolio action | Research / PM [T1-Research] |
| Node identity, dependency closure, freshness, provenance, canonical builder handles | Artifact Graph [T0-Artifact-Graph] when graph-admitted |

## 4. Bounded Metadata

The relation metadata should stay compact. It is an audit handle, not the whole reasoning surface; this follows the bounded metadata / reasoning prose rule in Design Doc Review Gate Contract [T0-Doc-Review].

Machine-auditable contract block:

```yaml
contract_id: expertise_application_contract
schema_kind: contract_shape
owner_t1: expertise
status: active_draft
runtime_schema_status: not_admitted
timestamp_semantics: follows designDoc/the_timestamp_semantic.md
relation_kind: capability_to_material_application
required_fields:
  - expertise_application_id
  - application_kind
  - capability_ref.expertise_id
  - input_material_refs
  - output_material_refs
  - allowed_use_in
  - allowed_use_out
  - blocked_outputs
application_kind_enum:
  - source_understanding
  - typed_claim_projection
  - channel_route
  - expert_artifact_generation
  - scenario_generation
  - decision_support
allowed_use_out_enum:
  - background
  - structural_only
  - candidate_only
  - trigger
  - decision_support
blocked_outputs:
  - evidence_record_without_belief_delta
  - scenario_note_admission
  - pm_conviction
  - pm_action
allowed_use_rule: output_use_must_not_exceed_input_permission
```

Machine-auditable relation template:

```yaml
expertise_application_id: draft_or_stable_id
application_kind: scenario_generation
capability_ref:
  expertise_id: example_expertise_id
  framework_id: example_framework_id
  framework_version: 0.1
input_material_refs:
  - example_input_material_ref
output_material_refs:
  - example_output_material_ref
allowed_use_in:
  - background
allowed_use_out: candidate_only
blocked_outputs:
  - scenario_note_admission
  - pm_action
validity:
  valid_until_calendar_day_utc: null
  requires_refresh_before: []
```

Optional machine-auditable route semantics:

```yaml
route_semantics:
  source_class: optional
  claim_type: optional
  epistemic_mode: optional
  decision_layer: optional
  channel_id: optional
  stance: optional
  salience: optional
  horizon: optional
  conditional_on: []
  falsified_by: []
```

The required prose around the block should explain:

- why this capability applies to these materials;
- what mechanism or route is being preserved;
- what the input materials cannot support;
- which permission or freshness constraints narrowed the output;
- what would make the application stale, invalid, or blocked.

Field completeness is not enough. If the mechanism, route rationale, cannot-support boundary, or PM-use boundary is only implied by field names, the application is under-written.

## 5. Allowed-Use Propagation

Expertise Application must never upgrade the allowed use of an input material.

Rules:

1. Output allowed use must be equal to or narrower than the strictest live input constraint needed by the output.
2. Stale or blocked material may be used as background only when the output says so explicitly.
3. A source-class / claim-type firewall violation cannot be repaired downstream.
4. A buy-side or practitioner read may shape market mapping, salience, or PM expression, but it cannot silently become official-source intent.
5. A `scenario_generation` application may produce a Scenario candidate, not a scenario_note or PM action.
6. A `decision_support` application may support a Decision Brief or Portfolio Decision, but PM admission remains outside the application relation.

If an input Source Card is `structural_only`, the application can only preserve structural or background use unless another input with stronger permission independently supports the live claim.

## 6. Application Kinds

| Kind | Typical input | Typical output | Must preserve |
|---|---|---|---|
| `source_understanding` | Raw Data / Canonical Input + capability | Source Card | source voice, allowed use, cannot-support grammar |
| `typed_claim_projection` | Source Card / source span + claim firewall | Typed Claim | source class, claim type, permission level |
| `channel_route` | Source Card / Angle Card / Typed Claim | route or application trace | channel, stance, salience, mechanism, horizon, conditions, falsifiers |
| `expert_artifact_generation` | Source Cards / Typed Claims / source set | Expert Artifact | schema, aggregation logic, material refs, blocked claims |
| `scenario_generation` | Thesis anchor + material refs + prediction framework | Scenario candidate | Thesis anchor, path role, triggers, falsifiers, observable deltas, PM-use boundary |
| `decision_support` | admitted material outputs + portfolio context | Decision Brief / Portfolio Decision support | decision-use scope, unresolved objections, PM authority boundary |

## 7. Scenario Generation Rule

Scenario generation is the first dogfood path for this contract.

```text
Prediction Framework [Expertise-Prediction] + Thesis anchor + material refs + Expertise Application
-> Scenario candidate
```

The application relation must preserve:

- `prediction_framework_id`
- framework version
- Thesis anchor refs
- input material refs and allowed use
- route or channel semantics when source-understanding material shaped the prediction
- output Scenario candidate ref
- trigger / falsifier families used by the framework
- PM-use boundary

The produced Scenario candidate remains a Material Catalog object. Research / PM decides whether it becomes `scenario_note` or enters belief use.

## 8. Fed Regime Transfer Dogfood

The first dogfood application is Fed Regime Transfer [Dogfood-Fed-Regime-Transfer].

In that example:

- capability: `fed_regime_transfer_v0_1`;
- anchor: `warsh_succession_reanchors_forced_pause_factor_a`;
- material inputs: existing scenario_note precedent plus VideoParser Fed Source Cards and route set;
- route semantics: source authority, Fed reaction-function channel, market-pricing channel, stale-background vs trigger use;
- output: `fed_regime_transfer__warsh_framework_substitution_path__2026_05_07`;
- allowed use: `candidate_only` until Research / PM admission.

The important test is not whether an index entry is complete. The test is whether a reader can see how the Fed regime capability transformed bounded source-understanding material and a Thesis anchor into a Scenario candidate without upgrading source permissions or bypassing scenario_note admission.

## 9. Failure Signatures

- Output material cites Expertise but no application relation.
- Application names a capability but no input material refs.
- Application names input refs but omits allowed-use propagation.
- A stale Source Card is used as live trigger evidence.
- A buy-side narrative updates official-source state.
- Route semantics are present as fields but the prose never explains the mechanism.
- Application produces Evidence, scenario_note, PM conviction, or PM action directly.
- Output material cannot tell whether it is background, candidate, trigger input, or decision support.

## 10. Non-Goals

- Do not create runtime schema in this admission.
- Do not require every existing Source Card, Expert Artifact, or Scenario to backfill an application relation.
- Do not make Expertise Application a top-level material asset.
- Do not let application metadata replace mechanism prose.
- Do not let application relation own the reusable framework or material output boundary.
- Do not make PM-facing workflows consume bare Expertise without materialized output.

## 11. Open Decisions

1. Which runtime surface should first persist `expertise_application_id`, if any?
2. Should `scenario_candidate` become a persisted data family before scenario_note migration?
3. Should `channel_route` remain a generic application kind or split into a Source Card route contract?
4. Which application fields become mandatory once a generated builder exists?
5. Should every Expert Artifact require an application ref before writer-package consumption?

## References

- `[Expertise-Overview]` [Expertise Overview](expertise_00_overview.md)
- `[Expertise-Prediction]` [Expertise Prediction Framework Contract](expertise_60_prediction_framework_contract.md)
- `[Material-Overview]` [Material Catalog Overview](material_00_overview.md)
- `[Material-Scenario]` [Scenario Material Contract](material_80_scenario_contract.md)
- `[Material-Source-Card]` [Source Card Material Contract](material_30_source_card_contract.md)
- `[Material-Typed-Claim]` [Typed Claim Material Contract](material_32_typed_claim_contract.md)
- `[T0-Artifact-Graph]` [Artifact Dependency Closure Contract](the_artifact_graph.md)
- `[T0-Doc-Review]` [Design Doc Review Gate Contract](the_design_doc_management.md)
- `[T1-Research]` [Research Family Overview](research_00_overview.md)
- `[Dogfood-Fed-Regime-Transfer]` [Fed Regime Transfer Prediction Dogfood](temp/fed_regime_transfer_prediction_dogfood_2026_05_07.md)
- `[External-Video-Parser]` sibling repo precedent, not runtime dependency: `video_parser` repo, `macro_fed_kb/design/28_source_card_schema.md`, `macro_fed_kb/design/25_claim_schema.md`, `macro_fed_kb/design/34_angle_channel_routing.md`, and `macro_fed_kb/design/32_transmission_channel_registry.md`
