---
name: research-theme-staleness-sweeper
description: Independent freshness sweeper for thesis_note + themes/metadata + scenario_note + path_observation. Walks the canonical store, computes freshness_state per object's review_policy (cadence + scheduled_for_at_utc + stale_after_days + review_trigger[]), and emits one freshness_event row per state transition into data/runtime/staleness_sweep/<YYYY-WNN>.jsonl plus a human-readable digest at <YYYY-WNN>.md. Does NOT mutate object body fields, does NOT auto-revive stale objects (revive requires PM-authored belief_delta evidence per charter §VII). Use weekly or on PM demand. Independent of priority-updater (do not couple).
---

# Theme Staleness Sweeper

> **Reader gain (Rule 36)**: by walking thesis_note + themes/metadata weekly and emitting one freshness_event per state transition, downstream `operation-portfolio-decision` gets a deterministic feed of fresh / due / stale signals to filter candidate sets. Without this sweeper, freshness_state stays at whatever value the object was last manually set to — meaning a thesis written 6 months ago with `freshness_state=fresh` from creation never decays. Sweeper IS the heartbeat that makes charter §VII's freshness law operational.

## What This Skill Does

Use this skill ONLY when:

- The user requests a freshness sweep ("跑一遍 staleness sweep" / "刷一下 freshness state" / "weekly sweeper run")
- A scheduled cron / launchd job triggers it
- A PM is about to consume `operation-portfolio-decision` output and wants the candidate set's freshness_state up-to-date

This skill is the **independent freshness gate** between authoring and downstream consumption. Its job is:

1. Walk all canonical files: `data/research/thesis_notes/*.json` + `data/research/themes/metadata/*.json` + `data/research/scenario_notes/*.json` + `data/research/path_observations/<weekiso>/*.json`
2. For each object, evaluate `review_policy` against `now()`:
   - `freshness_state="fresh"` if `now < scheduled_for_at_utc`
   - `freshness_state="due"` if `scheduled_for_at_utc <= now < scheduled_for_at_utc + stale_after_days`
   - `freshness_state="stale"` if `now >= scheduled_for_at_utc + stale_after_days`
3. If any `review_trigger[]` event has fired (sweeper input lists fired triggers), escalate to `due` or `stale` per cadence rules
4. For each state transition (prior `freshness_state` ≠ new `freshness_state`), append one row to `data/runtime/staleness_sweep/<weekiso>.jsonl` and update the object's `freshness_state` field (mutation allowed per charter §III: thesis_note + themes_metadata are overlay layer)
5. Generate `data/runtime/staleness_sweep/<weekiso>.md` with a per-object summary + state-transition counts for PM review
6. NEVER auto-revive: stale → fresh requires PM authoring a belief_delta evidence_record with `changed_dimension ∈ {conviction, scope_boundary}` AND `pm_acknowledged=true`. Sweeper writes the `revived` freshness_event ONLY when it observes such evidence

It is NOT:

- An author (do not change `belief_delta`, `claims`, `key_dependencies`, or any prose body field)
- A PM (do not flip `pm_acknowledged`; do not promote stale → fresh without PM-authored evidence)
- A retroactive editor (existing freshness_event rows are append-only per charter §III archive immutability)
- An evidence emitter (sweeper writes freshness_event, NOT evidence_record — charter §VII explicitly: freshness_event ≠ Evidence)

## Desired Result

Two artifacts per sweep pass:

1. `data/runtime/staleness_sweep/<weekiso>.jsonl` — one freshness_event row per state transition; each row validates against `data/runtime/schemas/freshness_event_v0_1.schema.json`
2. `data/runtime/staleness_sweep/<weekiso>.md` — human-readable digest with sections:
   - "Walked N objects" with breakdown by object_type
   - "M state transitions" listed
   - "Stale objects requiring PM review" — full list with object_id + scheduled_for_at_utc + days_overdue
   - "Revive requests pending PM" — any object PM has flagged with belief_delta evidence but sweeper has not yet processed
   - "Default cadences applied" — how many objects had no review_policy (sweeper applied defaults: thesis monthly+45d / theme monthly+60d / scenario bi-weekly+21d)

