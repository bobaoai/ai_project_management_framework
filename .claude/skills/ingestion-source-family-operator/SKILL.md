---
name: ingestion-source-family-operator
description: Operates source-family-specific ingestion. After this skill runs, downstream task agents can rely on `read_content.md` alone without inspecting raw archive internals. Use after messages land in `data/research/messages/` and before any analysis skill consumes them.
---

# Source Family Ingestion Operator

## What This Skill Does

Use this skill after a message has landed in the research archive and needs source-aware processing.

This skill is for:

- identifying source family from `source_collection`
- deciding whether the message is `text_led`, `image_led`, or `hybrid`
- deciding which images should be reviewed by Claude
- running the canonical image review and read-content refresh commands
- checking whether `read_content.md` is ready for downstream AI agents

This skill is not for:

- checking whether a message exists in the archive: route to `ingestion-research-archive-operator`
- designing a new connector: route to `ingestion-source-connector-designer`
- isolated image-reading prompt tuning: route through the image-review contract, then return here for readiness
- writing theme reports, thesis notes, PM recommendations, or portfolio actions

## Primary Truth Surfaces

Read in this order:

1. `designDoc/ingestion_50_source_family_playbook.md`
   - source-family rules: which images, which mode, which reader gain
2. `data/research/messages/<research_id>/read_content.md`
   - current downstream-facing artifact and readiness state
3. `data/research/messages/<research_id>/message.json`
   - source metadata and `source_collection` identity
4. `data/research/messages/<research_id>/image_reviews.jsonl`
   - per-image review status, evidence value, and reviewer model
5. `data/research/messages/<research_id>/image_placements.jsonl`
   - HTML / newsletter inline image anchors when source was downloaded from email
6. `data/research/messages/<research_id>/content_selection.json`
   - assembly/audit notes for read-content construction

Do not ask downstream analysis prompts to inspect raw archive internals.

## Inputs

- `research_id` is required.
- `message.json` must already exist under `data/research/messages/<research_id>/`.
- Upstream archive presence / freshness is owned by `ingestion-research-archive-operator`.

## Acceptance Contract

This skill is complete when:

- `read_content.md` exists.
- `readiness_status` is `ready`, `ready_with_warnings`, or `blocked`.
- Every evidence-bearing image required by `ingestion_50` has a reviewed row in `image_reviews.jsonl`.
- Every non-evidence image row has reached a terminal dismissal state rather than staying `pending`.
- `image_reviewed` in `read_content.md` matches the current `image_reviews.jsonl` ledger.
- For email-downloaded HTML/newsletter sources, evidence-bearing reviewed images are anchored through `image_placements.jsonl` and appear near source-local text in `read_content.md`.
- Decorative / non-evidence images do not appear in `read_content.md`.
- `upstream_blockers[]` and `warnings[]` reflect the actual archive state.
- Downstream agents can use `read_content.md` without re-judging image relevance, rendering PDF pages, or filtering source-family decoration.

## Canonical Operations

First classify pending rows. Do not send obvious non-evidence images to Claude review. Dismiss rows such as logo, branding, avatar, CTA button, publish / subscribe button, tracking pixel, spacer, repeated footer, or decorative legal / disclosure art as terminal reviewed rows with `has_visual_evidence=false`, `evidence_value=none`, and a deterministic local-gate `review_model`.

Run Claude review only for still-pending evidence-bearing rows:

```bash
./.venv/bin/python -m src.cli.tradectl message review-images-claude \
  --research-id <research_id> \
  --image-id <selected_image_id>
```

Refresh message-level reads after review:

```bash
./.venv/bin/python -m src.cli.tradectl message refresh \
  --research-id <research_id> \
  --force
```

Suggested method:

- Resolve source family from `message.json`.
- Read the matching section of `ingestion_50_source_family_playbook.md`.
- Inspect pending image rows.
- Dismiss obvious non-evidence rows locally.
- Select remaining evidence-bearing pending images.
- Run the two canonical operations above only when acceptance is not already satisfied.
- Re-read `read_content.md` and verify the acceptance contract.

## Image Reviewed State Logic

`image_reviews.jsonl` is the authority for `image_reviewed`; `read_content.md` frontmatter is only the latest projection.

Use this rule:

- no image review rows means `image_reviewed=true`
- all rows with `status: reviewed` means `image_reviewed=true`, including deterministic dismissals with `has_visual_evidence=false`
- any pending / failed / parse-failed / non-reviewed row means `image_reviewed=false`

Normal batch review must only target `status=pending` rows. Already reviewed rows are not rerun unless the user explicitly asks to repair or overwrite them.

After any row state changes, refresh `read_content.md` so the frontmatter and inline visual evidence match the ledger. Before running `message derive-agent-evidence`, check the current ledger again; do not rely only on an old frontmatter value.

