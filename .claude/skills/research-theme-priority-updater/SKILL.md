---
name: research-theme-priority-updater
description: "Updates macro theme priority, routing metadata, and the generated priority views from local theme metadata. Use when reprioritizing themes, refreshing the current macro stack, updating priority_bucket or priority_rank, regenerating the current priority tree, or doing a local-only routing pass."
---

# Theme Priority Updater

## What This Skill Does

Use this skill to update theme ranking and routing state without rewriting the underlying thesis content.

This skill is for:

- `priority_bucket`
- `priority_rank`
- `status`
- routing relevance
- generated tree refresh

This skill is not for writing new thesis content or importing outside evidence.

## Desired Result

The desired result is that local theme priority state becomes explicit, internally consistent, and regenerated correctly from canonical metadata.

By the time this skill is done, it should be explicit:

- which themes were re-ranked or left unchanged
- which routing-facing metadata fields changed
- why the priority state changed
- whether generated views were rebuilt successfully

If the ranking judgment changes but the source metadata and generated views do not line up, this skill has failed.

## Completion Standard

This skill is complete only when all of the following are explicit:

- target theme scope
- the ranking judgment
- the metadata fields changed or intentionally left unchanged
- regenerated `themes/index.json`
- regenerated `themes/current_priority_tree.json`
- a short explanation of why the routing priority changed

Accepted outcomes:

- reprioritized metadata plus regenerated views
- explicit `no_change` result when review does not justify rank edits

Do not treat manual metadata edits without regeneration as complete.

## Source-Of-Truth Rule

- Work local-only.
- Treat `themes/metadata/<theme_id>.json` as the editable source of truth.
- Treat `themes/index.json` as a generated directory view.
- Treat `themes/current_priority_tree.json` as a generated ranking view.
- Rebuild generated views after metadata edits.
- Do not hand-edit generated files.

## Canonical Inputs

Read these first:

- `data/research/themes/index.json`
- `data/research/themes/current_priority_tree.json`
- `data/research/themes/metadata/<theme_id>.json`
- `data/research/themes/reports/<theme_id>.md`
- `data/research/thesis_index.jsonl`
- `data/research/messages_index.jsonl`

## What This Skill May Change

Allowed metadata edits:

- `status`
- `priority_bucket`
- `priority_rank`
- `preferred_skill`
- routing-facing `summary`
- routing-facing `why_now`

Usually leave these to `research-theme-report-owner` / `research-theme-knowledge-and-package-curator`:

- thesis logic
- report body
- linked evidence interpretation
- `open_questions`
- `subthemes` content

## Cross-Theme Thesis Link Role (v1.5 surface)

Starting from `thesis_note v1.5` (see [`research_06`](../../../designDoc/research_40_thesis_note_schema_v1_5.md)), each thesis carries `cross_theme_links[]` with explicit `role`:

- `primary` — thesis is one of the central pillars of the linked theme
- `secondary` — thesis supports but is not central to the linked theme
- `boundary_reference` — thesis is NOT in the linked theme's scope, but the linked theme's report should still mention "this matter belongs next door at theme X"

When this skill ranks priorities, treat the role information as a routing signal:

- A theme that gains a NEW `primary`-role thesis since the last priority pass usually deserves a re-rank consideration (the theme just added a load-bearing claim)
- A theme that lost a `primary`-role thesis (e.g., thesis lifecycle moved to `retired`) usually deserves a re-rank consideration in the OTHER direction
- `boundary_reference` links do NOT change the linked theme's rank by themselves — they only indicate that the linked theme's report needs a "see also next door" mention; that is a content task for `research-theme-knowledge-and-package-curator`, not a priority task here
- Prefer reading `thesis_index.jsonl` for the up-to-date list of theses + their `cross_theme_links` rather than re-scanning every `thesis_notes/*.json` file

This skill DOES NOT:

- write or modify `thesis_notes/*.json` (that is `research-thesis-drafter` / `research-thesis-verifier` / `research-thesis-adversary`)
- create cross-theme links (that is the drafter's responsibility, sometimes guided by `research-theme-bootstrapper`)
- rebuild `thesis_index.jsonl` (that is a deterministic indexer build step)

## Ranking Inputs

Use repo-local evidence only:

- recent linked research
- recent linked theses
- cross-asset relevance
- whole-book routing importance
- time sensitivity

Prefer raising themes that currently drive portfolio-defense or routing decisions.
Prefer lowering themes that are educational, regional, stale, or narrow.

## Required Outputs

At minimum, the result should say:

- `theme_reviewed`
- `old_bucket` and `new_bucket`
- `old_rank` and `new_rank`
- whether `preferred_skill` changed
- why the routing priority changed
- whether generated views were rebuilt successfully

## Canonical Regeneration Step

When metadata changes, rebuild the generated views through:

```bash
python src/tools/build_theme_indexes.py
```

## Guardrails

- Do not fetch external materials.
- Do not hand-edit `index.json`.
- Do not hand-edit `current_priority_tree.json`.
- Do not create or rewrite thesis notes in this workflow.
- Do not create a dedicated skill unless the dedicated-skill rule is satisfied.

## Example Triggers

- “refresh theme priorities”
- “更新 current priority tree”
- “按现在重要程度重新排一下”
- “update priority_bucket and priority_rank”
- “local-only rerank the current themes”
