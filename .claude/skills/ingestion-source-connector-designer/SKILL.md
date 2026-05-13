---
name: ingestion-source-connector-designer
description: "Designs or reviews source connectors and ingestion boundaries for the trading platform. Use when adding Gmail, RSS, web, broker, market-data, or file-drop inputs, or when deciding what belongs in a connector versus the knowledge or analysis layers."
---

# Source Connector Designer

## What This Skill Does

Use this skill when the task is about designing or reviewing intake boundaries.

This skill is for:

- defining a new source connector boundary
- reviewing whether an existing input path is behaving like a true connector
- deciding what raw artifacts and minimal metadata a connector must preserve
- deciding what belongs in the connector versus later knowledge or analysis layers

This skill is not for:

- doing downstream PM interpretation
- turning connectors into naming centers for the whole architecture
- embedding ranking, theme advice, or synthesis logic into the intake layer

## Desired Result

The desired result is a stable connector contract that preserves raw inputs correctly and hands off cleanly into the `KnowledgeBase`.

By the time this skill is done, it should be explicit:

- what the connector boundary is
- what raw artifacts must be preserved
- what minimal metadata must be emitted immediately
- what should be deferred to later classification, retrieval, or synthesis
- how the connector hands off into the knowledge layer

Time contract:

- raw source / provider times should be preserved as precise UTC instants whenever they are persisted
- local ET/PT/business-date wording belongs downstream
- connector metadata may add derived labels, but must not replace the raw UTC fields

If the output still mixes connector work with downstream analysis ownership, this skill has failed.

## Core Principle

Connectors are boundary objects. They should:

- connect
- fetch
- save raw artifacts
- emit minimal metadata
- track sync status

They should not become the naming center for research, ranking, or PM advice.

## Completion Standard

This skill is complete only when all of the following are explicit:

- source type
- connector boundary
- canonical raw artifact path
- minimum metadata contract
- handoff target into `KnowledgeBase`
- deferred interpretation boundary

Accepted outputs:

- connector design decision
- connector review decision
- boundary correction recommendation when the current design is mixing layers

## Design Questions To Answer

At minimum, answer:

- What is the connector boundary?
- What raw artifacts are preserved?
- What metadata is required immediately?
- What can be deferred to later classification or synthesis?
- What should the connector explicitly refuse to own?

## Required Output Shape

At minimum, the result should say:

- `source_type`
- `connector_boundary`
- `raw_artifacts`
- `minimum_metadata`
- `knowledgebase_handoff`
- `deferred_interpretation`
- `boundary_risks`

Minimum metadata should explicitly say whether the connector emits:

- raw UTC timestamps
- provider-native time fields
- derived session/date labels if any
- which of those are canonical versus render-only

## Guardrails

- Avoid fallback-path loops.
- Avoid overloading the connector with downstream analysis.
- Keep the connector contract stable even if higher-level modules evolve.
- Route connector output into the `KnowledgeBase` before `AnalysisPlatform`.
- Do not normalize canonical stored timestamps into ET/PT-only values at the connector boundary.

## Example Triggers

- “add a Gmail connector”
- “design RSS ingestion”
- “should this live in research or connectors”
- “how should we save raw source material”
