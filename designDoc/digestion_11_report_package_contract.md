---
title: Digestion Report Package Contract
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - PM Report Writer
  - Package Reviewer
---

# Digestion Report Package Contract

## 1. 这份 contract 解决什么

本文定义 Digestion 层如何把 expert artifacts 转成 writer-ready report package。

`digestion_10_structure_contract.md` 定义长期存在的 digestion objects：Source Card、Typed Claim、Framework Card、Expert Artifact、Promotion Link。本文定义这些对象进入 Research 写作层之前的 handoff package 形状：

```text
Expert Artifact
  + Source Cards
  + Typed Claims
  + Source Packet / Route Metadata
  -> digestion_report_package
  -> Research PM-facing report instruction
```

Package 不是最终 report。它是 Digestion 和 Research 之间的受控接口。它必须保留 evidence boundary、reader end-state、claim eligibility、blocked assumptions、writer instruction，让 writer 不需要回到 raw source 重新发明 domain read。

## 2. 契约族 / Contract family

本文只定义通用 `digestion_report_package` contract。Domain-specific package contract 作为相邻文件单独存在，并显式继承本文。

当前 child contract：

- `digestion_12_private_company_report_package_contract.md` 定义 `private_company_report_package`。

未来 child contract 可以包括 listed-company、crypto-project、macro-framework、technical-summary 等 report package。

## 3. 通用 reader / writer end-state

一份合格的 Digestion report package，应该让下游 writer 在动笔前回答：

- PM 读完 report 后应该理解什么。
- 哪个 expert artifact 是 subject source，哪些 artifacts 只是 calibration 或 context。
- 哪些 claims 可以进入 main article，以及它们为什么对 PM 判断有用。
- 哪类 evidence 最强、最新，哪类只是 background。
- 哪些 assumptions 被 blocked，或无法从 public / local data 支持。
- 哪个后续 evidence 会改变判断。
- 哪些 outputs 被允许，哪些 outputs 被禁止。

如果 writer 只能按 expert artifact 的章节顺序复述，package 就失败了。

## 4. 通用 package object

最低 frontmatter：

```yaml
content_type: digestion_report_package
schema_version: digestion_report_package_v0
package_id:
subject_ref:
subject_expert_id:
source_packet:
expert_artifacts: []
included_source_card_ids: []
included_claim_ids: []
generated_at_utc:
status: ready_to_write | blocked
allowed_outputs: []
blocked_outputs: []
```

`subject_ref` 是 package subject 的稳定 ID。child contract 负责定义它的具体形状：asset key、theme id、framework id、subsystem id，或其他 domain-native identifier。

`allowed_outputs` 是 closed-list allow surface。`blocked_outputs` 是 explicit deny override。同一个 output 同时出现在两边时，deny wins。

`expert_artifacts[]` 可以包含多个 expert artifact。必须且只能有一个 entry 使用 `role: subject`；其他 entry 可以使用 `calibration_comp`、`context`、`technical_overlay` 等角色。

通用 body 顺序：

1. `Reader End-State`
2. `Anchor Read`
3. `Evidence Weighting`
4. `Claims For Main Article`
5. `Boundary / Blocked Assumptions`
6. `Watchpoints That Change The Read`
7. `Report Instruction`
8. `Manifest Pointer`

Package body 只放 writer-useful content。Assembly manifest、run metadata、hashes、source inventories 属于 sidecar，除非某个字段会直接帮助 writer 避免 overclaim。

## 5. 通用 hard rules / 硬规则

### R1. 读者终态优先 / Reader End-State First

Frontmatter 后第一个 judgment-bearing body section 必须说明 report 的 reader end-state。若 child contract 支持 per-asset owner direction，owner direction 可以作为 non-judgment-bearing preface 出现在 `Reader End-State` 前面；除此之外不能有其他 section 抢在 reader end-state 之前。

### R2. 上游 expert artifact 是输入，不是结构 / Expert Artifact Is Input, Not Structure

Package 不能照搬 expert artifact 的章节顺序，除非那个顺序同时也是 PM 的 judgment path。Package 按 writer need 组织，而不是按上游存储形状组织。

`Anchor Read` 是 writer 必须围绕、或必须明确说明为何偏离的 structural read。它不是 PM belief，不是 portfolio action，也不是 final headline judgment。

### R3. 证据 eligibility 必须传递 / Evidence Eligibility Must Survive

每条可进入 main article 的 claim 必须保留：

```yaml
claim:
source_card_id:
claim_id:
expert_id:
source_class:
claim_type:
allowed_use:
package_use_override:
time_validity:
downstream_blocked_use: []
why_it_matters_for_pm:
must_not_say:
```

