---
title: Streaming with Interruptions
description: Handling real-time streaming output that can be interrupted by user input
complexity: medium
model_maturity: emerging
typical_use_cases: ["Interactive chat", "Real-time updates", "User control"]
dependencies: []
category: interaction
---

The Streaming with Interruptions pattern enables real-time response streaming from LLMs while supporting user interaction to pause, cancel, or modify the generation mid-stream. This pattern is crucial for building responsive AI applications where users expect immediate feedback and control over the generation process. In traditional non-streaming implementations, users must wait for complete response generation before any interaction. The streaming interruption pattern allows for a more conversational experience where users can interrupt to ask clarifications, request changes, or stop irrelevant generations. The pattern requires careful handling of buffer states, message synchronization, and state management to ensure consistency between what has been streamed and what the model believes it has generated.

The implementation architecture manages three concurrent streams: the token stream from the LLM, the display stream to the user interface, and the control stream for user interruptions. When a user interrupts, the system must capture the current state, decide how to handle partial output (discard, finalize as incomplete, or regenerate), and properly reset the LLM context if needed. The pattern also handles the tricky synchronization between the streaming tokens and the conversation history—if part of the response is already committed to the conversation, partial regeneration must carefully manage this state. Key considerations include handling "busy" states where the model is mid-generation but receiving new input, managing the message buffer size, and ensuring atomic operations when committing streamed content.

```
┌─────────────────────────────────────────────────────────────┐
│           STREAMING WITH INTERRUPTIONS ARCHITECTURE          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    LLM RESPONSE STREAM                      │
│                                                             │
│  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐    │
│  │token│──▶│token│──▶│token│──▶│token│──▶│token│──▶│      │
│  │  1  │   │  2  │   │  3  │   │  4  │   │  5  │   │ ...  │
│  └──────┘   └──────┘   └──────┘   └──────┘   └──────┘    │
│       │          │              │                 │         │
│       ▼          ▼              ▼                 ▼         │
│  ┌─────────┐ ┌─────────┐  ┌─────────┐      ┌─────────┐     │
│  │ BUFFER  │ │ BUFFER  │  │ BUFFER  │      │ BUFFER  │     │
│  │  UPDATE │ │ UPDATE  │  │ UPDATE  │      │ UPDATE  │     │
│  └─────────┘ └─────────┘  └─────────┘      └─────────┘     │
│                          │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │   USER INTERRUPTION    │                      │
│              │      DETECTION        │                      │
│              └───────────────────────┘                      │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              INTERRUPTION HANDLING                  │   │
│  │                                                     │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    │   │
│  │  │  ABORT    │    │ COMPLETE  │    │REGENERATE │    │   │
│  │  │ current  │    │ as partial│    │ from     │    │   │
│  │  │ generation│   │ output   │    │ context  │    │   │
│  │  └──────────┘    └──────────┘    └──────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Terminal Chat Interface

```python
import sys
import asyncio

async def terminal_chat():
    """Interactive terminal chat with interruption."""
    
    client = OpenAI()
    chatbot = InterruptibleChatbot(client)
    
    print("Chat started. Type 'quit' to exit, 'interrupt' to stop generation.")
    print("Type 'retry' to regenerate from last checkpoint.\n")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == "quit":
            break
        
        if user_input.lower() == "interrupt":
            chatbot.interrupt(InterruptAction.COMPLETE)
            print(" [Interrupted and completed as partial]")
            continue
        
        if user_input.lower() == "retry":
            chatbot.regenerate()
            print(" [Regenerating...]")
            continue
        
        try:
            await chatbot.chat(user_input)
        except Exception as e:
            print(f"Error: {e}")

