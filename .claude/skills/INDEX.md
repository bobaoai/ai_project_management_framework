# Skills Index

This file explains the execution order of `.claude/skills/`.

For the underlying routing and layer-separation truth, defer first to:

- `designDoc/the_task_routing.md`
- the mainline and substep contracts in the individual `SKILL.md` files

Do not read all skills as peers.
The key distinction is whether a skill is:

- a top-level entry router
- a mainline contract
- a substep under a mainline
- a downstream gate or writer-facing step
- a specialist/design helper

## Naming Prefixes

Skill names should expose their layer before their task:

- `routing-*`: entry routing or overlay routing; chooses owner, does not own the artifact.
- `ingestion-*`: source intake, archive curation, read-content/image/source readiness.
- `digestion-*`: source packet, Source Card, Typed Claim, domain expert, dossier, decision brief.
- `research-*`: PM-facing research judgment, theme/thesis/single-stock/market interpretation.
- `operation-*`: PM / portfolio / risk / execution authority.
- `writer-*`: downstream package gate or prose writer.
- `engineering-*`: engineering review or repo-change verification.
- `support-*`: session support, handoff, compaction, or non-domain utilities.

Do not add unprefixed project skills unless the prefix taxonomy truly has no fit.

## 1. Top-Level Entry

Use this first when a request arrives and the owning task line is still unclear:

- `routing-task-mode-router`

This is the primary routing surface for:

- matching the `task mainline`
- identifying `first authority`
- pointing to the first truth surface
- deciding whether any overlay is needed

## 2. Mainline Skills

These are the primary task-line contracts:

- `ingestion-agentmail-inbox-triage`
- `ingestion-research-archive-operator`
- `research-current-market-reporter`
- `research-theme-report-owner`
- `research-company-financial-analysis`
- `research-single-stock-analysis`
- `operation-portfolio-decision`
- `research-external-learning`
- `digestion-independent-researcher`

Treat these as the main downstream destinations after top-level routing is stable.

`research-company-financial-analysis` owns PM-facing company financial / fundamental reports. It sits between Digestion company experts and ticker/tape-first single-stock analysis: use it when the desired artifact is a company memo, business / financial quality read, valuation bridge, public-comp read, or private-company / pre-IPO report. It handles public and private companies in one grammar; private-company subjects add secondary-surface and cannot-know boundaries.

When reading a mainline skill, prefer this order:

1. `Current persona`
2. `Current task`
3. `Primary truth surface`
4. `Output artifact`

The skill should first tell you what complete result it owns. Builder, package, gate, or writer details belong later as support structure rather than as the skill's public identity.

## 3. Mainline Substeps

These do useful work, but they are not top-level entry contracts:

- `digestion-company-expert`
- `routing-current-macro-priority-router`
- `digestion-interpretation-metaskill`
- `research-theme-knowledge-and-package-curator`
- `research-theme-priority-updater`

Typical meaning:

- `digestion-company-expert`: Digestion domain expert for one listed company; consumes an independent-research source packet and produces `CompanySourceCard`, `CompanyTypedClaim`, and `single_asset_dossier` before downstream company-financial or single-stock writing
- `routing-current-macro-priority-router`: macro-path chooser or overlay helper
- `digestion-interpretation-metaskill`: mines reusable analytical assets from reports/messages and routes them to Domain Experts; it does not draft thesis or evidence
- `research-theme-knowledge-and-package-curator`: worker under `research-theme-report-owner`
- `research-theme-priority-updater`: ranking/routing updater, not report owner

## 3.5 Thesis & Theme Analyst Sub-Cluster (Plan B v0.4 + charter alignment Phase B.0.7)

These six SKILLs form the **analyst sub-cluster** introduced in Plan B for the thesis-and-theme writing pipeline. They are NOT top-level entries — they always run under one of the existing controllers (`routing-task-mode-router`, `research-theme-report-owner`).

### Thesis sub-cluster (4 agents, strict execution order)

