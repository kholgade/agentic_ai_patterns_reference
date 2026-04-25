---
title: Few-Shot Learning
description: Providing examples in prompts to guide LLM behavior without fine-tuning
complexity: low
model_maturity: mature
typical_use_cases: ["Task guidance", "Format examples", "Behavior shaping"]
dependencies: []
category: prompting
---

## Detailed Explanation

Few-shot learning in the context of LLMs involves providing a small number of examples (typically 1-5) within the prompt to demonstrate the desired task behavior, format, or reasoning pattern. These examples serve as in-context learning - the model learns from the demonstration without any weight updates or fine-tuning. The key insight is that LLMs can infer patterns from just a few examples and apply them to new, unseen inputs. This makes few-shot learning an extremely powerful and efficient technique for shaping model outputs without the computational cost of training.

Dynamic few-shot learning extends this basic concept by intelligently selecting which examples to include based on the specific input being processed. Rather than using a fixed set of examples, the system retrieves the most relevant examples from a larger pool, considering factors like similarity to the input, diversity of demonstrations, and specific formatting requirements. This approach acknowledges that different inputs may require different types of examples for optimal performance. The retrieval mechanism can be simple (keyword matching) or sophisticated (semantic embedding similarity), and the selection can happen at runtime for each new input.

## ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 FEW-SHOT LEARNING FLOW                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  STATIC FEW-SHOT (Fixed Examples)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐        │
│  │ Example 1 │ +  │ Example 2 │ +  │ Example 3 │  ──▶  │
│  │ "Input → │    │ "Input → │    │ "Input → │        │
│  │  Output" │    │  Output" │    │  Output" │        │
│  └───────────┘    └───────────┘    └───────────┘        │
│        │             │             │                   │
│        └─────────────┴─────────────┴───┐               │
│                                       ▼               │
│                        ┌─────────────────────────┐      │
│                        │      LLM Inference     │      │
│                        │  + New Input           │      │
│                        │  = Learned Pattern    │      │
│                        └─────────────────────────┘      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  DYNAMIC FEW-SHOT (Selected Examples)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │  Example     │    │  Example     │                   │
│  │   Pool       │    │   Pool       │                   │
│  │ ┌────────┐  │    │ ┌────────┐  │                   │
│  │ │ Ex 1   │  │    │ │ Ex 5   │  │                   │
│  │ │ Ex 2   │  │    │ │ Ex 6   │  │                   │
│  │ │ Ex 3   │  │    │ │ Ex 7   │  │                   │
│  │ │ Ex 4   │  │    │ │ ...   │  │                   │
│  │ └────────┘  │    │ └────────┘  │                   │
│  └──────────────┘    └──────────────┘                   │
│         │                      │                          │
│         ▼                      ▼                          │
│  ┌──────────────────────────────────────────┐          │
│  │        Semantic Similarity Retrieval        │          │
│  │   (Select k-most relevant examples)      │          │
│  └──────────────────────────────────────────┘          │
│                      │                                   │
│                      ▼                                   │
│         ┌────────────────────────┐                       │
│         │       LLM + Examples  │                       │
│         │      = Task Output    │                       │
│         └────────────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Format Specification

Examples demonstrating required JSON structure, input for extracting structured data results in perfectly formatted output without telling the model to "output JSON."

### Example 2: Tone and Style

Using examples with specific writing styles (formal email, casual chat, technical documentation) to guide the model to match the desired tone without explicit instruction.

### Example 3: Reasoning Pattern

Showing examples where intermediate reasoning steps are displayed teaches the model to show its work on complex problems, improving accuracy on math and logic tasks.

## Reference Links

- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) - Original paper introducing few-shot learning in LLMs
- [GPT-3 Paper: Few-Shot Performance](https://arxiv.org/abs/2005.14165) - In-context learning analysis
- [Prompting Guide: Few-Shot Examples](https://www.promptingguide.ai/techniques/few-shot) - Practical guidance for effective examples


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
