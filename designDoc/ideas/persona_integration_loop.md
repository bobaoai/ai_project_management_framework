# Persona Integration Loop

## Goal

Define how `trading_platform` should embed `Hoveath` into daily development.

This is a host-repo implementation plan.
The portable standard now lives in `09_soul/core/DEVELOPMENT_INTEGRATION.md`.

## Scope

This doc answers local questions:

- where the persona already lives in this repo
- where integration is still weak
- which local files act as runtime projection
- where weekly distillation artifacts should go
- how local lessons should be separated from portable promotion candidates

It should stay specific to `trading_platform`.

## Current State In This Repo

The persona is already present in the control layer:

- `09_soul/core/SOUL.md`
- `09_soul/core/COMMUNICATION.md`
- `09_soul/core/PROJECT_ADAPTER_trading_platform.md`
- `AGENTS.md`
- `.cursor/rules/`

The repo also already has a strong local truth surface:

- `designDoc/` for architecture, strategy, and operating model
- `src/` for implementation truth
- `data/` for runtime artifacts and generated outputs
- `.cursor/context/update_batches/latest.md` for current implementation state

The weak point is not persona description.
The weak point is loop closure.

Current gaps:

- development chats are not consistently distilled into local memory
- local lessons are not consistently summarized into update batches
- portable promotion candidates are not consistently separated from repo-local lessons
- runtime projection changes still happen ad hoc rather than through a recurring review loop

## Local Runtime Projection

In `trading_platform`, the active runtime projection of `Hoveath` should remain concentrated in:

- `AGENTS.md`
- `.cursor/rules/`
- `09_soul/core/PROJECT_ADAPTER_trading_platform.md`
- `09_soul/core/USER.md`

These files should stay short and active.
They are not long-term historical logs.

## Session Start For This Repo

Before meaningful design or implementation work, the runtime should continue reading:

- `09_soul/core/USER.md`
- `09_soul/core/PROJECT_ADAPTER_trading_platform.md`
- `AGENTS.md`
- relevant `.cursor/rules/`
- `designDoc/README.md`
- `.cursor/context/update_batches/latest.md`

This is the minimum reload set that keeps the persona aligned with the repo's actual center of gravity.

## Local Artifact Routing

### Local Truth

Keep repo-specific truth in:

- `designDoc/`
- `src/`
- `data/`

This includes:

- workflow definitions
- module boundaries
- connector semantics
- archive and report layering
- current storage conventions
- migration and portability notes specific to this repo

### Local Reflection

Keep recurring but still local lessons in:

- `.cursor/context/update_batches/archive/`

If a lesson becomes important to a standing subsystem, it may also deserve a durable local home such as:

- `designDoc/modules/`
- a focused design note under `designDoc/ideas/`

### Portable Promotion Candidates

Do not promote directly from raw task flow into `09_soul`.

For this repo, promotion candidates should first be extracted from local weekly review output, then judged against the portable filter in `09_soul/core/DEVELOPMENT_INTEGRATION.md`.

## Weekly Distillation Loop For `trading_platform`

This repo should use a lightweight weekly loop.

### Inputs

Use the week's evidence from:

- agent transcripts
- major implementation diffs
- changed design docs
- changed adapter or rules files
- `.cursor/context/update_batches/`

### Output A: Local Weekly Digest

Write one short local digest that captures:

- what changed this week
- which architecture or workflow decisions became clearer
- what unresolved tensions still matter

Suggested home:

- `.cursor/context/update_batches/archive/<date>_weekly_dev_digest.md`

### Output B: Promotion Candidates

Extract a small set of candidate lessons and classify them as:

- likely local only
- portable judgment candidate
- portable communication candidate
- portable workflow candidate

These are review artifacts, not automatic promotions.

### Output C: Runtime Projection Changes

If a lesson is active now, project only the minimal active form into:

- `AGENTS.md`
- `.cursor/rules/`
- `09_soul/core/PROJECT_ADAPTER_trading_platform.md`

Do not move weekly summaries into runtime files.

## Recommended First Version

Keep the first version manual and explicit:

1. once a week, review important development chats
2. write one local weekly digest
3. extract up to five promotion candidates
4. promote at most one item into `09_soul`
5. update runtime projection files only if the lesson is currently active

This keeps the loop lightweight while the integration is still maturing.

## Local Success Criteria

For this repo, the integration should be considered healthy when:

- `designDoc/`, rules, and adapter files stay aligned with actual working practice
- weekly development work produces a digest without needing a custom one-off prompt every time
- current repo behavior is captured locally before anything is promoted into `09_soul`
- the assistant's planning, review, and design writing feel consistently like `Hoveath` in this workspace
- portable `09_soul` updates remain cleaner and slower-moving than local repo updates

## Recommendation

Treat the next phase here as a workflow installation task.

The real objective is:

- stronger weekly distillation
- cleaner local vs portable separation
- lighter but more intentional runtime projection

That is the path from `persona present in the prompt` to `persona embedded in the repo's working habits`.
