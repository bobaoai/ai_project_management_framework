# Asset Technical Signal Pipeline

## Goal

Track a reusable basket of macro-relevant assets with a management-layer-first workflow:

- ticker coverage/admission determines which tickers should be tracked
- per-ticker profiles hold durable methodology choices
- code generates current deterministic technical state only
- DeepSeek writes the final current asset summaries from the current index row plus profile and signal packet inputs
- downstream market-observation packages consume stable current artifacts

## Canonical Paths

- coverage index: `data/knowledge/asset_technicals/coverage_index.json`
- coverage markdown: `data/knowledge/asset_technicals/coverage_index.md`
- per-ticker profiles: `data/knowledge/asset_technicals/profiles/`
- generated fallback profiles: `data/knowledge/asset_technicals/generated_profiles/`
- legacy source manifest: `data/knowledge/asset_technicals/profiles.json`
- profile directory index: `data/knowledge/asset_technicals/profiles/index.json`
- observation baskets: `data/knowledge/asset_technicals/observation_baskets.json`
- current deterministic packets: `data/knowledge/asset_technicals/signal_packets/`
- current AI-written summaries: `data/knowledge/asset_technicals/reports/`
- generated total index: `data/knowledge/asset_technicals/index.json`

## Responsibility Split

### Deterministic layer

`src/tools/build_asset_technical_reports.py` now:

- rebuilds theme-driven coverage
- loads per-ticker profiles
- computes current technical state
- overwrites `signal_packets/` with only the latest current files
- rebuilds the total index

The packet should contain:

- requested and returned symbol
- current OHLCV
- raw UTC timestamp for the current OHLCV row
- derived session field for the current OHLCV row when needed
- daily percent move
- EMA stack
- RSI
- 1y weekly close context
- 3m daily close plus indicator context
- short support and resistance candidates
- annual range position
- rule-based signal labels
- multi-week structure state
- breakout and breakdown triggers
- upside and downside target candidates
- current setup candidates and top setup summary
- fib context when applicable
- technical setup projection for downstream writer consumption
- coverage metadata
- methodology metadata

The deterministic layer does not write final conclusion prose.

It also must not persist:

- dated technical packet archives
- temporary AI writer packages
- rolling 1y derived technical tables

### AI narrative layer

`writer-asset-technical` reads the current index row plus the current signal packet and methodology profile, then writes:

- the final current asset summary
- the method emphasis for continuity
- any level framing or confirmation logic that matters today

### Index layer

`src/tools/build_asset_technical_index.py` rebuilds the canonical index from:

- `coverage_index.json`
- `signal_packets/*.json`
- `reports/*.md`

Operator-facing dashboard pages may additionally project this index into static HTML:

- `data/dashboard/technical/index.html`
- `data/dashboard/technical/assets/*.html`

The index should show:

- coverage/theme linkage
- whether a ticker already has a profile
- latest signal date
- latest returned symbol
- primary methods
- latest deterministic status
- multi-week state
- top setup type and quality
- whether the packet includes weekly/daily price context windows
- latest AI report path
- latest AI takeaway

### Theme package layer

`src/tools/assemble_market_observation_package.py` should inject:

- deterministic current signal labels and packet references
- multi-week state and current daily move fields
- AI-written per-asset summaries
- local macro snapshot rows from the platform-owned macro store, with freshness status

This keeps market-observation packages evidence-backed without hardcoding Python-written technical prose.

Current workflow default:

- package builders should auto-refresh the relevant current AI-written asset reports before injecting them
- `assemble_market_observation_package.py` should refresh the theme basket from `observation_baskets.json`
- `build_theme_writer_package.py` should refresh the current relevant technical basket for the theme before assembling the writer package
- both builders may expose an explicit skip flag for recovery or debugging, but the safe default is refresh-first
- refresh-first does not mean rewrite-every-time: if an existing AI technical report already matches the current asset session label and was generated after the relevant close / completion rule for that asset, refresh may treat it as final for that session and skip re-drafting it unless the caller explicitly forces overwrite

