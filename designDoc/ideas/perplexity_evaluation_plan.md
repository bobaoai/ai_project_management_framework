# Perplexity Evaluation Plan

## Goal

Choose the default external-validation method for theme report writing with the smallest request budget that still returns enough public facts and citations.

## Theme Anchor

Use `iran-hormuz-escalation` as the anchor report because it contains three different external-validation needs:

1. price action verification
2. headline timeline verification
3. public-market mechanism confirmation

## APIs Under Test

1. `Search API`
2. `Agent API` with `fast-search`
3. `Agent API` with `pro-search`

## Evaluation Questions

### Q1 Price Action

Verify whether public sources can confirm the report's dated market anchors between `2026-03-20` and `2026-03-24`:

- `Brent`
- `WTI`
- `2Y Treasury`

### Q2 Headline Timeline

Verify whether public sources can reconstruct the event sequence around Iran / Hormuz escalation during the same window.

### Q3 Mechanism Confirmation

Test whether public sources can support the report's broader market mechanism:

- oil shock repricing rates
- crowded hedge / stagflation positioning
- system damaged but short-end funding not broken

This should be expected to be harder than Q1 and Q2 because some of the mechanism may live more in internal archive material than in public news reporting.

## Controls

- Keep the time window fixed per question.
- Keep preferred domains fixed where possible.
- Ask for dated facts and citations, not broad narrative summaries.
- For Agent API tests, set `max_steps=1` first to minimize spend.

## Metrics

Score each run on a 1-5 scale:

1. factual coverage
2. citation quality
3. date-window discipline
4. usefulness for direct report writing
5. noise level

Track cost separately:

- `Search API`: estimated fixed request cost
- `Agent API`: actual `usage.cost.total_cost` from the response when available

## Success Criteria

- If `Search API` captures most key facts with usable citations, it becomes the default validation layer.
- If `Agent fast-search` materially improves write-ready output at modest cost, it becomes the default "one-call summary" option.
- If `Agent pro-search` only marginally improves results relative to `fast-search`, reserve it for exceptional cases.

## First Round Budget

Run only one pass per API per question:

- 3 questions
- 3 methods
- total = 9 requests

This is enough to decide the default workflow without overpaying for early experimentation.
