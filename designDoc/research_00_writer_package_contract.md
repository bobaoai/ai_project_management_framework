# Writer Package Contract

**Version 0.2 — 2026-04-19**

## Scope And Inheritance

This document is the canonical contract for **any** writer-facing
package artifact in this repo. The same tier shape, fail-fast rules,
and size budgets apply across:

- `theme.package` (theme report) — current first concrete instance,
  used throughout this doc as the worked example
- `current-market.package` (market observation)
- `single_stock.package` (single-stock analysis)
- `asset_technical_report` package (per-asset)
- weekly account review package
- portfolio debate / decision package

When a future task line introduces its own package node, it should adopt
this contract first and only diverge with explicit justification.

It supersedes §7.1 `Writer Package Boundary` of
[`research_10_thematic_workflow.md`](research_10_thematic_workflow.md).
The original section now points here.

For the family-level position of this doc, see
[`research_00_overview.md`](research_00_overview.md).

## Why A Revised Contract Now

The existing §7.1 rule `full text in` (long sources keep full cleaned
text inside the package) was the structural root of a hard failure on
2026-04-19 with `iran-hormuz-escalation.package.md`:

- total size: 1,264,493 chars (~382K tokens)
- 7 raw `## File Contents` sections (~907K chars total) — each one a full
  embedded source file
- 40 `### Page N` PDF page-by-page dumps with the Citrini lockup banner
  repeated 40 times
- the standing report appeared **twice** (once as
  `## Backbone Finalized Theme Report Markdown`, once again as the
  `## File Contents` of the `## Group: Backbone` section)
- `owner.json` never reached the writer; the `## Writer Notes` section
  contained two template lines and `## Package Instructions` literally
  read `No explicit package instructions.`

The package failed both writer paths simultaneously:

- DeepSeek API: HTTP 400 (input exceeded 64K context)
- Cursor CLI: `OSError E2BIG` (1.3MB argv exceeds macOS argv limit)

Both failures are physical limits of writer surfaces. They are not
transient. Any theme with multi-PDF research will reproduce this under
the old contract.

The deeper failure was that the gate was passing structural duds:
because owner direction was never present in the package, the
`writer-handoff` gate could only check evidence presence, not whether
the writer would actually be steered against `owner_decision.scope`.

## Reader / Writer End-State

A compliant package must let the writer:

- read `scope` and the full `writer_direction[]` from `owner.json`
  before any evidence
- distinguish `primary` evidence from `boundary_reference` and
  `still_relevant_backbone` evidence
- consume thesis-level structured judgment (already-extracted
  `claim_bullets`, `key_numbers`, `supporting_evidence_ids`) before
  consuming bounded source excerpts
- see the standing report exactly once, clearly labelled as the
  framework backbone
- resolve `primary_visual_evidence[]` by `research_id + image_id +
  page + purpose` references, with per-image descriptive text already
  carried by `image_reviews.jsonl`, instead of receiving raw PDF page
  text

A compliant package must let `writer-handoff` answer these checks
mechanically:

- is `## Owner Writer Direction` present and non-empty
- does every `selected_thesis_note_id` resolve to an in-package thesis
  block
- does every `core_recent_research_id` resolve to a per-source card
  with a real `content_selection`-driven excerpt (not a
  head-N fallback, not a full file dump)
- is the `## Do Not Promote` list present whenever
  `do_not_promote_without_cleanup[]` is non-empty in `owner.json`
- is there exactly one backbone copy

If any of those checks cannot be answered without re-reading the
underlying archive, the package is malformed.

## Tiered Structure

A compliant theme package body is laid out in this fixed order. Each
tier has a target size budget. The package builder must emit the
tier headers even when a tier is empty (so reviewers see the absence).

