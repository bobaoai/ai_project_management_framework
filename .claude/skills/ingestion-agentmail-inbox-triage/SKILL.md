---
name: ingestion-agentmail-inbox-triage
description: "Triages AgentMail resource inbox emails into historical bundles, new single forwarded research items, or plain new messages using local rules plus agent review. Use when checking what new mail arrived, refreshing AgentMail inboxes, deciding whether a mail should expand attached .eml history files, or judging whether quoted/folded content should be collapsed before archiving."
---

# AgentMail Inbox Triage

## What This Skill Does

Use this skill when the task is about fetching, classifying, or reviewing mail from the canonical AgentMail intake path in `trading_platform`.

This skill is for:

- checking what new AgentMail items arrived
- classifying each envelope into the right archive bucket
- deciding whether attached `.eml` files should become the real research items
- deciding whether quoted or folded history should be collapsed before archiving

This skill is not for:

- Gmail intake
- downstream theme or PM interpretation
- archive image-evidence review beyond preserving the correct artifacts

## Canonical Path

- Treat AgentMail as the primary mail intake path.
- Do not route new mail work through the Gmail path.
- Use `tradectl message fetch-agentmail` as the canonical command surface.

## Desired Result

The desired result is a clean triage judgment for each inbox envelope so downstream archive work no longer has to guess what the email really is.

By the time this skill is done, it should be explicit:

- whether the envelope is a wrapper or the real research item
- whether attached `.eml` files should be expanded
- whether quoted or folded history should be collapsed
- what should be archived for provenance
- what should be treated as the primary downstream research content

## Completion Standard

This skill is complete only when all of the following are explicit for the envelope under review:

- envelope classification
- provenance handling decision
- primary content decision
- folded-history decision when relevant
- whether the result can proceed directly to archive promotion or still needs agent review

Accepted classifications:

- `historical_bundle`
- `new_single_forward`
- `plain_new_message`
- `forwarding_setup`

Accepted outcomes:

- direct archive-ready triage result
- triage result with `pending_agent_review` for edge cases

If the result still leaves downstream archive work guessing which content is primary, this skill is not done.

## Classification Model

Classify each envelope email into one of these buckets:

- `historical_bundle`: the email is mainly a wrapper carrying many attached `.eml` history files
- `new_single_forward`: the email carries one attached `.eml` that is the real new research item
- `plain_new_message`: the email body itself is the canonical content
- `forwarding_setup`: setup or confirmation mail, not research content

Also decide whether the body contains folded or quoted history that should be collapsed to new content only.

## Canonical Files

- `src/research/agentmail.py`
- `src/research/service.py`
- `src/cli/tradectl.py`
- `src/research/archive.py`

## Primary Truth Surfaces

Read these first:

- the fetched inbox envelope
- sender / subject / body shape
- attached `.eml` count and filenames
- archived external IDs when dedupe is relevant

Use local deterministic rules first.
Escalate to agent review only when the envelope shape is ambiguous enough that deterministic classification is not trustworthy.

## Required Outputs

At minimum, the triage result should say:

- `classification`
- `archive_container`
- `primary_research_item`
- `expand_attached_emls`
- `collapse_folded_history`
- `status`

The output should make it obvious what the downstream archive step should do next.

## Guardrails

- Keep AgentMail as a connector boundary and the archive as the durable knowledge layer.
- Preserve top-level envelope provenance even when child `.eml` files become the primary research items.
- Skip container emails in downstream summary/news flows when they are only wrappers.
- Prefer deterministic dedupe on archived external IDs before re-expanding history files.

## Downstream Archive Note

After new mail is archived, PDF/report-style materials should follow the archive's unified research-image contract:

- treat rendered PDF pages and archived images as `research-related image`
- detect real target visual evidence first
- only emit `visuals[]` when `has_visual_evidence=true`
- do not treat pure text pages or branded cover pages as image evidence

Triage should not try to solve this image-evidence boundary itself; it should preserve the right archived artifacts so the downstream archive/image workflow can do it correctly.

## Example Triggers

- “check if new agentmail arrived”
- “pull latest citrini mails”
- “is this a history bundle or a real new update”
- “expand attached eml files into the archive”
- “this forward looks folded, clean it before archiving”
