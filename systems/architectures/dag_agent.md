---
system: "DAG Execution System"
patterns: ["ReWOO", "LLM Compiler DAG"]
groups: ["execution-planning"]
execution_model: "dag"
scale: "single-agent"
primary_concern: "cost"
orchestrates: ["plan-generation", "variable-binding", "parallel-execution"]
---

# DAG Execution System

## Overview
ReWOO / compiled plan execution with dependency graphs.

## Composition
- ReWOO → [rewoo](../../patterns/rewoo/README.md)
- LLM Compiler DAG → [llm-compiler-dag](../../patterns/llm-compiler-dag/README.md)

## Execution Model
DAG (Directed Acyclic Graph)

## Flow
1. Plan workflow with variables
2. Bind variables from previous steps
3. Execute independent nodes in parallel
4. Aggregate results from dependent nodes
5. Return final output

## When to use
- Deterministic workflows
- Parallelizable tasks
- Cost-sensitive bounded tasks

## Trade-offs
- Less flexible for uncertain environments
- Requires upfront planning

## Failure Modes
- Incorrect variable binding
- Circular dependency in planning

## Minimal Code (pseudo)
```python
plan = create_plan(query)
bound_plan = bind_variables(plan, context)
results = execute_dag(bound_plan)
return aggregate_results(results)
```