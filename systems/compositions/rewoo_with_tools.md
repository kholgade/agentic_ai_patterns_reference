---
system: "ReWOO + Tool Execution"
patterns: ["ReWOO", "Tool Use"]
groups: ["execution-planning"]
execution_model: "dag"
scale: "single-agent"
primary_concern: "latency"
orchestrates: ["planning", "tool-execution", "result-aggregation"]
---

# ReWOO + Tool Execution

## Idea
Use ReWOO planning with deterministic tool execution.

## Combines
- ReWOO → [rewoo](../../patterns/rewoo/README.md)
- Tool calling → [tool-use](../../patterns/tool-use/README.md)

## Why
- reduces LLM calls
- improves latency

## Constraint
- requires predictable tools

## Flow
Plan → Bind variables → Execute tools → Aggregate