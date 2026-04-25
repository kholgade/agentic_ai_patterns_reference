---


# Reflexion
title: "Reflexion"
description: "A pattern where the agent reflects on its own outputs and uses that reflection to improve future responses."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["Self-correction", "Learning from mistakes", "Iterative improvement", "Quality assurance"]
dependencies: []
category: "reasoning"
---

# Reflexion



## Overview

Reflexion is a self-reflective prompting pattern where an AI agent evaluates its own outputs, identifies weaknesses or errors, and generates improved responses based on that reflection. Unlike patterns that treat each inference as independent, Reflexion creates a feedback loop where the agent learns from past outputs. The pattern draws inspiration from how humans often reconsider their work—drafting, reviewing, and revising—recognizing that initial outputs are rarely optimal and that reflection enables continuous improvement.

The pattern typically involves three components: an actor that generates responses, a critic that evaluates those responses against criteria or historical feedback, and a reflection mechanism that summarizes lessons learned. The actor and critic can be the same model using different system prompts, or separate prompts optimized for each role. The key insight is that evaluation and generation require different mental modes—generative thinking is fluent and confident, while evaluative thinking is skeptical and detail-oriented.

Reflexion is particularly valuable for complex, multi-step tasks where errors can compound, for tasks requiring adherence to specific formats or rules, and for iterative workflows where quality improves over time. The pattern has shown strong results in coding tasks, writing tasks, and decision-making where the agent can compare its outputs against expected outcomes or explicit criteria. It's a foundation for building AI systems that genuinely improve through experience.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REFLEXION LOOP                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                     ACTOR-CRITIC LOOP                                     │
  └─────────────────────────────────────────────────────────────────────────┘

       ┌─────────────────────────────────────────────────────────────────┐
       │                    EXTERNAL FEEDBACK                             │
       │            (test results, user input, etc.)                   │
       └────────────────────────────┬────────────────────────────────────┘
                                    │
       ┌───────────────────────────┼───────────────���───────────┐
       ▼                           ▼                           │
 ┌─────────────┐               ┌─────────────┐                   │
 │    ACTOR   │──────────────▶│   CRITIC    │                   │
 │            │   Generate    │             │   Evaluate        │
 │  Generate  │               │  Identify    │                   │
 │  response  │◀──────────────│  issues     │◀──────────────────┘
 │            │   Improved    │  and        │   Provide         │
 │            │   guidance    │  feedback   │   feedback        │
 └─────────────┘               └──────┬──────┘
                                       │
                                       ▼
                             ┌─────────────────────┐
                             │   REFLECTOR       │
                             │                   │
                             │  Synthesize       │
                             │  lessons and      │
                             │  update context   │
                             └─────────┬─────────┘
                                       │
                                       ▼
                             ┌─────────────────────┐
                             │   MEMORY/STORAGE   │
                             │                    │
                             │  Store reflection  │
                             │  for future use    │
                             └─────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       DETAILED ITERATION FLOW                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ITERATION 1                                                            │
  │  ┌───────────┐                                                          │
  │  │ ACTOR     │                                                          │
  │  │ "Write a  │                                                          │
  │  │  function │                                                          │
  │  │ to sort" │                                                          │
  │  └─────┬─────┘                                                          │
  │        │                                                                 │
  │        ▼                                                                 │
  │  ┌──────────────────────────────────────────────────────────────────┐    │
  │  │ OUTPUT:                                                           │    │
  │  │ def sort(arr):                                                    │    │
  │  │     return sorted(arr)                                             │    │
  │  └─────┬──────────────────────────────────────────────────────────────┘    │
  │        │                                                                 │
  │        ▼                                                                 │
  │  ┌───────────┐                                                          │
  │  │ CRITIC    │                                                          │
  │  │ "No tests │                                                          │
  │  │  passed,  │                                                          │
  │  │  O(n log  │                                                          │
  │  │  n) ok but│                                                          │
  │  │  missing │                                                          │
  │  │ explain" │                                                          │
  │  └─────┬─────┘                                                          │
  │        │                                                                 │
  │        ▼                                                                 │
  │  ┌───────────────────────────────────────────────────────────────────┐   │
  │  │ REFLECTION:                                                        │   │
  │  │ "Critic notes: (1) Tests not passing, (2) Should add comments,    │   │
  │  │ (3) Should handle edge cases. Will incorporate in next draft."    │   │
  │  └───────────────────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ITERATION 2 (with reflection context)                                  │
  │  ┌───────────┐                                                          │
  │  │ ACTOR     │                                                          │
  │  │ "Using    │                                                          │
  │  │  previous │                                                          │
  │  │  critic  │                                                          │
  │  │  feedback│                                                          │
  │  │  and     │                                                          │
  │  │  reflect"│                                                          │
  │  └─────┬─────┘                                                          │
  │        │                                                                 │
  │        ▼                                                                 │
  │  ┌──────────────────────────────────────────────────────────────────┐    │
  │  │ OUTPUT:                                                           │    │
  │  │ def sort(arr):                                                    │    │
  │  │     """Sort array using Timsort - O(n log n) average.""""""         │    │
  │  │     if not arr: return []                                         │    │
  │  │     return sorted(arr)  # Python's Timsort                          │    │
  │  │                                                                  │    │
  │  │ # All tests pass                                                 │    │
  │  └────────────────────────────────────────────────────────────────────�─┘    │
  │        │                                                                 │
  │        ▼                                                                 │
  │  ┌───────────┐                                                          │
  │  │ CRITIC    │                                                          │
  │  │ "Tests    │                                                          │
  │  │  pass,    │                                                          │
  │  │ docstring│                                                          │
  │  │ present" │                                                          │
  │  └─────┬─────┘                                                          │
  │        │                                                                 │
  │        ▼                                                                 │
  │  ┌───────────────────────────────────────────────────────────────────┐   │
  │  │ REFLECTION: "Issue resolved. Code now passes tests and has proper   │   │
  │  │ documentation. Consider this task complete."                       │   │
  │  └───────────────────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Code Improvement

**Task:** "Write a function to calculate factorial recursively"

```
ITERATION 1:
ACTOR OUTPUT:
function factorial(n) {
    return n * factorial(n - 1);
}

CRITIC FEEDBACK:
Issues:
1. Missing base case - will cause infinite recursion for n=0
2. No validation for negative numbers
3. No handling for non-integer inputs
4. Risk of stack overflow for large n
5. No type documentation

REFLECTION:
Must add base case (n <= 1), validate inputs, handle edge cases.

ITERATION 2:
ACTOR OUTPUT (improved):
/**
 * Calculate factorial of n
 * @param {number} n - non-negative integer
 * @returns {number} factorial result
 */
function factorial(n) {
    if (n < 0) throw new Error("Negative numbers not allowed");
    if (!Number.isInteger(n)) throw new Error("Must be integer");
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

CRITIC FEEDBACK:
Passes all test cases. Clear documentation. Consider memoization for large inputs.

REFLECTION:
Task complete. Note memoization for future performance optimization.

FINAL: Function now handles edge cases properly.
```

### Example 2: Writing Task

**Task:** "Write a product description for a new wireless headphone"

```
ITERATION 1:
ACTOR: "Introducing our new wireless headphones..."
CRITIC: "Generic, no unique selling points mentioned, no emotional appeal"
REFLECTION: "Need to identify unique features and add benefits"

ITERATION 2:
ACTOR: "Crystal-clear audio meets all-day comfort..."
CRITIC: "Better but missing price point and target audience"
REFLECTION: "Include target demographic and value proposition"

ITERATION 3:
ACTOR: [Complete product description with features, benefits, audience, price]
CRITIC: "Complete and compelling. Ready for publication."

FINAL: Polished product description ready for use.
```

### Example 3: Decision Making

**Task:** "Recommend a technology stack for a startup's first product"

```
ITERATION 1:
ACTOR: "Use React for frontend, Node.js for backend..."
CRITIC: "No consideration of team skills or project timeline"
REFLECTION: "Context matters - assess constraints first"

ITERATION 2 (with context):
ACTOR: "Given your small team and need to ship fast..."
CRITIC: "Good but missing cost and scalability considerations"
REFLECTION: "Add resource constraints and growth planning"

ITERATION 3:
ACTOR: [Full recommendation with options based on different scenarios]
CRITIC: "Comprehensive analysis with clear tradeoffs. Good decision framework."

FINAL: Recommendation with multiple options based on different scenarios.
```

## Best Practices

1. **Separate actor and critic prompts** - each role needs distinct framing
2. **Store reflection history** - learnings should accumulate across iterations
3. **Set clear completion criteria** - define what "done" looks like
4. **Limit iterations** - prevent infinite loops and control costs
5. **Make criteria explicit** - the critic needs clear evaluation standards
6. **Include external feedback** - integrate test results, user input when available
7. **Preserve good work** - don't rebuild from scratch each iteration

## Variants

### Self-Refinement (No External Critic)

Uses the same model for all three roles with careful prompt separation:

```
ACTOR: "Generate response"
  ↓
CRITIC: "What are the issues? [Re-prompt with different system]"  
  ↓
ACTOR: "Now improve based on..." (re-prompt to same model)
```

### Evolutionary Reflexion

Applies genetic algorithm principles:

```
Generate population of N responses
  ↓
Evaluate each (critic)
  ↓
Select top performers
  ↓
Mutate and crossover
  ↓
Repeat until convergence
```

## References

- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) - Original paper by Shinn et al. (2023)
- [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651) - Similar pattern
- [Learning to Refine Language Model Outputs](https://arxiv.org/abs/2305.11617) - Refinement techniques


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
