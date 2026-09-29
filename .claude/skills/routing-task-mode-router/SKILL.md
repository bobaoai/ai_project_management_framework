---
name: routing-task-mode-router
description: "Acts as the explicit top-level router for the repo's daily task mainlines. Use when a request first arrives and the system must decide which mainline owns it, which first authority should lead, which truth surface should be read first, and whether any downstream `theme overlay` is needed before deeper work begins."
---

# Task-Mode Router

## What This Skill Does

Use this skill as the explicit top-level gate when a request first arrives.

Its job is to decide:

- which daily task mainline owns the request
- which first authority should lead
- which truth surface should be read first
- which downstream mainline skill should receive the task
- whether any overlay is needed without changing first authority

This skill is not a downstream worker and not a domain analysis layer.

## Desired Result

The desired result is a clear routing decision before deeper work begins.

By the time this skill is done, the system should no longer need to guess:

- what type of task this actually is
- which mainline owns it
- whether the request is first about inbox, archive, market interpretation, theme maintenance, company financial analysis, single-stock analysis, portfolio decision, or external learning research
- whether a theme/ticker/account mention is first authority or only context

## Completion Standard

This skill is complete only when all of the following are explicit:

- `matched_mainline`
- `first_authority`
- `primary_truth_surface`
- `downstream_skill`
- `overlay_needed`
- `why_this_route_wins`

Accepted outputs:

- direct route to a stable mainline skill
- direct route to a non-skill workflow surface such as inbox/archive handling when that is the real top-level task
- route plus `theme overlay` note when another mainline still keeps first authority

If the result still depends on vague intuition such as “this feels thematic” or “this mentions a ticker,” this skill is not done.

## Mainline Inventory

Route into these stable top-level task lines first:

- inbox / mail triage → `ingestion-agentmail-inbox-triage`
- archive curation / message promotion → `ingestion-research-archive-operator`
- market recap / market observation → `research-current-market-reporter`
- theme update / theme report maintenance → `research-theme-report-owner`
- theme discovery (bottom-up) → `research-theme-discovery-scanner`
- company financial analysis → `research-company-financial-analysis`
- single-stock analysis → `research-single-stock-analysis`
- portfolio decision → `operation-portfolio-decision`
- external learning research → `research-external-learning`
- independent research (Digestion) → `digestion-independent-researcher`
- external agent build (review / extraction / triage) → `support-external-agent-builder`
- engineering review → `engineering-change-review`
- session support → `support-compaction-handoff`

Do not flatten those into fewer buckets just because they share some modules or materials.

## First-Authority Rule

Choose first authority by the real question being asked:

- inbox / archive flows: `operator` or archive-facing analyst posture
- market recap / market observation: `macro analyst`
- theme maintenance: `macro analyst`
- company financial analysis: company analyst / financial analyst authority
- single-stock analysis: ticker-first analytical authority, still closer to `macro analyst` than immediate PM action
- portfolio decision: `portfolio manager`
- external learning research: `research architect` posture inside Hoveath, using the user's axioms as the interpretation filter

Do not let persona labels replace task-mode judgment. First decide the task mainline, then assign the leading authority inside that line.

## Primary Truth Surface Rule

After matching the mainline, point to the first truth surface that should be read.

Typical first truth surfaces:

- inbox / archive:
  - message objects
  - `content.md`
  - `evidence_units`
  - `source_collection`
- market recap / market observation:
  - event window
  - chosen theme context
  - relevant snapshots
  - cross-asset evidence
- theme maintenance:
  - theme metadata
  - finalized report backbone
  - linked local materials
  - package or sufficiency state
- company financial analysis:
  - company source packet
  - `single_asset_dossier` or `private_company_dossier`
  - Source Cards and Typed Claims
  - financial disclosures, issuer voluntary disclosures, public comps, valuation surfaces, and secondary surfaces when applicable
- single-stock analysis:
  - ticker package
  - deterministic technical state
  - technical report
  - local theme overlay
- portfolio decision:
  - decision package
  - policy envelope
  - portfolio state
  - account review context
