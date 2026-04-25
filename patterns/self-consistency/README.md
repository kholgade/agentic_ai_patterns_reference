---


# Self Consistency
title: "Self Consistency"
description: "A pattern that generates multiple reasoning paths and selects the most consistent conclusion across all paths."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["Improved accuracy", "Robust reasoning", "Error reduction", "Consensus-based answers"]
dependencies: []
category: "reasoning"
---

# Self Consistency



## Overview

Self-Consistency is a prompting technique that improves reasoning accuracy by generating multiple diverse reasoning paths for the same problem and selecting the most consistent answer. The key insight is that while an LLM might make errors in any single reasoning chain, the majority of paths leading to the same answer are more likely to be correct. This ensemble-like approach leverages the model's ability to generate varied reasoning approaches and uses consensus voting to identify the most reliable conclusion.

The pattern builds on Chain-of-Thought prompting but adds a crucial enhancement: instead of taking the first reasoning path as truth, it explores many paths and checks for agreement. A reasoning path that leads to a unique answer is weighted less than one that many paths agree on. This works because different reasoning chains often make different mistakes, but the correct answer tends to emerge from multiple independent paths. The pattern is particularly effective for tasks where there's a clear correct answer and the reasoning process matters.

Self-Consistency trades off increased computation for improved accuracy. Instead of making one inference, you make N inferences (typically 5-40), each with a different reasoning path. This makes the pattern more expensive but significantly more reliable, especially for high-stakes applications. It's particularly valuable for mathematical reasoning, logical deduction, and factual question answering where accuracy matters more than speed.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SELF-CONSISTENCY FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       OVERVIEW                                           │
  └─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │   INPUT     │
                    │  QUESTION   │
                    └──────┬──────┘
                           │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │  REASONING  │  │  REASONING  │  │  REASONING  │
     │    PATH     │  │    PATH     │  │    PATH     │
     │     1       │  │     2       │  │     3       │
     │             │  │             │  │             │
     │ Step 1...   │  │ Step 1...   │  │ Step 1...   │
     │ Step 2...   │  │ Step 2...   │  │ Step 2...   │
     │ Step 3...   │  │ Step 3...   │  │ Step 3...   │
     │             │  │             │  │             │
     │ Answer: A   │  │ Answer: B   │  │ Answer: A   │
     └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
            │               │               │
            └───────────────┼───────────────┘
                            │
                            ▼
                   ┌─────────────────────┐
                   │   VOTE COUNTING     │
                   │                     │
                   │  Answer A: 2 votes  │
                   │  Answer B: 1 vote   │
                   └──────────┬──────────┘
                              │
                              ▼
                     ┌─────────────────────┐
                     │   SELECT WINNER     │
                     │                     │
                     │  Answer A (majority) │
                     └─────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       SAMPLE EXECUTION                                  │
  └─────────────────────────────────────────────────────────────────────────┘

  Question: "If all Roses are Flowers, and some Flowers are Red,
             can we conclude that some Roses are Red?"

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  PATH 1: Affirmative (INCORRECT reasoning leads to correct answer by    │
  │          coincidence)                                                    │
  │  Reasoning: "Since some flowers are red and roses are flowers, there   │
  │  might be some overlap. So some roses could be red."                   │
  │  Answer: YES (1 vote)                                                    │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  PATH 2: Negative (CORRECT reasoning)                                   │
  │  Reasoning: "The statement 'all roses are flowers' tells us roses are  │
  │  a subset of flowers. 'Some flowers are red' doesn't tell us which     │
  │  flowers. Roses could be the flowers that aren't red. We cannot        │
  │  conclude that some roses are red."                                     │
  │  Answer: NOT NECESSARILY (1 vote)                                        │
  └───────────────────────────────────────────────────────────���─��───────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  PATH 3: Negative (CORRECT reasoning - different approach)              │
  │  Reasoning: "Using set notation: roses ⊆ flowers. 'Some flowers are red'│
  │  means ∃x: flower(x) ∧ red(x). This doesn't imply ∃x: rose(x) ∧ red(x). │
  │  No valid conclusion can be drawn about roses specifically."          │
  │  Answer: NOT NECESSARILY (1 vote)                                       │
  └─────────────────────────────────────────────────────────────────────────┘

  RESULT:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  YES: 1 vote                                                           │
  │  NOT NECESSARILY: 2 votes                                              │
  │                                                                         │
  │  Selected Answer: NOT NECESSARILY (majority)                           │
  │  Note: One path was "correct by accident" but was outvoted             │
  └─────────────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Mathematical Reasoning

