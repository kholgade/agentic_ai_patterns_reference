---
group: "Evaluation & Improvement Loop"
patterns: ["Judge Evaluator", "Evaluator Optimizer"]
---

# Evaluation & Improvement Loop Patterns

## Overview

Both patterns separate evaluation from execution. The core difference: one evaluates (Judge), the other evaluates AND improves (Evaluator-Optimizer).

---

## Pattern Comparison

### Judge Evaluator

**What it does**: An independent agent assesses outputs from worker agents against defined criteria. Acts as a quality gate—provides feedback but doesn't fix.

**Flow**: Work → Judge Assessment → Feedback/Reject Signal

**State**: Stateless—judge doesn't loop back.

**Use When:**
- You need independent quality validation
- Feedback is informational (e.g., code review comments)
- Downstream processes handle rejections
- You want to measure quality without iteration
- External systems will act on feedback

**Example**: Code review agent that scores pull requests without submitting fixes.

**Cost**: Single evaluation pass.

---

### Evaluator Optimizer

**What it does**: Evaluator checks output quality, Optimizer incorporates feedback to refine. Creates an iterative loop until criteria are met or max iterations reached.

**Flow**: Generate → Evaluate → Optimize → [Loop back to Generate] → Final Output

**State**: Stateful—tracks iterations and improvement history.

**Use When:**
- Output quality must improve to meet thresholds
- You have clear stopping criteria (quality score, iteration limit)
- The optimizer can meaningfully act on feedback
- Iterative refinement adds value
- You control the full loop

**Example**: Writing quality improvement—generator produces draft, evaluator scores, optimizer revises until readability score reaches target.

**Cost**: Multiple passes × latency + tokens.

---

## Side-by-Side Comparison

| Aspect | Judge Evaluator | Evaluator Optimizer |
|--------|-----------------|-------------------|
| **Agents** | 1 judge + N workers | 2 agents (evaluator + optimizer) |
| **Feedback** | Informational | Actionable & iterative |
| **Loop** | None | Yes, until criteria met |
| **State** | Stateless | Stateful (tracks iterations) |
| **Stopping Point** | Always stops after evaluation | Continues until quality threshold or max iterations |
| **Cost** | Low (1 pass per output) | Higher (N passes until converged) |
| **Best for** | Quality gates, audits, scoring | Refinement, iterative improvement |

---

## When NOT to Use

### Judge Evaluator - Avoid When:
- You need outputs to actually improve (use Evaluator-Optimizer)
- No one will act on the feedback
- Feedback loop is necessary for the process
- Output must meet hard quality thresholds before use

### Evaluator Optimizer - Avoid When:
- Improvement is not possible or too expensive
- Evaluation criteria are vague or unmeasurable
- Single-pass output is sufficient
- Feedback doesn't correlate with better results
- You need immediate response (no iteration time)

---

## Quick Examples

### Judge Evaluator
```python
# Judge gives feedback, doesn't fix
judge_feedback = evaluate_code(worker_output, criteria)
# Output: {"score": 7.2, "issues": [...], "reviewer": "code_judge"}
# Someone else (human or another system) acts on feedback
```

### Evaluator Optimizer
```python
# Iterative refinement
output = initial_generation()
for i in range(max_iterations):
    score = evaluate(output)
    if score >= threshold:
        break
    output = optimize(output, evaluation_feedback)
return output
```

---

## Summary

- **Judge**: Quality inspection without implied action.
- **Evaluator-Optimizer**: Quality inspection WITH guaranteed improvement until threshold.
- Pick Judge if feedback is the deliverable; pick Evaluator-Optimizer if the improved output is the goal.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
