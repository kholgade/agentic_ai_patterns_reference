---
title: Meta Prompting
description: Using LLM-generated prompts to guide subsequent LLM behavior for better results
complexity: medium
model_maturity: emerging
typical_use_cases: ["Prompt engineering", "Self-optimization", "Adaptive prompting"]
dependencies: []
category: prompting
---

## Detailed Explanation

Meta prompting is an advanced prompting technique where an LLM generates or refines prompts that will be used to guide another LLM call or its own subsequent behavior. This creates a feedback loop where the model can iteratively improve its outputs by analyzing what worked or failed in previous attempts. The core insight is that LLMs can be prompted to act as "prompt engineers" themselves, analyzing task requirements and crafting optimized instructions. This approach is particularly powerful for complex tasks where a single prompt may not capture all nuances, or where the optimal prompting strategy depends on the specific type of input being processed.

The meta prompting loop typically consists of three stages: initial prompt execution, output analysis, and prompt refinement. During analysis, the LLM evaluates whether the previous prompt achieved the desired outcome and identifies specific failure modes or areas for improvement. This self-reflection is guided by meta-prompting instructions that ask the model to critique rather than solve. The refined prompts can then target specific edge cases or incorporate additional constraints identified during analysis. Research has shown that meta prompting can significantly improve performance on tasks requiring reasoning, creativity, or specialized output formats.

## ASCII Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    META PROMPTING LOOP                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Generate        │────▶│   Execute        │────▶│   Analyze       │
│   Initial        │     │   Prompt         │     │   Output        │
│   Prompt (P₁)   │     │   with LLM       │     │   Critically    │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                          │
                              ┌─────────────────────────────┘
                              ▼
                              ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Use Refined    │◀────│   Refine         │◀────│   Identify       │
│   Prompt (Pₙ)    │     │   Prompt         │     │   Improvements   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                              │
                              ▼
                        ┌──────────────────��
                        │   Final Output   │
                        │   Delivered      │
                        └──────────────────┘
```

## Examples

### Example 1: Code Generation

Initial prompt generates functional but basic code. After analysis finds it lacks error handling and documentation, the refined prompt explicitly requests "production-ready code with proper error handling, docstrings, and type hints."

### Example 2: Creative Writing

Initial prompt for a story receives analysis noting "lack of character development." Refined prompt includes "develop distinct character motivations and arcs" as explicit requirements, improving subsequent outputs.

### Example 3: Technical Explanation

A complex technical concept explained poorly. Analysis identifies missing analogies and assuming too much prior knowledge. Refined prompt requests "explain as to a motivated beginner, include real-world analogies."

## Reference Links

- [Meta-Prompting: Language Models as Prompt Generators](https://arxiv.org/abs/2311.12595) - Original research paper on meta prompting techniques
- [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651) - Related iterative improvement methodology
- [Prompting Guide: Meta-Prompting](https://www.promptingguide.ai/techniques/meta-prompting) - Practical applications and examples


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
