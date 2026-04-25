# Agentic AI Patterns - Complete Reference

This folder contains **60+ design patterns** for building intelligent LLM-powered applications. Each pattern is in its own folder with detailed documentation, code examples, and academic references.

---

## 📖 How to Use This Folder

1. **Browse by category** below to find your pattern
2. **Click the pattern link** to open its README
3. **Each pattern includes**:
   - Detailed explanation with ASCII diagrams
   - When to use (and when NOT to use)
   - Real-world examples
   - 5-10 academic references
   - Python and JavaScript code examples

---

## 🎯 Quick Links to All 60 Patterns

### 1️⃣ Core Reasoning Patterns (10)

Master foundational reasoning strategies for complex problem-solving.

| Pattern | Folder | Purpose | Complexity |
|---------|--------|---------|------------|
| [Chain of Thought](./chain-of-thought/) | `chain-of-thought/` | Step-by-step reasoning articulation | Foundational |
| [ReAct](./react/) | `react/` | Reasoning + Tool use in loops | Foundational |
| [Tree of Thoughts](./tree-of-thoughts/) | `tree-of-thoughts/` | Multiple parallel reasoning branches | Intermediate |
| [Graph of Thoughts](./graph-of-thoughts/) | `graph-of-thoughts/` | Graph-based multi-hop reasoning | Intermediate |
| [Self Consistency](./self-consistency/) | `self-consistency/` | Majority voting across reasoning paths | Foundational |
| [Reflexion](./reflexion/) | `reflexion/` | Self-critique and improvement loops | Foundational |
| [Plan and Solve](./plan-and-solve/) | `plan-and-solve/` | Two-phase: plan decomposition then execution | Foundational |
| [Self-Ask](./self-ask/) | `self-ask/` | Decomposition-first sub-questioning | Foundational |
| [Least-to-Most](./least-to-most/) | `least-to-most/` | Solve from easy subproblems to hard | Intermediate |
| [Chain-of-Verification](./chain-of-verification/) | `chain-of-verification/` | Draft, verify claims, then revise | Intermediate |

---

### 2️⃣ Agent Architecture Patterns (8)

Build robust individual agents with tools, memory, and state management.

| Pattern | Folder | Purpose | Complexity |
|---------|--------|---------|------------|
| [Tool Use](./tool-use/) | `tool-use/` | Function calling and API integration | Foundational |
| [Multi-Tool Orchestration](./multi-tool-orchestration/) | `multi-tool-orchestration/` | Coordinating multiple tools in sequence | Intermediate |
| [Short Term Memory](./short-term-memory/) | `short-term-memory/` | Conversation context within session | Foundational |
| [Long Term Memory](./long-term-memory/) | `long-term-memory/` | Persistent cross-session memory | Intermediate |
| [Agent State Machine](./agent-state-machine/) | `agent-state-machine/` | Finite state workflows and automation | Intermediate |
| [Hierarchical Agent](./hierarchical-agent/) | `hierarchical-agent/` | Parent-child agent delegation | Intermediate |
| [Program-Aided Language (PAL)](./program-aided-language/) | `program-aided-language/` | Generate and execute code for reasoning | Intermediate |
| [MCP Tool Registry](./mcp-tool-registry/) | `mcp-tool-registry/` | Dynamic tool discovery and binding | Intermediate |

---

### 3️⃣ Multi-Agent Collaboration Patterns (7)

Coordinate multiple agents working together with various architectures.

| Pattern | Folder | Purpose | Complexity | Related |
|---------|--------|---------|------------|---------|
| [Supervisor Pattern](./supervisor-pattern/) | `supervisor-pattern/` | Central coordinator with state tracking | Intermediate | [vs Orchestrator](../pattern-groups/task-delegation/) |
| [Agent Swarm](./agent-swarm/) | `agent-swarm/` | Decentralized emergent behavior | Advanced | [vs Debate](../pattern-groups/debate-consensus/) |
| [Round Robin Collaboration](./round-robin-collaboration/) | `round-robin-collaboration/` | Fair turn-taking coordination | Foundational | [vs Chaining](../pattern-groups/sequential-processing/) |
| [Publish-Subscribe](./publish-subscribe/) | `publish-subscribe/` | Event-driven decoupled messaging | Intermediate | [Standalone](../pattern-groups/standalone-patterns/) |
| [Debate Pattern](./debate-pattern/) | `debate-pattern/` | Adversarial argumentation for decisions | Intermediate | [vs Swarm](../pattern-groups/debate-consensus/) |
| [Judge Evaluator](./judge-evaluator/) | `judge-evaluator/` | Independent quality assessment | Foundational | [vs Optimizer](../pattern-groups/evaluation-loop/) |
| [Hierarchical Team](./hierarchical-team/) | `hierarchical-team/` | Multi-level organizational structure | Intermediate | [vs Supervisor](../pattern-groups/task-delegation/) |

