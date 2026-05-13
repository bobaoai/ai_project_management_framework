---
name: research-theme-knowledge-and-package-curator
description: "Curates a macro theme's two surfaces under upstream `research-theme-report-owner`: (a) knowledge mode drafts / restructures the theme's scenario / thesis / evidence-link structure and matching metadata; (b) report mode assembles the writer-ready package, runs the sufficiency gate, routes to `writer-handoff`. Renamed 2026-04-27 from `research-theme-content-maintainer` (old name suggested janitorial maintenance, hid the active drafting + assembly work this skill actually does). Use when the owner has already decided the pass and this curator must execute one of the two modes without taking over theme-priority authority."
---

# Theme Knowledge and Package Curator

## What This Skill Does

This skill curates a macro theme through **two distinct modes** that share infrastructure but produce different artifacts:

- **`knowledge mode`**: drafts and restructures the theme's reusable knowledge surface (scenario / thesis / evidence-link structure + matching metadata). Output is the standing `themes/reports/<theme_id>.md` and updated `thesis_notes/`.
- **`report mode`**: assembles the writer-ready package, runs the sufficiency gate, routes to `writer-handoff`, and lands an approved `theme_update_drafts/<theme_id>.ds.md`. Output is one PM-facing report pass.

**Cross-mode invariant**: if a single task needs both modes, run `knowledge mode` first to convergence, then start a separate `report mode` pass. Mixing the two in one run leaves the knowledge surface partially drafted while a report-quality artifact is already being assembled; the `knowledge mode` work is then forced through `report mode` deadlines and the writer reads stale or contradictory inputs.

Within each mode, the work covers:

| Mode | Work items |
|---|---|
| `knowledge mode` | refresh `thesis_notes`; update subtheme + scenario structure; maintain linked research/thesis references; refresh reusable abstractions; sync metadata fields belonging to the knowledge layer |
| `report mode` | assemble `theme_update_drafts/<theme_id>.package.md`; run package sufficiency gate; route to `writer-handoff`; review or merge returned PM-facing prose; update finalized report + matching metadata |

Authority not held by this skill: top-level report pass scope (owned by `research-theme-report-owner`), theme-stack ranking (owned by `research-theme-priority-updater`).

## Desired Result

The desired result is that the theme's content layer becomes internally consistent, source-grounded, and ready for either:

- future reuse in the knowledge layer
- or immediate downstream writing through a package that is actually sufficient

By the time this skill is done, the theme should no longer have a gap between:

- what the evidence says
- what the theme document claims
- what the metadata points to
- what the downstream writer needs

## Reader End-State

After this skill is done, the next downstream reader differs by mode:

**Knowledge mode reader** (future report rounds, downstream `research-theme-report-owner` passes that re-enter this theme):

- Can rely on the theme's standing report + metadata + linked thesis records being internally consistent, with no orphaned scenarios or stale evidence pointers
- Can reuse the abstractions (subthemes, scenario structure, transmission chain) without having to re-derive them from raw research
- Can tell what the current canonical view is versus what is still unresolved or in active drafting

**Report mode reader** (`writer-handoff` gate + `research-theme-report-reviewer` + downstream Stage 3 patcher / writer):

- Can judge whether the package is sufficient for confident writing without re-reading raw archive material
- Can see which package items map to which writer-direction directive
- Can write from the package directly, with each numeric anchor traceable to (a) thesis baseline / (b) package live anchor / (c) explicitly Writer-derived; no silent invention
- Can reach `accept_as_is` / `accept_with_revisions` / `needs_rewrite` without reopening upstream owner authority

If the next reader still has to re-derive the consistency layer (knowledge mode) or re-evaluate package sufficiency (report mode), this skill is not done.

Operational acceptance signal per mode (each invocation should observe + report):

- `report mode`: `writer-handoff` reaches a clean `ready_to_write` or `need_more_detail` verdict without re-reading raw archive material
- `knowledge mode`: a future `research-theme-report-owner` re-entering the same theme relies on the maintained artifacts (thesis_notes / scenario_notes / themes/reports) without re-deriving consistency

