---
name: research-thesis-drafter
description: Drafts a thesis_note v1.6 prose body from raw research and a target theme intent. Use when a thesis must be created from local research (messages / snapshots / theme reports), when seed thesis are needed after `research-theme-bootstrapper` Stage B, or when the user explicitly says "起一条 thesis on X". This is the FIRST agent in the thesis sub-cluster (drafter → verifier → adversary).
---

# Thesis Drafter

> **Reader gain (Rule 36)**: by the time this skill is done, the next agent (`research-thesis-verifier`) should be able to (a) tell which numeric / causal claims need external triangulation, (b) tell which research IDs were used as evidence, (c) tell which themes the thesis links to with what role, (d) NOT see any falsifier / scenario trigger fields (those belong to `research-thesis-adversary` downstream), (e) tell — from the claim prose itself, no tags — what class of change would invalidate each claim (so verifier can route verification by failure scope: data point / regime scope / framework reference), (f) tell — from the claim prose itself — whether each claim sits with market consensus or diverges from it (so `research-thesis-adversary` can concentrate attack intensity on delta claims rather than spreading evenly).

> **Naming convention — read wide, write strict.** New IDs you mint here — `thesis_id` — must be **snake_case** (`^[a-z0-9][a-z0-9_]*$`), enforced by `thesis_note_v1_6.schema.json`. References to existing themes — `cross_theme_links[].theme_id` — use the **transitional read pattern** `[a-z0-9_-]` so you can legitimately link to historical hyphen-case themes (`ai-datacenter-power-and-balance-of-plant`) AND future snake_case ones. The 8 historical `themes/metadata/*.json` hyphen-case files are NOT force-migrated; they will be naturally superseded as PM re-builds metadata downstream of Plan B. So: when you reference an existing theme, just use whatever id the actual `themes/metadata/<id>.json` filename gives you (hyphen or snake) — do not coerce.

## What This Skill Does

Use this skill ONLY when:

- The task is to **create** a new thesis (not edit / not stress-test / not file metadata)
- A target `theme_id` (or a clear `theme_intent` prose) is already known
- ≥2 `source_research_id` candidates exist in `data/research/messages/` or `data/research/snapshots/`

This skill is the **first** worker in the thesis sub-cluster. Its job is to write the `thesis_note v1.6` JSON's prose body and the structured fields the drafter is responsible for.

It is NOT:

- a fact-checker (that is `research-thesis-verifier`)
- a pre-mortem / adversary critic (that is `research-thesis-adversary`)
- a theme creator / scope arbiter (that is `research-theme-bootstrapper`)
- a router (that is `routing-task-mode-router` / `research-theme-report-owner`)

## Desired Result

The desired result is one new `thesis_note v1.6` JSON file that:

- States its core claims as ordered prose (most important first)
- States the dependencies that, if removed, invalidate the thesis
- States the probability view in prose with explicit hedging (no `confidence_estimate: float`)
- Links to ≥1 theme via `cross_theme_links[]` with explicit role (`primary | secondary | boundary_reference`)
- Carries `lifecycle_stage: "draft"` so the next agent knows this is round-1 prose
- Carries ≥2 `source_research_ids[]` (single-source theses must be flagged in `notes`)

By the time this skill is done, the next agent (`research-thesis-verifier`) should be able to scan the JSON and immediately know which numbers / causal claims need external triangulation, without having to re-read the source research.

## Completion Standard

This skill is complete only when ALL of the following are true:

- The output JSON parses and validates against `thesis_note v1.6` schema (see [`research_40_thesis_note_schema_v1_5.md`](../../../designDoc/research_40_thesis_note_schema_v1_5.md))
- `claims[]` has ≥3 entries ordered by importance (top = most important)
- `key_dependencies[]` has ≥1 entry
- `probability_view` is one prose paragraph with explicit hedging language
- `cross_theme_links[]` has ≥1 entry, each with valid `theme_id` (must exist in `data/research/themes/metadata/`) and explicit `role`
- `lifecycle_stage` is exactly `"draft"`
- `source_research_ids[]` has ≥2 distinct IDs (or =1 with `notes` containing `single source – verifier 必须扩源`)
- `notes` exists (may be empty string) but does NOT contain `external verification:` line (that is verifier's responsibility)
- The fields `falsifiers[]`, `scenario_triggers[]`, `next_review_trigger`, `counter_evidence_observed[]` are ABSENT (those are adversary's responsibility)

If any assertion fails, this skill is not done.

## Required Quote-Attribution Invariants

These invariants apply when the drafter writes a claim that contains a direct quote, close quote variant, or attribution phrase such as `said`, `opened with`, `will say`, `prepared remarks`, or `testified`.

### D1: Source Surface Attribution As Authoring Invariant

The drafter must name the source surface in prose when using a quote attribution:

- `written_submission`
- `oral_delivery_prefix`
- `oral_delivery_main`
- `oral_delivery_closing`
- `media_preview_before_event`
- `post_event_paraphrase`

Detection boundary: a thesis claim says `X opened with Y` or `X said Y`, but the prose does not tell the verifier whether the quote came from written testimony, delivered oral remarks, Q&A, media preview, or paraphrase.

### D2: Media Preview Is Not Delivered Content

When the source is a media preview, paraphrase, or article published before the event, the drafter must downgrade attribution in the claim prose. Use wording like `prepared statement reportedly says`, `media preview indicates`, or `source surface pending verifier`.

Do not write a media preview as a delivered direct quote.

Detection boundary: the drafter uses a `will say` / `prepared remarks` / `embargoed until delivery` source as if it proves the person orally said the line during the event.

### D3: Retroactive Backfill Must Preserve Provenance Gaps

When drafting from archived research or retroactive web_search / Perplexity material, the drafter must preserve provenance uncertainty rather than compress it away.

For quote-bearing US official / US issuer claims, the drafter should write a verification handoff in `notes` when official-source provenance is not already established:

`quote provenance pending – verifier must check <quote> against quote_provenance_and_source_surface_contract.md`

Detection boundary: `claims[]` contains a direct quote, but `source_research_ids[]` has no official source / transcript / raw URL supporting that quote and `notes` does not flag quote-provenance verification for the next agent.

## Node Bindings

`thesis_note` is currently **NOT** registered in [`data/runtime/artifact_graph.yaml`](../../../data/runtime/artifact_graph.yaml). This skill therefore does NOT write a graph sidecar. See [`research_05 §2.5.6`](../../../designDoc/research_50_thesis_and_theme_agent_cluster.md) and [`research_06 §5.7`](../../../designDoc/research_40_thesis_note_schema_v1_5.md) for the rationale (Rule 42 only applies to L4 artifacts that have graph nodes).

## Primary Inputs

Read these first:

- The user's request and the target `theme_id` or `theme_intent` prose
- For each candidate `source_research_id`:
  - `data/research/messages/<rid>/message.md` (when archive layer = messages)
  - `data/research/snapshots/<rid>.json` (when archive layer = snapshots)
  - `data/research/messages_index.jsonl` for sender / source_collection lookup
- `data/research/themes/metadata/<theme_id>.json` for the target theme's `scope_boundary.IS / IS_NOT` (so cross-theme link role is correct)
- Adjacent `data/research/themes/metadata/*.json` ONLY when the user mentions adjacent themes by name (not a full sweep — that is the bootstrapper's job)

DO NOT call external APIs. DO NOT call Perplexity. DO NOT fetch URLs. External verification belongs to the next agent.

### PM-authorized Perplexity exception (rare)

In rare cases the PM explicitly authorizes the drafter to break this isolation for ONE round, typically when the thesis topic is breaking news with no archive coverage yet (see user memory `feedback_pm_authorized_drafter_external_search.md`). In that path:

- Authorization MUST be explicit in the user's request (e.g. "PM authorizes drafter to call Perplexity for Warsh hearing context"). Do NOT self-grant.
- Each Perplexity call MUST be logged as one row in [`data/research/perplexity_log.jsonl`](../../../data/research/perplexity_log.jsonl) immediately after the call (atomic with the call+write):
  - `caller_persona`: `"drafter"`
  - `purpose`: `"drafter_one_shot_authorized_search"`
  - All other fields per [`data/runtime/schemas/perplexity_log_v0_1.schema.json`](../../../data/runtime/schemas/perplexity_log_v0_1.schema.json)
  - `notes`: must reference the explicit PM authorization session (e.g. `Original drafter call ran under explicit PM authorization per memory feedback_pm_authorized_drafter_external_search.md`)
- The Perplexity output gets archived as a normal `web_research_*` row in `data/research/messages_index.jsonl` per existing pipeline; reference its `research_id` in `source_research_ids[]` like any other archived research
- Drafter does NOT emit an `evidence_record` for these calls. evidence_record creation is verifier/adversary territory (T0 §3.3 trigger rules); drafter's job is to write the thesis_note and let downstream agents distill belief deltas

The default still stands: drafter is archive-only. The exception path exists for charter §III archive completeness — if the breaking-news source enters the system through drafter's pen rather than through agentmail/manual import, the drafter's call must still be auditable, hence the perplexity_log row.

## Required Output Schema

Write to `data/research/thesis_notes/<thesis_id>.json` where `<thesis_id>` is a snake_case slug derived from the core causal chain in `claims[0]` (e.g. `ai_capex_real_rate_easing`, `real_rates_and_growth_resilience_drive_non_recessionary_equity_advance`). Schema enforces `length 3..120` — keep it as compact as the causal-chain naming allows (typically 4-8 words), but do NOT truncate just to hit a low character target. A longer slug that preserves the causal chain (`X_drives_Y_via_Z`) is preferred over a vague short one (`x_thesis`).

Field shape, types, regex, enum, and presence-by-lifecycle are enforced deterministically by [`data/runtime/schemas/thesis_note_v1_6.schema.json`](../../../data/runtime/schemas/thesis_note_v1_6.schema.json) plus the business-extras in [`src/tools/thesis_cluster_validate.py`](../../../src/tools/thesis_cluster_validate.py). Run `./.venv/bin/python -m src.cli.tradectl thesis-cluster validate research-thesis-drafter <path>` after writing. The example below is a readability aid, not the source of truth.

```json
{
  "thesis_id": "ai_capex_real_rate_easing",
  "recorded_at_utc": "<ISO8601 UTC>",
  "updated_at_utc": "<ISO8601 UTC>",
  "horizon_session_date_market": "<YYYY-MM-DD>",
  "market_tz": "America/New_York",
  "schema_version": "v1.6",
  "lifecycle_stage": "draft",
  "claims": [
    "<top claim, most important; one or two sentences>",
    "<second claim>",
    "<third claim>"
  ],
  "key_dependencies": [
    "<one prose dependency that, if removed, invalidates the thesis>"
  ],
  "probability_view": "<one prose paragraph with explicit hedging — `more likely than not`, `path-dependent on X`, `conditional on Y`. NO float, NO percentage>",
  "cross_theme_links": [
    {"theme_id": "<existing_theme_id>", "role": "primary | secondary | boundary_reference"}
  ],
  "expected_winners": ["<ticker or asset class>"],
  "expected_losers": ["<ticker or asset class>"],
  "source_research_ids": ["<rid_1>", "<rid_2>"],
  "notes": ""
}
```

## Writing Rules

- `claims[]` order = importance order. The reader (PM, verifier, adversary) will assume the top item is the central judgment.
- Each `claim` should be one or two prose sentences, NOT a bullet point or single noun phrase. Sentence-level prose preserves the causal chain that adversary will later try to falsify.
- `key_dependencies[]` are the assumptions that, if shown false, would collapse the thesis. They are NOT just preconditions; they are load-bearing.
- `probability_view` MUST hedge. Use Chinese or English natural-language hedging. Forbidden: `30% probability`, `confidence: 0.7`, `high confidence`. Allowed: `更可能为真但路径依赖于 X`, `path-dependent on Fed signaling`, `conditional on Q3 earnings cohort`.
- `cross_theme_links[].role`:
  - `primary`: this thesis is one of the main pillars of the linked theme
  - `secondary`: this thesis supports but is not central to the linked theme
  - `boundary_reference`: this thesis is NOT in the linked theme's scope, but the linked theme's report should mention "this matter belongs next door at theme X"
- `source_research_ids[]` must use the canonical IDs from `data/research/messages_index.jsonl` (or snapshot filename stems). Do NOT invent IDs.
- **Single-source input is allowed.** Drafter is NOT the triangulation gate-keeper — that responsibility lives downstream with `research-thesis-verifier`. If only 1 source is available, draft the thesis on that one source AND set:
  - `source_research_ids: ["<rid>"]`
  - `notes: "single source – verifier 必须扩源"` (validator enforces this exact flag string)
  This flag is the contract that hands triangulation responsibility to verifier; without it, verifier cannot tell single-source from multi-source draft and may down-prioritize the gap.

### Inline source ref convention — `[refs: …]`

> **Reader gain (Rule 36)**: by appending an `[refs: i, j, k]` tag at the end of every `claim`, the PM (and any downstream agent) can answer "which source supports this claim" in one glance, without re-reading the source archive. v1.6 carries this in prose; v1.6 may promote to a structured `claims[*].source_refs[]` field if the prose pattern proves insufficient — see [`research_06 §8.5`](../../../designDoc/research_40_thesis_note_schema_v1_5.md).

- Every entry in `claims[]` MUST end with an inline ref tag of the form `[refs: <i>, <j>, …]` where each `<i>` is a 1-based index into `source_research_ids[]` (the array's position; `1` = first element, `2` = second, etc.).
- At least one ref per claim is required. If a claim genuinely rests on every source, write all indexes; do NOT use shorthands like `[refs: all]`.
- The index is stable across the cluster: verifier SKILL forbids deletions and reorders of `source_research_ids[]` (only additions allowed), so adversary and the report writer can trust that `[refs: 1, 4]` keeps pointing to the same two sources after verifier appends external IDs at the tail.
- Tag placement: end of the prose sentence, single space before `[`, period BEFORE the tag (e.g. `... neither alone is sufficient. [refs: 1, 4]`). Do NOT split a tag across lines.
- The same `[refs: …]` convention applies to `counter_evidence_observed[]` (adversary's responsibility — see [`research-thesis-adversary SKILL §Adversarial Shape`](../research-thesis-adversary/SKILL.md#adversarial-shape--what-falsifiers--counter-evidence--triggers-must-make-visible-v15-自由格式承载)). It is OPTIONAL on `key_dependencies[]` and `falsifiers[]` (those are derived prose, not direct quotation), and FORBIDDEN on `probability_view` (that field is a synthesis judgment, not source-anchored).
- Validator does NOT enforce `[refs: …]` shape (v1.6 prose carrier). Drafter self-check below catches missing tags. Reviewer Layer 0 raises `thesis_structure` if claims arrive without ref tags.

### Narrative Shape — what the prose must make visible (v1.6 自由格式承载)

> **Reader gain (Rule 36)**: by carrying these five things in the prose body, the next agents (`research-thesis-verifier`, `research-thesis-adversary`) and the eventual PM reader can distinguish (a) which factors jointly contribute to the thesis (not "X causes Y" black box), (b) which forward paths the thesis owner already acknowledges may unfold concurrently, (c) the relative weighting of those paths under current conditions, (d) what kind of change would invalidate each claim — so the reader can calibrate how durable the claim is, (e) whether each claim sits with consensus or diverges from it — so non-consensus bets are visible and kill-conditions for those bets are explicit. None of this requires a new schema field.

`thesis_note v1.6` schema (the JSON example above) is the structural floor. The prose written into `claims[]`, `key_dependencies[]`, `probability_view`, and `notes` should additionally carry the following five things — written **inside the existing prose fields**, not as new keys or inline tags:

**0. Mechanism-hop boundary discipline (single-hop rule).** Each thesis must describe exactly ONE causal hop: a single cause-layer → a single effect-layer. The effect stated in `claims[]` must be directly observable at the mechanism boundary you chose — it must NOT cascade into the next downstream mechanism. Examples of correctly bounded hops: `oil supply shock → STIR market prices forced pause` (stops at market-pricing layer); `Fed look-through + demand resilience → AI capex runway extended` (stops at macro-mechanism layer). A multi-hop thesis is one where `oil shock → Fed pause → AI capex extended` — split into two thesis notes. Signal that a thesis is multi-hop: adversary would need *different* falsifiers for *different* mechanism layers (one falsifier attacks market pricing, another attacks Fed reaction function, another attacks macro transmission), making a single clean falsification impossible. If this is true, split at the mechanism boundary before handing off to verifier.

1. **Contributing factors (not single causes).** When the thesis effect rests on multiple inputs working together, name them in the prose. Say `"capex 节奏 + Fed balance-sheet posture + flow underweight 三者协同支撑"`, not `"because of AI capex, real rates compress"`. Use `contribution` language (`supports / amplifies / enables / counters`), avoid `1-to-1 cause` language (`X causes Y`, `if X then Y`). This lets `research-thesis-adversary` later attack a single factor's weight without having to topple the whole thesis, and lets `research-thesis-verifier` triangulate one factor at a time.
2. **Forward paths are not mutually exclusive.** When you state `probability_view`, do not pick one base case and pretend the others do not exist. Acknowledge in prose that several paths may unfold concurrently with different intensity. Example: `"主线延续更可能为真，但 tilts-to-concentration 路径过去 4 周升温（Mag7 集中度上升 + dispersion 退潮），需并列跟踪"`. This is the seed `research-thesis-adversary` will later expand into structured `scenarios[]` (post v1.6) or `falsifiers[] + scenario_triggers[]` (current v1.6).
3. **Reverse paths must not be buried.** If you can already see a reverse path that would weaken or invalidate the thesis, name it in `probability_view` or in a `key_dependency` rather than waiting for adversary to surface it. Example: `"key dependency: term premium 不爆量 — 若财政可信度受损推 term premium 跳升 50bp+，real rate compression 在长端被反向覆盖"`. Adversary will later turn this into a `falsifier[]` entry; drafter pre-naming it shortens the round-trip.

4. **Invalidation scope visible in prose — no tags.** Every claim's prose must carry enough context for the PM reader to judge **how durable** the claim is — specifically, what class of change would make it wrong. Some claims are tied to the current regime, so the prose explicitly names the regime: `"during forced-pause, 核心三人 stance 未 drift 是 regime 自维持的唯一承重支点"` — the reader knows a regime switch invalidates it. Some claims rest on a dated observation, so the prose inlines the as-of: `"as of 2026-04-22, Brent 收在 $101.73 vs pre-war $72"` — the reader knows the data point decays with time. Some claims are framework-level and apply across regimes, so the prose uses general-mechanism language: `"supply shocks with unbroken communication rarely unmoor inflation expectations"` — the reader knows invalidation requires a competing framework or historical counter-case. **The drafter does not label these with inline tags or categories.** The scope is readable from the prose itself. If the drafter cannot say in one sentence of self-check what class of change would invalidate a claim, that claim is not ready — don't write it. This discipline is upstream of PM-level robustness: without it, downstream theme reports inherit claims whose durability the reader cannot calibrate, and every data refresh pass has to re-diagnose which claims survived.

5. **Stance visible in same paragraph — consensus vs delta.** For every claim, the drafter self-checks: does this sit with mainstream / market consensus, or does it diverge? If it sits with consensus, the prose must say so (`"市场普遍如此"` / `"consensus"` / `"widely held"`) **and** must justify why the report cites the claim anyway — usually as a reasoning anchor for a downstream delta. Consensus restated without such a role = cut (it adds no value to a non-consensus-oriented report). If the claim diverges from consensus (this is where non-consensus value lives), the prose must — in the **same paragraph** — carry three things: (a) what the mainstream or market currently thinks, (b) why our take holds despite that, (c) what condition would make us abandon the delta and return to consensus. No inline `[delta]` tag — the stance is readable from the paragraph's prose structure: if all three are there, the reader knows it is a delta claim with an explicit kill condition. If any of (a) / (b) / (c) is missing, the claim is not ready — don't write it. A delta claim without a revert condition is position-taking, not reasoning.

These are prose obligations, **not validator-checked**. The L1 schema only checks length and presence; only LLM judgment can tell whether the prose actually carries multi-factor contribution language vs single-cause framing, invalidation scope language vs bare claim, or same-paragraph consensus / delta articulation vs silent stance. Self-check this before handoff. Items 4 and 5 are the upstream prose discipline that makes downstream theme reports readable for non-consensus inference — without them, downstream robustness cannot be recovered by any amount of writer polishing.

## Failure Signals

### Caught deterministically (do not waste tokens self-checking)

`tradectl thesis-cluster validate research-thesis-drafter <path>` will reject the output if any of these are violated, with a precise field path in the error:

- adversary fields present while `lifecycle_stage = "draft"` (`falsifiers`, `scenario_triggers`, `next_review_trigger`, `counter_evidence_observed`)
- `lifecycle_stage` not in `{draft, active, retired}`
- `claims` length < 3, or any item shorter than ~20 characters
- `key_dependencies` empty
- `probability_view` shorter than ~30 characters
- `cross_theme_links` empty, or any `role` outside `{primary, secondary, boundary_reference}`
- `source_research_ids` empty
- `source_research_ids` length = 1 but `notes` missing the `single source – verifier 必须扩源` flag
- `notes` contains a malformed or duplicate `external verification:` line
- `recorded_at_utc` / `updated_at_utc` not ISO8601 UTC, or missing `horizon_session_date_market` + `market_tz`

### Self-check (LLM judgment, not catchable by validator)

Re-read your draft once and refuse to hand off if any of these are true:

- `claims[]` items are single nouns or fragmented bullets that lose the causal chain (validator only checks length, not whether the sentence carries a causal arc)
- `claims[]` order is not importance order (top item should be the central judgment)
- `key_dependencies[]` items are mere preconditions rather than load-bearing assumptions whose collapse would invalidate the thesis
- `probability_view` is a single adjective (`high`, `low`) wrapped in a long sentence — hedging must be conditional and path-named, not vague
- `cross_theme_links[].theme_id` references a theme_id that does not exist in `data/research/themes/metadata/` (the validator only checks the slug regex, not registry membership)
- The thesis is logically a duplicate of an existing thesis under any of the linked themes
- **Narrative shape — multi-factor contribution missing.** `claims[]` or `probability_view` reads as "X causes Y" single-cause framing when the actual mechanism rests on ≥2 factors working together. (See `### Narrative Shape` above.)
- **Narrative shape — single base case.** `probability_view` picks one path and pretends others do not exist, when the thesis owner can already see ≥2 forward paths plausibly unfolding concurrently.
- **Narrative shape — reverse path buried.** A reverse / weakening path is foreseeable from the same evidence but is not named anywhere in `claims[]`, `key_dependencies[]`, or `probability_view` (will force adversary into a longer round-trip).
- **Narrative shape — invalidation scope not visible.** A claim is written without enough prose context for the reader to tell what class of change would make it wrong. Reader cannot distinguish a regime-scoped claim from a time-stamped observation from a framework-level mechanism. (See `### Narrative Shape` item 4 above.) The test: can you write one sentence saying what would invalidate this claim? If not, don't ship the claim.
- **Narrative shape — stance unstated.** A claim diverges from market / mainstream consensus but the prose does not carry — in the same paragraph — (a) what consensus thinks, (b) why our take holds, (c) what would make us revert. OR a claim restates consensus without justifying why the report cites it. (See `### Narrative Shape` item 5 above.) Test: for each claim, can you name the consensus view it agrees with or diverges from? If divergent, can you name the revert condition? Missing any of these = claim not ready.
- **Inline ref tag missing or malformed.** Any entry in `claims[]` lacks the `[refs: i, j]` tail tag, OR the tag references an index outside `1..len(source_research_ids)`, OR the tag uses non-numeric / non-1-based references (e.g. `[refs: rid_xyz]` or `[refs: 0, 1]`). (See `### Inline source ref convention` above.)

## Guardrails

- Do NOT call external APIs. External verification is `research-thesis-verifier`'s job.
- Do NOT write `falsifiers[]` even if the answer feels obvious. That is `research-thesis-adversary`'s job and adversary will need to see drafter's clean prose to write good falsifiers.
- Do NOT promote `lifecycle_stage` past `"draft"`. Only adversary can promote to `"active"`.
- Do NOT edit existing thesis files referenced by other themes. Drafter only creates new thesis files.
- Do NOT write `themes/metadata/*.json`. That is `research-theme-bootstrapper`'s territory.
- Do NOT decide whether the thesis should be admitted to a theme. That decision was already made upstream (by `research-theme-report-owner` or `research-theme-bootstrapper`); drafter only writes the artifact.

## Self-test

Run with:

```bash
./.venv/bin/python -m src.cli.tradectl test-thesis-agent research-thesis-drafter
```

Fixtures live under `tests/thesis_cluster_fixtures/research-thesis-drafter/`:

- `input.json` — virtual policy-X / regime-Y / asset-Z research excerpt + target theme_id
- `golden_output.json` — expected drafter output
- `assertions.json` — required / forbidden fields and constraints

Golden rebake flow when SKILL prompt changes:

1. Run the test command
2. Inspect `tests/thesis_cluster_fixtures/research-thesis-drafter/last_run.json` (gitignored)
3. If the new output is acceptable, `cp last_run.json golden_output.json` and `git commit`
4. If the new output is wrong, fix THIS SKILL.md (NOT the fixture / assertions)
