interface Message {
  topic: string;
  payload: any;
  publisher: string;
  timestamp: Date;
}

type MessageHandler = (message: Message) => void | Promise<void>;

class PubSubBroker {
  private subscriptions: Map<string, Map<string, MessageHandler>> = new Map();
  private messageHistory: Message[] = [];

  subscribe(topic: string, agentId: string, handler: MessageHandler): void {
    if (!this.subscriptions.has(topic)) {
      this.subscriptions.set(topic, new Map());
    }
    this.subscriptions.get(topic)!.set(agentId, handler);
  }

  unsubscribe(topic: string, agentId: string): void {
    this.subscriptions.get(topic)?.delete(agentId);
  }

  async publish(topic: string, payload: any, publisher: string): Promise<void> {
    const message: Message = {
      topic,
      payload,
      publisher,
      timestamp: new Date()
    };

    this.messageHistory.push(message);
    if (this.messageHistory.length > 1000) {
      this.messageHistory.shift();
    }

    await this.deliverMessage(message);
  }

  private async deliverMessage(message: Message): Promise<void> {
    const handlers: MessageHandler[] = [];

    const exactHandlers = this.subscriptions.get(message.topic);
    if (exactHandlers) {
      exactHandlers.forEach(h => handlers.push(h));
    }

    this.subscriptions.forEach((subs, pattern) => {
      if (this.matchTopic(message.topic, pattern)) {
        subs.forEach(h => handlers.push(h));
      }
    });

    await Promise.all(handlers.map(h => this.safeHandler(message, h)));
  }

  private matchTopic(topic: string, pattern: string): boolean {
    if (pattern.endsWith("*")) {
      const prefix = pattern.slice(0, -1);
      return topic.startsWith(prefix);
    }
    return topic === pattern;
  }

  private async safeHandler(message: Message, handler: MessageHandler): Promise<void> {
    try {
      await handler(message);
    } catch (error) {
      console.error("Handler error:", error);
    }
  }
}

class PubSubAgent {
  receivedMessages: Message[] = [];

  constructor(
    private agentId: string,
    private broker: PubSubBroker
  ) {}

  subscribe(topic: string, handler?: MessageHandler): void {
    const finalHandler = handler ?? this.defaultHandler.bind(this);
    this.broker.subscribe(topic, this.agentId, finalHandler);
  }

  private async defaultHandler(message: Message): Promise<void> {
    this.receivedMessages.push(message);
    console.log(`[${this.agentId}] Received: ${message.topic}`);
  }

  async publish(topic: string, payload: any): Promise<void> {
    await this.broker.publish(topic, payload, this.agentId);
  }
}