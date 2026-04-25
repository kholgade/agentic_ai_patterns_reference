# Program-Aided Language (PAL)

## Overview
PAL delegates computation-heavy reasoning to generated code. The model writes a program, executes it, and then explains or returns results.

## When to Use
- Arithmetic, simulation, and deterministic transformations
- Data manipulation tasks where execution is safer than free-form reasoning
- Auditability requirements

## When Not to Use
- Tasks requiring only natural-language judgment
- Environments where code execution is unavailable

## Flow
`Problem -> Generate code -> Execute -> Validate -> Final response`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
