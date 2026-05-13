---
title: External Worker Execution Contract
status: active_draft
layer: T0
t0_layer_id: the_external_agent_management
reader_persona:
  - System Builder
  - External Worker Operator
  - Runtime Projection Maintainer
  - Reviewer
---

# External Worker Execution Contract

## 0. Contract Capsule

Machine-audit block. Keep paths, ids, aliases, commands, and ledger pointers plain; use citation ids only in body prose and `References`.

```yaml
layer: T0
t0_layer_id: the_external_agent_management
status: active_draft
canonical_owner: designDoc/the_external_agent_management.md
scope: governance for AI / model / CLI workers launched outside the current local agent loop, including prompt assembly, execution profiles, manifests, stale-output policy, and hard-stop policy
non_goals:
  - external facts, external verification, source connectors, broker APIs, market-data APIs, and PM/domain judgment
  - domain-specific review semantics owned by research, ingestion, writer, engineering, and schema/package skills
inputs:
  - 09_soul/skills/bestpractice_external_worker_general_module.md
  - 09_soul/skills/bestpractice_external_agent_builder.md
  - 09_soul/skills/bestpractice_prompt_boundary.md
  - owning skill CUSTOMIZE_MODULE / DATA_DEPENDENT_MODULE files
outputs:
  - external agent class taxonomy
  - admitted review_target_type registry
  - prompt-built manifests
  - external run manifests and sidecar logs
truth_surfaces:
  - 09_codex/skills/support-external-agent-builder/**
  - src/external_agents/manifest.py
  - src/tools/build_doc_review_prompt.py
  - src/writers/service.py
  - src/message_process/claude_image_review.py
runtime_triggers: see Machine Audit Runtime Surfaces
downstream_consumers:
  - support-external-agent-builder
  - support-design-doc-reviewer
  - support-skill-reviewer
  - support-schema-package-reviewer
  - research-thesis-verifier / research-evidence-reviewer / research-theme-report-reviewer
  - engineering-project-review
  - writer service and Claude image review runtime paths
open_decisions: see Open Decisions
review_gate: design-doc-reviewer
runtime_surface_ledger: see Machine Audit Runtime Surfaces
verification_hooks: see Machine Audit Runtime Surfaces
```

## 1. 这份文档负责什么

本文件定义 Hoveath / Analyst Billie 如何管理所有外部 AI 执行面。

外部执行面包括但不限于：

- Claude Code CLI
- DeepSeek V4
- Anthropic API
- Codex CLI
- OpenAI API
- Cursor / other agent CLI surfaces

这些 execution surfaces 是 control-plane。它们不定义任务本身。任务本身由本地 skill、Design Doc、prompt module、artifact contract、runner manifest 定义。

核心规则：

```text
External Worker 是被本地 contract 纳管的 worker，不是另一个自由聊天窗口。
```

## 1.5 Name Boundary / Non-Goals

This file does not own every repo concept that contains the word "external".

It owns only this boundary:

```text
an AI / model / CLI worker is launched outside the current local agent loop,
or an output from that worker is merged back into local artifacts.
```

It does not own:

- `external fact` / `external verification`: owned by research information gathering, source provenance, and evidence review contracts.
- `external source` / `source connector`: owned by Ingestion source connector, `source_collection.family` contracts (legacy alias: source-family), archive, and domain contracts.
- `external reference` / external project notes: owned by Learning Library and research-external-learning surfaces.
- external broker, market-data, or API services that are not AI workers: owned by their domain runtime contracts.

When one of those domains calls an AI worker, this contract governs the worker run mechanics. The domain still owns the meaning of the task.

## 2. 四类 External Worker Class

当前外部 worker 通过 `external_agent_class` 分四类。字段名保留 `external_agent_class`，因为它是运行时 manifest 里的稳定 schema 名；人读的 contract 名称使用 External Worker Execution。

| Class | Chinese shorthand | Owns | Does not own | Typical surface |
| --- | --- | --- | --- | --- |
| `external_writer` | 写作 | 从已装配 package 写初稿 / 改写稿 | canonical merge / PM judgment | DeepSeek V4, Claude Code CLI, Codex CLI |
| `external_editorial_reviewer` | 审稿 | 文章质量、reader-state、结构、表达、coverage critique | contract verdict / evidence verdict | Claude Code CLI, DeepSeek V4, Anthropic API, Codex CLI |
| `external_image_reader` | 看图 | 从图像提取 visible facts / visual evidence | `source_collection.family` policy / downstream thesis | Claude Code CLI today |
| `external_formal_reviewer` | Review | 独立 contract / schema / evidence / design / engineering verdict | authoring the artifact under review | Claude Code CLI, Codex CLI, sometimes DeepSeek V4 |

