# Least-to-Most Prompting

## Overview
Least-to-Most solves easier subproblems first, then uses those results to solve harder ones. It is effective for compositional reasoning.

## When to Use
- Problems with increasing difficulty steps
- Math and symbolic tasks with dependencies
- Structured planning where early outputs unlock later steps

## When Not to Use
- Independent tasks with no step dependency
- Low-latency one-shot responses

## Flow
`Task -> Easy subproblems -> Intermediate -> Hard subproblems -> Final answer`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
