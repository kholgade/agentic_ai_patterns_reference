# Tool-using Workflow Agent

## Overview
Router + executor + fallback pattern for reliable tool use.

## Composition
- Router → [router-pattern](../../patterns/router-pattern/README.md)
- Executor → [multi-tool-orchestration](../../patterns/multi-tool-orchestration/README.md)
- Fallback → [fallback-cascade](../../patterns/fallback-cascade/README.md)

## Execution Model
Hybrid (Router for decision, Orchestrator Workers for execution)

## Flow
1. Route request to appropriate tool
2. Execute tool with parameters
3. On failure, trigger fallback cascade
4. Aggregate results

## When to use
- Complex tool chains
- Unreliable external services
- Need for graceful degradation

## Trade-offs
- Increased complexity
- Latency from fallback attempts

## Failure Modes
- All fallback options exhausted
- Router misclassification

## Minimal Code (pseudo)
```python
tool = route(request)
try:
    result = execute_tool(tool, parameters)
except ToolFailure:
    result = fallback_chain(tool, parameters)
return result
```