# 06 Agent Manifest Schema

## Purpose

Define the compact schema for `data/agents/agent_manifest.json` so external AI routers can discover tools without reading code.

## File Contract

The orchestrator writes one manifest file:
- `data/agents/agent_manifest.json`

## Top-Level Shape

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-19T10:00:00Z",
  "agents": []
}
```

## Top-Level Fields

### `schema_version`
- type: `string`
- meaning: manifest schema version
- current value: `"1.0"`

### `generated_at`
- type: `string`
- format: ISO-8601 UTC timestamp
- meaning: when the manifest was exported

### `agents`
- type: `array[AgentManifest]`
- meaning: all registered AI-executable agents

## `AgentManifest` Shape

```json
{
  "name": "news",
  "version": "0.1.0",
  "description": "News & macro intelligence: Citrini, Capital Flow, Conk, RSS",
  "role": "NewsMacroAnalyst",
  "capabilities": ["fetch_research_inputs", "classify_news_relevance"],
  "inputs": {},
  "outputs": {},
  "guardrails": {}
}
```

## `AgentManifest` Fields

### `name`
- type: `string`
- meaning: stable machine-facing identifier
- examples: `news`, `advisor`, `screener`

### `version`
- type: `string`
- meaning: implementation version of the agent

### `description`
- type: `string`
- meaning: short human-readable summary

### `role`
- type: `string`
- meaning: conceptual AI role used by routers and planners
- examples: `NewsMacroAnalyst`, `PortfolioRiskAdvisor`, `TechnicalScreener`

### `capabilities`
- type: `array[string]`
- meaning: callable skill names exposed by the agent
- rule: these are the only functions a router should assume exist at the AI-contract level

### `inputs`
- type: `object`
- meaning: machine-readable description of expected inputs
- rule: keys should map to `AgentContext` fields or agent config keys

### `outputs`
- type: `object`
- meaning: machine-readable description of produced outputs

### `guardrails`
- type: `object`
- meaning: execution boundaries and safety declarations

## Guardrail Fields

Recommended keys:
- `mode`: usually `read_only`
- `external_sources_allowed`: `true` or `false`
- `can_trigger_downstream_actions`: `true` or `false`
- `can_mutate_broker_state`: `true` or `false`
- `failure_policy`: short string policy
- `confidence_threshold_required`: `true` or `false`

## Router Rules

A future AI router should:
1. load this manifest first
2. choose an agent by `role` and `capabilities`
3. inspect `guardrails` before invocation
4. refuse any action not declared in the manifest
5. treat manifest data as the source of truth for AI dispatch

## Validation Rules

- every registered agent must appear exactly once
- every manifest item must have non-empty `name`, `role`, and `capabilities`
- `capabilities` must be unique within an agent
- `generated_at` must be present on export
- manifest must be JSON-serializable
