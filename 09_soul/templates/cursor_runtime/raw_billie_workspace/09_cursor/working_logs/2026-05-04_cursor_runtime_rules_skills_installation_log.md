# Cursor Runtime Rules And Skills Installation Log

Date: 2026-05-04
Workspace: `billie_workspace`
Runtime: Cursor
Author: Hoveath

## Why This Log Exists

This working log records the reasoning and implementation behind the Cursor runtime rebuild in `billie_workspace`.

The immediate trigger was a comparison against `trading_platform/.cursor/rules/00_hoveath_always.mdc`. That file made clear that the existing `billie_workspace` Cursor installation was under-specified: the bootstrap rule existed, but it behaved like a short reminder list rather than a runtime contract.

The second trigger was a sharper installation failure: `.cursor/skills/<skill>/SKILL.md` files were pointer wrappers that told the agent to read `09_cursor/skills/...`. That makes the skill system pay a second routing cost every time a skill is invoked, and it leaves too much to the agent's temporary judgment. Cursor project skills should be directly consumable by Cursor. They should contain the actual skill body.

The outcome of this pass is a Cursor-native runtime layer that can be copied as a coherent `.cursor/` folder:

- `.cursor/rules/` contains thin executable trigger rules.
- `.cursor/skills/` contains full physical skill bodies, not pointer wrappers.
- `09_cursor/rules/INDEX.md` records the rule map.
- `09_cursor/routing/task_mainlines.md` maps user requests to truth surfaces, rules, and skills.
- `09_cursor/skills/INDEX.md` records the physical-copy skill contract.

## Initial Diagnosis

The original local setup had the right idea but the wrong density.

Before the rebuild, `.cursor/rules/` had only a small PIM-oriented set:

- `00_pim_always.mdc`
- `10_calendar_auto.mdc`
- `20_areas_auto.mdc`
- `25_eb1_petition.mdc`
- `30_tasks_auto.mdc`
- `40_paper_review_nathan_manual.mdc`
- `90_drift_audit_manual.mdc`

That was enough to protect calendar/task/area edits, but it was not enough to operate as Hoveath in Cursor. It missed the runtime trigger layer:

- when to route by task mainline
- when to retrieve axioms
- when to invoke skills
- when to run reader-state review
- when to verify time-sensitive claims
- when to use parallel subagents
- when to protect AI-facing docs from over-compression
- when to maintain rule/skill indexes
- when to keep `.cursor/skills` as physical copies

The rules were also numbered by historical addition order, not by runtime layer. That made the system harder to read and harder to extend. For example, `25_eb1_petition.mdc` sat between PIM files, even though it is a work-domain overlay. `40_paper_review_nathan_manual.mdc` was a domain persona, not a generic layer-40 rule. The numbering did not teach the agent what kind of rule it was looking at.

## Design Judgment

The main design decision was to split responsibility cleanly:

Rules answer: when does this behavior apply?

Skills answer: how should the agent execute that behavior?

Indexes answer: where does a future agent find the relevant rule or skill?

The old installation blurred these layers. Some rules had too much operational expectation, while skills were under-installed as wrappers. The fix was not to make every rule long. The fix was to make rules dense enough to trigger the right skill and truth surface, while keeping the full method inside skills.

The target shape became:

- `00` is the always-on runtime contract.
- `01-09` are routing and admission rules.
- `10-19` are PIM and area maintenance rules.
- `20-29` are work-domain overlays.
- `30-39` are AI-facing docs, prompt hygiene, reader-state, and prose quality.
- `40-49` are verification, subagent admission, and staged execution.
- `50-59` are Cursor runtime and projection contracts.
- `90-99` are maintenance and index hygiene.

This mirrors the useful part of `trading_platform`: it has enough trigger density that the agent does not need to rediscover the runtime on every task. But it avoids copying trading-specific concepts such as Schwab, KB/AP, PM report contracts, or artifact graph admission into `billie_workspace`.

## Phase 1: Rebuild The Always-On Bootstrap

The old `.cursor/rules/00_pim_always.mdc` was renamed to:

`.cursor/rules/00_hoveath_always.mdc`

