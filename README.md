# Agentic AI Patterns Library

**A comprehensive, production-ready collection of 50+ design patterns, architectures, and techniques for building intelligent AI-powered applications using Large Language Models (LLMs).**

This library provides battle-tested patterns that address the full lifecycle of agentic AI development—from core reasoning strategies to multi-agent coordination, workflow orchestration, knowledge integration, safety mechanisms, and operational reliability.

## 🎯 What This Library Offers

- **50+ Production Patterns**: Proven design patterns for LLM-powered systems
- **Real-World Architectures**: Multi-agent systems, RAG pipelines, orchestration patterns
- **Academic References**: 500+ peer-reviewed papers cited across patterns
- **Pattern Relationships**: Clear documentation of pattern similarities, differences, and when to use each
- **Multiple Implementations**: Python code examples and JavaScript/TypeScript usage
- **Complete Explanations**: ASCII diagrams, detailed use cases, tradeoff analysis

## 📖 Why This Library Matters

Building robust agentic AI systems is complex. You need to:
- Understand **reasoning patterns** (Chain-of-Thought, ReAct, Tree-of-Thoughts)
- Design **multi-agent architectures** (Supervisor, Swarm, Hierarchical Teams)
- Handle **workflow orchestration** (Prompt Chaining, Router, Orchestrator Workers)
- Integrate **knowledge systems** (RAG, Self-RAG, Graph RAG)
- Ensure **safety and quality** (Gates, Guardrails, Human-in-Loop)
- Maintain **reliability** (Retry strategies, Circuit Breakers, Caching)

This library consolidates all of this into accessible, well-documented patterns.

---

## 🗂️ Table of Contents

