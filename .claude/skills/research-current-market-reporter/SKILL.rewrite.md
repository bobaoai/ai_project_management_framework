---
name: research-current-market-reporter
description: "Interprets the current market window and explains how asset prices evolved in the newest trading day or current reporting window. Use when the task is current-market interpretation, daily recap, post-close reporting, or a complete current market report rather than standing theme maintenance."
---

# Current Market Reporter

## What This Skill Does

Use this skill for current-market interpretation and reporting, not for standing theme-report maintenance.

Enter this skill when the real task is:

- daily recap
- post-close note
- current market report
- snapshot rewrite
- event-window market observation
- explaining what the market traded in the newest reporting window

Do not use this skill as the first authority for:

- finalized theme reports
- thesis-note maintenance
- theme metadata updates
- tree reprioritization
- report-refresh ownership
- report-anchored theme-candidate discovery

For those, use `research-theme-report-owner`, `research-theme-content-maintainer`, or `research-theme-priority-updater`.

## Positive Contract

- `Current persona`: `macro analyst`
- `Current task`: interpret the current market window and explain how asset prices evolved through one chosen mainline
- `Primary truth surface`: `data_layer.fresh(D)`, `current-market.intake(D)`, refreshed `asset_technical_report(asset, D)` read through index, the current Watchlist / observation universe, the current `Main Driver`, the chosen `Theme / Thesis` overlay when needed, the settled judgment object, and the deterministic package
- `Output artifact`: a complete PM-facing current market report, post-close note, daily recap, snapshot rewrite, or other current-window market report
- `Reader end-state`: after reading, the `PM` should be able to rank the dominant market read, understand whether it is actionable, conditional, or not yet actionable, and know what next question matters most. The `trader` should be able to distinguish which assets are truly carrying today's tape, which names look like valid add-candidates, which are already extended, and which remain conditional with a clear invalidation or next-confirmation condition. The recap should function as a decision-facing filter on the Watchlist rather than as a generic market summary.

This skill is successful only if the recap works as a decision-facing filter on the Watchlist rather than as a generic market summary.

## Node Bindings

This skill owns the following nodes in `data/runtime/artifact_graph.yaml`:

- `current-market.judgment(D)` - L3 judgment object that locks the mainline, market stage, key-asset spine, and package admission
- `current-market.package(D)` - L3 deterministic writer-facing package
- `current-market.ds(D)` - L4 PM-facing market recap / market observation; identity is `(node_id, frontmatter.session_date_market)` with legacy alias `frontmatter.report_date`

This skill consumes:

- `data_layer.fresh(D)` (`must_be_fresh`) - shared freshness gate across daily-update layers
- `current-market.intake(D)` - pre-judgment truth surface for the run
- `asset_technical_report(asset, D)` (`must_be_fresh`) for assets that enter the observation universe
- `themes.current_priority_tree` (`optional_overlay`)
- prior `current-market.ds(D-N)` (`optional_overlay`) when the run explicitly contrasts with a recent prior session

Builder kinds:

- `current-market.judgment`: `ai_writer`
- `current-market.package`: `composite`
- `current-market.ds`: `ai_writer`

## Daily Recap Fast Path

For the normal `Daily Market Recap` path, prefer this compact execution order:

1. verify `data_layer.fresh(D)` rather than improvising from partial local reads
2. build or read `current-market.intake(D)` as the pre-judgment truth surface
3. let `current-market.judgment(D)` lock:
   - one mainline
   - one market stage
   - one key-asset spine
   - one package admission decision
4. let `current-market.package(D)` carry that settled judgment downstream without re-selecting from the full Watchlist
5. let `current-market.ds(D)` amplify the settled judgment into PM-facing prose

Fixed invariants:

- do not skip the `judgment -> package -> ds` order
- do not bypass the shared daily-update gate for routine runs
- do not re-open asset admission in the final writer if `Package Admission` already settled it
- do not write the canonical recap by hand when the canonical builder exists

