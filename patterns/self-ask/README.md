# Self-Ask Pattern

## Overview
Self-Ask is a decomposition-first pattern where the model generates focused sub-questions before answering the main question. This improves traceability and reduces reasoning jumps.

## When to Use
- Multi-hop QA and research tasks
- Questions requiring explicit decomposition
- Cases where intermediate answers matter

## When Not to Use
- Simple factual lookups
- Very low-latency paths where extra steps are too costly

## Flow
`Question -> Generate sub-questions -> Answer sub-questions -> Synthesize final answer`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