| # | Section | Source | Target size | Hard rule |
| - | --- | --- | --- | --- |
| 1 | `## Owner Writer Direction` | `theme_update_drafts/<theme_id>.owner.json` → `scope` (verbatim) + `writer_direction[]` (verbatim, all items, numbered) | < 5 KB | required when `owner.json` exists; missing owner ⇒ fail-fast |
| 2 | `## Do Not Promote` | `owner.json.selected_materials.do_not_promote_without_cleanup[]` + per-id reason from owner | < 2 KB | required iff list non-empty |
| 3 | `## Boundary References` | `owner.json.selected_materials.boundary_reference_research_ids[]` → per source: source card + `content_selection`-driven excerpt capped at ~50 lines, explicitly tagged `boundary, do not build article around this` | < 10 KB | one card per ID; full file dump forbidden |
| 4 | `## Standing Backbone` | latest `themes/reports/<theme_id>.md` only | ~30 KB | exactly once across the entire package |
| 5 | `## Theses (selected)` | each `owner.json.selected_materials.selected_thesis_note_ids[]` → one thesis block: `id`, `claim_bullets`, `key_numbers`, `supporting_evidence_ids`, and which `writer_direction[]` item this thesis serves | 5–10 KB / thesis | every selected thesis must appear; missing thesis_note file ⇒ fail-fast |
| 6 | `## Primary Source Cards` | each `owner.json.selected_materials.core_recent_research_ids[]` → source card + `content_selection`-driven excerpt | 10–20 KB / source | excerpt MUST come from `content_selection.json`; missing file ⇒ fail-fast |
| 7 | `## Primary Visual Evidence (by reference)` | `owner.json.selected_materials.primary_visual_evidence[]` → per image: `research_id`, `image_id`, `page`, `purpose` (one line) + the corresponding row from `image_reviews.jsonl` (description text only) | < 5 KB | image binary / base64 forbidden |
| 8 | `## Still Relevant Backbone Research (compact)` | `owner.json.selected_materials.still_relevant_backbone_research_ids[]` → per source: source card + 1-line "why still relevant" | < 10 KB | full file dump forbidden |
| — | `## Manifest Pointer` | one line referencing the assembly sidecar `<theme_id>.package.manifest.json` | <0.5 KB | manifest body lives in sidecar, not in package |

Total target: **< 300 KB** for a heavy theme; typical themes should land
**< 150 KB**. A package > 500 KB is a hard signal that this contract
has been violated.

The full plumbing layer (ephemeral context index, theme metadata
snapshot, theme index snapshot, priority tree snapshot, draft record
metadata, assembly manifest, group notes) belongs to the manifest
sidecar `<theme_id>.package.manifest.json`. It must not be inlined
into the package markdown body. The writer never needs that plumbing
to write the article.

## Hard Rules

These are non-negotiable. A package violating any of them is invalid
and `writer-handoff` should return `need_more_detail` referencing the
violated rule by name.

- `R1 Owner direction is first`: the package body's first section after
  any frontmatter must be `## Owner Writer Direction` rendered from
  `owner.json`.
- `R2 No silent owner skip`: if `<theme_id>.owner.json` does not exist
  for the report date, the builder fails fast. The builder does not
  proceed without owner direction.
- `R3 Thesis-first compression`: detail that the writer needs in order
  to follow `writer_direction[]` items must come from
  `thesis_notes/<id>.json`, not from raw source dumps. Thesis blocks
  are emitted before primary source cards.
- `R4 Excerpt comes from content_selection.json`: every selected source
  excerpt must be assembled from
  `messages/<research_id>/content_selection.json`. There is no head-N
  fallback. If `content_selection.json` is missing for a selected
  source, the builder fails with
  `error: content_selection_missing for <research_id>; run tradectl
  message refresh --research-id <research_id>`.
- `R5 No PDF page dumps`: PDF sources must not be inlined as
  `### Page 1 ... ### Page N`. Page-level evidence belongs to
  `image_reviews.jsonl`; quotable text passes through
  `content_selection.json`. The builder must not paste `content.md` of
  a multi-page PDF into the package.
- `R6 Backbone exactly once`: the standing report
  `themes/reports/<theme_id>.md` appears in `## Standing Backbone` and
  nowhere else.
- `R7 Plumbing in sidecar`: ephemeral context indexes, manifests,
  theme metadata snapshots, priority tree snapshots, draft record
  metadata, and assembly notes belong to the
  `<theme_id>.package.manifest.json` sidecar, not the package body.
- `R8 No do-not-promote leak`: if
  `owner.json.selected_materials.do_not_promote_without_cleanup[]` is
  non-empty, none of those IDs may appear in `## Theses (selected)`,
  `## Primary Source Cards`, or `## Boundary References`. They must
  appear only in `## Do Not Promote`, with the owner's stated reason.
- `R9 Identifiers stable`: every block referenced from owner.json
  carries its canonical ID and a repo-relative path so the writer can
  cite it; the builder must not invent new IDs.
- `R10 Multimodal by reference`: image evidence is referenced by
  `research_id + image_id + page` plus the descriptive text already
  produced by image review. Raw image bytes never enter the package.
