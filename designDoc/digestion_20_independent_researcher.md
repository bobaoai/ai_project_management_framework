---
title: Independent Research Orchestrator
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Analysis Platform Builder
---

# Independent Research Orchestrator

## 1. Purpose

`Independent Research Orchestrator` is a Digestion-layer workflow owner for cross-asset research.

It is used when the system needs to research an asset, company, crypto project, theme-adjacent object, or future domain object without relying only on already-ingested email or local documents.

It can search local archive state, request external search, create source packets, maintain an asset-level workbench, select a domain expert route, and hand the source packet to the right expert subsystem.

It does not generate generic Source Cards before routing. The domain expert creates the Source Card, Typed Claim, and Expert Brief according to its own schema.

Canonical shape:

```text
research request
  -> asset identity / research question
  -> local archive search
  -> optional external search
  -> canonical message archive
  -> asset source packet
  -> domain route selection
  -> domain expert
  -> expert-owned Source Card / Typed Claim / Expert Artifact
  -> package / dossier / decision brief / downstream promotion
```

## 2. Layer Boundary

### 2.1 Ingestion Boundary

Raw source artifacts stay in the canonical message archive:

```text
data/research/messages/<research_id>/
```

The orchestrator can request or call tools that create message archive objects, but the source does not become canonical inside the asset workspace. The asset workspace stores links, route decisions, source packets, and derived digestion outputs.

Correct:

```text
external web source
  -> data/research/messages/<research_id>/raw_payload.json
  -> data/research/messages/<research_id>/read_content.md
  -> data/digestion/independent_research/assets/<asset_key>/sources.jsonl
```

Incorrect:

```text
external web source
  -> data/digestion/independent_research/assets/<asset_key>/raw/
  -> downstream package reads raw files directly
```

The incorrect form creates a second archive root and bypasses `read_content.md`.

### 2.2 Digestion Boundary

The orchestrator belongs to Digestion because it operates after canonical source readability and before thesis, theme, single-stock, crypto decision, or portfolio judgment.

It owns:

- asset identity resolution;
- local source discovery;
- external source request planning;
- archive linking;
- asset-level source packet assembly;
- domain route selection;
- expert invocation package;
- handoff status and run logs.

It does not own:

- raw connector design;
- canonical source body selection;
- final thesis lifecycle;
- final theme report ownership;
- portfolio action;
- order execution.

### 2.3 Expert Boundary

The orchestrator does not create generic digestion objects before knowing the domain.

The domain expert owns its object vocabulary:

- Listed Company Expert creates listed-company Source Cards, listed-company typed claims, and `single_asset_dossier`.
- Private Company Expert creates private-company Source Cards, private-company typed claims, and `private_company_dossier`.
- Crypto Project Expert creates `CryptoSourceCard`, `CryptoClaim`, `DualTrackRead`, and `CryptoDecisionBrief`.
- Theme / Thesis Expert creates theme-specific Source Cards, typed claims, and candidate packets only when a thesis or theme route is actually selected.

This keeps source understanding inside the expert that knows the allowed `source_class`, `claim_type`, confidence caps, and blocked outputs.

## 3. Reader End-State

After reading an independent research run, the downstream analyst should know:

- what question was asked;
- which asset identity was used;
- which local and external sources were considered;
- which message archive objects hold the canonical source bodies;
- which domain route was selected and why;
- which expert generated the Source Cards, Typed Claims, and Expert Artifact;
- which conclusions are supported, proxy-only, unknown, or blocked;
- whether the output can become a company dossier, crypto decision brief, thesis candidate, package candidate, report draft, or blocked result.

Silent violation:

```text
The report looks complete, but no one can tell which source packet was routed to which expert or whether the expert was allowed to emit that conclusion.
```

That means the workflow produced prose, not a digestion-backed research object.

## 4. Asset Workspace

Canonical workspace root:

```text
data/digestion/independent_research/assets/<asset_key>/
```

