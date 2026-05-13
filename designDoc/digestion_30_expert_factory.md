---
title: Digestion Expert Factory
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Domain Expert Maintainer
---

# Digestion Expert Factory

## 1. Purpose

`Digestion Expert Factory` defines how new domain experts are created, reviewed, activated, projected into skills, and kept aligned with the Digestion graph.

It is the Digestion home for the reusable interpretation-framework pattern:

```text
arbitrary source
  -> reusable analytical asset candidate
  -> expert subsystem contract
  -> source card pattern
  -> typed claim firewall
  -> expert artifact schema
  -> generated skill projection
  -> downstream promotion policy
```

The factory produces experts. It does not run a one-off asset research workflow. One-off asset research is owned by `Independent Research Orchestrator`, which selects an already-defined expert route and passes a source packet to that expert.

## 2. Why This Belongs In Digestion

An expert subsystem exists to transform canonical source read content into typed, routed, reusable analysis assets.

That is the Digestion layer.

The expert factory therefore owns:

- reusable analytical asset extraction;
- domain expert admission;
- source card pattern definition;
- source-class and claim-type firewall;
- framework / channel / role route definition;
- expert artifact schema;
- output allow/block rules;
- skill projection metadata;
- lifecycle review for expert subsystem changes.

It does not own:

- PM role authority;
- trader / executor / risk authority;
- portfolio action;
- evidence verification;
- thesis lifecycle promotion.

Those remain downstream operation, research, and PM workflows.

## 3. Relationship To Operating Framework Governance

`Operating Framework Governance` remains responsible for role authority: PM, Trader, Executor, Risk, and the high-level Interpretation role.

It should not store domain lenses directly.

Correct split:

```text
Operating Framework
  -> says Interpretation role may maintain domain experts and hand off candidate objects

Digestion Expert Factory
  -> defines each domain expert's source card pattern, claim firewall, artifacts, and skill projection

Domain Expert
  -> reads source packets and emits domain-owned digestion objects
```

The operating layer answers:

```text
who is allowed to do what
```

The Digestion expert layer answers:

```text
how this domain reads source and what objects it may emit
```

## 4. Reader End-State

After reading an expert factory output, a future agent should know:

- why this expert should exist;
- which sources can update it;
- which sources can only trigger candidate questions;
- how this expert writes Source Cards;
- which typed claims it may emit;
- which outputs it is blocked from writing;
- which expert artifacts it owns;
- when it hands off to thesis, theme, single-stock, crypto, portfolio, or writer workflows;
- how the generated skill points back to the expert contract.

Silent violation:

```text
A skill claims to be an expert, but there is no expert contract defining source_class, claim_type, allowed outputs, blocked outputs, and review state.
```

That skill is a prompt, not an expert subsystem.

## 5. Expert Admission

Create or materially update a domain expert only when a source or repeated workflow reveals a reusable analytical asset.

Admission signals:

- repeatable method;
- metric;
- signal;
- pattern;
- failure mode;
- industry-specific leading indicator;
- stock-selection lens;
- evidence collection question;
- domain-specific report or dossier template;
- source card pattern that differs from existing experts.

Non-admission signals:

- one fact;
- one price move;
- one position update;
- one chart without a reusable method;
- one PM opinion;
- a report that is useful but only as a source, not as a framework.

Non-admitted material stays in message archive, evidence, snapshot, PM note, or asset workspace until it produces a reusable method.

## 6. Expert Factory Pipeline

### 6.1 MetaSkill Extraction

The MetaSkill reads arbitrary source material and asks:

- does this source teach a reusable way to read a domain;
- does it define a metric, signal, pattern, or failure mode;
- does it improve an existing expert's toolkit;
- does it suggest a new company or crypto template;
- does it only provide one-off facts.

Outputs:

- `analysis_asset_candidate`;
- `metric_candidate`;
- `signal_candidate`;
- `pattern_candidate`;
- `framework_rule_candidate`;
- `failure_mode_candidate`;
- `domain_expert_handoff`.

MetaSkill does not absorb the asset. It proposes a route.

### 6.2 Domain Expert Maintainer

The domain expert maintainer decides whether the candidate is:

- absorbed into an existing expert;
- rejected;
- deferred as unresolved;
- routed to a new expert proposal;
- routed to a company template or crypto module update.

The maintainer must separate:

- framework core;
- application snapshot;
- source-specific observation;
- downstream candidate task.

### 6.3 Reviewer

Reviewer confirms:

- the method is reusable across more than one source or future artifact;
- input signals are explicit;
- output types are explicit;
- evidence and thesis boundaries are not blurred;
- overlap with existing experts is named;
- the expert has a source-class and claim-type firewall;
- the expert can produce useful candidate objects without authoring final belief.

