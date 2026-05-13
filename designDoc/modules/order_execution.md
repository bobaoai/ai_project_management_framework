# Order Execution

## Purpose

`OrderExecution` is the thin broker execution layer for `trading_platform`.

It turns already-approved trading intent into Schwab order actions and records execution truth locally.

## Scope

First version supports:

- `equity / ETF` only
- `open`
- `close`
- `protective stop create`
- `protective stop replace`
- `protective stop cancel`
- close-time stop cleanup before submitting the close order

## Boundary

This layer does not decide whether a trade is allowed or desirable.

It does not own:

- position constraints
- theme constraints
- risk rules
- sizing logic
- strategy discipline

Those belong to separate upstream layers.

`OrderExecution` only owns:

- submit
- cancel
- replace
- close orchestration
- local execution receipts

## Runtime Surface

The first runtime surface is CLI-first through `tradectl`.

That keeps execution aligned with the current operator workflow and preserves the existing read-only boundary in `src/service/server.py`.

## Execution Agent

`OrderExecution` should also be exposed through one dedicated execution agent.

That agent should:

- run as a distinct order-entry and order-management role
- use Cursor `GPT-5.4`
- consume already-approved execution intent from upstream layers
- call the local deterministic execution tools instead of inventing broker actions in free-form prose

This agent is an execution endpoint, not a portfolio-construction or risk-governance agent.

It should not decide:

- whether the trade fits portfolio constraints
- whether the trade fits theme constraints
- whether sizing is appropriate
- whether risk rules permit the trade

Its job is narrower:

- translate approved intent into broker actions
- preview or submit orders
- manage stop create/replace/cancel
- handle close-time stop cleanup
- persist execution receipts

## Truth Surface

Execution receipts live under:

- `data/account/execution/receipts/`

Each receipt should persist:

- timestamp
- action or mode
- account hash
- symbol
- normalized intent
- working orders seen before submit
- cancelled order ids if any
- Schwab request payload
- Schwab response summary

These receipts are broker-execution truth artifacts, not editable review prose.

## Close Workflow

For `close`, the minimum safe path is:

1. Load current working orders for the symbol.
2. Identify working protective stops that would conflict with the close.
3. Require an explicit CLI acknowledgment such as `--cancel-conflicting-stops` before canceling them.
4. Cancel those stops first.
5. Submit the close order.
6. Persist one execution receipt with both the pre-close working orders, cancelled order ids, and the cancel responses.

## CLI Examples

Common command shapes:

```bash
python -m src.cli.tradectl orders open --account-hash <acct> --symbol SPY --side buy --qty 10 --preview
python -m src.cli.tradectl orders open --account-hash <acct> --symbol SPY --side buy --qty 10 --confirm-live
python -m src.cli.tradectl orders open --account-hash <acct> --symbol SPY --side buy --qty 10 --type limit --limit-price 620 --preview
python -m src.cli.tradectl orders close --account-hash <acct> --symbol SPY --preview
python -m src.cli.tradectl orders close --account-hash <acct> --symbol SPY --cancel-conflicting-stops --confirm-live
python -m src.cli.tradectl orders stop create --account-hash <acct> --symbol SPY --stop-price 600 --preview
python -m src.cli.tradectl orders stop create --account-hash <acct> --symbol SPY --stop-price 600 --confirm-live
python -m src.cli.tradectl orders stop replace --account-hash <acct> --symbol SPY --stop-price 605 --confirm-live
python -m src.cli.tradectl orders stop cancel --account-hash <acct> --symbol SPY --confirm-live
```

Operator shorthand assumptions for the current workflow:

- if no price is specified for `open` or `close`, treat it as `MARKET`
- use `preview` when checking broker acceptance and projected balance impact
- use live submit only with explicit `--confirm-live`
- for `close`, use `--cancel-conflicting-stops` when the symbol already has a working protective stop

## Non-Goals

This layer intentionally does not include:

- options execution
- OCO or bracket logic
- stop-limit logic
- scheduler-driven end-of-day flattening
- HTTP execution endpoints
- session-aware algo execution
