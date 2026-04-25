---


# Hierarchical Agent
title: "Hierarchical Agent"
description: "A pattern with a top-level agent that delegates sub-tasks to subordinate agents."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Complex task decomposition", "Large-scale projects", "Multi-domain problems", "Team simulation"]
dependencies: []
category: "architecture"
---

# Hierarchical Agent



# Hierarchical Agent Pattern

The Hierarchical Agent pattern organizes agents into parent-child structures where a supervisor agent delegates tasks to specialized sub-agents. Complex problems are decomposed into smaller subtasks handled by domain-specific child agents, with results aggregated or processed by the parent. This mirrors how human teams work - specialists handle their areas while a manager coordinates overall effort. This pattern scales agentic systems beyond what single agents can handle and enables specialization.

The parent agent analyzes the incoming task, decomposes it into subtasks, assigns each to appropriate child agents, collects results, and synthesizes a final response. Each child agent operates with specialized prompts, tools, and knowledge relevant to its domain. The hierarchy can be multiple levels deep, creating agent "trees" for very complex workflows. This pattern is fundamental to building agentic systems that can handle enterprise-scale tasks.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                Hierarchical Agent Structure                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                         ┌──────────┐                             │
│                         │  Parent  │                             │
│                         │  Agent   │                             │
│                         └────┬─────┘                             │
│                              │                                    │
│         ┌────────────────────┼────────────────────┐              │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│   ┌──────────┐        ┌──────────┐        ┌──────────┐          │
│   │  Child   │        │  Child   │        │  Child   │          │
│   │  Agent   │        │  Agent   │        │  Agent   │          │
│   │  (Code)  │        │  (Data)  │        │  (Web)   │          │
│   └──────────┘        └──────────┘        └──────────┘          │
│         │                    │                    │              │
│         └────────────────────┼────────────────────┘              │
│                              │                                    │
│                              ▼                                    │
│                       ┌──────────┐                                 │
│                       │Aggregated│                                 │
│                       │ Result   │                                 │
│                       └──────────┘                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Multi-Level Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                 Multi-Level Agent Tree                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                       ┌─────────┐                                │
│                       │  Root   │                                │
│                       └────┬────┘                                │
│                            │                                      │
│           ┌────────┬───────┴───────┬────────┐                    │
│           ▼        ▼               ▼        ▼                    │
│     ┌─────────┐┌─────────┐  ┌─────────┐┌─────────┐            │
│     │ Sub-    ││ Sub-    │  │ Sub-    ││ Sub-    │            │
│     │ Agent 1 ││ Agent 2 │  │ Agent 3 ││ Agent 4 │            │
│     └────┬────┘└────┬────┘  └────┬────┘└────┬────┘            │
│          │           │              │           │                  │
│          ▼           ▼              ▼           ▼                  │
│     ┌─────────┐┌─────────┐  ┌─────────┐┌─────────┐            │
│     │Worker A ││Worker B │  │Worker C ││Worker D │            │
│     │         ││         │  │         ││         │            │
│     └─────────┘└─────────┘  └─────────┘└─────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Code + Documentation

```
Task: "Create a REST API for user management"

Parent decomposes:
  1. "Write Flask REST API with CRUD endpoints" → CODER
  2. "Generate API documentation" → WRITER

Results combined → Complete API with docs
```

### Example 2: Research + Analysis + Report

```
Task: "Analyze AI market competition"

Decomposition:
  1. "Research major players in AI market" → RESEARCHER
  2. "Analyze competitive positioning data" → ANALYST
  3. "Write competitive analysis report" → WRITER

Final: Comprehensive market report with data
```

### Example 3: Multi-Level Team Simulation

```
Root Level 0: "Build a web app"
    │
    ├── Level 1: Frontend Agent
    │       └── Worker: React Component Writer
    │
    ├── Level 1: Backend Agent
    │       └── Worker: API Developer
    │       └─�� Worker: Database Designer
    │
    └── Level 1: DevOps Agent
            └── Worker: Deployment Script Writer
```

## Best Practices

1. **Clear Role Definitions**: Each sub-agent needs specialized, focused system prompts
2. **Error Handling**: Handle sub-agent failures gracefully
3. **Parallel Execution**: Run independent tasks in parallel
4. **Timeout Management**: Set timeouts for sub-agent execution

## Related Patterns

- [Orchestrator-Workers](orchestrator-workers.md) - Similar but more explicit coordination
- [Supervisor Pattern](supervisor-pattern.md) - Single-level hierarchy
- [Agent Swarm](agent-swarm.md) - Flat agent teams

## References

- [AutoGen](https://microsoft.github.io/autogen/) - Multi-agent framework
- [LangChain Agents](https://python.langchain.com/docs/modules/agents)
- [CrewAI](https://www.crewai.com/) - Agent team orchestration


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
