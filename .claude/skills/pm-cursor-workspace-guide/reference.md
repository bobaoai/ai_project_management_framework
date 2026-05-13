# PM Workspace Reference

## Recommended Canonical Path

For this repo, the canonical shared draft path is:

- `drafts/pm_common_workspace/`

If this skill is copied into another repo, ask the user to confirm the canonical workspace path before creating files.

## Recommended Workspace Shape

```text
pm_common_workspace/
├── 01_product/
│   ├── PRD.md
│   ├── BRD.md
│   └── user_personas.md
├── 02_rules/
│   ├── non_negotiables.md
│   ├── acceptance_criteria.md
│   └── edge_cases_and_risks.md
├── 03_handoffs/
│   ├── data_science_brief.md
│   ├── design_brief.md
│   └── engineering_brief.md
├── 04_reviews/
│   ├── review_log.md
│   ├── open_questions.md
│   └── decision_log.md
└── 05_demo/
    ├── mvp_scope.md
    └── live_demo_checklist.md
```

## Artifact Rules

### Product docs

These files define intent:

- PRD
- BRD
- user personas

### Rules docs

These files define the review bar:

- non-negotiables
- acceptance criteria
- edge cases and risks

### Handoff docs

These files tell each specialist:

- what problem they are solving
- what rules they must respect
- what output is expected

### Review docs

These files keep the PM in control without doing the specialist's work:

- what was reviewed
- what matches
- what is missing
- what decision was made

## Default Review Loop

1. PM writes or updates source-of-truth docs.
2. Cursor turns those docs into role-specific briefs.
3. Specialists produce outputs.
4. Cursor compares outputs against the rules and criteria.
5. PM approves, requests revisions, or narrows scope.
6. The team prepares an MVP demo that behaves like a mini production slice.

## What Good Cursor Usage Looks Like

- requirements stay visible
- prompts are reusable
- specialist outputs are reviewable
- iteration history is preserved
- open questions are explicit

## What Bad Cursor Usage Looks Like

- everything lives in chat only
- the PM keeps rewriting the same request from scratch
- the team cannot tell which rules are binding
- no one can trace why a decision changed
