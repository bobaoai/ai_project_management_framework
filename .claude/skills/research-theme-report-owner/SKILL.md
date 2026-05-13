---
name: research-theme-report-owner
description: "Upstream owner workflow for macro theme report maintenance. Use when a request is already recognized as theme maintenance and someone must review recent materials, judge recency and sufficiency, define the report pass, choose package scope, add local writer direction, and decide whether to route downstream to `research-theme-knowledge-and-package-curator`, `writer-handoff`, and `research-theme-priority-updater`."
---

# Theme Report Owner

## What This Skill Owns

Use this skill only after the task is already recognized as `theme maintenance`.

When `routing-task-mode-router` is available, it should route requests here only after matching the task to theme maintenance rather than to market observation, single-stock analysis, or portfolio decision.

This skill is the upstream owner of one theme-report pass. It owns the judgment that decides:

- what the user is actually asking for
- whether the current materials are recent enough
- whether the current materials are sufficient enough
- whether the pass is broad refresh, narrow update, validation pass, or combined content-plus-priority work
- what should go into the package
- what the downstream writer should emphasize or avoid

This skill is the default top-level `preferred_skill` for theme maintenance.

## Theme Layer Hierarchy

Inside this repo, `theme` is not one flat bucket.

Use this working hierarchy:

- top-level themes should stay few
- most durable theme objects should be `regional economic` themes or `industry` themes
- `thesis` objects should remain the finer-grained judgment layer beneath those themes

Interpret the layers like this:

- `top-level theme`:
  - cross-asset or cross-region regime layer
  - changes portfolio routing across many sectors, assets, or countries
  - should be rare
- `regional economic theme`:
  - country, region, or policy-economy branch with enough recurrence to deserve ongoing maintenance
  - examples include country normalization, regional energy shock, or regional liquidity structure
- `industry theme`:
  - sector, value-chain, or capability stack branch with enough repeated evidence to support standing maintenance
  - examples include datacenter power stack, modern warfare capability stack, or autonomy platform economics
- `thesis`:
  - durable but narrower judgment
  - may later fold into an existing theme, seed a regional/industry theme, or stay thesis-only

Default promotion rule:

- do not jump from a promising thesis cluster straight to a new top-level theme
- first ask whether the evidence really supports a `regional economic` or `industry` theme instead
- only promote to a new top-level theme when the object clearly governs many regional/industry branches rather than just one sleeve

## Desired Result

The desired result is not merely "a theme got updated."

The desired result is that one theme-report pass becomes explicitly governed before downstream work starts. By the time this skill is done, downstream workers should no longer need to guess:

- what kind of pass this is
- whether the latest evidence is good enough
- which materials matter most
- whether knowledge maintenance is needed before report writing
- whether priority work is part of the request
- what the writer should optimize for

## Reader End-State

After this skill is done, the next downstream reader (`research-theme-knowledge-and-package-curator` in either mode, sometimes followed by `writer-handoff` + `research-theme-report-reviewer` + `research-theme-priority-updater`) should newly be able to:

- Execute the chosen content leg without guessing `pass_type`, `scope`, or `recency_status`
- Assemble the package from a `selected_materials` set that has already been coverage-checked against the recent research window
- Write from explicit `writer_direction` items where each item ideally ships with its own `reader_end_state` (one sentence on what the PM should newly be able to do after reading the section that consumes this directive)
- See an explicit precedence rule when a `writer_direction` item is contradicted by a later `SCENARIO CORRECTION` / `THESIS INTEGRATION` entry, so Writer does not have to make silent framing choices
- Route between content / writer / reviewer / priority steps without ambiguity (the `selected_downstream_route` field is dispositive)

If the next reader still has to merge structural directives with this-round evidence corrections by hand, or has to guess which directive overrides which, this skill is not done.

_Validation pending (retrospective follow-up)._ This Reader End-State section was
added 2026-04-24 during the `critic_pipeline_20260424` retrospective (Item 1). The
language about `writer_direction` items ideally shipping with per-item
`reader_end_state` foreshadows Item 3 (owner.json schema split into
`structural_directives` / `this_round_evidence_anchors` / `precedence_when_conflict`) —
that schema change is in backlog, not executed. **Next time this skill is invoked for
a fresh theme report pass, observe whether the downstream `research-theme-knowledge-and-package-curator`
actually executes the route without re-asking the owner for clarification.** If
clarification was needed, update retrospective Item 1 with the gap; if not, close
Item 1 and consider promoting Item 3 from backlog to active.

