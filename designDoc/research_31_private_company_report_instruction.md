---
title: Private Company PM Report Instruction
status: active_draft
reader_persona:
  - PM
  - Research Analyst
  - Report Writer
  - Report Reviewer
---

# Private Company PM Report Instruction

## 1. 这份 instruction 解决什么

本文是 [`research_30_company_report_instruction.md`](research_30_company_report_instruction.md) 的 **private-company projection**。

通用 report grammar（section shape、prose rules、forbidden outputs、preflight gate）定义在 research_30。本文只增加 private-company subject 的额外要求：secondary surface、preferred/common gap、unit-of-account、cannot-know boundary、transfer constraints。

输入 package 由 `digestion_12_private_company_report_package_contract.md` 定义。本文不拥有 Source Card、Typed Claim、dossier、package assembly；本文只拥有 private-company report 相对于通用 grammar 的增量 prose contract。

如果 input package frontmatter 的 `status` 是 `blocked`，不要写 PM report。应把失败 gate 退回 package owner。

Report 不是：

- private-company dossier；
- source-card summary；
- valuation model；
- transaction recommendation；
- public equity recommendation for a comp。

Report 是 judgment artifact。它应该帮助 PM 理解：当前能得出什么结论，哪些判断被 blocked，哪个后续 evidence 会改变判断。

## 2. 读者终态 / Reader end-state

PM 读完 report 后应该能说清：

- 这家公司为什么值得现在读，而不是只作为一个数据点存档；
- business model / revenue engine / growth driver 的主线是什么；
- 当前 financial quality 是已被证明、只能由 management-prepared metrics 支撑，还是仍然不可知；
- valuation bridge 用的是什么 unit of account；
- 当前问题到底是 operating-company quality、security price、valuation translation、liquidity，还是 missing evidence；
- 哪类 evidence 承载主结论；
- 哪种常见解读是错误或过早的；
- public comps 应该如何使用、不能如何使用；
- 最新 secondary-market surfaces 是确认真实移动、只提示弱信号，还是不可用；
- bull case、bear case、variant view 的真正分歧在哪里；
- 哪个 evidence 会改变下一步判断。

如果 PM 只学到 “the dossier says X, Y, Z”，report 就失败了。

## 3. 默认报告结构 / Default report shape

默认使用 company financial analysis report shape，除非 package 给出更强的 reader path。

本节负责解释 package 的 `Narrative Analysis Inputs` 和 `Report Instruction -> Per-Asset Specialization` fields：

- `Core Read` 必须把 `writer_anchor_claim_refs` 和 anchor slots 转成最终 PM-facing headline language，但不能把 package 当成 PM belief；
- `Why This Company Matters Now` 必须解释为什么这家公司值得 PM 现在读；
- `Valuation Bridge` 与 `Private / Secondary Surface Read` 必须保留 package 的 unit-of-account、pricing-surface、public-comp 和 cannot-know boundaries；
- `Bull-Bear Debate And Variant View` 必须渲染 package 的 biggest misread、variant view、falsifiers；
- `What Would Change The Read` 必须渲染 `company_specific_watchpoints` 和 `evidence_gaps`。

Package 提供的是 `narrative_analysis_inputs` 和 per-asset specialization，不提供报告风格真理。Writer 必须以本文件的 reader end-state 和 section job 为准，把 package inputs 转成 analyst memo；不能把 package fields 逐项复述成文章。

Prose 可以展开或补充 context，但不能和 package 的 per-asset specialization 矛盾。Section title 是 reader path，不是表格格子；如果 report 读起来像 checklist completion，而不是帮助 PM 形成判断，report 就失败。

### 3.1 核心判断 / Core Read

开头用一个直接段落完成四件事：

- 陈述当前 judgment；
- 点出这家公司现在为什么值得看；
- 指出要拒绝的误读；
- 界定当前公开证据能支持与不能支持的范围。

Opening 必须分开：

- company quality；
- financial quality；
- business quality；
- private valuation / security price；
- recent secondary-market movement；
- evidence gaps。

### 3.2 为什么这家公司现在重要 / Why This Company Matters Now

这一节解释公司本身的 PM relevance，而不是解释 package 为什么存在。它应该回答：

- 公司处在哪条行业或产品变化线上；
- 当前规模、增长、客户、产品、商业模式或融资状态为什么让它进入 PM 视野；
- 哪个问题最可能改变公开 comp、主题理解、IPO / pre-IPO 读法或 private-market calibration。

