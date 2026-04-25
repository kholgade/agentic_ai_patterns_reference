---


# Short Term Memory
title: "Short Term Memory"
description: "A pattern that maintains context within a single conversation session."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["Conversation context", "Session state", "Current task memory", "User preference retention"]
dependencies: []
category: "memory"
---

# Short Term Memory



# Short Term Memory Pattern

The Short Term Memory pattern maintains conversation context within a single session, enabling the agent to remember what was discussed earlier in the current interaction. Modern LLMs have a context window - a maximum number of tokens that can be processed in a single request. This pattern efficiently manages that window by tracking conversation history, extracting key information, and determining what to keep or prune as the conversation grows. Without this pattern, the agent would treat each message as independent, losing all prior context.

The pattern operates through message lists where each turn contains role (system/user/assistant/tool) and content. As the conversation progresses, older messages may be summarized or dropped to stay within token limits. This is critical because context windows have hard limits (e.g., 128K tokens for GPT-4o), and exceeding them causes errors. The memory management strategy determines which messages to preserve, how to compress history, and when to synthesize summaries.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Conversation Flow                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Turn 1    │    │   Turn 2    │    │   Turn 3    │          │
│  │  User: msg  │───▶│  User: msg  │───▶│  User: msg  │          │
│  │ AI: response│    │ AI: response│    │ AI: response│          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Memory Buffer (Context Window)              │    │
│  │  [system] + [conversation history] + [current query]  │    │
│  │  <---------------------------------------------------->   │    │
│  │                    Token Limit: 128K                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Memory Management Strategies

```
Strategy 1: Keep All (when under limit)
┌────────────────────────────────────────────────────────┐
│ Turn 1 │ Turn 2 │ Turn 3 │ Turn 4 │ Turn 5 │ Current  │
├────────┼────────┼────────┼────────┼────────┼──────────┤
│  ✓     │   ✓   │   ✓   │   ✓   │   ✓   │    ✓    │
└────────────────────────────────────────────────────────┘

Strategy 2: Summarize + Keep Recent
┌────────────────────────────────────────────────────────┐
│ Summary: "User discussed X, Y, asked about Z"         │
├────────────────────────────────────────────────────────┤
│ Turn 4          │ Turn 5           │ Current          │
│  ✓ (truncated)  │  ✓ (full)        │    ✓             │
└────────────────────────────────────────────────────────┘

Strategy 3: Sliding Window (last N messages only)
┌────────────────────────────────────────────────────────┐
│ Turn 1 │ Turn 2 │ Turn 3 │ Turn 4 │ Turn 5 │ Current    │
├────────┼────────┼────────┼────────┼────────┼──────────┤
│   ✗    │   ✗   │   ✓   │   ✓   │  ✓    │    ✓      │
└────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Basic Conversation

```
Turn 1:
  User: "I need help with Python programming"
  AI: "I'd be happy to help! What specific aspect..."

Turn 2:
  User: "How do I read files?"
  AI: "You can use the open() function..."

Turn 3:
  User: "Can you show me a complete example?"
  AI: [Shows file reading example]

Context grows - agent maintains full history, responds appropriately
```

### Example 2: Long Conversation Pruning

```
Initial context: ~5K tokens (10 messages)

As conversation grows past 100K tokens:

┌──────────────────────────────────────────┐
│ Pruning triggered...                      │
├──────────────────────────────────────────┤
│ Before: 50 messages = 95K tokens          │
│ After:  Summary + 5 messages = 45K tokens │
└──────────────────────────────────────────┘

User can continue seamlessly - summary 
captures key information from earlier turns
```

### Example 3: Task Memory

```
User: "Let's track my shopping list: apples, bananas"
AI: "Added apples and bananas to your list."

User: "Add oranges"
AI: "Added oranges. List: apples, bananas, oranges"

User: "What do I have?"
AI: "Your list: apples, bananas, oranges"
```

## Best Practices

1. **Token Counting**: Always track token usage to prevent hitting limits
2. **Proactive Pruning**: Prune before hitting limits, not after
3. **Preserve Intent**: Keep messages that establish task intent/goal
4. **System Prompt Stability**: Keep system prompt in context even when pruning

## Related Patterns

- [Long Term Memory](long-term-memory.md) - Persisting across sessions
- [Conversation Context Window](short-term-memory.md) - This pattern
- [Agent State Machine](agent-state-machine.md) - State-based conversation

## References

- [OpenAI Context Windows](https://platform.openai.com/docs/models)
- [LangChain Memory](https://python.langchain.com/docs/modules/memory)
- [ tiktoken Library](https://github.com/openai/tiktoken)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
