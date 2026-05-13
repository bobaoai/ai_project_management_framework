# Scenario Report v0.1

## Status

Deprecated.

The standalone `scenario_report` module and CLI command were removed because they were adding a preset-shaped interpretation layer that did not fit the current workflow.

## Why It Was Removed

- the report introduced a fixed scenario schema too early
- it encouraged hardcoded basket logic instead of letting theme routing and research drive the analysis
- it duplicated responsibilities that already belong to:
  - `CurrentPriorityTree` for routing
  - `ThemeReport` / theme metadata for current macro framing
  - `AssetLogicCard` for asset memory
  - PM-facing analysis skills for the final diagnosis

## Current Workflow

Use this sequence instead:

1. refresh holdings with `python -m src.cli.tradectl positions update` when needed
2. inspect the saved book with `python -m src.cli.tradectl positions show`
3. inspect exposure with `python -m src.cli.tradectl exposure show`
4. route through `data/research/themes/current_priority_tree.json`
5. read the relevant theme metadata / report
6. combine that with `AssetLogicCard` context and produce PM-facing analysis directly

## Replacement Direction

If a future replacement is needed, it should be:

- theme-routed rather than preset-shaped
- derived from canonical routing and asset memory layers
- expressed as analysis support, not as a separate pseudo-risk engine
