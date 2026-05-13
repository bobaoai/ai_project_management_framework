---
name: support-external-agent-builder
description: Builds auditable external agents for Claude Code CLI, DeepSeek, OpenAI, Cursor subagents, and other worker surfaces. Use when converting chat-level prompts into stable runner artifacts, creating external-agent modules, assembling worker prompts, or preparing an external review / extraction / triage run.
---

# External Agent Builder

## What This Skill Does

Use this skill to turn an external AI call into a reusable external-agent surface.

It owns the runner architecture:

- stable prefix held by a builder or template
- `GENERAL_MODULE`, `CUSTOMIZE_MODULE`, and `DATA_DEPENDENT_MODULE`
- dynamic input appended last
- embedded evidence instead of bare local path lists
- preflight checks before quota work
- auditable output paths and hashes

It does not own every worker type directly. Worker-specific contracts live as subskills in this directory.

## Subskills

Read the matching subskill before building the runner:

- [`external_review_builder.md`](external_review_builder.md): doc / skill / design-artifact external reviews using `src/tools/build_doc_review_prompt.py`

Future peer subskills can cover DeepSeek source-card workers, image triage workers, evidence extractors, or other external-agent families.

## Required Local Inputs

Read before building:

- `09_soul/skills/bestpractice_external_agent_builder.md`
- `09_soul/skills/bestpractice_external_worker_general_module.md`
- `09_soul/skills/external_writer_merge_rule.md` when merging external writer drafts back into a canonical artifact
- `09_soul/skills/bestpractice_prompt_boundary.md`
- `09_soul/skills/bestpractice_skill_writing.md`
- the relevant subskill in this directory
- the target artifact, source packet, or object selection
- the local references that define the worker's task contract

## Core Invariants

The runner prompt is assembled, not hand-written.

Generic shape:

```text
stable runner prefix
  + GENERAL_MODULE
  + CUSTOMIZE_MODULE
  + DATA_DEPENDENT_MODULE
  + dynamic object suffix / embedded packet
```

The stable prefix remains stable across a batch. Task-specific intent goes into `CUSTOMIZE_MODULE`. Input-family semantics and evidence boundaries go into `DATA_DEPENDENT_MODULE`. Per-object facts, paths, hashes, and source packets stay in the dynamic suffix.

The canonical general module is `09_soul/skills/bestpractice_external_worker_general_module.md`. Builders should embed only its executable `WORKER_CHARTER / GENERAL_MODULE`, not the surrounding metadata or the raw upstream principle files it distilled.

Do not tell the worker which external surface is being used unless that fact changes the task. Execution surface is caller control-plane; task goal, allowed evidence, required judgment, output schema, and uncertainty rules are worker task-plane.

Silent violation signal:

- the runner prompt is a standalone manually written file that bypasses a builder or stable template
- task-specific requirements are mixed into the stable prefix
- local references are listed as paths but their content or source packet is not embedded
- the run cannot report `general_module_hash`, `customize_module_hash`, `data_dependent_module_hash`, and `input_payload_hash`
- a stale output from an invalid prompt remains next to the regenerated prompt and can be mistaken for the valid result

## Preflight Before Running

Before launching any external agent:

- check whether another runner is active for the same target, prompt, object selection, or output path
- stop or wait on obsolete runs before starting a new one
- delete, rename, or explicitly mark stale outputs produced from bad prompts
- confirm the generated prompt or payload has no `MISSING FILE`
- confirm module and dynamic-input sections are present
- confirm embedded code fences or serialization boundaries do not break the prompt

Treat quota, auth, `429`, missing runner dependency, and systemic malformed output as hard blockers.

## Completion Standard

The handoff must name:

- `runner_family`
- `target_artifact` or object selection
- `prompt_path` or request payload path
- `manifest_path`, when the builder emits one
- `module_path`
- `embedded_references` or source packet path
- `input_payload_hash`
- external surface used, if a run was launched
- `output_path`, if a run was launched
- stale prompts / outputs that were stopped, deleted, renamed, or intentionally retained
- validation performed on the generated runner input

## Known Failure Pattern

The common failure is trying to fix a worker result by writing a better one-off prompt. That bypasses the runner architecture. Encode the difference as a module or subskill, then let the builder or stable template splice it into the runner input.
