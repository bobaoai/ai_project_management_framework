---
title: Operating Framework Governance
status: active_draft
recorded_at_utc: 2026-04-28T19:14:00Z
updated_at_utc: 2026-04-28T19:14:00Z
reader_persona:
  - System Builder
  - Portfolio Manager
  - Risk Manager
  - Execution Trader
---

# Operating Framework Governance

## 1. Purpose

`Operating Framework` is the system contract for how `trading_platform` organizes roles, authority, handoffs, gates, and review queues.

It does not answer what the market means. It answers how different operating roles are allowed to reason, decide, verify, act, and hand off work.

This is a T1 governance layer. T1 means the framework is a foundational operating contract that downstream skills, packages, and agents must obey when role authority is involved.

## 2. Core Distinction

Operating and digestion are separate layers. Interpretation is an operating role, but reusable domain interpretation lenses are Digestion experts.

`Operating Framework` manages role systems:

- Portfolio Manager
- Trader
- Executor
- Risk
- Interpretation

The `Interpretation` role may select, apply, review, and route domain experts. The expert definitions themselves live in Digestion.

The relationship is:

```text
Operating Framework
  -> Interpretation Role Framework
      -> may use Digestion experts
  -> Portfolio Manager Role Framework
  -> Trader Role Framework
  -> Executor Role Framework
  -> Risk Role Framework
```

The `Interpretation` role is itself an operating role. It defines authority and handoff rules for reading the world. Domain lenses such as consumer demand sensing, Fed communication surfaces, technical stage analysis, crypto project expert, company expert, and AI power bottleneck mapping are Digestion expert subsystems.

## 3. What Operating Framework Owns

Operating frameworks own:

- role purpose
- role authority
- allowed inputs
- allowed outputs
- handoff contract
- escalation rules
- review gates
- PM acknowledgement requirements
- AI verified update boundaries
- stale / active / deprecated state
- generated skill projection boundaries

Operating frameworks do not own:

- raw source ingestion
- market data capture
- source truth judgment
- direct thesis authoring
- direct evidence verification
- portfolio execution without the relevant role gate

## 4. Role Framework Inventory

### 4.1 Interpretation Role

The interpretation role reads the world.

It can:

- select and apply interpretation frameworks
- generate candidate thesis questions
- generate scenario questions
- generate evidence collection tasks
- identify theme gaps
- prepare inputs for PM review

It cannot:

- write verified evidence by itself
- activate a thesis
- authorize a portfolio action
- bypass PM review on major framework changes

### 4.2 Portfolio Manager Role

The Portfolio Manager role turns sufficiently stable interpretation into book-level decisions.

It can:

- decide add / reduce / hold / hedge / wait framing
- acknowledge belief-relevant evidence
- decide whether active scenarios matter for the book
- set portfolio priority and target-book direction

It cannot:

- skip freshness gates
- treat unreviewed interpretation as a final decision
- let an interpretation framework directly authorize action

### 4.3 Trader Role

The Trader role turns PM intent into market-timing and execution-readiness judgment.

It can:

- define entry conditions
- define invalidation
- define timing risk
- distinguish addable, extended, failed, and watch-only states

It cannot:

- change thesis belief state
- override PM decision scope
- execute orders without Executor authorization

### 4.4 Executor Role

The Executor role turns approved action into implementation.

It can:

- produce execution plans
- translate action into order-ready steps
- record execution audit fields
- surface operational blockers

It cannot:

- invent PM intent
- reinterpret thesis or scenario belief
- ignore Risk constraints

### 4.5 Risk Role

The Risk role defines constraints, exposure checks, failure modes, and stop conditions.

It can:

- block or downgrade actions that violate policy
- define exposure and concentration limits
- force review when risk conditions change
- maintain scenario-aware risk constraints

It cannot:

- become a generic bearish commentator
- replace PM action selection
- replace Interpretation's job of reading the world

## 5. Lifecycle

Every operating framework has a lifecycle:

- `draft`: proposed but not accepted
- `reviewed`: structurally reviewed
- `active`: PM acknowledged and usable in workflows
- `ai_verified_update`: minor update verified by reviewer / adversary path
- `pending_pm_review`: AI verified update awaiting PM review
- `pm_ack_required`: major update awaiting PM acknowledgement
- `deprecated`: kept for history, not used for new workflows

First activation requires PM acknowledgement.

Minor iteration can be AI verified. Major changes require PM acknowledgement.

### 5.1 Runtime Object Contract

Every operating framework record must be machine-readable.

Minimum JSON fields:

- `framework_id`: stable snake_case id.
- `framework_version`: monotonic integer. Starts at `1`; every accepted change increments by `1`.
- `framework_class`: `operating`.
- `framework_type`: e.g. `interpretation_role`, `pm_role`, `trader_role`, `executor_role`, `risk_role`.
- `lifecycle_stage`: one of the lifecycle values in §5.
- `status`: `draft`, `reviewed`, `active`, or `deprecated`.
- `owner_role`: role responsible for maintaining the framework.
- `recorded_at_utc`, `updated_at_utc`.
- `role_authority`: what this role can authorize.
- `allowed_inputs`, `allowed_outputs`.
- `handoff_contracts`: upstream and downstream handoff rules.
- `review_logs`: reviewer and adversary pass references or embedded log entries.
- `pm_acknowledgements`: embedded PM acknowledgement entries.
- `generated_skill_refs`: projected skill paths and projection versions.
- `review_policy`: cadence, next review time, stale threshold, and triggers.

Minimum `index.json` row:

