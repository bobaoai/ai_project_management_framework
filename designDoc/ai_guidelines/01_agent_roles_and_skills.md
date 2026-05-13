# 01 Agent Roles And Skills

## Goal

Describe each AI role as a reusable skill bundle.

## NewsMacroAnalyst

### Role
- read research inputs and news feeds
- summarize macro regime
- identify portfolio-relevant events

### Skills
- `fetch_research_inputs`
- `classify_news_relevance`
- `build_macro_snapshot`
- `detect_macro_risk_flags`
- `generate_news_digest`

### Inputs
- portfolio symbols
- configured research sources
- optional event calendar

### Outputs
- `NewsItem[]`
- `MacroSnapshot`
- `RiskFlag[]`
- digest string

## PortfolioRiskAdvisor

### Role
- inspect current holdings and exposures
- identify concentration, delta imbalance, and expiry clustering
- propose manual adjustment ideas

### Skills
- `load_portfolio_state`
- `compute_exposure_summary`
- `detect_delta_gap_analysis`
- `detect_concentration_risk`
- `detect_expiration_risk`
- `generate_rebalance_ideas`

### Inputs
- `AccountSnapshot[]`
- `ExposureSummary[]`
- latest options/price state
- risk profile config

### Outputs
- `Recommendation[]`
- `RiskFlag[]`
- digest string

## TechnicalScreener

### Role
- scan the universe using the user's trading logic
- score symbols with multi-timeframe technical conditions

### Skills
- `build_screening_universe`
- `load_symbol_analytics`
- `score_wave_setup`
- `score_trend_alignment`
- `score_iv_condition`
- `evaluate_symbol`
- `rank_candidates`

### Inputs
- symbol universe
- wave outputs
- trend outputs
- IV metrics
- screening thresholds

### Outputs
- `Signal[]`
- `RejectReason[]`
- ranked watchlist

## WorkflowOrchestrator

### Role
- build shared context
- decide execution order
- persist outputs
- export manifest for future AI tool routers

### Skills
- `build_context`
- `run_agent`
- `run_all`
- `get_agent_manifest`
- `export_manifest`

### Outputs
- `AgentOutput`
- persisted JSON artifacts
- `agent_manifest.json`