### 2.1 写作

External writer 只写 draft。

它可以：

- 从 deterministic package 写 PM-facing prose
- 按 writer direction 改写
- 生成 candidate report, observation, decision brief, or technical summary

它不可以：

- 覆盖 canonical report
- 改 owner decision
- 修改 source packet
- 自己补未给出的事实
- 把 draft 当成 accepted artifact

写作输出必须经过本地 merge / reviewer / owner gate。

### 2.2 审稿

External editorial reviewer 审文章，不做系统裁决。

它可以检查：

- reader gain
- mainline clarity
- section balance
- missing context
- unclear prose
- contradiction inside a draft
- whether package material was underused

它不可以：

- 判定 evidence_record verified
- 判定 code/design contract accepted
- 修改 PM belief
- 代替 formal reviewer

审稿的输出通常是 critique / revision suggestions，而不是 binding verdict。

Current implementation note: no production runner directly emits an `external_editorial_reviewer` manifest yet. Until an editorial-review runner is admitted, this class remains a governed category for manual or experimental critique and must not be consumed as implemented production behavior.

### 2.3 看图

External image reader 从视觉材料提取 evidence。

它可以：

- 读 chart / table / dashboard / screenshot / PDF crop
- 输出 visible facts, key numbers, uncertainty, image relevance
- 为 `read_content.md` 或 specialized packet 提供视觉证据

它不可以：

- 决定 source family policy
- 推动 thesis / theme / PM action
- 把不可读图像硬解释成结论

当前 production financial research image reader 是 Claude Code CLI path。其他模型可以做实验或 triage，但不得替代 production source-read contract，除非相应 Ingestion doc 和 tests 更新。

### 2.4 Review

External formal reviewer 负责独立裁决。

它可以：

- review Design Doc / skill / prompt / schema / package / code diff
- 输出 severity-ranked findings
- 给出 pass / pass-with-fixes / block
- 形成外部独立视角

它不可以：

- 同时 author artifact
- 悄悄修 artifact 再宣布通过
- 替 PM 做信念层决定
- 在没有 embedded evidence 的情况下引用本地路径做判断

Formal review 必须通过 prompt builder / module / manifest 进入，而不是手写一次性 prompt。

Formal review also must declare a `review_target_type`. `external_formal_reviewer` is the worker class; `review_target_type` decides which local contract owns the review lens.

Current target types:

| review_target_type | Canonical owner / lens | External reviewer checks | External reviewer does not own |
| --- | --- | --- | --- |
| `design_doc_review` | [Skill:support-design-doc-reviewer], [T0-Doc-Review] | authority layer, Contract Capsule, handoff, naming drift, duplicated canonical owner | writing or promoting the doc |
| `skill_review` | `support-skill-reviewer`, `bestpractice_skill_writing.md`, target skill, routing contracts | trigger clarity, positive/negative contract, required inputs, resource loading, routing overlap, output contract | domain verdict of the skill's subject matter |
| `thesis_review` | `research_50_thesis_and_theme_agent_cluster.md`, thesis verifier/adversary/evidence reviewer contracts | schema handoff, verification line, falsifiers, scenario triggers, evidence alignment | PM belief update or final investment decision |
| `theme_report_review` | `research-theme-report-reviewer` and report package contracts | package fit, evidence support, report-side findings, reader-state issues | replacing report owner / writer |
| `evidence_review` | `research-evidence-reviewer`, `evidence_source_trust_contract.md` | whether evidence supports a claim and whether trust/source surface is adequate | `source_collection.family` admission or PM action |
| `code_review` | [Skill:engineering-project-review], [T0-Runtime-Code] | diff risk, tests, regression, contract mismatch, TradeCLI/runtime admission | editing the diff under review |
| `prompt_or_runner_review` | [Skill:support-external-agent-builder], [Portable-Prompt-Boundary] | prompt assembly, embedded evidence, manifest, cache shape, stale-output risk | domain-specific correctness of the worker's subject |
| `schema_or_package_review` | `support-schema-package-reviewer`, owning Design Doc / package contract | schema conformance, required fields, downstream handoff | inventing new schema authority |

If a review target is not in this table, the caller must either map it to the nearest owner contract or treat it as an exploratory manual review, not an admitted external formal review.