- external learning research:
  - external source URLs, official docs, repositories, papers, articles, or critiques
  - `09_soul/axioms/`
  - `09_soul/core/COMMUNICATION.md`
  - `09_soul/skills/workflow_deep_research_survey.md`
  - `designDoc/learning_library/`
  - relevant `designDoc/` architecture docs when the result may change local design

## Routing Rules

Use these top-level rules:

- if the user asks what is new, what arrived, or what should be triaged first:
  - route to `ingestion-agentmail-inbox-triage`
- if the user asks to normalize, archive, classify, promote, or convert material into reusable research objects:
  - route to `ingestion-research-archive-operator`
- if the user asks what the market traded, what confirmed, what did not confirm, or how to read a current event window:
  - route to `research-current-market-reporter`
- if the user asks whether a standing theme or theme report should be refreshed, widened, reviewed for gaps, or extended into a candidate:
  - route to `research-theme-report-owner`
- if the user asks the AI to **scan the recent archive for new theme candidates that no current theme covers** ("AI 自己进资料堆挖一下"，"看看最近资料里有什么没开成 theme 的"，"扫一遍最近的 messages 看有没有遗漏的题材"):
  - route to `research-theme-discovery-scanner` directly
  - this is **entry point #2** in the three-entry-point theme-creation map (see [`research_05 §4`](../../../designDoc/research_50_thesis_and_theme_agent_cluster.md))
  - the scanner outputs `data/research/theme_candidates/<scan_id>.json` + `<scan_id>.md` for PM review; PM then explicitly routes one candidate forward to `research-theme-report-owner` round-1 (which can later forward to `research-theme-bootstrapper` Stage A)
  - REQUIRES an explicit `as_of_utc` time anchor — if the user did not supply one, ask once before routing
  - distinguish from `research-theme-report-owner`: owner answers "given a known target theme, does it need updating?"; scanner answers "given the recent archive, are there NEW themes worth opening?"
- if the user asks for a business / financial / valuation memo, company report, fundamental analysis, public-comp read, IPO / pre-IPO read, or secondary-market surface read:
  - route to `research-company-financial-analysis`
- if the user asks what one stock or asset means now through ticker, tape, actionability, technical state, levels, watchlist status, or current price behavior:
  - route to `research-single-stock-analysis`
- if the user asks what the current book should do now:
  - route to `operation-portfolio-decision`
- if the user asks to study an external repo, paper, public skill system, product, architecture, or outside workflow so the lesson can improve this repo:
  - route to `research-external-learning`
  - this includes requests such as "把这个 skill 用在 external learning research 上", "研究这个 GitHub repo 对我们有什么用", "看这个外部 framework 值不值得借鉴"
  - distinguish from archive curation: archive work preserves or promotes incoming material under `data/research`; external learning research produces durable design judgment under `designDoc/learning_library/`
  - distinguish from theme maintenance: external learning research is about improving the platform, Hoveath, or operating model, not updating a market theme report
- if the user says "External Review", "external agent", "外部 runner", "build external agent", or "独立 + [task]" (e.g. "独立 review 一下", "独立跑一个检查", "独立做个 audit"):
  - route to `support-external-agent-builder`
  - subskill selection by action type: review → `external_review_builder.md`
  - this includes requests such as "对这个 doc 做 External Review", "用外部 agent 审一下", "独立 review 这批改动"
  - the key signal is that the task should be executed by an independent external runner surface, not in the current session
  - distinguish from `engineering-change-review`: engineering-change-review sends an exact engineering plan or exact commit to the registered engineering Reviewer on the local Agent Runtime; support-external-agent-builder assembles a prompt for an out-of-session runner (Claude Code CLI, DeepSeek, OpenAI, etc.)
  - distinguish from `research-external-learning`: external-learning studies outside systems to improve this repo; external-agent-builder builds a runner to execute a task through an outside AI surface
- if the user asks to independently research a company, crypto project, or asset from scratch (assemble sources, build source packet, produce dossier or decision brief):
  - route to `digestion-independent-researcher`
  - this includes requests such as "帮我查一下这家公司的资料", "做个 independent research", "从头研究一下 X"
  - distinguish from `research-company-financial-analysis`: independent researcher assembles upstream Digestion artifacts (source packet, source cards, dossier); company financial analysis writes the PM-facing report from those artifacts
  - distinguish from archive curation: archive operator normalizes already-received material; independent researcher actively assembles new material from local + external sources
