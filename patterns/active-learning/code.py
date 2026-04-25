import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

client = instructor.patch(OpenAI())

class ClarificationType(Enum):
    MISSING_INFO = "missing_information"
    AMBIGUITY = "ambiguity"
    UNCERTAINTY = "uncertainty"
    SAFETY = "safety_concern"

class ClarificationRequest(BaseModel):
    type: ClarificationType
    question: str
    context_needed: str
    priority: int

class ActiveLearningAgent:
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.pending_clarifications: List[ClarificationRequest] = []
    
    async def assess_confidence(self, task: str) -> float:
        assessment_prompt = f"""Analyze this task and assess your confidence in completing it accurately.
        
Task: {task}

Consider:
1. Do you have all necessary context?
2. Are there any ambiguous elements?
3. Are there multiple valid interpretations?

Respond with a confidence score between 0 and 1."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that assesses its own confidence honestly."},
                {"role": "user", "content": assessment_prompt}
            ]
        )
        
        content = response.choices[0].message.content
        try:
            score = float(content.split('\n')[0].strip())
            if not 0 <= score <= 1:
                score = 0.5
        except (ValueError, IndexError):
            score = 0.5
        
        return score
    
    async def identify_clarifications(self, task: str) -> List[ClarificationRequest]:
        clarification_prompt = f"""Analyze this task and identify any information gaps or ambiguities.
        
Task: {task}

For each issue, provide:
1. The type of clarification needed
2. A specific question to ask
3. Why this information is needed
4. Priority (1 = critical, 5 = nice to have)

If no clarifications needed, say "NONE"."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You identify clarification needs precisely."},
                {"role": "user", "content": clarification_prompt}
            ]
        )
        
        content = response.choices[0].message.content
        
        clarifications = []
        if content.strip() != "NONE":
            for line in content.split('\n'):
                if line.strip() and not line.startswith('Task'):
                    clarifications.append(ClarificationRequest(
                        type=ClarificationType.AMBIGUITY,
                        question=line.strip(),
                        context_needed="Additional context",
                        priority=3
                    ))
        
        return clarifications
    
    async def execute_with_clarification(self, task: str, user_responses: dict = None) -> dict:
        confidence = await self.assess_confidence(task)
        
        if confidence >= self.confidence_threshold:
            return await self._generate_output(task)
        
        clarifications = await self.identify_clarifications(task)
        
        pending = [c for c in clarifications if c.priority <= 2]
        
        if pending and not user_responses:
            return {
                "status": "clarification_needed",
                "requests": [c.model_dump() for c in pending],
                "confidence": confidence
            }
        
        augmented_task = task
        if user_responses:
            for key, value in user_responses.items():
                augmented_task += f"\n\nAdditional context: {key} = {value}"
        
        return await self._generate_output(augmented_task)
    
    async def _generate_output(self, task: str) -> dict:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You complete tasks accurately and thoroughly."},
                {"role": "user", "content": task}
            ]
        )
        
        return {
            "status": "completed",
            "output": response.choices[0].message.content
        }

async def run_active_learning():
    agent = ActiveLearningAgent(confidence_threshold=0.75)
    
    task = "Write a summary of the team's project progress"
    
    result = await agent.execute_with_clarification(task)
    
    if result["status"] == "clarification_needed":
        clarifications = result["requests"]
        print("Clarification needed:")
        for c in clarifications:
            print(f"  - {c['question']}")
        
        user_responses = {c["question"]: "The Q4 progress report for the mobile app team" 
                        for c in clarifications}
        
        result = await agent.execute_with_clarification(task, user_responses)
    
    return result