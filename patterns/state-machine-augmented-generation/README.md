---
title: "State-Machine Augmented Generation"
description: "A pattern that formalizes LLM generation as explicit state machine transitions, enabling predictable, controllable generation behavior by representing business logic and generation phases as formal states."
complexity: "medium"
model_maturity: "emerging"
typical_use_cases: ["Long-horizon customer service", "Complex business logic", "Regulated generation tasks", "Multi-step workflows"]
dependencies: ["Agent State Machine", "Tool Use"]
category: "control"
---

# State-Machine Augmented Generation (SMAG)

## Overview

LLM generation is often unpredictable—solutions may diverge, skip steps, or violate implicit constraints. **State-Machine Augmented Generation (SMAG)** brings formal control to generation by representing business logic and generation phases as explicit **state machines** that the LLM uses as tools during reasoning.

SMAG transforms generation from an open-ended process into a **state-guided traversal**:

1. **Business Logic as State Machine** - Formalize domain rules as state transitions
2. **LLM as State Navigator** - Model uses state machine as tool, not just prompt
3. **Adaptive Context Management** - Context scoped to current state
4. **Delegation to Tools** - Tasks dispatched from main reasoning loop to specialized tools

## Key Innovation

Traditional approaches embed state management in prompts ("First do X, then Y"). SMAG makes state **explicit and executable**:
- States are addressable entities
- Transitions are validated
- Context is scoped per-state
- Execution is observable and debuggable

## When to Use

Use SMAG when:
- Tasks involve complex business logic with many conditions
- Generation must follow specific regulatory or procedural requirements
- Long-horizon tasks (multiple steps, long context)
- Need for observability and auditability in generation
- Human-in-the-loop checkpoints at specific phases
- Reusability across similar tasks with different content

## ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  Traditional Generation                          │
└─────────────────────────────────────────────────────────────────┘

  Prompt: "Handle customer service request..."
                │
                ▼
  ┌─────────────────────────────────────────────────┐
  │               LLM Generates                      │
  │  (Unpredictable: may skip steps, diverge, etc.) │
  └─────────────────────────────────────────────────┘
                │
                ▼
           Output (Variable Quality)


┌─────────────────────────────────────────────────────────────────┐
│              State-Machine Augmented Generation                  │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │              State Machine Definition                      │
  │                                                             │
  │   ┌──────────┐     ┌──────────┐     ┌──────────┐        │
  │   │  STATE   │────▶│  STATE   │────▶│  STATE   │        │
  │   │   A      │     │   B      │     │   C      │        │
  │   │(validate)│     │(process) │     │(respond) │        │
  │   └──────────┘     └──────────┘     └──────────┘        │
  │        │                 │                 │              │
  │        │                 │                 │              │
  │        ▼                 ▼                 ▼              │
  │   ┌────────────────────────────────────────────────────┐  │
  │   │  Valid Transitions:                                 │  │
  │   │  A → B (if valid)                                  │  │
  │   │  A → ERROR (if invalid)                            │  │
  │   │  B → C (if processed)                              │  │
  │   │  B → HUMAN (if escalated)                          │  │
  │   └────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              ReAct-Style Reasoning Loop                       │
│                                                               │
│   Observation ──> Thought ──> Action (Use State Machine)    │
│        ▲                                        │            │
│        └────────────────────────────────────────┘            │
│                                                               │
│   Current State: STATE_B                                      │
│   Available Actions: [process, escalate, check_status]      │
│   Context: Scoped to STATE_B requirements                   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Delegated Tools                              │
│                                                               │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│   │ State-Based  │  │ Validation   │  │ Context      │     │
│   │ Action Tool  │  │ Tool         │  │ Manager      │     │
│   └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## The SMAG Architecture

