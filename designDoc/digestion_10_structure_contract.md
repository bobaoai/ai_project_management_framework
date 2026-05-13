---
title: Digestion Structure Contract
status: active_draft
reader_persona:
  - System Builder
  - Research Architect
  - Digestion Worker Designer
---

# Digestion Structure Contract

## 1. 这份 contract 解决什么

本文定义 `digestion` T1 layer 的结构对象、生成链路、Postgres backend contract、文件投影、以及下游消费方式。

`digestion_00_overview.md` 定义为什么需要这一层；本文定义这一层的数据如何存在、如何生成、如何被消费。

Material Catalog binding:

- `material_00_overview.md` 是 material-object authority；Source Card、Typed Claim、Expert Artifact、Evidence、Thesis、Scenario、Theme、Technical Report 的 object boundary 以 Material Catalog child contracts 为准。
- `expertise_00_overview.md` 是 reusable capability authority；expert framework / lens、source card pattern、claim firewall、artifact schema、scenario prediction grammar 和 skill projection contract 的 durable boundary 以 Expertise 为准。
- 本文保留 Digestion execution / current schema authority：source-understanding chain、expert route、framework route、Postgres rows、文件投影、prompt run、promotion edge。
- 当 Material Catalog child contracts 正式投影到 runtime schema 时，本文应只保留 Digestion-specific generation and storage details。

读完本文，读者应该能够：

- 设计一个新的 expert subsystem，而不重新发明 Source Card / Typed Claim / Framework / Channel / Scenario / Promotion Link。
- 判断一份文件是否只是 note，还是已经成为可查询、可追踪、可消费的 digestion asset。
- 知道 Postgres 中必须有哪些 registry / edge / run / claim 记录。
- 知道下游 thesis、theme、report、portfolio workflow 应该消费 refs 和 edges，而不是扫目录或复制大段正文。

Fed Rate Knowledge Base 是本文的第一个模板来源。本文抽取 Fed 模式的结构，不搬 Fed 专有术语。

## 2. Core Pipeline

Digestion 的标准链路：

```text
read_content.md
  -> Evidence Packet
  -> Domain Route / Expert Selection
  -> Source Card (Material Catalog object; expert-generated)
  -> Typed Claim (Material Catalog bridge object; expert-firewalled)
  -> Framework Route
  -> Channel / Role State
  -> Scenario Prediction (current Digestion execution object)
  -> Expert Artifact (Material Catalog object)
  -> Promotion Link
  -> Thesis / Theme / PM Artifact
```

每一步都必须保留：

- source lineage
- time semantics
- object identity
- content hash
- freshness state
- allowed use
- downstream consumer edge

Silent violation:

```text
一个 expert artifact 能被读懂，但无法反查它依赖哪些 source card、claim、channel route 和 prompt run。
```

这说明它是分析文档，不是 digestion-backed artifact。

## 3. Object Contract

### 3.1 Source Card

Source Card 是 source-level 独立理解层。它不写最终 thesis，也不做跨源 synthesis。

Source Card generation is expert-shaped. A cross-asset orchestrator may assemble the source packet, but it must select the domain route before Source Card generation. Company, crypto, macro, technical, and future experts may each project their own Source Card pattern from Expertise as long as the minimum fields below remain recoverable.

Canonical material contract: `material_30_source_card_contract.md`。This section defines the current Digestion generation/storage projection.

Reader end-state:

- 下游知道 source 是什么。
- 下游知道 source 的 voice、source_class、time semantics、evidence boundary。
- 下游知道 source 写了什么、没有写什么。
- 下游知道哪些 reasoning unit 可以进入后续 claim / framework。
- 下游不需要重读原文就能恢复关键机制和边界。

Minimum fields:

```yaml
object_type: source_card
source_card_id: <id>
subsystem_id: <domain subsystem>
source_ref: data/research/messages/<research_id>/read_content.md
source_title: <title>
source_class: <closed enum per subsystem>
voice: <speaker / publisher / source family>
observed_at_utc: <ISO-8601 with offset>
recorded_at_utc: <ISO-8601 with offset>
card_scope: full_source | excerpt | claim_subset
freshness_state: fresh | stale | unknown
allowed_use: evidence | background | framework | trigger | candidate_only | blocked
source_span_refs:
  - quote: <verbatim or locator>
    locator: <source-local locator>
    role: key_evidence | caveat | excluded | background
```

File projection:

```text
data/digestion/expert_subsystems/<subsystem_id>/source_cards/<source_slug>/<card_id>.md
```

