---
system: "Loop Execution Model"
patterns: ["ReAct", "Reflexion"]
groups: []
execution_model: "loop"
scale: "single-agent"
primary_concern: "adaptability"
orchestrates: ["iteration", "feedback", "state-maintenance"]
---

# Loop Execution Model

## Description
Iterative execution with feedback, where output influences next input.

## Used by
- ReAct → [react](../../patterns/react/README.md)
- Reflection → [reflexion](../../patterns/reflexion/README.md)
- REPL → [react](../../patterns/react/README.md) (interactive variant)

## Properties
- adaptive
- stateful
- potentially unbounded iterations

## When NOT to use
- deterministic workflows
- cost-sensitive bounded tasks