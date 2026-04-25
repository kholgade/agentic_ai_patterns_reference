# Plan-Then-Execute Pattern

## Overview

Separate planning from execution into distinct phases instead of interleaving them (like ReAct). When planning and execution are interleaved in one loop, untrusted tool outputs can influence which action is selected next, leading to prompt injection vulnerabilities and unpredictable behavior.

## How It Works

```
Phase 1: Planning          Phase 2: Execution
─────────────────          ──────────────────
LLM creates complete       Execute pre-approved plan
plan with all steps        step-by-step
         ↓                            ↓
   Review & validate            No replanning
         ↓                            ↓
   Lock the plan              Return results
```

## Implementation

```python
class PlanThenExecuteAgent:
    def __init__(self):
        self.planner_llm = LLM()
        self.executor = ToolExecutor()
    
    def execute(self, task: str) -> dict:
        # PHASE 1: Create complete plan
        plan = self.planner_llm.generate(f"""
            Create a complete step-by-step plan to accomplish:
            {task}
            
            For each step, specify:
            - step_id: unique identifier
            - action: tool to use
            - parameters: exact parameters
            - expected_output: what we expect
            - dependencies: which prior steps this depends on
            
            Return structured plan as JSON.
        """)
        
        # Validate plan (human or automated)
        validation = self._validate_plan(plan)
        if not validation['approved']:
            raise PlanValidationError(validation['reasons'])
        
        # PHASE 2: Execute locked plan
        results = {}
        for step in plan['steps']:
            # Execute without LLM decision-making
            result = self.executor.execute(
                tool=step['action'],
                params=step['parameters']
            )
            results[step['step_id']] = result
        
        # PHASE 3: Synthesize final result
        final = self.planner_llm.generate(f"""
            Synthesize final result from these step outputs:
            {results}
        """)
        
        return {
            'plan': plan,
            'results': results,
            'final': final
        }
    
    def _validate_plan(self, plan: dict) -> dict:
        """Validate plan before execution"""
        # Check for:
        # - All steps have valid tools
        # - Dependencies are valid (no cycles)
        # - Parameters match tool schemas
        # - No untrusted data in plan
        
        return {'approved': True, 'reasons': []}
```

## When to Use

- Deterministic workflows (known steps)
- Compliance requirements (audit trail needed)
- When tool outputs are untrusted (web, APIs)
- Cost-sensitive scenarios (fewer LLM calls)
- When you need predictable, repeatable execution

## When NOT to Use

- Exploratory tasks (unknown solution path)
- When each step depends on previous results
- Creative or open-ended tasks
- When environment is highly dynamic

## Trade-offs

| Aspect | Plan-Then-Execute | ReAct (Interleaved) |
|--------|-------------------|---------------------|
| **Security** | Higher (plan locked) | Lower (vulnerable to injection) |
| **Flexibility** | Lower (can't adapt) | Higher (adapts mid-execution) |
| **LLM Calls** | Fewer (2-3 total) | More (per step) |
| **Predictability** | High | Variable |
| **Best For** | Known workflows | Exploration |

## Related Patterns

- [ReAct](../react/) - Interleaved alternative
- [ReWOO](../rewoo/) - Similar separation pattern
- [Code-Then-Execute](https://agentic-patterns.com/patterns/code-then-execute-pattern) - Code-specific variant

## References

- [Plan-Then-Execute](https://agentic-patterns.com/patterns/plan-then-execute-pattern)
- [ReWOO](../rewoo/) - Variable-bound planning
- [LLM Compiler DAG](../llm-compiler-dag/) - Compiled execution