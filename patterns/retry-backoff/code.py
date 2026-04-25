import time
import random
import asyncio
from typing import Callable, TypeVar, Optional
from functools import wraps

T = TypeVar('T')

class RetryBackoff:
    """Exponential backoff retry handler for API calls."""
    
    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        max_retries: int = 5,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_on: tuple = (Exception,)
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_on = retry_on
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        if self.jitter:
            delay *= (0.5 + random.random())  # 50-150% of calculated delay
        return delay
    
    def sync_retry(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for synchronous functions."""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except self.retry_on as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        delay = self._calculate_delay(attempt)
                        print(f"Attempt {attempt + 1} failed: {e}. "
                              f"Retrying in {delay:.2f}s...")
                        time.sleep(delay)
            raise last_exception
        return wrapper
    
    async def async_retry(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for async functions."""
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(self.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except self.retry_on as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        delay = self._calculate_delay(attempt)
                        print(f"Attempt {attempt + 1} failed: {e}. "
                              f"Retrying in {delay:.2f}s...")
                        await asyncio.sleep(delay)
            raise last_exception
        return wrapper


# Usage examples
retry_handler = RetryBackoff(
    base_delay=1.0,
    max_delay=30.0,
    max_retries=4,
    jitter=True
)

# Synchronous usage
@retry_handler.sync_retry
def call_llm_api(prompt: str) -> dict:
    import random
    if random.random() < 0.7:  # 70% failure rate for demo
        raise ConnectionError("Temporary network failure")
    return {"response": "Success!", "tokens": 100}

# Async usage
@retry_handler.async_retry
async def call_llm_api_async(prompt: str) -> dict:
    import random
    if random.random() < 0.7:
        raise ConnectionError("Temporary network failure")
    return {"response": "Success!", "tokens": 100}

# Direct function call
def call_with_retry(prompt: str) -> dict:
    """Call API with retry logic directly."""
    for attempt in range(6):
        try:
            # Simulated API call
            result = {"answer": "Processed: " + prompt}
            return result
        except Exception as e:
            if attempt < 5:
                wait_time = min(1 * (2 ** attempt), 30)
                print(f"Retry {attempt + 1}, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                raise


# Example 1: Basic Retry for Rate Limited API
import time
import requests

def query_with_retry(prompt: str, max_retries: int = 5) -> dict:
    """Query LLM API with exponential backoff on rate limit."""
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.example.com/v1/completions",
                json={"prompt": prompt, "max_tokens": 500},
                headers={"Authorization": f"Bearer {API_KEY}"}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited - backoff
                retry_after = int(response.headers.get("Retry-After", 1))
                wait_time = retry_after if retry_after > 0 else 2 ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            delay = min(2 ** attempt, 32)
            print(f"Error: {e}. Retrying in {delay}s")
            time.sleep(delay)
    
    raise Exception("Max retries exceeded")


# Example 2: Async Retry with Circuit Breaker Integration
import asyncio
from typing import Optional

class AsyncAPIClient:
    def __init__(self):
        self.failures = 0
        self.circuit_open = False
        self.last_failure_time = 0
    
    async def call_with_backoff(self, prompt: str) -> dict:
        if self.circuit_open:
            if time.time() - self.last_failure_time > 30:
                self.circuit_open = False
                self.failures = 0
            else:
                raise Exception("Circuit breaker open")
        
        for attempt in range(5):
            try:
                result = await self._make_request(prompt)
                self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                
                if self.failures >= 5:
                    self.circuit_open = True
                    raise Exception("Circuit breaker opened")
                
                delay = min(1 * (2 ** attempt), 30)
                await asyncio.sleep(delay)
        
        raise Exception("Max retries exceeded")
    
    async def _make_request(self, prompt: str) -> dict:
        # Simulated request
        await asyncio.sleep(0.1)
        return {"response": "OK"}