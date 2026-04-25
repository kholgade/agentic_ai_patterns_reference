# Speculative Decoding

## Overview
Speculative decoding uses a smaller draft model to propose tokens and a larger model to verify/accept them. This reduces latency while preserving quality.

## When to Use
- Latency-sensitive generation at scale
- Dual-model deployments (small + large)
- Throughput optimization workloads

## When Not to Use
- Single-model stacks only
- Extremely short outputs where overhead dominates

## Flow
`Draft model proposes -> Verifier validates -> Accept/reject tokens -> Continue`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
