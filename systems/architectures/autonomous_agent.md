---
system: "Autonomous Agent"
patterns: ["Plan-and-Solve", "ReAct", "Reflexion", "Evaluator Optimizer"]
groups: ["evaluation-loop"]
execution_model: "loop"
scale: "single-agent"
primary_concern: "accuracy"
orchestrates: ["planning", "action-execution", "reflection", "termination-check"]
---

# Autonomous Agent (Controlled Loop)

## Overview
Goal → plan → act → reflect → terminate loop for autonomous operation.

## Composition
- Planner → [plan-and-solve](../../[plan-and-solve](../../patterns/plan-and-solve/README.md))
- Actor → [react](../../[react](../../patterns/react/README.md)) (for tool use)
- Reflector → [reflexion](../../[reflexion](../../patterns/reflexion/README.md))
- Terminator → [evaluator-optimizer](../../[evaluator-optimizer](../../patterns/evaluator-optimizer/README.md)) (evaluation for completion)

## Execution Model
Loop (with planning and reflection)

## Flow
1. Set goal
2. Plan steps to achieve goal
3. Act using ReAct (tools if needed)
4. Reflect on action outcome
5. Evaluate if goal met or max iterations reached
6. If not, replan with new context and repeat

## When to use
- Open-ended tasks
- Need for self-improvement through reflection
- Long-horizon planning

## Trade-offs
- Higher computational cost
- Potential for infinite loops without proper termination

## Failure Modes
- Planning fallacy (overly optimistic plans)
- Reflection without improvement
- Tool misuse in action phase

## Minimal Code (pseudo)
```python
goal = set_goal()
max_iterations = 10
for i in range(max_iterations):
    plan = planner.plan(goal, context)
    action_result = actor.act(plan)
    reflection = reflector.reflect(action_result)
    if terminator.evaluate(reflection, goal):
        break
    context = update_context(context, reflection)
return reflection
```