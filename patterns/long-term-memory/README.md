---


# Long Term Memory
title: "Long Term Memory"
description: "A pattern that persists information across multiple sessions using vector storage and embeddings."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Cross-session continuity", "User history", "Knowledge retention", "Persistent learning"]
dependencies: []
category: "memory"
---

# Long Term Memory



# Long Term Memory Pattern

The Long Term Memory pattern enables agents to retain and recall information across multiple conversation sessions, going beyond the temporary context window. While Short Term Memory resets each session, Long Term Memory persists by storing information in a vector database and retrieving relevant context when needed. This pattern uses embeddings to convert text into vectors, enabling semantic similarity search - finding relevant memories even when exact keywords don't match. The agent can "remember" user preferences, past conversations, learned facts, and accumulated knowledge.

The architecture involves three main components: an embedding model that converts text to vectors, a vector database for storage and similarity search, and a retrieval system that fetches relevant memories for each new session. When the agent receives a query, it embeds the query, searches for similar past contexts, and includes the retrieved memories in the prompt. This enables truly persistent agents that build knowledge over time across sessions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Long Term Memory System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STORAGE (Offline)                                              │
│  ┌─────────────────────────────────────────────────────────┐      │
│  │              Vector Database                          │      │
│  │  ┌─────────────────────────────────────────────────┐  │      │
│  │  │ id: 1  │ [0.1, 0.3, -0.2, ...] │ "User likes X" │  │      │
│  │  │ id: 2  │ [0.5, -0.1, 0.2, ...] │ "Fact about Y"   │  │      │
│  │  │  ...  │         ...            │      ...       │  │      │
│  │  └─────────────────────────────────────────────────┘  │      │
│  └─────────────────────────────────────────────────────────┘      │
│                         ▲                                        │
│                         │ Store                                   │
│  ──────────────────────┴─────────────────────────────────────    │
│                                                                 │
│  RETRIEVAL (Per Query)                                           │
│                                                                 │
│  Query: "What does user like?"                                   │
│         │                                                        │
│         ▼ Embed                                                 │
│  [0.1, 0.3, -0.2, ...]                                          │
│         │                                                        │
│         ▼ Similarity Search                                     │
│  Top-K matches: id:1 (0.95), id:3 (0.87)                        │
│         │                                                        │
│         ▼ Fetch                                                 │
│  "User likes X, prefers Y..."                                    │
│         │                                                        │
│         ▼ Inject                                                │
│  Prompt + Context                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Memory Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    Memory Types                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ User Profile    │    │ Preferences     │                    │
│  │  - Name         │    │  - Topics       │                    │
│  │  - Bio         │    │  - Style        │                    │
│  │  - Goals       │    │  - Format       │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ Session History │    │ Knowledge Base │                    │
│  │  - Past convos │    │  - Facts        │                    │
│  │  - Projects    │    │  - Learnings    │                    │
│  │  - Decisions   │    │  - Skills       │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: User Preferences

```
Session 1:
  User: "I prefer code examples in TypeScript"
  Agent: [stores preference]
  
Session 2:
  User: "How to parse JSON?"
  Agent: [retrieves preference] → Uses TypeScript examples
```

### Example 2: Project Context

```
User: Working on "Project Phoenix"

Agent stores:
  - "Project Phoenix: React app with Redux"
  - "Uses TypeScript, Jest for testing"
  - "API at /api/v1 endpoints"

Later session retrieves context automatically
```

### Example 3: Knowledge Base

```
Agent learns:
  "Python virtual environments use venv module"
  
Later query: "How do I set up Python?"
Agent retrieves → provides accurate context
```

## Best Practices

1. **Metadata Filtering**: Filter memories by user_id, type, date for multi-user systems
2. **Importance Scoring**: Prioritize important memories in retrieval
3. **Periodic Cleanup**: Remove outdated/irrelevant memories
4. **Embedding Updates**: Update embeddings if switching models

## Related Patterns

- [Short Term Memory](short-term-memory.md) - Session-level memory
- [RAG Patterns](../advanced-rag.md) - Retrieval-augmented generation
- [Vector Database](long-term-memory.md) - Storage backend

## References

- [ChromaDB](https://www.trychroma.com/)
- [Pinecone](https://www.pinecone.io/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Weaviate](https://weaviate.io/)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
