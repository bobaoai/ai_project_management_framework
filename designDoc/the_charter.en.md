---
title: Analyst Billie Charter
status: active
layer: T0
t0_layer_id: the_charter
canonical_owner: designDoc/the_charter.md
language: en
parallel_of: designDoc/the_charter.md
---

# Analyst Billie Charter

**Version 1.7 — 2026-05-06**
**Chinese parallel**: [T0-Charter-ZH]

## 0. Contract Capsule

Machine-audit block. Keep paths, ids, aliases, commands, and ledger pointers plain; use citation ids only in body prose and `References`.

```yaml
layer: T0
t0_layer_id: the_charter
status: active
canonical_owner: designDoc/the_charter.md
scope: English parallel of the supreme Analyst Billie constitutional constraints for object ontology, authority layering, system surface split, archive truth, canonical paths, false-precision refusal, belief-delta evidence, freshness, decision grounding, no-orphan structure, and amendment thresholds
non_goals:
  - runtime command discipline
  - schema implementation details and field-version listings
  - task inventories, external runner mechanics, or Design Doc review procedure
inputs:
  - designDoc/the_charter.md
outputs:
  - English parallel reading surface for the charter
truth_surfaces:
  - designDoc/the_charter.md
  - designDoc/the_charter.en.md
runtime_triggers: none
downstream_consumers:
  - English-language readers of the T0 charter
open_decisions: none
review_gate: owner / principal-manager amendment threshold
runtime_surface_ledger: none
verification_hooks:
  - ./.venv/bin/python -m pytest tests/test_design_doc_t0_layer_ids.py -q
```

---

## Preamble

Analyst Billie is a cognitive system that continuously distills market information into changes of belief state.

The bottleneck it confronts is not the acquisition of information, but the auditable revision of belief state.

It is operated by a single principal manager, organized around four object classes — Theme, Thesis, Scenario, Evidence — and conducts its memory, judgment, freshness, and decisions according to the articles below.

This charter is the supreme constraint on Analyst Billie. All design, protocol, contract, skill, and artifact below it presume this charter. Any subordinate document in conflict with this charter shall be withdrawn or revised; the charter does not yield.

---

## Article I · Object Ontology

The world of Analyst Billie is composed of four first-class object classes:

- **Theme** — a structural topic worth long-term tracking.
- **Thesis** — under a Theme, a falsifiable claim with a causal chain and falsification conditions.
- **Scenario** — under a Thesis, a possible realization path, including trigger signals and causal chain nodes.
- **Evidence** — an external observation or internal judgment that induces a change in some belief state, recording its prior, posterior, and changed dimension.

The four divide labor cleanly: Theme delineates the field of attention; Thesis explains why; Scenario describes how it might unfold; Evidence records why our view changed.

Beyond these four classes, **path observation** is recognized as an auxiliary object, governing early-path signals upstream of Scenario; it does not enjoy first-class status.

An observation may exist before any Thesis, but before entering any decision it shall be bound to a Thesis, a Scenario, or some belief object. No floating observation enters decision.

Every first-class object shall be traceable: Theme is the apex; Thesis and Scenario each have a single parent; Evidence binds to at least one explicit object. Orphan objects are not recognized.

---

## Article II · Authority Layering

Belief is the principal manager's domain.
Fact is the system's domain.

The **belief layer** comprises: lifecycle transitions of Thesis and Scenario, assignment of `pm_conviction`, assignment of `scenario_role`, assignment of `market_state`, and adjudication of scope boundaries. Actions in this layer require explicit acknowledgment by the principal manager.

The **fact layer** comprises: numeric verification, field consistency, timestamp normalization, reference integrity, the matching of objectively-verifiable trigger `signal_status`, ledger drafting, and freshness sweeping. Actions in this layer are executed and recorded by the system on its own authority.

However: a trigger signal match terminates at the `signal_status` level. A signal match is **not** equivalent to a Scenario being verified; the lifecycle of a Scenario or a Thesis cannot be advanced by the system on its own.

Decision rule: what can be settled by checking facts belongs to the system; what requires interpretation, weighing, or subjective conviction belongs to the principal manager. This article is enforced at the schema level — an Evidence not acknowledged by the principal manager shall not drive a belief-layer transition.

---

## Article II-A · System Surface Split

Analyst Billie's system surfaces divide authority as follows:

```text
DesignDoc owns what / why / boundary / authority.
Skills own how an AI should act now.
Code owns how something can be deterministically checked or executed.
```

DesignDoc is the authority entry for design and maintenance. It defines what objects, workflows, and artifacts the system recognizes, why they exist, where the boundaries are, and who owns authority. Work that changes a system contract, boundary, workflow, artifact shape, routing rule, skill responsibility, command behavior, schema, or runner profile shall start from DesignDoc, then pass through the review gate before projection into Skills, Code, tests, schemas, and artifacts.

T1 DesignDocs may define AI workflow semantics when they define durable design authority: why a workflow exists, which states it recognizes, what its boundaries are, which inputs and outputs are admitted, and when human adjudication is required. The corresponding Skill is that authority's execution projection in the current AI runtime, responsible for telling the AI how to act now. A Skill may orchestrate admitted Code, but it does not own deterministic command behavior, schema validation, or executable results.

