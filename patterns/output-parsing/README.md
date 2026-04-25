---
title: Output Parsing
description: Techniques for reliably extracting structured data from LLM outputs
complexity: low
model_maturity: mature
typical_use_cases: ["Data extraction", "Format conversion", "Parsing structured text"]
dependencies: []
category: output-generation
---

The Output Parsing pattern provides robust techniques for extracting structured data from LLM outputs that may be inconsistent, irregular, or partially malformed. Unlike structured output generation which enforces format compliance during generation, this pattern handles real-world scenarios where LLM outputs arrive with variations, extra text, formatting inconsistencies, or partial malformation. The key insight is that we cannot always rely on the LLM to produce perfectly formatted output, so we need resilient parsing strategies that can handle the messiness of natural language generation. This pattern is essential for building reliable production systems that must process diverse and unpredictable LLM outputs.

The implementation architecture combines multiple parsing strategies in sequence. Regex-based extraction targets specific patterns like JSON fragments, code blocks, or structured markers. Parser combinators build complex parsers from simpler ones, allowing partial matches and error recovery. Fuzzy matching uses edit distance and similarity thresholds to handle typos and near-matches. Finally, LLM-assisted parsing leverages a secondary LLM call to interpret and extract structured data from messy output. The pattern also includes fallback strategies: requesting regeneration, using default values, or surfacing parsing errors to humans. The key principle is graceful degradation—extracting as much valid data as possible rather than failing entirely.

```
┌─────────────────────────────────────────────────────────────┐
│                  OUTPUT PARSING PIPELINE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   RAW LLM    │───▶│   PARSING    │───▶│  STRUCTURED  │  │
│  │   OUTPUT     │    │   PIPELINE   │    │    DATA     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                            │                               │
│         ┌──────────────────┼──────────────────┐          │
│         ▼                  ▼                  ▼           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │    Regex     │  │   Parser     │  │   LLM-as-    │   │
│  │  Extraction │  │  Combinators │  │   Parser    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│         │                  │                  │               │
│         ▼                  ▼                  ▼           │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────��──┐   ��
│  │   Pattern   │  │  Partial   │  │  Semantic   │   │
│  │   Matching │  │   Match    │  │  Extraction │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                             │
│         FALLBACK STRATEGIES                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Request    │  │   Use       │  │   Surface   │   │
│  │  Regen     │  │  Defaults   │  │   Error    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Parsing JSON from Messy Output

```python
class ExtractedData(BaseModel):
    name: str
    age: int
    email: str
    active: bool = True

def parse_user_data(client, output: str) -> ExtractedData:
    """Parse user data from potentially messy LLM output."""
    
    parser = RobustOutputParser(client, ExtractedData)
    result = parser.parse(output)
    
    if not result.success:
        raise ValueError(f"Failed to parse: {result.error}")
    
    return ExtractedData(**result.data)

# Example messy outputs
messy_outputs = [
    """
    Here's the user info:
    ```json
    {"name": "John Doe", "age": 30, "email": "john@example.com"}
    ```
    """,
    """
    User: John Doe
    Age: 30
    Email: john@example.com
    Status: active
    """,
    """
    The user's name is John Doe, they're 30 years old.
    Email: john@example.com
    Active? Yes!
    """
]

for output in messy_outputs:
    try:
        data = parse_user_data(client, output)
        print(f"Parsed: {data.name}, {data.age}")
    except ValueError as e:
        print(f"Failed: {e}")
```

### Example 2: Extracting Multiple Entities

```python
from typing import List

class Person(BaseModel):
    name: str
    role: str
    department: Optional[str] = None

def extract_persons(text: str) -> List[Person]:
    """Extract multiple person entities from text."""
    
    parser = RegexExtractor(r"Person \d+: ([^\n]+)", "custom")
    
    # Extract each person block
    person_pattern = r"Person \d+: ([^\n]+)"
    blocks = re.findall(person_pattern, text)
    
    persons = []
    for block in blocks:
        try:
            parts = block.split(",")
            person = Person(
                name=parts[0].strip(),
                role=parts[1].strip() if len(parts) > 1 else "unknown",
                department=parts[2].strip() if len(parts) > 2 else None
            )
            persons.append(person)
        except Exception:
            continue
    
    return persons
```

### Example 3: Handling Code Extraction

```python
def extract_code_blocks(text: str) -> dict[str, str]:
    """Extract code blocks by language."""
    
    code_blocks = {}
    
    # Find all code blocks
    pattern = r"```(\w+)\s*\n([\s\S]*?)```"
    matches = re.findall(pattern, text)
    
    for language, code in matches:
        code_blocks[language] = code.strip()
    
    # Also handle inline code
    inline_pattern = r"`([^`]+)`"
    inline = re.findall(inline_pattern, text)
    if inline:
        code_blocks["inline"] = inline
    
    return code_blocks

# Example LLM output with mixed content
mixed_output = """
Here is a Python function to calculate fibonacci:

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
```

And here's some `inline_code` as well.

Also in JavaScript:
```javascript
function fib(n) {
    return n <= 1 ? n : fib(n-1) + fib(n-2);
}
```
"""

code = extract_code_blocks(mixed_output)
print(code.keys())  // ['python', 'javascript', 'inline']
```

## Comparison of Strategies

```
┌────────────────────────────────────────────────────────────────┐
│            OUTPUT PARSING STRATEGY COMPARISON                     │
├──────────────────────┬──────────────┬──────────────┬───────────┤
│   Strategy           │  Accuracy  │   Speed    │  Cost     │
├──────────────────────┼──────────────┼──────────────┼───────────┤
│ Regex Extraction    │   Medium   │   Fast    │   Free    │
│ Parser Combinators │   Medium   │   Fast    │   Free    │
│ Fuzzy Matching     │   Medium   │  Medium   │   Free    │
│ LLM-Assisted      │   High     │   Slow    │   Paid    │
│ Combined Pipeline │  Highest  │  Medium   │ Medium   │
└──────────────────────┴──────────────┴──────────────┴───────────┘
```

## Best Practices

1. **Start simple** - Try regex before more expensive LLM parsing
2. **Validate always** - Schema validation catches subtle errors
3. **Log failures** - Understanding parsing failures improves the system
4. **Graceful degradation** - Partial data is better than no data
5. **Test with real outputs** - Synthetic test data won't catch all issues

## Reference Links

- [Pydantic Validation](https://docs.pydantic.dev/latest/)
- [JSON Path Queries](https://goessner.net/articles/JsonPath/)
- [Regex Performance](https://www.regular-expressions.info/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Guardrails AI - Output Validation](https://github.com/guardrails-ai/guardrails)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
