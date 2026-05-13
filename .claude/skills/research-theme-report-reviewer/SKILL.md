---
name: research-theme-report-reviewer
description: "Reviewer-first gate that runs after a DS-written theme report draft exists at `data/research/theme_update_drafts/<theme_id>.ds.md`. Verifies the draft against the corresponding `theme.package` and `theme.owner_decision`, runs adversarial review, optionally uses Perplexity for narrow external verification, and returns a structured verdict with severity-tagged findings. Do not use this skill to author or rewrite the main article, and do not let it retake owner authority."
---

# Theme Report Reviewer

Design reference: [`designDoc/research_00_report_reviewer_pattern.md`](../../designDoc/research_00_report_reviewer_pattern.md)

## Positive Contract

- Current persona: reviewer
- Current task: review one DS-written theme report against its package, owner decision, and (when needed) external facts
- Primary truth surface:
  - `data/research/theme_update_drafts/<theme_id>.ds.md` (the draft under review)
  - `data/research/theme_update_drafts/<theme_id>.package.md` (the package the draft was supposed to consume)
  - `data/research/theme_update_drafts/<theme_id>.owner.json` (the owner decision that defined the pass)
  - `data/research/themes/reports/<theme_id>.md` (the standing report, used to detect mainline drift)
- Output artifact:
  - `data/research/theme_update_drafts/<theme_id>.review.md` (the review note)
  - `data/research/theme_update_drafts/<theme_id>.review.json` (machine-readable verdict sidecar)
- Reader end-state: the `research-theme-report-owner` and `research-theme-knowledge-and-package-curator` can decide `accept_as_is` / `accept_with_revisions` / `needs_rewrite` without re-reading the full package.

## When To Use

- After a DS-written theme draft exists and is being considered for merge into the standing theme report.
- Before `research-theme-knowledge-and-package-curator` overwrites `data/research/themes/reports/<theme_id>.md`.

## Do Not Use When

- The `theme.package` itself is missing or clearly insufficient — return to `research-theme-report-owner` instead.
- The user is asking for a brand new report or a different mainline.
- The user wants the reviewer to rewrite the main article (this skill never edits the DS file).
- The request is general theme priority work (route to `research-theme-priority-updater`).

## Relationship To Adjacent Skills

- `writer-handoff` is a **pre-writing** package-readiness gate; this skill is the **post-writing** draft-review gate. They do not overlap.
- `research-theme-report-owner` owns the pass. This skill never silently re-decides `pass_type`, `scope`, or `writer_direction`. If those need to change, return `needs_rewrite` and route back to the owner.
- `research-theme-knowledge-and-package-curator` owns the merge. This skill never edits the DS file or the standing report; it only emits the review artifact.

## Required Inputs

Read in this order before producing the verdict:

1. `data/research/theme_update_drafts/<theme_id>.ds.md`
2. `data/research/theme_update_drafts/<theme_id>.package.md`
3. `data/research/theme_update_drafts/<theme_id>.owner.json`
4. `data/research/themes/reports/<theme_id>.md`

Read on demand:

- prior `data/research/theme_update_drafts/<theme_id>.review.md` if it exists (last revision context)
- relevant `data/research/thesis_notes/*.json`
- for asset-centered themes (`gold` / `oil` / `usd` / `rates` / `btc`), the matching `asset_technical_report` for the relevant asset cluster
- overlapping themes only when the owner decision flagged cross-theme overlap

If any of the four required inputs is missing, do not produce a verdict — return a clear `missing_input` note and stop.

## Three-Layer Pipeline (Mandatory, In Order)

> Layer 0 (below) is a structural gate that runs **before** the three semantic layers and can short-circuit the whole review.

### Layer 0 — Thesis Structural Readiness (deterministic, fail-fast)

After reading this layer the reviewer can tell apart **a draft built on theses still in motion** (drafter / verifier / adversary not finished) from **a draft worth semantic review**. This catches a class of upstream-pipeline failure that has nothing to do with what the writer chose to say, so it must run before any Perplexity call or adversarial pass.

