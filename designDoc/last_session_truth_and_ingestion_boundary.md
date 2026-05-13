# Last-Session Truth And Ingestion Boundary

**Version 0.2 — 2026-04-05**

**Status:** normative for architecture and future implementation. Existing code may still violate this document until the implementation plan below is executed.

---

## 1. Problem

Wall-clock time is a bad universal `as_of` when the book spans:

- instruments with different session calendars (U.S. equity vs CME-style futures),
- nearly-continuous futures sessions vs discrete equity cash closes,
- macro prints with publication lags.

If a single calendar date (for example `2026-04-02`) is reused as the truth horizon for **all** assets, Sunday-night runs will silently mis-state futures freshness or equity freshness.

The system needs a **hard boundary**:

- **Ingestion** answers: what was captured, from whom, when, under what provider clock.
- **Daily report / theme / thesis read layers** answer: what is the **latest completed trading-session truth** per instrument or per asset-class rule set, and **when was this artifact generated** for audit.

---

## 2. Definitions

### 2.1 Ingestion layer

**Ingestion** is connector- and store-facing work: fetch, normalize, persist bars/quotes/prints, record ingest status, append to Postgres or file archives.

Properties:

- Ingestion is **not** defined by “today’s daily report date”.
- Ingestion timestamps (`ingested_at`, `provider_timestamp`, `bar_end`, etc.) are **operational**, not the same as “the session the PM should read as final”.
- Persisted ingestion/provider/bar timestamps MUST remain precise **UTC instants**. Do not pre-normalize the data layer into ET/PT-only clock values.

### 2.2 Read / report layers (Daily Report, Theme, Thesis)

These layers **consume** stored truth and produce PM-facing or writer-facing artifacts.

Normative rule:

- They **do not** choose truth by “what time is it now” on the wall clock.
- They choose truth by **last completed trading session** per **session policy** attached to each symbol or asset class (see §4).

### 2.3 Raw UTC instant (data-layer clock)

Every durable market-data object should preserve its raw time anchor as a precise **UTC instant**.

Examples:

- `provider_timestamp`
- `bar_start`
- `bar_end`
- `quote_time`
- `ingested_at`
- `timestamp_utc`

This layer answers:

- when the provider says the observation belongs in machine time
- when the platform persisted or saw it

It does **not** answer which completed trading session the PM should treat as final.

### 2.4 `generated_at` (artifact audit clock)

Every PM-facing or writer-facing artifact that depends on market data MUST record:

- **`generated_at`**: wall-clock timestamp when the artifact was produced (precise UTC with explicit `Z` or offset).

This answers reproducibility: “when did we run the pipeline,” not “what session we priced.”

### 2.5 `data_horizon` / `last_session` / session semantic (semantic truth clock)

Separately, the artifact MUST make the **semantic** horizon legible, for example:

- **`last_session_end`** or **`session_as_of`**: end boundary of the last **completed** session used for that instrument or section.
- For mixed packages, prefer **per-asset rows** over one global date in the header only.

This layer is a **derived market meaning** built from raw UTC timestamps, exchange/session calendars, and asset-class policy.

Naming in implementations may vary (`session_as_of`, `last_session_end`, `session_date_utc`) but the **meaning** MUST align with **last completed session under policy**, not ingestion time and not a single forced calendar date for all asset classes.

### 2.6 Report / render labels (human-facing wording layer)

Human-facing labels may still use:

- `report_date`
- `run label`
- ET/PT/local session wording
- phrases like “post-close”, “盘后”, or “上一常规收盘日”

But these are **render labels**, not the raw data-layer truth.

Normative rule:

- render labels may summarize
- render labels may localize
- render labels may not replace raw UTC timestamps
- render labels may not replace per-asset `session_as_of`

---

## 3. Canonical rules (normative)

1. **Data-layer instants stay in UTC.**  
   All persisted ingestion/provider/bar timestamps should remain precise UTC instants. ET/PT/local wording belongs to downstream render surfaces, not the canonical data layer.

2. **Ingestion is independent of Daily Report.**  
   Running or not running `data update` / connector poll does not redefine what “last equity session” means. Ingestion brings data forward; read layers decide eligible bars under session policy.

3. **Daily Report, Theme, and Thesis consumers take “latest through last session.”**  
   For each instrument, include all stored bars/prints **through** the end of its **last completed** session per policy. Do not drop newer futures data because equity has not opened.

