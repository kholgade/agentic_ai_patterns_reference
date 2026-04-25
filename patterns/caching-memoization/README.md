---
title: Caching and Memoization
description: Caching LLM responses to avoid redundant API calls for repeated queries
complexity: low
model_maturity: mature
typical_use_cases: ["Response caching", "Duplicate prevention", "Performance optimization"]
dependencies: []
category: performance
---

## Detailed Explanation

Caching and Memoization is a performance optimization pattern that stores LLM responses for reuse, avoiding redundant API calls for identical or similar queries. Since LLM API calls are both computationally expensive (requiring significant GPU resources and time) and monetarily costly (charged per token), caching responses dramatically reduces latency and costs for repeated queries. The pattern works by maintaining a cache of query-response pairs, typically using a hash of the input as the key. When a request comes in, the system first checks the cache; if a matching entry exists, the cached response is returned immediately instead of making an API call. This is particularly valuable for production systems where identical queries occur frequently (FAQ responses, domain-specific explanations, repeated user questions) or where slight variations can be normalized to cached versions.

The key challenge with LLM caching is ensuring that semantically equivalent queries map to the same cache entry. Simple exact-match caching has limited utility since users rarely ask identical questions word-for-word. More sophisticated implementations use semantic caching—computing embeddings for queries and finding similar cached responses based on vector similarity rather than exact text match. This allows "What is Python?" and "Tell me about Python programming language" to hit the same cache if they're semantically similar enough (typically within 0.1-0.2 cosine distance). Additionally, cache invalidation strategies are crucial: time-based expiration (TTL) handles stale data, while semantic distance thresholds control when a cache hit occurs versus a new call.

## Reference Links

- [Semantic Cache for LLMs](https://github.com/facebookresearch/llmcache) - Facebook research on semantic caching
- [Redis Cache Documentation](https://redis.io/docs/managing/patterns/caching/) - Distributed caching best practices
- [Vector Similarity Search](https://www.pinecone.io/learn/chunking-nlp/) - Semantic search techniques
- [GPTCache](https://github.com/gptcache/G PTCache) - Open-source LLM caching library


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
