import { trace, Span, SpanStatusCode } from '@opentelemetry/api';

interface AgentSpan extends Span {
  attributes: Record<string, string | number | boolean>;
}

class AgentTracer {
  private tracer = trace.getTracer('agent-service');
  
  async startSpan<T>(
    name: string,
    fn: (span: AgentSpan) => Promise<T>,
    attributes?: Record<string, string | number>
  ): Promise<T> {
    return this.tracer.startActiveSpan(
      name,
      { attributes },
      async (span) => {
        try {
          const result = await fn(span as AgentSpan);
          span.setStatus({ code: SpanStatusCode.OK });
          return result;
        } catch (error) {
          span.setStatus({
            code: SpanStatusCode.ERROR,
            message: error instanceof Error ? error.message : String(error)
          });
          span.recordException(error as Error);
          throw error;
        } finally {
          span.end();
        }
      }
    );
  }
  
  async traceLLMCall(
    model: string,
    prompt: string,
    options: RequestInit
  ): Promise<Response> {
    return this.startSpan(
      'llm.call',
      async (span) => {
        span.setAttribute('llm.model', model);
        span.setAttribute('llm.prompt_length', prompt.length);
        
        const start = Date.now();
        const response = await fetch('/api/llm', {
          ...options,
          body: JSON.stringify({ model, prompt })
        });
        
        const duration = Date.now() - start;
        span.setAttribute('llm.duration_ms', duration);
        
        const data = await response.json();
        span.setAttribute('llm.tokens_used', data.usage?.total_tokens || 0);
        
        return data;
      },
      { 'system.name': 'agent-tracer' }
    );
  }
  
  async traceAgent(
    prompt: string,
    fn: () => Promise<string>
  ): Promise<string> {
    return this.startSpan(
      'agent.execute',
      async (span) => {
        span.setAttribute('prompt', prompt);
        
        const result = await fn();
        
        span.setAttribute('response_length', result.length);
        
        return result;
      },
      { 'system.name': 'agent-tracer' }
    );
  }
}

// Metrics with Prometheus
// import { Counter, Histogram, Registry, collectDefaultMetrics } from 'prom-client';

const registry = {}; // new Registry();
// collectDefaultMetrics({ register: registry });

const requestCounter = {
  inc: (labels: any, value: number = 1) => {
    // implementation
  }
};

const latencyHistogram = {
  startTimer: (labels: any) => () => {
    // implementation
  }
};

const tokenCounter = {
  inc: (labels: any, value: number) => {
    // implementation
  }
};

// Usage
const tracer = new AgentTracer();

async function chat(prompt: string) {
  const end = latencyHistogram.startTimer({ operation: 'full' });
  
  try {
    const response = await tracer.traceAgent(prompt, async () => {
      const result = await tracer.traceLLMCall('gpt-4', prompt, {});
      return result.choices[0].message.content;
    });
    
    const tokens = 100; // Get from response
    tokenCounter.inc({ type: 'output', model: 'gpt-4' }, tokens);
    requestCounter.inc({ status: 'success', model: 'gpt-4' });
    
    return response;
  } catch (error) {
    requestCounter.inc({ status: 'error', model: 'gpt-4' });
    throw error;
  } finally {
    end();
  }
}


// Example 3: Node.js with OpenTelemetry
// import { NodeSDK } from '@opentelemetry/sdk-node';
// import { ConsoleSpanExporter } from '@opentelemetry/exporter-trace-console';
// import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
// import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';

const sdk = {
  start: () => {}
};

// sdk.start();

// import { trace, context } from '@opentelemetry/api';
const tracerAgent = {
  startActiveSpan: async (name: string, options: any, fn: (span: any) => Promise<string>) => {
    return fn({});
  },
  startSpan: (name: string, options: any) => {
    return {
      setAttribute: (key: string, value: any) => {},
      end: () => {}
    };
  }
};

export class AgentWithTracing {
  async execute(prompt: string): Promise<string> {
    return tracerAgent.startActiveSpan(
      'agent.execute',
      {},
      async (span: any) => {
        span.setAttribute('prompt', prompt);
        
        try {
          // Intent analysis
          const intent = await this.analyzeIntent(prompt, span);
          
          // Context retrieval
          const context = await this.retrieveContext(intent, span);
          
          // Generation
          const response = await this.generate(
            prompt, 
            context, 
            span
          );
          
          span.setStatus({ code: 1 }); // SpanStatusCode.OK
          return response;
        } catch (error: any) {
          span.setStatus({
            code: 2, // SpanStatusCode.ERROR
            message: error.message
          });
          throw error;
        } finally {
          span.end();
        }
      }
    );
  }
  
  private async analyzeIntent(prompt: string, parent: any): Promise<object> {
    return tracerAgent.startSpan(
      'analyze_intent',
      { parent },
      async (span: any) => {
        span.end();
        return { intent: 'question' };
      }
    );
  }
  
  private async retrieveContext(intent: object, parent: any): Promise<string[]> {
    return tracerAgent.startSpan(
      'retrieve_context',
      { parent },
      async (span: any) => {
        span.setAttribute('intent', JSON.stringify(intent));
        span.end();
        return ['context'];
      }
    );
  }
  
  private async generate(
    prompt: string, 
    context: string[], 
    parent: any
  ): Promise<string> {
    return tracerAgent.startSpan(
      'generate',
      { parent },
      async (span: any) => {
        const response = await fetch('/api/llm', {
          method: 'POST',
          body: JSON.stringify({ prompt, context })
        });
        
        const data = await response.json();
        span.setAttribute('model', data.model);
        span.setAttribute('tokens', data.usage?.total_tokens);
        
        span.end();
        return data.content;
      }
    );
  }
}