The recap is not "one DS write". It is an upstream judgment pass plus a downstream final-writing pass, with the package acting as deterministic carrier in between.

## Mismatch Impact Rule

When the tape contains a meaningful mismatch, do not smooth it away. Treat it as a decision object.

Typical market mismatches:

- broad beta tests a breakout but rates do not confirm
- oil de-risks but gold does not fully give back
- index strength is narrow and breadth lags
- one marquee asset confirms while the broader cluster still only probes
- the macro line looks cleaner than the technical state, or vice versa

For each real mismatch, make explicit:

- what is mismatching
- why that mismatch lowers confidence, changes stage, or narrows the valid read
- what next confirmation would resolve it
- whether the mismatch should stay central in the final article or remain supporting caution

Keep the interpretation adaptive:

- do not force theme-first when the tape is better explained directly from cross-asset state
- do not force a fixed asset count when fewer names fully carry the read
- do not force one article skeleton when a mismatch-heavy tape needs a different emphasis order

If the mismatch is workflow-level rather than market-level, fail closed instead of deciding locally:

- stale or undeclared mixed-horizon package
- malformed `Package Admission`
- missing required judgment object
- package missing the required time block for timing claims

## Time Contract

Before writing any market-timing claim, load the package's structured time block first.

Keep these layers separate:

- `*_at_utc`: exact machine-time facts
- `built_at_utc` / legacy `generated_at`: artifact build instant, not market close
- `session_date_market` / legacy `report_date`: market session day for the artifact
- `data_anchor.session_close_at_utc`: authoritative session close instant
- `session_as_of`: per-asset market-semantic horizon for technical claims

Rules:

- never use `built_at_utc` as a market close
- never let title date or run date replace per-asset `session_as_of`
- when assets disagree on session horizon, say that early and explicitly
- if the package lacks a usable UTC / session block, fail closed instead of improvising time claims
- all freshness and idempotency checks are made on UTC anchors first; human-readable ET / PT wording is a rendering step, not the decision layer

## Boundary Versus `research-theme-report-owner`

Keep the distinction simple:

- `research-current-market-reporter` explains the current market window
- `research-theme-report-owner` maintains the standing theme framework
- this skill may note that today's tape strengthened, weakened, or complicated a theme
- once the real task becomes standing-framework maintenance, report refresh, or framework revision, move first authority to `research-theme-report-owner`

Theme overlay is allowed here, but theme maintenance is not the center of gravity of this skill.

## Completion Standard

This skill is complete only when the produced market note leaves the downstream readers with clearer judgment ability rather than only a cleaner summary.

The `PM` should be able to leave the note knowing:

- the chosen observation mainline
- the current market stage
- the key asset spine that carries the article
- what confirmed the read
- what did not confirm the read
- what remains unresolved
- what next question matters most
- why the current read is actionable, conditional, or not yet actionable

The `trader` should be able to leave the note knowing:

- which assets are actually carrying today's tape versus which assets are only background confirmation
- which names look like valid add-candidates, which are extended, and which are still conditional
- what the key invalidation, failure, or next-confirmation condition is for the most important assets
- whether the current tape is in probe, first confirmation, extension, failed reclaim, or unresolved split state

Accepted outputs:

- PM-facing current market report
- post-close note
- daily recap
- snapshot rewrite
- other current-window market report built from the same canonical chain

If the note still leaves the `PM` unable to rank the read and its next question, or leaves the `trader` unable to distinguish addable versus extended versus still-conditional names, the skill is not done.

## Guardrails

- Do not let the priority tree override a user-specified mainline.
- Do not write a market observation without an explicit observation basket decision upstream.
- Do not bypass the shared daily-update gate by default when the run would consume technical refresh or writer work.
- Do not blur confirmed and unconfirmed evidence.
- Do not turn one day of price action into a regime conclusion without support.
- Do not let related-theme context replace the mainline.
- Do not treat the observation package as optional.
- Do not rewrite package admission in the final writer.
- Do not let builder / gate detail dominate the PM-facing result.

## Failure Signals

Treat these as signs the skill failed:

