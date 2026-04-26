---
group: "Sequential & Collaborative Processing"
patterns: ["Prompt Chaining", "Round Robin Collaboration"]
decision_axis: "sequencing-mechanism"
spectrum: "task-driven-to-agent-driven"
problem_statement: "How to process tasks sequentially"
pattern_relationship: "alternatives"
---

# Sequential & Collaborative Processing Patterns

## Overview

Both process tasks sequentially, but differ in structure: Chaining is step-based (different transformations), Round Robin is agent-based (same task, rotating agents).

---

## Pattern Comparison

### Prompt Chaining

**What it does**: Output of prompt N becomes input to prompt N+1. Each step applies a specialized transformation. Order is determined by task logic.

**Flow**: Input → Step 1 (Transform A) → Step 2 (Transform B) → Step 3 (Transform C) → Final Output

**Agents per Step**: Typically one specialized prompt/agent per step.

**Sequencing**: Logical (task-driven), not agent-driven.

**Use When:**
- Multi-step transformations where each stage has distinct purpose
- Earlier steps produce structured output for next steps
- You need intermediate checkpoints for validation/debugging
- Different stages require different prompts or logic
- Data pipeline with clear stages

**Example**: Data cleaning → Parsing → Validation → Normalization → Output. Each step builds on previous.

**Cost**: Predictable latency (sum of all steps).

**Flexibility**: Can branch on intermediate results (conditional chaining).

---

### Round Robin Collaboration

**What it does**: Same task passes through agents in rotation. Each agent contributes its perspective, building on what previous agents added. Cyclical, fair participation.

**Flow**: Task + Context → Agent 1 → Agent 2 → Agent 3 → Agent 1 (repeat) → Final Output

**Agents per Round**: Multiple agents, all working on same task.

**Sequencing**: Agent-based (rotation), not task-driven.

**Use When:**
- Multiple agents should all contribute to same task
- Diverse perspectives strengthen output
- Fair participation/load balancing is important
- Building consensus or refinement
- Iterative improvement from different viewpoints
- Order matters but tasks don't transform

**Example**: Writing refinement where editor 1 checks grammar, editor 2 checks style, editor 3 checks clarity, round 2 improves weaknesses. Repeat until done.

**Cost**: Variable (depends on max rounds).

**Flexibility**: Can set max rounds, can evaluate output after each agent's turn.

---

## Side-by-Side Comparison

| Aspect | Prompt Chaining | Round Robin |
|--------|-----------------|-------------|
| **Structure** | Step-based (Task stages) | Agent-based (Rotation) |
| **Agents** | Different per step | Same agents, rotating |
| **Purpose** | Transform/refine data | Consensus/multi-perspective |
| **Sequencing** | Logical (task-driven) | Fair rotation (agent-driven) |
| **Output of Step N** | Input for Step N+1 | Added to same output |
| **Intermediate Results** | Checkpoints between stages | Context for next agent |
| **Repetition** | No (each step once) | Yes (same agents, multiple rounds) |
| **Early Exit** | Conditional based on stage results | Based on quality or max rounds |
| **Best for** | Data pipelines, transformations | Collaborative refinement, consensus |

---

## When NOT to Use

### Prompt Chaining - Avoid When:
- Same agent needs multiple turns (use Round Robin)
- You want all agents to contribute equally (use Round Robin)
- No clear stage separation (use single prompt)
- Intermediate checkpoints aren't needed
- All transformations should happen in parallel
- Agents need visibility into all previous work (context explosion)

### Round Robin Collaboration - Avoid When:
- Tasks have distinct sequential stages (use Prompt Chaining)
- Agents solve different sub-problems (use Orchestrator)
- Single-pass analysis is sufficient
- You need deterministic, predictable output
- Context grows too large with multiple rounds
- Speed is critical (use parallelization)

---

## Quick Examples

### Prompt Chaining
```python
# Each step transforms data
data = load_input(user_input)

# Step 1: Extract key entities
entities = extract_entities(data)

# Step 2: Validate entities
validated = validate(entities)

# Step 3: Normalize format
normalized = normalize(validated)

return normalized
```

### Round Robin Collaboration
```python
agents = [grammar_editor, style_editor, clarity_editor]
output = initial_draft

for round in range(max_rounds):
    for agent in agents:
        output = agent.refine(output)
    
    if quality_score(output) >= threshold:
        break

return output
```

---

## When to Use Each

**Prompt Chaining** if:
- "I need to clean, then parse, then validate"
- Different operations at different stages
- Output of A directly feeds B
- Sequential stages are clear

**Round Robin** if:
- "I need multiple perspectives on the same thing"
- Same task, rotating contributors
- Building consensus/refinement
- Multiple passes improve output

---

## Summary

- **Chaining**: Different prompts, sequential stages, transform data. Pipeline pattern.
- **Round Robin**: Same task, rotating agents, collaborative refinement. Consensus pattern.
- Use Chaining for task stages; use Round Robin for agent perspectives.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