## Time Discipline

When this skill says materials are `recent` or `sufficient`, keep these time layers separate:

- research evidence window:
  - message dates, snapshot dates, publication dates
- raw market-data UTC time:
  - exact timestamps carried by technical or market artifacts
- technical session semantic:
  - per-asset `session_as_of` / session label
- artifact audit time:
  - `generated_at`

Rules:

- do not compress the layers above into one vague idea of `latest`
- do not let `report_date` replace raw UTC or `session_as_of`
- if a package mixes research, macro, and technical evidence, state the relevant time window for each source family explicitly

## Completion Standard

This skill is complete only when all of the following are explicit:

- the target `theme_id`
- the pass type for this round
- the current scope of the pass
- the recency judgment
- the sufficiency judgment
- the selected downstream route
- the local writer-direction notes when writing is part of the task

Accepted downstream route shapes:

- `research-theme-knowledge-and-package-curator` only
- `research-theme-knowledge-and-package-curator` then `writer-handoff` then `research-theme-report-reviewer`
- `research-theme-knowledge-and-package-curator` then `research-theme-priority-updater`
- `research-theme-knowledge-and-package-curator` then `writer-handoff` then `research-theme-report-reviewer` then `research-theme-priority-updater`
- `need_more_material` when the pass cannot responsibly continue yet

Whenever the pass produces a `theme.report.ds`, the route must include `research-theme-report-reviewer` between writing and merge. The owner only re-enters the loop on a `needs_rewrite` verdict (or when reviewer reports a `package`-root-cause finding); `accept_as_is` and `accept_with_revisions` route back to `research-theme-knowledge-and-package-curator`. See `designDoc/research_00_report_reviewer_pattern.md`.

If those decisions are still implicit, this skill is not done.

## Pass Types

Use one explicit pass type for each owner run:

- `report_refresh`
- `report_delta_scan`
- `report_gap_review`
- `theme_candidate_discovery`
- `seed_theme_brief`

Interpret them like this:

- `report_refresh`: the existing report needs a substantive refresh against newer material
- `report_delta_scan`: inspect recent news or recent materials and decide whether they actually change the current report
- `report_gap_review`: inspect whether the current report is missing an important leg, stale branch, verification block, or unresolved contradiction
- `theme_candidate_discovery`: use the current report, current materials, and current user request as the discovery anchor, and propose theme candidates implied by the evidence even when they are not merely adjacent to the current mechanism or scenario map
- `seed_theme_brief`: the user points to a possible theme and wants an initial framing brief before deciding whether it deserves fuller theme maintenance

Important boundary:

- this skill may do `report-anchored theme discovery`
- this skill should not silently become a universal `global theme ideation` surface
- when it does discovery, it should usually recommend `regional economic` or `industry` themes before considering a fresh top-level theme

If the request is really "scan the broad news flow and invent new themes in general," do not pretend that is ordinary theme maintenance.

## Primary Truth Surfaces

Read these first:

- the user's request and any time/window constraints
- `data/research/themes/metadata/<theme_id>.json`
- `data/research/themes/reports/<theme_id>.md`
- `data/research/theme_update_drafts/<theme_id>.json` when it exists
- the latest relevant local research artifacts already linked to the theme

Read these when needed:

- `data/research/themes/current_priority_tree.json` when the request may affect priority or when the user did not specify which active theme branch should lead
- related local theme reports and metadata when overlap can change the meaning of the current update
- package or technical artifacts that expose raw UTC timestamps and per-asset session fields when the pass depends on market timing

Same-theme backbone rule:

- for same-theme writing, the only backbone document is the latest finalized `themes/reports/<theme_id>.md`
- treat `theme_update_drafts/<theme_id>.ds.md` as review-stage output and merge candidate, not as a second backbone

## Required Outputs

