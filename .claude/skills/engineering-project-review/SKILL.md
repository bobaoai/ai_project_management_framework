---
name: engineering-project-review
description: "Independent reviewer-of-colleague's-work skill for engineering commits in this repo (charter-alignment phases, schema/contract changes, skill cluster modifications, validator/harness extensions). Triggered when a peer Claude/Cursor session lands one or more commits and the user says '独立 review 下' / '新一轮 review' / '同事干的活独立 review'. Reproduces every claimed validation gate, reads the actual commit diff (not just the message), cross-checks schema enums against canonical stores, instructions against runtime enforcement, mirror dirs against each other, and returns severity-tagged findings + a prioritized punch list. This skill is review-only: it does not author, fix, or refactor."
---

# Project Review

Independent peer review of engineering commits in `trading_platform`. Distilled from the
A.1 / A.2 charter-alignment review pattern.

This skill exists because **a colleague's self-summary describes what they intended, not
necessarily what they did**. Treat the colleague's commit message and校验门 claims as inputs
to verify. They are not truths to relay.

## Positive Contract

- Current persona: independent code reviewer
- Current task: verify peer-authored commit(s) against claimed gates + charter / contract
  invariants + cross-cutting hygiene checks; emit severity-tagged findings + punch list
- Primary truth surface:
  - the commit(s) under review (`git show <ref>`, `git diff <ref>~1 <ref>`)
  - the actual files in the working tree (post-commit state)
  - the校验门 commands the colleague claimed to have run
  - `designDoc/the_tradecli_code_management.md` when the change touches `tradectl`,
    runtime code, schemas, validators, fixtures, or command-side effects
  - `designDoc/the_charter.md` + `designDoc/the_timestamp_semantic.md` when phase scope
    intersects schema / contract layers
- Output artifact:
  - inline review reply by default (校验门 table + finding cards + punch list)
  - optional `data/internal_reviews/<YYYY-MM-DD>_<commit_short>.md` only if user asks
- Reader end-state: the user (or the colleague themselves) can decide which findings to
  fix immediately, which to defer to the next phase, and which to discard.

## When To Use

- A peer Claude / Cursor / human session has landed one or more commits and the user wants
  an independent verdict before moving to the next phase.
- The user types `我同事干的活独立 review 下` / `新一轮 review` / `review 下 commit X`.
- After a phase-labeled commit (e.g. "Phase A.1", "batch 1") to check phase entry / exit
  invariants.

## Do Not Use When

- The user is asking you to **author or rewrite** the work. This skill never produces
  the artifact under review; it only judges.
- The review target is content (theme report draft, thesis prose). Route to
  `research-theme-report-reviewer` or `research-theme-report-debater` instead.
- The user is asking for a security audit. Use the `/security-review` slash command.
- The user is asking "what should I do next" without a recent peer commit to anchor to.
  Route via `routing-task-mode-router`.
- The work is a generic PR that does not touch charter / schema / contract / skill
  cluster. Use the built-in `/review` slash command instead. This skill's cross-cutting
  checks pay off only on repo-internal phase commits.

## Relationship To Adjacent Skills

- `research-theme-report-reviewer`: content-layer reviewer for **theme report drafts**. This skill is
  engineering-layer reviewer for **code / schema / contract / skill commits**. No overlap.
- `research-theme-report-debater`: content-logic adversary on theme drafts. No overlap.
- `/review` (built-in): GitHub PR review. Use this skill instead when the work is a local
  commit chain not yet pushed, or when the review needs charter-rule cross-checks the
  generic PR reviewer cannot do.

## Required Inputs

Read in this order:

1. `git log --oneline -<N>` to map the commit chain under review
2. `git show --stat <ref>` for each commit (file count + line delta sanity)
3. `git show <ref>` for the full message; capture every claim the colleague made
4. `git diff <ref>~1 <ref> -- <touched-files>` to read the actual change rather than the summary
5. The post-commit state of any file the diff touched (Read tool, full file when small)
6. Any校验门 command the commit message named, rerun verbatim

Read on demand:
- `designDoc/the_charter.md` when phase touches charter rules
- `designDoc/the_timestamp_semantic.md` when phase touches time-field schemas
- `designDoc/the_tradecli_code_management.md` when phase touches `tradectl`, runtime
  builders, schemas, validators, fixtures, or command-side effects
