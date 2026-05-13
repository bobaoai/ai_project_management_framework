---
title: Task Intake Routing Contract
status: active_draft
layer: T0
t0_layer_id: the_task_routing
canonical_owner: designDoc/the_task_routing.md
reader_persona:
  - System Builder
  - Top-Level Router
  - Mainline Skill Owner
  - Workflow Reviewer
---

# Task Intake Routing Contract
**Version 0.2 - 2026-05-06**

## 0. Contract Capsule

Machine-audit block. Keep paths, ids, aliases, commands, and ledger pointers plain; use citation ids only in body prose and `References`.

```yaml
layer: T0
t0_layer_id: the_task_routing
status: active_draft
canonical_owner: designDoc/the_task_routing.md
scope: top-level user-intent intake into task mainlines, first-authority assignment, overlay discipline, and separation between task mainline, skill, deterministic builder/package, and writer gateway layers
non_goals:
  - artifact freshness internals, which belong to the_artifact_graph
  - external runner mechanics, prompt assembly, and manifests, which belong to the_external_agent_management
  - domain semantics inside any single T1 mainline or skill
  - TradeCLI / runtime code admission, which belongs to the_tradecli_code_management
inputs:
  - user request
  - task mainline inventory in this document
  - routing projection files and runtime skill indexes
outputs:
  - matched_mainline
  - first_authority
  - primary_truth_surface
  - downstream_skill
  - overlay_needed
  - why_this_route_wins
truth_surfaces:
  - designDoc/README.md
  - designDoc/the_task_routing.md
  - 09_codex/routing/task_mainlines.md
  - 09_codex/skills/routing-task-mode-router/SKILL.md
  - .cursor/skills/routing-task-mode-router/SKILL.md
runtime_triggers: see Machine Audit Runtime Surfaces
downstream_consumers:
  - routing-task-mode-router
  - 09_codex/routing/task_mainlines.md
  - .cursor/skills/INDEX.md
  - 09_codex/skills/INDEX.md
  - mainline skills that consume the routing decision
open_decisions:
  - whether routing-current-macro-priority-router should keep its current name after the top-level router is explicit
  - whether writer-handoff remains a visible skill or collapses into the writer-gateway layer
  - whether machine-readable task mainline registry should remain a Codex projection file or graduate into a runtime YAML registry
  - whether current skill consequence sections should migrate into a companion projection / migration notes doc
review_gate: design-doc-reviewer
runtime_surface_ledger: see Machine Audit Runtime Surfaces
verification_hooks: see Machine Audit Runtime Surfaces
```

This document defines the top-level execution and routing contract for `trading_platform` after the repo's shift toward:
- archive-first research memory
- source-aware routing
- deterministic package assembly
- unified external writer exits
- clearer separation between system layers that were previously easy to conflate
This is an AI-facing design document. It is intentionally detailed. The purpose is not to provide a skim-first summary, but to give downstream agents, skills, and future design work a stable top-level contract that reduces routing drift and naming confusion.

For this topic, the document should be treated as:

- written primarily for AI consumption rather than deck-style human scanning
- detailed by default when detail reduces routing ambiguity
- the canonical drafting surface for top-level routing and naming changes before they are pushed into lower-level runtime surfaces
---
## 1. Why This Document Exists
Recent design work exposed a repeated system-level mismatch:
- task lines were being compressed too early into a few abstract role buckets
- skill names were able to distort the perceived structure of the system
- downstream writer steps were at risk of being mistaken for top-level task routers
- `theme` was at risk of silently becoming the first router for tasks that only happened to mention a theme
- distinct layers such as `task mainline`, `skill`, `builder/package`, and `writer gateway` were being discussed as if they were the same object
This document exists to fix that projection problem at the top level.
It should be read together with:
- AI Native Trading Operating System [System-Operating-View]
- Knowledge Base And Memory System [Knowledge-Memory]
- Thematic Workflow [Research-Thematic-Workflow]
- Analysis Platform And PM Workspace [Analysis-PM-Workspace]
Those documents define the overall system, memory surface, research workflow, and current PM workspace. This document acts as the bridge contract between those longer-lived design surfaces and the execution-facing task / skill contracts that decide how a real request should move through the repo.

### 1.1 Effect-First Contract Design Rule

For new task contracts or workflow redesigns, do not start from:

- section lists
- package shapes
- builder / gate layering
- prompt wording

Those may still matter, but they are downstream implementation surfaces.

The preferred design order is:

1. define the final visible artifact and the effect it must create for the user
2. define which upstream judgment object must pre-compress or pre-rank reality so that effect becomes reliable
3. define which truth surface prepares inputs for that judgment
4. define which downstream carrier should only carry that judgment rather than recreate it
5. define which gate / writer / renderer should only check or express that prepared truth
6. only then finalize sections, schema, prompts, and code

In short:

- effect first
- judgment role second
- truth surface third
- carrier / gate / writer after that

This rule exists because a workflow can look structurally complete while still failing to help the final artifact do its real job.

### Review-First Rule For This Area

For architectural changes in this area, follow this order:

1. write or revise the design position in `designDoc/the_task_routing.md`
2. review the change as design first
3. only after review, propagate the approved position into:
   - `.cursor/rules/`
   - `.cursor/skills/`
   - implementation code
   - update batches and other supporting docs

Until that review happens, this file should be treated as the primary drafting and review surface for top-level routing changes.

### TODO: Code vs Doc Responsibility Boundary Cleanup

Status: TODO, not yet a routing behavior change.

This document is currently carrying several kinds of material in one surface. Before the next major routing rewrite, split or mark those materials by responsibility:

- T0 contract body: user-intent intake, task mainline admission, first-authority rules, layer boundaries, non-goals, and conflict resolution.
- AI judgment guidance: how to reason through ambiguous user requests before choosing a mainline.
- Machine registry candidates: mainline ids, aliases, owner skills, projection paths, canonical docs, artifact outputs, and validation hooks.
- Projection / skill consequence notes: current `09_codex`, `.cursor`, and `09_claude` skill implications that should not become permanent T0 rule body by accident.
- Migration history and open questions: useful context, but not binding routing law.

Candidate cleanup steps:

- keep `the_task_routing` focused on judgment and authority
- keep `09_codex/routing/task_mainlines.md` as the Codex-readable projection until a runtime YAML registry is admitted
- decide whether a future `data/runtime/...` task mainline registry should become the hard-audit source for ids / aliases / owners
- move long skill consequence sections into a companion projection or migration-notes doc if they keep growing
- update `design-doc-reviewer` to flag machine-readable registry content that is embedded in body prose without a ledger
---
## 2. Relationship To The Existing System-Level Picture
This document does not replace the repo's three-view system narrative. It refines how work should be routed inside it.
Current system-level picture:
1. `Functional Modules`
2. `Information Pool / archive-memory layer`
3. `AnalysisPlatform`
This document explains how a real user request should move through that system without collapsing distinct layers.
In practice, top-level work now needs to be read through **four routing-relevant layers**:
1. `task mainline layer`
2. `skill layer`
3. `deterministic builder / package layer`
4. `writer gateway layer`
These are not four new product layers. They are four different ways the system is projected during execution and design.
---
## 3. The Four Routing-Relevant Layers
### 3.1 Task Mainline Layer
This is the real first router.
It answers:
- what recurring task the user is actually trying to do
- which task line has first authority
- which workflow should start first
- which neighboring task lines are only overlays or downstream follow-ons
This layer must not be back-defined by:
- a skill name
- a writer backend name
- a package file name
- a currently open local file
- the fact that the request mentions a theme, ticker, or report artifact
The most important correction here is:
- do not start from abstract role buckets such as `eng`, `macro analyst`, or `portfolio manager`
- start from the user's real recurring task line first
Roles still matter, but only after the task line has already been identified.
### 3.2 Skill Layer
This is the AI/agent-facing task contract layer.
A skill should answer:
- current persona
- current task
- primary truth surface
- output artifact
A skill is not:
- a Python module
- a CLI command
- a writer backend
- a package manifest
It is the working contract that tells the AI how to operate inside one task line.
This means skill docs should be written for AI consumption, with enough detail to answer:
- when to enter this skill
- what this skill should read first
- what it should produce
- how it should hand off to adjacent task lines
- which neighboring concepts are easy to confuse with it
### 3.3 Deterministic Builder / Package Layer
This layer owns:
- canonical object selection
- deterministic package assembly
- projection and manifest construction
- package-facing shape for downstream writing or review
This layer should answer:
- which canonical objects were selected
- which local files provide payload truth
- what the writer or reviewer should receive as deterministic input
This layer must not silently own:
- top-level routing authority
- final prose judgment
- skill identity
This layer is where the repo enforces its preference for:
- indexes and registries for lookup
- canonical payload objects for truth
- deterministic assembly before external writing
### 3.4 Writer Gateway Layer
This layer is the unified external writing exit.
In the current repo it is represented by:
- `src/writers/service.py`
- `src/writers/models.py`
- `src/tools/draft_*`
This layer owns:
- `task_kind`
- backend selection
- package-to-markdown drafting
- output sidecars such as writer metadata
External AI runner mechanics, prompt assembly, execution profiles, manifests, and stale-output policy are governed by [T0-External-Worker]. This document only owns the routing boundary that keeps the writer gateway downstream of the task mainline.
This layer is not itself:
- the top-level task router
- a task mainline
- a skill
- a theme-only writer
The existence of a shared writer gateway means the repo should not rename every downstream writing object as if it were the gateway itself.
---
## 4. Top-Level Routing Order
All future routing, skill design, and workflow explanations should follow this order.

Treat this as the default entry rule for every new user conversation or request in this area:

1. route the request into the correct `task mainline` first
2. only after that, decide the deeper domain path, overlay, builder/package step, or downstream writer/reviewer step

All future routing, skill design, and workflow explanations should then follow this order:
1. identify the `task mainline`
2. identify the active `persona` inside that mainline
3. identify the `primary truth surface`
4. run the appropriate `deterministic builder / package` step if needed
5. hand off to the `writer gateway` or another downstream artifact step only after upstream context is stable
When this order is inverted, the same errors recur:
- a writer exit gets mistaken for a skill
- a skill name gets mistaken for a system layer
- a theme mention gets mistaken for top-level routing authority
- an archive workflow gets explained as if it were only connector work or only analyst prose
- one narrow task name gets projected onto the whole architecture
---
## 5. The Eight High-Priority Task Mainlines
The current repo should stabilize around **eight** high-priority recurring task mainlines.
These are not a permanent capped list. They are the highest-priority current inventory.
### 5.1 Inbox / Mail Triage
Purpose:
- inspect new mail
- determine what is new, duplicated, container-only, or worth archiving
- decide whether the next step is archive promotion or no further action
First authority:
- `operator`, with archive-aware judgment
Primary truth surface:
- inbox state
- envelope metadata
- archived external IDs
- triage-related body shape
Typical outputs:
- inbox status
- new-vs-archived classification
- archive candidate set
This mainline should not be collapsed into full archive promotion. Seeing what arrived and deciding what should proceed are not the same step.
### 5.2 Archive Curation / Message Promotion
Purpose:
- turn a message or imported material into reusable research objects
- choose the effective body surface
- assign source-aware routing context
- generate evidence-bearing intermediate objects
First authority:
- `macro analyst` or broader research-analysis posture, not pure connector plumbing
Primary truth surface:
- archived `message`
- `read_content.md`
- `content_selection`
- `source_collection`
- legacy `text_read` only when explicitly marked as an older audit surface
- `image_reads`
- `agent_evidence.json` as the research-promotion derivative when needed
Typical outputs:
- refreshed effective content
- `snapshot`
- `theme_update_draft`
- thesis candidate inputs
This mainline remains distinct even if long-term persona naming converges. Archive curation is a stable task line even when it shares the broader `macro analyst` working posture.
### 5.3 Theme Update / Theme Report Maintenance
Purpose:
- update how one theme is currently understood
- maintain report-level framework and evidence
- refresh theme content, scenario logic, and related thesis links
First authority:
- `macro analyst`
Primary truth surface:
- theme metadata
- linked research
- context index
- package
- finalized report backbone
Typical outputs:
- updated theme package
- updated theme draft
- updated final theme report
This mainline should stay distinct from market observation. A theme report is not just a longer market note.
### 5.4 Market Recap / Market Observation
Purpose:
- explain what the market traded today or in the event window
- interpret what price action confirmed or failed to confirm
- state whether the active mainline strengthened, weakened, or changed shape
- surface the next key question for the PM rather than ending at static recap
First authority:
- `macro analyst`
Primary truth surface:
- chosen observation mainline
- related local theme context
- price action package
- confirmed public anchors when needed
Typical outputs:
- market observation
- post-close note
- market recap
This mainline should stay independent from theme update. It may borrow theme context, but it is not subordinate to report maintenance.
### 5.5 Company Financial Analysis
Purpose:
- write a PM-facing company / financial analysis report
- interpret business model, revenue engine, growth drivers, financial quality, competitive position, valuation bridge, and public-comp or secondary-market surfaces
- convert Digestion company expert outputs into an analytic company memo rather than a dossier summary
First authority:
- company analyst / financial analyst
Primary truth surface:
- company source packet
- `single_asset_dossier` for listed-company subjects
- `private_company_dossier` for private / pre-IPO subjects
- Source Cards and Typed Claims
- filings, earnings releases, transcripts, issuer voluntary disclosures, public comps, valuation surfaces, and private secondary surfaces when applicable
Typical outputs:
- company financial analysis package
- PM-facing company analysis report
- valuation bridge / public-comp read
- private-company or pre-IPO company memo with secondary-surface boundaries
Routing boundary:
- `business / financial / valuation memo` routes here
- `ticker now / tape / actionability / technical state` routes to `single-stock analysis`
- if the user asks for both, run company financial analysis first, then single-stock analysis or portfolio decision only after the company read is stable
This mainline must not be silently absorbed into single-stock analysis just because the subject has a ticker. It also must not emit portfolio action, sizing, execution advice, or private-share transaction recommendations.
### 5.6 Single-Stock Analysis
Purpose:
- decide whether one asset or stock is interesting now
- integrate technical state, relevant theme overlays, and thesis context into one decision-facing view
First authority:
- still needs tighter stabilization, but the working direction should be closer to `macro analyst` than a pure PM/router-first framing
Primary truth surface:
- ticker package
- technical report
- relevant local theme overlays
- linked thesis context
Typical outputs:
- single-stock package
- single-stock analysis draft
This mainline must not be silently absorbed into theme maintenance just because a theme overlay is present. It also must not absorb company financial analysis when the real request is a business / valuation / fundamental memo.
### 5.7 Portfolio Decision
Purpose:
- decide what the portfolio should do now
- move from market and research context to account-aware debate, sizing, constraints, and next actions
First authority:
- `portfolio manager`
Primary truth surface:
- portfolio package
- policy envelope
- account review context
- current holdings and exposure
- active themes and technical state as decision inputs
Typical outputs:
- decision package
- debate report
- target book proposal
- execution preview
This mainline must remain distinct from both market observation and theme report maintenance.
### 5.8 External Learning Research
Purpose:
- research external projects, papers, frameworks, tools, or public operating systems that can improve `trading_platform`
- convert outside material into reusable local design judgment rather than a generic web summary
- write durable learning-library artifacts that preserve source provenance, extract transferable patterns, and state how the lesson should or should not change this repo
First authority:
- `research architect` posture inside Hoveath: it reads external systems through the user's axioms and the local architecture truth surface
Primary truth surface:
- external source URLs, official docs, repositories, papers, articles, and critiques
- `09_soul/axioms/` as the user's thinking filter
- `09_soul/core/COMMUNICATION.md` as the style and prose contract
- `09_soul/skills/workflow_deep_research_survey.md` as the research method for broad, source-heavy external surveys
- `designDoc/learning_library/` as the canonical durable output surface
- `designDoc/` architecture docs when the research is meant to influence local system design
Typical outputs:
- external project note under `designDoc/learning_library/repo_notes/`
- topic synthesis under `designDoc/learning_library/topics/`
- decision-oriented research project under `designDoc/learning_library/projects/<slug>/`
- explicit design-pressure items that may later cross-reference progress tracking, retrospectives, rules, skills, or implementation contracts
This mainline is distinct from archive curation. Archive curation turns incoming research materials into local knowledge objects under `data/research`; external learning research actively studies outside systems and turns them into architecture or operating-model judgment. It is also distinct from theme maintenance because the output is about improving the platform and Hoveath's operating system, not updating a market theme report.
---
## 6. Mainline Expansion Rule
The current eight mainlines are not a permanent final taxonomy.
A new task line should be promoted into the top-level inventory when a workflow is repeatedly used in practice and has its own distinct:
- first authority
- primary truth surface
- output artifact
- handoff shape
Do not resist adding a new mainline only because the current list already looks tidy. A tidy but false top-level inventory causes later drift.
When adding a new mainline, document all of the following in the same change:
- task definition
- current persona
- truth surface
- major modules / CLI / builder / writer touchpoints
- output artifact
- boundaries and handoffs
In other words, future extensibility should come from **well-described new task contracts**, not from flattening more workflows into fewer names.
---
## 7. Persona Convergence
The current direction should avoid exploding persona count too early.
The likely stable personas are trending toward:
- `operator`
- `macro analyst`
- `portfolio manager`
With this interpretation:
- archive curation can remain a distinct workflow without forcing a permanently separate long-term persona
- many research interpretation tasks can converge under `macro analyst`
- portfolio action and book-level recommendation stay under `portfolio manager`
This does not mean every task line owned by `macro analyst` should be merged. Distinct task lines can share one broader persona.
---
## 8. Current Skill-Layer Consequences
This top-level picture has immediate consequences for how skills should be written and positioned.
### 8.0 Top-Level Router Versus Macro Midstream Router

