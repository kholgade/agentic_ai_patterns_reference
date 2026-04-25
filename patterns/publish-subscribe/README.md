---


# Publish Subscribe
title: "Publish Subscribe"
description: "A pattern where agents publish messages to topics and other agents subscribe to receive relevant updates."
complexity: "medium"
model_maturity: "intermediate"
typical_use_cases: ["Event-driven systems", "Decoupled communication", "Real-time updates", "Notification systems"]
dependencies: []
category: "collaboration"
---

# Publish Subscribe



## Detailed Explanation

The Publish-Subscribe (Pub/Sub) pattern enables event-driven communication between agents through a message broker, creating a decoupled architecture where publishers and subscribers need not know about each other. This asynchronous communication model allows agents to emit events without waiting for responses, and interested parties automatically receive relevant updates through topic subscriptions. The pattern promotes loose coupling, scalability, and flexibility in multi-agent systems.

In agentic systems, pub/sub serves as the backbone for reactive workflows where multiple agents need to respond to events without tight coordination. A research agent might publish "new data available" events that trigger analysis by one agent, visualization by another, and notification to users by a third. The broker maintains subscriptions and delivers messages to all interested parties, handling the complexity of routing and delivery. This enables complex event-driven behaviors without explicit wiring between components.

Key considerations include designing a clear topic hierarchy, handling message delivery guarantees, managing subscription lifecycles, and dealing with message ordering in high-throughput scenarios. Topics should be named semantically to reflect the nature of events (e.g., "data.processed", "user.action", "system.alert"). The pattern excels in scenarios requiring real-time notifications, event sourcing, or any many-to-many communication patterns within an agent ecosystem.

## ASCII Diagram

```
┌────────────────────────────────────��────────────────────────────┐
│                    PUBLISH-SUBSCRIBE SYSTEM                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐      ┌──────────────────┐      ┌──────────┐     │
│   │PUBLISHER │      │                  │      │PUBLISHER │     │
│   │ AGENT A  │─────▶│                  │◀─────│ AGENT C  │     │
│   └──────────┘      │                  │      └──────────┘     │
│                     │                  │                        │
│   ┌──────────┐      │    MESSAGE       │      ┌──────────┐     │
│   │PUBLISHER │─────▶│     BROKER       │◀─────│ AGENT D  │     │
│   │ AGENT B  │      │                  │      └──────────┘     │
│   └──────────┘      │  ┌────────────┐  │                        │
│                     │  │ Topic Map  │  │                        │
│                     │  │            │  │                        │
│                     │  │ data.*     │──┼──▶ Subscribers: 1,3   │
│                     │  │ user.*     │──┼──▶ Subscribers: 2,4   │
│                     │  │ system.*   │──┼──▶ Subscribers: 5     │
│                     │  └────────────┘  │                        │
│                     │                  │                        │
│                     └────────┬─────────┘                        │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│   │  SUBSCRIBER  │    │  SUBSCRIBER  │    │  SUBSCRIBER  │      │
│   │    AGENT 1   │    │    AGENT 2   │    │    AGENT 3   │      │
│   │              │    │              │    │              │      │
│   │ Topics:      │    │ Topics:      │    │ Topics:      │      │
│   │ data.process │    │ user.action  │    │ data.*       │      │
│   │ system.alert │    │ system.*     │    │ system.alert │      │
│   └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
│   Message Flow:                                                 │
│   ───────────────────────────────────────────────────────────   │
│                                                                 │
│   Agent B ──publish──▶ "user.login" ──▶ Agent 2 receives        │
│                     ──▶ Agent 3 receives (wildcard)             │
│                                                                 │
│   Agent A ──publish──▶ "data.processed" ──▶ Agent 1 receives    │
│                     ──▶ Agent 3 receives (wildcard)             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Data Pipeline Events

Processing pipeline with event-driven stages.

```
Events flow:
1. "Ingest complete" → Triggers validation agent
2. "Validation passed" → Triggers transformation agent
3. "Transformation complete" → Triggers analysis + notification agents
4. "Analysis done" → Triggers dashboard update

Each stage publishes, interested parties subscribe
```

### Example 2: User Activity Notifications

Broadcasting user actions to multiple interested services.

```
User clicks "Purchase" button:
- Publish: "user.purchase" {user_id, item, amount}

Subscribers:
- Analytics: records purchase event
- Inventory: decrements stock
- Email: sends confirmation
- Fraud detection: validates transaction
- Recommendations: updates user preferences
```

### Example 3: System Monitoring

Alerting system with multiple notification channels.

```
System event: "cpu_high"
- Publish: "system.metrics" {cpu: 95, memory: 80}

Subscribers:
- AlertAgent: Creates alert ticket
- LogAgent: Records to monitoring system
- AutoScaleAgent: Triggers scaling if needed
- DashboardAgent: Updates status display
```

## Reference Links

- [Publish-Subscribe Pattern](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
- [Redis Pub/Sub](https://redis.io/docs/interact/pubsub/)
- [Event-Driven Architecture](https://aws.amazon.com/event-driven-architecture/)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
