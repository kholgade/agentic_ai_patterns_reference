# PII Tokenization

## Overview

Automatically detect and tokenize Personally Identifiable Information (PII) before it reaches the LLM, then detokenize for tool calls. This enables agents to orchestrate workflows with sensitive data without exposing raw PII to the model, reducing privacy risks and compliance scope.

## How It Works

```python
class PIITokenizer:
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        }
        self.token_map = {}
        self.counter = 0
    
    def tokenize(self, text: str) -> tuple:
        """Replace PII with tokens before sending to LLM"""
        tokenized_text = text
        
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                pii_value = match.group()
                token = f"__{pii_type.upper()}_{self.counter}__"
                self.token_map[token] = pii_value
                tokenized_text = tokenized_text.replace(pii_value, token)
                self.counter += 1
        
        return tokenized_text, self.token_map
    
    def detokenize(self, text: str) -> str:
        """Replace tokens with original PII for tool calls"""
        result = text
        for token, original in self.token_map.items():
            result = result.replace(token, original)
        return result
    
    def clear_map(self):
        """Clear token map after use (security)"""
        self.token_map.clear()
```

## Integration

```python
class PrivacyPreservingAgent:
    def __init__(self):
        self.tokenizer = PIITokenizer()
    
    def process_request(self, user_input: str):
        # Tokenize PII
        safe_input, token_map = self.tokenizer.tokenize(user_input)
        
        # Process with LLM (never sees raw PII)
        response = self.llm.generate(safe_input)
        
        # Detokenize for tool calls
        if needs_tool_call(response):
            detokenized_params = self.tokenizer.detokenize(response.params)
            result = self.tool.execute(detokenized_params)
        
        # Clear token map
        self.tokenizer.clear_map()
        
        return response
```

## When to Use

- Healthcare applications (HIPAA)
- Financial services (PCI-DSS)
- Customer support with PII
- HR/employee data processing
- GDPR-regulated applications

## Related Patterns

- [Secret Handling](../secret-handling/) - Credential protection
- [Audit Logging](../audit-logging/) - Track PII access
- [Guardrails Pattern](../guardrails-pattern/) - Output validation

## References

- [PII Tokenization](https://agentic-patterns.com/patterns/pii-tokenization)
- [HIPAA Audit Controls](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html)
- [GDPR Requirements](https://gdpr.eu/)