4. **No single global calendar `as_of` for mixed books.**  
   A package may display a **run label** date for operator convenience, but the **technical truth** inside must not pretend SPY and `/ES` share the same `report_date` when their last completed sessions differ.

5. **`generated_at` is mandatory on generated artifacts.**  
   Markdown frontmatter, JSON manifests, and ingestion artifact rows should all support audit: when generated vs what session was read.

6. **Session policy is index-first.**  
   Session calendar and “what counts as complete” should come from structured config (symbol metadata, asset class, exchange calendar), not ad hoc prompts.

7. **Downstream writers see explicit horizons.**  
   Writer prompts and packages must carry enough structured fields that the model does not infer the wrong session.

---

## 4. Per asset-class session policy (default intent)

Defaults below are the **target contract**. Exact calendars must be implemented via a single policy table or config, not scattered `if` branches in each tool.

| Asset class | Last completed session intent | Notes |
|-------------|------------------------------|--------|
| U.S. listed equity / equity ETF | Last **regular cash** session close | No pre-market / post-market as “final” unless policy explicitly upgrades |
| CME-style futures (e.g. `/ES`, `/NQ`, crypto futures roots) | Last **completed** session per exchange **session definition** for that root | Sunday evening can advance futures **session** while equity cash is still prior close |
| FX / macro index proxies | Policy per series: print date vs market close | Spot FX like `JPYUSD=X` may follow New York `17:00` roll; DXY-like public ICE proxies may follow the provider's ET trading day; macro series may use **observation_date** from source |
| Crypto spot tickers (if any) | 24h or provider-defined daily bar close | Must match bar construction in Postgres |

**Example (user scenario):**  
Sunday night, U.S. time: futures may already reflect the **new week’s** session progress per CME rules; U.S. equity ETFs should still read through **prior Friday’s** regular close until Monday RTH completes.

---

## 5. Artifact contract (minimum fields)

### 5.1 Per-asset technical signal packet / report

Minimum:

- `generated_at`
- raw UTC time such as `daily.ohlcv.timestamp_utc` or `last_bar_timestamp_utc`
- `session_as_of` or `last_bar_session_end` (instrument-relative semantic field)
- `asset_class` or link to session policy id
- Existing `report_date` field, if retained, MUST be documented as a **label field only**:
  - it may summarize the asset's current session label
  - it is not the raw UTC timestamp
  - it is not a substitute for explicit session fields

### 5.2 Market observation intake / package / judgment

Minimum:

- `generated_at` for the assembled artifact
- `run_report_date` only as a UTC orchestration label, not as universal market truth
- A **table or bullet block** of key underliers with **per-row** `last_session` / `session_as_of` (not one date only)
- If a package references exact price state, it should preserve or point back to raw UTC timestamps rather than only date labels
- `Run Context` should not imply all rows share the same session unless true

### 5.3 Theme / thesis drafts

Minimum:

- `generated_at`
- Explicit statement of which **evidence windows** apply (mail as_of, snapshot dates, technical last_session rows)

### 5.4 Ingestion artifact rows (Postgres / service)

Continue to store:

- provider time, ingest time, raw payload bounds, all in precise UTC when persisted  
Ingestion **does not** replace `session_as_of` on PM artifacts; it supports reconstruction.

---

## 6. Relationship to `daily_update_status`

`data/dashboard/daily_update_status.json` remains an **operator gate** for “are we allowed to run the daily refresh pipeline today?”

It MUST NOT be confused with §2.5:

- **Gate:** blocking / stale / ok for workflow
- **Semantic horizon:** last completed session per instrument for read outputs

The dashboard may still use a **business date** for operator messaging; read-layer artifacts must still carry **per-instrument** session truth where mixed calendars exist.

See also: [`modules/daily_data_update_dashboard.md`](modules/daily_data_update_dashboard.md).

---

## 7. Anti-patterns (forbidden)

- Forcing one `--as-of YYYY-MM-DD` for the entire technical universe when futures and equity last sessions diverge.
- Using wall-clock “today” as the equity `report_date` while futures bars already include a newer session.
- Persisting ET/PT-localized wall-clock values in place of canonical UTC timestamps.
- Hiding futures freshness inside prose without structured `last_session` fields.
- Letting the writer infer session boundaries from incomplete package headers.

