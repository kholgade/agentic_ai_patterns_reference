---


# Tree of Thoughts
title: "Tree of Thoughts"
description: "An extension of chain-of-thought that explores multiple reasoning paths in parallel, branching like a tree structure."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Complex decision making", "Creative problem solving", "Exploratory analysis", "Multiple solution paths"]
dependencies: []
category: "reasoning"
---

# Tree of Thoughts



## Overview

Tree of Thoughts (ToT) extends Chain-of-Thought by allowing deliberate exploration of multiple reasoning paths simultaneously. Where CoT follows a single linear path, ToT branches at decision points, exploring different possibilities in parallel before selecting the most promising path. This approach recognizes that complex problems often have multiple valid approaches, and committing to the first path can miss better solutions. By maintaining a tree structure, the model can evaluate branches independently, backtrack when paths lead nowhere, and combine insights from different branches.

The pattern is particularly valuable for creative tasks, complex decision-making, and problems where the solution space is large and poorly defined. A strategic planning task might have several viable approaches, each with different tradeoffs. ToT allows the model to explore multiple strategies, evaluate their potential outcomes, and either select the best or synthesize a hybrid solution. The tree structure also enables natural checkpoints where the model can assess progress and decide whether to continue exploring a branch or prune it.

Implementing ToT requires managing multiple reasoning threads, tracking their states, and implementing strategies for branch evaluation and selection. This adds complexity over simpler patterns but enables significantly more sophisticated reasoning. The pattern works best when combined with a critic or evaluation mechanism that can objectively assess the quality of different branches, preventing the model from simply following the most recent path.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TREE OF THOUGHTS STRUCTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

                          ┌─────────────┐
                          │   ROOT      │
                          │   PROBLEM   │
                          └──────┬──────┘
                                 │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
      │   BRANCH    │      │   BRANCH    │      │   BRANCH    │
      │   1         │      │   2         │      │   3         │
      │  "Approach  │      │  "Approach  │      │  "Approach  │
      │   A"        │      │   B"        │      │   C"        │
      └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
             │                    │                    │
       ┌─────┴─────┐         ┌─────┴─────┐        ┌─────┴─────┐
       │           │         │           │        │           │
       ▼           ▼         ▼           ▼        ▼           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
  │  NODE   │ │  NODE   │ │  NODE   │ │  NODE   │ │  NODE   │ │  NODE   │
  │  1.1    │ │  1.2    │ │  2.1    │ │  2.2    │ │  3.1    │ │  3.2    │
  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
      │           │         │           │        │           │
      ▼           ▼         ▼           ▼        ▼           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
  │ LEAF    │ │ LEAF    │ │ LEAF    │ │ LEAF    │ │ LEAF    │ │ LEAF    │
  │ 1.1.1   │ │ 1.2.1   │ │ 2.1.1   │ │ 2.2.1   │ │ 3.1.1   │ │ 3.2.1   │
  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                     BRANCH EVALUATION                                       │
  └─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────┐           ┌─────────┐           ┌─────────┐
  │ BRANCH  │           │ BRANCH  │           │ BRANCH  │
  │   A     │           │   B     │           │   C     │
  │ Score: │           │ Score: │           │ Score: │
  │  7/10  │           │  9/10  │           │  5/10  │
  └────┬────┘           └────┬────┘           └────┬────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  SELECTED  │
                    │  BRANCH B  │
                    │  (Highest) │
                    └─────────────┘


  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                     EXPLORATION vs EXPLOITATION                          │
  └─────────────────────────────────────────────────────────────────────────────┘

         EXPLORE MANY                         EXPLOIT BEST
         ┌─────────────────┐                 ┌───��─────────────┐
         │ Depth: shallow  │                 │ Depth: deep     │
         │ Breadth: wide   │                 │ Breadth: narrow │
         │ Parallel: yes  │                 │ Parallel: no   │
         └─────────────────┘                 └─────────────────┘
               │                                    │
               ▼                                    ▼
         ┌─────────────────────────────────────────────────────┐
         │        COMPLETE TREE EXPLORATION (with pruning)      │
         └─────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Strategic Decision Making

**Problem:** "Should our startup pivot from B2C to B2B?"

