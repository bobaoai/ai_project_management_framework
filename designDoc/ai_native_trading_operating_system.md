# AI-Native Trading Operating System

**Version 0.3.1 — 2026-05-07**

This document is a system overview for `trading_platform`.

It explains what the system is for and how the main conceptual views fit together. It is not a T0 authority layer. If this overview conflicts with a T0 or T1 Design Doc, the owning Design Doc wins.

## 1. What This System Is For

`trading_platform` is an AI-native investment cognition system.

Its job is not just to collect information or generate reports. Its job is to help a principal manager turn external material, market state, portfolio context, and prior memory into auditable changes in judgment.

The system supports five recurring kinds of work:

- collect and preserve source material
- turn source material into reusable analytical assets
- maintain themes, theses, scenarios, evidence, and portfolio context
- produce PM-facing packages, reports, briefs, reviews, and decision surfaces
- keep the links between Design Docs, Skills, Code, artifacts, and memory auditable

The current repo should be read as a layered workbench:

```text
source intake
-> canonical read surface
-> material object boundary
-> digestion / source understanding
-> research / analysis / PM workspace
-> package, report, decision, review
-> memory and audit loop
```

## 2. Three Primary Views

The older framework remains useful:

```text
Functional Modules
KnowledgeBase
AnalysisPlatform
```

The material underneath those labels has changed.

### 2.1 Functional Modules

Functional Modules describe the investment work the system performs.

| Module | Current meaning in this repo |
| --- | --- |
| `DataCollection` | Ingestion connectors, archive import, canonical source read surfaces such as `read_content.md`. |
| `InfoClassification` | Digestion routing, Source Cards, Typed Claims, expert artifacts, reusable framework extraction. |
| `PortfolioExposure` | Portfolio state, technical context, PM workspace constraints, exposures, and risk surfaces. |
| `OpportunityRanking` | Theme / thesis / scenario prioritization, research selection, current priority views. |
| `StructuredAdvice` | Writer packages, reports, decision briefs, monitoring plans, external review and writing loops. |

These are conceptual modules. The current contracts live in the owning Design Docs listed below.

### 2.2 KnowledgeBase

`KnowledgeBase` is the long-memory view, not one monolithic folder.

In the current repo, durable memory is split across:

- archive and source read surfaces
- ingestion state and source metadata
- Material Catalog object grammar for Raw Data, Operating Cycle Artifacts, Source Cards, Expert Artifacts, Evidence, Thesis, Scenario, Theme, and Technical Report
- Expertise capability contracts for frameworks, lenses, source-card patterns, claim firewalls, expert artifact schemas, and prediction grammar
- digestion Source Cards, Typed Claims, expert artifacts, and source packets
- research memory for themes, theses, scenarios, evidence, reports, and reviews
- artifact stores, sidecars, manifests, and runtime output state

The useful question is:

```text
Can a future reader recover what we saw, what we believed, why it changed, and which artifact or command produced the current state?
```

### 2.3 AnalysisPlatform

`AnalysisPlatform` is the current work surface where humans and AI agents organize judgment.

It combines:

- current source material
- current portfolio and exposure context
- active themes, theses, scenarios, and evidence
- technical and market context
- writer packages, reports, reviews, and decision artifacts
- stale / freshness / blocker state

The first implementation may be local files, CLIs, Codex / Claude Code / Cursor projections, and generated artifacts rather than a dedicated web UI. The important point is not the interface. The important point is that the system exposes current judgment and its evidence trail in a repeatable way.

## 3. Current Contract Owners

This overview does not own detailed operating rules. Use these owner docs for contract questions:

| Concern | Current owner |
| --- | --- |
| constitutional constraints, object ontology, surface ownership | `the_charter.md` |
| task entry, mainline, first authority, routing layer split | `the_task_routing.md` |
| artifact readiness, dependency closure, freshness, builder admission | `the_artifact_graph.md` |
| timestamp / date field semantics and comparisons | `the_timestamp_semantic.md` |
| Design Doc promotion, Contract Capsule, runtime ledger, review gate | `the_design_doc_management.md` |
| runtime code / command / schema admission and doc-skill-code-test sync | `the_tradecli_code_management.md` |
| external AI writing, review, image reading, formal review, model / CLI surfaces | `the_external_agent_management.md` |
| source intake and canonical read surfaces | `ingestion_00_overview.md` |
| material object boundaries across Raw Data, Operating Cycle Artifact, Source Card, Expert Artifact, Evidence, Thesis, Scenario, Theme, and Technical Report | `material_00_overview.md` |
| reusable analytical capabilities, expert frameworks / lenses, source-card patterns, claim firewalls, Expertise Application, expert artifact schemas, prediction grammar, and skill projection contracts | `expertise_00_overview.md` |
| source understanding, source cards, typed claims, expert subsystems | `digestion_00_overview.md` |
| research topology, theme / thesis / report workflows | `research_00_overview.md` |
| PM-facing workspace and analysis surfaces | `analysis_platform_and_pm_workspace.md` |

