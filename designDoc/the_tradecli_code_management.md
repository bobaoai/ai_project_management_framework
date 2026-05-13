---
title: Runtime Code Admission And Audit Contract
status: active_draft
layer: T0
t0_layer_id: the_tradecli_code_management
canonical_owner: designDoc/the_tradecli_code_management.md
reader_persona:
  - System Builder
  - T1 Owner
  - Runtime Maintainer
  - Engineering Reviewer
---

# Runtime Code Admission And Audit Contract

## 0. Contract Capsule

Machine-audit block. Keep paths, ids, aliases, commands, and ledger pointers plain; use citation ids only in body prose and `References`.

```yaml
layer: T0
t0_layer_id: the_tradecli_code_management
status: active_draft
canonical_owner: designDoc/the_tradecli_code_management.md
scope: governance for T1-owned tradectl and repo runtime code admission, command side-effect safety, doc / skill / code / schema / test sync, and engineering audit routing
non_goals:
  - domain-specific command semantics, which belong to the owning T1 doc
  - PM belief and portfolio decision logic
  - artifact freshness contracts and graph node identity, which belong to the_artifact_graph
  - timestamp field semantics, which belong to the_timestamp_semantic
  - external AI runner profiles and manifests, which belong to the_external_agent_management
inputs:
  - T1 owner Design Doc Contract Capsules
  - tradectl and runtime code change sets
  - data/runtime/schemas shape changes
  - artifact graph builder bindings
  - skills that claim commands, builders, schemas, or runtime hooks
outputs:
  - admitted command and builder discipline
  - cross-cutting sync obligation across docs, skills, code, schemas, fixtures, and tests
  - live-side-effect safety rule
  - engineering audit route through engineering-project-review
truth_surfaces:
  - src/cli/tradectl.py
  - src/cli/*.py
  - src/tools/**
  - data/runtime/schemas/**
  - data/runtime/**
  - 09_codex/skills/engineering-project-review/SKILL.md
  - 09_codex/skills/engineering-project-review/code_external_review_module.md
runtime_triggers: meta-contract; individual commands are triggered by their T1 owners
downstream_consumers:
  - every T1 owner that ships a tradectl command or runtime builder
  - engineering-project-review
  - design-doc-reviewer when reviewing runtime-bearing Design Docs
  - support-external-agent-builder when assembling external code_review prompts
open_decisions:
  - exact audit cadence for periodic engineering-project-review sweeps across T1 command surfaces
  - owner doc for operation-level broker/order commands if operation_00 is not yet specific enough
review_gate: design-doc-reviewer for this contract; engineering-project-review for T1 code changes governed by this contract
runtime_surface_ledger: see Machine Audit Runtime Surfaces
verification_hooks: see Machine Audit Runtime Surfaces
```

## 1. This Document Owns

This T0 contract defines how `tradectl` and repo runtime code are admitted, changed, synchronized, and audited.

Its core rule:

```text
T1 docs own their own TradeCLI/runtime code.
T0 owns the cross-cutting admission and audit discipline.
```

This means there should not be one giant central T0 registry that describes every domain command in detail. Ingestion, Digestion, Research, Operation, market data, and connector docs should each own the command semantics for their own workflow. This document only defines the minimum repo-wide invariants that all of those command surfaces must obey.

## 2. This Document Does Not Own

This document does not own:

- domain-specific command semantics
- PM belief, portfolio decision logic, or research conclusions
- artifact-node freshness definitions
- timestamp field meanings
- external AI runner profiles
- first-draft Design Doc writing style
- one-off implementation details inside a T1 module

Those belong to the relevant T0/T1 owner docs and runtime modules.

## 3. Runtime Scope Under This Contract

The contract applies when a change touches any of these surfaces:

- root CLI dispatch: `src/cli/tradectl.py`
- domain CLI groups: `src/cli/*.py`
- deterministic builders, validators, routers, prompt builders, and utility tools under `src/tools/`
- T1-owned domain runtime modules under `src/<domain>/`
- runtime schemas under `data/runtime/schemas/`
- artifact graph registry and runtime state surfaces under `data/runtime/`
- tests, fixtures, and smoke commands that validate the above
- agent-facing skills that claim a command, builder, schema, or runtime hook exists

The root `tradectl` entrypoint is an implementation dispatch surface, not the canonical owner of all domain meaning. It may list commands for discoverability; ownership remains with the T1 doc or runtime module that defines the workflow.

In this contract, `canonical stores` means archive truth surfaces owned by [T0-Charter], graph-admitted artifact paths owned by [T0-Artifact-Closure], and T1-owned runtime state under `data/runtime/`. It does not create a new storage authority.

## 4. T1 Ownership Rule

Every `tradectl` command group or runtime builder must have exactly one local owner.

Typical ownership:

