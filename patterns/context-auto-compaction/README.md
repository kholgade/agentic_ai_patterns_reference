# Context Window Auto-Compaction

## Overview

Automatically summarize and compact context before hitting token limits. Context overflow is a silent killer of agent reliability—when context windows fill up, agents lose track of instructions, prior decisions, and task progress. This pattern proactively manages context by identifying what to keep, what to summarize, and what to discard.

## How It Works

```python
class ContextManager:
    def __init__(self, max_tokens=100000, compaction_threshold=0.8):
        self.max_tokens = max_tokens
        self.threshold = compaction_threshold
        self.context = []
    
    def add_message(self, role: str, content: str):
        self.context.append({'role': role, 'content': content})
        
        # Check if compaction needed
        if self._current_tokens() > self.max_tokens * self.threshold:
            self._compact_context()
    
    def _compact_context(self):
        """
        Strategy:
        1. Keep system instructions (always)
        2. Keep last 5 messages (recent context)
        3. Summarize middle messages
        4. Discard old tool outputs (keep only results)
        """
        system_msg = self.context[0]  # Always keep
        
        recent_msgs = self.context[-5:]  # Keep recent
        
        # Summarize middle
        middle = self.context[1:-5]
        if middle:
            summary = self._summarize_messages(middle)
            middle_msg = {'role': 'system', 'content': f'Summary of prior conversation: {summary}'}
        else:
            middle_msg = None
        
        # Rebuild context
        self.context = [system_msg] + ([middle_msg] if middle_msg else []) + recent_msgs
    
    def _summarize_messages(self, messages: list) -> str:
        """Use LLM to summarize messages"""
        prompt = f"Summarize these messages in 3-5 sentences:\n{messages}"
        return llm.generate(prompt)
```

## Compaction Strategies

1. **Sliding Window** - Keep last N messages only
2. **Importance Scoring** - Score messages by relevance, keep high scores
3. **Topic Clustering** - Group by topic, summarize each cluster
4. **Decision Logging** - Extract and keep only decisions/conclusions
5. **Hybrid Memory** - Move old context to long-term memory, retrieve as needed

## When to Use

- Long-running agent sessions (>50 messages)
- Agents with verbose tool outputs
- Multi-turn conversations with context growth
- When using models with limited context windows

## Related Patterns

- [Episodic Memory Retrieval](../episodic-memory/) - Move to long-term storage
- [Working Memory via TodoWrite](../working-memory-via-todos/) - Track state externally
- [Context Minimization](../context-minimization/) - Reduce context proactively

## References

- [Context Window Auto-Compaction](https://agentic-patterns.com/patterns/context-window-auto-compaction)
- [LangChain Context Management](https://python.langchain.com/docs/modules/memory/)
- [Anthropic Context Window Best Practices](https://docs.anthropic.com/claude/docs/context-window)