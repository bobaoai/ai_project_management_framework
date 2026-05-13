# Rules Index — billie_workspace Cursor Projection

Cursor-native rules live in `.cursor/rules/` and are the executable rule layer. This index records how they fit into the Hoveath projection.

## Numbering Bands

| Band | Meaning |
|---|---|
| `00` | Always-on Cursor bootstrap and Hoveath runtime contract |
| `01-09` | Task routing, axiom retrieval, and skill admission |
| `10-19` | PIM and area maintenance rules tied to local file globs |
| `20-29` | Work-domain overlays and manually invoked expert personas |
| `30-39` | AI-facing docs, prompt hygiene, reader-state, and prose quality |
| `40-49` | Verification, subagent admission, and staged execution |
| `50-59` | Cursor runtime maintenance and projection contracts |
| `90-99` | Maintenance, drift audit, and cleanup rules |

## Rule Map

| Rule | Loading | Role |
|---|---|---|
| `.cursor/rules/00_hoveath_always.mdc` | always | Cursor startup, area-first framing, PLAN-only boundary |
| `.cursor/rules/01_core_task_routing.mdc` | trigger | route requests to local truth surfaces before acting |
| `.cursor/rules/02_axiom_retrieval_triggers.mdc` | trigger | retrieve axioms for higher-frame judgment |
| `.cursor/rules/03_skill_admission_contract.mdc` | trigger | decide when to invoke Hoveath skills |
| `.cursor/rules/10_pim_areas_auto.mdc` | `04_areas/**/*.md` | area plan and record editing |
| `.cursor/rules/11_pim_calendar_auto.mdc` | `01_calendar/**/*.md` | day/week/month file editing |
| `.cursor/rules/12_pim_tasks_auto.mdc` | `02_tasks/**/*.md` | task file maintenance |
| `.cursor/rules/13_pim_hard_commitment_safety.mdc` | PIM globs | protect hard commitments and plan-first behavior |
| `.cursor/rules/20_work_eb1_petition_auto.mdc` | `04_areas/work/EB1_B/**` | EB1-B petition writing and evidence discipline |
| `.cursor/rules/21_work_paper_review_nathan_manual.mdc` | manual | scientific review persona for glycoengineering and adjacent paper review |
| `.cursor/rules/22_work_due_diligence_research_auto.mdc` | work research globs | due diligence, external research, and source verification |
| `.cursor/rules/23_work_content_artifact_auto.mdc` | `04_areas/work/**/*.md` | work-area drafting, review, and content artifacts |
| `.cursor/rules/30_ai_facing_docs_detail_first.mdc` | AI-facing doc globs | preserve contract detail before compression |
| `.cursor/rules/31_prompt_boundary_task_vs_control_plane.mdc` | trigger | keep downstream prompts task-plane only |
| `.cursor/rules/32_reader_state_and_doc_self_review.mdc` | trigger | require reader-state and self-review for substantial handoffs |
| `.cursor/rules/33_chinese_writing_voice.mdc` | `**/*.md` | Chinese prose voice and anti-AI-writing checks |
| `.cursor/rules/34_prose_without_editorial_meta.mdc` | `**/*.md`, `**/*.mdc` | remove editorial meta from stable artifacts |
| `.cursor/rules/40_temporal_verification_tripwire.mdc` | trigger | verify current or time-sensitive claims |
| `.cursor/rules/41_parallel_subagent_admission.mdc` | trigger | admit parallel subagents only when justified |
| `.cursor/rules/42_staged_approach_for_destructive_ops.mdc` | trigger | dry-run and stage destructive or bulk operations |
| `.cursor/rules/50_subagent_model_parity.mdc` | trigger | avoid silent model downgrades in delegated work |
| `.cursor/rules/51_cursor_skill_physical_copy_contract.mdc` | skill globs | keep `.cursor/skills` as physical copies, not wrappers |
| `.cursor/rules/52_mirror_sync_contract.mdc` | mirror globs | maintain `09_soul` to `09_cursor` projection discipline |
| `.cursor/rules/90_maintenance_drift_audit_manual.mdc` | manual | drift audit and cleanup planning |
| `.cursor/rules/91_rules_skills_index_maintenance.mdc` | runtime globs | update indexes after rules or skills change |

## Portability Labels

- `<portable>` lives in `09_soul/` and is mirrored to `09_cursor/`.
- `<portable-shape>` describes how this Cursor projection mirrors portable material.
- `<project>` stays in this workspace because it depends on local paths, EB1-B, paper review persona, or PIM conventions.

The existing `.cursor/rules/` files are mostly `<project>`. They should not be promoted to `09_soul/` unless the lesson repeats across workspaces and can be expressed without local file paths.
