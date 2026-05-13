---
title: Entity Expert (Abstract)
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Domain Expert Maintainer
---

# Entity Expert

## 1. Purpose

`Entity Expert` 是 Digestion 层 4x 系列的抽象父类。它定义什么是实体专家、它和 Transmission Expert (5x) 的区别、以及所有 Entity Expert 共享的结构契约。

本文不拥有具体 domain logic。具体 domain 由子 expert 拥有（如 41 Company、42 Crypto Project、未来的 Commodities / Precious Metals）。

## 2. 定义

Entity Expert 的核心问题：

```text
这个实体（公司、项目、标的）的 quality / value / risk 怎么样？
```

对比 Transmission Expert (5x) 的核心问题：

```text
一个 signal 如何从 A 传导到 B 再到 C，传导过程中 signal 如何变形、衰减、放大或被阻断？
```

## 3. 与 Transmission Expert 的区别

| 维度 | Entity Expert (4x) | Transmission Expert (5x) |
|---|---|---|
| 分析对象 | 单一实体（公司、crypto project、commodity） | 传导链 / 行业 / 宏观机制 |
| Source 消费方式 | 围绕一个 asset_key 收集 | 跨多个 entity 读取，按 channel 路由 |
| Primary artifact | Dossier（单实体 structured read） | State Map + Transmission Chain + Impact Pool |
| Claim routing | 按 source_class → claim_type | 按 channel → transmission_step |
| Downstream 消费 | 直接进入 single-stock / thesis | 进入 theme / thesis，或作为 overlay 被 Entity Expert 消费 |
| Ticker 关系 | 1:1（一个 expert run 对应一个 asset_key） | 1:N（一条 transmission chain 影响多个 tickers） |

## 4. Source Cross-Consumption Principle

**一条 source 可以被两类 expert 同时消费。**

同一份报告、同一条消息、同一个数据点可以同时被 Entity Expert 和 Transmission Expert 消费，各自生成独立的 Source Card 和 Typed Claims。

例：

```text
Source: "MSFT Azure capex guidance $80B"

Entity Expert (MSFT):
  → Source Card: company_primary_disclosure
  → Typed Claim: capex_commitment (entity-level growth driver evidence)

Transmission Expert (AI Industry, step 1):
  → Source Card: company_primary_disclosure
  → Typed Claim: ai_capex_cycle (transmission step 1 confirmation)
```

规则：

- 两类 expert 独立持有各自的 Source Card instance；
- Claim type 由各自的 firewall 决定，不混用；
- 一类 expert 的 confidence 不自动传递给另一类；
- 两条消费路径可以互相引用结论（通过 `digestion_edges`），但不共享 authority。

## 5. Shared Structure Contract

所有 Entity Expert 必须定义：

### 5.1 Asset Identity

每个 Entity Expert run 绑定一个 `asset_key`。Asset identity 由 Independent Researcher 在路由前确定。

### 5.2 Source-Class Taxonomy

定义接受哪些 source classes，每个 source class 的 authority 和 confidence cap。

### 5.3 Typed-Claim Firewall

定义 `source_class × claim_type` 的 allowed / blocked pairs。

### 5.4 Dossier Schema

定义 entity-level primary artifact 的 section 结构、required fields、confidence-cap rules。

### 5.5 Permission Levels

每条 typed claim 必须区分：

```text
publicly_observable
  The source directly reports the fact.

proxy_inferable
  The source does not directly report the fact, but a bounded proxy supports a directional read.

not_knowable_from_current_sources
  The question matters, but the available source packet cannot answer it.
```

子 expert 可以增加更严格的 confidence caps，但不可削弱这三级。

### 5.6 Portfolio Boundary

Entity Expert 不 emit buy / sell / hold、target weights、hedge actions、execution instructions。这些属于 PM-facing analyst 和 portfolio workflows。

## 6. Sub-Expert 结构

Entity Expert 可以有 sub-expert 或 template variants（因为不同实体类型的 source surface 和 claim firewall 差异大）。

标准结构：

```text
4X  Entity Expert Family (umbrella / routing)
  4X_1  Sub-Expert A (owns specific entity type)
  4X_2  Sub-Expert B (owns another entity type)
  ...
```

