import time
import threading
from enum import Enum
from typing import Callable, TypeVar, Optional, Any
from functools import wraps

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for LLM API resilience."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3,
        excluded_exceptions: tuple = ()
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.excluded_exceptions = excluded_exceptions
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = threading.RLock()
    
    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time >= self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
            return self._state
    
    def _record_success(self):
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1
                if self._half_open_calls >= self.half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0
    
    def _record_failure(self, is_excluded: bool = False):
        if is_excluded:
            return
            
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
            elif (self._state == CircuitState.CLOSED and 
                  self._failure_count >= self.failure_threshold):
                self._state = CircuitState.OPEN
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        state = self.state
        
        if state == CircuitState.OPEN:
            raise CircuitOpenError(
                f"Circuit is OPEN. Service unavailable. "
                f"Will retry after {self.recovery_timeout}s"
            )
        
        if state == CircuitState.HALF_OPEN:
            # Allow through but limit calls
            pass
        
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except self.excluded_exceptions:
            raise
        except Exception as e:
            self._record_failure()
            raise
    
    def decorator(self, func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return self.call(func, *args, **kwargs)
        return wrapper


class CircuitOpenError(Exception):
    """Raised when circuit is open."""
    pass


# Usage
api_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30.0,
    half_open_max_calls=3
)

@api_breaker.decorator
def call_llm(prompt: str) -> dict:
    """Call LLM with circuit breaker protection."""
    import random
    if random.random() < 0.3:
        raise ConnectionError("API temporarily unavailable")
    return {"response": "Success", "model": "gpt-4"}

# Alternative: Context manager usage
def safe_call_llm(prompt: str) -> dict:
    """Call with circuit breaker as wrapper."""
    try:
        return api_breaker.call(
            lambda: call_llm(prompt)  # Pass lambda to avoid immediate call
        )
    except CircuitOpenError as e:
        # Return fallback or cached response
        return {"response": "Service temporarily unavailable", 
                "fallback": True}


# Example 1: Multi-Model Selection with Circuit Breakers
class ModelRouter:
    def __init__(self):
        self.breakers = {
            'gpt-4': CircuitBreaker(failure_threshold=3),
            'gpt-3.5': CircuitBreaker(failure_threshold=5),
            'claude': CircuitBreaker(failure_threshold=3),
        }
        self.fallback_order = ['gpt-4', 'claude', 'gpt-3.5']
    
    def select_model(self, query_complexity: str) -> str:
        """Select best available model based on complexity."""
        if query_complexity == 'high':
            candidates = ['gpt-4', 'claude', 'gpt-3.5']
        else:
            candidates = ['gpt-3.5', 'claude']
        
        for model in candidates:
            if self.breakers[model].state == CircuitState.CLOSED:
                return model
        
        return 'gpt-3.5'  # Ultimate fallback
    
    def call_with_routing(self, prompt: str, complexity: str) -> dict:
        model = self.select_model(complexity)
        try:
            result = self.breakers[model].call(call_llm_api, prompt, model)
            return result
        except CircuitOpenError:
            # Try next available
            for backup in self.fallback_order:
                if (self.breakers[backup].state != CircuitState.OPEN and 
                    backup != model):
                    result = self.breakers[backup].call(call_llm_api, prompt, backup)
                    return result
            raise Exception("All models unavailable")

def call_llm_api(prompt: str, model: str) -> dict:
    """API call"""
    # Implementation
    return {"response": "...", "model": model}


# Example 2: Circuit Breaker with Cache Fallback
class ResilientAPIClient:
    def __init__(self):
        self.circuit = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        self.cache = {}
    
    def call_with_fallback(self, prompt: str) -> str:
        # Check circuit state
        if self.circuit.state == CircuitState.OPEN:
            # Return cached response if available
            if prompt in self.cache:
                return self.cache[prompt]
            return "Service temporarily unavailable. Please try again later."
        
        try:
            # Make API call
            result = self.circuit.call(llm_api_call, prompt)
            self.cache[prompt] = result  # Cache successful response
            return result
        except Exception as e:
            # Return cached or error
            if prompt in self.cache:
                return self.cache[prompt]
            raise

def llm_api_call(prompt: str) -> str:
    """Make LLM API call"""
    # Implementation
    return "response"