import time
import json
import uuid
import logging
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from typing import Optional, Any, Callable
from functools import wraps
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent")

@dataclass
class Span:
    """Represents a trace span."""
    trace_id: str
    span_id: str
    parent_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    attributes: dict = field(default_factory=dict)
    status: str = "ok"
    
    @property
    def duration_ms(self) -> Optional[float]:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "duration_ms": self.duration_ms
        }

class Tracer:
    """Distributed tracer for agent operations."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.spans: list[Span] = []
    
    @contextmanager
    def span(
        self, 
        name: str, 
        parent_id: Optional[str] = None,
        attributes: Optional[dict] = None
    ):
        span_id = uuid.uuid4().hex[:8]
        trace_id = parent_id or uuid.uuid4().hex[:16]
        
        new_span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            operation_name=name,
            start_time=time.time(),
            attributes=attributes or {}
        )
        
        self.spans.append(new_span)
        
        try:
            yield new_span
        except Exception as e:
            new_span.status = "error"
            new_span.attributes["error"] = str(e)
            raise
        finally:
            new_span.end_time = time.time()
            self._emit_span(new_span)
    
    def _emit_span(self, span: Span):
        """Emit span to logging/tracing backend."""
        logger.info(
            "span completed",
            extra={
                "span": span.to_dict(),
                "service": self.service_name
            }
        )
    
    def clear(self):
        self.spans.clear()

@dataclass
class AgentMetrics:
    """Agent-specific metrics."""
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost: float = 0.0
    latencies: list[float] = field(default_factory=list)
    
    def record_latency(self, latency_ms: float):
        self.latencies.append(latency_ms)
    
    def to_dict(self) -> dict:
        return {
            "request_count": self.request_count,
            "success_rate": self.success_count / max(1, self.request_count),
            "error_rate": self.error_count / max(1, self.request_count),
            "total_tokens": self.total_tokens,
            "avg_tokens_per_request": self.total_tokens / max(1, self.request_count),
            "total_cost": self.total_cost,
            "latency_p50": self._percentile(50),
            "latency_p95": self._percentile(95),
            "latency_p99": self._percentile(99)
        }
    
    def _percentile(self, p: int) -> float:
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        idx = int(len(sorted_latencies) * p / 100)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]


class AgentObserver:
    """Complete observability wrapper for agents."""
    
    def __init__(self, service_name: str):
        self.tracer = Tracer(service_name)
        self.metrics = AgentMetrics()
        self.logger = logging.getLogger(f"agent.{service_name}")
    
    def traced(self, func: Callable) -> Callable:
        """Decorator to add tracing to a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.tracer.span(
                func.__name__,
                attributes={"args": str(args), "kwargs": str(kwargs)}
            ):
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    self.metrics.success_count += 1
                    return result
                except Exception as e:
                    self.metrics.error_count += 1
                    self.logger.error(f"Error in {func.__name__}: {e}")
                    raise
                finally:
                    self.metrics.request_count += 1
                    self.metrics.record_latency((time.time() - start) * 1000)
        return wrapper
    
    def trace_llm_call(
        self,
        model: str,
        prompt: str,
        **kwargs
    ):
        """Trace an LLM API call."""
        with self.tracer.span(
            "llm_call",
            attributes={
                "model": model,
                "prompt_length": len(prompt),
                **kwargs
            }
        ) as span:
            start = time.time()
            response = call_llm_api(prompt, model=model, **kwargs)
            
            # Record metrics
            prompt_tokens = response.get("usage", {}).get("prompt_tokens", 0)
            completion_tokens = response.get("usage", {}).get("completion_tokens", 0)
            
            self.metrics.input_tokens += prompt_tokens
            self.metrics.output_tokens += completion_tokens
            self.metrics.total_tokens += prompt_tokens + completion_tokens
            
            span.attributes.update({
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "finish_reason": response.get("choices", [{}])[0].get("finish_reason")
            })
            
            return response
    
    def log_event(self, event_type: str, **kwargs):
        """Log a structured event."""
        self.logger.info(
            f"agent_event:{event_type}",
            extra={"event": {"type": event_type, **kwargs}}
        )
    
    def get_metrics(self) -> dict:
        return self.metrics.to_dict()


