# 00 System Principles

## Purpose

Define the non-negotiable rules for AI in this platform.

## Core Principle

This system is an **AI-assisted trading intelligence platform**, not an autonomous trading system.

## AI Is Allowed To

- read portfolio, market, analytics, and research inputs
- normalize data into structured objects
- classify news and macro events
- compute risk summaries
- rank candidates
- generate recommendations
- persist structured JSON outputs for audit and UI consumption

## AI Is Not Allowed To

- place orders
- mutate broker state
- bypass human review
- invent missing market data
- silently suppress failures that affect decision quality

## Design Rules

- prefer explicit function boundaries over hidden workflows
- prefer structured outputs over free-form prose
- prefer partial output over total failure when safe
- keep all advisory logic reviewable by humans
- use the orchestrator as the only coordination and persistence layer

## Read/Write Boundary

### Read-only domains
- broker account state
- historical market data
- analytics results
- subscribed research inputs

### Writable domains
- `data/account/`
- `data/agents/`
- `data/dashboard/`
- `data/option_hist/`

### Forbidden write domains
- broker APIs
- live order execution systems
- hidden state outside orchestrator-managed persistence
