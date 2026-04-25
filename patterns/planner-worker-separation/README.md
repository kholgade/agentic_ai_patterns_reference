# Planner-Worker Separation

## Overview

Separate planning (task decomposition, coordination) from execution (worker agents doing actual work) for long-running multi-agent projects. Running multiple AI agents in parallel for complex, multi-week projects creates significant coordination challenges. Flat structures lead to conflicts, duplicated work, and lost context.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   PLANNER AGENT                          │
│                                                          │
│  - Breaks down project into tasks                       │
│  - Assigns tasks to workers                              │
│  - Tracks progress and dependencies                     │
│  - Resolves conflicts                                    │
│  - Maintains project state                              │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ↓           ↓           ↓
    ┌────────┐  ┌────────┐  ┌────────┐
    │Worker 1│  │Worker 2│  │Worker 3│
    │        │  │        │  │        │
    │Executes│  │Executes│  │Executes│
    │tasks   │  │tasks   │  │tasks   │
    └────────┘  └────────┘  └────────┘
```

## Implementation

```python
class PlannerWorkerSystem:
    def __init__(self, planner: Agent, workers: list[Agent]):
        self.planner = planner
        self.workers = workers
        self.task_queue = []
        self.completed_tasks = []
    
    def execute_project(self, project_goal: str):
        # Planner creates task breakdown
        plan = self.planner.generate(f"""
            Break down this project into discrete tasks:
            {project_goal}
            
            Return:
            - tasks: list of tasks with dependencies
            - estimated_effort: per task
            - required_skills: per task
        """)
        
        # Assign tasks to workers
        assignments = self._assign_tasks(plan['tasks'])
        
        # Workers execute in parallel
        results = self._execute_parallel(assignments)
        
        # Planner synthesizes results
        final_output = self.planner.generate(f"""
            Synthesize these worker results into final deliverable:
            {results}
        """)
        
        return final_output
    
    def _assign_tasks(self, tasks: list) -> dict:
        """Assign tasks to workers based on skills"""
        assignments = {}
        for task in tasks:
            # Find best worker for this task
            best_worker = self._select_worker(task['required_skills'])
            assignments[best_worker.id] = task
        return assignments
```

## When to Use

- Multi-week projects with many tasks
- Teams of specialized agents (coder, tester, documenter)
- Projects with task dependencies
- When coordination overhead is significant
- Complex refactoring or migration projects

## Related Patterns

- [Sub-Agent Spawning](../sub-agent-spawning/) - Task decomposition
- [Hierarchical Team](../hierarchical-team/) - Multi-level organization
- [Declarative Multi-Agent Topology](https://agentic-patterns.com/patterns/declarative-multi-agent-topology-definition) - Related pattern

## References

- [Planner-Worker Separation](https://agentic-patterns.com/patterns/planner-worker-separation-for-long-running-agents)
- [Multi-Agent Organizational Patterns](https://arxiv.org/abs/2308.03480)
- [CrewAI Orchestrator](https://docs.crewai.com/)