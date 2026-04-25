from enum import Enum
from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
import re

class HarmCategory(str, Enum):
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    SEXUAL = "sexual"
    SELF_HARM = "self_harm"
    MISINFORMATION = "misinformation"
    PII = "personal_identifiable_info"
    HARASSMENT = "harassment"
    ILLEGAL = "illegal_activity"

class Action(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    SANITIZE = "sanitize"
    ESCALATE = "escalate"

@dataclass
class GuardrailResult:
    action: Action
    category: Optional[HarmCategory]
    confidence: float
    reason: str
    sanitized_content: Optional[str] = None

class ContentClassifier:
    """Content classification guardrail using embeddings."""
    
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.harm_categories = {
            HarmCategory.VIOLENCE: ["violent content", "harm", "attack"],
            HarmCategory.HATE_SPEECH: ["hate", "discriminate", "slur"],
            HarmCategory.SELF_HARM: ["suicide", "self harm", "cutting"],
            HarmCategory.MISINFORMATION: ["fake news", "conspiracy"],
            HarmCategory.ILLEGAL: ["illegal", "fraud", "drug"]
        }
    
    def classify(self, text: str) -> list[tuple[HarmCategory, float]]:
        """Classify text and return categories with confidence scores."""
        results = []
        text_lower = text.lower()
        
        for category, keywords in self.harm_categories.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                if confidence >= self.threshold:
                    results.append((category, confidence))
        
        return results

class RuleBasedFilter:
    """Rule-based filtering with allowlists and blocklists."""
    
    def __init__(self):
        self.blocked_patterns = [
            r"ignore.*(previous|instructions|system|prompt)",
            r"\\(system\\)|\\(system\\)",
            "```system",
            "JAILBREAK",
            "DAN\\(",
            "developer.*mode",
        ]
        self.blocked_phrases = [
            "how to make a bomb",
            "how to create malware",
            "step-by-step hacking"
        ]
        self.compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.blocked_patterns
        ]
    
    def check(self, text: str) -> tuple[bool, Optional[str]]:
        """Check text against rules. Returns (is_blocked, reason)."""
        for phrase in self.blocked_phrases:
            if phrase.lower() in text.lower():
                return True, f"Blocked phrase: {phrase}"
        
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True, f"Blocked pattern: {pattern.pattern}"
        
        return False, None

class InputGuardrails:
    """Combined input guardrail pipeline."""
    
    def __init__(self):
        self.classifier = ContentClassifier(threshold=0.7)
        self.rule_filter = RuleBasedFilter()
        self.max_length = 10000
    
    def validate(self, text: str) -> GuardrailResult:
        """Validate input through all guardrail stages."""
        
        # Stage 1: Length check
        if len(text) > self.max_length:
            return GuardrailResult(
                action=Action.BLOCK,
                category=None,
                confidence=1.0,
                reason=f"Input exceeds max length of {self.max_length}"
            )
        
        # Stage 2: Rule-based filter
        is_blocked, reason = self.rule_filter.check(text)
        if is_blocked:
            return GuardrailResult(
                action=Action.BLOCK,
                category=None,
                confidence=1.0,
                reason=reason
            )
        
        # Stage 3: Content classification
        categories = self.classifier.classify(text)
        if categories:
            highest = max(categories, key=lambda x: x[1])
            return GuardrailResult(
                action=Action.BLOCK,
                category=highest[0],
                confidence=highest[1],
                reason=f"Detected {highest[0].value} content"
            )
        
        return GuardrailResult(
            action=Action.ALLOW,
            category=None,
            confidence=1.0,
            reason="Passed all guardrails"
        )

class OutputGuardrails:
    """Output guardrail pipeline."""
    
    def __init__(self):
        self.classifier = ContentClassifier(threshold=0.8)
        self.pii_patterns = [
            (r"\\b\\d{3}-\\d{2}-\\d{4}\\b", "SSN"),
            (r"\\b\\d{16}\\b", "Credit Card"),
            (r"\\b[\\w.-]+@[\\w.-]+\\.\\w+\\b", "Email"),
        ]
        self.max_retry = 3
    
    def sanitize_pii(self, text: str) -> str:
        """Remove PII from text."""
        for pattern, pii_type in self.pii_patterns:
            text = re.sub(pattern, f"[{pii_type} REDACTED]", text)
        return text
    
    def validate(self, text: str) -> GuardrailResult:
        """Validate output through guardrail stages."""
        
        # Check for harmful content
        categories = self.classifier.classify(text)
        if categories:
            highest = max(categories, key=lambda x: x[1])
            return GuardrailResult(
                action=Action.BLOCK,
                category=highest[0],
                confidence=highest[1],
                reason=f"Output contains {highest[0].value}"
            )
        
        # Sanitize PII
        sanitized = self.sanitize_pii(text)
        if sanitized != text:
            return GuardrailResult(
                action=Action.SANITIZE,
                category=HarmCategory.PII,
                confidence=0.9,
                reason="PII detected and redacted",
                sanitized_content=sanitized
            )
        
        return GuardrailResult(
            action=Action.ALLOW,
            category=None,
            confidence=1.0,
            reason="Output validated"
        )