Retrospective trace for the original framing of this Reader End-State section: [`designDoc/retrospectives/critic_pipeline_20260424.md`](../../designDoc/retrospectives/critic_pipeline_20260424.md) Item 1.

## Relationship To `research-theme-report-owner`

`research-theme-report-owner` owns the pass.

This skill executes the content leg after upstream decisions are already made. It should not silently retake authority over:

- top-level report scope
- broad refresh versus narrow update judgment
- material recency judgment
- writer emphasis or framing

If those decisions are missing, ask for them or return a concrete missing-owner-context signal instead of improvising a new top-level brief.

## Node Bindings

This skill owns the following nodes in `data/runtime/artifact_graph.yaml`:

- `theme.knowledge(theme_id)`: L2 standing theme report content at `data/research/themes/reports/<theme_id>.md` (knowledge mode)
- `theme.package(theme_id, D)`: L3 writer-facing package at `data/research/theme_update_drafts/<theme_id>.package.md` (report mode)
- `theme.report.ds(theme_id, D)`: L4 PM-facing finalized report (report mode + writer gateway)

This skill consumes:

- `theme.owner_decision(theme_id, D)` (must_be_fresh): produced by `research-theme-report-owner`; required for report mode
- `themes.metadata(theme_id)` (must_be_fresh)
- `asset_technical_report(asset, D)` (optional_overlay) for asset-centered themes
- local research artifacts under `data/research/messages/`, `data/research/snapshots/`, `data/research/thesis_notes/` (referenced by id, not as graph nodes in v0.1)

Builder kinds:

- `theme.knowledge`, `theme.report.ds`: `ai_writer`
- `theme.package`: `composite` (assembly + `writer-handoff` gate)

This skill does NOT own:

- `theme.owner_decision`: that is `research-theme-report-owner`
- `themes.metadata` direct edits beyond the allowed-fields whitelist below (broader metadata changes route to `research-theme-priority-updater`)
- `themes.current_priority_tree` regeneration: that is `research-theme-priority-updater`

Detection-side boundary, artifact-level violation (look at the resulting file/path):

- D1. `theme.report.ds` exists without a preceding `theme.package` at the canonical path (artifact lineage broken)
- D2. `theme.package` was written without a corresponding `theme.owner_decision(theme_id, D)` for the same date
- D3. `themes/reports/<theme_id>.md` was overwritten without writer-gateway trace (no `<theme_id>.ds.md` intermediate, no archived `<theme_id>.review.md` + `.review.json`)
- D4. `themes/metadata/<theme_id>.json` had ranking fields (`priority_bucket`, `priority_rank`) mutated by this skill instead of `research-theme-priority-updater`
- D5. A generated view (`themes/index.json`, `current_priority_tree.json`) was hand-edited rather than rebuilt by its canonical builder
- D6. Cross-artifact disagreement: `evidence` claims, `themes/reports/<theme_id>.md` claims, `themes/metadata/<theme_id>.json` fields, and linked `thesis_notes` no longer agree

## Completion Standard

### `knowledge mode` is complete only when:

- the target theme's scenario/subtheme/thesis structure is updated or explicitly left unchanged
- linked evidence references match the current judgment
- changed knowledge-layer fields are written back to canonical files
- no unresolved contradiction remains between the theme report, metadata, and linked thesis records

### `report mode` is complete only when:

- `theme_update_drafts/<theme_id>.package.md` exists and is current for this pass
- the package has been judged `ready_to_write` or `need_more_detail`
- if `ready_to_write`, the downstream writer path is triggered from a passed package-review gate and the resulting output is reviewed
- the resulting `theme_update_drafts/<theme_id>.ds.md` has been passed through `research-theme-report-reviewer` and a corresponding `<theme_id>.review.md` + `<theme_id>.review.json` exists for this date
- the review sidecar `verdict.status` is `accept_as_is`, or `accept_with_revisions` with every item in `required_revisions` applied to the DS file and re-reviewed
- if approved, the finalized report and metadata are updated to match
- generated views are rebuilt when the task actually lands a finalized change

