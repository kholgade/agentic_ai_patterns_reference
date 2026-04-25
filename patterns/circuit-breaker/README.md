---
title: Circuit Breaker
description: Pattern to prevent cascading failures by opening circuit after threshold failures
complexity: medium
model_maturity: mature
typical_use_cases: ["Failure isolation", "System protection", "Graceful degradation"]
dependencies: []
category: reliability
---

## Detailed Explanation

The Circuit Breaker pattern is a resilience mechanism that prevents cascading failures in AI systems by detecting when a service or component is experiencing repeated failures and temporarily halting requests to it. Originally derived from electrical engineering (where a circuit breaker trips to prevent damage from excessive current), this pattern in software operates in three distinct states: closed, open, and half-open. In the closed state, requests flow normally to the LLM API; when failure count exceeds a defined threshold, the circuit transitions to open state, immediately failing all requests without calling the API; after a timeout period, the circuit enters half-open state, allowing a limited number of test requests through to check if the service has recovered. This approach prevents overwhelming struggling services, gives them time to recover, and provides graceful degradation for the application.

For AI applications specifically, circuit breakers are invaluable because LLM APIs can experience various forms of degradation: complete outages (returns 500 errors), rate limiting (429 errors), latency spikes (timeout errors), or quality degradation (returning malformed responses). Without a circuit breaker, an application might continue hammering a struggling API, amplifying the problem and causing downstream failures in dependent systems. By opening the circuit, the system fails fast with a cached response or error message rather than waiting for timeouts, dramatically improving perceived reliability. The half-open state ensures the system automatically recovers when the API health improves, without requiring manual intervention.

This pattern becomes even more critical in complex AI systems using multiple models (e.g., primary and fallback), external tools, or third-party services. A single degraded service can cascade through the entire system; circuit breakers isolate failures, allowing other components to function normally while the problematic service recovers.

## ASCII Diagrams

```
┌───────────────────────────────────────────────────────────────────────────┐
│                     CIRCUIT BREAKER STATES                         │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                   │
│    ┌──────────┐                        ┌──────────┐             │
│    │ CLOSED   │────────────────────────▶│  OPEN    │             │
│    │ Normal  │   X failures threshold  │ Fail Fast│             │
│    │ Request │                        │          │             │
│    └──────────┘                        └────┬─────┘             │
│         ▲                                      │                   │
│         │          Success                    │ Timeout            │
│         │          resets                     │ elapses            │
│         │          counter                   │                    │
│         │                                      ▼                    │
│         │                             ┌──────────────┐             │
│         │                            │  HALF-OPEN   │             │
│         │                            │  Test Request│             │
│         │                            └──────┬───────┘             │
│         │                                   │                      │
│         │                   Success        │ Failure              │
│         └───────────────────────────────────┘                      │
│                                                                   │
└───────────────────────────────────────────────────────────────────────────┘
```

## Reference Links

- [Circuit Breaker Pattern - Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html) - Original pattern description
- [ Resilience patterns: Circuit Breaker](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) - Microsoft architecture patterns
- [Hystrix Circuit Breaker](https://github.com/Netflix/Hystrix) - Netflix implementation reference
- [Polly .NET Resilience](https://github.com/App-vNext/Polly) - Popular .NET resilience library
- [Resilience4j Circuit Breaker](https://resilience4j.readme.io/docs/circuitbreaker) - Java resilience library


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
