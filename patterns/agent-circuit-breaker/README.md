# Agent Circuit Breaker

## Overview

Prevent agents from wasting tokens and time on repeatedly failing tools by tracking failure rates and temporarily disabling broken tool endpoints. Unlike simple retry logic, circuit breakers prevent cascading failures and give failing services time to recover.

## How It Works

```python
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open" # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # seconds
        self.failures = defaultdict(int)
        self.last_failure = defaultdict(datetime)
        self.state = defaultdict(lambda: CircuitState.CLOSED)
    
    def call(self, tool_name: str, func: callable, *args, **kwargs):
        """Execute tool with circuit breaker protection"""
        
        # Check circuit state
        if self.state[tool_name] == CircuitState.OPEN:
            if self._should_attempt_reset(tool_name):
                self.state[tool_name] = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError(f"Tool {tool_name} is unavailable")
        
        try:
            # Execute tool
            result = func(*args, **kwargs)
            
            # Success - reset failures
            self.failures[tool_name] = 0
            self.state[tool_name] = CircuitState.CLOSED
            
            return result
            
        except Exception as e:
            # Record failure
            self.failures[tool_name] += 1
            self.last_failure[tool_name] = datetime.now()
            
            # Check if threshold exceeded
            if self.failures[tool_name] >= self.failure_threshold:
                self.state[tool_name] = CircuitState.OPEN
            
            raise
    
    def _should_attempt_reset(self, tool_name: str) -> bool:
        """Check if enough time has passed to attempt reset"""
        last_fail = self.last_failure[tool_name]
        return datetime.now() - last_fail > timedelta(seconds=self.recovery_timeout)
```

## Integration with Agent

```python
class AgentWithCircuitBreaker:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=300  # 5 minutes
        )
        self.tools = self._initialize_tools()
    
    def execute_tool(self, tool_name: str, params: dict):
        try:
            return self.circuit_breaker.call(
                tool_name,
                self.tools[tool_name],
                params
            )
        except CircuitOpenError:
            # Fallback strategy
            return self._handle_circuit_open(tool_name, params)
    
    def _handle_circuit_open(self, tool_name: str, params: dict):
        """Handle when tool circuit is open"""
        # Options:
        # 1. Use alternative tool
        # 2. Return cached result
        # 3. Fail gracefully with explanation
        # 4. Escalate to human
        
        return {
            'error': f'Tool {tool_name} is temporarily unavailable',
            'suggestion': 'Try again in a few minutes or use alternative approach'
        }
```

## When to Use

- External API integrations (unreliable by nature)
- Database connections
- Rate-limited services
- Multi-tenant shared resources
- Production systems requiring high availability

## Related Patterns

- [Retry Backoff](../retry-backoff/) - Simpler retry strategy
- [Fallback Cascade](../fallback-cascade/) - Graceful degradation
- [Agent Circuit Breaker](https://agentic-patterns.com/patterns/agent-circuit-breaker) - Enhanced version

## References

- [Agent Circuit Breaker](https://agentic-patterns.com/patterns/agent-circuit-breaker)
- [Circuit Breaker Pattern - Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Resilience patterns: Circuit Breaker](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [Polly .NET Resilience](https://github.com/App-vNext/Polly)
- [Hystrix Circuit Breaker](https://github.com/Netflix/Hystrix)