If the package exists but the sufficiency decision is still vague, `report mode` is not complete. If a DS draft exists but no passing `research-theme-report-reviewer` verdict exists, merge is forbidden; return to the reviewer (or back to `research-theme-report-owner` on `needs_rewrite`).

## Primary Truth Surfaces

Read these first:

- `data/research/themes/index.json`
- `data/research/themes/metadata/<theme_id>.json`
- `data/research/themes/reports/<theme_id>.md`
- `data/research/theme_update_drafts/<theme_id>.json` when it exists
- `data/research/thesis_index.jsonl`
- `data/research/messages_index.jsonl`
- `data/research/snapshots_index.jsonl`
- relevant files under `data/research/thesis_notes/`
- relevant files under `data/research/messages/`
- relevant files under `data/research/snapshots/`

Then do a related-theme sweep when overlap can materially change interpretation:

- relevant sibling rows in `data/research/themes/index.json`
- overlapping metadata under `data/research/themes/metadata/`
- finalized reports under `data/research/themes/reports/`
- overlapping active drafts under `data/research/theme_update_drafts/` when they exist

For asset-centered themes such as `gold`, `oil`, `usd`, `rates`, or `btc`, do an extra asset-cluster sweep across overlapping local themes before finalizing the package or report.

## Package Contract

Treat `theme_update_drafts/<theme_id>.package.md` as the canonical temporary writer input for one report pass.

The package is complete only when it makes the following legible:

- current judgment
- necessary background context
- key drivers and transmission path
- what the market is pricing now when relevant
- confirmed anchors
- not-confirmed items
- key debates and competing interpretations
- scenario path / what happens next
- portfolio fit or action framing
- key risks and monitoring items

Package rules:

- do not compress it into a shallow summary brief
- do not turn it into polished final prose
- keep metadata header standardized but body structure flexible
- prefer original source passages, raw notes, raw tables, raw price checks, and raw verification output over extra rewrite layers
- separate clearly what is explicit source content, what is inference, and what is cross-source synthesis
- prefer an ID-first selection contract and deterministic payload assembly from canonical objects

### Scenario + pricing_snapshot slot

> **Reader gain (Rule 36)**: by hard-requiring a scenario_note + pricing_snapshot slot in the package, the writer no longer has to re-derive "what path is this thesis taking" from prose alone. operation-portfolio-decision reads the same slot for its (pm_conviction, scenario_role, market_state) triplet + pricing_snapshots[-1]; theme report writer reads it for the "scenario path / what happens next" + "what the market is pricing now" sections. One canonical surface, two consumers.

When a thesis covered by this package has ≥1 `scenario_note` under `data/research/scenario_notes/` linked via `parent_thesis_id`, the package MUST include a structured "scenario + pricing" slot per linked thesis. Slot shape:

```markdown
## Scenarios for thesis `<thesis_id>`

Each scenario_note is rendered with these fields verbatim from `data/research/scenario_notes/<scenario_id>.json`:

- `scenario_id` + `scenario_role` enum (leading_path / parallel_path / tail_path / counterfactual)
- `pm_conviction` enum (high / medium / low / exploratory)
- `market_state` enum (underpriced / consensus / overpriced / ambiguous, all `_relative_to_scenario`)
- `narrative` prose
- `trigger_signals[]` machine-readable triggers (observable_data + threshold + direction + status)
- `pricing_snapshots[-1]`: the most recent `recorded_at_utc`, `market_state`, `pricing_anchor` prose, optional `cross_asset_signals[]`. Older snapshots accessible via append history but not rendered inline (charter §VIII pricing path retained at source, package shows current reading)
- `evolved_from_evidence[]`: evidence_record ids (link, do NOT inline content; reader follows to ledger)
```

Hard rules for the slot:

