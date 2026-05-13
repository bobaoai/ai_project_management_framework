---
name: research-company-financial-analysis
description: "Writes PM-facing company financial analysis reports from company expert dossiers, source cards, typed claims, financial disclosures, public comps, and market or secondary pricing surfaces. Use when the user asks for a company research report, financial analysis, equity-research-style memo, public-company fundamental report, private-company report, IPO/pre-IPO read, valuation bridge, business quality read, or Databricks-style company memo. Handles public and private companies in one skill; private-company subjects add secondary-surface and cannot-know boundaries."
---

# Research Company Financial Analysis

## What This Skill Does

Use this skill when the task is to write or shape a PM-facing company analysis report.

This skill is for:

- public-company fundamental analysis;
- private-company or pre-IPO analysis;
- equity-research-style company memos;
- business model, growth, margin, unit economics, moat, valuation, catalyst, and risk analysis;
- translating Digestion company expert output into a readable PM report;
- comparing company fundamentals against public comps or secondary-market surfaces.

This skill is not:

- `research-single-stock-analysis`, which asks what one listed ticker means now using tape and technical state;
- `writer-asset-technical`, which writes price-action technical reports;
- `research-theme-report-owner`, which maintains standing theme frameworks;
- `research-current-market-reporter`, which explains a market window;
- `operation-portfolio-decision`, which decides book action, sizing, hedges, or execution.

## When To Use This Versus Single-Stock

Use this skill when the user's question is primarily:

- business / financial / valuation memo;
- company report;
- fundamental analysis;
- business quality;
- revenue engine, margin, unit economics, balance sheet, or cash conversion;
- public comps, IPO / pre-IPO read, valuation bridge, or secondary-market surface.

Use `research-single-stock-analysis` when the user's question is primarily:

- ticker now;
- tape / technical state;
- actionability now;
- watchlist versus actionable;
- levels, trend, support / resistance, or current price behavior;
- how a listed security should be interpreted before portfolio action.

If the user wants both, run this skill first to establish the business / financial read, then hand the result to `research-single-stock-analysis` for ticker / tape action framing or to `operation-portfolio-decision` when the task becomes book action.

## Desired Result

The output should read like a company analyst memo, not a dossier summary.

After reading it, the PM should be able to say:

- why this company matters now;
- how the business makes money;
- what is driving growth;
- whether financial quality is improving, deteriorating, or still unknowable;
- what the competitive position or moat actually rests on;
- what valuation surface is being used and what it can or cannot prove;
- what the bull case, bear case, and variant view are;
- which next evidence would change the read.

## First Authority

The company is first authority.

Use evidence in this order:

1. company filings, earnings releases, transcripts, S-1 / F-1, investor presentations, or issuer voluntary disclosures;
2. company expert dossier, source cards, and typed claims from Digestion;
3. financial metrics and unit economics;
4. public comps, valuation surfaces, consensus or market data;
5. private-company secondary surfaces, fund marks, tender or broker indications when applicable;
6. theme overlay, technical state, or portfolio implications only after the company read is grounded.

Theme, tape, and portfolio context may sharpen the report, but they must not replace company-level reasoning.

## Public And Private Company Handling

Use one report grammar for both public and private companies.

For public companies, emphasize:

- reported financials and filing quality;
- revenue drivers, segment mix, margin structure, operating leverage, cash conversion, balance sheet, capital allocation;
- guidance, consensus, expectation gap, valuation bridge, catalysts, and risks;
- market price only as market behavior or valuation context, not proof of business quality.

For private companies, add:

- whether metrics are issuer-voluntary, management-prepared, third-party estimated, or transaction-derived;
- preferred-round valuation versus common-share fair value;
- secondary-market surface versus executable depth;
- share class, fees, transfer constraints, ROFR, lock-up, settlement, and platform access;
- cannot-know boundaries such as audited financials, fully diluted share count, liquidation stack, product-level margin, and employee selling pressure.

Private-company secondary prices can support recent pricing-surface context. They cannot prove business quality, common-share fair value, portfolio action, or private-share transaction advice.

## Primary Truth Surfaces

Read first:

- the user's request;
- the company asset workspace under `data/digestion/independent_research/assets/<asset_key>/` when present;
- `source_packet.md` and `source_packet.json`;
- expert outputs under `expert_outputs/company_expert/`, `expert_outputs/listed_company_expert/`, or `expert_outputs/private_company_expert/`;
- `single_asset_dossier` for listed-company subjects;
- `private_company_dossier` for private-company or pre-IPO subjects;
- Source Cards and Typed Claims;
- any writer package already built for the company.

Read next when relevant:

- `designDoc/research_30_company_report_instruction.md` for report grammar (listed + private, how PM forms judgment);
- `designDoc/research_31_private_company_report_instruction.md` for private-company projection additions;
- `designDoc/research_32_company_financial_report_preflight.md` for the three-gate preflight before writing;
- `designDoc/digestion_41_1_private_company_expert.md`;
- `designDoc/digestion_41_2_listed_company_expert.md`;
- `designDoc/digestion_11_report_package_contract.md`;
- `designDoc/digestion_12_private_company_report_package_contract.md` for private-company packages;
- local theme reports only as overlay context;
- technical reports only when the user asks how the security trades now.

This skill consumes Digestion outputs. It does not author Source Cards, Typed Claims, `single_asset_dossier`, or `private_company_dossier`.

Compatibility note: a private-company artifact may be invoked through a near-term compatibility route such as `company_expert + template_id: private_company_dossier`. Treat the semantic object as `private_company_dossier` and preserve the private-company contract even if the runtime path includes `company_expert`.

## Report Grammar

Default shape:

1. `Core Read`
2. `Why This Company Matters Now`
3. `Business Model And Revenue Engine`
4. `Growth Drivers`
5. `Financial Quality`
6. `Competitive Position`
7. `Valuation Bridge`
8. `Private / Secondary Surface Read` when applicable
9. `Bull-Bear Debate And Variant View`
10. `Catalysts, Falsifiers, And What Would Change The Read`
11. `Bottom Line`

The headings may change, but the reader gain must survive.

Do not write a field-by-field summary. Each paragraph should lead with a judgment, then support it with mechanism, evidence, and boundary.

## Package Contract

A sufficient company-financial package should make these explicit:

- company identity and subject type: public, private, pre-IPO, subsidiary, or comparable company;
- current company read;
- why-now reason;
- business model and revenue engine;
- growth drivers and their evidence quality;
- financial quality and missing data;
- competitive position;
- valuation surface and unit of account;
- public-comp bridge;
- private or secondary surface bridge when applicable;
- bull case, bear case, and variant view;
- catalysts, falsifiers, and cannot-know boundaries;
- allowed outputs and blocked outputs.

If these fields are missing, request a better package before writing.

Private / pre-IPO packages must additionally include:

- pricing-surface unit of account;
- share class;
- fee treatment;
- transfer constraints;
- firm versus indicative status;
- source publication date, measurement date, and retrieval date;
- preferred-round valuation versus common-share fair-value boundary;
- cannot-know boundaries for audited financials, fully diluted share count, cap table, liquidation stack, product-level margin, executable secondary depth, and employee selling pressure when unresolved.

If a private-company package lacks these fields, do not let the writer infer them. Route the gap through `writer-handoff` as `need_more_detail`.

## Blocked Outputs

This skill must not emit:

- buy / sell / hold as a recommendation;
- position sizing;
- mandate fit;
- execution advice;
- hedge construction;
- target-book changes;
- private-share transaction recommendations;
- claims that secondary-market surface proves business quality;
- claims that public comps directly price a private security;
- claims that preferred-round valuation equals common-share fair value.

## Writing Standard

Write in Chinese by default unless the user asks otherwise.

Use natural analyst prose. Keep English terms when they are market-standard or clearer.

Lead with the read. Do not bury the conclusion behind source inventory.

Prefer:

- "这家公司现在值得看，是因为..."
- "真正的分歧不在收入是否增长，而在..."
- "这个估值面只能说明..."
- "下一条能改变判断的证据是..."

Avoid:

- "the dossier says";
- "this package";
- "the source card";
- "the writer should";
- raw schema keys in prose unless needed for precision;
- portfolio or transaction action unless the task has moved to `operation-portfolio-decision`.

## Failure Signals

Treat these as skill failures:

- the report reads like a Source Card or dossier summary;
- the report reads like a theme report with the company attached;
- the report reads like a technical report with no financial analysis;
- valuation is discussed without naming the unit of account;
- secondary-market surface is used to prove business quality;
- public comps are used to directly price a private security;
- private-company gaps are hidden in disclaimers instead of becoming decision-relevant cannot-know boundaries;
- the memo prescribes buy / sell / hold, sizing, mandate fit, execution advice, hedge construction, target-book changes, or private-share transaction action;
- the PM cannot identify the bull-bear debate or the evidence that would change the read.

## Runtime Bindings

Runtime node bindings and `tradectl` entrypoints are not yet declared for this skill. Until they are added, use the owning Digestion package / dossier paths plus `writer-handoff` as the sufficiency gate, and do not claim the artifact is graph-admitted unless a node has been added to `data/runtime/artifact_graph.yaml`.

## Example Triggers

- "写一份公司分析报告"
- "做一个 financial analysis"
- "这家公司基本面怎么看"
- "Databricks 这种 private company 写成 PM report"
- "像 equity research 一样分析一下"
- "看一下估值桥和 public comps"
- "这个 pre-IPO / secondary surface 怎么读"
