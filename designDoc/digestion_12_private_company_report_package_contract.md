---
title: Private Company Report Package Contract
status: active_draft
reader_persona:
  - Research Architect
  - Digestion Worker Designer
  - PM Report Writer
  - Package Reviewer
---

# Private Company Report Package Contract

## 1. 这份 contract 解决什么

本文定义 `private_company_report_package` contract。

它继承 `digestion_11_report_package_contract.md` 的通用 Digestion report-package interface，并专门处理 private-company expert output：

```text
private_company_dossier
  + PrivateCompanySourceCard
  + PrivateCompanyTypedClaim
  + source_packet / route metadata
  -> private_company_report_package
  -> research_31_private_company_report_instruction.md
```

Package 不是 PM-facing report。它是 Private Company Expert 到 Research writer 的受控 handoff。

它防止两个 private-company failure mode：

- writer 机械压缩 dossier，写成字段逐项摘要；
- writer 把 pricing surface 写成 business quality、valuation advice 或 transaction recommendation。

## 2. 继承关系

本文继承 `digestion_11_report_package_contract.md` 的全部 common rules，尤其是：

- `Reader End-State` first；
- 使用 `Anchor Read`，不写成 PM belief；
- expert artifact 是 input，不是 package structure；
- claim eligibility fields 必须保留；
- blocked assumptions 是 writer inputs；
- 引用 Research-layer prose contract，但不重新定义它；
- 禁止 raw archive dump；
- package body 保持 compact，plumbing 进入 sidecar。

本文只在明确说明处增加 private-company-specific rules。

## 3. 输入 / Inputs

Builder-side inputs 由 package builder 消费，不能整份嵌进 package body：

- `source_packet.md` and `source_packet.json`;
- `private_company_dossier.md`;
- private-company Source Cards;
- private-company Typed Claims;
- source archive paths for quote verification;
- run log paths for source freshness and operation audit.

Package-body references 是 writer 用于 spot verification 的 path 或 ID：

- `source_packet`;
- `expert_artifacts[]`;
- `included_source_card_ids[]`;
- `included_claim_ids[]`;
- manifest pointer.

Optional inputs：

- public-comp single-stock packet;
- verified broker / SPV quote with share class, fee, size, and firm / indicative status;
- filing-like disclosure or S-1;
- fund mark with methodology.

缺少 optional input 时，必须形成显式 `Cannot-Know / Needs-Source` row，不能静默跳过。

## 4. 包体增量 / Package additions

`digestion_11_report_package_contract.md` 的通用 body order 继续适用。本文在对应 sections 里增加以下 required blocks：

- `Pricing-Surface Map` under `Evidence Weighting`;
- `Public-Comp Calibration` under `Evidence Weighting`;
- `Cannot-Know / Needs-Source` under `Boundary / Blocked Assumptions`;
- `Stable Contract` and deterministic `narrative_analysis_inputs` / `Per-Asset Specialization` under `Report Instruction`.

Package 不能在 body 里重新写 `research_31_private_company_report_instruction.md` 已经拥有的 report grammar、section job、reader path 或 prose style。Package 只投影 concrete asset data：claim ids、source classes、permission levels、unit-of-account fields、pricing-surface fields、watchpoints、evidence gaps 和 blocked uses。

## 5. 证据权重 / Evidence weighting

Ranking 使用 `digestion_41_1_private_company_expert.md` 拥有的同一套 `source_class × claim_type` firewall。

