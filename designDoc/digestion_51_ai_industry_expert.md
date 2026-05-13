---
title: AI Industry Expert Family
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - Independent Research Orchestrator
  - PM
---

# AI Industry Expert Family

## 1. Purpose

`AI Industry Expert` 是 Digestion 层的行业级专家 family。它不直接做 source digestion，而是：

- 判断 source 属于 AI 行业的哪个 sub-domain；
- route 到正确的 child expert；
- 定义跨 sub-expert 的 transmission chain（完整 AI value chain）；
- 组装行业级 artifacts（State Map、Transmission Chain、Stock Pool Impact），这些 artifacts 从 child expert 产出中 synthesize。

Family 存在的原因："AI industry" 不是一个 sufficient evidence model。AI 基础设施（capex → semis → power）和 AI 应用（adoption → monetization → enterprise demand）的 source surface、evidence permission、claim firewall 和 transmission logic 完全不同。用同一套 firewall 处理 Citrini 的 foundry capacity 分析和 TMT Breakout 的 application breakout 信号，会丢失 source authority 的精度。

## 2. Reader End-State

读完本文后，system builder 应该能判断：

- AI industry 类 source 何时应进入本 family 而非 listed company expert；
- routing 到哪个 child expert；
- AI Industry State Map / Transmission Chain / Stock Pool Impact 如何从 child expert outputs 组装；
- 什么时候需要新增 child expert；
- 本 family 不做什么（不做 company dossier，不做 thesis，不做 portfolio action）。

本文是 umbrella。执行层面的 source card pattern、claim firewall、domain artifacts 定义在 child expert docs。

## 3. Child Experts

| Sub-domain | Canonical doc | Primary focus | Primary sources |
|---|---|---|---|
| AI Semiconductor | [`digestion_51_1_ai_semiconductor_expert.md`](digestion_51_1_ai_semiconductor_expert.md) | chip supply chain、foundry/packaging、memory cycle (HBM/DRAM)、chip architecture、equipment/EDA | Citrini (semis)、SemiAnalysis、NVDA/TSM/MU filings、foundry data |
| AI Data Center | [`digestion_51_2_ai_datacenter_expert.md`](digestion_51_2_ai_datacenter_expert.md) | power/utility、optical/networking、DC construction/cooling | Citrini (power/optical)、utility filings、DC REIT earnings、BofA optical |
| AI Application (Platform) | [`digestion_51_3_ai_application_expert.md`](digestion_51_3_ai_application_expert.md) | enterprise adoption、monetization、model → commercial value、demand quality | TMT Breakout (application)、SaaS earnings、usage metrics、enterprise surveys |
Future child experts 候选（但当前不创建）：

- `AI Model / Frontier Research Expert` — 当模型能力分析所需的 source surface 和 claim firewall 与 semis/datacenter/application 都不匹配时
- `AI Regulation / Policy Expert` — 当 policy source（立法、executive order、export control）的 voice authority 和 time semantics 需要独立处理时

## 4. Routing Contract

AI Industry Expert 位于 Independent Research Orchestrator 下游。

```text
Independent Research Orchestrator
  -> source_packet (AI 行业 sources)
  -> domain_route: ai_industry_expert
  -> family router
  -> child expert (infrastructure | application)
  -> AIIndustrySourceCard + AIIndustryTypedClaim
  -> child expert artifacts
  -> family-level assembly: State Map / Transmission Chain / Stock Pool Impact
  -> downstream: theme / thesis / single-stock overlay / portfolio
```

### 4.1 Routing Signals

Family router 从 source packet metadata 和 content signals 判断 child expert：

| Signal | Route to |
|---|---|
| chip、foundry、packaging、CoWoS、HBM、DRAM、memory、ASIC、GPU architecture、equipment、EDA、wafer、semiconductor | `ai_semiconductor_expert` |
| power、utility、MW、interconnection、optical、transceiver、networking、cooling、DC construction、data center buildout | `ai_datacenter_expert` |
| adoption、usage、ARR、seats、enterprise、SaaS、API calls、monetization、pricing、churn、demand quality、copilot | `ai_application_expert` |
| drug discovery、clinical trial、CRO、autonomous、ADAS、OEM integration、lab automation、QC | **不属于 51**；route 到行业专属 expert（如 `healthcare_expert`） |
| capex、spending、budget (hyperscaler capex guidance) | umbrella Step 1 → split downstream to semiconductor + datacenter |
| 同一 source 包含多类信号 | split claims，route 到各自 child expert |

### 4.2 Route Format

```yaml
ai_semiconductor:
  asset_type: ai_industry
  selected_route: ai_industry_expert
  sub_route: ai_semiconductor_expert

ai_datacenter:
  asset_type: ai_industry
  selected_route: ai_industry_expert
  sub_route: ai_datacenter_expert

ai_application:
  asset_type: ai_industry
  selected_route: ai_industry_expert
  sub_route: ai_application_expert

```

### 4.3 一篇 Source 跨 Sub-Expert

