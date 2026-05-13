---
name: research-single-stock-analysis
description: "Analyzes one ticker as a Research mainline using ticker-first authority, deterministic technical state, local theme overlays, optional Digestion company dossier context, and related thesis context to produce a PM-facing single-stock package or draft. Use when the user asks for one stock view, one ticker analysis, whether a name matters now, or how a stock should be interpreted before moving into portfolio decision."
---

# Research Single-Stock Analysis

## What This Skill Does

Use this skill when the task is to interpret one ticker as its own mainline.

When `routing-task-mode-router` is available, it should send requests here only after matching the task to ticker-first analysis rather than to theme maintenance or portfolio decision.

This skill is for:

- one ticker analysis
- why this name matters now
- ticker-first PM-facing research notes
- integrating technical state, theme overlay, optional Digestion company dossier context, and thesis context into one stock view
- deciding whether the name is actionable now, watchlist-only, or structurally weak

This skill is not the primary workflow for:

- finalized theme-report maintenance
- market observations about what the whole market traded today
- business / financial / valuation memos where the company is first authority
- portfolio sizing, rebalancing, hedge sequencing, or target-book decisions
- pure asset-technical daily reports without stock-level synthesis

## Desired Result

The desired result is a ticker-first PM-facing view that makes these things explicit:

- the current judgment on the stock
- why the stock matters now
- what the tape says now
- what the local theme overlay adds or does not add
- what the bull-versus-bear debate really is
- what the action frame should be

Theme context may sharpen interpretation, but it must not replace ticker-specific judgment.

## Completion Standard

This skill is complete only when all of the following are explicit:

- target ticker
- current judgment
- why-now reason
- current technical state
- local theme overlay or explicit statement that no useful overlay exists
- related thesis context when relevant
- bull versus bear debate
- action framing
- monitoring items

Accepted outputs:

- deterministic single-stock package
- PM-facing single-stock analysis draft
- explicit conclusion such as `actionable now`, `watchlist only`, or `structurally weak`

If the output still reads like a generic theme note or a raw technical report, this skill is not done.

## Node Bindings

This skill owns the following nodes in `data/runtime/artifact_graph.yaml`:

- `single_stock.judgment(ticker, D)` — L3 judgment object that locks ticker-first read at `data/analysis/single_stock_analysis/<ticker>.judgment.md`
- `single_stock.package(ticker, D)` — L3 writer-facing package at `data/analysis/single_stock_analysis/<ticker>.package.md`
- `single_stock.ds(ticker, D)` — L4 PM-facing single-stock note at `data/analysis/single_stock_analysis/<ticker>.ds.md`

This skill consumes:

- `asset_technical_report(asset_id=ticker, D)` (must_be_fresh)
- `signal_packet(asset_id=ticker, D)` (must_be_fresh, transitively via `asset_technical_report`)
- optional `single_asset_dossier` from `digestion-company-expert` when independent company research has already produced company-owned evidence and claims
- `theme.knowledge(theme_id)` (optional_overlay) — overlay only, never first authority
- related thesis notes under `data/research/thesis_notes/` (referenced by id)

Builder kinds:

- `single_stock.judgment`, `single_stock.ds`: `ai_writer` (entrypoints `tradectl research draft-single-stock-analysis`)
- `single_stock.package`: `composite` (`tradectl research build-single-stock-analysis-package` + sufficiency review)

Detection-side boundary (what an unsigned violation looks like):

- the agent produced a `single_stock.ds(ticker, D)` whose backing `asset_technical_report(ticker, D)` is stale (`frontmatter.report_date < D`)
- the ds artifact exists but no `single_stock.judgment(ticker, D)` was produced — the judgment was implicit in chat
- the ds artifact reads as a theme note with the ticker attached — the theme overlay node silently took over first authority
- the ds artifact slid into book sizing or hedge sequencing language without explicit handoff to `operation-portfolio-decision`
- the ds was written through ad hoc python or hand-edit instead of `tradectl research draft-single-stock-analysis`
- the package step was skipped for non-trivial work; the ds was generated directly from the technical report alone

## First Authority

The stock itself is first authority.

Interpret the task in this order:

1. ticker and current tape
2. deterministic technical state
3. related local theme overlay
4. optional Digestion company dossier context
5. related thesis context
6. current market meaning
7. only then move toward portfolio-action language

This means:

- theme is overlay, not first authority
- PM-facing output does not automatically mean portfolio-manager-first routing
- the stock should not disappear into a broader theme just because a related theme exists
- a `single_asset_dossier` informs company evidence, but it does not decide the stock read by itself

## Boundary Versus Other Mainlines

Keep these boundaries explicit:

- versus `research-theme-report-owner`:
  - this skill asks what one stock means now
  - `research-theme-report-owner` asks how the standing theme framework should be maintained
- versus `research-current-market-reporter`:
  - this skill is ticker-first
  - `research-current-market-reporter` is market-window-first
