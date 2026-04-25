---


# Agent State Machine
title: "Agent State Machine"
description: "A pattern that models agent behavior as a finite state machine with defined states and transitions."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Workflow automation", "Process control", "Task lifecycle management", "Sequential operations"]
dependencies: []
category: "architecture"
---

# Agent State Machine



# Agent State Machine Pattern

The Agent State Machine pattern models agent conversations and workflows as finite state machines, providing explicit control over conversation flow, task lifecycle, and transition logic. Instead of freeform interaction, the agent operates within defined states (like "greeting", "collecting_info", "processing", "responding", "closing"), with valid transitions between them. This pattern is essential for structured interactions like customer support agents, multi-step data collection, approval workflows, and any process requiring defined stages.

The state machine tracks current state, manages transitions based on user input or internal events, and ensures the agent follows expected flows. Each state has associated behaviors: what to say, what actions to take, and which transitions are valid. This adds predictability and controllability to agent behavior - critical for production systems requiring audit trails, error handling, and process compliance.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 State Machine Diagram                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌──────────┐     user_ready      ┌──────────┐              │
│    │  IDLE    │ ──────────────────▶ │  READY   │              │
│    └──────────┘                    └──────────┘              │
│         △                                │                      │
│         │         reset                 │                      │
│         └───────────────────────────────┘                      │
│                                                           │
│    ┌──────────┐     got_query      ┌──────────┐            │
│    │  READY   │ ──────────────────▶ │PROCESSING│            │
│    └──────────┘                    └──────────┘            │
│         △                                │                      │
│         │         complete/error       │                      │
│         └───────────────────────────────┘                      │
│                                                           │
│    ┌──────────┐     got_result      ┌──────────┐            │
│    │PROCESSING│ ──────────────────▶ │RESPONDING│            │
│    └──────────┘                    └──────────┘            │
│         △                                │                      │
│         │         more_needed/resend  │                      │
│         └───────────────────────────────┘                      │
│                                                           │
└─────────────────────────────────────────────────────────────────┘
```

### State Machine Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    State Definition                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  State: PROCESSING                                              │
│  ├─ Entry: Set processing flag, show spinner                  │
│  ├─ Actions:                                                   │
│  │   ├─ Analyze intent (LLM)                                   │
│  │   ├─ Execute tool calls                                     │
│  │   └─ Format response                                        │
│  ├─ Valid Transitions:                                        │
│  │   ├─ got_result → RESPONDING                                │
│  │   ├─ error → ERROR                                         │
│  │   └─ timeout → TIMEOUT                                     │
│  └─ Exit: Clear processing flag                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Support Ticket Flow

```
┌────────────┐    ticket_received    ┌────────────┐
│    IDLE    │ ──────────────────▶  │COLLECTING  │
└────────────┘                       └────────────┘
                                          │
                         not_complete     │ complete
                                          ▼
                               ┌────────────┐    ┌────────────┐
                               │  DETAILS   │───▶│ PROCESSING │
                               └────────────┘    └────────────┘
                                                          │
                                                          ▼
                                          ┌────────────┐    ┌────────────┐
                                          │  RESPONDING │───▶│   CLOSED   │
                                          └────────────┘    └────────────┘
```

### Example 2: Multi-Step Form

```
State: PERSONAL_INFO → collect name
State: CONTACT_INFO → collect email  
State: PREFERENCES → collect preferences
State: CONFIRM → show summary → submit
```

### Example 3: Approval Workflow

```
State: SUBMITTED → initial submission
State: REVIEW → await review
State: APPROVED or REJECTED → based on decision
State: NOTIFIED → inform user of outcome
```

## Best Practices

1. **Finite States**: Keep state count manageable (5-10 states)
2. **Clear Transitions**: Define explicit conditions for transitions
3. **Error States**: Always include error handling states
4. **Logging**: Log state transitions for debugging

## Related Patterns

- [Tool Use](tool-use.md) - Action execution in states
- [Plan-and-Solve](plan-and-solve.md) - Planning within states
- [Supervisor Pattern](supervisor-pattern.md) - State-based routing

## References

- [LangChain LCEL](https://python.langchain.com/docs/lcel)
- [XState](https://xstate.js.org/) - State machine library
- [AutoGen](https://microsoft.github.io/autogen/)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
