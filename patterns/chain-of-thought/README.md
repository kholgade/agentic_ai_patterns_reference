---


# Chain of Thought
title: "Chain of Thought"
description: "A reasoning pattern where the model explicitly articulates its thought process step-by-step before reaching a conclusion."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["Complex reasoning tasks", "Math problem solving", "Logical deduction", "Step-by-step analysis"]
dependencies: []
category: "reasoning"
---

# Chain of Thought



## Overview

Chain-of-Thought (CoT) prompting is a foundational reasoning technique that guides language models to decompose complex problems into sequential intermediate steps. Rather than jumping directly from input to answer, the model explicitly verbalizes its reasoning process, making each inference step visible and traceable. This approach emerged from research showing that allowing models to "think out loud" significantly improves accuracy on multi-step reasoning tasks, particularly arithmetic, commonsense reasoning, and logical deduction problems. The key insight is that intermediate reasoning steps serve as explicit computational scratchpad that guides the model toward correct final conclusions.

The pattern works by providing the model with examples that include reasoning chains before the target question. These few-shot examples demonstrate the format and structure expected, establishing a template the model follows. When faced with novel problems, the model applies this learned pattern, generating its own intermediate reasoning steps before producing the final answer. This decomposition reduces cognitive load on the model by giving it smaller, more manageable sub-problems to solve sequentially. The effectiveness scales with problem complexity—simple arithmetic problems benefit moderately, while multi-step word problems show dramatic improvements.

CoT prompting has become a cornerstone of modern LLM applications, forming the foundation for more advanced reasoning patterns. Its simplicity to implement and significant performance gains make it a default choice for any reasoning-intensive task. The pattern is particularly valuable when tasks involve multiple pieces of information that must be combined, when solutions require domain-specific rules, or when the reasoning path matters as much as the final answer for explainability purposes.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CHAIN OF THOUGHT FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐      ┌─────────────────┐      ┌─────────────────┐
  │  INPUT   │      │  STEP 1         │      │  STEP 2         │
  │  Question│──────│  Reason         │──────│  Reason         │
  │  / Task  │      │  Intermediate   │      │  Intermediate   │
  └──────────┘      │  Thought       │      │  Thought       │
                     └────────┬────────┘      └────────┬────────┘
                              │                        │
                              └───────────┬────────────┘
                                          ▼
                           ┌────────────��────────────┐
                           │     FINAL ANSWER        │
                           │     Synthesized        │
                           │     Conclusion         │
                           └─────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  DETAILED FLOW (Multi-Step Example - Math Word Problem)                      │
  └─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐
  │   INPUT     │
  │             │
  │ "If John    │
  │  has 5      │
  │  apples and │
  │  buys 3     │
  │  more, then │
  │  gives 2    │
  │  to Mary,   │
  │  how many   │
  │  does he    │
  │  have?"     │
  └──────┬──────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  STEP 1: Understand the starting condition                               │
  │  "John starts with 5 apples"                                           │
  └──────┬────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  STEP 2: Process the addition                                           │
  │  "John buys 3 more apples"                                              │
  │  5 + 3 = 8 apples total                                                 │
  └──────┬────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  STEP 3: Process the subtraction                                        │
  │  "John gives 2 to Mary"                                                 │
  │  8 - 2 = 6 apples remaining                                             │
  └──────┬────────────────────────────────────────────────────────────────┘
          ▼
  ┌─────────────┐
  │   OUTPUT    │
  │             │
  │   "6"       │
  └─────────────┘
```

## Examples

### Example 1: Logical Deduction

**Prompt:**
> Three houses are on a street: red, blue, and green. The red house is not next to the blue house. The green house is at the end of the street. Where is the blue house?

**Reasoning Chain:**
> Let me work through this systematically.
> - We know: Green house is at an end of the street
> - Possibilities: [Green, Red, Blue] or [Blue, Red, Green]
> - We know: Red is not next to Blue
> - If green is first: Green | Red | Blue → Red not next to Blue? No, they ARE adjacent
> - If green is last: Blue | Red | Green → Red not next to Blue? No, they ARE adjacent
>
> Wait, I need to reconsider. If green is at one end, and red cannot be adjacent to blue:
> - [Green, X, Y] where X≠Red and Y≠Blue, and Red not adjacent to Blue
> - If position 2 is Red: [Green, Red, Blue] - Red adjacent to Blue, invalid
> - If position 2 is Blue: [Green, Blue, Red] - Red adjacent to Blue, invalid
>
> Actually, "not next to" means there must be exactly one house between them.
> - Green at end: [Green, X, Y] or [X, Y, Green]
> - For Red not adjacent to Blue, they must have the Green house between them
> - Therefore: Blue is at position 2 (middle), Red is at position 3 (other end)
>
> Answer: The blue house is in the middle of the street.

### Example 2: Mathematical Word Problem

**Prompt:**
> A rectangular garden is 15 meters long and 8 meters wide. The owner wants to plant flowers along the perimeter, with flowers spaced 1 meter apart. How many flowers are needed? (Assume flowers are planted at each corner and along the edges.)

**Reasoning Chain:**
> Step 1: Understand what we're calculating
> - We need flowers along the perimeter
> - Spacing: 1 meter apart
>
> Step 2: Calculate perimeter
> - Perimeter = 2 × (length + width)
> - Perimeter = 2 × (15 + 8)
> - Perimeter = 2 × 23 = 46 meters
>
> Step 3: Calculate number of flowers
> - If flowers are 1 meter apart along 46 meters, we need 46 + 1 flowers (corners inclusive)
> - Alternative: Number of flowers = (perimeter / spacing) + 1
> - Number of flowers = 46 + 1 = 47
>
> Answer: 47 flowers are needed.

### Example 3: Commonsense Reasoning

**Prompt:**
> If it's raining outside and Maria doesn't have an umbrella, but she needs to get to her car which is parked across the street, what might she do?

**Reasoning Chain:**
> Given information:
> 1. It's raining (water falling from sky)
> 2. Maria has no umbrella (no rain protection device)
> 3. Her car is across the street (destination not immediately accessible)
>
> Constraints:
> - She needs to stay dry OR accept getting wet
> - She must cross the street
>
> Possible actions:
> 1. Run quickly across the street (minimizes exposure but will get wet)
> 2. Wait for the rain to stop (delays but stays dry)
> 3. Find a covered walkway or building to use (stays dry if available)
> 4. Accept getting wet and just go (direct but uncomfortable)
>
> The most practical choice depends on urgency. For most cases, waiting briefly or finding cover would be preferred, but if very urgent, running is acceptable.
>
> Answer: Maria might wait for a break in the rain, find a covered path, or simply run through the rain accepting that she'll get wet.

## Best Practices

1. **Provide 3-5 diverse examples** in your few-shot prompts to establish the reasoning pattern clearly
2. **Make reasoning steps atomic** - each step should express a single inference or transformation
3. **Include the final answer explicitly** after the reasoning chain for easy extraction
4. **Use consistent formatting** (like "Step N:" or line breaks) for parseable outputs
5. **Match reasoning depth to problem complexity** - simple problems don't need elaborate chains
6. **Include edge cases in examples** when your target problems may involve them

## References

- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) - Original paper by Wei et al. (2022)
- [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171) - Builds on CoT
- [The Prompt Engineer's Guide to Chain of Thought](https://www.promptengineersguide.com/) - Practical applications guide


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
