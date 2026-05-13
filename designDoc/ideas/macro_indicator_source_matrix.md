# Macro Indicator Source Matrix

**Status:** temporary upgrade design doc  
**Date:** 2026-03-27  
**Purpose:** build a large, source-aware matrix for macro, liquidity, positioning, volatility, credit, commodity, and crypto indicators so the repo can verify data access and route the highest-value series into automation.

## 1. Scope And Boundary

This doc answers:

- what macro indicators are worth tracking
- what each indicator actually measures
- which source family should own it first
- how to verify availability
- whether it is realistic to automate in this repo

This doc does **not** define PM judgment or trade recommendations. It stays at the `provider / connector / canonical indicator object` boundary described in:

- [`../source_connectors_and_knowledge_ingestion.md`](../source_connectors_and_knowledge_ingestion.md)
- [`../market_data_architecture.md`](../market_data_architecture.md)
- [`../price_data_architecture.md`](../price_data_architecture.md)
- [`../analysis_platform_and_pm_workspace.md`](../analysis_platform_and_pm_workspace.md)

The paired interpretation-layer design doc is:

- [`macro_analysis_framework_upgrade.md`](macro_analysis_framework_upgrade.md)

## 2. Source Family Roles

### 2.1 Official / public sources

Best for canonical macro truth surfaces when the series is published by the institution that owns it.

Typical examples:

- `FRED`
- `New York Fed`
- `U.S. Treasury FiscalData`
- `Treasury.gov`
- `CFTC`
- `FINRA`
- `BIS`
- `ECB`
- `BoJ`
- `Cboe`
- `Alternative.me`

Use these first when available because:

- provenance is cleaner
- semantics are more stable
- costs are lower
- automation is easier to justify

### 2.2 Broker / price-adjacent providers

Best for tradable proxies, market quotes, FX, rates futures, ETFs, and cross-asset confirmation windows.

Current first-family example:

- `Schwab`

Use this family for:

- `UST` futures or ETF proxies
- `FX`
- `equity index / ETF proxies`
- `commodity / futures price windows`

Do **not** treat broker APIs as the canonical owner of deep macro time series like `TGA`, `ON RRP`, or `MMF flows`.

### 2.3 End-of-day / general market data vendors

Examples:

- `EODHD`
- other end-of-day vendor surfaces the user may test

Best for:

- FX and index history
- ETF histories
- broad market reference enrichment
- backup market-price coverage when broker coverage is thin

Do **not** assume end-of-day vendors are the best first source for institution-owned macro series.

### 2.4 Commercial terminals and vendor analytics

Examples:

- `Bloomberg`
- `Refinitiv`
- `FactSet`

Best for:

- richer coverage
- hard-to-source market structure fields
- positioning and cross-asset datasets
- derived vendor benchmarks such as `MOVE`

These are often the fastest path for validation, but should still be mapped back to canonical indicator objects instead of leaking terminal semantics into downstream workflows.

### 2.5 Sell-side / alt-data / crypto-specialist providers

Examples:

- `EPFR`
- `ICI`
- `NAAIM`
- `AAII`
- `BofA / GS / JPM flow datasets`
- `Glassnode`
- `Coin Metrics`

Use these as enrichment layers, not as the default starting point for the whole stack.

## 3. Current Access And Entitlement View

Before treating a source as part of the default macro stack, separate `theoretically useful`
from `available in this repo right now`.

### 3.1 Tier A: usable now without special entitlements

These should be the default starting point because they are public or effectively public:

- `FRED`
- `New York Fed`
- `U.S. Treasury FiscalData`
- `Treasury.gov`
- `CFTC`
- `FINRA`
- `Alternative.me`
- public exchange or institution pages when the series is directly published there

Interpretation:

- no paid terminal entitlement is required
- provenance is usually clean
- these sources are appropriate for first-pass automation and validation

### 3.2 Tier B: repo-wired, but credential-dependent

