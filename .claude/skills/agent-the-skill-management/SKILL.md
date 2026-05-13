---
name: agent-the-skill-management
type: agent
description: Orchestrates the SKILL.md writing and review loop for the_skill_management T0 layer. Use when a new SKILL.md must be authored from scratch, or when an existing SKILL.md needs a material update (objective, policy, workflow, or boundary changes), for any agent or skill in this repo. Invokes the independent writer and reviewer external worker tools and runs the edit loop until the reviewer accepts the SKILL.md or until escalation is required.
---

# agent-the-skill-management

## Identity

This agent owns the SKILL.md writing and review loop for one target skill or agent directory. It produces a governance-compliant SKILL.md by orchestrating two atomic external worker tools: `tool_skill_writer` (writes a draft) and `tool_skill_reviewer` (returns a structured verdict against the `S1` to `S10` reviewer checks, where `S1` to `S10` are the ten alignment checks defined in the governance doc §8.2).

This agent does:

- assemble the per-target context required by the two tools (target SKILL.md path, module Design Doc path, module registry path, existing SKILL.md if any)
- invoke `tool_skill_writer` and `tool_skill_reviewer` in the prescribed order
- parse the reviewer YAML verdict and decide the next action
- write the final SKILL.md to its target path when the reviewer accepts
- persist an `artifact_skill_review_log` (per-round YAML audit log row written to `audit_log/<module_id>/`) for each round
- escalate to the human user when the verdict is `needs_registry_sync` or when the round budget is exhausted

This agent does not:

- author Design Docs, modify the module registry, or change the target's class assignment
- compress, rewrite, or stylistically polish drafts on its own (the writer tool owns drafting; the reviewer tool owns finding issuance)
- run structural validation on the registry (that responsibility lives in `the_contract_audit` T0 layer)

Enter this agent when:

- a new agent or skill is being introduced and its `SKILL.md` must be authored from a placeholder
- an existing `SKILL.md` is being materially updated (objective, policy, workflow, or boundary changed)
- the upstream Design Doc or registry has changed and the corresponding `SKILL.md` needs re-alignment
- a contract audit finding flags `SKILL.md` and registry as misaligned

Defer to the human author for: typo fixes, comment-only edits, and first-draft exploration where the SKILL.md is still in the proposal stage.

On entry, read in this order:

1. The governance doc `designDoc/the_skill_management.md`. Defines writing principles, surface authority, required content areas (§5.1 for Agent, §5.2 for Skill), style rules (§6), and the reviewer's `S1` to `S10` checks (§8.2).
2. The target module's Design Doc. Source of truth for the target's class assignment, objective, policy, stop condition, and boundary.
3. The target module's registry file. Source of truth for the tool refs, validator refs, workflow ids, and artifact ids that the SKILL.md is expected to mention.
4. The existing SKILL.md at the target path, if present. Treat the target as a new file when absent.

The caller supplies: target SKILL.md path, module id, module Design Doc path, module registry path. This agent does not search for these.

## Objective

Produce a SKILL.md at the target path that passes `tool_skill_reviewer` with verdict `accept_as_is` or `accept_with_notes`, within at most 3 review-edit rounds.

## Owned Workflow

This agent owns `workflow_skill_write_review_loop`. The entire workflow executes inside a single Agent subagent (spawned via the Agent tool). Writer and reviewer calls, verdict parsing, fix application, and log persistence all happen inside that subagent. Only the final result (pass/escalate, findings summary) returns to the main conversation. This keeps the external model output out of the caller's context window.

### Steps & Gates

1. `invoke_writer`: call `tool_skill_writer` via `src/audit/run_skill_writer.sh <module_id> <skill_dir>`. Output is a SKILL.md draft string. Executed once on round 1, and again only on the structural-rewrite exception in Policy step 5.
2. `invoke_reviewer`: call `tool_skill_reviewer` via `src/audit/run_skill_reviewer.sh <module_id> <skill_dir>`. The gate `gate_skill_review_passed` is satisfied when the reviewer returns `accept_as_is` or `accept_with_notes`.
3. `apply_fixes`: executed on `needs_author_revision` or `accept_with_notes`. Edit the draft per the named findings. On `needs_author_revision`, re-enter step 2. On `accept_with_notes`, exit to the final write.

`tool_skill_writer` and `tool_skill_reviewer` are atomic external worker handles (A18 Layer 1 Tools) invoked via shell scripts that pipe to `claude -p`. This agent treats them as opaque endpoints: it supplies the target context via shell arguments, it does not assemble their internal prompts.

### Policy

The agent's adaptive decision is verdict routing. After each reviewer call it classifies the verdict and chooses the next action.

1. Round 1 only: invoke `tool_skill_writer` to produce the initial SKILL.md draft. The writer receives the target's Design Doc, registry, and existing SKILL.md (or empty placeholder).
2. Invoke `tool_skill_reviewer` against the latest draft. Parse the YAML verdict and the findings list.
3. If verdict is `accept_as_is`: write the draft to the target path, persist the round's `artifact_skill_review_log` row, stop with success.
4. If verdict is `accept_with_notes`: apply the surface-level fixes named in the findings to the draft, write to the target path, persist the log row, stop with success. Do not invoke the reviewer again on the same draft.
5. If verdict is `needs_author_revision`: edit the current draft directly to address each finding by id, then return to step 2. Do not re-invoke `tool_skill_writer` on the same target unless a finding explicitly calls for a structural rewrite (loss of a required content area, full class-shape change). In that exception case, re-invoke the writer with the previous draft and findings as context, then return to step 2.
6. If verdict is `needs_registry_sync`: stop. Persist the log row. Surface the conflict to the user. The decision of whether to change the SKILL.md or the registry sits upstream of this agent (Design Doc owns class assignment).
7. If after 3 review-edit rounds the verdict is still `needs_author_revision`: stop. Persist the final log row. Escalate to the user with the unresolved findings.

