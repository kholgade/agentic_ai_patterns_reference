---
title: Mixture of Agents
description: Combining multiple specialized agents to handle different aspects of complex tasks
complexity: high
model_maturity: emerging
typical_use_cases: ["Multi-agent coordination", "Task decomposition", "Collaborative problem solving"]
dependencies: []
category: multi-agent
---

## Detailed Explanation

Mixture of Agents (MoA) is a pattern where multiple specialized AI agents contribute their expertise to produce a superior final output compared to what any single agent could achieve. Each agent in the mixture has distinct capabilities, knowledge domains, or processing approaches. The agents either work in parallel contributing different pieces that are later combined, or iteratively refine each other's outputs. The key insight is that diversity in agent expertise leads to more robust and comprehensive solutions, similar to how ensemble methods in machine learning improve prediction accuracy.

The architecture consists of several components: specialized agents with defined roles, a coordination mechanism (sequential pipeline, hierarchical, or parallel aggregation), and a combination strategy to merge agent outputs. The design space is large - agents can differ in their base LLM, system prompts, tool access, temperature, or fine-tuning. The combination can be as simple as voting or as complex as hierarchical reasoning with debate. Choosing the right combination strategy depends on task type, the nature of agent specialization, and latency requirements.

## ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                 MIXTURE OF AGENTS ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              PARALLEL MOA (Independent Contributions)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│    │   Research  │    │   Analysis   │    │  Creative  │   │
│    │    Agent   │    │    Agent    │    │   Agent    │   │
│    │            │    │              │    │            │   │
│    │ • Web Search│    │ • Statistics│    │ • Writing │   │
│    │ • Document │    │ • Charts    │    │ • Ideas    │   │
│    │ • Code     │    │ • Data      │    │ • Concepts │   │
│    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘   │
│           │                   │                   │            │
│           └───────────────────┴───────────────────┘            │
│                           │                                       │
│                           ▼                                       │
│                  ┌─��───────────────┐                             │
│                  │    Combiner    │                              │
│                  │   (Merge/Vote) │                              │
│                  └────────┬────────┘                              │
│                           │                                       │
│                           ▼                                       │
│                  ┌─────────────────┐                             │
│                  │  Final Output   │                             │
│                  └─────────────────┘                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              SEQUENTIAL MOA (Iterative Refinement)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│    │Research │───▶│ Analyst  │───▶│Editor    │───▶│Reviewer  │ │
│    │ Agent   │    │ Agent    │    │ Agent    │    │ Agent   │ │
│    └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│        │                │                │                │       │
│        │                │                │                ▼       │
│        │                │                │          ┌──────────┐    │
│        │                │                │          │  Final  │    │
│        │                └────────────────┴──────────│ Output  │    │
│        │                                          └──────────┘    │
│        │                                                    │      │
│        └────────────────────────────────────────────────────┘     │
│                     Feedback Loop                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              HIERARCHICAL MOA (Orchestrated)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌──────────────┐                            │
│                    │  Orchestr   │                            │
│                    │   ation    │                            │
│                    └──────┬───────┘                            │
│                           │                                      │
│            ┌──────────────┼──────────────┐                       │
│            ▼              ▼              ▼                        │
│      ┌───────────┐  ┌───────────┐  ┌───────────┐              │
│      │  Domain   │  │  Domain   │  │  Domain   │              │
│      │  Expert 1 │  │  Expert 2 │  │  Expert 3 │              │
│      └───────────┘  └───────────┘  └───────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Writing Pipeline

Parallel agents: researcher, analyst, creativewriter. Combined response provides accurate facts, critical insights, and engaging prose.

### Example 2: Code Review

Reviewers with different specializations (security, performance, documentation) each critique the code, outputs prioritized by voting.

### Example 3: Complex Decision Making

Sequential: gather facts → analyze options → recommend → review. Each expert refines based on previous output.

## Reference Links

- [Mixture of Agents: LLM Ensemble](https://arxiv.org/abs/2404.15772) - Original research on mixture of agents
- [Expert Prompting](https://arxiv.org/abs/2401.12988) - Role-based agent prompting
- [CAMEL: Conversational Agents](https://camellabs.com/) - Multi-agent collaboration framework


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