- versus `portfolio decision`:
  - this skill produces interpretation and action framing for one name
  - `portfolio decision` turns sufficiently stable upstream interpretation into sizing, trade sequencing, hedge choices, and book construction
- versus pure technical writing:
  - this skill uses technical state as one layer
  - it should not collapse into indicator narration without stock-level judgment
- versus `research-company-financial-analysis`:
  - `research-company-financial-analysis` asks how the company business, financial quality, valuation bridge, public comps, and private / secondary evidence should be read
  - this skill asks what the listed security means now through ticker-first evidence, tape, technical state, theme overlay, and action framing
  - if the user wants both, consume the company-financial report first, then produce the ticker/tape/actionability read
- versus `digestion-company-expert`:
  - `digestion-company-expert` produces company evidence, permission boundaries, and `single_asset_dossier`
  - this skill consumes that dossier only as one input to PM-facing ticker interpretation

## Primary Truth Surfaces

Read these first:

- the user's request
- the target ticker's deterministic signal packet under `data/knowledge/asset_technicals/signal_packets/`
- the target ticker's AI-written technical report under `data/knowledge/asset_technicals/reports/`
- the deterministic package from `tradectl research build-single-stock-analysis-package` when available
- the package draft under `data/analysis/single_stock_analysis/<ticker>.package.md` when available

Read these next when relevant:

- `single_asset_dossier` under `data/digestion/independent_research/assets/<asset_key>/expert_outputs/company_expert/` when the request depends on independently collected company evidence
- related theme metadata and report chosen as overlay context
- related thesis notes tied to the ticker or chosen overlay theme
- recent local research items that materially change the ticker view

Use:

- `tradectl research build-single-stock-analysis-package`
- `tradectl research draft-single-stock-analysis`

as the canonical deterministic builder and writer exit for this mainline.

## Package Contract

Treat the single-stock package as the canonical writer-facing handoff for non-trivial work.

The package should make these explicit:

- ticker
- current technical state and key levels
- selected theme overlay and its role as overlay-only context
- selected thesis notes
- why the stock matters now
- bull case
- bear case
- action framing
- monitoring items

Package rules:

- keep the stock first
- do not let the theme overlay replace ticker-specific reasoning
- use exact technical levels and states when discussing trade framing
- preserve the difference between technical confirmation and fundamental support
- when consuming `single_asset_dossier`, preserve its public / proxy / cannot-know boundaries instead of upgrading digestion claims into PM certainty

## Writing Standard

Write the final output as one PM-facing single-stock analysis.

Keep these standards:

- lead with the current judgment
- explain why the name matters now
- separate what the tape says from what the fundamental overlay says
- make the bull-versus-bear debate legible
- state whether the name is actionable now, watchlist-worthy, or structurally weak
- end with action framing and monitoring items

Do not:

- let theme prose overwhelm ticker judgment
- turn the note into a macro theme report
- turn the note into a market recap
- hide behind vague stock-story language without current technical state
- jump straight into book sizing or execution sequencing unless the task has explicitly moved into `portfolio decision`

## Preferred Output Shape

- `Current judgment`
- `Why this name matters`
- `What the tape says now`
- `What the fundamental overlay says`
- `Bull vs bear debate`
- `Action framing`
- `Monitoring items`

## Routing Boundary With Company Financial Analysis

Use `research-company-financial-analysis` first when the request asks for:

- business / financial / valuation memo;
- company report;
- fundamental analysis;
- revenue engine, margin, unit economics, cash conversion, or balance sheet;
- public comps, valuation bridge, IPO / pre-IPO read, or secondary-market surface.

Use this skill first when the request asks for:

- ticker now;
- tape / technical state;
- actionability now;
- watchlist versus actionable;
- levels, trend, support / resistance, or current price behavior;
- how one listed security should be interpreted before portfolio action.

When both are requested, the order is:

```text
research-company-financial-analysis
  -> research-single-stock-analysis
  -> operation-portfolio-decision only if book action is requested
```

## Failure Signals

Treat these as signs this skill failed:

- the note reads like a theme report with a ticker attached
- the note reads like a technical report with no stock-level judgment
- action framing ignores the actual tape and levels
- theme overlay silently becomes first authority
- portfolio sizing or book-construction language appears before the upstream interpretation is stable
- the output cannot tell the reader whether the stock is actionable now, watchlist-only, or structurally weak

## Style Rules

- Write in Chinese by default unless the user requests another language.
- Keep market-standard English ticker and market terms when clearer.
- Use natural analyst prose, not literal translation.
- Keep the output decision-facing and readable by another PM without extra verbal explanation.

## Example Triggers

- “分析一下 ORCL”
- “这个票现在有没有意思”
- “写一份单股分析”
- “这个 ticker 现在是观察名单还是可以买”
- “结合 theme overlay 看一下这只股票”
