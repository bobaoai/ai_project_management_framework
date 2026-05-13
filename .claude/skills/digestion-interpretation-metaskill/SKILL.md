---
name: digestion-interpretation-metaskill
description: Extracts reusable analytical assets from archived reports, messages, image reviews, evidence units, or repeated local analysis and routes them into Digestion Expert Factory review. Use when a source may contain a reusable method, metric, signal, pattern, failure mode, industry-specific leading indicator, stock-selection lens, or expert/template candidate.
---

# Interpretation MetaSkill

## What This Skill Does

Use this skill when a source may teach the system a reusable way to analyze an industry, asset class, market mechanism, behavioral pattern, or signal surface.

This skill is the extraction substep of the Digestion Expert Factory:

```text
report / message / chart / repeated local analysis
  -> digestion-interpretation-metaskill prompt
  -> Claude Code CLI extraction run
  -> reusable analytical asset candidate
  -> digestion-expert-factory
  -> Domain Expert contract / template / reject / defer
```

The source does not need to follow any local framework.

The task is to mine reusable analytical assets from the source when they exist.

## Current Role

- `Current persona`: MetaSkill analyst inside the Digestion Expert Factory
- `Current task`: manage the extraction prompt, run Claude Code CLI, and route reusable analytical assets to Expert Factory review
- `Primary truth surface`: archive source files plus reviewed derived surfaces
- `Output artifact`: `analysis_asset_candidate` / `expert_factory_handoff`
- `Reader end-state`: the Expert Factory can decide whether to absorb, reject, defer, or create/update an expert without rereading the entire source

## Execution Surface

This skill runs through Claude Code CLI.

Canonical prompt:

```text
.claude/skills/digestion-interpretation-metaskill/claude_prompt.md
```

Invocation pattern:

```bash
/Users/bokanbao/.local/bin/claude -p "$(cat .claude/skills/digestion-interpretation-metaskill/claude_prompt.md)"
```

When source-specific context is needed, create a temporary prompt file that appends the source bundle paths and target output paths after the canonical prompt. Then call Claude CLI on that assembled prompt.

Do not substitute Cursor Subagent for this execution surface.

The Cursor agent may prepare the prompt file and inspect outputs. The Claude CLI run is the extraction agent.

## Primary Truth Surfaces

Read in this order:

1. `designDoc/digestion_30_expert_factory.md` for expert admission and firewall rules.
2. `designDoc/digestion_10_structure_contract.md` for Source Card / Typed Claim / Expert Artifact shape.
3. `designDoc/digestion_00_overview.md` for the Digestion boundary.
4. `read_content.md` as the canonical source read surface. Stop if its `upstream_blockers[]` are non-empty.
5. `message.json` for metadata, source collection, timestamps, attachment inventory, and provenance. Do not use embedded body fields as a second content body when `read_content.md` exists.
6. `agent_evidence.json` as the AI-derived claim index when reusable claim clusters or candidate tasks are needed.
7. Reviewed rows from `image_reviews.jsonl` only when `read_content.md` authorizes audit or image evidence needs provenance repair.

Conditional surfaces:

- Use `content_selection.json` only for content-mode audit, preferred variant, image-review state, or degradation flags.
- Use `content.md` / `content.txt` only for legacy audit when `read_content.md` is missing or blocked.
- Use `page_texts.jsonl` only for page-level attribution or OCR audit.
- Use legacy `text_read.json` / `evidence_units.jsonl` only when `agent_evidence.json` is absent and the task is explicitly archive repair.

## Admission Question

Ask one question first:

```text
Does this source teach a reusable analytical asset, or does it only contain one-off facts?
```

Reusable analytical assets include:

- method
- metric
- signal
- pattern
- failure mode
- industry-specific leading indicator
- stock-selection lens
- evidence collection question

Non-admission cases:

- ordinary report summary
- single price move
- position update
- one chart without reusable method
- one fact that only changes one belief
- PM opinion without reusable method

Non-admission sources stay in archive / evidence units / snapshot / PM note layers.

## Output Types

Allowed outputs:

- `analysis_asset_candidate`
- `metric_candidate`
- `signal_candidate`
- `pattern_candidate`
- `framework_rule_candidate`
- `failure_mode_candidate`
- `domain_expert_handoff`

Blocked outputs:

- `evidence_record`
- `thesis_note`
- `scenario_note`
- `portfolio_action`
- `PM Approved`
- `ai_verified=true`

## Candidate Object Shape

Write candidate artifacts under:

```text
data/digestion/expert_subsystems/_candidates/
```

Use one JSON file and, when useful, one Markdown file:

```text
data/digestion/expert_subsystems/_candidates/<source_id>.<candidate_id>.json
data/digestion/expert_subsystems/_candidates/<source_id>.<candidate_id>.md
```

Minimum JSON fields:

- `candidate_id`
- `source_research_id`
- `source_class`
- `asset_type`
- `asset_summary`
- `proposed_expert_id`
- `input_signals`
- `how_it_may_help`
- `cannot_do`
- `downstream_allowed_outputs`
- `downstream_blocked_outputs`
- `evidence_needed_before_thesis`
- `failure_modes`
- `confidence`
- `status`
- `recorded_at_utc`

## Prompt Assembly Contract

Every Claude CLI run must receive:

- the canonical prompt text
- `source_research_id`
- source bundle paths actually available
- target output directory
- candidate output schema
- Domain Expert routing options
- blocked outputs

The run prompt must include the communication and writing constraints needed for this task:

- direct, source-grounded, no generic praise
- no PM-facing recommendation language
- no thesis prose
- no evidence verdict
- no portfolio action language
- explicit `no_reusable_asset_found` when the source lacks reusable analytical assets

Store ad hoc assembled prompts under:

```text
data/digestion/expert_subsystems/_prompts/
```

These prompts are execution artifacts. The canonical reusable prompt remains in this skill directory.

## Expert Factory Routing

Route by the reusable asset, not by the report title.

Examples:

- consumer brand heat, social commerce, beauty, apparel, luxury, consumer AI trust decay -> `consumer_demand_sensing_expert`
- Fed communication surface, policy reaction function, rate transmission -> Fed / macro domain expert
- chart-stage or technical setup method -> technical analysis expert
- AI datacenter power, grid bottlenecks, electrical supply chain -> AI power / infrastructure domain expert

If no existing Domain Expert fits, emit:

```text
domain_expert_id: unresolved
status: needs_domain_expert_admission
```

Do not create a new Domain Expert just because the source is interesting.

## Expert Factory Handoff

After extracting one or more reusable analytical assets, this skill must hand off to `digestion-expert-factory`.

The Expert Factory owns the absorb / create / reject / defer decision. Existing Domain Experts may be consulted by that factory path.

The MetaSkill handoff should include:

- `source_research_id`
- `candidate_asset_type`
- `asset_summary`
- `why_it_may_help`
- `proposed_domain_expert_id`
- `evidence_needed_before_thesis`
- `downstream_allowed_outputs`
- `downstream_blocked_outputs`
- source paths read

The handoff must ask the Expert Factory to return one of:

- `absorb_into_existing_toolkit`
- `create_new_expert`
- `create_or_update_company_template`
- `update_crypto_project_expert`
- `defer_pending_validation`
- `reject_as_not_reusable`
- `route_to_different_domain_expert`

The handoff must also ask for:

- updated or proposed expert-tool fields when absorbed
- validation tasks when deferred
- reason and destination when routed elsewhere
- explicit boundary note when the asset should not produce thesis / evidence / portfolio output

MetaSkill should not decide absorption locally.

Detection boundary:

- if the MetaSkill output says an asset has been absorbed into a Domain Expert without an Expert Factory verdict, the loop is incomplete
- if the MetaSkill writes validation tasks directly when Expert Factory should decide whether the asset belongs, the loop is bypassing the expert
- if the MetaSkill writes thesis candidates after extraction without an Expert Factory verdict, it has skipped the middle layer

## Quality Bar

An extracted asset is high quality only if it:

- improves future interpretation across more than one artifact
- names what signal to inspect
- names how that signal changes interpretation
- names at least one failure mode
- states what evidence is needed before thesis use
- states what it cannot prove

If the source sounds smart but does not meet that bar, return `no_reusable_asset_found` with a short reason.

## Boundary With Domain Expert

MetaSkill extracts.

Domain Expert decides whether to absorb.

Correct:

```text
MetaSkill extracts "conversion proxy ladder" from a consumer report.
Domain Expert decides whether it belongs in the consumer demand sensing toolkit.
Domain Expert generates candidate thesis questions and evidence tasks.
Thesis Drafter writes formal thesis only after receiving a prepared candidate package.
```

Incorrect:

```text
MetaSkill reads a consumer report.
MetaSkill writes a thesis about APR.
```

## Detection Boundaries

Violations are observable:

- the output writes `claims[]`, `probability_view`, or thesis prose
- the output creates an `evidence_record`
- the output says a source proves a ticker thesis
- the output treats a report title as a Domain Expert identity
- the output promotes a source-specific framework name as the system's expert name
- the output routes a position update as a framework update

When these appear, stop and repair the Digestion expert boundary before downstream use.

## Example: Consumer Report

From a report such as The Girlfriend Index, extract reusable assets like:

- `brand_heat_signal`
- `loyalist_density`
- `conversion_proxy_ladder`
- `taste_judgment_requires_corroboration`
- `online_validation_to_retail_validation_path`
- `consumer_ai_slop_trust_decay_signal`

Route them to `consumer_demand_sensing_expert`.

Do not make The Girlfriend Index the expert identity.

Do not write a thesis.