The repo should now distinguish more explicitly between:

- the current `routing-task-mode-router` top-level routing surface
- the existing `routing-current-macro-priority-router`

These two objects should not be treated as the same layer.

Current design direction:

- top-level routing should decide the daily task mainline first
- only after the request is already understood as `macro/theme-oriented` should macro-internal routing begin
- the top-level router should answer:
  - which mainline this request belongs to
  - which first authority should lead
  - which truth surface should be read first
  - which downstream mainline skill should own the task
- the macro midstream router should answer only:
  - inside the macro path, which theme or macro mainline should lead
  - whether the result should go to `research-current-market-reporter`
  - whether the result should go to `research-theme-report-owner`
  - or whether another task line should only receive `theme overlay` context rather than ceding first authority

This is now more aligned with the redesign than the earlier transitional state.
Earlier, `routing-current-macro-priority-router` had to absorb ambiguity because several downstream mainlines were not yet clearly defined.
Now that `research-current-market-reporter`, `research-theme-report-owner`, `single-stock analysis`, and `portfolio decision` all have clearer contracts, the old mixed role should be reduced.

So the current judgment is:

- the system still needs macro-path internal routing
- but it no longer needs that routing layer to behave like a top-level front door
- `routing-current-macro-priority-router` should therefore be understood as a thin midstream chooser, not as the universal first router for analysis

More specifically, it now reads more naturally as a `macro substep pass` inside `routing-task-mode-router` than as a peer top-level layer.

Current preferred `macro substep pass` responsibilities:

- confirm that top-level task mode is already `macro/theme-oriented` or that another mainline explicitly requested `theme overlay`
- choose which macro/theme branch should lead inside that already-bounded context
- decide whether the macro result should:
  - continue into `research-current-market-reporter`
  - continue into `research-theme-report-owner`
  - or return to another mainline as `theme overlay only`
- explain why this branch wins over nearby competing branches inside the macro path

Current preferred `macro substep pass` outputs:

- `matched_theme`
- `matched_subtheme` when useful
- `time_horizon`
- `macro_route_result`
- `why_this_branch_wins`

Where `macro_route_result` should usually be one of:

- `route_to_current_market_reporter`
- `route_to_theme_report_owner`
- `return_theme_overlay_only`

This is important because it means `routing-current-macro-priority-router` is no longer best understood as:

- a second top-level gate
- a universal macro front door
- a first-authority chooser for stock or portfolio tasks

It is better understood as:

- an internal macro branch-selection step
- called only after top-level ownership is already stable
- allowed to recommend `theme overlay` without rewriting the owning mainline

Current preferred surface:

- make the top-level router explicit as `routing-task-mode-router`
- keep `routing-current-macro-priority-router` as the thinner macro-path router underneath it

Current `routing-task-mode-router` contract:

- purpose:
  - decide the top-level daily task mainline before any deeper domain routing begins
- primary inputs:
  - the user's request
  - the user's explicitly named object, if any, such as account, ticker, theme, report, message, or event window
  - the already-stable task-mainline inventory in this document
- minimum outputs:
  - `matched_mainline`
  - `first_authority`
  - `primary_truth_surface`
  - `downstream_skill`
  - `overlay_needed`
  - `why_this_route_wins`
- output boundary:
  - it should not decide which theme priority rank is higher inside the macro path
  - it should not decide package sufficiency
  - it should not decide writer structure or article prose
  - it should not silently absorb downstream pass-type decisions that belong to `research-theme-report-owner` or `operation-portfolio-decision`

Current preferred top-level route table:

- if the user is asking what arrived, what is new, or how to triage inbox items:
  - route to inbox / mail triage
- if the user is asking to normalize, classify, archive, promote, or turn new material into reusable research objects:
  - route to archive curation / message promotion
- if the user is asking what the market traded, what price action confirmed, or how to interpret an event window:
  - route to `research-current-market-reporter`
- if the user is asking whether a standing theme/report should be refreshed, widened, or re-framed:
  - route to `research-theme-report-owner`
- if the user is asking for a business / financial / valuation memo, company report, fundamental analysis, public-comp read, IPO / pre-IPO read, or secondary-market surface read:
  - route to `research-company-financial-analysis`
