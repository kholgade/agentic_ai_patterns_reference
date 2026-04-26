---
group: "Standalone Patterns"
patterns: ["Parallelization", "Publish-Subscribe"]
decision_axis: "infrastructure-concern"
spectrum: "throughput-to-decoupling"
problem_statement: "How to handle batch processing and event distribution"
pattern_relationship: "complementary"
---

# Standalone Patterns

## Overview

These patterns serve distinct purposes and don't overlap significantly with other patterns. They address fundamental architectural concerns.

---

## Pattern Breakdown

### Parallelization

**What it does**: Executes multiple independent tasks simultaneously using Map-Reduce. Maps tasks across parallel workers, reduces results into unified output.

**Flow**: Input Data (batch) → Map Phase [Worker 1, Worker 2, Worker 3] → Reduce Phase → Aggregated Output

**Use Cases**: Batch processing, concurrent operations, independent subtasks.

**Use When:**
- Multiple independent inputs share same processing logic
- Single complex task decomposes into independent subtasks
- Overall throughput matters more than per-item latency
- Batch processing is desired

**Example**: Summarize 1000 documents → process in parallel (10 workers × 100 docs) → aggregate summaries.

**Cost**: Baseline + parallel overhead; gains in throughput.

**Speed**: ~N times faster with N workers (minus coordination overhead).

---

### Publish-Subscribe

**What it does**: Event-driven communication via message broker. Publishers emit events on topics; subscribers receive relevant updates asynchronously. Decouples producers from consumers.

**Flow**: Publisher → Topic/Channel → Message Broker → Subscribers (parallel notification)

**Use Cases**: Event-driven systems, decoupled communication, real-time notifications, event sourcing.

**Use When:**
- Multiple agents need to react to events without tight coupling
- Asynchronous communication is acceptable/desired
- Many-to-many communication patterns are needed
- Real-time updates matter
- System should scale beyond point-to-point connections
- Loose coupling is a priority

**Example**: Data processing triggers visualization, analysis, and user notification simultaneously via event topics.

**Cost**: Message broker overhead; gains in decoupling and scalability.

**Latency**: Slight increase (async), but enables many-to-many at scale.

---

## Characteristics

| Aspect | Parallelization | Pub-Sub |
|--------|-----------------|---------|
| **Communication** | Request-response (batch) | Event-driven (async) |
| **Coupling** | Tight (caller waits) | Loose (fire-and-forget) |
| **Timing** | Synchronous (reduce waits for map) | Asynchronous (immediate return) |
| **Use Case** | Throughput optimization | Event distribution |
| **Coordination** | Centralized (reduce aggregates) | Decentralized (broker routes) |
| **Scalability** | Linear with worker count | Scales beyond number of agents |

---

## When NOT to Use

### Parallelization - Avoid When:
- Tasks are interdependent (must run sequentially)
- Single task is critical path (parallel gains negligible)
- Batch size is small (overhead not justified)
- Latency is critical for each task (use sequential)

### Pub-Sub - Avoid When:
- Direct response is needed (use request-response)
- Message ordering is critical and complex
- Guaranteed delivery at specific SLA is required
- Single consumer pattern (simpler solutions exist)
- Audit trail of every message exchange is required

---

## Quick Examples

### Parallelization
```python
documents = load_batch(1000)  # 1000 docs

# Map phase
summaries = parallel_map(
    lambda doc: summarize(doc),
    documents,
    num_workers=10
)

# Reduce phase
final_report = aggregate_summaries(summaries)
```

### Pub-Sub
```python
# Publisher
def process_data(data):
    broker.publish("data.processed", {"content": data, "timestamp": now()})

# Subscriber 1 (visualization)
broker.subscribe("data.processed", visualize_handler)

# Subscriber 2 (alert)
broker.subscribe("data.processed", alert_handler)

# Both visualize and alert happen independently
process_data(new_data)  # Returns immediately
```

---

## When to Use Each

| Scenario | Pattern |
|----------|---------|
| Need faster throughput on batch | Parallelization |
| Multiple agents should react to event | Pub-Sub |
| Process 1000 items faster | Parallelization |
| Real-time notifications to multiple systems | Pub-Sub |
| Reduce latency on single task | Neither (won't help) |
| Decouple producer from consumer | Pub-Sub |

---

## Summary

- **Parallelization**: Speed via concurrent execution. For batch throughput.
- **Publish-Subscribe**: Decoupling via event distribution. For event-driven systems.
- Neither are decision patterns (like Router or Debate); both are architectural infrastructure choices.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
