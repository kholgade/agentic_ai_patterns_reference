# Context Compression

## Overview
Context Compression maintains token budgets by summarizing history into high-signal memory while preserving retrievable facts and decisions.

## When to Use
- Long-running sessions
- Multi-turn agents with limited context windows
- Memory systems requiring bounded storage

## When Not to Use
- Short conversations
- Tasks requiring full transcript fidelity

## Flow
`Conversation stream -> Salience scoring -> Summarize + extract facts -> Store compact memory`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
