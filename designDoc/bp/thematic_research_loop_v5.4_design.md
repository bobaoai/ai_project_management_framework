# Thematic Research Loop Infrastructure · v5.4 Design Doc

> Status: Blueprint (canonical position-taking design doc of V5.4)
> Source PDF: [`Product-Definition-v5.4_1.pdf`](Product-Definition-v5.4_1.pdf)
> Reading note (chapter-by-chapter digest): [`Product-Definition-v5.4_digest.md`](Product-Definition-v5.4_digest.md)
> Forks MVP bridge to trading_platform: [`forks_mvp_relation_to_trading_platform.md`](forks_mvp_relation_to_trading_platform.md)
> Audience: future implementer / architect of a V5.4-style research loop product
> Voice: this doc is written from inside V5.4 ("we choose X because Y"), not from outside ("the PDF says X")

---

## 1. One-line definition

V5.4 is a **thematic research loop infrastructure** that turns the PM workflow `Theme → Thesis → Basket → Monitor → Scenarios & Evolve` into a 5-stage closed loop, with a named agent on every stage, sharing one object model and one Point-in-Time data stack. It serves institutional thematic teams (Tiger Cubs, multi-strat thematic sleeves, thematic ETF issuers, RIA / family office thematic desks).

The product is the **loop**, not any single primitive. Anything that breaks the loop's closure (Theme without Thesis, Thesis without Monitor, Monitor without Evolve) is not a smaller V5.4. It is a different product.

---

## 2. Goals and non-goals

### 2.1 Goals

- G1. Compress every stage of the thematic research workflow with **agent-driven pre-processing**, so PMs spend their time on judgment, not on copy-paste between Slack / PDF / Excel.
- G2. Make the **Thesis stage agent assistance** the densest assistance moment: turn brain-shaped theses into structured, falsifiable, machine-monitorable objects.
- G3. Close the loop end-to-end: `Monitor → Scenarios → Basket adjustment → Thesis vN+1`. No competitor does the full closure.
- G4. Keep PM authority inviolate: agents propose, score, and draft; PMs sign, finalize, and trigger any action.
- G5. Be PIT-correct from day one so that backtest, validation, and live monitor never disagree on "what did the world look like on date D".
- G6. Be compliance-native: SEC Rule 204-2, FINRA Rule 2210, RIA fiduciary duty are satisfied by the object model itself, not by a side compliance vault.

### 2.2 Non-goals (each one is deliberate)

- N1. **No thesis library**. We do not let PMs "publish / search theses". The loop is the product; theses are objects produced inside the loop.
- N2. **No public publishing platform**. Tenants default to no public path; we do not compete with Substack / Seeking Alpha.
- N3. **No order routing**. Output stops at `basket + adjustment recommendation`.
- N4. **No portfolio management system**. We do not compete with Aladdin / Charles River. Portfolio-level compliance / risk only at the bare minimum.
- N5. **No general quant backtest framework**. Backtest is an internal monitor / validation tool, never the product (V4 lesson).
- N6. **No retail product**. Decision archive (MiroFish) rejects this branch.
- N7. **No general LLM chat surface**. Chat is one of several UIs, never the product narrative.
- N8. **No automatic market prediction**. No system-generated probability numbers (see §7 for full rationale).

### 2.3 What V5.4 explicitly is *not* a sequel of

V5.3 (the rejected "overshoot" version) tried to make Thesis the only protagonist and used framings like *GitHub for thesis library*, *Substack for PMs*, *viral growth loop*, *public gallery*. **All of that is removed by design.** The Thesis stage is the densest agent stage but it is not the product; the loop is.

---

## 3. System overview

### 3.1 The loop

```
        ┌──────► (vN+1 feedback) ──────┐
        │                              │
        ▼                              │
   ┌────────┐  ┌────────┐  ┌────────┐  │
   │ Theme  │─►│ Thesis │─►│ Basket │  │
   └────────┘  └────────┘  └────────┘  │
                                  │    │
                                  ▼    │
                            ┌─────────┐│
                            │ Monitor ││
                            │ q + ql  ││
                            └─────────┘│
                                  │    │
                                  ▼    │
                            ┌──────────────┐
                            │ Scenarios &  │
                            │ Evolve       │──┘
                            └──────────────┘
```

Each stage holds the same four slots:

1. **Business purpose** (why the stage exists)
2. **PM contract** (what the PM must decide that the agent cannot decide for them)
3. **Agent contract** (concrete verbs the agent performs)
4. **Object & state machine** (what is produced and what states it can occupy)

### 3.2 Object model in one paragraph

Five top-level objects: `Theme`, `Thesis`, `Basket`, `MonitorEvent`, `Scenario`. Cardinalities: `Theme 1—N Thesis`, `Thesis 1—N Basket`, `Basket 1—N MonitorEvent`, `Thesis 1—N MonitorEvent`, `MonitorEvent 0—N Scenario`, `Scenario 0—1 BasketAdjustment`, `Thesis N—1 Thesis` via `parent_thesis_id` (lineage chain across evolve / fork / resurrect). All states cross-validated by §6.

### 3.3 Agent topology

Six agents, one per loop hand-off, each with its own `system_prompt` and tool list, all sharing the same object model:

| Agent | Loop stage | Mode |
|---|---|---|
| Discovery | §4.1 Theme | Background daemon + on-demand |
| Formulation | §4.2 Thesis | Multi-turn conversational with PM |
| Construction | §4.3 Basket | On-demand long task (factor / optimizer / PIT) |
| Monitor | §4.4 Monitor | 7×24 background daemon |
| Scenario | §4.5 Scenarios | On-demand + event-triggered |
| Evolve | §4.5 Evolve | Event-triggered, low-frequency |

**Key topology rule**: agents do not share prompt context. They share the object model. Any agent can fetch latest `Theme / Thesis / Basket / MonitorEvent / Scenario` through MCP tools at call time, instead of dragging full state through every prompt.

---

## 4. Loop stages (detailed contracts)

### 4.1 Theme stage

#### 4.1.1 Purpose

Convert a fuzzy intuition ("re-industrialization · USA", "reasoning models compress SaaS margins") into a structured Theme object with declared boundary, time window, and an initial 100–500 stock universe.

#### 4.1.2 PM contract

The PM must answer four things the agent cannot:

- Business boundary (hyperscaler vs IaaS/PaaS/SaaS? US onshore vs global re-shoring?)
- Time window (12 / 24 / 36 months)
- Universe scope at the 100–500 level (precision-to-20 is the Basket stage)
- "Why now" + "Why not already priced in"

