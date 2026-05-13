---
title: Company PM Report Instruction (Family)
status: active_draft
reader_persona:
  - PM
  - Research Analyst
  - Report Writer
  - Report Reviewer
---

# Company PM Report Instruction

## 1. Purpose

本文是 `research-company-financial-analysis` skill 的 report grammar truth surface。

它定义如何从 company writer package 写 PM-facing company analysis report，覆盖 listed company 和 private company。通用 grammar 在本文定义；private-company 额外要求在 [`research_31_private_company_report_instruction.md`](research_31_private_company_report_instruction.md)。

本文不拥有 Source Card、Typed Claim、dossier、package assembly。本文只拥有基于 package 写成 PM-facing report 的 prose contract。

结构对称关系：

| Layer | Family umbrella | Listed child | Private child |
|---|---|---|---|
| Digestion (expert) | `digestion_41_company_expert.md` | `digestion_41_2_listed_company_expert.md` | `digestion_41_1_private_company_expert.md` |
| Digestion (package) | `digestion_11_report_package_contract.md` | — | `digestion_12_private_company_report_package_contract.md` |
| Research (report instruction) | **本文** | 本文 §4 | `research_31_private_company_report_instruction.md` |

## 2. Reader End-State

PM 读完 report 后应该能说清：

- 这家公司为什么现在值得读；
- 公司如何赚钱，增长靠什么；
- financial quality 是被证明、被部分支撑，还是不可知；
- competitive position 靠什么，证据支撑到哪一步；
- valuation bridge 用什么 unit of account，public comps 能校准什么；
- bull case、bear case、variant view 的真正分歧在哪里；
- 哪类 evidence class 承载主结论（filing、voluntary disclosure、third-party estimate、AI-derived）；
- 当前 evidence 不支持哪些判断、gap 在哪里；
- 哪个 evidence 会改变下一步判断。

如果 PM 只学到 "the dossier says X, Y, Z"，report 就失败了。

## 3. Report Grammar (通用)

无论 listed 还是 private，default report shape：

1. `Core Read`
2. `Why This Company Matters Now`
3. `Business Model And Growth Drivers`
4. `Financial Quality`
5. `Competitive Position`
6. `Valuation Bridge`
7. `Bull-Bear Debate And Variant View`
8. `Catalysts, Falsifiers, And What Would Change The Read`
9. `Bottom Line`

Section title 可以轻微改名，但 reader gain 必须完整实现。不要逐字段复述 package；每段以 judgment 起手，用 mechanism + evidence + boundary 支撑。

### 3.1 Core Read

开头用一个直接段落完成：

- 陈述当前 judgment；
- 点出为什么值得现在看；
- 指出要拒绝的误读；
- 界定当前证据能支持与不能支持的范围。

Opening 应至少分开以下维度：

- company / business quality；
- financial quality（已由 filing 证明 vs 部分可见 vs 不可知）；
- current market price context（listed）或 secondary surface context（private）；
- evidence gaps。

Private company 额外维度（preferred vs common gap、secondary movement 确认级别）由 research_31 补充。

### 3.2 Why This Company Matters Now

回答为什么 PM 现在应该读这份 report。不是公司简介。落到具体事件、规模变化、估值触发点、行业周期位置、或 comp/theme relevance。

### 3.3 Business Model And Growth Drivers

公司如何赚钱。Revenue / ARR 口径。增长来自什么 driver。evidence class 是什么（filing、voluntary disclosure、third-party estimate）。分开写每个 growth driver：为什么重要，confidence cap 是什么。不堆列表。

### 3.4 Financial Quality

回答 financial quality 被证明到哪一步。Margin、cash conversion、SBC、capex、unit economics 是否可见。哪些字段仍不可知。

### 3.5 Competitive Position

具体 moat 或竞争位置靠什么。不接受 "market leader" 无证据标签。

### 3.6 Valuation Bridge

解释 public comps 能做什么（calibration band、stress-test assumptions、multiple trend）和不能做什么（直接定价 private security、替代缺失 financials）。必须说明 unit of account。

### 3.7 Bull-Bear Debate And Variant View

点名真正 debate。Bull case 靠什么 evidence，bear case 攻击哪个 assumption，最大误读是什么，哪条 falsifier 会推翻当前读法。