```
                    ┌─────────────────────────────┐
                    │  ROOT: PIVOT DECISION        │
                    └─────────────┬───────────────┘
                                  │
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
    ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
    │   APPROACH    │    │   APPROACH    │    │   APPROACH    │
    │   A           │    │   B           │    │   C           │
    │ "Full pivot"  │    │ "Hybrid"      │    │ "No pivot"    │
    │ Score: 6/10   │    │ Score: 8/10   │    │ Score: 4/10   │
    └───────┬───────┘    └───────┬───────┘    └───────────────┘
            │                    │
      ┌─────┴─────┐         ┌─────┴─────┐
      ▼           ▼         ▼           ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│  PHASE 1  │ │  PHASE 2  │ │  PHASE 1  │ │  PHASE 2  │
│ "Find     │ │ "Build    │ │ "Keep     │ │ "Add B2B  │
│  B2B      │ │  sales    │ │  current  │ │  as add-on│
│  clients" │ │  team"    │ │  users"   │ │
│Score: 7/10│ │Score: 8/10│ │Score: 6/10│ │Score: 9/10│
└───────────┘ └───────────┘ └───────────┘ └───────────┘

RESULT: Approach B (Hybrid) with Phase 2 expansion has highest total score.
Select this path with modifications from Phase 1 of Approach A.
```

### Example 2: Creative Writing

**Problem:** "Write a story opening where a detective discovers they're the murder victim."

```
TREE EXPLORATION:

Branch 1: "Innocent Discovery"
├─ Node 1.1: Detective finds own body in morgue → Too cliché
├─ Node 1.2: Colleagues react strangely around detective → Suspense building
└─ Node 1.3: Detective notices own name on victim's ID → Strong hook
    Score: 8/10

Branch 2: "Paranoid Investigation"
├─ Node 2.1: Detective investigates "John Doe" case → Building paranoia
├─ Node 2.2: Evidence points to detective personally → Dramatic irony
└─ Node 2.3: Detective finds photos of own murder → High impact reveal
    Score: 9/10

Branch 3: "Medical/Supernatural"
├─ Node 3.1: Detective is actually a ghost → Genre shift
├─ Node 3.2: Time loop scenario → Complex but risky
└─ Node 3.3: Witness protection gone wrong → Mundane horror
    Score: 6/10

SELECTED PATH: Branch 2 combining 2.2 + 2.3 for maximum dramatic impact.
```

### Example 3: Mathematical Problem Solving

**Problem:** "Find the sum of all multiples of 3 or 5 below 1000."

```
                    ┌─────────────────────────────┐
                    │  PROBLEM: Sum below 1000     │
                    └─────────────┬─────────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            ▼                     ▼                     ▼
    ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
    │   METHOD A    │     │   METHOD B    │     │   METHOD C   │
    │ "Brute force" │     │ "Formula"     │     │ "Inclusion-   │
    │ "List all     │     │ "Use arithmetic│    │  Exclusion"  │
    │  and sum"     │     │  series sum"   │     │ "3n + 5n -   │
    │               │     │               │     │  15n"        │
    │ Complexity:   │     │ Complexity:   │     │ Complexity:  │
    │ O(n)         │     │ O(1)          │     │ O(1)         │
    │ Score: 5/10  │     │ Score: 9/10   │     │ Score: 8/10   │
    └───────────────┘     └───────────────┘     └───────────────┘

SOLUTION (Method B refined):
Step 1: Sum multiples of 3 = (3 + 6 + ... + 999)
        n = 999/3 = 333
        sum = 333 * (3 + 999) / 2 = 166,833

Step 2: Sum multiples of 5 = (5 + 10 + ... + 995)
        n = 995/5 = 199
        sum = 199 * (5 + 995) / 2 = 99,500

Step 3: Subtract multiples of 15 (counted twice)
        n = 990/15 = 66
        sum = 66 * (15 + 990) / 2 = 33,165

Step 4: Final answer = 166,833 + 99,500 - 33,165 = 233,168
```

## Best Practices

1. **Set reasonable limits** on depth and breadth to control computational cost
2. **Use pruning aggressively** - discard low-scoring branches early to save resources
3. **Implement parallel expansion** when possible to speed up exploration
4. **Design informative evaluator prompts** that capture the key criteria for success
5. **Allow cross-branch synthesis** - sometimes the best solution combines elements from multiple branches
6. **Track node metadata** - depth, parentage, and scoring history aid in debugging and analysis
7. **Consider beam search** - maintain top-k branches rather than all, for large exploration spaces

## References

- [Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10600) - Original paper by Yao et al. (2023)
- [LLM Reasoning Frameworks Comparison](https://arxiv.org/abs/2309.09165) - ToT vs other methods
- [Prompt Engineering Guide - Tree of Thoughts](https://www.prompteng.guide/tree-of-thoughts) - Implementation tips


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