The content was rewritten from a short PIM reminder into a Cursor bootstrap contract.

Key changes:

- Identity now says Hoveath is the judgment, writing, review, planning, and memory layer for `billie_workspace`.
- The workspace is explicitly area-first: `04_areas/` is the real work surface; calendar and tasks route attention.
- Startup now reads:
  - `09_cursor/core/SOUL.md`
  - `09_cursor/core/USER.md`
  - `09_cursor/core/COMMUNICATION.md`
  - `09_cursor/core/PROJECT_ADAPTER.md`
  - `09_cursor/rules/INDEX.md`
- The file names itself as the Cursor-native canonical entry point.
- It points to `09_cursor/routing/task_mainlines.md` when the request touches multiple surfaces.
- It adds a rule/skill admission principle: rules decide when to enter; skills define how to execute.

The important change was conceptual: `00_hoveath_always.mdc` should not try to contain every rule. It should teach the agent where the executable runtime map lives.

## Phase 2: Rename Existing Rules By Layer

The original seven rules were renamed into a clearer banded system.

Renames:

- `.cursor/rules/00_pim_always.mdc` -> `.cursor/rules/00_hoveath_always.mdc`
- `.cursor/rules/20_areas_auto.mdc` -> `.cursor/rules/10_pim_areas_auto.mdc`
- `.cursor/rules/10_calendar_auto.mdc` -> `.cursor/rules/11_pim_calendar_auto.mdc`
- `.cursor/rules/30_tasks_auto.mdc` -> `.cursor/rules/12_pim_tasks_auto.mdc`
- `.cursor/rules/25_eb1_petition.mdc` -> `.cursor/rules/20_work_eb1_petition_auto.mdc`
- `.cursor/rules/40_paper_review_nathan_manual.mdc` -> `.cursor/rules/21_work_paper_review_nathan_manual.mdc`
- `.cursor/rules/90_drift_audit_manual.mdc` -> `.cursor/rules/90_maintenance_drift_audit_manual.mdc`

The manual invocation handles were updated too:

- `@40_paper_review_nathan_manual` -> `@21_work_paper_review_nathan_manual`
- `@90_drift_audit_manual` -> `@90_maintenance_drift_audit_manual`

References were updated in:

- `AGENTS.md`
- `SETUP.md`
- `09_cursor/core/USER.md`
- `09_cursor/core/PROJECT_ADAPTER.md`
- `09_cursor/routing/task_mainlines.md`
- `09_cursor/rules/INDEX.md`
- `04_areas/work/paper_review/geCHO/review_with_nathan.md`
- the renamed rule files themselves

After the rename, I searched for old filenames and old invocation handles. No old references remained.

## Phase 3: Convert Cursor Skills From Wrappers To Physical Copies

The original `.cursor/skills/<skill>/SKILL.md` files looked like this pattern:

```markdown
---
name: hoveath-doc-self-review
description: ...
---
# hoveath-doc-self-review

Read `09_cursor/skills/bestpractice_doc_self_review.md` and follow it as the source of truth.
```

That is the wrong installation shape for Cursor.

The corrected shape is:

```markdown
---
name: hoveath-doc-self-review
description: ...
---
# Doc Self-Review（交付前自审 doc）

<full skill body copied from 09_cursor/skills/bestpractice_doc_self_review.md>
```

I preserved the Cursor-required frontmatter in each `.cursor/skills/<skill>/SKILL.md`, then replaced the wrapper body with the full corresponding `09_cursor/skills/*.md` body.

Synchronized skills:

