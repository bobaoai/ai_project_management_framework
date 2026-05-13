# External Review Builder

## What This Subskill Does

Use this subskill when the external agent is reviewing a stable local artifact, AI-facing doc, skill, prompt, design artifact, learning-library artifact, or generated package.

It specializes `support-external-agent-builder` for review work. The result is an external reviewer prompt assembled by `src/tools/build_doc_review_prompt.py`, not a hand-written review prompt.

## Reader End-State

After this builder runs, the caller should know:

- exactly which local artifact is being reviewed
- which local references define the review contract
- which task-specific module controls the review lens
- what the external reviewer saw as embedded evidence
- whether any prior output is stale because it came from a bad prompt
- whether the generated prompt is ready to run through an external surface

## Required Inputs

Read before building:

- parent skill: `SKILL.md`
- `src/tools/build_doc_review_prompt.py`
- `09_soul/skills/bestpractice_external_worker_general_module.md`
- `09_soul/skills/bestpractice_doc_self_review.md`
- `09_soul/skills/bestpractice_skill_writing.md`
- `09_soul/skills/bestpractice_prompt_boundary.md`
- the target artifact
- the local references that define the review contract

Use domain reviewers instead of this subskill when the artifact type already has a canonical independent review gate, such as `engineering-project-review`, `research-theme-report-reviewer`, or `research-evidence-reviewer`.

## Build Pattern

Create a task module first. The module should contain only task-plane review requirements:

```text
# CUSTOMIZE_MODULE: <review task name>

- target artifact class
- required review questions
- severity mapping
- finding format additions
- out-of-scope checks

# DATA_DEPENDENT_MODULE: <evidence and target semantics>

- allowed evidence
- local references that define the contract
- source-check labeling rules
- target-specific caveats
```

Then assemble the prompt through the builder:

```bash
./.venv/bin/python -m src.tools.build_doc_review_prompt \
  --target <target-path> \
  --output <prompt-output-path> \
  --extra-reference <local-reference-path> \
  --module <review-module-path>
```

The builder owns the stable review prefix, embeds the distilled `GENERAL_MODULE`, embeds local file bodies, and writes a manifest sidecar. The review module owns the task-specific `CUSTOMIZE_MODULE` and `DATA_DEPENDENT_MODULE`. The target artifact remains the dynamic object under review.

## Validation Before Running

Before launching the external reviewer, confirm:

- no old runner is active for the same target / prompt / output
- prompt contains no `MISSING FILE`
- the generated `.manifest.json` exists
- the manifest records `full_prompt_sha256`, `general_module_hash`, `customize_module_hash`, `data_dependent_module_hash`, and `input_payload_hash`
- prompt contains `## Review Modules`
- prompt contains `## Target Artifacts`
- the target body is embedded, not merely named
- required local references are embedded, not merely listed
- code fences are intact when embedded files contain fenced blocks
- stale review outputs from invalid prompts are deleted, renamed, or labeled stale

For Claude Code CLI in this repo, run from repo root:

```bash
/Users/bokanbao/.local/bin/claude -p < <prompt-path> > <review-output-path>
```

For another external surface, keep the same generated prompt semantics and log the external surface, payload hash, output path, and failure state.

## Output Contract

The external review handoff should name:

- `target_artifact`
- `prompt_path`
- `manifest_path`
- `review_module_path`
- `embedded_references`
- `input_payload_hash`
- external surface used, if launched
- `review_output_path`, if launched
- stale outputs removed or retained
- validation result

## Silent Violation Signals

- A complete review prompt appears in `.scratch/` without a corresponding module and builder command.
- The prompt asks the reviewer to read local paths but does not embed their content.
- Review-specific requirements are edited into `src/tools/build_doc_review_prompt.py` stable prefix.
- The external reviewer output is treated as final even though the prompt was later judged invalid.
- The external run starts while an old review runner for the same target is still active.
