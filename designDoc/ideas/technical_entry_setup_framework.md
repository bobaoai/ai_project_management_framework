# Technical Entry Setup Framework

**Status:** idea proposal  
**Date:** 2026-03-31  
**Purpose:** extend the current `technical_framework` and `asset technical` pipeline so the system can identify higher-quality entry opportunities, not just describe current trend structure.

## 1. Why This Upgrade Is Needed

The repo already has useful technical building blocks:

- `technical_framework` for trend, risk, add zones, and reentry conditions
- deterministic signal packets for `EMA`, `RSI`, support/resistance, and multiweek state
- AI-written technical summaries for PM-facing daily reads

What it still lacks is a reusable object that answers:

- what kind of entry is available right now
- whether the market regime is compatible with that entry
- where the actual trigger is
- where the trade is wrong
- which targets define acceptable reward
- whether this setup type has historically worked well

Without that layer, the system can describe charts but cannot yet express a repeatable `high-quality entry playbook`.

## 2. Design Goal

This extension should make the technical layer capable of producing:

- current candidate entry setups
- setup quality grading
- explicit trigger, invalidation, and target structure
- later win-rate evaluation by setup family and regime

The system should move from:

- `technical state description`

to:

- `technical state description + executable setup object`

## 3. Core Boundary

This design must preserve the current split:

- deterministic code owns price math, setup detection, trigger logic, and result tracking
- AI owns weighting, judgment, and PM-facing prose

That means:

- code should decide whether a `pullback_in_uptrend` setup is present
- code should record whether a triggered setup later hit stop or target first
- AI may explain whether the setup is worth acting on today
- AI should not invent historical win rate without tracked outcomes

## 4. Key Principle

Do not treat `high win rate` as a subjective adjective.

Instead, split it into two layers:

### 4.1 Current setup quality

A deterministic or semi-structured judgment about whether the present chart offers:

- trend alignment
- nearby support or resistance clarity
- clean invalidation
- acceptable reward-to-risk
- confirmation from regime state

This can be expressed as:

- `setup_quality`: `A`, `B`, `C`, `avoid`
- `quality_reasons`: list of the structural reasons

### 4.2 Observed historical effectiveness

A tracked performance view of similar setup types over time:

- hit rate to first target
- stop-first rate
- average forward return after `5d`, `10d`, `20d`
- effectiveness by setup family
- effectiveness by asset family
- effectiveness by regime

This is the layer that earns the words `high win rate`.

## 5. Proposed New Objects

### 5.1 `entry_setups`

Add a new object under the current asset-level technical read.

Recommended role:

- hold current candidate setups for the asset as of one date
- allow multiple setup types at once
- keep structure explicit even if no setup is active

Suggested shape:

```json
{
  "entry_setups": [
    {
      "setup_id": "RTX_2026-03-31_pullback_in_uptrend_01",
      "setup_type": "pullback_in_uptrend",
      "status": "watching",
      "timeframe": "1d",
      "direction": "long",
      "regime_gate": {
        "trend_state": "bullish_trend",
        "multiweek_state": "uptrend"
      },
      "entry_zone": {
        "zone_low": 185.5,
        "zone_high": 188.0
      },
      "trigger_condition": "pullback_holds_support_and_closes_back_above_prior_day_high",
      "invalidation": {
        "type": "daily_close_below_level",
        "level": 182.9
      },
      "targets": [
        {
          "level": 197.0,
          "label": "target_1"
        },
        {
          "level": 214.5,
          "label": "target_2"
        }
      ],
      "reward_risk_ratio_estimate": 2.1,
      "setup_quality": "A",
      "quality_reasons": [
        "trend_aligned",
        "support_nearby",
        "clear_invalidation"
      ],
      "notes": "Prefer action only after reclaim confirmation."
    }
  ]
}
```

### 5.2 `setup_catalog`

The system should maintain a small canonical setup taxonomy instead of allowing ad hoc labels.

Suggested initial families:

- `pullback_in_uptrend`
- `breakout_from_compression`
- `reclaim_after_failed_breakdown`
- `range_low_reversal`
- `fib_retrace_to_key_level`

Optional later families:

- `base_breakout`
- `trend_resume_after_ema_reclaim`
- `failed_breakout_short`
- `range_high_rejection_short`

### 5.3 `entry_outcome_log`

To evaluate win rate, the repo eventually needs a tracked result surface.

Suggested role:

- record when a setup moved from `watching` to `triggered`
- record entry, stop, and targets
- record first outcome path
- record forward returns

Suggested shape:

```json
{
  "setup_id": "RTX_2026-03-31_pullback_in_uptrend_01",
  "asset_id": "RTX",
  "setup_type": "pullback_in_uptrend",
  "trigger_date": "2026-04-02",
  "entry_price": 188.4,
  "stop_level": 182.9,
  "target_1": 197.0,
  "target_2": 214.5,
  "first_resolution": "target_1_first",
  "max_favorable_excursion_pct": 6.7,
  "max_adverse_excursion_pct": -2.1,
  "forward_return_5d": 3.2,
  "forward_return_10d": 5.8,
  "forward_return_20d": 4.4
}
```

## 6. Where These Objects Should Live

### 6.1 Current deterministic packet

`signal_packets/*.json` should be the first host surface for:

- current `entry_setups`
- setup status such as `watching`, `triggered`, `invalid`, `expired`
- trigger and invalidation fields

This keeps the current daily technical packet as the canonical present-state object.

### 6.2 Index layer

`data/knowledge/asset_technicals/index.json` can later project only compact setup fields:

- `active_setup_count`
- `top_setup_type`
- `top_setup_quality`
- `top_setup_direction`
- `top_setup_trigger`
- `top_setup_invalidation`

This allows screening without reading every packet.

### 6.3 Historical evaluation layer

Historical setup results should not overload the current packet.

Recommended later path:

- `data/knowledge/asset_technicals/setup_outcomes/`
- or a future database table if the technical layer moves into Postgres

## 7. Canonical Contract Layers

This upgrade should use two distinct contracts rather than one oversized prompt blob.

### 7.1 Canonical storage contract

The first contract is the durable asset-level technical object.

Recommended host:

- `data/knowledge/asset_technicals/signal_packets/*.json`

Recommended role:

- store the deterministic current-state truth
- give downstream index builders and package assemblers one stable source
- remain asset-generic rather than theme-specific

### 7.2 Prompt projection contract

The second contract is a compressed view derived from the canonical packet.

Recommended host:

- built during package assembly
- embedded into theme writer packages as a structured technical appendix

Recommended role:

- give the writer or analysis agent only the fields needed for judgment
- keep prompt size smaller than the full packet
- avoid forcing the agent to rediscover the setup from raw technical data

Working rule:

- the agent should consume `technical_setup_projection`
- the system should persist truth in `signal_packet`

## 8. Proposed `signal_packet` Extension

The current packet already carries trend and level context.

This proposal extends it with a setup layer while preserving the existing fields.

Suggested top-level additions:

- `entry_setups`
- `top_setup_summary`
- `fib_context`
- `confluence_references`
- `volume_confirmation`
- `price_context.weekly_1y`
- `price_context.daily_3m`

Recommended minimal shape:

```json
{
  "report_id": "listed_orcl",
  "asset_id": "ORCL",
  "report_date": "2026-04-01",
  "data_status": "ok",
  "signal_labels": {
    "trend_state": "bearish_trend",
    "swing_state": "range",
    "multiweek_state": "range"
  },
  "daily": {
    "ohlcv": {
      "date": "2026-03-31",
      "close": 147.11
    },
    "ema": {
      "10": 146.58,
      "20": 149.15,
      "50": 159.33
    },
    "short_support": 136.95,
    "short_resistance": 171.76,
    "rsi_14": 45.89
  },
  "multiweek": {
    "state": "range",
    "breakout_trigger": 171.76,
    "breakdown_trigger": 136.95,
    "upside_target_candidate": 206.57,
    "downside_target_candidate": 102.14
  },
  "entry_setups": [
    {
      "setup_id": "ORCL_2026-04-01_range_low_reversal_01",
      "setup_type": "range_low_reversal",
      "status": "watching",
      "timeframe": "1d",
      "direction": "long",
      "regime_gate": {
        "trend_state": "bearish_trend",
        "multiweek_state": "range"
      },
      "entry_zone": {
        "zone_low": 137.0,
        "zone_high": 147.5
      },
      "trigger_condition": "daily_close_back_above_ema20",
      "invalidation": {
        "type": "daily_close_below_level",
        "level": 136.95
      },
      "targets": [
        {
          "label": "target_1",
          "level": 159.33
        },
        {
          "label": "target_2",
          "level": 171.76
        }
      ],
      "reward_risk_ratio_estimate": 1.8,
      "setup_quality": "B",
      "quality_reasons": [
        "range_support_nearby",
        "repair_not_confirmed",
        "clear_invalidation"
      ],
      "confluence_references": [
        "short_support",
        "range_low",
        "ema20_reclaim_needed"
      ],
      "notes": "Watching only until reclaim confirmation."
    }
  ],
  "top_setup_summary": {
    "setup_id": "ORCL_2026-04-01_range_low_reversal_01",
    "setup_type": "range_low_reversal",
    "status": "watching",
    "setup_quality": "B",
    "one_line": "Possible repair from range support, but not actionable before reclaim."
  },
  "fib_context": {
    "is_applicable": false,
    "reason": "no_canonical_impulse_leg_selected"
  },
  "volume_confirmation": {
    "is_available": false,
    "status": "not_yet_modeled"
  }
}
```

