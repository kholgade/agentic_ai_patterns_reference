---


# Graph of Thoughts
title: "Graph of Thoughts"
description: "A pattern that models reasoning as a graph where nodes represent thoughts and edges represent logical connections."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Complex reasoning", "Multi-step planning", "Knowledge graph reasoning", "Connected analysis"]
dependencies: []
category: "reasoning"
---

# Graph of Thoughts



## Overview

Graph of Thoughts (GoT) extends Tree of Thoughts by replacing the strict tree hierarchy with a more flexible graph structure where nodes can have multiple parents and arbitrary connections. This captures the non-linear nature of human reasoning, where insights often connect disparate concepts and conclusions build on multiple inputs. Unlike trees, graphs allow cycles (for iterative refinement), merging paths from different branches, and explicit representation of dependencies between thoughts. This makes GoT particularly powerful for complex reasoning tasks where the solution space is highly interconnected.

The pattern introduces specialized node types: generator nodes that produce new thoughts, aggregator nodes that combine multiple inputs, and critic nodes that evaluate or filter thoughts. Aggregation nodes are particularly valuable because they enable synthesis of different reasoning paths—a key capability missing from tree-based approaches. A complex problem might explore multiple angles, and the final answer often emerges from combining insights from several paths rather than selecting a single winner.

GoT represents a shift from sequential reasoning patterns to network-based reasoning. The model can maintain multiple active reasoning threads, establish explicit connections between related thoughts, and represent complex dependencies. This is especially useful for tasks like multi-document analysis where different sources provide complementary information, or complex planning where different constraints interact in non-obvious ways.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     GRAPH OF THOUGHTS STRUCTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                      SPECIALIZED NODE TYPES                             │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │  GENERATOR  │     │  AGGREGATOR │     │   CRITIC    │
  │     NODE    │     │     NODE    │     │    NODE     │
  │             │     │             │     │             │
  │ Creates new │     │ Combines    │     │ Evaluates   │
  │ thoughts    │     │ inputs into │     │ and filters │
  │ from single │     │ single      │     │ thoughts    │
  │ input       │     │ output      │     │             │
  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
          │                    │                    │
          ▼                    ▼                    ▼
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │ Produces:   │     │ Inputs:    │     │ Output:    │
  │ A           │     │ A, B, C    │     │ Quality    │
  │             │     │ Output:    │     │ Score      │
  │             │     │ Synthesis  │     │            │
  └─────────────┘     └─────────────┘     └─────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                      EXAMPLE GRAPH STRUCTURE                           │
  └─────────────────────────────────────────────────────────────────────────┘

       ┌───────────┐
       │  SOURCE   │
       │   DATA    │
       └─────┬─────┘
             │
     ┌────────┼────────┐
     │        │        │
     ▼        ▼        ▼
 ┌────────┐┌────────┐┌────────┐
 │ THOUGHT││ THOUGHT││ THOUGHT│
 │   A    ││   B    ││   C    │
 │ (from  ││ (from  ││ (from  │
 │ src1)  ││ src2)  ││ src3)  │
 └───┬────┘└───┬────┘└───┬────┘
     │         │         │
     │    ┌────┴────┐    │
     │    │AGGREGATOR│    │
     │    │    D     │    │
     │    │ combines │    │
     │    │ A + B    │    │
     │    └────┬────┘    │
     │         │         │
     │         └────┬────┘
     │              │
     ▼              ▼
 ┌────────────┐ ┌────────┐
 │  AGGREGATOR│ │THOUGHT │
 │     E      │ │   F    │
 │ combines   │ │        │
 │ D + C      │ │        │
 └─────┬──────┘ └────┬───┘
       │             │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │   CRITIC    │
       │     G       │
       │ Evaluates   │
       │ quality     │
       └─────┬───────┘
             │
             ▼
       ┌─────────────┐
       │   FINAL     │
       │   OUTPUT    │
       └─────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                      ITERATIVE REFINEMENT (CYCLES)                    │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
  │ THOUGHT X   │────────▶│   CRITIC    │────────▶��� THOUGHT X'  │
  │ (initial)   │         │  evaluates  │         │ (refined)   │
  └─────────────┘         └─────────────┘         └──────┬──────┘
       ▲                                                │
       │         ┌─────────────┐                        │
       └─────────│  Continue   │◀───────────────────────┘
                 │  refining?  │
                 └─────────────┘
