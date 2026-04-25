---
group: "Debate & Consensus Patterns"
patterns: ["Debate Pattern", "Agent Swarm"]
---

# Debate & Consensus Patterns

## Overview

Both generate multiple perspectives for better solutions, but differ fundamentally: Debate is structured and mediated, Swarm is decentralized and emergent.

---

## Pattern Comparison

### Debate Pattern

**What it does**: Multiple agents take assigned roles (proponent, skeptic, devil's advocate), engage in structured argument rounds with a moderator, converge on robust conclusions through adversarial collaboration.

**Flow**: Moderator → Assign Roles → Round 1 (all present arguments) → Moderator evaluates → Round 2 (respond to counterarguments) → ... → Synthesis → Final Conclusion

**Structure**: Formal, orchestrated, predefined roles.

**Coordination**: Centralized moderator controls rounds and synthesis.

**Use When:**
- High-stakes decisions need thorough exploration
- Multiple valid viewpoints exist
- You want to surface weaknesses systematically
- Roles and debate structure are predefined
- Clear consensus/synthesis is the goal
- Audit trail of reasoning is important

**Example**: Feature decision—one agent argues for, one against, one raises edge cases, moderator synthesizes into decision.

**Cost**: Multiple rounds × agents, moderator overhead.

**Convergence**: Guaranteed (moderator enforces rounds).

---

### Agent Swarm

**What it does**: Decentralized agents self-organize through local interactions, emergent communication, and stigmergy (indirect coordination via environment). No central controller; behavior emerges from simple local rules.

**Flow**: Agents → Local Interactions → Message Passing → Emergent Patterns → Collective Solution

**Structure**: Informal, self-organized, emergent roles.

**Coordination**: Decentralized (peer-to-peer communication, shared environment).

**Use When:**
- Problem is exploratory (not predetermined solutions)
- Diversity of perspectives is crucial
- Self-organization is desirable
- System should be fault-tolerant (loss of one agent doesn't collapse)
- Emergent behavior is valuable
- Central control is undesirable or impossible

**Example**: Swarm optimization problem—agents explore solution space independently, share discoveries, collectively converge on better optimum.

**Cost**: Uncertain (depends on convergence); potentially more parallel efficiency.

**Convergence**: Probabilistic (emergent, not guaranteed).

---

## Side-by-Side Comparison

| Aspect | Debate | Swarm |
|--------|--------|-------|
| **Coordination** | Centralized (Moderator) | Decentralized (Peer-to-peer) |
| **Structure** | Formal, predetermined | Informal, emergent |
| **Roles** | Pre-assigned (proponent, skeptic, etc.) | Emergent, fluid |
| **Rounds** | Fixed structure (R1, R2, synthesis) | Continuous interaction |
| **Communication** | Explicit arguments | Implicit (stigmergy, signals) |
| **Control** | Moderator enforces progress | Self-organized |
| **Convergence** | Deterministic (moderator decides) | Probabilistic (emergent) |
| **Best for** | High-stakes decisions, reasoning | Exploration, optimization, discovery |
| **Fault Tolerance** | Single moderator is bottleneck | Robust to individual failures |
| **Complexity** | Medium (controlled) | High (emergent, hard to predict) |

---

## When NOT to Use

### Debate Pattern - Avoid When:
- Problem requires exploration without predetermined roles
- Central moderator is a bottleneck
- Robustness to agent failures is critical
- Emergent behavior is desirable
- Simple problem doesn't warrant debate overhead
- Decentralized coordination is needed

### Agent Swarm - Avoid When:
- Clear decision-making process is required (use Debate)
- Audit trail of reasoning is important
- You need deterministic outcomes
- Problem has few "right" answers to converge on
- Communication must be explicit and tracked
- High-stakes decisions (emergence is too unpredictable)

---

## Quick Examples

### Debate Pattern
```python
moderator = Moderator(debate_topic="Should we ship feature X?")
agents = [
    Agent(role="proponent"),
    Agent(role="skeptic"),
    Agent(role="devil_advocate")
]

for round in range(num_rounds):
    arguments = [agent.present_argument(context) for agent in agents]
    moderator.evaluate(arguments)

conclusion = moderator.synthesize(all_arguments)
```

### Agent Swarm
```python
swarm = Swarm(agents=[Agent() for _ in range(20)])
shared_environment = Environment()

for iteration in range(max_iterations):
    for agent in swarm:
        local_solution = agent.explore(shared_environment)
        agent.communicate_discovery(shared_environment)  # Stigmergy
    
    if swarm.converged():
        break

best_solution = shared_environment.global_best()
```

---

## When to Use Each

**Debate** if:
- "I need reasoning I can audit and verify"
- "Different viewpoints should argue systematically"
- "Final decision should be clear and justified"
- High-stakes, well-defined problem

**Swarm** if:
- "I want emergence from simple local rules"
- "Problem is exploratory/optimization"
- "Fault tolerance matters"
- "Central control is undesirable"

---

## Summary

- **Debate**: Structured, moderated, formal roles, deterministic consensus. For reasoned decisions.
- **Swarm**: Decentralized, emergent, informal roles, probabilistic convergence. For exploration.
- Use Debate for decisions needing justification; use Swarm for optimization needing emergence.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