- if the user asks to review an engineering plan before implementation, or engineering commits, charter-alignment changes, schema changes, or skill cluster work that has already landed:
  - route to `engineering-change-review`
  - this includes requests such as "review 一下这批 commits", "看看这几个改动有没有问题", "engineering review"
  - distinguish from `support-external-agent-builder`: engineering-change-review reviews the exact plan or exact commit through the registered Reviewer on the local Agent Runtime; external-agent-builder assembles a prompt for an external runner
- if the user asks to compact the current session, generate a handoff note, or prepare to continue in a new chat:
  - route to `support-compaction-handoff`
  - this includes requests such as "compact", "session handoff", "帮我生成一个 handoff note"

## Real Route Cases

Use these as current concrete examples from the repo's actual working surface:

- “今天有什么新东西”:
  - `matched_mainline = inbox / mail triage`
  - `downstream_skill = ingestion-agentmail-inbox-triage`
- “把这批新材料整理进 archive”:
  - `matched_mainline = archive curation / message promotion`
  - `downstream_skill = ingestion-research-archive-operator`
- “今天市场到底在交易什么”:
  - `matched_mainline = market recap / market observation`
  - `downstream_skill = research-current-market-reporter`
- “从 Iran/Hormuz 这条线看今天收盘”:
  - `matched_mainline = market recap / market observation`
  - `downstream_skill = research-current-market-reporter`
  - `overlay_needed = none`, because the theme is already the mainline rather than a secondary overlay
- “这个 theme 要不要更新”:
  - `matched_mainline = theme update / theme report maintenance`
  - `downstream_skill = research-theme-report-owner`
- “总结下最近的 news，针对这个 report 看看有什么新变化”:
  - `matched_mainline = theme update / theme report maintenance`
  - `downstream_skill = research-theme-report-owner`
  - likely owner pass types later include `report_delta_scan` or `report_gap_review`
- “帮我扫一下最近两周的 messages 看看有没有应该开成 theme 的新东西”:
  - `matched_mainline = theme discovery (AI bottom-up)`
  - `downstream_skill = research-theme-discovery-scanner`
  - require explicit `as_of_utc` from user; default `time_window = last 14 days`
- “请帮我开一个 theme on <X>” / “我想新开一条 theme”:
  - `matched_mainline = theme update / theme report maintenance`
  - `downstream_skill = research-theme-report-owner` (round-1 first; owner decides whether to forward to `research-theme-bootstrapper` Stage A)
  - this is **entry point #1** (PM-driven new theme); router does NOT call `research-theme-bootstrapper` directly
- “分析一下 ORCL”:
  - `matched_mainline = single-stock analysis`
  - `downstream_skill = research-single-stock-analysis`
- “写一份 ORCL 的 financial analysis / company report / valuation memo”:
  - `matched_mainline = company financial analysis`
  - `downstream_skill = research-company-financial-analysis`
- “Databricks 这种 private company 写成 PM report”:
  - `matched_mainline = company financial analysis`
  - `downstream_skill = research-company-financial-analysis`
- “先看 Databricks 基本面，再看如果有可交易 ticker 怎么处理”:
  - `matched_mainline = company financial analysis first`
  - `downstream_skill = research-company-financial-analysis`
  - `next_handoff = research-single-stock-analysis or operation-portfolio-decision only after the company read is stable`
- “结合 theme overlay 看一下这只股票”:
  - `matched_mainline = single-stock analysis`
  - `downstream_skill = research-single-stock-analysis`
  - `overlay_needed = theme`
- “我现在该怎么调仓”:
  - `matched_mainline = portfolio decision`
  - `downstream_skill = operation-portfolio-decision`
- “当前最大风险先 hedge 什么”:
  - `matched_mainline = portfolio decision`
  - `downstream_skill = operation-portfolio-decision`
  - likely portfolio pass type later includes `hedge_priority`