Postgres rows:

- `digestion_objects(object_type='source_card')`
- `digestion_edges(edge_type='derived_from', to source read_content object/ref)`
- optional `digestion_prompt_runs` if AI-generated

Fed template:

Fed Source Card separates `Resource Card` from `Angle Card`. Portable lesson: a single source can contain multiple independently consumable reasoning units; each unit may need its own card and allowed-use gate.

### 3.2 Typed Claim

Typed Claim is the semantic bridge between source understanding and expert reasoning.

It prevents voice authority from leaking into claims the source cannot support.

Typed Claim is also expert-shaped. The valid `source_class`, `claim_type`, and confidence caps come from the selected Expertise firewall, not from a generic researcher prompt.

Canonical bridge contract: `material_32_typed_claim_contract.md`。A Typed Claim becomes Evidence only after it carries belief_delta / target_belief / promotion context under `material_40_evidence_contract.md`.

Minimum fields:

```yaml
object_type: typed_claim
claim_id: <id>
source_card_id: <source_card_id>
subsystem_id: <subsystem_id>
source_ref: <source card or read_content ref>
source_class: <closed enum>
claim_type: <closed enum>
claim_text: <one-sentence claim>
elaboration: <mechanism / boundary / counterfactual>
confidence: low | medium | high
time_validity: event_specific | cycle_specific | structural
observed_at_utc: <ISO-8601 with offset>
recorded_at_utc: <ISO-8601 with offset>
source_span_refs: []
falsifiers: []
allowed_use: evidence | background | trigger | candidate_only | blocked
```

Postgres rows:

- `digestion_objects(object_type='typed_claim')`
- `digestion_claims`
- `digestion_edges(edge_type='derived_from', from claim to source card)`

Firewall contract:

```text
source_class x claim_type route must be explicit per subsystem.
```

Fed template:

`buy_side_narrative` can support `market_mapping`; it cannot directly update Fed `framework / parameter / operation`. Portable lesson: every domain needs a voice-authority firewall.

### 3.3 Framework Card

Framework Card stores a reusable analysis lens. It is currently projected through Digestion, but durable framework authority belongs to Expertise.

It is not a report. It is a domain reasoning machine that says how claims should be interpreted.

Minimum fields:

```yaml
object_type: framework_card
framework_id: <id>
subsystem_id: <subsystem_id>
framework_name: <name>
problem_statement: <what this framework explains>
decision_layers: []
allowed_source_classes: []
allowed_claim_types: []
channels: []
roles: []
horizons: []
typical_misuse: []
falsifier_policy: <how framework updates or fails>
promotion_policy: <how framework can feed thesis/theme/PM artifacts>
```

Postgres rows:

- `digestion_objects(object_type='framework_card')`
- `digestion_edges(edge_type='uses_framework')` from routes / scenarios / expert artifacts

Fed template:

`State Estimation -> Transmission Diagnosis -> Portfolio Expression`.

Portable form:

```text
state read -> mechanism / transmission read -> expression / implication read
```

Do not force every domain into these names; preserve the function.

### 3.4 Channel / Role Registry

Channel / Role Registry defines how claims enter a framework.

Minimum channel fields:

```yaml
channel_id: <id>
subsystem_id: <subsystem_id>
decision_layer: <framework layer>
definition: <what this channel explains>
native_horizon: intraday | days_to_weeks | weeks_to_months | months_to_quarters | structural
observables: []
allowed_source_roles:
  strong: []
  weak: []
typical_misuse: []
falsifiers: []
missing_confirmations: []
```

Minimum role fields:

```yaml
role_id: <id>
subsystem_id: <subsystem_id>
definition: <what this source role contributes>
best_for: []
not_for: []
allowed_claim_types: []
preferred_channels: []
```

Postgres rows:

- `digestion_objects(object_type='channel_registry')`
- `digestion_framework_routes`

Fed template:

Fed channels include `front_end_plumbing`, `long_end_term_premium`, `credit_creation`, `inflation_expectations`, `dollar_fx`, `asset_price_fci`.

Portable lesson: channel registry prevents a true local observation from silently becoming an overbroad market conclusion.

### 3.5 Framework Route

Framework Route maps a Source Card or Typed Claim into a channel / role / decision layer.

Framework Route remains a Digestion execution object. It may become a candidate input to the child Expertise Application relation, but it cannot by itself upgrade `allowed_use` or authorize PM consumption.

Minimum fields:

```yaml
route_id: <id>
object_id: <source_card_id or claim_id>
framework_id: <framework_id>
channel_id: <channel_id>
role_id: <role_id>
stance: supports | weakens | contradicts | conditions | background_only
effect: <what the object says inside this channel>
mechanism: <why>
horizon: <native horizon>
allowed_use: trigger | current_state | background | structural_only | candidate_only | blocked
confidence: low | medium | high
conditional_on: []
falsified_by: []
```

Postgres rows:

- `digestion_framework_routes`
- `digestion_edges(edge_type='routes_to_channel')`

Fed template:

Conks may support a `front_end_plumbing` route without supporting a broad `risk_on` conclusion.

### 3.6 Scenario Prediction

Scenario Prediction is a conditional path generated from the digestion graph.

It is not thesis belief and not portfolio action.

Canonical Scenario contract: `material_80_scenario_contract.md`。The current `scenario_prediction` object is a Digestion graph projection: it can supply path steps, route refs, falsifiers, and watch triggers, but it is not the canonical thesis-anchored Scenario asset.

Minimum fields:

```yaml
object_type: scenario_prediction
scenario_id: <id>
subsystem_id: <subsystem_id>
framework_id: <framework_id>
scenario_name: <name>
state_assumption: <current state or conditional assumption>
path_steps:
  - step_id: <id>
    channel_id: <channel>
    mechanism: <mechanism>
    expected_effect: <effect>
    horizon: <horizon>
supporting_claim_ids: []
contradicting_claim_ids: []
channel_route_ids: []
historical_case_refs: []
likelihood_ordinal: more_likely | equally_likely | less_likely | tail_risk
confidence: low | medium | high
falsifiers: []
missing_confirmations: []
allowed_use: evidence | watch_trigger | candidate_only | blocked
promotion_targets: []
```

Postgres rows:

- `digestion_objects(object_type='scenario_prediction')`
- `digestion_edges(edge_type='supported_by')`
- `digestion_edges(edge_type='contradicted_by')`
- `digestion_edges(edge_type='routes_to_channel')`

Fed template:

Fed scenario prediction combines policy state, transmission channel state, historical cases, and falsifiers. Portable lesson: prediction must cite the graph path, not just analyst intuition.

### 3.7 Expert Artifact

Expert Artifact is the subsystem-level structured read.

It consumes source cards, typed claims, framework routes, and scenarios.

Canonical material contract: `material_35_expert_artifact_contract.md`。This section defines the current Digestion shape for building and storing expert subsystem output.

Minimum fields:

```yaml
object_type: expert_artifact
artifact_id: <id>
subsystem_id: <subsystem_id>
artifact_type: <closed enum per subsystem>
as_of: <date or timestamp>
framework_id: <framework>
included_scenario_ids: []
included_claim_ids: []
included_source_card_ids: []
freshness_state: fresh | stale | unknown
key_uncertainties: []
falsifiers: []
downstream_allowed_use: thesis_input | theme_input | report_input | portfolio_context | blocked
```

Postgres rows:

- `digestion_objects(object_type='expert_artifact')`
- `digestion_edges(edge_type='uses_framework')`
- `digestion_edges(edge_type='contains_claim')`
- `digestion_edges(edge_type='contains_scenario')`

Fed template:

`Regime Map`, `Trigger Chain`, and `Stock Pool Impact` are expert artifacts. Portable lesson: expert artifact is structured subsystem output, not the final PM report.

### 3.7A Expert Contract

Expert Contract records the domain expert that is allowed to generate Source Cards, Typed Claims, Framework Routes, and Expert Artifacts for a route.

Expert Contract is a capability contract, not a material object. If Expertise is later admitted as an independent T1 layer, this section should become the migration source for Expertise-owned capability identity, firewall, application policy, and generated skill projection.

Minimum fields:

```yaml
object_type: expert_contract
expert_id: <stable id>
expert_version: <monotonic integer>
expert_type: company | crypto_project | macro | technical | industry | behavioral | custom
lifecycle_stage: candidate | draft | reviewed | active | pending_pm_review | deprecated
source_card_pattern_ref: <path or object id>
source_classes: []
claim_types: []
typed_claim_firewall:
  allowed_source_class_claim_type_pairs: []
  blocked_pairs: []
expert_artifacts: []
outputs_allowed: []
outputs_blocked: []
generated_skill_refs: []
review_policy: {}
```

Postgres rows:

- `digestion_objects(object_type='expert_contract')`
- `digestion_edges(edge_type='projects_to_skill')` when a skill projection exists
- `digestion_edges(edge_type='owns_pattern')` to source card pattern / claim firewall projections when modeled separately

