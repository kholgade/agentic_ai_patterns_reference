from enum import Enum
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

class State(Enum):
    IDLE = "idle"
    GREETING = "greeting"
    COLLECTING = "collecting"
    PROCESSING = "processing"
    RESPONDING = "responding"
    ERROR = "error"
    CLOSED = "closed"

class TransitionType(Enum):
    USER_MESSAGE = "user_message"
    TASK_COMPLETE = "task_complete"
    ERROR = "error"
    TIMEOUT = "timeout"
    RESET = "reset"
    EXPLICIT = "explicit"

@dataclass
class StateTransition:
    from_state: State
    to_state: State
    trigger: TransitionType
    condition: Optional[Callable] = None
    action: Optional[Callable] = None

@dataclass
class StateConfig:
    state: State
    system_prompt: str
    entry_actions: List[Callable] = field(default_factory=list)
    exit_actions: List[Callable] = field(default_factory=list)
    allowed_transitions: List[TransitionType] = field(default_factory=list)

class AgentStateMachine:
    def __init__(self):
        self.current_state = State.IDLE
        self.history: List[Dict] = []
        self.context: Dict[str, Any] = {}
        self.state_configs = self._build_state_configs()
        self.transitions = self._build_transitions()
    
    def _build_state_configs(self) -> Dict[State, StateConfig]:
        return {
            State.IDLE: StateConfig(
                state=State.IDLE,
                system_prompt="Agent is idle, waiting to start",
                allowed_transitions=[TransitionType.USER_MESSAGE]
            ),
            State.GREETING: StateConfig(
                state=State.GREETING,
                system_prompt="Greet the user and offer help",
                allowed_transitions=[TransitionType.USER_MESSAGE]
            ),
            State.COLLECTING: StateConfig(
                state=State.COLLECTING,
                system_prompt="Ask clarifying questions to gather needed information",
                allowed_transitions=[TransitionType.USER_MESSAGE, TransitionType.TASK_COMPLETE]
            ),
            State.PROCESSING: StateConfig(
                state=State.PROCESSING,
                system_prompt="Process the request, may use tools",
                allowed_transitions=[TransitionType.TASK_COMPLETE, TransitionType.ERROR]
            ),
            State.RESPONDING: StateConfig(
                state=State.RESPONDING,
                system_prompt="Provide the final response to user",
                allowed_transitions=[TransitionType.USER_MESSAGE, TransitionType.RESET]
            ),
            State.ERROR: StateConfig(
                state=State.ERROR,
                system_prompt="An error occurred, apologize and offer to help",
                allowed_transitions=[TransitionType.RESET]
            ),
            State.CLOSED: StateConfig(
                state=State.CLOSED,
                system_prompt="Conversation complete",
                allowed_transitions=[TransitionType.RESET]
            )
        }
    
    def _build_transitions(self) -> List[StateTransition]:
        return [
            StateTransition(State.IDLE, State.GREETING, TransitionType.USER_MESSAGE),
            StateTransition(State.GREETING, State.COLLECTING, TransitionType.USER_MESSAGE),
            StateTransition(State.COLLECTING, State.COLLECTING, TransitionType.USER_MESSAGE),
            StateTransition(State.COLLECTING, State.PROCESSING, TransitionType.TASK_COMPLETE),
            StateTransition(State.PROCESSING, State.RESPONDING, TransitionType.TASK_COMPLETE),
            StateTransition(State.PROCESSING, State.ERROR, TransitionType.ERROR),
            StateTransition(State.RESPONDING, State.IDLE, TransitionType.RESET),
            StateTransition(State.ERROR, State.IDLE, TransitionType.RESET),
        ]
    
    def can_transition(self, trigger: TransitionType) -> bool:
        config = self.state_configs.get(self.current_state)
        return trigger in config.allowed_transitions
    
    def find_transition(self, trigger: TransitionType) -> Optional[StateTransition]:
        for t in self.transitions:
            if t.from_state == self.current_state and t.trigger == trigger:
                return t
        return None
    
    def transition(self, trigger: TransitionType) -> bool:
        if not self.can_transition(trigger):
            return False
        
        t = self.find_transition(trigger)
        if not t:
            return False
        
        old_state = self.current_state
        self.current_state = t.to_state
        self.history.append({
            "from": old_state.value,
            "to": self.current_state.value,
            "trigger": trigger.value,
            "timestamp": datetime.now().isoformat()
        })
        
        if t.action:
            t.action(self.context)
        
        return True
    
    def get_system_prompt(self) -> str:
        return self.state_configs[self.current_state].system_prompt
    
    def process_message(self, message: str) -> str:
        self.context["last_message"] = message
        
        # Determine next step based on state
        if self.current_state == State.IDLE:
            self.transition(TransitionType.USER_MESSAGE)
            return self._handle_greeting()
        
        elif self.current_state == State.GREETING:
            self.context["query"] = message
            if self._needs_more_info(message):
                self.transition(TransitionType.USER_MESSAGE)
                return self._ask_question()
            else:
                self.transition(TransitionType.TASK_COMPLETE)
                return self._handle_processing()
        
        elif self.current_state == State.COLLECTING:
            self.context["collected"] = message
            if self.has_enough_info():
                self.transition(TransitionType.TASK_COMPLETE)
                return self._handle_processing()
            else:
                return self._ask_question()
        
        elif self.current_state == State.RESPONDING:
            self.transition(TransitionType.RESET)
            return "How else can I help you?"
        
        return "I'm in " + self.current_state.value + " state."
    
    def _handle_greeting(self) -> str:
        return "Hello! How can I help you today?"
    
    def _ask_question(self) -> str:
        return "Could you provide more details about what you need?"
    
    def _needs_more_info(self, message: str) -> bool:
        return len(message) < 20
    
    def has_enough_info(self) -> bool:
        return "query" in self.context or "collected" in self.context
    
    def _handle_processing(self) -> str:
        return "I'm processing your request..."
    
    def reset(self):
        self.current_state = State.IDLE
        self.context = {}
        self.history.append({
            "action": "reset",
            "timestamp": datetime.now().isoformat()
        })

# Usage
agent = AgentStateMachine()

response = agent.process_message("Hi")  # IDLE → GREETING
print(response)  # "Hello! How can I help you today?"

response = agent.process_message("I need help with Python")  # GREETING → COLLECTING
print(response) 

# State machine is tracking conversation flow
print(f"Current state: {agent.current_state.value}")  # collecting