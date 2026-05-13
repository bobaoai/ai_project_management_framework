# Market Update Snapshot Template

Canonical runtime paths remain:

- `data/research/snapshots/<snapshot_id>.json`
- `data/research/snapshots/<snapshot_id>.md`
- `data/research/snapshots_index.jsonl`

Use this template for cross-theme intraday or end-of-day market updates that should stay separate from:

- `themes/reports/`
- `theme_update_drafts/`
- `thesis_notes/`

This is still a `snapshot` template, not a new research layer.

## When To Use

- one trading session creates a meaningful cross-asset change
- one event changes the market read-through across multiple themes
- you want a reusable market note before deciding which theme reports to update
- the move is important, but not yet a reviewed theme rewrite

## When Not To Use

- a full theme judgment belongs in `theme_update_drafts/`
- a durable approved conclusion belongs in `thesis_notes/`
- a single isolated fact with no broader read-through can use the simpler `research_snapshot_template.md`

## Writing Rules

Each market update snapshot should stay focused on one market window and answer seven questions:

1. What changed in the market today?
2. What was the catalyst?
3. What is the macro read-through, not just the price action?
4. Which assets confirmed the move, and which assets did not?
5. Which themes does this affect?
6. Does it change the prior view, or mainly validate an existing path?
7. What should be watched next session to confirm or reject the read?

Mixed Chinese-English writing is acceptable and often preferred in this workspace when it makes market shorthand clearer. Keep the structure stable, but feel free to write fields like `Core Read`, `Change Vs Prior`, or `Next Watch` in natural zh-en mixed prose.

## Suggested JSON Shape

```json
{
  "snapshot_id": "snapshot_live_20260325_iran-hormuz-partial-repair",
  "snapshot_type": "evidence_snapshot",
  "title": "Iran/Hormuz market update: oil war premium unwinds but shipping stress remains",
  "created_at": "2026-03-25T20:30:00Z",
  "updated_at": "2026-03-25T20:30:00Z",
  "source_research_ids": [
    "external_reuters_20260325_iran_war_fx",
    "external_cnbc_20260325_iran_oil_market"
  ],
  "source_message_ids": [],
  "theme_tags": [
    "iran-hormuz-escalation",
    "usd-liquidity-plumbing",
    "japan-policy-normalization"
  ],
  "related_tickers": [
    "USO",
    "XLE",
    "QQQ",
    "GLD"
  ],
  "related_assets": [
    "Brent",
    "WTI",
    "DXY",
    "UST 2Y",
    "VIX"
  ],
  "time_horizon": "tactical",
  "signal_type": "cross_asset_market_update",
  "what_happened": "Oil fell sharply on negotiation headlines while equities bounced, but volatility, gold, and the dollar did not fully unwind.",
  "why_it_matters": "The session looks more like a partial repair and hedge unwind than a full normalization of geopolitical risk.",
  "macro_context": "Macro-wise this is a relief move, not a clean regime reset: inflation-risk pressure eased at the margin, but funding, FX hedge demand, and physical shipping disruption still argue against declaring the shock over.",
  "key_numbers": [
    "Brent near 100",
    "WTI near 89",
    "VIX still elevated near high-20s"
  ],
  "evidence_refs": [
    "Reuters: Traders bet $500 million on oil price just before Trump's post on delay to Iran attack",
    "Reuters: Currencies pause amid uncertainty over U.S. efforts to end Iran war",
    "CNBC: Oil price: WTI, Brent fall as Trump signals Iran talks despite Tehran denial"
  ],
  "change_vs_prior": "Validates the report's partial-repair path more than it overturns the broader damage-already-done thesis.",
  "interpretation": "Good evidence that crowded hedges can unwind fast on softer headlines, but not enough to conclude that physical disruption or macro damage has cleared.",
  "novelty": "medium",
  "actionability": "watch",
  "confidence": 0.78,
  "stance": "framework",
  "status": "active",
  "notes": "Useful as a shared daily market note feeding multiple themes before any report-level edits.",
  "metadata": {
    "authoring_mode": "agent_assisted",
    "snapshot_origin": "live_market_update",
    "market_window": "2026-03-25_us_session"
  }
}
```

## Quick Markdown Shape

```md
# <market update title>

## Market Window
<date / session / region>

## Core Read
<state the main market interpretation directly; use the space you need>

## What Changed
- <cross-asset move 1>
- <cross-asset move 2>
- <cross-asset move 3>

## Catalyst
<headline, data release, policy signal, or flow explanation>

## Macro Context
<say the macro transmission path clearly and fully; cover regime, policy, funding, growth, inflation, or FX linkage as needed>

## Confirmations
- <asset or market that supports the read>
- <asset or market that also moved in the same direction>

## Non-Confirmations
- <asset that did not confirm a full regime shift>
- <remaining sign of stress or ambiguity>

## Affected Themes
- `<theme-id>`: <how this update matters>
- `<theme-id>`: <how this update matters>

## Change Vs Prior
<does this revise the prior view, narrow the path, or simply reinforce it?>

## Next Watch
- <level, asset, or condition to monitor next>
- <second confirmation or failure condition>

## Evidence Refs
- <source 1>
- <source 2>
- <source 3>
```

## Practical Guidance

- Keep one snapshot to one coherent market window.
- Cross-theme is fine; cross-regime is not. If the note mixes unrelated stories, split it.
- Use `Affected Themes` to fan the evidence out later instead of forcing the same prose into multiple reports.
- If the update accumulates enough evidence for one theme, promote it into `theme_update_drafts/` rather than expanding the snapshot indefinitely.
- Prefer concise market shorthand over forced full translation; examples like `partial repair`, `hedge unwind`, `non-confirmation`, and `tail risk` can stay in English inside Chinese sentences.
- Every market update should include a macro paragraph, even when the trigger is very event-driven. The note is not complete until it says what the move means for growth, inflation, rates, funding, FX, or regime pricing.
- Do not optimize for a sentence count. Optimize for saying the important thing cleanly and completely.
