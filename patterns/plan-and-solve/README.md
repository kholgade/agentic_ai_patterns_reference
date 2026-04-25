---


# Plan and Solve
title: "Plan and Solve"
description: "A pattern that first creates a detailed plan, then executes it step by step."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["Complex multi-step tasks", "Project planning", "Goal-oriented tasks", "Sequential problem solving"]
dependencies: []
category: "reasoning"
---

# Plan and Solve



## Overview

Plan and Solve (P&S) is a prompting pattern that separates planning from execution, breaking complex tasks into two distinct phases. In the planning phase, the model analyzes the task, identifies necessary steps, and creates an explicit roadmap. In the execution phase, it follows that roadmap step by step, potentially with intermediate validation. This separation is powerful because it mirrors how humans approach complex tasks—we first understand what needs to be done and how, then we do it methodically.

The pattern is particularly valuable for multi-step tasks where the sequence of operations matters, where intermediate results inform later steps, or where different sub-tasks require different approaches. A task like "Analyze our sales data, identify trends, and recommend actions" requires analysis before trends can be identified, and trends before recommendations make sense. P&S enforces this logical ordering by making planning explicit and linking steps.

Plan and Solve serves as a foundation for more complex agent architectures where the plan can be adapted based on execution feedback, where different agents handle planning vs execution, or where plans are stored and referenced. It's less computationally expensive than patterns that explore multiple paths (like ToT or GoT) but more structured than simple sequential approaches (like CoT). This makes it a good default for any task that can be decomposed into steps.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                        PLAN AND SOLVE FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    TWO-PHASE APPROACH                                  │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  PHASE 1: PLANNING                                                     │
  └─────────────────────────────────────────────────────────────────────────┘

       ┌─────────────┐
       │   INPUT     │
       │   TASK      │
       └──────┬──────┘
              │
              ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │  ANALYSIS                                                               │
  │  - Understand the goal                                                 │
  │  - Identify constraints                                                 │
  │  - Determine required information/actions                              │
  └──────┬──────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │  STEP IDENTIFICATION                                                   │
  │  - List all required steps                                            │
  │  - Determine dependencies (what must come first)                     │
  │  - Identify any parallel vs sequential steps                          │
  └──────┬──────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │  PLAN GENERATION                                                     │
  │  - Create numbered list of steps                                      │
  │  - Specify inputs/outputs for each step                              │
  │  - Add checkpoints or validation points                             │
  └──────┬──────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │  WRITTEN PLAN (example)                                                │
  │  1. [Step name] - [what to do]                                        │
  │  2. [Step name] - [what to do]                                         │
  │  3. [Step name] - [what to do]                                         │
  └───────┬────────────────────────────────────────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  PHASE 2: EXECUTION                                                     │
  └─────────────────────────────────────────────────────────────────────────┘

           │
           ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  EXECUTE STEP 1                                                         │
  │  - Perform the step                                                    │
  │  - Record intermediate results                                         │
  │  - Validate if possible                                               │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  EXECUTE STEP 2                                                         │
  │  - May use results from Step 1                                         │
  │  - Continue execution                                                   │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  EXECUTE STEP 3                                                         │
  │  ...                                                                   │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  FINAL OUTPUT                                                         │
  │  - Synthesize results from all steps                                    │
  │  - Present final answer                                               │
  └─────────────────────────────────────────────────────────────────────────┘


  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  EXAMPLE: Complex Task Planning                                         │
  └─────────────────────────────────────────────────────────────────────────────┘

  INPUT: "Research the feasibility of launching a subscription box
          service for pet products, and create a 90-day launch plan"

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  PLANNING PHASE                                                        │
  └─────────────────────────────────────────────────────────────────────────┘

  ANALYSIS:
  - Goal: Determine feasibility and create actionable plan
  - Requirements: Market research, financial analysis, operational planning
  - Constraints: 90-day timeline, budget considerations

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  GENERATED PLAN                                                        │
  │                                                                          │
  │  STEP 1: Market Research                                               │
  │  - Identify target market and customer segments                        │
  │  - Analyze competitors and their offerings                             │
  │  - Determine market size and growth potential                          │
  │                                                                          │
  │  STEP 2: Financial Analysis                                            │
  │  - Estimate startup costs                                             │
  │  - Project recurring costs and revenue                                 │
  │  - Calculate break-even point                                         │
  │                                                                          │
  │  STEP 3: Operational Planning                                         │
  │  - Define product sourcing strategy                                    │
  │  - Plan logistics and fulfillment                                     │
  │  - Design subscription tiers                                        │
  │                                                                          │
  │  STEP 4: 90-Day Launch Timeline                                        │
  │  - Week 1-4: Preparation and setup                                     │
  │  - Week 5-8: Testing and refinement                                     │
  │  - Week 9-12: Launch and initial marketing                            │
  │                                                                          │
  │  STEP 5: Risk Assessment and Contingencies                             │
  ��  - Identify key risks                                                   │
  │  - Develop mitigation strategies                                      │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  EXECUTION PHASE                                                       │
  └─────────────────────────────────────────────────────────────────────────┘

  Now executing each step in sequence, producing detailed outputs for each.