`asset_key` is a stable snake_case identifier. It should preserve domain where useful:

- `listed_aapl`
- `listed_elf`
- `private_databricks`
- `crypto_humanity_protocol_h`
- `future_es`

Recommended directory shape:

```text
data/digestion/independent_research/
  index.jsonl
  assets/
    <asset_key>/
      asset.json
      sources.jsonl
      source_packet.md
      source_packet.json
      domain_route.json
      run_log.jsonl
      expert_outputs/
        <subsystem_id>/
          source_cards/
          claims/
          artifacts/
      packages/
        package.md
      reports/
        report.md
```

Files under `expert_outputs/` become durable digestion assets only after registry rows and edges exist. Draft files may exist during dogfood, but must carry `status: draft` and must not be consumed as canonical digestion objects.

## 5. Workspace File Contracts

### 5.1 `asset.json`

Minimum fields:

```yaml
asset_key: <stable id>
asset_type: listed_equity | private_company | crypto_project | future | etf | theme_object | other
display_name: <human name>
primary_symbol: <ticker / token / contract>
aliases: []
canonical_refs:
  technical_profile: <optional path>
  company_profile: <optional path>
  crypto_project_profile: <optional path>
created_at_utc: <ISO-8601>
updated_at_utc: <ISO-8601>
status: active | draft | deprecated
```

Private-company runtime support:

- use `private_company` as a first-class `asset_type`;
- keep `private_company` parallel to `listed_equity`, because both describe issuer status;
- keep SPV, tender, secondary transfer, fund interest, or indirect exposure under `template_id`, `instrument_type`, or unit-of-account fields, not as separate `asset_type` values.

### 5.2 `sources.jsonl`

One row per linked source:

```json
{
  "asset_key": "<asset_key>",
  "research_id": "<research_id>",
  "relative_read_content_path": "messages/<research_id>/read_content.md",
  "link_role": "primary_source | market_context | official_disclosure | counter_evidence | background",
  "source_collection": "<source_collection>",
  "readiness_status": "ready | ready_with_warnings | blocked | unknown",
  "added_at_utc": "<ISO-8601>",
  "added_by": "agent | human | builder",
  "notes": ""
}
```

Rules:

- every row must resolve through `data/research/messages_index.jsonl`;
- every source used for expert generation must have a usable `read_content.md`;
- blocked sources may be linked, but the route must explain why they are excluded or what blocks use.

### 5.3 `source_packet.md` / `source_packet.json`

The source packet is the orchestrator's handoff to a domain expert.

It includes:

- research question;
- asset identity;
- source inventory;
- selected source roles;
- freshness and readiness;
- known blockers;
- user-provided constraints;
- requested expert route;
- forbidden downstream outputs.

It does not contain final expert conclusions.

### 5.4 `domain_route.json`

Minimum fields:

```yaml
asset_key: <asset_key>
research_question: <question>
selected_route: company_expert | listed_company_expert | private_company_expert | crypto_project_expert | thesis_theme_expert | custom_expert
selected_subsystem_id: <subsystem_id>
template_id: <optional template id>
route_reason: <why this expert owns the read>
non_default_routes_rejected: []
allowed_outputs: []
blocked_outputs: []
created_at_utc: <ISO-8601>
```

Runtime state:

- `private_company_expert` is a first-class route for `private_company` assets;
- `listed_company_expert` is accepted as an explicit route, while listed-company default compatibility still uses `selected_route: company_expert` with `template_id: default_company_dossier`;
- compatibility packets may still use `selected_route: company_expert` with `template_id: private_company_dossier`;
- route logs should preserve whether a run used the compatibility route or the first-class child-expert route.

Rules:

- crypto does not default to thesis/theme;
- single-company research does not default to thesis/theme;
- thesis/theme is selected only when the research question is explicitly about belief lifecycle, theme maintenance, or thesis candidate creation;
- future company templates should be represented as `template_id`, not as a new top-level route unless they change authority.