Plus **mutations** to walked objects:
- `thesis_note.freshness_state` updated when state transitions
- `themes_metadata.freshness_state` updated when state transitions
- `*.updated_at_utc` bumped to sweep instant on any mutated record (per the_timestamp_semantic.md §3.6)

## Completion Standard

This skill is complete only when ALL of the following are true:

- Output `<weekiso>.jsonl` exists; each row validates against freshness_event_v0_1
- Each freshness_event has `recorded_at_utc` matching the sweep instant (within ±5 minutes)
- For any row with `trigger_kind="revived"`, the `trigger_evidence_id` MUST point to an existing evidence_record with `changed_dimension ∈ {conviction, scope_boundary}` AND `pm_acknowledged=true` (sweeper itself validates; if no such evidence exists, the row is NOT written)
- Each walked object's `freshness_state` matches its review_policy evaluation against the sweep instant
- Output `<weekiso>.md` digest covers all walked objects (count matches)
- All other body fields on walked objects are byte-equal to their pre-sweep state
- `tradectl thesis-cluster validate research-theme-staleness-sweeper <jsonl-row>` passes for each row

If any assertion fails, this skill is not done.

## Primary Inputs

Read these first:

- `data/research/thesis_notes/*.json` — all thesis_notes (skip pre-v1.6 records lacking schema_version)
- `data/research/themes/metadata/*.json` — all theme metadata (read all 3 branches: v1, v1.6, v1.6)
- `data/research/evidence_ledger/<weekiso>/*.json` — for `revived` trigger detection: any evidence_record with `pm_acknowledged=true` AND `changed_dimension ∈ {conviction, scope_boundary}` whose `linked_objects[].object_id` references a currently-stale thesis or theme triggers a revive
- The user's input listing fired event triggers: explicit list like `[{trigger: "next FOMC dot plot release", fired_at_utc: "2026-04-26T...Z"}]`. Sweeper matches each fired trigger against object `review_policy.review_trigger[]` and escalates matched objects to `due`

External API calls: NONE. Sweeper reads on-disk state and current wall-clock time only.

## Default Cadences (when object has no review_policy)

| object_type | default cadence | default scheduled_for offset | default stale_after_days |
|---|---|---|---|
| thesis_note | monthly + event | 30 days from `recorded_at_utc` | 45 |
| themes/metadata | monthly | 30 days from top-level `updated_at_utc`; top-level `scheduled_for_at_utc` is required | 60 |
| scenario_note | bi-weekly + event | 14 days from `recorded_at_utc` | 21 |
| path_observation | event-only (no calendar cadence) | n/a | 30 |

When object has a `review_policy` field, those values override defaults.

## State Transition Rules

For each walked object:

```
prior_state = object.freshness_state OR "absent" (if field absent)

if any review_trigger[] event fired since last sweep:
    new_state = "due"
    trigger_kind = "trigger_fired"
elif now >= scheduled_for + stale_after_days:
    new_state = "stale"
    trigger_kind = "cadence_stale"
elif now >= scheduled_for:
    new_state = "due"
    trigger_kind = "cadence_due"
elif prior_state == "absent":
    new_state = "fresh"
    trigger_kind = "first_evaluation"
else:
    no transition; skip
```

For revive detection (separate pass):

```
for each evidence_record in current weekiso ledger:
    if pm_acknowledged != true: continue
    if changed_dimension not in {conviction, scope_boundary}: continue
    for linked_obj in evidence.linked_objects[]:
        if walked_object[linked_obj.object_id].freshness_state == "stale":
            new_state = "fresh"
            trigger_kind = "revived"
            trigger_evidence_id = evidence.evidence_id
```

## Required Output Schema

