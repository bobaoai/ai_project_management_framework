---
title: Design Doc Review Gate Contract
status: active_draft
layer: T0
t0_layer_id: the_design_doc_management
reader_persona:
  - System Builder
  - Design Doc Author
  - Design Doc Reviewer
  - Runtime Projection Maintainer
---

# Design Doc Review Gate Contract

## 0. Contract Capsule

Machine-audit block. Keep paths, ids, aliases, commands, and ledger pointers plain; use citation ids only in body prose and `References`.

```yaml
layer: T0
t0_layer_id: the_design_doc_management
status: active_draft
canonical_owner: designDoc/the_design_doc_management.md
scope: governance for free-form Design Doc drafting, bounded metadata / reasoning prose split, review-gate auditability, Contract Capsule recovery, runtime surface ledger discipline, T0 layer id registry, and Design Doc external-review prompt assembly
non_goals:
  - domain-specific correctness of any T1 workflow
  - external AI runner mechanics and stale-output policy, which belong to the_external_agent_management
  - code-level TradeCLI / runtime admission, which belongs to the_tradecli_code_management
  - PM belief, investment judgment, evidence truth, and report prose quality
inputs:
  - free-form Design Doc drafts and materially updated active Design Docs
  - adjacent owner docs named by the target
  - runtime, skill, schema, prompt, or runner surfaces named by the target
outputs:
  - recoverable Contract Capsule
  - runtime surface ledger and verification hooks for runtime-bearing docs
  - design-doc-reviewer verdict and reviewer notes
  - T0 layer id admission discipline
truth_surfaces:
  - designDoc/README.md
  - 09_codex/skills/support-design-doc-reviewer/SKILL.md
  - 09_codex/skills/support-design-doc-reviewer/design_doc_external_review_module.md
  - src/tools/build_doc_review_prompt.py
  - tests/test_doc_review_prompt_builder.py
runtime_triggers: see Machine Audit Runtime Surfaces
downstream_consumers:
  - support-design-doc-reviewer
  - support-external-agent-builder
  - T0/T1 Design Doc authors and reviewers
  - runtime projections that consume Design Doc authority
open_decisions:
  - status remains active_draft until the current T0 external-review cleanup pass closes capsule / ledger findings across admitted T0 docs
review_gate: design-doc-reviewer
runtime_surface_ledger: see Machine Audit Runtime Surfaces
verification_hooks: see Machine Audit Runtime Surfaces
```

## 1. 这份文档负责什么

本文件定义 Hoveath / Analyst Billie 里 Design Doc 的写作自由与审计纪律。

它的核心立场：

```text
Design Doc 作者保持自由写作。
Design Doc Reviewer 负责把自由文本投影成可审计 contract。
```

The metadata / prose split is a T0 writing law:

```text
Metadata, capsules, ledgers, and schema-like fields are bounded audit surfaces.
Body prose is the reasoning surface where mechanism, examples, judgment, and reader gain may expand.
```

因此本文件不要求每篇 Design Doc 写成填表文档。正文可以是推理、叙事、系统图、反例、设计备忘、迁移计划或审计报告。它只要求每篇进入长期系统面的 Design Doc，最终都能被 reviewer 抽取出一份稳定的 contract capsule。

## 1.5 Drafting Mode vs Review Gate

Design Doc writing has two modes.

### Drafting mode

When the user asks in a command-line conversation to "write a Design Doc", the authoring agent should prioritize:

- design clarity
- problem framing
- alternatives and tradeoffs
- examples and failure modes
- reader judgment

The authoring agent should not force the first draft into a table, capsule, or checklist unless the user explicitly asks for that shape. A draft may remain narrative, exploratory, or proposal-shaped.

### Review gate

When the draft is being finalized, promoted, materially updated, or propagated into skills / routing / code / schemas / runner commands, `design-doc-reviewer` must run.

`design-doc-reviewer` is a review-gate alias for the logical skill [Skill:support-design-doc-reviewer], not a runtime projection path.

At that point the reviewer explicitly requires the Contract Capsule, runtime surface ledger, and verification hooks to be recoverable. Missing recoverable fields may be patched. Missing unrecoverable fields become review findings.

This contract therefore binds the review process, not the writer's first creative pass.

## 2. Contract Capsule

Contract Capsule 是 Design Doc 的可审计投影，不是作者起草时的写作模板。

It is part of the machine-audit contract. It should use plain YAML paths, ids, and command names, not prose citations.

作者可以在文档顶部主动写 capsule；也可以只写正文，让 reviewer 在 review gate 补上或提出缺口。reviewer 补 capsule 时，不得改变正文主张；只能抽取、归纳、标出 open decision，或返回给作者修订。

