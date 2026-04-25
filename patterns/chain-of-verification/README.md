# Chain-of-Verification (CoVe)

## Overview
CoVe generates an initial answer, then creates targeted verification questions, answers them, and revises the output. It reduces hallucinations and unsupported claims.

## When to Use
- High-accuracy Q&A
- Claims that need explicit validation
- Compliance-sensitive responses

## When Not to Use
- Low-risk casual chat
- Extreme latency constraints

## Flow
`Draft answer -> Generate checks -> Verify checks -> Revise answer`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
