# Action Caching & Replay

## Overview

Cache LLM-based agent tool execution results to avoid redundant API calls. LLM-based agent execution is expensive (both in costs and latency) and non-deterministic. This pattern caches tool call results so identical requests return cached responses, reducing costs by 40-60% for repetitive tasks.

## How It Works

```python
import hashlib
import json
from datetime import datetime, timedelta

class ActionCache:
    def __init__(self, ttl_hours=24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, tool_name: str, params: dict) -> str:
        """Generate cache key from tool call"""
        key_data = {
            'tool': tool_name,
            'params': params
        }
        return hashlib.sha256(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()
    
    def get(self, tool_name: str, params: dict) -> any:
        """Get cached result if available and not expired"""
        key = self._generate_key(tool_name, params)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check TTL
            if datetime.now() - entry['timestamp'] < self.ttl:
                return entry['result']
            else:
                # Expired
                del self.cache[key]
        
        return None
    
    def set(self, tool_name: str, params: dict, result: any):
        """Cache tool call result"""
        key = self._generate_key(tool_name, params)
        
        self.cache[key] = {
            'result': result,
            'timestamp': datetime.now()
        }
```

## Integration

```python
class CachedAgent:
    def __init__(self):
        self.cache = ActionCache(ttl_hours=24)
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    def execute_tool(self, tool_name: str, params: dict):
        # Check cache first
        cached = self.cache.get(tool_name, params)
        
        if cached:
            self.cache_stats['hits'] += 1
            return cached
        
        # Cache miss - execute
        self.cache_stats['misses'] += 1
        result = self.tool_executor.execute(tool_name, params)
        
        # Cache result
        self.cache.set(tool_name, params, result)
        
        return result
    
    def get_cache_hit_rate(self) -> float:
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        return self.cache_stats['hits'] / total if total > 0 else 0
```

## When to Use

- Repetitive queries (same questions asked often)
- Expensive tool calls (APIs with rate limits or costs)
- Reference data lookups
- Static content generation
- Multi-agent systems with overlapping knowledge needs

## Related Patterns

- [Budget-Aware Model Routing](../budget-aware-routing/) - Cost optimization
- [Caching Memoization](../caching-memoization/) - Existing pattern in repo

## References

- [Action Caching & Replay](https://agentic-patterns.com/patterns/action-caching-replay)
- [Semantic Cache for LLMs](https://github.com/facebookresearch/llmcache)
- [Redis Cache Documentation](https://redis.io/docs/managing/patterns/caching/)