### 2.1 必须可恢复的字段

以下字段不要求每篇正文逐项填完，但 reviewer 必须能从文档中恢复出来。如果恢复不出来，就是 review finding。

```yaml
layer: T0 | T1 | T2 | temp | legacy
t0_layer_id: <the_* stable layer id; required when layer = T0>
status: active | active_draft | proposal | deprecated_pointer | legacy_context | temp_audit
canonical_owner: <this doc path or owner doc path>
scope: <what this doc owns>
non_goals: <what this doc explicitly does not own>
inputs: <upstream artifacts / truths consumed>
outputs: <artifacts / decisions / contracts produced>
truth_surfaces: <files, schemas, indexes, runtime stores, or docs that make claims checkable>
runtime_triggers: <commands, builders, skills, or none>
downstream_consumers: <skills, docs, runtime modules, or artifacts that rely on this doc>
open_decisions: <unsettled choices that must not be treated as implemented contract>
review_gate: <design-doc-reviewer | domain reviewer | engineering-project-review | none>
runtime_surface_ledger: <review-gate required when this doc names executable commands, builders, schemas, skills, runners, or tests>
verification_hooks: <review-gate required when runtime_surface_ledger is non-empty>
registry_path: <path to per-module Python registry file; required when module has a typed registry>
```

Authors may also include `reader_persona` to declare expected reader roles. It is editorial enrichment, not a binding capsule field unless a domain owner explicitly makes it part of that domain's capsule.

### 2.2 字段解释

| Field | Meaning | Common failure |
| --- | --- | --- |
| `layer` | Authority level of the doc | a T1 domain doc silently changes T0 routing |
| `t0_layer_id` | Stable id for a T0 layer; must start with `the_` | a T0 layer is referred to as `charter`, `timestamp_semantic`, or `design_doc_management` in one place and a different bare name elsewhere |
| `status` | How binding the doc is today | proposal language is consumed as active contract |
| `canonical_owner` | Where future changes belong | two docs both contain full rule bodies |
| `scope` | What problem the doc owns | doc title says one thing, body governs adjacent systems |
| `non_goals` | What the doc refuses to own | downstream work leaks into upstream contract |
| `inputs` | Required upstream artifacts | workflow cannot start deterministically |
| `outputs` | Produced artifact / contract | reader cannot tell what "done" means |
| `truth_surfaces` | Concrete checkable surfaces | design says "index" but no file/store exists |
| `runtime_triggers` | Commands/builders/skills that enact it | skill says run Python but no command exists |
| `downstream_consumers` | Who reads or depends on it | downstream prompt reads archive internals by habit |
| `open_decisions` | Real unresolved choices | TODO is phrased as implemented behavior |
| `review_gate` | Required reviewer before propagation | author self-review is mistaken for independent review |
| `runtime_surface_ledger` | Executable / machine-read surfaces the doc claims | doc changes CLI flags but command examples and tests stay old |
| `verification_hooks` | Smoke tests, unit tests, or manual checks proving runtime claims still bind | reviewer accepts prose while the command no longer runs |
| `registry_path` | Path to per-module typed Python registry; required when module has a typed registry | Design Doc declares class assignments but no registry exists to validate them |

## 2.5 Body References vs Machine Paths

Design Doc prose and machine-audited blocks have different reference rules.

This section governs durable Design Doc body prose. Codex chat / review-response file links are a top-level Codex Always Rule in `AGENTS.md`.

正文中的 normative repo-local dependency should use a human-readable name plus a short citation id, then resolve that id in a visible `References` section. The citation id is an audit handle, not a replacement for prose meaning.

Example:

```md
Task routing follows the Task Intake Routing Contract [T0-Task-Intake]. External review prompt assembly follows the external agent builder skill [Skill:support-external-agent-builder].

## References

- `[T0-Task-Intake]` [Task Intake Routing Contract](the_task_routing.md)
- `[Skill:support-external-agent-builder]` logical skill id; current Codex projection: [External Agent Builder Skill](../09_codex/skills/support-external-agent-builder/SKILL.md)
```

Machine-audited blocks keep plain paths and commands:

- YAML frontmatter
- Contract Capsule fields
- `runtime_surface_ledger`
- `verification_hooks`
- code blocks, shell commands, glob patterns, and placeholders

Those areas are for hardcoded audit, not prose navigation. Do not force Markdown links into them.

The review gate should distinguish:

- **Normative body references**: external docs, skills, schemas, code paths, indexes, or generated artifacts whose contents affect the claim being made. These should have citation ids and a visible reference-list link.
- **Non-normative mentions**: examples, historical notes, obvious repeated mentions after a first citation, or machine-readable path lists. These do not need a separate citation.

