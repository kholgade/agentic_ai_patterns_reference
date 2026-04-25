---


# Tool Use
title: "Tool Use"
description: "A pattern where agents can invoke external tools to gather information or perform actions."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["API integration", "Data retrieval", "Code execution", "External computations"]
dependencies: []
category: "action"
---

# Tool Use



# Tool Use Pattern

The Tool Use pattern enables AI agents to interact with external systems by calling functions or APIs to perform actions beyond text generation. This pattern extends the model's capabilities beyond pure language understanding, allowing it to fetch real-time data, execute code, manipulate files, or trigger external processes. Modern Language Models (LLMs) like GPT-4 and Claude can detect when tool invocation is appropriate based on user queries and return structured tool calls with proper arguments. The model receives tool descriptions in its prompt, understands each tool's purpose and parameters, and decides when to invoke them autonomously or in response to explicit requests.

The pattern works through a function calling interface where developers define available tools with JSON schemas describing parameters and return types. The LLM generates structured outputs conforming to these schemas, which are then executed by the application, and results are fed back into the conversation context. This creates a feedback loop: model requests action → application executes → results returned → model incorporates results → continued interaction. This enables agents to be genuinely useful for tasks requiring external state, computation, or side effects.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Query                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LLM Engine                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Intent Detection → Check if tool needed → Generate call  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Tool Call: {name, args}
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Tool Executor                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   API Call   │  │  File I/O    │  │   Code Execution     │ │
│  └──────────────┘  └─────���────────┘  └──────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Tool Result
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              Update Context → Continue                           │
└─────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Stock Price Retrieval

```
User: "What's the current price of AAPL stock?"

LLM Request → Tool Call: get_stock_price({symbol: "AAPL"})
                                    │
                                    ▼
                              Returns: {price: 178.52, change: +2.3%}
                                    │
                                    ▼
LLM Response: "AAPL is currently trading at $178.52, up 2.3% today."
```

### Example 2: Multi-Tool Query

```
User: "Compare the weather in Paris vs London, then decide where to visit"

→ Tool Call 1: get_weather({location: "Paris"})
→ Tool Call 2: get_weather({location: "London"})
              │
              ▼
    Paris: 72°F, sunny  London: 55°F, rainy
              │
              ▼
LLM Response: "Paris has better weather - 72°F sunny vs London's 55°F rainy."
```

### Example 3: Code Execution with Data Processing

```
User: "Calculate compound interest on $10000 at 5% for 10 years"

→ Tool Call: execute_code({
  code: "principal = 10000; rate = 0.05; years = 10\namount = principal * (1 + rate) ** years\nprint(f'Final amount: ${amount:.2f}')"
})
              │
              ▼
       Final amount: $16,288.95
              │
              ▼
"The compound interest earns $6,288.95 over 10 years."
```

## Best Practices

1. **Schema Design**: Define clear, descriptive tool schemas with proper types and descriptions
2. **Error Handling**: Implement robust error handling for tool failures with graceful fallbacks
3. **Security**: Validate all tool arguments server-side; never trust LLM-generated arguments directly
4. **Idempotency**: Design tools to be idempotent where possible to handle retries safely

## Related Patterns

- [Multi-Tool Orchestration](multi-tool-orchestration.md) - Coordinating multiple tools
- [Plan-and-Solve](plan-and-solve.md) - Tool use as part of planning

## References

- [OpenAI Function Calling Docs](https://platform.openai.com/docs/guides/function-calling)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools)
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