### 1. State Machine as Tool
```json
{
  "states": {
    "INTAKE": {
      "transitions": ["VALIDATE", "ESCALATE"],
      "context": ["customer_info", "request_type"],
      "actions": ["classify", "validate_format"]
    },
    "VALIDATE": {
      "transitions": ["PROCESS", "REJECT"],
      "context": ["validation_rules", "constraints"],
      "actions": ["check_constraints", "verify_eligibility"]
    },
    "PROCESS": {
      "transitions": ["COMPLETE", "ESCALATE"],
      "context": ["business_logic", "available_actions"],
      "actions": ["execute", "delegate"]
    }
  },
  "transitions": {
    "INTAKE→VALIDATE": "request_is_valid",
    "VALIDATE→PROCESS": "meets_constraints",
    "PROCESS→COMPLETE": "successfully_executed"
  }
}
```

### 2. Adaptive Context Management
Context is scoped to the current state:
```python
# In STATE_INTAKE
context = {
    "system": "You are handling customer intake...",
    "tools": ["classify_request", "validate_format"],
    "history": get_state_specific_history("INTAKE"),
    "constraints": get_state_constraints("INTAKE")
}

# In STATE_PROCESS
context = {
    "system": "You are processing a validated request...",
    "tools": ["execute_action", "check_compliance"],
    "history": get_state_specific_history("PROCESS"),
    "business_rules": get_applicable_rules()
}
```

### 3. Delegation Pattern
Tasks are delegated to LLM-powered tools:
```
Main Loop (ReAct style)
    │
    ├──► State Machine Tool
    │     (Determine next state/action)
    │
    ├──► Validation Tool
    │     (LLM-powered constraint checking)
    │
    ├──► Context Management Tool
    │     (Load state-appropriate context)
    │
    └──► Business Logic Tool
          (Execute domain-specific actions)
```

## Minimal Code (Pseudo)

```python
from enum import Enum, auto
from typing import Dict, List, Optional
from dataclasses import dataclass

class State(Enum):
    INTAKE = auto()
    VALIDATE = auto()
    PROCESS = auto()
    COMPLETE = auto()
    ESCALATE = auto()
    ERROR = auto()

@dataclass
class Transition:
    from_state: State
    to_state: State
    condition: str
    action: str

class StateMachine:
    """Executable state machine for generation control"""
    
    def __init__(self):
        self.current_state = State.INTAKE
        self.transitions = self._define_transitions()
        self.state_context = {}
    
    def _define_transitions(self) -> Dict[tuple, Transition]:
        return {
            (State.INTAKE, State.VALIDATE): Transition(
                State.INTAKE, State.VALIDATE,
                "request_is_valid", "prepare_validation"
            ),
            (State.VALIDATE, State.PROCESS): Transition(
                State.VALIDATE, State.PROCESS,
                "meets_all_constraints", "initialize_processing"
            ),
            (State.PROCESS, State.COMPLETE): Transition(
                State.PROCESS, State.COMPLETE,
                "execution_successful", "finalize"
            ),
            (State.INTAKE, State.ESCALATE): Transition(
                State.INTAKE, State.ESCALATE,
                "requires_human", "handoff_to_human"
            ),
        }
    
    def get_valid_transitions(self) -> List[State]:
        """Get all valid transitions from current state"""
        valid = []
        for (from_state, to_state), transition in self.transitions.items():
            if from_state == self.current_state:
                valid.append(to_state)
        return valid
    
    def transition(self, to_state: State, context: dict) -> bool:
        """Attempt state transition"""
        key = (self.current_state, to_state)
        if key not in self.transitions:
            return False
        
        transition = self.transitions[key]
        
        # Execute transition action
        self._execute_action(transition.action, context)
        
        # Update state
        self.current_state = to_state
        self.state_context[to_state] = context
        
        return True
    
    def _execute_action(self, action: str, context: dict):
        """Execute transition-side effect"""
        actions = {
            "prepare_validation": self._load_validation_context,
            "initialize_processing": self._load_processing_context,
            "finalize": self._generate_output,
            "handoff_to_human": self._create_handoff_package,
        }
        if action in actions:
            actions[action](context)

class SMAGAgent:
    """Agent using State-Machine Augmented Generation"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.state_machine = StateMachine()
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict:
        """Initialize LLM-powered tools"""
        return {
            "state_machine": StateMachineTool(self.state_machine),
            "validate": ValidationTool(self.llm),
            "context_manager": ContextManager(self.llm),
            "execute": ExecutionTool(self.llm),
        }
    
    def generate(self, task: str, max_iterations: int = 20) -> str:
        """Generate output using SMAG"""
        context = {"task": task, "history": []}
        
        for iteration in range(max_iterations):
            # Build state-scoped prompt
            prompt = self._build_prompt(context)
            
            # Get LLM response
            response = self.llm.generate(prompt)
            
            # Parse action
            action = self._parse_action(response)
            
            # Execute action (may use state machine tool)
            if action.tool == "state_machine":
                result = self.tools["state_machine"].execute(action)
                if result.transition_made:
                    context["state"] = result.new_state
            
            elif action.tool == "validate":
                result = self.tools["validate"].execute(action, context)
                if not result.valid:
                    context["errors"] = result.errors
            
            elif action.tool == "execute":
                result = self.tools["execute"].execute(action, context)
                context["output"] = result.output
                
                if self.state_machine.current_state == State.COMPLETE:
                    return result.output
            
            # Update history
            context["history"].append({
                "iteration": iteration,
                "action": action,
                "result": result
            })
        
        # Max iterations reached
        return context.get("output", "Generation incomplete")
    
    def _build_prompt(self, context: dict) -> str:
        """Build state-scoped prompt"""
        current_state = self.state_machine.current_state
        
        prompt_parts = [
            f"Current State: {current_state.name}",
            f"Task: {context['task']}",
            f"Available Transitions: {[s.name for s in self.state_machine.get_valid_transitions()]}",
            f"State Context: {self.state_machine.state_context.get(current_state, {})}",
            "\nChoose your action:",
            "- Use 'state_machine' tool to change state",
            "- Use 'validate' tool to check constraints",
            "- Use 'execute' tool to perform action",
            "\nResponse format: {tool: string, parameters: object}"
        ]
        
        return "\n".join(prompt_parts)

# Example state machine tool
class StateMachineTool:
    def __init__(self, state_machine: StateMachine):
        self.sm = state_machine
    
    def execute(self, action):
        """Execute state machine transition"""
        to_state = State[action.parameters["target_state"]]
        success = self.sm.transition(to_state, action.parameters.get("context", {}))
        
        return {
            "transition_made": success,
            "new_state": self.sm.current_state.name if success else None,
            "valid_transitions": [s.name for s in self.sm.get_valid_transitions()]
        }

# Usage
agent = SMAGAgent(llm_client=openai)
result = agent.generate(
    "Process a customer refund request for order #12345"
)
```

