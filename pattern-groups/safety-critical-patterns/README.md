---
group: "Safety-Critical Patterns"
patterns: ["Convergent AI Agent", "Agent Cascading Injection Defense", "Circuit Breaker"]
decision_axis: "safety-assurance"
spectrum: "preventive-to-recovery"
problem_statement: "How to ensure safety, security, and reliability in production agent systems"
pattern_relationship: "complementary"
---

# Safety-Critical Patterns

## Overview

These patterns address the unique challenges of deploying agent systems in safety-critical, production environments where failures have real consequences. Unlike patterns optimized for experimentation or rapid prototyping, these prioritize **determinism, verifiability, auditability, and graceful degradation**.

The core insight: safety in agent systems requires **defense in depth**—multiple layers of protection working together:

1. **Prevention** - Stop problems before they occur (CAAF's fail-safe determinism)
2. **Containment** - Limit blast radius when issues arise (ACI Defense's trust boundaries)
3. **Recovery** - Graceful handling of failures (Circuit Breaker's isolation)

---

## Pattern Comparison

### Convergent AI Agent (CAAF)

**What it does**: Transitions agent workflows from open-loop generation to closed-loop Fail-Safe Determinism through recursive decomposition, constraint registries, and structured semantic gradients.

**Flow**: Input → Recursive Decomposition → UAI Constraint Checking → Semantic Gradient Convergence → Deterministic Output

**Key Properties**:
- 100% paradox detection (vs 0% baseline)
- Monotonic convergence to correctness
- Deterministic outputs invariant to prompt hints
- Offline deployment capability

**Use When:**
- Operating in safety-critical domains (automotive, healthcare, industrial control)
- Multiple simultaneous constraints must never be violated
- System must detect logical paradoxes and physical contradictions
- Compliance and audit trails are mandatory

**Cost**: Higher computational overhead, complex constraint modeling

---

### Agent Cascading Injection Defense (ACI)

**What it does**: Prevents malicious instructions from cascading through multi-agent chains by implementing trust boundaries, message authentication, and input sanitization at agent boundaries.

**Flow**: External Input → Perimeter Sanitization → Trust Boundary Check → Signed Message → Capability Validation → Safe Delivery

**Key Properties**:
- Trust zone isolation
- Cryptographic message authentication
- Capability-based access control
- Runtime anomaly detection

**Use When:**
- Operating multi-agent systems with 3+ agents
- Agents have different trust levels or origins
- System handles sensitive data or privileged operations
- Operating in adversarial environments

**Cost**: Latency from crypto operations, complex trust modeling

---

### Circuit Breaker

**What it does**: Prevents cascade failures by temporarily disabling problematic components when error rates exceed thresholds, enabling graceful degradation.

**Flow**: Request → Error Rate Check → (If high) Open Circuit → Fallback Response / (If normal) Pass Through

**Key Properties**:
- Automatic failure detection
- Configurable thresholds
- Graceful degradation
- Self-healing capability

**Use When:**
- Calling external services with variable reliability
- Need to prevent cascade failures
- Want automatic recovery when services stabilize
- Operating under load with partial degradation acceptable

**Cost**: Additional latency for checks, requires fallback logic

---

## Side-by-Side Comparison

| Aspect | CAAF | ACI Defense | Circuit Breaker |
|--------|------|-------------|-----------------|
| **Threat Model** | Internal logic errors, constraint violations | External attacks, injection | External service failures |
| **Mechanism** | Deterministic constraint enforcement | Trust boundaries + authentication | Failure rate monitoring |
| **Timing** | Pre-execution | During execution | Runtime |
| **Response** | Prevent execution | Block propagation | Disable component |
| **Best For** | Safety-critical systems | Multi-agent security | Service resilience |
| **Complexity** | High | High | Medium |

---

## Defense in Depth Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   External Input                                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: PERIMETER (ACI Defense)                               │
│  • Input sanitization                                           │
│  • Trust boundary enforcement                                   │
│  • Message authentication                                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: EXECUTION (CAAF)                                      │
│  • Recursive atomic decomposition                               │
│  • UAI constraint checking                                      │
│  • Monotonic convergence                                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: RESILIENCE (Circuit Breaker)                        │
│  • Error rate monitoring                                        │
│  • Graceful degradation                                         │
│  • Self-healing                                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Safe Output                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

### CAAF - Avoid When:
- Low-stakes applications where safety guarantees are overkill
- Exploratory tasks where constraint violations are acceptable
- Rapid prototyping where development velocity matters more
- Creative generation where deterministic constraints would limit output

### ACI Defense - Avoid When:
- Single-agent systems (use Prompt Injection Defense instead)
- Trusted, closed environments where overhead isn't justified
- High-performance requirements where crypto adds latency
- Simple sequential pipelines without branching

### Circuit Breaker - Avoid When:
- All-or-nothing reliability is required
- No acceptable fallback exists
- System must process every request regardless of cost

---

## Hybrid Approach

**CAAF + ACI + Circuit Breaker**: Full defense in depth for production multi-agent systems.

```
User Input
    │
    ├──► ACI Perimeter ──► Rejected (malicious)
    │
    ├──► CAAF Core ──► Rejected (constraint violation)
    │
    ├──► Circuit Breaker ──► Degraded Mode (service down)
    │
    └──► Safe Execution ──► Validated Output
```

This combines prevention, containment, and recovery for maximum safety.

---

## Quick Examples

### Safety-Critical Customer Service
```python
# Layer 1: ACI Defense
sanitized_input = aci_defense.sanitize(user_message)

# Layer 2: CAAF Execution
result = caaf_agent.execute(
    task=sanitized_input,
    constraints=customer_service_constraints
)

# Layer 3: Circuit Breaker for external API
if circuit_breaker.is_closed():
    api_response = external_api.call(result)
else:
    api_response = fallback_cache.get(result)
```

### Multi-Agent Research System
```python
# ACI: Secure inter-agent communication
secure_message = aci.send_message(
    sender="research_agent",
    recipient="analysis_agent",
    payload=findings
)

# CAAF: Verify research conclusions
verified = caaf.verify(
    claims=findings,
    constraints=scientific_validity_constraints
)

# Circuit Breaker: Handle analysis service outage
if cb_analysis.is_available():
    analysis = analysis_service.process(verified)
else:
    analysis = local_heuristic.analyze(verified)
```

---

## Decision Tree

1. **Do you need deterministic safety guarantees?**
   - Yes → **CAAF**

2. **Are you operating multi-agent systems in adversarial environments?**
   - Yes → **ACI Defense**

3. **Do you need to handle external service failures gracefully?**
   - Yes → **Circuit Breaker**

4. **Need comprehensive protection?**
   - Use **All Three** in layers

---

## Summary

- **CAAF**: Fail-safe determinism through constraint enforcement. For safety-critical logic.
- **ACI Defense**: Trust boundaries for multi-agent security. For adversarial environments.
- **Circuit Breaker**: Graceful degradation on failure. For service resilience.
- Use **CAAF** for correctness, **ACI** for security, **Circuit Breaker** for reliability.
- Combine all three for defense-in-depth in production systems.


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
