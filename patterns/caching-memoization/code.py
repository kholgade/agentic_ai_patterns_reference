import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from collections import OrderedDict

@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    ttl: Optional[float] = None
    embedding: list[float] = None

class SemanticCache:
    """LRU cache with optional semantic matching."""
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: float = 3600,
        similarity_threshold: float = 0.1,
        enable_semantic: bool = True
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.similarity_threshold = similarity_threshold
        self.enable_semantic = enable_semantic
        
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._embedding_fn: Optional[Callable[[str], list[float]]] = None
        self._hits = 0
        self._misses = 0
    
    def set_embedding_fn(self, fn: Callable[[str], list[float]]):
        """Set function to compute query embeddings."""
        self._embedding_fn = fn
    
    def _compute_hash(self, key: str) -> str:
        """Compute cache key hash."""
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between embeddings."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        hash_key = self._compute_hash(key)
        
        # Exact match
        if hash_key in self._cache:
            entry = self._cache[hash_key]
            if self._is_valid(entry):
                self._cache.move_to_end(hash_key)
                self._hits += 1
                return entry.value
            else:
                del self._cache[hash_key]
        
        # Semantic match
        if self.enable_semantic and self._embedding_fn:
            query_emb = self._embedding_fn(key)
            
            best_match = None
            best_similarity = float('-inf')
            
            for cache_key, entry in self._cache.items():
                if entry.embedding is not None:
                    similarity = self._cosine_similarity(query_emb, entry.embedding)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = (cache_key, entry)
            
            if best_match and best_similarity > self.similarity_threshold:
                hash_key, entry = best_match
                if self._is_valid(entry):
                    self._cache.move_to_end(hash_key)
                    self._hits += 1
                    return entry.value
        
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache."""
        hash_key = self._compute_hash(key)
        
        embedding = None
        if self._embedding_fn:
            embedding = self._embedding_fn(key)
        
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        
        self._cache[hash_key] = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=ttl or self.default_ttl,
            embedding=embedding
        )
    
    def _is_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid."""
        if entry.ttl is None:
            return True
        return time.time() - entry.timestamp < entry.ttl
    
    def clear(self):
        """Clear entire cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    @property
    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0
        return {
            'size': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate
        }


def cached_completion(
    cache: SemanticCache,
    compute_embedding: Optional[Callable] = None
):
    """Decorator for caching LLM responses."""
    def decorator(func: Callable):
        def wrapper(prompt: str, **kwargs):
            # Check cache
            cached = cache.get(prompt)
            if cached is not None:
                return cached
            
            # Call API
            result = func(prompt, **kwargs)
            
            # Store in cache
            cache.set(prompt, result)
            
            return result
        return wrapper
    return decorator


# Usage
cache = SemanticCache(
    max_size=500,
    default_ttl=3600,
    similarity_threshold=0.15
)

# Example embedding function (use actual embedding model in production)
def compute_embedding(text: str) -> list[float]:
    """Simplified sentence embedding."""
    import random
    random.seed(hash(text))
    return [random.random() for _ in range(512)]

cache.set_embedding_fn(compute_embedding)

# Decorator usage
@cached_completion(cache)
def call_llm(prompt: str) -> dict:
    """Make LLM API call."""
    return {"response": "Generated response", "prompt": prompt}

# First call - cache miss
result = call_llm("What is Python?")
# API call made, result cached

# Second call - exact match cache hit
result = call_llm("What is Python?")
# Returns cached response immediately

# Similar query - semantic cache hit
result = call_llm("Tell me about Python")
# Returns cached "What is Python?" response


# Example 1: LLM API Response Caching
import requests

class LLMCache:
    def __init__(self, cache: SemanticCache):
        self.cache = cache
    
    def complete(
        self, 
        prompt: str, 
        model: str = "gpt-4",
        temperature: float = 0.7,
        **kwargs
    ) -> dict:
        """Complete with caching."""
        
        # Create cache key including parameters
        cache_key = f"{prompt}|{model}|{temperature}|{json.dumps(kwargs)}"
        
        # Check cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return {**cached_result, 'cached': True}
        
        # API call
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                **kwargs
            }
        )
        
        result = response.json()
        
        # Cache result
        self.cache.set(cache_key, result, ttl=1800)  # 30 min TTL
        
        return {**result, 'cached': False}


# Example 2: Multi-Tenant Caching
class MultiTenantCache:
    def __init__(self):
        self.caches: dict[str, SemanticCache] = {}
    
    def get_cache(self, tenant_id: str) -> SemanticCache:
        """Get or create cache for tenant."""
        if tenant_id not in self.caches:
            self.caches[tenant_id] = SemanticCache(max_size=500)
        return self.caches[tenant_id]
    
    def complete(self, tenant_id: str, prompt: str) -> dict:
        """Complete with tenant-isolated caching."""
        cache = self.get_cache(tenant_id)
        
        cached = cache.get(prompt)
        if cached:
            return cached
        
        result = call_llm(prompt)
        cache.set(prompt, result)
        
        return result

def call_llm(prompt: str) -> dict:
    """Make LLM API call"""
    return {"response": "response"}