---

### 4️⃣ Workflow Orchestration Patterns (9)

Orchestrate multi-step processes and intelligent routing.

| Pattern | Folder | Purpose | Complexity | Related |
|---------|--------|---------|------------|---------|
| [Prompt Chaining](./prompt-chaining/) | `prompt-chaining/` | Sequential transformations | Foundational | [vs Round-Robin](../pattern-groups/sequential-processing/) |
| [Parallelization](./parallelization/) | `parallelization/` | Concurrent batch processing | Foundational | [Standalone](../pattern-groups/standalone-patterns/) |
| [Router Pattern](./router-pattern/) | `router-pattern/` | Intent-based request routing | Foundational | [vs Orchestrator](../pattern-groups/request-distribution/) |
| [Orchestrator Workers](./orchestrator-workers/) | `orchestrator-workers/` | Dynamic task decomposition | Intermediate | [vs Router](../pattern-groups/request-distribution/) |
| [Evaluator Optimizer](./evaluator-optimizer/) | `evaluator-optimizer/` | Iterative feedback-driven refinement | Intermediate | [vs Judge](../pattern-groups/evaluation-loop/) |
| [Human in the Loop](./human-in-the-loop/) | `human-in-the-loop/` | Human approval checkpoints | Foundational | [vs Gate](../pattern-groups/workflow-gates/) |
| [Gate Checkpoint](./gate-checkpoint/) | `gate-checkpoint/` | Automated validation gates | Foundational | [vs HITL](../pattern-groups/workflow-gates/) |
| [ReWOO](./rewoo/) | `rewoo/` | Plan with variables, then execute deterministically | Advanced | [vs Orchestrator](../pattern-groups/request-distribution/) |
| [LLM Compiler DAG](./llm-compiler-dag/) | `llm-compiler-dag/` | Compile workflows into dependency graphs | Advanced | [vs Chaining](../pattern-groups/sequential-processing/) |

---

### 5️⃣ RAG & Knowledge Integration (6)

Retrieval-augmented generation and knowledge systems.

| Pattern | Folder | Purpose | Complexity |
|---------|--------|---------|------------|
| [Basic RAG](./basic-rag/) | `basic-rag/` | Simple retrieve-then-generate | Foundational |
| [Advanced RAG](./advanced-rag/) | `advanced-rag/` | Query transformation and reranking | Intermediate |
| [Self-RAG](./self-rag/) | `self-rag/` | Conditional retrieval with reflection tokens | Intermediate |
| [Corrective RAG](./corrective-rag/) | `corrective-rag/` | Self-evaluation and correction loops | Intermediate |
| [Graph RAG](./graph-rag/) | `graph-rag/` | Knowledge graph-based retrieval | Advanced |
| [Multimodal RAG](./multimodal-rag/) | `multimodal-rag/` | Text, image, audio retrieval | Advanced |

---

### 6️⃣ Output & Safety Patterns (5)

Structured outputs, validation, and safety guardrails.

| Pattern | Folder | Purpose | Complexity |
|---------|--------|---------|------------|
| [Structured Output](./structured-output/) | `structured-output/` | JSON/XML schema enforcement | Foundational |
| [LLM as Judge](./llm-as-judge/) | `llm-as-judge/` | Multi-dimensional quality scoring | Emerging |
| [Guardrails Pattern](./guardrails-pattern/) | `guardrails-pattern/` | Input/output validation and filtering | Intermediate |
| [Output Parsing](./output-parsing/) | `output-parsing/` | Structured data extraction | Foundational |
| [Streaming with Interruptions](./streaming-interruptions/) | `streaming-interruptions/` | Real-time streaming with controls | Emerging |

