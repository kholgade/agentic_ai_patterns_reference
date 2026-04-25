---
group: "Execution-Centric Planning"
patterns: ["Program-Aided Language", "ReWOO", "LLM Compiler DAG"]
---

# Execution-Centric Planning Patterns

## Overview

These patterns shift from pure text reasoning to executable structure. PAL emphasizes code execution, ReWOO emphasizes variable-bound plans, and LLM Compiler DAG emphasizes dependency graphs.

---

## Pattern Comparison

### Program-Aided Language (PAL)
- Generate code and execute for deterministic computation
- Best for numeric, symbolic, and transformation-heavy tasks

### ReWOO
- Planner emits steps with reusable intermediate variables
- Best for tool workflows with explicit state reuse

### LLM Compiler DAG
- Compiles tasks into a graph of dependencies
- Best for orchestrated pipelines with parallel branches

---

## Side-by-Side

| Aspect | PAL | ReWOO | LLM Compiler DAG |
|--------|-----|-------|------------------|
| Main abstraction | Executable code | Variable-bound step plan | Task dependency graph |
| Parallelism | External/manual | Limited by plan | Native DAG-level |
| Best for | Deterministic compute | Tool-chain workflows | Large orchestrations |
| Complexity | Medium | Medium-High | High |

---

## Summary

- **PAL**: Use execution to improve reasoning reliability.
- **ReWOO**: Use variable-bound plans to reduce replanning.
- **LLM Compiler DAG**: Use graph planning for scalable orchestration.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