- `framework_id`
- `framework_version`
- `framework_type`
- `lifecycle_stage`
- `status`
- `owner_role`
- `path_json`
- `path_markdown`
- `generated_skill_refs`
- `last_pm_acknowledgement`
- `next_review_at_utc`

`framework-maintainer` is the only writer of the index.

### 5.2 PM Acknowledgement Mechanism

PM acknowledgement lives inside each framework record as `pm_acknowledgements[]`.

Each acknowledgement entry must include:

- `ack_id`
- `framework_id`
- `framework_version`
- `ack_type`: `first_activation`, `major_update`, `deprecation`, or `reactivation`
- `ack_scope`: prose naming the specific authority being acknowledged
- `pm_reviewer`
- `recorded_at_utc`
- `rationale`

First activation requires an entry with `ack_type="first_activation"` for the current `framework_version`.

Major updates require an entry with `ack_type="major_update"` for the new `framework_version`.

AI agents cannot write PM acknowledgement entries.

### 5.3 Version Semantics

Use a monotonic integer version, not semver.

Reason:

- framework changes are governance changes, not software releases
- downstream only needs to know whether the projected skill is current
- `framework_version=7` is easier to audit than `v1.2.3`

Every accepted change increments `framework_version` by `1`.

Draft proposals may carry `proposed_next_version`, but only `framework-maintainer` writes the accepted version.

## 6. Major vs Minor Changes

Major operating-framework changes require PM acknowledgement.

The `operating-framework-reviewer` is the default arbiter of whether a proposed change is major or minor.

The adversary can challenge the classification. PM can override the reviewer. If reviewer and adversary disagree and PM has not ruled, classify as major by default.

Major changes include:

- adding or removing a role
- changing a role's authority
- changing handoff rules
- changing review gates
- changing who can trigger PM review queue
- changing what counts as major vs minor update
- allowing any role to generate or consume a new class of artifact
- promoting a role framework to default routing

Minor changes can be AI verified:

- clarifying wording
- adding examples
- adding failure signals
- adding non-authoritative watch questions
- tightening a boundary without changing authority
- adding source provenance to an already accepted rule

## 7. Review Architecture

Operating frameworks need reviewer and adversary passes.

Reviewer asks:

- Is the role boundary clear?
- Are allowed inputs and outputs explicit?
- Are handoffs testable?
- Are review gates enforceable?
- Is PM acknowledgement correctly scoped?

Adversary asks:

- Where can the role overreach?
- Where can the framework silently authorize too much?
- Where can an AI agent self-verify?
- Where can a stale framework keep driving workflows?
- Where can Interpretation, PM, Trader, Executor, and Risk collapse into each other?

No operating framework becomes `active` without both passes and PM acknowledgement.

## 8. Skill Cluster Implication

This layer implies an `operating-framework` skill cluster.

Minimum agents:

- `operating-framework-extractor`: drafts role frameworks from design decisions and observed workflows
- `operating-framework-reviewer`: checks authority, handoff, and gate clarity
- `operating-framework-adversary`: attacks overreach, self-authorization, and role collapse
- `operating-framework-maintainer`: manages lifecycle, review queue, and version updates
- `operating-framework-router`: selects the active role framework for a task

Generated skills are projections of active frameworks. A generated skill is not the source of truth. The source of truth is the operating framework record and its governance contract.

Cursor is the first projection target:

```text
.cursor/skills/<skill_id>/SKILL.md
```

Claude projection may be added later when cross-runtime synchronization is explicitly needed.

Generated skill frontmatter must include:

- `projected_from_framework_id`
- `projected_from_framework_version`
- `projection_generated_at_utc`
- `projection_owner`

If the skill's projected version is lower than the active framework version, the skill is stale and cannot be treated as canonical.

## 9. Storage Direction

Planned runtime root:

```text
data/analysis/operating_frameworks/
```

Planned files:

```text
data/analysis/operating_frameworks/index.json
data/analysis/operating_frameworks/<framework_id>.json
data/analysis/operating_frameworks/<framework_id>.md
```

This is AnalysisPlatform state, not KnowledgeBase state.

KnowledgeBase stores source memory. Operating frameworks govern how the AnalysisPlatform acts on that memory.

## 10. Boundary With Interpretation Frameworks

Operating frameworks can include an `Interpretation` role framework.

They should not store domain lenses directly. Domain lenses live under Digestion as expert contracts, source card patterns, typed claim firewalls, expert artifacts, and generated skill projections.

Correct:

```text
operating_framework: interpretation_role
  says interpretation can extract, review, adversarially test, and maintain domain lenses

digestion_expert: consumer_demand_sensing_expert
  says how to read beauty and consumer demand signals through source cards, typed claims, and expert artifacts
```

Incorrect:

```text
operating_framework: pm_role
  embeds consumer demand signal taxonomy directly
```

The incorrect form blurs role authority with domain interpretation.

Canonical Digestion references:

- `digestion_00_overview.md`
- `digestion_10_structure_contract.md`
- `digestion_30_expert_factory.md`

## 11. Detection Boundaries

Violations are observable:

- PM role framework includes domain signal taxonomy that belongs to Interpretation.
- Operating framework stores source card pattern, claim type enum, or expert artifact schema that belongs to Digestion.
- Trader role changes thesis belief instead of timing / invalidation.
- Executor invents PM intent rather than implementing approved action.
- Risk role becomes a general market view instead of constraint system.
- Interpretation framework directly writes portfolio action.
- Generated skill differs from the active framework contract and no maintainer review exists.

Fix the operating boundary before continuing downstream.
