# Rules Index: Hoveath Mother Repo Cursor Projection

Cursor-native rules live in `.cursor/rules/` and are the executable rule layer for Cursor.

## Numbering Bands

| Band | Meaning |
|---|---|
| `00` | Always-on Cursor bootstrap and Hoveath runtime contract |
| `01-09` | Task routing, axiom retrieval, and skill admission |
| `30-39` | AI-facing docs, prompt hygiene, reader-state, and prose quality |
| `40-49` | Verification, subagent admission, and staged execution |
| `50-59` | Cursor runtime maintenance and projection contracts |
| `90-99` | Index hygiene and maintenance |

## Rule Map

| Rule | Loading | Role | Portability |
|---|---|---|---|
| `.cursor/rules/00_hoveath_always.mdc` | always | Cursor startup and mother-repo runtime contract | `<project>` |
| `.cursor/rules/01_core_task_routing.mdc` | trigger | route requests to mother-repo truth surfaces before acting | `<portable-shape>` |
| `.cursor/rules/02_axiom_retrieval_triggers.mdc` | trigger | retrieve axioms for higher-frame judgment | `<portable-shape>` |
| `.cursor/rules/03_skill_admission_contract.mdc` | trigger | decide when to invoke Hoveath skills | `<portable-shape>` |
| `.cursor/rules/30_ai_facing_docs_detail_first.mdc` | AI-facing doc globs | preserve contract detail before compression | `<portable-shape>` |
| `.cursor/rules/31_prompt_boundary_task_vs_control_plane.mdc` | trigger | keep downstream prompts task-plane only | `<portable-shape>` |
| `.cursor/rules/32_reader_state_and_doc_self_review.mdc` | trigger | require reader-state and self-review for substantial handoffs | `<portable-shape>` |
| `.cursor/rules/33_chinese_writing_voice.mdc` | markdown globs | Chinese prose voice and anti-AI-writing checks | `<portable-shape>` |
| `.cursor/rules/34_prose_without_editorial_meta.mdc` | markdown/rule globs | remove editorial meta from stable artifacts | `<portable-shape>` |
| `.cursor/rules/40_temporal_verification_tripwire.mdc` | trigger | verify current or time-sensitive claims | `<portable-shape>` |
| `.cursor/rules/41_parallel_subagent_admission.mdc` | trigger | admit parallel subagents only when justified | `<portable-shape>` |
| `.cursor/rules/42_staged_approach_for_destructive_ops.mdc` | trigger | dry-run and stage destructive or bulk operations | `<portable-shape>` |
| `.cursor/rules/50_subagent_model_parity.mdc` | trigger | avoid silent model downgrades in delegated work | `<portable-shape>` |
| `.cursor/rules/51_cursor_skill_physical_copy_contract.mdc` | skill globs | keep `.cursor/skills` as physical copies, not wrappers | `<portable-shape>` |
| `.cursor/rules/52_mirror_sync_contract.mdc` | mirror globs | maintain `09_soul` to runtime projection discipline | `<portable-shape>` |
| `.cursor/rules/91_rules_skills_index_maintenance.mdc` | runtime globs | update indexes after rules or skills change | `<portable-shape>` |

## Excluded From Mother Repo

The raw billie snapshot also contains PIM and work-domain overlays. They are intentionally not installed in the mother repo:

- `10-13` PIM rules
- `20-23` work-domain rules
- `90_maintenance_drift_audit_manual.mdc`

These stay in `09_soul/templates/cursor_runtime/raw_billie_workspace/` as distillation input.