This skill should produce an explicit owner decision package in the handoff, log, or routing note. At minimum it must contain:

- `theme_id`
- `pass_type`
- `scope`
- `recency_status` (includes the coverage-check audit line; see `Source Coverage Check`)
- `sufficiency_status`
- `selected_materials` or package-selection direction (includes `internal_market_state_reference` when scope touches asset prices, equity dispersion, rates / FX, or live market regime)
- `writer_direction` when relevant
- `next_step`

## Node Bindings

This skill owns the following node in `data/runtime/artifact_graph.yaml`:

- `theme.owner_decision(theme_id, D)` — L3 owner decision artifact for one theme-maintenance pass; canonical path `data/research/theme_update_drafts/<theme_id>.owner.json`

This skill consumes:

- `theme.knowledge(theme_id)` (must_be_fresh) — the standing theme report content under `data/research/themes/reports/<theme_id>.md`
- `themes.metadata(theme_id)` (must_be_fresh)
- `themes.current_priority_tree` (optional_overlay)
- `asset_technical_report(asset, D)` (optional_overlay) for asset-centered themes such as `gold`, `oil`, `usd`, `rates`, `btc`
- `current-market.ds(D)` (optional_overlay) — the latest internal current-market judgment; consumed during the coverage check when scope touches asset prices, equity dispersion, rates / FX, or live market regime, and surfaced into the package via `selected_materials.internal_market_state_reference`
- `data/research/messages_index.jsonl` (must_be_fresh, scan-only) — the candidate set for the window scan inside `Source Coverage Check`

Downstream nodes that depend on this skill's output:

- `theme.package(theme_id, D)` owned by `research-theme-knowledge-and-package-curator` (must_be_fresh edge into `theme.owner_decision(theme_id, D)`)

Builder kind: `ai_writer`

This skill does NOT own:

- `theme.knowledge` content edits (that is `research-theme-knowledge-and-package-curator` knowledge mode)
- `theme.package` assembly (that is `research-theme-knowledge-and-package-curator` report mode)
- `theme.report.ds` final prose (that is `research-theme-knowledge-and-package-curator` + writer gateway)
- `themes.metadata` direct edits (that is `research-theme-priority-updater`)
- `themes.current_priority_tree` regeneration (that is `research-theme-priority-updater`)

Detection-side boundary (what an unsigned violation looks like):

- a downstream `theme.package(theme_id, D)` was assembled without a corresponding `theme.owner_decision(theme_id, D)` artifact existing for D
- the owner decision exists but `pass_type` is empty, vague (`general update`), or mixes content + priority work without specifying ordering between the two
- `recency_status` and `sufficiency_status` are not stated, so downstream workers must guess whether material set is current and complete enough
- the owner decision was produced from chat reasoning only and was never persisted; downstream workers cannot verify which scope decision they are executing
- discovery-mode passes (`theme_candidate_discovery`, `seed_theme_brief`) silently jumped to top-level theme candidates without first asking whether a `regional economic` or `industry` theme would better fit
- this skill silently retook ownership over `themes/metadata/<theme_id>.json` or `themes/current_priority_tree.json` instead of routing that work to `research-theme-priority-updater`
- the owner_decision was produced without running `Source Coverage Check`: `recency_status.note` does not record a window scan, and the package later turns out to have missed an in-window archive item that materially changes the writer's framing

Typical `writer_direction` items:

- current central contradiction
- biggest directional change
- framing to emphasize
- framing to avoid
- whether the report should read as framework refresh, path update, or validation pass

For discovery-oriented pass types, also make these explicit:

- `recent_change_summary`
- `does_current_report_need_update`
- `theme_candidates`
- `candidate_level`: adjacent evidence, thesis_only, regional_theme_candidate, industry_theme_candidate, or rare top_level_theme_candidate
- `recommended_action`

## Downstream Routing Contract

Route by authority, not by keyword overlap:

- use `research-theme-knowledge-and-package-curator` for content maintenance, evidence maintenance, thesis/scenario structure work, package assembly, and finalized theme-report editing
- use `writer-handoff` only after package sufficiency is established or when the downstream task is explicitly package-driven writing
- use `research-theme-report-reviewer` immediately after a DS-written theme draft (`<theme_id>.ds.md`) exists and before any merge into the standing report; the reviewer's verdict (`accept_as_is` / `accept_with_revisions` / `needs_rewrite`) decides whether the merge proceeds, the maintainer revises, or this skill re-decides scope
- use `research-theme-priority-updater` for `priority_bucket`, `priority_rank`, `preferred_skill`, status, and tree refresh
- use `research-theme-bootstrapper` Stage A when the request creates a NEW theme (PM-driven OR forwarded from `research-theme-discovery-scanner`) and the candidate's overlap with existing themes must be explicitly arbitrated before metadata is written; see `New Theme Bootstrapping (round-1 + round-2)` below

## New Theme Bootstrapping (round-1 + round-2)

When the request is **theme creation** (not theme update), this skill operates in TWO rounds with `research-theme-bootstrapper` in between. Confusing the two rounds is a common failure pattern; keep them strictly separated.

### Round-1 — "is this candidate worth opening at all"

Trigger: any of:

- PM-driven: "请帮我开一个 theme on X" arrives directly through `routing-task-mode-router`
- AI bottom-up: a `research-theme-discovery-scanner` candidate arrives via PM ("接受 candidate <slug>，往下走")

In round-1 this skill does NOT call `research-theme-bootstrapper`. It produces a `round_1_verdict`:

| Round-1 verdict | What it means | Next step |
|---|---|---|
| `worth_arbitrating_via_bootstrapper` | candidate clears the "is this even a theme-shaped question" bar | route to `research-theme-bootstrapper` Stage A |
| `defer_as_thesis_only` | the candidate is real but should live as a `thesis_note` under an existing theme, not as a new theme | route to `research-thesis-drafter` (with parent theme_id) |
| `not_worth_opening` | candidate is too narrow / educational / regional / one-off (Rule 41 dedicated-skill admission) | record decision; do NOT route forward |
| `need_more_evidence` | candidate is interesting but the supporting evidence in archive is too thin to even arbitrate | request the user to wait for more material or ask `ingestion-research-archive-operator` for a wider sweep |

### Round-2 — "given bootstrapper's proposal, which negotiation outcome do we execute"

Trigger: `research-theme-bootstrapper` Stage A has produced `bootstrapper_proposal.json` + `bootstrapper_proposal.summary.md`.

In round-2 this skill reads the proposal, OPTIONALLY shows the `.summary.md` to the PM for explicit confirmation, then writes `data/research/theme_candidates/<scan_id>/bootstrap_arbitration_decision.json`:

```json
{
  "scan_id": "scan_2026_04_19_1400Z",
  "candidate_slug": "modular_nuclear_capex_chain",
  "recorded_at_utc": "2026-04-19T15:10:00Z",
  "chosen_outcome": "narrow_existing_then_admit",
  "chosen_outcome_overrides_bootstrapper_recommendation": false,
  "pm_explicit_confirm": true,
  "pm_chat_message_id": "<message-id-or-stable-anchor>",
  "rationale": "<one or two sentences. If chosen_outcome differs from bootstrapper.recommended_outcome, prefix rationale with [OVERRIDE] for calibration tracking>",
  "proposed_existing_theme_edits": "<echo from bootstrapper.proposed_existing_theme_edits_if_any, possibly modified by PM>",
  "proposed_new_theme_skeleton": "<echo from bootstrapper.proposed_new_theme_skeleton_if_any, possibly modified by PM>"
}
```

Hard rules for round-2:

- `pm_explicit_confirm: true` is REQUIRED before bootstrapper Stage B will execute (V01 verifiability). Do NOT decide round-2 silently.
- `pm_chat_message_id` is REQUIRED for traceability — point to the chat turn where PM said "yes, do it" (or its equivalent).
- If `chosen_outcome = carve_out_from_existing`, the next step is bootstrapper Stage B Phase 4a (dry-run), NOT direct execution. PM will get a `bootstrapper_carve_out_diff.json` to review and must round-trip ONE MORE time with `chosen_outcome: carve_out_from_existing_confirmed` + `observed_at_utc`.
- If `chosen_outcome = subordinate_to_existing`, bootstrapper will raise `subordinate_executor_not_implemented`. The recommended workaround is to re-run round-2 with `chosen_outcome = merge_into_existing` AND separately invoke `research-thesis-drafter` to write the candidate as a sub-thesis.
- When `chosen_outcome` differs from `bootstrapper.recommended_outcome`, prefix `rationale` with `[OVERRIDE]`. The harness tracks override frequency; if overrides exceed 30% of decisions in a quarter, the bootstrapper's deterministic dimension weights need calibration (M01 closed-loop calibration).

