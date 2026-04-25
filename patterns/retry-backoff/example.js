interface RetryConfig {
  baseDelay?: number;
  maxDelay?: number;
  maxRetries?: number;
  exponentialBase?: number;
  jitter?: boolean;
  retryOn?: (error: Error) => boolean;
}

class RetryBackoff {
  private baseDelay: number;
  private maxDelay: number;
  private maxRetries: number;
  private exponentialBase: number;
  private jitter: boolean;
  private retryOn: (error: Error) => boolean;

  constructor(config: RetryConfig = {}) {
    this.baseDelay = config.baseDelay ?? 1000;
    this.maxDelay = config.maxDelay ?? 60000;
    this.maxRetries = config.maxRetries ?? 5;
    this.exponentialBase = config.exponentialBase ?? 2;
    this.jitter = config.jitter ?? true;
    this.retryOn = config.retryOn ?? (() => true);
  }

  private calculateDelay(attempt: number): number {
    let delay = this.baseDelay * Math.pow(this.exponentialBase, attempt);
    delay = Math.min(delay, this.maxDelay);
    if (this.jitter) {
      delay *= (0.5 + Math.random() * 0.5); // 50-150%
    }
    return delay;
  }

  async retry<T>(fn: () => Promise<T>): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        
        if (!this.retryOn(lastError) || attempt === this.maxRetries) {
          throw lastError;
        }

        const delay = this.calculateDelay(attempt);
        console.log(`Attempt ${attempt + 1} failed: ${lastError.message}. ` +
                    `Retrying in ${delay}ms...`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError;
  }
}

// Usage
const retry = new RetryBackoff({
  baseDelay: 1000,
  maxDelay: 30000,
  maxRetries: 4,
  jitter: true
});

async function callLLM(prompt: string): Promise<string> {
  const result = await retry.retry(() => fetch('/api/llm', {
    method: 'POST',
    body: JSON.stringify({ prompt })
  }));
  
  return result.json();
}

// Wrapper function version
async function withRetry<T>(
  fn: () => Promise<T>,
  config?: RetryConfig
): Promise<T> {
  const retry = new RetryBackoff(config);
  return retry.retry(fn);
}


// TypeScript with Multiple Error Handling
enum ApiErrorType {
 _RATE_LIMIT = 'rate_limit',
 _SERVER_ERROR = 'server_error', 
  TIMEOUT = 'timeout',
  NETWORK = 'network',
  AUTH = 'auth'
}

interface ApiError {
  type: ApiErrorType;
  message: string;
}

async function callWithSmartRetry(prompt: string): Promise<string> {
  const config = {
    maxRetries: 5,
    baseDelay: 1000,
    jitter: true,
    retryOn: (error: Error) => {
      const apiError = error as ApiError;
      // Don't retry auth errors
      if (apiError.type === ApiErrorType.AUTH) return false;
      // Retry rate limits with longer delay
      if (apiError.type === ApiErrorType.RATE_LIMIT) return true;
      // Retry server errors and timeouts
      if (apiError.type === ApiErrorType.SERVER_ERROR || 
          apiError.type === ApiErrorType.TIMEOUT) return true;
      // Retry network errors
      return apiError.type === ApiErrorType.NETWORK;
    }
  };
  
  const retry = new RetryBackoff(config);
  
  return retry.retry(async () => {
    // API call logic here
    const response = await fetch('/api/llm', {
      method: 'POST',
      body: JSON.stringify({ prompt })
    });
    
    if (!response.ok) {
      if (response.status === 429) {
        throw { type: ApiErrorType.RATE_LIMIT, message: 'Rate limited' };
      }
      if (response.status === 401) {
        throw { type: ApiErrorType.AUTH, message: 'Unauthorized' };
      }
      throw { type: ApiErrorType.SERVER_ERROR, message: 'Server error' };
    }
    
    return response.text();
  });
}