**Question:** "What is 15% of 200?"

```
PATH 1: "15% = 0.15. 200 × 0.15 = 30. Answer: 30" → Vote: YES
PATH 2: "10% of 200 is 20. 5% of 200 is 10. 20 + 10 = 30. Answer: 30" → Vote: YES
PATH 3: "15% × 200 = (15/100) × 200 = 15 × 2 = 30. Answer: 30" → Vote: YES
...
(8 more paths all yielding 30)

RESULT: "30" with 10/10 votes = 100% confidence
```

### Example 2: Logical Deduction

**Question:** "If it rains, the ground gets wet. The ground is wet. Can we conclude it rained?"

```
PATH 1: "Rain causes wet ground. Ground is wet. So it must have rained." → YES
PATH 2: "Could be sprinklers, spilled water, etc. Can't conclude rain." → NO
PATH 3: "Wet ground doesn't prove rain - other causes possible." → NO
PATH 4: "Correlation isn't causation. Ground could be wet for other reasons." → NO
PATH 5: "The ground being wet is consistent with rain but doesn't prove it." → NO

VOTE COUNT: YES: 1, NO: 4

RESULT: "No - we cannot conclude it rained"
Note: Multiple independent paths correctly identify the logical fallacy
```

### Example 3: Multi-Step Word Problem

**Question:** "A rectangle has perimeter 50 cm. Its length is 5 cm longer than its width. What is its area?"

```
PATH 1 (method: algebra):
- Let w = width, l = w + 5
- Perimeter: 2(w + w + 5) = 50
- 2(2w + 5) = 50 → 4w + 10 = 50 → w = 10
- Length = 15, Area = 150 cm² → Vote: 150

PATH 2 (method: guess and check):
- Try w=10: l=15, P=2(10+15)=50 ✓, A=150 → Vote: 150

PATH 3 (method: direct formula):
- L = (P/2 + extra)/2 = (25 + 5)/2 = 15
- W = 15 - 5 = 10
- A = 150 → Vote: 150

VOTE COUNT: 150 cm²: 3 votes (100%)

RESULT: "150 square centimeters"
```

## Best Practices

1. **Generate 10-40 paths** - more paths increase accuracy but at higher cost
2. **Use diverse prompts** - vary the wording or add random tokens to get different paths
3. **Normalize answers carefully** - account for equivalent representations (30 vs "30", etc.)
4. **Keep reasoning chains complete** - paths should show full reasoning, not just final answers
5. **Consider confidence thresholds** - if no answer reaches 50%, flag for human review
6. **Track voting patterns** - if two answers tie, the reasoning may need investigation
7. **Balance cost vs accuracy** - self-consistency is expensive; use selectively for high-value questions

## Variations

### Weighted Self-Consistency

Instead of simple majority voting, weight paths by self-reported confidence:

```
PATH 1: Answer A, Confidence: 0.8
PATH 2: Answer B, Confidence: 0.6
PATH 3: Answer A, Confidence: 0.9
PATH 4: Answer A, Confidence: 0.7

Weighted: A = 0.8 + 0.9 + 0.7 = 2.4, B = 0.6
Result: Answer A (with weighted score 2.4 vs 0.6)
```

### Iterative Self-Consistency

After initial voting, ask model to evaluate each reasoning path and select the most sound:

1. Generate N reasoning paths
2. Ask model to score each path for logical validity
3. Weight votes by validity scores
4. Select answer with highest weighted score

## References

- [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171) - Original paper by Wang et al. (2022)
- [Rationale-Augmented Ensembles for Self-Consistency](https://arxiv.org/abs/2305.13663) - Enhanced variants
- [Chain of Thought Prompting: Best Practices](https://www.prompteng.guide/self-consistency) - Implementation guide


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
