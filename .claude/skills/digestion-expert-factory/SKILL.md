---
name: digestion-expert-factory
description: Creates and maintains Digestion domain experts. Use when a reusable analytical method, metric, source-card pattern, typed-claim firewall, company template, crypto module, or generated expert skill needs to be admitted, reviewed, updated, or projected from design docs into skills.
---

# Digestion Expert Factory

## What This Skill Does

Use this skill when the task is to create, update, review, or project a Digestion expert.

This skill is for producing experts, not for running a single asset research workflow.

Canonical shape:

```text
reusable analytical asset
  -> expert admission
  -> expert contract
  -> source card pattern
  -> typed claim firewall
  -> expert artifact schema
  -> generated skill projection
```

For one-off company or crypto research, use `digestion-independent-researcher` first. It will call an existing expert or return `blocked_missing_expert`.

## Desired Result

The desired result is an expert subsystem that can safely generate its own Source Cards, Typed Claims, and Expert Artifacts.

By the end, it should be explicit:

- why this expert should exist;
- what reusable method or template it owns;
- which sources can update it;
- which source classes are allowed;
- which claim types are allowed;
- which outputs are allowed and blocked;
- what artifact schemas it owns;
- which skill projection corresponds to the active expert contract;
- which downstream workflows may consume its outputs.

If a skill claims expert authority without an expert contract and output firewall, this skill has failed.

## Primary Truth Surfaces

Read first:

- `designDoc/digestion_30_expert_factory.md`
- `designDoc/digestion_10_structure_contract.md`
- `designDoc/digestion_00_overview.md`

Read when relevant:

- `designDoc/digestion_20_independent_researcher.md`
- `designDoc/digestion_42_crypto_project_expert.md`
- `.claude/skills/digestion-interpretation-metaskill/SKILL.md`
- existing expert skill or design doc being updated

Operating role authority remains in:

- `designDoc/operation_00_operating_framework_governance.md`

Do not move PM / Trader / Executor / Risk authority into a Digestion expert.

## Admission Question

Ask first:

```text
Does this material teach a reusable way to read a domain, or is it only a one-off source?
```

Admit when it provides one or more:

- repeatable method;
- metric;
- signal;
- pattern;
- failure mode;
- industry-specific leading indicator;
- stock-selection lens;
- evidence collection question;
- company or crypto report template;
- domain-specific Source Card pattern.

Do not admit:

- one fact;
- one price move;
- one position update;
- one chart without reusable method;
- one PM opinion;
- ordinary report summary.

Non-admitted material stays in message archive, evidence, snapshot, PM note, or asset workspace.

## Expert Contract

Every expert needs a contract with at least:

```yaml
expert_id: <stable snake_case id>
expert_version: <monotonic integer>
expert_class: digestion_expert
expert_type: company | crypto_project | macro | technical | industry | behavioral | custom
lifecycle_stage: candidate | draft | reviewed | active | pending_pm_review | deprecated
domain: []
purpose: <what this expert reads>
source_requirements: []
source_classes: []
claim_types: []
source_card_pattern:
  required_sections: []
typed_claim_firewall:
  allowed_source_class_claim_type_pairs: []
  blocked_pairs: []
expert_artifacts: []
outputs_allowed: []
outputs_blocked: []
downstream_interfaces: []
generated_skill_refs: []
review_policy: {}
```

The contract is the authority surface. A `SKILL.md` is only a projection.

## Factory Pipeline

### 1. Extract Candidate

Use `digestion-interpretation-metaskill` when starting from an arbitrary report, message, chart, or repeated local analysis.

Expected candidate:

- `analysis_asset_candidate`
- source provenance
- proposed expert
- proposed asset class
- blocked downstream outputs

### 2. Decide Expert Route

Return one:

- `absorb_into_existing_expert`
- `create_new_expert`
- `create_or_update_company_template`
- `update_crypto_project_expert`
- `defer_pending_validation`
- `reject_as_not_reusable`

### 3. Define Firewall

Specify:

- `source_classes[]`
- `claim_types[]`
- allowed `source_class x claim_type` pairs
- blocked pairs
- confidence caps
- cannot-know boundaries

### 4. Define Artifacts

Specify the expert outputs:

- Source Card pattern
- Typed Claim schema
- Framework Route if relevant
- Expert Artifact / Dossier / Decision Brief schema
- Promotion policy

### 5. Review And Adversary

Reviewer checks reuse, schema clarity, overlap, and handoff boundaries.

Adversary attacks overreach, false confidence, source overfitting, hidden portfolio action, and generated skill authority creep.

### 6. Project Skill

When an expert is active or approved for dogfood, create or update the skill projection.

Projection frontmatter or body should include:

- `projected_from_expert_id`
- `projected_from_expert_version`
- `projection_generated_at_utc`
- `projection_owner`
- allowed outputs
- blocked outputs

## Company Template Registry

Company research templates are expert-factory objects.

Default:

```text
company_expert:default_company_dossier
```

Future templates:

```text
company_template:<template_id>
```

A company template may define sections, metrics, source requirements, report shape, and confidence caps. It does not authorize thesis lifecycle or portfolio action.

## Crypto Expert Boundary

Crypto project research routes through `Crypto Project Expert`.

Canonical shape:

```text
CryptoSourceCard
  -> CryptoClaim
  -> DualTrackRead
  -> CryptoDecisionBrief
```

Do not route crypto by default into thesis/theme writing.

## Blocked Outputs

This skill must not directly write:

- active thesis notes;
- evidence records;
- `ai_verified=true`;
- scenario activation;
- PM acknowledgement entries;
- portfolio action;
- order or execution plans.

It may create candidate tasks or projection requests for those owning workflows.

## Completion Standard

This skill is complete when it leaves one of:

- expert contract draft;
- expert contract update proposal;
- company template contract;
- crypto expert module update proposal;
- generated skill draft tied to expert version;
- `reject_as_not_reusable`;
- `defer_pending_validation`;
- `blocked_missing_authority`.

Minimum handoff:

```yaml
expert_id: <id or proposed id>
decision: <absorb/create/update/reject/defer>
source_basis: []
source_classes: []
claim_types: []
outputs_allowed: []
outputs_blocked: []
skill_projection: <path or none>
review_needed: <reviewer/adversary/PM/system_owner>
```

## Failure Signals

Treat these as failures:

- a generated skill has no expert contract;
- `outputs_blocked[]` is absent;
- the expert emits final belief or portfolio action;
- source class authority is not explicit;
- claim types are generic enough to allow anything;
- a company template becomes a thesis/theme route;
- a crypto project run bypasses `CryptoDecisionBrief`;
- an expert conflict is smoothed over in prose instead of preserved.
