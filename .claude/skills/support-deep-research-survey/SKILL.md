---
name: support-deep-research-survey
description: Adapts the portable Deep Research workflow to trading_platform output surfaces. Use when a mainline needs broad, source-heavy external research with overlapping dimensions, URL/quote preservation, and one final survey artifact, but the artifact location must follow the local task contract.
---

# Support Deep Research Survey

## What This Skill Does

This skill is the Cursor host adapter for the portable Deep Research method.

Method source:

```text
09_soul/skills/workflow_deep_research_survey.md
```

The portable workflow defines the research method:

- broad-to-narrow scanning;
- 3-5 overlapping research dimensions;
- independent passes that can contradict each other;
- URL and direct-quote preservation;
- one final survey artifact;
- no saved sub-agent intermediate notes.

This adapter decides where the final survey belongs inside `trading_platform`.

## Desired Result

By the end of a Deep Research pass, the system should have one reusable, traceable final artifact on the correct local surface.

The output path is not chosen by the portable workflow. It is chosen by the owning mainline:

- asset / company / crypto independent research belongs to message archive first;
- external learning belongs to `designDoc/learning_library/`;
- pure Hoveath cognitive surveys may remain under `09_soul/contexts/survey_sessions/`.

If a market or asset research survey lands only under `09_soul/contexts/survey_sessions/`, this adapter has failed.

## Output Routing

### Digestion Independent Research

Use this route when `digestion-independent-researcher` invokes `external_search_deep_research`.

Canonical surface:

```text
data/research/messages/<research_id>/
```

Required flow:

```text
external_search_deep_research
  -> support-deep-research-survey
  -> archive_message_create
  -> message_index_rebuild
  -> asset_source_link
  -> asset_source_packet_build
  -> domain_expert_invoke
```

The final survey is upstream source material. It must be imported as a message before an expert consumes it.

Recommended import shape:

```bash
./.venv/bin/python -m src.cli.tradectl message import-text \
  --title "<survey title>" \
  --file "<final survey markdown path>" \
  --source "deep_research_survey" \
  --sender "hoveath" \
  --sender-name "Hoveath Deep Research" \
  --tags "<asset>,deep_research,<source families>" \
  --document-type "deep_research_survey" \
  --stance "mixed" \
  --time-horizon "cross_horizon" \
  --primary-entities "<entities>" \
  --data-observed-at "<UTC timestamp>" \
  --message-produced-at "<UTC timestamp>"
```

Then link the returned `research_id`:

```bash
./.venv/bin/python -m src.cli.tradectl digestion independent-research link \
  --asset-key "<asset_key>" \
  --research-id "<research_id>" \
  --link-role "external_search_deep_research"
```

The asset workspace may link the message, but it must not become the raw archive root.

### External Learning Research

Use this route when `research-external-learning` studies outside workflows, repos, products, public skill systems, papers, or methodologies to improve local design judgment.

Canonical surfaces:

```text
designDoc/learning_library/repo_notes/<slug>.md
designDoc/learning_library/topics/<slug>.md
designDoc/learning_library/projects/<slug>/README.md
```

External learning artifacts are design-learning outputs. They should not be imported into `data/research/messages/` unless a separate archive-curation task needs to preserve the source body as research material.

### Pure Soul Survey

Use this route only for portable Hoveath memory or cognitive surveys that are not owned by a `trading_platform` mainline.

Canonical surface:

```text
09_soul/contexts/survey_sessions/<topic>_survey_<YYYYMMDD>.md
```

This route is not appropriate for asset research, public-comp calibration, private-company secondary-market checks, market reports, or domain-expert source packets.

## Final Survey Content Contract

The final survey should include:

- research question and time window;
- key conclusion with evidence strength;
- dimension split and overlap logic;
- source candidates with URLs and direct quotes;
- cross-validation findings;
- disagreements between sources;
- cannot-know boundaries;
- downstream handoff shape.

For time-sensitive market questions, include the exact window in the title or opening section, such as `last_2_weeks_secondary_softening_check`.

## Failure Signals

Treat these as failures:

- a Digestion Deep Research survey is saved only under `09_soul/contexts/survey_sessions/`;
- a Deep Research survey enters `source_packet.md` without a message archive `research_id`;
- intermediate sub-agent notes are saved as canonical outputs;
- the final survey lacks URLs for quoted claims or numeric claims;
- the final survey hides the time window for a time-sensitive market question;
- an external-learning artifact is imported as a message instead of written to `designDoc/learning_library/`;
- the adapter becomes the owning mainline instead of returning control to `digestion-independent-researcher` or `research-external-learning`.