---

## 8. AI-facing instruction contract (models are not humans)

Humans already know: “Sunday night, futures can move but my stock screen is still Friday’s close.” Models **default to collapsing** everything onto one calendar day, one “report date,” or “today,” unless the **task prompt and package** make the distinction **machine-obvious**. This section is the **copy-paste contract** for prompts, skills, and package builders.

### 8.1 Mental model the model must load (state explicitly in system or task prompt)

Put this near the top of writer/judgment instructions (paraphrase allowed; meaning not optional):

- There are **three time layers**:
  - **raw UTC timestamp**: exact machine-time instant on the underlying data object, such as `timestamp_utc`, `bar_start`, or `provider_timestamp`.
  - **`generated_at`**: when this artifact was produced (audit clock).
  - **`session_as_of` / last completed session**: what market truth is “final” **for that symbol or asset class**, per policy — **not** the same for all rows in a mixed book.
- **Daily Report may be generated on a weekend or off-hours.** That only affects `generated_at`. It does **not** mean all underliers share one equity session.
- Raw UTC timestamps and `session_as_of` are not interchangeable. One is a machine-time instant; the other is a derived market-semantic horizon.
- **Do not infer** that because the document title says “daily” or includes one date, every asset is priced through that same session.

### 8.2 What the orchestration layer MUST put in the package (so the model does not guess)

Minimum structured block in every Daily Report / market-observation **writer or judgment** package (markdown table or JSON the model must read first):

| Field | Purpose |
|-------|---------|
| `generated_at` | Audit: when we ran |
| optional raw UTC fields such as `timestamp_utc`, `bar_start`, or `last_bar_timestamp_utc` | Exact machine-time anchors behind the package |
| `report_profile` | e.g. `mixed_session_weekend` \| `equity_rth_only` \| `replay_backfill` |
| `rows[]` with `asset_id`, `asset_class`, `session_as_of`, `session_policy_id` (or plain-language policy name) | Per-row semantic horizon |

Rule: if `rows[]` is missing, the writer prompt MUST say “do not write prices or session claims; request upstream package fix” (fail closed).

### 8.3 Task-prompt block (paste into writer / judgment user prompt)

Use verbatim or with filled placeholders:

```text
Truth rules (non-negotiable):
- Raw UTC timestamps are exact machine-time facts. Keep them distinct from session labels and from prose render dates.
- Treat each asset row’s session_as_of as the only authoritative “through when” for that asset’s technical or price claims.
- generated_at is only when this note was written, not the market close for any asset.
- Do not unify SPY, QQQ, and /ES under one implicit session date unless the package explicitly states they share the same session_as_of.
- If session_as_of differs across rows, say so early in plain language (e.g. 期货已反映至…，美股现货仍截至上一常规收盘日…).
- Never replace missing session_as_of with “today” or the title date.

Weekend / off-hours Daily Report:
- You may still write a coherent “daily” narrative, but you must label it as a mixed-session snapshot when rows disagree.
- Prefer one short “读者应先知道” paragraph before the mainline that states the split horizons.
```

### 8.4 Forbidden model behaviors (list in prompt; use for eval)

- Inferring “the market closed today” for U.S. equities on Saturday/Sunday.
- Writing “截至今日收盘” for all assets when only some have updated.
- Using a single `YYYY-MM-DD` in the title as the de facto horizon for futures and equities without per-row confirmation.
- Explaining away calendar mismatch in vague prose (“整体而言”) without naming which asset class is stale vs fresh.

### 8.5 Self-check the model must run before finalizing (short checklist in prompt)

Add to “before finalizing” in writer instructions:

- Did I state `generated_at` meaning vs `session_as_of` meaning for at least one representative row per **asset class** present?
- Did I avoid replacing raw UTC timestamps with a looser date label when the package already gave me the exact time anchor?
- Did I avoid any sentence that implies one close for the whole book when rows differ?
- If futures and equity sessions diverge, did I put that fact **above** the mainline, not only in a footnote?

### 8.6 Control-plane vs task-plane (boundary hygiene)