```

## Examples

### Example 1: Technical Problem Solving

**Task:** "Debug and fix a Python script that's supposed to filter valid emails but isn't working correctly"

```
PLAN:
Step 1: Analyze the current code
Step 2: Identify potential bugs
Step 3: Test with various inputs
Step 4: Implement fixes
Step 5: Verify all cases work

EXECUTION:

Step 1 Output: [Code analysis reveals potential regex issues]

Step 2 Output: "Bugs identified: (1) Regex doesn't handle +addresses, (2) Missing dot handling"

Step 3 Output: [Test results showing what passes and fails]

Step 4 Output: [Fixed regex implementation]

Step 5 Output: [All test cases pass]

FINAL: Debugged and working code with explanation of fixes.
```

### Example 2: Business Analysis

**Task:** "Assess whether we should migrate our database to the cloud"

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PLAN                                                                    │
│  1. Current State Assessment - Analyze existing database usage           │
│  2. Cost Analysis - Compare on-prem vs cloud costs                      │
│  3. Risk Assessment - Identify migration risks                     │
│  4. Vendor Comparison - Evaluate AWS, Azure, GCP                   │
│  5. Recommendation - Synthesize findings into recommendation           │
└─────────────────────────────────────────────────────────────────────────┘

OUTPUT:
[Full analysis with structured outputs for each step]
[Final recommendation: Migrate to AWS with 18-month timeline]
```

### Example 3: Research Task

**Task:** "Write a literature review on AI ethics in healthcare"

```
PLAN:
Step 1: Define search scope and key terms
Step 2: Identify major themes and frameworks
Step 3: Find and summarize key papers (15-20)
Step 4: Organize by theme
Step 5: Synthesize into coherent narrative

EXECUTION:
[Each step produces structured output]
[Step 5 synthesizes into literature review with citations]

FINAL: [Complete literature review ready for submission]
```

## Best Practices

1. **Make planning explicit** - write down the plan rather than assuming it's understood
2. **Specify dependencies** - make clear which steps depend on others
3. **Include validation checkpoints** - verify each step before proceeding
4. **Allow plan adaptation** - be willing to modify the plan based on findings
5. **Keep steps atomic** - each step should be a single, coherent unit of work
6. **Document intermediate outputs** - these become context for subsequent steps
7. **Set clear completion criteria** - know when the task is truly done

## Variations

### Hierarchical Plan and Solve

For very complex tasks, create high-level plans first, then detail each step:

```
HIGH-LEVEL PLAN:
Phase 1: Research
Phase 2: Analysis
Phase 3: Synthesis

↓ Each phase becomes its own P&S problem
```

### Adaptive Plan and Solve

After executing each step, re-evaluate and potentially modify the remaining plan:

```
PLAN → EXECUTE STEP → EVALUATE → MODIFY PLAN → EXECUTE NEXT STEP
```

### Parallel Plan and Solve

Identify independent steps and execute them concurrently:

```
PLAN:
Step 1: Data collection (parallel paths for different sources)
Step 2: Analysis (depends on Step 1)
Step 3: Synthesis (depends on Step 2)

Execute 1a, 1b, 1c in parallel → Then 2 → Then 3
```

## References

- [Plan and Solve Prompting: Improving Chain-of-Thought Planning](https://arxiv.org/abs/2305.04091) - Original paper by Wang et al. (2023)
- [Large Language Models as Managers](https://arxiv.org/abs/2306.10055) - Plan and execute frameworks
- [Prompt Engineering Guide - Planning Patterns](https://www.prompteng.guide/plan-and-solve) - Implementation examples


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