### 2.5.1 T0 Layout Rule

T0 documents should keep these surfaces visually separate:

| Surface | Purpose | Link style |
| --- | --- | --- |
| YAML frontmatter | repo-level metadata | plain values |
| `## 0. Contract Capsule` | recoverable machine-audit contract | plain paths / ids / aliases |
| Body prose | human and agent reasoning surface | readable names plus citation ids, such as `Timestamp Semantic Contract [T0-Time]` |
| `Machine Audit Runtime Surfaces` | ledger, hooks, commands, concrete projection paths | plain paths / commands |
| `References` | citation id resolution for body prose | clickable Markdown links |

The reviewer should not require the first draft to follow this layout. At review gate, active T0/T1 docs should converge toward it.

## 2.6 Logical Skills vs Runtime Projections

Design Docs manage logical skill contracts. Runtime directories implement projections of those skills.

This is the boundary:

```text
Design Doc body -> logical skill id
References -> logical skill id plus available projection links
runtime_surface_ledger -> concrete projection path for hard audit
```

正文 should not treat `09_codex/skills/**`, `09_claude/skills/**`, `.claude/skills/**`, or `.cursor/skills/**` as the canonical skill itself. Those are runtime projections.

Use a stable logical skill citation in body prose:

```md
Design Doc review is handled by [Skill:support-design-doc-reviewer].

## References

- `[Skill:support-design-doc-reviewer]` logical skill id; current Codex projection: [Design Doc Reviewer Skill](../09_codex/skills/support-design-doc-reviewer/SKILL.md)
```

When a claim is genuinely projection-specific, say so explicitly:

```md
The current Codex projection for [Skill:support-design-doc-reviewer] carries the external review module used by the Codex prompt builder.
```

Concrete projection paths still belong in the runtime ledger:

```yaml
runtime_surface_ledger:
  - surface: skill
    projection: codex
    path_or_command: 09_codex/skills/support-design-doc-reviewer/SKILL.md
```

Reviewer stance:

- `skill_id` is stable conceptual identity.
- Runtime projection path is executable / readable local implementation.
- A Design Doc may require a skill by logical id.
- A runtime projection may be the current available implementation.
- Only the ledger should make the hardcoded projection path an audit target.

## 3. Writing Freedom

Design Docs are allowed to be different shapes.

Allowed shapes:

- architectural contract
- domain overview
- source-family playbook
- schema support note
- migration plan
- implementation audit
- temporary investigation report
- deprecated pointer
- retrospective

Authors should optimize for reader judgment, not capsule completeness. If a design needs a diagram, narrative, failure story, or long example, write it. The review gate exists so the writer does not have to stop every paragraph to maintain a table.

The capsule is the audit surface. The body is the thinking surface.

### 3.1 Bounded Metadata And Reasoning Prose

Design Docs should keep audit metadata bounded and let reasoning prose carry the full design argument.

Bounded surfaces include:

- YAML frontmatter
- Contract Capsule fields
- runtime surface ledgers
- verification hooks
- schema-like metadata tables
- machine paths, ids, aliases, and command shapes

These surfaces exist for identity, routing, audit, dependency closure, review gates, and machine checks. They should be stable, compact, and difficult to reinterpret. A field that cannot be checked or routed should not be added just because the prose contains a rich idea.

Reasoning prose exists for:

- mechanism
- examples
- failure modes
- tradeoffs
- reader judgment
- field rationale
- cannot-know / cannot-support nuance
- domain-specific writing quality

The review gate may require missing recoverable metadata before promotion. It must not compress the reasoning surface into metadata just to make the document look more structured. Field completeness is not contract success if the reader can no longer understand the mechanism, judgment, or boundary being carried.

This rule applies across Design Docs, Source Cards, phase notes, Theme writing, Expertise contracts, and other long-lived artifact contracts: bounded metadata gives the system handles; expansive prose transfers judgment.

### 3.2 Auditable YAML Blocks

Material and Expertise contracts should include auditable YAML blocks when they define a reusable contract shape or dogfood instance.

Rules:

