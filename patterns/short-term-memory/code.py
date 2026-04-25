from openai import OpenAI
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import tiktoken

client = OpenAI(api_key="sk-...")

@dataclass
class Message:
    role: str
    content: str
    tool_calls: Optional[List] = None
    tool_call_id: Optional[str] = None

@dataclass 
class ShortTermMemory:
    max_tokens: int = 128000
    system_prompt: str = ""
    messages: List[Message] = field(default_factory=list)
    _encoding = None
    
    def __post_init__(self):
        try:
            self._encoding = tiktoken.encoding_for_model("gpt-4o")
        except:
            self._encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        return len(self._encoding.encode(text))
    
    def total_tokens(self) -> int:
        total = self.count_tokens(self.system_prompt)
        for msg in self.messages:
            total += self.count_tokens(msg.content) + 4
            total += len(msg.role)
        return total
    
    def add_user_message(self, content: str):
        self.messages.append(Message(role="user", content=content))
    
    def add_assistant_message(self, content: str, tool_calls: Optional[List] = None):
        msg = Message(role="assistant", content=content, tool_calls=tool_calls)
        self.messages.append(msg)
    
    def get_context(self) -> List[Dict]:
        context = []
        if self.system_prompt:
            context.append({"role": "system", "content": self.system_prompt})
        for msg in self.messages:
            d = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                d["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                d["tool_call_id"] = msg.tool_call_id
            context.append(d)
        return context
    
    def prune(self, preserve_recent: int = 5):
        """Keep only last N messages plus summary of earlier ones"""
        if self.total_tokens() <= self.max_tokens:
            return
        
        if len(self.messages) <= preserve_recent:
            return
        
        old_messages = self.messages[:-preserve_recent]
        recent_messages = self.messages[-preserve_recent:]
        
        summary = self._summarize_messages(old_messages)
        
        self.messages = [
            Message(role="system", content=summary)
        ] + recent_messages
    
    def _summarize_messages(self, messages: List[Message]) -> str:
        """Create a summary of messages"""
        summary_parts = []
        for msg in messages:
            if msg.role == "user":
                summary_parts.append(f"User: {msg.content[:100]}...")
            elif msg.role == "assistant" and msg.content:
                summary_parts.append(f"AI: {msg.content[:100]}...")
        
        return "Conversation summary: " + " | ".join(summary_parts[:5])
    
    def slide_window(self, window_size: int = 10):
        """Keep only last N messages"""
        if len(self.messages) > window_size:
            self.messages = self.messages[-window_size:]
    
    def clear(self):
        self.messages = []

class ConversationManager:
    def __init__(self, max_tokens: int = 128000):
        self.memory = ShortTermMemory(max_tokens=max_tokens)
    
    def chat(self, user_input: str) -> str:
        self.memory.add_user_message(user_input)
        
        if self.memory.total_tokens() > self.memory.max_tokens * 0.9:
            self.memory.prune()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=self.memory.get_context()
        )
        
        assistant_message = response.choices[0].message.content
        self.memory.add_assistant_message(assistant_message)
        
        return assistant_message

# Usage
manager = ConversationManager(max_tokens=128000)
print(manager.chat("My name is Yashodhan."))
print(manager.chat("What's my name?"))  # Remembered from context
print(manager.chat("What's my name backwards?"))  # Still remembered