# LLM Compiler DAG

## Overview
This pattern compiles a request into a DAG of tasks with dependencies, enabling safe parallel execution and deterministic joins.

## When to Use
- Complex workflows with dependency structure
- Workloads that benefit from parallel branches
- Auditable orchestration pipelines

## When Not to Use
- Tiny linear tasks
- Environments without a scheduler/executor abstraction

## Flow
`Goal -> Compile DAG -> Execute ready nodes in parallel -> Join -> Final output`

## Minimal Python
See `code.py`.

## Minimal JavaScript
See `example.js`.

From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
