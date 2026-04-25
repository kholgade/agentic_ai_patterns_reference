import asyncio
import threading
from typing import Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import time

class StreamState(str, Enum):
    IDLE = "idle"
    GENERATING = "generating"
    PAUSED = "paused"
    INTERRUPTED = "interrupted"
    COMPLETED = "completed"

class InterruptAction(str, Enum):
    ABORT = "abort"
    COMPLETE = "complete"
    REGENERATE = "regenerate"

@dataclass
class StreamChunk:
    text: str
    is_final: bool = False
    token_id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class StreamContext:
    messages: list[dict] = field(default_factory=list)
    partial_response: str = ""
    state: StreamState = StreamState.IDLE
    start_time: Optional[datetime] = None

class StreamingGenerator:
    """Streaming LLM generator with interruption support."""
    
    def __init__(
        self,
        client,
        on_token: Callable[[str], None],
        on_complete: Callable[[str], None],
        on_error: Callable[[Exception], None],
        buffer_size: int = 50
    ):
        self.client = client
        self.on_token = on_token
        self.on_error = on_error
        self.on_complete = on_complete
        self.buffer_size = buffer_size
        
        self._current_context = StreamContext()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._abort_requested = False
    
    async def stream_generate(
        self,
        messages: list[dict],
        model: str = "gpt-4o"
    ) -> AsyncGenerator[StreamChunk, None]:
        """Generate stream with interruption support."""
        
        with self._lock:
            self._current_context = StreamContext(
                messages=messages.copy(),
                state=StreamState.GENERATING,
                start_time=datetime.now()
            )
            self._stop_event.clear()
            self._abort_requested = False
        
        buffer = []
        
        try:
            # Create streaming response
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                max_tokens=2000
            )
            
            for chunk in response:
                # Check for interruption
                if self._stop_event.is_set():
                    yield StreamChunk(
                        text="".join(buffer),
                        is_final=False
                    )
                    return
                
                # Check for abort request
                if self._abort_requested:
                    with self._lock:
                        self._current_context.state = StreamState.INTERRUPTED
                    yield StreamChunk(
                        text="".join(buffer),
                        is_final=False
                    )
                    return
                
                # Extract content delta
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    text = delta.content
                    buffer.append(text)
                    
                    # Update context
                    with self._lock:
                        self._current_context.partial_response += text
                    
                    yield StreamChunk(text=text, is_final=False)
                    
                    # Trigger callback
                    self.on_token(text)
            
            # Completed normally
            final_text = "".join(buffer)
            with self._lock:
                self._current_context.state = StreamState.COMPLETED
                self._current_context.partial_response = final_text
            
            yield StreamChunk(text=final_text, is_final=True)
            self.on_complete(final_text)
            
        except Exception as e:
            self.on_error(e)
            yield StreamChunk(text="", is_final=True)
            raise
    
    def interrupt(self, action: InterruptAction = InterruptAction.ABORT):
        """Handle user interruption."""
        if action == InterruptAction.ABORT:
            self._stop_event.set()
            self._abort_requested = True
            with self._lock:
                self._current_context.state = StreamState.INTERRUPTED
        
        elif action == InterruptAction.COMPLETE:
            self._stop_event.set()
            with self._lock:
                self._current_context.state = StreamState.COMPLETED
        
        elif action == InterruptAction.REGENERATE:
            self._abort_requested = True
            with self._lock:
                self._current_context.state = StreamState.INTERRUPTED
    
    def get_partial_response(self) -> str:
        """Get current partial response."""
        with self._lock:
            return self._current_context.partial_response
    
    def get_conversation_with_partial(self) -> list[dict]:
        """Get conversation including partial response."""
        with self._lock:
            messages = self._current_context.messages.copy()
            if self._current_context.partial_response:
                messages.append({
                    "role": "assistant",
                    "content": self._current_context.partial_response
                })
            return messages

class InterruptibleChatbot:
    """Chatbot with streaming interruption support."""
    
    def __init__(self, client):
        self.client = client
        self.generator: Optional[StreamingGenerator] = None
        self.conversation: list[dict] = []
        self._streaming_task: Optional[asyncio.Task] = None
    
    async def chat(self, user_input: str):
        """Chat with streaming support."""
        
        # Add user message
        self.conversation.append({"role": "user", "content": user_input})
        
        # Create generator
        self.generator = StreamingGenerator(
            client=self.client,
            on_token=self._on_token,
            on_complete=self._on_complete,
            on_error=self._on_error
        )
        
        # Collect output
        output_buffer = []
        
        async for chunk in self.generator.stream_generate(self.conversation):
            output_buffer.append(chunk.text)
            
            # Display streaming token
            print(chunk.text, end="", flush=True)
        
        # Add assistant response to conversation
        full_response = "".join(output_buffer)
        self.conversation.append({
            "role": "assistant",
            "content": full_response
        })
        
        return full_response
    
    def interrupt(self, action: InterruptAction = InterruptAction.ABORT):
        """Interrupt current generation."""
        if self.generator:
            self.generator.interrupt(action)
            
            if action == InterruptAction.COMPLETE:
                # Include partial in conversation
                partial = self.generator.get_partial_response()
                self.conversation.append({
                    "role": "assistant",
                    "content": f"{partial}[interrupted]"
                })
    
    def regenerate(self):
        """Regenerate from context before partial response."""
        if self.generator:
            context = self.generator.get_conversation_with_partial()
            # Remove last assistant message (partial)
            self.conversation = context[:-1] if context else []
    
    def _on_token(self, token: str):
        pass
    
    def _on_complete(self, full_response: str):
        print("\n[Generation complete]")
    
    def _on_error(self, error: Exception):
        print(f"\n[Error: {error}]")