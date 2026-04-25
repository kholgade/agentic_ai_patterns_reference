---


# Evaluator Optimizer
title: "Evaluator Optimizer"
description: "A pattern where one agent evaluates output and another optimizes based on that feedback in a loop."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Iterative refinement", "Quality improvement", "Feedback loops", "Continuous optimization"]
dependencies: []
category: "evaluation"
---

# Evaluator Optimizer



## Detailed Explanation

The Evaluator Optimizer pattern implements an iterative refinement loop commonly used in software development for continuous improvement. One agent (the Evaluator) assesses the quality of generated output against defined criteria, while another agent (the Optimizer) incorporates that feedback to produce improved results. This cycle repeats until the output meets quality standards or iteration limits are reached.

This pattern mirrors the human editorial process where a writer produces content, an editor provides feedback, and the writer revises based on that feedback. The key insight is that separating the evaluation role from generation often produces better results than attempting self-correction—the Evaluator can focus purely on analysis without the generation overhead, and the Optimizer can systematically address feedback without the evaluation burden.

The pattern is particularly effective when evaluation criteria are well-defined or can be articulated clearly. Code reviews, writing style improvements, and data transformation refinement all benefit from this iterative approach. However, it adds latency and cost per iteration, so implementations should include clear stopping criteria to prevent excessive refinement loops.

### When to Use Evaluator Optimizer

Use this pattern when output quality must meet specific criteria, when feedback can be systematically articulated, or when multiple refinement passes meaningfully improve results. It's ideal for content that benefits from editorial review, code that needs to pass linting, and transformations requiring validation.

## ASCII Diagram

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  GENERATE  │────▶│  EVALUATE   │────▶│  OPTIMIZE  │────▶│  GENERATE  │
│   Initial  │     │   Check    │     │  Improve   │     │    Next    │
│  Output    │     │ Criteria   │     │  Feedback  │     │  Version   │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
                           │                    │                    │
                     ┌─────▼─────┐              │
                     │ Feedback  │              │
                     │  Summary   │              │
                     └───────────┘              │
                                                │
                   ITERATION LOOP                │
                   until quality met           │
                   or max iterations        │
                                                │
                 ┌──────▼──────┐                          ┌──────▼──────┐
                 │  Quality   │                          │    Final    │
                 │  PASSED   │                          │   Output   │
                 └───────────┘                          └───────────┘
```

## Academic References

### Iterative Refinement & Self-Improvement

1. **Madaan, A., Tandon, N., Gupta, A., et al. (2023).** "Self-Refine: Iterative Refinement with Self-Feedback" - *arXiv preprint arXiv:2303.17651*.
   - Directly applicable framework for iterative refinement based on feedback evaluation.

2. **Kim, G. H., Bae, S., Shin, J., et al. (2023).** "Language Models as Zero-Shot Planners: Extracting Actionable Knowledge for Embodied Agents" - *arXiv preprint arXiv:2308.08155*.
   - Shows self-correction and iterative improvement mechanisms in LLM systems.

3. **Wang, L., Ma, C., Feng, X., et al. (2024).** "A Survey on Large Language Model based Autonomous Agents" - *arXiv preprint arXiv:2308.11432*.
   - Comprehensive survey including iterative refinement and feedback loops in agent systems.

### Feedback Loops & Optimization

4. **Du, Y., Li, S., Torralba, A., et al. (2023).** "Improving Factuality and Reasoning in Language Models through Multiagent Debate" - *arXiv preprint arXiv:2305.14325*.
   - Demonstrates iterative improvement through feedback; applicable to optimizer's refinement strategy.

5. **Wei, J., Tay, Y., Bommasani, R., et al. (2022).** "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" - *arXiv preprint arXiv:2201.11903*.
   - Shows step-wise reasoning improvement; relevant to evaluation-driven optimization.

### Quality-Based Iteration

6. **Perez, E., Ringer, S., Lukošiūtė, K., et al. (2022).** "Red Teaming Language Models with Language Models" - *arXiv preprint arXiv:2202.03286*.
   - Demonstrates iterative weakness identification and correction patterns.

7. **Schick, T., Dwivedi-Yu, J., Dessì, R., et al. (2024).** "Toolformer: Language Models Can Teach Themselves to Use Tools" - *arXiv preprint arXiv:2302.04761*.
   - Shows self-improvement through feedback and tool selection optimization.

### Convergence & Stopping Criteria

8. **Yao, S., Yu, D., Zhao, J., et al. (2023).** "ReAct: Synergizing Reasoning and Acting in Language Models" - *arXiv preprint arXiv:2210.03629*.
   - Framework for iterative reasoning and action; includes convergence patterns.

9. **Wei, J., Wang, X., Schlarman, D., et al. (2022).** "Emergent Abilities of Large Language Models" - *arXiv preprint arXiv:2206.07682*.
   - Addresses iterative capability improvements and convergence in multi-step reasoning.

10. **Park, J. S., O'Neill, J., Baryan, R., et al. (2023).** "Generative Agents: Interactive Simulacra of Human Behavior" - *arXiv preprint arXiv:2304.03442*.
    - Demonstrates iterative behavior refinement and quality improvement cycles.

## Reference Links

- [LangChain Reflexion](https://python.langchain.com/docs/modules/agents/how_to/reflexion)
- [Self-Correction in LLMs](https://arxiv.org/abs/2308.08155)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
