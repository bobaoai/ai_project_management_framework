# 04 Output Contracts

## Shared Types

### `Recommendation`
Use for manual adjustment ideas.

Required fields:
- `action`
- `symbol`
- `rationale`
- `urgency`
- `source_agent`

Optional fields:
- `confidence`
- `suggested_qty`
- `suggested_price`
- `delta_impact`
- `metadata`

### `Signal`
Use for ranked technical opportunities.

Required fields:
- `symbol`
- `signal_type`
- `score`
- `timeframe`

Optional fields:
- `direction`
- `details`

### `RiskFlag`
Use for structured warnings.

Required fields:
- `code`
- `severity`
- `message`
- `source_agent`

Optional fields:
- `symbols`
- `metadata`

### `RejectReason`
Use when a screener or filter excludes a symbol.

Required fields:
- `symbol`
- `code`
- `message`
- `source_agent`

Optional fields:
- `metadata`

## `AgentOutput`

Every run returns:
- `agent_name`
- `run_at`
- `status`
- `recommendations`
- `signals`
- `risk_flags`
- `reject_reasons`
- `digest`
- `raw`
- `error_message`

## JSON Rules

- must be JSON-serializable
- timestamps should be ISO-8601 strings when persisted
- nested raw payloads must stay machine-readable
- avoid large duplicated narrative blobs in `raw`