- if the user is asking what one ticker or one asset means now through ticker, tape, actionability, technical state, levels, watchlist status, or current price behavior:
  - route to `single-stock analysis`
- if the user is asking what the current book should do now:
  - route to `portfolio decision`
- if the user is asking to study an external repo, paper, product, architecture, public skill system, or outside workflow so the result can improve this repo:
  - route to `research-external-learning`

Current preferred top-level anti-drift rules:

- a mention of a `theme` does not by itself justify routing into theme maintenance
- a mention of a `ticker` does not by itself justify routing into single-stock analysis if the real ask is about company business / financial analysis or about the book
- a mention of `portfolio` or `account` does not by itself justify routing into portfolio decision if the user is still asking for first-pass market interpretation
- a package path, writer path, or report filename does not by itself define task mode

This future router should therefore stay thin.
Its job is to identify which stable mainline owns the request, not to become another heavyweight analysis layer.

### 8.1 `research-current-market-reporter`
- `research-current-market-reporter` should remain an independent task mainline rather than being explained as a lightweight subcase of theme maintenance.
- Its first authority should be `macro analyst`.
- Its purpose is to answer questions such as:
  - what the market traded today
  - what price action confirmed
  - what did not confirm
  - whether the active mainline strengthened, weakened, or changed shape
- It may consume theme context, but it should not inherit the full lifecycle of finalized theme-report maintenance.
- It should hand off to `portfolio manager` only when the user explicitly moves from market interpretation to:
  - account impact
  - rebalance consequences
  - hedge priority
  - position sizing or action sequencing

Positive contract:

- `Current persona`:
  - `macro analyst`
- `Current task`:
  - interpret the current market window and explain how asset prices evolved in the newest trading day through one chosen mainline
- `Primary truth surface`:
  - current window
  - fixed `ObservationTickerPool`
  - database observation universe:
    - current holdings from latest account snapshots
    - watchlist
    - theme-related stocks already defined in indexes
  - refreshed external technical reports read through generated indexes
  - current `Main Driver`
  - chosen `Theme / Thesis` framework
  - this run's observation package
  - local snapshots / linked research when relevant
  - explicit observation basket
- `Output artifact`:
  - a complete PM-facing market observation, post-close note, daily recap, or other current-window market report

Effect standard:

- the reader should grasp the dominant market mainline immediately
- the reader should understand where the tape has progressed relative to the recent few sessions
- the key assets should read like a state map, not a loose ticker list
- the key assets should still carry enough selected technical evidence that the state map feels grounded rather than abstract
- the report should make the tape's transmission chain legible
- the report should leave the PM with the next key question, not only a generic watchlist

Current object boundary:

- `ObservationTickerPool`:
  - the current run's observation surface
  - fixed baseline plus selected same-day additions
- `MainDriverRead`:
  - what the market is pricing now
  - the main transmission chain across the observation surface
- `Theme / Thesis`:
  - explanatory framework
  - not the owner of the current package or report
- `ObservationRun`:
  - the concrete current-window task object
  - owns package and final report
- `ObservationPackage`:
  - prepared writing input for the run
  - should not be treated as a disguised theme-draft object

Boundary versus `research-theme-report-owner`:

- `research-current-market-reporter` is for event-window or current-market interpretation
- `research-theme-report-owner` is for maintaining the standing report framework of a theme
- one theme may drive both workflows, but they remain different mainlines
- a market observation may later become evidence for a theme report, but should not be treated as the same task

More explicit boundary after the owner-contract expansion:

- `research-current-market-reporter` may conclude that current price action strengthened, weakened, or complicated a theme
- it may also say that today's move reveals a new branch worth later folding into theme maintenance
- but it should still center the current market window, current cross-asset behavior, and what the market appears to be pricing now
- once the task becomes "should the standing theme report be refreshed", "is the report missing a structural leg", or "does this evidence justify a theme candidate for deeper maintenance", first authority should move to `research-theme-report-owner`
- in other words:
  - `research-current-market-reporter` can emit evidence and first-pass interpretation
  - `research-theme-report-owner` owns standing-framework maintenance, report refresh judgment, and report-anchored theme-candidate discovery

Typical output difference:

- `research-current-market-reporter` produces a complete market observation artifact first:
  - PM-facing market observation
  - post-close note
  - daily recap
  - snapshot rewrite or other current-window market report
- the observation package is a fixed upstream requirement for this mainline, but it should remain a support surface rather than the public identity of the skill
- `research-theme-report-owner` produces an owner decision package for a theme-maintenance pass

Current direction:

- market observation remains a result-first report skill, not a workflow-shaped note about package handling
- this mainline should start from a fixed baseline observation surface, then review non-core tradable equities through refreshed technical reports, then identify the `Main Driver`, then choose the explanatory `Theme / Thesis` framework
- this mainline should still use one run-owned observation package and one explicit observation basket before drafting
- the output contract should stay effect-oriented:
  - make the reader understand what the market traded
  - make the reader feel what stage the tape has reached
  - make the reader see what remains unresolved
  - make the reader know what next question matters most
- latest-ready daily-update status should be treated as a hard execution precondition for routine market-observation builds
- if the shared daily-update surface is missing, outdated, or lacks required deterministic artifacts, the workflow should trigger the deterministic daily update flow before package generation
- if the run would trigger technical refresh or other token-consuming writer work, that preflight update should stay deterministic-only unless the user explicitly approves additional writer work
- bypass flags such as `--ignore-update-status` should be reserved for explicit diagnostic or user-approved forced runs rather than normal package generation
- the candidate non-core tradable universe should come from the database observation universe:
  - current holdings from latest account snapshots
  - watchlist
  - theme-related stocks already defined in indexes
- non-core tradable equities should be reviewed through canonical technical reports first, then selected into the same-day observation pool
- the fixed baseline should always include:
  - major rates, FX, and equity-index futures
  - gold, oil, and volatility
  - next `FOMC`
  - important macro release dates in the next 30 days, with the next week treated as the most sensitive window
- `CalendarWatch` should be treated as a deterministic builder artifact rather than as a live-only skill concern:
  - call the local builder/program that assembles `CalendarWatch`
  - persist successful outputs under `data/macro/calendar_watch/`
  - if the refresh is incomplete, reuse the latest saved local artifact
  - if that latest saved artifact is older than the current observation day/window, stop and surface the error rather than silently carrying stale calendar dates forward
- builder/package/gate detail should support quality, but should not dominate the skill-level contract or make the mainline read like a workflow note

Compact optimization rule for `Daily Market Recap`:

- the fastest reliable path is not "write sooner"; it is `fresh gate -> intake -> judgment -> package -> final note`
- keep the invariants fixed:
  - fresh upstream data
  - explicit upstream judgment before package assembly
  - exact package admission carried downstream
- keep the interpretation adaptive:
  - do not force a theme-first explanation when the tape is better explained directly from cross-asset state
  - do not force one fixed asset count, one fixed article skeleton, or one fixed causal template
  - let the judgment layer decide whether today's tape is best framed as breakout, first confirmation, failed reclaim, rotation, squeeze, or unresolved split tape
- treat mismatches as decision objects rather than as noise:
  - if rates, breadth, dollar, oil, gold, or one key asset fail to confirm the dominant read, the system should preserve that mismatch and explain its impact on confidence, stage, and next question
  - if the mismatch is workflow-level instead of market-level (stale gate, mixed session horizon not declared, malformed package admission), the workflow should stop rather than improvise

