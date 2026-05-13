---
name: support-compaction-handoff
description: Generates a compact, copy-paste-ready session handoff for continuing long work in a new Cursor chat. Use when the user asks to compact context, prepare a handoff, summarize current state for a new chat, or preserve where a multi-step task stands before context window pressure.
---

# Compaction Handoff

## What This Skill Does

Use this skill to produce a compact handoff that the user can paste into a new chat.

The handoff should let the next agent continue from the current state without re-discovering the whole repo history.

It is for:

- context window handoff
- long-running implementation or review threads
- multi-commit migration work
- multi-agent dogfood sessions
- "what should the next chat know" requests

It is not for:

- full retrospective writing
- commit messages
- PM-facing market reports
- replacing source-of-truth docs

## Primary Truth Surfaces

Read only what materially improves the handoff:

- `git log --oneline -10`
- `git status --short`
- latest relevant plan / handoff doc, if the current task named one
- latest validation output if it exists in the current chat context
- files the user explicitly points at

Do not broaden into a repo-wide exploration unless the current state is genuinely unclear.

## Required Output

Return one copy-paste-ready markdown block.

Use this exact top-level shape:

```markdown
# Session Handoff

## Current Mainline

## Completed Since Last Handoff

## Current Git State

## Validation Gates

## Open Findings / Risks

## Next Action

## Do Not Touch

## Key Files To Read First
```

## Content Rules

- Keep it compact enough to paste into a new chat.
- Prefer facts over narrative.
- Name commit hashes when relevant.
- Separate committed work from uncommitted work.
- State exactly what the next action should be.
- Include "Do Not Touch" for dirty files, unrelated user changes, and known out-of-scope areas.
- Mention blockers and review findings only if they change the next action.
- Do not include hidden orchestration details, tool IDs, terminal file paths, or agent transcript internals.

## Quality Bar

The next agent should be able to answer:

- where the project is in the larger phase
- what was already committed
- what remains uncommitted
- what validation is trusted
- what the next safe move is
- what not to accidentally revert or stage

If the handoff does not answer those questions, it is not done.

## Minimal Template

```markdown
# Session Handoff

## Current Mainline
<One or two sentences: overall project and current phase.>

## Completed Since Last Handoff
- `<commit>` <short meaning>
- <uncommitted completed work, if any>

## Current Git State
- Clean / dirty summary.
- Current relevant uncommitted files.
- Known unrelated dirty files to ignore.

## Validation Gates
- `<command>`: PASS / FAIL / not run.
- Note any dirty-worktree caveat.

## Open Findings / Risks
- <Only findings that affect the next action.>

## Next Action
<One concrete next step, not a long menu.>

## Do Not Touch
- <Files or directories that are dirty but unrelated.>

## Key Files To Read First
- `<path>`
- `<path>`
```