Field notes:

- `entry_setups` is the full current tactical object list
- `top_setup_summary` is a compressed screening layer
- `fib_context` should exist even when fib is not applicable
- `confluence_references` should point to deterministic anchors already present in the packet
- `volume_confirmation` should stay explicit rather than implied by prose
- `price_context.weekly_1y` gives the agent one year of weekly close structure
- `price_context.daily_3m` gives the agent three months of daily close and indicator context

## 9. Proposed `technical_setup_projection`

This is the contract that package builders should feed to the writer or analysis agent.

Recommended host:

- generated during `build_theme_writer_package.py`
- inserted into the theme package as structured JSON or compact markdown

Recommended role:

- compress packet complexity
- preserve the most important setup logic
- make prompt assembly asset-generic

Suggested shape:

```json
{
  "asset_id": "ORCL",
  "display_name": "ORCL",
  "report_date": "2026-04-01",
  "data_status": "ok",
  "theme_tags": [
    "ai-datacenter-power-and-balance-of-plant"
  ],
  "technical_state": {
    "trend_state": "bearish_trend",
    "swing_state": "range",
    "multiweek_state": "range",
    "daily_move_state": "flat_day"
  },
  "key_levels": {
    "close": 147.11,
    "ema_10": 146.58,
    "ema_20": 149.15,
    "ema_50": 159.33,
    "support": 136.95,
    "resistance": 171.76,
    "breakout_trigger": 171.76,
    "breakdown_trigger": 136.95
  },
  "top_setup_summary": {
    "setup_type": "range_low_reversal",
    "status": "watching",
    "setup_quality": "B",
    "trigger_condition": "daily_close_back_above_ema20",
    "invalidation_level": 136.95,
    "target_1": 159.33,
    "target_2": 171.76,
    "one_line": "Watching for repair confirmation from range support."
  },
  "entry_setups": [
    {
      "setup_type": "range_low_reversal",
      "status": "watching",
      "setup_quality": "B",
      "trigger_condition": "daily_close_back_above_ema20",
      "invalidation_level": 136.95,
      "confluence_references": [
        "short_support",
        "range_low"
      ]
    }
  ],
  "fib_context": {
    "is_applicable": false,
    "reason": "no_canonical_impulse_leg_selected"
  },
  "prompt_focus": {
    "ask_agent_to_decide": [
      "is there a real setup or only weak repair",
      "what exact condition upgrades watching to actionable",
      "does the technical structure confirm or drag on the theme expression"
    ],
    "forbid": [
      "inventing new price levels",
      "claiming historical win rate without tracked outcomes"
    ]
  }
}
```

Keep this projection smaller than the full packet.

The projection should be:

- enough for agent judgment
- not a replacement for the canonical packet
- consistent across all assets

## 10. Package Integration Path

The current repo already has the right assembly surface in `build_theme_writer_package.py`.

Recommended integration path:

1. `asset_technical_runtime.py` computes current setup fields into `signal_packet`
2. `build_asset_technical_index.py` projects only the top setup screening fields into the index
3. `build_theme_writer_package.py` reads the packet and current report for each relevant asset
4. `build_theme_writer_package.py` emits one `technical_setup_projection` per asset into the package
5. the writer or analysis agent consumes the projection instead of reverse-engineering the raw packet

This keeps:

- packet as truth
- package as assembly surface
- agent as judgment layer

## 11. Setup Detection Model

The detection model should stay simple at first.

### 11.1 `pullback_in_uptrend`

Use when:

- daily `trend_state` is bullish
- multiweek state is not bearish
- price pulls back toward `EMA20`, `EMA50`, or prior breakout support
- invalidation is close and obvious

Why it matters:

- this is usually the cleanest long entry type for trend-following assets

### 11.2 `breakout_from_compression`

Use when:

- multiweek state is `compression` or tight `range`
- price is near the upper boundary
- breakout trigger and measured-move target are both clear

Why it matters:

- this captures trend birth rather than trend continuation

### 11.3 `reclaim_after_failed_breakdown`

Use when:

- price loses support
- quickly reclaims the broken level
- closing behavior suggests breakdown failure instead of true trend damage

Why it matters:

- failed moves can create sharp reversals with good asymmetric entry

### 11.4 `range_low_reversal`