Skills are the execution entry for admitted product operation. When executing an existing workflow, the system should enter through the routing skill or task skill, reading only the necessary DesignDoc capsule / ledger as authority context. A product run should not require rereading the entire design corpus.

Artifacts, runtime state, sidecars, and reports hold what the system has produced; they do not independently own system authority in the sense of this article. Code executes and validates deterministic rules; it answers "what can be checked or run repeatably."

No surface shall pretend to own all four authorities. When ownership is unclear, return to this article first.

---

## Article III · The Seat of Truth

The archive is the sole source of truth of Analyst Billie.

The archive shall not be rewritten; it may only be appended. All other surfaces are references, indexes, or interpretations of the archive, and shall not duplicate its content.

Any state in which "the overlay was modified but the archive was not" does not constitute a fact.

---

## Article IV · The Single Path

Each resource class shall have one canonical path.

When the canonical path cannot serve a request, the system shall raise a hard error, visible immediately to the caller. Any silent fallback, any "try-canonical-then-legacy" structure, is a defect and shall be removed.

Better to halt loudly than to pollute silently.

---

## Article V · The Refusal of False Precision

The causal chains Analyst Billie processes are predominantly macro and semi-macro. Their default expressive form is enum and prose.

- Belief strength is expressed in enum (`high / medium / low / exploratory`), not as a 0–1 float.
- Thresholds are expressed in prose, with explicit annotation of the chain node they would break (`demand / supply / pricing / policy / adoption / margin`); they shall not be expressed as a bare numeric threshold alone.
- Magnitude is expressed in three-tier enum (`minor / moderate / major`), not as a float.

Numbers are not the default. Whoever introduces a number must demonstrate that it is genuinely auditable; a non-auditable number is false precision, and this charter rejects it.

---

## Article VI · Learning, Not Bookkeeping

Evidence is not a log.

Every Evidence record shall set forth:

- **Prior state** — what the belief was before.
- **Posterior state** — what the belief is after.
- **Changed dimension** — along which axis the change occurred.
- **Rationale** — why it changed.

An Evidence without a belief delta is not Evidence. Anything that records "what was seen" without recording "what was newly believed" is admitted by the archive but rejected by the ledger. The two have distinct domains and shall not be conflated.

Evidence shall not be biased. Counter-evidence and unresolved objections shall enter the ledger on equal footing with supporting evidence; the system shall not record only what supports.

---

## Article VII · The Law of Freshness

Every active object shall carry a review policy.

**Freshness** and **lifecycle** are distinct properties and shall not be conflated — freshness speaks to currency, lifecycle to existence. A Thesis may simultaneously be `active` (its lifecycle still standing) and `stale` (its freshness expired). Each occupies its own dimension; neither substitutes for the other.

A freshness sweeper shall conduct sweeps on a designated cadence; objects past due have their freshness automatically set to `stale`, with a freshness event recorded. A freshness event does not constitute an Evidence — only when the object is reused via the revive procedure, or cited again in a new decision, shall a belief-change record be written. Lifecycle does not change because of freshness.

The candidate set of any portfolio decision shall satisfy both `lifecycle_stage = active` and `freshness_state = fresh`. This is enforced at the schema level.

To revive a stale object, the revive procedure shall be followed and a belief-delta Evidence shall be written, recording the reason for revival.

Freshness is not advisory; it is law.

---

## Article VIII · The Ground of Decision

A portfolio decision shall cite at least one Scenario that is both `active` and `fresh`, and shall explicitly reference its (`pm_conviction`, `scenario_role`, `market_state`) triple together with its pricing anchor.

`market_state` shall preserve a time series: every update appends a new snapshot and does not overwrite prior values. In retrospective review, the pricing path matters as much as its current state.

The current value of each element of this triple shall be traceable, via the Evidence ledger, back to its belief origin.

A decision shall expose the unresolved objections of the cited Scenario; ignoring an unresolved objection requires an explicit rationale.
A decision shall not bypass the Scenario layer to read Thesis prose directly.
A decision shall not cite a belief delta not acknowledged by the principal manager.

Thereby, every portfolio decision shall be auditable element by element after the fact.

---

## Article IX · No Orphan

Within Analyst Billie, no capability, artifact, or action may exist orphaned from the system.

Three structures uphold this rule:

- **Three Views** — Functional Modules, KnowledgeBase, AnalysisPlatform. Every capability shall locate itself in these three views.
- **Four Routes** — task mainline, skill, deterministic builder / package, writer gateway. The four layers shall not penetrate one another; every request shall traverse the four.
- **One Artifact Graph** — every PM-facing artifact is a node in this graph, carrying canonical path, freshness contract, builder, and owner skill. Composite tasks are sets of goal-nodes; every artifact shall hang within this graph.

What cannot be hung is either misplaced in capability or missing in position; it shall be remedied first and proceed only thereafter. Orphan things do not enter the system.

---

