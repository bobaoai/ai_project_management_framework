---
name: ingestion-image-review-reader
description: Reads charts, screenshots, slides, infographic-like images, and multi-page research PDF pages into structured evidence rows. Use when reviewing local archive images, tuning image-analysis prompts, classifying page role, extracting chart/table details, or writing reviewed results back to `image_reviews.jsonl`.
---

# Image Review Reader

## Purpose

Use this skill when the task is to read image evidence as research input rather than as generic OCR.

Default execution surface:

- for financial research archive images, use the source-family ingestion route:
  `./.venv/bin/python -m src.cli.tradectl message review-images-claude --research-id <rid>`
- the canonical reader is Claude Code CLI with `--model claude-opus-4-7 --effort max`
- no fallback to Cursor Agent or OpenAI for production archive review
- use this skill directly only for prompt experimentation, local inspection, or non-production review notes

This skill is for:

- single charts
- screenshots
- slides
- tables
- infographic-like pages
- multi-page research PDFs that have already been split into page images

This skill is not for:

- PM-facing report writing
- theme ranking
- thesis-note drafting
- connector design

## Default Posture

- Treat images as first-class evidence, not as an OCR afterthought.
- Distinguish strictly between:
  - what is visibly present
  - what claim that evidence supports
  - what remains uncertain
- Prefer structured evidence over fluent prose.
- Do not invent precise numbers, labels, dates, or correlations if they are not clearly visible.
- For multi-page research PDFs, classify each page before deciding how much detail it deserves.
- Disclosure, legal, appendix, and admin pages should usually be tagged as low-value or no-value evidence.

## Output Contract

Return a structured review row suitable for `image_reviews.jsonl`.

Preserve the legacy top-level fields:

- `image_type`
- `summary`
- `ocr_text`
- `key_numbers`
- `claims_supported`
- `confidence`

Also populate the richer fields when supported:

- `page_role`
- `evidence_value`
- `main_takeaway`
- `visible_facts`
- `inference`
- `uncertainties`
- `pm_relevance`
- `incremental_evidence`
- `visuals`

## Archive State Rules

For production financial research archive work, this skill operates under the source-family ingestion contract:

- `image_reviews.jsonl` is the authority for image review state.
- Already `status: reviewed` rows are not rerun by default.
- Normal batch work handles only `status=pending` rows.
- Obvious non-evidence images should be dismissed before model review: logo, branding, avatar, CTA / subscribe / publish button, tracking pixel, spacer, repeated footer, decorative legal / disclosure art.
- A dismissed non-evidence row is still terminal: set `status=reviewed`, `has_visual_evidence=false`, `evidence_value=none`, `incremental_evidence=false`, and explain the dismissal in `summary`.
- Only pending rows that may contain chart, table, dashboard, screenshot, diagram, infographic, or PDF page evidence should reach the canonical image reader.
- Do not use `--permission-mode bypassPermissions` in production archive review. The reader only needs the explicit local image path; Python writes `image_reviews.jsonl`.
- Keep the prompt prefix byte-stable: fixed instructions first, dynamic `image_id` / `image_path` at the end.
- Append Claude Code outer `usage` to `image_review_usage.jsonl` so `cache_read_input_tokens` and `cache_creation_input_tokens` are observable.
- Keep production review to one image per Claude call; bounded batches may orchestrate multiple single-image calls, but must not combine multiple images into one prompt without a new quality review.

`read_content.md` frontmatter `image_reviewed` is computed from the current `image_reviews.jsonl` ledger:

- no rows: true
- all rows terminal reviewed, including local dismissals: true
- any pending / failed / parse-failed row: false

After changing review rows, rerun `tradectl message refresh --research-id <rid> --force` so `read_content.md` reflects the current ledger.

## Mode Selection

Choose one of two contracts:

- `single_chart_or_screenshot`
- `multi_page_research_pdf`

Use `single_chart_or_screenshot` when the file is one standalone chart, screenshot, or infographic-like image.

Use `multi_page_research_pdf` when the image is one page from a larger research PDF or deck.

## Single Chart Or Screenshot

Extract:

- image type
- page role
- evidence value
- concise summary
- OCR-like text only when actually visible
- visible facts
- supported claims
- uncertainty limits
- visual breakdown in `visuals`

For each visual in `visuals`, prefer:

- `title`
- `visual_type`
- `series_or_segments`
- `x_axis`
- `y_axis`
- `units`
- `time_window`
- `direction`
- `key_inflections`
- `approx_numbers_visible`
- `comparison_relationship`
- `visible_facts`
- `supported_claims`
- `uncertainties`

## Multi Page Research PDF

Treat the input as one page from a larger document.

First classify:

- `page_role`: `analysis`, `chart`, `table`, `cover`, `disclosure`, `appendix`, or `other`
- `evidence_value`: `high`, `medium`, `low`, or `none`
- whether the page adds `incremental_evidence`

Then separate:

- page text thesis
- chart or table evidence
- key numbers worth preserving
- supported claims
- uncertainties

Rules:

- do not let disclosure pages masquerade as thesis evidence
- do not blend page text and chart evidence into one vague summary
- if a page is mostly legal or admin content, say so explicitly

## Writing Rules

- Return compact, analysis-usable language.
- Keep `summary` short.
- Keep `claims_supported` to claims the image actually supports.
- Use `inference` only for modest interpretation that clearly follows from visible evidence.
- Use `uncertainties` for unreadable axes, cropped context, ambiguous labels, or missing scales.
- If exact numeric extraction is not justified, say so and keep the claim directional.

## Validation

Before finalizing a row, check:

- page role is explicit
- evidence value is explicit
- visible facts and inference are separated
- disclosure pages are filtered correctly
- no unsupported exact numbers were invented
- `visuals` is present when the page contains charts or tables

## Example Triggers

- “read this chart”
- “review the screenshot”
- “analyze the PDF page images”
- “improve image review prompt”
- “write reviewed image evidence back to archive”