These are realistic near-term sources because the repo already has code paths or config hooks,
but they should not be treated as available until local credentials are actually present.

- `Schwab`
- `EODHD`

Current repo evidence:

- `Schwab`: implemented client plus CLI wiring exist under `src/core/schwab_client.py`, `src/market_data/providers.py`, and `src/cli/tradectl.py`
- `EODHD`: implemented client plus fundamentals provider wiring exist under `src/core/eodhd_client.py`, `src/market_data/providers.py`, and `src/cli/tradectl.py`

Current local-state caveat:

- the checked-in `.env` still shows placeholder values
- the local `token/` directory is currently empty in this workspace snapshot
- so these sources are `code-ready` but not yet `credential-confirmed`

### 3.3 Tier C: plausible, but no local entitlement evidence

These may be useful later, but the repo currently shows no strong evidence that they should be
treated as default-access sources:

- `Bloomberg`
- `Refinitiv`
- `FactSet`
- `ICE` proprietary datasets
- `Markit`
- `EPFR`
- `ICI`
- `Glassnode`
- `Coin Metrics`
- sell-side proprietary flow datasets

Interpretation:

- do not make these first-line dependencies
- keep them as optional enrichment or later validation surfaces
- require explicit entitlement confirmation before designing default workflows around them

### 3.4 Practical default rule

For the first macro-monitor implementation pass, prefer sources in this order:

1. `Tier A` public/official sources
2. `Tier B` repo-wired sources once local credentials are confirmed
3. `Tier C` only when a series is not realistically obtainable from the first two tiers

## 4. Verification Protocol

Each candidate indicator should be validated in this order:

1. confirm the repo actually has a use case for it
2. identify the canonical raw series or formula
3. test the cheapest credible source first, with `Tier A` ahead of credentialed vendors whenever possible
4. record whether the source is `public_ready`, `repo_wired_needs_credentials`, `manual_only`, or `entitlement_unknown`
5. record whether `Schwab`, `EODHD`, or another already-wired source can supply a tradable proxy if the canonical public series is insufficient
6. define the normalized indicator object and cadence
7. only then route it into automation

Suggested validation fields:

- `available_now`
- `access_tier`
- `tested_source`
- `tested_symbol_or_endpoint`
- `history_ok`
- `freshness_ok`
- `notes_on_semantics`

## 5. Priority Buckets

### P0: verify and automate first

These are the highest-value series because they support recurring macro regime calls and are realistic to automate:

- `WALCL`
- `TGA`
- `ON RRP`
- `SOFR`
- `EFFR`
- `IORB`
- `UST 2Y`
- `UST 10Y`
- `2s10s`
- `SOFR-FF`
- `USDJPY`
- `EURUSD`
- `DXY`
- `VIX`
- `MOVE`
- `Brent / WTI`
- `IG OAS`
- `HY OAS`

### P1: add after the core stack works

- `MMF flows`
- `bill yields`
- `swap spreads`
- `cross-currency basis`
- `NAAIM`
- `AAII`
- `CFTC positioning`
- `gold`
- `broad commodity indexes`
- `crypto funding and stablecoin proxies`

### P2: niche, expensive, or harder-to-validate

- dealer balance-sheet proxies
- hedge-fund leverage
- JPM-style retail flow datasets
- State Street risk-appetite / positioning datasets
- prime-broker crowding datasets
- some shipping / freight or LNG datasets

## 6. Current-Access-First Routing

The first useful question is not "what is the best imaginable source", but "what can this repo
reliably pull now with the permissions we already have or can confirm quickly".

### 6.1 Public/official first choices

These should move first because they are high-value and do not need paid entitlements:

- `WALCL` -> `FRED`
- `TGA balance` -> `U.S. Treasury FiscalData` or `Treasury.gov`
- `ON RRP` -> `New York Fed`
- `SOFR` -> `New York Fed`
- `EFFR` -> `New York Fed`
- `IORB` -> `FRED`
- `HY OAS` -> `FRED`
- `IG OAS` -> `FRED`
- `VIX` -> `FRED` or `Cboe`
- `2Y UST yield` -> `FRED`
- `10Y UST yield` -> `FRED`
- `30Y UST yield` -> `FRED`
- `2s10s` -> derived locally from public yields
- `SOFR-FF` -> derived locally from public short-rate series
- `Net liquidity` -> derived locally from `WALCL`, `TGA`, and `ON RRP`
- `CFTC positioning` -> `CFTC`
- `FINRA margin debt` -> `FINRA`

Current implementation direction:

- `SOFR` / `EFFR` -> `New York Fed` JSON search endpoints
- `ON RRP` -> `New York Fed` reverse-repo propositions search endpoint
- `TGA balance` -> `Treasury FiscalData` API
- `VIX` -> `Cboe` direct CSV
- `UST 2Y` / `UST 10Y` / `3M bill` -> `Treasury` XML feed pages

### 6.2 Credentialed but already aligned with repo reality

These are reasonable next sources once local credentials are confirmed:

- `USDJPY` -> `Schwab` first, `EODHD` second
- `EURUSD` -> `Schwab` first, `EODHD` second
- `Brent / WTI` -> `Schwab` first for market proxy, `EODHD` second
- `Gold` -> `Schwab` first, `EODHD` second
- `Copper` -> `Schwab` first, `EODHD` second
- broad ETF-style commodity or equity proxies -> `Schwab` first, `EODHD` second

### 6.3 Defer until entitlement is explicit

Do not make these blocking dependencies for the first pass:

- `MOVE`
- cross-currency basis
- `CDX`
- swap spreads from proprietary feeds
- `SPX` skew
- crude skew
- `MVRV`
- institutional flow datasets

These can stay in `research-only`, `manual-validation`, or `enrichment-later` status until a clear entitlement path is confirmed.

### 6.4 Availability snapshot by priority

Status meanings:

- `available_now`: should be obtainable now from public/official sources without special entitlements
- `needs_credentials`: repo wiring exists or a realistic connector path exists, but local credentials are not yet confirmed
- `manual_only`: source likely exists, but the current repo does not yet have a clean automated path or the public path is too inconsistent
- `entitlement_unknown`: probably useful, but we should not assume access until you explicitly confirm the source entitlement

#### P0 snapshot

| Indicator | Preferred source now | Availability status | Notes |
| --- | --- | --- | --- |
| `WALCL` | `Fed H.4.1` bulk XML | `available_now` | Official Federal Reserve balance-sheet series now normalized locally from `RESPPA_N.WW`. |
| `TGA balance` | `FiscalData` / `Treasury.gov` | `available_now` | Official source should be canonical. |
| `ON RRP` | `New York Fed` reverse-repo API | `available_now` | Official daily total accepted amount path. |
| `SOFR` | `New York Fed` | `available_now` | Official daily rate. |
| `EFFR` | `New York Fed` / `FRED` | `available_now` | Public official path. |
| `IORB` | `FRED` | `available_now` | Public policy-rate anchor. |
| `UST 2Y` | `Treasury` XML feed | `available_now` | Prefer official Treasury XML over a FRED relay when possible. |
| `UST 10Y` | `Treasury` XML feed | `available_now` | Prefer official Treasury XML over a FRED relay when possible. |
| `2s10s` | derived from `FRED` | `available_now` | Derived locally after yields are ingested. |
| `SOFR-FF` | derived from public short-rate series | `available_now` | Derived locally after `SOFR` and `EFFR`. |
| `USDJPY` | `Schwab`, then `EODHD` | `needs_credentials` | Repo-aligned, but local auth is not yet confirmed. |
| `EURUSD` | `Schwab`, then `EODHD` | `needs_credentials` | Same as `USDJPY`. |
| `DXY` | public proxy or proprietary feed | `manual_only` | Exact canonical path is still awkward without confirmed entitlement. |
| `VIX` | `FRED` or `Cboe` | `available_now` | Good public first-pass series. |
| `MOVE` | `Bloomberg` / `ICE` / `Refinitiv` | `entitlement_unknown` | Do not assume access. |
| `Brent / WTI` | `Schwab`, then `EODHD` | `needs_credentials` | Repo-ready market proxy path, pending credentials. |
| `IG OAS` | `FRED API` | `needs_credentials` | Source path is straightforward, but this environment needs `FRED_API_KEY`; legacy `fredgraph` timed out. |
| `HY OAS` | `FRED API` | `needs_credentials` | Same as `IG OAS`; route is ready once `FRED_API_KEY` is configured. |

