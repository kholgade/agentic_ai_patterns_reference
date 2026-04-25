---


# Judge Evaluator
title: "Judge Evaluator"
description: "A pattern where one agent evaluates the outputs of other agents to ensure quality and correctness."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["Quality assurance", "Output validation", "Scoring and feedback", "Calibration"]
dependencies: []
category: "evaluation"
---

# Judge Evaluator



## Detailed Explanation

The Judge Evaluator pattern introduces a dedicated evaluation agent that assesses the quality, correctness, and appropriateness of outputs produced by other agents. This pattern implements a separation of concerns where the "doing" agents focus on task execution while the "judging" agent provides independent quality assessment. The judge can apply consistent evaluation criteria, catch errors that producers might miss, and provide actionable feedback for improvement.

This pattern draws from software engineering practices like code review and automated testing, where separate entities verify the work of creators. The judge agent evaluates outputs against defined criteria such as accuracy, completeness, safety, and style, often producing structured scores or detailed feedback. Unlike self-evaluation where agents assess their own work, the judge provides an independent perspective that catches blind spots and biases inherent in self-assessment.

The judge-evaluator pattern is foundational for building reliable agentic systems, enabling automated quality control at scale. It serves as a critical component in recursive improvement loops, where outputs are repeatedly refined until they meet quality thresholds. Implementation considerations include defining clear evaluation criteria, handling edge cases, and determining when to accept versus reject outputs.

## ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    JUDGE EVALUATOR PATTERN                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    INPUT TASK                           │   │
│   └─────────────────────────┬───────────────────────────────┘   │
│                             │                                    │
│                             ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              AGENT 1 (Producer)                         │   │
│   │  ┌─────────────────────────────────────────────────┐    │   │
│   │  │                                                 │    │   │
│   │  │            Produces Output                      │    │   │
│   │  │                                                 │    │   │
│   │  └─────────────────────────────────────────────────┘    │   │
│   └─────────────────────────┬───────────────────────────────┘   │
│                             │                                    │
│                             ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              JUDGE AGENT                                │   │
│   │                                                         │   │
│   │  ┌─────────────────────────────────────────────────┐   │   │
│   │  │  Evaluation Criteria:                           │   │   │
│   │  │  ┌─────────────┐  ┌─────────────┐              │   │   │
│   │  │  │ Correctness │  │ Completeness│              │   │   │
│   │  │  │    85%      │  │    90%      │              │   │   │
│   │  │  └─────────────┘  └─────────────┘              │   │   │
│   │  │  ┌─────────────┐  ┌─────────────┐              │   │   │
│   │  │  │  Safety     │  │    Style    │              │   │   │
│   │  │  │   100%     │  │    70%      │              │   │   │
│   │  │  └─────────────┘  └─────────────┘              │   │   │
│   │  └─────────────────────────────────────────────────┘   │   │
│   │                                                         │   │
│   │  Overall Score: 82/100  Status: ACCEPT (with feedback) │   │
│   └─────────────────────────┬───────────────────────────────┘   │
│                             │                                    │
│              ┌──────────────┴──────────────┐                    │
│              │                             │                    │
│              ▼                             ▼                    │
│   ┌─────────────────────┐     ┌─────────────────────┐          │
│   │      ACCEPT         │     │       REJECT        │          │
│   │                     │     │                     │          │
│   │ Output passes       │     │ Return to producer  │          │
│   │ quality thresholds  │     │ with feedback       │          │
│   └─────────────────────┘     └─────────────────────┘          │
│                                                                 │
│   Evaluation Feedback:                                         │
│   ───────────────────────────────────────────────────────────   │
│   - Style score low: Add more section headers                  │
│   - Consider adding code examples to illustrate points         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Code Review

Automated code quality evaluation before submission.

```
Task: "Write a function to sort a list"

Judge evaluates:
- Correctness: 95% (algorithm is correct)
- Completeness: 100% (handles edge cases)
- Safety: 100% (no security issues)
- Style: 75% (needs more comments)

Passed with feedback: Add docstring explaining time complexity
```