如果这一节只复述公司简介，report 失败。它必须交代 why now。

### 3.3 业务模式与增长引擎 / Business Model And Growth Drivers

这一节把 operating-company read 写成 business analysis：

- 公司如何赚钱；
- revenue / ARR / run-rate 的口径是什么；
- 增长来自客户数、价格、用量、产品 mix、地域、AI / product cycle，还是一次性披露；
- 当前 evidence 是 issuer voluntary、management-prepared、third-party estimate，还是 audited / filing-like。

不要把增长数字直接堆成列表。每段要说明一个 driver 为什么重要，以及它的 confidence cap。

### 3.4 财务质量 / Financial Quality

这一节回答 financial quality 到哪一步：

- margin、cash conversion、SBC、capex、gross margin by product、FCF 质量是否可见；
- 公开资料是否足以判断 unit economics；
- 哪些字段仍然不能从 public data 得知；
- 如果是 issuer voluntary disclosure，必须说明 unaudited / management-prepared 的边界。

### 3.5 竞争位置 / Competitive Position

解释 moat 或竞争位置具体靠什么：

- product breadth；
- switching cost；
- customer depth；
- ecosystem / platform effect；
- performance / cost advantage；
- distribution or go-to-market；
- scarcity or strategic relevance。

不要把 "market leader" 当结论，必须说明 evidence 支撑到哪一步。

### 3.6 估值桥 / Valuation Bridge

解释 comp comparison 能做什么：

- 建立 private valuation 的 calibration band，并识别 growth、retention、margin、multiple 等哪个 assumption 在驱动判断；
- stress-test growth and margin assumptions；
- 显示 public-market multiple trend 是 compression、expansion，还是 stable；
- 点出 private company 在 IPO 或 public-market translation 前必须证明什么。

解释它不能做什么：

- 证明 private company 便宜或昂贵；
- 在缺少 unit-of-account adjustment 时给 preferred round、common share、SPV unit、tender 或 fund mark 定价；
- 替代缺失的 private-company financials。

### 3.7 私有证券价格与定价表面解读 / Private / Secondary Surface Read

当 report 讨论 secondary 或 OTC price 时：

- 命名 platform / source；
- 命名 signal type；
- 按 package 提供的字段命名 measurement date、source publication date、retrieval date；
- 在数字之前先说明 unit of account；
- 说明 bid / ask / last matched / size / share class / fee treatment 是否可见；
- 说明 ROFR / board approval / lock-up / settlement risk 等 transfer constraints 是否可见或未知；
- 说明该 surface 是 firm、indicative、model-derived、stale，还是 gated。

如果 measurement date 和 retrieval date 相差超过一个 trading day，必须写出来。

使用窄动词：

- “shows”；
- “suggests”；
- “does not confirm”；
- “cannot prove”；
- “requires a verified quote”。

不要写：

- “the market says”；
- “the stock is down”；
- “valuation has reset”；
- “buyers are walking away”；

除非 source 真的证明这些 claims。

### 3.8 分歧与变体观点 / Bull-Bear Debate And Variant View

点名真正的 debate，而不是简单列风险。

这一节应该说明：

- bull case 依赖哪些 evidence；
- bear case 攻击哪个 assumption；
- variant view 是否存在；
- 最大误读是什么；
- 哪条 falsifier 会让当前 read 失效。

常见误读包括：

- “secondary price down” 不证明 business deterioration；
- latest primary valuation 不等于 common-share fair value；
- public comp multiple 不直接给 private security 定价；
- strong issuer metrics 不证明 audited margin quality。

### 3.9 什么会改变判断 / What Would Change The Read

每篇 report 都应列出 decision-relevant watchpoints：

- audited 或 filing-like disclosure：S-1、lender disclosure，或 audit / preparation basis 可见的其他 filing-like disclosure；
- 带 share class、size、fees、transfer constraints 的 verified firm quote；
- tender document；
- 带 methodology 的 fund mark；
- public comp multiple break；
- product-level margin / AI revenue quality；
- cap table / liquidation preference disclosure。

Watchpoints 按对 PM 判断的影响排序，不按容易获得的程度排序。

### 3.10 最终落点 / Bottom Line

结尾用一段话把以下内容合在一起：

- core read；
- 公司为什么现在重要；
- 最大分歧；
- 最强 evidence class；
- 最高影响 watchpoint。

