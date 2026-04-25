# Output Verification Loop

## Overview

Verify LLM outputs by extracting individual claims, checking each against evidence sources, and returning per-claim trust scores before acting on the result. This pattern prevents hallucinations and misinformation from propagating through agent workflows.

## How It Works

```python
class OutputVerifier:
    def __init__(self, evidence_sources: list):
        self.sources = evidence_sources
    
    def verify(self, llm_output: str) -> VerificationResult:
        """
        Step 1: Extract claims from output
        Step 2: Verify each claim against evidence
        Step 3: Return trust scores per claim
        """
        
        # Extract claims
        claims = self._extract_claims(llm_output)
        
        # Verify each claim
        verified_claims = []
        for claim in claims:
            verification = self._verify_claim(claim)
            verified_claims.append(verification)
        
        # Calculate overall trust
        trust_score = self._calculate_trust(verified_claims)
        
        return VerificationResult(
            original_output=llm_output,
            claims=verified_claims,
            overall_trust=trust_score,
            recommendation=self._recommend_action(trust_score)
        )
    
    def _extract_claims(self, text: str) -> list:
        """Extract factual claims from text"""
        prompt = f"""
        Extract all factual claims from this text.
        Return as a list of simple statements.
        
        Text: {text}
        """
        return llm.generate(prompt)
    
    def _verify_claim(self, claim: str) -> ClaimVerification:
        """Verify single claim against evidence sources"""
        evidence = self._search_evidence(claim)
        
        if not evidence:
            return ClaimVerification(
                claim=claim,
                status='unverifiable',
                confidence=0.5
            )
        
        # Check if evidence supports claim
        support_score = self._calculate_support(claim, evidence)
        
        return ClaimVerification(
            claim=claim,
            status='supported' if support_score > 0.7 else 'contradicted' if support_score < 0.3 else 'uncertain',
            confidence=support_score,
            evidence=evidence
        )
    
    def _search_evidence(self, claim: str) -> list:
        """Search evidence sources for relevant information"""
        results = []
        for source in self.sources:
            evidence = source.search(claim)
            results.extend(evidence)
        return results
```

## When to Use

- RAG systems (verify retrieved information)
- Medical/legal/financial advice
- News/fact-checking applications
- Research assistance
- Any high-stakes decision making

## Related Patterns

- [CriticGPT-Style Review](../criticgpt-review/) - Code quality verification
- [Guardrails Pattern](../guardrails-pattern/) - Output validation
- [LLM as Judge](../llm-as-judge/) - Quality assessment

## References

- [Output Verification Loop](https://agentic-patterns.com/patterns/output-verification-loop)
- [Chain-of-Verification](../chain-of-verification/) - Related pattern
- [Self-RAG](../self-rag/) - Self-verification during generation