The design target is therefore:

- highest-speed path for the AI to reach the right current-market artifact
- without hardcoding one market logic
- while still making the cost of a mismatch legible enough that the AI can choose how much confidence to assign and whether to continue

In practical terms:

- use the canonical artifacts to remove routing ambiguity
- use the judgment layer to keep autonomy on interpretation
- use mismatch-impact language to keep autonomy disciplined instead of freewheeling

Judgment-first refinement for the next pass:

- the current implementation still leans too package-first in one important way: it can assemble a writer-facing scaffold before the upstream `Main Driver` judgment is actually settled
- the preferred next direction is `judgment-first`, not `package-first`
- in that direction, the system should first sweep:
  - `ObservationTickerPool` technical reports
  - current news / event window
  - `macro report + macro snapshot + calendar watch`
- only after that sweep should the system produce run-owned judgment objects such as:
  - `MainDriverRead`
  - `ObservationBasketDecision`
- only after those judgment objects exist should the writer-facing `ObservationPackage` be assembled
- this means the package should become the downstream carrier of judgment, not the upstream substitute for judgment
- the real design test here is effect-first:
  - if the final PM-facing note should make the mainline, stage, asset state map, conditionality, and next question legible
  - then the upstream judgment layer must already have decided which materials and assets deserve that central reading role
  - otherwise the package will silently regain second-order selection authority and the design will drift back toward `package-first`
- the real reader split should also stay explicit:
  - single-asset technical reports are `trader + PM` dual-reader objects
  - upstream market judgment is a `PM / macro analyst` convergence object
  - the final market note is the PM-facing cognitive interface

Preferred object order for the next market-observation revision:

1. `ObservationIntake`
2. `MainDriverRead`
3. `ObservationBasketDecision`
4. `ObservationPackage`
5. `writer-handoff`
6. final market note

`ObservationIntake` should stay narrower than the final package and should be treated as the pre-judgment truth surface for the run.

Recommended first-pass `ObservationIntake` sections:

- `Run Context`
- `Macro Report`
- `Local Macro Snapshot`
- `Calendar Watch`
- `Current News / Event Window`
- `Theme Context`
- `ObservationTickerPool`
- `Technical Report Sweep`
- `Open Questions`

Recommended downstream `ObservationPackage` reading order:

- start from the fixed observation framework and macro truth surface first
- keep `Macro Report`, `Local Macro Snapshot`, `Calendar Watch`, and the current news / event window ahead of downstream writing notes
- expose `Theme Context` explicitly, including theme snapshots and thesis list, before the per-asset technical block
- keep the package's technical appendix as `Technical Report Sweep` so the downstream writer is reading canonical technical reports rather than a second summary layer

`Calendar Watch` note:

- this belongs to the deterministic builder layer, not the skill contract
- the intake should consume the local `CalendarWatch` artifact produced by the builder/program call
- when the refresh path is incomplete, the builder may fall back to the latest saved local artifact only if that artifact still covers the current observation day/window
- if the saved artifact no longer covers the current observation day/window, the builder should fail explicitly

The purpose of this intake object is not to produce prose. Its purpose is to let the upstream market-judgment pass decide:

- what the market is trading today
- which assets belong in the basket
- which technical reads are signal versus noise
- which macro constraints materially change the current read

Current refinement note for intake:

- `ObservationIntake` should stay the pre-judgment truth surface, but it should no longer stop at raw section assembly alone
- it should still consume canonical technical reports through `Technical Report Sweep`, but that is not sufficient by itself
- the intake layer should also compress those technical inputs into judgment-ready state rows that make it easier to see:
  - role in the current mainline
  - current stage
  - highest-priority next trigger
  - main still-unconfirmed caution
  - why the asset belongs in today's basket
- this keeps the boundary explicit:
  - intake prepares truth for judgment
  - judgment decides `Mainline`, `Main Driver`, `Observation Basket`, `Confirmed Public Anchors`, `Not Confirmed`, and `Working Read`
  - package carries that judgment downstream to writing
- without that intake-side compression, the judgment layer risks collapsing back into macro-heavy prose with weaker asset ranking and weaker `Not Confirmed` / basket logic
- when this layer is handed to an AI worker, the prompt should be framed as a `judgment + package-selection` pass rather than as a final writing pass:
  - decide `main topic`, `mainline`, and `main driver`
  - decide which assets belong in the basket and why
  - decide which materials belong in the package's main reading surface versus supporting detail
  - preserve the most important `Not Confirmed` chain instead of collapsing early into one polished story
- under the repo's broader effect-first design rule, that judgment layer should be understood as doing work for the final market note, not as producing a decorative middle markdown:
  - it should pre-lock the mainline
  - pre-rank the 3-6 key assets that deserve the article spine
  - pre-separate main-reading materials from appendix-only detail
  - pre-preserve the most important unresolved question

Under this refinement, `writer-handoff` should continue to act as a downstream package review gate rather than absorbing the upstream market-judgment role.

### 8.2 `research-theme-report-owner`
- `research-theme-report-owner` should remain the top-level theme-maintenance mainline.
- It should be framed clearly as a `macro analyst` mainline.
- It should act as the upstream owner of the whole report-maintenance pass, not as a shallow label that immediately disappears into downstream workers.
- It should consume:
  - user request
  - latest relevant local materials
  - finalized report backbone
  - thesis and scenario context
  - package status and sufficiency signals
- It should not consume archive plumbing as if archive metadata were the report's truth surface.

Theme hierarchy rule:

- `theme` is not one flat layer
- top-level themes should stay few
- the system should usually contain more `regional economic themes` and `industry themes` than top-level themes
- `thesis` remains the finer-grained layer below those themes

Interpret the hierarchy like this:

- `top-level theme`:
  - cross-asset or cross-region regime layer
  - changes routing across many sectors, countries, or sleeves
  - should be rare
- `regional economic theme`:
  - country, region, or policy-economy branch with enough recurrence to deserve standing maintenance
- `industry theme`:
  - sector, value-chain, or capability-stack branch with enough repeated evidence to deserve standing maintenance
- `thesis`:
  - narrower durable judgment that may later fold into an existing theme or seed a new middle-layer theme

Promotion rule:

- the system should not jump from a cluster of related theses directly into a fresh top-level theme by default
- first ask whether the evidence more naturally supports a `regional economic` or `industry` theme
- only create a new top-level theme when the object clearly governs many regional/industry branches rather than one sleeve

Its task is not merely "write a long note about a theme". Its task is to maintain:

- the current theme framework
- active scenario branches inside that framework
- the evidence set that materially changes the framework
- the downstream report artifact

Current preferred ownership:

- review the user's request
- review the newest relevant materials
- judge whether the material set is current enough for the requested report
- judge whether the current material set is sufficient
- decide the report scope for this pass
- decide which objects should enter the package
- add local adhoc brief comments for the downstream writer, such as:
  - what changed in direction
  - which contradiction is central now
  - what framing to emphasize
  - what framing to avoid

Current preferred pass types inside `research-theme-report-owner`:

- `report_refresh`:
  - the existing report needs a real refresh pass against newer material
- `report_delta_scan`:
  - the user mainly wants to know whether recent news or recent materials actually change the current report
- `report_gap_review`:
  - the owner should inspect whether the current report is missing an important leg, stale branch, missing verification block, or unresolved contradiction