- the note reads like a standing theme report instead of a market-window interpretation
- the current judgment is not stated clearly
- the key assets do not form a readable state map
- the mainline is silently replaced by overlay context
- a meaningful mismatch was present upstream but got flattened into a cleaner story
- package / gate language becomes more prominent than the market judgment itself
- the note implies timing certainty that the package's time block does not actually support

## Appendix: Reference Heuristics

This appendix is reference material, not the primary execution contract. Use it to improve judgment quality, not to replace the canonical fast path above.

### Mainline And Truth Surface Heuristics

Choose one observation mainline from:

1. the user's explicit request
2. the most clearly implied theme, event line, or asset lens
3. `data/research/themes/current_priority_tree.json` only as fallback

Then prefer this reading order:

1. the user's request and time/window constraints
2. the fixed baseline observation surface
3. the observation universe for non-core tradable equities:
   - current holdings from latest account snapshots
   - watchlist
   - theme-related stocks already defined in indexes
4. refreshed technical reports for that non-core tradable universe, read through generated indexes first
5. the current `Main Driver`
6. relevant local theme report only when it materially helps explain the current tape
7. relevant snapshots and linked local research
8. public verification only when the note depends on dated price action, headline sequencing, or public wording

Reference rules:

- do not override a user-specified mainline with the tree
- keep one mainline and treat overlapping themes as supporting context
- do not choose non-core tradable equities by loose intuition before reviewing refreshed technical reports

### Fixed Baseline Heuristics

The fixed baseline should normally cover:

- major rates, FX, and equity-index futures
- gold, oil, and volatility
- the next `FOMC`
- important macro release dates in the next 30 days, with the next week treated as the most sensitive watch window

### Observation Basket Heuristics

Every market observation should have an explicit observation basket before final prose drafting.

Build the basket in layers:

1. core driver assets
2. first-order confirmation assets
3. disconfirmation / hedge assets
4. physical, flow, or plumbing assets when relevant

The basket should be able to answer:

- what should move if this read is right
- what should confirm the move
- what should fail to confirm if the read is weak

When the basket includes futures, use slash-root notation by default:

- `/ES`
- `/NQ`
- `/CL`
- `/GC`
- `/ZN`
- `/VX`

### Evidence And Verification Heuristics

Start local-first:

- this run's observation package
- relevant theme report when needed
- relevant snapshots
- linked local research

Add public verification only when:

- the user asked for it
- the note depends on dated price action
- the note depends on headline sequencing
- the note depends on public policy wording

If public verification is needed, prefer narrow prompts and explicit date windows. Keep confirmed and unconfirmed evidence separate.

### Package And Technical Heuristics

Every observation should use the dedicated package before final drafting.

The package should mainly carry:

- settled market judgment
- admitted key asset spine
- admitted main-reading materials
- unresolved questions worth preserving for the final note

When the repo has generated technical inputs, use them explicitly:

- deterministic packets: `data/knowledge/asset_technicals/signal_packets/`
- AI-written summaries: `data/knowledge/asset_technicals/reports/`
- generated index: `data/knowledge/asset_technicals/index.json`

Use deterministic packets for technical evidence and AI-written asset summaries for interpretation.

### Output-Shape Heuristics

Default article shape for most runs:

- `Current judgment`
- `Price action by key assets`
- `What the market priced`
- `What did not confirm`
- `Why it matters`
- `Next watch`

For very short snapshots, compress to:

- judgment
- key asset reactions
- takeaway

For event-driven post-close notes, prefer:

- `Current judgment`
- `Catalyst`
- `Cross-asset reaction`
- `What remains unresolved`
- `Next watch`

These are default shapes, not required templates. If today's tape is cleaner with a different emphasis order, adapt.

### Example Triggers

- "这个 theme 今天市场怎么走"
- "写个今天的市场报告"
- "写一个盘后 note"
- "今天市场到底在交易什么"
- "从 Iran/Hormuz 这条线看今天收盘"
- "根据 gold 这条 theme 写个 market observation"
