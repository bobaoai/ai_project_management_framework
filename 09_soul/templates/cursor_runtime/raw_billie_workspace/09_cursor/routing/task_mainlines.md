# Task Mainlines: billie_workspace

Cursor 默认先读 `.cursor/rules/00_hoveath_always.mdc`。本表用于把用户请求路由到本地 truth surface 与 Hoveath downstream skill。

| Signal | Mainline | First Authority | Truth Surface | Downstream Skill |
|---|---|---|---|---|
| EB1-B、petition、letter、attorney、recommendation | EB1-B petition writing | `.cursor/rules/20_work_eb1_petition_auto.mdc` | `04_areas/work/EB1_B/` | `hoveath-doc-self-review`, `hoveath-prose-without-editorial-meta` |
| paper review、manuscript、claim、reviewer、Nathan | Scientific review | `.cursor/rules/21_work_paper_review_nathan_manual.mdc` | `04_areas/work/paper_review/` | `hoveath-reader-state` |
| due diligence、research、survey、current info、verify | Research synthesis | `.cursor/rules/22_work_due_diligence_research_auto.mdc` | relevant `04_areas/work/**` | `hoveath-deep-research-survey`, `hoveath-temporal-verification` |
| strategy、plan、priority、trade-off、area review | Area planning | `.cursor/rules/01_core_task_routing.mdc` | `04_areas/**` | `hoveath-staged-approach`, `hoveath-doc-self-review` |
| calendar、today、tomorrow、week、schedule、time block | Time routing | `.cursor/rules/11_pim_calendar_auto.mdc` | `01_calendar/` | PIM rules |
| task、todo、breakdown、next step | Task maintenance | `.cursor/rules/12_pim_tasks_auto.mdc` | `02_tasks/` | PIM rules |
| cleanup、drift audit、missing yaml、ghost task | Drift audit | `.cursor/rules/90_maintenance_drift_audit_manual.mdc` | full workspace | PIM rules |
| 中文写作、润色、voice、改写 | Chinese writing | `.cursor/rules/33_chinese_writing_voice.mdc` | user-specified file | `hoveath-chinese-writing-voice` |
| proposal、design、methodology、retrospective | Proposal quality | `.cursor/rules/32_reader_state_and_doc_self_review.mdc` | user-specified file | `hoveath-doc-self-review` |
| prompt、subagent brief、worker instruction | Prompt boundary | `.cursor/rules/31_prompt_boundary_task_vs_control_plane.mdc` | prompt or instruction file | `hoveath-prompt-boundary` |
| rules、skills、INDEX、adapter、agent runtime | Runtime maintenance | `.cursor/rules/91_rules_skills_index_maintenance.mdc` | `.cursor/`, `09_cursor/`, `09_soul/` | `hoveath-skill-writing`, `hoveath-mirror-sync` |

## Overlay Rules

- If a request touches both area content and calendar scheduling, route to the area content mainline first, then schedule only after the work artifact is clear.
- If a request touches EB1-B facts, material-file discipline overrides prose polish.
- If a request asks for external or current facts, temporal verification overrides speed.
- If the user says `apply` or ends with `!`, file edits are allowed after interpreting scope; otherwise PIM maintenance stays PLAN-only.
