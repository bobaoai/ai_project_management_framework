# AI Guideline Series

This folder breaks the AI operating design into small, scalable documents so future AI tools do not need to load the full system architecture file every time.

## Files

- `00_system_principles.md`: platform-level AI principles and hard boundaries
- `01_agent_roles_and_skills.md`: agent roles, skills, and callable capability map
- `02_protocol_stack.md`: discovery, context, invocation, validation, persistence, and review protocols
- `03_execution_guidelines.md`: execution lifecycle, failure policy, and operator workflow
- `04_output_contracts.md`: shared schemas and JSON-facing output rules
- `05_scaling_patterns.md`: how to extend the system with more agents, skills, and manifests
- `06_agent_manifest_schema.md`: compact schema for `agent_manifest.json`
- `07_example_payloads.md`: example JSON payloads for context, outputs, flags, and manifest

## Intended Use

Use these docs as the AI-facing instruction layer for:
- future orchestrators
- skill routers
- LLM tool wrappers
- human reviewers who want the AI contract without loading the full product architecture