## Article X · Amendment

This charter may be amended; the threshold is strict.

- **Cognitive Articles** — when one of Articles I through VIII is persistently falsified: through several independent cases demonstrating fundamental conflict with the actual workflow.
- **Structural Article** — when the structure described in Article IX undergoes fundamental change: e.g., a re-cut of the three views, a merger or split of the four routes, or a reconstruction of the artifact graph model.
- **New Article** — when establishing Article XI: when a new cognitive constraint, stable for more than three months and spanning multiple skills and schemas, appears.
- **Charter Restart** — when the principal manager explicitly declares: a major business direction change.

This charter does not accept the following changes:

- Writing in schema implementation details, field version numbers, or skill lists (the charter only names constitutional-level commitments; it does not lock implementation);
- Writing in runtime discipline — that is the responsibility of the operator's manual;
- Soft re-wording — a change in wording is a change in commitment, and shall pass the thresholds above.

An amendment shall increment the Version line.

---

## References

- `[T0-Charter-ZH]` [Chinese parallel Charter](the_charter.md)

## Amendment Record

- **v1.7 (2026-05-06)** — added the refined interpretation to **Article II-A · System Surface Split**: T1 DesignDocs may define durable AI workflow semantics; Skills are the current runtime execution projection; Skills may orchestrate Code but do not own deterministic command behavior, schema validation, or executable results.
- **v1.6 (2026-05-06)** — added **Article II-A · System Surface Split**, defining the DesignDoc / Skills / Code authority boundary and separating the design-maintenance entry from the product-operation entry; artifacts, sidecars, reports, and runtime state hold produced results but do not independently own system authority.
- **v1.5 (2026-04-26)** — four small semantic-boundary refinements after a third review; structure and commitments unchanged:
  - Article I added a one-line synthesis of the four object classes' division of labor;
  - Article I final clause changed from "unique upward lineage" to per-class traceability (Theme apex; Thesis & Scenario single parent; Evidence ≥1 explicit binding) — the original was inaccurate for Evidence's multi-link design;
  - Article VII changed sweeper output from "Evidence" to "freshness event", explicitly stating freshness events do not constitute Evidence — resolving conflict with Article VI's "no belief delta, no Evidence" rule;
  - Article VII candidate-set filter clarified to "both `lifecycle_stage = active` and `freshness_state = fresh`", removing a misleading earlier phrasing.
  - Reviewer's fourth point (Article II "ledger drafting") not adopted: existing tail clause "an Evidence not acknowledged by the principal manager shall not drive a belief-layer transition" already covers it.
- **v1.4 (2026-04-26)** — three commitments restored after revisiting prior reviews:
  - **Article VI** added "Evidence shall not be biased": counter-evidence and unresolved objections enter the ledger on equal footing with supporting evidence. Responds to the first reviewer's warning about confirmation machines.
  - **Article VIII** added "`market_state` shall preserve a time series": every update appends a snapshot, never overwrites. In retrospect, the pricing path matters as much as its current state.
  - **Article VIII** added "A decision shall expose the unresolved objections of the cited Scenario": ignoring requires an explicit rationale. Closes the loop with the Article VI impartiality clause.
  - (No v1.3 in English: v1.3 was a Chinese-only stylistic revision; English text unchanged.)
- **v1.2 (2026-04-26)** — seven article revisions plus full Chinese-language unification.
  - Internal consistency: Article II `pm_conviction` / `market_state` field names aligned with Article VIII;
  - Self-contradiction removed: Article VII "weekly sweep" changed to "designated cadence", to avoid runtime frequency leaking into the constitution;
  - Implicit promise made explicit: Article VIII added "the current value of each element of the triple shall be traceable, via the Evidence ledger, back to its belief origin", making the audit promise hold;
  - Redundancy removed: Article VIII's three prohibitions reduced after deletion of "shall not be based on stale objects" (covered by the main clause);
  - Anti-false-precision counter-example removed: Article X's "at least three cases" changed to "several independent cases", to not violate Article V;
  - Amendment thresholds layered: Article X separates Cognitive Articles / Structural Article / New Article / Charter Restart into four distinct rows;
  - Schema boundary clarified: Article X's "shall not write in schema fields" changed to "shall not write in schema implementation details, field version numbers", acknowledging that the charter naming constitutional-level fields is not forbidden;
  - Full Chinese unification (in the Chinese parallel): aside from the four core object classes (Theme / Thesis / Scenario / Evidence), enums, schema field names, and architectural proper nouns (Functional Modules / KnowledgeBase / AnalysisPlatform), all other English terms are translated into Chinese, with the original English given parenthetically at first occurrence.
- **v1.1 (2026-04-26)** — preamble augmented with the auditability north star; Article I added the rule that an observation must bind before entering decision; Article II clarified that signal-status matching terminates at the fact layer; Article VI emphasized the distinction between archive and ledger; Article VII introduced the two-dimensional separation of freshness and lifecycle; Article VIII renamed `narrative_role` to `scenario_role`; Article IX renamed to "No Orphan".
- **v1.0 (2026-04-26)** — first composition.
