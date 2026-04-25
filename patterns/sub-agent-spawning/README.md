# Sub-Agent Spawning

## Overview

Decompose large tasks by spawning parallel sub-agents with focused context windows. Large multi-file tasks blow out the main agent's context window and reasoning budget. Instead of one agent struggling with everything, spawn specialized sub-agents for independent subtasks.

## How It Works

```python
class SubAgentSpawner:
    def __init__(self, max_parallel=5):
        self.max_parallel = max_parallel
    
    def spawn_subagents(self, parent_task: str, subtasks: list) -> list:
        """Spawn sub-agents for independent subtasks"""
        
        # Group into batches (respect parallel limit)
        batches = self._chunk(subtasks, self.max_parallel)
        
        results = []
        for batch in batches:
            # Spawn parallel sub-agents
            batch_results = self._execute_parallel(batch, parent_task)
            results.extend(batch_results)
        
        return results
    
    def _execute_parallel(self, subtasks: list, parent_task: str) -> list:
        """Execute subtasks in parallel"""
        from concurrent.futures import ThreadPoolExecutor
        
        def run_subagent(subtask):
            # Create focused context for subtask only
            subagent_context = self._build_focused_context(subtask, parent_task)
            
            # Execute with fresh agent instance
            subagent = Agent(context=subagent_context)
            return subagent.execute(subtask)
        
        with ThreadPoolExecutor(max_workers=len(subtasks)) as executor:
            futures = [executor.submit(run_subagent, task) for task in subtasks]
            return [f.result() for f in futures]
```

## When to Use

- Multi-file code changes
- Independent component updates
- Data processing across multiple sources
- Testing multiple modules
- Documentation updates across files

## Related Patterns

- [Planner-Worker Separation](../planner-worker-separation/) - Coordination pattern
- [Parallel Tool Execution](../parallel-tool-execution/) - Parallel execution
- [Recursive Best-of-N Delegation](../recursive-best-of-n/) - Advanced delegation

## References

- [Sub-Agent Spawning](https://agentic-patterns.com/patterns/sub-agent-spawning)
- [LangGraph Multi-Agent](https://python.langchain.com/docs/modules/agents/how_to/multi-agent)
- [AutoGen Group Chat](https://microsoft.github.io/autogen/docs/API-reference/Core/GroupChat)