#### P1 snapshot

| Indicator | Preferred source now | Availability status | Notes |
| --- | --- | --- | --- |
| `MMF flows` | public association data, maybe `ICI` | `manual_only` | Public coverage is partial and may need hand validation first. |
| `bill yields` | `Treasury` / `FRED` | `available_now` | Good public follow-on series. |
| `swap spreads` | proprietary feed or local derivation later | `entitlement_unknown` | Likely not a clean first-pass public series. |
| `cross-currency basis` | `Bloomberg` / `Refinitiv` / partial public sources | `entitlement_unknown` | Keep out of the first implementation wave. |
| `NAAIM` | `NAAIM` official publication | `manual_only` | Probably accessible, but automation path is not yet defined. |
| `AAII` | `AAII` official publication | `manual_only` | Likely usable, but still needs a stable scrape/import path. |
| `CFTC positioning` | `CFTC` | `available_now` | Public and realistic to automate. |
| `gold` | `Schwab`, then `EODHD` | `needs_credentials` | Repo-aligned market-data route. |
| `broad commodity indexes` | ETF proxy via `Schwab` / `EODHD` | `needs_credentials` | Use ETF proxies first, not premium benchmark dependency. |
| `crypto funding and stablecoin proxies` | public crypto aggregators | `manual_only` | Fragmented source quality; treat as later enrichment. |

## 7. Indicator Matrix