- `hoveath-ai-debugging-diagnosis` <- `09_cursor/skills/bestpractice_ai_debugging_diagnosis.md`
- `hoveath-chinese-writing-voice` <- `09_cursor/skills/bestpractice_chinese_writing_voice.md`
- `hoveath-deep-research-survey` <- `09_cursor/skills/workflow_deep_research_survey.md`
- `hoveath-doc-self-review` <- `09_cursor/skills/bestpractice_doc_self_review.md`
- `hoveath-mirror-sync` <- `09_cursor/skills/bestpractice_mirror_sync.md`
- `hoveath-multi-agent-analysis` <- `09_cursor/skills/bestpractice_multi_agent_analysis.md`
- `hoveath-parallel-subagents` <- `09_cursor/skills/workflow_parallel_subagents.md`
- `hoveath-prompt-boundary` <- `09_cursor/skills/bestpractice_prompt_boundary.md`
- `hoveath-prose-without-editorial-meta` <- `09_cursor/skills/bestpractice_prose_without_editorial_meta.md`
- `hoveath-reader-state` <- `09_cursor/skills/bestpractice_reader_state_and_judgment_gain.md`
- `hoveath-retrospective-writing` <- `09_cursor/skills/bestpractice_retrospective_writing.md`
- `hoveath-skill-writing` <- `09_cursor/skills/bestpractice_skill_writing.md`
- `hoveath-staged-approach` <- `09_cursor/skills/bestpractice_staged_approach.md`
- `hoveath-temporal-verification` <- `09_cursor/skills/bestpractice_temporal_info_verification.md`

I then updated `09_cursor/skills/INDEX.md` to state the contract explicitly:

Cursor project skills in `.cursor/skills/<skill>/SKILL.md` are physical copies, not pointer wrappers. Each file keeps Cursor-required YAML frontmatter, then embeds the corresponding `09_cursor/skills/*.md` body verbatim.

This matters because Cursor skill discovery and execution should be direct. A skill invocation should not depend on a second document lookup unless the skill intentionally uses progressive disclosure.

## Phase 4: Add Missing Runtime Rules

After renaming the existing files, I expanded `.cursor/rules/` from 7 rules to 25 rules.

The new rule set:

```text
00_hoveath_always.mdc

01_core_task_routing.mdc
02_axiom_retrieval_triggers.mdc
03_skill_admission_contract.mdc

10_pim_areas_auto.mdc
11_pim_calendar_auto.mdc
12_pim_tasks_auto.mdc
13_pim_hard_commitment_safety.mdc

20_work_eb1_petition_auto.mdc
21_work_paper_review_nathan_manual.mdc
22_work_due_diligence_research_auto.mdc
23_work_content_artifact_auto.mdc

30_ai_facing_docs_detail_first.mdc
31_prompt_boundary_task_vs_control_plane.mdc
32_reader_state_and_doc_self_review.mdc
33_chinese_writing_voice.mdc
34_prose_without_editorial_meta.mdc

40_temporal_verification_tripwire.mdc
41_parallel_subagent_admission.mdc
42_staged_approach_for_destructive_ops.mdc

50_subagent_model_parity.mdc
51_cursor_skill_physical_copy_contract.mdc
52_mirror_sync_contract.mdc

90_maintenance_drift_audit_manual.mdc
91_rules_skills_index_maintenance.mdc
```

The added rules are intentionally thin. They do not duplicate full skill content.

### `01_core_task_routing.mdc`

Purpose: force routing before acting when a request touches multiple surfaces or when the open file may be misleading.

First authority: `09_cursor/routing/task_mainlines.md`.

Why it exists: the agent otherwise over-weights open files and local phrasing. The workspace is area-first, so task routing needs to happen before edits or strong recommendations.

### `02_axiom_retrieval_triggers.mdc`

Purpose: retrieve axioms when a task needs higher-frame judgment or alignment with Bokan's thinking.

It maps trigger families such as AI management, prompt design, hidden assumptions, reader persona, verification, and prioritization to relevant axiom IDs.

Why it exists: axioms should not sit as passive docs. They are judgment filters and should be retrieved at decision points.

### `03_skill_admission_contract.mdc`

Purpose: teach the agent that rules trigger skills, while skills execute workflows.

It maps common requests to Cursor skill names:

- proposal / design / retrospective -> `hoveath-doc-self-review`
- reader-facing doc -> `hoveath-reader-state`
- Chinese prose -> `hoveath-chinese-writing-voice`
- prompt design -> `hoveath-prompt-boundary`
- current facts -> `hoveath-temporal-verification`
- research -> `hoveath-deep-research-survey`
- parallel investigations -> `hoveath-parallel-subagents`, `hoveath-multi-agent-analysis`
- rules / skills editing -> `hoveath-skill-writing`

