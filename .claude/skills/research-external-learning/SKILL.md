---
name: research-external-learning
description: "Studies external repos, papers, products, public skill systems, architectures, or workflows and turns them into durable local design judgment. Use when the user asks what an outside source teaches this repo, whether to adopt a method, or how an external research/workflow pattern should enter designDoc/learning_library."
---

# External Learning Research

## What This Skill Does

Use this skill when the task is to study outside material so `trading_platform` can learn from it.

This skill is for:

- external repo / paper / product / architecture / public skill-system research
- comparing an outside workflow with this repo's current system
- extracting design pressure, reusable patterns, and adoption boundaries
- producing durable learning-library artifacts under `designDoc/learning_library/`

The defining standard is that the final article should read like Bokan's own research judgment: direct, systems-oriented, source-grounded, and filtered through the local axiom set rather than written as a neutral web summary.

## Desired Result

The desired result is a durable local artifact that helps future work make better design decisions.

By the time this skill is done, the reader should be able to state:

- what the external source actually does
- which parts matter for `trading_platform`
- which parts should be adopted, adapted, rejected, or left as inspiration only
- how the lesson maps onto the repo's current `KnowledgeBase`, `AnalysisPlatform`, Hoveath, skill, routing, or writer layers
- what source evidence supports the judgment

If the result only summarizes the external source without changing local design judgment, this skill has failed.

## First Authority

Current persona:

- `research architect` posture inside Hoveath

Interpretation filter:

- read `09_soul/axioms/INDEX.md` first when the task is broad or strategic
- read the specific axiom files that match the question, especially when the result depends on user's thinking style
- use `09_soul/core/COMMUNICATION.md` as the writing style contract
- use `.claude/skills/support-deep-research-survey/SKILL.md` as the local Deep Research adapter
- use `09_soul/skills/workflow_deep_research_survey.md` as the portable method source

The external source supplies material. The local axioms supply judgment.

## Primary Truth Surfaces

Read these before writing:

- the external URL, repo, paper, docs, product page, article, or public criticism supplied by the user
- `09_soul/axioms/` for the user's thinking model
- `09_soul/core/COMMUNICATION.md` for prose style
- `.claude/skills/support-deep-research-survey/SKILL.md` for source-heavy research output placement
- `09_soul/skills/workflow_deep_research_survey.md` for the portable research method
- `designDoc/learning_library/README.md` for output placement and existing conventions
- relevant local design docs when the research may change architecture or routing, especially:
  - `designDoc/ai_native_trading_operating_system.md`
  - `designDoc/the_task_routing.md`
  - `designDoc/knowledge_base_and_memory_system.md`
  - topic-specific `designDoc/research_*.md` files when the lesson concerns research memory or PM workflows

## Research Method

Use the local Deep Research adapter as the execution bridge:

- `.claude/skills/support-deep-research-survey/SKILL.md` chooses the correct host output surface
- `09_soul/skills/workflow_deep_research_survey.md` supplies the portable broad-scan / overlap / URL-preservation method

For this mainline, the final output surface is `designDoc/learning_library/...`, not `data/research/messages/`.

Use the portable method this way:

- begin with a broad scan to identify the external source's real shape
- split deeper investigation into overlapping dimensions when the topic is large enough
- preserve URLs and direct quotes for important claims
- cross-check positive claims against critiques, alternatives, implementation details, or actual repo behavior
- deliver one final durable artifact; do not leave piles of intermediate notes unless the user explicitly asks for them

Runtime adaptation:

- in Cursor, use the available web/search/fetch and repo-inspection tools instead of assuming the exact external tools named in the source workflow
- use parallel subagents only when the topic is genuinely large enough to benefit from independent overlapping research
- for narrow source-reading tasks, direct reading plus targeted web search is enough

## Output Artifacts

Choose the output path by the job:

- external repo or public project note:
  - `designDoc/learning_library/repo_notes/<slug>.md`
- cross-source theme or architecture synthesis:
  - `designDoc/learning_library/topics/<slug>.md`
- decision-oriented research project:
  - `designDoc/learning_library/projects/<slug>/README.md`

The artifact should usually contain:

- `Source`
- `What It Is`
- `What Matters For Us`
- `Axiom-Lens Read`
- `Adopt / Adapt / Reject`
- `Design Pressure For trading_platform`
- `Open Questions`
- `Source Notes`

Section names may vary when another shape serves the reader better. The invariant is the reader end-state, not the exact headings.

## Style Contract

The prose should follow `09_soul/core/COMMUNICATION.md`:

- direct and judgment-forward
- no generic praise
- no marketing adjectives
- concrete enough that a future agent can reuse the judgment
- source-grounded when making claims about the external material
- written about the system and the world, not about the drafting process

When an axiom is explicitly named, include its meaning inline on first mention in the reply or artifact, such as `T10（Index First, AI For Gaps）`.

## Boundary Versus Neighboring Mainlines

Use `ingestion-research-archive-operator` when the task is to ingest or promote local research materials under `data/research/`.

Use `ingestion-source-connector-designer` when the task is to design an intake boundary such as Gmail, RSS, broker, market data, or file-drop connectors.

Use `research-theme-report-owner` when the task is to update a standing market theme report.

Use this skill when the external material is being studied as a design, architecture, workflow, or operating-model lesson for this repo.

## Completion Standard

This skill is complete only when the final handoff names:

- `external_source`
- `local_output_path`
- `main_local_lesson`
- `adopt_adapt_reject`
- `axiom_lens_used`
- `source_evidence`
- `follow_up_target`

Accepted outcomes:

- a new or updated learning-library artifact
- a scoped research plan when the topic is too large to execute in one pass
- a blocked result that names exactly which source access or evidence gap prevents responsible judgment

## Failure Signals

Treat these as signs the skill failed:

- the output could have been written without reading local axioms
- the output summarizes the external source but never says what should change locally
- the article sounds like generic analyst prose instead of Bokan-aligned systems judgment
- claims about the external source lack URLs or quoted evidence where verification matters
- the output lands in chat only when the lesson should become a reusable local artifact
- the final external-learning artifact is imported only as a message archive object instead of written to `designDoc/learning_library/`
- the task silently turns into market theme maintenance, archive ingest, or connector design

## Example Triggers

- “研究一下这个 GitHub repo，对我们有什么可以借鉴”
- “把这个外部 workflow 用在我们的 external learning research 上”
- “这篇文章讲的 context infrastructure 对 Hoveath 有什么启发”
- “看这个 public skill system，哪些应该进我们的 Routing”
- “比较这个外部项目和我们的 KnowledgeBase / AnalysisPlatform”
- “研究一下 private-company / pre-IPO / secondary-market PPS 方法，沉淀成我们自己的研究流程”
