---
name: research-theme-bootstrapper
description: Dual-stage similarity-and-negotiation orchestrator + executor for new theme creation. Stage A — given a candidate scope (from PM-driven request OR from a `research-theme-discovery-scanner` candidate), perform multi-dimensional similarity scan against ALL existing themes, propose ONE of five negotiation outcomes (admit_new | merge_into_existing | narrow_existing_then_admit | carve_out_from_existing | subordinate_to_existing), and write `bootstrapper_proposal.json` + `bootstrapper_proposal.summary.md`. Stage B — given the owner's round-2 arbitration decision, execute the chosen path against `data/research/themes/metadata/` (4 implemented branches + 1 raise branch). Use ONLY after `research-theme-report-owner` round-1 confirms a new candidate is worth arbitrating. Has STRICT input isolation: Stage B does NOT see Stage A's proposal — Stage B trusts only the owner's round-2 decision (prevents LLM context leak T03 + A14).
---

# Theme Bootstrapper

> **Reader gain (Rule 36)**: by the time Stage A is done, the PM should be able to (a) tell which existing themes legitimately overlap with the candidate and on which dimensions, (b) tell which dimensional scores were deterministically computed (and are therefore not LLM-judgment) vs which were LLM-computed (and need a sanity check), (c) tell which of five negotiation outcomes the bootstrapper recommends and why, (d) tell whether following the recommendation would invalidate any existing theme's `scope_boundary`. By the time Stage B is done, the PM should be able to read the changed `themes/metadata/` files and tell exactly what was created, merged, narrowed, or carved out — with a writer sidecar trail.

> **Length / scope discipline (maintainer note).** This file is the LARGEST SKILL in the cluster (~400 lines, two stages, five branches). That is intentional — Stage A and Stage B share strict input-isolation contracts and one-of-five branch logic that would lose its joint contract if split prematurely. But the size is a known maintenance risk. **Triggers for splitting into `theme-bootstrapper-stage-a/SKILL.md` + `theme-bootstrapper-stage-b/SKILL.md`**:
>
> - Total file length crosses ~600 lines, OR
> - A 6th branch is added to Stage B, OR
> - Stage A grows a 3rd LLM-scored dimension (currently 2: scope_boundary + scenario_map semantic overlap)
>
> Until any of these triggers, KEEP IT WHOLE. The cost of two SKILLs that drift on their shared isolation contract is higher than the cost of one long SKILL. If you are reading this and considering a split for "readability" reasons alone — don't. Add a section anchor instead.

> **Naming convention — read wide, write strict.** New IDs minted by Stage B — `themes/metadata/<id>.json`'s `id` field, `subthemes[].id`, `candidate_slug` — must be **snake_case** (`^[a-z][a-z0-9_]*[a-z0-9]$`). Stage B's `_check_themes_metadata_stage_b_extras` validator rejects any new id with a hyphen for branches `admit_new` / `narrow_existing_then_admit` / `carve_out_from_existing_confirmed`. References from Stage A to existing themes — `neighbor_themes_evaluated[]`, `dimension_scores` keys, `dimension_score_provenance` keys, `synthesis_narrative_per_theme` keys — use the **transitional read pattern** `[a-z0-9_-]` so Stage A can legitimately compare against historical hyphen-case themes (`ai-datacenter-power-and-balance-of-plant`) AND future snake_case ones. The 8 historical hyphen-case files are NOT force-migrated — they will be naturally superseded as PM re-builds metadata downstream of Plan B. Stage B Branch 3 (`narrow_existing_then_admit`) edits hyphen-case neighbors in place — do NOT rename the file, only edit content.

## Why This Skill Exists (生态位)

The trading-platform has THREE entry points where a "new theme" question can arise:

1. **PM-driven** — "请帮我开一个 theme on X" → arrives at `research-theme-report-owner` round-1 → if owner says "open is worthwhile", routes here Stage A
2. **AI bottom-up** — `research-theme-discovery-scanner` proposes candidates → PM picks one → arrives at `research-theme-report-owner` round-1 → routes here Stage A
3. **Update existing theme** — `research-theme-report-owner` invokes `research-theme-knowledge-and-package-curator` directly; bootstrapper is NOT involved