| Source class | Operating-quality support_status | Operating-quality priority | Recent-price support_status | Recent-price priority | Notes |
| --- | --- | --- | --- | --- | --- |
| `company_filing:private_issuer_voluntary` | `primary` | 1 | `background` | 4 | 只有 filing-like status 与 audit / preparation basis 清楚时才最强。 |
| `issuer_voluntary_disclosure` | `primary` | 2 | `background` | 5 | 对“issuer 说了什么”强；unaudited / management-prepared metrics 必须带 confidence cap。 |
| `primary_round_disclosure` | `calibration` | 1 | `calibration` | 3 | 支持 round valuation / terms；不能证明 current common-share fair value。 |
| `secondary_market_surface` | `blocked` | 0 | `primary` | 1 | recent pricing signal 的直接 surface；business-quality claim types 禁用。 |
| `fund_mark_surface` | `calibration` | 2 | `secondary` | 2 | 只有 methodology 与 measurement date 清楚时，才支持 investor mark context。 |
| `third_party_private_research` | `secondary` | 1 | `secondary` | 4 | 没有 primary-source support 时只能是 proxy-inferable。 |
| `public_comp_surface` | `calibration` | 3 | `calibration` | 5 | Public comps 只校准 bridge；不直接给 private security 定价。 |

`support_status` 必须是 `primary`、`secondary`、`calibration`、`background`、`blocked` 之一。`priority` 只是在同一 `support_status` 内部排序，不是跨 status 的全局 rank。

对 operating-quality claims，`secondary_market_surface` 在 `revenue_growth_quality`、`retention_quality`、`margin_or_cash_conversion`、`product_mix` 等 business-quality claim types 上是 blocked。它可以支持以 pricing surface 本身为对象的 claim types，例如 transaction close risk、liquidity constraint、recent price movement。

对 recent price-movement claims，`secondary_market_surface` 自然排在最前，因为它就是被解释的直接 surface。即便如此，它也不能覆盖 operating-company fundamentals 或证明 business quality。

任何 ranking 变化都必须在 package 中记录明确理由。

## 6. 字段投影扩展 / Claim projection extension

每条可以进入 main article 的 private-company claim，除了继承 `digestion_11_report_package_contract.md` 的 common claim fields，还必须保留 `digestion_41_1_private_company_expert.md` 的 private-company fields：

```yaml
permission_level:
confidence_cap_reason:
unit_of_account:
metrics:
  period:
  source_basis:
falsifiers: []
```

当 claim 涉及 valuation、PPS、tender、SPV、fund mark、primary round 或 secondary surface 时，`unit_of_account` 必填。

`digestion_11_report_package_contract.md` §5 R3 的 common claim fields 仍然必填，包括 `source_class`、`claim_type`、`allowed_use`、`package_use_override`、`time_validity`、`downstream_blocked_use`、`why_it_matters_for_pm`、`must_not_say`。

## 7. 定价表面图 / Pricing-Surface Map

每个可见 pricing surface 必须包括：

- platform or source；
- signal type：bid、ask、last matched、indicative model price、primary round、tender、fund mark、SPV all-in price；
- measurement date / source publication date / retrieval date；
- PPS or valuation；
- unit of account；
- share class；
- fee treatment；
- firm vs indicative；
- known transfer constraints；
- blocked fields。

Package 必须说明该 surface 能支持什么：

- recent movement；
- executable depth；
- primary-round consistency；
- common-share fair value；
- business quality。

Non-contract note：常见 public secondary-market pages 往往只能支持 recent movement，有时能支持 primary-round consistency；package 仍必须按上面的 field-level support checks 判断，不能依赖这个经验描述。

## 8. 可比 public comp 校准 / Public-Comp Calibration

使用 `digestion_41_1_private_company_expert.md` 的 public-comp calibration template：

1. Public comp baseline
   - selected public comps、comparability rationale、revenue scale、growth、NRR / NDR、gross margin / FCF margin、EV / revenue、denominator、public-market multiple trend。
2. Private subject scope
   - disclosed or externally estimated revenue / ARR、growth、product mix、profitability status、period、confidence cap。
3. Premium / discount bridge
   - growth-quality premium、retention gap、profitability gap、scale、information asymmetry、liquidity discount、share-class / unit-of-account differences。
   - 每个 adjustment 都必须带 `permission_level` 和 `confidence_cap_reason`。
