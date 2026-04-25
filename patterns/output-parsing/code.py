import re
import json
import xml.etree.ElementTree as ET
from typing import Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field

class ParseStrategy(str, Enum):
    REGEX = "regex"
    PARSER_COMBINATOR = "parser_combinator"
    LLM_ASSISTED = "llm_assisted"
    FUZZY = "fuzzy"

@dataclass
class ParseResult:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    confidence: float = 0.0
    strategy_used: Optional[ParseStrategy] = None

class RegexExtractor:
    """Regex-based structured extraction."""
    
    def __init__(self, pattern: str, extract_type: str = "json"):
        self.pattern = pattern
        self.extract_type = extract_type
    
    def extract(self, text: str) -> ParseResult:
        """Extract structured data using regex."""
        
        if self.extract_type == "json":
            # Try to find JSON block
            json_pattern = r"```json\s*([\s\S]*?)\s*```|(\{[\s\S]*\})"
            match = re.search(json_pattern, text)
            
            if match:
                json_str = match.group(1) or match.group(2)
                try:
                    data = json.loads(json_str)
                    return ParseResult(
                        success=True,
                        data=data,
                        confidence=0.9,
                        strategy_used=ParseStrategy.REGEX
                    )
                except json.JSONDecodeError as e:
                    return ParseResult(
                        success=False,
                        error=f"JSON parse error: {e}",
                        strategy_used=ParseStrategy.REGEX
                    )
        
        elif self.extract_type == "xml":
            xml_pattern = r"<([\w-]+)>.*?</\1>|<([\w-]+)>([^<]+)"
            matches = re.findall(xml_pattern, text)
            if matches:
                data = {m[0] or m[1]: m[2] for m in matches}
                return ParseResult(
                    success=True,
                    data=data,
                    confidence=0.7,
                    strategy_used=ParseStrategy.REGEX
                )
        
        return ParseResult(
            success=False,
            error="No matching pattern found",
            strategy_used=ParseStrategy.REGEX
        )

class ParserCombinator:
    """Combinator-based parser with fallback chains."""
    
    def __init__(self, parsers: list[tuple[Callable, float]]):
        self.parsers = parsers  # List of (parser_func, confidence)
    
    def parse(self, text: str) -> ParseResult:
        """Try parsers in order until one succeeds."""
        
        for parser, confidence in self.parsers:
            try:
                result = parser(text)
                if result:
                    return ParseResult(
                        success=True,
                        data=result,
                        confidence=confidence,
                        strategy_used=ParseStrategy.PARSER_COMBINATOR
                    )
            except Exception:
                continue
        
        return ParseResult(
            success=False,
            error="All parsers failed",
            strategy_used=ParseStrategy.PARSER_COMBINATOR
        )

class LLMAssistedParser:
    """Use LLM to parse unstructured output."""
    
    def __init__(self, client, schema: type[BaseModel]):
        self.client = client
        self.schema = schema
    
    def parse(self, text: str) -> ParseResult:
        """Use LLM to extract structure from messy output."""
        
        prompt = f"""Extract the following data from this output.
        
Output:
```
{text}
```

Extract ONLY valid JSON matching this schema:
{self.schema.model_json_schema()}

If data cannot be extracted, return:
{{"error": "Could not extract data", "partial": "<extracted info>"}}
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        try:
            data = json.loads(response.choices[0].message.content)
            if "error" in data:
                return ParseResult(
                    success=False,
                    error=data.get("error"),
                    data=data.get("partial"),
                    confidence=0.3,
                    strategy_used=ParseStrategy.LLM_ASSISTED
                )
            
            validated = self.schema.model_validate(data)
            return ParseResult(
                success=True,
                data=validated.model_dump(),
                confidence=0.8,
                strategy_used=ParseStrategy.LLM_ASSISTED
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error=str(e),
                strategy_used=ParseStrategy.LLM_ASSISTED
            )

class RobustOutputParser:
    """Complete output parsing pipeline with fallbacks."""
    
    def __init__(self, client, schema: type[BaseModel]):
        self.schema = schema
        
        # Stage 1: Direct regex extraction
        self.regex_parser = RegexExtractor(r"(\{[\s\S]*\})", "json")
        
        # Stage 2: Parser combinator with multiple patterns
        def parse_key_value(text):
            pattern = r"(\w+):\s*([^\n]+)"
            matches = re.findall(pattern, text)
            if matches:
                return {k.strip(): v.strip() for k, v in matches}
            return None
        
        def parse_yaml_like(text):
            lines = text.strip().split("\n")
            data = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    data[key.strip()] = value.strip()
            return data if data else None
        
        self.combinator = ParserCombinator([
            (lambda t: self.regex_parser.extract(t).data, 0.8),
            (parse_key_value, 0.5),
            (parse_yaml_like, 0.4),
        ])
        
        # Stage 3: LLM-assisted as final fallback
        self.llm_parser = LLMAssistedParser(client, schema)
    
    def parse(self, text: str) -> ParseResult:
        """Parse with multiple fallback strategies."""
        
        # Strategy 1: Try regex
        result = self.regex_parser.extract(text)
        if result.success:
            try:
                result.data = self.schema.model_validate(result.data)
                return result
            except Exception:
                pass  # Try next strategy
        
        # Strategy 2: Try combinator
        result = self.combinator.parse(text)
        if result.success:
            try:
                result.data = self.schema.model_validate(result.data)
                return result
            except Exception:
                pass
        
        # Strategy 3: LLM-assisted
        return self.llm_parser.parse(text)