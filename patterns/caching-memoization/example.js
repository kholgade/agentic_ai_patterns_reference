interface CacheEntry<T> {
  value: T;
  timestamp: number;
  ttl?: number;
  embedding?: number[];
}

class SemanticCache<T> {
  private cache: Map<string, CacheEntry<T>> = new Map();
  private embeddingFn?: (text: string) => number[];
  
  constructor(
    private maxSize: number = 1000,
    private defaultTTL: number = 3600000,
    private similarityThreshold: number = 0.1
  ) {}

  setEmbeddingFn(fn: (text: string) => number[]): void {
    this.embeddingFn = fn;
  }

  private computeHash(key: string): string {
    let hash = 0;
    for (let i = 0; i < key.length; i++) {
      hash = ((hash << 5) - hash + key.charCodeAt(i)) | 0;
    }
    return hash.toString(16);
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    const dot = a.reduce((sum, x, i) => sum + x * b[i], 0);
    const normA = Math.sqrt(a.reduce((sum, x) => sum + x * x, 0));
    const normB = Math.sqrt(b.reduce((sum, x) => sum + x * x, 0));
    return dot / (normA * normB);
  }

  private isValid(entry: CacheEntry<T>): boolean {
    if (!entry.ttl) return true;
    return Date.now() - entry.timestamp < entry.ttl;
  }

  get(key: string): T | null {
    const hash = this.computeHash(key);
    
    // Exact match
    const exactEntry = this.cache.get(hash);
    if (exactEntry && this.isValid(exactEntry)) {
      return exactEntry.value;
    }
    
    // Semantic match
    if (this.embeddingFn) {
      const queryEmbedding = this.embeddingFn(key);
      let bestMatch: { key: string; entry: CacheEntry<T>; similarity: number } | null = null;
      
      for (const [cacheKey, entry] of this.cache.entries()) {
        if (entry.embedding) {
          const similarity = this.cosineSimilarity(queryEmbedding, entry.embedding);
          if (similarity > this.similarityThreshold && 
              similarity > (bestMatch?.similarity ?? -1)) {
            bestMatch = { key: cacheKey, entry, similarity };
          }
        }
      }
      
      if (bestMatch) {
        return bestMatch.entry.value;
      }
    }
    
    return null;
  }

  set(key: string, value: T, ttl?: number): void {
    const hash = this.computeHash(key);
    
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(hash, {
      value,
      timestamp: Date.now(),
      ttl: ttl ?? this.defaultTTL,
      embedding: this.embeddingFn?.(key)
    });
  }

  clear(): void {
    this.cache.clear();
  }
}

// Usage with async function
async function cachedCallLLM(
  prompt: string,
  cache: SemanticCache<string>
): Promise<string> {
  const cached = cache.get(prompt);
  if (cached) {
    return cached;
  }
  
  const response = await fetch('/api/llm', {
    method: 'POST',
    body: JSON.stringify({ prompt })
  });
  
  const result = await response.text();
  cache.set(prompt, result);
  
  return result;
}


// Example 3: Redis-Backed Distributed Cache
// import Redis from 'redis';

class DistributedCache<T> {
  // private redis: Redis;
  private localCache: SemanticCache<T>;
  
  constructor(
    private similarityThreshold: number = 0.15
  ) {
    // this.redis = new Redis();
    this.localCache = new SemanticCache(100, 300, similarityThreshold);
  }
  
  async get(key: string): Promise<T | null> {
    // Check local first
    const local = (this.localCache as any).get(key);
    if (local) return local;
    
    // Check distributed
    // const cached = await this.redis.get(key);
    // if (cached) {
    //   const parsed = JSON.parse(cached);
    //   (this.localCache as any).set(key, parsed);
    //   return parsed;
    // }
    
    return null;
  }
  
  async set(key: string, value: T, ttl: number = 3600): Promise<void> {
    const serialized = JSON.stringify(value);
    
    // Store in both local and distributed
    (this.localCache as any).set(key, value, ttl);
    // await this.redis.setex(key, ttl, serialized);
  }
}