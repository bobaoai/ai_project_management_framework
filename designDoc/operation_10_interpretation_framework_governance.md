---
title: Interpretation Framework Governance Pointer
status: compatibility_pointer
reader_persona:
  - System Builder
  - Research Architect
  - Digestion Worker Designer
---

# Interpretation Framework Governance Pointer

## 1. Canonical Ownership

Reusable interpretation frameworks are Digestion experts.

The canonical design now lives in:

- `digestion_00_overview.md`
- `digestion_10_structure_contract.md`
- `digestion_30_expert_factory.md`

This document remains as a compatibility pointer for older references to `operation_10_interpretation_framework_governance.md`.

## 2. Boundary

The operating layer owns role authority:

- what the Interpretation role may do;
- what the PM, Trader, Executor, and Risk roles may do;
- which role gates are required before downstream action;
- when PM acknowledgement is needed.

The Digestion layer owns domain experts:

- reusable analytical asset extraction;
- expert admission and lifecycle;
- source card pattern;
- typed claim firewall;
- framework route;
- expert artifact schema;
- generated skill projection;
- promotion links.

The distinction:

```text
Operating Framework
  -> who may reason, decide, verify, act, and hand off

Digestion Expert Factory
  -> how a domain expert reads sources and what digestion objects it may emit
```

## 3. Correct Route

Use this route for reusable interpretation frameworks:

```text
read_content.md
  -> MetaSkill / reusable asset candidate
  -> Digestion Expert Factory
  -> Expert Contract
  -> Source Card Pattern
  -> Typed Claim Firewall
  -> Expert Artifact Schema
  -> Generated Skill Projection
```

Use this route for single asset research:

```text
research request
  -> Independent Research Orchestrator
  -> message archive / source packet
  -> domain route selection
  -> selected domain expert
  -> expert-owned Source Card / Typed Claim / Expert Artifact
```

## 4. What Moved To Digestion

The following concepts belong to `digestion_30_expert_factory.md`:

- MetaSkill extraction;
- Domain Expert maintenance;
- reusable analytical asset admission;
- framework reviewer and adversary checks;
- source-class firewall;
- claim-type firewall;
- output allow/block lists;
- framework conflict notes;
- expert lifecycle;
- generated skill projection metadata.

## 5. What Stays In Operation

The following concepts stay in `operation_00_operating_framework_governance.md`:

- PM authority;
- Trader authority;
- Executor authority;
- Risk authority;
- Interpretation role authority;
- handoff gates;
- PM acknowledgement for operating authority changes;
- role-level review and adversary checks.

## 6. Detection Boundaries

Violations are observable:

- an operating role framework stores a source card pattern or claim-type enum;
- an expert skill has no Digestion expert contract;
- a domain expert emits portfolio action;
- a generated skill claims authority beyond its expert contract;
- a PM-facing report cites an expert name without source card, typed claim, expert artifact, or promotion link.

When these appear, route the domain framework work to Digestion and keep operation focused on role authority.