- Use a short text label immediately before the fenced block, such as `Machine-auditable contract block:` or `Machine-auditable dogfood block:`.
- The fenced block must be valid YAML under ` ```yaml `.
- Keep it to fields that a test, reviewer, builder, or future schema can actually read.
- Put mechanism, rationale, edge cases, examples, and cannot-support nuance in prose around the block.
- Do not use placeholder-only YAML as the only auditable surface for an admitted child contract; if the contract is admitted, at least one block should name `contract_id` or `schema_kind`.
- Dogfood examples may carry real ids and refs even before a runtime schema exists.
- Any date / timestamp field in an auditable YAML block must follow the Timestamp Semantic Contract [T0-Time]. Prefer semantic field names such as `created_at_utc`, `valid_until_calendar_day_utc`, `session_date_market`, or `recorded_at_utc`.
- Bare time names such as `date`, `timestamp`, `valid_until`, `created_at`, or `updated_at` are not allowed in new auditable YAML blocks unless the block is explicitly documenting a legacy field and names the replacement.
- Artifact Graph [T0-Artifact-Graph] takes over only when a YAML block is used as a graph node, edge, freshness predicate, sidecar, provenance, or builder surface.

Minimum contract-shape block:

```yaml
contract_id: <stable_contract_id>
schema_kind: <contract_shape | dogfood_instance | runtime_schema_candidate>
owner_t1: <material | expertise | digestion | research | operation>
status: active_draft
required_fields: []
blocked_outputs: []
runtime_schema_status: not_admitted | proposed | active
timestamp_semantics: follows designDoc/the_timestamp_semantic.md
```

Reviewer rules:

- If a Material or Expertise contract defines a durable object or relation but has no auditable YAML block, flag `missing_auditable_yaml_block`.
- If a block contains fields whose semantics are explained nowhere in prose, flag `yaml_without_reasoning_surface`.
- If prose changes a field requirement but the auditable block stays old, flag `contract_block_drift`.
- If a block contains a date / timestamp field that does not follow Timestamp Semantic naming, flag `timestamp_semantic_violation`.

## 4. Reviewer Contract

`design-doc-reviewer` is a sub-reviewer under the self-review family.

It runs when a Design Doc draft is ready for review, finalization, promotion, or propagation into skills / routing / code / schemas / runner commands. It also runs when an already-active Design Doc is materially updated, or during audit when an existing doc family shows drift.

The reviewer is allowed to:

- add or normalize the Contract Capsule
- add a short `Reviewer Notes` section
- mark open decisions
- convert a migrated full doc into a deprecated pointer when the canonical owner is clear
- flag stale references, missing runtime triggers, duplicated authority, or contract drift
- flag metadata overreach when schema-like fields swallow reasoning that belongs in body prose
- flag missing or stale auditable YAML blocks for admitted Material / Expertise contracts

The reviewer is not allowed to:

- rewrite the design argument as the author
- collapse mechanism, examples, failure modes, or judgment prose into metadata-only fields
- silently decide an open product/design question
- move a proposal into active contract without owner/PM approval
- replace domain-specific reviewers such as evidence reviewer, theme report reviewer, or engineering project reviewer
- add runtime requirements that the codebase cannot satisfy

## 5. Review Procedure

The reviewer runs these checks in order.

### 5.1 Classify

Classify the document:

```text
T0 system contract
T1 domain / workflow contract
T2 schema / implementation support
temp audit / investigation
legacy / deprecated pointer
```

If the doc class is unclear, stop and mark `layer: unresolved` rather than guessing.

### 5.2 Recover The Capsule

Recover the Contract Capsule from the document body.

If a field is absent but recoverable, fill it.
If a field is not recoverable, add a finding such as:

```text
missing_contract_field: runtime_triggers
```

Do not invent a trigger, owner, or output just to make the capsule look complete.

### 5.3 Check Authority

Check whether the doc is claiming authority it should not have.

Common checks:

- A domain doc must not override T0 routing.
- A schema support doc must not redefine workflow ownership.
- A deprecated pointer must not retain a full competing rule body.
- A temp audit must not become the canonical source by being more detailed than the real contract.
- A T0 system contract must declare a stable `t0_layer_id` starting with `the_`.

Canonical T0 layer ids currently admitted:

```text
the_charter
the_task_routing
the_artifact_graph
the_timestamp_semantic
the_design_doc_management
the_contract_audit
the_tradecli_code_management
the_external_agent_management
```

### 5.4 Check Upstream And Downstream Contracts

For each input and output, verify the adjacent document or artifact exists.

Check:

- upstream input names match real artifact names
- output path exists or is clearly proposed
- downstream consumer reads the declared surface, not an older cache
- runtime trigger exists when the doc says an operator can run it
- open decisions are not described as finished implementation

### 5.4.1 Check Surface Ownership Drift

Check whether the target keeps the four-surface ownership split intact (extended from Charter v1.6 by the Contract Audit Architecture [T0-CA]):

```text
DesignDoc owns what / why / boundary / authority / class assignment reasoning.
Registry owns typed refs / class definitions / structural validation.
Skills own how an AI should act now.
Code owns how something can be deterministically checked or executed.
```

Registry is admitted by [T0-CA]. When a module declares a `registry_path`, the registry becomes the typed authority for class ids, ref lists, and structural validation. The DesignDoc remains the upstream authority for design intent and class assignment reasoning. The sync direction is: DesignDoc prose → Registry → Code / Skills.

This is a review-gate check, not a first-draft writing constraint. A draft may be exploratory. Before promotion or propagation, the reviewer must flag places where one surface starts doing another surface's job.

Reviewer rules:

- DesignDocs may define recognized objects, workflows, artifact shapes, why they exist, boundaries, owners, and synchronization obligations. DesignDocs do not maintain complete ref id lists when a registry exists.
- Registry owns all typed class ids, ref lists, and structural validation. Registry does not own design reasoning or boundary justification.
- T1 DesignDocs may define AI workflow semantics as durable authority; the corresponding Skill is the runtime projection that tells an AI how to act now.
- Skills may orchestrate admitted Code, but they do not own deterministic command behavior, schema validation, or executable results.
- Code may enforce and validate deterministic behavior, but it must not become the hidden authority for why a workflow exists or which domain boundary wins.
- Produced artifacts, reports, sidecars, and runtime stores hold generated state; they are not independent design authority unless a DesignDoc explicitly makes that artifact the canonical state surface and lists the relevant ledger / validation hook.
- External worker prompts must keep model / CLI identity as execution surface; the task lens belongs to the owner Skill and the authority lens belongs to the owner DesignDoc.
- If a DesignDoc maintains complete ref id lists (section ending with "refs:" followed by per-line ids) and the module has a `registry_path`, flag `ref_list_belongs_in_registry`.

Common findings:

- prose embeds registry-like fields that should be in a projection / runtime surface, with no `Machine Audit Runtime Surfaces` ledger
- a DesignDoc maintains complete ref id lists that duplicate the registry
- a registry changes class assignment without a corresponding DesignDoc prose update
- a Skill changes durable domain authority without pointing to the owner DesignDoc
- Code changes workflow contract behavior but no owner DesignDoc update or implementation-only declaration exists
- a generated report, sidecar, or runtime output is cited as design authority rather than produced state
- an external-review prompt treats the model / CLI identity as the review lens instead of execution metadata

### 5.4.2 Check Registry Alignment

When a Design Doc declares a `registry_path`, check the alignment between Design Doc prose and the typed registry.

Reviewer rules:

- The registry file must exist and be importable as Python.
- Class ids mentioned in Design Doc prose (in backtick format) must exist in the registry.
- If the Design Doc declares a class assignment ("writer is a Tool, not a Skill"), the registry's class type for that entity must match.
- If the Design Doc declares "Skill layer is empty for this module", the registry must contain zero Skill instances.
- If the Design Doc declares forbidden outputs, the registry's `forbidden_output_refs` should be consistent.

This check is a lightweight version of the full three-layer audit defined in [T0-CA] §7. The full audit (capsule recovery + registry structural validation + AI semantic alignment) is the canonical mechanism. This reviewer step catches the most common mismatches without requiring a full AI audit pass.

Common findings:

- `registry_file_missing`: `registry_path` declared but file does not exist or fails import
- `class_id_not_in_registry`: Design Doc prose mentions a class id that the registry does not contain
- `class_assignment_mismatch`: Design Doc says "X is a Tool" but registry has X as a Skill or Agent
- `skill_layer_contradiction`: Design Doc says "no Skills" but registry contains Skill instances
- `forbidden_output_drift`: Design Doc forbidden output list and registry `forbidden_output_refs` disagree

### 5.4.3 Check Machine Audit Runtime Surfaces

If a Design Doc names any command, builder, schema, skill, prompt module, runner, CLI flag, test, generated artifact, or executable code path, the review gate must recover or patch a runtime surface ledger. The author does not need to include this ledger during first drafting. Before the doc is treated as canonical or propagated, the ledger must exist in the capsule, in a dedicated `Machine Audit Runtime Surfaces` section, or in reviewer notes.

Minimum ledger shape:

```yaml
runtime_surface_ledger:
  - surface: <command | builder | builder_command | skill | prompt_module | registry | schema | helper | runner | rule | doc | test | generated_artifact>
    projection: <codex | claude_code | cursor | portable | runtime_agnostic | n/a>  # optional; required when a surface is a runtime projection
    path_or_command: <exact local path or command shape>
    owner: <owning Design Doc / skill / runtime module>
    doc_claim: <what this doc claims about the surface>
    sync_obligation: <what must change together if this surface changes>
    status: active | proposed | deprecated | external_dependency
