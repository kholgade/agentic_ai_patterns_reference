import { ConversationChain } from "langchain/chains";
import { ChatOpenAI } from "langchain/chat_models/openai";

const State = {
  IDLE: "idle",
  GREETING: "greeting", 
  COLLECTING: "collecting",
  PROCESSING: "processing",
  RESPONDING: "responding",
  ERROR: "error"
};

const transitions = {
  [State.IDLE]: { next: State.GREETING, trigger: "user_message" },
  [State.GREETING]: { next: State.COLLECTING, trigger: "user_message" },
  [State.COLLECTING]: { 
    next: State.PROCESSING, 
    trigger: "complete",
    condition: (ctx) => ctx.hasEnoughInfo
  },
  [State.PROCESSING]: { next: State.RESPONDING, trigger: "complete" },
  [State.RESPONDING]: { 
    next: State.IDLE, 
    trigger: "response_complete" 
  }
};

class StateMachineAgent {
  constructor(llm) {
    this.currentState = State.IDLE;
    this.context = {};
    this.llm = llm;
  }

  async process(input) {
    const transition = transitions[this.currentState];
    
    if (transition.condition && !transition.condition(this.context)) {
      // Stay in current state
      return { 
        state: this.currentState, 
        response: "Could you provide more details?",
        continue: true
      };
    }
    
    if (transition.next) {
      this.currentState = transition.next;
    }
    
    return {
      state: this.currentState,
      response: "Processing...",
      continue: this.currentState !== State.RESPONDING
    };
  }

  reset() {
    this.currentState = State.IDLE;
    this.context = {};
  }
}