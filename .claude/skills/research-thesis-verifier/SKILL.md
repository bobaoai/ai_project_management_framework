---
name: research-thesis-verifier
description: Performs external triangulation on a drafted thesis_note v1.6. Verifies key numeric / causal / US official or US issuer quote-bearing claims with quote-first provenance discovery, official-source attempt proof, source-surface attribution, and an research-evidence-reviewer pass before any PM-facing verdict. Use ONLY after `research-thesis-drafter` has produced a draft (lifecycle_stage = "draft"). This is the SECOND agent in the thesis sub-cluster; every verifier evidence_record must route through `research-evidence-reviewer` before PM-facing consumption.
---

# Thesis Verifier

> **Reader gain (Rule 36)**: by the time this skill is done, the next agent (`research-thesis-adversary`) should be able to scan one line in `notes` plus the linked `evidence_record` and know exactly which numeric / causal / US official or US issuer quote-bearing claims have independent review behind them, which are partial, which remain pending, and which source surface supports each quote. The PM should see the research-evidence-reviewer's verdict, not the verifier's unaudited reading.

## What This Skill Does

Use this skill ONLY when:

- The input is a `thesis_note v1.6` JSON file with `lifecycle_stage: "draft"` written by `research-thesis-drafter`
- External fact-checking is desired (the default; only skip when offline / no Perplexity available, in which case still write the pending line)
- The user has NOT asked for prose editing or scope arbitration (that is drafter's or bootstrapper's territory)

This skill is the **second** worker in the thesis sub-cluster. Its job is to externally triangulate the most important factual claims, record the result as ONE prose line in `notes`, write the corresponding evidence artifacts, and route those artifacts through `research-evidence-reviewer` before any PM-facing verdict.

It is NOT:

- a prose editor (do not change drafter's `claims[]` / `key_dependencies[]` / `probability_view`)
- a falsifier writer (that is `research-thesis-adversary`)
- a lifecycle promoter (only adversary can promote `draft → active`)
- a thesis-quality judge (verifier reports facts, does not rate the thesis)

## Desired Result

The desired result is the same input JSON, in-place updated with:

- A single fixed-format prose line appended to `notes`: `external verification: <verified | partial | pending> – <one-sentence summary>`
- Possibly extended `source_research_ids[]` if external verification surfaced an additional source
- One `perplexity_log` row per Perplexity call, when Perplexity is used
- One verifier-authored `evidence_record` per verification finding, written with `ai_verified=false` at creation
- One independent `research-evidence-reviewer` pass per evidence_record before any PM-facing verdict is surfaced

By the time this skill is done, `research-thesis-adversary` should be able to (a) scan one line and instantly know the verification status, (b) trust the prose drafter wrote because verifier did not silently rewrite it, (c) decide whether falsifiers should focus on path / mechanism risk rather than basic fact risk, and (d) inspect the reviewer verdict when a quote-bearing or T1A-dependent claim matters.

## Completion Standard

This skill is complete only when ALL of the following are true:

- `notes` contains exactly ONE line matching the regex `external verification: (verified|partial|pending) – .+`
- `lifecycle_stage` is unchanged (still `"draft"`)
- `claims[]`, `key_dependencies[]`, `probability_view`, `cross_theme_links[]`, `expected_winners[]`, `expected_losers[]` are unchanged from drafter's output (byte-equal)
- `source_research_ids[]` length is ≥ the input length (only additions allowed, not deletions / reorders)
- The output JSON still validates against `thesis_note v1.6` schema
- `falsifiers[]`, `scenario_triggers[]`, `next_review_trigger`, `counter_evidence_observed[]` are ABSENT (adversary's territory)
- Each verifier finding has a corresponding `evidence_record` with `author_persona="verifier"` and `ai_verified=false` at creation
- Each evidence_record has been routed through `research-evidence-reviewer`; PM-facing output cites the reviewer's `final_verdict`, not the verifier's unaudited reading
- US quote-bearing evidence follows [`quote_provenance_and_source_surface_contract.md`](../../../designDoc/quote_provenance_and_source_surface_contract.md): quote provenance, discovered event metadata, official-source attempts, source surface, and quote status are legible in the evidence prose

If any assertion fails, this skill is not done.

## Required Invariants

These four invariants are hard requirements. They are the level this skill pins down. Prose shape, section order, and exact query wording remain flexible as long as these invariants are satisfied.

### V1: Quote-First Provenance Discovery

For any quote or phrase attributed to a person, start from the quote rather than from an assumed event. Reconstruct the provenance chain before writing any evidence verdict:

1. Search exact quote plus person.
2. Search exact quote alone.
3. Search key phrase plus person.
4. Search key phrase variants plus person.
5. Search for prior public use before the discovered event when novelty or origin is implied.
6. Extract event metadata from secondary results only as discovery clues: date, venue, event title, document title, and labels such as `prepared remarks`, `opening statement`, `embargoed until delivery`, `transcript`, `he will say`, or `according to`.
7. Use the discovered metadata to locate official or primary sources.
8. Compare the claimed surface with the found surface.

Detection boundary: the verifier starts with `site:<official domain> <event>` before discovering whether the quote is prepared text, oral delivery, media preview, or paraphrase. That path assumes the event attribution is already true.

### V2: US Official Source Attempt Proof

After quote-first provenance identifies a US official event, US regulatory event, US macro-data release, or US issuer disclosure, look up the mandatory official source pattern in [`quote_provenance_and_source_surface_contract.md`](../../../designDoc/quote_provenance_and_source_surface_contract.md), derive the specific URL or institution pattern, and perform direct official-source lookup.

The evidence prose must record:

- `attempted_official_patterns`
- `official_source_results`
- `official_source_urls`
- `secondary_sources_used_for_discovery`

If Perplexity returns only T2/T3 sources, that is not proof that official sources are unavailable. Perform direct official lookup before writing a verdict.

Detection boundary: evidence_summary says official source is unavailable, but it does not list attempted official patterns and per-pattern results.

Non-US events are outside this v0.1 contract. For those, use ordinary trust-tier judgment under `evidence_source_trust_contract.md` unless a future contract revision admits the event class.

### V3: Source-Surface Attribution

Any quote-bearing evidence must name the supporting source surface:

- `written_submission`
- `oral_delivery_prefix`
- `oral_delivery_main`
- `oral_delivery_closing`
- `media_preview_before_event`
- `post_event_paraphrase`

Trust tier and source surface are orthogonal. A `senate.gov` page can host prepared written testimony, delivered oral remarks, Q&A, and transcript material that do not support the same placement claim.

Detection boundary: evidence_summary quotes a phrase but does not say which surface supports it. The downstream reader cannot tell whether the quote is prepared, delivered, previewed, or paraphrased.

### V4: Evidence-Reviewer Pass Before PM Surface

The verifier sequence is:

1. Run the verification query or local check.
2. Write the `perplexity_log` row when Perplexity is used.
3. Write a verifier-authored `evidence_record` with `ai_verified=false` and `ai_review_log=[]`.
4. Route the evidence_record to `research-evidence-reviewer`.
5. Surface the research-evidence-reviewer's `final_verdict` to the PM.

Detection boundary: a PM-facing reply contains a verifier finding, but the evidence ledger has no corresponding evidence_record or the evidence_record has no `research-evidence-reviewer` entry in `ai_review_log[]`. That is author self-attestation.

## Node Bindings

`thesis_note` is currently **NOT** in [`data/runtime/artifact_graph.yaml`](../../../data/runtime/artifact_graph.yaml). No graph sidecar to emit. See [`research_05 §2.5.6`](../../../designDoc/research_50_thesis_and_theme_agent_cluster.md).

## Primary Inputs

Read these first:

- The drafter's `data/research/thesis_notes/<thesis_id>.json` output
- [`designDoc/quote_provenance_and_source_surface_contract.md`](../../../designDoc/quote_provenance_and_source_surface_contract.md) for quote-first provenance discovery, US official-source attempt proof, source-surface attribution, and escalation wording
- [`designDoc/evidence_source_trust_contract.md`](../../../designDoc/evidence_source_trust_contract.md) for trust_tier judgment
- **For Fed / monetary-policy claims：先读 `data/knowledge/fed/cognitive/`（Fed 领域 KB cognitive layer，由 Fed-watcher persona 叙事）**，具体：
  - `cognitive/chairs/<chair_id>.md` —— chair profile（Powell / Warsh 等），framework 源流 + 任期内 pivot + 当前 posture
  - `cognitive/speakers/<speaker_id>.md` —— 单人 speaker digest（Williams / Jefferson / Waller 等），过去 12-24 月 framework 演变 + reaffirm/hedge/shift 节奏
  - `cognitive/committee_stance/<yyyy_ww>.md` —— 周级 multi-speaker synthesis（若存在）
  - `cognitive/voting_patterns/<period>.md` —— 投票模式叙事
  - `cognitive/themes/<topic>.md` —— 跨主题叙事（look-through doctrine / FAIT arc 等）
  - 消费方式：prose payload 作为 verification 的 baseline 背景，**不复制**到 verifier 输出；用作 "是否值得对某条 claim 做 external triangulation + 去哪拉"的 route 判断
  - 若 cognitive layer 内容与 claim 不符，**优先 trust cognitive layer**（它已做过 T1 discipline），然后在 notes 的 verification 行标 contradiction
  - 若 cognitive layer 对某 claim 显式 pending T1（见各 .md 的 §Raw / T1 gaps），此时允许 verifier 直接下钻 T1 URL（fed.gov / senate.gov / newyorkfed.org 等）补 gap
- For each numeric / causal claim that needs external check （**经 Fed KB 判断仍需外部** 或 **非 Fed 领域 claim**）：
  - **Perplexity (preferred — best at recent fact triangulation)** via the canonical helper [`src/tools/perplexity_search.py`](../../../src/tools/perplexity_search.py); see `### Canonical Perplexity Helper` below for invocation
  - Direct URL fetch (when Perplexity returns inadequate sources)
  - Local time-series in `data/market/` or `data/macro/` if the claim is a quantitative market / macro fact
  - Local research archive in `data/research/messages/` for cross-corroboration
- `data/research/themes/metadata/<theme_id>.json` is read-only here; do NOT modify it

### Fed KB 作为上游的意义

Fed KB cognitive layer 是本 project 第一个"领域 distilled 叙事层"（由 [`fed_knowledge_base_initiative`](../../../designDoc/progress/fed_knowledge_base_initiative.md) 建立）。它的存在让 verifier 对 Fed-related claim 不再每次 Perplexity 零拉：如果 drafter 引用 Waller 4/17 Auburn speech 或 Powell FAIT framework，verifier 先读 `cognitive/speakers/waller.md` / `cognitive/chairs/powell.md`，90% 的 verification context 已被 Fed-watcher persona 承载，零拉只在 cognitive layer 明示 pending T1 时触发。这个消费方式让 verifier 节省 token、保持信号连贯、跨 thesis 复用 Fed 领域基础判断。

### Canonical Perplexity Helper

> **Reader gain (Rule 36)**: by naming the exact helper invocation here, the next verifier does not have to rediscover the script (a real failure mode — agents tend to reach for ad hoc `WebSearch` when the canonical helper exists but is undocumented in the SKILL). The helper enforces a uniform query / date-window / preset shape so verifier outputs stay comparable across runs.

The repo ships a CLI wrapper at [`src/tools/perplexity_search.py`](../../../src/tools/perplexity_search.py). Use it instead of any ad hoc web-search tool whenever Perplexity is the right verification surface. Auth via env var `PERPLEXITY_API_KEY` (set in shell or `.env`).

Default invocation for thesis verification (`agent` mode, single-step, factual temperature):

```bash
./.venv/bin/python src/tools/perplexity_search.py \
  --api agent \
  --preset fast-search \
  --query "<one narrow factual question, e.g. 'US 1y real rate value on 2026-04-09 from FRED'>" \
  --start-date 2026-04-08 \
  --end-date 2026-04-11 \
  --max-steps 1 \
  --output-format markdown
```

Invocation discipline:

- **One claim per call.** Verifier triangulates 1-2 top claims; that is 1-2 helper calls, not a sweeping multi-claim query.
- **Always pass `--start-date` / `--end-date`** to bound the search window. Drafter's claims usually have a 1-7 day natural window; widening past that pulls noise.
- **For quote-bearing claims, start quote-first.** Search the exact quote and variants before accepting the claimed event or surface.
- **For US official / issuer claims discovered from quote search, record official-source attempts.** Name the concrete official source family from `quote_provenance_and_source_surface_contract.md`, such as `senate.gov`, `govinfo.gov`, `federalreserve.gov`, `sec.gov/edgar`, or the issuer IR domain.
- **Default `--preset fast-search` + `--max-steps 1`.** Escalate to `--preset pro-search` (and optionally `--max-steps 2-3`) only for mechanism-heavy verification (e.g., `did the Fed actually look through supply-side oil inflation in the 4/16 minutes`). The fast-search default keeps cost low.
- **`--api search` vs `--api agent`**: prefer `agent` for verification (it returns one synthesized answer with citations). Use `search` only when you specifically want a paginated list of raw results.
- **Capture failures as evidence**, not as silent skips. If the helper returns `pending` / no usable source / contradictory sources, write the line as `partial` or `pending` per the rules above and name the failure mode in the prose; do NOT fall back to `WebSearch` and pretend the verification was canonical. If `PERPLEXITY_API_KEY` is missing, set the line to `pending – Perplexity helper unavailable (PERPLEXITY_API_KEY missing); claims unverified, adversary should revisit if/when key is restored` and stop. Do NOT improvise a non-canonical web tool just to populate a `verified` or `partial` line.

Common helper failure modes and how to tag them in `notes`:

- `Missing PERPLEXITY_API_KEY environment variable` (raised at line 138 of the helper) → `pending – Perplexity helper unavailable (env)`; do not `verified`.
- HTTP 4xx / 5xx from the API → `pending – Perplexity API <status code>`; record the verbatim error in the verifier's run log if available.
- Helper returns clean answer but cites only paywalled / second-hand sources for a numeric claim → `partial – sources behind paywall, primary corroboration not confirmable from public surface`.
- Helper returns answer that contradicts drafter → see verification rules below: write `partial` or `pending` with the contradiction, do NOT silently rewrite drafter's prose.

## Required Thesis Note Output Schema

Same thesis_note file as input. Two fields are touched:

- `notes`: append (or set if empty) the fixed-format line
- `source_research_ids`: optionally extend with new IDs

The full thesis_note schema lives at [`data/runtime/schemas/thesis_note_v1_6.schema.json`](../../../data/runtime/schemas/thesis_note_v1_6.schema.json); the verifier-specific extras (notes line regex, at-most-one verification line, single-source flag) are enforced in [`src/tools/thesis_cluster_validate.py`](../../../src/tools/thesis_cluster_validate.py). Pre-condition (verifier may only run on `lifecycle_stage = "draft"` without an existing verification line) is enforced by [`src/tools/thesis_cluster_router.py`](../../../src/tools/thesis_cluster_router.py). Run `./.venv/bin/python -m src.cli.tradectl thesis-cluster gate research-thesis-verifier <input>` before, and `... validate research-thesis-verifier <output>` after.

```json
{
  // ... all drafter fields unchanged ...
  "source_research_ids": ["rid_1", "rid_2", "ext_reuters_2026_04_18_us_real_rates"],
  "notes": "external verification: partial – top claim's `1y real rate negative` confirmed via FRED; second claim's `Q3 hyperscaler capex +30% YoY` could not be re-confirmed within window, marked partial"
}
```

## Evidence Ledger Emission

> **Reader gain (Rule 36)**: by emitting structured `evidence_record` and `perplexity_log` rows alongside the in-place `external verification:` line, each verifier run leaves an auditable belief-delta trail that downstream `research-theme-report-reviewer` and PM review can index by `evidence_id`. Without this, the verification line decays into prose that the next reviewer must re-parse to recover what was actually checked.

**v0.1 dual-write contract** — verifier writes BOTH the legacy in-place `external verification:` line (drafter/adversary readers depend on it) AND the new ledger artifacts. Both surfaces are mandatory; the prose line may be culled in a future schema bump.

The dual-write is not complete until `research-evidence-reviewer` has appended one review entry to the evidence_record. The verifier's own reading is an authoring output, not an independent verdict.

### A. perplexity_log row per Perplexity call

Every invocation of [`src/tools/perplexity_search.py`](../../../src/tools/perplexity_search.py) appends ONE JSON object as a new line to [`data/research/perplexity_log.jsonl`](../../../data/research/perplexity_log.jsonl).

Schema: [`data/runtime/schemas/perplexity_log_v0_1.schema.json`](../../../data/runtime/schemas/perplexity_log_v0_1.schema.json) (validate before append).

Required fields per row:

- `log_id`: snake_case slug `<topic>_<yyyy_mm_dd>_<short_qualifier>` (e.g. `warsh_4_21_hearing_synthesis_2026_04_24`)
- `schema_version`: `"v0.1"`
- `recorded_at_utc`: ISO 8601 UTC instant when the row was appended (atomic with the call)
- `observed_at_utc`: same instant when call+write are atomic; if backfilling, the original call instant
- `caller_persona`: `"verifier"`
- `purpose`: `"thesis_external_verification"` for canonical thesis triangulation; `"thesis_null_finding_check"` when explicitly probing for absence of public statements
- `query`: the verbatim Perplexity prompt
- `response_summary`: prose 30–4000 chars; do NOT copy full Perplexity output (it lives at the source URLs); summarize key facts + citations
- `source_urls`: array of urls Perplexity cited; **empty array is intentional** for null-findings
- `linked_thesis_ids`: `[<thesis_id>]`
- `linked_theme_ids`: optional, theme ids the call serves
- `ai_generated`: `true`
- `notes`: optional caller-side context (PM authorization rationale, query construction reasoning, etc.)

Charter §III archive immutability: once written, perplexity_log rows are NOT edited. If the same query is re-run later and yields different output, append a new row with `supersedes_log_id` pointing to the original.

### B. evidence_record per verification finding

After the `external verification:` line is appended, write ONE JSON file at `data/research/evidence_ledger/<weekiso>/<evidence_id>.json` capturing the verification's belief-delta.

Schema: [`data/runtime/schemas/evidence_record_v0_2.schema.json`](../../../data/runtime/schemas/evidence_record_v0_2.schema.json) (validate before write).

Path convention: `<weekiso>` = current ISO week (`YYYY-WNN`). `<evidence_id>` = `<weekiso_short>_verifier_<thesis_topic>_<verification_outcome>` snake_case slug (e.g. `2026_w17_verifier_warsh_external_verification_partial`).

Required field shapes for a verifier evidence_record:

- `author_persona`: `"verifier"`
- `ai_generated`: `true`
- `ai_verified`: **`false` at write time**. Authoring persona MUST NOT self-flip to `true`. The independent `research-evidence-reviewer` subagent (B.0.7) is the only AI gate that may flip `ai_verified=true`, after re-judging trust_tier + belief_delta coherence + source-content support. schema v0.2 R3 enforces: `ai_verified=true` ⟹ ≥1 ai_review_log entry with final_verdict='verified'; reviewer_persona enum excludes verifier so self-review is structurally impossible
- `ai_review_log`: **`[]` at write time** (REQ field per v0.2 schema; minItems=0 allowed at creation). Reviewer subagent appends entries later
- `pm_acknowledged`: `false` (PM must explicitly confirm before this evidence drives any thesis lifecycle transition; the v2.0 schema bump will enforce minItems=1 on lifecycle=active)
- `schema_version`: `"v0.2"` (current canonical schema; see [`data/runtime/schemas/evidence_record_v0_2.schema.json`](../../../data/runtime/schemas/evidence_record_v0_2.schema.json))
- `source_type`: `"perplexity_verify"` for canonical thesis verification calls
- `source_quality`: `"primary"` if all top-claim corroboration came from primary sources (FRED, fed.gov, central bank releases, regulatory filings); `"secondary"` for sell-side / press wire mix; `"inferred"` if the finding rests on aggregated null-finding or pattern observation rather than direct citation
- `source_refs[]`: ≥1 entry. Mandatory pattern: include the perplexity_log id(s) just appended (system=`perplexity_log`, trust_tier=`none`) AND the thesis_index id (system=`thesis_index`, trust_tier=`none`). To make `ai_verified=true` legal after reviewer pass, ALSO include ≥1 `external_url` entry pointing to the underlying T1 source URL with the matching `trust_tier` (T1A/T1B/T1C/T1D); see [`designDoc/evidence_source_trust_contract.md`](../../../designDoc/evidence_source_trust_contract.md) §2 for tier judgment. Caller AI evaluates the URL's publisher and assigns trust_tier; the research-evidence-reviewer subagent independently re-judges. Internal-system refs (perplexity_log / thesis_index / messages_index / snapshots_index / themes_metadata) MUST carry `trust_tier="none"` even when the underlying content is from a primary publisher. Only `system="external_url"` may carry T1A/T1B/T1C/T1D/T2/T3
- `evidence_summary`: 50–800 char prose. Must explicitly tag which `claim[i]` was checked and which causal-chain node (`demand`/`supply`/`pricing`/`policy`/`adoption`/`margin`/`scope_boundary`) the verification touches. For US quote-bearing evidence, also make the provenance fields from `quote_provenance_and_source_surface_contract.md` recoverable in prose: `quoted_text`, `attributed_person`, `discovered_event`, `discovered_event_date`, `claimed_surface`, `found_surface`, `semantic_status`, `quote_status`, `prior_public_use`, and `official_source_attempts`
- `linked_objects[]`: 1 entry per thesis whose claim(s) were verified, typically `[{object_type: "thesis", object_id: <thesis_id>, update_direction: "support" | "ambiguous", affected_chain_node: <enum>, magnitude: "minor" | "moderate" | "major", confidence: <enum>}]`. `confidence` follows charter §V four-tier (`high` / `medium` / `low` / `exploratory`); pick `high` only when ≥2 independent primary sources corroborate
- `belief_delta` (REQ): four prose fields
  - `prior_state`: drafter's belief snapshot before verification (paraphrase the cited claims, NOT the full prose)
  - `posterior_state`: belief after verification — explicitly state which claims are `verified` vs `partial` vs `pending`, mirroring the in-place `external verification:` line
  - `changed_dimension`: typically `"causal_chain_node"` (mechanism modification) or `"conviction"` (PM-conviction adjustment hint); use `"adversarial_resolution"` only when verification specifically resolves a previously-flagged unresolved objection
  - `rationale`: prose explaining why this evidence triggers the delta — must reference the specific source_refs entries
- `caused_transitions[]`: empty array `[]` at write time (verifier cannot promote lifecycle); a future PM-ack-driven transition may backfill this
- `recorded_at_utc` / `updated_at_utc`: same ISO 8601 UTC instant at write time
- `observed_at_utc`: ONLY fill if the evidence anchors to a single point external event such as a speech delivery, statement publication, hearing, filing, or earnings call. Multi-day cross-window syntheses such as "checked 4/21-4/24 silence" MUST leave this field absent. Do not use the verifier call time as `evidence_record.observed_at_utc`

### C. Mapping the in-place line to the ledger

| In-place line outcome | evidence_record `update_direction` | evidence_record `confidence` |
|---|---|---|
| `verified` (≥2 independent primary corroborations) | `support` | `high` |
| `partial` (some claims verified, some not) | `ambiguous` | `medium` |
| `pending` (sources unavailable / contradictions) | `ambiguous` | `low` or `exploratory` |

Outright contradiction with drafter (rare, but explicit) → `update_direction: "weaken"`, `confidence` whatever the contradicting source's quality supports.

### D. Failure modes specific to ledger emission

- evidence_record file written but Perplexity call NOT logged in `perplexity_log.jsonl` → ledger has dangling source_ref. ALWAYS append the perplexity_log row first, then write evidence_record citing its log_id.
- evidence_id slug collides with an existing file in the same weekiso directory → bump the qualifier suffix (e.g. `..._partial_v2`) and continue. Do NOT overwrite an existing evidence_record.
- Skipping evidence_record emission "because verification was pending" → still emit. A `pending` outcome IS a belief delta (prior was unverified-by-default; posterior is unverified-and-source-unavailable, with reason). The PM ack workflow needs to see pending records to know what to retry.
- Stopping after writing the evidence_record but before research-evidence-reviewer pass → the skill is still incomplete. Surface a blocker/status note, not a PM-facing verdict.

## Verification Rules

- **Single-source draft is the highest-priority case.** If input `notes` contains the flag `single source – verifier 必须扩源`, then the primary task this round is **expanding source breadth**, not just appending one verification line. Concretely:
  - Search for ≥2 additional independent sources covering `claims[0]` (primary source preferred for numeric claims; cross-publisher corroboration for causal claims)
  - Add every source you actually consulted to `source_research_ids[]` with `ext_<source>_<yyyy_mm_dd>_<topic>` slugs, even sources that did NOT corroborate (negative coverage is also evidence)
  - Only mark `verified` if the top claim now has ≥2 independent corroborating sources. If you only added 1, the line must be `partial` and explicitly say `single-source flag carried, verifier 仅补充 1 source — adversary 应继续追问`
  - Treat "I added 1 source and called it verified" as a verification failure, not as a successful single-source rescue
- Pick the **top 1-2 claims by importance** (i.e., `claims[0]` and `claims[1]`) for verification. Do NOT try to verify every claim — verifier is a triangulation step, not a full audit.
- For numeric claims, prefer **primary sources** (FRED, central bank releases, regulatory filings, company filings) over secondary commentary (sell-side notes).
- For causal claims, look for **independent corroboration** (≥2 sources that are not citing each other).
- For US quote-bearing claims, apply V1-V3 before deciding outcome. Separate semantic truth from verbatim / surface truth. If the meaning is supported but the exact quote or placement is wrong, write `semantic_status=semantic_true` and explicitly mark the surface correction instead of flattening the surfaces.
- For T2/T3-only claims about US official wording, use the escalation language from `quote_provenance_and_source_surface_contract.md` and keep `ai_verified=false` unless a later official source anchor and research-evidence-reviewer pass satisfy the gate.
- The fixed-format line:
  - `verified` — top claims have ≥2 independent corroborating sources within the relevant window
  - `partial` — at least one top claim has ≥1 corroboration; at least one could not be confirmed (state which)
  - `pending` — external sources unavailable (offline, Perplexity down, paywall) OR all top claims could not be confirmed
- Add new external source IDs to `source_research_ids[]` using a stable slug like `ext_<source>_<yyyy_mm_dd>_<topic>` (e.g. `ext_fred_2026_04_15_dgs1`, `ext_reuters_2026_04_18_us_real_rates`).
- If the verified value contradicts the drafter's claim materially (e.g., drafter said `1y real rate -1%` but FRED shows `+0.5%`), DO NOT silently rewrite drafter's prose. Set the line to `partial` or `pending` and state the contradiction in the line. Adversary will pick this up and may write a counter_evidence_observed.

## Failure Signals

### Caught deterministically (do not waste tokens self-checking)

`tradectl thesis-cluster gate research-thesis-verifier` and `... validate research-thesis-verifier` together reject any of:

- input `lifecycle_stage != "draft"` (gate refuses to run)
- input `notes` already contains an `external verification:` line (gate refuses; verifier must replace, never stack)
- output `notes` contains a malformed verification line (regex `external verification: (verified|partial|pending) – .+`)
- output `notes` contains more than one `external verification:` line
- output `lifecycle_stage` changed (validator + diff guard)
- output adds adversary fields (`falsifiers`, `scenario_triggers`, `next_review_trigger`, `counter_evidence_observed`) — `lifecycle_stage = "draft"` schema rule rejects
- output fails to bump `updated_at_utc` while adding a verification line

### Self-check (LLM judgment, not catchable by validator)

- Verifier rewrote drafter's prose silently. The L2 diff guard will catch byte-level changes to `claims`, `key_dependencies`, `probability_view`, `cross_theme_links`, `expected_winners`, `expected_losers`; semantic re-paraphrasing while keeping bytes equal is impossible by construction. But re-confirm: `claims[i]` and `probability_view` should be byte-equal to input.
- Verifier picked `verified` when one of the top claims was actually only weakly supported. Choose `partial` whenever any top claim could not be re-confirmed.
- Verifier skipped quote-first provenance. If the first search assumes the event and surface instead of discovering them from the quote, rerun before writing evidence.
- Verifier omitted official-source attempt proof. If the evidence says official source is missing but does not list attempted official patterns and results, rerun before writing evidence.
- Verifier omitted source-surface attribution. If `evidence_summary` contains a quote but does not say whether it came from `written_submission`, `oral_delivery_prefix`, `oral_delivery_main`, `oral_delivery_closing`, `media_preview_before_event`, or `post_event_paraphrase`, the evidence is incomplete.
- Verifier surfaced a PM-facing verdict before research-evidence-reviewer pass. If there is no evidence_record or no `research-evidence-reviewer` entry in `ai_review_log[]`, the only allowed output is a blocker/status note.
- Verifier appended a new external source ID using a non-stable slug (e.g. wall-clock now, query-string-bearing URL). Use `ext_<source>_<yyyy_mm_dd>_<topic>` shape.
- Verifier added an enum field like `evidence_strength: "moderate"` instead of writing the verification prose. v1.6 explicitly rejected enums in favor of the prose verification line — see [`research_06 §4`](../../../designDoc/research_40_thesis_note_schema_v1_5.md).

## Guardrails

- Do NOT change drafter's prose. If a fact is wrong, mark `partial` / `pending` in the line; let adversary write counter_evidence_observed.
- Do NOT write `falsifiers[]`. Falsifiers are forward-looking ("if X happens, thesis fails") — verifier is backward-looking ("did the cited fact hold").
- Do NOT promote `lifecycle_stage`. That is adversary's responsibility after stress-testing.
- Do NOT call destructive tools. All external lookups are read-only.
- Do NOT surface a PM-facing verified / false / partial verdict until `research-evidence-reviewer` has reviewed the evidence_record. Before that, describe the state as "verifier provisional reading" or "blocked pending research-evidence-reviewer".
- Do NOT add an enum field like `evidence_strength: "moderate"`. v1.6 explicitly rejected enums in favor of the prose verification line — the prose forces the verifier to write `verified what / pending what` rather than collapsing to a single label (see [`research_06 §4`](../../../designDoc/research_40_thesis_note_schema_v1_5.md)).

## Self-test

Run with:

```bash
./.venv/bin/python -m src.cli.tradectl test-thesis-agent research-thesis-verifier
```

Fixtures live under `tests/thesis_cluster_fixtures/research-thesis-verifier/`:

- `input.json` — a hand-prepared simulated drafter output that contains a verifiable number (the harness substitutes a known FRED-style series) and a non-verifiable one
- `golden_output.json` — expected verifier output (notes line + 1 added external source ID; drafter prose byte-equal)
- `assertions.json` — regex match on notes line, byte-equal check on drafter prose, source_research_ids length monotonic

The fixture is **independently prepared** (not piped from a real drafter run), so verifier remains testable even if drafter's prompt changes.

Golden rebake flow: same as `research-thesis-drafter` (run command → inspect `last_run.json` → if acceptable, `cp` to golden and commit; if wrong, fix THIS SKILL.md).
