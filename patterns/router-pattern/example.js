enum RouteType {
  TECHNICAL = 'technical',
  BILLING = 'billing',
  SALES = 'sales',
  GENERAL = 'general',
  FALLBACK = 'fallback'
}

interface RouteResult {
  route: RouteType;
  confidence: number;
  reasoning: string;
}

interface Handler {
  handle(input: string): Promise<string>;
}

class Router {
  private client: OpenAI;
  private handlers: Map<RouteType, Handler> = new Map();

  constructor(client: OpenAI) {
    this.client = client;
  }

  registerHandler(route: RouteType, handler: Handler): void {
    this.handlers.set(route, handler);
  }

  async classify(input: string): Promise<RouteResult> {
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{
        role: 'user',
        content: `Classify into one of [technical, billing, sales, general]: ${input}`
      }]
    });

    const result = response.choices[0]?.message.content as string;
    const [route, confidence] = result.split('|');

    return {
      route: route.trim() as RouteType,
      confidence: parseFloat(confidence),
      reasoning: ''
    };
  }

  async route(input: string): Promise<string> {
    const classification = await this.classify(input);
    const handler = this.handlers.get(classification.route);

    if (handler) {
      return handler.handle(input);
    }

    return this.handlers.get(RouteType.FALLBACK)?.handle(input) ?? 
      'Unhandled route';
  }
}