---
system: "DAG Execution Model"
patterns: ["ReWOO", "LLM Compiler DAG"]
groups: ["execution-planning"]
execution_model: "dag"
scale: "single-agent"
primary_concern: "latency"
orchestrates: ["parallel-execution", "dependency-resolution", "variable-binding"]
---

# DAG Execution Model

## Description
Precompiled execution graph with variable dependencies.

## Used by
- ReWOO → [rewoo](../../patterns/rewoo/README.md)
- LLM Compiler → [llm-compiler-dag](../../patterns/llm-compiler-dag/README.md)

## Properties
- deterministic
- parallelizable
- low latency

## When NOT to use
- uncertain environments
- tasks requiring runtime branching