4. Cross-check against private pricing surfaces
   - primary round、secondary-market surface、tender、fund mark、SPV all-in price；按 measurement date、source publication date、retrieval date、share class、fees、transfer constraints reconciled。
5. Output gate
   - 说明 comp 能校准什么，不能证明什么。

Package 不能让 writer 仅因为某个 public comp 的 multiple 不同，就写 private company 便宜或昂贵。

## 9. 被阻断假设 / Blocked assumptions

以下 blocked assumptions 必须作为 first-class writer inputs 进入 package：

- audited financials;
- fully diluted share count;
- common-vs-preferred fair value;
- liquidation preferences;
- cap table;
- transfer approval probability;
- executable secondary depth;
- employee selling pressure;
- product-level margin;
- AI pass-through cost or gross margin where relevant.

## 10. 报告输入投影 / Report input projection

Package 的 Report Instruction section 是 `research_31_private_company_report_instruction.md` 的 runtime input projection，不是新的写作指令。

Package 必须：

- 渲染 `Stable Contract` block，引用 `research_31_private_company_report_instruction.md` 作为 binding prose contract；
- 渲染 `Narrative Analysis Inputs` block，字段名必须对应 `research_30_company_report_instruction.md` §3 的 slots，但字段值只能是 deterministic data projection；
- 每个 slot input 尽量使用 claim refs、source-card refs、permission level、unit of account、confidence cap、pricing-surface field、watchpoint 或 evidence gap，不写 PM-facing prose；
- 携带该 contract 留给 per-asset 的变量：writer anchor claim refs、biggest misread ids、company-specific watchpoints、evidence gaps；
- 不重新定义 report format、target reader、blocked outputs、final prose order。

不能只写 “write a PM-facing report”。也不能在 package 里写 “bull case 应该怎么说 / bear case 应该怎么说 / report 应该如何定调” 这类 prose decision。那些属于 `research_30_company_report_instruction.md` 和 writer judgment。

## 11. 禁止输出 / Blocked outputs

Package 必须 block 以下 canonical output identifiers：

| Blocked output id | Meaning |
| --- | --- |
| `portfolio_action` | buy / sell / hold-as-recommendation |
| `position_sizing` | position size, exposure, or allocation |
| `private_share_transaction_recommendation` | recommendation to transact private shares |
| `mandate_fit` | whether the security fits a mandate |
| `execution_advice` | execution preview, hedge construction, or transaction instruction |
| `secondary_price_proves_business_quality` | claim that secondary price proves business quality |
| `preferred_round_equals_common_share_fair_value` | claim that preferred-round valuation equals current common-share fair value |
| `public_comp_multiple_implies_private_cheap_or_expensive` | claim that public-comp multiple directly proves the private subject is cheap or expensive |
| `public_ticker_recommendation_for_comp` | public ticker recommendation for a comp |

## 12. 验证门槛 / validation gates

`private_company_report_package` 出现以下情况即 invalid：

- 缺少 per-asset reader end-state；
- 缺少 anchor read；
- `Report Instruction` 包含 `summarize the dossier`、`compress the dossier`、`rewrite the dossier into prose`；
- `Report Instruction` 重新定义 `research_30_company_report_instruction.md` 的 report grammar、section job、reader path 或 prose style；
- `Report Instruction` 缺少 deterministic `Narrative Analysis Inputs`；
- `Claims For Main Article` 为空，或只复述 dossier subsection titles；
- report-eligible claims 缺 `source_class` / `allowed_use` / `permission_level` / confidence caps；
- valuation 或 pricing claim 缺 `unit_of_account`；
- pricing surface 缺 measurement date、source publication date 或 retrieval date；
- measurement date、source publication date、retrieval date 不一致时没有显式标出；
- 缺 pricing-surface blocked uses；
- 缺 public-comp limitations；
- 缺 cannot-know boundaries；
- §3 optional inputs 缺失时，没有对应 `Cannot-Know / Needs-Source` rows；
- 缺 watchpoints that change the read；
- 没有显式 block buy / sell / sizing / mandate fit / execution advice / private-share transaction recommendation；
- 没有显式 block analytical leaks：secondary price proving business quality、preferred-round valuation equaling common-share fair value、public-comp multiple proving private subject cheap/expensive、public ticker recommendation for a comp。

