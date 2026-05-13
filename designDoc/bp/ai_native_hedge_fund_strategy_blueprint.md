# AI-Native Hedge Fund — Strategy Blueprint

**Version 0.2 — 2026-03-21**

Working strategy document that turns the high-level AI-native hedge fund narrative into a more concrete investment-process blueprint. This revision aligns the strategy narrative with the repo's newer operating-system view: `functional modules`, `KnowledgeBase`, and `AnalysisPlatform`.

---

## 1. Purpose

This document defines how the fund can translate its AI-native operating model into an investable strategy framework. It is not a final offering memorandum or compliance document. It is a practical strategy draft for internal alignment, system design consistency, and future investor refinement.

---

## 2. Strategy Definition

The fund is designed as an **AI-amplified discretionary public-markets strategy** focused on liquid equities, options, and thematic baskets.

The strategy combines:

- macro and regime interpretation
- portfolio exposure awareness
- event and research sensitivity
- technical confirmation
- options-aware risk management

The objective is to produce asymmetric trade selection with tighter risk discipline than a purely manual process and greater flexibility than a purely systematic black-box strategy.

This is best understood as an `AI-native operating system for discretionary investing`, not as a single prediction engine.

---

## 3. Target Opportunity Set

### Primary universe

- large-cap and liquid mid-cap U.S. equities
- index and single-name options with sufficient liquidity
- thematic baskets driven by sector, macro, or event concentration

### Secondary filters

- high average daily volume
- options chains with tradable spreads and usable open interest
- names with clear catalyst calendars or macro sensitivity

The initial strategy should avoid illiquid securities, complex structured products, and markets where data quality or execution confidence is weak.

---

## 4. Where Alpha May Come From

The strategy does not rely on one prediction engine. It seeks edge from a set of information-processing advantages organized through the platform.

### 4.1 Faster synthesis

The system digests portfolio state, market data, and research inputs continuously instead of waiting for periodic analyst review.

### 4.2 Better prioritization

AI agents and workflows rank what matters now: catalysts, concentration risks, volatility conditions, and candidate setups.

### 4.3 Better portfolio context

Ideas are evaluated against live exposures, not in isolation.

### 4.4 Better memory and review

Recommendations, actions, and outcomes can be stored and compared, allowing the process to improve over time.

---

## 5. Functional Operating Modules

The operating system is built around five practical modules:

### 5.1 DataCollection

Collect market, research, portfolio, and event inputs through pluggable connectors and save them as raw artifacts plus minimal metadata.

### 5.2 InfoClassification

Convert raw materials into reusable knowledge objects through normalization, tagging, linking, summarization, and retrieval-oriented organization.

### 5.3 PortfolioExposure

Maintain a live view of account state, directional exposure, basket concentration, options context, and risk flags.

### 5.4 OpportunityRanking

Turn many possible ideas into a short prioritized list using catalyst awareness, expected payoff, portfolio fit, and risk gating.

### 5.5 StructuredAdvice

Produce PM-facing artifacts: recommendations, memos, action framings, and monitoring checklists.

---

## 6. Knowledge Base As Strategic Edge

The strategy increasingly depends on a strong `KnowledgeBase`, not just a strong model.

The knowledge base should preserve:

- research memory
- portfolio state history
- recommendation history
- memo archive
- review archive

This matters because the system's edge is cumulative. A fund that remembers prior context, prior debates, prior errors, and prior outcomes can refine judgment in a way that ad hoc prompting cannot.

For this strategy, knowledge quality is part of alpha infrastructure.

---

## 7. Analysis Platform As PM Workspace

The `AnalysisPlatform` is the current working surface where humans and agents organize judgment.

It should combine:

- current research materials
- current portfolio state
- current risk boundaries
- current opportunity list
- prior memos and prior decisions

Its role is not simply to answer questions. Its role is to organize:

- what matters now
- why it matters
- how it affects the existing portfolio
- what action framing is most appropriate

In the current repo direction, Cursor is expected to become the primary operator endpoint for this workspace, backed by local files, local state, and deterministic CLI actions.

---

## 8. Strategy Archetypes

The operating system is best suited to a small number of repeatable trade archetypes.

### Archetype A: Catalyst-aware directional equity trades

Use macro context, news flow, and technical confirmation to build or reduce equity exposure around major catalysts.

### Archetype B: Options-based expression or hedge adjustment

Use options where they improve convexity, hedge concentrated exposure, or express a volatility view with defined risk.