- “先做一个 portfolio debate”:
  - `matched_mainline = portfolio decision`
  - `downstream_skill = operation-portfolio-decision`
- “研究一下这个 GitHub repo，对我们的 trading platform 有什么可以借鉴”:
  - `matched_mainline = external learning research`
  - `downstream_skill = research-external-learning`
  - `primary_truth_surface = external source + 09_soul/axioms + designDoc/learning_library`
- “把这套外部 skill 方法用到我们的 external learning research 里”:
  - `matched_mainline = external learning research`
  - `downstream_skill = research-external-learning`
  - `overlay_needed = none`, because this is a platform-learning workflow rather than market-theme work
- “对 Research 30 做 External Review”:
  - `matched_mainline = external agent build`
  - `downstream_skill = support-external-agent-builder`
  - subskill = `external_review_builder.md`
  - target artifact = `designDoc/research_30_company_report_instruction.md`
- “独立 review 一下这批 skill 改动”:
  - `matched_mainline = external agent build`
  - `downstream_skill = support-external-agent-builder`
  - subskill = `external_review_builder.md`
- “帮我从头研究一下 Databricks”:
  - `matched_mainline = independent research`
  - `downstream_skill = digestion-independent-researcher`
- “review 一下这批 commits”:
  - `matched_mainline = engineering review`
  - `downstream_skill = engineering-change-review`
- “compact” / “session handoff”:
  - `matched_mainline = session support`
  - `downstream_skill = support-compaction-handoff`
- “review this package before writing”:
  - this is not a new top-level mainline by default
  - keep the owning mainline and send the package through `writer-handoff` as a downstream package review gate

## Overlay Rule

Do not confuse overlay context with first authority.

Examples:

- a single-stock request may still need one macro theme as overlay, but the request remains `research-single-stock-analysis`
- a operation-portfolio-decision request may still need one leading macro theme as overlay, but the request remains `operation-portfolio-decision`
- a theme mention inside a portfolio or stock question does not automatically move the whole request into theme maintenance

When macro overlay is needed:

- keep the current mainline
- note `overlay_needed = theme`
- then let `routing-current-macro-priority-router` choose the leading macro branch inside that overlay step

Package-review rule:

- if the request is only about whether an already-built package is ready for prose, do not re-route the whole task into theme maintenance or portfolio decision again
- keep the current owning mainline and use `writer-handoff` as the downstream package review gate

## What This Skill Must Not Do

- do not decide internal macro theme priority ranking
- do not decide report pass type inside theme maintenance
- do not decide package sufficiency
- do not decide writer structure or article prose
- do not absorb downstream domain work just because the front-door choice was ambiguous

## Failure Signals

Treat these as signs this skill failed:

- a theme mention silently turns the task into theme maintenance
- a ticker mention silently turns the task into single-stock analysis when the real ask is about company business / financial analysis or about the book
- a portfolio/account mention silently turns the task into portfolio decision when the real ask is still first-pass market interpretation
- an external repo or paper is treated as generic archive material when the user is asking for platform-learning judgment
- an external-learning request produces a neutral web summary without applying the user's axioms, local architecture context, and style contract
- "External Review" or "独立 + task" is handled ad-hoc in-session instead of routing to `support-external-agent-builder`
- an independent research request is confused with archive curation or company financial analysis
- an engineering review request is confused with external-agent-builder
- package paths, report files, or writer surfaces are used as the main signal for task mode
- the router emits a macro branch but never states which top-level mainline owns the request

## Preferred Output Shape

- `Task mode`
- `First authority`
- `Primary truth surface`
- `Downstream skill`
- `Optional overlay`
- `Why this route wins`

## Example Triggers

- “今天有什么新东西”
- “把这批新材料整理进 archive”
- “今天市场到底在交易什么”
- “这个 theme 要不要更新”
- “分析一下 ORCL”
- “我现在该怎么调仓”
- “研究这个外部 repo / paper / workflow，对我们有什么用”
- “对这个 doc 做 External Review”
- “独立 review 一下这批改动”
- “帮我从头研究一下 X 公司”
- “review 一下这几个 commits”
- “compact” / “session handoff”
