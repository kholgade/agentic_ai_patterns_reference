---
group: "Task Delegation & Orchestration"
patterns: ["Orchestrator Workers", "Supervisor Pattern", "Hierarchical Team"]
decision_axis: "control-complexity"
spectrum: "low-to-high"
problem_statement: "How to delegate work to specialized agents"
pattern_relationship: "progressive"
---

# Task Delegation & Orchestration Patterns

## Overview

All three delegate work to specialized agents, but differ in complexity, statefulness, and organizational structure.

---

## Pattern Comparison

### Orchestrator Workers

**What it does**: Analyzes incoming request, dynamically decomposes into independent subtasks, dispatches to workers in parallel, aggregates results.

**Flow**: Request → Decompose → [Parallel Workers] → Aggregate → Response

**Statefulness**: Minimal—mainly tracks which workers are running.

**Control**: Dynamic decomposition per request.

**Use When:**
- Complex requests benefit from multi-perspective analysis
- Subtasks are independent and parallelizable
- Task decomposition varies by input
- You need fast turnaround (parallel execution)
- Subtasks are predictable/standard

**Example**: Research request → parallelize web search, document lookup, data analysis, then synthesize results.

**Cost**: Low coordination overhead; parallelism saves time.

**Scalability**: Limited by number of parallel workers (~5-10 practical limit).

---

### Supervisor Pattern

**What it does**: Central supervisor maintains state of each worker, makes context-aware routing decisions, can pause/resume workers, re-routes based on intermediate results, handles failures.

**Flow**: Request → Supervisor (intelligent routing) → [Workers with state tracking] → Re-route/Retry → Final Result

**Statefulness**: High—tracks worker state, partial results, execution history.

**Control**: Strategic, with feedback loops and adaptive decisions.

**Use When:**
- You need to monitor and adjust work mid-stream
- Partial results inform next steps
- Failure recovery is critical
- Workers have variable load or performance
- Complex dependencies between worker outputs
- Long-running workflows requiring checkpoints

**Example**: Multi-stage analysis where supervisor monitors intermediate results, decides if additional workers are needed, or re-routes based on confidence levels.

**Cost**: Higher coordination overhead; gains in robustness and adaptability.

**Scalability**: Handles more complex scenarios; scales to 10-20+ workers with proper design.

---

### Hierarchical Team

**What it does**: Multi-level organizational structure (CEO → Managers → Team Leads → Workers) with clear reporting chains, responsibility boundaries, and layered delegation.

**Flow**: Task → CEO → Managers → Team Leads → Workers → Report Up Ladder

**Statefulness**: Very high—full organizational state, reporting relationships, hierarchical decisions.

**Control**: Structured via organizational layers.

**Use When:**
- Large-scale complex projects requiring organizational structure
- Clear role differentiation and accountability chains are essential
- Information needs to flow through hierarchical layers
- Domain-specific teams need independence
- You're simulating organizational behavior
- Audit trails and accountability are critical

**Example**: Large software project where CEO delegates to engineering/QA/product managers, who delegate to team leads, who coordinate individual developers.

**Cost**: Most coordination overhead; organizational complexity.

**Scalability**: Designed for large teams (20+ members) across multiple domains.

---

## Side-by-Side Comparison

| Aspect | Orchestrator | Supervisor | Hierarchical |
|--------|-------------|-----------|-------------|
| **Complexity** | Low | Medium | High |
| **Statefulness** | Minimal | High | Very High |
| **Decomposition** | Dynamic per request | Mixed (strategic) | Predetermined |
| **Adaptability** | Limited | High (feedback-driven) | Medium |
| **Parallelism** | Yes, native | Yes, with coordination | Limited by hierarchy |
| **Control Loop** | Simple dispatch | Multi-level feedback | Reporting chain |
| **Failure Handling** | Ignore/timeout failures | Explicit recovery | Escalate up chain |
| **Best for** | Fast, parallel analysis | Complex, adaptive workflows | Large projects, accountability |
| **Practical Worker Limit** | ~5-10 | ~10-20 | Unlimited (multi-layer) |

---

## When NOT to Use

### Orchestrator Workers - Avoid When:
- Subtasks are interdependent (not parallelizable)
- You need adaptive routing based on intermediate results
- Long-running workflows requiring state management
- Worker performance varies significantly
- Organizational accountability is required
- Tasks are pre-defined and not decomposed per request

### Supervisor Pattern - Avoid When:
- Simple parallel work (overhead not justified)
- No adaptive decisions needed
- Organizational structure is required (use Hierarchical)
- Subtasks are truly independent with no feedback
- Low-latency response is critical

### Hierarchical Team - Avoid When:
- Fast execution is critical (overhead too high)
- Project is simple or small (not justified)
- No organizational structure needed
- Reporting/audit trails are unnecessary
- Parallel execution is the main requirement

---

## Quick Examples

### Orchestrator Workers
```python
subtasks = decompose_request(user_request)  # ["web_search", "db_query", "file_analysis"]
results = run_parallel([
    worker_web_search(subtasks[0]),
    worker_db_query(subtasks[1]),
    worker_file_analysis(subtasks[2])
])
return aggregate(results)
```

### Supervisor Pattern
```python
supervisor = Supervisor(workers=[analyst1, analyst2, validator])
response = supervisor.execute(request)
# Supervisor monitors each worker's output
# Decides if validation is needed
# Re-routes if confidence is low
# Handles worker failures
```

### Hierarchical Team
```python
ceo = CEO(managers=[eng_mgr, qa_mgr, product_mgr])
result = ceo.execute(strategy)
# eng_mgr delegates to team_leads
# team_leads coordinate workers
# Reports propagate back up
```

---

## Decision Tree

1. **Can subtasks run in parallel with no interdependencies?** 
   - Yes → Consider **Orchestrator Workers**
   
2. **Do you need adaptive decisions based on intermediate results?**
   - Yes → **Supervisor Pattern**
   
3. **Do you need clear organizational structure, accountability, and hierarchical reporting?**
   - Yes → **Hierarchical Team**

---

## Summary

- **Orchestrator**: Fast, parallel, dynamic decomposition. Best for analysis tasks.
- **Supervisor**: Adaptive, stateful, feedback-driven. Best for complex workflows needing recovery.
- **Hierarchical**: Structured, accountable, multi-layer. Best for large projects simulating organizations.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
