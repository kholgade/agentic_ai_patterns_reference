---
group: "Workflow Gates & Approval"
patterns: ["Gate Checkpoint", "Human in the Loop"]
decision_axis: "review-automation"
spectrum: "automated-to-human"
problem_statement: "How to control workflow progression through checkpoints"
pattern_relationship: "alternatives"
---

# Workflow Gates & Approval Patterns

## Overview

Both control workflow progression through checkpoints, but differ fundamentally: Gates are automated criteria-based, HITL is human judgment-based.

---

## Pattern Comparison

### Gate Checkpoint

**What it does**: Automated quality gates evaluate output against predefined criteria. Approves advancement, requires revision, or terminates based on evaluation results. No human required.

**Flow**: Stage Output → Evaluate Against Criteria → Pass Gate? (Yes: Advance, No: Recycle/Reject)

**Evaluation**: Rules, scores, automated checks.

**Decision Maker**: System/AI (deterministic).

**Use When:**
- Quality criteria are well-defined and measurable
- Routine validations can be automated
- Human review is impractical at scale
- Clear pass/fail thresholds exist
- Speed and consistency matter
- Cost efficiency is important

**Example**: Content pipeline—gate checks for length, keyword density, readability score. Auto-approve if all pass; reject if any fail.

**Cost**: Low (automated, batch-friendly).

**Throughput**: High (no human bottleneck).

---

### Human in the Loop (HITL)

**What it does**: Human explicitly reviews, modifies, or approves AI output before progression. Human judgment is central to the process, not automated checks.

**Flow**: AI Output → Human Review → Approve/Reject/Modify → Progression

**Evaluation**: Human judgment, contextual understanding, accountability.

**Decision Maker**: Human (subjective, contextual).

**Use When:**
- Compliance/regulatory requirements mandate human review
- Human accountability is necessary
- Outputs require contextual judgment
- Edge cases need human interpretation
- High stakes (legal, financial, medical, public)
- AI confidence varies (conditional human review)

**Example**: Legal document generation—human lawyer reviews for compliance, tone, legal accuracy before sending to client.

**Cost**: High (human time).

**Throughput**: Limited by human availability.

---

## Side-by-Side Comparison

| Aspect | Gate Checkpoint | Human in the Loop |
|--------|-----------------|------------------|
| **Evaluation** | Automated, rules-based | Human judgment |
| **Criteria** | Well-defined, measurable | Contextual, subjective |
| **Decision** | Deterministic | Subjective |
| **Speed** | Fast | Slower |
| **Cost** | Low | High |
| **Scalability** | Linear with requests | Limited by human availability |
| **Accountability** | System accountability | Human accountability |
| **Judgment** | Fixed thresholds | Adaptive, contextual |
| **Edge Cases** | Must be predefined | Handled on case-by-case basis |
| **Best for** | Routine approvals, quality gates | Compliance, high stakes |

---

## Hybrid Approach

**Gate + HITL**: Use gates for routine approvals, escalate failures to humans.

```
Output → Gate (check criteria) 
  → Pass? → Approve
  → Fail? → Send to Human Review
```

This combines efficiency (most approvals automated) with safety (humans handle exceptions).

---

## When NOT to Use

### Gate Checkpoint - Avoid When:
- Criteria are vague or unmeasurable (use HITL)
- Human judgment is required
- Compliance/regulatory review is needed
- Edge cases are common
- Context matters more than rules
- Accountability requires human sign-off

### Human in the Loop - Avoid When:
- Criteria are well-defined and measurable (use Gate)
- Throughput is critical (speed matters)
- High volume requires automation
- Judgments are routine and predictable
- Human unavailability is a problem
- Cost must be minimized

---

## Quick Examples

### Gate Checkpoint
```python
output = generate_content(prompt)

criteria = {
    "length": (100, 500),  # word count range
    "reading_level": (7, 10),  # grade level
    "keyword_density": (0.02, 0.05)
}

score = evaluate(output, criteria)

if all(criteria[k].contains(score[k]) for k in criteria):
    approve(output)  # Advance
else:
    reject(output)  # Recycle or fail
```

### Human in the Loop
```python
output = generate_legal_doc(client_request)

# Send to human for review
review = human_lawyer.review(output)  # Approve/Reject/Modify

if review.status == "approved":
    send_to_client(output)
elif review.status == "modified":
    send_to_client(review.modified_output)
else:
    regenerate_with_feedback(review.feedback)
```

### Gate + HITL Hybrid
```python
output = generate_email(customer)

# First: automated gate
criteria_check = check_tone_length_clarity(output)

if criteria_check.pass:
    send_email(output)  # Auto-approve
else:
    human_review = send_to_human()  # Escalate
    if human_review.approve:
        send_email(output)
    else:
        regenerate_with_feedback(human_review.feedback)
```

---

## Decision Matrix

| Scenario | Use |
|----------|-----|
| Content meets well-defined criteria | Gate |
| Legal/compliance document | HITL |
| Routine quality checks | Gate |
| High-stakes decision | HITL |
| Edge cases are common | HITL |
| Mostly routine, occasional exceptions | Gate + HITL Hybrid |
| High volume, low risk | Gate |
| Low volume, high risk | HITL |

---

## Summary

- **Gate**: Automated, rule-based, fast, scalable. For routine quality checks.
- **HITL**: Human judgment, contextual, slower, limited throughput. For compliance/accountability.
- **Hybrid**: Gates for routine, humans for exceptions. Best of both worlds.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
