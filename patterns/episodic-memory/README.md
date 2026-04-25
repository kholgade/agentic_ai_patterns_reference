# Episodic Memory Retrieval

## Overview

Store and retrieve agent experiences in long-term memory for cross-session learning. Stateless request handling causes agents to repeatedly rediscover decisions, constraints, and prior failures. This pattern enables agents to learn from past interactions across sessions.

## How It Works

```python
class EpisodicMemory:
    def __init__(self, vector_store, llm_embedder):
        self.vector_store = vector_store
        self.embedder = llm_embedder
    
    def store_episode(self, episode: dict):
        """Store agent experience in memory"""
        # Create summary for retrieval
        summary = self._summarize_episode(episode)
        
        # Generate embedding
        embedding = self.embedder.embed(summary)
        
        # Store with metadata
        self.vector_store.add(
            text=summary,
            embedding=embedding,
            metadata={
                'task_type': episode['task_type'],
                'outcome': episode['outcome'],
                'lessons': episode['lessons'],
                'timestamp': episode['timestamp']
            }
        )
    
    def retrieve_relevant(self, current_context: str, top_k=3) -> list:
        """Retrieve relevant past episodes"""
        # Embed current context
        query_embedding = self.embedder.embed(current_context)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )
        
        # Format for injection into context
        return [self._format_episode(r) for r in results]
    
    def _summarize_episode(self, episode: dict) -> str:
        """Create retrieval-friendly summary"""
        return f"""
        Task: {episode['task_type']}
        Approach: {episode['approach']}
        Outcome: {episode['outcome']}
        Lessons: {episode['lessons']}
        """
```

## When to Use

- Multi-session user interactions
- Agents that should learn from mistakes
- Customer support (remember prior interactions)
- Personal assistants (learn preferences)
- Code agents (remember project conventions)

## Related Patterns

- [Context Window Auto-Compaction](../context-auto-compaction/) - Manage context
- [Long Term Memory](../long-term-memory/) - Existing pattern in repo
- [Self-Identity Accumulation](https://agentic-patterns.com/patterns/self-identity-accumulation) - Related pattern

## References

- [Episodic Memory Retrieval](https://agentic-patterns.com/patterns/episodic-memory-retrieval-injection)
- [Weaviate](https://weaviate.io/)
- [Pinecone](https://www.pinecone.io/)