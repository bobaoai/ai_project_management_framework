---
title: Transmission Expert (Abstract)
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Domain Expert Maintainer
---

# Transmission Expert

## 1. Purpose

`Transmission Expert` 是 Digestion 层 5x 系列的抽象父类。它定义什么是传导链专家、它和 Entity Expert (4x) 的区别、以及所有 Transmission Expert 共享的结构契约。

本文不拥有具体 domain logic。具体 domain 由子 expert 拥有（如 51 AI Industry、52 Fed Rate）。

## 2. 定义

Transmission Expert 的核心问题：

```text
一个 signal 如何从 A 传导到 B 再到 C，传导过程中 signal 如何变形、衰减、放大或被阻断？
```

对比 Entity Expert (4x) 的核心问题：

```text
这个实体（公司、项目）的 quality / value / risk 怎么样？
```

## 3. 与 Entity Expert 的区别

| 维度 | Entity Expert (4x) | Transmission Expert (5x) |
|---|---|---|
| 分析对象 | 单一实体（公司、crypto project） | 传导链 / 行业 / 宏观机制 |
| Source 消费方式 | 围绕一个 asset_key 收集 | 跨多个 entity 读取，按 channel 路由 |
| Primary artifact | Dossier（单实体 structured read） | State Map + Transmission Chain + Impact Pool |
| Claim routing | 按 source_class → claim_type | 按 channel → transmission_step |
| Downstream 消费 | 直接进入 single-stock / thesis | 进入 theme / thesis，或作为 overlay 被 Entity Expert 消费 |
| Ticker 关系 | 1:1（一个 expert run 对应一个 ticker） | 1:N（一条 transmission chain 影响多个 tickers） |

**同一条 source 可以被两类 expert 同时消费。** Entity Expert 问 "这条信息对 NVDA 意味着什么"；Transmission Expert 问 "这条信息对 AI capex → delivery chain 意味着什么"。各自生成独立 Source Card 和 Typed Claims，互不干扰。

## 4. Shared Structure Contract

所有 Transmission Expert 必须定义：

### 4.1 Transmission Chain

一条有序的传导路径，从 trigger/input → intermediate steps → terminal outcome。每步标注：

- `step_id`
- `step_name`
- `owner_child_expert`（如果 umbrella 下有多个 child expert）
- `native_horizon`
- `observables[]`
- `typical_misuse`
- `falsifiers[]`

### 4.2 Channel Registry

每个 Transmission Expert 内部按 channel 路由 claims。Channel 定义：

- `channel_id`
- `transmission_step` — 对应 chain 的哪一步
- `native_horizon`
- `observables[]`
- `typical_misuse`
- `falsifiers[]`

### 4.3 State Map (Required Artifact)

每个 Transmission Expert 必须能产出一个 State Map：当前 transmission chain 各步的状态判断、evidence tier、key uncertainties。

### 4.4 Impact Pool (Required Artifact)

按 transmission step 分组的 affected tickers / assets。

### 4.5 Evidence Tier Per Step

Transmission chain 的每步必须标注当前 evidence tier：

```text
confirmed  — primary-source-backed fact
signaled   — proxy-inferable from multiple sources
assumed    — single-source or inference, needs confirmation
unknown    — no evidence available
```

不允许用一步的 confirmed evidence 推导另一步的 certainty（每步独立 evidence）。

## 5. Sub-Expert 结构

Transmission Expert 通常需要 sub-experts（因为 transmission chain 不同段的 source surface 和 claim firewall 不同）。

标准结构：

```text
5X  Transmission Expert Family (umbrella / orchestrator)
  5X1  Sub-Expert A (owns steps 1-K)
  5X2  Sub-Expert B (owns steps K+1-N)
  ...
```

Umbrella owns：
- routing contract（source → sub-expert）
- transmission chain definition（完整路径）
- family-level artifact assembly（State Map、Impact Pool）
- shared evidence rules
- sub-expert admission

Sub-Expert owns：
- source-class taxonomy 和 firewall
- channel registry（自己覆盖的 steps）
- domain-specific artifacts
- validation gates

## 6. Shared Evidence Rules

所有 Transmission Expert 共享：

### 6.1 One Claim, One Step

一条 typed claim 只能证明 transmission chain 的一步。不允许一条 claim 跨越多步（"A is happening therefore Z will happen"）。跨步推论属于 scenario prediction，不属于 typed claim。

### 6.2 Narrative Heat ≠ Transmission Proof

Newsletter enthusiasm、market momentum、CEO statements 是 signals，不是 transmission proof。只有 primary-source-backed evidence（filings、official data、operator disclosure）可以 confirm 一步。

### 6.3 Per-Step Independence

每步的 evidence 独立。上游步骤 confirmed ≠ 下游步骤 confirmed。

```text
❌ "capex is growing therefore adoption will follow"
✓ "capex is growing (step 1: confirmed)" + "adoption evidence is X (step 8: signaled)"
```

### 6.4 Permission Levels

```text
publicly_observable — primary source directly reports
proxy_inferable    — bounded proxy supports directional read
not_knowable       — cannot answer from current source packet
```

### 6.5 Portfolio Boundary

Transmission Expert 不 emit portfolio action、position sizing、thesis activation、theme priority update。

## 7. Admission Criteria

创建新 Transmission Expert (5X) 当且仅当：

- 分析对象是 multi-step transmission chain（不是单一实体）；
- source voice authority 在不同 steps 之间差异大；
- claims 需要按 transmission step 路由（不是按 entity 路由）；
- 错误 routing 会产生 "把 step 1 证据当 step N 证明" 的风险；
- 反复影响 PM judgment；
- 现有 Entity Expert 无法表达传导逻辑。

**不创建** 如果：
- 本质是单实体分析（→ 用 4x Entity Expert）；
- 只有 1-2 步的简单因果（→ 用 thesis note）；
- source volume 低且 voice authority 均匀（→ 不需要 expert）。

## 8. Current Transmission Experts

| ID | Domain | Status | Entry doc |
|---|---|---|---|
| 51 | AI Industry | active_draft | `digestion_51_ai_industry_expert.md` |
| 52 | Fed Rate / Monetary Transmission | external (macro_fed_kb) | `video_parser/macro_fed_kb/design/` |

## 9. Relationship To Entity Expert

当 Transmission Expert 产出影响特定 ticker 的 signal，handoff 到对应 Entity Expert 做 entity-level 消化：

```text
Transmission Expert: "AI capex acceleration confirmed (step 1)"
  -> Entity Expert (NVDA): "incorporate as catalyst evidence in company dossier"
```

反向也存在：Entity Expert 的 company-level 发现可以成为 Transmission Expert 的 step evidence：

```text
Entity Expert (MSFT): "Azure capex guidance $80B confirmed"
  -> Transmission Expert (AI Industry): "incorporate as step 1 capex_commitment claim"
```

两者通过 `digestion_edges` typed edge (`contributes_to_transmission` / `transmission_informs_entity`) 关联。

## 10. Adjacent Docs

| Doc | Relationship |
|---|---|
| `digestion_00_overview.md` | Layer overview and §8A Expert Taxonomy |
| `digestion_30_expert_factory.md` | Expert lifecycle and admission |
| `digestion_40_entity_expert.md` | Entity Expert abstract（对称参考） |
| `digestion_41_company_expert.md` | First Entity Expert family |
| `digestion_51_ai_industry_expert.md` | First Transmission Expert implementation |
| `digestion_10_structure_contract.md` | Object schema for Source Card, Typed Claim |