- `R11 Size budget enforced`: if the assembled body exceeds 500 KB,
  the builder fails with `error: package_size_budget_exceeded
  (<actual> bytes, limit 512000)`. The fix is to tighten
  `content_selection.json` upstream, not to silently truncate.

## Owner Direction Integration

This is the contract gap that turned the writer-handoff gate
ceremonial. Make it explicit:

- builder reads `theme_update_drafts/<theme_id>.owner.json`
- emits `## Owner Writer Direction` with:
  - `Scope:` `<owner.scope verbatim>`
  - `Writer direction:` numbered list of `owner.writer_direction[]`,
    items rendered verbatim (no rewriting, no compression)
- emits `## Do Not Promote` from
  `owner.selected_materials.do_not_promote_without_cleanup[]`
- emits `## Boundary References` from
  `owner.selected_materials.boundary_reference_research_ids[]`
- threads `selected_thesis_note_ids` and `core_recent_research_ids`
  into tiers 5 and 6 in the order owner gave them

`owner.json` becomes the package's first-class control surface. The
writer reads it as part of the package body. `writer-handoff` checks
that what was decided in owner shows up in the package.

When this is in place, the `research-theme-report-reviewer` (post-writing gate)
can score `mainline_alignment` and `evidence_alignment` mechanically
by diffing the writer's output against
`## Owner Writer Direction` + `## Theses (selected)`.

## Per-Source Excerpt Contract

For each `core_recent_research_id` and each
`boundary_reference_research_id`:

- the builder reads `messages/<research_id>/content_selection.json`
- emits a Source Card:
  - `research_id`
  - title, source_collection, author / publisher, dated original URL if
    canonical
  - one-line `purpose` derived from owner direction
- emits `Selected Excerpt:` from `content_selection.json`'s chosen
  passages, preserving original ordering
- emits `Numbers and Quotes Of Record:` from
  `content_selection.json`'s `key_numbers` and `key_quotes` fields if
  present
- never emits `## File Contents` of `content.md`
- never emits `### Page N` blocks

When a source is short enough that the entire content is the
selection, `content_selection.json` should record
`use_whole_content: true` and the excerpt is the whole `content_main.txt`
(short cleaned text). The builder still routes through
`content_selection.json`; it does not bypass.

If `content_selection.json` does not exist for a selected source, the
builder fails fast (R4). The fix is upstream
(`message refresh`), not downstream. If the package also needs
AI-derived evidence from `agent_evidence.json`, run
`message derive-agent-evidence` after `read_content.md` is current.

## PDF / Multimodal Source Rule

For PDF / multimodal sources:

- `content_selection.json` carries the human/AI-selected paragraph-level
  text passages
- `image_reviews.jsonl` carries per-image descriptive text + key
  numbers extracted from charts / tables
- `agent_evidence.json` may carry already-decomposed atomic claims in
  `evidence_units`
- `document_read` inside `agent_evidence.json` is a thin first-pass
  record, not a writer surface

The package consumes all of the above through tier 6 (Primary Source
Cards) and tier 7 (Primary Visual Evidence). It does not paste raw
`content.md` page-by-page.

When a PDF has dozens of pages and only specific pages matter, the
owner is expected to call them out via
`primary_visual_evidence[].page`. The builder mirrors that selection
and appends `image_reviews.jsonl` row text for the named pages.

The Citrini PDF case in the failed Hormuz package is the canonical
counter-example: 40 page dumps that the writer never needed because the
toll-booth, polyethylene, and post-fracking-elasticity claims had
already been distilled into thesis_notes.

## Backbone Rule

Backbone is the standing finalized theme report.

- only `themes/reports/<theme_id>.md` qualifies
- `theme_update_drafts/<theme_id>.ds.md` cannot be a same-theme
  backbone (it is the candidate to be reviewed and merged, not a
  parallel framework)
- `lifecycle_stage = draft_candidate` reports cannot serve as backbone
- backbone appears in `## Standing Backbone` exactly once; no second
  copy under any other heading

## Detection-Side (What Counts As A Violation)

Treat any of these as a contract violation:

- package body contains `## File Contents` of any source file
- package body contains `### Page N` blocks for N > 1
- the same backbone text appears under more than one heading
- `## Owner Writer Direction` is missing while `<theme_id>.owner.json`
  exists for the report date
- a `selected_thesis_note_id` from owner has no thesis block in the
  package
- a `core_recent_research_id` from owner has a card whose excerpt was
  not assembled from `content_selection.json` (e.g. head-200, full file,
  or empty)