```
research-thesis-drafter  →  research-thesis-verifier  →  research-evidence-reviewer  →  research-thesis-adversary  →  research-evidence-reviewer
  (researcher)     (external fact-       (independent AI      (critic / pre-mortem,   (independent AI
                    checker, writes       review before PM     writes falsifiers,       review of adversary
                    evidence_record)      surface)             emits counter records)   records)
```

- `research-thesis-drafter` — writes `thesis_note v1.5` prose body + `claims[]` + `cross_theme_links[]` + `lifecycle_stage: draft`
- `research-thesis-verifier` — appends ONE fixed-format `external verification: <verified|partial|pending> – <line>` to `notes`; does NOT change drafter's prose; emits perplexity_log row(s) + verifier evidence_record JSON with `ai_verified=false` + `ai_review_log=[]`; US quote-bearing checks must use `quote_provenance_and_source_surface_contract.md`; PM-facing verdict waits for `research-evidence-reviewer`
- `research-thesis-adversary` — writes `falsifiers[]` (≥1 required) + `scenario_triggers[]` (status=pending) + `next_review_trigger`; promotes lifecycle to `active`; emits one `evidence_record_v0_2` per `counter_evidence_observed[]` entry with `ai_verified=false` + `ai_review_log=[]`; adversary never self-verifies
- `research-evidence-reviewer` (charter alignment B.0.7) — independent AI gate. Reads each evidence_record + linked perplexity_log rows, re-judges trust_tier (per [`designDoc/evidence_source_trust_contract.md`](../../designDoc/evidence_source_trust_contract.md)) + belief_delta coherence + source-content support; for quote-bearing records also audits quote provenance, official-source attempts, source surface, surface timing, oral-surface attempts, and secondary-only downgrade per [`designDoc/quote_provenance_and_source_surface_contract.md`](../../designDoc/quote_provenance_and_source_surface_contract.md). Appends one `ai_review_log[]` entry; flips `ai_verified=true` IFF all required sub-verdicts pass AND schema R1 already satisfied. Cannot self-author (reviewer_persona enum excludes drafter / verifier / adversary / scanner / sweeper) and cannot edit body fields (only ai_review_log + updated_at_utc + the ai_verified flip)

### Theme sub-cluster (2 agents, conditional)

- `research-theme-discovery-scanner` — bottom-up: scans `messages_index.jsonl` in an explicit `as_of_utc` window, clusters into candidates not yet covered by any existing theme; outputs `theme_candidates/<scan_id>.json` + `.md` for PM review
- `research-theme-bootstrapper` — dual-stage:
  - **Stage A** (arbitration) — given a candidate, scans ALL existing themes on 5 similarity dimensions (3 deterministic + 2 LLM); proposes ONE of `admit_new | merge_into_existing | narrow_existing_then_admit | carve_out_from_existing | subordinate_to_existing`; outputs `bootstrapper_proposal.json` + `bootstrapper_proposal.summary.md`
  - **Stage B** (execution) — given owner's round-2 decision, executes the chosen branch against `themes/metadata/`. STRICT input isolation: Stage B does NOT see Stage A's proposal — only the owner-confirmed plan
  - `subordinate_to_existing` is currently a `raise` (not implemented); use `merge_into_existing` + write a thesis_note instead

### Three theme-creation entry points (designDoc/research_05 §4)

| # | Entry path | Routing |
|---|---|---|
| 1 | PM-driven ("请帮我开 theme on X") | `routing-task-mode-router` → `research-theme-report-owner` round-1 → `research-theme-bootstrapper` Stage A → owner round-2 → bootstrapper Stage B |
| 2 | AI bottom-up ("扫一下资料堆挖新题材") | `routing-task-mode-router` → `research-theme-discovery-scanner` → PM picks candidate → `research-theme-report-owner` round-1 → bootstrapper Stage A → owner round-2 → bootstrapper Stage B |
| 3 | Update existing theme | `routing-task-mode-router` → `research-theme-report-owner` (no bootstrapper involved) → `research-theme-knowledge-and-package-curator` |

### Independent per-agent testing

