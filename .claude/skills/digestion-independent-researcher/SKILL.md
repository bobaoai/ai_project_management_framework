---
name: digestion-independent-researcher
description: Orchestrates cross-asset independent research in the Digestion layer. Use when the user asks to research a company, stock, crypto project, or asset by assembling local and external sources, building an asset source packet, selecting a domain expert route, and producing a dossier, decision brief, package candidate, or blocked handoff.
---

# Digestion Independent Researcher

## What This Skill Does

Use this skill when the task is independent asset research and the needed information may not already exist in local email or documents.

This skill owns the Digestion orchestration loop:

```text
research question
  -> asset identity
  -> local archive search
  -> optional external search
  -> message archive link
  -> asset source packet
  -> domain route selection
  -> selected domain expert
  -> expert-owned digestion output
  -> downstream handoff
```

This skill does not generate generic Source Cards before routing. It selects the route first, then hands the source packet to the matching expert. The expert owns its Source Card, Typed Claim, and Expert Artifact schema.

## Desired Result

The desired result is an asset-level research state that can be audited and reused.

By the end, it should be explicit:

- what research question was asked;
- what asset identity and aliases were used;
- which local and external sources were considered;
- which canonical message archive objects hold the source bodies;
- which asset workspace was updated;
- which domain route was selected;
- which expert output was created or why the run blocked;
- what downstream handoff is allowed.

If the work only produces a polished report without source packet, route, expert output, or blocked-output boundary, this skill has failed.

## Primary Truth Surfaces

Read first:

- `designDoc/digestion_20_independent_researcher.md`
- `designDoc/digestion_00_overview.md`
- `designDoc/digestion_10_structure_contract.md`
- `.claude/skills/support-deep-research-survey/SKILL.md` when the run needs broad external research rather than one targeted public-source check
- `09_soul/skills/workflow_deep_research_survey.md` as the portable method source used by the local adapter

Then inspect:

- `data/research/messages_index.jsonl`
- `data/research/links_index.jsonl`
- existing `data/digestion/independent_research/assets/<asset_key>/` workspace when present
- relevant `data/research/messages/<research_id>/read_content.md`

Read domain docs when route selection points there:

- company family routing: `designDoc/digestion_41_company_expert.md`
- listed company: `designDoc/digestion_41_2_listed_company_expert.md`
- private company / pre-IPO issuer: `designDoc/digestion_41_1_private_company_expert.md`
- crypto: `designDoc/digestion_42_crypto_project_expert.md`
- expert creation or missing expert: `designDoc/digestion_30_expert_factory.md`
- single-stock downstream context: `.claude/skills/research-single-stock-analysis/SKILL.md`
- package sufficiency: `.claude/skills/writer-handoff/SKILL.md`

## Workspace Contract

Use this Digestion workspace:

```text
data/digestion/independent_research/assets/<asset_key>/
```

Expected files:

- `asset.json`
- `sources.jsonl`
- `source_packet.md`
- `source_packet.json`
- `domain_route.json`
- `run_log.jsonl`
- `expert_outputs/<subsystem_id>/...`
- optional `packages/package.md`
- optional `reports/report.md`

Raw source remains under:

```text
data/research/messages/<research_id>/
```

Do not make the asset workspace a second raw archive root.

## Route Before Source Card

Always select the domain route before asking for Source Cards or Typed Claims.

Default routes:

- listed company / public equity issuer: `company_expert:default_company_dossier` or future `listed_company_expert`
- private company / pre-IPO issuer: `private_company_expert:private_company_dossier`; compatibility route is `company_expert` with `template_id: private_company_dossier`
- crypto project: `crypto_project_expert`
- thesis or theme lifecycle: `thesis_theme_expert`
- missing route: `blocked_missing_expert`

Route rules:

- company research does not default to thesis/theme;
- private-company research must preserve unit of account, secondary-market signal type, liquidity / transfer constraints, and cannot-know boundaries;
- crypto research does not default to thesis/theme;
- thesis/theme is used only when the research question is explicitly about belief lifecycle, theme maintenance, or thesis candidate creation;
- future company templates change section and evidence requirements, not lifecycle authority.

## Tool Interfaces

Use explicit interfaces where available or keep the same operation names in the run log:

- `asset_identity_resolve`
- `local_archive_search`
- `external_search_plan`
- `external_search_perplexity`
- `external_search_deep_research`
- `archive_message_create`
- `message_index_rebuild`
- `asset_workspace_init`
- `asset_source_link`
- `asset_source_packet_build`
- `domain_route_select`
- `domain_expert_invoke`
- `package_candidate_build`
- `report_draft_write`
- `promotion_link_record`

External search returns source candidates, not final conclusions. Selected external sources must be archived as message objects before expert consumption.

Use `external_search_perplexity` for narrow public-source checks, event confirmation, and source discovery.

Use `external_search_deep_research` when the question needs the local Deep Research adapter from `.claude/skills/support-deep-research-survey/SKILL.md`: broad scan, overlapping dimensions, cross-checking, preserved URLs / quotes, and one final survey artifact. Good triggers include public-comp calibration, private-company secondary-market price-history ambiguity, and broad source-family discovery.

The adapter uses `09_soul/skills/workflow_deep_research_survey.md` as the method source, but overrides the portable default output location for Digestion runs.

The Deep Research artifact is still upstream source material. It must be archived under `data/research/messages/<research_id>/`, linked into the asset workspace, and consumed through the selected domain expert. It must not directly become a dossier, report, or portfolio recommendation.

## Allowed Outputs

Accepted terminal outputs:

- `blocked_missing_source`
- `blocked_missing_expert`
- `source_packet_ready`
- `expert_output_ready`
- `crypto_decision_brief`
- `single_asset_dossier`
- `private_company_dossier`
- `company_research_report`
- `package_candidate`
- `report_draft`
- `promoted_to_downstream`

For report drafts, mark the artifact as draft / public-info-only / not-portfolio-action when appropriate.

## Blocked Outputs

This skill must not directly produce:

- active thesis lifecycle state;
- verified evidence record;
- final theme report ownership;
- portfolio action;
- sizing;
- execution plan;
- order instructions.

It may hand off to the owning workflow when the expert output is ready.

## Completion Standard

A run is complete only when one of these is true:

- a domain expert output exists with source refs and blocked outputs;
- a source packet is ready and waiting for expert invocation;
- the run is blocked with a concrete missing source, missing expert, or insufficient public data reason;
- a package/report draft exists with explicit source and authority boundaries.

Minimum handoff summary:

```yaml
asset_key: <asset>
research_question: <question>
workspace: <path>
sources_linked: <count>
selected_route: <route>
expert_output: <path or none>
handoff_status: <status>
blocked_outputs: []
next_step: <specific next step>
```

## Failure Signals

Treat these as failures:

- Source Card is generated before route selection.
- External web result is cited without a message archive object.
- Deep Research output is saved only under `09_soul/contexts/survey_sessions/` for an asset research run.
- Deep Research output is used directly in a dossier without first becoming an archived message and source-packet input.
- Asset workspace stores canonical raw source.
- Company research is forced through thesis/theme.
- Private-company secondary-market pricing is treated as business-quality proof or public ticker recommendation.
- Crypto research is forced through thesis/theme instead of Crypto Project Expert.
- Report prose hides public / proxy / cannot-know boundaries.
- The skill writes portfolio action language before handoff to `operation-portfolio-decision`.
- Missing expert is covered by generic prose instead of `blocked_missing_expert`.
