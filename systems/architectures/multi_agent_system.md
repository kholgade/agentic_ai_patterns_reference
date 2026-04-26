---
system: "Multi-agent System"
patterns: ["Plan-and-Solve", "Supervisor Pattern", "Mixture of Agents"]
groups: ["task-delegation"]
execution_model: "multi-agent"
scale: "small-team"
primary_concern: "flexibility"
orchestrates: ["task-decomposition", "parallel-execution", "result-aggregation"]
---

# Multi-agent System

## Overview
Planner + workers + aggregator pattern for collaborative problem solving.

## Composition
- Planner → [plan-and-solve](../../patterns/plan-and-solve/README.md)
- Workers → [supervisor-pattern](../../patterns/supervisor-pattern/README.md) (as worker agents)
- Aggregator → [mixture-of-agents](../../patterns/mixture-of-agents/README.md)

## Execution Model
Multi-agent coordination (Supervisor-worker variant)

## Flow
1. Planner decomposes task into subtasks
2. Workers execute subtasks in parallel
3. Aggregator combines worker outputs
4. Planner evaluates if goal met, else replan

## When to use
- Complex tasks requiring diverse expertise
- Parallelizable subtasks
- Need for specialized agent roles

## Trade-offs
- Coordination overhead
- Potential for inconsistent worker outputs

## Failure Modes
- Planner decomposition errors
- Worker failure causing partial results
- Aggregator bias

## Minimal Code (pseudo)
```python
subtasks = planner.decompose(task)
worker_results = [worker.execute(st) for st in subtasks]
aggregated = aggregator.combine(worker_results)
if not planner.goal_met(aggregated):
    task = planner.replan(task, aggregated)
    return multi_agent_system(task)
return aggregated
```