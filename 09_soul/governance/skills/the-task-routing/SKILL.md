---
name: the-task-routing
description: Resolves a new request to one authorized semantic task mainline using the code-owned Task Routing registry. Use when the requested result or owner is not already explicit. It never selects a provider, model, adapter, Runtime binding, process, or UI.
metadata:
  skill_class: primary_agent_development
  primary_agent_entry_role: routing
  primary_agent_entry_subject: task_request
  first_authority_ref: designDoc/the_task_routing.md
---

# Task Mainline Routing

This is a `routing` Skill. It selects a logical mainline and never becomes the
author, operator, or reviewer for the selected work.

## Objective

Return one bounded semantic routing resolution from the exact Product
Authorization eligible set and the project-bound, code-owned mainline catalog.

Read:

1. `designDoc/the_task_routing.md` for routing intent and failure law;
2. the project-bound code-owned routing Registry for current mainline registrations;
3. its generated human inspection for current routing facts;
4. the selected first authority only after routing succeeds.

Do not use a manual table in a prompt, project instruction, or compatibility
projection as routing authority.

## Input Contract

The trusted caller supplies:

- authenticated request-envelope ref and hash;
- immutable `RouteEligibilityDecision` ref and hash;
- pinned routing-registry release ref and hash;
- request text or structured intent;
- authorized context-overlay refs.

This skill may classify only mainlines present in the eligible set. It must not
reveal an unauthorized candidate through a question, count, log, timing, or
error.

## Decision Law

Classify the requested durable result, not a noun mentioned in the request.
Theme, ticker, account, Source, file, provider, model, framework, and UI names
are context unless they define the requested output.

Design titles, T0 names, Skill IDs, directories, filenames, Reviewers, and
component names follow the same rule. They may help locate registered evidence;
they never establish the requested outcome, governed layer, or logical owner by
lexical similarity.

When the requested durable result mutates any governed Design, Skill, Runtime,
Data, Registry, schema, code, test, release, deployment, rollback, or retirement
surface, the only parentless route is the registered `system_change_intake`
mainline. Task Routing does not select Design, Skill, Runtime registration,
Engineering, Audit, or Software Delivery steps inside the resulting Plan.
The reviewed SystemChangePlan assigns those authoring and review methods.

This mutation test chooses the System Change mainline. It does not classify
affected files, author the Plan, execute Plan steps, or supervise completion.

Intersect semantic candidates with the eligible set and return:

- `routed` when exactly one authorized mainline wins;
- `clarification_required` when multiple authorized candidates would produce
  materially different outputs;
- `no_authorized_route` when no eligible mainline matches;
- `request_contract_invalid` when the trusted request-validity verdict is not
  exactly true;
- `routing_registry_unavailable` when registry identity, validation, or lookup
  fails.

Ask at most one bounded outcome-level clarification and expose only authorized
candidate descriptions. Never choose a nearby route because its projection or
Runtime binding happens to exist.

Provider, model, execution profile, adapter, Runtime release, workflow engine,
process, CLI, SDK, and host presentation are downstream choices and do not
belong in a routing result.

## Output Contract

A successful result binds:

```yaml
outcome: routed
request_ref: <exact authenticated request-envelope ref>
request_sha256: <exact request-envelope hash>
matched_mainline_id: <registered canonical id>
logical_owner_id: <registered logical owner>
first_authority_ref: <registered authority>
completion_kind: <registered completion class>
completion_type: <registered output type>
route_eligibility_decision_ref: <immutable ref>
route_eligibility_decision_sha256: <exact decision hash>
routing_registry_release_ref: <immutable ref>
routing_registry_release_sha256: <exact release hash>
context_overlay_refs: []
reason_code: <bounded code>
classification_explanation: <bounded semantic explanation>
```

Non-success outcomes contain no unauthorized owner or route identity.
The project binding declares whether its classifier, immutable Registry
release, authorization integration, and decision store are admitted. A host
proposal cannot be represented as formal product-routing evidence.
An unavailable or unadmitted authorization integration returns
`request_contract_invalid`; an unavailable or unadmitted routing Registry
release returns `routing_registry_unavailable`.

## Downstream Boundary

After `routed`:

1. `system_change_intake` hands off to its registered first authority; the
   downstream code-owned registration resolves the operating method;
2. the reviewed SystemChangePlan is handed to the Primary Agent;
3. each Plan step validates its authoring method and produced subject kind;
4. downstream Workflow, authorization, Runtime, and domain owners act only when
   their step requires them.

Before an operating method acts, that method validates the exact reviewed
SystemChangePlan step. If the method returns an applicability rejection, stop
it and return the evidence to Task Routing or a successor SystemChangePlan.
When the rejection identifies a wrong
logical owner, record a Routing Gap of the registered `wrong_logical_owner`
kind. Do not
continue because the method was named and do not fall back to a nearby Skill.

A failure in those stages does not change or retry semantic routing through a
different mainline.

## Completion Standard

The result is complete when it uses a canonical registry ID or a bounded
failure outcome, binds the exact request plus the eligibility and Registry
releases, contains no execution selection, and lets the downstream owner start
from the registered first authority without reconstructing chat history.