### Archetype C: Basket-level thematic positioning

Group related names into themes such as AI infrastructure, biotech, semiconductors, or macro-sensitive sectors, then monitor exposure at the basket level.

### Archetype D: Risk reduction and portfolio reshaping

Let the platform identify when exposure has become crowded, unbalanced, or misaligned with the current regime, then rebalance or hedge.

---

## 9. Portfolio Construction Principles

The initial portfolio should follow simple, explainable rules:

- prefer liquid instruments
- size positions relative to conviction and liquidity
- monitor aggregate directional and thematic concentration
- use options selectively rather than by default
- maintain enough cash and hedge capacity to respond to regime change

A practical early-stage framework:

- core book of highest-conviction themes and positions
- tactical overlay for catalyst-driven or shorter-horizon trades
- explicit hedge layer for downside regime shifts or concentration control

---

## 10. Role Of The Platform

The platform supports each stage of the investment loop.

### 10.1 Observe

- ingest broker positions and historical market data
- collect research, macro inputs, and relevant external materials
- update options and exposure metrics

### 10.2 Organize

- classify relevant developments
- preserve them in a durable knowledge base
- connect research items to symbols, baskets, and macro topics

### 10.3 Evaluate

- detect technical and volatility conditions
- surface portfolio concentration and risk clusters
- rank candidate opportunities by fit and urgency

### 10.4 Recommend

- suggest adds, reductions, rolls, or hedges
- create PM-facing memos and action framings
- preserve the rationale and evidence trail

### 10.5 Review

- compare recommendations with actual decisions
- support attribution and post-trade learning
- refine future prioritization and triage

---

## 11. Human vs Machine Responsibilities

### Machine responsibilities

- data collection and normalization
- monitoring and alerting
- summarization and triage
- screening and recommendation generation
- process memory and reporting

### Human responsibilities

- final thesis judgment
- capital allocation
- override decisions
- exception handling
- risk acceptance and accountability

This separation is central to the strategy. The goal is augmented decision-making, not unsupervised automation.

---

## 12. Risk Framework

A credible AI-native fund narrative requires a visible risk framework from day one.

### Core risk checks

- single-name concentration
- sector and basket concentration
- delta exposure by book and theme
- options expiration clustering
- liquidity and spread awareness
- event risk around earnings, CPI, Fed, and similar catalysts

### Operating principle

No recommendation should be evaluated without seeing its effect on the existing portfolio.

Risk is not a downstream afterthought. It is a first-class input into ranking and advice generation.

---

## 13. Example Decision Loop

1. A source connector captures new macro, news, or research material.
2. The knowledge base stores and links the material to current symbols, baskets, and prior memos.
3. The analysis platform overlays the new context onto current portfolio exposure and risk state.
4. Ranking workflows identify the most relevant add, reduce, hedge, or watch actions.
5. A PM-facing memo or structured recommendation is produced.
6. The final decision and later outcome are preserved for review.

This loop is important because the fund edge comes from the cycle, not just the entry signal.

---

## 14. Metrics To Track

The strategy should be evaluated on both investment and operating metrics.

### Investment metrics

- gross and net return
- hit rate and payoff ratio
- drawdown
- exposure-adjusted return
- contribution by theme and trade archetype

### Operating metrics

- number of actionable recommendations produced
- recommendation-to-action conversion rate
- time from catalyst detection to decision review
- false-positive rate in alerts or screening
- quality of post-trade attribution coverage
- memo and review coverage ratio

---

## 15. Initial Operating Constraints

To keep the strategy disciplined in early stages:

- stay in highly liquid instruments
- avoid excessive leverage
- cap single-name and theme concentration
- prefer simple option structures first
- favor explainability over complexity

The goal of the first phase is not maximum complexity. It is repeatability, auditability, and clean learning.

---

## 16. What Needs Further Definition

Before this becomes an allocator-ready strategy memo, the next revision should add:

- target net and gross exposure ranges
- position sizing rules
- hedge policy examples
- turnover expectations
- holding period buckets
- drawdown response rules
- instrument eligibility and liquidity thresholds
- memo and review standards
- operating cadence for PM review

---

## 17. One-Paragraph Internal Strategy Summary

The fund is an AI-amplified discretionary strategy in liquid public markets, using a proprietary operating system to unify data collection, knowledge organization, portfolio monitoring, opportunity ranking, and structured recommendation generation. Edge comes from better memory, better prioritization, and better portfolio-aware action selection, while final capital allocation and risk ownership remain in human hands.