Fixed sequence for theme package work:

1. decide the target theme metadata first
2. make sure the theme metadata already lists the ticker set that the package is expected to reason about
3. admit those theme tickers into technical coverage, even when the theme is still `draft_candidate`
4. rebuild current signal packets for that explicit ticker set
5. draft or refresh the AI-written asset technical summaries
6. update the theme context index `technical_paths` explicitly
7. only then assemble the writer package

Canonical path interpretation of that sequence:

- if a theme package needs a ticker that is currently missing from the technical layer, first expand the theme metadata asset admission rather than leaving the ticker as research-only context
- after that admission, run the technical refresh path directly so the ticker becomes a first-class canonical technical artifact set
- the expected canonical flow is:
  - `data/research/themes/metadata/<theme_id>.json`
  - `data/knowledge/asset_technicals/coverage_index.json`
  - `data/knowledge/asset_technicals/generated_profiles/`
  - `data/knowledge/asset_technicals/signal_packets/`
  - `data/knowledge/asset_technicals/reports/`
  - `data/knowledge/asset_technicals/index.json`
- in operator terms: first expand theme metadata `linked_asset_tickers` or active subtheme tickers so the missing ticker is formally admitted into the canonical technical workflow; then run technical refresh so `generated_profiles/`, `signal_packets/`, and `reports/` are actually materialized before package assembly
- do not stop at "the theme mentions the ticker" if the package is expected to reason about price structure, levels, or trade framing; the ticker should be pushed all the way through the canonical technical path unless market data itself is unavailable

Guardrail:

- do not rely on the writer or package assembler to "notice" a ticker from raw source prose and silently pull it into the technical layer
- if a ticker matters to the theme package, it must first become explicit in theme metadata or the context index and then be admitted into the technical refresh path

## Writer Output Boundary

`asset technical report` 现在也应被视为正式报告流，而不是“signal packet 顺手配一段 prose”。

推荐固定为：

1. deterministic technical inputs
2. `asset technical package`
3. `external writer layer`
4. `final asset technical report`

固定边界：

- profile / signal packet / technical index row 属于 deterministic input
- packager 负责把这些输入整理成 writer-facing package body
- manifest sidecar 负责保存 report_id、asset_id、source paths、generation metadata、backend choice 等 control-plane 信息
- writer backend 默认走 `DeepSeek`
- `Cursor CLI` 可以作为显式可选 backend

这样做的目的不是把 technical 变成自由写作，而是：

- 让 technical、theme、market observation、weekly review、portfolio debate 共用同一个输出层
- 保证 writer 看到的是受控 package，而不是直接面对散乱 runtime objects
- 让 future `single-stock analysis` 能复用同一 writer contract

## Shared Daily Update Status

**Normative target:** technical signal packets and AI reports should align with per-instrument **last completed session** and carry:

- precise raw UTC time fields for the underlying market data
- derived session fields such as `session_as_of` / `session_date_utc`
- `generated_at` for the artifact audit clock

They should not collapse everything into a single forced calendar `as_of` when sessions diverge across asset classes. See [`../last_session_truth_and_ingestion_boundary.md`](../last_session_truth_and_ingestion_boundary.md). Until implementation fully lands, some tools may still use a global `report_date`; treat that as a transitional label rather than primary time truth.

Current implementation now adds one shared operator-facing status surface:

- `tradectl data status`
- `tradectl data update`
- `data/dashboard/daily_update_status.json`

Technical-layer rule inside that surface:

- missing or stale signal packets are blocking for downstream technical-driven package rebuilds
- stale or missing AI-written summaries are visible in status and should normally be refreshed before package assembly
- asset-level `data_status != ok` should stay explicit in the signal packet rather than being silently hidden by package builders

This means downstream package builders should not invent their own freshness logic ad hoc.
They should read the shared daily update status first, then either:

- proceed
- stop with a deterministic blocking message
- or continue only in explicitly allowed degraded cases