- `designDoc/the_artifact_graph.md` when phase touches graph-admitted artifact builders
- `designDoc/the_design_doc_management.md` when phase touches Design Doc runtime ledgers
- `09_soul/axioms/` when finding implicates a foundational axiom (e.g. T11, FP)
- prior commits in the chain when current commit references them (e.g. "addresses F1 from
  commit X")

If the user only gave a commit ref and no claimed gates, derive the gates from the commit
message body. If even those are missing, ask the user for the校验门 list explicitly. Do
not invent gates the colleague did not claim.

## Three-Phase Pipeline (Mandatory, In Order)

### Phase 1: Reproduce Claimed Gates

Every校验门 claim in the commit message becomes one row of a table. Rerun the command
verbatim using `./.venv/bin/python` per repo R9. Compare:

| 校验门 (colleague's claim) | 我复跑结果 | 一致 |
|---|---|---|
| `tradectl test-thesis-agent` 29/29 | <actual> | ✓ / ✗ |
| `pytest -k "..."` 43/43 | <actual> | ✓ / ✗ |
| `timeaudit` global N | <actual> | ✓ / ✗ |
| jsonschema validate K samples | <actual> | ✓ / ✗ |

When a number doesn't match, state both the claimed and observed numbers and investigate
before judging. Sometimes the colleague filtered tests differently (`-k "X or Y"` vs raw
`pytest tests/<file>.py`); reconcile filter scope before calling it a discrepancy.

If the colleague claimed "0 finding" on a focused timeaudit, rerun with `--include` on the
exact paths they touched, not the global scan.

### Phase 2: Read The Diff

The commit message is a hypothesis; the diff is the truth. For each touched file:

- `git diff <ref>~1 <ref> -- <file>` and read the actual change
- `Read` the full post-commit file when the change is structural (schema, contract,
  registry). Partial diff context misses cross-section invariants.
- Compare diff against commit message and flag every change not mentioned (scope bleed).
- For `.gitignore` / framework files, list every entry added/removed; commit messages
  routinely undersell `.gitignore` churn.

Phase 2 produces a "what actually changed" mental model independent of what the colleague
said changed.

### Phase 3: Cross-Cutting Checks

Each is a known foot-gun in this repo's history.

| Check | When to run |
|---|---|
| 3.1 Schema enum vs canonical store | Every review (cheap; covers F1 trap) |
| 3.2 SKILL.md / schema instruction vs runtime fixture coverage | Every review (covers F5 + B.1/D.1 validator-fixture pairing trap) |
| 3.3 Mirror consistency | Only when commit touches `.claude/` / `.cursor/` / `09_soul/` / `09_claude/` |
| 3.4 Contract / registry / test sync | Only when commit modifies `the_timestamp_semantic.md` §4 matrix |
| 3.5 Commit scope bleed | Every review (cheap; covers F3 trap) |
| 3.6 Time-field semantic correctness | Every review when commit introduces new evidence_record / perplexity_log / thesis_note / fixture file |
| 3.7 Cross-phase delta narration | Every review when commit message mentions a numeric "stable" / "unchanged" claim (timeaudit count, corpus validation count, fixture pass count) |
| 3.8 Aggregate-count denominator transparency | Every review when commit message contains an "X/X valid" or "N/N pass" form |
| 3.9 Vertical vs longitudinal review 区分 | Every single-phase review startup — must explicitly distinguish vertical (this phase only) findings from longitudinal (cross-phase pattern) observations |
| 3.10 Working tree dirty state 必查 | Every review, before reproducing claimed gates (Phase 1) — `git status --short` first, dirty-state-induced fail rate ≠ commit failure |

#### 3.1 Schema enum vs canonical store existence

For every JSON schema added or modified, find every `enum` whose values look like store /
system slugs (e.g. `messages_index`, `perplexity_log`, `image_reviews`, `broker_record`):

- Confirm each slug has a corresponding canonical store under `data/research/` or
  `data/runtime/` (`ls data/research/<slug>*` / find the path the slug points to)
- Slugs in the enum without a canonical store are **dangling enum values** (F1 / F6 class
  finding). Schema validation passes but charter §IV "fail loud" is broken: future records
  can fabricate IDs against a non-existent store.

#### 3.2 SKILL.md / schema instruction vs runtime fixture coverage

Two related foot-guns:

**(a) SKILL.md "MUST X" instruction vs tool reality.** For every new "MUST emit X" / "Every
invocation appends Y" instruction added to a SKILL.md:

- Check whether the named tool / module actually performs the action (`git diff` the tool
  source, or `Read` the function)
- Check whether the validator / harness actually fails when the action is skipped
- Instruction-only enforcement (no runtime gate) is an **F5 class finding**: fail-loud
  charter §IV承诺 mismatch. Note whether the gap is naturally closed by an upcoming phase
  (Phase B reviewer gate, Phase D adversarial_review_log etc).

**(b) Schema description "validator-side cross-check" vs fixture coverage.** When a schema
description writes "validator-side cross-check: file must exist at <path>" (or any phrase
delegating enforcement to validator-level rather than schema-level):

- Confirm the validator function actually exists (`grep -n "def validate_" src/tools/`)
- Confirm a fixture exercises the cross-check path (happy + dangling negative pair)
- Confirm the harness wires the validator into the fixture run (otherwise validator is
  unreached code)

Validator function exists but harness does not call it = **half-implemented gate** (B.1
F5(b) perplexity_log_ref_integrity pattern; D.1 parent_thesis_id pattern). Either补 fixture
in the same commit or open a follow-up commit before next phase locks.

#### 3.3 Mirror consistency

If the commit touches `.claude/skills/` or `.claude/skills/`, diff the two mirrors for
every modified skill:

```
diff .claude/skills/<id>/SKILL.md .claude/skills/<id>/SKILL.md
```

Empty diff = clean mirror. Non-empty diff = mirror drift, flag immediately. Note whether
commit message mentions dual-mirror update (F8 class finding when not mentioned).

#### 3.4 Contract / registry / test sync

If the commit modifies `designDoc/the_timestamp_semantic.md` §4 matrix:
- `src/core/timekeeping/registry.py` `PER_CLASS_MATRIX` must update in same commit
- `tests/test_timekeeping.py` `EXPECTED_CLASSES` + `archive_classes` must update
- `tradectl timeaudit` must still pass on touched fixtures

If the commit adds a new class to the matrix, the三方 sync (contract / registry / test)
must all land together. Partial sync is a **regression vector**.

#### 3.5 Commit scope bleed

For each commit, list every concern touched. Concerns to itemize:
- the headlined work (what the commit message advertises)
- contract / design doc changes
- previously-untracked files entering git (check `.gitignore` diff)
- `.gitignore` rule additions unrelated to the headlined work
- mirror sync (.claude / .cursor / 09_soul / 09_claude)

If the commit touches more than one concern and the message does not call out each one
explicitly, that is **F3 class finding**. Bisect / revert hygiene degrades.

#### 3.6 Time-field semantic correctness on new samples / fixtures

For every new evidence_record / perplexity_log / thesis_note / fixture file the commit
introduces:
- Validate against schema (`jsonschema.validate`)
- Re-validate against `src.core.timekeeping.registry.validate_object` for the matrix row
- Read each timestamp field and verify it carries the **right semantics** (charter §III
  recorded_at = 我方 write moment; observed_at = 外部事件 moment; updated_at = mutable-field
  last-edit moment). Watch for the F2 class mistake: setting `observed_at_utc` to the
  agent-action moment instead of the underlying event moment, or filling it on
  interval / 综合性 evidence (schema rule says leave empty).

#### 3.7 Cross-phase delta narration

Foot-gun: commit message says "X stable" / "X unchanged" but X is only stable
**within-commit**, not across phases (B.1 / C.1 / C.3 trio all hit this on `timeaudit`
counts).

For every numeric claim phrased "stable at N" / "unchanged at N" (timeaudit violations,
fixture pass counts, corpus validation counts):

- Compare N against the prior phase commit's number (`git show <prior> | grep -i "<metric>"`)
- If N changed, commit message must narrate: (a) current value, (b) delta vs prior phase,
  (c) where the delta is going (deferred phase / plan link / fix commit reference)
- "Stable" alone is fine within a single commit. Across phases, "stable" without delta
  narration is a transparency lapse (same class as 3.8 creative-count). Flag and ask the
  colleague to update the message or land a follow-up note.

Engineering quality加分 when the commit pre-emptively writes the delta line (e.g. D.1's
"665 → 672 (+7 inherited fixture field names; Phase D.6 rename 时归零)". That's the
target shape.

#### 3.8 Aggregate-count denominator transparency

Foot-gun: commit message claims "X/X valid" but X is a hand-picked numerator over a much
larger denominator (C.3 "15/15 thesis_notes valid"; actual was 15 of 56, with 41
pre-v1.5 records silently failing).

For every "X/X" / "N/N" form in the commit message:

- Independently `glob` the corpus the claim implies (`data/research/<class>/*.json`,
  fixture set, etc.) and validate with the schema the colleague named
- If denominator > numerator, commit message must phrase as "X of TOTAL valid; (TOTAL-X)
  deferred to <phase>" or equivalent
- Single-number claims with hidden denominators are **creative accounting**. Flag as
  MEDIUM finding (real production-state misrepresentation) plus ask for a follow-up to
  patch (a) message wording, (b) the deferred-scope item in the plan doc

The honest form trades brevity for replay-correctness: future readers can `glob` and
verify the corpus state without re-deriving the denominator.

#### 3.9 Vertical vs longitudinal review 区分

每次 single-phase review 启动时, 显式区分当前 review 是 **vertical** (single phase exit
criterion 自洽 — 仅按 phase 自身的 charter / contract / plan 字面要求评 finding) 还是
**longitudinal** (跨 phase pattern — 4 phase 全部 dogfood 0%, contract inheritance 漏审
跨 phase 累积, [done]-vs-partial 错位跨 4 phase 同款).

不要把 longitudinal verdict (e.g. "alignment chain 失败" / "4 phase 全错标 done") 强加到
single-phase finding 上. Single-phase review 的 finding severity 仅按 phase 自身要求评.
Cross-phase pattern 单独写 longitudinal section, severity 跟 single-phase finding 不混.

输出 report 必须显式标两段:

- **§N. Vertical findings (this phase only)** — 按 phase 自身 charter / contract / plan
  字面要求, severity 按 §Severity Taxonomy. Author 责任范围.
- **§N+1. Longitudinal observations (cross-phase pattern)** — 跨 phase pattern, attribution
  归 framework gap / process gap, 不归单一 author. severity 跟 vertical finding 不混 — 可单
  列 "framework-level cleanup" 或 "process gap codify" 类 follow-up.

**Failure mode (无声违反时长什么样)**: review report 把 cross-phase pattern observation 当
single-phase BLOCKING finding, attribution 错位 (framework gap 误判 author failure), severity
inflation (rollout pending 升级 alignment chain failure). Detection: report 含 "alignment
chain" / "整链" / "全链" 等跨 phase scope 措辞但 severity 标 BLOCKING / 归责到单 phase
author, 即触发 §3.9 violation.

#### 3.10 Working tree dirty state 必查

reproduce gates (Phase 1) 之前, 跑 `git status --short`, untracked files (`??`) + modified
tracked files (`M`) 单独 itemize. 跑 `tradectl test-thesis-agent` / `pytest` / `timeaudit`
之前, 如果 working tree non-clean, 在 reproduction table 上方先 narrate dirty state.

fail rate 跟 dirty state 关联性显式判断 — 是 working tree 影响 (untracked v1-shape fixtures
让 04 个 fixture fail, 但 commit 本身 clean) 还是 commit 引入 (HEAD 真有 schema bug, 跟
working tree 无关). 不要 silently 把 dirty-state 引起的 fail 算 commit failure.

具体步骤:

1. `git status --short | head -30` 在 reproduce gates 之前跑
2. 输出分两段: `M` (modified tracked) + `??` (untracked) 各 list
3. 如有 working-tree mods, 在 reproduction table 上方加一行 narrate "working tree dirty:
   N modified + M untracked, dirty-state fail attribution 待逐 case 判断"
4. 跑每个 gate 后, 如有 fail, grep 对应 file path 看是否在 dirty-state list 中. 是: 标
   "dirty-state induced (working tree, 不算 commit failure)"; 否: 标 "commit-induced
   (HEAD bug)"

**Failure mode (无声违反时长什么样)**: review report 报 "claim 48/48 PASS, 我跑 44 PASS / 4
FAIL" 但 4 FAIL 是 untracked v1-shape fixtures 引起, 跟 commit 完全无关. 让 colleague
commit 背 dirty-state 的锅. Detection: review report 报告 fail 但 dirty-state 在 review
开头没 itemize, 即触发 §3.10 violation.

## Severity Taxonomy

Use these four levels exactly. Don't invent intermediates.

- **BLOCKING**: violates charter rule, breaks the next phase's entry invariants, or
  contains a dangling reference that cannot be resolved without changing the schema /
  store. Must be fixed before next phase commits.
- **MEDIUM**: charter §IV fail-loud承诺 unmet at runtime, semantic borderline that will
  cause downstream confusion, or schema design flaw that future commits will inherit.
  Should be fixed in this phase or explicitly deferred with a recorded rationale.
- **LOW**: future foot-gun, hygiene drift, or doc cross-reference out of sync. Can ride
  along with the next phase commit.
- **NIT**: commit-message phrasing, missing dual-mirror mention, or code style. Not worth
  a separate fix commit; surface for awareness only.

Tag every finding with severity in brackets: `### F5 [MEDIUM] <title>`.

## Output Shape

Emit, in this order:

### 1. 校验门 reproduction table
Markdown table with columns: 校验门 (claim) / 我复跑 / 一致 (✓/✗). One row per claim.

### 2. Prior-finding follow-up (when reviewing a fix-up commit)
If the commit's message says it addresses prior findings (e.g. "addresses F1 from
commit X"), emit a small table mapping each prior finding → fix path → completion check.

Beyond finding-level fixes, also check whether **prior-review process patterns** have been
internalized into the current commit message. Process patterns from earlier reviews
include:

- Cross-phase delta narration (§3.7): does message proactively narrate "X → Y (+N)" with
  delta destination?
- Aggregate-count denominator transparency (§3.8): does message phrase claims as "X of
  TOTAL" rather than "X/X"?
- Commit scope itemization (§3.5): does message itemize cross-phase boundaries (e.g.
  "NO skill changes in this commit; D.2 onward extends")?
- Mirror dual-mirror narration (§3.3): does message mention ".claude / .cursor mirror,
  content identical" when both are touched?

When a colleague applies a process pattern from a prior review without being asked, call
it out as **engineering quality加分** in §4. Not internalizing a previously-flagged process
pattern (e.g. still writing "stable at N" in the next phase after §3.7 was raised) is a
follow-up failure worth flagging in §3.

### 3. New findings, severity-ordered
For each finding:

```
### F<N> [SEVERITY] <one-line title>

[location reference, e.g. file:line markdown link]

<2–4 sentences: what it is, why it matters per charter / contract, evidence>

**Two paths** / **建议**: <fix options or single recommendation>
```

Use markdown link syntax `[file.json:42](path/file.json#L42)` per IDE convention.

### 4. Engineering quality note (optional, ~3 sentences)
When the work shows notably good or notably poor engineering pattern (sidecar validator
pattern, additive enforcement layer, mirror drift, partial registry sync), name it
explicitly. Save for findings worth carrying forward to other phases.

### 5. Prioritized punch list
Numbered, with effort estimate and blocking / non-blocking flag.

Effort estimate is a coarse bucket (minutes / hours / days). Don't aim for precision; the
goal is to communicate "trivial fix vs new mini-phase" not to commit to a deadline.

```
1. **F<N> 先修**（5 分钟改）：<concrete change>
2. **F<N> 顺手修**（~30 行代码，独立 commit）：<concrete change>
3. **F<N> 在 Phase B 设计时显式纳入**：<integration note>
4. F<N> / F<N> 不 blocking，未来 commit hygiene
```

Close with one short paragraph: overall verdict, whether to proceed to the next phase as
planned, and one explicit ask-back if a finding requires user judgment (e.g. "要不要我现在
就把 F6 改了？").

## Boundaries

Each禁止式 is paired with a "无声违反时长什么样" detection signal so the agent can
self-check.

| 禁止式 | 检测式（无声违反时长什么样） |
|---|---|
| Does not edit the code under review | Review reply contains an `Edit` or `Write` tool call against a file in the commit's diff. If the user asks "fix it now" mid-review, the skill emits the review and stops; the fix is a separate action. |
| Does not invent校验门 | Reproduction table contains a row for a gate the colleague's commit message did not name. If a colleague-claimed gate is absent, note "not claimed" rather than inventing one. |
| Does not replace the colleague's self-review | Review reply relays a finding from the commit message verbatim without independent verification. Every claim must be cross-checked against the diff or校验门 output. |
| Does not rewrite commit messages, amend commits, or push | Review reply contains a `git commit --amend` / `git push` / `gh pr edit` call. All findings return to the user as text; the user decides whether to amend or land follow-up commits. |

## Rules-Of-Thumb (from real review history)

- A校验门 the colleague reports as passing has a non-trivial probability of passing only
  under their filter / scope assumptions. Always rerun on the **same scope and the global
  scope**, then reconcile.
- Commit messages systematically undersell `.gitignore` churn and previously-untracked
  files entering git. Read `git diff <ref>~1 <ref> -- .gitignore` every time.
- Schema enums that look like "system slugs" (lowercase snake_case nouns) are an F1 trap
  factory. Always cross-check enum membership against actual store presence.
- Doc-only enforcement (SKILL.md "MUST X") is a charter §IV fail-loud承诺 deferred. Note
  whether the deferral has a named landing phase, and verify when that phase lands.
- Mirror dirs (`.claude/` / `.cursor/`, `09_claude/` / `09_soul/`) drift silently. Diff
  every time the commit touches one mirror; never trust "mirror updated" claims without
  a diff.
- Phase-tagged commits ("Phase A.1") attract scope bleed because the colleague is in flow.
  Itemize every concern and flag the unmentioned ones.
