# 02 Protocol Stack

## Protocol 1: Discovery

### Purpose
Allow a router to discover what tools exist before invocation.

### Mechanism
- orchestrator exports `data/agents/agent_manifest.json`
- each agent declares role, capabilities, inputs, outputs, and guardrails

### Rule
A router must inspect the manifest before dynamic dispatch.

## Protocol 2: Context Build

### Purpose
Create a shared read-only state for a single AI cycle.

### Context Fields
- `positions`
- `exposure`
- `price_cache`
- `history_db_path`
- `hist_dir`
- `analytics_results`
- `config`
- `run_date`

### Rule
Agents treat context as immutable during one run.

## Protocol 3: Capability Invocation

### Purpose
Keep execution decomposed into explicit stages.

### Rule
Every agent exposes named capabilities and a top-level `run(ctx)` wrapper.

### Expected Pattern
- gather inputs
- normalize
- score or analyze
- validate outputs
- synthesize digest

## Protocol 4: Output Validation

### Rule
Every agent run must return `AgentOutput` and only structured payloads.

### Required Output Channels
- `recommendations`
- `signals`
- `risk_flags`
- `reject_reasons`
- `digest`
- `raw`

## Protocol 5: Persistence

### Rule
Only the orchestrator writes final result files.

### Standard Files
- `data/agents/news_result.json`
- `data/agents/advisor_result.json`
- `data/agents/screener_result.json`
- `data/agents/agent_manifest.json`

## Protocol 6: Human Review

### Rule
No recommendation may cross into order execution automatically.

### Human Review Boundary
All outputs are advisory only until manually reviewed outside the AI layer.