Why it exists: without this admission layer, skills exist but are inconsistently invoked.

### `13_pim_hard_commitment_safety.mdc`

Purpose: protect hard commitments across `01_calendar/`, `02_tasks/`, and `04_areas/`.

It states that hard commitments are not moved, deleted, shortened, or reclassified without explicit user instruction.

Why it exists: the previous PIM rules covered file format, but hard commitment safety should be a cross-PIM invariant.

### `22_work_due_diligence_research_auto.mdc`

Purpose: route due diligence and external research under `04_areas/work/`.

It triggers `hoveath-temporal-verification` for current facts and `hoveath-deep-research-survey` for broad multi-source research.

Why it exists: due diligence is a recurring work surface, but it previously had no dedicated rule trigger.

### `23_work_content_artifact_auto.mdc`

Purpose: handle work-area drafting, rewriting, reviewing, auditing, and strategy artifacts.

It forces the agent to identify the reader, desired reader state, fact-controlling materials, and artifact type before editing.

Why it exists: `billie_workspace` is not mainly a coding repo. Much of the value is content judgment.

### `30_ai_facing_docs_detail_first.mdc`

Purpose: protect stable AI-facing docs from being over-compressed.

It requires AI-facing docs to answer:

1. What layer this is.
2. When to enter it.
3. What to read first.
4. What output or behavior it controls.
5. How it hands off to adjacent layers.
6. What nearby concept it must not be confused with.

Why it exists: rule, skill, adapter, and index docs are not just human docs. They are runtime contracts for future agents.

### `31_prompt_boundary_task_vs_control_plane.mdc`

Purpose: keep downstream prompts task-plane only.

It triggers `hoveath-prompt-boundary` and removes orchestration metadata, persona-source labels, package assembly notes, and guardrails already guaranteed by structure.

Why it exists: prompt bloat often comes from leaking caller-internal context into worker instructions.

### `32_reader_state_and_doc_self_review.mdc`

Purpose: require reader-state framing and self-review for substantial handoffs.

It triggers `hoveath-reader-state` and `hoveath-doc-self-review`.

Why it exists: content work fails most often when the document has more text but no clearer reader judgment.

### `33_chinese_writing_voice.mdc`

Purpose: trigger Chinese writing voice checks for Chinese reader-facing prose.

It points to `hoveath-chinese-writing-voice`.

Why it exists: Chinese prose quality is a stable preference and should not depend on the agent remembering the style file manually.

### `34_prose_without_editorial_meta.mdc`

Purpose: remove editorial meta from reader-facing and stable AI-facing prose.

It points to `hoveath-prose-without-editorial-meta`.

Why it exists: stable docs should describe the world or the contract, not the conversation that created them.

### `40_temporal_verification_tripwire.mdc`

Purpose: verify time-sensitive facts before relying on model memory.

It triggers `hoveath-temporal-verification`.

Why it exists: models should not reject new versions, dates, policies, or current facts just because they look newer than training memory.

### `41_parallel_subagent_admission.mdc`

Purpose: use parallel subagents only when justified.

It triggers `hoveath-parallel-subagents` and `hoveath-multi-agent-analysis`.

Why it exists: parallelism is useful for independent investigations with synthesis value. It is wasteful for narrow lookups.

### `42_staged_approach_for_destructive_ops.mdc`

Purpose: require staged execution and dry runs before destructive or bulk operations.

It triggers `hoveath-staged-approach`.

Why it exists: bulk edits, deletes, API writes, and publishing need preview and rollback thinking.

### `50_subagent_model_parity.mdc`

Purpose: prevent silent capability downgrade when delegating.

Why it exists: high-judgment analysis should not be silently moved to a weaker model.

### `51_cursor_skill_physical_copy_contract.mdc`

Purpose: encode the main lesson from this session: Cursor skills are physical copies, not wrappers.

It states that each `.cursor/skills/<skill>/SKILL.md` must contain:

1. Cursor YAML frontmatter.
2. The corresponding `09_cursor/skills/*.md` body embedded directly after frontmatter.

Why it exists: this is the installer bug that should not recur.

