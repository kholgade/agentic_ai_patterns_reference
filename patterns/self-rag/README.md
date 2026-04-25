---


# Self RAG
title: "Self RAG"
description: "RAG with reflective retrieval where the model decides when to retrieve."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Efficient retrieval", "Conditional grounding", "Self-aware RAG"]
dependencies: ["basic-rag"]
category: "rag"
---

# Self RAG



# 30. Self-RAG (Self-Retrieval Augmented Generation / Reflective RAG)

## Overview

Self-RAG (Self-Retrieval Augmented Generation) introduces a reflective mechanism where the model actively decides whether retrieval is needed for each part of a task. Unlike basic RAG that retrieves before generating, Self-RAG treats retrieval as a conditional, internal decision made by the language model during generation. The model learns to emit special "retrieve" tokens that signal when external knowledge would improve the response, then continues generation using the retrieved content. This approach reduces unnecessary retrieval overhead while ensuring complex queries receive appropriate grounding.

The key innovation of Self-RAG is training the LLM to generate special reflection tokens: `[RETRIEVE]` to trigger retrieval, `[ISREL]` to evaluate document relevance, `[ISSUP]` to assess whether retrieved content supports the claim, and `[Utility]` to rate overall response quality. During inference, the model generates these tokens natively, determining retrieval frequency and relevance assessment without separate classifier models. For queries that are answerable from parametric memory (simple factual recall like "What is Python?"), no retrieval occurs.

This pattern significantly improves efficiency and accuracy compared to always-retrieve approaches. By only retrieving when needed, it reduces latency and compute costs for straightforward queries while maintaining thorough grounding for complex reasoning tasks. The reflection tokens also enable better debugging—you can inspect exactly when and why the model chose to retrieve, and whether retrieved content was deemed relevant and supportive.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       SELF-RAG FLOW                                 │
└─────────────────────────────���───────────────────────────────────────┘

                         USER QUERY
                              │
                              ▼
                    ┌─────────────────────┐
                    │   LANGUAGE MODEL    │
                    │                     │
                    │  ┌───────────────┐  │
                    │  │ Generate Next │  │
                    │  │ Token         │  │
                    │  └───────┬───────┘  │
                    │          │          │
                    │    ┌─────▼─────┐    │
                    │    │ Is RETRIEVE│    │
                    │    │ Token?    │    │
                    │    └─────┬─────┘    │
                    │          │          │
                    │    ┌─────▼─────┐    │
                    │    │   RETRIEVE │    │
                    │    │ Documents  │    │
                    │    └─────┬─────┘    │
                    │          │          │
                    │    ┌─────▼─────┐    │
                    │    │  ISREL    │    │
                    │    │  Check    │    │
                    │    │ Relevance │    │
                    │    └─────┬─────┘    │
                    │          │          │
                    │    ┌─────▼─────┐    │
                    │    │  ISSUP    │    │
                    │    │  Support  │    │
                    │    │  Check    │    │
                    │    └─────┬─────┘    │
                    │          │          │
                    └──────────┼──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  GENERATE RESPONSE  │
                    │  (with reflection   │
                    │   tokens visible)   │
                    └─────────────────────┘

REFLECTION TOKENS:
┌──────────────────────────────────────────────────────┐
│ [RETRIEVE]      → Trigger external retrieval         │
│ [ISREL:relevant]→ Retrieved doc is relevant          │
│ [ISREL:irrelevant]→ Retrieved doc not helpful        │
│ [ISSUP:supported]→ Evidence supports claim           │
│ [ISSUP:partially supported]→ Partial support          │
│ [ISSUP:no support]→ Evidence contradicts             │
│ [Utility:5]     → Response quality score (0-5)       │
└──────────────────────────────────────────────────────┘
```

## Code Implementation

### Python (Using Together AI / Self-RAG Model)

### JavaScript

## Examples

### Example 1: Simple Factual Query (No Retrieval)

```
Query: "Who wrote Romeo and Juliet?"
Output: Shakespeare wrote Romeo and Juliet in 1597.[UTILITY:5]
Reflection: No [RETRIEVE] token emitted—the model answered from memory.
```

### Example 2: Complex Technical Query (Retrieval Triggered)

```
Query: "How does transformer attention mechanism work?"
Output: Transformers use [RETRIEVE]
       [ISREL:relevant] Document discusses multi-head attention...
       [ISSUP:supported] The attention formula is: Attention(Q,K,V)...
       The attention mechanism computes weighted sums of values...
       [UTILITY:5]
Reflection: Retrieved paper on attention; marked relevant and supporting.
```

### Example 3: Contradictory Evidence Handling

```
Query: "Is fasting beneficial for longevity?"
Output: [RETRIEVE]
       [ISREL:relevant] Study A shows 15% lifespan increase...
       [ISSUP:no support] Contradicts: Study B shows no significant effect
       The evidence is mixed. Some studies (Study A, n=1000) show benefits,
       while others (Study B, n=2000) found no significant correlation.
       [UTILITY:3]
Reflection: Retrieved conflicting studies; marked one as unsupported.
```

## References

- [Self-RAG Paper (Asai et al., 2024)](https://arxiv.org/abs/2310.11511)
- [Together AI Self-RAG Models](https://together.ai/blog/self-rag)
- [HuggingFace Self-RAG Implementation](https://huggingface.co/docs/transformers/en/generation_strategies)
- [Reflection Tokens in LLM Generation](https://arxiv.org/abs/2310.11511)
- [Self-RAG vs Standard RAG Benchmark](https://github.com/Arize-ai/self-rag)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
