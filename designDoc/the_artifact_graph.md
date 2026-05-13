---
title: Artifact Dependency Closure Contract
status: active_draft
layer: T0
t0_layer_id: the_artifact_graph
canonical_owner: designDoc/the_artifact_graph.md
---

# Artifact Dependency Closure Contract
**Version 0.1 - 2026-04-17**

## 0. Contract Capsule

Machine-audit block. Keep paths, ids, aliases, commands, and ledger pointers plain; use citation ids only in body prose and `References`.

```yaml
layer: T0
t0_layer_id: the_artifact_graph
status: active_draft
canonical_owner: designDoc/the_artifact_graph.md
scope: artifact goal-node dependency closure, artifact node identity, dependency edges, freshness predicates, graph-admitted builder binding, sidecar hash contracts, graph / material-object boundary inheritance, planner / executor semantics, and graph-first PM-facing artifact admission
non_goals:
  - deciding which user task line owns the request, which belongs to the_task_routing
  - domain-specific schema semantics inside T1 workflows
  - material object semantics and child material contract boundaries, which belong to designDoc/material_00_overview.md
  - PM belief, investment judgment, and final prose quality
  - TradeCLI code-admission discipline, which belongs to the_tradecli_code_management
inputs:
  - designDoc/the_task_routing.md
  - designDoc/the_timestamp_semantic.md
  - data/runtime/artifact_graph.yaml
  - graph-admitted artifact sidecars
outputs:
  - artifact node model
  - freshness predicate semantics
  - canonical builder admission rules
  - tradectl plan / produce contract
  - writer sidecar artifact_graph section contract
truth_surfaces:
  - data/runtime/artifact_graph.yaml
  - src/tools/artifact_graph.py
  - src/tools/artifact_produce.py
  - src/cli/tradectl.py
  - .cursor/rules/42_artifact_graph_admission.mdc
runtime_triggers: see Machine Audit Runtime Surfaces
downstream_consumers:
  - graph-admitted PM-facing report skills
  - T1 material contracts and material-producing workflows
  - tradectl plan / produce
  - writer sidecar consumers
  - routing and package-check operators
open_decisions:
  - expanded builder.invoke coverage for L3/L4 ai_writer and composite nodes
  - automatic sidecar emission inside ai_writer builders
  - formal parameter resolvers for deep dependency walks
  - must_be_referenced_in_output enforcement details
review_gate: design-doc-reviewer for this contract; engineering-project-review when planner / executor runtime behavior changes
runtime_surface_ledger: see Machine Audit Runtime Surfaces
verification_hooks: see Machine Audit Runtime Surfaces
```

This document defines the repo's next-generation routing and execution substrate.

It does not replace [T0-Task-Intake]. It introduces a deeper substrate underneath that contract so that:

- the four routing layers in that document still hold (`task mainline`, `skill`, `deterministic builder / package`, `writer gateway`)
- but their boundaries are no longer enforced only by verbal rules and skill prose
- they are instead enforced by an explicit `artifact graph` whose nodes, freshness contracts, and dependency edges decide what work must run before any PM-facing artifact is produced

This is an AI-facing design document. It is intentionally detailed.
The purpose is to give downstream agents, skills, and future design work a stable substrate that prevents the recurring failure mode where:

- a verbal "must do X before Y" rule exists in some skill,
- but the agent finds a shorter path through ad hoc scripts,
- and produces a PM-facing artifact on stale or partial inputs.

For this topic, this document should be treated as:

- written primarily for AI consumption rather than deck-style human scanning
- detailed by default when detail reduces routing ambiguity
- the canonical drafting surface for the artifact-graph substrate before that substrate is propagated into rules, skills, and CLI tooling

---

## 1. Why This Document Exists

### 1.1 Recurring failure mode

The repo has accumulated a healthy stack of:

- task mainlines
- skill contracts
- builder/package layers
- writer gateways
- hard rules under `.cursor/rules/`

But several recent failures share one structural shape:

- a multi-step PM artifact (daily recap, portfolio decision, theme report, single-stock note) was produced
- without the agent first ensuring that all upstream data and judgment artifacts were `fresh as-of` the artifact's intended report date
- because the agent reasoned: "the canonical workflow is slow; I have lower-level capability that can produce the answer faster; the verbal rule does not strictly forbid this"

The most recent example:

- the user asked for a daily recap and a cross-day position review
- the canonical chain is `data update` → signal packets → AI technical reports → `research-current-market-reporter`'s intake / judgment / package / handoff / ds
- the agent instead ran `positions update` + `history update --symbols ...` for a chosen subset, called `build_runtime_payload` directly, and wrote a recap markdown by hand
- the artifact looked plausible but bypassed `daily_update_status.json`, the package admission gate, the judgment gate, and the writer-handoff gate

This is not primarily a discipline failure. It is a structural failure: the system has the capability surface to bypass the contract surface, and there is no machine-readable substrate that says "for this artifact, these upstream nodes must be fresh as-of this date".

### 1.2 What this substrate adds

This document proposes that the repo treat:

- every PM-facing or downstream artifact as a `node` in an explicit `artifact graph`
- every dependency between artifacts as a typed `edge` carrying a `freshness contract`
- every routing decision as a graph-traversal problem rather than a skill-template selection problem

When this substrate is in place:

- `routing-task-mode-router` is a thin policy that maps user intent to one or more goal nodes
- skills become builders for one or more nodes, not end-to-end pipelines
- "must do X before Y" rules become edge contracts, not prose paragraphs
- composite tasks (which were previously homeless or improvised) become subgraphs the router computes from the goal node set
- ad hoc shortcuts are no longer reasonable, because the agent can always check whether a node satisfies its freshness contract before producing a downstream artifact

### 1.3 Read together with

- `ai_native_trading_operating_system.md`
- Task Intake Routing Contract [T0-Task-Intake]
- `analysis_platform_and_pm_workspace.md`
- `modules/daily_data_update_dashboard.md`
- `last_session_truth_and_ingestion_boundary.md`

This document sits between [T0-Task-Intake] and the lower-level skill and rule files. It does not redefine the operating system view, nor does it micro-design any one skill. It defines the substrate the other layers should rest on.

### 1.4 Effect-first frame for this document

After reading this document, a downstream agent or designer should be able to:

- name the artifact node a request is asking for, by canonical path and report date
- name the upstream nodes that must be fresh before that artifact can be produced
- decide whether the freshness contracts on those upstream nodes are currently satisfied
- if not, produce a runnable plan that walks the dependency closure and brings each stale node back into validity
- recognize that any path that produces the artifact without satisfying those contracts is a structural error, not a stylistic preference

If the document does not give the reader those abilities, it has failed.

---

## 2. Relationship To The Existing Four Routing Layers

[T0-Task-Intake] defines four routing-relevant layers:

1. `task mainline layer`
2. `skill layer`
3. `deterministic builder / package layer`
4. `writer gateway layer`

This substrate is orthogonal, not a fifth layer.

It re-projects the four layers under one shared object model:

- a `task mainline` becomes a `goal node policy`: it tells the router which node id(s) to treat as the goal for a recurring user intent class
- a `skill` becomes a `node builder binding`: a contract for producing one or more node ids
- a `deterministic builder / package` becomes the concrete `builder` attached to one or more nodes
- a `writer gateway` becomes the concrete builder for L4 prose nodes

The four layers still hold. They now share one machine-readable substrate.

---

## 3. Core Concepts

### 3.1 Artifact node

An artifact node is anything that has all of the following:

- a stable id
- a canonical local path
- a layer label (`L0` through `L4`, see §4)
- a `session_date_market` field (legacy alias `report_date`) that is part of the node identity for date-scoped artifacts; the field semantics follow axiom T11 — see §3.10
- one explicit builder
- one explicit owner skill (may be `deterministic` for non-AI builders)
- a freshness contract (see §3.3)
- a list of upstream dependencies, each with an edge type (see §3.4)

A node represents an artifact, not an action. Actions are builders attached to nodes.

### 3.1.1 Material nodes and T1 object boundaries

Artifact Graph is the T0 graph law for any artifact that needs identity, dependencies, freshness, provenance, canonical production, or downstream readiness checks.

Material Catalog [T1-Material-Catalog] is the T1 material-object law for what material assets are allowed to mean. It owns boundaries for Raw Data, Operating Cycle Artifact, Source Card, Expert Artifact, Evidence, Thesis, Scenario, Theme, Technical Report, and support surfaces.

The inheritance rule:

```text
Artifact Graph owns the node and edge contract.
Material Catalog owns the material object contract.
```

When a material object is graph-admitted, the graph may require:

- node id
- canonical path
- material type / contract id
- producer or builder binding
- owner skill or owning workflow
- upstream dependencies
- freshness / readiness predicate
- sidecar or provenance surface

The graph must not duplicate the material boundary prose. It should point to the owning material contract and carry only the handles needed for graph traversal and audit.

Examples:

- A Source Card node can be required by the graph before a writer package runs, but Source Card allowed-use and cannot-support grammar belong to Material Catalog and Expertise.
- A Scenario node can carry freshness, producer, and dependency edges in the graph, but the Thesis anchor + Expertise Application + forward prediction boundary belongs to the Scenario material contract.
- A Technical Report node can be planned and freshness-checked by the graph, but current-market-state report semantics belong to its T1 material and research owners.

### 3.2 Node identity and session_date_market

For most date-scoped artifacts, identity is `(node_id, session_date_market)` (legacy alias: `report_date`). The field carries the asset's market session day in its own market timezone — see §3.10.

This means:

- `current-market.ds.md(2026-04-17)` is a different node instance from `current-market.ds.md(2026-04-15)`
- the canonical local path may be the same file (`data/analysis/market_observation/current-market.ds.md`), but the system tracks the market session date as a first-class field through writer metadata sidecars and frontmatter
- when the agent is asked to "write today's recap", the goal node is `current-market.ds.md(today)`; if the file on disk has `session_date_market < today`, the node is missing for `today`, regardless of mtime

For non-date-scoped artifacts (registries, indexes, profiles, schemas), identity is just `node_id`. Their freshness contract is usually source-state-based, not date-based.

### 3.3 Freshness contract

A freshness contract is the predicate that decides whether a node instance is currently `valid`.

Common predicate shapes:

- `date_anchor`: the node's `report_date` (from frontmatter or sidecar) must equal the requested instance's report_date
- `source_state_hash`: the node was produced from a hash of upstream source state that matches the current upstream state
- `blocking_flag`: a status registry says this layer is `blocking == false`
- `monotonic_at_least`: the node's underlying data has an anchor timestamp at or after a stated UTC or session boundary (`price_bars`: max(bar_start) ≥ session anchor for D)
- `series_recency_per_category`: a JSON index lists multiple series; each series's `end` date must satisfy `end ≥ D - lag_days_by_category[series.category]`, with a `default_lag_days` fallback (used for `macro_indicators` so weekly Fed publications and daily yields are each held to their own cadence)
- `recency_within_days`: a JSON file's top-level `generated_at` (or another configured field) must satisfy `generated_at ≥ D - max_age_days` (used for `big_events_calendar`)
- `referenced_existence`: the node referenced a peer artifact (e.g., yesterday's pm_action) that must merely exist and not be edited
- `composite` (virtual aggregator only): the node holds no truth of its own; validity is the conjunction of a declared set of child-node predicates (see §3.8)

Contracts compose. Example for `current-market.ds.md(D)`:

- `date_anchor`: report_date == D
- requires upstream `current-market.judgment.md(D)` valid
- requires upstream `daily_update_status.json` blocking flags for `technical`, `macro`, `news` all false as-of D
- requires upstream L2 `asset_technical_reports/*.md` for the goal observation universe each valid as-of D

### 3.3.1 Detailed semantics for each predicate type

The planner at `src/tools/artifact_graph.py` decides `FRESH / STALE / MISSING / UNKNOWN` per node by interpreting these predicates. Their precise semantics:

- `date_anchor` — date-equality check against a named source field:
  - if the `canonical_path` template contains `<D>` and the date-expanded file exists, the date is encoded in the filename itself and the anchor is satisfied (path-encoded date)
  - if the `canonical_path` is a singleton (no `<D>`), then `args.source` names where the date actually lives; v0.1 recognizes `frontmatter.report_date` (read markdown frontmatter) and `packet.<field>` (read a top-level JSON field, typically `packet.report_date`)
  - mismatch between the source date and the requested D is `STALE`; missing source field is `UNKNOWN` (the contract is intact but the file forgot to declare its date)

- `blocking_flag` — aggregated status-registry check:
  - reads `data/dashboard/daily_update_status.json` and inspects each `layers.<layer_id>.blocking` boolean in `args.layer_set`
  - any layer reporting `blocking == true` → `STALE`, with the offending layer(s) named in the reason
  - the registry's `as_of` is compared to requested D; a mismatch is noted but does not by itself turn the node `STALE`, because some layers are not re-polled every day

- `monotonic_at_least` — time-bound on underlying raw data:
  - used for `price_bars` and other node kinds whose truth lives in Postgres rather than in a file on disk
  - contract: `max(timestamp) for (symbol, interval) >= args.anchor` (typically the latest expected session-close for D)
  - shipped: the planner opens a Postgres connection via `PlatformStore`, resolves `asset_id` → `(symbol, asset_type, provider)` from `data/knowledge/asset_technicals/profiles/<asset_id>.json` (with `signal_packets/<asset_id>.json` as fallback), computes the expected anchor session for the asset class (`equity_last_completed_rth_date(D)` for equity / ETF; `futures_last_completed_session_date(D)` for futures; D itself for 24/7 markets), and compares against `max(bar_start)::date`
  - returns `FRESH / STALE` per asset_id; only true gaps (Postgres unreachable, calendar library missing, `asset_id` not in any profile or signal-packet manifest, bare `price_bars` reference with no symbol param) collapse to `UNKNOWN`

- `series_recency_per_category` — per-series cadence on a JSON index:
  - used for `macro_indicators` against `data/macro/index.json`
  - contract: every series in `index.series` satisfies `end >= D - lag_days_by_category[series.category]` (with `default_lag_days` for missing categories)
  - rationale: macro indicators are heterogeneous in cadence (UST yields are daily-business; WALCL / NET_LIQUIDITY are weekly Fed publications). A single binary "macro is stale" flag was too coarse — the planner now lists each lagging series with its category, last `end`, and the expected minimum so the next refresh action is unambiguous
  - returns `FRESH` only when every series satisfies its own cadence; returns `STALE` with the laggard list otherwise

- `recency_within_days` — recency window on a single JSON file:
  - used for `big_events_calendar` against `data/macro/calendar_watch/latest.json`
  - contract: `parse(file.<args.source_field>).date() >= D - args.max_age_days` (default field is `generated_at`)
  - rationale: a calendar fetched a month ago no longer reflects the current event window even if it parses fine; the recency check makes the planner refuse silently-aged calendars
  - returns `FRESH / STALE` directly; only file-not-found or unparsable timestamp degrade to `MISSING / UNKNOWN`

- `source_state_hash` — derivative produced from hashed upstream state:
  - used for non-date-scoped nodes such as `themes.current_priority_tree`, `themes.metadata`, `theme.knowledge`, `asset_technicals.index`
  - contract: the hash of the listed upstream sources at check time must equal the hash recorded when this node was last produced
  - v0.1 cannot check this because no writer sidecar currently records consumed upstream hashes; all such nodes surface as `UNKNOWN: source_state_hash_needs_hash_store (v0.2)`
  - v0.2 must require every `ai_writer` and `composite` builder to emit a `<artifact>.writer.json` sidecar that records `{ upstream_node_id, content_hash }` per consumed node; the planner then rehashes and compares

- `referenced_existence` — peer artifact must merely be present:
  - satisfied iff the named peer file exists; no content check
  - used for low-stakes audit-style references where a richer `must_exist_unchanged_since` contract is not needed

- `composite` — see §3.8 below.

Edge-level contracts (carried by `depends_on[*].edge`):

- `must_be_fresh` — default. Recurse into the upstream node and trust its own freshness check.
- `must_exist_unchanged_since` — read the **downstream** node's writer sidecar, find the recorded `content_hash` for this upstream (matched by `node_id` + params), and compare against the upstream file's current hash. Outcomes:
  - `FRESH` only if the upstream's own freshness check is `FRESH` and the recorded hash equals the current hash (reason: `... | must_exist_unchanged_since:hash_match=<sha12>`)
  - `STALE` if the recorded hash and current hash differ (reason: `must_exist_unchanged_since:hash_changed recorded=<sha12> current=<sha12>`)
  - `MISSING` if the upstream file is gone
  - `UNKNOWN` if the downstream artifact has no sidecar yet, no record for this upstream, or no recorded hash; this means "you have not yet committed to a hash for this upstream — you cannot claim unchanged-ness". The fix is to produce the downstream via its canonical builder and emit a sidecar.
- `optional_overlay` — never recursed; reported as `SKIPPED`. Provides interpretive context to the writer but cannot block validity.

### 3.8 Reading `tradectl plan` output: `UNKNOWN` has three distinct shapes

The planner never lies about `STALE` or `MISSING`, but `UNKNOWN` covers three very different situations. A reader who cannot tell them apart will either treat every `UNKNOWN` as alarming (slowing down every workflow) or treat every `UNKNOWN` as fine (restoring the shortcut problem). The distinction:

1. **Tool-gap `UNKNOWN` (real deferred check)**
   - This bucket has narrowed substantially: `monotonic_at_least` (price_bars), `source_state_hash` (theme metadata, etc.), `series_recency_per_category` (macro_indicators), and `recency_within_days` (big_events_calendar) all return real `FRESH / STALE` in the current build.
   - What still degrades to `UNKNOWN` is genuinely tool-gap-ish: a bare `price_bars` reference with no symbol param (the `daily_update_status` rollup is the documented case; agents should query a specific `asset_id` for a real signal), Postgres unreachable, missing `exchange_calendars`, or an `asset_id` that exists in neither profile nor signal-packet manifests.
   - **How to read it**: the planner is announcing a precise diagnostic. Fix the gap (e.g., add the missing profile, restore Postgres connectivity, query with a concrete `asset_id`) rather than treating the `UNKNOWN` as background noise.
   - **When this matters**: if the upstream node is the kind that routinely drifts (prices, regenerated indexes), treat the `UNKNOWN` as a reminder to have run the canonical builder recently. If in doubt, rerun the upstream builder; it is cheap.

2. **Input-gap `UNKNOWN` (caller under-specified the goal)**
   - `unresolved_params:<param_name>` — the node is parameterized (e.g., `signal_packet(asset_id)`), but the caller did not supply the parameter, so the canonical path cannot be resolved
   - `no_target_date_supplied` — the node needs a date but none was given
   - `frontmatter_report_date_missing` — the file exists at the expected path, but the file itself never declared its date
   - **How to read it**: the call, not the artifact, is under-specified. For parameter gaps, rerun `plan` with `--params`. For missing-frontmatter cases, the artifact was produced outside the canonical builder; this is a recap-shortcut signature and should be treated as a `STALE`-equivalent for admission purposes.

3. **Designed `UNKNOWN` (virtual aggregator; by construction)**
   - the node has no truth of its own (e.g., `data_layer.fresh`). It is a meta-node whose only job is to let many L4 nodes share one fresh-data gate instead of repeating a dependency checklist five times.
   - **How the planner handles this**: composite/virtual nodes are rolled up post-walk. The aggregator inherits `FRESH` iff every non-`optional_overlay` child is `FRESH`; `STALE` if any child is `STALE` or `MISSING` (with the offending child(ren) named in the reason as `composite_blocked_by=[...]`); `UNKNOWN` only when at least one child is itself `UNKNOWN` and none are `STALE / MISSING`.
   - **How to read it**: read the aggregator line first. If it says `STALE`, the `composite_blocked_by=[...]` reason names the exact child blocking the gate, and that child's own line carries the actionable `fix:` hint.

Admission rule for producing an L4 node:

- any `STALE` or `MISSING` on a `must_be_fresh` or `must_exist_unchanged_since` edge in the goal node's closure is a hard block
- any tool-gap `UNKNOWN` (category 1) must be acknowledged; preferably the agent reruns the upstream builder to eliminate uncertainty
- any input-gap `UNKNOWN` (category 2) must be resolved before proceeding; it is almost always a sign that the planner call itself was wrong, not that the artifact is intrinsically unreachable
- designed `UNKNOWN` (category 3) is ignored at the aggregator; judgment is deferred to its children

This three-way reading is a contract in its own right. It should be preserved as the planner evolves, even as specific messages change.

### 3.9 Writer sidecar schema (enables `source_state_hash` and `must_exist_unchanged_since`)

Every artifact file at `<canonical_path>` has a paired writer sidecar at `<canonical_path>.writer.json`. Some builders already emit sidecars to record routing info (`task_kind`, `writer_role`, `writer_backend`, etc.). The artifact graph adds one additional top-level key into that same sidecar without disturbing existing fields:

```json
{
  "task_kind": "...",            // legacy routing fields stay untouched
  "writer_role": "...",
  "artifact_graph": {
    "schema_version": "2.0",
    "graph_version": null,
    "time_semantics_contract_id": "T11",
    "time_semantics_version": "2026-04-19T06:00:00+00:00",
    "produced_for": {
      "node_id": "theme.knowledge",
      "params": { "theme_id": "gold-monetary-fragmentation" },
      "session_date_market": "2026-04-17",
      "report_date": "2026-04-17"      // legacy alias of session_date_market
    },
    "planner": {
      "tool": "src/tools/artifact_graph.py",
      "emitted_at_utc": "2026-04-17T19:09:14+00:00",
      "emitted_at": "2026-04-17T19:09:14+00:00"  // legacy alias
    },
    "status_at_emit": "FRESH",
    "reason_at_emit": "upstream_hashes_match (n=1)",
    "upstream_nodes": [
      {
        "node_id": "themes.metadata",
        "params": { "theme_id": "gold-monetary-fragmentation" },
        "edge_kind": "must_be_fresh",
        "status_at_read": "FRESH",
        "canonical_path": "/abs/path/to/gold-monetary-fragmentation.json",
        "content_hash": "1db89c1515..."
      }
    ]
  }
}
```

The `schema_version` was bumped from `"v1"` to `"2.0"` on 2026-04-19 when axiom T11 (timestamp semantics) became the contract for every date / timestamp field in the graph; see [Axiom-Timestamp] and [T0-Time] for the rules and `src/tools/time_semantics.py` for the runtime guards. Legacy field names (`report_date`, `generated_at`, `emitted_at`) remain readable during the deprecation window — the planner's `date_anchor` / `recency_within_days` contracts try the new names first and fall back to legacy with a `legacy_alias` tag in the freshness reason.

Rules:

- only the **direct** upstream dependencies of the produced node are recorded, not the entire transitive closure; deeper validity is the responsibility of each parent's own sidecar
- `optional_overlay` edges are deliberately excluded from `upstream_nodes`
- `content_hash` is SHA-256 over raw file bytes; a `null` hash is allowed for non-file upstream nodes (virtual, DB-backed, etc.)
- the sidecar is always a merge, not a replace; legacy fields in an existing `.writer.json` are preserved

How the planner reads the sidecar:

- **`source_state_hash` contract**: if the node's own sidecar exists and has `upstream_nodes`, the planner rehashes each listed canonical_path and compares. All match → `FRESH`; any mismatch → `STALE`; no sidecar → `UNKNOWN: source_state_hash_no_sidecar` (a gentle nudge to run `--emit-sidecar`).
- **`must_exist_unchanged_since` contract** (v0.2): the downstream node's sidecar will be consulted to verify the upstream node's hash at read time; this is how cross-date references like `pm_action_review` reading a prior `pm_action` become verifiable rather than promised.

How to write the sidecar without a real builder yet:

- `tradectl plan <node> --emit-sidecar auto` produces the correct sidecar at `<canonical_path>.writer.json` after planning; `auto` derives the path from the graph
- a custom path can also be provided: `--emit-sidecar <path>`
- `--verify-sidecar auto` re-verifies a sidecar without running a new plan

This mechanism is deliberately opt-in in v0.1. A builder that does not emit the `artifact_graph` section is not penalized; its node simply shows `UNKNOWN` on `source_state_hash` contracts until a sidecar is produced. As builders migrate, more of the graph moves from `UNKNOWN` to real `FRESH / STALE`.

### 3.10 Time-semantics contract (T11)

Every date / timestamp field that participates in identity, freshness, or idempotency in this graph follows axiom **T11** — full text in [Axiom-Timestamp], executable contract in [T0-Time], runtime guards in `src/tools/time_semantics.py`. The pattern in one sentence: every field's timezone semantics is encoded in its name (suffix-based), and any comparison must verify the two sides carry the same semantics before the operator runs.

The canonical fields the planner reads:

| Field | Semantics | Example |
|---|---|---|
| `*_at_utc` | UTC wall-clock instant, ISO-8601 with offset | `recorded_at_utc: "2026-04-19T06:00:00Z"` |
| `*_calendar_day_utc` | a 24-hour UTC calendar day | `crypto_calendar_day_utc: "2026-04-17"` |
| `session_date_market` + `market_tz` | the asset's market session day in its own market timezone (IANA) | `session_date_market: "2026-04-17"`, `market_tz: "America/New_York"` |
| `data_anchor.session_close_at_utc` | the UTC close instant of that session, sourced from the exchange calendar (DST-safe, early-close-aware) | `"2026-04-17T20:00:00Z"` |
| `data_freshness_class` | `pre_open` / `intraday` / `post_close` / `unknown` derived from `recorded_at_utc` vs `session_close_at_utc` | `"post_close"` |

The legacy field names (`report_date`, `generated_at`, `emitted_at`) remain readable as **aliases** during the deprecation window. The planner's `date_anchor` and `recency_within_days` contracts try the canonical T11 name first and fall back to the legacy name with a `legacy_alias` tag in the freshness reason. After the deprecation window the writers will stop emitting the legacy aliases and the fallbacks will be removed.

The `signal_packet` schema carries an explicit `data_anchor` block at the top level:

```json
{
  "data_anchor": {
    "session_date_market": "2026-04-17",
    "market_tz": "America/New_York",
    "session_close_at_utc": "2026-04-17T20:00:00Z",
    "data_freshness_class": "post_close",
    "derivation": "daily.ohlcv.date"
  }
}
```

The block is the canonical source-of-truth for downstream comparisons. The `derivation` field records which signal in the packet produced the anchor (`daily.ohlcv.date`, `recent_30m_window.session_dates[-1]`, `recent_30m_window.bars[-1]`, or `report_date_legacy` for macro packets where `daily` is intentionally empty); when the planner re-derives an anchor in memory for a packet that pre-dates the schema, the freshness reason is tagged `derived_in_memory`.

The sidecar schema version was bumped from `"v1"` to `"2.0"` on 2026-04-19 to mark the T11 cutover; sidecars below `"2.0"` are still readable but `tradectl plan --emit-sidecar` always rewrites at the current version. Two new top-level fields stamp the contract version on every sidecar emission: `time_semantics_contract_id` (`"T11"`) and `time_semantics_version` (an ISO-8601 timestamp with explicit offset, e.g. `"2026-04-19T06:00:00+00:00"`, validated by `_assert_iso8601_with_offset_minute`).

### 3.4 Edge types

Edges carry typed contracts so the router knows what "satisfied" means.

Defined edge types:

- `must_be_fresh(D)`: upstream node must be valid for the same `D` (or another stated date) under its own freshness contract
- `must_exist_unchanged_since(D)`: upstream node must exist and its content hash must match what was hashed when this downstream node was last produced; used for cross-date references such as "today's review reads yesterday's pm_action without rewriting it"
- `must_be_referenced_in_output`: upstream node must be cited or hash-recorded in this artifact's writer sidecar; used for audit and traceability
- `optional_overlay`: upstream node may inform output but is not required for validity

The default edge type is `must_be_fresh(D)` unless explicitly downgraded.

### 3.5 Builder

A builder is the concrete code that produces a node from its valid upstream nodes.

Builders are typed:

- `deterministic`: pure code, idempotent given upstream + parameters
- `ai_writer`: LLM-driven, non-deterministic prose; produces an artifact plus a writer sidecar that records inputs and parameters
- `composite`: a builder that internally invokes multiple sub-builders and returns one node

Each node has exactly one canonical builder. If two paths can produce the same canonical artifact, only one is allowed; the other is a bug.

Builders must:

- consume only the declared upstream nodes (no hidden inputs)
- write to the canonical path of the produced node
- emit or update a writer sidecar that records the consumed upstream node hashes and the producing builder version

Builders may be invoked manually (CLI), by the router as part of a plan, or by future automation. The graph does not care.

### 3.6 Owner skill

Each node names one owner skill. The owner skill:

- is the contract layer for the human-facing or PM-facing meaning of this node
- is the layer that defines `desired result`, `completion standard`, `writing rules`
- is the layer the agent enters when it must reason about whether this node was produced well, not merely whether the file exists

A skill may own multiple nodes (e.g., `research-current-market-reporter` owns `current-market.{intake,judgment,package,handoff,ds}.md`). One node has one owner skill.

A node without an owner skill is allowed only at L0 and L1 (raw data and deterministic derivatives). Any L2-L4 node without an owner skill is a graph error.

### 3.7 Logical-asof versus file mtime

`logical-asof` is the explicit task time used to interpret freshness. It is set by the router when a goal node is requested and propagates through the dependency closure.

`logical-asof` is the truth, not file mtime. A file produced at 09:00 ET for `report_date=D` may still be the valid node for asof `D`, even if that file's mtime is now several hours old.

This separation matters because:

- mtime drifts in irrelevant ways (someone touched the file)
- mtime cannot express "this judgment was correct as-of morning, but the afternoon move requires re-judgment"
- asof allows explicit invalidation: an upstream may be re-stamped with a new asof to force downstream rebuilds

For non-date-scoped nodes, asof is replaced by `source_state_hash`.

---

## 4. Layer Cake

The layers are not new; they reuse the operating-system view but make node placement explicit.

### 4.1 L0 — Raw data layers

Inputs from outside the repo, persisted under canonical paths.

Examples:

- `price_bars(symbol, interval)` in Postgres
- `positions_snapshot(date)` under `data/account/snapshots/`
- `mail_inbox` under research ingestion
- `macro_series(name)` under `data/macro/`

Freshness:

- typically `monotonic_at_least(today_session_anchor)` or `must_exist(today)`

Builders:

- `deterministic` only; usually CLI subcommands like `tradectl history update`, `positions update`, `tradectl macro fetch`, `agentmail check`

### 4.2 L1 — Deterministic derivatives

Code-only transformations of L0 into structured derivatives that downstream layers consume.

Examples:

- `signal_packets/<asset>.json` under `data/knowledge/asset_technicals/signal_packets/`
- `daily_update_status.json` under `data/dashboard/`
- `technical_index.json` under `data/knowledge/asset_technicals/`
- `coverage_index.json` for asset universes

Freshness:

- typically `must_be_fresh(D)` where D is the report date for the asset universe
- often expressed as a status registry flag (`blocking == false`) on `daily_update_status.json`

Builders:

- `deterministic`; `tradectl data update` and its internal sub-builders

### 4.3 L2 — AI interpretive

LLM-written interpretations of L1 that produce per-asset or per-theme structured prose.

Examples:

- `asset_technical_reports/*.md` under `data/knowledge/asset_technicals/reports/`
- `theme_thesis_notes/<theme_id>.md` under research memory
- `theme_update_drafts/<theme_id>.json`

Freshness:

- `date_anchor`: report_date == D
- `must_be_fresh(D)` on its declared L1 inputs

Builders:

- `ai_writer`; e.g., `tradectl technical draft-reports-ds`

### 4.4 L3 — Judgment objects

Pre-compressed judgment that locks mainline, market stage, basket, debate frame, and conditionality before the final PM-facing prose is generated.

Examples:

- `current-market.judgment.md`
- `single-stock.judgment.md(<ticker>)`
- `theme.report_owner_decision(<theme_id>)`
- `portfolio_decision.judgment.md`

Freshness:

- `date_anchor`: report_date == D
- `must_be_fresh(D)` on L2 inputs

Builders:

- `ai_writer` or `composite` (deterministic intake + ai_writer judgment pass)

### 4.5 L4 — PM-facing artifacts

The final visible artifacts that PMs read.

Examples:

- `current-market.ds.md` (daily recap)
- `single_stock_analysis/<ticker>.ds.md`
- `theme_reports/<theme_id>.ds.md`
- `portfolio_decision/pm_action.md(D)`
- `portfolio_decision/pm_action_review.md(D)`

Freshness:

- `date_anchor`: report_date == D
- `must_be_fresh(D)` on its declared L3 inputs
- in many cases, also `referenced_existence` on related L4 artifacts (e.g., a review references prior pm_action)

Builders:

- `ai_writer` through the writer gateway

---

## 5. Composite Task = Goal Node Set

A composite user task does not need a new skill. It is just a set of goal nodes.

Example, the recent failure-driving request:

- "落地 4/15 加仓建议为正式 daily recap" → goal node `pm_action.md(2026-04-15)` (L4)
- "写今天的 recap" → goal node `current-market.ds.md(2026-04-17)` (L4)
- "对照 4/15 看今天该如何调整" → goal node `pm_action_review.md(2026-04-17)` (L4)

The router does not need to invent a skill for "review loop". It accepts the three goal nodes, walks dependencies, deduplicates shared upstream work, and produces a runnable plan.

This is the central reason this substrate is being added: composite tasks are first-class. They were previously homeless and got improvised into "recap" markdowns that bypassed contracts.

---

## 6. Router Responsibilities Under This Substrate

`routing-task-mode-router` becomes thinner.

Its job is now strictly:

1. read user intent
2. map intent to one or more `goal nodes` from the artifact graph
3. resolve the dependency closure for those goals as-of the requested logical date
4. classify each upstream node as `valid` or `stale`, with the reason
5. produce a runnable plan that brings the closure to validity, in topological order
6. surface the plan to the user (or to the agent's plan-mode) for approval before any builder runs

`routing-task-mode-router` should not:

- decide writing structure
- decide judgment content
- choose which assets enter the basket (that is `research-current-market-reporter` judgment work, not routing)
- bypass freshness contracts even when a "shortcut" exists at the capability layer

When `routing-task-mode-router` cannot map intent to any goal node, it returns `unmapped_intent` with a candidate list of nearest existing nodes, not an improvised path.

The `routing-current-macro-priority-router` continues to exist as a thin midstream chooser inside macro-led mainlines. Under this substrate, it only decides which theme overlay node should attach to a goal node already chosen by `routing-task-mode-router`.

---

## 7. Boundaries Replace Hard Rules

Many existing `.cursor/rules/*.mdc` files are verbal hard rules of the form "do X before Y" or "do not do Z when W". Several of those should migrate into edge contracts.

Examples of conversions:

- "data update gate before PM artifact": `every L4 node has a must_be_fresh edge into the relevant L1 status registry`
- "package builder is canonical, do not handwrite": `every L4 node names the canonical builder; ad hoc Python that writes to the canonical path is a graph violation`
- "PM artifact must have a canonical path": `every L4 node has a canonical_path; new L4 files outside the canonical_path set are graph violations`
- "futures naming uses slash-root in baskets": stays a verbal rule, since it is about prose style not data dependency

Verbal rules remain useful for prose style, tone, and persona work. They should not be the primary enforcement mechanism for `freshness`, `path`, or `composition`.

---

## 8. Skill = Node Builder Binding

A skill file under `.cursor/skills/<name>/SKILL.md` should evolve to make these explicit:

- `owns_nodes`: the list of node ids this skill owns
- `consumes_nodes`: the list of node ids this skill reads as truth surface
- `produces_nodes`: the list of node ids this skill produces (subset of `owns_nodes`)
- `builder_kind`: one of `deterministic`, `ai_writer`, `composite`
- `desired_reader_state`: kept (effect-first, per existing rule)
- `completion_standard`: kept

Skills that previously read as end-to-end pipelines should re-anchor themselves as "I own this node and these are the upstream nodes I require." The existing prose about reader state, judgment quality, and writing standards remains valid; it now lives next to a machine-readable node binding.

A skill is not required to own any node. Some skills will own zero (e.g., `routing-task-mode-router` itself owns no artifact node; it produces ephemeral plans, not persisted artifacts). That is fine; "skill" remains the agent contract layer.

---

## 9. Minimum Viable Implementation

This substrate does not require an immediate engineering build-out. The MVP order is:

### 9.1 Phase 0 — Static graph definition

Land one file:

- `data/runtime/artifact_graph.yaml`

It lists the active L0..L4 graph-admitted nodes across the active mainlines. For each node:

- `id`
- `canonical_path`
- `layer`
- `report_date_scoped`: bool
- `depends_on`: list of `(node_id, edge_type)`
- `freshness_contract`: structured predicate
- `builder`: command or skill+entrypoint
- `owner_skill`: skill name or `deterministic`

Even without any tooling, the existence of this file enforces:

- new PM-facing artifacts must claim a node
- artifacts without a node are visible drift, not invisible
- agents reasoning about a task can read this file and answer "what is stale" without code

### 9.2 Phase 1 — Read-only plan tool (shipped)

- `tradectl plan <node_id> --date <YYYY-MM-DD> [--params k=v,...] [--json]`

Reads the yaml, walks the dependency closure, classifies each node as `FRESH / STALE / MISSING / UNKNOWN / SKIPPED`, prints a tree and a summary, and returns a non-zero exit code if any `STALE` or `MISSING` appears. Executes no builder. Implemented in `src/tools/artifact_graph.py`.

### 9.3 Phase 2 — Writer sidecar round-trip + edge contracts + executor (shipped, v0.1 scope)

- `tradectl plan <node_id> --date <D> --emit-sidecar auto` writes an `artifact_graph` section into `<canonical_path>.writer.json` recording direct upstream content hashes
- `tradectl plan <node_id> --date <D> --verify-sidecar auto` re-hashes the recorded upstream files and returns `FRESH / STALE / MISSING`
- composite/virtual nodes (e.g., `data_layer.fresh`) now roll up to a real `FRESH / STALE / UNKNOWN` from their non-overlay children instead of a fixed `UNKNOWN`
- `must_exist_unchanged_since` edges are verified through the downstream node's sidecar: `FRESH` only when the recorded upstream hash still matches the current file (see §3.3.1)
- every non-`FRESH` node in the planner's tree output is followed by a `fix: <command>` line pulled from the node's declared `builder.command`, so the next action is copy-pastable

With sidecars present and edge contracts active, both `source_state_hash` and `must_exist_unchanged_since` now return real `FRESH / STALE` instead of v0.1 placeholder `UNKNOWN`s. See §3.9 for the sidecar schema.

L0 source nodes are also no longer black boxes:

- `price_bars` runs a real Postgres probe via `PlatformStore`, resolves `asset_id` → `(symbol, asset_type, provider)` from `data/knowledge/asset_technicals/profiles/<asset_id>.json` (with fallback to `data/knowledge/asset_technicals/signal_packets/<asset_id>.json`), and compares `max(bar_start)::date` against the appropriate session anchor (XNYS for equity / ETF / etc. via `equity_last_completed_rth_date`, CMES for futures via `futures_last_completed_session_date`, calendar=`24_7` for crypto / FX / commodity proxies). The contract returns real `FRESH / STALE` per asset_id; only true gaps (Postgres unreachable, calendar library missing, asset_id not mapped) collapse to `UNKNOWN` with a precise reason
- `macro_indicators` runs a `series_recency_per_category` check against `data/macro/index.json`: each indicator series must satisfy `end >= D - lag_days_by_category[category]`, with a `default_lag_days` fallback for categories not in the table. Stale series are listed individually so the next action is obvious (e.g., `WALCL(cat=liquidity,end=2026-04-07,expected>=2026-04-16)`)
- `big_events_calendar` runs a `recency_within_days` check against `data/macro/calendar_watch/latest.json`'s `generated_at`, so a stale calendar window (e.g., planning 30 days after the calendar was fetched) is automatically caught

Executor (also shipped):

- `tradectl produce <node_id> --date <D> [--params ...]` walks the same dependency tree and either previews (default `--dry-run`) or executes (`--apply`) the canonical builders for every STALE / MISSING node (and any UNKNOWN node whose file exists but is missing its frontmatter / sidecar)
- only nodes whose YAML declares `builder.invoke` (a clean argv array; supports `{date}`, `{<param>}`, and the derived `{symbol}` placeholder) are auto-runnable; everything else surfaces as `[NEEDS-AGENT]` and `--apply` refuses to run partially when blockers exist (so the user cannot get a "data fresh, but report still hand-written" shortcut)
- `{symbol}` is resolved from `params.asset_id` via the same profile / signal-packet manifest the freshness probe consults, so cascades rooted at an `asset_id` parameter can reach broker-side fetchers (`tradectl history update --symbols <S>`) without the caller knowing the underlying ticker
- after each successful invocation, the executor emits a graph sidecar so downstream contracts immediately become verifiable (suppress with `--no-emit-sidecar`)
- the v0.1 invoke set now covers the **full per-asset hot path** end-to-end: `price_bars` → `tradectl history update --symbols {symbol}`, `signal_packet` → `tradectl technical refresh-packets --asset {asset_id} --as-of {date}`, `asset_technical_report` → `tradectl technical draft-reports-ds --asset {asset_id} --as-of {date}`. Combined with the data-layer invokes (`account.snapshot` → `tradectl positions update`, `daily_update_status` → `tradectl data update`, macro nodes → `tradectl macro daily`), `tradectl produce asset_technical_report --apply --params asset_id=<id> --date <D>` can rebuild a single asset's daily report from raw bars to AI-written markdown without any manual relay.

Still deferred to v0.2:

- expanded `builder.invoke` coverage on the L3 / L4 `ai_writer` and `composite` nodes (`current-market.ds`, `current-market.judgment`, `current-market.package`, `theme.report`, `single_stock_analysis.ds`, `portfolio.pm_action_review`); these still surface as `[NEEDS-AGENT]` until their writer wrappers gain a single-shot CLI form
- auto-emit of sidecars from inside `ai_writer` builders themselves (today the executor calls emit_sidecar after the build completes; agents producing artifacts outside `tradectl produce` still need to call `tradectl plan --emit-sidecar auto` manually)
- formal parameter resolvers (`observation_universe(D)`, `book_relevant_tickers(D)`, `theme_observation_assets(theme_id)`, `D_offset: variable`) so deep dependency walks on `portfolio.pm_action_review` and similar L4 goals stop hitting `unresolved_params:asset_id` mid-tree

### 9.4 Phase 3 — Skill rebinding (in progress)

Each owner skill gets a small `Node Bindings` section that declares `owns_nodes` and `consumes_nodes`. The verbal contract stays. Done for the six core production-chain skills (`research-current-market-reporter`, `operation-portfolio-decision`, `research-theme-report-owner`, `research-theme-knowledge-and-package-curator`, `research-single-stock-analysis`, `writer-asset-technical`). Remaining skills are mostly deterministic or routing-only and will be migrated only when they gain real node ownership.

### 9.5 Phase 4 — Rule consolidation

Hard rules that are now expressible as edge contracts can be removed or downgraded to "see artifact graph for the contract". Style rules stay. `42_artifact_graph_admission.mdc` is the current entry-point rule; it mandates running `tradectl plan` before producing any L4 node.

---

## 10. Open Issues

These are deliberately not resolved in v0.1. They will be revisited once the MVP yaml exists.

### 10.1 AI judgment freshness is not pure mtime

A judgment object can become "logically stale" mid-day even when the file is unchanged, because the market moved. Possible directions:

- allow explicit `invalidate <node_id>` actions that bump asof
- attach a `valid_until` predicate to L3 judgment nodes (e.g., "valid until next session boundary or until source-state hash on L1 changes")

### 10.2 Partial dependency satisfaction

Some downstream nodes only depend on a slice of an upstream universe (e.g., a single-stock note depends on one asset's L2 report, not the whole universe). The yaml needs a way to express "this dependency parameterizes by the artifact's identity field".

### 10.3 Cross-date references

`pm_action_review.md(D)` reads `pm_action.md(D-2)` without rewriting it. The `must_exist_unchanged_since` edge type covers this in principle. The implementation needs to record content hashes at production time so future reviews can check unchanged-ness.

### 10.4 Non-date-scoped registries

Indexes, registries, manifests, and schemas are not date-scoped. Their freshness is source-state-hash based. The graph should treat them as a separate node kind so the date-scoped logic does not pollute them.

### 10.5 Agent capability versus contract capability

Agents will continue to have lower-level capability surfaces (Postgres, Python, ad hoc tools). The substrate cannot prevent capability access; it can only define contract violations. The enforcement loop is:

- the agent reads the graph before acting on PM-facing work
- the agent declares the goal nodes
- the agent runs `tradectl plan` for every PM-facing goal node before invoking any builder
- the agent does not produce a node by any path other than the canonical builder
- if the agent uses an ad hoc path, the produced artifact is a graph violation and must be retracted

If `tradectl plan` is temporarily unavailable, the agent must explicitly declare the fallback state and record the reason in the handoff or sidecar rather than silently substituting an implicit mental check.

The substrate makes the violation visible. It does not auto-prevent it. This is acceptable for a PM-facing repo where the agent operator is also the owner.

### 10.6 Migration cost

Every existing skill needs a small node binding section. Every existing rule that encodes a freshness or path contract should be re-evaluated. The migration is incremental but real. Phase 0 (yaml) should not block on Phase 3-4.

### 10.7 Output-reference enforcement

`must_be_referenced_in_output` is an admitted edge type, but enforcement details remain open. Future runtime work should decide whether the writer sidecar, final markdown, or both must carry the explicit citation/hash proof.

---

## 11. Machine Audit Runtime Surfaces

```yaml
runtime_surface_ledger:
  - surface: registry
    projection: runtime_agnostic
    path_or_command: data/runtime/artifact_graph.yaml
    owner: designDoc/the_artifact_graph.md
    doc_claim: canonical registry of graph-admitted artifact nodes, builders, dependencies, and freshness predicates
    sync_obligation: update when PM-facing artifact paths, node ids, builder bindings, or freshness predicates change
    status: active
  - surface: command
    projection: runtime_agnostic
    path_or_command: ./.venv/bin/python -m src.cli.tradectl plan <node_id> --date <YYYY-MM-DD> [--params k=v,...] [--json] [--emit-sidecar auto] [--verify-sidecar auto]
    owner: src/tools/artifact_graph.py
    doc_claim: reads the graph, walks dependency closure, classifies freshness, and optionally writes/verifies sidecar graph hashes
    sync_obligation: update this doc, rule 42, CLI help, and focused smoke checks when planner flags or status semantics change
    status: active
  - surface: command
    projection: runtime_agnostic
    path_or_command: ./.venv/bin/python -m src.cli.tradectl produce <node_id> --date <YYYY-MM-DD> [--params k=v,...] [--apply] [--no-emit-sidecar]
    owner: src/tools/artifact_produce.py
    doc_claim: previews or executes declared builder.invoke steps for stale/missing graph dependencies
    sync_obligation: update this doc, graph yaml builder.invoke entries, CLI help, and smoke checks when executor behavior changes
    status: active
  - surface: generated_artifact
    projection: n/a
    path_or_command: <canonical_path>.writer.json
    owner: src/tools/artifact_graph.py
    doc_claim: records artifact_graph upstream node hashes, status_at_emit, reason_at_emit, and produced_for metadata
    sync_obligation: update sidecar schema consumers and planner verification when sidecar shape changes
    status: active
  - surface: rule
    projection: cursor
    path_or_command: .cursor/rules/42_artifact_graph_admission.mdc
    owner: designDoc/the_artifact_graph.md
    doc_claim: Cursor-side always-on rule requiring graph planning before L4 PM-facing artifact production
    sync_obligation: update when graph admission, UNKNOWN semantics, planner command shape, or sidecar obligations change
    status: active
  - surface: doc
    projection: n/a
    path_or_command: designDoc/temp/skill_routing_migration_to_artifact_graph.md
    owner: designDoc/the_artifact_graph.md
    doc_claim: temporary migration analysis for mapping current skills onto graph nodes
    sync_obligation: retire to historical archive or update status when migration completes
    status: temp_audit
verification_hooks:
  - ./.venv/bin/python -m src.cli.tradectl plan current-market.ds --date <YYYY-MM-DD> --json
  - ./.venv/bin/python -m src.cli.tradectl produce asset_technical_report --date <YYYY-MM-DD> --params asset_id=<asset_id>
  - manual sidecar round-trip: run plan with --emit-sidecar auto, then rerun plan with --verify-sidecar auto on the same node/date
```

## 12. Status

This document is currently `active_draft`.

It is the canonical substrate contract surface for the artifact graph and task network. The v0.1 planner, sidecar round-trip, and executor scope described in §9 are shipped where their runtime ledger rows are `status: active`; v0.2 items and §10 open issues remain draft. It does not replace [T0-Task-Intake]; it extends it with a machine-readable substrate.

For the current round, all design proposals about routing, skill responsibility migration, freshness contracts, or canonical artifact paths should reference this document.

Companion document:

- [Artifact-Graph-Migration] — the running migration analysis that maps current skills onto nodes, identifies gaps, and lists the migration phases to run

When the migration completes, the companion document will move to historical archive and this document will remain as the long-lived substrate definition.

## 13. References

- `[T0-Task-Intake]` [Task Intake Routing Contract](the_task_routing.md)
- `[T0-Time]` [Timestamp Semantic Contract](the_timestamp_semantic.md)
- `[Axiom-Timestamp]` [T11 Timestamp Semantics Axiom](../09_soul/axioms/t11_timestamp_semantics_explicit.md)
- `[T0-Runtime-Code]` [Runtime Code Admission And Audit Contract](the_tradecli_code_management.md)
- `[T0-Doc-Review]` [Design Doc Review Gate Contract](the_design_doc_management.md)
- `[T1-Material-Catalog]` [Material Catalog Overview](material_00_overview.md)
- `[Artifact-Graph-Migration]` [Artifact Graph Skill Migration Analysis](temp/skill_routing_migration_to_artifact_graph.md)
