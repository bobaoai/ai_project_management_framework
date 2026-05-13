# Cross-Source Theme Candidates

This note is a non-canonical backlog for themes that can be mined across different research sources.

It is meant to answer one practical question:

- which recurring ideas are already strong enough to be `approved themes`
- which ones already have a serious `draft`
- which ones should stay as `industry specific beta themes`
- which ones are only `thesis / snapshot` material for now

## Status Legend

- `approved`: already represented in generated routing views under `data/research/themes/`
- `draft_candidate`: already has a substantial local draft or candidate report surface, but is not yet promoted into the routing index
- `candidate`: recurring enough across sources to deserve continued development
- `thesis_only`: useful lens, but still too narrow or too single-name to become a top-level theme

## Source Map

### `capitalflows`

Best at:

- macro regime
- rates / FX / liquidity
- geopolitical shock transmission
- cross-asset positioning
- AI and software rotation through the equity-macro lens

Most useful for theme mining:

- `war shock -> oil / rates / gold / USD / risk-off`
- `gold / monetary fragmentation`
- `USD liquidity plumbing`
- `software vs infra / AI profit-pool rotation`

### `conks`

Best at:

- money markets
- reserve scarcity
- repo / RRP / TGA / SOFR plumbing
- Fed funding transmission

Most useful for theme mining:

- `USD liquidity plumbing`
- `shadow liquidity and funding stress`

### `tmt_breakout`

Best at:

- software vs semis relative performance
- earnings and buyside bogey framing
- AI infra broadening beyond the most crowded names
- optical / memory / networking / server chain

Most useful for theme mining:

- `AI application-layer rerating`
- `AI infrastructure bottlenecks beyond GPU`
- `custom silicon and memory profit-pool shift`

### `citrini`

Best at:

- deep thematic framing
- industry architecture
- industrial buildout logic
- power / optics / modern warfare / single-stock field research

Most useful for theme mining:

- `AI industrial buildout`
- `power and optics`
- `modern warfare / defense-electronics`
- `single-stock deep research clusters`

Important boundary:

- `citrini` deep research can often seed a theme
- `citrini index / thread / administrative routing` should usually stay snapshot-first
- many `single-stock deep research` pieces should not be promoted into top-level themes unless they connect to a broader industry beta

### `manual` and `external`

Best at:

- adding high-signal event updates
- importing bank notes and long PDFs
- confirming or challenging a theme already surfacing elsewhere

Most useful for theme mining:

- `Japan policy normalization`
- `Iran / Hormuz escalation`
- `agentic stablecoin settlement`
- `modern warfare / defense`

## Already Approved Themes

These are already strong enough to exist as formal themes, so they do not need to be re-added as new ideas. They should still remain in this backlog because many new materials will attach to them.

### `iran-hormuz-escalation`

- Status: `approved`
- Source support: `capitalflows`, `manual`, `external`, some `tmt_breakout`
- Why it survives: clear cross-asset routing power across energy, shipping, rates, gold, Japan, and defense

### `gold-monetary-fragmentation`

- Status: `approved`
- Source support: `capitalflows`, `external`, linked macro material
- Why it survives: reserve, fiscal, real-rate, and geopolitical stress all converge here

### `usd-liquidity-plumbing`

- Status: `approved`
- Source support: `conks`, `capitalflows`, macro manual notes
- Why it survives: true system-routing theme, not just a rates subtopic

### `japan-policy-normalization`

- Status: `approved`
- Source support: `manual`, macro research, linked war-energy logic
- Why it survives: BoJ, imported inflation, and energy-shock timing interact in a portfolio-relevant way

### `agentic-stablecoin-settlement`

- Status: `approved`
- Source support: `manual`, policy notes, crypto / payment rails material
- Why it survives: not just crypto beta; it can affect settlement rails, payment architecture, and agentic transaction flow

### `ai-datacenter-power-and-balance-of-plant`

- Status: `approved`
- Source support: `capitalflows`, `tmt_breakout`, `citrini`, manual imports
- Why it survives: a real multi-leg industrial buildout theme with direct asset mapping

## Existing Draft Waiting For Promotion

### `enterprise-ai-execution-layer`

- Status: `draft`
- Source support: `tmt_breakout`, `citrini`, manual `Agentic Utilities`
- Current local draft: `data/research/theme_update_drafts/enterprise-ai-execution-layer.md`
- Why it matters: this is the clearest local attempt to separate `agentic utility layer` from both `datacenter buildout` and `stablecoin settlement`
- Promotion test:
  - needs broader cross-source repetition
  - needs cleaner boundaries versus existing AI themes
  - should prove it is a durable routing layer rather than a one-off synthesis

## New Candidate Themes

These are the best current candidates to keep in `ideas` before promotion.

### `ai-application-layer-rerating`