### Round-1 vs Round-2 boundary (do not collapse)

A common failure pattern is to "decide both rounds at once" — i.e., the owner sees the PM-driven request and immediately writes a `chosen_outcome` without going through bootstrapper Stage A. This is wrong because:

- bootstrapper's similarity scan is the only place where overlap with ALL existing themes is checked dimensionally
- round-2 cannot be PM-confirmed in a meaningful way if PM has not seen the proposal first

If a request is genuinely small and PM is already certain about the outcome ("just admit it, I don't need the bootstrapper to scan"), do NOT bypass bootstrapper. Instead, run round-1 with `worth_arbitrating_via_bootstrapper` and let bootstrapper produce a thin proposal — this preserves the audit trail (`bootstrapper_proposal.json` exists for every new theme) and makes future calibration possible.

If the request includes both content work and priority work:

- do the content leg first
- do the priority leg second

If scenario/thesis structure is stale enough that report writing would be built on weak abstractions:

- route `research-theme-knowledge-and-package-curator` through `knowledge mode` first
- then run a separate `report mode` pass

## Ownership Boundary

This skill owns upstream authority. It should explicitly own:

- request interpretation
- material review
- recency judgment
- sufficiency judgment
- report scope
- writer framing

This skill does not own:

- full downstream content maintenance execution
- final PM-facing prose generation
- generated tree/index editing

Do not use this skill as the top-level router for every analysis request that merely mentions a theme. A theme overlay inside `single-stock`, `news`, or `portfolio` work does not by itself move the whole task here.

## Source Coverage Check (Pre-Sufficiency Step)

Before deciding `sufficiency_status`, run an explicit `source coverage check`. This step exists because the downstream `research-theme-report-reviewer` can detect when a draft cited the wrong sources, but cannot reliably detect when the package failed to admit a relevant source that exists in the archive but was never selected. That gap is structurally upstream of the reviewer's contract and must close here.

The check has three steps:

1. `Window scan`. Enumerate `data/research/messages_index.jsonl` for every entry whose `received_at` (or equivalent date field) falls inside `recency_status.research_window`. List each candidate's `id` + `subject` + `sender_name` + `source_collection`. Use chronological order so newer items are easy to spot.

2. `Topic relevance triage`. For every candidate, decide one of:
   - `selected_core` → admit into `selected_materials.core_recent_research_ids`
   - `selected_boundary` → admit into `selected_materials.boundary_reference_research_ids`
   - `still_relevant_backbone` → admit into `selected_materials.still_relevant_backbone_research_ids`
   - `out_of_scope_acknowledged` → record as deliberately excluded, with one-sentence reason in `recency_status.note`
   - `archive_only` → deliberate exclusion, no record needed

3. `Coverage gap log`. Any candidate marked `selected_core` / `selected_boundary` / `still_relevant_backbone` that is NOT yet in the prior owner_decision is a `coverage gap`. The new owner_decision must close every such gap or explicitly justify exclusion in `recency_status.note`. If the prior owner decision was already merged into a finalized report and the gap surfaces only now, this round is a `report_refresh` even if the user requested only a `report_delta_scan`.