Bottom line 不新增 claim。它应该把 PM 留在正确的下一个问题上。

## 4. Narrative Analysis Slots

`Narrative Analysis Slots` 是 Research 层 report grammar，不是 package layer 的写作规则。Package 只提供 `narrative_analysis_inputs`，writer 在本文语法下决定如何组织成自然 analyst prose。

每个 slot 的作用是回答一个 reader question：

| Slot | Reader question | Package input should provide | Report failure mode |
| --- | --- | --- | --- |
| `why_this_company_matters_now` | 为什么这家公司值得 PM 现在读，而不是只存档？ | relevance facts、规模 / 增长 / 产品 / 融资 / 估值触发点、theme / comp / IPO relevance | 只写公司简介或行业背景，没有 why-now judgment |
| `business_model_and_growth_drivers` | 公司如何赚钱，增长到底靠什么？ | revenue / ARR / run-rate facts、customer / product / usage / geography / AI driver facts、source class 和 confidence cap | 把增长数字堆成列表，没有解释 driver 或证据边界 |
| `financial_quality` | 当前财务质量被证明到哪一步？ | margin / cash conversion / SBC / capex / product gross margin / FCF fields、audited vs unaudited status、cannot-know rows | 把 management-prepared metrics 写成 audited quality，或只用 generic disclaimer |
| `competitive_position` | 竞争位置具体靠什么，证据支撑到哪一步？ | product breadth、switching cost、customer depth、ecosystem / platform、distribution、scarcity facts | 用 “market leader / moat strong” 这类标签代替机制 |
| `valuation_bridge` | 估值桥的 unit of account 是什么，public comps 能校准什么？ | valuation numerator / denominator、public comp calibration facts、unit-of-account gap、confidence cap | 直接说便宜 / 贵，或把 public comp multiple 当 private security price |
| `private_secondary_surface_read` | secondary surface 真正说明什么，不能说明什么？ | platform / signal type / measurement date / source publication date / retrieval date / unit / visible and missing fields | 把 indicative platform price 写成 executable depth、business quality 或 common-share fair value |
| `bull_bear_debate_and_variant_view` | 真正分歧在哪里，哪条 falsifier 会推翻当前读法？ | bull evidence refs、bear assumption refs、biggest misread ids、variant view inputs、falsifiers | 只列风险，没有说明 debate 的核心 assumption |
| `what_would_change_the_read` | 哪些证据会改变 PM 判断，优先级如何？ | watchpoints、evidence gaps、cannot-know rows、counterevidence / falsifier refs | watchpoints 按容易获得排序，或变成泛泛 “monitor news” |

Writer 使用这些 slots 时必须先问 “PM 读完后能多判断什么”，再决定段落结构。Slot 不要求逐项露出字段名；只要求 reader gain 被完整实现。

## 5. 必需章节 / Required sections

默认 PM-facing report 应包含：

1. `Core Read`
2. `Why This Company Matters Now`
3. `Business Model And Growth Drivers`
4. `Financial Quality`
5. `Competitive Position`
6. `Valuation Bridge`
7. `Private / Secondary Surface Read`
8. `Bull-Bear Debate And Variant View`
9. `What Would Change The Read`
10. `Bottom Line`

Section title 可以轻微改名，但 §2 的 reader end-states 必须清楚可见。

## 6. 正文规则 / Prose rules

### 6.1 写公司、价格表面和证据 / Write About The Company, Price Surface, And Evidence

不要写 workflow meta：

- 不写 “this package”；
- 不写 “the dossier says”；
- 不写 “the source card”；
- 不写 “the writer should”；
- 不写 “this report will”。

### 6.2 不制造虚假精确 / No False Precision

Private-company numbers 常混合不同 unit of account。任何 private-company price 或 valuation 出现在 prose 中时，必须先说明 unit of account，再说数值。

Examples：

- preferred-round post-money valuation；
- common-share PPS；
- indicative platform PPS；
- SPV all-in price；
- tender price；
- fund mark；
- public enterprise value。

Bare dollar figure for a private-company price is non-compliant。

### 6.3 不用 disclaimer 填充判断 / No Disclaimer Padding

不要用 generic disclaimer 藏住边界。要写 operational boundary：

```text
This read does not support buy / sell / sizing because the packet lacks executable security terms.
```

