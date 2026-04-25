# ReAct + Memory Composition

## Idea
Enhance ReAct loop with short-term and long-term memory for context retention.

## Combines
- ReAct → [react](../../patterns/react/README.md)
- Short Term Memory → [short-term-memory](../../patterns/short-term-memory/README.md)
- Long Term Memory → [long-term-memory](../../patterns/long-term-memory/README.md)

## Why
- reduces redundant retrieval
- maintains conversation context
- enables learning from past interactions

## Constraint
- memory management overhead

## Flow
1. Retrieve relevant memories (short and long term)
2. Reason (ReAct) with memory context
3. Execute action
4. Store observation in memory
5. Repeat until goal met