For every thesis_note referenced under `## Theses (selected)` in `<theme_id>.package.md`, open the corresponding `data/research/thesis_notes/<thesis_id>.json` and check:

1. `lifecycle_stage == "active"`. If still `draft`, the verifier or adversary stage has not promoted the thesis; the package should not have surfaced it.
2. When `lifecycle_stage == "active"`, the v1.5 conditional fields must all be present and populated: `falsifiers[]`, `scenario_triggers[]`, `next_review_trigger`. Any missing one means the schema's `if active then required` was bypassed and the file is structurally incomplete.
3. `counter_evidence_observed[]` may be empty **only if** `notes` contains the `single-perspective risk:` acknowledgement line. Empty + no flag is structural omission, not a null finding.
4. `notes` contains **at most one** line starting with `external verification:`, and that line uses the controlled vocabulary `(verified|partial|pending) – <prose>`. Stacked or off-vocabulary verification lines mean the verifier's own contract was broken.
5. Every `cross_theme_links[].theme_id` resolves to an existing `data/research/themes/metadata/*.json` file (read-side accepts both hyphen-case and snake_case ids per the cluster's read-wide naming convention).

Checks 1–5 are already enforced by [`tradectl thesis-cluster validate <agent_id> <thesis_note_path>`](../../src/tools/thesis_cluster_validate.py) at write time. The reviewer may shell out to `tradectl thesis-cluster validate` for each referenced thesis instead of re-implementing them.

The next two checks (6 and 7) are **narrative-shape gates** that the L1 schema cannot enforce — they require human / LLM judgment on the prose carried inside existing fields (see [`research-thesis-drafter SKILL §Narrative Shape`](../research-thesis-drafter/SKILL.md#narrative-shape--what-the-prose-must-make-visible-v15-自由格式承载) and [`research-thesis-adversary SKILL §Adversarial Shape`](../research-thesis-adversary/SKILL.md#adversarial-shape--what-falsifiers--counter-evidence--triggers-must-make-visible-v15-自由格式承载)). The reviewer applies them by reading the prose; if either fails, treat as `thesis_structure` root cause:

6. **Reverse path not buried.** Open the referenced thesis_note. The reverse / weakening path must appear either as a prose `falsifier[]` entry written as a structured forward path (factors → mechanism → effect), or as an explicit `key_dependency` whose collapse would invalidate the thesis. A thesis whose `falsifiers[]` is a list of one-line nitpicks against single numbers (e.g. `"if real rate > 1.5%, thesis is wrong"`) without any path-shaped reverse case **fails this check**. Adversary would have surfaced a real reverse path; absence indicates adversary did not run a real adversarial pass.
7. **Concurrent reverse path acknowledgement.** When at least one `scenario_triggers[*]` is `triggered` or `reverse_triggered`, OR when `counter_evidence_observed[]` contains an entry that materially weakens the main claim, `notes` must contain a single line of the form `concurrent reverse path: <prose>` (placed after the verifier's `external verification:` line). The line must be substantive (≥ ~30 chars), not a placeholder. A thesis with active reverse evidence but no concurrent-path acknowledgement means adversary did not surface the now-vs-future distinction; PM reading the report would think the reverse path is purely hypothetical when in fact it is partially unfolding.
8. **Inline source ref tags present.** Every entry in `claims[]` must end with a `[refs: <i>, <j>, …]` tag where each index is a 1-based position in `source_research_ids[]` (see [`research-thesis-drafter SKILL §Inline source ref convention`](../research-thesis-drafter/SKILL.md#inline-source-ref-convention--refs-)). Every entry in `counter_evidence_observed[]` must end with `[refs: …]` accepting `0` for adversary self-observation (see [`research-thesis-adversary SKILL §Inline source ref convention`](../research-thesis-adversary/SKILL.md#inline-source-ref-convention--refs--counter_evidence_observed-mandatory)). A thesis whose claims or counter-evidence arrive without ref tags forces the PM and the writer to reverse-engineer "which source backs this sentence" from prose context — that defeats the purpose of carrying `source_research_ids[]` at all. Index-out-of-range references (e.g. `[refs: 99]` when only 6 sources exist) and non-numeric tags also fail this check.
9. **Trigger threshold carries baseline window when relative.** For every entry in `scenario_triggers[]`, if the `threshold` references a percentile, std-band, historical extreme (max/min), multi-year average, or any other reference to a historical distribution, the threshold prose MUST inline the baseline window + aggregation grain + reference statistic (see [`research-thesis-adversary SKILL §Trigger threshold MUST carry baseline window`](../research-thesis-adversary/SKILL.md#trigger-threshold-must-carry-baseline-window-v15-prose-carrier)). `threshold: "30 percentile"` fails — window unspecified. `threshold: "trailing 5y daily, > 30th percentile of NYSE TTM PE"` passes. Absolute thresholds (`"0"`, `"+5%"`, `">2.5%"`) are exempt. **Source-availability sub-check**: if the threshold relies on a daily 5y series for a metric whose daily history is NOT retrievable through declared `source_research_ids[]` plus the canonical Perplexity helper coverage (Perplexity returns current value + 5y average + monthly/year-end snapshots, NOT daily percentile rank — see [`research-thesis-verifier SKILL §Canonical Perplexity Helper`](../research-thesis-verifier/SKILL.md#canonical-perplexity-helper)), the threshold is unverifiable and fails this check; adversary should reword to a verifiable statistic or drop to `falsifier` prose.

10. **Trigger label matches underlying measurement.** For every entry in `scenario_triggers[]`, if the trigger prose names a metric (e.g. `Breakeven 2y-10y spread`) AND references underlying FRED / Bloomberg / CME / Fed / BLS / BEA series IDs (e.g. `FRED T5YIE and T10YIE derived`), the named metric MUST match the actual computation those IDs produce. A trigger labelled `Breakeven 2y-10y spread` but using `T5YIE + T10YIE` as the underlying series is actually a 5y-10y spread, not 2y-10y; this naming-vs-measurement mismatch is a write-time bug that propagates downstream into theme-report observable framework rows and asset-mapping prose, where it becomes much harder to detect. Fail the check when:
    - the metric tenor in the label does not match the tenor in the FRED ID (e.g. label says `2y` but FRED ID is `T5YIE` which is 5y breakeven)
    - the metric kind in the label does not match the FRED series kind (e.g. label says `nominal yield` but FRED ID is a real-yield series)
    - the label references a derived / computed quantity but the underlying IDs are insufficient to compute it (e.g. label says `spread` but only one tenor's ID is provided)

    Route patch to `research-thesis-adversary` to either rename the trigger label OR add the missing FRED field. This check was added 2026-04-24 after the federal_rate_cycle V4 dogfood surfaced exactly this mismatch in `stagflation_policy_mistake_tail_regime` (label `Breakeven 2y-10y spread` + IDs `T5YIE + T10YIE` = actually 5y-10y).

    _Validation pending (retrospective follow-up)._ This check is currently unvalidated
    beyond the single dogfood incident that motivated it. The **first time it fires in
    a real reviewer run on a thesis outside `stagflation_policy_mistake_tail_regime`**,
    append the thesis_id + run date to `designDoc/retrospectives/critic_pipeline_20260424.md`
    Item 4 to close the loop. If after several critic runs the check never fires, that
    is also signal — update the retrospective with the null finding and decide whether
    the precision / coverage needs adjustment.

If any Layer 0 check fails:

- set `mainline_alignment` and `evidence_alignment` to `fail` and `status` to `needs_rewrite`
- set `root_cause` to `thesis_structure` (do not pick `package` or `writing` — those describe semantic failure, not structural)
- in `Notes For Owner`, name the responsible upstream agent:
  - `research-thesis-drafter` — checks 1, 5; check 6 when reverse path absence reflects drafter never naming reverse-path candidates in `key_dependencies[]` / `probability_view`; check 8 when missing tags are on `claims[]` (drafter's responsibility)
  - `research-thesis-verifier` — checks 4 (stacked or malformed `external verification:` lines)
  - `research-thesis-adversary` — checks 2, 3 (lifecycle promotion contract); checks 6, 7 in most cases (path-shaped reverse case is adversary's responsibility, as is the `concurrent reverse path:` line on `notes`); check 8 when missing tags are on `counter_evidence_observed[]` (adversary's responsibility); check 9 (trigger threshold baseline window) — adversary owns `scenario_triggers[]` shape; check 10 (trigger label vs underlying measurement) — same ownership
- do **not** continue to Layer 1, 2, or 3. Spending a Perplexity call or an adversarial pass on a structurally broken thesis wastes budget and produces noise.

### Layer 1 — Self-audit Against Package

For every claim in the draft, check:

- **Mainline alignment**: does the DS final mainline match `owner_decision.scope`? Polish is allowed; trigger / direction / framing change is not.
- **Evidence alignment**: does every numeric / dated / policy-wording claim trace back to the package? Flag any claim introduced from outside.
- **Confirmed vs not-confirmed**: did the draft promote any package `not_confirmed` item to settled fact?
- **Time discipline**: are research-evidence window, raw market UTC, `session_as_of`, `report_date`, and `generated_at` kept distinct, or were they collapsed into one vague "latest"?
- **Block coverage**: are these blocks present where they belong — current judgment / background / what the market is pricing / drivers and transmission / confirmed anchors / not-confirmed / key debates / scenario path / portfolio fit / risks and monitoring? Note any missing block.

### Layer 2 — External Verification (Conditional, Narrow)

Trigger Perplexity verification only when at least one **hard trigger** is met. Do not call it as a default scan.

Hard triggers:

- Draft cites a specific price / yield / official rate decision / policy statement timing that the package has no anchor for.
- The draft's narrative window contains a known major public event (rate decision, OPEC communiqué, regulator release, geopolitical event) and the package is clearly older than the event.
- Draft makes a "event X happened at time Y" assertion with no dated package anchor.
- Draft and standing report disagree on mainline and only an external timeline can resolve which side is current.

Forbidden triggers:

- pure thesis / mechanism prose
- long-horizon framing
- facts that already have a confirmed package anchor
- pure stylistic or polish concerns

Call discipline:

- one leg per query (single asset / event / policy)
- explicit date window in the query
- default `--preset fast-search`; escalate to `--preset pro-search` only for mechanism-heavy verification
- record each result as `confirmed` / `not_confirmed` / `contradicted`
- never let Perplexity be the verdict author — it is evidence

### Layer 3 — Adversarial Review

Ask all four:

1. **Mismatch handling** — did the draft smooth over cross-asset, technical-vs-narrative, or intra-thesis mismatches?
2. **Cherry-pick** — did the draft only cite supporting assets / windows and quietly drop the contrary ones?
3. **Over-attribution** — did the draft promote single-day price moves to regime shifts, or single events to structural triggers?
4. **Silent mainline drift** — does the final DS mainline still match `owner_decision.scope` and the standing report's framing? If not, this alone forces `needs_rewrite`.

## Verdict Shape

Every review must produce these fixed fields:

- `mainline_alignment`: `ok` | `weak` | `fail`
- `evidence_alignment`: `ok` | `partial` | `fail`
- `mismatch_handling`: `ok` | `weak` | `fail`
- `status`: `accept_as_is` | `accept_with_revisions` | `needs_rewrite`

Decision rules:

- any field = `fail` ⇒ `status` must be `needs_rewrite`
- any field = `weak` and none = `fail` ⇒ `status` is at most `accept_with_revisions`
- all three = `ok` and no `critical` finding ⇒ `accept_as_is`

Severity rules for findings:

- `critical` — affects PM decision correctness (mainline drift, treating `not_confirmed` as confirmed, sizable numeric error)
- `major` — affects judgment robustness (smoothed mismatches, over-attribution, missing key debate)
- `minor` — wording, structure, section order, editorial / process language leakage

For `needs_rewrite`, state explicitly which root cause applies:

- `thesis_structure` — Layer 0 caught a structurally invalid thesis_note; route back to the responsible agent in the thesis cluster (`research-thesis-drafter` / `research-thesis-verifier` / `research-thesis-adversary`), not to research-theme-knowledge-and-package-curator
- `package` — package itself is mis-scoped or insufficient; return to `research-theme-report-owner` for re-scoping
- `writing` — package is fine but the draft mishandled it; return to `research-theme-knowledge-and-package-curator` report mode for a redraft

## Output Template

Write to `data/research/theme_update_drafts/<theme_id>.review.md`:

```markdown
---
theme_id: <theme_id>
report_date: <D>
draft_path: data/research/theme_update_drafts/<theme_id>.ds.md
package_path: data/research/theme_update_drafts/<theme_id>.package.md
owner_decision_path: data/research/theme_update_drafts/<theme_id>.owner.json
reviewer: research-theme-report-reviewer
generated_at: <UTC>
---

## Verdict
- status: <accept_as_is | accept_with_revisions | needs_rewrite>
- mainline_alignment: <ok | weak | fail>
- evidence_alignment: <ok | partial | fail>
- mismatch_handling: <ok | weak | fail>
- external_verification_used: <yes (n legs) | no>
- root_cause (when needs_rewrite): <thesis_structure | package | writing>

## Critical Findings
- [C1] <claim in draft> — <why it fails> — <package anchor or missing anchor>

## Major Findings
- [M1] ...

## Minor Findings
- [m1] ...

## External Verification (Perplexity)
- query: "<narrow query, single leg>"
- date_window: <explicit window>
- preset: <fast-search | pro-search>
- result: <confirmed | not_confirmed | contradicted>
- impact: <which finding this resolves or strengthens>

## Required Revisions
- <concrete edit instruction tied to a finding id>

## Notes For Owner
- <only if status = needs_rewrite or owner-level decision is implicated>
```

Also write a sidecar `data/research/theme_update_drafts/<theme_id>.review.json`:

```json
{
  "theme_id": "...",
  "report_date": "...",
  "draft_path": "...",
  "package_path": "...",
  "owner_decision_path": "...",
  "verdict": {
    "status": "accept_with_revisions",
    "mainline_alignment": "ok",
    "evidence_alignment": "partial",
    "mismatch_handling": "weak",
    "root_cause": null
  },
  "findings": {
    "critical": [],
    "major": [],
    "minor": []
  },
  "external_verification": [
    {
      "query": "...",
      "date_window": "...",
      "preset": "fast-search",
      "result": "confirmed",
      "impact": "..."
    }
  ],
  "required_revisions": [],
  "generated_at": "..."
}
```

## Routing After Verdict

- `accept_as_is` ⇒ hand back to `research-theme-knowledge-and-package-curator` to merge `<theme_id>.ds.md` into `themes/reports/<theme_id>.md`, update metadata, delete `<theme_id>.package.md`, run `python src/tools/build_theme_indexes.py`.
- `accept_with_revisions` ⇒ hand back to `research-theme-knowledge-and-package-curator` (report mode) to apply each item in `Required Revisions` to the DS file, then re-enter this skill for a second pass.
- `needs_rewrite` with `root_cause: thesis_structure` ⇒ hand back to the named cluster agent (`research-thesis-drafter` / `research-thesis-verifier` / `research-thesis-adversary`) to fix the underlying `thesis_notes/<thesis_id>.json`, then rerun the upstream package builder before re-entering this skill.
- `needs_rewrite` with `root_cause: package` or `writing` ⇒ hand back to `research-theme-report-owner` to re-decide `pass_type` / `scope` / `writer_direction`; if root cause is `package`, the owner may also need `research-theme-knowledge-and-package-curator` knowledge mode before another report mode pass.

## Hard Rules

- Do not edit the DS file, the package, the owner decision, or the standing report.
- Do not author replacement prose for the main article. Findings must be diagnostic, not rewrites.
- Do not re-decide pass type, scope, or writer direction.
- Do not turn Perplexity output into the verdict.
- Do not use editorial / process language (`这次 package`, `这版`, `本次更新`, `相比现有报告`) inside `Critical / Major / Minor Findings`.
- Do not skip the sidecar JSON. Downstream routing depends on a machine-readable verdict.
- Do not start without the four required inputs. If any is missing, return `missing_input` and stop.

## Failure Signals

Treat these as signs this skill itself failed:

- The reviewer rewrote the article instead of returning a verdict.
- The reviewer silently changed the mainline.
- Perplexity output was presented as the conclusion.
- Mismatches were smoothed away inside review notes.
- Editorial / process language leaked into findings.
- Verdict block missing the three alignment fields, or `status` not in the allowed set.
- No sidecar JSON was emitted.
- Layer 0 was skipped and a structurally invalid thesis (lifecycle != active, missing falsifiers / scenario_triggers / next_review_trigger, stacked verification line) reached Layer 1 or 2 — Perplexity budget burned on a pipeline-broken thesis.
- Layer 0 narrative checks (6, 7) skipped: `falsifiers[]` is a list of one-line nitpicks with no path-shaped reverse case, OR active reverse evidence exists but `notes` lacks the `concurrent reverse path:` line, and the reviewer still passed the draft to Layer 1+.
- Layer 0 inline-ref check (8) skipped: `claims[]` arrives without `[refs: …]` tags, OR `counter_evidence_observed[]` arrives without `[refs: …]` tags, and the reviewer still passed the draft to Layer 1+ — PM and writer cannot trace which source backs which sentence.
- Layer 0 trigger-baseline check (9) skipped: `scenario_triggers[*].threshold` uses a relative reference (percentile / std-band / multi-year average / historical extreme) without inlining the baseline window + grain + reference statistic, OR the threshold relies on a daily 5y series that is not retrievable from declared sources + canonical Perplexity coverage, and the reviewer still passed the draft to Layer 1+ — the trigger becomes unverifiable downstream and any "triggered" status the PM later writes is not machine-defensible.
- Layer 0 trigger-label-vs-measurement check (10) skipped: `scenario_triggers[*]` trigger prose names a metric tenor / kind that does not match the underlying FRED / Bloomberg / CME series IDs (e.g. label says `2y-10y spread` but IDs are `T5YIE + T10YIE` which is 5y-10y), and the reviewer still passed the draft to Layer 1+ — the naming-vs-measurement bug propagates downstream into theme-report observable framework rows where it becomes much harder to detect.
- `root_cause: thesis_structure` was used but the verdict still routed to `research-theme-report-owner` instead of the responsible cluster agent.

## Example Triggers

- "DS 写完这版 theme report 了，你 review 一下"
- "review the latest `<theme_id>.ds.md` against its package"
- "这版 theme report 能 merge 吗"
- "需要拿外部事实核一下这份 DS 文里的政策时间"

## Node Bindings (planned)

This skill is intended to own the planned node `theme.report.review` in `data/runtime/artifact_graph.yaml`:

- canonical path: `data/research/theme_update_drafts/<theme_id>.review.md`
- sidecar: `data/research/theme_update_drafts/<theme_id>.review.json`
- depends on (must_be_fresh): `theme.report.ds`, `theme.package`, `theme.owner_decision` (all keyed by `theme_id`)
- downstream gate: `theme.knowledge` may only be overwritten when the latest `theme.report.review.status` ∈ {`accept_as_is`, `accept_with_revisions` (with all `required_revisions` applied and re-reviewed)}.

When the node is added to `artifact_graph.yaml`, this section becomes the canonical contract; until then, treat the same shape as the working contract.