Prompt / runner review has one extra independence rule. When the target under review is itself owned by `support-external-agent-builder` (for example `SKILL.md`, `external_review_builder.md`, `formal_review_targets.json`, or `src/tools/build_doc_review_prompt.py`), the builder may assemble the prompt but must pair the review with a peer lens such as `support-design-doc-reviewer` or `engineering-project-review`. Builder-only self-review is not an admitted final gate for builder-owned surfaces.

This independence rule is currently a review-gate discipline, not a builder-code hard stop. If it needs automation, the manifest must grow a `paired_reviewer_skill` field and the review gate must validate it before accepting builder-owned surface reviews.

## 3. Execution Surface Registry

External Worker Execution 层记录 execution surface，但不把 surface 身份写进 worker prompt。

| Surface | Registry id | Typical use | Operational notes |
| --- | --- | --- | --- |
| Claude Code CLI | `claude_code_cli` | formal review, image read, extraction, high-quality rewrite | local CLI path and auth are runtime concerns |
| DeepSeek V4 | `deepseek_v4` | long-form writing, editorial critique, second-opinion review | writer backend / API surface |
| Anthropic API | `anthropic_api` | long-form writing, vision reads, evaluator / reviewer experiments | API key and model are runtime concerns |
| Codex CLI | `codex_cli` | external coding/design review, repo-local implementation worker | local CLI auth and session state are runtime concerns |
| OpenAI API | `openai_api` | structured extraction, evaluator, lightweight reviewer | model choice recorded in run manifest |
| Cursor CLI | `cursor_cli` | local external writer / agent execution | treated like any other execution surface |

New local agent CLIs must apply for their own registry id. They do not inherit `cursor_cli` as a catch-all bucket.

Execution surface belongs in:

- runner manifest
- run log
- handoff
- cost / quota records

Execution surface does not belong in:

- worker task-plane prompt
- target artifact
- source evidence

Silent violation signal:

```text
worker output says "as Claude / as DeepSeek / as Codex CLI..."
```

That usually means control-plane leaked into task-plane prompt.

## 4. Prompt Assembly Contract

External prompts must be assembled, not hand-written.

Canonical shape:

```text
stable builder prefix
  + GENERAL_MODULE
  + CUSTOMIZE_MODULE
  + DATA_DEPENDENT_MODULE
  + embedded references
  + embedded target artifacts
```

Rules:

- Stable prefix is owned by builder code.
- General module is portable worker conduct.
- Customize module defines task goal, verdict labels, output schema.
- Data-dependent module defines target artifact semantics and allowed evidence.
- Task-specific prompt modules must be carried by the owning skill, not generated as loose `.scratch/` prompts.
- Dynamic input is appended last.
- Local files must be embedded, not merely named.
- Manifest must record prompt hashes and execution surface.

The ownership shape is:

```text
builder code owns the stable upstream prompt
portable soul owns GENERAL_MODULE
owning skill owns CUSTOMIZE_MODULE + DATA_DEPENDENT_MODULE
runtime object selection owns the dynamic suffix
```

For external review, `src/tools/build_doc_review_prompt.py` must receive at least one `--module` path from an admitted skill directory. A generated prompt without a skill-carried module is not an admitted External Worker prompt.

Admitted module roots:

- `09_codex/skills/`: active Codex project skill modules.
- `09_soul/skills/`: portable source modules when the review lens is genuinely portable.
- `.cursor/skills/`: legacy / frozen Cursor skill modules; do not add new external-review modules here unless the Cursor projection is explicitly reopened.

Current doc/skill/design review builder:

```text
src/tools/build_doc_review_prompt.py
```

Current review subskill:

```text
09_codex/skills/support-external-agent-builder/external_review_builder.md
```

Current target registry:

```text
09_codex/skills/support-external-agent-builder/formal_review_targets.json
```

## 5. Manifest And Run Log

Every external run must be recoverable from local state.

`runner_family` is not enough. It says which execution surface was used, not which concrete model / effort / timeout profile was launched.

Every external run must also record an explicit execution profile:

```yaml
execution_profile:
  profile_id: <stable local profile id>
  model_id: <exact model or CLI model string>
  reasoning_profile: <xhigh | high | max | reasoning_max | none | provider-specific label>
  temperature: <number | null>
  max_output_tokens: <integer | null>
  timeout_sec: <integer | null>
  max_retries: <integer | null>
  parallelism: <integer | null>
```

Execution profile values are control-plane metadata. They belong in manifests / run logs / handoffs, not worker prompts, unless the task genuinely depends on the model capability.

