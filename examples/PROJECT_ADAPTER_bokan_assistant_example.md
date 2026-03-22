# Example Project Adapter: bokan_assistant

This example shows what a host-specific adapter can look like after localization.

## Current Read Of The Repo

This repo started with a calendar-first operating model, but current usage suggests it functions more like a general daily assistant workspace.

## Practical Center Of Gravity

- `04_areas/` for active work and longer-running materials
- `02_tasks/` for explicit task records
- `01_calendar/` when scheduling or commitments are relevant

## Local Truths

- Do not assume calendar is the primary entry point for every request.
- Treat `04_areas/` as a first-class working surface.
- Keep plan-only behavior unless the user explicitly asks to apply changes.
- Preserve existing file-based truth even when the soul would prefer a cleaner structure.

## When To Summon Hoveath

- architecture direction
- workflow design
- review style
- prioritization philosophy
- promotion of lessons from project work
- deciding what should become portable

## What Stays Local

- folder-specific workflows
- one-off project conventions
- temporary operating shifts
- content that belongs in active work files rather than durable persona memory
