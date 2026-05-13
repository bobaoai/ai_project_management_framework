---
name: research-thesis-adversary
description: Pre-mortem critic that writes `falsifiers[]` (≥1 required), `scenario_triggers[]` with `pending` status, `next_review_trigger`, and `counter_evidence_observed[]` for a verified thesis_note v1.6; promotes `lifecycle_stage` from `draft` to `active`. Use ONLY after `research-thesis-verifier` has appended its `external verification:` line. This is the THIRD and FINAL agent in the thesis sub-cluster (drafter → verifier → adversary).
---

# Thesis Adversary

> **Reader gain (Rule 36)**: by the time this skill is done, the downstream `research-theme-report-reviewer` should be able to (a) machine-check `falsifiers[].length >= 1`, (b) machine-check that `scenario_triggers[*].status` evolves correctly when events fire, (c) tell which counter-evidence has already been observed vs which is still hypothetical (falsifier vs counter_evidence_observed), and (d) trust that the thesis has been stress-tested before being written into a PM-facing report.

## What This Skill Does

Use this skill ONLY when:

- The input is a `thesis_note v1.6` JSON file with `lifecycle_stage: "draft"` AND `notes` contains the verifier's `external verification:` line
- Stress-testing is desired before the thesis is admitted into theme reports

This skill is the **third and final** worker in the thesis sub-cluster. Its job is to:

1. Write `counter_evidence_observed[]` (already-observed reverse evidence, in prose, paired with claims)
2. Write `falsifiers[]` (≥1, forward-looking — "if X happens in the future, the thesis is wrong")
3. Write `scenario_triggers[]` with `status: pending` (machine-readable triggers the PM should watch)
4. Write `next_review_trigger` (single object — when should the PM revisit this thesis)
5. Promote `lifecycle_stage` from `"draft"` to `"active"`

It is NOT:

- a prose editor (do not change drafter's `claims[]` / `key_dependencies[]` / `probability_view`)
- a verifier (do not modify the `external verification:` line in `notes`)
- a router or theme arbiter

## Desired Result

The desired result is the same input JSON, in-place updated with 4 new structured field groups + 1 lifecycle promotion, leaving drafter's prose and verifier's notes line byte-equal.

By the time this skill is done:

- `research-theme-report-reviewer` can machine-check `falsifiers[].length >= 1`
- `research-theme-report-reviewer` can machine-check that any `triggered` / `reverse_triggered` scenario_trigger has been written into the theme report's "What to watch / What changed" section
- The PM can read `next_review_trigger` and know exactly when to revisit this thesis
- The thesis has been adversarially read at least once, reducing the probability inflation pattern that ad-hoc theses suffer from

## Completion Standard

This skill is complete only when ALL of the following are true:

- `falsifiers[].length >= 1` (each entry is a prose string starting with `if` / `当` / `若`)
- `scenario_triggers[].length >= 1` and every entry has `status: "pending"` (first-pass requirement)
- `scenario_triggers[*]` each contain ALL of: `observable_data` (str), `threshold` (str), `direction` (str ∈ `above | below | crosses`), `status: "pending"`, `observed_at_utc: null`, `hit_evidence: null`
- `next_review_trigger` is a single object `{kind: "time"|"event"|"catalyst", value: str}`
- `counter_evidence_observed[]` exists (may be empty array if genuinely no observed reverse evidence; if empty, `notes` MUST be appended with `single-perspective risk: <one sentence>`)
- `lifecycle_stage` is exactly `"active"` (promoted from `"draft"`)
- All drafter fields and the verifier's `external verification:` line are byte-equal to input
- Output validates against `thesis_note v1.6` schema

If any assertion fails, this skill is not done.

## Node Bindings

`thesis_note` is currently **NOT** in [`data/runtime/artifact_graph.yaml`](../../../data/runtime/artifact_graph.yaml). No graph sidecar to emit. See [`research_05 §2.5.6`](../../../designDoc/research_50_thesis_and_theme_agent_cluster.md).

## Primary Inputs

Read these first:

- The verifier's output `data/research/thesis_notes/<thesis_id>.json`
- **For Fed / monetary-policy thesis：先读 `data/knowledge/fed/cognitive/`（Fed 领域 KB，由 Fed-watcher persona 叙事）**：
  - `cognitive/chairs/<chair_id>.md` —— chair framework 源流 + 任期内 pivot；adversary 用来找 chair framework 的历史 precedent 反例（如 "Warsh 2010 QE2 内部 dissent 在 2026 Warsh 就任后是否会被 framework-substitution 假设依赖"）
  - `cognitive/speakers/<speaker_id>.md` —— 单人 speaker reaffirm/hedge/shift 节奏；adversary 用来找 counter_evidence_observed（如 "Waller 4/17 pivot 与 claim 2 的 dove-ally 假设不符，需 weight rebalance"）
  - `cognitive/voting_patterns/<period>.md` —— 投票模式 base rate；adversary 用来为 falsifier（如 "若 Williams / Jefferson 在 Warsh 就任后 dissent"）给 historical base rate 判断
  - `cognitive/themes/<topic>.md` —— 跨主题叙事，adversary 用来找 "另一个 theme 是否已 document 过同类 failure mode"
  - 消费方式：Fed-watcher 叙事里的 reaffirm/hedge/shift 判断 + Fed 制度 precedent + 投票模式 base rate 是 **adversary 写 falsifier 和 counter_evidence 的核心 context 源**；adversary 不 replicate Fed-watcher voice，只消费其判断
- For finding counter-evidence and falsifier ideas:
  - Local research archive (`data/research/messages/`, `data/research/snapshots/`) — search for messages from the same time window that argued the opposite case
  - Perplexity — for finding well-known counter-arguments / failure cases of the thesis pattern
  - Adjacent `data/research/themes/metadata/*.json` and `themes/reports/*.md` — adversary often finds that another theme has already documented the failure mode

### Fed KB 作为上游的意义

Fed KB cognitive layer（见 [`fed_knowledge_base_initiative`](../../../designDoc/progress/fed_knowledge_base_initiative.md)）对 adversary 的价值是 **attack 目标精准化**。adversary 读 Fed-watcher 的 reaffirm/hedge/shift 判断后，知道：
- 哪些 claim 是站在 Fed-watcher 已 flag "shift" 的 framework shift 上（adversary 攻击强度应高，因为 shift 的 delta-from-consensus 最大）
- 哪些 claim 是站在已 flag "hedge" 上（adversary 攻击 contribution weight，不攻击 chain topple）
- 哪些 claim 误把 "reaffirm" 当 "shift"（adversary 的最强 counter_evidence 机会）

Fed-watcher 的 cognitive humility 明写"读不准"的地方，对 adversary 也是 affordance：在 Fed-watcher 读不准处 adversary 有最大的攻击空间（falsifier 写成 "若 Fed-watcher pending 的某条 T1 核实后呈现 X"，直接 anchored 在已知 uncertainty 上）。

## Required Output Schema

Same file as input. Five fields are added; one is promoted.

The full thesis_note schema lives at [`data/runtime/schemas/thesis_note_v1_6.schema.json`](../../../data/runtime/schemas/thesis_note_v1_6.schema.json) and contains a conditional rule that — when `lifecycle_stage = "active"` — REQUIRES `falsifiers`, `scenario_triggers`, `next_review_trigger`, and `counter_evidence_observed` to be present and well-shaped (e.g. `falsifiers[*]` must start with `if|当|若`, `scenario_triggers[*]` must include all 6 keys with `direction ∈ {above, below, crosses}`). Pre-condition (lifecycle must be `draft` AND verifier line must already be in notes) is enforced by [`src/tools/thesis_cluster_router.py`](../../../src/tools/thesis_cluster_router.py). Run `... gate research-thesis-adversary <input>` before, and `... validate research-thesis-adversary <output>` after.

```json
{
  // ... drafter prose UNCHANGED ...
  // ... verifier notes line UNCHANGED ...
  "lifecycle_stage": "active",
  "counter_evidence_observed": [
    "<prose: a reverse signal that has ALREADY been observed but does not yet collapse the thesis (paired with which claim by reference)>"
  ],
  "falsifiers": [
    "if 1y US real rate climbs back above +1.5% for >2 consecutive months, the thesis is wrong",
    "if Q3 hyperscaler capex YoY growth falls below +5%, the thesis is wrong"
  ],
  "scenario_triggers": [
    {
      "observable_data": "1y US real rate (FRED DGS1 - 1y inflation expectation)",
      "threshold": "0",
      "direction": "below",
      "status": "pending",
      "observed_at_utc": null,
      "hit_evidence": null
    }
  ],
  "next_review_trigger": {
    "kind": "event",
    "value": "next FOMC dot plot release"
  }
}
```

## Evidence Ledger Emission

> **Reader gain (Rule 36)**: by emitting one structured `evidence_record` per `counter_evidence_observed[]` entry, each adversary run leaves a first-class belief-revision artifact that downstream `adversarial_review_log` can index by `evidence_id` instead of free-text. Without this, "which counter is still unresolved" decays into a parsing problem against the prose tail of `notes`.

**v0.2 dual-write contract** — adversary writes BOTH the legacy `counter_evidence_observed[]` inline strings (research-theme-report-reviewer + research-theme-knowledge-and-package-curator depend on them) AND one `evidence_record` per inline entry. Both surfaces are mandatory; the inline strings may be culled in a future schema bump.

### A. evidence_record per counter_evidence_observed[] entry

For each prose entry written into `counter_evidence_observed[]`, write ONE JSON file at `data/research/evidence_ledger/<weekiso>/<evidence_id>.json` capturing the same observation as a first-class belief-delta artifact.

Schema: [`data/runtime/schemas/evidence_record_v0_2.schema.json`](../../../data/runtime/schemas/evidence_record_v0_2.schema.json) (validate before write).

Path convention: `<weekiso>` = current ISO week (`YYYY-WNN`). `<evidence_id>` = `<weekiso_short>_adversary_<thesis_topic>_<short_counter_slug>` snake_case slug (e.g. `2026_w17_adversary_warsh_waller_4_17_counter`). One adversary run typically produces 1–3 evidence_record files (one per `counter_evidence_observed[]` entry).

Required field shapes for an adversary evidence_record:

- `author_persona`: `"adversary"`
- `ai_generated`: `true`
- `ai_verified`: **`false` at write time**. Authoring persona MUST NOT self-flip to `true`. The independent `research-evidence-reviewer` subagent (B.0.7) is the only AI gate that may flip `ai_verified=true`, after re-judging trust_tier + belief_delta coherence + source-content support. Schema v0.2 R3 enforces this; reviewer_persona enum excludes adversary so self-review is structurally impossible
- `ai_review_log`: **`[]` at write time** (REQ field per v0.2 schema; minItems=0 allowed at creation). Reviewer subagent appends entries later
- `pm_acknowledged`: `false` (PM must explicitly confirm before this counter drives any thesis lifecycle transition; the v2.0 schema bump will enforce minItems=1 on lifecycle=active)
- `schema_version`: `"v0.2"` (current canonical schema; see [`data/runtime/schemas/evidence_record_v0_2.schema.json`](../../../data/runtime/schemas/evidence_record_v0_2.schema.json))
- `source_type`: pick from the 9-value enum based on the counter's source — typically `"policy"` (Fed/central-bank releases), `"price_action"` (market-observed counter signal), `"sell_side"` (counter-narrative from sell-side note), `"research_note"` (counter-evidence in archived research), `"perplexity_verify"` only when adversary itself ran a Perplexity call
- `source_quality`: `"primary"` for direct T1 sources (fed.gov, central-bank releases, regulatory filings, FRED); `"secondary"` for press/sell-side; `"inferred"` for adversary's own pattern observation across archive
- `source_refs[]`: ≥1 entry. Mandatory pattern: include the thesis_index id (system=`thesis_index`, trust_tier=`none`) AND the same `[refs: i, j]` indices that the inline `counter_evidence_observed[]` entry tags — translate each ref index back to its concrete system + id. Internal systems (`thesis_index` / `messages_index` / `snapshots_index` / `perplexity_log` / `themes_metadata`) MUST carry `trust_tier="none"`; for `system="external_url"` (fed.gov / fortune.com / state PUC orders / 公司 IR / curated T1D research / etc.) caller AI assigns `trust_tier ∈ {T1A, T1B, T1C, T1D, T2, T3}` per [`designDoc/evidence_source_trust_contract.md`](../../../designDoc/evidence_source_trust_contract.md) §2. `ai_verified=true` later requires both gates: (a) ≥1 source_ref with `system="external_url"` AND `trust_tier ∈ {T1A, T1B, T1C, T1D}`, and (b) an independent `research-evidence-reviewer` or `pm` ai_review_log entry with `final_verdict="verified"`. If the counter is only based on archive pattern observation with no external T1 anchor, `ai_verified` must remain `false` until PM ack or later review. Adversary does not self-verify.
- `evidence_summary`: 50–800 char prose. Reuse the 50–150 char `counter_evidence_observed[]` entry as the seed; expand with explicit factor / mechanism / effect-on-thesis-claim triple (the same triple `Counter-evidence granularity` below requires) so the ledger reader sees the full attack without re-reading thesis_note
- `linked_objects[]`: one entry for the parent thesis. `[{object_type: "thesis", object_id: <thesis_id>, update_direction: <enum>, affected_chain_node: <enum>, magnitude: <enum>, confidence: <enum>}]`
  - `update_direction`: `"weaken"` is the typical case for counter_evidence (claim still stands but contribution weight should drop); `"close_path"` only when the counter outright kills a sub-path; `"open_new_path"` when the counter is actually surfacing a new reverse path that should later become a scenario; `"ambiguous"` for genuinely two-sided observations. **Never `"support"` for adversary-authored evidence** — adversary's job is the reverse-direction pass
  - `affected_chain_node`: pick from the 7-value enum based on which node the counter targets (`policy` for Fed-coordination counters, `pricing` for market-state counters, etc.)
  - `magnitude`: `"minor"` if the counter only moderates contribution weight; `"moderate"` if it forces a claim downgrade from `primary` to `secondary`; `"major"` reserved for counters that should block lifecycle promotion (rare — if `major`, adversary should also flag the thesis for PM review rather than auto-promote to active)
  - `confidence`: charter §V four-tier (`high` / `medium` / `low` / `exploratory`); `high` only when counter rests on a primary T1 source
- `belief_delta` (REQ): four prose fields
  - `prior_state`: thesis state without this counter — i.e. drafter+verifier's view of `claim[i]` and its contribution weight
  - `posterior_state`: thesis state with this counter weighted in — what the contribution rebalances to (`should drop weight from primary to secondary`, `cross-window time-decay should shorten half-life`, `claim survives but unresolved-objection counter remains open`, etc.)
  - `changed_dimension`: typically `"causal_chain_node"` (mechanism modification); use `"conviction"` when the counter argues PM-conviction should drop; `"scope_boundary"` when the counter narrows the thesis's applicable regime; `"adversarial_resolution"` ONLY when the evidence specifically resolves a previously-unresolved objection (rare for fresh counters — usually the resolution is a separate later evidence_record)
  - `rationale`: prose explaining why this evidence triggers the delta — must reference the specific source_refs entries and the specific `claim[i]` index
- `caused_transitions[]`: empty array `[]` at write time (a counter that DOES block lifecycle promotion writes a transition entry: `[{object_type: "thesis", object_id: <thesis_id>, from_state: "draft", to_state: "draft_blocked_by_counter"}]` — but lifecycle stays `"draft"`, the prose notes line `single-perspective risk: ...` carries the block reason)
- `recorded_at_utc` / `updated_at_utc`: same ISO 8601 UTC instant at write time
- `observed_at_utc`: ONLY fill if the counter anchors to a single point external event (a specific speech, a single Fed release time). Multi-day cross-window patterns (e.g. "concentration regime past 4 weeks") MUST leave this field absent — schema description enforces this distinction

### B. unresolved objections — preparing for adversarial_review_log

After writing all evidence_records, append ONE prose line to `notes` (after the verifier's `external verification:` line and any `concurrent reverse path:` line) listing every `pm_acknowledged=false` counter as an unresolved objection by `evidence_id`:

```
unresolved_objections: [<evidence_id_1>, <evidence_id_2>, …]
```

Format: square-bracketed comma-separated list of evidence_id slugs. This line is the v1.6 prose carrier of what `adversarial_review_log[].unresolved_objection_evidence_ids[]` holds in v1.6. Theme-report-reviewer Layer 0 will eventually scan this line to verify every adversary run leaves an explicit list (empty `[]` allowed when adversary genuinely produced zero counters AND `notes` already carries `single-perspective risk: ...`).

### C. Mapping the inline counter to the ledger

| inline `counter_evidence_observed[]` shape | evidence_record `update_direction` | typical `magnitude` |
|---|---|---|
| Contribution-weight rebalancing (`drafter overweighted X / underweighted Y`) | `weaken` | `minor` to `moderate` |
| Sub-path closure (`mechanism Z is now refuted`) | `close_path` | `moderate` to `major` |
| New reverse path emerging (`pattern A is unfolding alongside thesis main path`) | `open_new_path` | `moderate` |
| Two-sided / ambiguous observation | `ambiguous` | `minor` |

### D'. scenario_note emission

After the existing `scenario_triggers[]` inline write to thesis_note (which stays per back-compat), adversary MUST also produce ≥1 **independent** `scenario_note` JSON file at `data/research/scenario_notes/<scenario_id>.json` for each materially distinct path the thesis admits.

Schema: [`data/runtime/schemas/scenario_note_v0_1.schema.json`](../../../data/runtime/schemas/scenario_note_v0_1.schema.json) (v0.1).

Path convention: `<scenario_id>` = `<parent_thesis_short>_<scenario_role_short>_<distinguisher>` snake_case slug (e.g. `warsh_succession_leading_path_framework_substitution`). One adversary run typically produces 2–4 scenario_note files (the same paths the inline `scenario_triggers[]` summarizes, but as first-class objects).

Required field shapes for an adversary-emitted scenario_note:

- `parent_thesis_id`: REQ, exact match to the thesis being attacked. v0.1 enforces 1:1 (T0 §Q1). Validator-side cross-check (`validate_scenario_parent_thesis`) confirms the parent file exists at `data/research/thesis_notes/<parent_thesis_id>.json`; dangling parent reference rejected.
- `narrative`: 80–2000 char prose describing factor → mechanism → effect on the parent thesis claim(s). MUST mirror the same factor the inline `scenario_triggers[]` entry covers, but as a coherent path narrative not a one-liner.
- `trigger_signals[]` ≥ 1: machine-observable signals (same shape as thesis_note.scenario_triggers[*] for symmetry — observable_data + threshold + direction + status=pending). Hash-link to thesis_note.scenario_triggers[*] when there is a 1:1 correspondence.
- `pm_conviction`: **`exploratory` at write time**. Adversary cannot self-set high/medium/low conviction; PM ack lift this later (charter §II信念层 PM authority).
- `scenario_role`: pick from 4-value enum based on the path's relation to thesis main path:
  - `leading_path` — primary expected unfolding (typically the scenario whose triggers fire if thesis main claim plays out)
  - `parallel_path` — co-existing alternative that does NOT contradict the main thesis
  - `tail_path` — low-probability but non-zero (for thesis robustness checking)
  - `counterfactual` — "if NOT main thesis" reverse path
- `market_state`: pick from 4-value enum based on adversary's read of consensus-vs-thesis pricing. Default to `ambiguous` if adversary genuinely cannot tell; `consensus_with_scenario` reserved for cases where pricing already prices in the scenario.
- `rank_within_thesis`: integer ≥ 1; adversary's relative ranking of this scenario among siblings under same parent thesis.
- `lifecycle_stage`: **`draft` at write time**. PM ack flips to `active`.
- `freshness_state`: `fresh` at write time. research-theme-staleness-sweeper computes thereafter.
- `review_policy`: populate with default scenario cadence (bi-weekly + event triggers, 21-day stale grace); or override with thesis-specific event triggers. `scheduled_for_at_utc` = creation instant + 14 days.
- `evolved_from_evidence[]`: list of evidence_record ids that drove this scenario's creation. SHOULD include the same `[refs: i, j]` evidence_record ids that adversary cited in the corresponding `counter_evidence_observed[]` entry (the inline-to-ledger lineage from §A above). Empty array allowed when adversary's pattern observation has no T1 anchor — same fail-loud honesty as ai_verified=false.
- `pricing_snapshots[]`: ≥ 0 entries at write time; adversary populates 1 if a current market_state reading is honestly available (with prose `pricing_anchor`); else leave empty for downstream (research-theme-knowledge-and-package-curator / operation-portfolio-decision) to populate first snapshot.
- `ai_generated`: `true`
- `pm_acknowledged`: `false`

### D''. Production write requirement

When this skill runs against a real thesis_note (not a fixture), the scenario_note files MUST land under `data/research/scenario_notes/` (the canonical production path). At least one production scenario_note for each active thesis the adversary attacks is REQ to validate the schema against actual writer pipeline behavior; fixture replays alone are not sufficient. A schema-only introduction without at least one production-grade write is staged-rollout, not done.

### D. Failure modes specific to ledger emission

- Adversary writes `counter_evidence_observed[]` entries but emits ZERO evidence_records → ledger has no first-class artifact. Ledger emission is mandatory; one record per inline entry.
- Adversary picks `update_direction: "support"` for any of its evidence_records → conceptual error; adversary's role is reverse-direction. If the observation actually supports the thesis, it does NOT belong in `counter_evidence_observed[]` — let drafter or PM author it instead.
- `evidence_id` slug collides with an existing file in the same weekiso directory → bump the qualifier suffix (`..._counter_v2`) and continue. Never overwrite an existing evidence_record.
- Skipping the `unresolved_objections: [...]` line in `notes` because "adversary already wrote falsifiers and counter_evidence inline" → still required. The line is the cross-link pointer that downstream `adversarial_review_log` consumers rely on.

## Writing Rules

### `counter_evidence_observed[]` vs `falsifiers[]` (the critical distinction)

- `counter_evidence_observed[]` = **past tense / already observed** reverse evidence. Format: prose. Example: "Q1 actually saw real rates climb 30bps despite the dovish FOMC tone, contradicting the rate-easing premise but not yet decisive."
- `falsifiers[]` = **future tense / hypothetical** failure conditions. Format: prose starting with `if` / `当` / `若`. Example: "if 1y real rate climbs back above +1.5% for >2 consecutive months, the thesis is wrong."

These are NOT the same field. The reviewer machine-checks both:

- empty `falsifiers[]` → reviewer raises minor finding "adversary 没跑透"
- empty `counter_evidence_observed[]` is acceptable IF `notes` is appended with `single-perspective risk: <one sentence>`

### `scenario_triggers[]` machine-readability

Every trigger must be machine-observable. Forbidden trigger fields:

- `observable_data: "市场情绪转好"` (subjective, no data source)
- `observable_data: "AI 叙事破灭"` (no operational definition)

Allowed trigger fields:

- `observable_data: "1y US real rate (FRED DGS1 - 1y inflation expectation)"` + `threshold: "0"` + `direction: "below"`
- `observable_data: "Mag7 Q3 capex YoY growth (company filings)"` + `threshold: "+5%"` + `direction: "below"`

If you cannot state the trigger as `observable_data + threshold + direction`, do NOT write it as a scenario_trigger. Write it as a `falsifier` prose instead.

### Trigger threshold MUST carry baseline window (v1.6 prose carrier)

> **Reader gain (Rule 36)**: a `threshold` like `"30 percentile"` or `"PE 偏高"` is unverifiable — the reader and any future check script cannot tell **which 5y / 10y / 1y window** was meant, **rolling vs fixed**, or **what metric** the percentile was taken on. By forcing the threshold prose to carry the baseline window inline (e.g. `"trailing 5y daily, > 80th percentile"` or `"5y average + 1 std"`), the next reviewer can re-check the trigger against the same series adversary intended, and the PM can see what evidence base the trigger was sized against.

When the threshold uses a **percentile**, **standard-deviation band**, **historical extreme** (max/min), **multi-year average**, or any reference to **historical distribution**, the `threshold` string MUST inline:

1. **The baseline window** — explicit length and rolling-vs-fixed (`trailing 5y daily`, `rolling 3y monthly`, `since 2015`, `2021-2026 fixed window`)
2. **The aggregation grain** — `daily` / `weekly` / `monthly` / `quarterly`, when not obvious from the metric
3. **The reference statistic** — `> 80th percentile` / `> 5y average + 1 std` / `> max of trailing 3y` / `< 5y median`

Examples (right vs wrong):

- ✅ `threshold: "trailing 5y daily, > 80th percentile of NYSE TTM PE"` (window + grain + stat all inline)
- ✅ `threshold: "rolling 3y monthly, > average + 1 std on US 1y real rate"` (window + grain + stat)
- ✅ `threshold: "0"` (absolute level — no historical comparison, baseline window not required)
- ✅ `threshold: "+5%"` (absolute level — fine)
- ❌ `threshold: "high"` (no baseline)
- ❌ `threshold: "30th percentile"` (window unspecified — 1y? 5y? rolling? fixed?)
- ❌ `threshold: "above historical norm"` ("norm" undefined)
- ❌ `threshold: "PE 偏高"` (subjective + no baseline)

Source-availability constraint (only when relevant):

- If the historical series can be retrieved by the canonical Perplexity helper (`current PE`, `5y average PE`, `monthly snapshot`, year-end series — see [`research-thesis-verifier SKILL §Canonical Perplexity Helper`](../research-thesis-verifier/SKILL.md#canonical-perplexity-helper)), the trigger is **viable**.
- If the threshold needs **daily percentile rank of a 5y daily series** (a known [path α gap](../../../designDoc/research_40_thesis_note_schema_v1_5.md)), do NOT silently write the trigger as if a daily percentile is checkable. Either (a) reword the threshold to use the data Perplexity can give (`> 5y average`, `near 5y high`, `above 75th percentile of monthly snapshots`) OR (b) drop the trigger to `falsifier` prose ("若 PE 升至明显高于 5y 历史均值且持续 30 个交易日") with no false machine-readability claim.
- The Layer 0 reviewer (check 9) will fail any trigger whose threshold is unverifiable from the surfaces declared in `source_research_ids[]` plus the canonical Perplexity helper coverage.

### Lifecycle promotion

- Adversary is the ONLY agent allowed to promote `lifecycle_stage` from `"draft"` to `"active"`
- If you cannot find ≥1 falsifier even after searching, do NOT promote. Instead:
  - Set `lifecycle_stage: "draft"` (unchanged)
  - Append to `notes`: `single-perspective risk: 找不到独立反例，请 PM 复核是否需要扩源后再升 active`
  - Raise a flag in your output for the test harness

### `next_review_trigger`

- `kind: "time"` → `value: "2026-05-15"` (absolute date) or `"weekly"` / `"monthly"` (cadence)
- `kind: "event"` → `value: "next FOMC"` / `"GEV Q2 earnings"` / `"OPEC+ June meeting"`
- `kind: "catalyst"` → `value: "OpenAI IPO pricing window opens"` / `"Iran nuclear deal signed"`

Pick the kind that makes the next-review timing tightest. Prefer `event` / `catalyst` over `time` when a known dated event is the natural revisit moment.

### Adversarial Shape — what falsifiers / counter-evidence / triggers must make visible (v1.6 自由格式承载)

> **Reader gain (Rule 36)**: by carrying these three things in the prose payload of `falsifiers[]` / `counter_evidence_observed[]` and (when present) the prose tail of `notes`, the downstream `research-theme-report-reviewer` and the eventual PM reader can distinguish (a) reverse paths written as **paths** rather than nitpicks against a single claim, (b) attacks on **contribution weight** rather than attempts to topple the entire causal chain, and (c) which reverse paths are already partially unfolding now, not just hypothetical futures.

`thesis_note v1.6` schema gives you 4 structured slots (`falsifiers[]`, `counter_evidence_observed[]`, `scenario_triggers[]`, `next_review_trigger`). The prose written **inside those slots** should additionally carry the following three things — written into the existing fields, not as new keys:

1. **Reverse paths are paths, not nitpicks.** Each `falsifier[]` entry should describe a coherent **forward path** that, if it unfolds, weakens or invalidates the thesis — not a one-line counter-claim. Bad: `"if real rates rise, thesis is wrong"`. Good: `"若财政可信度受损推 term premium 跳升 50bp+，real rate compression 在长端被反向覆盖；capex 强但传导被截断 — 此时 thesis 在因端站立但 effect 端被隔断，应判 fades"`. This signals to reviewer / PM that the reverse path is structured the same way as the main path: factors → mechanism → effect on thesis. Adversary in v1.6 expresses this in `falsifier` prose; v1.6 may give it a structured `scenarios[].effect_on_thesis: "fades" | "falsifies"` slot — the v1.6 prose pattern carries forward into that field.
2. **Attack contribution weight, not the whole causal chain.** When the thesis rests on multi-factor contribution (drafter should have already named the factors in claims), the strongest adversarial reading is usually **"factor X is given too much weight"** or **"factor Y was missed"**, not **"the whole thesis is wrong"**. Examples: `counter_evidence_observed` = `"过去 4 周 Mag7 集中度上升而二梯队 power-cap underperform — drafter 把 dispersion 当主线，但 contribution 已偏向 concentration"`; `falsifier` = `"若 hyperscaler capex Q3 YoY 仍 +30%+ 但 small-cap AI infra 整体 underperform 30 个交易日以上，thesis 主线在但 dispersion 表达失效，应降为 secondary"`. Reviewer can then see whether the draft handles weight rebalancing vs full topple.
3. **Concurrent reverse path acknowledgement.** If a reverse path is **already partially unfolding now** (not just a future hypothetical), say so explicitly. Append to `notes` a one-line `concurrent reverse path: <prose>` after the verifier's `external verification:` line. Example: `concurrent reverse path: tilts-to-concentration 信号过去 4 周升温（dispersion 退至历史 30 分位以下 + Mag7 集中度 +3pp），与 extends 主线并行 unfold，PM 应同时跟踪`. This is the v1.6 prose carrier of what v1.6 may later structure as `scenarios[].current_intensity` + `scenario_weighting_note`. Until v1.6, the prose line in notes is the contract; reviewer Layer 0 will check it.

These are prose obligations, **not validator-checked**. The L1 schema only checks the `if|当|若` opener on falsifiers and the 6-key shape on triggers; it cannot tell whether the falsifier is a path or a nitpick, whether the attack targets weight or chain, or whether the reverse path is acknowledged as concurrent. Adversary self-check this before promoting `lifecycle_stage` to `"active"`.

### Counter-evidence granularity — one observation per entry, ~50-150 chars

> **Reader gain (Rule 36)**: by holding each `counter_evidence_observed[]` entry to a single observation at a consistent grain, the PM and `research-theme-report-reviewer` can scan the array and see "how many distinct weakening signals exist now" instead of having to mentally split a long paragraph into multiple observations. It also forces adversary to either separate two observations into two entries OR raise the heavier one to a `falsifier[]` (forward-looking) — the granularity discipline keeps `counter_evidence_observed` and `falsifiers` from blurring into each other.

Each entry in `counter_evidence_observed[]` should follow this shape:

- **Length**: roughly 50-150 chars (中文) or 50-200 chars (English). One sentence, optionally with a 1-clause supporting parenthetical.
- **Content shape — exactly three things**: (1) the **factor** that the drafter overweighted or missed; (2) the **observable mechanism** that demonstrates the rebalancing (a number, a price move, a sentence from a source); (3) the **effect on the thesis claim** in `claim[i]` terms (which claim's contribution weight needs to be lowered, or which path is partially unfolding now). Skip any of these three and the reader has to reconstruct what adversary already knew.
- **One observation per entry.** If you find yourself writing `"... 而且 ..."` or `"X; meanwhile Y"` connecting two distinct observations, split into two entries. Two factors, two entries.
- **Hard upper bound ~200 chars**: if a single observation needs more than ~200 chars to express, the chances are it is no longer "counter-evidence already observed" but a "reverse path that may unfold" — promote it to `falsifiers[]` instead, where path-shaped multi-clause prose is the norm.
- **Hard lower bound ~30 chars**: shorter than this is almost always a nitpick (`"PE too high"`) without the factor / mechanism / effect triple. Such entries fail [`thesis-report-reviewer Layer 0 §check 6 / 8`](../research-theme-report-reviewer/SKILL.md#layer-0--thesis-structural-readiness-deterministic-fail-fast).

Examples (drawn from the dogfood `real_rates_and_growth_resilience_drive_non_recessionary_equity_advance` pass):

- **Right grain** (~120 chars, factor + mechanism + effect): `"S&P Global Q1 2026 consumer pulse 报告 consumption decelerated at the start of 2026, in direct tension with Citrini 4/19 'consumption recovery after weak 2025' framing — claim 2 中 consumption pillar 应降为 conditional 而非 already-confirmed。 [refs: 6]"`. One factor (consumption pulse), one mechanism (S&P Q1 报告), one effect (claim 2 weight rebalancing).
- **Wrong grain — too compressed** (~25 chars, no mechanism, no effect): `"Consumption looks weaker now [refs: 6]"`. Reader has to guess which claim, what mechanism, what's the contribution weight implication. Should fail Layer 0.
- **Wrong grain — too sprawling** (~280 chars, two factors merged): `"Consumption decelerated per S&P Q1, AND real-rate measurement diverges 100bp between Capital Flows daily proxy and FRED Cleveland model, AND tilts-to-concentration 信号过去 4 周升温 — drafter 把 dispersion 当主线但 contribution 已 shift。"`. Three observations stuffed into one. Split into 3 separate entries.

This discipline applies only to `counter_evidence_observed[]`. `falsifiers[]` (forward-looking reverse paths) and `scenario_triggers[*]` (machine-readable trigger objects) follow their own shape rules above and are NOT subject to the 50-150 char range.

### Inline source ref convention — `[refs: …]` (counter_evidence_observed mandatory)

> **Reader gain (Rule 36)**: by appending `[refs: i, j]` to every `counter_evidence_observed` entry, the PM (and `research-theme-report-reviewer`) can answer "which source surfaced this reverse evidence" without re-reading the archive. Counter-evidence almost always cites a specific source (a number from FRED, a passage from a research note); leaving the cite implicit forces the next reader to reconstruct what adversary already knew.

- Every entry in `counter_evidence_observed[]` MUST end with `[refs: <i>, <j>, …]`, where each `<i>` is a 1-based index into `source_research_ids[]`. Same convention as drafter's `claims[]` ([`research-thesis-drafter SKILL §Inline source ref convention`](../research-thesis-drafter/SKILL.md#inline-source-ref-convention--refs-)).
- The index is stable: verifier already extended `source_research_ids[]` with external IDs (e.g. `ext_fred_*`, `ext_bls_*`) at the tail; adversary normally cites those by their tail-position index (e.g. an FRED number that came in at position 4 → `[refs: 4]`). Do NOT reorder; only reference.
- If a counter-evidence rests on observation by adversary itself (no specific source — rare), still tag it `[refs: 0]` and explain in prose. `0` is the convention for "adversary's own pattern observation"; reviewer Layer 0 accepts it but flags >1 such entries per thesis.
- Tag is OPTIONAL on `falsifiers[]` (forward-looking hypotheticals usually don't have a specific cite) and `scenario_triggers[*]` (those are machine-readable structured objects, not prose).
- Validator does NOT enforce `[refs: …]` shape on counter_evidence (v1.6 prose carrier). Adversary self-check below catches missing tags. Reviewer Layer 0 raises `thesis_structure` if counter_evidence arrives without ref tags.

## Failure Signals

### Caught deterministically (do not waste tokens self-checking)

`tradectl thesis-cluster gate research-thesis-adversary` and `... validate research-thesis-adversary` together reject any of:

- input `lifecycle_stage != "draft"` (gate refuses)
- input `notes` does not yet contain an `external verification:` line (gate refuses; verifier must run first)
- output promoted `lifecycle_stage = "active"` but missing any of `falsifiers`, `scenario_triggers`, `next_review_trigger`, `counter_evidence_observed`
- `falsifiers[]` empty when present
- any `falsifiers[i]` missing the `if | 当 | 若` conditional opening
- `scenario_triggers[*]` missing one of the 6 required keys (`observable_data` / `threshold` / `direction` / `status` / `observed_at_utc` / `hit_evidence`)
- `scenario_triggers[*].direction` not in `{above, below, crosses}`
- `scenario_triggers[*].status` not in `{pending, triggered, reverse_triggered}`
- `next_review_trigger.kind` not in `{time, event, catalyst}`
- `counter_evidence_observed = []` while `notes` does NOT contain `single-perspective risk:`

### Self-check (LLM judgment, not catchable by validator)

- A `scenario_trigger` whose `observable_data` is technically a string but operationally subjective (e.g. `"市场情绪转好"`, `"AI 叙事破灭"`). The schema accepts any non-empty string; only the agent can decide whether the trigger is genuinely machine-observable.
- A `falsifier` that rewords `claim[i]` as a tautology (`if claim is wrong, thesis is wrong`). The validator only checks the `if/当/若` opener, not the logical content.
- Promoting to `active` while one of the 5 falsifiers is actually a soft adverse condition rather than a real refutation.
- Picking `next_review_trigger.kind = "time"` and a vague `value: "soon"` when a concrete event/catalyst would have been the natural revisit anchor.
- Drafter prose or verifier verification line silently rephrased while leaving them byte-equal in spirit but not in letter — the L2 diff guard will catch byte changes; this self-check is for cases where the agent is tempted to "improve" upstream work.
- **Adversarial shape — falsifier reads as nitpick.** A `falsifier[]` entry is a one-line counter-claim against a single number, not a structured forward path with factors → mechanism → effect on thesis. (See `### Adversarial Shape` above.)
- **Adversarial shape — chain-topple instead of weight rebalancing.** All falsifiers attempt to invalidate the entire thesis, none of them targets contribution weight rebalancing (e.g. "main path stays but dispersion expression fails, should downgrade to secondary"). For multi-factor theses this usually means the adversarial pass missed the most realistic reverse paths.
- **Adversarial shape — concurrent reverse path not acknowledged.** A reverse / weakening path is **already partially unfolding** in the current evidence window, but `notes` does not carry the `concurrent reverse path: <prose>` line. Reviewer Layer 0 will surface this; adversary catching it pre-handoff avoids a round-trip.
- **Inline ref tag missing or malformed on counter_evidence.** Any entry in `counter_evidence_observed[]` lacks the `[refs: i, j]` tail tag, OR the tag references an index outside `0..len(source_research_ids)` (where `0` = adversary self-observation, see `### Inline source ref convention` above), OR the tag uses non-numeric references. Counter-evidence without a ref forces the next reader to guess the source.
- **Counter-evidence granularity off.** A `counter_evidence_observed[]` entry packs two distinct observations (signal: an `而且` / `;` / `meanwhile` connecting two factors), OR a single entry exceeds ~200 chars (signal: it is really a reverse path → promote to `falsifiers[]`), OR an entry is shorter than ~30 chars and lacks the factor + mechanism + effect triple (signal: it is a nitpick). See `### Counter-evidence granularity` above. Reviewer Layer 0 / 8 will flag these.
- **Trigger threshold missing baseline window.** A `scenario_triggers[*].threshold` uses a percentile / std-band / historical-extreme / multi-year-average reference but does NOT inline the baseline window + grain + reference statistic (e.g. `"30 percentile"` instead of `"trailing 5y daily, > 30th percentile"`). See `### Trigger threshold MUST carry baseline window` above. Reviewer Layer 0 check 9 will fail it. Absolute thresholds (`"0"`, `"+5%"`) are exempt.
- **Trigger threshold needs unavailable historical surface.** A `threshold` claims daily percentile rank of a 5y daily series for a metric whose daily history is NOT retrievable through `source_research_ids[]` plus the canonical Perplexity helper (e.g., `"trailing 5y daily, > 80th percentile of trailing PE"` for an asset where Perplexity can only return year-end / monthly snapshots). Either reword to a verifiable statistic OR drop to `falsifier` prose; do NOT publish a trigger that the next reviewer cannot machine-check.

## Guardrails

- Do NOT silently rewrite drafter's `claims[]` even when adversarial reading suggests one claim is too strong. State the weakness as a `counter_evidence_observed` or `falsifier`; let PM later decide whether to ask drafter for a revised round.
- Do NOT modify the `external verification:` line in notes. If verifier's verification status looks too generous, state your concern in `counter_evidence_observed[]`, not by editing verifier's line.
- Do NOT write `confidence_estimate: float` even when the thesis feels weak. v1.6 explicitly rejected float confidence in favor of prose hedging in `probability_view` (which drafter wrote, not adversary).
- Do NOT promote `lifecycle_stage` to `"active"` if `falsifiers[]` is empty. Always raise to PM in that case.

## Self-test

Run with:

```bash
./.venv/bin/python -m src.cli.tradectl test-thesis-agent research-thesis-adversary
```

Fixtures live under `tests/thesis_cluster_fixtures/research-thesis-adversary/`:

- `input.json` — hand-prepared simulated drafter+verifier output where ≥1 claim has an obvious falsifier hook (e.g., a rate-dependent thesis whose falsifier should be a rate threshold)
- `golden_output.json` — expected adversary output (≥1 falsifier, ≥1 scenario_trigger with pending status, lifecycle = active)
- `assertions.json` — required field shapes, regex on falsifier prose, status enum check, lifecycle = active enforcement

A second fixture pair `input_no_falsifier_hook.json` / `golden_output_no_falsifier_hook.json` covers the negative case where adversary cannot find a falsifier and must (a) NOT promote lifecycle, (b) append `single-perspective risk:` to notes.

Golden rebake flow: same as `research-thesis-drafter`.
