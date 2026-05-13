# 07 Example Payloads

## Purpose

Provide minimal example JSON payloads so future AI tools can integrate with the platform without reading Python dataclasses first.

## Example `AgentContext` (conceptual JSON view)

`AgentContext` is an in-memory dataclass, but this is the conceptual shape an AI router should assume.

```json
{
  "positions": [
    {
      "symbol": "NVDA",
      "asset_type": "EQUITY",
      "qty_net": 100,
      "mv_broker": 118500.0,
      "delta_quote": 1.0,
      "mv_delta_quote": 118500.0
    },
    {
      "symbol": "NVDA250620C00120000",
      "asset_type": "OPTION",
      "qty_net": -2,
      "mv_broker": -4200.0,
      "delta_quote": 42.0,
      "mv_delta_quote": -9954.0
    }
  ],
  "exposure": {
    "TECH": {
      "basket_id": "TECH",
      "basket_name": "Technology",
      "mv_broker": 145000.0,
      "mv_delta_quote": 132000.0,
      "pnl_open": 9200.0
    }
  },
  "price_cache": "PriceCache(handle)",
  "history_db_path": "data/ticks.sqlite",
  "hist_dir": "data/hist",
  "analytics_results": {
    "wave_scores": {
      "NVDA": {"score": 78, "timeframe": "30m"}
    },
    "signals": {
      "NVDA": {"aligned": true, "direction": "long"}
    },
    "iv_data": {
      "NVDA": {"iv_percentile": 61}
    }
  },
  "config": {
    "target_delta_pct": 0.5,
    "max_single_name_pct": 0.15
  },
  "run_date": "2026-03-19T10:15:00Z"
}
```

## Example `AgentOutput`

```json
{
  "agent_name": "advisor",
  "run_at": "2026-03-19T10:16:00Z",
  "status": "partial",
  "recommendations": [
    {
      "action": "REDUCE",
      "symbol": "NVDA",
      "rationale": "Single-name concentration exceeds configured threshold.",
      "urgency": "medium",
      "source_agent": "advisor",
      "confidence": 0.83,
      "delta_impact": -25000.0,
      "metadata": {
        "basket": "TECH"
      }
    }
  ],
  "signals": [],
  "risk_flags": [
    {
      "code": "CONCENTRATION_ALERT",
      "severity": "medium",
      "message": "NVDA concentration is above the configured ceiling.",
      "source_agent": "advisor",
      "symbols": ["NVDA"],
      "metadata": {
        "current_pct": 0.22,
        "max_pct": 0.15
      }
    }
  ],
  "reject_reasons": [],
  "digest": "Portfolio Advisory (1 recommendations): [MEDIUM] REDUCE NVDA ...",
  "raw": {
    "total_positions": 8,
    "recommendation_count": 1
  },
  "error_message": null
}
```

## Example `RiskFlag`

```json
{
  "code": "MACRO_REGIME_ALERT",
  "severity": "medium",
  "message": "Macro regime flagged as risk_watch.",
  "source_agent": "news",
  "symbols": [],
  "metadata": {}
}
```

## Example `RejectReason`

```json
{
  "symbol": "TSLA",
  "code": "IV_TOO_HIGH",
  "message": "IV percentile 91 exceeds max 80.",
  "source_agent": "screener",
  "metadata": {
    "iv_percentile": 91,
    "iv_percentile_max": 80
  }
}
```

## Example `agent_manifest.json`

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-19T10:17:00Z",
  "agents": [
    {
      "name": "news",
      "version": "0.1.0",
      "description": "News & macro intelligence: Citrini, Capital Flow, Conk, RSS",
      "role": "NewsMacroAnalyst",
      "capabilities": [
        "fetch_research_inputs",
        "classify_news_relevance",
        "build_macro_snapshot",
        "generate_news_digest"
      ],
      "inputs": {
        "positions": "list[PositionSnapshot] used to determine portfolio relevance",
        "config.sources": "list[str] of research/news sources to query"
      },
      "outputs": {
        "news_items": "list[NewsItem]",
        "macro_snapshot": "MacroSnapshot",
        "risk_flags": "list[RiskFlag]"
      },
      "guardrails": {
        "mode": "read_only",
        "external_sources_allowed": true,
        "can_trigger_downstream_actions": false,
        "can_mutate_broker_state": false,
        "failure_policy": "log errors, return partial output",
        "confidence_threshold_required": false
      }
    }
  ]
}
```

## Consumer Guidance

When integrating externally:
- treat these examples as shape references, not fixed payload templates
- rely on field names and semantic meaning, not list order
- tolerate additional keys in `raw` and `metadata`
- never assume recommendations imply permission to trade
