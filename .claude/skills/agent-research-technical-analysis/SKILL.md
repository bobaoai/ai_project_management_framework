---
name: agent-research-technical-analysis
type: agent
description: "Orchestrates the Research Technical Analysis pipeline for one ticker. Owns the full lifecycle: build signal packet, build writer package, invoke writer, invoke reviewer, evaluate reviewer feedback, decide retry / adjust / escalate, validate and index the final report. Use when the user asks for a technical analysis report on a ticker, or when a `tradecli research technical <asset>` trigger fires."
---

# Agent Research Technical Analysis

## Identity

This agent produces a passing Technical Report Material for one ticker by driving the full build, review, validate, and index pipeline.

Enter this agent when:

- the user asks for a technical analysis report on a specific ticker
- a `tradecli research technical <asset>` runner trigger fires
- another caller needs to drive the Research Technical Workflow end to end for one asset

On entry, read these in order before driving the Workflow:

1. `designDoc/temp/smoke/designDoc/research_20_technical_module_smoke_design.md`: module Design Doc. Confirms current scope, class assignment, failure signatures, and the Agent's authority boundary.
2. `data/knowledge/asset_technicals/profiles.json`: profiles config Artifact. Confirms the requested asset is eligible for technical analysis and resolves the asset fixture (`asset_id`, `report_id`).
3. Upstream constraint Design Docs (`designDoc/research_20_technical_signal_pipeline_v2.md`, `designDoc/research_00_writer_package_contract.md`, `designDoc/material_70_technical_report_contract.md`, `designDoc/the_timestamp_semantic.md`): read when a boundary or contract question arises during execution. Do not load preemptively.

Do not enter this agent for:

- single-stock synthesis that integrates theme overlays and thesis context (use `research-single-stock-analysis`)
- portfolio decisions that consume a Technical Report (use `operation-portfolio-decision`)
- defining Material schema, Artifact graph rules, Workflow class semantics, or Tool implementations
- owning raw market-data truth or upstream data pipelines

## Objective

Produce one Technical Report Material for the requested ticker that passes the reviewer Tool, passes deterministic report validation, passes downstream admission validation, and lands in the Technical Report index.

## Owned Workflow

This agent owns `workflow_research_technical_analysis` (the Research Technical Analysis Workflow). The Workflow has five steps executed in fixed order.

### Steps & Gates

1. **build_research_technical_signal_packet_artifact**: invoke `tool_research_technical_signal_packet_builder` (signal packet builder Tool). Produces `artifact_research_technical_signal_packet` (signal packet markdown Artifact) and `artifact_research_technical_signal_packet_payload` (signal packet payload JSON Artifact). Gate: `validator_research_technical_signal_packet` (signal packet Validator) must pass before step 2.
2. **build_research_technical_writer_package_artifact**: invoke `tool_research_technical_writer_package_builder` (writer package builder Tool). Produces `artifact_research_technical_writer_package` (writer package Artifact) and `artifact_research_technical_writer_package_manifest` (writer package manifest Artifact). Gate: `validator_research_technical_writer_package` (writer package Validator) must pass before step 3.
3. **invoke_research_technical_writer**: invoke `tool_research_technical_writer` (writer Tool) on the writer package. Produces the Technical Report Material file parts, `artifact_research_technical_writer_prompt_projection` (writer prompt projection Artifact), and `artifact_research_technical_writer_sidecar` (writer sidecar Artifact). No Workflow gate on this step; the reviewer is the next gate (`gate_research_technical_reviewer_passed`).
4. **invoke_research_technical_reviewer**: invoke `tool_research_technical_reviewer` (reviewer Tool) with the Technical Report and the writer package. Produces `artifact_research_technical_review_result` (review result Artifact). No Workflow gate on this step. The reviewer verdict feeds this agent's revision policy.
5. **validate_and_index_research_technical_report**: invoke `tool_research_technical_fidelity_checker` (fidelity checker Tool), then `validator_research_technical_report` (report Validator; gate: `gate_research_technical_report_validated`), then `tool_research_technical_index_builder` (index builder Tool), then `validator_research_technical_downstream_admission` (downstream admission Validator; gate: `gate_research_technical_downstream_admission`). The report Validator must pass before the index row is written. The admission Validator audits the index row against the report and review result and must pass before downstream consumers may use the report. Produces `artifact_research_technical_index_row` (index row Artifact at `data/knowledge/asset_technicals/index.json`).

The Workflow declares step order, Tool refs, Validator refs, and step gates. The revision loop after step 4 is this agent's adaptive policy, not a Workflow step.

### Policy

The revision loop is this agent's adaptive decision surface. After step 4 emits `artifact_research_technical_review_result`, read the verdict and select one of three actions.

- **Retry writer with the same package.** Trigger: the reviewer flags prose quality, structure, or formatting problems without citing missing data or unsupported claims. Action: re-enter the Workflow at step 3 with the existing writer package.
- **Adjust the package and retry the writer.** Trigger: the reviewer flags missing data, insufficient evidence, or claims unsupported by the package. Action: re-enter the Workflow at step 2 with package modifications, then continue through steps 3 and 4.
- **Escalate to PM.** Trigger: the underlying data is fundamentally insufficient for this ticker, or the same data gap persists after one package adjustment. Action: stop the run. Further retry or adjustment will not produce a passing report.

