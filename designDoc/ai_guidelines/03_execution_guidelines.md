# 03 Execution Guidelines

## One Full AI Cycle

1. export or load manifest
2. choose agent by role and capability
3. build read-only context
4. execute capability stages
5. validate structured output
6. persist result file
7. surface digest to CLI/dashboard/API
8. wait for human review

## Failure Policy

### Prefer Partial Over Empty
- if one research source fails, continue with the rest
- if one symbol fails in screening, continue with other symbols
- if all critical inputs fail, return `status="error"`

### Status Semantics
- `ok`: usable primary output exists
- `partial`: some stages failed but output remains useful
- `error`: no meaningful output produced

## Logging Rules

- log source-level failures with context
- log symbol-level screening failures without aborting whole run
- log manifest export and result persistence
- do not silently swallow errors that affect advisory quality

## Operator-Facing Rule

Every AI result must be understandable without reading internal code.
That means:
- digest first
- structured payload second
- raw debug detail third