## Email Image Placement Contract

Email-downloaded Substack/newsletter sources often preserve image order in `body.html`. When an email source has several evidence-bearing reviewed images, the operator must ensure the archive has a usable placement surface:

- `image_placements.jsonl` should be generated from `body.html` plus `external_images.jsonl`.
- `read_content.md` should use those anchors to place reviewed visual evidence near the paragraph where the image appeared.
- Inline image blocks in `read_content.md` should use `<image id="...">...</image>` and include only the image id plus reader-useful fields such as Takeaway, Key Numbers, Visible Facts, and Interpretation. Do not include `image_path`, placement labels, file names, or URLs in the inline body.
- If `read_content.md` has `email_image_anchors_missing` in `upstream_blockers[]`, stop and repair the archive before routing the source to downstream analysis.
- Repair means inspecting the audit paths named by the blocker, usually `body.html`, `external_images.jsonl`, `image_reviews.jsonl`, and `image_placements.jsonl`, then rebuilding `read_content.md`.
- Do not let a source with many evidence-bearing images silently fall back to one global trailing `Reviewed Image Evidence` section.

## Canonical Image Reader

The only canonical image reader for financial research images is the local Claude Code CLI invoked as:

```bash
claude -p --model claude-opus-4-7 --effort max
```

Runtime resolution order: `CLAUDE_CODE_BIN`, then `claude` on `PATH`, then the local user default discovered by code. If no Claude Code CLI is found, report a blocker. The production archive path has no alternate reader.

Do not add `--permission-mode bypassPermissions` for image review. The image reader only needs to read the explicit local image path and return JSON; Python owns archive writes. If default CLI permissions cannot read the image, report a blocker instead of widening permissions silently.

Prompt and usage contract:

- Fixed review instructions must appear before dynamic fields.
- Dynamic fields such as `image_id` and `image_path` belong at the end of the prompt.
- Keep CLI flags stable across runs: `--model claude-opus-4-7`, `--effort max`, `--output-format json`.
- Record Claude Code outer `usage` rows in `image_review_usage.jsonl`; use `cache_read_input_tokens` and `cache_creation_input_tokens` to verify cache behavior instead of assuming it.
- Keep the production quality path as one image per Claude call. Use bounded batches only as orchestration (`25` separate image calls), not as multi-image prompts.

If Claude image review fails, surface the failure and leave the image row pending or failed. The production archive path has no alternate reader.

Neighboring skill boundary:

- `ingestion-image-review-reader` is the older generic image-reading contract. Source-family ingestion uses `ingestion_50_source_family_playbook.md` plus Claude Code CLI as the canonical route for financial research images.
- If `ingestion-image-review-reader` is used for prompt experimentation, its output must still be written back through `image_reviews.jsonl` and then verified here.

## Source-Family Rules

Canonical truth: `designDoc/ingestion_50_source_family_playbook.md` §3–§7.

Read the section matching `source_collection.family` / `collection_id`. Do not improvise rules for unfamiliar families; use the generic section and surface a warning that the family needs a dedicated section if it recurs.

## Silent Violation Signals

- Non-Claude fallback ran silently: `image_reviews.jsonl` has reviewed rows for financial research images with `review_model` not matching `claude-opus-4-7`.
- Decorative images polluted read content: `read_content.md` references image rows whose `evidence_value` is `none` or whose review says `has_visual_evidence=false`.
- Decorative images consumed model quota: obvious logo / CTA / avatar / tracking rows remain pending until Claude review instead of being locally dismissed.
- Reviewed images were rerun by default: already reviewed rows have new `reviewed_at` values even though no repair / overwrite was requested.
- Stale frontmatter was treated as authority: `read_content.md` says `image_reviewed=true` while current `image_reviews.jsonl` still has pending / failed rows.
- Cache behavior became invisible: image reviews run without appending usage rows, so `cache_read_input_tokens` cannot be audited.
- Multi-image prompt was introduced silently: several images are passed to one Claude prompt without revalidating the quality contract.
- Archive internals leaked downstream: a downstream prompt cites `message.json`, `content.md`, `image_reviews.jsonl`, or raw `image_path` instead of `read_content.md`.
- Image rows never existed: source has PDF pages / external images, but `image_reviews.jsonl` is missing or empty and `read_content.md` is marked `ready`.
- Email image anchors were lost: email source has several reviewed visual-evidence rows, no usable `image_placements.jsonl`, and `read_content.md` is not blocked.
- Source-family policy was skipped: `source_collection.family` is known, but the corresponding `ingestion_50` section was not applied before readiness was reported.

## Status Output

Return a short status:

```text
archive_scope: <research_id>
source_family: <family / collection_id>
image_review: <reviewed_count>/<total_count>
readiness_status: <ready|blocked|ready_with_warnings>
next_action: <none|review remaining images|repair blockers>
```