Detection boundary:

```text
A skill calls itself an expert, but no expert_contract defines its source_class x claim_type firewall.
```

That skill is not a canonical Digestion expert.

### 3.8 Promotion Link

Promotion Link records how a digestion object enters downstream research or analysis.

Minimum fields:

```yaml
object_type: promotion_link
promotion_id: <id>
from_object_id: <digestion object>
to_surface: thesis_note | theme | report_package | portfolio_decision | watchlist | rejected
to_ref: <downstream id or path>
use_type: evidence | framework | background | falsifier | watch_trigger | rejected_clue
freshness_state_at_promotion: fresh | stale | unknown
promoted_by: agent | human | builder
recorded_at_utc: <ISO-8601 with offset>
notes: <why this was promoted>
```

Postgres rows:

- `digestion_objects(object_type='promotion_link')`
- `digestion_edges(edge_type='promoted_to_thesis' / 'consumed_by_theme' / 'used_in_report')`

Silent violation:

```text
Theme or thesis cites a source card / claim, but no promotion edge exists.
```

This makes downstream belief impossible to audit.

## 4. Postgres Contract

### 4.1 `digestion_objects`

Every durable digestion object has one row.

```text
object_id
object_type
subsystem_id
title
canonical_path
content_hash
status
freshness_state
observed_at_utc
recorded_at_utc
updated_at_utc
metadata_json
```

Allowed initial `object_type`:

- `expert_contract`
- `source_card`
- `typed_claim`
- `framework_card`
- `channel_registry`
- `framework_route`
- `scenario_prediction`
- `expert_artifact`
- `promotion_link`

### 4.2 `digestion_edges`

All cross-object relationships live here.

```text
edge_id
from_object_id
to_object_id
edge_type
confidence
created_at_utc
metadata_json
```

Initial `edge_type`:

- `derived_from`
- `contains_claim`
- `routes_to_channel`
- `uses_framework`
- `supported_by`
- `contradicted_by`
- `falsifies`
- `corroborates`
- `promoted_to_thesis`
- `consumed_by_theme`
- `used_in_report`
- `projects_to_skill`
- `owns_pattern`

### 4.3 `digestion_claims`

Typed query surface for claims.

```text
claim_id
object_id
source_card_id
source_ref
source_class
claim_type
claim_text
elaboration
time_validity
confidence
observed_at_utc
recorded_at_utc
metadata_json
```

This is the primary firewall enforcement table.

### 4.4 `digestion_framework_routes`

Structured channel / role mapping.

```text
route_id
object_id
framework_id
channel_id
role_id
stance
effect
mechanism
horizon
allowed_use
confidence
falsifier_refs
metadata_json
```

### 4.5 `digestion_prompt_runs`

AI worker audit surface.

```text
run_id
runner_backend
model
effort
prompt_template_version
static_prompt_hash
general_module_hash
customize_module_hash
data_dependent_module_hash
input_payload_hash
object_id
status
started_at_utc
completed_at_utc
log_path
metadata_json
```

This table aligns with `bestpractice_external_agent_builder.md`.

## 5. Filesystem Projection Contract

Files are projections for review and human reading. Postgres is the registry and graph backend.

Initial path shape:

```text
data/digestion/
  source_cards/
  claims/
  frameworks/
  expert_subsystems/
    fed_rate/
      expert.json
      source_cards/
      claims/
      frameworks/
      channel_registry/
      scenarios/
      artifacts/
  exports/
  independent_research/
    index.jsonl
    assets/
```

Rules:

1. Every durable file under `data/digestion/` must have a `digestion_objects` row.
2. Every file-backed object must have `canonical_path` and `content_hash`.
3. Edges are not inferred by path shape. Edges must be written to Postgres.
4. Generated index files are derived from Postgres.
5. Drafts may exist outside the registry only under explicit scratch / temp paths; they are not digestion assets.

## 6. Generation Contract

### 6.1 Source Card generation

Input:

```text
source_packet from selected domain route
```

Worker prompt modules:

- `GENERAL_MODULE`
- `CUSTOMIZE_MODULE: <Expert Source Card Writer>`
- `DATA_DEPENDENT_MODULE: <source family>`

Output:

- source card file projection
- `digestion_objects` row
- `digestion_edges(derived_from)`
- `digestion_prompt_runs`
- validation result

Hard block:

```text
No selected expert route or expert contract exists.
```

Generic source-card generation before route selection is not allowed for durable digestion objects.

### 6.2 Typed Claim generation