Bootstrapper exists because the question "should this become a new theme, or does it belong inside / next to / under / instead-of an existing theme?" is **not the same** as the question "is this candidate worth opening at all?" (which is owner round-1) and **not the same** as the question "what should the new theme say in its first report?" (which is `research-theme-knowledge-and-package-curator`).

Without bootstrapper, every new-theme decision risks one of:

- silent duplication (two themes covering the same scope)
- invisible overlap (theme X claims jurisdiction over what theme Y already covers)
- scope drift (the new theme is admitted with a vague IS / IS_NOT and later quietly absorbs neighbors)

Bootstrapper makes the negotiation **explicit, dimensional, and PM-confirmed** before any `themes/metadata/` file is written.

## Two Stages, Two Inputs, Two Outputs

| Stage | Trigger | Input | Output | Hand-off |
|---|---|---|---|---|
| **A — Arbitration** | `research-theme-report-owner` round-1 verdict = "worth arbitrating" | candidate description + slim-slice neighbor metadata + precomputed overlap scores | `bootstrapper_proposal.json` + `bootstrapper_proposal.summary.md` | back to `research-theme-report-owner` for round-2 decision |
| **B — Execution** | `research-theme-report-owner` round-2 decision (with `pm_explicit_confirm: true`) | owner round-2 decision JSON + relevant existing `themes/metadata/*.json` (NOT Stage A's proposal) | modified / created `themes/metadata/*.json` files + writer sidecar | back to `research-theme-report-owner` for downstream routing |

**Strict input isolation between stages**: Stage B does NOT receive Stage A's `bootstrapper_proposal.json` as context. It receives ONLY the owner's round-2 decision (which already encodes the chosen outcome and any modifications PM made). This is enforced because Stage A's narrative is upstream advisory; Stage B must execute the owner-confirmed plan, not re-litigate the arbitration. See [`research_05 §2.5.4`](../../../designDoc/research_50_thesis_and_theme_agent_cluster.md) on T03 + A14.

---

## Stage A — Arbitration

### What Stage A Does

Use Stage A ONLY when:

- `research-theme-report-owner` round-1 has explicitly set `round_1_verdict: "worth_arbitrating_via_bootstrapper"`
- The candidate description (slug, IS, IS_NOT, supporting evidence) is provided
- A list of "all existing themes" slim-slice metadata is provided (the harness pre-extracts this)

Stage A is a **judgment-only** step. It does NOT modify any `themes/metadata/*.json` file. Its only outputs are:

1. `data/research/theme_candidates/<scan_id>/bootstrapper_proposal.json`
2. `data/research/theme_candidates/<scan_id>/bootstrapper_proposal.summary.md`

### Stage A Input Discipline (A14 prompt boundary)

The prompt LLM sees contains ONLY:

- `candidate.slug`, `candidate.IS_prose`, `candidate.IS_NOT_prose`, `candidate.supporting_message_ids` (from PM or scanner)
- For EACH existing theme, the **6-field slim slice** ONLY:
  - `theme_id`
  - `scope_boundary.IS` (prose)
  - `scope_boundary.IS_NOT` (prose)
  - `scenario_map.dominant` (prose, 1-2 lines)
  - `theme_tags` (string array)
  - `linked_research_ids` (string array)
- `precomputed_overlap_scores` — a structured object the harness computed deterministically before the LLM was called

Forbidden in the prompt (A14 violation if present):

- Full `themes/metadata/<theme_id>.json` body for every existing theme (would be 10× larger and contains mostly task-irrelevant control-plane state)
- Full theme reports
- The PM's chat history about why this candidate matters
- Routing rationale from upstream owner

### Stage A Process

> **Reading guide.** Each step below is tagged `[HARNESS]` (deterministic Python, runs before the LLM is called or as a post-LLM check) or `[LLM]` (your actual work this turn). If you find yourself doing a `[HARNESS]` step in your head, stop — the result is already in your input as `precomputed_overlap_scores` or will be re-derived from your output and rejected if it disagrees.

**Step 1 `[HARNESS]` — Pre-computation of structural overlaps (deterministic, T10).** Before the LLM is called, the harness computes 3 of the 5 similarity dimensions:

| Dimension | Method | Output |
|---|---|---|
| `linked_research_ids_overlap` | Jaccard(`candidate.supporting_message_ids`, `theme.linked_research_ids`) for every existing theme | `{theme_id: float}` |
| `theme_tags_overlap` | Jaccard(`candidate.implied_tags`, `theme.theme_tags`) | `{theme_id: float}` |
| `source_collection_overlap` | Jaccard of `source_collection` field looked up via `messages_index.jsonl` | `{theme_id: float}` |

These 3 maps are passed to the LLM as `precomputed_overlap_scores`. The LLM is FORBIDDEN from inventing numbers for these dimensions; it must echo the harness values byte-equal. Validator enforces byte-equality and rejects on drift.

**Step 2 `[LLM]` — Dimensional scoring of the 2 semantic dimensions only.** The LLM scores the remaining 2 dimensions per existing theme (these CANNOT be done by harness because they require reading prose):

| Dimension | Method | Output |
|---|---|---|
| `scope_boundary_semantic_overlap` | LLM reads candidate IS/IS_NOT vs theme IS/IS_NOT prose; outputs 0.0..1.0 | float per theme |
| `scenario_map_semantic_overlap` | LLM reads candidate's implied scenario direction vs theme's `scenario_map.dominant` prose | float per theme |

**Step 3 `[LLM]` — Synthesis narrative + `[HARNESS]` weighted composite.** For each existing theme, the LLM produces:

- A 1-2 sentence `synthesis_narrative` explaining whether the overlap is "duplicate / adjacent / orthogonal / parent-child" `[LLM]`
- The composite `overlap_score` is computed by the **fixed weighted formula** `0.30·linked_research_ids_overlap + 0.20·theme_tags_overlap + 0.10·source_collection_overlap + 0.25·scope_boundary_semantic_overlap + 0.15·scenario_map_semantic_overlap` `[HARNESS]` — the LLM must write this number into the proposal but the validator re-derives it from the per-dimension scores and rejects on drift > 1e-6. Do not adjust weights.

**Step 4 `[LLM]` — Recommended outcome.** The LLM picks ONE of:

| Outcome | When | What Stage B will do |
|---|---|---|
| `admit_new` | All existing themes have low overlap (composite < 0.4); candidate IS_NOT cleanly excludes neighbors | Stage B writes a new `themes/metadata/<new_theme_id>.json` |
| `merge_into_existing` | One existing theme has very high overlap (composite ≥ 0.75); candidate would be redundant | Stage B does NOT create a theme; appends `candidate.supporting_message_ids` to existing theme's `linked_research_ids` |
| `narrow_existing_then_admit` | One existing theme overlaps moderately (0.4 ≤ composite ≤ 0.75) AND its current IS/IS_NOT could be tightened to legitimately exclude the candidate | Stage B first edits existing theme's `scope_boundary.IS_NOT` to add the exclusion clause, THEN creates the new theme |
| `carve_out_from_existing` | One existing theme has high overlap (≥ 0.6) AND PM agrees the existing theme should split — candidate is a "subset that deserves its own metadata" | Stage B writes a `bootstrapper_carve_out_diff.json` dry-run FIRST; only after PM's `pm_explicit_confirm: true` on the diff does it modify existing theme + create new theme + write a `merge_audit` field on both with `merged_at_utc` |
| `subordinate_to_existing` | Candidate is conceptually a sub-thesis of an existing theme but the user / scanner explicitly wants a separate sub-theme metadata | **NOT IMPLEMENTED** in this phase. Stage B will raise `subordinate_executor_not_implemented`. Use `merge_into_existing` (and write the sub-thesis as a thesis_note instead) for now. See [`research_05 §2.5.5`](../../../designDoc/research_50_thesis_and_theme_agent_cluster.md). |

### Stage A Output Schema

`data/research/theme_candidates/<scan_id>/bootstrapper_proposal.json` — field shape, `scan_id` regex, `recommended_outcome` enum, `dimension_score_provenance.*` per-source const values, neighbor-key consistency across `dimension_scores` / `dimension_score_provenance` / `synthesis_narrative_per_theme`, and the **composite weighted formula** (`0.30·linked_research_ids_overlap + 0.20·theme_tags_overlap + 0.10·source_collection_overlap + 0.25·scope_boundary_semantic_overlap + 0.15·scenario_map_semantic_overlap`, tolerance 1e-6) are all enforced deterministically by [`data/runtime/schemas/bootstrapper_proposal.schema.json`](../../../data/runtime/schemas/bootstrapper_proposal.schema.json) plus [`src/tools/thesis_cluster_validate.py`](../../../src/tools/thesis_cluster_validate.py). Pre-condition (input must be `round_1_verdict = worth_arbitrating_via_bootstrapper` with a `candidate` block) is enforced by [`src/tools/thesis_cluster_router.py`](../../../src/tools/thesis_cluster_router.py). Run `... gate theme-bootstrapper-stage-a <input>` before, and `... validate theme-bootstrapper-stage-a <output>` after.

```json
{
  "scan_id": "scan_2026_04_19_1400Z",
  "candidate_slug": "modular_nuclear_capex_chain",
  "recorded_at_utc": "2026-04-19T14:35:00Z",
  "bootstrapper_version": "v0.1",
  "neighbor_themes_evaluated": ["ai_power_grid", "us_industrial_capex", "energy_transition"],
  "dimension_scores": {
    "ai_power_grid": {
      "linked_research_ids_overlap": 0.18,
      "theme_tags_overlap": 0.30,
      "source_collection_overlap": 0.50,
      "scope_boundary_semantic_overlap": 0.60,
      "scenario_map_semantic_overlap": 0.45,
      "composite_overlap_score": 0.42
    }
  },
  "dimension_score_provenance": {
    "ai_power_grid": {
      "linked_research_ids_overlap": "deterministic_harness",
      "theme_tags_overlap": "deterministic_harness",
      "source_collection_overlap": "deterministic_harness",
      "scope_boundary_semantic_overlap": "llm_judgment",
      "scenario_map_semantic_overlap": "llm_judgment",
      "composite_overlap_score": "weighted_composite_documented_in_proposal"
    }
  },
  "synthesis_narrative_per_theme": {
    "ai_power_grid": "Adjacent — ai_power_grid covers utility-scale grid + transmission; modular nuclear (NNE/OKLO/SMR) is a distinct asset cluster the existing IS_NOT could legitimately exclude. Not duplicate."
  },
  "recommended_outcome": "narrow_existing_then_admit",
  "recommended_outcome_rationale": "ai_power_grid's current IS_NOT does not exclude SMR; tightening it (`IS_NOT: small modular reactors / SMR — see modular_nuclear_capex_chain`) preserves both themes' integrity and admits the candidate cleanly.",
  "proposed_existing_theme_edits_if_any": {
    "ai_power_grid": {
      "scope_boundary.IS_NOT.append": "small modular reactors / SMR build-out — see `modular_nuclear_capex_chain`"
    }
  },
  "proposed_new_theme_skeleton_if_any": {
    "theme_id": "modular_nuclear_capex_chain",
    "scope_boundary": {
      "IS": "Capex chain around small modular reactors and supply-side enablers, tied to AI datacenter power demand.",
      "IS_NOT": "Utility-scale nuclear or grid transmission — see `ai_power_grid`."
    }
  }
}
```

`data/research/theme_candidates/<scan_id>/bootstrapper_proposal.summary.md` is a 30-50 line PM-readable summary covering: candidate name, top-3 neighbor themes by composite score, recommended outcome with one-paragraph rationale, what Stage B will do if PM accepts, what Stage B will do if PM picks a different outcome.

### Stage A Failure Modes

#### Caught deterministically (do not waste tokens self-checking)

`tradectl thesis-cluster gate theme-bootstrapper-stage-a` and `... validate theme-bootstrapper-stage-a` together reject any of:

- input `round_1_verdict != "worth_arbitrating_via_bootstrapper"` (gate refuses)
- output `recommended_outcome` not in the 5-value enum (`recommended_outcome_not_in_enum`)
- any deterministic-dimension `*_provenance` value other than the documented const (catches `llm_overrode_deterministic_score` indirectly: LLM cannot mark its own value as `deterministic_harness`)
- `composite_overlap_score` does not equal the documented weighted formula within `1e-6` tolerance (`composite_formula_violation` — direct catch of `llm_overrode_deterministic_score`)
- `neighbor_themes_evaluated` keys do not match `dimension_scores` / `dimension_score_provenance` / `synthesis_narrative_per_theme` keys
- any dimension score outside `[0, 1]`

The `prompt_boundary_violation_full_metadata` (A14) check is enforced by the prompt-construction harness layer, not by the validator running on the artifact — but the harness will refuse to send the prompt if the slim-slice extractor is bypassed.

#### Self-check (LLM judgment, not catchable by validator)

- The two semantic dimensions (`scope_boundary_semantic_overlap`, `scenario_map_semantic_overlap`) are scored cargo-cult-style (e.g. always 0.5) rather than reflecting the agent's actual read of the candidate's `IS_NOT` vs each neighbor's `IS_NOT`.
- `synthesis_narrative_per_theme[<theme_id>]` is generic (`"adjacent but distinct"`) rather than naming the specific axis on which they differ — the narrative is the only LLM-output that downstream PM uses to actually decide.
- `recommended_outcome = subordinate_to_existing` is chosen even though `merge_into_existing + write a thesis_note under the parent theme` would have served the same purpose. Stage B will refuse subordinate; PM should be steered toward the workaround in `bootstrapper_proposal.summary.md`.

---

## Stage B — Execution

### What Stage B Does

Use Stage B ONLY when:

- `research-theme-report-owner` round-2 has explicitly produced a decision JSON containing:
  - `chosen_outcome ∈ {admit_new, merge_into_existing, narrow_existing_then_admit, carve_out_from_existing, subordinate_to_existing}`
  - `decided_at_utc` (ISO8601 UTC)
  - `pm_explicit_confirm: true` (V01 verifiability)
  - `pm_chat_message_id` (the chat message where PM explicitly confirmed — V01 traceability)

Stage B is an **execution** step. It writes / modifies `data/research/themes/metadata/*.json` files and emits a writer sidecar.

### Stage B Input Discipline (T03 + A14 strict isolation)

The prompt LLM sees in Stage B contains ONLY:

- The owner's round-2 decision JSON (the full file)
- The candidate slug + supporting_message_ids
- For each theme that round-2 decision touches, the FULL `themes/metadata/<theme_id>.json` (Stage B needs to actually edit, so full body is required)

Forbidden in Stage B prompt (T03 + A14 isolation if present):

- Stage A's `bootstrapper_proposal.json` — Stage B must NOT re-litigate Stage A. The owner's round-2 decision IS the contract.
- Stage A's `synthesis_narrative_per_theme` text in any form
- The PM's chat history beyond the `pm_chat_message_id` reference

This is enforced by the harness's prompt construction pre-check. If `bootstrapper_proposal.json` content appears in the Stage B prompt, raise `stage_b_context_leak` and refuse to execute.

### Stage B Branches

#### Branch 1 — `admit_new`

1. Construct `data/research/themes/metadata/<new_theme_id>.json` (conforming to `themes_metadata_v1_5.schema.json`) with:
   - `theme_id: <slug>` — bootstrapper-final
   - `scope_boundary: {IS, IS_NOT}` — bootstrapper-final, **lifted from owner round-2 decision** (NOT from Stage A; owner may have refined)
   - `scenario_map: {dominant: null, alternative_paths: [], placeholder_reason: "to_be_authored_by_research-theme-knowledge-and-package-curator", placeholder_owner: "research-theme-knowledge-and-package-curator"}` — bootstrapper writes a structured placeholder, NOT prose. The next downstream step is `research-theme-knowledge-and-package-curator` knowledge-mode pass, which fills `dominant` and `alternative_paths` based on linked research. Bootstrapper must NEVER write prose into `scenario_map.dominant` even if it has a guess — that would burn the boundary between routing-layer (this skill) and content-layer (`research-theme-knowledge-and-package-curator`)
   - `linked_research_ids: <candidate.supporting_message_ids>` — bootstrapper-final
   - `theme_tags: <inferred from candidate.implied_tags, intersected with v1.5 theme_tags vocabulary>` — bootstrapper-final
   - `key_assets: []` — bootstrapper writes empty; `research-theme-knowledge-and-package-curator` populates after first knowledge-mode pass
   - `priority_bucket: "watch"` — default; `research-theme-priority-updater` later
   - `status: "candidate"` — default; flips to `active` only after `research-theme-priority-updater` decides priority
   - `lifecycle_stage: "draft_candidate"` — default; flips to `approved` after first PM-confirmed report
   - `recorded_at_utc: <now>`
   - `created_via: "bootstrapper_admit_new"`
2. Write the file (refuse to overwrite if it already exists — raise `theme_id_collision`)
3. Emit writer sidecar `<theme_id>.json.bootstrapper.json` recording owner round-2 decision hash + harness pre-compute hash
4. **Mandatory hand-off note in the response back to `research-theme-report-owner`**: include `next_required_skill: "research-theme-knowledge-and-package-curator"` and `unfilled_v1_5_fields: ["scenario_map.dominant", "scenario_map.alternative_paths", "key_assets"]`. This makes it impossible for the owner to silently route the new theme to a writer step without first running `research-theme-knowledge-and-package-curator` to fill the structural fields.

**Boundary clarification.** Branch 1 produces a v1.5 metadata skeleton with **routing-layer fields complete** and **content-layer fields explicitly empty + owned by next skill**. If you find yourself writing scenario prose, draft thesis content, or filling `key_assets` with guesses, stop — that is `research-theme-knowledge-and-package-curator`'s job, not yours.

#### Branch 2 — `merge_into_existing`

1. Load `themes/metadata/<existing_theme_id>.json`
2. Append `candidate.supporting_message_ids` to `linked_research_ids` (deduplicate)
3. Append a `merge_audit` entry: `{merged_at_utc, source: "bootstrapper_merge", candidate_slug, supporting_message_ids_added: [...]}`
4. Write back the existing theme metadata
5. Do NOT create a new theme file
6. Emit writer sidecar on the existing theme

#### Branch 3 — `narrow_existing_then_admit`

1. Load `themes/metadata/<existing_theme_id>.json`
2. Apply the IS_NOT edit specified in owner round-2 decision (`proposed_existing_theme_edits.scope_boundary.IS_NOT.append: "<exclusion clause>"`)
3. Append `merge_audit`: `{narrowed_at_utc, source: "bootstrapper_narrow", new_exclusion: "<...>", reason: "make room for <new_theme_id>"}`
4. Write back the existing theme metadata
5. THEN execute Branch 1 (`admit_new`) for the new theme
6. Emit writer sidecars on BOTH themes

#### Branch 4 — `carve_out_from_existing` (TWO-PHASE: dry-run + confirm)

This is the only destructive branch (existing theme loses scope content), so it requires explicit two-phase execution.

**Phase 4a — dry-run.**

1. Load `themes/metadata/<existing_theme_id>.json`
2. Compute the proposed `linked_research_ids` split: which IDs move to the new theme, which stay
3. Compute the proposed scope_boundary edits to existing
4. Construct `data/research/theme_candidates/<scan_id>/bootstrapper_carve_out_diff.json`:
   ```json
   {
     "existing_theme_id": "ai_power_grid",
     "new_theme_id": "modular_nuclear_capex_chain",
     "linked_research_ids_to_move": ["..."],
     "linked_research_ids_to_keep": ["..."],
     "existing_theme_scope_edits": {"IS_NOT.append": "..."},
     "new_theme_skeleton": {"...": "..."},
     "computed_at_utc": "..."
   }
   ```
5. STOP. Do NOT modify any metadata file. Surface the diff path to PM for review.

**Phase 4b — confirmed execution (separate skill invocation).**

Owner re-invokes Stage B with `chosen_outcome: "carve_out_from_existing_confirmed"` AND `pm_explicit_confirm: true` AND `observed_at_utc: <ISO8601>`. Only then:

1. Apply the diff exactly as computed (do NOT re-derive — load the diff file and execute it)
2. Write back existing theme + new theme
3. Emit writer sidecars on both with `created_via: "bootstrapper_carve_out"` / `narrowed_via: "bootstrapper_carve_out"`

If `chosen_outcome: "carve_out_from_existing"` arrives WITHOUT a corresponding diff file already existing for this `scan_id`, treat it as Phase 4a (dry-run). If the diff exists but `pm_explicit_confirm` is false or missing on the new invocation, raise `missing_pm_confirmation_round2`.

#### Branch 5 — `subordinate_to_existing` (NOT IMPLEMENTED)

```
raise subordinate_executor_not_implemented
```

Recommended PM workaround:

- Re-invoke `research-theme-report-owner` round-2 with `chosen_outcome: "merge_into_existing"`
- Then write the candidate as a `thesis_note` (via `research-thesis-drafter`) under the parent theme

When `subordinate_to` becomes a real first-class need, this branch will be implemented in a future phase. Until then, attempting it must FAIL LOUDLY (not silently fall back to merge — that would lose the PM's intent).

### Stage B Failure Modes

#### Caught deterministically (do not waste tokens self-checking)

Stage B input is an owner round-2 decision validated against [`data/runtime/schemas/owner_round_2_decision.schema.json`](../../../data/runtime/schemas/owner_round_2_decision.schema.json) plus [`src/tools/thesis_cluster_router.py`](../../../src/tools/thesis_cluster_router.py). The router rejects any of:

- `pm_explicit_confirm` not the boolean `true` → `missing_pm_confirmation_round2`
- empty `pm_chat_message_id` → `missing_pm_confirmation_round2`
- `chosen_outcome = subordinate_to_existing` → `subordinate_executor_not_implemented` (with the merge-then-thesis workaround in the message)
- `chosen_outcome = carve_out_from_existing` while a `bootstrapper_carve_out_diff.json` already exists for this scan_id (PM should have used `_confirmed`)
- `chosen_outcome = carve_out_from_existing_confirmed` while no diff file exists for this scan_id → `carve_out_diff_missing`
- `chosen_outcome = carve_out_from_existing_confirmed` without `observed_at_utc`
- override flag inconsistency — when `chosen_outcome != bootstrapper.recommended_outcome`, the validator demands `chosen_outcome_overrides_bootstrapper_recommendation = true` AND `[OVERRIDE]` prefix in `rationale` (M01 calibration)

The `stage_b_context_leak` (T03) check is enforced by the prompt-construction harness layer — it will refuse to send a Stage B prompt that contains any content from `bootstrapper_proposal.json` for this scan_id.

#### Self-check (LLM judgment, not catchable by validator)

- `theme_id_collision` — `admit_new` would overwrite an existing `themes/metadata/<theme_id>.json`. Stage B agent must check filesystem before writing. Validator does not have this context.
- `linked_research_ids_to_move_empty` — `carve_out_from_existing` Phase 4a computed an empty move list. Refuse the carve-out and steer PM toward `narrow_existing_then_admit` instead. The validator does not see the move-list contents.
- Branch-specific edits to `themes/metadata/*.json` actually preserve every untouched field byte-equal — L2 diff guard catches gross changes; agent must self-check that the surgical edit only changed what the chosen branch documents.

---

## Node Bindings

This skill currently has no entry in [`data/runtime/artifact_graph.yaml`](../../../data/runtime/artifact_graph.yaml) (themes/metadata is not yet a graph node). When admitted in a future phase, this skill will own the metadata-side node for newly created themes.

This skill consumes (Stage A):

- `data/research/themes/metadata/*.json` (slim-slice extraction by harness; LLM sees only 6 fields per theme)
- `data/research/theme_candidates/<scan_id>.json` when triggered via discovery path

This skill writes (Stage A):

- `data/research/theme_candidates/<scan_id>/bootstrapper_proposal.json`
- `data/research/theme_candidates/<scan_id>/bootstrapper_proposal.summary.md`

This skill consumes (Stage B):

- The owner round-2 decision file (path supplied by `research-theme-report-owner`)
- Full `data/research/themes/metadata/<affected_theme_id>.json` for every theme the chosen outcome touches

This skill writes (Stage B):

- New / modified `data/research/themes/metadata/<theme_id>.json`
- Writer sidecars `<theme_id>.json.bootstrapper.json`
- `data/research/theme_candidates/<scan_id>/bootstrapper_carve_out_diff.json` (Branch 4 Phase 4a only)

---

## Guardrails

- Do NOT skip the harness pre-compute step in Stage A. The 3 deterministic dimensions are NOT to be re-derived by LLM.
- Do NOT echo Stage A's prose into the Stage B prompt. Stage B is an executor of the owner-confirmed plan, not an arbiter.
- Do NOT silently fall back to `merge_into_existing` when `subordinate_to_existing` is requested. Raise loudly.
- Do NOT create / modify `themes/metadata/*.json` in Stage A — Stage A is judgment-only.
- Do NOT execute `carve_out_from_existing` in one shot. Always Phase 4a (dry-run + diff file) → wait for explicit PM confirmation → Phase 4b (apply diff).
- Do NOT write `merge_audit` without `merged_at_utc` / `narrowed_at_utc` (T11 timestamp semantics).
- Do NOT proceed in Stage B without `pm_explicit_confirm: true` AND `pm_chat_message_id` in the owner decision (V01 verifiability).
- Do NOT route Stage A output directly to Stage B. The owner's round-2 decision is the only valid Stage B entry contract.
- Do NOT write `priority_bucket` other than `"watch"` in Stage B — actual prioritization is `research-theme-priority-updater`'s territory.
- Do NOT write `scenario_map.dominant` content in Stage B — that is `research-theme-knowledge-and-package-curator`'s first knowledge-mode pass after admission.

---

## Self-test

Run with:

```bash
./.venv/bin/python -m src.cli.tradectl test-thesis-agent research-theme-bootstrapper
```

Fixtures live under `tests/thesis_cluster_fixtures/research-theme-bootstrapper/`. There are **17 files total** organized as follows:

### Stage A fixtures (3 files)

- `stage_a/input.json` — synthetic candidate (slug + IS / IS_NOT prose) + 3 synthetic neighbor themes' 6-field slim slices
- `stage_a/precomputed_overlap_scores.json` — what the deterministic harness computed for the 3 deterministic dimensions
- `stage_a/golden_proposal.json` — expected Stage A `bootstrapper_proposal.json` (LLM correctly echoes harness scores byte-equal, fills 2 semantic dimensions, picks `narrow_existing_then_admit`, fills synthesis narrative)

Plus:

- `stage_a/assertions.json` — must include: deterministic-dimension byte-equal check, 6-field slim slice check on prompt, `recommended_outcome ∈ enum`, `dimension_score_provenance` present, summary.md exists

### Stage B fixtures (14 files = 4 execution branches × 3 + 1 raise branch × 2)

For EACH of `admit_new`, `merge_into_existing`, `narrow_existing_then_admit`, `carve_out_from_existing`:

- `stage_b/<branch>/input_owner_round_2_decision.json`
- `stage_b/<branch>/input_existing_themes_metadata.json` (the full metadata bodies the harness will load)
- `stage_b/<branch>/golden_outputs/` (expected post-write metadata files + sidecars; for `carve_out`, also includes the `bootstrapper_carve_out_diff.json` from Phase 4a)

For the raise branch `subordinate_to_existing`:

- `stage_b/subordinate/input_owner_round_2_decision.json`
- `stage_b/subordinate/expected_raise.json` (the expected raise: `subordinate_executor_not_implemented`)

### Cross-stage assertions

- `stage_b/<branch>/assertions.json` must verify:
  - Stage B prompt did NOT contain Stage A's `bootstrapper_proposal.json` content (`stage_b_context_leak` check)
  - Stage B prompt DID contain `pm_explicit_confirm: true` from owner round-2
  - Output `themes/metadata/*.json` matches golden byte-equal
  - Writer sidecars present and reference the owner round-2 decision hash
  - For `carve_out`, Phase 4a diff matches golden; Phase 4b only modifies what the diff said

### Test command behavior

`tradectl test-thesis-agent research-theme-bootstrapper` runs **6 sub-cases**: Stage A + 5 Stage B branches (4 execution + 1 raise). Each sub-case is independently pass/fail. The 5 Stage B branches do NOT share state — each gets its own clean fixture set so a regression in one branch does not mask another.

Golden rebake flow: same as `research-thesis-drafter` (run command → inspect `last_run.json` → if acceptable, `cp` to golden and commit; if wrong, fix THIS SKILL.md, NOT the fixture / assertions).