## Comparison with Existing Patterns

| Aspect | SMAG | Agent State Machine | ReAct |
|--------|------|---------------------|-------|
| **State Management** | Formal, tool-based | Implicit in prompt | Action-based |
| **Business Logic** | Explicit state machine | Described in text | Ad-hoc |
| **Context** | State-scoped | Full history | Full history |
| **Observability** | High (state is explicit) | Medium | Low |
| **Best For** | Complex workflows | Agent lifecycle | General reasoning |

## Academic References

1. **Wu, Y., et al.** (2025). "The Art of Tool Interface Design: Thinker Framework" - *arXiv preprint arXiv:2503.21036*
   - Achieves 82.6% success rate on τ-bench retail dataset (vs 68.3% baseline)
   - Key insight: tool interface design matters as much as architecture
   - Demonstrates state machines as tools for generation control

## Related Patterns

- **Agent State Machine**: SMAG extends this by making state machine executable and usable as tool
- **ReAct**: SMAG augments ReAct with formal state management
- **Tool Use**: Heavy use of specialized tools for state operations
- **Prompt Chaining**: SMAG provides formal structure for chains

## When NOT to Use

- **Simple, open-ended generation** where creativity matters more than structure
- **Rapid prototyping** where formal state machine overhead isn't justified
- **Highly variable tasks** where state space would explode
- **Real-time requirements** where state transitions add latency

## Trade-offs

| Benefit | Cost |
|---------|------|
| Predictable generation | Formal modeling overhead |
| Observable execution | Additional tool calls |
| Business logic enforcement | Complex state machine maintenance |
| Reusable across tasks | Upfront design required |
| Audit trail | State explosion risk |


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