### Example 2: Content Generation

Evaluating marketing copy for brand alignment.

```
Task: "Write product description for AI tool"

Judge evaluates:
- Correctness: 90% (accurate features)
- Completeness: 85% (missing pricing)
- Safety: 100% (appropriate)
- Style: 80% (needs stronger CTA)

Rejected: Add pricing information and stronger call-to-action
```

### Example 3: Data Analysis

Validating analytical outputs meet requirements.

```
Task: "Analyze sales data and provide insights"

Judge evaluates:
- Correctness: 85% (calculations correct)
- Completeness: 70% (missing regional breakdown)
- Safety: 100% (no PII exposed)
- Style: 90% (clear visualization)

Rejected: Add regional breakdown analysis
```

## Academic References

### LLM-Based Evaluation & Scoring

1. **Zheng, L., Chiang, W. L., Sheng, Y., et al. (2023).** "Judging LLM-as-a-Judge with an LLM-as-a-Reference" - *arXiv preprint arXiv:2306.05685*.
   - Foundational work on using LLMs as evaluators; directly applicable to judge evaluator pattern.

2. **Wang, L., Ma, C., Feng, X., et al. (2024).** "A Survey on Large Language Model based Autonomous Agents" - *arXiv preprint arXiv:2308.11432*.
   - Comprehensive survey including evaluation patterns in agentic systems.

3. **Wei, J., Tay, Y., Bommasani, R., et al. (2022).** "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" - *arXiv preprint arXiv:2201.11903*.
   - Shows step-by-step reasoning in evaluation; applicable to structured scoring frameworks.

### Quality Assurance & Validation

4. **Du, Y., Li, S., Torralba, A., et al. (2023).** "Improving Factuality and Reasoning in Language Models through Multiagent Debate" - *arXiv preprint arXiv:2305.14325*.
   - Demonstrates evaluation of multi-agent outputs and quality validation mechanisms.

5. **Perez, E., Ringer, S., Lukošiūtė, K., et al. (2022).** "Red Teaming Language Models with Language Models" - *arXiv preprint arXiv:2202.03286*.
   - Shows systematic evaluation and weakness identification; relevant to judge criteria design.

### Automated Scoring & Feedback

6. **Yao, S., Yu, D., Zhao, J., et al. (2023).** "ReAct: Synergizing Reasoning and Acting in Language Models" - *arXiv preprint arXiv:2210.03629*.
   - Framework for evaluating action correctness; applicable to structured feedback generation.

7. **Schick, T., Dwivedi-Yu, J., Dessì, R., et al. (2024).** "Toolformer: Language Models Can Teach Themselves to Use Tools" - *arXiv preprint arXiv:2302.04761*.
   - Demonstrates evaluation of tool selection appropriateness and output correctness.

### Independent Assessment

8. **Wei, J., Wang, X., Schlarman, D., et al. (2022).** "Emergent Abilities of Large Language Models" - *arXiv preprint arXiv:2206.07682*.
   - Addresses evaluation challenges and assessment methodologies for LLM outputs.

9. **Park, J. S., O'Neill, J., Baryan, R., et al. (2023).** "Generative Agents: Interactive Simulacra of Human Behavior" - *arXiv preprint arXiv:2304.03442*.
   - Demonstrates evaluation of agent behavior and output quality in simulation.

10. **Khattab, O., Santhanam, K., Li, X. L., et al. (2022).** "Demonstrate-Search-Predict: Composing Retrieval and Language Models for Knowledge-Intensive NLP" - *arXiv preprint arXiv:2212.14024*.
    - Shows evaluation at multiple pipeline stages; relevant to judge evaluation placement.

## Reference Links

- [LLM as Judge](https://arxiv.org/abs/2306.05685)
- [LangChain Judge Evaluator](https://python.langchain.com/docs/guides/evaluation/)
- [AutoGen Judge](https://microsoft.github.io/autogen/docs/)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