Use when:

- multiweek state is range
- price is near range low
- downside invalidation is tight
- reversal trigger is explicit

Why it matters:

- it gives the system a non-trend entry family without forcing breakout-only logic

### 11.5 `fib_retrace_to_key_level`

Use when:

- the asset has a clean prior impulse leg worth measuring
- retracement lands near a meaningful `Fib` level such as `0.382`, `0.5`, or `0.618`
- the `Fib` level overlaps with another structural reference such as `EMA20`, `EMA50`, prior breakout level, horizontal support, or range boundary
- invalidation is still close enough to keep reward-to-risk attractive

Why it matters:

- many assets do not reverse at a `Fib` level alone, but retracement confluence with existing structure can create a high-attention entry zone

Guardrail:

- do not treat standalone `Fib` levels as sufficient evidence
- prefer `Fib` only when it overlaps with already-supported deterministic structure
- if the prior impulse leg is ambiguous, do not emit this setup

## 12. Quality Grading Framework

Before historical win-rate tracking is mature, the system still needs a current ranking rule.

Suggested inputs:

- `trend_alignment_score`
- `support_clarity_score`
- `trigger_clarity_score`
- `reward_risk_score`
- `regime_confirmation_score`
- `distance_to_invalidation_score`

Suggested output:

- `A`: strong alignment and clear asymmetric structure
- `B`: decent setup but missing one confirmation
- `C`: tradable only with caution or smaller size
- `avoid`: structurally messy or no clear edge

The grade should stay interpretable. Avoid opaque composite scores at first.

## 13. Relationship To Existing `technical_framework`

This upgrade should extend the current object model rather than replace it.

Recommended relationship:

- `technical_framework` stays the durable execution schema
- `entry_setups` becomes the current tactical expression surface

Working split:

- `risk_levels`, `take_profit_levels`, `add_zones`, `reentry_condition` remain the durable framework
- `entry_setups` expresses whether the chart is currently offering an actionable opportunity

In other words:

- `technical_framework` says how the asset should generally be managed
- `entry_setups` says what the best current entry pattern is, if any

## 14. Proposed Profile Extensions

Per-asset profiles may later need a lightweight extension to guide setup detection.

Possible additions:

- `preferred_setup_types`
- `avoid_setup_types`
- `preferred_support_reference`
- `preferred_trigger_style`
- `minimum_reward_risk_ratio`
- `fib_leg_anchor_style`
- `preferred_fib_levels`

This would let some assets emphasize:

- trend pullbacks
- tight ranges
- breakout continuation
- mean-reversion entries
- retracement-confluence entries

without forcing one setup logic across every asset.

## 15. Win-Rate Evaluation Rules

To avoid fake precision, the first evaluation pass should be modest.

Recommended first metrics:

- `target_1_hit_rate`
- `stop_hit_rate`
- `target_1_before_stop_rate`
- median `forward_return_10d`
- sample count

Recommended grouping dimensions:

- by `setup_type`
- by `asset_type`
- by `theme-linked basket`
- by top-level regime such as `uptrend`, `range`, `downtrend`

Guardrails:

- do not display strong win-rate claims on tiny sample sizes
- always show sample count
- separate current setup quality from historical hit statistics

## 16. Suggested Implementation Order

### Phase 1: current setup object only

- add `entry_setups` to deterministic signal packets
- implement the first five setup families
- expose one top setup in the total index
- let AI summaries mention setup quality and trigger logic

### Phase 2: triggered setup tracking

- persist setup transitions from `watching` to `triggered`
- record stop and target levels at trigger time
- capture forward returns

### Phase 3: setup analytics

- build aggregated hit-rate views by setup family and regime
- expose sample-aware setup statistics to dashboards and reports

### Phase 4: PM workflow integration

- allow package builders and PM tools to surface `best current entries`
- connect setup quality to opportunity ranking and position sizing discussions

## 17. Immediate Low-Risk Version

If the repo wants a minimal first step, do only this:

1. add `entry_setups` to current signal packets
2. keep only `watching` setups, not full outcome logging yet
3. support only five setup types
4. rank them with `A/B/C/avoid`

This would already make the technical layer much more actionable without requiring a full backtest or heavy data model migration.

## 18. Promotion Criteria

This doc should stay in `designDoc/ideas/` until the repo has:

- a stable `entry_setups` object shape
- at least one canonical persistence path for setup outcomes
- a decision on whether historical evaluation belongs in files or database tables

Once those are stable, the durable parts should be promoted into:

- `research_20_technical_framework_v0_1.md`
- `modules/asset_technical_signal_pipeline.md`
- relevant runtime or schema docs