Known execution profile shapes:

| profile_id | runner_family | model_id semantics | reasoning_profile | status | Notes |
| --- | --- | --- | --- | --- | --- |
| `claude_code_cli_opus_4_7_max` | `claude_code_cli` | `claude-opus-4-7` | `max` | active | production image-review path |
| `anthropic_api_opus_4_7_xhigh` | `anthropic_api` | resolved model, default `claude-opus-4-7` | `xhigh` | active | Anthropic writer backend default profile; manifest records resolved `model_id` |
| `codex_cli_gpt_5_5_xhigh` | `codex_cli` | `gpt-5.5` | `xhigh` | admitted | formal external review payloads |
| `openai_api_gpt_5_5_xhigh` | `openai_api` | `gpt-5.5` | `xhigh` | proposed | becomes admitted only when the OpenAI API runner supports this exact model/profile pair |
| `deepseek_v4_reasoning_max` | `deepseek_v4` | resolved model, default `deepseek-reasoner` | `reasoning_max` | active | writer service profile; operators may override the resolved model via `DEEPSEEK_MODEL` without creating a new profile id |
| `cursor_cli_<safe_model>_none` | `cursor_cli` | resolved model from caller/backend | `none` | active | dynamic writer-service profile id; model text is normalized into `<safe_model>` |

Profile status semantics:

- `active` means current production code can emit this profile today.
- `admitted` means the profile is reviewed and may be used by a new runner without a new T0 design decision.
- `proposed` means the profile remains an open decision and must not appear in production manifests until a runner and tests land.

Minimum manifest fields:

```yaml
schema_version:
runner_family: claude_code_cli | deepseek_v4 | anthropic_api | codex_cli | openai_api | cursor_cli | unspecified
external_agent_class: external_writer | external_editorial_reviewer | external_image_reader | external_formal_reviewer
review_target_type: required when external_agent_class = external_formal_reviewer
execution_profile:
prompt_path:
manifest_path:
full_prompt_sha256:
static_prompt_hash:
general_module_hash:
customize_module_hash:
data_dependent_module_hash:
input_payload_hash:
target_artifacts:
embedded_references:
output_path:
status:
```

Two manifest schemas are admitted:

- `external_agent_run_manifest_v1` for non-formal-review runs such as writers and image readers.
- `doc_review_prompt_manifest_v1` for formal-review prompt-built artifacts.

Schema-specific extension fields:

```yaml
doc_review_prompt_manifest_v1:
  generated_at_utc: required
  review_modules: list of skill-carried module paths
  components: per-embedded-file records with role, path, sha256, and optional section_sha256

external_agent_run_manifest_v1:
  generated_at_utc: required
  extra: task-specific fields passed through by the runner, such as writer_task_kind, writer_role, operation, or research_id
```

For prompt-only builder manifests that have not launched a worker yet, `output_path` may be null and `status` should be `prompt_built`. A post-execution run manifest / run log must fill the actual worker output path and final status.

For legacy writer / image-reader workers that do not yet use the `GENERAL_MODULE / CUSTOMIZE_MODULE / DATA_DEPENDENT_MODULE` split, the module hash fields remain present and may be null. The run must still record the full prompt hash, static prompt hash when recoverable, input payload hash, execution profile, target artifacts, output path, and status.

Long-running or batch runners should produce a batch-level JSONL run log with:

- `run_start`
- `object_submitted`
- `object_result`
- `object_saved`
- `run_complete` or `run_stopped_*`

Existing Claude image review currently records per-object launch attempts and pre-flight skip outcomes in `image_review_manifests.jsonl`. Batch-level event logging remains proposed until a runner implements these event names and tests cover them.

Hard blockers such as auth failure, quota, `429`, missing CLI, systemic parser failure, or malformed prompt stop the run.

## 5.5 Open Decisions

These are unsettled and must not be consumed as implemented behavior:

- Production image-read admission for execution surfaces other than Claude Code CLI.
- Production editorial-review runner admission for `external_editorial_reviewer`.
- A source/text external reader class beyond image reading.
- OpenAI API `gpt-5.5` xhigh profile admission, pending an implemented runner with that exact model/profile pair.
- Batch-level JSONL event logging for long-running runners.

## 6. Relationship To Skills

`support-external-agent-builder` owns runner construction.

Domain skills own what the worker should judge or produce.

Examples:

- [Skill:support-design-doc-reviewer] defines design-doc review requirements.
- The Codex prompt module [Module-External-Review-Builder] assembles the external review prompt.
- `research-thesis-verifier`, `research-thesis-adversary`, and `research-evidence-reviewer` own thesis / evidence review semantics.
- `support-skill-reviewer` owns the skill-review lens; `bestpractice_skill_writing.md`, the target skill, and routing contracts are the lens references it draws from.
- `support-schema-package-reviewer` owns schema/package handoff review; the owning Design Doc or package contract remains the domain authority.
- `ingestion-source-family-operator` (skill id retained for compatibility) owns `source_collection.family` image policy.
- `ingestion-image-review-reader` owns production image review execution; `message review-images-claude` is a runtime command / runner alias for that path.
- `writer-handoff` and package-producing research tools own writer package / draft semantics; `src/writers/service.py` owns the shared writer runtime sidecar implementation.

Do not let external agent builder replace domain ownership. It builds the runner surface; it does not decide the domain verdict.

## 6.5 Current Class Admission Records

| external_agent_class | Current admission | Output artifact | Validation gate | Stale / hard-stop policy |
| --- | --- | --- | --- | --- |
| `external_writer` | active through writer service sidecars | `<output>.writer.json` plus draft output | local writer merge / reviewer / owner gate | stale sidecars are not accepted as canonical merge evidence; backend/auth/parser blockers stop the run |
| `external_image_reader` | active for Claude Code CLI production image reader | `image_review_manifests.jsonl` rows plus extracted image review output | ingestion image-reader tests and source-read owner gate | pre-flight skip outcomes are logged; auth/quota/parser blockers stop the batch path |
| `external_formal_reviewer` | active for prompt-built formal review | prompt markdown plus `doc_review_prompt_manifest_v1` | owning review skill plus manifest/test hooks | prompt-built output is not accepted as final review until worker output path/status are recorded |
| `external_editorial_reviewer` | proposed / governed class only | n/a until runner admission | n/a until runner admission | do not emit production manifests with this class until runner and tests exist |

## 7. Admission Rule For New External Worker Types

A new external agent type must define:

```yaml
external_agent_class:
review_target_type:  # required for external_formal_reviewer
execution_profile:
owner_skill:
prompt_builder_or_template:
skill_prompt_module_path:
customize_module:
data_dependent_module:
input_selection_rule:
output_artifact:
validation_gate:
stale_output_policy:
hard_stop_policy:
```

When `customize_module` and `data_dependent_module` live in the same skill module file, list the same path in `skill_prompt_module_path`, `customize_module`, and `data_dependent_module`. When a writer, image-reader, or other runner splits these modules across files, list each concrete path separately and use `n/a` rather than a blank value for a module the runner does not use.

If these are absent, the task can still be done manually in-session, but it is not an admitted External Worker.

## 7.5 Machine Audit Runtime Surfaces

