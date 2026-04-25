---


# ReAct
title: "ReAct"
description: "A pattern combining reasoning and acting by interleaving thought, action, and observation steps."
complexity: "low"
model_maturity: "foundational"
typical_use_cases: ["Question answering", "Tool use scenarios", "Multi-step reasoning", "Information retrieval"]
dependencies: []
category: "reasoning"
---

# ReAct



## Overview

ReAct (Synergizing Reasoning and Acting) is a prompting pattern that enables language models to handle complex tasks requiring external information retrieval and tool usage. Unlike Chain-of-Thought which keeps reasoning purely internal, ReAct interleaves explicit reasoning steps with actions that interact with external systems—databases, web search APIs, code interpreters, or custom tools. After each action, the model receives an observation (the result of the action) which becomes input for the next reasoning step. This closed loop between thought, action, and observation creates a self-directed agent capable of exploring solution spaces dynamically.

The pattern emerged from recognizing that real-world reasoning often requires gathering information that isn't in the model's training data. A question like "What was Apple's stock price on the day they announced the iPhone 16?" cannot be answered from internal knowledge—the model must search for current information. ReAct provides a structured way to do this: the model decides what information to look up, takes an action (calls a tool), observes the result, reasons about whether it has the answer, and either continues or concludes. This makes the reasoning traceable and correctable at each step.

ReAct is particularly powerful because it combines the best of two worlds: explicit reasoning chains that make thought processes transparent, and tool-augmented capabilities that extend the model's reach beyond static knowledge. The pattern works especially well for multi-hop questions where one piece of information leads to the next, for tasks requiring real-time data, and for complex workflows where the next step depends on the previous result. It's the foundation for most modern AI agent architectures.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ReAct LOOP                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │   START      │
  │   Question   │
  └──────┬───────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  THOUGHT 1                                                                │
  │  Reason about current state and decide next action                        │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  ���  ACTION 1                                                                 │
  │  Execute tool call (search, database query, function invocation)         │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  OBSERVATION 1                                                            │
  │  Receive result from action                                              │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  THOUGHT 2                                                                │
  │  Incorporate observation, reason about next step                          │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ACTION 2                                                                 │
  │  ...                                                                     │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  OBSERVATION 2                                                            │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ... continue until ANSWER is reached                                   │
  └──────┬───────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌──────────────┐
  │   FINAL      │
  │   ANSWER     │
  └──────────────┘ 


  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  EXAMPLE: Multi-hop Question with Web Search                               │
  └──���──────────────────────────────────────────────────────────────────────────┘

  Question: "What company acquired the developer of the game that won
             the 2023 Game of the Year award at The Game Awards?"

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  THOUGHT: I need to first find out which game won Game of the Year in │
  │  2023. Let me search for that information.                               │
  └─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ACTION: Search[query="2023 Game of the Year winner The Game Awards"]     │
  └─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  OBSERVATION: "Baldur's Gate 3" won Game of the Year at The Game Awards   │
  │  2023, developed by Larian Studios.                                     │
  └─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  THOUGHT: Now I need to find what company acquired Larian Studios or     │
  │  their developer. I don't recall this being acquired, so let me search.   │
  └─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ACTION: Search[query="Larian Studios acquisition company"]                │
  └─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  OBSERVATION: Larian Studios has not been acquired and remains           │
  │  independently owned. They received investment fromEmbracer Group but     │
  │  not an acquisition.                                                    │
  └───────────────────��─��───────────────────────────────────────────────────┘
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  FINAL ANSWER: Larian Studios (developer of Baldur's Gate 3) has not     │
  │  been acquired and remains an independent game studio.                   │
  └─────────────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Database Query Task

**Question:** "How many orders were placed by customers in California in Q4 2023?"

```
THOUGHT: I need to query the database to count orders. First, I should check
         the database schema to understand the tables and their structure.
ACTION: query_schema[]
OBSERVATION: Tables: customers(id, name, state, created_at), 
             orders(id, customer_id, amount, order_date, status)

THOUGHT: I now understand the schema. I need to count orders where:
         1. customer's state is 'California'
         2. order_date is in Q4 2023 (Oct 1 - Dec 31, 2023)
ACTION: execute_sql[SELECT COUNT(*) FROM orders o 
         JOIN customers c ON o.customer_id = c.id 
         WHERE c.state = 'California' 
         AND o.order_date BETWEEN '2023-10-01' AND '2023-12-31']
OBSERVATION: Result: 1,847

FINAL ANSWER: 1,847 orders were placed by customers in California in Q4 2023.
```

### Example 2: Multi-Step Research

**Question:** "Who was the CEO of the company that makes the most popular smartphone in 2024, and what college did they attend?"

```
THOUGHT: I need to first find which smartphone was the most popular in 2024.
         Let me search for market share data.
ACTION: search[smartphone market share 2024 most popular]
OBSERVATION: According to multiple sources, Apple iPhone dominated global 
             smartphone sales in 2024 with approximately 20% market share.

THOUGHT: Apple's iPhone was the most popular. Now I need to find who is
         Apple's CEO and their educational background.
ACTION: search[Apple CEO Tim Cook educational background college]
OBSERVATION: Tim Cook is Apple's CEO. He earned his MBA from Duke University's
             Fuqua School of Business and holds a Bachelor of Science degree
             in Industrial Engineering from Auburn University.

FINAL ANSWER: Tim Cook is the CEO of Apple (maker of the most popular 
              smartphone, iPhone). He attended Auburn University (B.S. in 
              Industrial Engineering) and Duke University (MBA).
```

### Example 3: Code Debugging

**Question:** "Why is this Python function returning None instead of the expected sum?"

```python
def add_numbers(a, b):
    result = a + b
    # Missing return statement
```

```
THOUGHT: The user wants to debug a function. Let me first run the code to
         observe the actual behavior, then analyze why it returns None.
ACTION: execute_python[
def add_numbers(a, b):
    result = a + b

output = add_numbers(5, 3)
print(f"Returned: {output}")
print(f"Type: {type(output)}")
]
OBSERVATION: Returned: None
             Type: <class 'NoneType'>

THOUGHT: The observation confirms the issue. The function calculates 
         a + b correctly but doesn't return the result. In Python, functions
         without an explicit return statement return None by default.

FINAL ANSWER: The function is missing a `return result` statement. 
              In Python, when a function doesn't have an explicit return,
              it automatically returns None. To fix this, add:
              
              def add_numbers(a, b):
                  result = a + b
                  return result
              
              Or simply: return a + b
```

## Best Practices

1. **Define tools clearly** with descriptive names and well-documented input/output formats
2. **Include error handling** in tool implementations so observations reveal what went wrong
3. **Set maximum iterations** to prevent infinite loops and control costs
4. **Make the system prompt explicit** about the expected format for Thought/Action/Observation
5. **Provide diverse tool examples** in few-shot prompts showing different tool combinations
6. **Design tools to be idempotent** when possible—repeated calls shouldn't cause side effects
7. **Include context about tool limitations** in the system prompt (rate limits, data freshness, etc.)

## References

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) - Original paper by Yao et al. (2022)
- [React Synergy with Chain-of-Thought](https://arxiv.org/abs/2305.04427) - Combining ReAct with CoT
- [LangChain ReAct Documentation](https://python.langchain.com/docs/modules/agents/how_to/custom_agent) - Implementation patterns


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
