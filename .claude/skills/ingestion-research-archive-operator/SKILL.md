---
name: ingestion-research-archive-operator
description: "Operates the repo's research and knowledge archive workflows. Use when refreshing research sources, checking archive status, inspecting local research artifacts, or turning newly fetched materials into reusable local knowledge."
---

# Research Archive Operator

## What This Skill Does

Use this skill when the task belongs to archive refresh, archive inspection, or archive-first promotion of local research materials.

This skill is for:

- refreshing source-connected research into the local archive
- checking what is already stored, missing, stale, or blocked
- turning archived materials into durable local knowledge objects
- confirming which external-facing archive surface downstream tasks should consume

This skill is not the primary workflow for:

- top-level portfolio or PM interpretation
- connector design itself
- freehand summarization that bypasses archive truth surfaces

## Desired Result

The desired result is that the archive becomes more usable and more trustworthy for downstream work.

By the time this skill is done, it should be explicit:

- what archive scope was checked or refreshed
- what changed
- what durable objects were created, updated, or left unchanged
- what the best downstream-facing archive surface is
- what still requires human review or later follow-up

If the work only produces chat commentary without improving archive state or archive clarity, this skill has failed.

## Completion Standard

This skill is complete only when all of the following are explicit:

- target archive scope
- current archive status or refresh result
- affected local artifacts or object paths
- whether durable knowledge objects were created, updated, or intentionally left untouched
- any unresolved blockers, missing inputs, or review-needed items
- the recommended next archive-facing action when the task cannot fully complete

Accepted outcomes:

- refreshed local archive state
- inspected archive status with explicit findings
- promoted durable knowledge objects such as `snapshot`, `theme_update_draft`, or related archive-side records
- explicit `needs_review` / `blocked` output when archive work cannot responsibly continue

## Primary Truth Surfaces

Read these first when relevant:

- local archive files under `data/research/`
- archive indexes such as `messages_index.jsonl`, `snapshots_index.jsonl`, `thesis_index.jsonl`
- canonical CLI or tool outputs that refresh archive state
- archived `message`, `content.md`, `content_selection`, `text_read`, `image_reads`, and `evidence_units`

Read design docs only when architecture or boundary is actually unclear:

- `designDoc/ai_native_trading_operating_system.md`
- `designDoc/knowledge_base_and_memory_system.md`
- `designDoc/source_connectors_and_knowledge_ingestion.md`

## Derived Surfaces Audit Boundary

Use `tradectl research audit-derived-surfaces` when the task is to check whether
research archive indexes, AI read sidecars, generated context surfaces, or theme
priority views still match their canonical payloads.

This command is a lightweight research archive surface audit. It should read
indexes and generated surface files directly. It should not start source
connectors, run message-processing refreshes, or construct the full
`ResearchService` workflow just to answer archive status questions.

Use heavier archive / message-processing commands only when the audit identifies
missing, stale, or blocked surfaces that actually need to be rebuilt.

## Required Outputs

This skill should leave behind one of these:

- updated archive artifacts
- updated durable knowledge objects
- a status summary that names changed paths, unchanged paths, and blockers
- a concrete next-step recommendation when the archive pass cannot fully finish

At minimum, the handoff or summary should say:

- `archive_scope`
- `status`
- `changed_objects`
- `best_downstream_surface`
- `blockers_or_review_needed`

## Content Surface Rule

For archived research messages, keep one simple external-facing body interface even if the archive keeps multiple internal variants.

Recommended internal contract:

- keep `main content`
- keep `normalized content`
- run an AI review that decides whether normalization preserved the real main content
- if normalization materially degrades the source, tag the item and prefer `main content`
- expose only one default external body surface to downstream workflows

Recommended downstream posture:

- downstream callers should not have to decide between `main`, `normalized`, or image evidence on their own
- the archive should return the single best default surface for the task
- image evidence remains first-class; do not let URL cleanup outrank reviewed charts, slides, screenshots, or OCR-backed evidence when those carry the real signal

## Research Image First-Pass Rule

For PDF pages, screenshots, charts, and other research-related images, use the archive's unified research-image contract.

- Treat every image passed into the first-pass reader as `research-related image`, not as a generic consumer photo
- First detect whether the page/image contains target visual evidence
- Only when `has_visual_evidence=true` should the first-pass result contain `visuals[]`
- Pure text pages, covers, logos, headers, footers, and decorative layout should not be treated as image evidence
- `content.md` should inline only true visual evidence blocks, not page-level narrative disguised as image summaries
- downstream consumers such as `content.md`, writer packages, and `evidence_units` should prefer `visuals[]` over page-level summary text

Current target visual types:

- `line_chart`
- `bar_chart`
- `area_chart`
- `scatter_chart`
- `pie_chart`
- `heatmap`
- `data_table`
- `diagram`
- `infographic`
- `screenshot`
- `photo`

## Runtime Guardrail

- Image first-pass should use both a per-call timeout and a per-image total hard limit
- Do not let retries plus fallback paths stretch one image read into many minutes
- If the total per-image budget is exhausted, fail that image explicitly rather than silently hanging

## Guardrails

- Treat local archive files as ground truth.
- Prefer canonical CLI and local tools over ad hoc one-off flows.
- Do not treat Gmail or another connector as the whole research system.
- Keep source connectors separate from downstream analysis.
- Preserve durable artifacts before producing summaries.
- Prefer minimal ingest parsing unless the user explicitly wants deeper preprocessing.
- Preserve source provenance and file-path references.

## Example Triggers

- “refresh research”
- “pull newsletters”
- “what new materials arrived”
- “check the archive”