| Command / code family | Owning doc |
| --- | --- |
| source archive, message, read-content, image-review ingestion commands | `designDoc/ingestion_00_overview.md` and the specific `ingestion_NN_*.md` owner |
| Digestion source packets, domain experts, dossiers, decision briefs | `designDoc/digestion_00_overview.md` and the specific `digestion_NN_*.md` owner |
| research packages, thesis/theme validators, report drafts | `designDoc/research_00_overview.md` and the specific `research_NN_*.md` owner |
| portfolio decision, account review, order preview / live order actions | `designDoc/operation_00_operating_framework_governance.md` until a more specific operation T1 owner is admitted |
| history, macro, fundamentals, market-data fetchers | `designDoc/market_data_architecture.md`, `designDoc/price_data_architecture.md`, and relevant connector / ingestion data docs |
| artifact graph planning and production helpers | `the_artifact_graph` plus the node owner T1 |
| cross-domain review of engineering changes | `engineering-project-review` skill under this T0 contract |

If a new command cannot name its T1 owner, it is not admitted as active runtime. It may remain proposed in a Design Doc, but skills must not claim it as runnable.

## 5. Command Admission Rule

A command is admitted when all of the following are true:

1. A T1 owner doc, Design Doc Contract Capsule, or runtime surface ledger names the command and its purpose.
2. The command has an explicit namespace under `tradectl` or a documented reason for living outside `tradectl`.
3. Inputs, side effects, and output paths are visible from help text, docs, or the owning skill.
4. Date-sensitive behavior aligns with `the_timestamp_semantic`.
5. PM-facing or downstream artifact production aligns with `the_artifact_graph` when the artifact is graph-admitted.
6. The owning skill or T1 doc names the validation hook that proves the command still works.

Do not admit command behavior by implication. "The Python function exists" is not enough; a downstream agent needs to know the owner, invocation surface, outputs, and validation gate.

## 6. Side-Effect Safety

Local file writes are allowed when the command's owner and output paths are explicit.

External or irreversible side effects require stronger gates:

- broker/order actions must default to preview or no-op behavior unless an explicit live confirmation flag is supplied; current `tradectl` order surfaces use `--confirm-live`
- live trading actions must separate decision generation from order placement
- provider writes, token refreshes, and account/broker interactions must expose the side effect in help text or command naming
- commands that mutate canonical stores should either emit a manifest/status artifact or have a deterministic validation hook

No T1 doc may hide live side effects behind a research, report, or package command.

## 7. Sync Obligation

When a T1 owner changes a command or runtime builder, the same change set should update every affected surface:

- owning Design Doc or Contract Capsule
- owning skill text
- `src/cli/tradectl.py` or domain CLI parser
- runtime module or builder implementation
- schema / fixture / validator when data shape changes
- artifact graph node or builder binding when graph-admitted artifacts are affected
- tests or explicit smoke command

This is the code-side version of the Design Doc Review Gate failure mode:

```text
Design Doc changed, but the command / skill / test / prompt builder stayed old.
```

Trigger rule: any change set that touches a runtime surface listed in §3 must state which T1 owner doc, skill, schema, fixture, and test were updated or explicitly mark them as not affected. `engineering-project-review` must run when a change modifies a `tradectl` command name, flag, side effect, output path, runtime schema, graph-admitted builder binding, broker/order/account live-adjacent behavior, or skill claim about a runtime hook. Comment-only and non-runtime helper edits may bypass this trigger when no command behavior, schema, generated artifact, or runtime contract changes.

## 8. Review And Audit Rule

`engineering-project-review` is the local independent reviewer for TradeCLI/runtime code changes when the change touches:

- `tradectl` command names, flags, side effects, or output paths
- schemas, validators, fixtures, or generated package shapes
- skills that claim a command or runtime hook
- artifact graph builder bindings
- broker/order/account live-adjacent behavior
- T0/T1 contract propagation
- cross-runtime mirror surfaces: code or scripts that synchronize authoritative content between `09_soul/`, `09_claude/`, `09_codex/`, `.claude/`, and `.cursor/`

The review should read the actual diff, reproduce claimed validation gates, and check doc / skill / code / test sync. It is review-only; it does not author the patch under review.

External AI review may be used as a second opinion, but it must route through [T0-External-Worker]. External code review must be classified as `external_agent_class: external_formal_reviewer` and `review_target_type: code_review`, with the prompt module owned by `engineering-project-review`. The external worker is an execution surface; the local review owner remains `engineering-project-review`.

## 9. Boundary With Other T0 Layers