- Status: `candidate`
- Main source support: `tmt_breakout`, `capitalflows equity`, some `citrini`
- Core idea: the market may be moving from `AI infra only` toward a more selective repricing of the software and application layer, but only for names with real workflow ownership and monetizable AI uplift
- Why this is not yet active:
  - evidence is recurring, but still partly wrapped inside daily TMT tape
  - it needs more separation between `winners`, `generic software under pressure`, and `execution-layer beneficiaries`
- Best expression: `industry specific beta theme`

### `ai-infrastructure-bottlenecks-beyond-gpu`

- Status: `candidate`
- Main source support: `tmt_breakout`, `citrini`, `capitalflows`
- Core idea: AI profit pools may keep broadening from GPU and hyperscaler capex into optics, interconnect, memory, networking, server architecture, packaging, and balance-of-plant
- Why this is not yet active:
  - large overlap with `ai-datacenter-power-and-balance-of-plant`
  - may be better as a widened subtheme rather than a separate top-level theme
- Best expression: `industry specific beta theme`

### `custom-silicon-and-memory-profit-pool-shift`

- Status: `candidate`
- Main source support: `tmt_breakout`, `citrini`
- Core idea: value may rotate from the most crowded general-purpose AI compute chain toward custom silicon, memory, and adjacent system bottlenecks
- Why this is not yet active:
  - still narrower than a full cross-asset routing theme
  - currently behaves more like a high-quality industry thesis cluster
- Best expression: `industry specific beta theme`

### `modern-warfare-capability-stack`

- Status: `draft_candidate`
- Main source support: `Thematic Update: Modern Warfare`, `The New WFH (War From Home)`, and the highest-related `26 Trades for 2026` defense slices
- Core idea: modern warfare increasingly reprices toward a layered capability stack across missile defense, counter-UAS, EW, ISR / surveillance, directed energy, and subsea / maritime security
- Candidate report surface: `data/research/themes/reports/modern-warfare-capability-stack.md`
- Routing note: keep it outside generated theme indexes until a new package -> writer draft -> review pass promotes it to `approved`
- Boundary: keep this as an `industry-capability umbrella`, not a macro war-routing theme; do not collapse it into `iran-hormuz-escalation`
- Best expression: `industry specific beta theme`

### `ai-industrial-buildout`

- Status: `candidate`
- Main source support: `citrini`, `tmt_breakout`, active datacenter theme inputs
- Core idea: the AI buildout should be read not only as compute and chips, but as a broader industrial deployment cycle across power equipment, cooling, electrical gear, buildout, optics, and deployment services
- Why this is not yet active:
  - meaningful overlap with the existing `ai-datacenter-power-and-balance-of-plant`
  - may be better treated as a higher-level framing layer or naming refresh
- Best expression: `industry specific beta theme`

## Themes That Should Usually Stay `thesis_only`

### `single-stock-deep-research`

- Status: `thesis_only`
- Main source support: `citrini`
- Why it stays here:
  - high value for idea generation
  - low value as a reusable routing theme unless multiple single-name pieces clearly map to one industry beta

### `thread-index-noise`

- Status: `thesis_only`
- Main source support: `capitalflows_index`, `tmt_breakout_index`, `citrini_index`, `citrindex`
- Why it stays here:
  - low `theme_bias`
  - snapshot-first by design
  - useful as routing hints, not as standalone theme evidence

## Industry Specific Beta Theme Frame

Many future themes in this repo probably should not jump directly from `single stock` to `macro super-theme`.

An intermediate layer is useful:

- `industry specific beta theme`

This is the right bucket when an idea has:

- repeated evidence across 2 or more sources
- a clear industry transmission path
- multiple related names or subsegments
- real portfolio usefulness
- but not yet enough cross-asset routing power to deserve a top-level macro theme

Good examples right now:

- `AI application-layer rerating`
- `AI infrastructure bottlenecks beyond GPU`
- `custom silicon and memory profit-pool shift`
- `modern warfare capability stack`
- `power and optics`

Weak examples:

- one-off single-stock long thesis
- a thread notice or chat index
- one PDF with no cross-source reinforcement

## Promotion Rules

Promote a candidate toward a formal theme only when most of the following are true:

- it appears across multiple source families, not just one publisher
- it can route portfolio attention more than once
- it has a stable boundary versus nearby themes
- it maps to a basket, segment, or repeated decision surface
- it is more than a snapshot cluster and more than a single-stock memo

Keep it in `ideas` when:

- evidence is interesting but still early
- it overlaps too heavily with an active theme
- it still depends too much on one author's framing

Keep it as `thesis_only` when:

- it is basically one company idea
- the repeat signal is weak
- it does not change portfolio routing outside a narrow sleeve

## Current Working Take

The repo is probably moving toward a two-level theme system:

- `macro / portfolio-routing themes`
- `industry specific beta themes`

That structure fits the current source mix better than forcing everything into one flat theme list.

The strongest next `industry specific beta` candidates today are:

- `AI application-layer rerating`
- `AI infrastructure bottlenecks beyond GPU`
- `modern warfare and defense-electronics`

The clearest draft that may eventually bridge into that system is:

- `enterprise-ai-execution-layer`
- `modern-warfare-capability-stack`