- [Quick Navigation](#quick-navigation)
- [Pattern Groups & Comparisons](#pattern-groups--comparisons)
- [Model Maturity & Capability Matrix](#model-maturity--capability-matrix)
- [Categories Overview](#categories-overview)
- [All 50 Patterns](#all-50-patterns)
- [Getting Started](#getting-started)
- [How to Use This Library](#how-to-use-this-library)

---

## 🔗 Quick Navigation

### Pattern Groups (Similar Patterns Explained)
For patterns that are similar or overlapping, start with the **Pattern Groups** folder for detailed comparisons:

- **[Evaluation & Improvement Loop](./pattern-groups/evaluation-loop/)** — Judge Evaluator vs Evaluator Optimizer
- **[Task Delegation & Orchestration](./pattern-groups/task-delegation/)** — Orchestrator Workers vs Supervisor vs Hierarchical Team
- **[Sequential & Collaborative Processing](./pattern-groups/sequential-processing/)** — Prompt Chaining vs Round Robin
- **[Request Distribution](./pattern-groups/request-distribution/)** — Router vs Orchestrator
- **[Debate & Consensus](./pattern-groups/debate-consensus/)** — Debate Pattern vs Agent Swarm
- **[Workflow Gates & Approval](./pattern-groups/workflow-gates/)** — Gate Checkpoint vs Human-in-Loop
- **[Standalone Patterns](./pattern-groups/standalone-patterns/)** — Parallelization & Pub-Sub

👉 **Start here if you're choosing between similar patterns!**

---

## 📚 Pattern Groups & Comparisons

Not sure which pattern to use? Check the **[Pattern Groups INDEX](./pattern-groups/INDEX.md)** for:
- Side-by-side pattern comparisons
- When to use each pattern
- When NOT to use each pattern
- Decision trees for choosing
- Concrete code snippets

---

## 🧠 Model Maturity & Capability Matrix

Different patterns require different model capabilities. This **4-quadrant matrix** helps you choose patterns based on your model size and capabilities.

### 4-Quadrant Model Capability Map

![Model Maturity & Capability Matrix](./images/Model-Maturity-Capability-Matrix.png)

**Legend:**
- ⭐ **Q1**: Premium Models (Claude Opus, GPT-4) - 14 patterns - Advanced Reasoning + Multi-Agent
- ⚠️ **Q2**: Constrained Design (7B models) - 8 patterns - Reasoning Intensive Tasks
- ✅ **Q3**: Simple & Efficient (Local models) - 16 patterns - Simple Tasks + Templates
- 🚀 **Q4**: Large & Efficient (Sonnet, 3.5) - 12 patterns - Complex Orchestration + Efficiency

### Quadrant Breakdown

#### **Q1: Advanced Reasoning + Multi-Agent** ⭐ Premium Models
**Best Models**: Claude Opus, GPT-4, o1, Gemini 2.0

**Patterns** (14):
- [Tree of Thoughts](./patterns/tree-of-thoughts/) — Complex multi-branch reasoning
- [Graph of Thoughts](./patterns/graph-of-thoughts/) — Graph-based reasoning
- [Debate Pattern](./patterns/debate-pattern/) — Adversarial argumentation
- [Agent Swarm](./patterns/agent-swarm/) — Decentralized emergent behavior
- [Constitutional AI](./patterns/constitutional-ai/) — Principle-based alignment
- [Mixture of Agents](./patterns/mixture-of-agents/) — Ensemble collaboration
- [Corrective RAG](./patterns/corrective-rag/) — Self-evaluation loops
- [Graph RAG](./patterns/graph-rag/) — Knowledge graph reasoning
- [Multimodal RAG](./patterns/multimodal-rag/) — Complex multi-modal integration
- [Hierarchical Team](./patterns/hierarchical-team/) — Multi-level organization
- [Meta-Prompting](./patterns/meta-prompting/) — Self-optimizing prompts
- [Active Learning](./patterns/active-learning/) — Uncertainty-aware clarification
- [Simulated Environment](./patterns/simulated-environment/) — Complex sandbox scenarios
- [Cost-Aware Routing](./patterns/cost-aware-routing/) — Intelligent model selection

**Why These**: Require strong reasoning, planning, evaluation capabilities; benefit from multi-turn reasoning; handle complex abstractions.

---

#### **Q2: Reasoning Intensive Tasks** ⚠️ Use Careful Design
**Best Models**: Open-source 7B-13B (Mistral, Llama), Smaller APIs

**Patterns** (8):
- [Reflexion](./patterns/reflexion/) — Simple self-critique loops
- [Plan and Solve](./patterns/plan-and-solve/) — Explicit decomposition
- [Self Consistency](./patterns/self-consistency/) — Majority voting
- [Few-Shot Learning](./patterns/few-shot-learning/) — In-context examples
- [Self-RAG](./patterns/self-rag/) — Reflection tokens for routing
- [Advanced RAG](./patterns/advanced-rag/) — Query transformation
- [Output Parsing](./patterns/output-parsing/) — Structured extraction
- [Guardrails Pattern](./patterns/guardrails-pattern/) — Input/output validation

**Constraints**: Limited reasoning depth; works better with guided prompts; needs strong few-shot examples; benefits from decomposition; simpler architectures.

**Strategy**: Use structured prompts, simpler chains, avoid multi-turn debates, rely on retrieval + templates.

---

#### **Q3: Simple Tasks + Templates** ✅ Optimal for Small Models
**Best Models**: Edge models, 3B-7B local models, API-lite options

**Patterns** (16):
- [Chain of Thought](./patterns/chain-of-thought/) — Simple step-by-step (with few-shots)
- [ReAct](./patterns/react/) — Basic reasoning + tools (structured)
- [Prompt Chaining](./patterns/prompt-chaining/) — Sequential transformations
- [Tool Use](./patterns/tool-use/) — Function calling
- [Short Term Memory](./patterns/short-term-memory/) — Conversation context
- [Router Pattern](./patterns/router-pattern/) — Simple intent classification
- [Basic RAG](./patterns/basic-rag/) — Retrieve then generate
- [Structured Output](./patterns/structured-output/) — JSON/XML output
- [Retry Backoff](./patterns/retry-backoff/) — Failure recovery
- [Caching Memoization](./patterns/caching-memoization/) — Response caching
- [Gate Checkpoint](./patterns/gate-checkpoint/) — Automated validation
- [Parallelization](./parallelization/) — Batch processing
- [Round Robin Collaboration](./patterns/round-robin-collaboration/) — Sequential turns
- [Human in the Loop](./patterns/human-in-the-loop/) — Human approval
- [Streaming with Interruptions](./patterns/streaming-interruptions/) — Real-time control
- [A/B Testing](./patterns/ab-testing/) — Experimentation

**Why These**: Simple operations; deterministic routing; static pipelines; benefit from templates; don't require deep reasoning.

---

#### **Q4: Complex Orchestration + Efficiency** 🚀 Maximum Efficiency
**Best Models**: Any frontier model (Claude, GPT-4, o1)

**Patterns** (12):
- [Multi-Tool Orchestration](./patterns/multi-tool-orchestration/) — Complex tool chains
- [Orchestrator Workers](./patterns/orchestrator-workers/) — Dynamic decomposition
- [Supervisor Pattern](./patterns/supervisor-pattern/) — Intelligent coordination
- [Publish-Subscribe](./patterns/publish-subscribe/) — Event-driven systems
- [Judge Evaluator](./patterns/judge-evaluator/) — Quality assessment
- [Evaluator Optimizer](./patterns/evaluator-optimizer/) — Iterative refinement
- [Long Term Memory](./patterns/long-term-memory/) — Semantic search + embedding
- [Agent State Machine](./patterns/agent-state-machine/) — Complex state transitions
- [Hierarchical Agent](./patterns/hierarchical-agent/) — Multi-level delegation
- [LLM as Judge](./patterns/llm-as-judge/) — Multi-dimensional scoring
- [Observability Tracing](./patterns/observability-tracing/) — Detailed logging
- [Circuit Breaker](./patterns/circuit-breaker/) — Failure isolation

**Benefit**: Leverage full capability for efficiency; handle dynamic scenarios; reduce infrastructure needs.

---

### Model Size & Capability Reference

| Model Category | Examples | Capability Level |
|---|---|---|
| **Ultra-Small** | 3B | Basic tasks only (Q3) |
| **Small Local** | 7B-13B (Mistral, Llama 2) | Simple reasoning (Q2, Q3) |
| **Medium Open** | 34B-70B (Llama 3, Code Llama) | Intermediate reasoning (Q2, Q3, Q4) |
| **Large API** | Claude Sonnet, GPT-3.5 | Strong reasoning (Q1, Q4) |
| **Frontier** | Claude Opus, GPT-4, o1 | Expert reasoning (Q1, Q4) |

---

### Quick Selection Guide

**"I have a small 7B model"**
→ Start with Q3 patterns (Chain of Thought + structured prompts)
→ Use Q2 patterns with careful design (simple decomposition)
→ Avoid Q1 (too complex)

**"I have Claude Sonnet / GPT-3.5"**
→ Use Q4 patterns (dynamic orchestration)
→ Can handle most Q3 patterns with less structure
→ Some Q1 patterns work with careful design

**"I have Claude Opus / GPT-4"**
→ Use all Q1 patterns (complex reasoning)
→ Use Q4 for efficiency and cost savings
→ Combine patterns freely

**"I'm running locally (open-source)"**
→ Focus on Q3 + Q2 patterns
→ Use simple chains, strong templates
→ Add retrieval for knowledge (RAG)
→ Minimize reasoning complexity

---

### Model Maturity Level Indicators

**Foundational Maturity** (Works with Q3 models):
- Can follow instructions reliably
- Can extract structured data
- Can use tools with clear schemas
- Can chain simple steps

**Intermediate Maturity** (Works with Q2/Q4 models):
- Can do multi-step reasoning
- Can self-critique
- Can evaluate quality
- Can handle ambiguity

**Advanced Maturity** (Works with Q1 models):
- Can debate and argue
- Can optimize prompts
- Can manage complex agents
- Can reason about reasoning

---

## Categories Overview

| Category | Count | Description | Key Use Cases |
|----------|-------|-------------|---|
| **Core Reasoning** | 7 | Step-by-step reasoning strategies for complex problem solving | Math, logic, analysis, decision-making |
| **Agent Architecture** | 6 | Core agent components: tools, memory, state management | Building robust individual agents |
| **Multi-Agent Collaboration** | 7 | Patterns for multiple agents working together | Teams, swarms, hierarchies, debates |
| **Workflow Orchestration** | 7 | Orchestrating multi-step processes and intelligent routing | Pipelines, task distribution, approval flows |
| **RAG & Knowledge Integration** | 6 | Retrieval-augmented generation and knowledge systems | Q&A, document search, context grounding |
| **Output & Safety** | 5 | Structured outputs, validation, and safety guardrails | Data extraction, compliance, safety |
| **Operational Reliability** | 6 | Reliability, cost optimization, caching, observability | Production systems, monitoring, resilience |
| **Advanced Techniques** | 6 | Meta-prompting, self-improvement, simulated environments | Optimization, learning, experimentation |

---

## 📋 All 50 Patterns by Category

### 1️⃣ Core Reasoning Patterns (7)
| Pattern | Complexity | Use Case | Link |
|---------|------------|----------|------|
| [Chain of Thought](./patterns/chain-of-thought/) | Foundational | Step-by-step reasoning articulation | [README](./patterns/chain-of-thought/README.md) |
| [ReAct](./patterns/react/) | Foundational | Reasoning + Tool use in loops | [README](./patterns/react/README.md) |
| [Tree of Thoughts](./patterns/tree-of-thoughts/) | Intermediate | Multiple parallel reasoning branches | [README](./patterns/tree-of-thoughts/README.md) |
| [Graph of Thoughts](./patterns/graph-of-thoughts/) | Intermediate | Graph-based multi-hop reasoning | [README](./patterns/graph-of-thoughts/README.md) |
| [Self Consistency](./patterns/self-consistency/) | Foundational | Majority voting across reasoning paths | [README](./patterns/self-consistency/README.md) |
| [Reflexion](./patterns/reflexion/) | Foundational | Self-critique and improvement loops | [README](./patterns/reflexion/README.md) |
| [Plan and Solve](./patterns/plan-and-solve/) | Foundational | Two-phase: plan decomposition then execution | [README](./patterns/plan-and-solve/README.md) |

### 2️⃣ Agent Architecture Patterns (6)
| Pattern | Complexity | Use Case | Link |
|---------|------------|----------|------|
| [Tool Use](./patterns/tool-use/) | Foundational | Function calling and API integration | [README](./patterns/tool-use/README.md) |
| [Multi-Tool Orchestration](./patterns/multi-tool-orchestration/) | Intermediate | Coordinating multiple tools in sequence | [README](./patterns/multi-tool-orchestration/README.md) |
| [Short Term Memory](./patterns/short-term-memory/) | Foundational | Conversation context within session | [README](./patterns/short-term-memory/README.md) |
| [Long Term Memory](./patterns/long-term-memory/) | Intermediate | Persistent cross-session memory | [README](./patterns/long-term-memory/README.md) |
| [Agent State Machine](./patterns/agent-state-machine/) | Intermediate | Finite state workflows and automation | [README](./patterns/agent-state-machine/README.md) |
| [Hierarchical Agent](./patterns/hierarchical-agent/) | Intermediate | Parent-child agent delegation | [README](./patterns/hierarchical-agent/README.md) |

### 3️⃣ Multi-Agent Collaboration Patterns (7)
| Pattern | Complexity | Use Case | Link | Comparison |
|---------|------------|----------|------|-----------|
| [Supervisor Pattern](./patterns/supervisor-pattern/) | Intermediate | Central coordinator with state tracking | [README](./patterns/supervisor-pattern/README.md) | [vs Orchestrator](./pattern-groups/task-delegation/) |
| [Agent Swarm](./patterns/agent-swarm/) | Advanced | Decentralized emergent behavior | [README](./patterns/agent-swarm/README.md) | [vs Debate](./pattern-groups/debate-consensus/) |
| [Round Robin Collaboration](./patterns/round-robin-collaboration/) | Foundational | Fair turn-taking coordination | [README](./patterns/round-robin-collaboration/README.md) | [vs Chaining](./pattern-groups/sequential-processing/) |
| [Publish-Subscribe](./patterns/publish-subscribe/) | Intermediate | Event-driven decoupled messaging | [README](./patterns/publish-subscribe/README.md) | [Standalone](./pattern-groups/standalone-patterns/) |
| [Debate Pattern](./patterns/debate-pattern/) | Intermediate | Adversarial argumentation for decisions | [README](./patterns/debate-pattern/README.md) | [vs Swarm](./pattern-groups/debate-consensus/) |
| [Judge Evaluator](./patterns/judge-evaluator/) | Foundational | Independent quality assessment | [README](./patterns/judge-evaluator/README.md) | [vs Optimizer](./pattern-groups/evaluation-loop/) |
| [Hierarchical Team](./patterns/hierarchical-team/) | Intermediate | Multi-level organizational structure | [README](./patterns/hierarchical-team/README.md) | [vs Supervisor](./pattern-groups/task-delegation/) |

### 4️⃣ Workflow Orchestration Patterns (7)
| Pattern | Complexity | Use Case | Link | Comparison |
|---------|------------|----------|------|-----------|
| [Prompt Chaining](./patterns/prompt-chaining/) | Foundational | Sequential transformations | [README](./patterns/prompt-chaining/README.md) | [vs Round-Robin](./pattern-groups/sequential-processing/) |
| [Parallelization](./patterns/parallelization/) | Foundational | Concurrent batch processing | [README](./patterns/parallelization/README.md) | [Standalone](./pattern-groups/standalone-patterns/) |
| [Router Pattern](./patterns/router-pattern/) | Foundational | Intent-based request routing | [README](./patterns/router-pattern/README.md) | [vs Orchestrator](./pattern-groups/request-distribution/) |
| [Orchestrator Workers](./patterns/orchestrator-workers/) | Intermediate | Dynamic task decomposition | [README](./patterns/orchestrator-workers/README.md) | [vs Router](./pattern-groups/request-distribution/) |
| [Evaluator Optimizer](./patterns/evaluator-optimizer/) | Intermediate | Iterative feedback-driven refinement | [README](./patterns/evaluator-optimizer/README.md) | [vs Judge](./pattern-groups/evaluation-loop/) |
| [Human in the Loop](./patterns/human-in-the-loop/) | Foundational | Human approval checkpoints | [README](./patterns/human-in-the-loop/README.md) | [vs Gate](./pattern-groups/workflow-gates/) |
| [Gate Checkpoint](./patterns/gate-checkpoint/) | Foundational | Automated validation gates | [README](./patterns/gate-checkpoint/README.md) | [vs HITL](./pattern-groups/workflow-gates/) |

### 5️⃣ RAG & Knowledge Integration (6)
| Pattern | Complexity | Use Case | Link |
|---------|------------|----------|------|
| [Basic RAG](./patterns/basic-rag/) | Foundational | Simple retrieve-then-generate | [README](./patterns/basic-rag/README.md) |
| [Advanced RAG](./patterns/advanced-rag/) | Intermediate | Query transformation and reranking | [README](./patterns/advanced-rag/README.md) |
| [Self-RAG](./patterns/self-rag/) | Intermediate | Conditional retrieval with reflection tokens | [README](./patterns/self-rag/README.md) |
| [Corrective RAG](./patterns/corrective-rag/) | Intermediate | Self-evaluation and correction loops | [README](./patterns/corrective-rag/README.md) |
| [Graph RAG](./patterns/graph-rag/) | Advanced | Knowledge graph-based retrieval | [README](./patterns/graph-rag/README.md) |
| [Multimodal RAG](./patterns/multimodal-rag/) | Advanced | Text, image, audio retrieval | [README](./patterns/multimodal-rag/README.md) |

### 6️⃣ Output & Safety Patterns (5)
| Pattern | Complexity | Use Case | Link |
|---------|------------|----------|------|
| [Structured Output](./patterns/structured-output/) | Foundational | JSON/XML schema enforcement | [README](./patterns/structured-output/README.md) |
| [LLM as Judge](./patterns/llm-as-judge/) | Emerging | Multi-dimensional quality scoring | [README](./patterns/llm-as-judge/README.md) |
| [Guardrails Pattern](./patterns/guardrails-pattern/) | Intermediate | Input/output validation and filtering | [README](./patterns/guardrails-pattern/README.md) |
| [Output Parsing](./patterns/output-parsing/) | Foundational | Structured data extraction | [README](./patterns/output-parsing/README.md) |
| [Streaming with Interruptions](./patterns/streaming-interruptions/) | Emerging | Real-time streaming with controls | [README](./patterns/streaming-interruptions/README.md) |

### 7️⃣ Operational & Reliability Patterns (6)
| Pattern | Complexity | Use Case | Link |
|---------|------------|----------|------|
| [Retry Backoff](./patterns/retry-backoff/) | Foundational | Exponential backoff on failures | [README](./patterns/retry-backoff/README.md) |
| [Circuit Breaker](./patterns/circuit-breaker/) | Intermediate | Failure isolation and fast-fail | [README](./patterns/circuit-breaker/README.md) |
| [Cost-Aware Routing](./patterns/cost-aware-routing/) | Emerging | Model selection by complexity | [README](./patterns/cost-aware-routing/README.md) |
| [Caching Memoization](./patterns/caching-memoization/) | Foundational | Response caching for duplicates | [README](./patterns/caching-memoization/README.md) |
| [Observability Tracing](./patterns/observability-tracing/) | Intermediate | Built-in logging and debugging | [README](./patterns/observability-tracing/README.md) |
| [A/B Testing](./patterns/ab-testing/) | Mature | Prompt/model experimentation | [README](./patterns/ab-testing/README.md) |

### 8️⃣ Advanced Techniques (6)
| Pattern | Complexity | Use Case | Link |
|---------|------------|----------|------|
| [Meta-Prompting](./patterns/meta-prompting/) | Emerging | Self-optimizing prompts | [README](./patterns/meta-prompting/README.md) |
| [Few-Shot Learning](./patterns/few-shot-learning/) | Foundational | Dynamic in-context examples | [README](./patterns/few-shot-learning/README.md) |
| [Active Learning](./patterns/active-learning/) | Emerging | Agent clarification requests | [README](./patterns/active-learning/README.md) |
| [Simulated Environment](./patterns/simulated-environment/) | Emerging | Sandbox testing and training | [README](./patterns/simulated-environment/README.md) |
| [Constitutional AI](./patterns/constitutional-ai/) | Advanced | Principle-based self-alignment | [README](./patterns/constitutional-ai/README.md) |
| [Mixture of Agents](./patterns/mixture-of-agents/) | Advanced | Ensemble agent collaboration | [README](./patterns/mixture-of-agents/README.md) |

---

---

## 🚀 Getting Started

### I'm New to Agentic AI. Where Do I Start?

1. **Read the [Quick Navigation](#quick-navigation) section** above for pattern groups
2. **Start with foundational patterns**:
   - [Chain of Thought](./patterns/chain-of-thought/README.md) - Learn reasoning
   - [Tool Use](./patterns/tool-use/README.md) - Add capabilities
   - [Prompt Chaining](./patterns/prompt-chaining/README.md) - Build pipelines
   - [Router Pattern](./patterns/router-pattern/README.md) - Route requests

3. **Pick a use case and follow the pattern links**:
   - **"I need to answer questions"** → RAG patterns → Basic RAG → Advanced RAG
   - **"I need multiple agents"** → [Supervisor Pattern](./patterns/supervisor-pattern/README.md) or [Agent Swarm](./patterns/agent-swarm/README.md)
   - **"I need workflows"** → Prompt Chaining → Orchestrator Workers
   - **"I need decision-making"** → [Debate Pattern](./patterns/debate-pattern/README.md)

### I'm Choosing Between Similar Patterns

Go to **[Pattern Groups](./pattern-groups/INDEX.md)** for detailed comparisons:
- Which is better: Supervisor vs Orchestrator vs Hierarchical?
- When to use Judge vs Evaluator-Optimizer?
- Debate vs Swarm - what's the difference?

Each pattern group has side-by-side comparisons, decision trees, and code examples.

### I Want to Learn Academic Background

Each pattern includes **5-10 academic references** from:
- **AI Safety via Debate** (Irving et al., 2018)
- **Generative Agents** (Park et al., 2023)
- **Chain-of-Thought Prompting** (Wei et al., 2022)
- **ReAct** (Yao et al., 2023)
- And 500+ more peer-reviewed papers

👉 Open any pattern README.md to find academic references at the bottom.

---

## 📖 Detailed Pattern Briefs

### 1. Core Reasoning Patterns (7)

#### 1. Chain of Thought
**folder:** `chain-of-thought/`
- Guides LLM to articulate reasoning step-by-step before final answer
- Works by providing few-shot examples with reasoning chains
- Best for: math, logic, multi-step analysis problems

#### 2. ReAct
**folder:** `react/`
- Interleaves reasoning (thought) with acting (tool use) and observation
- Loop: Think → Action → Observation → Think...
- Best for: tool-augmented question answering, research tasks

#### 3. Tree of Thoughts
**folder:** `tree-of-thoughts/`
- Explores multiple reasoning branches in parallel
- Each branch evaluated and best path selected
- Best for: creative writing, strategy, complex decisions

#### 4. Graph of Thoughts
**folder:** `graph-of-thoughts/`
- Generalized reasoning as graph with nodes and edges
- Supports aggregation, scoring, critique nodes
- Best for: complex multi-hop reasoning, analysis

#### 5. Self Consistency
**folder:** `self-consistency/`
- Generate multiple reasoning paths, vote on consensus
- Improves accuracy by reducing single-path errors
- Best for: reasoning tasks requiring high accuracy

#### 6. Reflexion
**folder:** `reflexion/`
- Actor generates → Critic evaluates → Reflector improves
- Maintains external memory of past failures
- Best for: iterative refinement, learning from mistakes

#### 7. Plan and Solve
**folder:** `plan-and-solve/`
- Two-phase: (1) Generate plan, (2) Execute stepwise
- Planning phase decomposes into sub-tasks
- Best for: complex multi-step tasks, project planning

---

### 2. Agent Architecture Patterns (6)

#### 8. Tool Use
**folder:** `tool-use/`
- LLM invokes external functions/API calls
- Define tools with JSON schema, LLM decides when to call
- Best for: web search, calculations, database queries

#### 9. Multi-Tool Orchestration
**folder:** `multi-tool-orchestration/`
- Coordinate multiple tools in sequence or parallel
- Dynamic dependency resolution
- Best for: complex workflows, data pipelines

#### 10. Short Term Memory
**folder:** `short-term-memory/`
- Maintain conversation context within session
- Sliding window, summary, or pruning strategies
- Best for: conversation continuity, stateful interactions

#### 11. Long Term Memory
**folder:** `long-term-memory/`
- Persistent storage across sessions via vector embeddings
- Semantic search over user history
- Best for: user preferences, cross-session continuity

#### 12. Agent State Machine
**folder:** `agent-state-machine/`
- Model agent behavior as finite states with transitions
- Explicit workflow: idle → processing → waiting → complete
- Best for: predictable workflows, process automation

#### 13. Hierarchical Agent
**folder:** `hierarchical-agent/`
- Parent agent delegates to child sub-agents
- Decomposition: manager → specialized workers
- Best for: large-scale projects, multi-domain tasks

---

### 3. Multi-Agent Collaboration Patterns (7)

#### 14. Supervisor Pattern
**folder:** `supervisor-pattern/`
- Central supervisor routes tasks to specialized workers
- Task queue, state tracking, progress monitoring
- Best for: task distribution, load balancing

#### 15. Agent Swarm
**folder:** `agent-swarm/`
- Decentralized autonomous agents
- Emergent behavior through local interactions
- Best for: massive parallel optimization, exploration

#### 16. Round Robin Collaboration
**folder:** `round-robin-collaboration/`
- Agents take turns in sequence
- Scheduler enforces turn order, task queuing
- Best for: sequential refinement, fair resource use

#### 17. Publish Subscribe
**folder:** `publish-subscribe/`
- Event-driven messaging between agents
- Topic-based routing, message broker
- Best for: real-time updates, decoupled systems

#### 18. Debate Pattern
**folder:** `debate-pattern/`
- Multiple agents present opposing viewpoints
- Proponent, skeptic, synthesist roles
- Best for: decision making, critical analysis

#### 19. Judge Evaluator
**folder:** `judge-evaluator/`
- Dedicated evaluation agent scores outputs
- Criteria-based scoring, threshold acceptance
- Best for: quality assurance, validation

#### 20. Hierarchical Team
**folder:** `hierarchical-team/`
- Multi-level organization: executive → manager → lead → worker
- Reporting relationships, clear responsibilities
- Best for: organizational simulation, project management

---

### 4. Workflow Orchestration Patterns (7)

#### 21. Prompt Chaining
**folder:** `prompt-chaining/`
- Sequential LLM calls where output → input of next
- Each step transforms data for next stage
- Best for: multi-step transformations, pipelines

#### 22. Parallelization
**folder:** `parallelization/`
- Multiple independent tasks executed concurrently
- Map phase: distribute, Reduce phase: aggregate
- Best for: batch processing, speed optimization

#### 23. Router Pattern
**folder:** `router-pattern/`
- Classify intent, route to specialized handlers
- Intent classification determines handler
- Best for: versatile handling, load distribution

#### 24. Orchestrator Workers
**folder:** `orchestrator-workers/`
- Dynamic task decomposition and delegation
- Central orchestrator decides what to delegate
- Best for: complex workflows, result aggregation

#### 25. Evaluator Optimizer
**folder:** `evaluator-optimizer/`
- Iterative feedback loop: evaluate → optimize
- Improves output through multiple iterations
- Best for: content refinement, quality improvement

#### 26. Human in the Loop
**folder:** `human-in-the-loop/`
- Humans approve critical outputs before proceeding
- Checkpoint-based pause for human review
- Best for: compliance, content approval workflows

#### 27. Gate Checkpoint
**folder:** `gate-checkpoint/`
- Validation gates control workflow progression
- Pass/fail based on criteria
- Best for: quality control, stage-gated workflows

---

### 5. RAG & Knowledge Patterns (6)

#### 28. Basic RAG
**folder:** `basic-rag/`
- Simple retrieve → generate pipeline
- Vector search + LLM context
- Best for: Q&A, documentation search

#### 29. Advanced RAG
**folder:** `advanced-rag/`
- Query transformation, reranking, hybrid search
- Addresses misaligned queries, poor recall
- Best for: production RAG systems

#### 30. Self RAG
**folder:** `self-rag/`
- Model decides when to retrieve via reflection tokens
- Conditional retrieval reduces unnecessary calls
- Best for: efficiency-focused retrieval

#### 31. Corrective RAG
**folder:** `corrective-rag/`
- Self-evaluation loop verifies retrieval quality
- Corrective actions on failure
- Best for: accuracy-critical applications

#### 32. Graph RAG
**folder:** `graph-rag/`
- Knowledge graph based retrieval
- Entity/relationship traversal
- Best for: multi-hop questions, entity domains

#### 33. Multimodal RAG
**folder:** `multimodal-rag/`
- Text, image, audio retrieval
- Unified multimodal embeddings
- Best for: healthcare, media, multimedia knowledge

---

### 6. Output & Safety Patterns (5)

#### 34. Structured Output
**folder:** `structured-output/`
- Enforce JSON/XML schema in responses
- Tool calling or parser-based
- Best for: data extraction, API integration

#### 35. LLM as Judge
**folder:** `llm-as-judge/`
- Use LLM to evaluate other LLM outputs
- Multi-dimension scoring
- Best for: benchmarking, quality assurance

#### 36. Guardrails Pattern
**folder:** `guardrails-pattern/`
- Input/output validation and filtering
- Content classification, PII protection
- Best for: safety, compliance

#### 37. Output Parsing
**folder:** `output-parsing/`
- Extract structured data from potentially malformed output
- Regex, parser combinators, LLM-assisted
- Best for: production reliability

#### 38. Streaming with Interruptions
**folder:** `streaming-interruptions/`
- Real-time streaming with pause/cancel controls
- Buffer management, state sync
- Best for: interactive applications

---

### 7. Operational & Reliability Patterns (6)

#### 39. Retry Backoff
**folder:** `retry-backoff/`
- Exponential backoff on transient failures
- Jitter to prevent thundering herd
- Best for: API resilience

#### 40. Circuit Breaker
**folder:** `circuit-breaker/`
- Open circuit after threshold failures
- Fail fast, graceful degradation
- Best for: failure isolation

#### 41. Cost Aware Routing
**folder:** `cost-aware-routing/`
- Route to different models by cost/complexity
- Simple tasks → cheap, complex → expensive
- Best for: cost optimization

#### 42. Caching Memoization
**folder:** `caching-memoization/`
- Cache responses for identical queries
- Semantic or exact matching
- Best for: duplicate prevention, latency

#### 43. Observability Tracing
**folder:** `observability-tracing/`
- Built-in logging and tracing
- Span breadcrumbs for debugging
- Best for: production debugging, audits

#### 44. A/B Testing
**folder:** `ab-testing/`
- Experiment with prompt variations
- Statistical significance tracking
- Best for: prompt optimization

---

### 8. Advanced Patterns (6)

#### 45. Meta Prompting
**folder:** `meta-prompting/`
- LLM generates/refines prompts for itself
- Feedback-driven prompt optimization
- Best for: prompt engineering automation

#### 46. Few Shot Learning
**folder:** `few-shot-learning/`
- Dynamic example selection from library
- Semantic retrieval of relevant examples
- Best for: task-specific guidance

#### 47. Active Learning
**folder:** `active-learning/`
- Agent requests clarification when uncertain
- Ambiguity detection, clarification prompts
- Best for: interactive problem solving

#### 48. Simulated Environment
**folder:** `simulated-environment/`
- Run agents in sandbox for testing
- Safe training, RL-style feedback
- Best for: agent training, testing

#### 49. Constitutional AI
**folder:** `constitutional-ai/`
- Self-alignment through principles
- Principle chains, harmlessness checking
- Best for: ethical AI systems

#### 50. Mixture of Agents
**folder:** `mixture-of-agents/`
- Multiple specialized agents collaborate
- Sequential/parallel aggregation
- Best for: ensemble intelligence

---

## 💻 How to Use This Library

### Option 1: Browse Patterns Online

Each pattern has a **README.md** with:
- ✅ Detailed explanation of what it does
- ✅ ASCII diagrams showing the architecture
- ✅ Real-world examples
- ✅ When to use (and when NOT to use)
- ✅ Academic references (5-10 papers)

**Example**: To understand Chain-of-Thought:
```
./patterns/chain-of-thought/
├── README.md          ← Start here for explanation
├── code.py            ← Python implementation
└── example.js         ← JavaScript usage
```

### Option 2: Review Pattern Groups & Comparisons

For patterns that are similar:
```bash
# Navigate to pattern groups
./pattern-groups/
├── evaluation-loop/           # Judge vs Evaluator-Optimizer
├── task-delegation/           # Orchestrator vs Supervisor vs Hierarchical
├── sequential-processing/     # Chaining vs Round-Robin
├── request-distribution/      # Router vs Orchestrator
├── debate-consensus/          # Debate vs Swarm
├── workflow-gates/            # Gate vs Human-in-Loop
└── INDEX.md                   # Start here for decision guide
```

Each group has:
- **Side-by-side comparison tables**
- **Decision trees** ("should I use A or B?")
- **Tradeoff analysis**
- **Code examples**
- **Anti-patterns** (when NOT to use)

### Option 3: Find by Use Case

What do you want to build?

| Goal | Patterns | Start Here |
|------|----------|-----------|
| Answer questions from documents | RAG | [Basic RAG](./patterns/basic-rag/README.md) → [Advanced RAG](./patterns/advanced-rag/README.md) |
| Multi-agent team | Collaboration | [Supervisor](./patterns/supervisor-pattern/README.md) or [Hierarchical Team](./patterns/hierarchical-team/README.md) |
| Complex workflows | Orchestration | [Prompt Chaining](./patterns/prompt-chaining/README.md) → [Orchestrator](./patterns/orchestrator-workers/README.md) |
| Multi-step reasoning | Reasoning | [Chain-of-Thought](./patterns/chain-of-thought/README.md) → [ReAct](./patterns/react/README.md) |
| Reliable production | Operational | [Retry Backoff](./patterns/retry-backoff/README.md) + [Circuit Breaker](./patterns/circuit-breaker/README.md) + [Observability](./patterns/observability-tracing/README.md) |
| Safe AI systems | Safety | [Guardrails](./patterns/guardrails-pattern/README.md) + [Gate Checkpoint](./patterns/gate-checkpoint/README.md) + [Human-in-Loop](./patterns/human-in-the-loop/README.md) |

### Option 4: Import Code Examples

Each pattern includes Python and JavaScript implementations:

```python
# Python
from patterns.chain_of_thought import ChainOfThought
cot = ChainOfThought()
result = cot.execute("What is 23 * 47?")
```

```javascript
// JavaScript/TypeScript
import { ChainOfThought } from './patterns/chain-of-thought/example.js';
const cot = new ChainOfThought();
const result = await cot.execute("What is 23 * 47?");
```

---

## 📊 Library Statistics

```
Total Patterns: 50+
Categories: 8
Academic References: 500+

Pattern Types:
├── Foundational (mature, well-tested): 20 patterns
├── Intermediate (proven in production): 22 patterns
├── Emerging (newer, experimental): 6 patterns
└── Advanced (specialized, complex): 4+ patterns

Usage Distribution:
├── Core reasoning: 7 patterns
├── Multi-agent: 7 patterns
├── Workflows: 7 patterns
├── RAG/Knowledge: 6 patterns
├── Agent architecture: 6 patterns
├── Operational: 6 patterns
├── Safety/Output: 5 patterns
└── Advanced: 6 patterns
```

---

## 🔍 What You'll Find in Each Pattern

Every pattern folder contains:

```
pattern-name/
├── README.md                          # Complete explanation
│   ├── What it does
│   ├── When to use (and when NOT to)
│   ├── ASCII diagrams
│   ├── Real-world examples
│   ├── 5-10 academic references
│   └── Related links
│
├── code.py                            # Python implementation
│
└── example.js                         # JavaScript/TypeScript example
```

---

## 📚 Academic Foundation

This library is grounded in peer-reviewed research:

**Key Foundational Papers**:
- Irving et al. (2018) - AI Safety via Debate
- Wei et al. (2022) - Chain-of-Thought Prompting
- Yao et al. (2023) - ReAct: Reasoning + Acting
- Park et al. (2023) - Generative Agents
- Wang et al. (2024) - Survey on LLM-based Autonomous Agents

**Academic Coverage**:
- Multi-agent systems (agent coordination, emergent behavior)
- AI safety (alignment, verification, guardrails)
- Retrieval systems (RAG, knowledge graphs)
- Workflow orchestration (task decomposition, scheduling)
- Operational reliability (failure handling, monitoring)

Open any pattern README to find complete academic references.

---


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
