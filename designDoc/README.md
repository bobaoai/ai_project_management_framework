# Design Docs

This folder is organized so the root only keeps active core design docs. This README is a portal; authority lives in the linked Design Docs.

## Core Entry

T0 layer ids use the `the_` prefix. Use this table for T0 / system-boundary first reads, then follow the linked owner document for the contract body.

For broad architecture context before choosing a T0 owner, read [ai_native_trading_operating_system.md](ai_native_trading_operating_system.md). It is a system overview, not a T0 authority layer.

The [Design Doc Management](the_design_doc_management.md) contract defines document metadata, content structure, and review requirements. This README provides navigation to the relevant authority; it does not define a separate document format.

| Entry | Function / question cluster | Owns | Does not own | Coordinates / conflict rule |
| --- | --- | --- | --- | --- |
| [the_charter](the_charter.md) | surface ownership; constitutional conflicts; object ontology; PM/system authority split | constitutional constraints; DesignDoc / Skill / Code surface split; archive truth; no false precision; no floating objects | runtime commands; field-by-field schema listings; task inventories | wins conflicts; use first when asking which surface owns a claim or change |
| [the_task_routing](the_task_routing.md) | new user request; task mainline; first authority; routing layer separation; skill-boundary intake | user request entry; recurring task mainline; first authority; routing layer separation | artifact freshness internals; T1 domain decisions; PM belief | defers to Charter for surface ownership |
| [the_timestamp_semantic](the_timestamp_semantic.md) | timestamp/date field roles; storage suffixes; time comparisons; mixed-session freshness semantics | timestamp and date field authority; valid comparison semantics | object ontology; task routing; non-time fields; code implementation procedure | Code enforces deterministic comparisons |
| [the_design_doc_management](the_design_doc_management.md) | Design Doc authoring, metadata, content structure, and review | Design Intent; document metadata and structure; review requirements | domain correctness; model / provider execution; PM belief | defers to the owning Design for substance |
| [Topic Branches](#topic-branches) | domain-family next read after T0/system-boundary selection | directory for ingestion, digestion, research, operation, analysis, source/data, portability | T0 conflict resolution; system-boundary authority; child-doc registries | use after the table resolves system-boundary first; each family overview owns its child registry |

## Global Conflict Shortcut

If system contracts conflict:

1. `the_charter` wins for constitutional constraints, surface ownership, object ontology, and PM / system authority split.
2. Use the question-specific T0 owner next: `the_task_routing` for user-intent routing, `the_timestamp_semantic` for time fields, `the_design_doc_management` for Design Doc authoring and review, `the_software_delivery` for code changes and engineering review, and `the_agent_runtime` for Agent Module and Workflow execution.
3. T1 family docs may specialize domain workflows inside those T0 boundaries; they cannot override T0 contracts.

## Question Routing Shortcut

If the question is about:

- surface ownership, object ontology, or "which layer should own this claim": start with [the_charter.md](the_charter.md).
- broad system shape: read [ai_native_trading_operating_system.md](ai_native_trading_operating_system.md), then return to the T0 owner table above.
- task intake, first authority, or skill-boundary routing: read [the_task_routing.md](the_task_routing.md).
- timestamp / date field semantics or time comparisons: read [the_timestamp_semantic.md](the_timestamp_semantic.md).
- Design Doc authoring, metadata, content structure, or review: read [the_design_doc_management.md](the_design_doc_management.md).
- code changes, engineering plans, exact-commit engineering review, release, or deployment: read [the_software_delivery.md](the_software_delivery.md).
- provider-neutral Agent Module or Workflow execution: read [the_agent_runtime.md](the_agent_runtime.md).
- material object boundaries across Raw Data, Operating Cycle Artifact, Source Card, Expert Artifact, Evidence, Thesis, Scenario, Theme, or Technical Report: read [material_00_overview.md](material_00_overview.md). Material Catalog inherits Artifact Graph node handles; it owns material meaning, not global graph law.
- reusable analytical capabilities, expert frameworks / lenses, source-card patterns, claim firewalls, Expertise Application, or Thesis-anchored prediction grammar: read [expertise_00_overview.md](expertise_00_overview.md).
- source intake, archive layout, or canonical source read content: read [ingestion_00_overview.md](ingestion_00_overview.md).
- turning canonical source reads into Source Cards, Typed Claims, expert artifacts, or domain routes: read [digestion_00_overview.md](digestion_00_overview.md).
- research promotion, theses, themes, technical reports, or writer packages: read [research_00_overview.md](research_00_overview.md).
- PM workspace behavior or last-session truth: read [analysis_platform_and_pm_workspace.md](analysis_platform_and_pm_workspace.md) and [last_session_truth_and_ingestion_boundary.md](last_session_truth_and_ingestion_boundary.md).

## Topic Branches

After the core entry docs, branch by topic:

- ingestion family:
  - `ingestion_00_overview.md` — start here for source intake,
    archive object boundaries, canonical source read content, and
    blocker/readiness contracts. It owns the `ingestion_00..40_*`
    family map and points to connector, archive message, read content,
    and error/blocker contracts.
- material family:
  - `material_00_overview.md` — start here for material object
    boundaries across Raw Data, Operating Cycle Artifact, Source Card,
    Expert Artifact, Evidence, Thesis, Theme, Technical Report, and
    Scenario. It owns the Material Catalog overview and admitted child
    contracts; it inherits Artifact Graph node identity / dependency /
    provenance handles without redefining global graph law; adjacent
    domain families still own execution and current schema details inside
    these admitted material boundaries.
  - `material_10_raw_data_contract.md` — Raw Data material identity,
    provider/origin boundary, and non-interpretation rule.
  - `material_20_operating_cycle_artifact_contract.md` — Data Recap,
    Weekly Recap, Snapshot, Decision Brief, and Portfolio Decision family.
  - `material_30_source_card_contract.md` — Source Card, Resource Card,
    Angle Card, allowed-use, and cannot-support boundary.
  - `material_32_typed_claim_contract.md` — Typed Claim bridge boundary
    and source-class / claim-type firewall handoff.
  - `material_35_expert_artifact_contract.md` — Dossier, State Map,
    Transmission Chain, Impact Pool, and related expert artifact outputs.
  - `material_40_evidence_contract.md` — Evidence as belief-change
    record, distinct from source summary or raw observation.
  - `material_50_thesis_contract.md` — Thesis as falsifiable belief
    container.
  - `material_60_theme_contract.md` — Theme as durable research-memory
    container.
  - `material_70_technical_report_contract.md` — Technical Report as
    current market-state expression, distinct from Scenario.
  - `material_80_scenario_contract.md` — Scenario as Thesis-anchored,
    Expertise-driven forward prediction.
  - `material_90_support_surfaces.md` — Canonical Input, Feature,
    Path Observation, and Freshness Event support surfaces.
- expertise family:
  - `expertise_00_overview.md` — start here for reusable capability
    boundaries: expert identity / lifecycle, frameworks, lenses,
    source-card patterns, source-class / claim-type firewalls,
    Expertise Application, expert artifact schemas, Scenario prediction
    grammar, validation policy, and generated skill projection contracts.
    It owns capability authority, not materialized Source Card, Expert
    Artifact, Evidence, Thesis, Scenario, Theme, report, or PM decision
    instances.
  - `expertise_20_application_contract.md` — admitted Expertise
    Application relation contract. It owns capability-to-material
    application semantics, input/output material refs, allowed-use
    preservation, route semantics, and PM-use boundary without creating a
    runtime schema.
  - `expertise_60_prediction_framework_contract.md` — first admitted
    Expertise child contract. It owns Thesis-anchored Scenario prediction
    grammar, trigger / falsifier families, observable-delta maps, path
    taxonomy, and the PM-use boundary for Scenario candidates.
- digestion family:
  - `digestion_00_overview.md` — start here for the T1 layer between
    canonical source read content and research / analysis judgment. It
    executes Source Card / Typed Claim / Framework Card / expert
    subsystem workflows under Material Catalog object boundaries, and
    owns Expert Factory / Independent Research Orchestrator boundaries,
    Postgres-backed digestion registry and graph support, and the Fed
    Rate KB dogfood path.
  - `digestion_10_structure_contract.md` — structural contract for
    digestion objects, Postgres tables, file projections, generation
    steps, expert contracts, independent-research source packets, and
    downstream consumption, using Fed Rate as the first template.
  - `digestion_11_report_package_contract.md` — report-package contract
    for turning Digestion expert artifacts into writer-ready packages.
    It owns the generic `digestion_report_package` shape and child-contract
    admission / inheritance rules.
  - `digestion_12_private_company_report_package_contract.md` — domain-specific
    contract for `private_company_report_package`. It inherits `digestion_11`
    and adds private-company pricing-surface, public-comp, unit-of-account,
    cannot-know, and blocked-output boundaries.
  - `digestion_42_crypto_project_expert.md` — seed design for the
    Crypto Project Expert subsystem, extracted from a dual-track crypto
    analysis framework source. It defines evidence-permission boundaries,
    typed crypto claims, project-type modules, decision-brief outputs, and
    a `90 Example` full framework plus a public-info Humanity (`H`) smoke test.
  - `digestion_20_independent_researcher.md` — cross-asset Digestion
    orchestrator for local archive search, external source collection,
    canonical message linking, asset workspaces, source packets, domain
    route selection, expert invocation, and package/report handoff.
  - `digestion_30_expert_factory.md` — governance contract for creating
    and maintaining domain experts, including reusable analytical asset
    admission, source card patterns, typed claim firewalls, expert
    artifacts, lifecycle, and generated skill projection.
  - `digestion_41_company_expert.md` — Company Expert family umbrella for
    routing company-like research targets to listed-company, private-company,
    or future company child experts while preserving shared evidence boundaries.
  - `digestion_41_1_private_company_expert.md` — Private Company Expert
    contract for pre-IPO / private-company research. It owns operating-company
    value vs security-price separation, secondary-market pricing surfaces,
    primary-round and fund-mark evidence, public-comp calibration,
    `private_company_dossier`, and cannot-know boundaries.
  - `digestion_41_2_listed_company_expert.md` — Listed Company Expert contract
    for public-company / public-equity issuer research. It owns filings,
    earnings, transcripts, market-data surfaces, company typed claims,
    `single_asset_dossier`, and the handoff to `research-single-stock-analysis`.
- research family (3 legs: thematic, technical, fundamentals):
  - `research_00_overview.md` — start here for any research-related
    question. Owns the topology, naming convention
    (`research_NN_<descriptor>.md`), and a per-doc registry covering
    all `research_00..03_*` files (thematic promotion workflow,
    deprecated message-archive pointer, technical signal pipeline,
    technical framework, fundamentals architecture, shared writer-package
    contract, shared report reviewer pattern, and private-company PM
    report instruction).
  - `knowledge_base_and_memory_system.md` — system-level memory
    framing the research family sits inside.
- operation family:
  - `operation_00_operating_framework_governance.md` — T1 governance
    contract for role-level operating frameworks such as Interpretation,
    PM, Trader, Executor, and Risk.
  - `operation_10_interpretation_framework_governance.md` — compatibility
    pointer for the older Interpretation Ecosystem framing. Canonical
    domain-expert and interpretation-framework production now belongs in
    the digestion family, especially `digestion_30_expert_factory.md`.
- analysis workspace / PM-facing work:
  - `analysis_platform_and_pm_workspace.md`
  - `last_session_truth_and_ingestion_boundary.md` (ingestion vs read layers; raw UTC timestamps vs session semantics vs report/render labels; per-instrument last session; `generated_at`; §8 AI prompt/package contract)
- source and data architecture:
  - `ingestion_00_overview.md`
  - `source_connectors_and_knowledge_ingestion.md` (legacy connector
    boundary note; new work should start from the ingestion family)
  - `market_data_architecture.md`
  - `price_data_architecture.md`
- portability / repo-level support docs:
  - `cross_machine_portability_and_github_seed.md`
  - `postgres_ticker_coverage_design_v0_1.md`

## Time-Contract Shortcut

- raw UTC data-layer timestamps:
  - `last_session_truth_and_ingestion_boundary.md`
  - `price_data_architecture.md`
- session-semantic horizons:
  - `last_session_truth_and_ingestion_boundary.md`
- report-layer local / ET / PT wording:
  - `last_session_truth_and_ingestion_boundary.md`

## Subfolders

- `learning_library/`: external references, extracted lessons, topic notes
- `modules/`: module-level design notes
- `ai_guidelines/`: agent-facing protocol and output rules
- `agreement/`: higher-level written agreements
- `bp/`: blueprint, template, deck, and reference-style docs
- `ideas/`: future-facing design proposals and not-yet-implemented plans
  - `ideas/archive_library.md`: 5-family archive library plan (持仓 / theme / technical / recap / single_stock 跨制品归档统一根 `data/archive/`，latest singleton 不动；旁路写 immutable copies for replay / backtest)
- `temp/`: handoff notes, migration notes, historical or temporary docs
