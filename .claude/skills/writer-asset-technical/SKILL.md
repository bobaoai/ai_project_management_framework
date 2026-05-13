---
name: writer-asset-technical
description: Writes daily asset technical summaries from canonical methodology profiles and deterministic signal packets. Use when the user asks for per-asset technical reports, daily price-action summaries, technical sections for a market-observation package, or wants GPT-5.4 to interpret generated technical signals instead of hardcoded Python prose.
---

# Asset Technical Writer

## What This Skill Does

Use this skill when the repo already has:

- `data/knowledge/asset_technicals/profiles.json`
- `data/knowledge/asset_technicals/signal_packets/*.json`

The job is to turn those deterministic packets into concise PM-facing asset summaries.

Code owns:

- bars
- indicator values
- signal labels
- symbol mapping
- methodology metadata

GPT owns:

- weighting signals
- deciding what matters today
- framing support and resistance
- writing the final summary

## Desired Result

The desired result is a concise PM-facing technical report that turns deterministic signal state into a reusable asset-level state read without inventing a narrative the packet does not support.

By the time this skill is done, a downstream reader should be able to tell:

- which asset is being read
- which deterministic methods dominate the interpretation
- what stage the asset is in now
- what key levels or confirmation / failure conditions matter
- why this asset matters now in a broader market workflow
- whether the read is directional, mixed, or data-limited
- over **days to weeks**, what **conditional** entry or add-risk paths (if-then) are worth ranking, what invalidation costs versus the next objectives the packet supports, and whether the PM should treat the name as **watch**, **size only if triggers fire**, or **do not add risk** until structure improves

If the output only restates indicators or sounds like raw packet narration, this skill has failed.

## Completion Standard

This skill is complete only when all of the following are true:

- the asset identity and packet date are correct
- the asset identity, raw UTC timestamp, and session label are not confused
- the dominant methods are named or clearly reflected in the prose
- the current read is explicit
- the current stage is explicit enough to reuse downstream
- important levels or confirmation / failure conditions are stated when relevant
- a `Trade Framing (几日到几周)` layer gives **reader gain** for trader and PM (conditional paths, asymmetry / odds framing), not empty section headers
- uncertainty is preserved when signals are mixed or incomplete
- the final report is written to `data/knowledge/asset_technicals/reports/<report_id>.md`

Accepted outcomes:

- one decisive technical summary
- one mixed / conditional technical summary
- one explicit data-limited summary when the packet is insufficient

## Node Bindings

This skill owns the following node in `data/runtime/artifact_graph.yaml`:

- `asset_technical_report(asset_id, D)` — L2 AI-interpretive report at `data/knowledge/asset_technicals/reports/<report_id>.md`

This skill consumes:

- `signal_packet(asset_id, D)` (must_be_fresh) — deterministic packet at `data/knowledge/asset_technicals/signal_packets/<asset_id>.json`
- `data/knowledge/asset_technicals/profiles.json` (treated as configuration, not a graph node in v0.1)

Downstream nodes that depend on this skill's output:

- `current-market.judgment(D)` (must_be_fresh, parameterized over the day's observation universe)
- `single_stock.judgment(ticker, D)` (must_be_fresh)
- `theme.package(theme_id, D)` (optional_overlay for asset-centered themes)

Builder kind: `ai_writer` (entrypoint `tradectl technical draft-reports-ds` or equivalent)

Detection-side boundary (what an unsigned violation looks like):

- the report's `frontmatter.report_date` does not match the requested D, even though the file was written today
- the report's `frontmatter.report_date` is older than the underlying `signal_packet`'s `as_of` — the packet was refreshed but the report was not regenerated
- the report was hand-edited instead of regenerated through the canonical writer (no writer sidecar, no record of which packet hash it consumed)
- the report copies packet numerics verbatim with no method-emphasis judgment layer
- the report invents levels, stages, or trade framing the packet does not support
- the report mixes raw UTC market timestamps with `report_date` in a way that obscures which is the session label and which is machine time

## Primary Inputs

Read these first:

- `data/knowledge/asset_technicals/profiles.json`
- the latest `data/knowledge/asset_technicals/signal_packets/*.json`
- the packet's paired markdown file when it carries useful human-readable context

Time discipline on those inputs:

- treat `daily.ohlcv.timestamp_utc` or equivalent UTC fields as the raw machine-time truth
- treat `session_date_utc` / `session_as_of` as derived market-semantic fields
- treat `report_date` as a label field unless the packet explicitly states a narrower meaning

## Required Report Frontmatter

Use this frontmatter so the index builder can discover the latest AI-written summary:

```markdown
---
report_id: future_es
asset_id: /ES
display_name: E-mini S&P 500 Futures
report_date: 2026-03-26
generated_at: 2026-03-27T00:15:00Z
source_signal_packet: data/knowledge/asset_technicals/signal_packets/future_es.md
takeaway: Short one-line takeaway.
---
```

Frontmatter rule:

- `generated_at` is the report audit time
- `report_date` is a reader-facing session label only
- raw UTC market timestamps should stay in the packet/package, not be silently replaced by `report_date`

## Required Output Shape

At minimum, the report should contain:

- frontmatter discoverable by the index builder
- the current technical judgment
- an `Asset State` layer that makes the current stage legible
- method emphasis when it materially explains the read
- key levels, confirmation conditions, or failure conditions when relevant
- a short `Why It Matters Now` layer so downstream market reports can use the asset in context
- a `Trade Framing (几日到几周)` layer: trader can rank conditional entry paths and rough risk vs next objectives from the packet; PM can place the name in the book stack (watch vs conditional size vs no add) without duplicating `Asset State`

## Writing Rules

- Keep futures in slash-root notation.
- Mention the returned contract mapping when it helps, for example `/ES -> /ESM26`.
- Keep raw UTC market timestamps conceptually separate from session labels and prose render dates.
- State which methods were emphasized so the read is durable day to day.
- Prefer a short decisive paragraph over a laundry list of indicators.
- If signals are mixed, say they are mixed. Do not force a trend call.
- If data is missing, say so directly and do not invent a technical narrative.

## Suggested Body Shape

```markdown
# /ES technical summary

Method emphasis: `trend_ema_stack`, `swing_structure`, `support_resistance`.

## Asset State

<One compact section on stage, recent path, key levels, confirmation, and failure conditions.>

## Why It Matters Now

<One compact section on why this asset matters in the broader market read right now.>

## Trade Framing (几日到几周)

<Conditional entry or add-risk paths, invalidation vs next objectives from the packet, asymmetry framing — reader should know watch vs actionable-if-X.>
```

## Package Use

When these summaries feed a theme package:

- let the asset report carry the narrative interpretation
- let the signal packet carry the deterministic evidence
- keep proxy assets such as `SPY`, `QQQ`, `GLD`, `XLE`, `XOP` as confirmation layers rather than replacements for futures

## Canonical Follow-Through

After report updates, rebuild the generated index so the latest AI-written summary is discoverable.

## Guardrails

- Do not copy the packet verbatim into prose.
- Do not turn support or resistance candidates into certainty.
- Do not ignore the methodology profile notes.
- Do not let public anchors override the tracked asset.
- Do not treat `report_date` as the raw market-data timestamp when the packet already provides a UTC time field.