Each of the 5 agents has its own fixture set under `tests/thesis_cluster_fixtures/<agent_id>/` and is invoked through:

```bash
./.venv/bin/python -m src.cli.tradectl test-thesis-agent <agent_id>
```

The bootstrapper runs **6 sub-cases** (Stage A + 4 Stage B execution branches + 1 Stage B raise branch).

## 4. Downstream Gate And Writer Steps

These should not be mistaken for upstream mainlines:

- `writer-handoff`
- `writer-asset-technical`

Current reading:

- `writer-handoff` is a downstream `package review gate`
- `writer-asset-technical` is a specialized writing step for deterministic technical packets
- these steps should stay thin and should not overload the upstream mainline with redundant control-plane context

`research-external-learning` belongs in mainline skills, not specialist helpers, because it owns a recurring top-level workflow: studying outside systems and turning them into durable local design judgment under `designDoc/learning_library/`.

`digestion-independent-researcher` belongs in mainline skills because it owns a recurring cross-asset Digestion workflow: independently assemble local/external sources for a company, crypto project, or asset; archive and link sources; build an asset source packet; select a domain expert route; and produce a dossier, decision brief, package candidate, report draft, or blocked handoff.

## 5. Specialist Or Design Helpers

These are narrower or design-focused helpers:

- `ingestion-source-connector-designer`
- `ingestion-source-family-operator`
- `ingestion-image-review-reader`
- `engineering-change-review`
- `digestion-expert-factory`
- `support-deep-research-survey`
- `support-external-agent-builder`

Use them when the task is connector architecture, source-family message ingestion readiness, source-image interpretation, independent engineering plan or exact-commit review, Digestion expert creation/maintenance, Deep Research output-surface adaptation, or external AI runner construction, not as default entry points for ordinary research/PM workflows.

`digestion-expert-factory` creates and maintains domain experts, source-card patterns, typed-claim firewalls, company templates, crypto modules, and generated expert skill projections. It produces experts; it does not run one-off asset research.

`support-deep-research-survey` adapts the portable `09_soul/skills/workflow_deep_research_survey.md` method to the local artifact surface chosen by the owning mainline. Under `digestion-independent-researcher`, Deep Research output must become a message archive object before it enters `source_packet.md`; under `research-external-learning`, the output remains a learning-library artifact.

`support-external-agent-builder` turns external AI calls such as Claude Code CLI, DeepSeek, OpenAI, Cursor subagent, or external reviewer runs into stable runner artifacts: fixed prefix, canonical general module, task module, data-dependent module, embedded evidence, manifest hashes, preflight, hard-stop behavior, and auditable output paths. Its review-specific subskill is `support-external-agent-builder/external_review_builder.md`. It builds the runner surface; it does not replace the domain reviewer or decide the final PM-facing verdict.

`engineering-change-review` is governed by `designDoc/the_software_delivery.md` (Software Delivery). It organizes independent review of an exact engineering plan (CodeDesignBasis) before implementation, or of an exact commit after implementation, through the registered `engineering_change_reviewer` Module on the local Agent Runtime, and checks that the verdict binds to the reviewed plan or commit. It is review-only and does not edit the work under review.

## Routing Reminder

Preferred execution order:

1. route the request
2. enter the correct mainline
3. call substeps only when the mainline needs them
4. call downstream gate/writer steps only after upstream context is stable

For PM-facing lines such as `research-current-market-reporter`, the mainline should still read as the owner of a complete report artifact. Downstream gate/writer steps support that artifact; they do not replace the mainline's result contract.

If a skill is mentioned in a package, report, or writer path, that alone does not make it the owning contract.

This index is an execution-order aid, not a replacement for the bridge contract or the skill files themselves.

## Current New-Generation Center

The most stable result-first contracts right now are:

- `routing-task-mode-router`
- `research-theme-report-owner`
- `research-company-financial-analysis`
- `research-single-stock-analysis`
- `operation-portfolio-decision`
- `research-external-learning`
- `digestion-independent-researcher`
- `writer-handoff`

These should be treated as the current quality bar when rewriting older skills.
