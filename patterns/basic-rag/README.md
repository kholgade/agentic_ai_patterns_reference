---


# Basic RAG
title: "Basic RAG"
description: "The foundational retrieve-then-generate pattern for grounding LLM responses in external knowledge."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["Q&A systems", "Documentation search", "Knowledge base assistants"]
dependencies: []
category: "rag"
---

# Basic RAG



# 28. Basic RAG (Retrieval-Augmented Generation)

## Overview

Basic RAG is the foundational pattern for building LLM applications that can access external knowledge. It combines the parametric knowledge of a language model with the factual retrieval from a knowledge base, enabling models to answer questions about information they weren't trained on. The pattern works by embedding user queries into vector representations, searching a pre-indexed corpus for relevant documents, and then feeding those documents to the LLM as context for generation. This architecture separates concerns cleanly—retrieval handles information access while generation handles response synthesis.

The retrieval component typically uses a vector database like Pinecone, Weaviate, Chroma, or pgvector. Documents are chunked, embedded using models like OpenAI embeddings or open-source alternatives like BGE, and stored with their vectors. At query time, the same embedding model converts the query, and similarity search retrieves the top-k documents. The generation component receives both the retrieved context and the original question, instructing the LLM to answer based solely on the provided context. This grounding reduces hallucinations and enables verifiable, citeable responses.

Basic RAG works well for straightforward Q&A, documentation search, and knowledge base assistants. Its simplicity makes it easy to implement and debug, while its modularity allows swapping embedding models, vector stores, or LLMs independently. The pattern forms the baseline against which more advanced RAG strategies are measured. Performance depends heavily on chunking strategy, embedding quality, and the relevance of retrieved documents to user queries.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      BASIC RAG FLOW                         │
└──────────────────────────────────��──────────────────────────┘

  ┌──────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────┐
  │  USER    │───▶│  EMBEDDER   │───▶│  VECTOR DB   │───▶│   LLM    │
  │  QUERY   │    │  (query)    │    │  (similarity │    │ (generate│
  └──────────┘    └─────────────┘    │   search)    │    │  answer) │
                                      └──────┬───────┘    └────┬─────┘
                                             │                  │
                                      ┌──────▼───────┐    ┌─────▼─────┐
                                      │   RETRIEVED  │    │ RESPONSE  │
                                      │  DOCUMENTS   │    │ (grounded │
                                      └──────────────┘    │ in docs)  │
                                                         └──────────┘

INDEXING PHASE:
  ┌────────────┐    ┌─────────────┐    ┌──────────────┐
  │  RAW DOCS  │───▶│  CHUNKING   │───▶│  EMBEDDER    │
  └────────────┘    └──────┬──────┘    │  (documents) │
                            │           └──────┬───────┘
                            ▼                  ▼
                     ┌──────────────┐   ┌──────────────┐
                     │ TEXT CHUNKS │──▶│ VECTOR STORE │
                     └─────────────┘   └──────────────┘
```

## Code Implementation

### Python (Using LangChain)

### JavaScript (Using LangChain.js)

## Examples

### Example 1: Internal Documentation Q&A

```
User: "How do I reset the production database?"
Retrieval: Returns chunks about database administration, backup procedures,
           and disaster recovery protocols.
Response: "To reset the production database, follow these steps:
           1. Ensure you have backup confirmation from the last 24 hours
           2. Request approval from the DBA team lead
           3. Execute the reset script from the /scripts directory
           [Reference: ops-manual.md, section 4.2]"
```

### Example 2: Customer Support Knowledge Base

```
User: "I was charged twice for my subscription"
Retrieval: Returns policies about billing, refund procedures, charge disputes.
Response: "I apologize for the duplicate charge. Based on our policy,
           duplicate charges are refunded within 5-7 business days.
           Your case ID is #12345. Is there anything else I can help with?"
```

### Example 3: Research Paper Summarization

```
User: "What methodology did the paper use?"
Retrieval: Returns sections from the research paper mentioning methodology.
Response: "The paper employed a mixed-methods approach consisting of
           quantitative surveys (n=500) and qualitative interviews
           (n=30) conducted over a 6-month period."
```

## References

- [LangChain RAG Documentation](https://python.langchain.com/docs/tutorials/rag/)
- [Pinecone RAG Architecture](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Chroma Vector Database](https://docs.trychroma.com/)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
