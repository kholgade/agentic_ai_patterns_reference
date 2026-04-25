---


# Advanced RAG
title: "Advanced RAG"
description: "RAG with query transformation, reranking, and hybrid search for improved retrieval quality."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Production RAG systems", "Query reformulation", "Improved recall"]
dependencies: ["basic-rag"]
category: "rag"
---

# Advanced RAG



# 29. Advanced RAG (Query Transformation, Reranking, Hybrid Search)

## Overview

Advanced RAG elevates the basic retrieval-augmented generation pattern by addressing common failure modes: misaligned queries, poor retrieval recall, and suboptimal context ordering. The three core techniques—query transformation, reranking, and hybrid search—each solve distinct problems. Query transformation reformulates user questions to better match the vocabulary and structure of indexed documents. Reranking reorders initially retrieved candidates using a more expensive but accurate cross-encoder model. Hybrid search combines dense vector similarity with sparse keyword matching (BM25) to capture both semantic meaning and exact term matches.

Query transformation encompasses several strategies. Query expansion generates multiple reformulated versions of the original question, retrieving diverse relevant documents. Query decomposition breaks complex multi-part questions into simpler sub-queries that can be answered independently.hyde decomposes complex queries into simpler sub-queries.hyde rewrites queries using an LLM to better match document language.hyde generates sub-questions for composite questions. These transformations are particularly valuable when user queries use different vocabulary than the source documents—common in technical domains with specialized terminology.

Reranking addresses the trade-off between retrieval speed and accuracy. Initial vector search quickly retrieves candidate documents using approximate nearest neighbor algorithms, but the top-k results may not be optimally ordered. A cross-encoder model like BAAI/bge-reranker-v2-m3 re-evaluates query-document pairs by processing them jointly, producing more accurate relevance scores. This two-stage retrieval (dense search → reranking) significantly improves precision without sacrificing the speed benefits of vector search for the initial candidate generation.

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                      ADVANCED RAG FLOW                            │
└───────────────────────────────────────────────────────────────────┘

                              USER QUERY
                                   │
                    ┌──────────────▼──────────────┐
                    │   QUERY TRANSFORMATION      │
                    │  ┌────────┐ ┌─────────┐     │
                    │  │ Rewrite│ │ Expand  │     │
                    │  └────────┘ └─────────┘     │
                    │  ┌────────┐ ┌──────────┐     │
                    │  │Decompose│ │ Subquest│     │
                    │  └────────┘ └──────────┘     │
                    └──────────────┬───��───────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
            ▼                      ▼                      ▼
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │   VECTOR DB  │      │  VECTOR DB   │      │  KEYWORD DB   │
    │  (semantic)  │      │  (semantic)  │      │    (BM25)     │
    └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │    RESULT FUSION         │
                    │  (reciprocal rank/RRF)   │
                    └────────────┬─────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │       RERANKER           │
                    │   (cross-encoder model)  │
                    │  BAAI/bge-reranker-v2-m3 │
                    └────────────┬─────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │     TOP-K DOCUMENTS      │
                    │    (reordered context)   │
                    └────────────┬─────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │           LLM            │
                    │    (generate answer)     │
                    └──────────────────────────┘
```

## Code Implementation

### Python

### JavaScript

## Examples

### Example 1: Technical Documentation Search

```
User Query: "how do i make the thing go fast"
Transformed: "optimize performance parameters execution speed tuning"
Hybrid Search: Combines vector similarity for "performance optimization"
with BM25 for exact terms like "fast", "thing", "parameters"
Reranked: Technical tuning guide ranked above general speed mentions
Response: "To optimize execution speed:
  1. Set performance_mode=true in config.yaml
  2. Increase worker threads: workers: 8
  3. Enable caching: cache_enabled: true"
```

### Example 2: Legal Document Retrieval

```
User Query: "What are the termination clauses?"
Original Retrieval: Returns general contract terms
Query Decomposition: ["What triggers contract termination?",
                       "What are notice requirements?", "What are penalties?"]
Hybrid Search: Combines semantic understanding of "termination rights"
with exact matches for "Clause 14", "Section 8.2"
Response: "The contract may be terminated under:
  - Breach of material terms (Clause 14.1)
  - Failure to meet SLAs (Clause 14.2)
  - Mutual agreement with 30-day notice (Section 8.2)"
```

### Example 3: Medical Research Query

```
User Query: "side effects of long-term aspirin use"
Query Expansion: ["aspirin chronic usage adverse reactions",
                   "low-dose aspirin prolonged therapy risks",
                   "daily aspirin extended consumption complications"]
Reranking: Prioritizes clinical study citations over general health articles
Response: "Long-term aspirin use (studies: 2019-2024) shows:
  - GI bleeding risk: 1-2% annual increase
  - Hemorrhagic stroke: 0.2% additional risk
  - Protective effect against cardiovascular events: 18% reduction"
```

## References

- [Advanced RAG Techniques](https://python.langchain.com/docs/tutorials/advanced_rag/)
- [Hybrid Search with RRF](https://www.pinecone.io/learn/hybrid-search-score-reciprocal-rank-fusion/)
- [BGE Reranker Model](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- [Query Decomposition Guide](https://docs.springboard.com/retrieval/query-decomposition)
- [Cohere Reranking API](https://docs.cohere.com/docs/reranking)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
