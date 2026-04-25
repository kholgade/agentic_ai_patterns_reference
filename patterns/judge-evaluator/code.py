from typing import Any, Optional
from dataclasses import dataclass
from openai import AsyncOpenAI
import json

@dataclass
class EvaluationCriteria:
    correctness: float = 0.0
    completeness: float = 0.0
    safety: float = 0.0
    style: float = 0.0
    
    @property
    def overall_score(self) -> float:
        weights = {"correctness": 0.35, "completeness": 0.30, "safety": 0.20, "style": 0.15}
        return sum(getattr(self, k) * v for k, v in weights.items())

@dataclass
class EvaluationResult:
    criteria: EvaluationCriteria
    passed: bool
    feedback: str
    details: str

class JudgeAgent:
    def __init__(self, client: AsyncOpenAI, threshold: float = 0.7):
        self.client = client
        self.threshold = threshold
    
    async def evaluate(self, task: str, output: str) -> EvaluationResult:
        prompt = f"""Evaluate this output against the criteria.

Task: {task}

Output to evaluate:
{output}

Evaluate on a scale of 0-100 for each criterion:
1. Correctness: Is the information accurate and technically sound?
2. Completeness: Does it fully address the task?
3. Safety: Is it free from harmful content?
4. Style: Is it well-written and clear?

Return JSON with: correctness, completeness, safety, style (as floats), feedback (string), details (string)"""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        
        criteria = EvaluationCriteria(
            correctness=data.get("correctness", 0),
            completeness=data.get("completeness", 0),
            safety=data.get("safety", 0),
            style=data.get("style", 0)
        )
        
        passed = criteria.overall_score >= self.threshold
        
        return EvaluationResult(
            criteria=criteria,
            passed=passed,
            feedback=data.get("feedback", ""),
            details=data.get("details", "")
        )

class ProducerAgent:
    def __init__(self, client: AsyncOpenAI):
        self.client = client
    
    async def produce(self, task: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": task}]
        )
        return response.choices[0].message.content

class JudgeEvaluatorWorkflow:
    def __init__(self, client: AsyncOpenAI, max_attempts: int = 3):
        self.judge = JudgeAgent(client)
        self.producer = ProducerAgent(client)
        self.max_attempts = max_attempts
    
    async def execute(self, task: str) -> tuple[str, EvaluationResult]:
        for attempt in range(self.max_attempts):
            output = await self.producer.produce(task)
            result = await self.judge.evaluate(task, output)
            
            if result.passed:
                return output, result
            
            if attempt < self.max_attempts - 1:
                task = f"{task}\n\nPrevious output feedback:\n{result.feedback}\n\nPlease improve."
        
        return output, result

judge = JudgeAgent(client, threshold=0.75)
producer = ProducerAgent(client)

output = await producer.produce("Explain quantum computing")
result = await judge.evaluate("Explain quantum computing", output)

if result.passed:
    print(f"Accepted! Score: {result.criteria.overall_score:.1f}")
else:
    print(f"Needs revision: {result.feedback}")