### 6.4 主线要窄 / Keep The Mainline Narrow

宁可给窄而有用的结论，不要给宽泛安全摘要。

Good：

```text
Visible secondary surfaces do not confirm a recent markdown; the real risk is whether the preferred-round mark can survive public-market translation.
```

Bad：

```text
The company is strong, but risks remain.
```

### 6.5 权限层级必须在正文可见 / Permission Level Must Be Visible In Prose

任何依赖 non-`publicly_observable` source 的 claim，都必须用 hedge 让 PM 不重读 package 也能恢复 permission level：

- `publicly_observable`：可直接陈述，但要 attribution。
- `proxy_inferable`：使用 “appears to,” “is estimated at,” “third-party research suggests” 等语言，并显式标注 source-class attribution。
- `not_knowable_from_public_data`：直接点名 gap，不要改写成 guess。

Package emit 的任何 claim，只要 `permission_level != publicly_observable` 或 `confidence_cap_reason` 非空，就必须在 prose 中带 inline qualifier。常见 phrasing 包括 `unaudited`、`management-prepared`、`voluntary disclosure`、`indicative platform price`；其他 cap 直接渲染 package 的 `confidence_cap_reason`。

## 7. 禁止输出 / Forbidden outputs

Report 不得产生：

- buy / sell / hold；
- position sizing；
- private-share transaction recommendation；
- mandate fit；
- execution preview；
- 声称 secondary-market surface 证明 business quality；
- 声称 public comp 直接给 private security 定价；
- preferred-round valuation equaling common-share fair value；
- public ticker recommendation for a comp。

同时继承 `digestion_12_private_company_report_package_contract.md` §11 列出的全部 blocked output identifiers。本文只补充 prose-level 禁止表述，不能缩小 package 层的 canonical deny surface。

## 8. 审稿检查表 / Reviewer checklist

Private-company PM report 只有满足以下条件才通过：

- package status 不是 `blocked`；
- core read 必须清楚分开 company quality、financial quality、business quality、private valuation / security price、recent secondary-market movement 和 evidence gaps；混在一起即不通过；
- report 的 core read、why-now、bull-bear debate、watchpoints、evidence gaps 不与 package 的 `Per-Asset Specialization` fields 矛盾；
- why-now 必须说清公司为什么现在值得 PM 读；
- business model / growth drivers 不能只堆数字，必须说明 driver 和 evidence class；
- financial quality 必须说明 audited / unaudited / management-prepared / not-knowable 边界；
- competitive position 必须落到具体 moat / go-to-market / product / customer / ecosystem evidence；
- valuation bridge 必须说明 public comp 能做什么和不能做什么；
- biggest misread 或 variant view 必须点名；
- evidence classes 不能合并；
- permission level 必须按 §6.5 在正文可见；
- 每个 package claim 如果 `confidence_cap_reason` 非空，都在 prose 中 inline 渲染；
- 每个 private-company price 都必须说明 unit of account；
- unaudited、voluntary、management-prepared、indicative metrics carry an inline qualifier；
- public comp use 必须被界定；
- pricing surfaces 必须带 signal type、measurement date、source publication date、retrieval date；
- pricing-surface paragraphs distinguish measurement date from retrieval date when the package shows them as different；
- pricing surfaces state whether transfer constraints are visible or unknown；
- cannot-know boundaries change the read rather than sit in a disclaimer；
- watchpoints that would change judgment are explicit and ordered by impact；
- report contains no workflow-meta language such as `this package`, `the dossier says`, `the writer should`, or `this report will`；
- no paragraph closes with a generic disclaimer in place of an operational boundary statement；
- bottom line takes a narrow position rather than a broad-safe summary；
- report 不能像 checklist completion；每节必须回答对应 reader question；
- `digestion_12` §11 的 package-level blocked output identifiers 不得泄漏进 report；
- prose-level forbidden phrasing 不得出现。

## 9. 相邻文档关系

- `digestion_12_private_company_report_package_contract.md` 定义本文消费的 private-company package。
- `digestion_11_report_package_contract.md` 定义 private-company package 继承的通用 Digestion report-package interface。
- `digestion_41_1_private_company_expert.md` 定义 private-company expert artifacts 与 evidence firewalls。
- `research_00_writer_package_contract.md` 定义共享 package hygiene、size 与 evidence rules。
- `research_00_report_reviewer_pattern.md` 定义通用 report review posture。
