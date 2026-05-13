---
name: research-current-market-reporter
description: "Interprets the current market window and explains how asset prices evolved in the newest trading day or current reporting window. Use when the task is current-market interpretation, daily recap, post-close reporting, or a complete current market report rather than standing theme maintenance."
---

# Current Market Reporter

## What This Skill Does

Use this skill for current-market interpretation and reporting, not for standing theme-report maintenance.

When `routing-task-mode-router` is available, it should send requests here only after matching the task to the market observation / market recap mainline.

This skill is for:

- daily recap
- post-close notes
- current market reports
- snapshot rewrites
- event-window market observations
- explaining how asset prices evolved in the newest trading day or current reporting window

This skill is not the primary workflow for:

- finalized theme reports
- thesis-note maintenance
- theme metadata updates
- tree reprioritization
- report-refresh ownership
- report-anchored theme-candidate discovery

For those, use `research-theme-report-owner`, `research-theme-content-maintainer`, or `research-theme-priority-updater`.

## Positive Contract

- `Current persona`: `macro analyst`
- `Current task`: interpret the current market window and explain how asset prices evolved in the newest trading day or current reporting window through one chosen mainline
- `Primary truth surface`: the current window, the current `Watchlist` (= fixed `ObservationTickerPool` core slice ∪ `database observation universe` non-core slice; dynamic, currently ≈ 71 assets, designed to grow), refreshed asset technical reports read via index, the current `Main Driver`, the chosen `Theme / Thesis` framework, this run's observation package, and the concrete observation basket
- `Output artifact`: a complete PM-facing current market report, post-close note, daily recap, snapshot rewrite, or other current-window market report
- `Reader end-state`: after reading, the PM should be able to look at the current Watchlist and identify which assets are sitting at low / oversold / base-rebuild positions that warrant adding exposure, which are extended and not for adding, and which are still in conditional state. The recap functions as a **low-add-candidate filter on the Watchlist**, not a generic market summary; if a reader cannot leave the recap with a shortlist of add-candidates and a stop/condition for each, the recap missed its job

## Node Bindings

This skill owns the following nodes in `data/runtime/artifact_graph.yaml`:

- `current-market.judgment(D)` — L3 judgment object that locks the mainline, main driver, and observation basket for date D
- `current-market.package(D)` — L3 writer-facing package
- `current-market.ds(D)` — L4 PM-facing recap / market observation; identity is `(node_id, frontmatter.session_date_market)` (legacy alias: `frontmatter.report_date`) even though the canonical path is a singleton (`current-market.ds.md`)

This skill consumes:

- `data_layer.fresh(D)` (must_be_fresh) — the meta gate that aggregates `daily_update_status`, `signal_packet(*, D)`, and `account.snapshot(D)`
- `asset_technical_report(asset, D)` (must_be_fresh) for each asset in the observation universe
- `themes.current_priority_tree` (optional_overlay)
- prior `current-market.ds(D-N)` (optional_overlay) when the recap consciously contrasts with a recent prior session

## Daily Recap Fast Path

For the normal `Daily Market Recap` path, prefer this compact execution order:

1. verify `data_layer.fresh(D)` rather than improvising from partial local reads
2. build or read `current-market.intake(D)` as the pre-judgment truth surface
3. let `current-market.judgment(D)` lock:
   - one mainline
   - one market stage
   - one key-asset spine
   - one admitted main-reading surface
4. let `current-market.package(D)` carry that locked judgment downstream without re-selecting from the full Watchlist
5. let `current-market.ds(D)` amplify the locked judgment into PM-facing prose

Fixed invariants for efficiency:

- do not skip the `judgment -> package -> ds` order
- do not bypass the shared daily-update gate for routine runs
- do not re-open asset admission in the final writer if `Package Admission` already settled it

## Adaptive Decision Rule

The workflow should stay judgment-first, but not template-rigid.

Keep these choices adaptive to the actual tape:

- whether a theme overlay is needed at all
- whether the mainline is best expressed as macro shock, cross-asset repair, technical squeeze, de-escalation unwind, or still-unresolved mixed tape
- whether the key-asset spine is closer to 3 names or 6 names
- whether public verification is necessary or the local package is already sufficient
- which mismatch deserves to become the article's main unresolved question

Do not optimize for one fixed logic such as:

- always theme-first
- always broad-index-first
- always 5 named assets
- always one identical article skeleton regardless of the tape

