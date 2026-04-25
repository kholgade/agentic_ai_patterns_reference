# Agentic AI Pattern Groups - Complete Index

This directory organizes patterns into semantic groups based on their closeness, purpose, and decision criteria.

---

## Pattern Groups

### 1. [Evaluation & Improvement Loop](./evaluation-loop/README.md)
**Patterns**: Judge Evaluator, Evaluator Optimizer

Quality assessment and iterative refinement. Core difference: Judge is a gate, Evaluator-Optimizer adds improvement loop.

- Judge Evaluator: Quality inspection without implied action
- Evaluator Optimizer: Quality inspection WITH guaranteed improvement until threshold

---

### 2. [Task Delegation & Orchestration](./task-delegation/README.md)
**Patterns**: Orchestrator Workers, Supervisor Pattern, Hierarchical Team

Delegating work to specialized agents with varying complexity and control. Three levels of sophistication.

- Orchestrator Workers: Fast, parallel, dynamic decomposition
- Supervisor Pattern: Adaptive, stateful, feedback-driven
- Hierarchical Team: Structured, accountable, multi-layer

---

### 3. [Sequential & Collaborative Processing](./sequential-processing/README.md)
**Patterns**: Prompt Chaining, Round Robin Collaboration

Sequential processing with different emphasis. Chaining is step-based (task stages), Round Robin is agent-based (rotating perspectives).

- Prompt Chaining: Different prompts, sequential stages, transform data
- Round Robin Collaboration: Same task, rotating agents, collaborative refinement

---

### 4. [Request Distribution](./request-distribution/README.md)
**Patterns**: Router Pattern, Orchestrator Workers

Routing/dispatching requests to handlers. Core difference: Router selects from pre-existing handlers, Orchestrator creates dynamic tasks.

- Router Pattern: Intent classification, static handler selection
- Orchestrator Workers: Dynamic decomposition, parallel execution

---

### 5. [Debate & Consensus Patterns](./debate-consensus/README.md)
**Patterns**: Debate Pattern, Agent Swarm

Multiple perspectives for better solutions. Debate is structured and mediated, Swarm is decentralized and emergent.

- Debate Pattern: Structured, moderated, formal roles, deterministic consensus
- Agent Swarm: Decentralized, emergent, informal roles, probabilistic convergence

---

### 6. [Workflow Gates & Approval](./workflow-gates/README.md)
**Patterns**: Gate Checkpoint, Human in the Loop

Controlling workflow progression through checkpoints. Gates are automated, HITL is human judgment-based.

- Gate Checkpoint: Automated, rule-based, fast, scalable
- Human in the Loop: Human judgment, contextual, slower, limited throughput
- Hybrid approach: Gates for routine, humans for exceptions

---

### 7. [Standalone Patterns](./standalone-patterns/README.md)
**Patterns**: Parallelization, Publish-Subscribe

Fundamental architectural choices that serve specific purposes without significant overlap with other patterns.

- Parallelization: Speed via concurrent execution. For batch throughput.
- Publish-Subscribe: Decoupling via event distribution. For event-driven systems.

---

### 8. [Decomposition & Verification](./decomposition-verification/README.md)
**Patterns**: Self-Ask, Least-to-Most, Chain-of-Verification

Reasoning quality through explicit structure. Self-Ask and Least-to-Most shape decomposition before solving; Chain-of-Verification validates after drafting.

- Self-Ask: Break down into focused sub-questions
- Least-to-Most: Solve from easy to hard dependencies
- Chain-of-Verification: Verify claims, then revise output

---

### 9. [Execution-Centric Planning](./execution-planning/README.md)
**Patterns**: Program-Aided Language (PAL), ReWOO, LLM Compiler DAG

Execution-oriented planning and reasoning. PAL uses code execution, ReWOO uses variable-bound plans, DAG compilation structures dependencies for orchestration.

- PAL: Generate code and execute for deterministic reasoning
- ReWOO: Plan with reusable intermediate variables
- LLM Compiler DAG: Compile and run dependency graphs

---

