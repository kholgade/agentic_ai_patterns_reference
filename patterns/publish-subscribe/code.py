import asyncio
from typing import Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Message:
    topic: str
    payload: Any
    publisher: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

MessageHandler = Callable[[Message], Any]

class PubSubBroker:
    def __init__(self):
        self.subscriptions: dict[str, list[tuple[str, MessageHandler]]] = {}
        self.message_history: list[Message] = []
        self.max_history = 1000
    
    def subscribe(self, topic: str, agent_id: str, handler: MessageHandler):
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append((agent_id, handler))
    
    def unsubscribe(self, topic: str, agent_id: str):
        if topic in self.subscriptions:
            self.subscriptions[topic] = [
                (aid, h) for aid, h in self.subscriptions[topic]
                if aid != agent_id
            ]
    
    async def publish(self, topic: str, payload: Any, publisher: str):
        message = Message(topic=topic, payload=payload, publisher=publisher)
        
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        await self._deliver_message(message)
    
    async def _deliver_message(self, message: Message):
        handlers = []
        
        if message.topic in self.subscriptions:
            handlers.extend(self.subscriptions[message.topic])
        
        for pattern, subs in self.subscriptions.items():
            if self._match_topic(message.topic, pattern):
                for agent_id, handler in subs:
                    if not any(h[0] == agent_id for h in handlers):
                        handlers.extend(subs)
        
        await asyncio.gather(*[
            self._safe_handler(message, handler)
            for _, handler in handlers
        ])
    
    def _match_topic(self, topic: str, pattern: str) -> bool:
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return topic.startswith(prefix)
        return topic == pattern
    
    async def _safe_handler(self, message: Message, handler: MessageHandler):
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)
        except Exception as e:
            print(f"Handler error: {e}")

class PubSubAgent:
    def __init__(self, agent_id: str, broker: PubSubBroker):
        self.agent_id = agent_id
        self.broker = broker
        self.received_messages: list[Message] = []
    
    def subscribe(self, topic: str, handler: Optional[MessageHandler] = None):
        if handler is None:
            handler = self._default_handler
        self.broker.subscribe(topic, self.agent_id, handler)
    
    async def _default_handler(self, message: Message):
        self.received_messages.append(message)
        print(f"[{self.agent_id}] Received: {message.topic} - {message.payload}")
    
    async def publish(self, topic: str, payload: Any):
        await self.broker.publish(topic, payload, self.agent_id)

broker = PubSubBroker()

agent_data = PubSubAgent("data_processor", broker)
agent_alert = PubSubAgent("alert_system", broker)
agent_notify = PubSubAgent("notifier", broker)

agent_data.subscribe("data.processed")
agent_alert.subscribe("system.alert")
agent_notify.subscribe("data.*")
agent_notify.subscribe("user.*")

await agent_data.publish("data.processed", {"records": 1000})
await agent_alert.publish("system.alert", {"level": "warning"})