Listed-company research is defined in `designDoc/digestion_41_2_listed_company_expert.md`. Runtime may use `selected_route: company_expert` with `template_id: default_company_dossier` for compatibility or explicit `selected_route: listed_company_expert` when the caller wants the child route named directly.

Private-company research is defined in `designDoc/digestion_41_1_private_company_expert.md`. Runtime should use `selected_route: private_company_expert` with `template_id: private_company_dossier`; `company_expert + private_company_dossier` remains a compatibility surface for older packets.

### 5.5 `run_log.jsonl`

Every run logs:

- `run_id`;
- `operation`;
- `tool_interface`;
- `inputs`;
- `outputs`;
- `status`;
- `started_at_utc`;
- `completed_at_utc`;
- source counts;
- selected route;
- blockers.

External AI/tool calls should additionally record prompt/template hashes according to `bestpractice_external_agent_builder.md` when applicable.

## 6. Tool Interface

The orchestrator should call explicit interfaces rather than inventing ad hoc steps.

Initial interface set:

```text
asset_identity_resolve
local_archive_search
external_search_plan
external_search_perplexity
external_search_deep_research
archive_message_create
message_index_rebuild
asset_workspace_init
asset_source_link
asset_source_packet_build
domain_route_select
domain_expert_invoke
package_candidate_build
report_draft_write
promotion_link_record
```

Current v0 CLI surface:

```bash
./.venv/bin/python -m src.cli.tradectl digestion independent-research init \
  --asset-key <asset_key> \
  --asset-type <asset_type> \
  --display-name <name> \
  --primary-symbol <symbol>

./.venv/bin/python -m src.cli.tradectl digestion independent-research link \
  --asset-key <asset_key> \
  --research-id <research_id> \
  --link-role <role>

./.venv/bin/python -m src.cli.tradectl digestion independent-research build-source-packet \
  --asset-key <asset_key> \
  --research-question "<question>"

./.venv/bin/python -m src.cli.tradectl digestion independent-research status [--asset-key <asset_key>]

./.venv/bin/python -m src.cli.tradectl digestion independent-research rebuild-index
```

`build-read-content` is a v0 compatibility alias for `build-source-packet`; the generated file is still a source packet, not a canonical message `read_content.md`.

### 6.1 `local_archive_search`

Searches:

- `data/research/messages_index.jsonl`;
- `data/research/links_index.jsonl`;
- existing digestion indexes;
- existing asset workspace sources;
- thesis/theme/snapshot indexes only when the route requires downstream context.

### 6.2 `external_search_perplexity`

Used when local archive is insufficient or the user asks for independent public research.

It must return source candidates, not final conclusions. Each selected external source must become a message archive object before expert consumption.

### 6.3 `external_search_deep_research`

Used when the research gap is broad enough that one search query or one Perplexity pass would create false confidence.

The host-local adapter is:

```text
.cursor/skills/support-deep-research-survey/SKILL.md
```

The adapter uses this portable method source:

```text
09_soul/skills/workflow_deep_research_survey.md
```

Use this path for multi-source calibration questions such as:

- public-comp calibration across more than one company;
- private-company secondary-market price history where signal type matters;
- cross-source disagreement between issuer disclosure, platform pricing, third-party private research, and public comps;
- external workflow / method research that must become source candidates before an expert consumes it.

The Deep Research output inside independent research is not a final PM conclusion. It should produce one durable survey or source-candidate artifact, then enter the normal archive path:

```text
external_search_deep_research
  -> support-deep-research-survey
  -> deep_research_source_candidates
  -> archive_message_create
  -> asset_source_link
  -> asset_source_packet_build
  -> domain_expert_invoke
```

Rules:

- use overlapping research dimensions so different passes can contradict or corroborate each other;
- preserve URLs and direct quotes for important claims;
- explicitly mark disagreements and cannot-know fields;
- archive the final Deep Research artifact as a message before any expert uses it;
- treat `data/research/messages/<research_id>/` as the canonical storage surface for Digestion Deep Research output;
- do not let the Deep Research artifact bypass the selected domain expert or become a direct dossier / report.
- do not store an asset-research Deep Research survey only under `09_soul/contexts/survey_sessions/`.

### 6.4 `archive_message_create`

Creates or requests creation of:

- `message.json`;
- raw payload / raw artifact;
- `content_selection.json`;
- `read_content.md`;
- source links.

This interface must preserve the message archive contract. It must not write only to the asset workspace.

### 6.5 `domain_route_select`

Selects the expert before Source Card generation.

Route examples:

```text
crypto project -> crypto_project_expert
listed company -> company_expert or company_template:<template_id>
private company / pre-IPO issuer -> planned_runtime private_company_expert, near-term company_expert + template_id:private_company_dossier
macro theme -> theme_expert
thesis candidate -> thesis_theme_expert
```

### 6.6 `domain_expert_invoke`

Passes the source packet to the selected expert.

The expert produces:

- Source Cards;
- Typed Claims;
- Framework Routes where relevant;
- Expert Artifact / Dossier / Decision Brief;
- allowed downstream handoff.

## 7. Domain Routes

### 7.1 Listed Company Route

Default route:

```text
company_expert:default_company_dossier
```

Governing family and child contracts:

```text
digestion_41_company_expert.md
digestion_41_2_listed_company_expert.md
```

Expected output:

- listed-company Source Cards;
- listed-company typed claims;
- `single_asset_dossier`;
- optional `company_research_report`;
- handoff to `research-single-stock-analysis` or `operation-portfolio-decision` only when requested.

The company route should answer:

- business model quality;
- financial and operating metrics;
- competitive position;
- product / customer / channel evidence;
- valuation framing;
- catalysts;
- risks;
- evidence gaps;
- confidence caps.

It should not write a thesis note unless the user explicitly asks for thesis promotion.

Future company templates:

```text
company_template:<template_id>
```

Templates can change section contract, metric priority, source requirements, report shape, and confidence caps. They do not change lifecycle authority.

### 7.2 Private Company Route

Route state:

```text
default_runtime: private_company_expert
compatibility: company_expert + template_id:private_company_dossier
```

Governing expert contract:

```text
digestion_41_1_private_company_expert.md
```

Expected output:

- private-company Source Cards;
- private-company typed claims;
- `private_company_dossier`;
- downstream handoff only when the dossier clearly separates operating-company value, security price, unit of account, public-comp calibration, and cannot-know fields.

The private company route should answer:

- what exact issuer / exposure is being researched;
- what unit of account is being priced;
- whether the source is issuer disclosure, primary round, secondary market, fund mark, public comp, or third-party private research;
- which claims are publicly observable, proxy-inferable, or not knowable from public data;
- how public comps and private pricing surfaces calibrate the read.

The route must not turn a secondary-market surface into business-quality proof or portfolio action.

### 7.3 Crypto Route

Default route:

```text
crypto_project_expert
```

Expected output follows `digestion_42_crypto_project_expert.md`:

```text
CryptoSourceCard
  -> CryptoClaim
  -> DualTrackRead
  -> CryptoDecisionBrief
```

The crypto route must preserve:

- Evidence Permission Layer;
- Survival / Fundamental Track;
- Reflexive Market Track;
- Decision Layer;
- project-type module;
- public / proxy / cannot-know boundaries.

It should not default to thesis/theme.

### 7.4 Thesis / Theme Route

This route is selected only when the research request is about thesis or theme lifecycle.

Expected output:

- theme/thesis Source Cards;
- typed claims;
- candidate thesis questions;
- candidate scenario questions;
- `thesis_candidate_packet`;
- promotion links.

The route does not activate thesis lifecycle. It hands off to the thesis cluster.

### 7.5 Custom Expert Route

Custom experts are created through the Expert Factory, not ad hoc inside a research run.

