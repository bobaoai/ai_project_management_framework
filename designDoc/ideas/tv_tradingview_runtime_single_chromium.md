# TradingView Runtime — Single Chromium Plan
**Version 0.1 — 2026-03-23**

Goal: all TradingView-related capabilities run through **one Playwright-controlled Chromium** so we can share:
- one login/session
- one network sniffer surface
- one set of rate limits + retries
- one consistent operational lifecycle (start/stop/status/logs)

This doc defines the **function list** to sync and the **shared runtime contract**.

---

## 1) Canonical Runtime Boundary

### 1.1 Connector boundary (SourceConnectorLayer)
TradingView runtime lives in the connector layer:
- **Capture**: fetch or observe TradingView outputs (news, watchlist membership, fundamentals, quotes)
- **Persist (operational store)**: idempotent writes and recovery (PostgreSQL / Prisma tables for TV connector-owned data)
- **Emit (knowledge objects)**: normalized archives for agents (filesystem KnowledgeBase)

It must *not* become the analysis naming center.

### 1.2 Canonical paths (no fallback search)
Use the existing canonical paths in `.env.example`:
- worker dir: `resource/tv-news-feed-main`
- worker env: `resource/tv-news-feed-main/.env`
- connector state: `data/connectors/tv_news`
- knowledge archive: `data/knowledge/news/tv_news`

---

## 2) One Chromium = One Runtime Service

### 2.1 Service shape
We treat Chromium as an owned runtime with pluggable modules:

- **BrowserManager**
  - launches Chromium (headless configurable)
  - manages one persistent `BrowserContext` for shared cookies/session
  - owns one or more `Page` objects

- **NetworkRouter**
  - subscribes to `page.on("response")`, `page.on("requestfailed")`, `page.on("framenavigated")`
  - routes JSON responses by URL patterns to modules
  - provides dedupe/signature gating to avoid spam

- **Modules (plugins)**
  - each module declares:
    - `match(url, headers) -> boolean`
    - `handle(json, url) -> void`
    - persistence contract (operational store vs knowledge archive)

### 2.2 Why “listen to IO” is the primitive
For TradingView features that are easiest via the web app (watchlists, news flow UI, some APIs), the most robust approach is:
- open the page once
- **listen to the network IO**
- parse JSON responses
- upsert to DB / emit knowledge objects

This avoids brittle DOM scraping.

---

## 3) Function List to Sync (what the runtime must support)

### 3.1 News ingestion (DONE; keep aligned)
- **Source**: `news-mediator.tradingview.com`
  - feed list: `news-flow/v2/news` (cursor pagination)
  - story fetch: `public/news/v1/story?id=...`
- **Operational store**: `news_feed.tradingview_news_items`
- **Knowledge archive**: normalized message objects under `data/knowledge/news/tv_news`
- **Interfaces**
  - start/stop/status (CLI)
  - backfill last N days (cursor pagination)
  - ingest last N hours into KnowledgeBase

### 3.2 Watchlist membership sync (NEXT; naming: Macro + thisweek)
User expectation: switching watchlists like `Macro`, `thisweek` should yield a **current symbol set**.

Two stages:
- **Stage A (IO sniff)**: while Chromium is open, detect watchlist/scanner payloads and extract `EXCHANGE:SYMBOL` strings.
- **Stage B (direct API)**: once we discover the real watchlist endpoints, call them directly (still using the same Chromium session if auth is required).

Outputs:
- operational store (optional): `tv_watchlists`, `tv_watchlist_symbols` tables or JSON blobs keyed by watchlist name
- knowledge archive: `data/knowledge/watchlists/tradingview/<watchlist_name>.json`

### 3.3 Fundamentals snapshot (READY; integrate)
Fundamentals can be fetched via TradingView WebSocket quote sessions.

Design decision:
- WebSocket can run without Chromium, but **we may still centralize orchestration** under the same runtime service for consistency.

Outputs:
- operational store (optional): `tv_symbol_fundamentals` (snapshots with `asof`)
- knowledge archive: snapshots for agent retrieval

### 3.4 Historical bars (>= 30m) for watchlist tickers (PLANNED)
Scope: for all tickers present in `Macro` + `thisweek`, maintain OHLCV history at:
- 30m
- 1h
- 4h
- 1d

Design notes:
- **Symbol universe source**: TradingView watchlists (via the single Chromium runtime).
- **Historical bar source (canonical)**: keep using the existing platform’s historical loader (currently Schwab REST) unless/ until TradingView becomes the canonical bar source.
- **Storage**: `data/hist/` (existing Parquet layout)

Refresh logic (proposed):
- **Daily refresh**: once per day (e.g. after market close) update all intervals for the current watchlist universe.
- **Triggered refresh**:
  - when watchlist membership changes (new ticker appears) → immediately backfill last N days for that ticker (configurable), then join daily schedule.
  - manual `tradectl` trigger for a subset.

Interfaces (target):
- `tradectl tv universe export --name Macro --out data/knowledge/watchlists/tradingview/macro.json`
- `tradectl history update --symbols <from universe> --intervals 30m,1h,4h,1d`
- `tradectl tv history refresh --watchlists Macro,thisweek --intervals 30m,1h,4h,1d`

### 3.5 Realtime quote feed (HOLD; planned)
Streaming quotes is possible via a long-lived quote session:
- output JSONL for piping
- optionally persist to timeseries store later

This is out-of-scope for the first “fundamentals first” milestone, but should share the same symbol universe as watchlists.

---

## 4) Operational Contracts

### 4.1 Single session / login
- Chromium runtime must clearly log if it is on `/accounts/signin/`
- runtime should treat session/cookies as stateful and reusable during one run

### 4.2 Idempotency + recovery
- all persistence operations are **upserts**
- state dir stores pid, logs, and checkpoints (`published_after`, cursor, etc.)

### 4.3 Observability
Minimum signals:
- current page URL
- matched endpoint URL for each module
- counts (items saved / symbols detected / failures)

---

## 5) CLI / Workflow (target)

Single top-level entry in `tradectl`:
- `tradectl tv start` (starts Chromium runtime)
- `tradectl tv status`
- `tradectl tv stop`

Subcommands:
- `tradectl tv news backfill --days 7`
- `tradectl tv news ingest --since-hours 168`
- `tradectl tv watchlists sniff` (during interactive use)
- `tradectl tv watchlists sync --name Macro`
- `tradectl tv fundamentals snapshot --watchlist Macro`
- `tradectl tv history refresh --watchlists Macro,thisweek --intervals 30m,1h,4h,1d`

---

## 6) Immediate Next Milestone (fundamentals + >=30m history for watchlists)

Deliverables:
- Stable extraction of `symbols[]` from watchlist switching (IO sniff)
- Fundamentals snapshot for `symbols[]` with a reproducible output file
- A “Macro / thisweek” symbol universe file suitable for agents
- Daily-refreshable historical bars (>=30m) for the watchlist universe (canonical source: existing history loader)

Acceptance criteria:
- User switches watchlist in Chromium → runtime prints a symbol set (deduped)
- User runs fundamentals snapshot → outputs one JSONL row per symbol with key fields
- User runs history refresh → updates 30m/1h/4h/1d bar parquet for all tickers in the universe