### 10. [Runtime Resilience & Efficiency](./runtime-efficiency/README.md)
**Patterns**: Speculative Decoding, Fallback Cascade

Production runtime optimization and resilience under failure.

- Speculative Decoding: Draft-verify token generation for latency
- Fallback Cascade: Ordered graceful degradation on failure

---

### 11. [Context & Tooling Infrastructure](./context-tooling/README.md)
**Patterns**: Context Compression, MCP Tool Registry

Infrastructure patterns for long-running agent reliability and interoperable tool usage.

- Context Compression: Preserve high-signal memory in bounded context windows
- MCP Tool Registry: Standardized tool discovery and dynamic binding

---

## Quick Decision Guide

**Need to improve output quality?** → [Evaluation & Improvement Loop](./evaluation-loop/README.md)

**Need to delegate work to agents?** → [Task Delegation & Orchestration](./task-delegation/README.md)

**Need sequential processing?** → [Sequential & Collaborative Processing](./sequential-processing/README.md)

**Need to route/dispatch requests?** → [Request Distribution](./request-distribution/README.md)

**Need multiple perspectives?** → [Debate & Consensus Patterns](./debate-consensus/README.md)

**Need workflow approval?** → [Workflow Gates & Approval](./workflow-gates/README.md)

**Need speed or event distribution?** → [Standalone Patterns](./standalone-patterns/README.md)

**Need better decomposition or verification?** → [Decomposition & Verification](./decomposition-verification/README.md)

**Need execution-oriented planning?** → [Execution-Centric Planning](./execution-planning/README.md)

**Need runtime latency/reliability improvements?** → [Runtime Resilience & Efficiency](./runtime-efficiency/README.md)

**Need memory/tooling infrastructure patterns?** → [Context & Tooling Infrastructure](./context-tooling/README.md)

---

## How to Use These Guides

Each group folder contains a detailed README with:

1. **Overview**: What problem the patterns solve
2. **Individual Pattern Breakdowns**: Purpose, flow, when to use
3. **Comparison Table**: Side-by-side differences
4. **When NOT to Use**: Anti-patterns and tradeoffs
5. **Code Snippets**: Minimal examples showing structure
6. **Decision Trees**: How to choose between patterns in the group

---

## All Patterns at a Glance

| Pattern | Category | Best For |
|---------|----------|----------|
| Judge Evaluator | Evaluation | Quality gates, scoring |
| Evaluator Optimizer | Evaluation | Iterative refinement |
| Orchestrator Workers | Delegation | Fast parallel analysis |
| Supervisor Pattern | Delegation | Complex adaptive workflows |
| Hierarchical Team | Delegation | Large projects, accountability |
| Prompt Chaining | Sequential | Data pipelines, transformations |
| Round Robin | Sequential | Collaborative refinement |
| Router Pattern | Distribution | Intent-based routing |
| Orchestrator Workers | Distribution | Dynamic task decomposition |
| Debate Pattern | Consensus | High-stakes decisions |
| Agent Swarm | Consensus | Exploration, optimization |
| Gate Checkpoint | Approval | Routine quality checks |
| Human in the Loop | Approval | Compliance, accountability |
| Parallelization | Infrastructure | Batch throughput |
| Publish-Subscribe | Infrastructure | Event-driven systems |
| Self-Ask | Decomposition | Multi-hop sub-questioning |
| Least-to-Most | Decomposition | Compositional easy-to-hard solving |
| Chain-of-Verification | Verification | Draft-check-revise reliability |
| Program-Aided Language (PAL) | Execution Planning | Deterministic compute via code |
| ReWOO | Execution Planning | Variable-bound tool workflows |
| LLM Compiler DAG | Execution Planning | Dependency-graph orchestration |
| Speculative Decoding | Runtime Efficiency | Lower generation latency |
| Fallback Cascade | Runtime Resilience | Graceful degradation under failures |
| Context Compression | Context Infrastructure | Long-context memory compaction |
| MCP Tool Registry | Tooling Infrastructure | Dynamic tool discovery and binding |

---

## Related Resources

- Original pattern definitions: `../patterns/` directory
- Each group's README contains links to the original patterns


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
