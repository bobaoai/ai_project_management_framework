---
name: research-theme-discovery-scanner
description: Scans `data/research/messages_index.jsonl` within an explicit time window and clusters in-window messages into one or more theme candidates that are NOT yet covered by any existing `themes/metadata/*.json`. Outputs `data/research/theme_candidates/<scan_id>.json` + `<scan_id>.md` for PM review. Use when the task is "AI 自己进资料堆扫一遍，看看有什么新题材应该开" (entry point #2 in the three theme-creation entry points). Does NOT create theme metadata directly — PM must explicitly route a candidate forward.
---

# Theme Discovery Scanner

> **Reader gain (Rule 36)**: by the time this skill is done, the PM should be able to (a) tell which clusters of recent research are NOT yet covered by any existing theme, (b) tell why each candidate cluster is coherent (which tickers / macro_topics / thesis_family fields ties them), (c) tell which existing themes each candidate is closest to (so PM can decide "this is really a sub-thesis of theme X" without re-doing the similarity work), (d) tell which scan window was actually scanned (so PM can ask for a wider scan when needed).

> **Naming convention — read wide, write strict.** New IDs you mint here — `candidate_slug` — must be **snake_case** (`^[a-z0-9][a-z0-9_]*$`), enforced by `theme_candidate.schema.json`. References to existing themes — `closest_existing_themes[].theme_id`, the `<existing_theme_id>` portion of `recommended_action: already_covered_by_theme_<id>` — use the **transitional read pattern** `[a-z0-9_-]` so the scanner can legitimately point at historical hyphen-case themes (`ai-datacenter-power-and-balance-of-plant`) AND future snake_case ones. The 8 historical hyphen-case files are NOT force-migrated; they will be naturally superseded as PM re-builds metadata downstream of Plan B. So: when listing closest existing themes, just use whatever id the actual `themes/metadata/<id>.json` filename gives you (hyphen or snake) — do not coerce.

## What This Skill Does

Use this skill ONLY when:

- The user request is "scan the recent archive for new theme candidates" / "看看最近的资料堆里有没有新题材" / "AI 自己挖一下" — i.e., the request is **bottom-up discovery**, not top-down "open theme X" (that is `research-theme-bootstrapper` Stage A directly)
- The PM has supplied (or implicitly accepts) an explicit `as_of_utc` time anchor and a window range (default: last 14 days)

This skill is a **scanner / candidate proposer**. Its job is to:

1. Enumerate recent in-window archive items deterministically
2. Cluster them by overlapping `tickers` / `macro_topics` / `thesis_family` / `source_collection` fields (deterministic similarity, T10)
3. For each cluster, check whether ≥1 existing theme already covers it
4. Output the **uncovered** clusters (or weakly-covered ones) as named candidates with rationale

It is NOT:

- a theme creator (does not write `themes/metadata/*.json` — that is `research-theme-bootstrapper` Stage B)
- a similarity arbiter (does not decide `merge_into` / `narrow_existing` / `carve_out_from` — that is `research-theme-bootstrapper` Stage A)
- a thesis writer (does not write `thesis_notes/*.json` — that is `research-thesis-drafter`)
- an owner-decision writer (does not write `theme.owner_decision` — that is `research-theme-report-owner`)

## Desired Result

The desired result is a single `theme_candidates/<scan_id>.json` file (machine) + a paired `<scan_id>.md` file (PM-readable) listing 0..N candidate clusters, each with:

- A proposed candidate slug (not yet a theme_id)
- Why this cluster is coherent (which structured fields tie it together)
- Which existing themes it is closest to (so PM does not need to redo overlap analysis)
- Whether scanner judges it likely worth `research-theme-report-owner` round-1 entry, or unlikely (e.g., already saturated by an existing theme — listed for visibility but not recommended)

By the time this skill is done, the PM should be able to read the .md and either:

- pick one candidate → invoke `research-theme-report-owner` round-1 with this candidate as input → proceed to `research-theme-bootstrapper` Stage A
- reject all candidates → confirm scanner ran successfully but nothing new emerged this window
- ask for a wider scan window → re-invoke this skill with a larger range

## Completion Standard

This skill is complete only when ALL of the following are true:

- `as_of_utc` is explicit (NOT `now()` silently — must be passed in or read from a stable anchor)
- `time_window` is explicit (`{from_utc: ISO8601, to_utc: ISO8601}`) and `to_utc <= as_of_utc`
- The output JSON contains `scanned_window_utc: {from_utc, to_utc, as_of_utc}` matching the input window (V04 timestamp grounding)
- Every in-window message in `messages_index.jsonl` has been triaged into one of: `assigned_to_candidate(<slug>)`, `assigned_to_existing_theme(<theme_id>)`, `unassigned_low_signal`
- Each candidate has ≥3 supporting message IDs (single-message "candidates" are noise and must be dropped or merged into `unassigned_low_signal`)
- Each candidate's `closest_existing_themes[]` (top 3) is computed by deterministic overlap of `tickers ∪ macro_topics ∪ thesis_family` against existing `themes/metadata/*.json` (T10)
- Each candidate has `recommended_action ∈ {worth_owner_round_1, weak_consider_skip, already_covered_by_theme_<id>}`
- A paired markdown summary `<scan_id>.md` is written for PM review
- `themes/metadata/*.json` is NOT modified
- `theme.owner_decision.json` is NOT created (that is `research-theme-report-owner`'s territory; scanner only proposes candidates)

If `as_of_utc` is not supplied → raise `missing_temporal_anchor` and refuse to scan. Do NOT silently use wall-clock now().

## Node Bindings

This skill currently has NO entry in [`data/runtime/artifact_graph.yaml`](../../../data/runtime/artifact_graph.yaml) (theme_candidates are an upstream proposal layer; not yet a graph node). When `thesis_note` and `theme_candidates` are admitted to the graph in a future phase, this skill will own the `theme_candidates(scan_id)` node.

This skill consumes (deterministic, read-only):

- `data/research/messages_index.jsonl` (must_be_fresh) — primary scan target
- `data/research/themes/metadata/*.json` (must_be_fresh) — coverage check baseline

This skill writes:

- `data/research/theme_candidates/<scan_id>.json` (new file)
- `data/research/theme_candidates/<scan_id>.md` (new file, PM-readable)

## Primary Inputs

- `as_of_utc` — REQUIRED. ISO8601 UTC timestamp, the upper bound of the scan window.
- `time_window` — `{from_utc, to_utc}`. Default `from_utc = as_of_utc - 14 days` if not supplied.
- `min_cluster_size` — default 3. Drop clusters with fewer messages.
- `optional_topic_filter` — when the user says "scan recent commodity stuff specifically", pre-filter messages by `macro_topics` overlap before clustering.

DO NOT call external APIs. This is a deterministic local scan + cluster step. LLM judgment is used ONLY for naming candidates and summarizing rationale prose, NOT for similarity scoring (similarity is computed from structured index fields per T10).

## Required Output Schema

Field shape, types, regex (including the `scan_id = scan_<YYYY_MM_DD>_<HHmm>Z` rule), enum, and presence-by-conditional are enforced deterministically by [`data/runtime/schemas/theme_candidate.schema.json`](../../../data/runtime/schemas/theme_candidate.schema.json) plus the business-extras (window monotonicity) in [`src/tools/thesis_cluster_validate.py`](../../../src/tools/thesis_cluster_validate.py). Pre-condition (must supply explicit `as_of_utc`, no wall-clock fallback) is enforced by [`src/tools/thesis_cluster_router.py`](../../../src/tools/thesis_cluster_router.py). Run `... gate research-theme-discovery-scanner <input>` before, and `... validate research-theme-discovery-scanner <output>` after. The example below is a readability aid.

### Machine — `data/research/theme_candidates/<scan_id>.json`

```json
{
  "scan_id": "scan_2026_04_19_1400Z",
  "scanned_window_utc": {
    "from_utc": "2026-04-05T00:00:00Z",
    "to_utc": "2026-04-19T00:00:00Z",
    "as_of_utc": "2026-04-19T14:00:00Z"
  },
  "scanner_version": "v0.1",
  "messages_scanned": 142,
  "messages_assigned_to_existing_themes": 87,
  "messages_assigned_to_candidates": 41,
  "messages_unassigned_low_signal": 14,
  "candidates": [
    {
      "candidate_slug": "modular_nuclear_capex_chain",
      "supporting_message_ids": ["agentmail_20260408T...", "agentmail_20260411T...", "agentmail_20260415T..."],
      "structural_signature": {
        "shared_tickers": ["NNE", "OKLO", "GEV"],
        "shared_macro_topics": ["energy", "ai_capex"],
        "shared_thesis_family": ["nuclear", "ai_power"],
        "dominant_source_collections": ["independent_research"]
      },
      "candidate_rationale_prose": "Three messages in the window cluster around small-modular-reactor build-out tied to AI datacenter power. Two are independent research notes; one is a forwarded sell-side update. No existing theme covers this directly.",
      "closest_existing_themes": [
        {"theme_id": "ai_power_grid", "overlap_score": 0.42, "overlap_dimensions": ["macro_topics:energy", "thesis_family:ai_power"]},
        {"theme_id": "us_industrial_capex", "overlap_score": 0.18, "overlap_dimensions": ["macro_topics:industrial"]}
      ],
      "recommended_action": "worth_owner_round_1",
      "recommended_action_rationale": "Closest existing theme `ai_power_grid` covers grid + utility scale; modular nuclear is a distinct asset cluster (NNE/OKLO) that ai_power_grid's IS_NOT could legitimately exclude — looks like a real new candidate."
    }
  ]
}
```

### Human — `data/research/theme_candidates/<scan_id>.md`

```markdown
# Theme Discovery Scan — <scan_id>

Window: 2026-04-05 → 2026-04-19 (as_of 2026-04-19 14:00Z)
Messages scanned: 142 (existing-theme: 87, new-candidate: 41, low-signal: 14)

## Candidate 1 — `modular_nuclear_capex_chain` — recommend: worth owner round-1

Three messages cluster around SMR build-out tied to AI datacenter power...
Closest existing theme: `ai_power_grid` (overlap 0.42) — but distinct asset cluster (NNE/OKLO), likely real new candidate.

## Candidate 2 — `<slug>` — recommend: <action>

...

## Recommendation

PM should review candidate 1 first (highest novelty, smallest overlap with existing themes). If accepted, route to `research-theme-report-owner` round-1.
```

## path_observation Emission

> **Reader gain (Rule 36)**: by emitting `path_observation` JSON files alongside theme candidates, the scanner closes the gap between bottom-up clustering and the formal Scenario authoring path. A path_observation captures an early signal that has clustered (multiple supporting evidence ids) but is NOT yet ready to become a Theme — too narrow / too speculative / waiting for more corroboration. PM later promotes path_observation to a scenario_note via the graduation flow (charter §I 旁路对象 → 一等对象 only via belief_delta evidence).

When the scanner identifies clusters that are **NOT ripe for theme candidacy** (single-publisher / sub-theme of an existing theme / exploratory pattern), emit a `path_observation` JSON file in addition to (or instead of) a theme_candidate output.

Schema: [`data/runtime/schemas/path_observation_v0_1.schema.json`](../../../data/runtime/schemas/path_observation_v0_1.schema.json) (v0.1).

Path convention: `data/research/path_observations/<weekiso>/<path_id>.json` where `<path_id>` = `<weekiso>_<topic_short>_<distinguisher>` snake_case slug.

When to emit path_observation vs theme_candidate:

| Signal | Output |
|---|---|
| Cluster ≥3 messages from ≥2 publishers, novel topic, plausible new theme | theme_candidate (existing path) |
| Cluster ≥3 messages but single-publisher (e.g. all from `citrini` family) — needs corroboration | path_observation, `lifecycle_stage="cluster_formed"` |
| Cluster ≥2 messages, sub-theme of an existing theme — needs more evidence to graduate | path_observation, `lifecycle_stage="observed"`, tentative_themes=[<existing_theme_id>] |
| Single message, important looking | NEITHER — promote via `research-theme-report-owner` direct route |

Required field shapes for scanner-emitted path_observation:

- `path_id`: snake_case slug per convention
- `narrative`: 50–1500 char prose describing what was observed + what would need to happen to graduate
- `supporting_evidence_ids[]`: ≥1; each entry is a `messages_index.jsonl` research_id (these are pre-existing archive ids, not evidence_record ids; D.2 cross-check is path_supporting_evidence which expects evidence_record file shape — for scanner outputs the ids point to messages_index entries instead, scanner uses `external_url` system convention or extends supporting_evidence_ids semantics; for now: one stub evidence_record per supporting message OR explicit messages_index ref via different cross-check path TBD)
- `tentative_themes[]`: theme_ids the path may belong to. minItems=0 in `observed` stage; minItems=1 required when lifecycle_stage='cluster_formed' (schema conditional allOf rule).
- `lifecycle_stage`: pick `observed` for fresh signals (1–2 supporting items, no tentative theme yet) or `cluster_formed` (≥3 supporting items AND ≥1 tentative theme).
- `freshness_state`: `fresh` at write time
- `review_policy`: default `event-only` cadence + 30-day stale grace; sweeper transitions stale → dismissed if no graduation within window.
- `ai_generated`: `true`

Scanner does NOT emit `lifecycle_stage="graduated_to_scenario"` or `dismissed` — those transitions belong to PM (graduation requires writing a scenario_note + belief_delta evidence) or to research-theme-staleness-sweeper (dismissed via stale grace expiry).

### Production write requirement

When this skill runs against real `messages_index.jsonl` (not a fixture), path_observation files MUST land under the canonical production path `data/research/path_observations/<weekiso>/`. A schema-only introduction without at least one production-grade write against current-week archive content is staged-rollout, not done; close the loop with a real write before treating the path as live.

## Clustering (Done by Harness, Not LLM)

> **Read this section first.** The clustering algorithm below is executed by deterministic Python in the harness BEFORE the LLM is called. The LLM does NOT compute Jaccard similarity, does NOT decide cluster membership, and does NOT decide which items go to which existing theme. If you find yourself trying to score message similarity in your head, stop — that work was already done and the result is in your `precomputed_clusters` input.
>
> The LLM's actual job is downstream of clustering:
>
> 1. **Names** the candidate slug (snake_case, descriptive)
> 2. **Writes** the prose rationale and recommended_action prose
> 3. **Picks** which low-signal items inside an already-formed cluster to drop vs roll into an adjacent candidate (only re-organization, never re-clustering)
>
> If a cluster from the harness looks wrong to you semantically, surface it in `recommended_action` prose — do NOT silently re-cluster. Re-clustering must be a separate harness pass triggered by PM, not an LLM-level override.

Deterministic clustering algorithm (executed by the harness, documented here for reference):

1. For each in-window message, build a **signature vector** from `tickers ∪ macro_topics ∪ thesis_family`
2. Compute pairwise Jaccard similarity between signature vectors
3. Greedy single-link cluster with threshold `>= 0.4`
4. For each cluster, compute overlap against every existing `themes/metadata/<theme_id>.json`'s `linked_research_ids` ∪ `theme_tags` ∪ `key_assets` — also Jaccard
5. If max overlap ≥ 0.6 → mark cluster as `assigned_to_existing_theme`
6. If max overlap < 0.6 AND cluster size ≥ `min_cluster_size` → mark as candidate; pass to LLM for naming + rationale

This division mirrors `research-theme-bootstrapper` Stage A's deterministic-vs-LLM split (T10 + A14).

## Failure Signals

### Caught deterministically (do not waste tokens self-checking)

`tradectl thesis-cluster gate research-theme-discovery-scanner` and `... validate research-theme-discovery-scanner` together reject any of:

- input missing `as_of_utc` (gate raises `missing_temporal_anchor`)
- output `scan_id` does not match `scan_<YYYY_MM_DD>_<HHmm>Z`
- output `scanned_window_utc` missing any of `from_utc / to_utc / as_of_utc`, or violates `from_utc < to_utc <= as_of_utc`
- any candidate's `supporting_message_ids` < 3 (min cluster size invariant)
- any `recommended_action` outside `{worth_owner_round_1, weak_consider_skip, already_covered_by_theme_<theme_id>}`
- `recommended_action` set without non-empty `recommended_action_rationale`
- `closest_existing_themes[*].overlap_score` outside `[0, 1]`
- `structural_signature` missing any of the 4 required key arrays

### Self-check (LLM judgment, not catchable by validator)

- LLM computed any `overlap_score` value rather than echoing the deterministic harness output (T10). Validator only checks the range `[0, 1]`; the agent must refuse to overwrite harness scores with its own intuition.
- A cluster with ≥3 messages was silently dropped without appearing in `messages_unassigned_low_signal` count (validator only checks structure, not whether `messages_scanned == messages_assigned_to_existing_themes + messages_assigned_to_candidates + messages_unassigned_low_signal` — agent must self-check this conservation invariant).
- `closest_existing_themes[]` is empty even though ≥3 active themes existed in the harness's neighbor scan — agent must verify the scan returned neighbors before claiming none.
- `themes/metadata/*.json` was modified (scanner is read-only on metadata; this is a Stage B / research-theme-bootstrapper responsibility).
- Candidate slug is generic (`new_theme_1`, `cluster_a`) rather than descriptive snake_case.

## Guardrails

- Do NOT write `themes/metadata/<theme_id>.json` directly. Candidates are PROPOSALS, not theme creations.
- Do NOT route directly to `research-theme-bootstrapper`. Always route through `research-theme-report-owner` round-1 first (PM must explicitly decide "this candidate is worth opening").
- Do NOT infer time anchor from wall-clock. PM must supply `as_of_utc`. If absent, raise `missing_temporal_anchor` and stop.
- Do NOT rate similarity by reading prose — use the deterministic Jaccard score computed by the harness.
- Do NOT promote a single-message "candidate". If a single message looks important, it belongs in `research-theme-report-owner`'s direct route, not in scanner output.

## Self-test

Run with:

```bash
./.venv/bin/python -m src.cli.tradectl test-thesis-agent research-theme-discovery-scanner
```

Fixtures live under `tests/thesis_cluster_fixtures/research-theme-discovery-scanner/`:

- `input.json` — synthetic `as_of_utc` + window + a small synthetic `messages_index.jsonl` slice (10 messages clustering into 2 obvious topical groups + 2 outliers) + a synthetic existing-theme set (1 theme that legitimately covers group A; nothing covers group B)
- `precomputed_clusters.json` — the deterministic Jaccard cluster output the harness generates from `input.json` (so the LLM step is testable in isolation)
- `golden_output.json` — expected scanner output: 1 candidate (group B), 0 candidates flagged from group A (covered), correct `scanned_window_utc`, correct counts
- `assertions.json` — `scanned_window_utc` present, `recommended_action_rationale` non-empty for every candidate, `themes/metadata` byte-equal before/after, `as_of_utc` echoed correctly, no LLM-computed overlap_score (must trace back to precomputed_clusters.json)

A second fixture `input_no_anchor.json` covers the negative case: scanner must raise `missing_temporal_anchor` and write nothing.

Golden rebake flow: same as `research-thesis-drafter`.