- **Package / builder** owns: `rows[]`, `report_profile`, `generated_at`, policy ids.
- **Writer prompt** owns: how to turn those rows into PM prose, forbidden collapses, self-check.
- Do not rely on the writer knowing repo internals (“Schwab”, “Postgres”, “ingestion”) unless needed for a factual claim already in the package.

### 8.7 Why this is not redundant with “be accurate”

Models compress. “Be accurate” does not specify **which** date dimension. This contract names **two dimensions** and forbids **one** common compression path (single calendar day for all assets). That is the gap between human intuition and model failure mode.

### 8.8 Repo-wide time-field checklist

Use this checklist whenever a new market-data field, package field, skill rule, or prompt line is introduced:

- Is this field a **raw UTC instant**, a **derived session-semantic field**, or a **render label**?
- If it is raw time truth, is it still stored as a precise UTC instant instead of ET/PT-localized text?
- If it is a session field, is it clearly marked as derived from policy rather than presented as the raw timestamp?
- If a prompt or skill uses `today`, `latest`, `post-close`, or `report_date`, does the upstream package already provide the exact UTC/session block that justifies that wording?
- If a mixed-session package lacks per-asset session rows, does the downstream writer fail closed instead of guessing?

---

## 9. Implementation plan (for approval before coding)

Phased so each step has a verifiable outcome.

### Phase A — Policy and schema sketch

- Add a single **session policy registry** (config JSON or Postgres table): `symbol` or `asset_class` → calendar / session close rule.
- Document field names in `signal_packet` schema and frontmatter (this file is source of truth for meaning).
- Lock the time-field split:
  - raw UTC instant fields
  - derived session-semantic fields
  - render-label fields

**Exit:** schema doc + example rows for SPY vs `/ES`.

### Phase B — Technical runtime and signal packets

- `asset_technical_runtime` / `build_asset_technical_reports`: preserve raw UTC time fields, resolve **per asset** `last_completed_session` from bars + policy, and set `generated_at` on write.
- Stop using one global `as_of` date for all assets in the default daily path; CLI may keep `as_of` only for **replay** or **explicit backfill**, not for “current run.”

**Exit:** two assets on a synthetic Sunday show different `session_as_of` in JSON; `generated_at` present.

### Phase C — Market observation pipeline

- `build_market_observation_package` / intake: `Run Context` lists **per-spine asset** last session; judgment intake carries structured rows for DS.
- Align `market_date` resolution with §3 (no `max(report_date)` across asset classes if that mixes incompatible semantics).

**Exit:** intake markdown shows per-row session; judgment prompt unchanged except consuming clearer fields.

### Phase D — Theme / thesis builders

- Package builders attach `generated_at` and evidence window; theme technical injections use per-asset session fields from index.

**Exit:** one theme package shows technical excerpts with matching session metadata.

### E — Dashboard and operator docs

- Update [`modules/daily_data_update_dashboard.md`](modules/daily_data_update_dashboard.md) and [`modules/asset_technical_signal_pipeline.md`](modules/asset_technical_signal_pipeline.md) to reference this doc and distinguish gate vs semantic horizon.

**Exit:** no contradictory “single report_date” language without the §3 caveat.

---

## 10. Related documents

- [`price_data_architecture.md`](price_data_architecture.md) — bar and `as_of` object semantics
- [`modules/asset_technical_signal_pipeline.md`](modules/asset_technical_signal_pipeline.md) — technical refresh and status gate
- [`modules/daily_data_update_dashboard.md`](modules/daily_data_update_dashboard.md) — operator freshness surface
- [`knowledge_base_and_memory_system.md`](knowledge_base_and_memory_system.md) — ingestion artifact discipline
- [`analysis_platform_and_pm_workspace.md`](analysis_platform_and_pm_workspace.md) — PM workspace boundaries

---

## 11. Remaining decisions

- Whether macro / multi-source packages use a **dominant asset class** spine date for titles while keeping per-row session truth in body.
- Source of truth for **holiday calendars** (vendor vs exchange calendar file).

Already locked in this document:

- raw data-layer timestamps stay precise UTC
- `session_as_of` is a derived semantic field, not a raw timestamp
- `report_date` may survive only as a label field, not as the primary time truth

Once the remaining decisions are resolved, update code and templates to match the locked field meanings above.

Also wire §8.2–§8.3 into the canonical Daily Report / market-observation writer packages and skills so every run carries the structured block and the pasteable task rules.