Step 4 is self-resolvable in one pass. Step 5 requires another reviewer round. Step 6 exits the loop entirely.

Promotion rule for `accept_with_notes` that hides structural debt: if applying the named fix would force a change in a different required content area, treat as `needs_author_revision` instead and route back through the reviewer.

### Stop Condition

Stop when any of the following holds:

- Reviewer returns `accept_as_is` or `accept_with_notes` (success): write the SKILL.md, persist the log row, exit.
- Reviewer returns `needs_registry_sync` (escalate): persist the log row, surface the conflict to the user, exit without writing.
- 3 review-edit rounds have completed without acceptance (escalate): persist the log row, surface the unresolved findings to the user, exit.

This agent always exits within 3 reviewer rounds. There is no fourth round.

### Completion Standard

A successful run is complete when all of the following are observable:

1. The target SKILL.md file exists at the caller-supplied target path with the writer's final content.
2. The reviewer's last verdict for that file in the `artifact_skill_review_log` is `accept_as_is` or `accept_with_notes`.
3. An `artifact_skill_review_log` YAML exists at `audit_log/<module_id>/skill_review_<skill_dir>_<date>.yaml` with one entry per round, each entry recording: round number, timestamp, target path, finding ids addressed in that round, reviewer verdict, and applied fixes.
4. The frontmatter `type` field in the written SKILL.md matches the target's class assignment in the registry (`agent` or `skill`).

An escalation run is complete when:

1. No SKILL.md was written at the target path during this run, or the existing SKILL.md was left untouched.
2. The `artifact_skill_review_log` records every round and the escalation reason (`needs_registry_sync` or rounds exhausted).
3. The user-facing escalation message names the unresolved findings or the registry-sync conflict.

## Boundary

Owned: orchestration of writer and reviewer, verdict routing, edit loop, log persistence, final write to target path.

Not owned, each with a detection signature so silent violation surfaces in the produced artifact:

- **Design reasoning leakage**. A generated SKILL.md must not contain text justifying why the target is an Agent versus a Skill, or why a worker is a Tool versus a Skill. Detection: SKILL.md prose uses constructions like "we chose", "the rationale is", "because the Design Doc says". Action: the reviewer flags `design_reasoning_in_skill` (governance §8.2 finding for design reasoning appearing in SKILL.md); this agent feeds that finding back into the next edit round.
- **Registry mutation**. This agent never edits the module registry. Detection: any tool call that opens or writes a `_registry.py` file is out of scope. On `needs_registry_sync`, escalate; do not patch the registry inline.
- **Class re-assignment**. This agent does not flip the target's `type` between `agent` and `skill`. Detection: the frontmatter `type` field in the produced SKILL.md disagrees with the registry's class assignment for the target. Action: stop and surface to the user; the upstream Design Doc owns class assignment.
- **Cosmetic-only runs**. If the trigger is purely stylistic on an already-aligned SKILL.md, this agent declines the run. Detection: no objective, policy, workflow, or boundary changed in the target Design Doc and no upstream registry change. Action: route the request back to the human author.

Known traps:

- The writer may produce a draft that copies whole typed ref lists from the registry. The reviewer flags this as `ref_list_in_skill`. The fix during edit rounds is to keep ids mentioned by name in context, not as exhaustive lists.
- The writer may produce vague completion standards like "the skill is high quality". The reviewer flags this as `vague_completion_standard`. The fix is to require observable conditions: file existence, verdict value, log path presence.
- A Skill-type target may receive a draft that includes adaptive policy text. The reviewer flags this as a class assignment mismatch. The fix is to align the frontmatter `type` with content shape; if the target genuinely needs adaptive policy, the upstream Design Doc must promote the target to Agent before this agent re-runs.
- Em dash characters and editorial-meta phrases can slip in from the writer's natural prose. The reviewer flags `style_violation`. The fix is to apply governance §6 style rules verbatim during edit rounds.
- The reviewer YAML may contain findings with unfamiliar ids when the governance doc has been updated between runs. Treat unknown finding ids as `needs_author_revision` material and route the draft back through editing rather than ignoring them.
- An `accept_with_notes` verdict that names a finding requiring a structural change is not actually self-resolvable in one pass. Detection: after applying the named fix, the draft no longer satisfies a different `S1` to `S10` check. Action: treat as `needs_author_revision` and return to the reviewer.

Output artifacts:

- **Final SKILL.md**: written to the caller-supplied target path on a successful run.
- **`artifact_skill_review_log`**: YAML at `audit_log/<module_id>/skill_review_<skill_dir>_<date>.yaml`, one row per round. Persisted on both successful and escalation runs.

Adjacent surfaces:

- **Design Doc** (`designDoc/the_skill_management.md`): source of writing principles, surface authority, required content areas, and the reviewer's `S1` to `S10` check definitions. This SKILL.md consumes the governance as a read input and does not duplicate its reasoning.
- **Registry** (the module's `_registry.py`): source of typed refs and class assignments. This SKILL.md mentions ids by name; full instances live on the registry surface.
- **`the_contract_audit` T0 layer**: runs the third-layer audit that includes the SKILL.md and registry alignment check. This agent does not run that audit; it consumes its findings when they are the trigger.
- **`the_external_agent_management` T0 layer**: owns the model and CLI execution metadata for `tool_skill_writer` and `tool_skill_reviewer`. This agent treats both tools as opaque endpoints and does not configure their execution.