Default budget: at most one writer retry on the same package, and at most one package adjustment per ticker. Once both are spent on the same reviewer-flagged gap, escalate.

Track across iterations: retry count, revision history (what the reviewer flagged each iteration and what action followed), and package adjustments tried. These live as runtime in-memory state on the Agent run. `artifact_research_technical_review_result` is the only artifact-backed state surface.

### Stop Condition

Stop on success when the Technical Report passes the reviewer at step 4, passes `validator_research_technical_report`, passes `validator_research_technical_downstream_admission`, and the row has been appended by `tool_research_technical_index_builder`. Emit `artifact_research_technical_workflow_run_result` (workflow run result Artifact) with terminal status `complete`.

Stop on escalation when the policy selects escalate or the retry budget is exhausted. Emit `artifact_research_technical_workflow_run_result` with terminal status `escalated`. The escalated run result must include the revision history (per-iteration reviewer flags and action taken) and the latest reviewer feedback so the PM can decide manually.

### Completion Standard

The agent run is complete only when `artifact_research_technical_workflow_run_result` exists and one of the two conditions below holds.

Condition A: terminal status `complete`.

- `artifact_research_technical_review_result` records a pass verdict from the reviewer Tool.
- `artifact_research_technical_signal_packet_validation_result` (signal packet Validator output Artifact) records a pass.
- `artifact_research_technical_writer_package_validation_result` (writer package Validator output Artifact) records a pass.
- `artifact_research_technical_report_validation_result` (report Validator output Artifact) records a pass or carries an explicit warning override per the report Validator gate.
- `artifact_research_technical_downstream_admission_result` (downstream admission Validator output Artifact) records a pass.
- `artifact_research_technical_index_row` (index row Artifact at `data/knowledge/asset_technicals/index.json`) carries the row for the resolved `report_id`.

Condition B: terminal status `escalated`.

- The revision history is attached to the run result Artifact.
- The latest `artifact_research_technical_review_result` is referenced.

If the workflow run result is missing, or it carries `complete` while any artifact in Condition A is missing or failing, the run is not complete.

## Boundary

This agent owns:

- the revision loop policy after the reviewer Tool returns a verdict
- the call sequence and step dispatch for the five Workflow steps
- `artifact_research_technical_workflow_run_result` and its terminal status

This agent does not own the following. Each item is paired with a detection signature: the observable shape of a silent violation that the agent can spot in its own output before declaring `complete`.

- **Material schema or Technical Report contract content.** Detection: the report file omits, renames, or invents a field defined in the Technical Report Material contract while the agent reports `complete`. The Material contract is upstream; read it, do not redefine it.
- **Tool implementation logic.** Detection: this SKILL.md, the workflow run result, or any agent log describes signal-packet field computation rules, writer prompt template internals, or fidelity-comparison criteria. Each Tool owns its own code binding; the agent invokes Tools and consumes their outputs.
- **Raw data truth.** Detection: the agent fabricates, edits, or overrides values that the signal packet payload already supplies. The signal packet payload is authoritative for technical state.
- **PM-level portfolio decisions.** Detection: the workflow run result, the report body, or the reviewer prompt contains a position recommendation, hedge instruction, or book-level action. Stop at the indexed report.
- **Single-stock synthesis with theme overlays.** Detection: the report body weaves theme thesis prose, scenario triggers, or cross-asset narrative. The Technical Report is technical-only; cross-asset synthesis belongs to `research-single-stock-analysis`.
- **Workflow-level gate evaluation for the reviewer step.** Detection: the workflow run result records a deterministic pass/fail assertion as a Workflow gate on step 4. Step 4 has no Workflow gate; the reviewer verdict feeds this agent's revision policy.
- **Bypassing the reviewer or any validator.** Detection: `artifact_research_technical_workflow_run_result` carries `complete` while any of `artifact_research_technical_review_result`, `artifact_research_technical_signal_packet_validation_result`, `artifact_research_technical_writer_package_validation_result`, `artifact_research_technical_report_validation_result`, or `artifact_research_technical_downstream_admission_result` is missing or failing.
- **Mutating the workflow run result into Evidence, Thesis, Theme, Scenario, Portfolio Decision, or PM acknowledgement.** Detection: the run result file lands under `data/research/evidence_ledger/`, `data/research/thesis_notes/`, theme metadata, or scenario notes. The run result is an audit artifact for one runner invocation.

**Known Traps:**

- **Treating a reviewer pass as final admission.** A reviewer pass authorizes step 5; it does not replace step 5. The report Validator and downstream admission Validator still gate the index row.
- **Skipping fidelity and report validation on the retry path.** Every writer invocation that ends a run with `complete` must rerun the fidelity checker and report Validator on the new report file, not only the first iteration's output.
- **Emitting `complete` while any of the four validator-output Artifacts is missing.** The four Validator outputs are the audit trail. A `complete` run without all four indicates a silent gate bypass.
- **Retrying the writer on a known-empty package.** If the writer package Validator fails because the package is empty or stub, the gap is in the package builder Tool, not in the writer. Escalate; do not loop the writer on a package that step 2's gate already rejected.
- **Counting a package adjustment as cheap.** A package adjustment is a budgeted action. Adjust once per ticker on a given gap, then escalate if the gap persists. Repeated adjustment cycles burn writer calls without changing the underlying data sufficiency.
