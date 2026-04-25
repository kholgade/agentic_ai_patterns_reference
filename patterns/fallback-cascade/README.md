# Fallback Cascade

## Overview
Fallback Cascade defines a prioritized recovery chain across models, prompts, tools, and providers. It enables graceful degradation under failures and policy blocks.

## When to Use
- Production systems with availability SLOs
- Multi-provider or multi-model stacks
- Robustness against outages and timeouts

## When Not to Use
- Non-critical prototypes
- Environments with only one execution path

## Flow
`Primary path -> Error/timeout/policy block -> Next fallback tier -> Success or terminal fail`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
