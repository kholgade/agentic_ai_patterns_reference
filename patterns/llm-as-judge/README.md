---
title: LLM as Judge
description: Using an LLM to evaluate and judge outputs from other AI systems
complexity: medium
model_maturity: emerging
typical_use_cases: ["Quality assessment", "Output evaluation", "Benchmarking"]
dependencies: []
category: evaluation
---

The LLM as Judge pattern leverages a capable language model to evaluate, score, and provide feedback on outputs from other AI components or systems. This pattern addresses a fundamental challenge in AI development: objective quality assessment. Traditional metrics like BLEU or ROUGE scores fail to capture semantic quality, nuance, and helpfulness. By using an LLM as a judge, we gain access to sophisticated evaluation capabilities that understand context, intent, and subtleties. The judge model can assess outputs across multiple dimensions including accuracy, relevance, coherence, safety, and helpfulness. This pattern is particularly valuable for evaluating the output quality of AI agents, comparing different response strategies, and building automated quality assurance pipelines.

The architectural pattern involves three key components: the evaluee (the system being judged), the judge prompt (defining evaluation criteria and format), and the judge model itself. The judge prompt must be carefully crafted to minimize bias, define clear scoring criteria, and provide chain-of-thought reasoning prompts. Self-consistency improves reliability—using multiple judge prompts and aggregating scores reduces variance. The pattern works bidirectionally: standalone LLMs can self-judge their own outputs, or a dedicated judge model can evaluate other agents. Key considerations include preventing judge bias toward certain response styles, handling edge cases where output quality is genuinely ambiguous, and ensuring reproducibility through temperature and seed control.

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM AS JUDGE FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   EVALUEE   │    │   JUDGE     │    │   SCORE &    │  │
│  │   SYSTEM    │───▶│   PROMPT    │───▶│  FEEDBACK   │  │
│  │              │    │            │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │               │
│         ▼                   ▼                    ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Agent      │    │ Evaluation  │    │   Numeric  │  │
│  │ Output       │    │   Criteria  │    │   Score    │  │
│  │              │    │ Rubric       │    │   + Reasons │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
│  ┌───────────────────────────────��─────���───────────────┐   │
│  │            SELF-EVALUATION LOOP                     │   │
│  │                                                     │   │
│  │   ┌──────────┐    ┌──────────┐    ┌──────────┐   │   │
│  │   │ Generate │───▶│   Judge  │───▶│  Retry/  │   │   │
│  │   │ Output   │    │  Self    │    │  Improve │   │   │
│  │   └──────────┘    └──────────┘    └──────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Evaluating Agent Responses

```python
# Criteria for evaluating customer service agent
customer_service_criteria = """
Evaluate the response based on:
1. Accuracy: Does it correctly address the user's issue?
2. Relevance: Does it stay on topic and provide relevant information?
3. Tone: Is it polite, professional, and empathetic?
4. Completeness: Does it fully answer the user's question?
5. Actionability: Can the user act on the information provided?
"""

def evaluate_agent_response(agent_output: str, user_query: str) -> JudgeResult:
    """Evaluate a customer service agent response."""
    return judge_output(
        output_to_judge=agent_output,
        criteria=customer_service_criteria,
        context=f"User query: {user_query}"
    )

# Example usage
agent_response = """
Thank you for reaching out! I understand you're having trouble 
with your password reset. Here's what you need to do:

1. Go to the login page
2. Click "Forgot Password"
3. Enter your email address
4. Check your inbox for the reset link
5. Click the link and create a new password

The link will expire in 24 hours. Let me know if you need more help!
"""

result = evaluate_agent_response(
    agent_response,
    "I can't reset my password"
)
print(f"Score: {result.overall_score}/10")
```

### Example 2: Benchmarking Two Systems

```python
def benchmark_systems(
    system_a_output: str,
    system_b_output: str,
    benchmark_prompt: str
) -> dict:
    """Compare outputs from two different systems."""
    
    criteria = "Compare helpfulness, accuracy, and clarity."
    
    # Judge both outputs
    result_a = judge_output(system_a_output, criteria, benchmark_prompt)
    result_b = judge_output(system_b_output, criteria, benchmark_prompt)
    
    return {
        "system_a": {
            "score": result_a.overall_score,
            "summary": result_a.summary
        },
        "system_b": {
            "score": result_b.overall_score,
            "summary": result_b.summary
        },
        "winner": "A" if result_a.overall_score > result_b.overall_score else "B"
    }

# Example: Comparing two RAG implementations
system_a = "Based on the documents found, the key information is..."
system_b = "After searching the knowledge base, here's the answer..."

benchmark = benchmark_systems(system_a, system_b, "What is the capital of France?")
```

### Example 3: Self-Correction Loop

```python
def self_correcting_generation(
    initial_prompt: str,
    quality_criteria: str,
    max_iterations: int = 3,
    min_score: float = 8.0
) -> tuple[str, JudgeResult]:
    """Generate output with self-evaluation and improvement."""
    
    criteria = """
    Evaluate the generated response on:
    1. Factual accuracy
    2. Completeness
    3. Clarity of explanation
    4. Appropriate detail level
    """
    
    # Initial generation
    current_output = generate_response(initial_prompt)
    result = judge_output(current_output, criteria)
    
    for iteration in range(max_iterations):
        if result.overall_score >= min_score:
            break
            
        # Request improvement
        improvement_prompt = f"""
        Previous output scored {result.overall_score}/10.
        
        Summary of issues: {result.summary}
        
        Specific improvements needed:
        {chr(10).join(f"- {s}" for s in result.improvement_suggestions)}
        
        Please regenerate with these improvements in mind:
        {initial_prompt}
        """
        
        current_output = generate_response(improvement_prompt)
        result = judge_output(current_output, criteria)
    
    return current_output, result
```

## Comparison: Judge vs Metrics

```
┌────────────────────────────────────────────────────────────────┐
│              EVALUATION METHOD COMPARISON                       │
├──────────────────┬──────────────┬──────────────┬───────────────┤
│    Method        │  Semantic    │   Cost       │  Reliability  │
├──────────────────┼──────────────┼──────────────┼───────────────┤
│ LLM as Judge     │  Excellent   │   Higher     │    High       │
│ BLEU/ROUGE       │    Poor      │    Low       │    Medium     │
│ Embedding Sim.   │   Medium     │   Medium     │    Medium     │
│ Human Eval       │  Excellent  │   Highest    │  Excellent    │
│ Combined         │  Excellent   │   Medium     │  Excellent    │
└──────────────────┴──────────────┴──────────────┴───────────────┘
```

## Best Practices

1. **Define clear rubrics** - Ambiguous criteria lead to inconsistent scores
2. **Use chain-of-thought reasoning** - Forces judge to explain its thinking
3. **Multiple perspectives** - Reduce bias by using varied judge prompts
4. **Handle ties gracefully** - Some outputs genuinely have the same quality
5. **Monitor judge consistency** - Track agreement rates over time

## Reference Links

- [OpenAI Evals](https://github.com/openai/evals)
- [LLM as a Judge - DeepMind](https://arxiv.org/abs/2306.05685)
- [Chatbot Arena - LLM Evaluation](https://lmsys.org/)
- [AlpacaEval](https://tatsu-lab.github.io/alpaca_eval/)
- [Self-Reflection with LLM as Judge](https://arxiv.org/abs/2303.11391)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
