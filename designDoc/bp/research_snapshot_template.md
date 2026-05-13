# Research Snapshot Template

Canonical runtime paths:

- `data/research/snapshots/<snapshot_id>.json`
- `data/research/snapshots/<snapshot_id>.md`
- `data/research/snapshots_index.jsonl`

Use this object for short-form research cards, not for full reports.

## When To Use

- one fact that matters
- one chart or table worth saving
- one market move with a clear implication
- one incremental interpretation that should feed a theme later

## Suggested JSON Shape

```json
{
  "snapshot_id": "snapshot_agentmail_20250710_money-market-liquidity-shift_01",
  "snapshot_type": "evidence_snapshot",
  "title": "Money-market update shows front-end liquidity preference remains dominant",
  "created_at": "2026-03-24T22:00:00Z",
  "updated_at": "2026-03-24T22:00:00Z",
  "source_research_ids": [
    "agentmail_20250710T012045Z_money-market-update_7b495892df"
  ],
  "source_message_ids": [
    "agentmail_20250710T012045Z_money-market-update_7b495892df"
  ],
  "theme_tags": [
    "rates",
    "liquidity",
    "money-markets"
  ],
  "related_tickers": [
    "BIL",
    "SHY"
  ],
  "related_assets": [
    "UST 2Y",
    "T-bills"
  ],
  "time_horizon": "tactical",
  "signal_type": "liquidity_preference",
  "what_happened": "The source highlights continued preference for front-end liquidity instruments over duration extension.",
  "why_it_matters": "This supports the view that risk appetite remains selective and that cash-like instruments still anchor portfolio positioning.",
  "key_numbers": [
    "3m bill yield near local highs",
    "front-end demand remains firm"
  ],
  "evidence_refs": [
    "content.md#Cleaned Body",
    "image_reviews.jsonl:image_abc123"
  ],
  "change_vs_prior": "Reinforces the prior liquidity-first view rather than changing the core thesis.",
  "interpretation": "Useful as supporting evidence for rates and liquidity themes, but not enough on its own to create a new thesis note.",
  "novelty": "medium",
  "actionability": "watch",
  "confidence": 0.72,
  "stance": "framework",
  "status": "active",
  "notes": "Keep linked to the rates theme draft until a broader duration rotation is confirmed.",
  "metadata": {
    "authoring_mode": "agent_assisted",
    "snapshot_origin": "agentmail_newsletter"
  }
}
```

## Writing Rule

Each snapshot should answer five questions:

1. What happened?
2. Why does it matter?
3. What evidence supports it?
4. Which theme or assets does it affect?
5. Does it change the prior view, or just reinforce it?

## Quick Markdown Shape

```md
# <snapshot title>

## What Happened
<1-3 sentences>

## Why It Matters
<1-3 sentences>

## Key Numbers
- <number or metric>

## Evidence Refs
- <research_id / image_id / section>

## Change Vs Prior
<what changed, or "reinforces prior view">

## Interpretation
<short investment interpretation>

## Notes
<optional>
```
