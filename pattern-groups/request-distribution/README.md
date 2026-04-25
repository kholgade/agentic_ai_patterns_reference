---
group: "Request Distribution"
patterns: ["Router Pattern", "Orchestrator Workers"]
---

# Request Distribution Patterns

## Overview

Both route/dispatch requests to workers, but differ in selection mechanism: Router selects from pre-existing handlers, Orchestrator creates dynamic tasks.

---

## Pattern Comparison

### Router Pattern

**What it does**: Classifies incoming request (intent/type), directs to appropriate pre-built handler. Selection from existing, predetermined paths.

**Flow**: Request → Classify Intent → Select Handler → Route → Response

**Routing Logic**: Rule-based or ML classifier; deterministic selection.

**Handler Count**: Fixed set of handlers (e.g., sales_handler, support_handler, billing_handler).

**Use When:**
- Request types are known and finite
- Each type requires different specialized handling
- You want to specialize handlers for accuracy
- Low-latency routing is critical
- Handlers are pre-built and optimized
- Intent classification is straightforward

**Example**: Customer inquiry → Classify as (sales/support/billing) → Route to appropriate handler.

**Cost**: Low (single classification + dispatch).

**Scalability**: Easy to add new handlers; scales linearly.

---

### Orchestrator Workers

**What it does**: Analyzes request, dynamically determines what subtasks are needed, spawns workers to execute them in parallel, aggregates results.

**Flow**: Request → Analyze & Decompose → Create Subtasks → Spawn Workers → Aggregate → Response

**Routing Logic**: Dynamic task generation per request; adaptive decomposition.

**Worker Types**: Generic workers that can handle diverse subtasks (search, analysis, lookup, etc.).

**Use When:**
- Request complexity varies widely
- Subtasks are not pre-determined
- Multiple perspectives/analyses are needed
- Subtasks can run in parallel
- Task decomposition is non-trivial
- Flexibility matters more than speed

**Example**: Research request → Decompose into (web_search, db_lookup, document_analysis) → parallelize → synthesize.

**Cost**: Higher (analysis + task creation overhead).

**Scalability**: Scales with worker availability; more complex logic.

---

## Side-by-Side Comparison

| Aspect | Router | Orchestrator |
|--------|--------|-------------|
| **Selection** | Static (from predefined handlers) | Dynamic (create per request) |
| **Routing Logic** | Intent classification | Task decomposition |
| **Handler Knowledge** | Fixed set of specialized handlers | Generic workers + composition logic |
| **Parallelism** | Limited (one handler) | Native (multiple tasks) |
| **Task Flexibility** | None (select existing) | High (compose new combinations) |
| **Best for** | Simple classification routing | Complex analysis, multi-perspective |
| **Speed** | Fast (minimal overhead) | Slower (decomposition overhead) |
| **Complexity** | Low | Medium-High |

---

## When NOT to Use

### Router Pattern - Avoid When:
- Request decomposition is needed (use Orchestrator)
- Subtasks should run in parallel
- Task combinations vary per request
- Complex analysis requiring multiple perspectives
- New task types emerge dynamically

### Orchestrator Workers - Avoid When:
- Simple intent-based routing is sufficient
- Request types are known and finite
- Decomposition overhead not justified
- Single handler per request type
- Speed is critical (latency-sensitive)
- Task types are predetermined

---

## Quick Examples

### Router Pattern
```python
intent = classify_request(user_input)  # "billing", "technical", "sales"

handlers = {
    "billing": billing_handler,
    "technical": support_handler,
    "sales": sales_handler
}

response = handlers[intent](user_input)
```

### Orchestrator Workers
```python
tasks = orchestrator.decompose(research_request)
# [{"type": "search", "query": "..."}, 
#  {"type": "db_lookup", "params": "..."}, 
#  {"type": "document_analysis", "docs": [...]}]

results = parallel_execute(tasks)
final_response = aggregate(results)
```

---

## Decision Tree

1. **Is the request type known upfront and finite?**
   - Yes → **Router Pattern**

2. **Does the request need decomposition into multiple subtasks?**
   - Yes → **Orchestrator Workers**

3. **Are subtasks independent and parallelizable?**
   - Yes → **Orchestrator**; No → Consider Prompt Chaining

---

## Summary

- **Router**: Intent classification, static handler selection. Best for predetermined request types.
- **Orchestrator**: Dynamic decomposition, parallel execution. Best for complex multi-perspective requests.
- Use Router when types are known; use Orchestrator when composition varies.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