## 4. Current Data-To-Decision Flow

The current system is best understood as a pipeline with review loops, not as one chat loop.

### 4.1 Source Intake

Source intake gets external material into auditable local form.

It includes connectors, imports, archives, raw files, metadata, and canonical read surfaces. Its job is to preserve source truth and make it readable. It does not decide investment meaning.

Owner entry: `ingestion_00_overview.md`.

### 4.2 Digestion

Digestion turns canonical read surfaces into reusable analytical assets under Material Catalog object boundaries and selected Expertise capability rules.

It creates source-understanding outputs such as Source Cards, Typed Claims, Framework Cards, expert artifacts, source packets, and domain routes. Material Catalog owns the material object boundary; Expertise owns reusable capability rules; Digestion owns the execution and current schema details.

Owner entries: `material_00_overview.md`, `expertise_00_overview.md`, and `digestion_00_overview.md`.

### 4.3 Research And Analysis

Research and analysis use material objects, digestion outputs, portfolio context, technical context, and PM constraints to maintain themes, theses, scenarios, evidence, and reports.

This is where source-understanding becomes belief-relevant work. The PM remains the authority for belief-layer decisions.

Owner entries: `research_00_overview.md` and `analysis_platform_and_pm_workspace.md`.

### 4.4 Package, Report, Review, Decision

The system increasingly separates deterministic package assembly from AI writing, review, and final PM-facing artifacts.

Packages, reports, manifests, sidecars, and reviews are produced state. They do not become design authority by themselves. External models, CLIs, and workers are execution surfaces governed by External Worker Execution and owner Skills.

Owner entries: `the_artifact_graph.md`, `the_external_agent_management.md`, and the relevant T1 workflow doc.

### 4.5 Memory And Audit Loop

Every useful output should strengthen memory:

- what source was used
- what changed
- which object was updated
- which package / artifact / report was produced
- which command, skill, prompt, or external worker participated
- what still needs review

This is why the repo emphasizes canonical paths, runtime ledgers, verification hooks, and produced-state sidecars.

## 5. Runtime Projection View

The current system can be operated through multiple runtime projections:

- Codex
- Claude Code
- Cursor
- CLI / local tools
- future UI surfaces

No runtime projection is the system authority by itself.

Runtime projections should:

- read the appropriate Design Doc authority
- use admitted Skills for AI operating behavior
- call deterministic Code for repeatable execution and validation
- write outputs to artifacts, reports, sidecars, manifests, or runtime stores
- surface drift when Design Docs, Skills, Code, and produced artifacts stop matching

Runtime-specific startup and skill details belong in the runtime projection directories and skill files, not in this overview.

## 6. Time Horizon And PM Use

The system must preserve time horizon, not just directional opinion.

A position or theme may be:

- structurally positive
- tactically risky
- technically extended
- portfolio-constrained
- stale until new evidence arrives

This is why the system distinguishes themes, theses, scenarios, evidence, technical context, portfolio context, freshness, and PM decisions. A useful report should help the PM see both the durable thesis and the current path risk.

Detailed horizon, theme, thesis, and PM workflow rules belong in research and PM workspace docs.

## 7. Design Principles

- Source truth is preserved before interpretation.
- Digestion creates reusable source-understanding assets before research synthesis.
- Design Docs own what / why / boundary / authority.
- Skills own how an AI should act now.
- Code owns deterministic checks, commands, schemas, tests, and executable behavior.
- Produced artifacts hold generated state; they do not independently own design authority.
- Runtime projections are work surfaces, not the system constitution.
- The best output is not a chat answer; it is an auditable artifact, report, review, decision surface, or memory update.

## 8. Where To Go Next

Start with `designDoc/README.md` for the current T0 entry matrix.

For domain work:

- source intake: `ingestion_00_overview.md`
- reusable expertise: `expertise_00_overview.md`
- source understanding and expert subsystems: `digestion_00_overview.md`
- research and reports: `research_00_overview.md`
- PM workspace: `analysis_platform_and_pm_workspace.md`

For system-boundary work, use the T0 owner docs named in `designDoc/README.md`.
