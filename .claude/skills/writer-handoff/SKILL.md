---
name: writer-handoff
description: "Thin downstream package review gate that receives a prepared package plus local writer direction, decides whether the package is sufficient, returns a concrete `need_more_detail` request when it is not, and only when the gate passes lets the package move into the shared writer gateway. Use only after upstream scope, package selection, and writer framing are already decided."
---

# Writer Handoff

## What This Skill Does

Use this skill as the thin downstream package review gate after upstream owner and package-preparation work are already done.

Its default identity is closer to a reviewer or gatekeeper than to an upstream analyst.

This skill has only two legitimate jobs:

- decide whether the incoming package is sufficient for confident writing
- if sufficient, let that package proceed cleanly into the shared writer path

Do not use this skill as the top-level analysis owner, package selector, or report-scope decider.

When this skill is reused by a formal `market observation` flow, keep the same identity:

- the market-observation mainline still owns the complete report artifact
- this step only decides whether the prepared observation package is sufficient for writing
- do not let this step add unnecessary routing or process context back into the writing task

## Desired Result

The desired result is one of two explicit outcomes:

- a concrete `need_more_detail` response that tells the upstream worker what is missing and why it blocks writing
- or a clear `ready_to_write` gate result that allows the shared writer path to proceed on a sufficiently reviewed package

If the output is neither a real gate decision nor a real writer-readiness judgment, this skill has failed.

## Reader End-State

After this skill is done, the next reader is one of two:

**On `ready_to_write`** — the shared writer pathway (DS / Claude / human writer) should newly be able to:

- Proceed to write knowing the package satisfies all minimum block checks (current judgment / background / market pricing / drivers / confirmed-vs-not / debates / scenario / portfolio fit / risks)
- Write without inferring "what was the upstream owner really asking for" (writer-direction notes have already been preserved into the gate's pass-through)
- Trust that uncertainty and not-confirmed items in the package are intact, not silently upgraded

**On `need_more_detail`** — the upstream owner / `research-theme-knowledge-and-package-curator` should newly be able to:

- See specifically which blocks are missing and why each gap blocks decision-ready writing
- Know whether the gap should be filled from local material or narrow Perplexity verification
- Re-enter the gate after the patch without redoing scope decisions

If the next reader still has to re-evaluate package sufficiency (on `ready_to_write`) or has to infer what specifically to add (on `need_more_detail`), this skill is not done.

_Validation pending (retrospective follow-up)._ This dual-outcome Reader End-State
was added 2026-04-24 during the `critic_pipeline_20260424` retrospective (Item 1).
The V4 dogfood produced a `ready_to_write` verdict; `need_more_detail` has not been
exercised with the new end-state language in place. **Next time this skill emits
either outcome, observe whether the downstream reader (writer path or upstream
owner / maintainer) acted on the handoff without re-asking for scope or specificity.**
Update `designDoc/retrospectives/critic_pipeline_20260424.md` Item 1 accordingly;
if `need_more_detail` consistently triggers follow-up questions about which gap
takes priority, that is a signal to add a priority field to the gap list.

## Completion Standard

This skill is complete only when one of these is true:

### Outcome A: `need_more_detail`

- status is explicitly `need_more_detail`
- missing blocks are named specifically
- the reason each missing block matters is stated
- the request says whether the gap should be filled from local material or narrow public verification

### Outcome B: `ready_to_write`

- status is explicitly `ready_to_write`
- the package is explicitly judged ready for the shared writer path
- the gate judgment preserves uncertainty and not-confirmed items correctly
- if prose is generated in the same step, it is still clearly downstream from the gate rather than the reason the gate exists

## Primary Inputs

Read these first and treat them as primary:

- the prepared package file
- local writer-direction notes
- the requested output form

When the upstream package includes ad hoc downstream instructions for major news, catalysts, or transmission drivers, treat them as part of the local writer-direction notes and preserve them into the specific downstream writer prompt.

Go back to the broader repo only when:

- the package is obviously incomplete
- the upstream owner explicitly asks for validation of a gap
- the user explicitly asks for expansion beyond the package

## Package Sufficiency Gate

The first decision is always whether the package can support writing.

Return only one of these statuses:

- `ready_to_write`
- `need_more_detail`

Minimum package checks:

- current judgment is explicit
- required background context is present
- what the market is pricing now is explicit or inferable from concrete anchors when relevant
- key drivers and transmission path are present
- confirmed anchors and not-confirmed items are clearly separated
- key debates and unresolved uncertainty are present
- scenario path or what happens next is present
- portfolio fit or action framing is present
- key risks and monitoring items are present

Preferred gate output shape:

- `Status: ready_to_write` or `Status: need_more_detail`
- `Missing required:` specific missing blocks
- `Why it blocks writing:` why those gaps prevent a decision-ready artifact
- `Please add:` concrete additions, including whether Perplexity is actually needed

Do not silently write around large evidence gaps.

This gate is the main reason this skill exists.
If the system can preserve the same gate elsewhere later, the standalone skill may eventually collapse into a more explicit writer-gateway review step.

## Reviewer Boundary

Treat upstream scope, package selection, and framing judgments as already decided unless the package is clearly insufficient.

This skill should not retake authority over:

- which materials should have been selected
- what the report pass is fundamentally about
- whether the task should really have been another mainline

If the package is bad, say so through the gate. Do not quietly redesign the upstream workflow inside the report.

## Writing Standard

When the package passes the gate, any writing that happens here should still be understood as a downstream consequence of the gate, not the main identity of the skill.

Keep these standards:

- do not reduce the package to a shallow summary before writing
- preserve source-grounded reasoning, essential background, and real debate where they matter to the judgment
- translate schema labels, notes, and raw records into natural analyst prose
- write like a PM/client memo, not like tech docs, workflow notes, or research triage
- keep uncertainty explicit and do not upgrade not-confirmed items into facts
- when the topic is market-facing, connect evidence to price behavior, expectations, and forward path
- leave the reader with action framing, not only interpretation

Default posture:

- gate first
- reviewer first
- prose second

When writing in Chinese:

- use natural Chinese analyst prose rather than literal translation
- remove machine-translated wording and English syntax traces

## Main-Article Language Boundary

Unless the user explicitly asks for workflow explanation, do not expose process vocabulary in the main article.

Avoid terms such as:

- `operator`
- `package`
- `confirmed anchors`
- `not confirmed items`
- `subtheme`
- `trade thesis`
- raw schema keys

Ban editorial/process phrasing in the main article, including:

- `这次 package`
- `相比现有报告`
- `本次更新`
- `新增证据`
- `这版`
- `原文`
- `我们把...改成`

If a sentence sounds like an editor describing document production instead of an analyst describing markets, policy, business, or assets, rewrite it.

## Preferred Output Shape

For PM-facing outputs, prefer a stable logic order:

- current judgment
- background and setup
- what the market is pricing now
- key drivers and transmission path
- evidence and confirming / disconfirming anchors
- key debates and uncertainty
- scenario path / what happens next
- portfolio fit or action framing
- risks and monitoring items

Adapt headings to the topic, but preserve this logical order unless there is a strong reason not to.

## Common Failure Signals

Treat these as failure signs:

- the gate is skipped and the step drafts anyway
- the draft sounds informed but never makes a real judgment
- the draft over-compresses and loses necessary setup or debate
- the draft repeats package labels instead of translating them into analyst prose
- the draft mentions unconfirmed items as facts
- the draft disconnects price action from the actual thesis when price behavior matters
- the draft becomes a polished material dump instead of a decision-ready memo
- the step behaves like an upstream analyst instead of a reviewer of package readiness

## Guardrails

- Do not retake upstream ownership over package scope, source selection, or writer framing if that judgment was already supplied.
- Do not rely on chat-only reasoning when local artifacts are available.
- Do not omit portfolio context if it is present in the package.
- Do not drift into tech-doc tone when the task is report or memo writing.
- Do not mistake wide coverage for quality if the report fails to identify the key contradiction.
- Do not mistake brevity for quality if it drops essential context, detail, or debate.
- Do not write a static summary when the real question depends on price, expectations, or scenario evolution.
- Do not leave action framing implicit when the task is decision-facing.

## Example Triggers

- “review this package before writing”
- “check whether this package is ready”
- “package review gate”
- “prepare the review memo”
- “write the report from this package”
- “turn this detailed package into PM-readable prose”
- “review this market observation package before writing”
- “is this post-close package ready”
