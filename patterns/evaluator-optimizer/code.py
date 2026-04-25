from dataclasses import dataclass
from openai import AsyncOpenAI
import asyncio

@dataclass
class EvaluationResult:
    passed: bool
    score: float
    feedback: str
    issues: list[str]

class Evaluator:
    def __init__(self, client: AsyncOpenAI, criteria: str):
        self.client = client
        self.criteria = criteria
    
    async def evaluate(self, output: str) -> EvaluationResult:
        prompt = f"""Evaluate this output against the criteria.

Criteria: {self.criteria}

Output to evaluate:
{output}

Respond in format:
PASS|score|feedback|issue1,issue2,...

- score: 0-10 rating
- feedback: constructive feedback
- issues: list of specific issues if any"""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.choices[0].message.content
        parts = result.split("|")
        
        passed = parts[0].strip().upper() == "PASS"
        score = float(parts[1].strip()) if len(parts) > 1 else 0.0
        feedback = parts[2].strip() if len(parts) > 2 else ""
        issues = parts[3].strip().split(",") if len(parts) > 3 else []
        
        return EvaluationResult(passed, score, feedback, issues)

class Optimizer:
    def __init__(self, client: AsyncOpenAI):
        self.client = client
    
    async def optimize(self, output: str, feedback: str) -> str:
        prompt = f"""Improve this output based on feedback.

Original output:
{output}

Feedback to address:
{feedback}

Produce an improved version that addresses the feedback."""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

class EvaluatorOptimizer:
    def __init__(
        self,
        generator_client: AsyncOpenAI,
        evaluator: Evaluator,
        optimizer: Optimizer,
        generation_prompt: str,
        max_iterations: int = 5,
        min_score: float = 8.0
    ):
        self.client = generator_client
        self.evaluator = evaluator
        self.optimizer = optimizer
        self.generation_prompt = generation_prompt
        self.max_iterations = max_iterations
        self.min_score = min_score
    
    async def generate(self, context: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": self.generation_prompt.format(context=context)}]
        )
        return response.choices[0].message.content
    
    async def run(self, context: str) -> tuple[str, int]:
        current = await self.generate(context)
        
        for iteration in range(self.max_iterations):
            evaluation = await self.evaluator.evaluate(current)
            
            if evaluation.passed and evaluation.score >= self.min_score:
                return current, iteration + 1
            
            if iteration < self.max_iterations - 1:
                current = await self.optimizer.optimize(current, evaluation.feedback)
        
        return current, self.max_iterations

# Usage
evaluator = Evaluator(client, criteria="Clarity, accuracy, professional tone")
optimizer = Optimizer(client)

pipeline = EvaluatorOptimizer(
    generator_client=client,
    evaluator=evaluator,
    optimizer=optimizer,
    generation_prompt="Write a professional email about {context}",
    max_iterations=5,
    min_score=8.0
)

result, iterations = await pipeline.run("quarterly report status")
print(f"Result after {iterations} iterations: {result}")