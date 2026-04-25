---
title: Retry with Backoff
description: Exponential backoff strategy for handling transient failures in API calls
complexity: low
model_maturity: mature
typical_use_cases: ["API resilience", "Failure recovery", "Reliable requests"]
dependencies: []
category: reliability
---

## Detailed Explanation

The Retry with Backoff pattern is a resilience strategy that handles transient failures in API calls by automatically retrying failed requests with increasing delays between each attempt. When an LLM API call fails—whether due to network issues, rate limiting, temporary service unavailability, or server-side errors—the pattern doesn't immediately give up but schedules subsequent retry attempts with exponentially increasing wait times. This approach prevents overwhelming struggling services while giving them time to recover, significantly improving the reliability of AI-powered applications. The exponential growth in delay (typically doubling each time) ensures that if the problem persists, retry intervals become substantial enough to avoid contributing to the failure condition.

The core principle behind exponential backoff is to balance two competing needs: retrying quickly enough to recover from brief outages, while spacing out retries enough to avoid exacerbating the problem. A basic implementation starts with a minimal delay (often 1 second), doubles it after each failure, and adds a small random jitter to prevent thundering herd problems where multiple clients retry simultaneously. Most implementations cap the maximum number of retries (commonly 3-5) and maximum delay (often 30-60 seconds) to prevent indefinite waiting. Some advanced versions also consider the type of error—rate limit errors (429) might trigger longer waits than timeout errors (500s), while authentication errors (401) should fail immediately without retry.

This pattern is essential for production AI applications because LLM APIs can be inherently unstable, especially under high load. Rate limiting is common with many providers, and brief server issues occur regularly. Without retry logic, applications fail unnecessarily; with naive retry (fixed intervals), they can amplify problems. Exponential backoff provides the robustness needed for reliable, production-grade AI systems.

## ASCII Diagrams

```
┌─────────────────────────────────────────────────────────────────┐
│                    RETRY BACKOFF FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐              │
│  │ Make     │────▶│ Request  │────▶│ Failure? │              │
│  │ Request  │     │ Succeeds │     │ Yes      │              │
│  └──────────┘     └────┬────┘     └────┬─────┘              │
│                         │               │                     │
│                         │ No            │ Yes                 │
│                         ▼               ▼                     │
│                   ┌──────────┐     ┌──────────┐              │
│                   │ Return   │     │ Increment│              │
│                   │ Response │     │ Backoff  │              │
│                   └──────────┘     └────┬─────┘              │
│                                         │                     │
│                                         ▼                     │
│                              ┌──────────────────┐             │
│                              │ Delay = min(max, │             │
│                              │ base * 2^attempt│             │
│                              │ + random_jitter)│             │
│                              └────────┬────────┘             │
│                                       │                       │
│                                       ▼                       │
│                              ┌───────────────┐               │
│                              │ Wait for      │               │
│                              │ delay seconds │               │
│                              └───────┬───────┘               │
│                                      │                       │
│                                      ▼                        │
│                              ┌───────────────┐               │
│                              │ Retry request │──────────────▶
│                              └───────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────┐
│                 BACKOFF DELAY TIMELINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Attempt 1: │███│            (1 second base)                   │
│  Attempt 2: │███████│          (2 seconds)                     │
│  Attempt 3: │█████████████│        (4 seconds)                  │
│  Attempt 4: │██████████████████████│    (8 seconds)              │
│  Attempt 5: │██████████████████████████████████████│ (16 seconds) │
│                                                                 │
│  ─────────────────────────────────────────────────────▶ Time    │
│       0s    5s   10s  15s  20s  25s  30s                        │
│                                                                 │
│  With jitter: each bar may shift ±1-2 seconds                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Code Implementation

### Python Implementation

### JavaScript/TypeScript Implementation

## Reference Links

- [AWS Exponential Backoff](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) - Official AWS guidance on backoff with jitter
- [Google Cloud Retry Documentation](https://cloud.google.com/apis/design/errorhandling) - API design best practices for retries
- [Python tenacity library](https://tenacity.readthedocs.io/) - Popular retry library for Python
- [axios-retry](https://github.com/softonic/axios-retry) - JavaScript retry interceptor for axios
- [HTTP Retry IETF RFC](https://datatracker.ietf.org/doc/html/rfc7231#section-4.2.9) - HTTP method semantics for retry


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