- `theme_candidate_discovery`:
  - the owner may use the current report, current materials, and current user request as the discovery anchor, and propose theme candidates implied by the evidence even when they are not merely adjacent to the current mechanism or scenario map
  - in practice, these candidates will usually be `regional economic` or `industry` themes before they are rare top-level-theme candidates
- `seed_theme_brief`:
  - the user points to a possible theme and asks for an initial framing brief, but this should still be treated as a bounded edge case rather than the general default behavior of theme maintenance

The important boundary is:

- `research-theme-report-owner` may do `report-anchored theme discovery`
- it should not silently become the repo's universal `global theme ideation` surface

That means:

- "summarize the recent news around this report and tell me what changed" fits naturally inside `research-theme-report-owner`
- "look at this current report and tell me whether there is a theme candidate worth opening" can also fit inside `research-theme-report-owner`
- "invent new themes from the broad news flow" should not be silently absorbed into this skill contract
- "here is theme x, help me think through whether it deserves a fuller theme object" can be temporarily handled here as `seed_theme_brief`, but it should remain explicitly marked as an edge pass type rather than the default center of gravity

For those discovery-oriented pass types, the owner's output should still stay explicit rather than conversationally vague. At minimum it should say:

- what the current report or current materials say
- what changed recently
- whether the change is large enough to justify a report update
- whether the change points to a nearby theme candidate
- whether that candidate is only adjacent evidence, thesis-only, a regional/industry theme candidate, or a rare top-level theme candidate
- what the recommended next step is

This also means:

- theme maintenance should not be used as the universal first router for any request that mentions a theme
- theme overlay inside another task line does not automatically justify routing the whole request here
- the theme-report flow should stay distinct from market observation, single-stock analysis, and portfolio decision even when they share some materials

Current preferred downstream order:

1. `research-theme-report-owner`
2. `research-theme-knowledge-and-package-curator`
3. optional current asset technical reports as package inputs
4. `writer-handoff`
5. shared writer gateway

In this order:

- `research-theme-report-owner` owns the pass
- `research-theme-knowledge-and-package-curator` works as the content-maintenance and package-preparation worker
- technical reports do not become a peer router; they remain optional package inputs
- `writer-handoff` does not regain upstream judgment authority

Current contract note for those optional technical inputs:

- current asset technical reports should be treated as reusable state reads, not as generic prose summaries
- the preferred truth surface is now:
  - upstream-ingested recent `30m` raw bars for the last five sessions
  - daily / weekly higher-timeframe anchors for calibration
- the writer/package layer should consume that prepared truth surface, not query market data ad hoc during writing
- the output contract should emphasize:
  - one explicit current stage
  - one highest-priority next trigger
  - confirmation and failure conditions
  - the main still-unconfirmed caution
  - why the asset matters for downstream market reading
- prefer result clarity and reminder value over enforcing one rigid house style
- when prompt wording is revisited later, keep the stable mainline:
  - read recent `30m` path first
  - calibrate with higher-timeframe anchors
  - state one decisive current stage early
  - state one highest-priority next trigger
  - state the main caution / still-unconfirmed point
  - explain downstream relevance beyond standalone chart commentary

Current naming direction:

- `research-theme-report-owner` is currently the preferred name because it matches upstream ownership more clearly than the older updater wording

### 8.2.1 `routing-current-macro-priority-router`

`routing-current-macro-priority-router` should now be treated as a transitional-but-still-useful midstream routing layer rather than as a hidden top-level router.

Current contract direction:

- it should be used only after top-level task mode is already identified
- it should not decide whether a request belongs to `single-stock analysis`, `portfolio decision`, `news check`, or other non-theme-first paths
- it should choose the leading macro/theme branch only inside the already-confirmed macro path
- when another mainline needs macro context, it may provide a `theme overlay` recommendation without stealing first authority

In practical terms:

- if the task is truly a macro market-interpretation request, this router may choose the leading theme and then send the task toward `research-current-market-reporter`
- if the task is truly theme-maintenance work, this router may choose the leading theme and then send the task toward `research-theme-report-owner`
- if the task is really `portfolio decision` or `single-stock analysis`, the top-level router should keep first authority there, and `routing-current-macro-priority-router` should be used only when a macro overlay is still useful

That means the current router is still systemically useful, but in a thinner role than before.

### 8.3 `writer-handoff`
`writer-handoff` is the downstream writer step.

Current review direction:

- do not assume this object owns the shared writing exit just because it appears immediately before the shared writer gateway
- keep the distinction explicit between:
  - top-level task line
  - AI-facing writer handoff contract
  - shared writer gateway

Current preferred reading:

- `writer-handoff` is increasingly closer to a `package review gate` or reviewer step than to an independent writer identity
- its most justified role is to judge whether a package is ready, what is missing, and whether the package may proceed into the shared writer path
- any prose generation that still happens here should be treated as downstream consequence of a passed gate, not as the reason this object exists

Current contract:

- `writer-handoff` should not be treated as a top-level mainline
- it is a downstream writer/report handoff step rather than a universal front-door analysis skill
- it should receive:
  - the finished package
  - the local adhoc brief from the upstream owner
  - any stable shared writer requirements
- it should not retake:
  - material review authority
  - package-selection authority
  - top-level report-scope authority
  - first-pass macro analysis authority

Current preferred use:

- use this object as the `package review gate`
- let it return `ready_to_write` or `need_more_detail`
- let the shared writer gateway remain the actual prose-generation surface
- do not let the existence of this skill imply a separate analyst persona or a separate top-level task line
- when reused under `research-current-market-reporter`, keep it as a thin sufficiency gate rather than letting it restate the whole routing or package-building story
- for `market observation`, prefer a deterministic gate implementation that checks package completeness and judgment presence rather than sending the package through a second AI review pass
- when the gate finds gaps, do not block normal report delivery by default; persist the gate checklist alongside the final market-observation markdown so the PM can see what was present, what was missing, and what writer direction was preserved
- this means the report artifact may carry both:
  - the PM-facing article body
  - a downstream `Writer Handoff Checklist` appendix for feedback and auditability

If the object ultimately does nothing beyond passing `package + brief` into the shared writer gateway and returning the resulting prose, then the longer-term cleaner design may be:

- retire the skill-level name entirely
- explain this step directly inside the `writer gateway layer`

### 8.3.1 `research-theme-knowledge-and-package-curator`

`research-theme-knowledge-and-package-curator` is the worker underneath `research-theme-report-owner`.

It is no longer best understood as "the place where theme ownership lives". It becomes the worker that:

- updates theme/scenario/thesis content structure
- maintains knowledge-layer links
- prepares package content under the scope decided upstream
- supports report maintenance without owning the top-level report pass

Current contract split inside this worker:

- `knowledge mode`:
  - refresh theme/scenario/thesis structure
  - maintain reusable knowledge links
  - update subtheme and thesis-facing content
- `report mode`:
  - assemble the writer-facing package
  - preserve source-heavy evidence
  - run the package through the writer-facing sufficiency gate
  - hand the package to `writer-handoff`

This means `research-theme-knowledge-and-package-curator` is a real worker contract, not merely a cosmetic rename of older thesis-centered wording.

### 8.3.2 Theme-Report Chain Status

The current theme-report chain should now be treated as the repo's active stable naming and responsibility picture:

1. `research-theme-report-owner`
2. `research-theme-knowledge-and-package-curator`
3. optional technical inputs
4. `writer-handoff`
5. shared writer gateway

