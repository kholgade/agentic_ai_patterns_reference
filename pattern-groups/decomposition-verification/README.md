---
group: "Decomposition & Verification"
patterns: ["Self-Ask", "Least-to-Most", "Chain-of-Verification"]
decision_axis: "reliability-strategy"
spectrum: "decompose-to-verify"
problem_statement: "How to improve reasoning reliability through explicit structure"
pattern_relationship: "complementary"
---

# Decomposition & Verification Patterns

## Overview

These patterns improve reasoning reliability using explicit structure. Self-Ask and Least-to-Most focus on decomposition strategy; Chain-of-Verification focuses on post-draft checking.

---

## Pattern Comparison

### Self-Ask
- Breaks a question into sub-questions first
- Good for multi-hop QA and traceable reasoning
- Best when intermediate answers are directly useful

### Least-to-Most
- Orders subproblems from easy to hard
- Good for compositional tasks with dependency buildup
- Best when early simpler steps unlock harder ones

### Chain-of-Verification
- Drafts an answer, generates verification checks, then revises
- Good for factual reliability and reducing unsupported claims
- Best when correctness matters more than raw speed

---

## Side-by-Side

| Aspect | Self-Ask | Least-to-Most | Chain-of-Verification |
|--------|----------|---------------|------------------------|
| Primary stage | Pre-solve decomposition | Pre-solve decomposition ordering | Post-solve verification |
| Core goal | Coverage of sub-questions | Progressive reasoning stability | Hallucination/error reduction |
| Typical latency | Medium | Medium | Higher |
| Best for | Multi-hop QA | Compositional reasoning | High-accuracy answers |

---

## Summary

- **Self-Ask**: Decompose into targeted sub-questions.
- **Least-to-Most**: Solve in increasing difficulty order.
- **Chain-of-Verification**: Verify then revise final answer.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