```

## Examples

### Example 1: Multi-Source Analysis

**Sources:** Legal document, Financial report, Technical specification

```
GRAPH STRUCTURE:

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   LEGAL       │     │   FINANCIAL  │     │   TECHNICAL  │
│   DOCUMENT    │     │   REPORT     │     │   SPEC       │
│   Generator   │     │   Generator  │     │   Generator  │
│               │     │              │     │              │
│ Key finding:  │     │ Key finding: │     │ Key finding: │
│ IP ownership  │     │ Revenue down │     │ Scalability  │
│ clause weak  │     │ 10% due to   │     │ concerns     │
│               │     │ technical    │     │              │
│               │     │ debt         │     │              │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────────┬──┴─────────────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  AGGREGATOR  │
                   │  Synthesize  │
                   │  All findings│
                   └───────┬──────┘
                          │
                          ▼
                   ┌──────────────┐
                   │    CRITIC    │
                   │  Score: 7/10│
                   │  Gaps in     │
                   │  legal review│
                   └───────┬──────┘
                          │
                          ▼
                   ┌──────────────┐
                   │    FINAL     │
                   │  RECOMMEND-  │
                   │  ATION       │
                   └──────────────┘

OUTPUT: "Three critical issues identified: (1) Weak IP ownership 
requires contract revision, (2) Revenue decline tied to technical 
debt requires infrastructure investment, (3) Scalability concerns 
need architectural review before Q2 launch."
```

### Example 2: Iterative Refinement

**Task:** Write a product requirements document

```
ITERATION 1:
Initial draft node → Critic scores 5/10 (missing acceptance criteria)
                            │
                            ▼
                       Refinement needed
                            │
                            ▼
ITERATION 2:
Refined draft → Aggregator combines with new requirements
                            │
                            ▼
                    Critic scores 7/10 (good structure)
                            │
                            ▼
                    Minor polish needed
                            │
                            ▼
ITERATION 3:
Final polish → Aggregator combines all
                            │
                            ▼
                    Critic scores 9/10 ✓
                            │
                            ▼
                     FINAL DOCUMENT
```

### Example 3: Complex Planning

**Task:** Plan a product launch across multiple teams

```
GRAPH CONNECTIONS: 

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐              │
│  │Engineering│──────▶│Marketing│◀───────│Product  │              │
│  │ Timeline │        │ Strategy│        │ Vision  │              │
│  └────┬────┘        └────┬────┘        └────┬────┘              │
│       │                  │                  │                    │
│       │     ┌───────────┴───────────┐      │                    │
│       │     │                       │      │                    │
│       ▼     ▼                       ▼      ▼                    │
│  ┌─────────┐   ┌─────────────────────────┐   ┌─────────┐       │
│  │Dependency│   │    LAUNCH COORDINATOR   │   │Customer │       │
│  │  Graph   │──▶│    (Aggregator)         │◀──│ Success │       │
│  │         │   │    Syncs all constraints │   │ Criteria│       │
│  └─────────┘   └───────────────┬───────────┘   └─────────┘       │
│                               │                                  │
│                               ▼                                  │
│                        ┌─────────────┐                           │
│                        │   CRITIC    │                           │
│                        │ Validates   │                           │
│                        │ feasibility │                           │
│                        └──────┬──────┘                           │
│                               │                                  │
│                               ▼                                  │
│                        ┌─────────────┐                           │
│                        │   FINAL     │                           │
│                        │   LAUNCH     │                           │
│                        │   PLAN      │                           │
│                        └─────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Best Practices

1. **Design node types intentionally** - each type should have a clear purpose in your graph
2. **Use aggregation nodes sparingly** - only combine when synthesis adds value
3. **Implement cycle detection** to prevent infinite loops in iterative refinement
4. **Track dependencies explicitly** - this aids debugging and ensures proper ordering
5. **Consider graph visualization** for debugging complex graphs
6. **Use scores strategically** - propagate quality metrics through the graph
7. **Allow dynamic node creation** - graphs should grow based on reasoning needs

## References

- [Graph of Thoughts: Reasoning with Large Language Models](https://arxiv.org/abs/2308.09687) - Original paper by Besta et al. (2023)
- [Graph-based Prompting for LLM Reasoning](https://arxiv.org/abs/2309.12188) - Practical applications
- [Prompt Engineering Guide - Graph of Thoughts](https://www.prompteng.guide/graph-of-thoughts) - Implementation patterns


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