# Usage
observer = AgentObserver("chat-agent")

@observer.traced
def analyze_intent(prompt: str) -> dict:
    """Analyze user intent."""
    with observer.tracer.span("analyze_intent"):
        # Intent analysis logic
        return {"intent": "question", "entities": []}

@observer.traced
def generate_response(context: str, prompt: str) -> str:
    """Generate response."""
    with observer.tracer.span("generate"):
        response = observer.trace_llm_call(
            model="gpt-4",
            prompt=f"Context: {context}\nQuestion: {prompt}"
        )
        return response["choices"][0]["message"]["content"]

def agent_execute(prompt: str) -> dict:
    """Main agent execution with full observability."""
    with observer.tracer.span("agent_execution", attributes={"prompt": prompt}):
        observer.log_event("request_start", prompt=prompt[:100])
        
        # Execute pipeline
        intent = analyze_intent(prompt)
        context = retrieve_context(intent)
        response = generate_response(context, prompt)
        
        observer.log_event("request_complete")
        
        return {"response": response, "metrics": observer.get_metrics()}


# Example 1: LangChain Integration with LangSmith
# Using LangChain's built-in tracing
# from langchain_openai import ChatOpenAI
# from langchain.callbacks.tracing import LangChainTracer
# from langchain.schema import HumanMessage

# Configure LangChain tracing
# tracer = LangChainTracer(
#     project_name="production-agent",
#     endpoint_langchain_api=os.getenv("LANGSMITH_ENDPOINT"),
#     api_key=os.getenv("LANGSMITH_API_KEY")
# )

# llm = ChatOpenAI(
#     model="gpt-4",
#     callbacks=[tracer],
#     tags=["production", "v2"]
# )

# Wrapped execution with automatic tracing
# response = llm.invoke(
#     [HumanMessage(content="Explain quantum computing")],
#     config={"tags": ["important"]}
# )
# Automatically traced in LangSmith


# Example 2: Custom Agent with Full Instrumentation
import asyncio
from typing import Any

class InstrumentedAgent:
    def __init__(self, name: str, tracer: Tracer):
        self.name = name
        self.tracer = tracer
    
    async def execute(self, prompt: str) -> dict:
        """Execute agent with full tracing."""
        with self.tracer.span(f"agent.{self.name}") as span:
            span.attributes["input"] = prompt
            
            # Step 1: Parse intent
            with self.tracer.span("parse_intent"):
                intent = await self._parse_intent(prompt)
                span.attributes["intent"] = str(intent)
            
            # Step 2: Retrieve context
            with self.tracer.span("retrieve_context") as retrieve_span:
                context = await self._retrieve_context(intent)
                retrieve_span.attributes["docs_retrieved"] = len(context)
            
            # Step 3: Generate answer
            with self.tracer.span("generate") as gen_span:
                answer = await self._generate(prompt, context)
                gen_span.attributes["answer_length"] = len(answer)
            
            # Step 4: Validate
            with self.tracer.span("validate"):
                is_valid = await self._validate(answer)
                if not is_valid:
                    raise ValueError("Response validation failed")
            
            return {"answer": answer, "context": context}
    
    async def _parse_intent(self, prompt: str) -> dict:
        await asyncio.sleep(0.01)  # Simulated
        return {"type": "question"}
    
    async def _retrieve_context(self, intent: dict) -> list[str]:
        await asyncio.sleep(0.02)
        return ["context document"]
    
    async def _generate(self, prompt: str, context: list[str]) -> str:
        return "Generated response"
    
    async def _validate(self, answer: str) -> bool:
        return len(answer) > 0


def call_llm_api(prompt: str, model: str = "gpt-4", **kwargs):
    """Make LLM API call"""
    return {"choices": [{"message": {"content": "response"}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 100, "completion_tokens": 50}}

def retrieve_context(intent: dict) -> str:
    """Retrieve context"""
    return "context"