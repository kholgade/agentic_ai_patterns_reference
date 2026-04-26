---
system: "Hybrid Execution Model"
patterns: ["Orchestrator Workers"]
groups: ["task-delegation"]
execution_model: "hybrid"
scale: "variable"
primary_concern: "flexibility"
orchestrates: ["loop-execution", "dag-execution", "sub-workflow-calling"]
---

# Hybrid Execution Model

## Description
Combination of different execution paradigms (e.g., loop within DAG, or agent calling sub-workflows).

## Used by
- Orchestrator Workers → [orchestrator-workers](../../patterns/orchestrator-workers/README.md)
- Tool-using workflow agent → systems/architectures/tool_using_agent.md

## Properties
- flexible
- adaptable
- can handle both deterministic and uncertain components

## When NOT to use
- simple purely sequential tasks
- when a single paradigm suffices