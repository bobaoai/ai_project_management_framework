---
name: routing-current-macro-priority-router
description: "Acts as a thin macro/theme midstream chooser after task mode is already identified. Use when a request already belongs to the macro/theme path and the system still needs to decide which theme or macro mainline should lead, or when another mainline needs a `theme overlay` without giving up first authority."
---

# Current Macro Priority Router

## What This Skill Does

Use this skill to decide which current macro theme and macro-side workflow should drive the next step.

This skill is a thin midstream router, not the top-level task classifier and not the final analysis layer.

It should be used only after the request has already been understood as `macro/theme-oriented`.

It exists to route *inside* the macro path, not to act as the universal front door for all analysis requests.

When `routing-task-mode-router` is available, that top-level router should decide entry first and only then call this skill for macro-path internal branching or overlay help.

## Desired Result

The desired result is a clear macro-path routing choice, not a full analysis artifact.

By the time this skill is done, it should be explicit:

- which theme or macro mainline leads
- why that branch wins
- whether the task should go to `research-current-market-reporter`
- whether the task should go to `research-theme-report-owner`
- or whether another mainline should merely receive macro `theme overlay` context

## Completion Standard

This skill is complete only when all of the following are explicit:

- `matched_theme`
- `matched_subtheme` when relevant
- `time_horizon`
- `macro_route_result`
- `why_this_branch_wins`

Where `macro_route_result` should usually be one of:

- `route_to_current_market_reporter`
- `route_to_theme_report_owner`
- `return_theme_overlay_only`

If the result still leaves top-level ownership ambiguous, this skill is not done.

## Canonical Source

Read these files first:

- `data/research/themes/index.json`
- `data/research/themes/current_priority_tree.json`

Treat them as generated views, not hand-maintained sources.

Do not guess the current priority stack from chat memory when these files exist.

## Primary Inputs

Read these first:

- the user's request
- explicitly named theme, subtheme, asset cluster, or risk lens when present
- `data/research/themes/index.json`
- `data/research/themes/current_priority_tree.json`
- `data/research/themes/reports/<theme_id>.md` once the likely theme is identified

Use `index.json` as the lightweight directory view.
Use `current_priority_tree.json` as the current ranking and fallback chooser.

## Routing Rules

### Mainline Priority

- `user-specified mainline` wins over `current_priority_tree`.
- Use the tree as the fallback chooser only when the user did not clearly specify what should drive the observation.
- When the user names a theme, asset, event line, or observation frame, do not silently override it just because another branch ranks higher in the tree.
- When the user does not specify the mainline, the tree should decide which theme drives the first-pass analysis.
- If the user-specified mainline conflicts with the tree, keep the user's mainline but note the tree-based context in downstream analysis when useful.

### Task-Mode Boundary

- This skill does not decide the top-level `task mode`.
- It assumes the request already belongs to a `macro/theme` path.
- It may still be used as a `theme overlay` helper for another task, but in that case the other task keeps first authority.
- Example: a `single-stock monitor` request may borrow one theme as overlay context, but the request still belongs to the stock-monitor path rather than this router.

### When the request is about structural opportunity ranking

Prefer the relevant `medium_term_theme`.

Typical triggers:

- structural theme ranking
- medium-term setup
- 未来几个季度看什么
- where optionality is underpriced

### When the request spans multiple themes

- start with the highest-ranked short-term theme if the question is portfolio-defense oriented
- start with the relevant medium-term theme if the question is opportunity-ranking oriented
- if both matter, say so explicitly and separate `defense now` from `build for later`

If the first authority still belongs to another mainline such as `operation-portfolio-decision`, return the winning theme as overlay context rather than pretending this skill now owns the full downstream task.

### When the request is to write a market observation

- if the user wants a `snapshot`, `intraday note`, `post-close note`, or `market observation`, route to `research-current-market-reporter`
- keep the chosen theme as the observation mainline and use the tree only if the user did not specify that mainline
- do not route these requests to `research-theme-report-owner` unless the user is actually asking to rewrite the full theme report

### When the request is to update themes

Split update requests by intent:

- if the user wants to rerank, reprioritize, or refresh the tree, route to `research-theme-priority-updater`
- if the user wants to refresh theme report logic, subthemes, thesis links, or evidence, route to `research-theme-report-owner`
- if the user wants both, run `research-theme-report-owner` first and `research-theme-priority-updater` second

### When another mainline only needs macro overlay

- if `research-single-stock-analysis` needs a theme overlay, return the leading theme and why it matters, but keep ticker-first authority downstream
- if `operation-portfolio-decision` needs macro context, return the leading theme and why it matters for the current book, but keep portfolio-manager-first authority downstream
- do not turn overlay help into hidden ownership transfer

## Required Output Shape

At minimum, state:

- `matched_macro_path_assumption`
- `matched_theme`
- `matched_subtheme` if any
- `time_horizon`
- `macro_route_result`
- `why_this_branch_wins`

Then let the owning downstream mainline continue.

## Guardrails

- Do not skip the priority tree when the user is asking “what matters now”.
- Do not use the priority tree to override an explicitly requested observation mainline.
- Do not collapse short-term risk routing and medium-term opportunity routing into one vague answer.
- Do not replace downstream skills; this skill only selects and frames them.
- Do not use this skill as the universal first router for non-theme tasks.
- Do not let PM-style prompts such as `调仓建议` or `先 hedge 什么` silently become macro-owned tasks when they should keep `operation-portfolio-decision` as first authority.

## Failure Signals

Treat these as signs this skill failed:

- it silently behaves like a top-level router
- it chooses a theme but never states whether the result is observer, owner, or overlay-only
- it steals first authority from `research-single-stock-analysis` or `operation-portfolio-decision`
- it uses the priority tree to override a clearly user-specified mainline
- it returns broad macro commentary instead of a routing result

## Example Triggers

- “在 macro path 里现在最该先看什么”
- “short term highest priority 是什么（宏观层）”
- “which macro theme should drive the next observation”
- “给单票分析一个 theme overlay”
- “给当前 portfolio debate 一个 macro overlay”