| Indicator | Category | What it measures | Raw series or formula | Source candidates | Best-first validation path | Cadence | Automation readiness | Priority | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `WALCL` | Fed plumbing | Fed total assets | `RESPPA_N.WW` | `Fed H.4.1`, `Bloomberg` | official `Fed H.4.1` bulk XML first | weekly | high | `P0` | Core net-liquidity input; now normalized from the official Fed release. |
| `TGA balance` | Fed plumbing | Treasury cash drain/injection effect | Treasury General Account balance | `FiscalData`, `Treasury`, `Bloomberg` | official Treasury dataset first | daily | high | `P0` | Needed for net-liquidity and tax-date stress windows. |
| `ON RRP` | Fed plumbing | parked cash at the Fed | Overnight reverse repo usage | `New York Fed`, `FRED`, `Bloomberg` | `New York Fed` first | daily | high | `P0` | Core official liquidity-stack input. |
| `Reserve balances` | Fed plumbing | bank reserve conditions | reserve balances with Fed banks | `FRED`, `Fed H.4.1`, `Bloomberg` | `FRED` first | weekly | medium | `P1` | Useful but less immediate than `TGA` and `ON RRP`. |
| `Net liquidity` | Derived liquidity | broad system liquidity proxy | `WALCL - TGA - ON RRP` | derived from official inputs, `Bloomberg` | compute locally from official series | daily/weekly | high | `P0` | Should be platform-owned derived object, not provider-native. |
| `SOFR` | Funding | secured overnight funding rate | SOFR daily print | `New York Fed`, `FRED`, `Bloomberg` | `New York Fed` first | daily | high | `P0` | Repo plumbing anchor. |
| `EFFR` | Funding | unsecured overnight funding rate | Effective Fed Funds Rate | `New York Fed`, `FRED`, `Bloomberg` | `New York Fed` first | daily | high | `P0` | Pair with `SOFR` for basis. |
| `IORB` | Policy plumbing | reserve remuneration floor | Interest on Reserve Balances | `FRED`, `Fed`, `Bloomberg` | `FRED` first | event-driven | high | `P0` | Policy anchor, not high-frequency stress signal. |
| `SOFR-FF` | Funding stress | secured vs unsecured short-end spread | `SOFR - EFFR` | derived locally, `Bloomberg` | compute locally from official series | daily | high | `P0` | Mentioned repeatedly in local macro drafts. |
| `TGCR / BGCR` | Funding detail | repo benchmark context beyond SOFR | TGCR, BGCR | `New York Fed`, `Bloomberg` | `New York Fed` first | daily | medium | `P1` | Useful if repo segmentation matters. |
| `Repo volume` | Funding detail | depth and softness in repo markets | NY Fed repo statistics | `New York Fed`, `Bloomberg` | official first | daily | medium | `P1` | Complements rate prints. |
| `MMF assets / flows` | Cash migration | money-market fund inflows and cash parking | ICI MMF assets or equivalent flow series | `ICI`, `FRED` if available, `Bloomberg` | `Bloomberg` and public association data | weekly | medium | `P1` | Important in repo narrative; public coverage may be partial. |
| `Bill yields` | Funding / T-bills | front-end safe-asset demand | 1M, 3M, 6M T-bill yields | `Treasury`, `FRED`, `Bloomberg`, `Schwab` | `Treasury` or `FRED` first | daily | high | `P1` | Good confirmation of cash demand. |
| `Bill-OIS` | Funding stress | Treasury-bill rich/cheap vs OIS | bill yield minus OIS | derived, `Bloomberg` | derive after bill/yield inputs exist | daily | medium | `P1` | Helpful for front-end strain. |
| `2Y UST yield` | Rates repricing | front-end policy expectations | `DGS2` or market quote | `FRED`, `Treasury`, `Bloomberg`, `Schwab` | `FRED` first, `Schwab` for trade proxy | daily | high | `P0` | Core cuts/hikes window. |
| `10Y UST yield` | Rates repricing | long-end growth/inflation discount rate | `DGS10` or market quote | `FRED`, `Treasury`, `Bloomberg`, `Schwab` | `FRED` first | daily | high | `P0` | Also links to existing `UST` technical anchors. |
| `30Y UST yield` | Rates repricing | long-duration discount rate | `DGS30` | `FRED`, `Treasury`, `Bloomberg`, `Schwab` | `FRED` first | daily | high | `P1` | Helps term-premium and long-duration framing. |
| `2s10s` | Curve | curve shape / growth-policy regime | `10Y - 2Y` | derived, `Bloomberg` | derive locally from `2Y` and `10Y` | daily | high | `P0` | Core regime classifier. |
| `5s30s` | Curve | deeper curve steepening signal | `30Y - 5Y` | derived, `Bloomberg` | derive locally after base yields exist | daily | medium | `P1` | Useful for reflation / term-premium moves. |
| `Real yields` | Rates / inflation | inflation-adjusted discount rate | TIPS real yields | `FRED`, `Bloomberg`, `Schwab` via proxies | `FRED` first | daily | high | `P1` | Useful for gold and duration themes. |
| `Breakevens` | Inflation pricing | inflation compensation | nominal yield minus TIPS real yield | `FRED`, `Bloomberg` | derive locally from public series | daily | medium | `P1` | Strong cross-asset interpretation value. |
| `SOFR futures cuts/hikes path` | Rates repricing | forward policy path | front SOFR futures strip, e.g. `ZQ/SR3` chain | `Bloomberg`, `Schwab`, `EODHD` if supported | `Bloomberg` first, test `Schwab` for futures access | intraday/daily | medium | `P1` | Valuable but implementation depends on futures access. |
| `MOVE` | Rates volatility | Treasury vol / rates hedging cost | ICE BofA MOVE | `Bloomberg`, `ICE`, `Refinitiv` | `Bloomberg` first | daily | medium | `P0` | Usually commercial; worth testing early. |
| `VIX` | Equity volatility | equity index implied vol | `VIX Index` | `Cboe`, `FRED`, `Bloomberg`, `Schwab`, `EODHD` | `Cboe` or `FRED` first | daily/intraday | high | `P0` | Already appears in local observation packages. |
| `VVIX` | Vol surface | vol-of-vol / crash convexity demand | `VVIX Index` | `Cboe`, `Bloomberg` | `Cboe` first | daily | medium | `P1` | Useful for crowded hedge detection. |
| `SPX put skew` | Vol surface | crash insurance richness | skew or 25d put metrics | `Bloomberg`, `Cboe DataShop` | `Bloomberg` first | daily | low/medium | `P2` | High value, but usually commercial and more complex. |
| `Crude skew / implied vol` | Commodity vol | oil tail-hedge pricing | crude option skew/iv surface | `Bloomberg`, `Refinitiv` | `Bloomberg` first | daily | low/medium | `P2` | Theme-specific, useful for event shock packs. |
| `Brent spot/front future` | Commodity | global oil shock window | Brent front contract or spot proxy | `Bloomberg`, `Schwab`, `EODHD`, public market data | `Schwab` or `Bloomberg` first | intraday/daily | high | `P0` | Core geopolitical transmission anchor. |
| `WTI spot/front future` | Commodity | U.S. oil shock window | WTI front contract or spot proxy | `Bloomberg`, `Schwab`, `EODHD`, public market data | `Schwab` or `Bloomberg` first | intraday/daily | high | `P0` | Pairs naturally with energy equity basket. |
| `Gold` | Commodity / monetary hedge | policy uncertainty / real-yield interaction | spot gold or front gold future | `Bloomberg`, `Schwab`, `EODHD` | `Schwab` or `Bloomberg` first | intraday/daily | high | `P1` | Use within `gold-monetary-fragmentation`, not as a universal hedge shortcut. |
| `Broad commodity index` | Inflation transmission | generalized commodity impulse | BCOM / GSCI or ETF proxy | `Bloomberg`, `EODHD`, `Schwab` via ETF proxy | `Bloomberg` first, ETF fallback | daily | medium | `P1` | Better than single-commodity overfitting in some regimes. |
| `USDJPY` | Cross-border dollar | yen funding and Japan import shock window | spot FX | `Bloomberg`, `Schwab`, `EODHD` | `Schwab` or `Bloomberg` first | intraday/daily | high | `P0` | Central local observation window. |
| `EURUSD` | Cross-border dollar | Europe funding / energy-import window | spot FX | `Bloomberg`, `Schwab`, `EODHD` | `Schwab` or `Bloomberg` first | intraday/daily | high | `P0` | Cleaner than `DXY` for some external-shock questions. |
| `DXY` | Broad dollar | broad USD strength | Dollar index | `Bloomberg`, `Schwab`, public market data | `Bloomberg` first, public proxy verify | daily | medium | `P0` | Useful but not always the cleanest observation window. |
| `Cross-currency basis` | Offshore dollar stress | hedging cost / offshore USD strain | EURUSD or USDJPY basis series | `Bloomberg`, `Refinitiv`, `BIS` partial | `Bloomberg` first | daily | medium | `P1` | High signal, but mostly commercial. |
| `US2Y-JP2Y spread` | Cross-border rates | carry / policy divergence pressure on yen | `UST2Y - JGB2Y` | derived, `Bloomberg` | `Bloomberg` first for JGB series | daily | medium | `P1` | Good complement to `USDJPY`. |
| `NAAIM exposure index` | Positioning | active manager equity exposure | NAAIM weekly exposure survey | `NAAIM`, `Bloomberg` | NAAIM official publication first | weekly | medium | `P1` | Public enough to test quickly. |
| `AAII sentiment` | Positioning | retail investor sentiment survey | bullish / bearish survey shares | `AAII`, `Bloomberg` | official AAII first | weekly | high | `P1` | Low cost, useful as soft sentiment check. |
| `CFTC futures positioning` | Positioning | speculative crowdedness across futures | COT net positions | `CFTC`, `Bloomberg` | CFTC first | weekly | high | `P1` | Works well for oil, rates, FX, gold. |
| `FINRA margin debt` | Leverage | retail / market leverage backdrop | FINRA margin debt series | `FINRA`, `Bloomberg` | official first | monthly | high | `P1` | Slow-moving but useful for risk appetite regime. |
| `State Street risk appetite / positioning` | Positioning | institutional allocation pressure | proprietary State Street series | `Bloomberg`, vendor research | commercial validation first | daily/weekly | low | `P2` | Valuable, but access uncertain. |
| `JPM retail flows` | Positioning | retail buying pressure | proprietary JPM dataset | `Bloomberg`, JPM research | commercial validation first | daily/weekly | low | `P2` | Likely sell-side gated. |
| `HY OAS` | Credit stress | high-yield credit spread stress | option-adjusted spread | `FRED`, `Bloomberg` | `FRED` first | daily | high | `P0` | Simple, high-signal macro stress input. |
| `IG OAS` | Credit stress | investment-grade spread stress | option-adjusted spread | `FRED`, `Bloomberg` | `FRED` first | daily | high | `P0` | Good quality-spread benchmark. |
| `CDX HY / CDX IG` | Credit stress | faster-moving credit hedge pricing | CDX indexes | `Bloomberg`, `Markit` | `Bloomberg` first | intraday/daily | medium | `P1` | More tactical than OAS. |
| `Swap spreads` | Treasury plumbing | dealer balance-sheet and UST intermediation stress | swap rate minus Treasury yield | `Bloomberg`, derived from swap and UST series | `Bloomberg` first | daily | medium | `P1` | Already appears in local plumbing theme. |
| `TED spread` | Legacy funding stress | bank funding spread proxy | LIBOR or replacement minus T-bill | `Bloomberg`, public historical sources | commercial first | daily | low | `P2` | Legacy metric, lower priority in current framework. |
| `BBB corporate spread` | Credit / growth | middle-quality credit stress | BBB spread series | `FRED`, `Bloomberg` | `FRED` first | daily | high | `P1` | Useful bridge between IG and HY. |
| `Copper` | Growth / industrial | cyclical demand pulse | front copper future or ETF proxy | `Bloomberg`, `Schwab`, `EODHD` | `Schwab` or `Bloomberg` first | intraday/daily | high | `P1` | Good cross-check on growth damage. |
| `LNG Asia / JKM proxy` | Energy import shock | Asia energy import cost | JKM or LNG proxy series | `Bloomberg`, vendor data | commercial first | daily | low/medium | `P2` | Important for Japan window but not easy to source cheaply. |
| `Baltic / tanker rates` | Shipping stress | physical disruption and freight stress | BDI or tanker-rate series | `Bloomberg`, public exchange sources | public + Bloomberg validation | daily | medium | `P2` | Useful for event themes, not always macro-core. |
| `BTC spot` | Crypto liquidity | risk appetite and liquidity beta | BTCUSD spot | `Bloomberg`, `Schwab` if available, crypto APIs, `EODHD` | easiest reliable market-data source first | intraday/daily | high | `P1` | Tradable proxy window, not a complete crypto regime view. |
| `BTC funding rates` | Crypto positioning | speculative leverage in crypto | exchange funding rate aggregates | exchange APIs, `CoinGlass`, `Bloomberg` | public crypto aggregation first | intraday | medium | `P2` | Valuable, but fragmented by venue. |
| `MVRV` | Crypto valuation / pain | market value vs realized value | MVRV ratio | `Glassnode`, `Coin Metrics` | commercial crypto specialist first | daily | low/medium | `P2` | Strong signal, but usually paid. |
| `Stablecoin supply` | Crypto liquidity | crypto-native dollar liquidity | aggregate stablecoin market cap | `Glassnode`, `Coin Metrics`, public aggregators | public aggregator first, specialist confirm | daily | medium | `P2` | Better as crypto-liquidity layer than a standalone trigger. |
| `Crypto fear and greed` | Crypto sentiment | broad crypto mood | composite sentiment index | `Alternative.me`, public aggregators | official public index first | daily | high | `P2` | Easy to automate, lower signal than on-chain + funding. |

