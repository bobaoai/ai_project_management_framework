---
name: operation-portfolio-decision
description: "Turns sufficiently stable upstream interpretation into portfolio-manager decisions using policy limits, portfolio state, active themes, technical state, account review context, and candidate assets. Use when the user asks for rebalance implications, hedge priority, target-book direction, reduce/add/hold choices, debate before action, or execution-preview style portfolio decisions."
---

# Portfolio Decision

## What This Skill Does

Use this skill when the task has already moved from interpretation into portfolio-manager decision work.

When `routing-task-mode-router` is available, it should send requests here only after matching the task to book-level action rather than to first-pass market or ticker interpretation.

This skill is for:

- rebalance framing
- hedge priority
- add / reduce / hold / close judgment
- target-book direction
- debate before action
- execution-preview style planning

This skill is not the primary workflow for:

- standing theme-report maintenance
- current-market observation
- single-name interpretation before portfolio consequences are considered
- archive curation or research ingestion

## Desired Result

The desired result is a portfolio-manager decision artifact that makes these things explicit:

- what the current portfolio problem or opportunity is
- what the current interpretation means for the existing book
- what constraints the book must obey
- which assets or exposures should be opened, added, reduced, closed, held, or watched
- why those actions are justified now
- how the book should be positioned
- how the book should be defended
- what should be done first
- what risks block or weaken the action
- what the next execution or monitoring step should be

This skill begins only after upstream interpretation is stable enough that the task is truly about the book.

## Main PM Questions

The center of gravity for this skill is not generic recommendation language.

It should answer questions closer to:

- what does this mean for my current book
- how should I position
- how should I defend
- what should I do first

If the artifact cannot answer those questions, it is still too upstream.

## Pass Types

Use one explicit pass type for each operation-portfolio-decision run:

- `book_defense`
- `rebalance_trim_add`
- `hedge_priority`
- `wait_no_action`
- `offense_build`

Interpret them like this:

- `book_defense`: reduce fragility, defend the book, and cut the exposures most likely to hurt if the active shock continues
- `rebalance_trim_add`: decide what to trim, what to add, and in what order
- `hedge_priority`: decide which risk should be hedged first and why
- `wait_no_action`: decide whether the correct PM action is to wait, hold, or stay watchlist-only
- `offense_build`: decide how to add risk after interpretation is already stable enough to support offense

If the task asks for a book answer but never clarifies which of these PM problems it is solving, the decision contract is still too vague.

## Completion Standard

This skill is complete only when all of the following are explicit:

- account scope
- policy envelope or governing constraints
- current portfolio state
- current market regime
- active themes that matter for the decision
- candidate assets or current holdings under debate
- current book impact
- pass type
- proposed action frame
- action priority
- key blockers or risks
- next step
- per scenario-anchored action: scenario_id + `(pm_conviction, scenario_role, market_state)` triplet + `pricing_snapshots[-1]` reading + handling of parent thesis's `unresolved_objection_evidence_ids`; silent ignore of any of the four is forbidden

Accepted outputs:

- portfolio decision package
- PM-facing debate report
- target-book proposal
- execution preview

If the output still feels like upstream interpretation without a real decision surface, this skill is not done.

## Node Bindings

This skill owns the following nodes in `data/runtime/artifact_graph.yaml`:

- `portfolio.judgment(D)` — L3 judgment object that locks debate frame, pass type, and book impact view
- `portfolio.package(D)` — L3 writer-facing decision package
- `portfolio.pm_action(D)` — L4 formal action plan (add / reduce / hold / hedge with explicit levels and pass type in frontmatter); canonical path `data/analysis/portfolio_decision/pm_action_<D>.md`
- `portfolio.pm_action_review(D)` — L4 cross-day review of a prior `pm_action(D-N)`; canonical path `data/analysis/portfolio_decision/pm_action_review_<D>.md`

This skill consumes:

- `account.snapshot(D)` (must_be_fresh)
- `current-market.judgment(D)` (must_be_fresh)
- `single_stock.judgment(ticker, D)` (optional_overlay) for each ticker under debate
- `themes.current_priority_tree` (optional_overlay)
- `scenario_note(scenario_id)` (must_be_fresh) for each scenario whose triplet drives an action; `lifecycle_stage="active"` AND `freshness_state="fresh"`
- `thesis_note(thesis_id)` (must_be_fresh) for each scenario's `parent_thesis_id`; `adversarial_review_log[].unresolved_objection_evidence_ids` MUST be read so unresolved objections can be handled
- for `pm_action_review`: prior `portfolio.pm_action(D-N)` (must_exist_unchanged_since); the reviewed action plan must exist and its content hash must match what was hashed when this review reads it

Builder kinds:

- `portfolio.judgment`, `portfolio.pm_action`, `portfolio.pm_action_review`: `ai_writer`
- `portfolio.package`: `composite` (`tradectl portfolio package` + sufficiency gate)

Pass type (frontmatter on `pm_action`):

- one of `book_defense | rebalance_trim_add | hedge_priority | wait_no_action | offense_build`
- the pass type chosen here governs `pm_action_review(D')` framing later

Detection-side boundary (artifact-level violation, look at the resulting file):

- D1. the agent produced an add / reduce / hold table inline in chat or inside a recap markdown, but no `pm_action_<D>.md` artifact exists at the canonical path
- D2. `pm_action_<D>.md` exists but lacks an explicit pass type in frontmatter
- D3. `pm_action_<D>.md` claims action levels (add at X, reduce below Y) but the upstream `current-market.judgment(D)` and `account.snapshot(D)` it depends on are stale or missing for D
- D4. a cross-day review markdown was produced without reading the prior `pm_action(D-N)` file; the review is opinions on memory rather than a backtest against a recorded plan
- D5. a review modifies the prior `pm_action(D-N)` file instead of producing a new `pm_action_review(D)`; `must_exist_unchanged_since` was violated
- D6. the artifact uses execution-language (specific add lots, hedge sizing) without a stable underlying judgment node; the decision surface was skipped
- D7. an action references a thesis without naming the scenario_note that anchors it; the (pm_conviction, scenario_role, market_state) triplet is the decision unit, not the thesis (charter §VIII)
- D8. a scenario_note is named but its `(pm_conviction, scenario_role, market_state)` triplet and most-recent `pricing_snapshots[-1]` reading are not surfaced in the artifact; the reader cannot tell why this scenario produces this action at this market price
- D9. the parent `thesis_note.adversarial_review_log[].unresolved_objection_evidence_ids` is non-empty AND the action does not address those objections (cite as supporting / acknowledge as deferred-acceptable with rationale / explicitly override with rationale); silent ignore is the failure mode this gate exists to prevent (charter §VIII 暴露未决反驳)

## First Authority

The first authority here is `portfolio manager`.

This mainline turns:

- portfolio state
- risk constraints
- active themes
- technical state
- current market interpretation

into:

- debate
- decision
- target book
- execution preview

If the task is still mainly trying to understand one theme or one ticker, stay in the upstream mainline first.

In PM language, this means turning interpretation into:

- positioning
- sizing
- hedge priority
- action sequencing

## Boundary Versus Other Mainlines

Keep these boundaries explicit:

- versus `research-single-stock-analysis`:
  - `research-single-stock-analysis` decides what one name means
  - `operation-portfolio-decision` decides what the book should do with that meaning
- versus `research-current-market-reporter`:
  - `research-current-market-reporter` explains what the market traded
  - `operation-portfolio-decision` decides what to do about that market read in the portfolio
- versus `research-theme-report-owner`:
  - `research-theme-report-owner` maintains the standing theme framework
  - `operation-portfolio-decision` consumes active theme state as one decision input

Do not let this skill silently retake upstream interpretation when the real missing step is still theme or stock analysis.

## Primary Truth Surfaces

Read these first:

- the user's request
- the active policy envelope
- the current portfolio decision package
- current holdings and exposure state
- active themes from the current priority tree and related theme package/report surfaces
- candidate assets and their current technical state
- recent account review context when available

### Freshness and PM Review Queue Gate

Per charter §VII, operation-portfolio-decision candidate set is hard-filtered by lifecycle and freshness. Per charter §II, PM acknowledgement is a visible review state, not a hard precondition for AI-verified / AI-proof thesis or scenario use.

Hard filter applied BEFORE any package / debate / decide pass:

- For every `thesis_note` candidate considered: include only if `lifecycle_stage="active"` AND `freshness_state="fresh"`. `due` and `stale` thesis are excluded.
- For every `scenario_note` candidate considered: include only if `lifecycle_stage="active"` AND `freshness_state="fresh"`. `draft`, `due`, and `stale` scenarios are excluded.
- For every theme metadata candidate considered: include only if `status="active"` AND `freshness_state="fresh"`. D.6.5 makes `freshness_state` required on themes/metadata, so missing freshness is a contract violation, not a silent fresh default.
- For thesis / scenario objects, independent AI proof is required for use when PM acknowledgement is missing. AI proof means linked evidence_record(s) have `ai_verified=true` from an independent research-evidence-reviewer or PM review entry. Objects with neither PM acknowledgement nor independent AI proof are excluded as `excluded_due_to_no_independent_review`.

PM review queue applied AFTER the hard filter:

- A thesis with non-empty `pm_acknowledged_by[]` is `pm_review_state="acknowledged"`.
- A thesis with empty `pm_acknowledged_by[]` but at least one linked evidence_record with `ai_verified=true` is `pm_review_state="pending_pm_review"`; it may be used, but the package must count it and remind PM to review.
- A scenario with `pm_acknowledged=true` is `pm_review_state="acknowledged"`.
- A scenario with `pm_acknowledged=false` but evolved_from_evidence / linked evidence includes `ai_verified=true` is `pm_review_state="pending_pm_review"`; it may be used, but the package must count it and remind PM to review.

When the package builder excludes a candidate due to staleness or missing independent review, the exclusion MUST be visible in the package. When it includes a candidate pending PM review, the package MUST include `pm_review_queue_summary` with counts and ids, for example `thesis_pending_pm_review_count`, `scenario_pending_pm_review_count`, and the corresponding id lists. Silent omission is the failure mode this gate exists to prevent.

AI proof lookup rule:

- Thesis AI proof is present when `data/research/evidence_ledger/**/<evidence_id>.json` contains at least one evidence_record with `ai_verified=true` and `linked_objects[]` containing `{"object_type": "thesis", "object_id": <thesis_id>}`. Do not infer thesis AI proof from chat memory or from the thesis prose itself.
- Scenario AI proof is present when `scenario_note.evolved_from_evidence[]` contains at least one id that resolves under `data/research/evidence_ledger/**/<id>.json` to an evidence_record with `ai_verified=true`. If `evolved_from_evidence[]` is empty, the scenario is excluded as `excluded_due_to_no_independent_review` unless a future schema adds another explicit scenario-side evidence pointer.
- `pm_acknowledged_by[]` and `pm_acknowledged=true` still mark PM review state; they are not required for AI proof, but they should be surfaced separately.

### Revive flow (when stale thesis is needed for a decision)

Per charter §VII + the evidence ledger:

1. PM authors a new evidence_record at `data/research/evidence_ledger/<weekiso>/<id>.json` with:
   - `author_persona="pm"`
   - `pm_acknowledged=true`
   - `belief_delta.changed_dimension ∈ {conviction, scope_boundary}`
   - `linked_objects[].object_id` referencing the stale thesis_id
   - rationale prose explaining what changed in PM belief that justifies revive
2. research-theme-staleness-sweeper (next run) detects the evidence and emits a `revived` freshness_event row taking the thesis from stale → fresh.
3. AFTER step 2 lands, operation-portfolio-decision can include the object if it is active and fresh. If PM acknowledgement is still missing, the package marks it `pending_pm_review` rather than silently treating it as acknowledged.