- If the thesis has 0 scenario_notes, render `## Scenarios for thesis <thesis_id> (none yet, await research-thesis-adversary scenario_note emission)` rather than silently omitting the slot. Silent omission is the failure mode equivalent to operation-portfolio-decision §Freshness gate's `excluded_due_to_stale[]` requirement.
- If a scenario's `lifecycle_stage="draft"` and `pm_acknowledged=false`, render with prefix `[draft, pending PM ack]` so the writer knows not to rely on it as decision-anchoring.
- If a scenario's `freshness_state="stale"`, render with prefix `[stale, await revive]` and DO NOT include its triplet/pricing in the writer's main "what we believe now" section (writer can still cite it under "deferred / waiting for new evidence").
- pricing_snapshots[-1] inclusion is REQ when scenario `lifecycle_stage="active"`. If active scenario has no pricing_snapshot, mark explicitly `[active scenario but pricing_snapshots empty: package builder MUST ask research-theme-knowledge-and-package-curator to populate before report writes]`.
- The slot rendering pulls verbatim from canonical scenario_note JSON. Do NOT paraphrase the enum values (they're machine-readable for the package-review gate).

Path convention recap: `data/research/scenario_notes/<scenario_id>.json` per the v0.1 scenario_note schema. Multiple scenarios per thesis OK; render all in rank_within_thesis order (1 first).

## Canonical Outputs

Possible outputs from this skill:

- updated `data/research/thesis_notes/*.json`
- updated `data/research/theme_update_drafts/<theme_id>.package.md`
- updated `data/research/theme_update_drafts/<theme_id>.ds.md` through `writer-handoff`
- updated `data/research/themes/reports/<theme_id>.md`
- updated `data/research/themes/metadata/<theme_id>.json`

Allowed metadata/report edits include:

- `summary`
- `why_now`
- `updated_at_utc`
- `evidence_status`
- `open_questions`
- `linked_research_ids`
- `linked_thesis_ids`
- `linked_asset_tickers`
- `subthemes`

If the content update implies a ranking change, state that explicitly and hand off to `research-theme-priority-updater` rather than mutating generated priority views here.

## Evidence Standard

Use these quality rules:

- start local-first
- use external sources only when the user explicitly asks
- when source packets exist, read the underlying source content rather than stopping at summaries
- for important claims, preserve the full reasoning chain rather than one-line takeaways
- distinguish explicit source claims from your inference
- when multiple packets support one report, know which packet supports which leg of the thesis

For public-source validation:

- use the canonical helper in Perplexity `Agent API` mode only as a narrow verification layer
- default to `--preset fast-search`
- escalate to `--preset pro-search` only for mechanism-heavy checks
- ask one narrow verification question at a time
- anchor time-sensitive checks to an explicit window
- return confirmed facts, exact anchors when available, citations, and not-confirmed items
- do not ask Perplexity to design the macro framework or decide the main thesis

## Report Standard

When this skill updates report content, the result should read like a polished client-facing analyst note rather than an update memo.

Keep these standards:

- main article first; logs are secondary
- integrate changed facts into the article instead of appending update fragments
- preserve important background, mechanism, and debate where they explain the judgment
- restate the trigger or changed setting explicitly inside the article
- explain company and asset relevance through value capture, dependencies, and risks
- connect major claims through `trigger -> mechanism -> market consequence -> investable mapping`
- use natural Chinese analyst prose by default unless the user asks otherwise
- avoid editorial/process headings or sentences in the main article

Do not let `knowledge mode` labels such as `subtheme`, `company thesis`, `trade thesis`, `reusable abstraction`, or similar workflow vocabulary leak into the client-facing article.

### Carrying thesis narrative shape into the report (v1.5 自由格式承载)

> **Reader gain (Rule 36)**: by carrying these two things from `thesis_notes/*.json` into the report's scenario / risks / drivers sections, the PM reader can distinguish (a) which thesis paths are unfolding **concurrently** with what relative weight, not just which "base case" was chosen, and (b) reverse paths that are **partially active now**, not only hypothetical futures. Without this, the report silently regresses to a one-base-case framing and the PM gets blindsided when the reverse path turns out to have been visible in the thesis_note.

When the package ([`build_theme_writer_package.py`](../../src/tools/build_theme_writer_package.py)) renders thesis prose under `## Theses (selected)`, two pieces of narrative carried inside `thesis_note v1.5` prose fields must surface in the corresponding sections of the finalized report:

1. **Multi-path acknowledgement in `scenario path / what happens next`.** When a thesis_note's `probability_view` explicitly named ≥2 forward paths plausibly unfolding concurrently (per [`research-thesis-drafter SKILL §Narrative Shape`](../research-thesis-drafter/SKILL.md#narrative-shape--what-the-prose-must-make-visible-v15-自由格式承载)), the report's scenario-path section must reflect that, not collapse to one base case. Acceptable phrasing: "主线延续仍是更可能路径，但 tilts-to-concentration 路径过去 4 周升温，需并列跟踪"; not acceptable: silently dropping the secondary path because it is not the base case.
2. **Concurrent reverse path in `risks and monitoring`.** When a thesis_note's `notes` carries a `concurrent reverse path: <prose>` line (per [`research-thesis-adversary SKILL §Adversarial Shape`](../research-thesis-adversary/SKILL.md#adversarial-shape--what-falsifiers--counter-evidence--triggers-must-make-visible-v15-自由格式承载)), the report's risks-and-monitoring section must mention this reverse path as **partially active now**, not bury it as a future hypothetical. Acceptable: "risk: tilts-to-concentration 信号过去 4 周升温（dispersion 退至历史 30 分位以下 + Mag7 集中度 +3pp），与主线并行，需提前在仓位上为 dispersion 失效留余地"; not acceptable: only listing the structural falsifier ("if X happens in the future, thesis is wrong") and omitting the now-vs-future distinction.

These obligations are read-time, not write-time:

- Do **not** invent multi-path framing if the underlying `thesis_notes/*.json` only contained a single base case (that is drafter's job, not maintainer's). If the upstream prose is single-path and this is a problem, raise back to `research-theme-report-owner` rather than fabricate a "balanced view" that is not in the source.
- Do **not** copy thesis_note `notes`'s control-plane lines (`external verification:`, `single-perspective risk:`, `concurrent reverse path:`) verbatim into the article. Those are workflow markers; the article should re-express their substance in analyst prose (which factor, which path, what to watch).

### Inline source ref tags: strip on render, surface as footnotes (v1.5)

> **Reader gain (Rule 36)**: by stripping the `[refs: i, j]` machine tags from claim and counter-evidence prose at render time and surfacing them as footnote-style source markers (e.g. `[1][3]`) tied to a `## Sources` block, the PM can read clean analyst prose without `[refs: 1, 4]` clutter, and still trace each sentence to a specific source in one click. Leaving raw `[refs: …]` tags in the article body looks like debug output; dropping them entirely loses the traceability PM explicitly asked for.

Drafter writes `claims[]` and adversary writes `counter_evidence_observed[]` with mandatory `[refs: i, j]` tail tags pointing into `source_research_ids[]` (1-based; `0` on counter-evidence = adversary self-observation; conventions defined in [`research-thesis-drafter SKILL §Inline source ref convention`](../research-thesis-drafter/SKILL.md#inline-source-ref-convention--refs-) and [`research-thesis-adversary SKILL §Inline source ref convention`](../research-thesis-adversary/SKILL.md#inline-source-ref-convention--refs--counter_evidence_observed-mandatory)). When a thesis prose passage from `thesis_notes/<thesis_id>.json` flows into the article body via the package's `## Theses (selected)` block, the maintainer should:

1. **Strip the literal `[refs: i, j]` tag from the rendered sentence.** The article body should read as analyst prose, not as a debug payload.
2. **Surface the same indexes as footnote markers** at the end of that sentence in the article, e.g. `... real-rate compression and the central-bank-posture channel jointly support a non-recessionary equity advance. [1][4]`. Use `[<i>]` per index, no spaces, in original order.
3. **Add a `## Sources` (or `## 引用资料`) block** at the bottom of the report listing every footnote index in numeric order, mapping `[<i>]` to a one-line human-readable description of `source_research_ids[i-1]` (e.g. `[1] Capital Flows 2026-04-10: PCE / real rates / melt-up setup`, `[4] FRED DGS1 2026-04-09 series`). For `[0]` (adversary self-observation, only on counter-evidence), the line reads `[0] adversary 自有观察 (不绑定单一外部 source)`.
4. Index numbering in the article body must match `source_research_ids[]` order in the underlying thesis_note. If a single article cites multiple thesis_notes whose `source_research_ids[]` arrays differ, the maintainer can either (a) maintain a per-thesis footnote namespace (clearest, recommended) or (b) merge into one global `## Sources` block with renumbered indexes (more readable but requires re-tagging; only do this when the source overlap is high).

Edge cases:

- If the underlying claim's `[refs: …]` tag references an index that does not exist in `source_research_ids[]` (drafter or adversary bug), do NOT silently fix it. Strip the tag, surface no footnote for that sentence, and add a `[reviewer-flag]` margin note when handing back so research-theme-report-reviewer Layer 0 check 8 can route back upstream.
- If a quoted thesis_note prose passage gets paraphrased / compressed in the article, keep the source indexes pointing to the same factual support as the original; do NOT drop refs just because the sentence got shorter.
- The `## Sources` block is part of the article body and is read by PM; do NOT confuse it with the package's machine-readable `metadata.source_research_ids[]` list (which lives in the package frontmatter and is consumed by the writer pipeline, not by PM).

## Merge And Rebuild Rules

If the user says `merge`, treat that as approval of the current draft unless they explicitly scope it otherwise.

Before merging, confirm that `theme_update_drafts/<theme_id>.review.json` exists for the current pass and `verdict.status` ∈ {`accept_as_is`, `accept_with_revisions` (with every `required_revisions` item already applied to the DS file)}. If neither holds, do not merge; route back to `research-theme-report-reviewer` (or to `research-theme-report-owner` if reviewer returned `needs_rewrite`).

Default merge behavior:

- overwrite `themes/reports/<theme_id>.md` with the approved `theme_update_drafts/<theme_id>.ds.md`
- update `themes/metadata/<theme_id>.json` to match the approved report
- delete `theme_update_drafts/<theme_id>.package.md` after the merge
- archive `theme_update_drafts/<theme_id>.review.md` + `.review.json` alongside the merged report (do not delete; they are the audit trail for this pass)
- run `python src/tools/build_theme_indexes.py`

Use selective/manual merge only when the user explicitly asks to merge part of a draft or preserve specific existing sections.

## Failure Signals (task-flow-level, during execution)

These describe pathology **during** the curation pass, distinct from §Detection-side artifact-level violations (which describe wrong shape **after** the artifact lands):

- F1. `report mode` started drafting before the package sufficiency gate produced a `ready_to_write` or `need_more_detail` verdict
- F2. `knowledge mode` and `report mode` ran together in one pass without finishing knowledge mode first (cross-mode invariant violated; see §What This Skill Does)
- F3. Package body is mostly abstract summary instead of source-bearing material (raw notes, raw tables, raw price checks, raw verification output)
- F4. Report prose contains internal workflow labels (`subtheme`, `company thesis`, `reusable abstraction`, `[refs: i, j]`, `external verification:` etc.) that should have been stripped or rephrased before client-facing render
- F5. Public verification was needed but the report states unconfirmed facts as settled (verifier-line `partial` or `pending` collapsed to absolute claims in prose)

## Guardrails (hard prohibitions, each with explicit detection counterpart)

These are the must-not-do rules. Each rule names where its violation surfaces in §Detection-side or §Failure Signals so the agent can self-check after the fact:

- G1. Do not hand-edit `index.json` or `current_priority_tree.json` (counterpart: §Detection-side D5)
- G2. Do not fetch external evidence unless the user explicitly asked (no §Detection or §Failure counterpart; this is a pure prohibition, violation surfaces only by post-hoc network-trace audit)
- G3. Do not blur curation work (knowledge / package) with ranking work unless the user asked for both (counterpart: §Detection-side D4)
- G4. Do not treat this skill as the final writer when the real task is package-to-prose handoff (counterpart: §Failure Signals F1)
- G5. Do not mix knowledge mode and report mode in one pass (counterpart: §Failure Signals F2; cross-mode invariant in §What This Skill Does)

## Example Triggers

- “update this theme from local research”
- “把这个 theme 的 thesis 刷新一下”
- “fold this report into the theme report”
- “refresh subthemes and linked theses”
- “use archive plus web to update the theme”