#### 4.1.3 Agent contract (Discovery agent)

Six concrete verbs:

1. **Cluster the daily news / transcript / filing / analyst-report stream** by embedding co-occurrence; surface 3–8 candidate Themes per morning.
2. **Run a counter-evidence checklist** on any PM-drafted Theme: similar Themes in the last 10 years, their out/under-performance vs SPY, time-to-realize, key differences this time.
3. **Recall a candidate universe** from three channels (factor exposure, sector classification, text similarity), pre-scored by *theme purity*.
4. **Reject a fuzzy Theme** outright when the boundary is undefined; offer 2–3 sharper splits as alternatives.
5. **Overlap-check** against existing Themes inside the same tenant; surface duplicates so two PMs do not silently both stand up "data center power consumption".
6. **(Opt-in)** Anonymous similarity check against extended-network Themes, only if tenant admin enables it.

#### 4.1.4 Object & state

`Theme` schema (selected fields):

```
id, tenant_id, name, boundary {geo, industry, time_window},
universe_ids[],
base_state ∈ {draft, active, archived},
pm_manual_state ∈ {null, peaking, decaying},   -- v5.4: PM-only
pm_manual_state_reason, pm_manual_state_at,
created_by, created_at, updated_at
```

`current_state` is **derived**, not stored:

```sql
CASE
  WHEN base_state = 'archived'                                THEN 'archived'
  WHEN pm_manual_state IN ('peaking','decaying')              THEN pm_manual_state
  WHEN EXISTS (active Thesis under this Theme)                THEN 'monitoring'
  WHEN base_state = 'active'                                  THEN 'active'
  ELSE 'draft'
END
```

This deliberately prevents Theme/Thesis state drift inside the database.

#### 4.1.5 Hand-off to Thesis

PM clicks "立项" → `Theme.base_state = active`, `universe_ids` frozen as v0. The PM can now create Thesis objects underneath.

---

### 4.2 Thesis stage (the agent-densest stage; not the product)

#### 4.2.1 Purpose

Turn one directional intuition inside a Theme into a falsifiable directional bet with explicit causal chain, time window, falsification conditions, and named catalysts. Output is a `Thesis` object whose `body.sub_assertions[]` can each be independently monitored and falsified.

#### 4.2.2 Why agent assistance is critical here

A PM's thesis usually exists as `verbal + a long Slack message + an email + a few charts`. That state is unmonitorable. Until it is structured text:

- It cannot be backtested
- It cannot be tied to monitor sensors
- It cannot be challenged by teammates
- It cannot be retrospectively read 12 months later

The Thesis-stage agent's only job is to take it from brain-shaped to operable.

#### 4.2.3 Agent contract: three core actions

The Formulation agent does three things while the PM is writing, not after.

##### Action 1 · Coaching (push hidden assumptions out)

The agent does not wait for a finished draft. It pops questions during writing:

> PM types "AI is bullish for cloud computing"
>
> Agent (each line is a question the PM can answer or skip):
>   1. "Bullish" = price outperforms SPY by what %? Or revenue growth >20%? Or gross margin expansion?
>   2. "AI" = end-user demand for AI apps? Or enterprise internal AI workload? Training or inference?
>   3. "Cloud computing" = hyperscaler (AWS/Azure/GCP), or IaaS/PaaS/SaaS in full?
>   4. Time window: 12 / 24 / 36 months?
>   5. Strongest counterfactual — what happens that would make you say "I was wrong"?
>
> PM answers, the agent stitches the answers back into the draft body.

##### Action 2 · Fine-tune (mark ambiguity, offer rewrites)

The agent highlights ambiguous spans and offers 2–3 rewrites in parallel.

> PM types "GLP-1 will rerate the entire pharma sector"
>
> Agent flags 3 ambiguities (rerate direction? scope? time horizon?) and offers candidates A/B/C, each a sharper version. PM picks one or rewrites a fourth.

##### Action 3 · Decompose (cut high-level claims into falsifiable sub-assertions)

For genuinely high-level claims, the agent refuses direct ingestion and offers a decomposition:

> PM types "AI will change retail"
>
> Agent returns 4 sub-assertions:
> - Demand-side: "AI personalization lifts top-platform GMV/MAU 15% in 18m" (verify via AMZN/MELI/PDD GMV/MAU)
> - Supply-chain: "AI inventory optimization lifts WMT/TGT/COST inventory turnover 0.5 turns in 24m" (verify via 10-Qs)
> - Labor: "AI customer service + warehouse automation cuts retail labor cost / revenue 150bp in 36m" (verify via BLS + filings)
> - New entrants: "AI-native retail startups capture >2% of US online retail in 24m" (verify via e-commerce trackers)
>
> The PM keeps 1–4 as the Thesis body. Each sub-assertion has its own falsification condition + verification data source + confidence weight.

#### 4.2.4 Other agent verbs

- **Counter-evidence list**: 3–5 historical near-precedents that would falsify the thesis
- **Catalyst mining**: pull from earnings calendar / FDA PDUFA / policy calendar; attach to the thesis timeline
- **PIT backtest at v0**: as soon as the thesis is finalized at v0, an automatic PIT backtest runs over a prototype basket built on pre-finalize data; this is V5.4's *Validation* — collapsed into the tail of the Thesis stage instead of being a standalone workflow.

#### 4.2.5 Object & state

`Thesis` schema (selected):

```
id, theme_id, version, author_id,
body.sub_assertions[]: { text, falsification_condition,
                         verification_data_source, confidence },
catalysts[]: { event, expected_date, impact_direction },
falsification_conditions_global[],
time_window, confidence,
state ∈ {draft, under_review, active, stress_tested,
         evolving, invalidated, archived},
parent_thesis_id, evolved_from_version,
resurrected_from_invalidated bool,         -- v5.4
resurrection_rationale text (>=100 chars)  -- v5.4
signed_hash sha256, finalized_at
```

State machine:

```
draft → under_review → active → stress_tested
           │              │            │
           │              ▼            │
           │           evolving ◄──────┘
           │              │
           ▼              ▼
         archived     active(vN+1)
                          │
                ┌─────────┼─────────┐
                ▼         ▼         ▼
          invalidated  archived  (back to monitor)
                │
                │ (PM resurrects + rationale ≥ 100 chars)
                ▼
            evolving → active(vN+1)
```

Transition rules:

- `draft → under_review`: PM marks the draft ready; triggers full agent fine-tune + decomposition + PIT backtest.
- `under_review → active`: PM signs v0; can now attach a Basket.
- `active → stress_tested`: at least one Scenarios round completed.
- `active → evolving`: monitor feedback triggers a rewrite; produces vN+1.
- `active → invalidated`: at least **two** core sub-assertions explicitly falsified by monitor.
- `invalidated → evolving` (**v5.4 resurrection path**): PM-explicit, requires `resurrection_rationale ≥ 100 chars`. This is intentionally a friction wall, both for compliance (SEC 204-2 decision rationale) and to prevent flippant un-invalidation. See §6.4 for the full rationale.
- `active → archived`: time_window expired and PM does not renew.

#### 4.2.6 What the Thesis stage is **not**

It is not a "thesis library" surface. It is not a "publish thesis to teammates" surface. It is the step in the loop that converts brain-shape into operable shape, and every downstream stage (Basket, Monitor, Scenarios, Evolve) consumes the resulting Thesis object.

---

### 4.3 Basket stage

#### 4.3.1 Purpose

Convert one Thesis into one tradeable basket: pick names, set weights, apply constraints, choose benchmark.

#### 4.3.2 PM contract

PM judgments the agent cannot make:

- Concentration (10 names vs 40 names)
- Weighting philosophy (equal vs cap-weight vs theme-purity vs risk-parity vs constrained-optimizer)
- Benchmark neutrality
- Cash retention

#### 4.3.3 Agent contract (Construction agent)

1. **Map sub-assertions to candidates**: for each sub-assertion, recall names with exposure to that specific assertion (not generic Theme).
2. **Score purity**: text-similarity + historical factor loading + revenue exposure → "this name's earnings sensitivity to *this thesis*".
3. **Always offer 3–5 weighting variants** (Equal / Cap / Purity / Risk Parity / Optimizer-under-constraint), each with PIT backtest preview.
4. **Apply constraints**: max single name, max sector, min liquidity (ADV days), beta cap, tracking error cap.
5. **Decompose risk**: factor exposure (growth / value / momentum / quality / low-vol + sector beta) so the PM sees what else the basket is exposed to besides the Thesis.
6. **Estimate cost**: implementation cost based on ADV + expected turnover.
7. **Suggest rebalances** post-launch: when monitor triggers, recommend `rebal yes/no, magnitude X`.

#### 4.3.4 Object & state

```
Basket {
  id, version,
  thesis_id, thesis_version,        -- IMMUTABLE pair
  holdings[]: { ticker, weight, rationale },
  weighting_method ∈ {equal, cap, purity, risk_parity, optimizer},
  constraints { max_single_name, max_sector,
                min_liquidity_days, tracking_error_cap, ... },
  benchmark, PIT_backtest_ref,
  state ∈ {draft, proposed, active, rebalancing, retired}
}
```

**Hard rule**: `(thesis_id, thesis_version)` is immutable across the basket's life. To switch underlying thesis version, open a new basket version. This is what lets us audit "the basket was built against thesis vN, here is exactly that vN".

---

### 4.4 Monitor stage (two legs in parallel)

> Monitor is the only stage with a 7×24 daemon agent. Theme / Thesis / Basket agents fire on PM call. Monitor fires continuously. This means the data pipeline (`L0` in §8) directly determines product credibility — freshness, latency, throughput are Monitor's hard constraints, not nice-to-haves.

#### 4.4.1 Purpose

Track every live Basket continuously through two legs in parallel:

- **Quant leg**: the basket's own statistical properties (drift, attribution, benchmark, risk exposure)
- **Qualitative leg**: the narrative and event surface the underlying Thesis depends on (narrative velocity, catalyst hits, competitor moves, sub-assertion verification)

#### 4.4.2 PM contract (the fork)

When the basket starts to lag, the PM has to decide *which* thing changed:

- The **basket** drifted (price-driven weight drift, factor exposure breach) → **rebalance**
- The **thesis** itself was undermined by a new fact (sub-assertion falsified, catalyst missed, narrative collapsed) → **Thesis evolve**

Confusing these two is the most expensive PM mistake. Monitor's two-leg design is built so that the PM can always tell them apart.

#### 4.4.3 Agent contract: quant leg (Monitor agent)

1. Holdings drift vs basket v0
2. Attribution breakdown (market beta / sector beta / theme purity / alpha)
3. Benchmark diff (excess return + tracking error)
4. Risk monitoring (factor exposure delta, vol, drawdown, rolling Sharpe)
5. Rebalance signal (drift > threshold or factor exposure > constraint → "consider rebal")
6. PIT backtest rolling continuation (live performance vs the original PIT backtest curve)
7. Portfolio-level context (this basket's contribution to the PM's *total* exposure across all active baskets — not for portfolio management, for crowding awareness)

#### 4.4.4 Agent contract: qualitative leg

1. **Narrative velocity**: weekly delta of mention frequency in news + transcripts + filings, plus sentiment.
2. **Catalyst hit detection**: when an attached catalyst's expected_date arrives, the agent grabs related earnings / news / filings and labels `hit / miss / partial`.
3. **News event alerts**: M&A / regulation / major product launches with high relevance to the thesis.
4. **Competitor / counter-flow**: 13F / insider trading / ETF inflow-outflow signals on basket constituents.
5. **Sub-assertion verification**: every sub-assertion that has a `verification_data_source` is re-evaluated when fresh data lands (e.g. "hyperscaler capex YoY > 30%" recomputed every quarter).

#### 4.4.5 Object & state

```
MonitorEvent {
  id, affected_thesis_id, affected_basket_id (optional),
  event_type ∈ {drift, attribution_shift, catalyst_hit,
                catalyst_miss, narrative_spike, news_shock,
                exposure_breach, sub_assertion_verified,
                sub_assertion_invalidated, ...},
  severity ∈ {info, warn, critical},
  evidence_refs[],
  suggested_next_action ∈ {rebalance, spawn_scenarios,
                           evolve_thesis, dismiss},
  state ∈ {raised, acknowledged, action_taken,
           dismissed, archived}
}
```

`MonitorEvent` is **append-only**. Deletion is forbidden. This is the compliance backbone of §9.

---

### 4.5 Scenarios & Evolve stage (loop closure; the V5.4 moat)

#### 4.5.1 Purpose

Two things happen here in parallel; both are required for the loop to close:

- **Scenarios derivation**: rather than wait for shocks to actually arrive, proactively generate 3–5 candidate paths the next 3–6 months might take, and decide *now* how the basket should be adjusted under each.
- **Thesis evolve**: monitor feedback + scenario insights are absorbed back into the Thesis, producing vN+1. Without this, every Thesis stays at v0 and the product collapses to a one-shot research tool.

#### 4.5.2 Architectural rule: Scenario is not a top-level primitive

`Scenario.parent_thesis_id` always points back to a Thesis. A Scenario cannot exist without a parent Thesis. This is deliberate:

- It prevents Scenario from becoming a parallel narrative track that drifts away from the active Thesis.
- It enforces the loop closure: every Scenario's `basket_adjustment_plan` and `trigger_signals` are evaluated against *the same* Thesis whose evolution it feeds.
- It is the structural reason V5 is a loop product, not a "scenario planner" tool.

#### 4.5.3 Agent contract: Scenarios derivation (Scenario agent)

1. From `Thesis (active version) + last N weeks' MonitorEvents`, generate 3–5 scenarios — typically `base / bull / bear / tail`, but the agent may generate asymmetric counts when the Thesis structure warrants.
2. For each scenario, produce a fixed three-piece artifact: `narrative + trigger_signals[] + basket_adjustment_plan`. (See §7 for why probability is **not** part of this artifact.)
3. Map the `basket_adjustment_plan` to concrete basket deltas (which names to add, trim, hedge; whether to change beta).
4. Extract `trigger_signals[]` as observable data points with thresholds and direction (e.g. "AWS quarterly capex YoY breaks 35%").
5. Continuously evaluate triggers as new MonitorEvents arrive; mark `triggered` when threshold is crossed.

#### 4.5.4 Agent contract: Thesis evolve (Evolve agent)

1. Detect trigger conditions: ≥N sub-assertions falsified, or a critical catalyst miss, or a sub-assertion's time horizon expired.
2. Draft vN+1: changes to sub-assertions (delete / modify / add), updated catalysts, recomputed confidence.
3. Highlight version diff between vN and vN+1.
4. Propose basket re-association: "the basket currently attached to vN — keep, retire, or open a new version against vN+1?" The default is **keep current attachment**; the PM must explicitly approve switching.

#### 4.5.5 Object & state

```
Scenario {
  id, parent_thesis_id, parent_thesis_version,
  narrative,                                  -- MVP core deliverable
  trigger_signals[]:                          -- MVP core deliverable
    { observable_data, threshold, direction },
  basket_adjustment_plan:                     -- MVP core deliverable
    { holdings_delta[], weight_changes, rationale },
  pm_personal_score,                          -- nullable; PM judgment, not derived
  pm_score_rationale,
  market_implied_probability,                 -- Phase 1; risk-neutral; system-only
  market_implied_snapshot_time,
  market_implied_instruments[],
  state ∈ {proposed, active, triggered,
           obsolete, archived}
}
```

Loop closure expressed as a sentence:

> `Thesis vN → Monitor → Scenarios → basket adjustment → execution observation → Monitor → Thesis evolve → Thesis vN+1`.

This is the closure that no competitor product owns end-to-end. Each individual segment exists in isolated tools (a narrative-velocity dashboard, a factor backtest, a scenario planner). What V5 ships is the integration: four stages on one object model, with one set of agent orchestration rules.

---

## 5. Object model summary

### 5.1 Cardinalities

| Parent | Child | Cardinality | Notes |
|---|---|---|---|
| Theme | Thesis | 1—N | one Theme can hold multiple Thesis branches / versions |
| Thesis | Basket | 1—N | a Thesis can have several baskets (different constraints) |
| Basket | MonitorEvent | 1—N | the basket emits drift / exposure events |
| Thesis | MonitorEvent | 1—N | the thesis emits catalyst-hit / sub-assertion events |
| MonitorEvent | Scenario | 0—N | severe events spawn scenarios |
| Scenario | BasketAdjustment | 0—1 | each scenario carries one adjustment plan |
| Thesis | Thesis | N—1 | `parent_thesis_id` lineage chain |

### 5.2 Schema evolution invariants

1. `(Basket.thesis_id, Basket.thesis_version)` is immutable for that basket's lifetime. Switch the underlying thesis version → open a new basket version.
2. A Thesis once `active` is never mutated in place; any change opens vN+1.
3. `MonitorEvent` is append-only. No deletion under any path.
4. All top-level objects carry a soft-delete `deleted_at`. Physical deletion only on legal request.
5. `Thesis.resurrected_from_invalidated`, once `true`, cannot be flipped back to `false`.
6. `Scenario.market_implied_probability` is system-computed only; PMs cannot edit it.

---

## 6. State machines and cross-state invariants

### 6.1 Two state lines

```
Theme:  draft → active → monitoring → peaking → decaying → archived
Thesis: draft → under_review → active → stress_tested → evolving → active(vN+1)
                              ↘ invalidated → (resurrect) → evolving → active(vN+1)
                              ↘ archived
```

### 6.2 Cross-legality matrix

| Thesis → ↓ Theme | draft | under_review | active | stress_tested | evolving | invalid / archived |
|---|---|---|---|---|---|---|
| **draft** | OK | illegal | illegal | illegal | illegal | illegal |
| **active** | OK | OK | OK | OK | OK | OK |
| **monitoring** | OK | OK | OK | OK | OK | OK |
| **peaking** | OK | OK | OK | OK | OK | OK |
| **decaying** | warn | warn | OK | OK | OK | OK |
| **archived** | illegal | illegal | illegal | illegal | illegal | OK |

### 6.3 Four invariants

- **I1 — Theme precedes Thesis.** A Thesis cannot transition to `under_review` while its parent Theme is `draft`. Implementation auto-promotes Theme to `active` (with PM confirm) when the first Thesis crosses `under_review`.
- **I2 — Theme protects all live Thesis.** A Theme can only `→ archived` when every Thesis under it is `invalidated` or `archived`. Theme archive is a cascade operation; it cannot be triggered standalone.
- **I3 — Decaying Theme warns, does not block.** A decaying Theme still allows existing Thesis to run to time_window expiry; new Thesis drafted under decaying Theme gets a strong warning (it usually means the PM mis-clicked).
- **I4 — Theme `peaking / decaying` is PM-manual only in MVP.** No automatic threshold-driven promotion. Auto-suggestion is deferred to Phase 1 and surfaces as PM-confirmable suggestions only.

### 6.4 Why invalidated is not terminal (v5.4 resurrection path)

The earlier draft made `invalidated` terminal. We override that, and define `invalidated → evolving → active(vN+1)` as a valid path. Reasons:

- **Real-world phenomenon**: a Thesis can be falsified short-term and revived long-term ("AI bullish for cloud" was falsified by 2024 Q3 macro chop and re-validated by 2025 Q2). Forcing a brand-new Thesis breaks lineage.
- **Audit clarity is preserved**: lineage stays intact via `parent_thesis_id + evolved_from_version + resurrected_from_invalidated`. The audit trail can answer "you previously called this dead — what changed your mind?".
- **Friction wall against flippancy**: resurrection requires `resurrection_rationale ≥ 100 chars`. This is both an SEC 204-2 decision rationale and a behavioral filter — PMs must articulate the reason in writing before the system permits the path.

### 6.5 Cascade rules summary

Theme → Thesis cascades:

| Theme transition | Effect on child Thesis |
|---|---|
| `draft → active` | unblocks Thesis state transitions |
| `→ monitoring` (derived) | indicator only, no forced cascade |
| `→ peaking` (PM-manual) | child Thesis carries a "Theme peaking" badge |
| `→ decaying` (PM-manual) | child Thesis gets review reminder; new draft Thesis gets strong warning |
| `archive` request | refused unless every child Thesis is invalidated / archived |

Thesis → Theme cascades:

| Thesis transition | Effect on parent Theme |
|---|---|
| First Thesis → `under_review` (parent Theme draft) | auto-promote Theme `base_state` draft → active (PM-confirm) |
| First Thesis → `active` | parent Theme `current_state` flips to monitoring |
| Last active Thesis exits | parent Theme `current_state` returns to active (PM `peaking/decaying` retained) |
| `invalidated → evolving` (resurrection) | parent unchanged; audit log records the resurrection event |
| `evolving → active(vN+1)` | parent unchanged; audit log records the version finalization |

Basket dependency on Thesis state:

| Basket op | Thesis state required |
|---|---|
| Create | `active / stress_tested / evolving` (never under draft / under_review / invalidated) |
| Thesis invalidated | Basket must be retired or re-associated within N=30 days |
| Thesis archived | All child Baskets must already be retired |
| Thesis resurrection | Old Basket stays retired; new vN+1 may get a new Basket — **never auto-reactivate the old one** |

MonitorEvent dependency on Thesis state:

- `active / stress_tested / evolving` → MonitorEvent generated normally
- `invalidated` → MonitorEvent **continues** to be generated (compliance: keep recording until archived), but **does not** trigger Scenario derivation or Thesis evolve
- `archived` → MonitorEvent stops; history retained
- Resurrection → Monitor sensors re-bind to vN+1; old vN events archived to lineage but do not pollute vN+1

---

## 7. Probability design (the v5.4 reframe)

### 7.1 The reframe

The earlier draft asked "should Bayesian update on Scenario probability be agent-driven or PM-driven?". This is the wrong question. The product value of a Scenario lives in its *qualitative structure* (`narrative + trigger_signals + basket_adjustment_plan`), not in a probability number. A well-written Scenario *is* a complete playbook; the PM does not need a "23%" sticker to act on it.

### 7.2 Hard product position (immutable across phases)

> **MVP does not produce system-generated probability numbers.** The Scenario's core deliverable is qualitative. PMs may optionally fill `pm_personal_score` as a personal judgment record. Phase 1 surfaces market-implied probability from options data as a **reference badge** (explicitly labeled risk-neutral). Historical-analogue probability is deferred to Phase 2 and may never ship.
>
> **Product stance**: V5.4 does not predict markets. V5.4 makes the PM's judgment process structurable, traceable, and replayable.

### 7.3 Why MVP refuses auto-probability

| Reason | Detail |
|---|---|
| LLM-generated probability is narrative-derived, not data-derived | Customers will ask "where does this 30% come from?" and there is no defensible answer — this is precisely the MiroFish path that was already rejected |
| Small-sample historical Bayesian is worse than no prior | A 200-thesis archive accumulated over 2 years gives confidently wrong priors; thematic thesis branching combinatorics outrun any plausible sample size |
| Institutional buyers are skeptical of "AI predicts markets" | Differentiating on "we structure judgment, not predict markets" is more institutional-friendly than competing on probability accuracy |
| Cleaner compliance posture | If the system never emits probability, the system never owns probability accuracy. PM-entered scores stay PM-attributable under SEC 204-2 |

### 7.4 Why market-implied is the right Phase 1, not historical

| Dimension | Market-implied (Phase 1) | Historical analogues (Phase 2 maybe) |
|---|---|---|
| Ground truth | live market money | small-sample stats |
| Buyer language | natural to institutional buyers | requires methodology explanation |
| Demo defensibility | "options price this scenario at 23%" | "23 historically similar theses..." |
| Hallucination risk | zero | medium — embedding similarity ≠ situational similarity |
| Onboarding cost | options data feed (~$50k/year) | 500+ labeled theses (5+ years) |
| Coverage | liquid underliers only | theoretically all theses |
| Compliance posture | clean — non-system, market-sourced | medium — system prior counts as prediction |

### 7.5 Three-phase implementation path

**Phase 0 (MVP, day 0–120)**: pure qualitative + optional PM score. Agent owns `narrative + triggers + adjustment plan`. Probability fields stay null unless the PM types into `pm_personal_score`. UI shows the optional score as "PM personal judgment, not system-derived".

**Phase 1 (after options data ingest)**: market-implied as a sidebar reference. For each Scenario, the agent identifies an option combination whose payoff matches the scenario shape (bull → OTM call basket; bear → OTM put basket; tail → deep-OTM or VIX call; base → forward price). Risk-neutral probability is read off the implied vol surface and shown as `market-implied: 23% (risk-neutral)`. The Scenario's primary probability field remains `pm_personal_score`. When liquidity is insufficient, the field is explicitly tagged `insufficient liquidity` — never guessed.

**Phase 2 (Year 2+, possibly never)**: historical analogues as a tertiary reference badge. Only enabled when the labeled-thesis library exceeds ~500 with multi-regime coverage. Even when shown, never replaces `pm_personal_score` or `market_implied_probability` as primary fields. Multiple reference lines coexist as parallel badges (PM / Market / Historical).

### 7.6 Three hard rules that survive every phase

- **R1 — Every probability number must be attributable.** UI clicks on any probability number must open a "why this number" drawer with provenance.
- **R2 — PM always overrides.** Agent priors and market-implied numbers are reference; the PM's number is final.
- **R3 — LLM never emits probability numbers.** LLM owns narrative, sub-assertion mapping, retrieval. All numbers come from deterministic compute (market data or PM input).