Instead optimize for the shortest path that still leaves the PM with the declared `Reader end-state`.

## Mismatch Impact Rule

When the tape contains a meaningful mismatch, do not smooth it away. Use it as a decision object.

Typical examples:

- broad beta tests a breakout but rates do not confirm
- oil de-risks but gold does not fully give back
- index strength is narrow and breadth lags
- one marquee asset confirms while the broader cluster still only probes

For each real mismatch, make explicit:

- what is mismatching
- why that mismatch lowers confidence, changes stage, or narrows the valid read
- what next confirmation would resolve it

If the mismatch is upstream-structural rather than market-semantic, fail closed instead of deciding locally:

- stale or mixed-horizon package that was not declared
- malformed `Package Admission`
- missing required judgment object

Builder kinds:

- `current-market.judgment` and `current-market.ds`: `ai_writer`
- `current-market.package`: `composite` (deterministic intake assembly + `writer-handoff` gate)

Three LLM passes (a recap is **not one DS write — it is three sequential LLM jobs**, in this order):

- `DS pass #1` — `asset_technical_report(asset, D)` × N: triggered by `tradectl data update`, which (a) refreshes price bars in Postgres, (b) deterministically rebuilds every Watchlist asset's `signal_packet`, and (c) calls the per-asset DS writer only for assets whose L2 report is not already anchored to the new post-close data. The idempotency invariant — **expressed entirely in UTC** per axiom T11 — is: an existing report is safe to reuse iff its underlying packet (= the packet whose hash the report was written from) already contains the **post-close, fully-formed daily bar** for the requested market session. Operationally this means `packet.data_anchor.session_date_market` covers the requested session and `packet.built_at_utc` is at or after `packet.data_anchor.session_close_at_utc`. The session close instant comes from the exchange calendar (`xnys_session_close_at_utc(D)` for XNYS-listed; `cmes_session_close_at_utc(D)` for futures; `D + 1d 00:00Z` for 24/7 markets), never from a hardcoded `16:00 ET` literal — see `09_soul/axioms/t11_timestamp_semantics_explicit.md` §2.5 (DST sub-contract) and `designDoc/the_timestamp_semantic.md` §4.1 for why. "Report wrote from intraday packet" and "report wrote from post-close packet" are not interchangeable even when both carry the same `session_date_market` field — only the `built_at_utc ≥ session_close_at_utc` test discriminates them. The agent does not write in this pass; the deterministic CLI loops the writer per asset. Override with `--force`.
- `DS pass #2` — `current-market.judgment(D)`: **cross-asset selection pass.** Reads all N L2 reports + `data_layer.fresh` + (optional) priority tree, locks the mainline, names the market stage, and chooses the `key asset spine` (= the subset of the Watchlist that becomes the recap's reading center). This is the "DS first reviews everything, then keeps what is interesting" step. The article body cannot center an asset that did not survive this pass. The selection criterion follows the `Reader end-state` declared in `Positive Contract` (low-add-candidate filter on the Watchlist).
- `DS pass #3` — `current-market.ds(D)`: takes the `judgment` + the deterministically assembled `package` and writes the final PM-facing recap. Writing target is the same `Reader end-state`; this pass does not re-do selection.

`current-market.package(D)` sits between pass #2 and pass #3 as a deterministic carrier — it does not re-do selection. If `judgment` chose a 12-asset spine out of a 71-asset Watchlist, `package` carries those 12 forward exactly, and `ds` writes from those 12. Skipping pass #2 (i.e., assembling a package directly from the full Watchlist and writing) is a graph-level violation even if the resulting markdown looks plausible.

Fail-closed rule:

- `current-market.package` must parse the machine-readable `Package Admission` lines from `current-market.judgment` (`main_reading_assets`, `supporting_detail_assets`, `excluded_or_background_only_assets`) and use those exact admissions
- if any required line is missing, unparsable, or leaves the package with zero admitted assets, the builder must raise an error
- it must not silently fall back to `Key Asset Spine`, the full Watchlist, or any prior candidate set when the judgment artifact is malformed

Detection-side boundary (what an unsigned violation looks like):

- the agent produced `current-market.ds.md` whose frontmatter `session_date_market` (legacy alias `report_date`) does not equal the requested D, even though the file exists on disk
- the agent produced `current-market.ds.md` while `daily_update_status.json` reported a blocking layer for D as `true`
- the agent wrote a recap markdown into the canonical path through ad hoc Python or hand-edit instead of `tradectl research draft-market-observation-ds`
- the recap exists but no upstream `current-market.judgment(D)` artifact was produced — the judgment was implicit in chat or in the package only
- the recap consumed `asset_technical_report(asset, D)` files whose own frontmatter `session_date_market` is older than D for assets in today's observation universe
- the recap appears under a path not declared as the canonical_path of `current-market.ds`

## Time Contract

Before writing any market-timing claim, load the package's structured time block first.

Use this split (post-T11 field names; legacy aliases in parens):

- raw UTC timestamps:
  - exact machine-time facts from data / package inputs (`*_at_utc` suffix)
- `built_at_utc` (legacy alias `generated_at`):
  - when this package, packet, or note was built — physical instant in UTC
- `session_date_market` (legacy alias `report_date`):
  - the market session day this artifact is anchored to, in the asset's own market timezone (`market_tz`); for ETF/listed = ET (XNYS), for futures = CT (CMES), for crypto/fx = UTC
- `data_anchor.session_close_at_utc`:
  - the exact UTC instant of that session's close, sourced from the exchange calendar (handles DST + early-close days correctly); never construct this locally with `datetime.combine(..., 16:00, tzinfo=ET)`
- `session_as_of`:
  - per-asset market-semantic horizon used in package projection
- render wording:
  - phrases like `today`, `post-close`, `上一常规收盘日`, ET/PT-local labels

Rules:

- never use `built_at_utc` (or its legacy alias `generated_at`) as a market close — it's a wall-clock build instant, unrelated to session boundary
- never let the title date or run date replace per-asset `session_as_of`
- when assets disagree on session horizon, say that early and explicitly
- if the package lacks a usable UTC / session block, fail closed instead of improvising time claims
- **UTC-first for all timestamp comparisons.** Every "is X already past close / is Y newer than Z" check (idempotency skips, freshness probes, `must_be_fresh` evaluations, sidecar verification) must read the canonical T11 fields (`packet.data_anchor.session_close_at_utc`, `packet.built_at_utc`, `frontmatter.session_date_market`) and compare in UTC. Never feed a bare calendar-day string like `2026-04-18` into `datetime.combine(..., 16:00, tzinfo=ET)` — see `09_soul/axioms/t11_timestamp_semantics_explicit.md` §2.5 for the DST failure mode this prevents
- **And rendering goes the other way.** Once a comparison or selection is done in UTC, the final wording for the PM may use ET / PT or "post-close" labels for readability, but the underlying decision must already have been made on UTC anchors. Never reverse the order.

## Core Object View

Keep the object boundary explicit:

- `ObservationTickerPool`:
  - the market observation surface for this run
  - built from a fixed baseline plus selected same-day additions
- `MainDriverRead`:
  - what the market is trading now
  - the main transmission chain that explains the cross-asset move
- `Theme / Thesis`:
  - the explanatory framework
  - not the owner of this run's package or final report
- `ObservationRun`:
  - the concrete current-window observation task
  - owns the package and the final market report
- `ObservationPackage`:
  - the prepared writing input for this run
  - not a disguised `theme_update_drafts` object

## Desired Result

The desired result is a complete current-market artifact that makes the active read legible:

- what the market seems to have traded
- which assets confirmed that read
- which assets did not confirm it
- what remains unresolved
- what the reader should watch next

The result should do more than summarize.
It should function as a PM-facing current-market interface that lets the reader:

- grasp the dominant mainline immediately
- feel which stage the tape has reached relative to the last few sessions
- read the key assets as a coherent state map rather than a loose ticker list
- see enough selected technical evidence that the asset state map feels earned, not abstract
- see where the interpretation is still conditional
- know which next question matters most

This skill may conclude that today's move creates evidence for later theme maintenance, but it should still center the current market window rather than convert itself into a standing report workflow.

## Effect-First Design Rule

When extending this workflow, do not start from:

- package section lists
- handoff fields
- prompt wording
- builder / gate sequencing by itself

Start from the final PM-facing note instead.

Ask first:

- what the PM must understand immediately after reading
- which 3-6 assets must become the article's state-map spine
- what still needs to remain conditional
- what next question the note should leave behind

Only after those effects are explicit should you define:

1. what `ObservationIntake` must prepare
2. what upstream `judgment` must settle
3. what `ObservationPackage` should carry downstream
4. what `writer-handoff` should merely check

In this skill, upstream `judgment` should serve the final note by:

- locking the mainline
- naming the market stage
- choosing the key asset spine
- preserving the most important `Not Confirmed` chain
- deciding which materials deserve the package's main reading surface versus supporting detail

`ObservationPackage` is downstream of that judgment. It should carry those choices into writing rather than recreate them.

Keep the reader split explicit:

- single-asset technical reports should still be treated as `trader + PM` dual-reader state objects
- upstream market judgment should be treated as a `PM / macro analyst` convergence object
- the final market note should be treated as the PM-facing cognitive interface

## Completion Standard

This skill is complete only when all of the following are explicit:

- the chosen observation mainline
- the observation window or event window
- the observation basket
- the current judgment
- what confirmed the judgment
- what did not confirm it
- the next watch or next risk
- what stage the market appears to be in relative to the recent path
- which 3-6 assets matter most for understanding today's tape
- what the current analysis still cannot fully resolve
- what the next key question is, not only the next key watchpoint

Accepted outputs:

- PM-facing current market report
- post-close note
- daily recap
- snapshot rewrite
- other current-window market report built from the same observation package

If the note still leaves the reader unable to tell:

- what the market traded
- which assets mattered most
- whether today's move was extension, confirmation, failed reclaim, or still unresolved
- what remains open and why
- what the next key question is

then this skill is not done.

## Boundary Versus `research-theme-report-owner`

Keep the distinction simple:

- `research-current-market-reporter` explains the current market window
- `research-theme-report-owner` maintains the standing theme framework
- this skill may note that today's move strengthened, weakened, or complicated a theme
- once the real task becomes report maintenance, refresh judgment, or framework revision, move first authority to `research-theme-report-owner`

## Mainline, Truth Surface, And Related Sweep

Choose one observation mainline from:

1. the user's explicit request
2. the most clearly implied theme, event line, or asset lens
3. `data/research/themes/current_priority_tree.json` only as fallback

Then read:

1. the user's request and time/window constraints
2. the fixed baseline observation surface for the current window
3. the database observation universe for non-core tradable equities:
   - current holdings from latest account snapshots
   - watchlist
   - theme-related stocks already written in the relevant indexes
4. refreshed external technical reports for the non-core tradable universe, read through the generated indexes first
5. the current `Main Driver`
6. `data/research/themes/index.json`
7. the chosen mainline theme report when one exists
8. relevant snapshots and directly linked local research
9. overlapping local theme reports only when they materially change the read
10. public verification only when the note depends on dated price action, headline sequencing, or public wording

Rules:

- do not override a user-specified mainline with the tree
- keep one mainline and treat overlapping themes as supporting context
- do not choose non-core tradable equities by loose intuition before reviewing the refreshed technical reports
- for asset-centered observations such as `gold`, `oil`, `usd`, `rates`, or `btc`, do one extra asset-cluster sweep across materially overlapping local themes

### Fixed baseline requirement

The fixed baseline is always present before same-day dynamic selection. At minimum it should cover:

- major rates, FX, and equity-index futures
- gold, oil, and volatility
- the next `FOMC`
- important macro release dates in the next 30 days, with the next week treated as the most sensitive watch window

## Observation Basket Contract

Every market observation must define a concrete observation basket before prose drafting.

Before locking the basket, make sure the tracked asset prices for the basket are updated to the latest available observation window. Do not build the report on stale price state when a fresher update should exist.

The basket is not the top-level host object. It should be derived from:

1. the fixed baseline observation surface
2. the selected same-day tradable equity additions
3. the current `Main Driver`

Build the basket in layers:

1. core driver assets
2. first-order confirmation assets
3. disconfirmation or hedge assets
4. physical, flow, or plumbing assets if relevant

The basket is complete only when it can answer:

- what should move if this read is right
- what should confirm the move
- what should fail to confirm if the read is weak

Default examples:

- `iran-hormuz-escalation`:
  - core driver: `Brent`, `/CL`
  - confirmation: `/ES`, `/NQ`, `/ZN`, `XLE`, `XOP`
  - disconfirmation / hedge: `DXY`, `/GC`, `/VX`
  - physical / market-structure: tanker, freight, LNG, shipping disruption
- `gold-monetary-fragmentation`:
  - core driver: `/GC`, `Gold`, `GLD`
  - confirmation: `real yields`, `DXY`, `/ZN`, `UST 10Y/30Y`, central-bank-buying references
  - validation: `GDX`, `BTC` if relevant
- `usd-liquidity-plumbing`:
  - core driver: `DXY`, front-end rates, funding indicators
  - confirmation: `UST 2Y`, `SOFR` or public funding proxies, `/ES`, `/NQ`, `/VX` reaction
  - disconfirmation: stable front-end conditions despite headline stress

Do not write a current-market report without an explicit observation basket.

### Futures naming rule

When the basket includes futures, use slash-root notation by default:

- `/ES`
- `/NQ`
- `/CL`
- `/GC`
- `/ZN`
- `/VX`

If public verification only gives a cash or spot proxy, keep the futures basket explicit and state the public proxy separately.

## Evidence And Verification Standard

Start local-first:

- this run's observation package
- theme report
- relevant snapshots
- linked local research

Add public verification only when:

- the user asked for it
- the note depends on dated price action
- the note depends on headline sequencing
- the note depends on public policy wording

For public verification, prefer the canonical helper in Perplexity `Agent API` mode:

- `python src/tools/perplexity_search.py --api agent --preset fast-search --query "..."`

Verification rules:

- use narrow prompts rather than one blended macro prompt
- ask one narrow question per transmission leg
- use explicit date windows
- keep `confirmed` and `not confirmed` separate
- do not write exact close numbers as facts unless they were actually verified

## Observation Package Rule

Every observation in this skill must use a dedicated observation package before drafting.

Preferred path:

- `data/analysis/market_observation/<theme_id>.package.md`

Execution surface:

- rebuild the package with `python src/tools/assemble_market_observation_package.py [--theme-id <theme_id> ...]`
- draft the final report with `tradectl research draft-market-observation-ds --package "data/analysis/market_observation/<theme_id>.package.md"`

Use this minimal SOP:

1. choose the mainline and lock the observation window
2. make sure the tracked asset prices are updated to the latest available window
3. before any package rebuild that may trigger technical refresh or writer-token spend, confirm the required daily-update layers are latest-ready for this run
4. if the daily-update surface is missing, outdated, or missing deterministic artifacts, trigger the deterministic daily update flow first rather than bypassing the gate by default
5. refresh the non-core tradable equity universe from the database observation universe:
   - current holdings from latest account snapshots
   - watchlist
   - theme-related stocks already written in indexes
6. trigger the external technical-report update flow for that universe
7. review the refreshed technical indexes and the linked full reports
8. choose today's same-day tradable equity additions
9. identify the current `Main Driver`
10. choose the `Theme / Thesis` framework that best explains that driver
11. rebuild the observation package for this run
12. add any ad hoc downstream instructions when major news or drivers materially change framing
13. hand the package to `writer-handoff`
14. only after `ready_to_write`, call `draft-market-observation-ds`

The package should make these explicit:

- chosen mainline
- structured time block with UTC timestamps and per-asset session fields
- fixed baseline observation surface
- database observation universe used for non-core review
- selected same-day tradable equity additions
- current `Main Driver`
- observation basket
- deterministic asset technical references when available
- AI-written per-asset technical summaries when available
- key headline timeline
- local-theme context
- confirmed public anchors
- not-confirmed items
- raw notes or excerpts that explain why the move matters
- ad hoc downstream instructions when major news, catalysts, or transmission drivers materially change the framing, emphasis, or caution needed in the final report

The package should support four downstream effects:

- `reader takeaway`: the reader can identify the dominant mainline quickly
- `asset readability`: the key assets read like a state map
- `tape meaning`: the cross-asset transmission chain becomes legible
- `forward inquiry`: the final note can surface the next key questions, not only the next watchpoints

Under the effect-first rule, that package should not behave like a second judgment layer.
It should mainly carry:

- the settled market judgment
- the admitted key asset spine
- the admitted main-reading materials
- the unresolved questions worth preserving for the final note

If a new package or handoff field does not make one of those downstream effects more reliable, it is probably workflow bulk rather than real report support.

Rules for tradable equities:

- non-core tradable equities should enter the observation flow only after their refreshed technical reports were reviewed
- if a tradable equity enters the package, consume its full canonical technical report via index rather than writing a temporary local substitute inside this skill
- do not re-derive theme-related stocks here when the relevant indexes already define them

Update-status rule:

- for normal market-observation builds, treat latest-ready daily-update status as a hard precondition rather than a soft hint
- when the shared daily-update surface is missing, outdated, or lacks the required deterministic artifacts, run the deterministic update flow first
- if the package rebuild would trigger technical refresh or other token-consuming writer work, do not use `--ignore-update-status` by default
- when forcing that preflight update, keep it deterministic-only unless the user explicitly asked for extra writer work
- use gate-bypass flags only for explicit diagnostic runs or when the user specifically approves a forced run

Next-step handoff:

- once the observation package is prepared, hand it to `writer-handoff`
- pass any ad hoc downstream instructions together with the package rather than leaving them in loose chat context
- `writer-handoff` should return `ready_to_write` or `need_more_detail`
- only after that gate passes should the package and those instructions move into the specific downstream writer/report prompt

Do not draft a market observation from vague memory, loose chat context, or ad hoc note fragments instead of the fixed package.

## Signal-First Technical Block

When the repo has generated asset technical inputs, use them explicitly:

- deterministic packets: `data/knowledge/asset_technicals/signal_packets/`
- AI-written summaries: `data/knowledge/asset_technicals/reports/`
- generated index: `data/knowledge/asset_technicals/index.json`

Rules:

- let deterministic packets provide the technical evidence
- let AI-written asset summaries provide the final interpretation
- let the external technical-report flow own technical report generation
- let this skill trigger refresh and consume the resulting reports through the generated indexes
- do not replace the asset summary with copied indicator dumps
- if an asset summary is missing, keep the deterministic packet visible and mark the narrative layer as pending

## Writing Standard

Write the output as a formal market note, not as process commentary.

Default posture:

- direct
- analytical
- decision-facing
- written for a PM, not for workflow audit

The reader should feel they received a complete market read, not a partial package summary or a workflow-shaped memo.

Do:

- lead with the current judgment
- explain what the market priced
- tie the theme to actual asset behavior
- show what confirmed the read
- show what did not confirm it
- explain why the move matters now
- end with what to watch next

Do not:

- compare to an earlier draft unless the user explicitly asks
- narrate your research process
- dump source summaries
- write chatty transitions
- turn the note into a full theme report
- omit the key assets that make the observation believable

## Preferred Output Shape

For most market observations, use:

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

## Failure Signals

Treat these as signs this skill failed:

- the note reads like a standing theme report instead of a market-window interpretation
- the note never states the current judgment clearly
- confirming and disconfirming assets are not explicit
- the mainline is silently replaced by related-theme context
- unconfirmed public facts are written as confirmed anchors
- the note jumps from one day's move to a regime conclusion without evidence
- the package requirement is skipped or treated as optional
- package or gate language becomes more prominent than the market judgment itself

## Style Rules

- Write in Chinese by default unless the user requests another language.
- Keep English market terms when they are the clearest expression.
- Use natural analyst prose, not literal translation.
- Prefer precise statements over dramatic phrasing.
- Keep the tone formal enough that the note can be read by another PM without verbal explanation.

## Guardrails

- Do not let the tree override a user-specified mainline.
- Do not write a market observation without an explicit observation basket.
- Do not write `today`, `post-close`, or `latest close` as if they were universal market truth without checking the package's UTC/session block first.
- Do not replace per-asset `session_as_of` with one shared calendar date when mixed-session assets are present.
- Do not skip the fixed baseline observation surface before selecting same-day additions.
- Do not pick non-core tradable equities before reviewing their refreshed technical reports.
- Do not bypass the daily-update gate by default when the run would consume technical-refresh or writer tokens.
- Do not blur confirmed and unconfirmed public facts.
- Do not turn one day of price action into a regime conclusion without evidence.
- Do not write exact market closes as verified facts unless they were actually verified.
- Do not let related-theme context replace the mainline.
- Do not reuse finalized theme-report structure when the task is a market note.
- Do not treat the observation package as optional.
- Do not regenerate theme-related stock membership here when the index already provides it.
- Do not let builder/gate detail take over the skill contract; keep execution support thin unless it materially improves the output artifact.

## Example Triggers

- “这个 theme 今天市场怎么走”
- “写个（今天 当前 盘中 盘后）市场报告”
- “写一个盘后 note”
- “今天市场到底在交易什么”
- “从 Iran/Hormuz 这条线看今天收盘”
- “根据 gold 这条 theme 写个 market observation”
