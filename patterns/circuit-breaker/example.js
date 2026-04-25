enum CircuitState {
  CLOSED = 'closed',
  OPEN = 'open',
  HALF_OPEN = 'half_open'
}

interface CircuitConfig {
  failureThreshold?: number;
  recoveryTimeout?: number;
  halfOpenMaxCalls?: number;
}

class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount: number = 0;
  private lastFailureTime: number = 0;
  private halfOpenCalls: number = 0;
  
  private config = {
    failureThreshold: 5,
    recoveryTimeout: 30000,  // ms
    halfOpenMaxCalls: 3,
    ...{}}
  };

  constructor(config: CircuitConfig = {}) {
    if (config.failureThreshold) this.config.failureThreshold = config.failureThreshold;
    if (config.recoveryTimeout) this.config.recoveryTimeout = config.recoveryTimeout;
    if (config.halfOpenMaxCalls) this.config.halfOpenMaxCalls = config.halfOpenMaxCalls;
  }

  private checkState(): void {
    if (this.state === CircuitState.OPEN) {
      const now = Date.now();
      if (now - this.lastFailureTime >= this.config.recoveryTimeout) {
        this.state = CircuitState.HALF_OPEN;
        this.halfOpenCalls = 0;
      }
    }
  }

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    this.checkState();
    
    if (this.state === CircuitState.OPEN) {
      throw new Error(
        `Circuit is OPEN. Service unavailable. ` +
        `Retry after ${this.config.recoveryTimeout}ms`
      );
    }

    try {
      const result = await fn();
      this.recordSuccess();
      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }

  private recordSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.halfOpenCalls++;
      if (this.halfOpenCalls >= this.config.halfOpenMaxCalls) {
        this.state = CircuitState.CLOSED;
        this.failureCount = 0;
      }
    } else if (this.state === CircuitState.CLOSED) {
      this.failureCount = 0;
    }
  }

  private recordFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.OPEN;
    } else if (this.state === CircuitState.CLOSED &&
              this.failureCount >= this.config.failureThreshold) {
      this.state = CircuitState.OPEN;
    }
  }

  getState(): CircuitState {
    this.checkState();
    return this.state;
  }
}

// Usage
const breaker = new CircuitBreaker({
  failureThreshold: 5,
  recoveryTimeout: 30000,
  halfOpenMaxCalls: 3
});

async function callLLM(prompt: string): Promise<string> {
  return breaker.execute(async () => {
    const response = await fetch('/api/llm', {
      method: 'POST',
      body: JSON.stringify({ prompt })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.text();
  });
}

// Wrapper for multiple models
async function callWithFallback(prompt: string): Promise<string> {
  const primary = new CircuitBreaker({ failureThreshold: 3 });
  const fallback = new CircuitBreaker({ failureThreshold: 5 });
  
  try {
    return await primary.execute(async () => {
      const res = await fetch('/api/primary', {
        method: 'POST',
        body: JSON.stringify({ prompt })
      });
      return res.text();
    });
  } catch {
    // Primary failed, try fallback
    return await fallback.execute(async () => {
      const res = await fetch('/api/fallback', {
        method: 'POST',
        body: JSON.stringify({ prompt })
      });
      return res.text();
    });
  }
}


// Example 3: TypeScript Distributed Circuit Breaker
interface BreakerMetrics {
  failures: number;
  successes: number;
  rejections: number;
  avgLatency: number;
}

class DistributedCircuitBreaker {
  private localBreaker: CircuitBreaker;
  private metrics: BreakerMetrics = { failures: 0, successes: 0, rejections: 0, avgLatency: 0 };
  
  constructor(private serviceName: string) {
    this.localBreaker = new CircuitBreaker({
      failureThreshold: 5,
      recoveryTimeout: 60000
    });
  }

  async call<T>(fn: () => Promise<T>): Promise<T> {
    const start = Date.now();
    
    try {
      const result = await this.localBreaker.execute(fn);
      this.metrics.successes++;
      this.metrics.avgLatency = (this.metrics.avgLatency * (this.metrics.successes - 1) + 
                                  (Date.now() - start)) / this.metrics.successes;
      return result;
    } catch (error) {
      this.metrics.failures++;
      this.publishMetrics();
      throw error;
    }
  }

  private async publishMetrics(): Promise<void> {
    // Publish to monitoring system
    await fetch('/api/metrics', {
      method: 'POST',
      body: JSON.stringify({
        service: this.serviceName,
        ...this.metrics,
        state: this.localBreaker.getState()
      })
    });
  }
}