`Internal cross-mainline references`. For any theme whose scope touches asset prices, equity dispersion, rate / FX state, or live market regime, also include `data/analysis/market_observation/current-market.ds.md` (the latest internal current-market judgment for the theme's session date range) via a new field `selected_materials.internal_market_state_reference`:

```json
"internal_market_state_reference": {
  "path": "data/analysis/market_observation/current-market.ds.md",
  "purpose": "Coherence anchor — the writer must not draft equity / asset-state claims that contradict this internal current-market judgment. Treat as live snapshot the PM is already carrying; do NOT cite as evidence (it is our own internal write-up, not external research)."
}
```

The package builder renders this as a sub-section under the Boundary References tier, NOT as a primary source card. The writer reads it for coherence calibration only.

`Failure signals for this step`:

- The package contains research IDs whose latest dates are >7 days behind `recency_status.research_window` upper bound, with no `recency_status.note` explaining why newer items in the same window were not admitted.
- The reviewer's verdict comes back `accept_with_revisions` or `needs_rewrite` and the root cause is `package`-level (e.g., "draft used stale source X while archive item Y from the same window was not selected"). When this happens twice on the same theme inside one quarter, the coverage check is being skipped and should be reinforced rather than re-blamed downstream.
- The theme touches equity / asset state but `selected_materials` does not include any `internal_market_state_reference`.
- The owner relies entirely on `themes.metadata.linked_research_ids` as the candidate set without doing the window scan against `messages_index.jsonl`. `linked_research_ids` is a slow-moving registration record; it does not guarantee coverage of the most recent window.

When this check passes, record one short audit line in the owner JSON's `recency_status.note` describing what was scanned, what was admitted, and what was deliberately excluded with reason.

## Sufficiency Rule

Before body drafting begins anywhere downstream, this skill should make the sufficiency judgment legible.

The package or evidence set must be strong enough to support:

- the current core judgment
- the background context required to understand that judgment
- what the market is pricing now when the topic is market-facing
- the key drivers and transmission path
- confirmed anchors versus not-confirmed items
- key debates, counterarguments, and unresolved disagreements
- scenario path or what happens next
- portfolio fit or action framing
- key risks and monitoring items

If one or more of those blocks is missing, return `need_more_material` or route the downstream worker to broaden the package. Do not let the downstream writer absorb those gaps silently.

Time-window sufficiency rule:

- if the package cannot clearly state which research window, which market UTC anchors, and which technical session horizons support the pass, it is not sufficient yet

## Method Guidance

Prefer these working rules:

- choose the observation mainline from the user's explicit request first
- if the user did not specify it, use the priority tree as fallback routing context rather than as override authority
- do a related-theme sweep before approving a substantive rewrite
- for asset-centered themes such as `gold`, `oil`, `usd`, `rates`, or `btc`, do an extra asset-cluster sweep across overlapping local themes
- if the user asks for public-market verification in a defined window, use narrow external checks only for the specific missing leg
- keep `writer-handoff` as a standalone downstream writer step rather than merging writing authority back into content maintenance
- for discovery-oriented passes, prefer opening `regional economic` or `industry` themes before escalating something into a fresh top-level theme
- when several related theses cluster around one country, policy regime, sector, value chain, or capability stack, treat that as evidence for a middle-layer theme candidate first

When the user asks:

- "summarize the recent news around this report"
- "tell me whether anything important changed for this report"
- "see if there is a theme candidate worth opening from this report"
- "here is a possible theme x, think through it"

default to treating those as owner-level pass framing questions first, not as immediate downstream writing requests.

## Failure Signals

Treat these as signs that this skill has not been completed correctly:

- downstream workers still need to guess scope
- downstream workers still need to guess whether materials are current enough
- the task silently mixes content work and priority work without a clear ownership order
- the writer receives a package but no directional brief even though the pass clearly changed direction
- the owner says materials are sufficient but cannot state what judgment, debate, or action frame the package should support
- the same theme returns from the reviewer twice in one quarter with a `package`-root-cause finding (stale or missing source admitted to the owner_decision) — that is a coverage-check skip pattern, not a recurring writer failure

## Guardrails

- Do not hand-edit `index.json` or `current_priority_tree.json`.
- Do not maintain a parallel content-maintenance workflow here that drifts from `research-theme-knowledge-and-package-curator`.
- Do not let downstream workers retake top-level authority over report scope, material sufficiency, or writer framing once this skill has already decided them.
- Use `research-theme-report-owner` as the preferred top-level owner name in new guidance.

## Example Triggers

- “update this theme report”
- “refresh the current themes from local research”
- “整理一下当前 themes 和 report”
- “把这个 theme 更新一下顺便看看要不要调 priority”