常见情况：Citrini 或 TMT Breakout 一篇文章既讲 infra 又讲 adoption。

处理方式：source card 归属于 primary channel 对应的 child expert 生成；但 claim 按 channel routing 分别归入正确的 child expert。一条 claim 只归属一个 child expert。

## 5. Shared Evidence Rules

> **Canonical Taxonomy**: Claim Type Taxonomy（umbrella + industry subtypes）和 Source Class Authority
> 的完整定义已迁移到 [`digestion_35_claim_taxonomy_and_source_authority.md`](digestion_35_claim_taxonomy_and_source_authority.md)。
> Machine-readable 版本：`data/runtime/schemas/claim_type_taxonomy.yaml`。
> 各 child expert 的 subtype 和 firewall supplements 定义在各自的
> `data/digestion/expert_subsystems/<expert_id>/expert_contract.yaml` 中。
>
> 本节保留 family-level 的 shared rules，不再内联定义 source_class 或 claim_type。

所有 AI Industry child experts 必须遵守：

### 5.1 Permission Levels

Permission levels 定义见 taxonomy §5.2。核心三级：

- `publicly_observable` — source 直接报告的事实
- `proxy_inferable` — 有限 proxy 支持 directional read
- `not_knowable_from_public_data` — 问题 matters，但当前 public source 无法回答

Source class 与 permission level 的约束关系由 routing matrix 控制（taxonomy §6）。

### 5.2 Narrative Heat ≠ Demand Proof

最核心的 shared firewall：

```text
Newsletter conviction / practitioner enthusiasm / market momentum
  ≠ real demand evidence (disclosed revenue, usage metrics, confirmed orders)
```

任何 child expert 都不能把 practitioner inference 或 market price 标为 `publicly_observable` demand proof。

### 5.3 Transmission Step Discipline

每条 claim 必须标注它证明的是 transmission chain 的哪一步。不允许一条 claim 跨越多步（"AI capex is booming so AI SaaS will monetize"）。

### 5.4 Market And Business Separation

Market price / sector rotation / relative strength 是 positioning signal，不是 business quality proof 或 demand certainty。

### 5.5 Portfolio Boundary

AI Industry experts 不 emit buy/sell/hold、position sizing、thesis activation、theme priority update。

## 6. AI Transmission Chain（Family Owned）

Transmission Chain 是 family umbrella 的核心 artifact。它定义 AI value chain 从 capex decision 到 end-user monetization 的完整传导路径：

```text
1. Capex Decision (hyperscaler budget allocation)
   ↓
2. Chip Order (GPU/ASIC procurement)
   ↓
3. Foundry & Packaging (wafer starts, advanced packaging capacity)
   ↓
4. Power & Infrastructure (data center power, cooling, networking)
   ↓
5. Cloud Capacity Available (GPU-hours, inference slots)
   ↓
6. Model Training & Serving (frontier model capability, inference cost)
   ↓
7. Platform & API Pricing (inference pricing, API tiers)
   ↓
8. Enterprise Adoption (pilot → production → scaled usage)
   ↓
9. End-User Monetization (AI-attributed revenue, margin impact)
```

**Step 1**: owned by umbrella（capex decision triggers both semiconductor and datacenter）
**Steps 2–3**: owned by `ai_semiconductor_expert`
**Step 4**: owned by `ai_datacenter_expert`
**Steps 5–9**: owned by `ai_application_expert`
**Step 5**: overlap zone — datacenter expert 看 capacity delivery，application expert 看 cost-to-serve

> **Vertical industries**: AI 改造垂直行业（healthcare、auto 等）由各行业自己的 expert family 负责，不属于 51。
> 51 的 transmission chain 终止于 Step 9（end-user monetization of AI platform/enterprise products）。
> 当 AI 的影响进入特定行业价值链后，证据评估需要行业 domain knowledge，不再是 AI 行业分析。

每步标注：

- 当前 evidence tier（confirmed / signaled / assumed / unknown）
- limiting factor
- falsifier
- affected tickers

## 7. Family-Level Artifacts（从 Child Expert 输出组装）

### 7.1 AI Industry State Map

组装自两个 child expert 的 domain artifacts。回答 "AI 行业当前处于什么状态"。

Assembly rule：umbrella 从 child expert 的 typed claims 和 domain artifacts 中提取 channel-level state，不重新 digest raw sources。

Sections：

1. **Capex Cycle Position** ← from umbrella Step 1
2. **Semiconductor Supply State** ← from semiconductor expert
3. **Data Center Infrastructure State** ← from datacenter expert
4. **Adoption State** ← from application expert
5. **Monetization Evidence Tier** ← from application expert
6. **Competitive Landscape** ← from all three
7. **Cross-Chain Gaps** — transmission chain 中哪步缺 evidence
8. **Falsifier Watch** — 如果出现，需要 revision

### 7.2 AI Stock Pool Impact

按 transmission chain position 分组 affected tickers。从 child expert 的 `affected_tickers` 字段汇总。

