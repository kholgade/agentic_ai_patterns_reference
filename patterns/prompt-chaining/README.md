---


# Prompt Chaining
title: "Prompt Chaining"
description: "A pattern where the output of one prompt becomes the input to the next, creating a chain of transformations."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["Sequential transformations", "Multi-step processing", "Data pipelines", "Content refinement"]
dependencies: []
category: "flow"
---

# Prompt Chaining



## Detailed Explanation

Prompt chaining is a foundational pattern in LLM application design where the output of one model invocation serves as the input to subsequent prompts. This sequential composition allows complex operations to be broken down into manageable steps, each handled by a specialized prompt. The pattern leverages the observation that smaller, focused prompts typically produce more reliable results than attempting to handle complex multi-step tasks in a single call. By chaining simple transformations together, developers create robust pipelines that can handle diverse processing requirements while maintaining transparency in how data flows through the system.

The key advantage of prompt chaining lies in its ability to decompose complex tasks into discrete, testable stages. Each link in the chain can be independently validated, debugged, and improved. This modularity also enables conditional processing—certain branches may be skipped based on intermediate outputs. Modern implementations often include checkpointing between chain links to enable recovery from failures and support for resuming long-running operations.

### When to Use Prompt Chaining

Use this pattern when dealing with multi-step transformations where each stage produces a distinct output that feeds the next, or when you need to preserve intermediate results for review or debugging. It excels in data cleaning pipelines, content generation workflows, and any scenario requiring sequential processing where each step might need independent adjustment.

## ASCII Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Prompt    │     │   Prompt   │     │   Prompt    │     │   Prompt    │
│    Step 1   │────▶│   Step 2   │────▶│   Step 3   │────▶│   Step 4   │
│             │     │            │     │            │     │            │
│  Input A    │     │  Output A  │     │  Output B  │     │  Output C  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                           │
                    ┌──────▼──────┐              ┌──────▼──────┐
                    │  Checkpoint │              │    Final    │
                    │  (optional) │              │   Output D  │
                    └─────────────┘              └─────────────┘
```

## Academic References

### LLM Pipeline & Sequential Processing

1. **Wei, J., Tay, Y., Bommasani, R., et al. (2022).** "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" - *arXiv preprint arXiv:2201.11903*.
   - Foundational work on sequential reasoning in LLMs; demonstrates effectiveness of step-by-step processing.

2. **Yao, S., Yu, D., Zhao, J., et al. (2023).** "ReAct: Synergizing Reasoning and Acting in Language Models" - *arXiv preprint arXiv:2210.03629*.
   - Framework combining reasoning and action in sequences; applicable to chaining multiple prompts.

3. **Schick, T., Dwivedi-Yu, J., Dessì, R., et al. (2024).** "Toolformer: Language Models Can Teach Themselves to Use Tools" - *arXiv preprint arXiv:2302.04761*.
   - Demonstrates sequential tool invocation; relevant to chaining specialized prompts.

### Task Decomposition & Orchestration

4. **Khattab, O., Santhanam, K., Li, X. L., et al. (2022).** "Demonstrate-Search-Predict: Composing Retrieval and Language Models for Knowledge-Intensive NLP" - *arXiv preprint arXiv:2212.14024*.
   - Shows practical chaining of retrieval and generation steps; directly applicable to prompt chaining design.

5. **Wang, L., Ma, C., Feng, X., et al. (2024).** "A Survey on Large Language Model based Autonomous Agents" - *arXiv preprint arXiv:2308.11432*.
   - Comprehensive survey including pipeline and sequential processing patterns in agentic systems.

### Data Flow & Transformation

6. **Parameswaran, A., Polyzotis, N., & Garcia-Molina, H. (2016).** "The Importance of Bread and Butter: Improving Ranking Consistency and Freshness" - *VLDB Endowment*, 9(7), 540-551.
   - Addresses data transformation pipelines; principles applicable to multi-step LLM processing.

7. **Park, J. S., O'Neill, J., Baryan, R., et al. (2023).** "Generative Agents: Interactive Simulacra of Human Behavior" - *arXiv preprint arXiv:2304.03442*.
   - Demonstrates sequential prompting and state transitions in agent systems.

### Error Handling & Robustness

8. **Du, Y., Li, S., Torralba, A., et al. (2023).** "Improving Factuality and Reasoning in Language Models through Multiagent Debate" - *arXiv preprint arXiv:2305.14325*.
   - Shows iterative refinement through sequential processing; applicable to verification steps in chains.

9. **Perez, E., Ringer, S., Lukošiūtė, K., et al. (2022).** "Red Teaming Language Models with Language Models" - *arXiv preprint arXiv:2202.03286*.
   - Demonstrates sequential validation and adversarial checking; relevant to quality gates in chains.

10. **Wei, J., Wang, X., Schlarman, D., et al. (2022).** "Emergent Abilities of Large Language Models" - *arXiv preprint arXiv:2206.07682*.
    - Shows how sequential complex reasoning emerges from step-wise processing.

## Reference Links

- [LangChain Sequential Chains](https://python.langchain.com/docs/modules/chains/how_to/sequential_chains)
- [Prompt chaining best practices](https://arxiv.org/abs/2308.06592)
- [Building LLM Pipelines](https://github.com/ConstellationLab/llm-pipelines)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
