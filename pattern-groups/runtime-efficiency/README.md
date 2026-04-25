---
group: "Runtime Resilience & Efficiency"
patterns: ["Speculative Decoding", "Fallback Cascade"]
---

# Runtime Resilience & Efficiency Patterns

## Overview

Both patterns optimize runtime behavior in production. Speculative Decoding targets latency; Fallback Cascade targets reliability under failures.

---

## Pattern Comparison

### Speculative Decoding
- Small model drafts, larger model verifies/accepts tokens
- Best for reducing generation latency at scale

### Fallback Cascade
- Ordered alternatives across models/providers/prompts/tools
- Best for graceful degradation and availability SLOs

---

## Side-by-Side

| Aspect | Speculative Decoding | Fallback Cascade |
|--------|-----------------------|------------------|
| Primary objective | Latency/throughput | Reliability/availability |
| Trigger | Every generation step | Errors/timeouts/policy blocks |
| Typical architecture | Dual-model decode path | Multi-tier execution policy |
| Best for | High-QPS generation systems | Production fault tolerance |

---

## Summary

- **Speculative Decoding**: Optimize token generation speed.
- **Fallback Cascade**: Preserve service reliability when primaries fail.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
