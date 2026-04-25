# CriticGPT-Style Code Review

## Overview

Use AI to review AI-generated code with iterative feedback and improvement cycles. As AI models generate increasing amounts of code, the bottleneck in software development shifts from code generation to code verification and review. This pattern provides systematic AI-assisted code review.

## How It Works

```python
class CriticGPTReviewer:
    def __init__(self, reviewer_llm, coder_llm):
        self.reviewer = reviewer_llm  # Specialized in code review
        self.coder = coder_llm        # Code generation
    
    def review_and_improve(self, code: str, requirements: str) -> dict:
        """
        Iterative review and improvement cycle
        """
        iteration = 0
        max_iterations = 3
        current_code = code
        
        while iteration < max_iterations:
            # Review current code
            review = self.reviewer.generate(f"""
                Review this code for:
                1. Correctness (does it meet requirements?)
                2. Security vulnerabilities
                3. Performance issues
                4. Code quality (readability, maintainability)
                5. Edge cases and error handling
                
                Requirements: {requirements}
                Code: {current_code}
                
                Return specific, actionable feedback.
            """)
            
            # Check if review found issues
            if review['issues_found'] == 0:
                break
            
            # Generate improved code
            current_code = self.coder.generate(f"""
                Improve this code based on the review feedback:
                
                Original code: {code}
                Review feedback: {review}
                
                Return improved code addressing all issues.
            """)
            
            iteration += 1
        
        return {
            'final_code': current_code,
            'iterations': iteration,
            'review': review
        }
```

## Review Categories

```python
REVIEW_CATEGORIES = {
    'correctness': 'Does it work as intended?',
    'security': 'Any vulnerabilities (injection, XSS, auth)?',
    'performance': 'Time/space complexity, bottlenecks?',
    'maintainability': 'Clean, readable, documented?',
    'testing': 'Adequate test coverage?',
    'edge_cases': 'Handles errors and edge cases?',
}
```

## When to Use

- AI-generated code verification
- Code quality assurance
- Security review automation
- Learning/mentoring junior developers
- Catching subtle bugs AI might introduce

## Related Patterns

- [AI-Assisted Code Review](https://agentic-patterns.com/patterns/ai-assisted-code-review-verification) - Related pattern
- [Output Verification Loop](../output-verification-loop/) - General verification
- [Guardrails Pattern](../guardrails-pattern/) - Validation

## References

- [CriticGPT-Style Code Review](https://agentic-patterns.com/patterns/criticgpt-style-evaluation)
- [AI-Assisted Code Review](https://agentic-patterns.com/patterns/ai-assisted-code-review-verification)
- [Abstracted Code Representation](https://agentic-patterns.com/patterns/abstracted-code-representation-for-review)