Input:

- source card
- source span refs
- subsystem firewall config

Output:

- claim objects
- `digestion_claims` rows
- `digestion_edges(derived_from)`

Hard block:

```text
Claim type violates subsystem source_class x claim_type firewall.
```

### 6.3 Framework Route generation

Input:

- typed claims
- framework card
- channel / role registry

Output:

- framework routes
- channel edges
- falsifier refs

### 6.4 Scenario generation

Input:

- current framework state
- typed claims
- framework routes
- historical cases
- falsifiers / missing confirmations

Output:

- scenario prediction
- support / contradiction edges
- allowed downstream use

Hard block:

```text
Scenario lacks claim lineage or channel route lineage.
```

### 6.5 Expert artifact generation

Input:

- framework routes
- scenarios
- claims
- freshness state

Output:

- expert artifact projection
- object / edge rows
- downstream allowed-use contract

### 6.6 Independent research source packet generation

Input:

- research request;
- asset identity;
- local archive search result;
- optional external search result already written to message archive;
- source readiness status.

Output:

- `data/digestion/independent_research/assets/<asset_key>/source_packet.md`
- `source_packet.json`
- `domain_route.json`
- run log rows

Hard block:

```text
External source was used but never written to message archive.
```

### 6.7 Expert factory generation

Input:

- reusable analytical asset candidate;
- existing expert registry;
- source packet or source card candidates;
- overlap analysis.

Output:

- expert contract draft or update;
- source card pattern;
- claim firewall;
- artifact schema;
- generated skill projection request;
- reviewer / adversary task.

Hard block:

```text
The candidate is only a one-off fact, position update, or price move.
```

## 7. Consumption Contract

Downstream consumers must query Postgres, not scan Markdown.

Typical query:

```text
Find fresh source cards / claims / scenario predictions for:
  subsystem_id = fed_rate
  channel_id = front_end_plumbing
  allowed_use in (evidence, watch_trigger)
  freshness_state = fresh
```

Package builders may expand Markdown bodies only after selecting refs through Postgres.

Downstream package should preserve:

- `source_card_id`
- `claim_id`
- `framework_id`
- `route_id`
- `scenario_id`
- `expert_artifact_id`
- `content_hash`
- `freshness_state`
- `allowed_use`

Silent violation:

```text
Writer package includes copied digestion prose but drops object refs and hashes.
```

This breaks stale detection and audit.

## 8. Fed Template Instantiation

The first Fed-shaped instance should use:

```yaml
subsystem_id: fed_rate
framework_id: fed_policy_transmission_expression
framework_layers:
  - state_estimation
  - transmission_diagnosis
  - portfolio_expression
source_classes:
  - primary_policy_record
  - quasi_official_signal
  - academic_framework
  - market_interpretation
  - buy_side_narrative
  - historical_case
claim_types:
  - framework
  - parameter
  - operation
  - market_mapping
  - historical_analogy
  - structural_observation
channels:
  - front_end_plumbing
  - long_end_term_premium
  - credit_creation
  - inflation_expectations
  - dollar_fx
  - asset_price_fci
  - fed_reaction_function
  - fiscal_treasury_supply
```

Minimal dogfood path:

```text
one read_content.md
  -> one source card
  -> 2-3 typed claims
  -> one front_end_plumbing route
  -> one scenario prediction
  -> one promotion link to a thesis or theme candidate
```

This is enough to test the structure contract without building the full Fed KB.

## 9. Contract Boundaries

### 9.1 Digestion does not own final belief

Scenario prediction and expert artifact are conditional analysis assets. Thesis owns belief.

### 9.2 File existence is not asset existence

A Markdown file without Postgres object row is a note, not a digestion asset.

### 9.3 Schema compliance is not content quality

A valid YAML / JSON object can still fail digestion if it drops mechanism, horizon, falsifier, or source authority.

### 9.4 General module cannot serve intention

Every worker prompt must include:

- general module,
- task-specific customize module,
- data-dependent module.

Missing customize or data module means worker only knows style, not task or source semantics.

## 10. Open Questions

1. Should `digestion_objects.object_type` stay broad, or should high-volume object types get dedicated tables first?
2. Should scenario predictions be generated only inside expert subsystems, or can they be cross-subsystem?
3. Should file bodies remain canonical in v0, or should Postgres own canonical object body after dogfood?
4. Should domain-specific source_class / claim_type enums live in Postgres registry tables, YAML sidecars, or both?
5. How should digestion freshness invalidate artifact graph nodes and writer packages?