### `52_mirror_sync_contract.mdc`

Purpose: keep `09_soul` and `09_cursor` projection discipline.

It triggers `hoveath-mirror-sync`.

Why it exists: portable source and Cursor projection must not drift silently.

### `91_rules_skills_index_maintenance.mdc`

Purpose: require index updates when rules or skills change.

It names the relevant files:

- `09_cursor/rules/INDEX.md`
- `09_cursor/routing/task_mainlines.md`
- `09_cursor/skills/INDEX.md`
- `09_cursor/core/PROJECT_ADAPTER.md`

Why it exists: a rule or skill that is not indexed is only half-installed.

## Phase 5: Update Indexes And Routing

### `09_cursor/rules/INDEX.md`

I rewrote the index around numbering bands.

It now records:

- `00`: bootstrap
- `01-09`: task routing, axiom retrieval, skill admission
- `10-19`: PIM and area maintenance
- `20-29`: work-domain overlays
- `30-39`: AI-facing docs, prompt hygiene, reader-state, prose quality
- `40-49`: verification, subagent admission, staged execution
- `50-59`: Cursor runtime maintenance and projection contracts
- `90-99`: maintenance, drift audit, cleanup

It also lists all 25 rules with loading mode and role.

### `09_cursor/routing/task_mainlines.md`

I updated task routing to point to the new rule names and Cursor skill names.

Examples:

- EB1-B -> `.cursor/rules/20_work_eb1_petition_auto.mdc` -> `hoveath-doc-self-review`, `hoveath-prose-without-editorial-meta`
- paper review -> `.cursor/rules/21_work_paper_review_nathan_manual.mdc` -> `hoveath-reader-state`
- due diligence -> `.cursor/rules/22_work_due_diligence_research_auto.mdc` -> `hoveath-deep-research-survey`, `hoveath-temporal-verification`
- Chinese writing -> `.cursor/rules/33_chinese_writing_voice.mdc` -> `hoveath-chinese-writing-voice`
- runtime maintenance -> `.cursor/rules/91_rules_skills_index_maintenance.mdc` -> `hoveath-skill-writing`, `hoveath-mirror-sync`

This matters because the routing table should name the Cursor-invokable skill IDs, not the old source filenames like `bestpractice_doc_self_review`.

### `09_cursor/core/PROJECT_ADAPTER.md`

I changed the local rule description from a file-by-file list to a banded explanation.

That keeps the adapter stable as rule count grows.

### `SETUP.md`

I updated the setup doc to stop listing the old seven rules. It now points to bands and says the full map lives in `09_cursor/rules/INDEX.md`.

## Phase 6: Verification

I checked four things after the rebuild.

First, old rule names and old manual handles:

- no `00_pim_always`
- no `10_calendar_auto`
- no `20_areas_auto`
- no `25_eb1_petition`
- no `30_tasks_auto`
- no `40_paper_review_nathan_manual`
- no `90_drift_audit_manual`
- no old `@40_...` or `@90_...` handles

Second, `.cursor/skills` wrappers:

- no `Read \`09_cursor/skills`
- no `If that file references`
- no pointer wrapper text remained

Third, `ReadLints`:

- no linter errors on `.cursor/rules`
- no linter errors on `.cursor/skills`
- no linter errors on the updated indexes and adapters

Fourth, git status:

- Git shows renamed rules as deleted old files plus untracked new files until staged.
- The workspace already had unrelated dirty files, including `.DS_Store`, EB1-B drafts, paper review files, and other work-area materials. I did not revert or normalize those.

## What The Mother Installer Got Wrong

The mother-side installation logic appears to have at least five problems.

### 1. It installed Cursor skills as wrappers

The installer created `.cursor/skills/<skill>/SKILL.md` as a pointer to `09_cursor/skills/*.md`.

That is wrong for Cursor.

Correct logic:

- Keep `09_cursor/skills/*.md` as source/projection material.
- Generate `.cursor/skills/<skill>/SKILL.md` as:
  - Cursor YAML frontmatter
  - full source body embedded directly

Cursor's skill layer should be directly consumable. A project skill should not require the agent to discover and read a second file just to get the actual instructions.