What is already stable:

- upstream ownership belongs to `research-theme-report-owner`
- content maintenance and package preparation belong to `research-theme-knowledge-and-package-curator`
- downstream writer gating/drafting belongs to `writer-handoff`
- technical reports remain package inputs rather than peer routers

What is still intentionally not overclaimed:

- whether `writer-handoff` should remain a visible skill forever
- how broad the future shared writer gateway abstraction should become
- whether other non-theme report flows should reuse exactly the same handoff contract

### 8.4 Company financial, single-stock, and portfolio contracts

#### Company financial analysis

`research-company-financial-analysis` should be treated as the company / financial report mainline.

Current review direction:

- its first authority should be the company and its financial evidence, not the ticker tape
- the task is PM-facing, but PM-facing output does not automatically mean portfolio-decision authority
- the workflow should integrate:
  - company source packet
  - `single_asset_dossier` or `private_company_dossier`
  - Source Cards and Typed Claims
  - filings, earnings, transcripts, issuer voluntary disclosures, public comps, and valuation surfaces
  - secondary-market surfaces only as private-company pricing context
- only after that integrated company read should the workflow move into ticker/tape action framing or portfolio action language

This means company financial analysis should not be silently absorbed into:

- single-stock analysis
- theme maintenance
- market recap
- portfolio decision
- pure Digestion expert output

Current contract direction:

- keep `company-first` authority
- use Digestion expert artifacts as the evidence firewall
- consume `single_asset_dossier` for listed-company subjects
- consume `private_company_dossier` for private / pre-IPO subjects
- preserve `permission_level`, `confidence_cap_reason`, `allowed_use`, `blocked_uses`, and cannot-know boundaries
- produce a PM-facing company report or writer-ready company package rather than a chat-only answer
- route to `research-single-stock-analysis` only when the user asks how the listed security trades now, whether it is actionable, or what the tape says
- route to `operation-portfolio-decision` only when the user asks what the book should do

Routing rule:

```text
business / financial / valuation memo -> research-company-financial-analysis
ticker now / tape / actionability / technical state -> research-single-stock-analysis
both requested -> company-financial first, then single-stock or portfolio
```

#### Single-stock analysis

`single-stock analysis` is now ready to be treated as a real AI-facing mainline contract rather than a future placeholder.

Current review direction:

- its first authority should likely be closer to `macro analyst` than to immediate `portfolio manager`
- the task is still PM-facing, but PM-facing output does not automatically mean PM-first routing
- the workflow should integrate:
  - ticker technical state
  - local theme overlays
  - thesis context
  - current market meaning
- only after that integrated read should the workflow move toward more direct portfolio-action language

This means single-stock analysis should not be silently absorbed into:

- theme maintenance
- portfolio decision
- pure technical-report writing
- company financial analysis when the user is asking for ticker / tape / actionability

It is its own mainline.

Current contract direction:

- keep `ticker-first` authority
- use deterministic technical state as the opening truth surface
- use local theme context as overlay rather than first authority
- use thesis context only after the stock/tape read is already grounded
- produce a PM-facing single-stock package and draft rather than a chat-only answer
- allow direct action framing such as `actionable now`, `watchlist only`, or `structurally weak`
- consume a company-financial report as upstream context when the user asks for both business analysis and ticker actionability
- move into `portfolio decision` only when the task explicitly becomes about sizing, hedge sequencing, target book, or execution plan

#### Portfolio decision

`portfolio decision` is now ready to be treated as a real AI-facing mainline contract rather than a future placeholder.

Its first authority should remain `portfolio manager`.

This mainline should start only after upstream interpretation is sufficiently stable. It is the task line that turns:

- portfolio state
- risk constraints
- active themes
- technical state
- current market interpretation

into:

- debate
- decision
- target book
- execution preview

Current contract direction:

- start only after upstream interpretation is sufficiently stable
- consume portfolio state, policy envelope, active themes, technical state, and account review context as decision inputs
- produce decision-facing artifacts rather than more upstream interpretation
- keep `single-stock analysis` and `theme` interpretation as inputs, not hidden substitutes for portfolio authority
- make explicit whether the right answer is `open`, `add`, `reduce`, `close`, `hold`, or `watch`
- keep debate-first and action-first outputs distinct
- move into target-book or execution-preview language only after the decision frame is explicit

The practical PM questions this mainline should answer are closer to:

- what does this mean for my current book
- how should I position
- how should I defend
- what should I do first

So `portfolio decision` should not stop at abstract recommendation language. It should explicitly surface:

- current book impact
- priority ordering across actions
- defense-first versus offense-first framing
- which changes belong to immediate action versus watchlist status

Current preferred pass types inside `portfolio decision`:

- `book_defense`:
  - the user mainly wants to know how to cut fragility, reduce drawdown risk, or defend the current book against an active shock
- `rebalance_trim_add`:
  - the user wants to know what to trim, what to add, and in what order
- `hedge_priority`:
  - the user wants to know which risk to hedge first and which hedge is actually highest priority
- `wait_no_action`:
  - the real task is to determine whether the correct PM action is to wait, do nothing, or only maintain watchlist posture
- `offense_build`:
  - the user wants to know how to build offense after interpretation is already stable enough to support new risk

These pass types matter because your practical PM conversations are usually not asking for a generic `decision artifact`.
They are more often asking:

- where the current book is fragile
- whether risk should be reduced on repair rather than in chaos
- whether a move deserves hedge, trim, watchlist, or no action
- whether offense should wait until defense is done first

So this mainline should also preserve a few practical PM distinctions:

- do not treat all risk reduction as the same thing; trimming fragile high-beta or near-dated exposure is not the same as cutting core holdings
- do not assume the correct defense is to chase the headline winner; sometimes the right move is to avoid adding new exposure and instead clean the weakest existing risk
- do not assume `action now` beats `wait`; `wait_no_action` is a valid outcome when the market window is chaotic but the structure is not yet clear
- when multiple actions compete, ordering matters: what to do first is part of the output, not an optional afterthought
---
## 8.5 Current Stable Names Versus Open Questions

To avoid future drift, distinguish clearly between `stable now` and `still open`.

Stable now:

- `routing-task-mode-router`
- `research-theme-report-owner`
- `research-theme-knowledge-and-package-curator`
- `writer-handoff`
- `research-current-market-reporter`
- `research-company-financial-analysis`
- `research-single-stock-analysis`
- `operation-portfolio-decision`
- `research-external-learning`

Stable substeps, not top-level mainlines:

- `research-theme-priority-updater` under theme maintenance / prioritization surfaces

Still open:

- whether `routing-current-macro-priority-router` should keep its current name after the top-level router becomes explicit
- whether `writer-handoff` should remain a visible skill or later collapse into a more explicit writer-gateway layer
- whether any additional recurring mainline should be promoted above the current eight-item inventory