Umbrella owns：
- routing contract（asset_type → sub-expert）
- shared evidence rules（permission levels、claim provenance、portfolio boundary）
- admission criteria for new sub-experts
- cross-reference hygiene

Sub-Expert owns：
- source-class taxonomy 和 firewall
- dossier schema
- source-specific confidence caps
- route template defaults
- validation gates

## 7. Shared Evidence Rules

所有 Entity Expert 共享：

### 7.1 Claim Provenance

每条 operational claim 必须标注：

- `source_ref`
- source class
- source authority
- source span / quote where available
- time semantics
- confidence cap where source cannot prove the full claim

### 7.2 Market And Business Separation

Market price、public comparables、private marks、secondary indications、valuation multiples 描述 pricing surfaces and expectations。它们不单独证明 operating quality。

Operating facts、product claims、customer signals、regulatory risk、guidance 需要各自的 source support。

### 7.3 Cannot-Know Boundaries

当 source packet 无法回答某个分析维度时，必须显式标注为 `not_knowable`，而非用 AI prose 填补。

## 8. Admission Criteria

创建新 Entity Expert (4X) 当且仅当：

- 分析对象是单一 identifiable entity（不是传导链或宏观机制）；
- 现有 Entity Expert 的 source surface 和 claim firewall 无法表达这类实体；
- 新 expert 需要 materially 不同的 source classes 或 claim-type firewalls；
- 输出 artifact schema 与现有 expert 有结构性差异；
- 错误 routing 会产生 "用错误 source surface 读实体" 的风险。

**不创建** 如果：

- 只是一个重要的 entity（→ 用现有 expert 多跑一次）；
- 差异只在 section naming（→ 用 template variant）；
- 本质是传导链 / 行业分析（→ 用 5x Transmission Expert）；
- source volume 低且 voice authority 与现有 expert 一致。

## 9. Current Entity Experts

| ID | Domain | Status | Entry doc |
|---|---|---|---|
| 41 | Company (umbrella) | active_draft | `digestion_41_company_expert.md` |
| 41_1 | Private Company | active_draft | `digestion_41_1_private_company_expert.md` |
| 41_2 | Listed Company | active_draft | `digestion_41_2_listed_company_expert.md` |
| 42 | Crypto Project | active_draft | `digestion_42_crypto_project_expert.md` |

Future candidates（需经 Expert Factory admission）：

- Commodities / Futures
- Precious Metals

## 10. Relationship To Transmission Expert

Entity Expert 和 Transmission Expert 通过 `digestion_edges` 关联：

### 10.1 Transmission → Entity

当 Transmission Expert 产出影响特定 entity 的 signal，handoff 到对应 Entity Expert 做 entity-level 消化：

```text
Transmission Expert (AI Industry): "AI capex acceleration confirmed (step 1)"
  -> Entity Expert (NVDA): "incorporate as catalyst evidence in company dossier"
```

Edge type: `transmission_informs_entity`

### 10.2 Entity → Transmission

Entity Expert 的 entity-level 发现可以成为 Transmission Expert 的 step evidence：

```text
Entity Expert (MSFT): "Azure capex guidance $80B confirmed"
  -> Transmission Expert (AI Industry): "incorporate as step 1 capex_commitment claim"
```

Edge type: `contributes_to_transmission`

### 10.3 Independence

尽管两类 expert 可以互相引用，各自的 confidence 和 claim 独立。Entity Expert 的 confirmed claim 不自动 confirm Transmission Expert 的 step（反之亦然）。

## 11. Adjacent Docs

| Doc | Relationship |
|---|---|
| `digestion_00_overview.md` | Layer overview and section 8A Expert Taxonomy |
| `digestion_30_expert_factory.md` | Expert lifecycle and admission |
| `digestion_50_transmission_expert.md` | Transmission Expert abstract（对称参考） |
| `digestion_41_company_expert.md` | First Entity Expert family |
| `digestion_42_crypto_project_expert.md` | Crypto entity expert |
| `digestion_10_structure_contract.md` | Object schema for Source Card, Typed Claim |