verification_hooks:
  - <unit test, smoke command, schema validation, or explicit manual check>
```

This is the contract that prevents the common failure:

```text
Design Doc changed, but the command / skill / test / prompt builder stayed old.
```

Reviewer rules:

- If a doc includes a copy-pastable command, the command's flags must match the current code or be marked `proposed`.
- If a doc references a concrete skill projection path, the skill file must exist or be marked `proposed`.
- If a doc body references a skill as canonical, prefer logical `Skill:<skill_id>` citation and keep concrete projection paths in the ledger.
- If a doc references a schema or generated artifact, the owner and validation hook must be named.
- If a doc changes a command contract, at least one verification hook must exercise the new command shape or explicitly state why no automated hook exists.
- Do not accept "run the tool" as a hook; name the exact command, test, or manual artifact check.

### 5.4.4 Check Bounded Metadata And Reasoning Prose

Check whether the document preserves the metadata / prose split from §3.1.

Reviewer rules:

- Metadata, capsules, ledgers, and schema-like tables should stay compact, recoverable, and machine-auditable.
- Body prose should remain free to carry mechanism, examples, failure modes, tradeoffs, and judgment transfer.
- A document may define minimum required fields, but those fields should not pretend to contain the whole reasoning surface.
- When a field list grows large enough to describe method, salience, stance, causal mechanism, falsifiers, or reader interpretation, the reviewer should ask whether that content belongs in prose or a dedicated child contract.
- If the body prose is thin because all meaning was pushed into metadata, flag `reasoning_compressed_into_metadata`.
- If metadata is unbounded because it tries to carry every nuance of the writing, flag `metadata_overreach`.

Common findings:

- a Source Card or expert artifact contract hardens dozens of fields but leaves no prose room for source voice, mechanism, or cannot-support reasoning
- a Theme or phase-writing contract treats prose quality as a checklist instead of preserving the writer's judgment surface
- a Design Doc adds audit fields that no reviewer, builder, or downstream consumer can check
- a reviewer patch removes examples and failure modes while normalizing the capsule

### 5.4.5 Check Body References

For prose outside YAML / code / command blocks, check whether normative repo-local dependencies remain readable in place and also resolve to clickable entries in a visible `References` section.

Reviewer rules:

- If the body makes a normative claim that depends on another local doc, skill, schema, code file, index, or generated artifact, the first body-level mention should include a human-readable name plus a short id, such as `Timestamp Semantic Contract [T0-Time]` or `Design Doc reviewer skill [Skill:support-design-doc-reviewer]`.
- Do not leave a citation id standing alone as the only meaningful text in a sentence or list item.
- The target must contain a visible `References` section that maps the id to a clickable Markdown link.
- The linked path must exist, unless explicitly marked `proposed`, `external_dependency`, or historical.
- Repeated mentions after the first citation may use the citation id, the title, or an inline code path.
- Do not require citation ids for YAML frontmatter, Contract Capsule paths, runtime ledger paths, verification hooks, shell commands, code blocks, glob patterns, or placeholders. Those remain plain auditable paths.

Common findings:

- body says "see `the_timestamp_semantic.md`" but the document has no reference-list link
- body cites `[T0-Time]` but the `References` section has no matching entry
- body list item says only `[Knowledge-Memory]`, forcing readers to jump to references to understand the sentence
- reference-list link points to a moved or deleted file
- a YAML path is converted into a Markdown link, making hardcoded audit harder

### 5.4.6 Check Skill Projection Boundary

For body prose, check that skill references are logical, not accidentally tied to the current runtime.

Reviewer rules:

- Body prose should reference skills by logical id, such as `[Skill:support-design-doc-reviewer]`.
- `References` entries for skills should name the logical skill id and may list current projection links, such as Codex / Claude Code / Cursor.
- If only one projection exists today, the entry may say `current Codex projection`; it must not imply that Codex is the skill's canonical identity.
- Runtime projection paths belong in `runtime_surface_ledger.path_or_command`, with `projection` named when useful.
- If the body is explicitly discussing Codex, Claude Code, or Cursor runtime behavior, projection-specific paths are allowed, but the claim must be framed as projection-specific.

Common findings:

- body says a workflow is owned by `09_codex/skills/<name>/SKILL.md` rather than `[Skill:<name>]`
- a reference-list entry labels a Codex path as the canonical skill without a logical `skill_id`
- a runtime projection path is missing from the ledger, so the concrete file cannot be hard-audited
- a projection-specific claim omits which runtime projection it belongs to

### 5.4.7 Check Auditable YAML Blocks

For admitted Material and Expertise contracts, check whether the document includes a machine-readable YAML block for any reusable object or relation shape it defines.

Reviewer rules:

- A contract defining a durable object or relation should include a fenced `yaml` block with `contract_id` or `schema_kind`.
- A dogfood fixture should include at least one real YAML block with real ids / refs when the fixture is meant to test a contract.
- The block should contain only audit handles and fields that a test, builder, reviewer, or future schema can read.
- The block should not replace prose explanation.
- If the block and prose disagree, the reviewer should flag drift and ask the owner to pick the intended contract.

Common findings:

- `missing_auditable_yaml_block`: a Material / Expertise child contract defines a relation or object shape only in prose
- `contract_block_drift`: prose names a required field but the YAML block omits it
- `yaml_without_reasoning_surface`: YAML fields exist but no prose explains mechanism, cannot-support boundary, or PM-use boundary
- `dogfood_block_not_parseable`: dogfood YAML does not parse or misses required relation fields
- `timestamp_semantic_violation`: auditable YAML block contains `date`, `timestamp`, `valid_until`, `created_at`, or `updated_at` instead of a Timestamp Semantic field name

### 5.5 Check Naming Drift

Search for old vocabulary that would misroute future agents.

Each domain may have its own watchlist. General watchlist:

```text
KnowledgeBase when Information Pool or archive is meant
content.md / content.txt when read_content.md is the downstream surface
evidence_units when agent_evidence.json is meant
source_family when source_collection.family is meant
publish_date / email_date when observed_at_utc / recorded_at_utc is meant
```

Old vocabulary is allowed only when explicitly marked as legacy or historical context.

### 5.6 Emit Review Result

The reviewer writes one of:

```text
accept_as_is
accept_with_capsule_patch
accept_with_notes
needs_author_revision
needs_owner_decision
deprecated_pointer_recommended
```

The review result must name exact file paths and the reason for each unresolved issue.

## 6. Relationship To Existing Self-Review

The portable doc self-review method [Portable-Doc-Self-Review] remains the portable self-review method for proposals and long-form docs.

This contract adds one specialized sub-reviewer:

```text
doc self-review
  -> design-doc-reviewer