## 8. First Validation Queue

The first validation sprint should stay narrow and executable.

### 8.1 Phase A: public/official first

- `WALCL`
- `TGA balance`
- `ON RRP`
- `SOFR`
- `EFFR`
- `IORB`
- `HY OAS`
- `IG OAS`
- `VIX`

### 8.2 Phase B: public-derived objects

- `Net liquidity`
- `SOFR-FF`
- `2s10s`

### 8.3 Phase C: repo-wired credentialed windows after auth is confirmed

- `UST 2Y`
- `UST 10Y`
- `USDJPY`
- `EURUSD`
- `Brent`
- `WTI`

### 8.4 Phase D: defer until explicit entitlement

- `DXY` if only proprietary or awkward proxy routes are available
- `MOVE`
- cross-currency basis
- `CDX HY / CDX IG`
- swap spreads

## 9. Automation Readiness Rule

An indicator can enter the default automation flow only when all of the following are true:

1. the source is stable enough to refresh without manual rescue
2. the semantic definition is clear enough to normalize
3. the series is useful across more than one analysis context
4. the repo can explain the indicator without terminal-specific hidden assumptions

If any of those are false, keep the indicator in `manual-validation` or `research-only` status.

## 10. Proposed Normalized Indicator Object

Every validated series should eventually normalize into a lightweight platform-owned object such as:

- `indicator_id`
- `indicator_name`
- `category`
- `provider`
- `provider_symbol_or_endpoint`
- `access_tier`
- `availability_status`
- `value`
- `unit`
- `observation_time`
- `as_of`
- `cadence`
- `is_derived`
- `formula`
- `freshness_bucket`
- `confidence`
- `notes`

## 11. Cross-Links To Existing Repo Reality

These local surfaces already point to a real need for this matrix:

- [`../../data/research/themes/reports/usd-liquidity-plumbing.md`](../../data/research/themes/reports/usd-liquidity-plumbing.md)
- [`../../data/research/theme_update_drafts/iran-hormuz-escalation.ds.md`](../../data/research/theme_update_drafts/iran-hormuz-escalation.ds.md)
- [`../analysis_platform_and_pm_workspace.md`](../analysis_platform_and_pm_workspace.md)
- [`macro_analysis_framework_upgrade.md`](macro_analysis_framework_upgrade.md)

The repo already repeatedly uses windows like `SOFR-FF`, `TGA`, `RRP`, `USDJPY`, `EURUSD`, `VIX`, `DXY`, `cross-currency basis`, and `UST` yields. This doc turns those recurring references into a validation and automation plan instead of leaving them as ad hoc research mentions.

## 12. Implementation Backlog

1. Validate all `P0` public-series endpoints and record exact symbols or URLs.
2. Confirm whether local `Schwab` credentials and `EODHD` token are actually present on the machine before treating them as default sources.
3. Define a normalized `MacroIndicatorSnapshot` object in the platform layer with `access_tier` and `availability_status`.
4. Implement local derivation for `Net liquidity`, `SOFR-FF`, and `2s10s`.
5. Mark each matrix row as `validated`, `partial`, `manual-only`, `blocked`, or `needs_credentials`.
6. Promote the validated public subset into a first macro monitor pack before adding terminal-dependent enrichments.