---

### 7️⃣ Security & Access Control Patterns (5)

Security hardening, threat prevention, and compliance for agentic systems.

| Pattern | Folder | Purpose | Complexity |
|---------|--------|---------|------------|
| [Prompt Injection Defense](./prompt-injection-defense/) | `prompt-injection-defense/` | Protect against adversarial prompt attacks | Advanced |
| [Tool Permissioning](./tool-permissioning/) | `tool-permissioning/` | Fine-grained access control for tools | Intermediate |
| [Secret Handling](./secret-handling/) | `secret-handling/` | Secure credential management | Intermediate |
| [Sandboxing](./sandboxing/) | `sandboxing/` | Isolated execution environments | Advanced |
| [Audit Logging](./audit-logging/) | `audit-logging/` | Security event tracking and compliance | Intermediate |

---

### 8️⃣ Operational & Reliability Patterns (8)

Production reliability, cost optimization, monitoring.

| Pattern | Folder | Purpose | Complexity |
|---------|--------|---------|------------|
| [Retry Backoff](./retry-backoff/) | `retry-backoff/` | Exponential backoff on failures | Foundational |
| [Circuit Breaker](./circuit-breaker/) | `circuit-breaker/` | Failure isolation and fast-fail | Intermediate |
| [Cost-Aware Routing](./cost-aware-routing/) | `cost-aware-routing/` | Model selection by complexity | Emerging |
| [Caching Memoization](./caching-memoization/) | `caching-memoization/` | Response caching for duplicates | Foundational |
| [Observability Tracing](./observability-tracing/) | `observability-tracing/` | Built-in logging and debugging | Intermediate |
| [A/B Testing](./ab-testing/) | `ab-testing/` | Prompt/model experimentation | Mature |
| [Speculative Decoding](./speculative-decoding/) | `speculative-decoding/` | Draft-verify token generation for low latency | Advanced |
| [Fallback Cascade](./fallback-cascade/) | `fallback-cascade/` | Ordered graceful degradation across providers/models | Intermediate |

---

### 9️⃣ Advanced Techniques (7)

Meta-prompting, self-improvement, simulated environments.

| Pattern | Folder | Purpose | Complexity |
|---------|--------|---------|------------|
| [Meta-Prompting](./meta-prompting/) | `meta-prompting/` | Self-optimizing prompts | Emerging |
| [Few-Shot Learning](./few-shot-learning/) | `few-shot-learning/` | Dynamic in-context examples | Foundational |
| [Active Learning](./active-learning/) | `active-learning/` | Agent clarification requests | Emerging |
| [Simulated Environment](./simulated-environment/) | `simulated-environment/` | Sandbox testing and training | Emerging |
| [Constitutional AI](./constitutional-ai/) | `constitutional-ai/` | Principle-based self-alignment | Advanced |
| [Mixture of Agents](./mixture-of-agents/) | `mixture-of-agents/` | Ensemble agent collaboration | Advanced |
| [Context Compression](./context-compression/) | `context-compression/` | Summarize long context into compact memory | Intermediate |

---

## 🔍 Find Patterns by Use Case

### "I need to answer questions"
→ [Basic RAG](./basic-rag/) → [Advanced RAG](./advanced-rag/) → [Self-RAG](./self-rag/)

### "I need complex reasoning"
→ [Chain of Thought](./chain-of-thought/) → [ReAct](./react/) → [Tree of Thoughts](./tree-of-thoughts/)

### "I need multiple agents"
→ [Supervisor Pattern](./supervisor-pattern/) or [Hierarchical Team](./hierarchical-team/)

### "I need workflows"
→ [Prompt Chaining](./prompt-chaining/) → [Orchestrator Workers](./orchestrator-workers/)

### "I need safe production systems"
→ [Retry Backoff](./retry-backoff/) + [Circuit Breaker](./circuit-breaker/) + [Observability Tracing](./observability-tracing/) + [Gate Checkpoint](./gate-checkpoint/)

### "I need security hardening"
→ [Prompt Injection Defense](./prompt-injection-defense/) + [Tool Permissioning](./tool-permissioning/) + [Secret Handling](./secret-handling/)

### "I need compliance and audit"
→ [Audit Logging](./audit-logging/) + [Guardrails Pattern](./guardrails-pattern/) + [Human in the Loop](./human-in-the-loop/)

