# 05 Scaling Patterns

## Why Split The Docs

Do not keep all AI operating rules in one file.
Split by concern so future AI tools only load the minimum context they need.

## Pattern 1: Add A New Agent

When adding a new agent:
1. define role
2. define capability list
3. define inputs and outputs
4. define guardrails
5. implement `run(ctx)`
6. register it in the orchestrator
7. ensure it appears in the manifest
8. document it in this series

## Pattern 2: Add A New Skill

A skill should:
- do one bounded job
- accept explicit typed inputs
- return structured output
- avoid hidden side effects
- be callable independently if useful

## Pattern 3: Keep Routing Cheap

Future LLM routers should usually load in this order:
1. `README.md`
2. `01_agent_roles_and_skills.md`
3. `02_protocol_stack.md`
4. only then the specific code file they need

## Pattern 4: Keep Main Design Doc Stable

The main architecture doc should explain the product and system.
This AI guideline series should explain how AI is supposed to operate inside it.

## Pattern 5: No Hidden Automation Drift

As the platform scales:
- do not let advisory outputs become execution commands
- do not add broker mutations to agent protocols
- keep human review as a hard boundary
- keep manifest export as the single source of truth for AI routing