- an ID listed in `do_not_promote_without_cleanup[]` appears as
  evidence anywhere outside `## Do Not Promote`
- the assembled body is > 500 KB
- the package emits raw image bytes or base64
- ephemeral context index, theme index snapshot, priority tree
  snapshot, or assembly manifest is inlined in the package body

The writer-handoff gate should call these out by rule ID (R1–R11) so
the upstream owner / content maintainer can act without having to
re-derive what's wrong.

## Implementation State

The 2026-04-19 failure surfaced the original gaps. The contract-driven
builder now lives at `src/tools/build_theme_writer_package.py` and
satisfies R1–R11. The previous keyword-based builder is preserved as
`src/tools/build_theme_writer_package_v1_legacy.py` for archaeology
only — it is no longer wired into `tradectl`. The `tests/test_theme_lifecycle.py`
suite still exercises the legacy module while a contract-driven test
rewrite is on the backlog.

Status:

1. ✅ Contract doc landed.
2. ✅ `research-theme-knowledge-and-package-curator/SKILL.md` and `writer-handoff/SKILL.md`
   cross-reference this contract by rule ID instead of restating it.
3. ✅ Canonical builder satisfies R1–R11 and emits the 8-tier structure;
   v1 keyword builder retired to `_v1_legacy`.
4. ✅ Validated end-to-end on `iran-hormuz-escalation`:
   `report_date = 2026-04-19` (first DS pass) and a follow-up
   `report_date = 2026-04-20` rebuild after the owner-side coverage
   gap was fixed. Body sizes ~110–145 KB, well inside the 500 KB
   ceiling.
5. ✅ Owner / metadata gaps for `iran-hormuz-escalation` were closed
   (missing April research linkage, noisy `iran-update_*` theses
   demoted, `ai_capex_is_the_real_melt_up_engine_via_real_rate_easing`
   thesis added).
6. ✅ `writer-handoff` gate ran cleanly on the fresh package and the
   reviewer reached `accept_as_is` after one revision pass.
7. ✅ `draft-theme-report-ds` runs under DeepSeek context limits with
   the new package shape.
8. ✅ `research-theme-report-reviewer` verdict structure works against a fresh
   DS draft (Hormuz round 3 audit).

Open follow-ups (tracked in `research-theme-report-owner/SKILL.md` and
`artifact_graph.yaml`):

- Apply the same tiered shape to `current-market.package`,
  `single_stock.package`, and remaining task-line packages.
- Rewrite `tests/test_theme_lifecycle.py` against the canonical
  contract-driven builder so the legacy module can be deleted.
- v0.2 of `artifact_graph.yaml` formalizes a `must_not_contradict`
  edge from `current-market.ds` to `theme.report.ds` (open issue #6),
  replacing the current `optional_overlay + note` placeholder.

## Cross References

- family overview: [`research_00_overview.md`](research_00_overview.md)
- post-writing reviewer pattern that consumes the same package:
  [`research_00_report_reviewer_pattern.md`](research_00_report_reviewer_pattern.md)
- artifact graph nodes: `theme.package`, `current-market.package`,
  `single_stock.package`, `theme.report.review` — see
  [`the_artifact_graph.md`](the_artifact_graph.md)
- adjacent skills (current first instance):
  [`.cursor/skills/research-theme-report-owner/SKILL.md`](../.cursor/skills/research-theme-report-owner/SKILL.md),
  [`.cursor/skills/research-theme-knowledge-and-package-curator/SKILL.md`](../.cursor/skills/research-theme-knowledge-and-package-curator/SKILL.md),
  [`.cursor/skills/writer-handoff/SKILL.md`](../.cursor/skills/writer-handoff/SKILL.md),
  [`.cursor/skills/research-theme-report-reviewer/SKILL.md`](../.cursor/skills/research-theme-report-reviewer/SKILL.md)
- ingestion contract that guarantees `content_selection.json` exists:
  [`research_10_thematic_workflow.md`](research_10_thematic_workflow.md) §9
- ID-first / no-heuristic-middle-layer rule:
  [`09_soul/axioms/t10_index_first_ai_for_gaps.md`](../09_soul/axioms/t10_index_first_ai_for_gaps.md)
  and host-local
  [`.cursor/rules/13_index_first_ai_for_gaps.mdc`](../.cursor/rules/13_index_first_ai_for_gaps.mdc)
- supersedes:
  [`research_10_thematic_workflow.md`](research_10_thematic_workflow.md) §7.1