### 6.4 Adversary

Adversary attacks:

- overreach;
- false confidence;
- source overfitting;
- missing failure modes;
- hidden portfolio action;
- conflict with existing experts;
- generated skill authority creep.

### 6.5 Maintainer And Projection

The maintainer records lifecycle state, stores the expert contract, and produces or updates skill projections.

Generated skills are projections, not the source of truth.

Every projected skill should carry:

- `projected_from_expert_id`;
- `projected_from_expert_version`;
- `projection_generated_at_utc`;
- `projection_owner`;
- allowed outputs;
- blocked outputs.

If a skill's projected version is older than the active expert contract, the skill is stale.

## 7. Expert Contract

Minimum expert contract fields:

```yaml
expert_id: <stable snake_case id>
expert_version: <monotonic integer>
expert_class: digestion_expert
expert_type: company | crypto_project | macro | technical | industry | behavioral | custom
lifecycle_stage: candidate | draft | reviewed | active | pending_pm_review | deprecated
status: draft | reviewed | active | deprecated
domain: []
purpose: <what this expert reads>
source_requirements: []
source_classes: []
claim_types: []
source_card_pattern:
  required_sections: []
  source_span_policy: <quote / locator requirements>
typed_claim_firewall:
  allowed_source_class_claim_type_pairs: []
  blocked_pairs: []
framework_routes: []
expert_artifacts: []
outputs_allowed: []
outputs_blocked: []
downstream_interfaces: []
review_logs: []
pm_acknowledgements: []
generated_skill_refs: []
review_policy: {}
recorded_at_utc: <ISO-8601>
updated_at_utc: <ISO-8601>
```

### Design Doc as Truth

Expert 有两个持久化表面：

| Surface | 形式 | 内容 | 角色 |
|---------|------|------|------|
| **Design Doc** | `designDoc/digestion_5x_*.md` | value chain、channels（含 observables / falsifiers / typical misuse）、source classes（含 allowed / blocked 及原因）、firewall supplements、validation gates、dogfood examples、cross-expert edge 规则 | **Source of truth**：expert 的完整知识 |
| **expert_contract.yaml** | `data/digestion/expert_subsystems/<expert_id>/expert_contract.yaml` | channels、subtypes、firewall rules、ticker coverage（machine-readable subset） | **Derived index**：服务于 routing 和 validation |

Design doc 包含 YAML contract 的全部信息，plus 只存在于 design doc 中的上下文——value chain 结构、typical misuse patterns、validation gates、dogfood examples。这些上下文是 AI expert 在 runtime 正确判断的关键。

YAML contract 是 design doc 的机器可读派生物。两者冲突时，以 design doc 为准。

消费关系：

```text
Design Doc ──→ Runtime Prompt（expert 的 domain knowledge 层）
             ──→ Human reader（Research Architect 理解 expert）

expert_contract.yaml ──→ Router（确定性 routing）
                      ──→ Validator（产出合规检查）
```

Skill projection 是 thin wiring layer——指向 design doc 和 shared scaffold，不存 domain content。见 [`digestion_31_expert_runtime.md`](digestion_31_expert_runtime.md) §9。

## 8. Source Class Firewall

Every expert declares its source classes.

Initial source class families:

- `official_primary_disclosure`;
- `regulatory_record`;
- `company_filing`;
- `official_project_disclosure`;
- `market_data_surface`;
- `onchain_data`;
- `security_audit`;
- `third_party_research`;
- `curated_practitioner_framework`;
- `market_positioning_signal`;
- `single_observation`;
- `internal_dogfood_synthesis`.

Each expert may narrow or rename these classes.

Rule:

```text
source_class x claim_type route must be explicit per expert
```

Example:

```text
official_project_disclosure can support tokenomics_structure
official_project_disclosure cannot prove real_user_demand
market_data_surface can support liquidity_context
market_data_surface cannot prove fundamental_value
company_filing can support revenue_margin_trend
company_filing cannot prove next-quarter market reaction
```

## 9. Claim-Type Firewall

Each expert declares claim types.

Generic families:

- `framework_rule`;
- `input_signal_definition`;
- `interpretation_mapping`;
- `failure_mode`;
- `source_fact`;
- `proxy_estimate`;
- `cannot_know_boundary`;
- `candidate_thesis_question`;
- `candidate_scenario_question`;
- `evidence_collection_task`;
- `watchlist_mapping`;
- `historical_analogy`.

Domain examples:

- Crypto Project Expert adds `token_supply_pressure`, `real_usage_quality`, `reflexive_upside`, `distribution_pressure`.
- Listed Company Expert may add `business_quality`, `operating_metric_trend`, `competitive_position`, `valuation_context`, `catalyst_path`.

