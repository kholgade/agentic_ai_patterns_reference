---
title: Structured Output
description: Pattern for generating outputs in specific structured formats like JSON or schemas
complexity: low
model_maturity: mature
typical_use_cases: ["API responses", "Data extraction", "Schema validation"]
dependencies: []
category: output-generation
---

The Structured Output pattern enables LLMs to generate responses that conform to predefined schemas, ensuring consistent and parseable outputs. This pattern is essential for building reliable AI applications where downstream systems expect data in a specific format. Modern LLMs support native structured output generation through various mechanisms: JSON mode, tool calling, and constrained decoding. By providing a schema definition or example, developers can dramatically improve the predictability of LLM outputs, making them suitable for integration into production systems that require typed data structures. The key challenge lies in balancing schema flexibility with the model's ability to accurately generate compliant output.

The implementation architecture typically involves three components: schema definition, output generation, and validation. Schema definition can be provided through JSON Schema, Pydantic models, TypeScript interfaces, or XML DTDs. Some LLM providers offer native support for structured output through "tool calling" or "function calling" APIs that guarantee valid output within a specified format. When native support isn't available, prompt engineering techniques combined with post-processing validation can achieve similar results. The validation layer is crucial—it serves as a safety net to catch any non-compliant output and either correct it or request regeneration.

```
┌─────────────────────────────────────────────────────────────┐
│                    STRUCTURED OUTPUT FLOW                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   SCHEMA     │    │   LLM WITH   │    │  VALIDATION  │  │
│  │ DEFINITION   │───▶│   STRUCTURED │───▶│    LAYER     │  │
│  │              │    │   OUTPUT    │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │               │
│         ▼                   ▼                    ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ JSON Schema │    │ Guided Decoding│    │ Parse/Retry │  │
│  │ Pydantic   │    │ Tool Calling │    │ Fallback    │  │
│  │ OpenAPI    │    │ JSON Mode    │    │ Rerompt    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: API Response Formatting

A travel booking application needs to return flight search results in a consistent format:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class FlightSegment(BaseModel):
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    aircraft: str

class FlightItinerary(BaseModel):
    total_price: float
    currency: str = "USD"
    segments: List[FlightSegment]
    layover_duration_minutes: Optional[int] = None

def search_flights(origin: str, destination: str, date: str) -> FlightItinerary:
    """Search flights and return structured itinerary."""
    prompt = f"""
    Find flights from {origin} to {destination} on {date}.
    Return the best itinerary with pricing and schedule.
    """
    # Generate and validate structured output
    return generate_structured_output(prompt, FlightItinerary)
```

### Example 2: Data Extraction for Analytics

Extracting structured data from unstructured customer feedback:

```python
class SentimentAnalysis(BaseModel):
    sentiment: str = Field(..., pattern="^(positive|negative|neutral)$")
    confidence: float = Field(..., ge=0, le=1)
    key_themes: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    urgency: str = Field(default="normal")

def analyze_feedback(feedback_text: str) -> SentimentAnalysis:
    """Analyze customer feedback and extract structured sentiment."""
    prompt = f"""
    Analyze this customer feedback and extract:
    - Overall sentiment (positive/negative/neutral)
    - Confidence score (0-1)
    - Key themes mentioned
    - Relevant categories
    - Urgency level
    
    Feedback: {feedback_text}
    """
    return generate_structured_output(prompt, SentimentAnalysis)
```

### Example 3: XML Generation for Legacy Systems

```python
import xml.etree.ElementTree as ET

def generate_xml_output(data: dict, template: str) -> str:
    """Generate XML output matching a legacy system schema."""
    
    prompt = f"""
    Generate XML output matching this DTD template:
    {template}
    
    Data to encode: {json.dumps(data)}
    Output must be valid XML matching the template structure.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "text"},
        temperature=0
    )
    
    # Post-process to ensure valid XML
    xml_output = response.choices[0].message.content.strip()
    if not xml_output.startswith('<?xml'):
        raise ValueError("Invalid XML output")
    
    return xml_output
```

## Architecture Comparison

```
┌────────────────────────────────────────────────────────────────┐
│              STRUCTURED OUTPUT METHODS COMPARISON               │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│   Method     │ Reliability │ Flexibility │ Provider Support  │
├──────────────┼──────────────┼──────────────┼───────────────────┤
│ Tool Calling │   Highest   │    High     │ OpenAI, Anthropic │
│ JSON Mode    │    High     │    High     │ OpenAI, Cohere    │
│ Constrained  │   Medium    │   Medium    │ Custom implem.    ��
│ Prompt+Parse│    Medium   │    High     │ All providers     │
└──────────────┴──────────────┴──────────────┴───────────────────┘
```

## Best Practices

1. **Always validate output** - Even with guided decoding, add validation as a safety net
2. **Use tool calling when available** - It provides the highest reliability
3. **Provide clear error messages** - Help the LLM understand what went wrong
4. **Iterate on schema design** - Start simple, add complexity as needed
5. **Test edge cases** - Include invalid inputs to ensure graceful handling

## Reference Links

- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic Schema Generation](https://docs.pydantic.dev/latest/)
- [JSON Schema Specification](https://json-schema.org/)
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Guardrails for AI - Pydantic Integration](https://github.com/guardrails-ai/guardrails)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