Do NOT bypass this flow. If a decision is urgent and the sweeper has not run yet, the PM can run the sweeper on demand (`tradectl thesis-cluster ...`); the bypass is to accelerate the sweeper, not to use stale objects.

### Decision input contract

Every action in `pm_action_<D>.md` (and every debate move in `pm_debate`) must be traceable to four explicit inputs, in this read order:

1. **Scenario unit**: `data/research/scenario_notes/<scenario_id>.json` with `lifecycle_stage="active"` AND `freshness_state="fresh"`, plus `pm_review_state` surfaced as acknowledged or pending. The scenario is the decision unit, NOT the parent thesis. A thesis with no active+fresh scenario is not actionable; route back to `research-theme-knowledge-and-package-curator` (knowledge mode) rather than improvise.
2. **Conviction triplet**: the scenario's `(pm_conviction, scenario_role, market_state)` enum values, surfaced verbatim in the artifact (e.g. `(high, leading_path, underpriced_relative_to_scenario)`). Do NOT paraphrase the enums; they are machine-readable for downstream `pm_action_review`.
3. **Pricing reading**: `pricing_snapshots[-1]` (the most recent snapshot). Surface `recorded_at_utc`, `market_state`, `pricing_anchor` prose. If pricing is older than session start AND the action is intraday, flag as a missing-data constraint rather than acting on stale pricing.
4. **Unresolved objections**: read `parent_thesis_id` → `thesis_note.adversarial_review_log[*].unresolved_objection_evidence_ids[]` (most recent log entry first). For each objection evidence_id, the action MUST do exactly one of:
   - cite as supporting (the objection has been refuted by newer evidence; cite the resolution evidence_id)
   - cite as deferred-acceptable (the objection stands but does not change THIS action; inline rationale REQ)
   - explicitly override (the objection is judged wrong; inline rationale + which axis of the objection is being overridden REQ)
   
   Silent ignore is forbidden. If the action cannot honestly say which of the three handlings applies, the upstream interpretation is not stable enough for portfolio action; route back to `research-thesis-adversary` for a fresh review pass.

When the action's pass type is `wait_no_action`, inputs 2-4 are still REQ; the artifact must show why waiting is the right call given the triplet + pricing + unresolved objections, not as an excuse to skip the read.

Use these canonical implementation surfaces:

- `tradectl portfolio policy-show`
- `tradectl portfolio package`
- `tradectl portfolio debate`
- `tradectl portfolio decide`
- `tradectl portfolio preview`

Treat those as the real decision-engine surfaces rather than inventing a parallel chat-only workflow.

## Decision Package Contract

Treat the portfolio decision package as the canonical fact-first decision surface.

It should make these explicit:

- policy constraints
- market regime
- active themes
- current portfolio state
- account review context
- candidate assets
- warnings and missing-data constraints
- per active+fresh scenario under consideration: scenario_id, `(pm_conviction, scenario_role, market_state)` triplet verbatim, `pricing_snapshots[-1]` (recorded_at_utc + market_state + pricing_anchor prose), parent thesis_id, parent thesis `pm_acknowledged_by[]`, `pm_review_state`, parent thesis's `adversarial_review_log[-1].unresolved_objection_evidence_ids`

Do not skip the package when the task is non-trivial and clearly book-level.

## Debate Standard

When the task is still contested, produce a debate artifact before pretending a final book decision exists.

The debate should make explicit:

- what should be added or cut and why
- what should be held despite discomfort and why
- what should remain watch-only
- which risks should be defended first
- which actions are urgent versus later
- what the main downside scenarios are
- which policy limits or data gaps block stronger action

Do not confuse "many facts were listed" with "a real portfolio debate happened."

## Decision And Action Standard

When moving from debate toward action:

- tie every action to current portfolio constraints
- distinguish clearly between `open`, `add`, `reduce`, `close`, `hold`, and `watch`
- keep hedge and trim logic separate from new-idea logic
- make the order of operations explicit when multiple actions compete
- separate `defend the book now` from `build offense now` when both appear in the same answer
- prefer explicit blockers over vague caution
- preserve uncertainty when evidence is partial

Keep these practical PM distinctions visible:

- trimming fragile high-beta or near-dated exposure is not the same as cutting core holdings
- if the market is chaotic, do not assume the best defense is to chase the obvious headline beneficiary
- sometimes the right first move is to clean weak existing risk rather than add a new hedge or new offense leg
- `wait_no_action` is a valid PM output when the structure is not yet clear enough for forced action
- when multiple moves compete, the output must say what to do first rather than only listing options

Useful operating guidance from prior PM-style conversations:

- prefer selling risk into repair or rebound windows when that gives a cleaner exit, rather than treating every weak tape print as the mandatory moment to cut
- do not panic-cut core holdings at the worst intraday location just because headlines are noisy
- if immediate risk reduction is required, first look at the most fragile exposures such as near-dated options, duplicated beta, or the weakest technical structures
- separate `core holdings`, `high-beta satellites`, and `fragile options exposure` before deciding what to cut
- if both defense and offense appear in the same answer, finish the defense ordering first

If the best outcome is to wait, say that directly and explain why waiting is the correct portfolio decision rather than a lack of work.

## Preferred Output Shape

- `Current portfolio judgment`
- `Why now`
- `What this means for the current book`
- `Pass type`
- `Main adds / trims / holds / watches` (each line cites scenario_id + triplet + pricing_snapshot reading + objection-handling per §Decision input contract)
- `Defense first / offense later`
- `Risk constraints and blockers`
- `Target-book direction`
- `Execution preview or next step`
- `Excluded-due-to-stale` (per §Freshness gate, list excluded thesis/scenario IDs with one-line reason)
- `Unresolved objections handling` (per scenario, list `unresolved_objection_evidence_ids` with one of: cite-as-supporting / cite-as-deferred-acceptable / explicit-override + rationale; charter §VIII)

When the task is debate-first, prefer:

- `Decision question`
- `Bull case for action`
- `Bear case / why wait`
- `Constraint check`
- `Tentative conclusion`
- `What would change the decision`

## Failure Signals (task-flow-level, during the decision pass)

These describe pathology **during** the decision pass, distinct from §Detection-side artifact-level violations (which describe wrong shape **after** the artifact lands):

- F1. the output still reads like theme interpretation instead of book decision
- F2. actions are suggested without reference to policy or portfolio constraints
- F3. single-name enthusiasm silently becomes portfolio action without book context
- F4. the artifact cannot tell the reader what to add, trim, hold, or watch
- F5. the artifact cannot tell the reader what to do first
- F6. defense and offense are mixed together without priority
- F7. fragile options, duplicated beta, and core holdings are all treated as one undifferentiated bucket
- F8. hedge, trim, and new-position logic are blurred together
- F9. execution language appears without a stable underlying decision
- F10. the agent read thesis prose instead of the scenario_note's `(pm_conviction, scenario_role, market_state)` triplet (input contract per §Decision input contract violated)
- F11. parent thesis's `unresolved_objection_evidence_ids` was not opened during the decision pass; the agent decided without seeing what the adversary still has unrefuted

## Style Rules

- Write in Chinese by default unless the user requests another language.
- Keep market-standard English terms and symbols when they are clearer.
- Use direct PM language, not research-workflow commentary.
- Keep the artifact decision-facing and readable without extra verbal explanation.

## Example Triggers

- “我现在该怎么调仓”
- “先做一个 portfolio debate”
- “哪些该减，哪些该加”
- “当前最大风险先 hedge 什么”
- “这对我当前组合意味着什么”
- “现在应该先做什么”
- “这波先防守还是先进攻”
- “是不是该先减最脆的仓”
- “现在正确动作是不是先不动”
- “给我一个 target book 方向”
- “做一个 execution preview”