```yaml
runtime_surface_ledger:
  - surface: skill
    projection: codex
    path_or_command: 09_codex/skills/support-external-agent-builder/SKILL.md
    owner: designDoc/the_external_agent_management.md
    doc_claim: Codex-side entry skill for external AI runner construction.
    sync_obligation: Update when external agent classes, execution surface ids, prompt assembly invariants, manifest fields, or admission rules change.
    status: active
  - surface: prompt_module
    projection: codex
    path_or_command: 09_codex/skills/support-external-agent-builder/external_review_builder.md
    owner: 09_codex/skills/support-external-agent-builder/SKILL.md
    doc_claim: Formal external review builder for doc / skill / design / code / evidence / package review prompts.
    sync_obligation: Update when `external_formal_reviewer`, `review_target_type`, or prompt-builder CLI args change.
    status: active
  - surface: registry
    projection: codex
    path_or_command: 09_codex/skills/support-external-agent-builder/formal_review_targets.json
    owner: 09_codex/skills/support-external-agent-builder/SKILL.md
    doc_claim: Maps each admitted formal `review_target_type` to its owning skill module, default references, and smoke target.
    sync_obligation: Update when a review target type, owning skill, module path, or default reference set changes.
    status: active
  - surface: helper
    projection: runtime_agnostic
    path_or_command: src/external_agents/manifest.py
    owner: designDoc/the_external_agent_management.md
    doc_claim: Shared manifest/hash/execution-profile helper for non-formal external writer and image-reader runs.
    sync_obligation: Update when manifest minimum fields, execution profile shape, status naming, or JSONL sidecar behavior changes.
    status: active
  - surface: builder
    projection: runtime_agnostic
    path_or_command: src/tools/build_doc_review_prompt.py
    owner: 09_codex/skills/support-external-agent-builder/external_review_builder.md
    doc_claim: Builds prompt + manifest for external formal review.
    sync_obligation: Update tests, Design Doc reviewer skill, and docs when CLI args or manifest fields change.
    status: active
  - surface: runner
    projection: runtime_agnostic
    path_or_command: src/writers/service.py
    owner: 09_codex/skills/writer-handoff/SKILL.md and src/writers/service.py
    doc_claim: Writes external_writer sidecar manifests into `<output>.writer.json`.
    sync_obligation: Update writer tests and this contract when writer backend ids, execution profile mapping, prompt hash fields, or sidecar naming change.
    status: active
  - surface: runner
    projection: runtime_agnostic
    path_or_command: src/message_process/claude_image_review.py
    owner: 09_codex/skills/ingestion-image-review-reader/SKILL.md and src/message_process/claude_image_review.py
    doc_claim: Runs Claude Code CLI production image review through runner alias `message review-images-claude` and appends one `image_review_manifests.jsonl` row per launch attempt or pre-flight skip outcome, with status in `reviewed`, `failed`, `parse_failed`, `blocked_quota`, or `skipped_already_reviewed`.
    sync_obligation: Update image review tests and this contract when model/effort, hard-stop behavior, prompt shape, output row identity, or manifest fields change.
    status: active
  - surface: test
    projection: runtime_agnostic
    path_or_command: tests/test_doc_review_prompt_builder.py
    owner: src/tools/build_doc_review_prompt.py
    doc_claim: Regression test for manifest-only execution surface metadata and formal review target classification.
    sync_obligation: Update when manifest minimum fields or prompt leakage rules change.
    status: active
  - surface: test
    projection: runtime_agnostic
    path_or_command: tests/test_external_review_target_modules.py
    owner: 09_codex/skills/support-external-agent-builder/formal_review_targets.json
    doc_claim: Regression test that every admitted formal review target has an existing skill-carried module and can build a prompt + manifest.
    sync_obligation: Update with registry shape, target type list, or module ownership changes.
    status: active
  - surface: test
    projection: runtime_agnostic
    path_or_command: tests/test_writer_service.py
    owner: src/writers/service.py
    doc_claim: Regression test that external_writer sidecars include T0 manifest fields and execution profile.
    sync_obligation: Update when writer sidecar fields or backend profile mapping changes.
    status: active
  - surface: test
    projection: runtime_agnostic
    path_or_command: tests/test_claude_image_review.py
    owner: src/message_process/claude_image_review.py
    doc_claim: Regression test that Claude image review prompt keeps runner identity out of task-plane and writes external_image_reader manifest rows.
    sync_obligation: Update when image prompt shape, model/effort, manifest path, or usage fields change.
    status: active
verification_hooks:
  - ./.venv/bin/python -m pytest tests/test_doc_review_prompt_builder.py -q
  - ./.venv/bin/python -m pytest tests/test_external_review_target_modules.py -q
  - ./.venv/bin/python -m pytest tests/test_writer_service.py tests/test_claude_image_review.py -q
```

## 8. Bottom Line

External Worker Execution 层的目标不是多接几个模型，而是让每个外部模型调用都能回到本地 contract、artifact、manifest、review gate。

模型可以不同；runner 不变量必须相同。

## 9. References

- `[T0-Doc-Review]` [Design Doc Review Gate Contract](the_design_doc_management.md)
- `[T0-Runtime-Code]` [Runtime Code Admission And Audit Contract](the_tradecli_code_management.md)
- `[Portable-Prompt-Boundary]` [Portable Prompt Boundary](../09_soul/skills/bestpractice_prompt_boundary.md)
- `[Skill:support-design-doc-reviewer]` logical skill id `support-design-doc-reviewer`; current Codex projection: [Design Doc Reviewer Skill](../09_codex/skills/support-design-doc-reviewer/SKILL.md)
- `[Skill:support-external-agent-builder]` logical skill id `support-external-agent-builder`; current Codex projection: [External Agent Builder Skill](../09_codex/skills/support-external-agent-builder/SKILL.md)
- `[Skill:engineering-project-review]` logical skill id `engineering-project-review`; current Codex projection: [Engineering Project Review Skill](../09_codex/skills/engineering-project-review/SKILL.md)
- `[Module-External-Review-Builder]` Codex projection prompt module for `[Skill:support-external-agent-builder]`: [External Review Builder Module](../09_codex/skills/support-external-agent-builder/external_review_builder.md)