---

## 8. Agent architecture and orchestration

### 8.1 Six agents, one object model

See §3.3 for the topology table. Key orchestration rule: **agents do not share prompt context**, agents do share the object model. Any agent can fetch latest `Theme / Thesis / Basket / MonitorEvent / Scenario` through MCP tools at call time. This avoids dragging full state through every prompt and lets each agent's `system_prompt` stay specialized.

### 8.2 Specialization principle

Each agent has its own `system_prompt` and tool list because the action shapes differ enough that one prompt cannot serve all:

- Formulation agent is a **coaching** agent (asks questions, evaluates the PM's draft)
- Construction agent is an **execution** agent (runs parameterized backtest variants)
- Monitor agent is a **detection** agent (stream-processing event generator)
- Scenario / Evolve agents are **planning + diff** agents (multi-path generation; structured rewrite)

### 8.3 Tech stack

- **LLM**: Claude (Anthropic API) as the primary reasoning engine. Other models as fallback for specific subtasks (embeddings, ranking).
- **Tool interface**: MCP. Typical MCP servers: market-data, news, factor-model, PIT-backtest, portfolio-analytics.
- **Tool implementation**: in-house for `PIT backtest`, `factor model`, `monitor stream processor`. Wrappers around vendors (Bloomberg / FactSet / S&P CapIQ / Quiver / AlphaSense) for the rest.
- **Persistence**: object store on Postgres + S3. Timeseries (monitor events, price panel) on Postgres timeseries extension or ClickHouse.
- **Tenancy**: market data shared pool (vendor-licensed); thesis content / PM operation log / basket holdings / scenarios / comments under schema-per-tenant or row-level isolation with KMS tenant-keyed.

### 8.4 The Evolve sequence (loop-closure mechanism)

```
1. Monitor agent continuously writes MonitorEvents to the object store.
2. Trigger condition met (e.g. ≥N sub-assertions falsified) → Monitor notifies Evolve.
3. Evolve agent fetches Thesis vN + related MonitorEvents + Scenarios.
4. Evolve agent drafts vN+1 candidate:
     - flag sub-assertions to delete / modify / add
     - update catalysts
     - recompute confidence
5. Evolve pushes "Thesis update suggested" notification to PM (with diff).
6. PM enters Formulation session (reuses §4.2 agent) to refine vN+1 collaboratively.
7. PM finalizes vN+1; state → active.
8. Monitor sensors re-bind to vN+1.
     - Old basket re-association dialog fires.
     - Old vN MonitorEvents stay in thesis lineage.
```

Critical design: **Evolve does not produce the final version itself.** It produces a candidate diff with explanation. Final adoption is handed back to Formulation (the §4.2 agent) for PM-collaborative finalization. This is what makes the loop technically close: no agent unilaterally finalizes, and PMs always re-enter through the same authoring surface they already know.

### 8.5 Responsibility boundary (cross-cutting)

- Agents may **propose, score, draft** independently.
- Agents must **never finalize, sign, trigger orders** without explicit PM confirmation.
- Agents must **never modify an active Thesis or Basket in place**. Every change is a new version + a PM merge request.

This boundary is grounded in two reasons: AI cannot substitute for fiduciary decision-making (compliance), and institutional buyers do not trust "AI silently changed my position" (trust).

### 8.6 v5.4-specific hard rule for Scenario agent

The Scenario agent (and any other agent) is **not allowed** to write into:

- `Scenario.pm_personal_score` (PM-only field)
- `Scenario.market_implied_probability` (Phase 1 options engine only, never LLM)

LLM is permitted to write only the three qualitative fields (`narrative / trigger_signals / basket_adjustment_plan`). This is the agent-layer enforcement of §7.6 R3.

---

## 9. Data stack and Point-in-Time discipline

### 9.1 Why PIT is a hard product constraint

Backtest, validation, and monitor all depend on time-consistent data — "what did the world look like on 2023-03-15 when this Theme was first identified?". Without PIT correctness, any backtest leaks future information and any historical analogy becomes indefensible. Institutional buyers will ask exactly this in bake-off ("how do you handle restatements? split-adjustments? ETF weight changes?"). V5 must answer with an audit trail.

### 9.2 Three data layers

- **L0a — Market & Fundamental.** Market data (OHLC + volume + dividend / split / restatement adjustments) and fundamental data (financials + forward consensus). Vendor-sourced; landed as PIT-safe — every restatement carries an effective date and never overwrites history.
- **L0b — Factor & Classification.** Factor panel computed from L0a (growth / value / momentum / quality / low-vol). One value per factor per stock per day, stamped with its as-of date. Classification: GICS + custom thematic taxonomy.
- **L0c — Universe & Theme snapshots.** Daily PIT universe snapshots and a theme-to-stock taxonomy snapshot. Answers questions of the form "on 2023-03-15, who was in the Russell 3000 and what factor loadings did each have, and which thematic taxonomy nodes did each belong to?".

### 9.3 The shared-snapshot rule (the design that makes PIT cheap)

Backtest and live monitor consume the **same** universe-as-of-date API. The only difference is the `as_of` date passed in:

```
                ┌─ Universe-as-of-Date API ─┐
                │                            │
                ▼                            ▼
         ┌────────────────┐           ┌────────────────┐
         │ Backtest       │           │ Live Monitor   │
         │ as_of=hist     │           │ as_of=today    │
         └───────┬────────┘           └───────┬────────┘
                 │                            │
                 └────────► PIT snapshot ◄────┘
                              store
```

This eliminates the most common "backtest looked great, live underperformed" failure mode: **training and production are the same source**.

### 9.4 Data freshness SLAs

| Data | SLA |
|---|---|
| Market quotes | < 15 min intraday; EOD landed same evening |
| News / transcripts / filings | < 5 min trigger to monitor sensors |
| Factor panel | T+1 EOD refresh |
| Universe snapshots | daily |

These are bake-off baselines, not aspirational targets.

### 9.5 Multi-tenancy

- Market and text raw data: shared pool (vendor licenses permit it).
- Thesis content, PM operation log, basket holdings, scenarios, comments: strict tenant isolation (schema-per-tenant or row-level + KMS tenant-keyed).
- Audit log: tenant-partitioned; clients can independently extract for legal discovery.

---

## 10. Compliance surface

### 10.1 Regulatory baseline

| Regulation | V5.4 satisfaction path |
|---|---|
| SEC Rule 204-2 (RIA records, ≥5 yr) | Thesis version history + audit trail + monitor event log natively satisfy; no external compliance vault needed |
| FINRA Rule 2210 (broker-dealer comm supervision) | Comment audit + version lineage cover supervision basics |
| SEC Rule 10b-5 / Reg FD (non-public information) | Tenant default = no public path; opening it requires explicit disclaimer flow |
| SEC Marketing Rule 206(4)-1 | Product never emits "guarantee" / "best" / "must-buy" language; backtests carry standard disclaimers |

### 10.2 How the object model satisfies 204-2 natively

- `Thesis.finalized_at` writes `body` snapshot to append-only storage with SHA-256 hash.
- Any edit becomes a new vN+1 draft; vN is never overwritten.
- `MonitorEvent` is append-only.
- All operations log to a tenant-partitioned audit log with **7-year retention** (5-year SEC + buffer for FINRA).
- One-click export of full thesis lineage + monitor history as compliance evidence.

### 10.3 Resurrection audit (v5.4-specific)

Resurrection is a high-sensitivity compliance event. Required record:

- `who`: PM ID who triggered resurrection
- `when`: trigger timestamp
- `what`: from `invalidated vN` into `evolving`, producing vN+1
- `why`: PM-written rationale (≥100 chars, mandatory)
- `evidence`: optional — PM may attach related MonitorEvents or external news links

In compliance report exports, resurrection events are **highlighted** because SEC 204-2 explicitly cares about decision rationale.

### 10.4 Posture: compliance is a tie-breaker, not a wedge

This is a V4 lesson: the differentiation that wins deals is `loop + agent + closure`. Compliance is what gets the procurement department to release the contract. Doing compliance to "industry standard" is required; selling on compliance is wrong.

### 10.5 SOC 2 path

- Y1: SOC 2 Type II (institutional bake-off blocker)
- Y2: ISO 27001 (international expansion)
- Day 1: GDPR compliance for EU tenants (PII minimization, tenant-level data deletion)
- Y1 H1: first penetration test

---

## 11. Team workflow surface (hygiene only)

This section is intentionally short.

| Capability | Granularity | Default |
|---|---|---|
| Thesis readable inside tenant | object | on |
| Thesis fork (parent_thesis_id link) | operation | on, tenant admin can disable |
| Thesis cite (explicit reference) | operation | on |
| @-mention + Slack/Teams notify | operation | on, user can disable |
| Inline comment on a sub-assertion | operation | on |
| IC review checklist (lightweight) | flow | optional |
| Extended visibility (cross-tenant whitelist) | object | tenant-admin opt-in |
| Public publishing | object | tenant-admin opt-in; **product never gives it a top-level entry** |

### 11.1 Why this section is short

The earlier (rejected) v5.3 turned collaboration into 80 pages of independent workflows: `Thesis Formulation workflow`, `Thesis Collaboration workflow`, `Visibility model and tenant admin control`. This was overshoot. Collaboration verbs are hygiene that any team product must have; they do not constitute a separate product narrative. They get one page total.

### 11.2 Conservative posture on extended / public

- Default: tenant admin disallows extended visibility.
- Even when tenant admin opens public, the UI does not promote it. **This is not Substack for PMs.**
- A compliance review flow is mandatory before any public-channel publication.

---

## 12. MVP scope and the Forks bridge

### 12.1 The MVP rule

> **MVP must cover every stage of the loop.** Stage-skipping is not a smaller MVP, it is a different product. A buyer in bake-off who sees Theme + Basket but no Monitor + Scenarios prototype will not believe the closure claim.

### 12.2 P0 per stage

| Stage | P0 scope |
|---|---|
| Theme | PM-typed + agent counter-evidence checklist; universe = GICS + 3 factors |
| Thesis | All 3 agent actions (coaching / fine-tune / decompose); 3 sub-assertion patterns; manual catalyst attach; one prototype basket PIT backtest |
| Basket | 3 weighting variants (equal / cap / purity); 5 standard constraints; PIT backtest + factor exposure |
| Monitor | Quant leg in full; qualitative leg = narrative velocity + catalyst hit; alert center + Slack integration |
| Scenarios | Agent generates 3 scenarios (narrative + triggers + adjustment); no auto probability; pm_personal_score optional; Evolve supports manual version-up + resurrection |

P0 acceptance: every stage end-to-end walkable, agent has at least 2 verb-level actions per stage, and the PM perceives "agent help" rather than "chatbot ornament".

### 12.3 Recommended timeline (option A: 120 days, full loop)

```
Day 0–30   object model + L0 data backbone + Theme/Thesis/Basket P0 frontend
Day 30–60  Monitor P0 (quant leg first) + first usable Formulation agent
Day 60–90  Monitor qualitative leg + Scenarios & Evolve P0
Day 90–120 internal dogfood (Citrini) + ≥1 external design partner live
```

Team: 2 FE + 3 BE + 1 quant + 1 PM (doubling as product owner).

### 12.4 Disallowed cuts (architectural guardrails)

- ❌ "Theme + Basket first; Thesis / Monitor / Scenarios later" — not an MVP
- ❌ "Monitor as EOD dashboard, live alert later" — live alert is the credibility anchor
- ❌ "Users hand-build their own scenarios" — then the product is no longer agent-driven loop
- ❌ "Evolve is a v2 feature" — without Evolve the loop does not close; defensibility evaporates
- ❌ "Add an auto-probability algorithm to MVP" — explicitly prohibited by §7

### 12.5 Forks: a non-institutional MVP variant

For non-institutional clients (fintwit / aspiring buyside / semi-pro / students), V5.4 ships a separate MVP product called Forks. Forks deliberately covers only `Scenarios + Monitor + Evolve` (the three stages that matter most for that audience), and defers `Theme + Thesis-agent-three-actions + Basket + PIT stack` to months 9–24.

This is **not an exception to the §12.1 rule**. The §12.1 rule is "MVP must cover the buyer's full workflow loop". For institutional Tiger Cubs the workflow is the full 5 stages; for fintwit the workflow is only Scenarios + Monitor. The rule maps to "buyer workflow", not to "the V5.4 canonical 5 stages".

The Forks → V5.4 canonical 24-month evolution path:

| Phase | Months | Adds | Buyer | V5.4 sections activated |
|---|---|---|---|---|
| Forks MVP | 0–3 | Scenarios + Monitor + Evolve | fintwit / semi-pro | §4.4 / §4.5 |
| Forks v1.x | 3–9 | Trigger automation + paid data feeds | + institutional PM personal users | §7 Phase 1 (market-implied) |
| + Basket | 9–15 | PIT backtest + basket construction | family office / RIA / small hedge fund | §4.3 |
| V5.4 Canonical | 15–24 | Theme + Thesis-agent-3 + multi-PM collab + compliance | Tiger Cub / multi-strat / theme ETF issuer | §4.1 / §4.2 / §10 |

Forks-specific design is in [`forks_mvp_relation_to_trading_platform.md`](forks_mvp_relation_to_trading_platform.md) (the trading_platform-side bridge) and in the standalone Forks Product Spec.

---

## 13. Cross-cutting trade-offs

### 13.1 No auto-probability (§7) trade-off

Lose: the demo flair of "AI told me this is 73% likely".
Gain: defensibility, compliance clarity, institutional trust, and immunity to the most common "AI predicts markets" backlash. Net positive for institutional buyers; net negative for retail demo. Aligned with §2.2 N6 (no retail product).

### 13.2 Agent never modifies active objects (§8.5) trade-off

Lose: some workflow steps that could be one-click become two-click (PM must merge a draft).
Gain: complete fiduciary responsibility chain; complete audit trail; institutional buyer trust. Required for the SEC 204-2 posture in §10.

### 13.3 PIT shared between backtest and live (§9.3) trade-off

Lose: more upfront engineering investment (the as-of-date snapshot store).
Gain: zero "backtest looked great, live underperformed" failures. Required for any defensible historical-analogy or backtest claim.

### 13.4 Scenario tied to parent Thesis (§4.5.2) trade-off

Lose: cannot ship Scenario as a standalone planner product.
Gain: loop closure stays mechanically enforced. The decision is upstream of every other architectural choice.

### 13.5 Compliance-as-tie-breaker not wedge (§10.4) trade-off

Lose: a marketing angle some competitors will lean into ("we are the most compliant AI product").
Gain: marketing message stays focused on the real moat (the loop), and compliance investment is right-sized — not gold-plated.

---

## 14. Migration from v5.3-concept

V5.4 is a strict superset of v5.3-concept's structure with three deliberate additions and one schema-breaking change.

### 14.1 New chapters

- **§6 cross-state matrix + 4 invariants** — v5.3-concept defined Theme states and Thesis states separately and never specified legal cross-products. V5.4 closes this gap so impossible combinations cannot enter the database.
- **§6.5 cascade rules** — bidirectional. Theme `archive` requires all child Theses already invalid/archived; first Thesis to `under_review` auto-promotes parent Theme to active; etc.
- **§7 probability design (3-phase)** — v5.3-concept listed this as "open question". V5.4 closes it with a definite stance and a phased path.

### 14.2 Two open questions resolved

- **Thesis invalidated handling**: locked as **resurrectable** via the explicit-rationale path (§6.4). v5.3-concept had this as terminal; V5.4 overrides.
- **Theme peaking / decaying threshold**: locked as **PM-manual only in MVP**. Auto-thresholding deferred to Phase 1 as PM-confirmable suggestions.

### 14.3 Schema-breaking change (one)

- `Scenario.probability` (single field) is **deleted** and replaced by `Scenario.pm_personal_score` + `Scenario.market_implied_probability` (two explicitly source-tagged fields). Any caller that read or wrote `Scenario.probability` must migrate.

### 14.4 What is *not* changed (preserved verbatim)

The loop's 5-stage structure, the Thesis stage's 3 agent actions, Monitor's quant + qualitative two-leg design, the PIT 3-layer data stack, the compliance chapter, the MVP discipline, and the explicit posture of "collaboration is hygiene, not a selling point" — all preserved from v5.3-concept without modification.

---

## 15. Open questions

V5.4 explicitly leaves five questions open. They do not block the MVP architecturally, but each must be answered before the corresponding capability ships.

| # | Question | Must answer by |
|---|---|---|
| 1 | Monitor qualitative-leg data source: build scrapers (~$50k/yr) or buy AlphaSense / RavenPack / Prattle ($500k+/yr)? | Day 30 of MVP build |
| 2 | Cross-tenant extended visibility IP model (explicit cite required? non-cite fork allowed?) | Before extended-visibility ships (P1) |
| 3 | Monitor stage subscription model and pricing (per basket / per seat / per compute unit?) | Before first commercial contract |
| 4 | Quantitative threshold for `active → evolving` (≥2 sub-assertions falsified vs confidence drop >20% vs PM-only) | 2 weeks before MVP launch (it is a tunable parameter) |
| 5 | Will the deliberately conservative extended/public posture cost us "thought leadership" PM acquisitions? | Before GA (does not block MVP) |

---

## 16. Glossary

- **Theme** — a top-level investable trend with declared boundary, time window, and 100–500 stock candidate universe.
- **Thesis** — a falsifiable directional bet inside a Theme, decomposed into sub-assertions each carrying a `falsification_condition` and `verification_data_source`.
- **Basket** — a tradeable instantiation of a Thesis: holdings, weights, constraints, benchmark.
- **MonitorEvent** — an append-only event emitted by the Monitor agent against a Basket or a Thesis (e.g. drift, catalyst hit, sub-assertion invalidated).
- **Scenario** — a future-path branch of an active Thesis, carrying narrative + trigger signals + basket adjustment plan; cannot exist without a parent Thesis.
- **Sub-assertion** — one clause of a Thesis body, individually falsifiable, individually monitorable, independently weighted into the Thesis confidence.
- **PIT (Point-in-Time)** — data discipline guaranteeing that a query "what was the world on date D" returns only data known to be true on or before D, with restatements never overwriting history.
- **Loop closure** — the cycle `Thesis vN → Monitor → Scenarios → Basket adjustment → Monitor → Thesis evolve → Thesis vN+1`. The defining product property of V5.4.

---

## 17. Companion docs

- [`Product-Definition-v5.4_1.pdf`](Product-Definition-v5.4_1.pdf) — original PDF (69 pp).
- [`Product-Definition-v5.4_digest.md`](Product-Definition-v5.4_digest.md) — chapter-by-chapter reading note with §13 mapping V5.4 concepts to trading_platform.
- [`forks_mvp_relation_to_trading_platform.md`](forks_mvp_relation_to_trading_platform.md) — Forks-MVP-side bridge between V5.4 §10 and the trading_platform repo (Trigger state machine, Scenario-as-first-class-object, sub-assertion schema upgrade, etc).

— End of V5.4 Design Doc —