## 13. 最小模板 / Minimum template

这是 child contract template。使用前必须先确认 §3 inputs、§10 report instruction、§12 validation gates 已就位，不能只复制模板。

```markdown
---
content_type: private_company_report_package
schema_version: digestion_report_package_v0
package_id:
subject_ref:
subject_expert_id: private_company_expert
source_packet:
expert_artifacts:
  - expert_id: private_company_expert
    artifact_id:
    role: subject
included_source_card_ids: []
included_claim_ids: []
generated_at_utc:
status: ready_to_write | blocked
allowed_outputs:
  - pm_facing_private_company_report
blocked_outputs:
  - portfolio_action
  - position_sizing
  - mandate_fit
  - execution_advice
  - private_share_transaction_recommendation
  - secondary_price_proves_business_quality
  - preferred_round_equals_common_share_fair_value
  - public_comp_multiple_implies_private_cheap_or_expensive
  - public_ticker_recommendation_for_comp
---

# <Company> Private-Company PM Writer Package

## Reader End-State

## Anchor Read

## Evidence Weighting

### Pricing-Surface Map

### Public-Comp Calibration

## Claims For Main Article

## Boundary / Blocked Assumptions

### Cannot-Know / Needs-Source

## Watchpoints That Change The Read

## Report Instruction

### Stable Contract

Use `research_31_private_company_report_instruction.md` as the binding PM-facing prose contract.

### Narrative Analysis Inputs

```yaml
narrative_analysis_inputs:
  why_this_company_matters_now:
    claim_refs: []
    source_card_refs: []
    facts: []
  business_model_and_growth_drivers:
    claim_refs: []
    source_card_refs: []
    facts: []
  financial_quality:
    claim_refs: []
    permission_level:
    confidence_cap_reason:
    evidence_gaps: []
  competitive_position:
    claim_refs: []
    source_card_refs: []
    facts: []
  valuation_bridge:
    claim_refs: []
    unit_of_account:
    calibration_refs: []
    cannot_use_as_direct_private_security_price: true
  private_secondary_surface_read:
    claim_refs: []
    pricing_surface_refs: []
    unit_of_account:
    visible_fields: []
    missing_fields: []
    blocked_uses: []
  bull_bear_debate_and_variant_view:
    bull_evidence_claim_refs: []
    bear_assumption_refs: []
    biggest_misread_ids: []
    falsifiers: []
  what_would_change_the_read:
    watchpoints: []
    evidence_gaps: []
```

### Per-Asset Specialization

- writer_anchor_claim_refs:
- biggest_misread_to_prevent:
- company_specific_watchpoints:
- evidence_gaps:

## Manifest Pointer
```

## 14. 相邻文档关系

Read before:

- `digestion_10_structure_contract.md` 拥有 Source Card、Typed Claim、Expert Artifact、Promotion Link 与共享对象图。
- `digestion_11_report_package_contract.md` 拥有通用 report-package interface。
- `digestion_41_1_private_company_expert.md` 拥有 private-company expert artifacts 与 evidence firewalls。
- `research_00_writer_package_contract.md` 拥有 repo 级 writer-package 体积、证据与 fail-fast 原则。

Read after:

- `research_31_private_company_report_instruction.md` 拥有 PM-facing private-company report prose contract。

Consumed by:

- private-company report package builders；
- `writer-handoff`-style pre-writing gates；
- PM-facing private-company report writers and reviewers。

Dogfood:

- `designDoc/learning_library/projects/databricks_private_company_research/README.md` 是使用本文的第一个 concrete private-company project。