Each freshness_event row in `<weekiso>.jsonl` must validate against
[`data/runtime/schemas/freshness_event_v0_1.schema.json`](../../../data/runtime/schemas/freshness_event_v0_1.schema.json):

```json
{
  "event_id": "2026_w17_thesis_note_warsh_succession_to_due",
  "schema_version": "v0.1",
  "recorded_at_utc": "2026-04-26T22:00:00Z",
  "object_type": "thesis_note",
  "object_id": "warsh_succession_reanchors_forced_pause_factor_a",
  "from_state": "fresh",
  "to_state": "due",
  "trigger_kind": "cadence_due",
  "rationale": "scheduled_for_at_utc 2026-04-15 has passed (now 2026-04-26); no review evidence appended since."
}
```

Run `tradectl thesis-cluster validate research-theme-staleness-sweeper <path-to-row>` after writing each row.

## Failure Signals

### Caught deterministically (do not waste tokens self-checking)

`tradectl thesis-cluster validate research-theme-staleness-sweeper <row>` will reject any of:

- `schema_version` ≠ "v0.1"
- `object_type` not in {thesis_note, theme.metadata, scenario_note, path_observation}
- `from_state` not in {fresh, due, stale, absent}
- `to_state` not in {fresh, due, stale}
- `trigger_kind` not in {cadence_due, cadence_stale, trigger_fired, revived, first_evaluation}
- `rationale` shorter than 20 chars
- `event_id` not snake_case slug 3..160 chars

### Self-check (LLM judgment, not catchable by validator)

- Sweeper auto-revived a stale object without finding pm_acknowledged=true evidence with the right changed_dimension. The validator only checks shape, not the cross-link integrity. If revive trigger_kind is set, MANUALLY verify the linked evidence_record exists + pm_acknowledged + changed_dimension.
- Sweeper applied default cadence when the object DID have review_policy (defaults are FALLBACK only, never override). Re-read object's review_policy before falling back.
- Sweeper missed a fired trigger because the trigger string didn't match exactly. Use case-insensitive substring match: `any(fired.lower() in policy_trigger.lower() for fired in fired_triggers)`.

## Guardrails

- Do NOT mutate `belief_delta`, `claims`, `key_dependencies`, `probability_view`, `falsifiers`, `scenario_triggers`, `notes` (except sweeper-side prose tail like `freshness_sweep: <YYYY-WNN> <new_state>`), `cross_theme_links`, `expected_winners`, `expected_losers`, `pm_acknowledged_by`, or any other body field. The ONLY mutations sweeper makes to walked objects are `freshness_state` and `updated_at_utc`.
- Do NOT delete or edit prior freshness_event rows. Append-only.
- Do NOT call external APIs. Sweeper reads on-disk state only.
- Do NOT auto-revive stale objects. Revive requires PM-authored belief_delta evidence.
- Do NOT promote a `due` state directly to `stale` mid-cycle if `now < scheduled_for + stale_after_days`. Honor the grace period.
- If a thesis or theme is missing schema_version (pre-v1.6 lazy file), SKIP it; freshness_state is undefined for those objects until they migrate.

## Self-test

Run with:

```bash
./.venv/bin/python -m src.cli.tradectl test-thesis-agent research-theme-staleness-sweeper
```

Fixtures live under `tests/thesis_cluster_fixtures/research-theme-staleness-sweeper/`:

- `01_first_pass_emits_first_evaluation` — walking a fresh object that has no prior freshness_state field; sweeper emits a `first_evaluation` row and sets `freshness_state="fresh"`
- `02_cadence_stale_transition` — walking an object whose `scheduled_for_at_utc` is in the past beyond stale_after_days; sweeper emits `cadence_stale` row and sets `freshness_state="stale"`
- `03_revive_requires_belief_delta` — walking a stale object alongside an evidence_record with pm_acknowledged=true + changed_dimension=conviction; sweeper emits `revived` row + flips state back to `fresh`
