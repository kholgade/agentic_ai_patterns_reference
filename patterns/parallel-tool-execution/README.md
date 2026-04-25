# Parallel Tool Execution

## Overview

Execute independent tool calls concurrently instead of sequentially. When an AI agent decides to use multiple tools in a single reasoning step, executing them strictly sequentially creates significant delays, especially if many tools are read-only and could run concurrently.

## How It Works

```python
class ParallelToolExecutor:
    def __init__(self):
        self.tool_registry = ToolRegistry()
    
    def execute_parallel(self, tool_calls: list) -> list:
        """
        Identify independent tool calls and execute in parallel
        """
        # Build dependency graph
        graph = self._build_dependency_graph(tool_calls)
        
        # Find independent calls (no dependencies)
        independent = self._find_independent_calls(graph)
        dependent = [c for c in tool_calls if c not in independent]
        
        # Execute independent calls in parallel
        parallel_results = self._execute_concurrent(independent)
        
        # Execute dependent calls sequentially
        sequential_results = self._execute_sequential(dependent, parallel_results)
        
        return parallel_results + sequential_results
    
    def _execute_concurrent(self, calls: list) -> dict:
        """Execute independent calls concurrently"""
        from concurrent.futures import ThreadPoolExecutor
        
        def execute_call(call):
            try:
                result = self.tool_registry.execute(call.tool, call.params)
                return {'call': call, 'result': result, 'error': None}
            except Exception as e:
                return {'call': call, 'result': None, 'error': str(e)}
        
        with ThreadPoolExecutor(max_workers=len(calls)) as executor:
            futures = [executor.submit(execute_call, call) for call in calls]
            return [f.result() for f in futures]
```

## Dependency Detection

```python
def _build_dependency_graph(self, calls: list) -> dict:
    """
    Detect if call B depends on output from call A
    """
    graph = {call.id: [] for call in calls}
    
    for i, call_a in enumerate(calls):
        for j, call_b in enumerate(calls[i+1:], i+1):
            # Check if call_b references call_a's output
            if self._references_output(call_b, call_a):
                graph[call_b.id].append(call_a.id)
    
    return graph

def _references_output(self, call_b, call_a) -> bool:
    """Check if call_b uses output from call_a"""
    # Look for variable references
    pattern = f"result_{call_a.id}"
    return pattern in str(call_b.params)
```

## When to Use

- Multiple independent API calls
- Parallel database queries
- Concurrent file reads
- Batch data processing
- Multi-source data aggregation

## When NOT to Use

- Tools with side effects that affect each other
- Rate-limited APIs (respect limits)
- Tools that must execute in specific order
- When debugging (sequential is easier to trace)

## Related Patterns

- [Sub-Agent Spawning](../sub-agent-spawning/) - Parallel agents
- [Conditional Parallel Tool Execution](../conditional-parallel-tool-execution/) - Smart parallelization
- [Agent Circuit Breaker](../agent-circuit-breaker/) - Handle failures

## References

- [Parallel Tool Execution](https://agentic-patterns.com/patterns/parallel-tool-execution)
- [LangChain Parallel Map](https://python.langchain.com/docs/modules/chains/how_to/parallel)
- [Async LLM Processing](https://github.com/anyscale/academy/tree/main/llm-engineering/async-processing)