- [T0-Charter] overrides this document on object ontology, belief authority, no false precision, and live-decision safety.
- [T0-Task-Intake] decides which task line a user request enters before code execution is chosen.
- [T0-Artifact-Closure] decides artifact node identity, dependency closure, freshness contracts, and canonical builder admission.
- [T0-Time] owns timestamp/date field meanings and valid time comparisons.
- [T0-Doc-Review] owns Contract Capsule and runtime surface ledger requirements for Design Docs.
- [T0-External-Worker] owns external AI execution surfaces and manifests.

For schemas under `data/runtime/schemas/` that bind to graph-admitted artifact nodes, [T0-Artifact-Closure] owns artifact identity, freshness, and builder admission. This document owns the doc / skill / code / test sync discipline around the schema file.

This document owns the code admission and audit discipline that lets those contracts become reliable runtime behavior.

## 10. Machine Audit Runtime Surfaces

```yaml
runtime_surface_ledger:
  - surface: command
    projection: runtime_agnostic
    path_or_command: src/cli/tradectl.py
    owner: designDoc/the_tradecli_code_management.md for dispatch discipline; T1 owner docs for command semantics
    doc_claim: root tradectl entrypoint dispatches T1-owned command groups
    sync_obligation: update help text, command registration, owning T1 docs, and tests when a top-level command group is admitted, renamed, or removed
    status: active
  - surface: command
    projection: runtime_agnostic
    path_or_command: src/cli/*.py
    owner: per-T1 owner doc declared by the command family
    doc_claim: domain command groups admitted under tradectl
    sync_obligation: T1 owner updates its Design Doc capsule, skill claim, parser, output contract, and validation hook in the same change set
    status: active
  - surface: builder
    projection: runtime_agnostic
    path_or_command: src/tools/**
    owner: per-T1 owner doc or shared tool owner declared by the tool contract
    doc_claim: deterministic builders, validators, routers, prompt builders, and audit helpers used by T1 workflows
    sync_obligation: tool behavior changes update owning skill, schemas/manifests, generated artifact contract, and focused tests
    status: active
  - surface: schema
    projection: runtime_agnostic
    path_or_command: data/runtime/schemas/**
    owner: per-T1 schema owner; graph-admitted artifact schemas also coordinate with the_artifact_graph
    doc_claim: machine-readable runtime and artifact shape contracts
    sync_obligation: schema changes update validators, fixtures, downstream consumers, and graph binding when applicable
    status: active
  - surface: skill
    projection: codex
    path_or_command: 09_codex/skills/engineering-project-review/SKILL.md
    owner: designDoc/the_tradecli_code_management.md
    doc_claim: local independent reviewer for tradectl and runtime code changes
    sync_obligation: update when this T0's admission rule, sync obligation, or review-gate checklist changes
    status: active
  - surface: prompt_module
    projection: codex
    path_or_command: 09_codex/skills/engineering-project-review/code_external_review_module.md
    owner: 09_codex/skills/engineering-project-review/SKILL.md
    doc_claim: task-specific module for external code_review prompts
    sync_obligation: update when code-review severity mapping or TradeCLI admission semantics change
    status: active
verification_hooks:
  - ./.venv/bin/python -m src.cli.tradectl --help
  - ./.venv/bin/python -m pytest tests/test_external_review_target_modules.py -q
  - manual engineering-project-review check: for runtime-bearing changes, confirm the review report names T1 owner, affected command/schema/skill/test surfaces, and claimed validation gates
```

## 11. Review-Gate Checklist

For any non-trivial TradeCLI/runtime code change, the reviewer should be able to answer:

- Which T1 owner owns this command or builder?
- What user/task line enters it?
- What local files, stores, schemas, or external providers does it read?
- What side effects can it perform?
- What artifact or state does it produce?
- Which docs/skills mention it?
- Which test, validator, or smoke command proves it still works?
- If it is live-adjacent, is preview/no-op the default and live execution explicit?
- If it produces a graph-admitted artifact, does the artifact graph binding still match?

If those answers are not recoverable, the change is not audit-ready.

This checklist is the reference list for `engineering-project-review`. That skill must cite this contract when reviewing `tradectl`, runtime code, schema, fixture, or graph-builder changes.

## 12. References

- `[T0-Charter]` [Analyst Billie Charter](the_charter.md)
- `[T0-Task-Intake]` [Task Intake Routing Contract](the_task_routing.md)
- `[T0-Artifact-Closure]` [Artifact Dependency Closure Contract](the_artifact_graph.md)
- `[T0-Time]` [Timestamp Semantic Contract](the_timestamp_semantic.md)
- `[T0-Doc-Review]` [Design Doc Review Gate Contract](the_design_doc_management.md)
- `[T0-External-Worker]` [External Worker Execution Contract](the_external_agent_management.md)
- `[Skill:engineering-project-review]` logical skill id `engineering-project-review`; current Codex projection: [Engineering Project Review Skill](../09_codex/skills/engineering-project-review/SKILL.md)
