# RAG Agent System

## Overview
Retrieval-augmented agent with tool use and evaluation loop.

## Composition
- Retrieval → [basic-rag](../../patterns/basic-rag/README.md)
- ReAct → [react](../../patterns/react/README.md)  
- Tool use → [tool-use](../../patterns/tool-use/README.md)
- Evaluation → [evaluator-optimizer](../../patterns/evaluator-optimizer/README.md)

## Execution Model
Loop (ReAct)

## Flow
1. Retrieve context
2. Reason (ReAct)
3. Call tools if needed
4. Evaluate response
5. Retry or return

## When to use
- Knowledge-grounded tasks
- External data dependency

## Trade-offs
- Higher latency
- Retrieval quality dependency

## Failure Modes
- bad retrieval → hallucination
- loop inefficiency

## Minimal Code (pseudo)
```python
while not done:
    context = retrieve(query)
    action = agent(context)
    result = execute(action)
    if evaluate(result):
        return result
```