### "I need to make decisions"
→ [Debate Pattern](./debate-pattern/) or [Self Consistency](./self-consistency/)

### "I need knowledge integration"
→ [Basic RAG](./basic-rag/) → [Graph RAG](./graph-rag/) or [Multimodal RAG](./multimodal-rag/)

---

## 📋 Pattern Categories Summary

| Category | Count | Best For |
|----------|-------|----------|
| Core Reasoning | 10 | Math, logic, step-by-step analysis |
| Agent Architecture | 8 | Building individual agent components |
| Multi-Agent Collaboration | 7 | Teams, swarms, coordination |
| Workflow Orchestration | 9 | Pipelines, task routing, approval flows |
| RAG & Knowledge | 6 | Q&A, document search, knowledge grounding |
| Output & Safety | 5 | Data extraction, compliance, safety |
| Operational & Reliability | 8 | Production systems, monitoring, resilience |
| Advanced Techniques | 7 | Optimization, learning, experimentation |

---

## 🔗 Related Resources

### Pattern Comparisons
If you're unsure which pattern to choose, visit the **[Pattern Groups](../pattern-groups/)** folder:
- [Evaluation Loop](../pattern-groups/evaluation-loop/) — Compare Judge vs Evaluator-Optimizer
- [Task Delegation](../pattern-groups/task-delegation/) — Compare Orchestrator vs Supervisor vs Hierarchical
- [Sequential Processing](../pattern-groups/sequential-processing/) — Compare Chaining vs Round-Robin
- [Request Distribution](../pattern-groups/request-distribution/) — Compare Router vs Orchestrator
- [Debate & Consensus](../pattern-groups/debate-consensus/) — Compare Debate vs Swarm
- [Workflow Gates](../pattern-groups/workflow-gates/) — Compare Gate vs Human-in-Loop
- [Standalone Patterns](../pattern-groups/standalone-patterns/) — Parallelization & Pub-Sub

### Main Project README
See **[../README.md](../README.md)** for:
- Project overview
- Getting started guides
- Use case mapping
- How to navigate the library

### Reference Materials
- **[REFERENCE_MATERIALS.md](../REFERENCE_MATERIALS.md)** - Complete list of 168 papers, tools, and resources

---

## 📖 Each Pattern Includes

Every pattern folder contains:

```
pattern-name/
├── README.md                    # Complete explanation
│   ├── What it does
│   ├── When to use (and when NOT to)
│   ├── ASCII diagrams
│   ├── Real-world examples
│   ├── 5-10 academic references
│   └── Related links
│
├── code.py                      # Python implementation
│
└── example.js                   # JavaScript/TypeScript example
```

---

## 📊 Statistics

```
Total Patterns: 60+
Total Folders: 8 categories

Complexity Distribution:
├── Foundational (mature, well-tested): 20 patterns
├── Intermediate (proven in production): 22 patterns
├── Emerging (newer, experimental): 6 patterns
└── Advanced (specialized, complex): 4+ patterns

Academic References: 32+ arxiv papers, 130+ tools/docs/benchmarks (see [../../REFERENCE_MATERIALS.md](../../REFERENCE_MATERIALS.md))
Implementation Examples: Python + JavaScript for each pattern
```

---

## 🚀 Getting Started

1. **Know your use case** (choose from "Find Patterns by Use Case" above)
2. **Click the pattern link** to open its README
3. **Read the explanation** with diagrams and examples
4. **Review academic references** for deeper understanding
5. **Check related pattern comparisons** if needed (in [pattern-groups](../pattern-groups/))
6. **Use code examples** to implement (Python or JavaScript)

---

## 💡 Tips

- **Too many choices?** Start with foundational patterns (marked as "Foundational")
- **Unsure between two?** Check [pattern-groups](../pattern-groups/) for detailed comparisons
- **Want academic rigor?** Each pattern includes 5-10 peer-reviewed references
- **Need code?** Every pattern has Python and JavaScript examples
- **Building production?** Combine patterns from "Operational & Reliability" category

---

## 📧 Questions?

Each pattern README includes:
- When NOT to use it
- Common mistakes
- Tradeoffs to consider
- Similar patterns to explore
- Related academic papers


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