If no suitable expert exists:

```text
status: blocked
blocker: missing_expert_subsystem
recommended_next_step: create or update expert through digestion expert factory
```

## 8. Output States

Allowed terminal states:

- `blocked_missing_source`;
- `blocked_missing_expert`;
- `source_packet_ready`;
- `expert_output_ready`;
- `package_candidate_ready`;
- `report_draft_ready`;
- `promoted_to_downstream`;

Blocked states are valid outputs. The orchestrator should stop rather than forcing a report when the route, source packet, or expert schema is missing.

## 9. Handoff Contract

### 9.1 To Expert Factory

Use when the run discovers a repeatable method, metric, signal, or template need that no current expert owns.

Handoff payload:

- source packet;
- reusable asset candidate;
- proposed domain;
- expected source card pattern;
- blocked downstream outputs;
- why existing experts are insufficient.

### 9.2 To Thesis Cluster

Use only after a thesis/theme expert emits a candidate packet.

The packet must include:

- candidate mechanism;
- dependencies;
- falsifiers;
- source refs;
- evidence gaps;
- blocked assumptions.

### 9.3 To Single-Stock / Portfolio

Company route outputs may be consumed by downstream analyst or portfolio workflows, but only as context or package input. Position action and sizing remain outside the orchestrator.

The company path is intentionally two-step:

```text
Digestion
  Independent Research Orchestrator -> Listed Company Expert -> single_asset_dossier

PM-facing analyst
  research-single-stock-analysis -> PM-facing report / portfolio handoff

Digestion
  Independent Research Orchestrator -> Private Company Expert -> private_company_dossier

Downstream use
  public-comp ticker interpretation only when the dossier needs a listed comparable read
  theme evidence only when the private-company read supports a broader mechanism
  portfolio workflow only when an investable exposure exists and the PM explicitly asks
```

The first step prepares evidence, source permissions, company claims, and blocked assumptions. For listed companies, the second step writes the ticker-first investment interpretation, combining the dossier with technical state, market context, theme overlays, and portfolio constraints when the task asks for them. For private companies, the dossier does not become an implicit ticker report or buy / sell call; downstream use must preserve the unit of account, investability, liquidity, transfer restriction, and cannot-know boundaries.

### 9.4 To Writer

The orchestrator may create a report draft for user-facing review when explicitly requested, but formal PM-facing reports should still pass the appropriate package and writer gate.

## 10. Dogfood Plan

Minimum dogfood set:

1. Crypto: `crypto_humanity_protocol_h`
   - source packet from public web and market pages;
   - route to `crypto_project_expert`;
   - output `CryptoDecisionBrief`.
2. Listed equity: one company with public filings and market coverage.
   - route to `company_expert:default_company_dossier`;
   - output `single_asset_dossier`.
3. Private company: one pre-IPO / secondary-market issuer such as `private_databricks`.
   - route through near-term `company_expert:private_company_dossier` compatibility or first-class `private_company_expert` when runtime supports it;
   - output `private_company_dossier`.
4. Missing expert case:
   - source contains reusable method with no owner;
   - route to Expert Factory as `missing_expert_subsystem`.

Success criteria:

- raw sources are in message archive;
- asset workspace only links sources;
- route is selected before Source Card generation;
- expert outputs use domain-owned schema;
- blocked outputs are explicit;
- downstream handoff does not skip lifecycle or portfolio gates.

## 11. Detection Boundaries

Violations are observable:

- asset workspace stores canonical raw source instead of linking message archive;
- Source Card is generated before domain route selection;
- company research defaults to thesis/theme;
- crypto research defaults to thesis/theme;
- external search result is used in an expert artifact without first becoming a message archive source;
- expert output lacks source refs, confidence caps, or blocked outputs;
- report draft claims portfolio action authority;
- missing expert route is hidden by generic prose.

When any violation appears, repair the Digestion boundary before downstream use.