## Coverage Model

Coverage is assembled from two upstream sources:

- active short-term and medium-term theme metadata via `linked_asset_tickers` and active subthemes
- explicit observation-basket assets used by current market-observation packages
- latest saved account holdings, normalized to underlying symbols for current portfolio monitoring

更上层应把它理解为一个统一的 `ticker coverage / admission layer`，而不是“theme 附带的 technical 宇宙”。

当前 admission source 至少包括：

- approved theme routing surface
- explicit draft-theme technical admission
- observation baskets
- latest portfolio holdings

后续还应允许：

- manual ticker list
- task-scoped ticker list

This allows the total technical universe to expand with theme metadata while still preserving the current macro observation basket used in day-to-day package assembly.

Candidate-theme extension:

- approved themes still drive the default daily coverage surface through `current_priority_tree.json`
- a theme package rebuild may additionally admit one explicit `draft_candidate` theme into coverage when the package needs its ticker set
- this admission is for technical evidence support only; it does not promote the theme into routing or priority views

把这类 admission 正式称为：

- `technical_admission_only`

其语义固定为：

- 允许某个 theme 或 ticker 集进入当前 technical coverage
- 允许其生成 `coverage -> generated_profiles -> signal_packets -> reports -> index`
- 但不意味着它进入 `themes/index.json` 或 `current_priority_tree.json`
- 也不意味着它自动获得正式 routing authority

Current runtime extension:

- if a covered theme asset already has a manual profile under `data/knowledge/asset_technicals/profiles/`, that manual profile stays canonical
- if a covered theme asset does not yet have a manual profile, the build step auto-generates a minimal runtime profile under `data/knowledge/asset_technicals/generated_profiles/`
- runtime, refresh, and AI drafting should read a merged profile view where manual profiles override generated profiles

This means theme-linked assets are no longer limited to coverage-only visibility; they are pulled into the actual daily technical refresh surface unless they still fail at the market-data layer.

Current account-holdings extension:

- latest saved account snapshots should also admit current holdings into technical coverage
- option positions should contribute their underlying symbol, not the option contract itself
- holding-admitted assets may auto-generate minimal runtime profiles the same way theme-admitted assets do
- operator-facing index/card views should keep visible which account-held assets were admitted through portfolio holdings

后续 manual/task admission extension:

- manual ticker list 应允许 admission 到当前 technical coverage，而不要求先挂到某个 theme
- task-scoped ticker list 也应允许作为当前工作批次的临时 admission source
- 这类 admission 是否持久化，应由更上层的 coverage policy 决定，而不是由 technical pipeline 自己猜

## Compute Boundary

Current implementation decision:

- compute technical state in application code
- use PostgreSQL-backed platform bar storage first
- if local daily bars are unavailable, pull the configured primary provider's daily bars in memory as a fallback
- `history_loader` is the canonical persistence path for price bars and writes into platform-owned PostgreSQL tables
- local parquet files are export/cache artifacts, not the canonical runtime source
- do not persist the fetched rolling technical table back as a derived artifact

Time contract inside this compute boundary:

- data-layer bars remain precise UTC-backed observations
- runtime may derive `session_date_utc` / `session_as_of` for semantics
- AI-written summaries may render ET/PT/session wording only after those upstream fields are explicit

This keeps the downstream contract stable while leaving room to move the computation surface into Postgres later without changing:

- signal packet shape
- current report shape
- total index shape
- theme package integration

## Current Basket

Current profiled basket:

- `/CL`
- `/ES`
- `/NQ`
- `/ZN`
- `/GC`
- `/VX`
- `XLE`
- `XOP`
- `GLD`
- `SPY`
- `QQQ`

## Current Known Constraint

`/VX` daily history may still be unavailable from Schwab even when other futures roots return mapped contracts. In that case:

- keep `/VX` in the basket
- preserve the missing-data status in the signal packet
- do not fabricate a futures technical summary
- use public VIX context only as a labeled proxy