```

Use the general self-review for reader-state, structure, and prose quality.
Use `design-doc-reviewer` for system auditability:

- contract capsule
- authority layer
- upstream/downstream handoff
- runtime trigger existence
- bounded metadata / reasoning prose split
- auditable YAML blocks for Material / Expertise contracts
- naming drift
- duplicate canonical owner

Author self-review can improve the doc. It does not replace the design-doc-reviewer when the doc changes a T0/T1 contract.

## 7. Relationship To External Worker Execution

Design-doc review can run in-session or through an external reviewer.

When it runs externally, the runner mechanics must follow the External Worker Execution Contract [T0-External-Worker], the external review builder skill [Skill:support-external-agent-builder], and the prompt builder [Builder-Doc-Review-Prompt].

When it runs through an external surface, it must follow:

```text
designDoc/the_external_agent_management.md
09_codex/skills/support-external-agent-builder/external_review_builder.md
src/tools/build_doc_review_prompt.py
```

The logical design-doc reviewer skill [Skill:support-design-doc-reviewer] owns the review lens. The External Worker Execution Contract [T0-External-Worker] owns the runner surface, prompt assembly, manifest, hashes, and stale-output policy.

For Design Doc external review, the task-specific prompt module [Module-Design-Doc-External-Review] is currently carried by the Codex projection of [Skill:support-design-doc-reviewer]:

```text
09_codex/skills/support-design-doc-reviewer/design_doc_external_review_module.md
```

The external manifest must classify this as:

```yaml
external_agent_class: external_formal_reviewer
review_target_type: design_doc_review
execution_profile: required
```

Execution surfaces such as Claude Code CLI, DeepSeek V4, Anthropic API, Codex CLI, and OpenAI API are recorded in the manifest. They should not be leaked into the worker prompt unless the surface's capabilities change the evidence the worker can inspect.

## 8. Machine Audit Runtime Surfaces

```yaml
runtime_surface_ledger:
  - surface: skill
    projection: codex
    path_or_command: 09_codex/skills/support-design-doc-reviewer/SKILL.md
    owner: designDoc/the_design_doc_management.md
    doc_claim: Codex-side Design Doc sub-reviewer under doc self-review.
    sync_obligation: Update when Contract Capsule fields, reviewer layers, metadata / prose split rules, auditable YAML block rules, body-reference traceability rules, surface ownership drift rules, or external review command shape change.
    status: active
  - surface: prompt_module
    projection: codex
    path_or_command: 09_codex/skills/support-design-doc-reviewer/design_doc_external_review_module.md
    owner: 09_codex/skills/support-design-doc-reviewer/SKILL.md
    doc_claim: External formal-review module for Design Doc contract audit.
    sync_obligation: Update when Design Doc review questions, capsule fields, metadata / prose split rules, auditable YAML block rules, body-reference traceability rules, surface ownership drift rules, runtime ledger rules, or external agent manifest semantics change.
    status: active
  - surface: builder_command
    projection: runtime_agnostic
    path_or_command: ./.venv/bin/python -m src.tools.build_doc_review_prompt --runner-family <runner_family> --review-target-type design_doc_review --execution-profile-id <profile-id> --model-id <model-id> --reasoning-profile <reasoning-profile> --target <target-design-doc-path> --output <prompt-output-path> --extra-reference designDoc/the_design_doc_management.md --extra-reference designDoc/the_external_agent_management.md --include-target-runtime-surfaces --module 09_codex/skills/support-design-doc-reviewer/design_doc_external_review_module.md
    owner: src/tools/build_doc_review_prompt.py
    doc_claim: Assembles an external Design Doc review prompt and manifest.
    sync_obligation: Update this command wherever it appears when builder CLI args or manifest fields change.
    status: active
  - surface: test
    projection: runtime_agnostic
    path_or_command: tests/test_doc_review_prompt_builder.py
    owner: src/tools/build_doc_review_prompt.py
    doc_claim: Verifies runner_family and review_target_type stay manifest metadata and required hashes exist.
    sync_obligation: Update when external review manifest contract changes.
    status: active