This distinction matters because the repo now has enough settled theme-routing structure that further edits should not reopen the already-fixed naming chain unless new evidence shows a real mismatch.
---
## 9. Relationship To Archive-First Research Memory
This routing document depends on the repo's archive-first design.
It assumes:
- `data/research` remains the canonical research root
- `source_collection` remains a routing registry, not a cosmetic label
- `messages`, `snapshots`, `theme_update_drafts`, `themes/reports`, and `thesis_notes` remain distinct layers
It also assumes:
- deterministic package assembly should happen upstream
- external writing should consume package truth
- builder/package code should not be reabsorbed into vague prompt-time behavior
This document therefore acts as a top-level routing companion to `research_10_thematic_workflow.md`, not as a replacement for it.
---
## 10. AI-Facing Writing Standard For Rules, Skills, And Top-Level Design
All future rules, skills, and top-level design docs in this area should be written with an explicit `AI-facing detail first` posture.
That means:
- prefer detailed explanation over neat compression
- do not optimize for skim-first readability at the cost of losing task boundaries, routing rules, handoff logic, or ambiguity resolution
- explain which nearby concepts are easy to confuse
- allow summaries only after the detailed contract is already clear
This standard exists because premature compression is itself one of the recurring sources of routing drift in this repo.

### 10.1 How To Use The Skill-Writing Meta-Skill In This Redesign

The repo now also has a portable meta-skill for writing or rewriting skills:

- `09_soul/skills/bestpractice_skill_writing.md`

In the current redesign round, that file should be treated as the `authoring law for skills`, not as a template to be copied into each local skill.

Its role is:

- define how a skill should be written
- define how to judge whether a skill contract is actually usable
- prevent skills from collapsing into long SOP-style scripts

Its role is not:

- to replace this document as the architecture truth surface
- to provide the routing map of this repo
- to be pasted verbatim into every `SKILL.md`

Use the layers in this order:

1. this document defines the repo's routing and responsibility architecture
2. the meta-skill defines how individual skills should be written
3. concrete `.cursor/skills/*/SKILL.md` files define the local task contracts

In other words:

- this document answers `what structure do we want`
- the meta-skill answers `how should a skill express that structure well`
- the concrete skill answers `what should this one agent task do`

For the current redesign, apply the meta-skill mainly as a review checklist against the most important local skills:

- `research-theme-report-owner`
- `research-theme-knowledge-and-package-curator`
- `writer-handoff`
- later, `single-stock analysis`
- later, `portfolio decision`

For each of those skills, review at least these questions:

- is the target result explicit
- can the agent judge completion from the acceptance standard
- are the usable resources and hard boundaries explicit
- is the output artifact clear
- is the file still enabling rather than SOP-heavy

The current preferred use is therefore:

- read the meta-skill before writing or heavily rewriting a local skill
- use it to critique the skill draft
- land only the local conclusions into the actual skill file

Do not duplicate the whole meta-skill into each skill file, because that would waste context window and recreate documentation bloat under a different name.

### 10.2 Result-First Rule For New Docs

When writing any new doc during this redesign, stop first and re-evaluate the desired result before writing the document body.

At minimum, answer:

- what behavior or routing decision should become more reliable after this doc exists
- who is the real reader: router, worker skill, writer step, or human reviewer
- what completion test should the reader be able to perform after reading it
- what output artifact or contract should become clearer
- what nearby scope should remain out of this document

Only after those questions are clear should the document body be written.

This rule exists because a clean-looking new doc is not automatically a useful doc. In this redesign round, a document is only good if it makes routing, ownership, handoff, or completion judgment more reliable.
---
## 11. Practical Reading Rule
When reloading this part of the architecture, prefer this order:
1. AI Native Trading Operating System [System-Operating-View]
2. Task Intake Routing Contract (this document)
3. Knowledge Base And Memory System [Knowledge-Memory]
4. Thematic Workflow [Research-Thematic-Workflow]
5. Analysis Platform And PM Workspace [Analysis-PM-Workspace]
If the question is specifically about implementation surfaces, then continue into:
- `.cursor/skills/`
- `src/writers/`
- `src/tools/draft_*`
- `src/cli/tradectl.py`
---
## 12. Machine Audit Runtime Surfaces

```yaml
runtime_surface_ledger:
  - surface: registry
    projection: codex
    path_or_command: 09_codex/routing/task_mainlines.md
    owner: designDoc/the_task_routing.md
    doc_claim: Codex-local projection of task mainlines, first authority, truth surface, skill contract, and operator move.
    sync_obligation: update when this document adds, removes, renames, or reclassifies a top-level mainline.
    status: active
  - surface: skill
    projection: codex
    path_or_command: 09_codex/skills/routing-task-mode-router/SKILL.md
    owner: designDoc/the_task_routing.md
    doc_claim: Codex-side AI-facing routing skill for matched_mainline and first_authority decisions.
    sync_obligation: update when routing output fields, overlay rules, or stable mainline inventory change.
    status: active
  - surface: skill
    projection: cursor
    path_or_command: .cursor/skills/routing-task-mode-router/SKILL.md
    owner: designDoc/the_task_routing.md
    doc_claim: Cursor-side projection of the same top-level routing contract.
    sync_obligation: keep semantically aligned with the Codex router and this T0 doc.
    status: active
  - surface: registry
    projection: codex
    path_or_command: 09_codex/skills/INDEX.md
    owner: 09_codex/skills/INDEX.md
    doc_claim: Lists mainline skills, substeps, downstream gates, and specialist helpers according to this routing contract.
    sync_obligation: update when mainline/substep classification changes.
    status: active
  - surface: runner
    projection: runtime_agnostic
    path_or_command: src/writers/service.py
    owner: designDoc/the_tradecli_code_management.md for code admission; this doc for routing boundary only
    doc_claim: writer gateway is downstream of task mainline and package sufficiency, not a top-level router.
    sync_obligation: update this routing boundary if writer gateway semantics change.
    status: active
verification_hooks:
  - ./.venv/bin/python -m pytest tests/test_design_doc_t0_layer_ids.py -q
  - manual routing projection check: compare this doc's top-level mainline inventory against 09_codex/routing/task_mainlines.md and 09_codex/skills/INDEX.md
```

---
## 13. Status
This document is currently `active_draft`. It is the current long-lived bridge contract surface for top-level task routing and layer separation, but the review-gate fields in `## 0. Contract Capsule` and `## 12. Machine Audit Runtime Surfaces` remain the active promotion surface before this doc should move to `status: active`.
An active batch-tracking companion may continue to exist under:
- `.cursor/context/update_batches/`
It sits between the system-level operating-system view and the more specific AnalysisPlatform / research-memory docs, so the canonical design position for this topic should live here rather than only in update-batch working notes.

For the current round, all design proposals in this topic should be written here first, reviewed here, and only then landed into lower-level runtime surfaces.

Current status for the theme-report chain:

- naming has been migrated to `research-theme-report-owner`, `research-theme-knowledge-and-package-curator`, and `writer-handoff`
- the skill/doc/runtime naming surface has been aligned around that chain
- the remaining work in this area is no longer first about renaming; it is mainly about strengthening nearby contracts such as `single-stock analysis`, `portfolio decision`, and any future writer-gateway generalization

## 14. References

- `[System-Operating-View]` [AI Native Trading Operating System](ai_native_trading_operating_system.md)
- `[Knowledge-Memory]` [Knowledge Base And Memory System](knowledge_base_and_memory_system.md)
- `[Research-Thematic-Workflow]` [Thematic Workflow](research_10_thematic_workflow.md)
- `[Analysis-PM-Workspace]` [Analysis Platform And PM Workspace](analysis_platform_and_pm_workspace.md)
- `[T0-Doc-Review]` [Design Doc Review Gate Contract](the_design_doc_management.md)
- `[T0-External-Worker]` [External Worker Execution Contract](the_external_agent_management.md)
- `[T0-Runtime-Code]` [Runtime Code Admission And Audit Contract](the_tradecli_code_management.md)