### 2. It under-installed rules

The installer installed local PIM rules, but not the runtime trigger layer.

A Cursor Hoveath installation needs rules for:

- task routing
- axiom retrieval
- skill admission
- AI-facing doc contracts
- prompt boundary hygiene
- reader-state and doc self-review
- Chinese writing voice
- editorial meta removal
- temporal verification
- parallel subagent admission
- staged execution for risky operations
- subagent model parity
- skill physical-copy contract
- mirror sync contract
- rules/skills index maintenance

Without these, the runtime relies too heavily on the agent's general memory.

### 3. It treated numbering as incidental

The old numbers were historical, not semantic.

Correct logic:

- numbering should explain runtime layer
- nearby numbers should mean nearby responsibilities
- domain overlays should not be mixed into PIM bands
- maintenance contracts should live in their own band

This matters because agents use filenames as routing hints.

### 4. It did not make indexes authoritative enough

The previous installation had indexes, but the runtime did not depend on them strongly enough.

Correct logic:

- `00_hoveath_always.mdc` should tell the agent to read `09_cursor/rules/INDEX.md`.
- `09_cursor/rules/INDEX.md` should list every executable Cursor rule.
- `09_cursor/routing/task_mainlines.md` should map signals to first authority, truth surface, and skill.
- `09_cursor/skills/INDEX.md` should document source skill status and Cursor physical-copy behavior.

Indexes are not decoration. They are the runtime map.

### 5. It did not encode installation lessons back into rules

The installer bug about skills would recur unless the corrected behavior becomes a rule.

That is why `51_cursor_skill_physical_copy_contract.mdc` now exists.

The installation logic should not depend on a human remembering this session. It should be executable as a rule.

## Copyable Installation Logic

If the mother installer is rewritten, the Cursor projection install should roughly do this.

### Step 1: Install `.cursor/rules/`

Copy the full rule set into `.cursor/rules/`.

Required files:

```text
00_hoveath_always.mdc
01_core_task_routing.mdc
02_axiom_retrieval_triggers.mdc
03_skill_admission_contract.mdc
10_pim_areas_auto.mdc
11_pim_calendar_auto.mdc
12_pim_tasks_auto.mdc
13_pim_hard_commitment_safety.mdc
20_work_eb1_petition_auto.mdc
21_work_paper_review_nathan_manual.mdc
22_work_due_diligence_research_auto.mdc
23_work_content_artifact_auto.mdc
30_ai_facing_docs_detail_first.mdc
31_prompt_boundary_task_vs_control_plane.mdc
32_reader_state_and_doc_self_review.mdc
33_chinese_writing_voice.mdc
34_prose_without_editorial_meta.mdc
40_temporal_verification_tripwire.mdc
41_parallel_subagent_admission.mdc
42_staged_approach_for_destructive_ops.mdc
50_subagent_model_parity.mdc
51_cursor_skill_physical_copy_contract.mdc
52_mirror_sync_contract.mdc
90_maintenance_drift_audit_manual.mdc
91_rules_skills_index_maintenance.mdc
```

Project-specific overlays can be added or removed, but the runtime bands should remain stable.

### Step 2: Install `09_cursor/`

Install:

- `09_cursor/core/SOUL.md`
- `09_cursor/core/USER.md`
- `09_cursor/core/COMMUNICATION.md`
- `09_cursor/core/PROJECT_ADAPTER.md`
- `09_cursor/rules/INDEX.md`
- `09_cursor/routing/task_mainlines.md`
- `09_cursor/skills/INDEX.md`
- relevant `09_cursor/skills/*.md`
- relevant `09_cursor/axioms/*.md`

The Cursor bootstrap should read `09_cursor` files, not Claude projection files.

### Step 3: Generate `.cursor/skills/` From `09_cursor/skills/`

For each Cursor skill:

1. Create `.cursor/skills/<skill-name>/SKILL.md`.
2. Write Cursor frontmatter:

```yaml
---
name: <skill-name>
description: <specific discovery description>
---
```

3. Append the full source body from `09_cursor/skills/<source>.md`.

Do not write a wrapper body.

Bad:

