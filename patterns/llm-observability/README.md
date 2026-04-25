# LLM Observability

## Overview

Integrate LLM observability platforms for span-level tracing of agent workflows, providing visual UI debugging, workflow linking, and aggregate metrics to enable fast navigation of complex multi-step executions. Essential for production agent systems.

## What to Observe

1. **Traces** - Full execution paths through agent workflows
2. **Spans** - Individual LLM calls, tool executions, decisions
3. **Metrics** - Latency, cost, token usage, success rates
4. **Logs** - Prompts, completions, tool inputs/outputs
5. **Evaluations** - Quality scores, user feedback

## Implementation

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

class ObservabilityAgent:
    def __init__(self, tracer_provider: TracerProvider):
        self.tracer = tracer_provider.get_tracer("agent")
    
    def execute(self, task: str):
        with self.tracer.start_as_current_span("agent_execution") as span:
            span.set_attribute("task", task)
            
            # Trace LLM call
            with self.tracer.start_as_current_span("llm_call") as llm_span:
                llm_span.set_attribute("model", "gpt-4")
                response = self.llm.generate(task)
                llm_span.set_attribute("tokens", response.usage.total_tokens)
            
            # Trace tool call
            with self.tracer.start_as_current_span("tool_execution") as tool_span:
                tool_span.set_attribute("tool", "search")
                result = self.tool.execute(response)
                tool_span.set_attribute("success", True)
            
            return result
```

## Key Metrics to Track

- **Cost per request** - Track by model, feature, user
- **Latency breakdown** - LLM time vs tool time vs orchestration
- **Token usage** - Prompt vs completion tokens
- **Success/failure rates** - By task type, model, tool
- **Escalation rates** - How often agents need human help
- **Tool usage patterns** - Which tools are used most

## When to Use

- All production agent systems
- Multi-agent workflows (debugging complexity)
- Cost optimization initiatives
- Performance troubleshooting
- Compliance/audit requirements

## Related Patterns

- [Audit Logging](../audit-logging/) - Security event tracking
- [Observability Tracing](../observability-tracing/) - Existing pattern in repo

## References

- [LLM Observability](https://agentic-patterns.com/patterns/llm-observability)
- [LangSmith Tracing](https://docs.langchain.com/docs/tracing)
- [OpenTelemetry](https://opentelemetry.io/)
- [Datadog APM](https://docs.datadoghq.com/tracing/)
- [Arize Phoenix](https://docs.arize.com/phoenix/)