verification_hooks:
  - ./.venv/bin/python -m pytest tests/test_doc_review_prompt_builder.py -q
  - ./.venv/bin/python -m src.tools.build_doc_review_prompt --runner-family codex_cli --review-target-type design_doc_review --execution-profile-id codex_cli_gpt_5_5_xhigh --model-id gpt-5.5 --reasoning-profile xhigh --target designDoc/the_design_doc_management.md --output .scratch/design_doc_review_prompt_smoke.md --extra-reference designDoc/the_external_agent_management.md --include-target-runtime-surfaces --module 09_codex/skills/support-design-doc-reviewer/design_doc_external_review_module.md
```

## 9. Application Rule

For new or materially changed active Design Docs:

1. Author writes freely.
2. Draft may remain proposal-shaped without a capsule, ledger, or hooks.
3. Author or operator runs general doc self-review when reader-state or prose quality needs it.
4. `design-doc-reviewer` runs when the draft is being finalized, promoted, materially updated, or propagated.
5. Reviewer adds / normalizes recoverable capsule fields, runtime surface ledger, and verification hooks, or emits findings for unrecoverable fields.
6. Only after review should the position be propagated into skills, routing files, runtime code, schemas, runner commands, or mirror projections.

For legacy docs:

- Do not mass-rewrite all existing docs just to add capsules.
- Add capsules opportunistically when a doc is touched for real work.
- If a legacy doc conflicts with a newer canonical owner, convert it into a pointer rather than maintaining two full bodies.

## 10. References

- `[Portable-Doc-Self-Review]` [Portable Doc Self Review](../09_soul/skills/bestpractice_doc_self_review.md)
- `[T0-External-Worker]` [External Worker Execution Contract](the_external_agent_management.md)
- `[Skill:support-design-doc-reviewer]` logical skill id `support-design-doc-reviewer`; current Codex projection: [Design Doc Reviewer Skill](../09_codex/skills/support-design-doc-reviewer/SKILL.md)
- `[Module-Design-Doc-External-Review]` Codex projection prompt module for `[Skill:support-design-doc-reviewer]`: [Design Doc External Review Module](../09_codex/skills/support-design-doc-reviewer/design_doc_external_review_module.md)
- `[Skill:support-external-agent-builder]` logical skill id `support-external-agent-builder`; current Codex projection: [External Agent Builder Skill](../09_codex/skills/support-external-agent-builder/SKILL.md)
- `[Builder-Doc-Review-Prompt]` [Doc Review Prompt Builder](../src/tools/build_doc_review_prompt.py)
- `[T0-CA]` [Contract Audit Architecture](the_contract_audit.md)

## 11. Bottom Line

The system should stay pleasant to think in and hard to misroute.

Free writing preserves design quality and judgment transfer. Reviewer-enforced capsules preserve audit quality. Bounded metadata gives the system handles; body prose keeps the reasoning alive. The boundary between those jobs is the contract.