```markdown
Read `09_cursor/skills/bestpractice_doc_self_review.md` and follow it.
```

Good:

```markdown
# Doc Self-Review（交付前自审 doc）

<full source body>
```

### Step 4: Update Indexes

The installer should generate or validate:

- `09_cursor/rules/INDEX.md`
- `09_cursor/routing/task_mainlines.md`
- `09_cursor/skills/INDEX.md`
- project adapter local rule summary

Every installed rule should appear in the rules index.

Every installed Cursor skill should have either:

- a source entry in `09_cursor/skills/INDEX.md`
- or a clear reason it is project-only

### Step 5: Validate

The installer should run checks equivalent to:

- no stale old rule filenames
- no `.cursor/skills` wrapper text
- no missing rule files referenced by indexes
- no missing skill source files referenced by generated Cursor skills
- no unindexed `.cursor/rules/*.mdc`
- no unindexed `.cursor/skills/*/SKILL.md`

For this workspace, I manually validated these conditions using file search and lints.

## Why Copying The Whole `.cursor/` Folder May Be Reasonable

Copying the whole `.cursor/` folder from this workspace is reasonable if the target workspace wants the same Cursor-native Hoveath runtime shape.

The copy works because `.cursor/` now contains:

- a proper always-on bootstrap
- executable trigger rules
- physically installed skills
- local PIM and work overlays
- maintenance rules that preserve the system

But it is not enough by itself.

The target workspace also needs the matching `09_cursor/` projection, because the bootstrap and rules reference:

- `09_cursor/core/SOUL.md`
- `09_cursor/core/USER.md`
- `09_cursor/core/COMMUNICATION.md`
- `09_cursor/core/PROJECT_ADAPTER.md`
- `09_cursor/rules/INDEX.md`
- `09_cursor/routing/task_mainlines.md`
- `09_cursor/skills/INDEX.md`
- `09_cursor/axioms/INDEX.md`

So the copyable unit is not only `.cursor/`. The copyable Cursor runtime unit is:

```text
.cursor/rules/
.cursor/skills/
09_cursor/core/
09_cursor/rules/
09_cursor/routing/
09_cursor/skills/
09_cursor/axioms/
AGENTS.md as pointer
```

If the target repo has different domains, replace only the local overlays:

- `20-29` work-domain rules
- `10-19` PIM rules if the workspace is not area-first
- `09_cursor/core/PROJECT_ADAPTER.md`
- `09_cursor/routing/task_mainlines.md`

Keep the runtime layers:

- `00`
- `01-03`
- `30-34`
- `40-42`
- `50-52`
- `91`

Those are portable enough to dogfood further.

## Current State After This Pass

The runtime is now materially stronger than the original install.

What changed:

- Bootstrap is now a real Cursor contract.
- Rule numbering expresses runtime layers.
- Rules expanded from 7 to 25.
- Skills are physical copies rather than wrappers.
- Indexes and routing now point to new rule and skill IDs.
- The main installer failure is encoded as a rule: `51_cursor_skill_physical_copy_contract.mdc`.
- Future rule/skill changes must update indexes via `91_rules_skills_index_maintenance.mdc`.

What remains worth improving later:

- Add a deterministic sync script for `.cursor/skills` generation from `09_cursor/skills`.
- Add a validation script that checks rule/skill index completeness.
- Decide whether `09_cursor/working_logs/` should get an `INDEX.md` if logs become a repeated artifact.
- Consider promoting stable portable runtime rules into `09_soul/` after dogfooding in at least one more workspace.

## Bottom Line

The core installation lesson is:

Cursor runtime material should be executable at the layer Cursor reads it.

That means:

- always-on behavior belongs in `.cursor/rules/00_hoveath_always.mdc`
- trigger behavior belongs in thin `.cursor/rules/*.mdc`
- full skill behavior belongs directly in `.cursor/skills/<skill>/SKILL.md`
- source/projection material lives in `09_cursor/`
- indexes are runtime maps, not documentation afterthoughts

The original mother-side installation treated `.cursor/skills` as pointers and `.cursor/rules` as a small local safety set. This pass turns them into a coherent Cursor-native Hoveath runtime.