`allowed_use` 复用 `digestion_10_structure_contract.md` §3.2 的 closed enum：`evidence | background | trigger | candidate_only | blocked`。`package_use_override` 是 optional，只能收窄 upstream `allowed_use`，不能扩大。

### R4. 被阻断的假设是 writer 输入 / Blocked Assumptions Are Writer Inputs

Cannot-know fields、missing optional inputs、stale evidence、blocked assumptions 必须进入 package body。它们不是只放在 audit metadata 里的东西。

### R5. 写作指令是投影 / Writer Instruction Is A Projection

Package 可以携带 per-asset 或 per-topic specialization，但当 Research-layer prose contract 已存在时，必须引用它。Package 不能重新定义 Research 拥有的 final report prose rules。

### R6. 禁止 raw archive dump / No Raw Archive Dump

Package 可以引用 source archive path 供 quote verification，但不能粘贴完整 raw message body、完整 PDF、raw image bytes 或 base64。应使用 Source Cards、Typed Claims、selected excerpts、reviewed visual evidence。

### R7. 大小与 plumbing 纪律 / Size And Plumbing Discipline

Package 应足够 compact，能进入 external writer surfaces。除非 child contract 设更严格限制，否则继承 `research_00_writer_package_contract.md` 的 500 KB hard ceiling。Plumbing 放 sidecar。

### R8. 组合动作不是 Digestion 输出 / Portfolio Action Is Not A Digestion Output

`allowed_outputs[]` 不能包含 buy / sell / short / cover / hold-as-recommendation、position sizing、hedge construction、transaction-instruction outputs。这些属于 Research 下游的 portfolio-decision workflow，只有明确拥有该步骤的 workflow 才能产生。

Child contract 可以添加 domain-specific blocked outputs，但不能放松这个默认限制。

## 5.5 通用 detection-side examples

以下都是可观察的 contract violation：

- R1：frontmatter 后第一个 judgment-bearing body section 不是 `Reader End-State`。
- R2：package body sections 与某个 `expert_artifact` body 一一对应。
- R3：`Claims For Main Article` 下的 claim 缺 `claim_id`、`source_card_id` 或 `allowed_use`。
- R4：cannot-know 或 blocked-assumption 只出现在 manifest sidecar，不出现在 package body。
- R5：`Report Instruction` 直接定义 final report 的章节顺序、reader path 或 prose 风格，但没有引用 Research 层 prose contract。
- R6：package body 包含完整 raw message body、完整 PDF、raw image bytes 或 base64 payload。
- R7：package body 超过 500 KB，或 run metadata / hashes / assembly plumbing 出现在 body 内。
- R8：`allowed_outputs[]` 包含 portfolio-action、sizing、hedge-construction 或 transaction-instruction output。

## 6. 与 `research_00_writer_package_contract.md` 的关系

本文继承 `research_00_writer_package_contract.md` 的 repo-wide writer-package principles，但针对 Digestion-origin packages 做替换。

原样继承：

- 禁止 raw image bytes 或 base64；
- 禁止 full-file dump；
- manifest 与 assembly plumbing 必须放在 sidecar；
- ID 与 repo-relative path 保持稳定；
- multimodal evidence 用引用方式调用；
- package body 保持 compact，超出体积上限即 fail-fast。

带替换继承：

- theme `Owner direction first` 在非 theme-owned package 中替换为 `Reader End-State first`。
- 当 domain experts 已经生成 Source Cards / Typed Claims 时，`content_selection.json-driven excerpts` 替换为 `expert-artifact-driven evidence`。
- `Do Not Promote` 替换为 domain-specific `Boundary / Blocked Assumptions` section。

不自动继承：

- theme `owner.json` 要求；
- same-theme standing-backbone rules；
- selected thesis-note tiering。

## 7. 子契约准入 / Child contract admission

当一个 domain 满足以下条件时，可以单独新增 `digestion_1x_*_report_package_contract.md`：

- domain 的 evidence hierarchy 无法只靠通用字段表达；
- domain 需要额外 blocked-output 或 cannot-know rules；
- domain 需要专门的 writer handoff template；
- domain 已有稳定的 expert artifact、Source Card、Typed Claim shapes。

Child contract 必须说明继承了哪些 common rules，以及新增了哪些 domain-specific fields。Child contract 不应该嵌入本文。

## 8. 相邻文档关系

Read before:

- `digestion_10_structure_contract.md` 拥有 Source Card、Typed Claim、Expert Artifact、Promotion Link 与共享对象图。
- `research_00_writer_package_contract.md` 拥有 repo 级 writer-package 体积、证据与 fail-fast 原则。

Read after:

- domain-specific package contracts，例如 `digestion_12_private_company_report_package_contract.md`。

Consumed by:

- domain-specific report package builders；
- `writer-handoff`-style pre-writing gates；
- PM-facing report writers and reviewers。