## 10. Expert Artifacts

Expert artifacts are structured subsystem outputs. They are not final PM reports.

Examples:

- `CryptoDecisionBrief`;
- `single_asset_dossier`;
- `company_research_report_draft`;
- `Regime Map`;
- `Trigger Chain`;
- `Stock Pool Impact`;
- `brand_heat_map`;
- `demand_conversion_chain`.

Every expert artifact must list:

- included source card ids;
- included claim ids;
- framework route ids where relevant;
- key uncertainties;
- blocked assumptions;
- downstream allowed use;
- downstream blocked use.

## 11. Company Expert Template Registry

Company templates belong to the Expert Factory.

The company family umbrella lives in `digestion_41_company_expert.md`. The Private Company Expert contract lives in `digestion_41_1_private_company_expert.md`. The Listed Company Expert contract lives in `digestion_41_2_listed_company_expert.md`. The factory owns template admission and maintenance; each expert design owns the runtime interpretation contract for its Source Cards, Typed Claims, and dossier artifact.

Default:

```text
company_expert:default_company_dossier
listed_company_expert:default_company_dossier
private_company_expert:private_company_dossier
```

Future templates use:

```text
company_template:<template_id>
```

A company template may define:

- required sections;
- required source types;
- metric requirements;
- industry-specific signals;
- confidence caps;
- report outputs;
- blocked outputs.

It does not change portfolio authority or thesis lifecycle.

## 12. Crypto Expert Relationship

`Crypto Project Expert` is a domain expert under this factory.

Its canonical route is:

```text
CryptoSourceCard
  -> CryptoClaim
  -> DualTrackRead
  -> CryptoDecisionBrief
```

Its governing design is `digestion_42_crypto_project_expert.md`.

The factory can update the crypto expert contract, but a single crypto research run should not rewrite the crypto framework. It should produce a source packet and let the crypto expert generate its own objects.

## 13. Independent Research Orchestrator Relationship

The orchestrator calls experts. It does not create them.

When the orchestrator cannot find a suitable expert:

```yaml
status: blocked_missing_expert
recommended_handoff: digestion_expert_factory
```

The handoff should include:

- source packet;
- asset identity;
- reusable asset candidate;
- proposed expert type;
- why existing experts do not fit;
- blocked downstream outputs.

## 14. Expert Runtime Scaffold

Expert 在运行时如何被调用——prompt 组成、isolation rule、shared execution rules、routing protocol、multi-expert dispatch、cross-expert edge——由 [`digestion_31_expert_runtime.md`](digestion_31_expert_runtime.md) 管理。

Factory 管 expert 怎么出生和维护；Runtime 管 expert 怎么执行。

## 15. Lifecycle

Expert lifecycle:

- `candidate`: identified but not structured;
- `draft`: structured by MetaSkill / maintainer;
- `reviewed`: reviewer and adversary passes complete;
- `active`: PM or system owner acknowledged the expert for use;
- `pending_pm_review`: material update awaiting acknowledgement;
- `deprecated`: retained for history but not used.

Activation criteria:

- reusable method is clear;
- source classes are declared;
- claim types are declared;
- output firewall is explicit;
- at least one source card pattern is defined;
- at least one expert artifact is defined;
- reviewer and adversary pass;
- PM or system owner acknowledgement when downstream authority changes.

Expert activation is not a belief update. It authorizes a way to read sources.

## 16. Storage

Planned projection root:

```text
data/digestion/expert_subsystems/<expert_id>/
```

Recommended shape:

```text
data/digestion/expert_subsystems/<expert_id>/
  expert.json
  expert.md
  source_card_pattern.md
  claim_firewall.json
  artifact_schemas/
  generated_skill_refs.json
  review_logs/
```

Registry ownership:

- durable expert files should have `digestion_objects` rows;
- generated indexes should come from the registry;
- skill projection metadata should point back to `expert_id` and `expert_version`.

## 17. Detection Boundaries

Design-time violations（Factory scope）：

- a generated skill has no expert contract;
- an expert has no `outputs_blocked`;
- an expert emits final thesis, evidence verification, or portfolio action;
- a source class updates a framework when the expert contract only allows candidate questions;
- a company template is treated as thesis lifecycle authority;
- a crypto project run bypasses `CryptoDecisionBrief`;
- a PM-facing report cites an expert name but no source card, claim, artifact, or promotion link;
- two experts conflict and the writer smooths the conflict away.

Runtime violations 见 [`digestion_31_expert_runtime.md`](digestion_31_expert_runtime.md) §8。

When these appear, stop downstream promotion and repair the expert contract.
