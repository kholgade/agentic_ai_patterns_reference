---


# Corrective RAG
title: "Corrective RAG"
description: "RAG with self-evaluation and corrective actions for knowledge verification."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Accuracy-critical applications", "Self-correcting retrieval"]
dependencies: ["basic-rag", "self-rag"]
category: "rag"
---

# Corrective RAG



# 31. Corrective RAG (CRAG / Knowledge Correction)

## Overview

Corrective RAG introduces a self-evaluation loop that verifies the quality and relevance of retrieved information before using it for generation. The pattern adds a critical "critic" component that assesses whether retrieved documents actually support the generated answer, whether they are relevant to the query, and whether the generated response is accurate. When evaluation fails, CRAG triggers corrective actions ranging from query reformulation and re-retrieval to direct answer fallback or external search. This closed-loop architecture significantly reduces hallucinations by catching and correcting errors before they reach the user.

The key insight behind CRAG is that retrieval is inherently imperfect—vector similarity doesn't guarantee semantic relevance, and retrieved chunks often lack sufficient context for accurate answers. Rather than assuming retrieval always succeeds, CRAG treats retrieval as a hypothesis to be verified. The critic evaluates two dimensions: document-level relevance (do documents address the query?) and claim-level support (do retrieved facts support specific claims in the answer?). When either check fails, the system can self-correct before generating a potentially misleading response.

CRAG typically implements a decision tree of corrective actions. If retrieved documents are highly relevant and supportive, proceed with generation. If documents are somewhat relevant but lack specific support, try re-retrieval with a different query or expanded context. If documents are irrelevant, perform web search or query rewrite. If the model generates a confident but unsupported claim, flag for human review or fallback to "I don't know." This adaptive approach balances thoroughness with efficiency, escalating corrective effort only when needed.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CORRECTIVE RAG FLOW                             │
└─────────────────────────────────────────────────────────────────────┘

                      USER QUERY
                           │
                    ┌──────▼──────┐
                    │  RETRIEVE   │
                    │  DOCUMENTS  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    CRITIC   │
                    │  EVALUATOR  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
      ┌───────────┐ ┌───────────┐ ┌───────────┐
      │ RELEVANT  │ │ PARTIAL   │ │IRRELEVANT │
      │   HIGH    │ │  MATCH    │ │  (LOW)    │
      └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
            │             │             │
            ▼             │             │
    ┌──────────────┐      │             │
    │ VERIFY CLAIMS│      │             │
    └─────┬───────┘      │             │
          │               │             │
    ┌─────┴─────┐         │             │
    │           │         │             │
    ▼           ▼         ▼             ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│SUPPORTED│ │PARTIAL │ │RE-RETRIEVE│ │  WEB     │
│         │ │/REFORM│ │  (diff   │ │  SEARCH  │
│         │ │        │ │  query)  │ │          │
└────┬────┘ └───┬────┘ └────┬─────┘ └────┬────┘
     │          │           │             │
     ▼          ▼           └─────────────┘
┌────────────────────┐              │
│   LLM GENERATE     │◄─────────────┘
│   (grounded)       │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│   VERIFY OUTPUT    │
│   (claim check)    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│   FINAL RESPONSE   │
└────────────────────┘

CORRECTIVE ACTIONS:
┌──────────────────────────────────────────────────────┐
│ Level 0: No correction - High relevance, supported   │
│ Level 1: Self-RAG - Partial match, re-retrieve       │
│ Level 2: Query rewrite - Low relevance               │
│ Level 3: Web search - No local documents match        │
│ Level 4: Fallback - "I don't have this information"  │
└──────────────────────────────────────────────────────┘
```

## Code Implementation

### Python (Using LangChain Expression Language)

### JavaScript

## Examples

### Example 1: High-Relevance Response

```
Query: "How do I configure OAuth 2.0 in Keycloak?"
Retrieval: Returns Keycloak documentation about OAuth setup
Relevance Score: 9/10
Corrective Action: high
Response: "To configure OAuth 2.0 in Keycloak:
  1. Navigate to Clients → Create Client
  2. Set Client Protocol: openid-connect
  3. Configure Valid Redirect URIs..."
```

### Example 2: Re-Retrieval with Expanded Query

```
Query: "mitochondrial DNA inheritance patterns"
Retrieval: Returns general genetics content, score 4/10
Relevance Score: 4/10
Corrective Action: retry
Expanded Query: "maternal inheritance mitochondrial DNA chromosome"
Re-retrieval: Returns specific mitochondrial inheritance documentation
Final Response: "Mitochondrial DNA is exclusively inherited maternally..."
```

### Example 3: Web Search Fallback

```
Query: "Latest developments in AI regulation EU 2024"
Retrieval: Returns policy documents from 2023
Relevance Score: 3/10
Corrective Action: web
Web Search: Retrieves latest 2024 news about EU AI Act
Response: "The EU AI Act passed final vote in March 2024, with full
  enforcement beginning in 2026..."
```

## References

- [Corrective RAG Paper (Yan et al., 2024)](https://arxiv.org/abs/2401.15884)
- [LangChain RAG with Evaluation](https://python.langchain.com/docs/tutorials/rag/#custom-retrieval-and-reranking)
- [Self-RAG vs Corrective RAG](https://github.com/your-tech/self-rag)
- [Tavily Search API](https://tavily.com)
- [Evaluation Metrics for RAG](https://docs.ragas.io/)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