- **Capex Senders** (step 1): MSFT, GOOG, AMZN, META
- **GPU/Logic** (step 2): NVDA, AMD, AVGO, MRVL, QCOM
- **Foundry/Packaging/Memory** (step 3): TSM, ASML, AMAT, MU, SK Hynix
- **Power/Utility** (step 4): VST, CEG, GEV, NRG
- **Optical/Networking** (step 4): GLW, ALAB, COHR, ANET, CIEN
- **DC Operator** (step 4): EQIX, DLR, VRT
- **Cloud/Platform** (step 5–7): MSFT, AMZN, GOOG
- **Application/SaaS** (step 8–9): CRM, SNOW, various

## 8. Child Expert Responsibilities

Child experts own：

- industry subtypes（定义在 `expert_contract.yaml`，归入 taxonomy umbrella）；
- subtype-level firewall supplements（超越 routing matrix 的 domain-specific 约束）；
- Source Card schema（AISemiSourceCard / AIDatacenterSourceCard / AIAppSourceCard）；
- domain-specific channel registry；
- domain-specific artifacts；
- validation gates。

Family umbrella owns：

- routing contract（source → child expert）；
- shared evidence permission semantics（引用 taxonomy routing matrix）；
- AI Transmission Chain definition（跨 child expert 的完整 value chain）；
- family-level artifact assembly（State Map、Stock Pool Impact）；
- admission criteria for new child experts；
- cross-child evidence hygiene（一条 claim 不跨步）。

## 9. Admission For New Child Experts

Create a new child expert only when：

- 目标仍然是 AI industry（不是 single company、不是 macro、不是 crypto）；
- 现有 infrastructure expert 和 application expert 的 source class 和 claim firewall 无法准确表达该 sub-domain；
- 新 expert 需要不同的 evidence permission 处理（如 regulatory source 的 authority 模型不同）；
- output artifact 改变下游判断，不只是 section naming；
- route 可以在 `domain_route` metadata 中表达。

不创建 new child expert ���果：

- 差异可以通过现有 expert 的 channel 扩展解决；
- 只是 source volume 大但 firewall logic 相同；
- 差异只影响 formatting 不影响 evidence routing。

## 10. Boundaries With Adjacent Workflows

### 10.1 Independent Researcher

Independent Research Orchestrator 负责 source collection、archive、source-packet assembly、route selection。AI Industry family 从 route 开始。

### 10.2 Listed Company Expert

AI Industry Expert 做行业级 cross-company synthesis。当 industry signal 需要影响特定 ticker 的 company-level judgment，handoff 到 `listed_company_expert` 做 company dossier。

```text
AI Industry Expert: "hyperscaler capex acceleration confirmed"
  -> Listed Company Expert (NVDA): "incorporate as catalyst evidence"
```

不重复工作：industry expert 不写 company dossier，company expert ���做 cross-company industry synthesis。

### 10.3 Fed Rate Expert

AI capex cycle 和 Fed Rate 有交叉（利率影响 capex decision、power cost 影响 infra economics）。两个 expert family 各自独立 digest，交叉 claim 通过 `digestion_edges` typed edge 关联，不在一个 expert 内部混合。

### 10.4 Theme / Thesis / Portfolio

AI Industry artifacts 可以作为 theme evidence 被 `research-theme-report-owner` 消费。但 industry expert 不激活 thesis lifecycle、不 emit portfolio action。

## 11. First Implementation Slice

1. 注册 `expert_id: ai_industry_expert` 和三个 child experts；
2. 从 Citrini semis archive 选 2 篇 → route 到 semiconductor expert；
3. 从 Citrini power/optical archive 选 2 篇 → route 到 datacenter expert；
4. 从 TMT Breakout archive 选 2 篇 → route 到 application expert；
5. 验证 routing：同一篇如果跨 sub-domain，claims 是否正确 split；
6. 生成第一版 AI Industry State Map（从三个 child expert claims 组装）；
7. 验证 transmission chain annotation：每条 claim 的 `transmission_step` 是否准确。

## 12. Adjacent Docs

| Doc | Relationship |
|---|---|
| `digestion_00_overview.md` | Layer overview and admission criteria |
| `digestion_10_structure_contract.md` | Object schema for Source Card, Typed Claim |
| `digestion_30_expert_factory.md` | Expert lifecycle and admission |
| `digestion_41_company_expert.md` | Company expert family（同级 umbrella 模式参考） |
| `digestion_41_2_listed_company_expert.md` | Listed company expert（AI ticker 的 company-level digestion） |
| `digestion_51_1_ai_semiconductor_expert.md` | AI Semiconductor child expert |
| `digestion_51_2_ai_datacenter_expert.md` | AI Data Center child expert |
| `digestion_51_3_ai_application_expert.md` | AI Platform/Enterprise Application child expert |
| `digestion_52_healthcare_expert.md` | Healthcare/Life Sciences expert（独立 family，AI 是 channel 之一） |