# Example interaction:
# You: Tell me a long story about a dragon
# [streaming output begins...]
# You: interrupt
# [Dragon was a mighty creature who...] [Interrupted and completed as partial]
# You: retry
# [Regenerating...]
```

### Example 2: Web Interface with Real-time Updates

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

class WebSocketChatManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str, exclude: WebSocket = None):
        for connection in self.active_connections:
            if connection != exclude:
                await connection.send_text(message)

chat_manager = WebSocketChatManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await chat_manager.connect(websocket)
    
    chatbot = InterruptibleChatbot(client)
    conversation = []
    
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            
            if data_json.get("type") == "interrupt":
                chatbot.interrupt(InterruptAction.COMPLETE)
                await websocket.send_text(json.dumps({
                    "type": "interrupted",
                    "partial": chatbot.generator.get_partial_response()
                }))
                continue
            
            if data_json.get("type") == "regenerate":
                chatbot.regenerate()
                await websocket.send_text(json.dumps({
                    "type": "regenerating"
                }))
                continue
            
            # Normal message
            conversation.append({
                "role": "user",
                "content": data_json.get("message")
            })
            
            # Stream response
            async for chunk in chatbot.stream_generate(conversation):
                await websocket.send_text(json.dumps({
                    "type": "token",
                    "content": chunk.text
                }))
            
            conversation.append({
                "role": "assistant",
                "content": chatbot.generator.get_partial_response()
            })
            
    except WebSocketDisconnect:
        chat_manager.disconnect(websocket)
```

### Example 3: Progress Indicator with Cancel

```python
import cursor

class StreamingProgressUI:
    """UI with progress and cancel button."""
    
    def __init__(self):
        self.token_count = 0
        self.start_time = None
        self.cancelled = False
    
    def start(self):
        """Start progress display."""
        self.start_time = time.time()
        self.token_count = 0
        cursor.hide()
        print("Generating: [..........] ", end="", flush=True)
    
    def update(self, token: str):
        """Update progress."""
        if self.cancelled:
            return False
        
        self.token_count += 1
        
        # Update progress bar every 10 tokens
        if self.token_count % 10 == 0:
            elapsed = time.time() - self.start_time
            rate = self.token_count / elapsed if elapsed > 0 else 0
            
            progress = min(self.token_count // 5, 10)
            bar = "." * progress + " " * (10 - progress)
            
            print(f"\rGenerating: [{bar}] {rate:.1f} tok/s ", end="", flush=True)
        
        return True
    
    def cancel(self):
        """Signal cancel."""
        self.cancelled = True
        cursor.show()
        print(f"\nCancelled after {self.token_count} tokens")
    
    def complete(self):
        """Complete."""
        elapsed = time.time() - self.start_time
        cursor.show()
        print(f"\nDone! {self.token_count} tokens in {elapsed:.1f}s")


async def progress_chat():
    """Chat with progress UI."""
    
    client = OpenAI()
    ui = StreamingProgressUI()
    
    gen = StreamingGenerator(
        client=client,
        on_token=ui.update,
        on_complete=ui.complete,
        on_error=lambda e: ui.cancel()
    )
    
    ui.start()
    
    # Example: This would be connected to a cancel button
    # In practice, you'd hook this to a UI cancel button
    # button.on_click = lambda: gen.interrupt(InterruptAction.COMPLETE)
```

## State Diagram

```
┌──────���─���────────────────────────────────────────────────────────┐
│                    STREAM STATE DIAGRAM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                        ┌──────────┐                            │
│                        │   IDLE   │                            │
│                        └────┬─────┘                            │
│                             │ start                           │
│                             ▼                                 │
│                      ┌──────────────┐                          │
│            ┌────────│ GENERATING  │────────┐                    │
│            │        └──────┬───────┘        │                    │
│            │             │                 │                    │
│    interrupt        token           finish_reason                │
│            │             │                 │                    │
│            ▼             ▼                 ▼                   │
│    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│    │INTERRUPTED  │ │   STREAMING   │ │ COMPLETED   │      │
│    └──────────────┘ └──────────────┘ └──────────────┘      │
│            │                                                   │
│            │ regenerate                                        │
│            ▼                                                   │
│      ┌──────────────┐                                        │
│      │  REGENERATE  │────────────────────────────────┐       │
│      └──────────────┘                                │       │
│                                                     │       │
└─────────────────────────────────────────────────────┘       │
```

## Best Practices

1. **Handle abort gracefully** - Clean up resources and state properly
2. **Preserve context** - Keep partial output for potential regeneration
3. **Atomic commits** - Ensure partial output doesn't corrupt conversation state
4. **User feedback** - Always show what's happening during interruption
5. **Buffer wisely** - Don't hold too much in-memory during long generations

## Reference Links

- [OpenAI Streaming](https://platform.openai.com/docs/guides/text-generation)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Async Generators in Python](https://docs.python.org/3/library/asyncio-stream.html)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [AbortController API](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
