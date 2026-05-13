# Cursor CLI Parallel Image Read Isolation

## Goal

Define a safer parallel execution design for archive image first-pass reads that use the local Cursor CLI.

This is an idea-stage note, not implemented behavior.

## Problem

The current image first-pass path can launch multiple local Cursor CLI processes in parallel from Python.

That looks attractive for multi-page PDF research because:

- one report can have dozens of page images
- image first-pass is the slowest step in the pipeline
- serial execution is operationally safe but too slow for large backfills

However, the current local CLI path is not concurrency-safe on this machine.

Observed failure mode:

- multiple concurrent Cursor CLI processes race on shared user-level state under `~/.cursor/`
- one concrete error was:
  `ENOENT: no such file or directory, rename '~/.cursor/cli-config.json.tmp' -> '~/.cursor/cli-config.json'`

This means the issue is not "multi-agent is impossible".
The issue is that the current subprocess model shares one mutable global Cursor config surface.

## Current State

Current pattern:

- Python `ThreadPoolExecutor`
- each worker calls local Cursor CLI through subprocess
- all workers share the same `HOME` and the same Cursor config directory

Current outcome:

- parallel image reads can fail nondeterministically
- retries do not reliably solve the race
- large report runs can stall or silently degrade into fallback paths

## Design Requirement

We want all of the following:

1. keep local Cursor CLI as the preferred high-quality first-pass path
2. preserve deterministic archive outputs
3. allow parallelism for multi-page PDF image reads
4. avoid shared mutable global config collisions
5. keep fallback paths explicit and observable

## Proposed Options

## Option A

Per-worker isolated Cursor runtime directories.

Design:

- each image-read worker gets its own isolated temp home or Cursor config root
- subprocess env sets worker-specific paths before invoking Cursor CLI
- no worker writes to the same `~/.cursor/cli-config.json`

Benefits:

- keeps true parallel local Cursor reads
- preserves current Python orchestration shape
- likely the closest path to existing code

Risks:

- may require discovering which env vars Cursor CLI actually respects
- auth/session material may need controlled bootstrap into each isolated runtime
- temp dir lifecycle and cleanup must be deterministic

Best use:

- highest-priority option if per-worker isolation can be made reliable

## Option B

Single long-lived local Cursor worker with queued tasks.

Design:

- replace N parallel short-lived CLI invocations with one persistent local worker
- worker processes image tasks sequentially or with internally managed concurrency
- repo orchestration stays parallel at the queue level, not at the raw CLI-process level

Benefits:

- avoids config-file race entirely
- simpler auth/session handling
- easier logging and retry control

Risks:

- lower throughput than true parallel workers
- more implementation work if a stable long-lived worker wrapper does not already exist

Best use:

- safest fallback if isolated parallel workers prove too fragile

## Option C

Hybrid routing: serial Cursor, parallel non-Cursor fallback.

Design:

- use local Cursor only for selected high-value pages
- use OpenAI multimodal or other providers for the rest in parallel
- select pages by `page_role`, `evidence_value`, or reviewed local gating

Benefits:

- reduces pressure on local Cursor CLI
- faster than full serial local execution
- makes cost/performance tradeoffs explicit

Risks:

- mixed-provider outputs may vary in tone or detail
- routing heuristics become another source of complexity

Best use:

- practical interim strategy when full local parallelism is not yet safe

## Option D

Keep local Cursor serial, optimize everything around it.

Design:

- no concurrent local Cursor CLI calls
- improve page gating, page-role filtering, and caching
- skip low-value pages and only model-read high-signal images

Benefits:

- operationally stable now
- minimal architectural risk

Risks:

- slower for large archives
- does not solve the underlying scalability problem

Best use:

- immediate safety baseline

## Recommended Direction

Recommended order:

1. keep `Option D` as the immediate safe baseline
2. prototype `Option A` in a narrow experiment
3. if Cursor runtime isolation is unreliable, fall back to `Option B`
4. use `Option C` only when speed matters enough to justify mixed-provider complexity

Why this order:

- the repo already has working local-first logic
- the main missing piece is process isolation, not higher-level workflow design
- `Option A` preserves the current quality target with the smallest conceptual change

## Narrow Experiment Plan

Prototype on one report only:

- choose one multi-page `manual_report`
- create 2-4 worker-specific temp runtime dirs
- run a small batch of page images in parallel
- verify:
  - no shared config race
  - no auth/bootstrap breakage
  - outputs remain valid JSON and schema-compliant
  - throughput is materially better than serial

Success criteria:

- zero config-file race failures
- zero malformed image-read payloads
- stable completion across repeated runs
- clear speedup versus serial mode

## Implementation Notes

If this idea is promoted later, the implementation should:

- keep one deterministic archive schema for `image_reads.jsonl`
- log the execution path per row:
  - isolated_cursor_worker
  - serial_cursor_worker
  - openai_fallback
- avoid hidden heuristic downgrade when provider execution fails
- expose the concurrency mode in usage or audit metadata

## Non-Goals

This idea does not propose:

- removing local Cursor as the preferred image-read path
- changing the research archive object model
- replacing image first-pass with only heuristic summaries
- treating the connector or CLI process model as the system's conceptual center

## Promotion Trigger

Promote this note out of `ideas/` only after:

- a worker-isolation experiment succeeds
- the runtime contract is stable enough for `designDoc/research_10_thematic_workflow.md`
- the repo has a clear default concurrency policy for image first-pass
