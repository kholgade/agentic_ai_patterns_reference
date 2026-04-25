# ReWOO Pattern

## Overview
ReWOO (Reasoning Without Observation) separates planning from execution using variable-bound plan steps. The planner emits an execution graph with reusable intermediate variables.

## When to Use
- Multi-step tool workflows with reusable intermediates
- Cases needing fewer planner calls during execution
- Structured agent pipelines

## When Not to Use
- Very small tasks where planner overhead is unnecessary
- Dynamic environments requiring frequent replanning

## Flow
`Goal -> Plan with variables (#E1, #E2...) -> Execute steps -> Compose final answer`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