### 3.8 Catalysts, Falsifiers, And What Would Change The Read

按对 PM 判断的影响排序。不按容易获得排序。

### 3.9 Bottom Line

把 core read + why-now + 最大分歧 + 最强 evidence + 最高影响 watchpoint 合成一段。不新增 claim。

## 4. Listed Company Additions

Listed company report 在通用 grammar 基础上，按 section 强调：

**§3.3 Business Model And Growth Drivers：**
- revenue drivers、segment mix、margin structure、operating leverage、cash conversion、balance sheet、capital allocation 应来自 filings；
- reported financials 和 filing quality 是 first authority，不是 voluntary disclosure。

**§3.4 Financial Quality：**
- filing quality 和 audit opinion 是 first authority；evidence class 默认 `filing`，其他 class 需标明。

**§3.6 Valuation Bridge：**
- market price 作为 valuation context 和 market behavior，不作为 business quality proof；
- guidance、consensus、expectation gap 是 listed company 特有的 judgment input。

**§3.8 Catalysts, Falsifiers, And What Would Change The Read：**
- catalysts 常与 earnings、guidance、product announcements、macro regime 挂钩。

**Overlay：**
- technical state 可作为 overlay context，但不替代 fundamental read。

## 5. Private Company Additions

Private company report 在通用 grammar 基础上增加：

- 在 §3.6 Valuation Bridge 与 §3.7 Bull-Bear Debate 之间插入 `Private / Secondary Surface Read` 节；
- secondary surface、preferred/common gap、unit-of-account 和 cannot-know boundary 的完整要求。

详见 [`research_31_private_company_report_instruction.md`](research_31_private_company_report_instruction.md)。

## 6. Prose Rules (通用)

### 6.1 写公司，不写 workflow

不写 "this package"、"the dossier says"、"the source card"、"the writer should"、"this report will"。

### 6.2 不制造虚假精确

任何 valuation number 出现在 prose 中时，先说明 unit of account，再说数值。Listed company 的 public market price 本身即 unit-of-account context（公开市场普通股），无需额外前缀；EV、DCF fair value、comp-implied 估值等 derived number 仍需说明口径。

### 6.3 Permission level 在正文可见

- `publicly_observable`：直接陈述，attribution；
- `proxy_inferable`：使用 "appears to," "is estimated at," "third-party research suggests"；
- `not_knowable_from_public_data`：点名 gap，不改写成 guess。

### 6.4 主线要窄

宁可给窄而有用的结论，不要给宽泛安全摘要。

### 6.5 不用 disclaimer 填充判断

不要用 generic disclaimer 藏边界。写 operational boundary：说明 "本 read 不支持 X 因为 Y 缺失"，不写 "risks remain" 或 "past performance does not guarantee"。

## 7. Forbidden Outputs (通用)

Report 不得产生：

- buy / sell / hold；
- position sizing；
- mandate fit；
- execution advice；
- hedge construction；
- target-book changes；
- 声称 market price 变动证明 business quality 改变；
- 把 consensus estimate 当作已实现事实陈述。

Private company 额外禁止项见 `research_31` §7。

## 8. Preflight Gate

所有 company financial report 写作前必须通过 [`research_32_company_financial_report_preflight.md`](research_32_company_financial_report_preflight.md) 三门检查：

1. Package 有足够 benchmark（带 unit-of-account）
2. 所有数字 package-backed
3. Writer 只消费 deterministic narrative inputs + stable grammar

Gate fail 时的修复路径定义在 research_32。

## 9. Adjacent Docs

| Doc | Relationship |
|---|---|
| `research_31_private_company_report_instruction.md` | Private-company projection of this grammar |
| `research_32_company_financial_report_preflight.md` | Three-gate preflight before writing |
| `research_33_company_fundamentals_data_architecture.md` | Fundamentals data object model |
| `digestion_41_company_expert.md` | Company expert family routing |
| `digestion_41_1_private_company_expert.md` | Private-company expert artifacts |
| `digestion_41_2_listed_company_expert.md` | Listed-company expert artifacts |
| `digestion_11_report_package_contract.md` | Shared package interface |
| `digestion_12_private_company_report_package_contract.md` | Private-company package contract |
| `research_00_writer_package_contract.md` | Shared package hygiene |
| `research_00_report_reviewer_pattern.md` | Report review posture |
