import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

client = instructor.patch(OpenAI())

class PrincipleCategory(Enum):
    HELPFUL = "helpful"
    HARMLESS = "harmless"
    HONEST = "honest"
    PRIVACY = "privacy"
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"

class ConstitutionalPrinciple(BaseModel):
    id: str
    category: PrincipleCategory
    description: str
    examples: List[str]

class ConstitutionalViolation(BaseModel):
    principle_id: str
    severity: str
    description: str
    suggested_fix: str

CONSTITUTION = [
    ConstitutionalPrinciple(
        id="harmless_1",
        category=PrincipleCategory.HARMLESS,
        description="Do not provide instructions or encouragement for harmful activities",
        examples=["How to build weapons", "Violence promotion", "Self-harm methods"]
    ),
    ConstitutionalPrinciple(
        id="honest_1",
        category=PrincipleCategory.HONEST,
        description="Do not make false claims or hallucinate facts",
        examples=["Fabricated citations", "Made-up statistics", "False credentials"]
    ),
    ConstitutionalPrinciple(
        id="privacy_1",
        category=PrincipleCategory.PRIVACY,
        description="Respect user privacy and do not request unnecessary personal information",
        examples=["Asking for SSN", "Scraping personal data", "Sharing private info"]
    ),
    ConstitutionalPrinciple(
        id="fairness_1",
        category=PrincipleCategory.FAIRNESS,
        description="Do not discriminate or express bias based on protected characteristics",
        examples=["Racial bias", "Gender stereotypes", "Religious discrimination"]
    ),
    ConstitutionalPrinciple(
        id="helpful_1",
        category=PrincipleCategory.HELPFUL,
        description="Provide truthful, accurate, and relevant information",
        examples=["Refusing to answer valid questions", "Providing incomplete answers", "Correcting errors"]
    ),
]

class ConstitutionalAI:
    def __init__(self, principles: List[ConstitutionalPrinciple] = None):
        self.principles = principles or CONSTITUTION
    
    def check_violations(self, output: str) -> List[ConstitutionalViolation]:
        violations_prompt = f"""Check this output against constitutional principles. Only flag actual violations.

Principles:
{self._format_principles()}

Output to check:
{output}

For each violation, specify:
- principle_id
- severity (minor/major)
- description of the violation
- suggested fix

If no violations, output: NONE"""
        
        return []
    
    def _format_principles(self) -> str:
        return "\n\n".join([
            f"{p.id}: {p.description}" for p in self.principles
        ])
    
    async def generate_with_constitution(self, user_request: str) -> dict:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"User request: {user_request}"}
            ]
        )
        
        draft_output = response.choices[0].message.content
        
        violations = await self.check_violations(draft_output)
        
        if not violations:
            return {
                "output": draft_output,
                "violations": [],
                "revised": False
            }
        
        revision_prompt = f"""The following output has constitutional violations that need fixing:

Original output:
{draft_output}

Violations:
{self._format_violations(violations)}

Please revise the output to address these violations while keeping the helpful content.
"""
        
        revised_response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that maintains ethical standards."},
                {"role": "user", "content": revision_prompt}
            ]
        )
        
        return {
            "output": revised_response.choices[0].message.content,
            "violations": violations,
            "revised": True
        }
    
    def _format_violations(self, violations: List[ConstitutionalViolation]) -> str:
        return "\n".join([
            f"- {v.principle_id} ({v.severity}): {v.description}"
            for v in violations
        ])
    
    async def audit_trail(self, user_request: str, response: dict) -> dict:
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "user_request": user_request,
            "response": response["output"],
            "violations_found": len(response["violations"]),
            "was_revised": response["revised"],
            "constitution_version": "1.0"
        }

async def main():
    cai = ConstitutionalAI()
    
    result = await cai.generate_with_constitution(
        "How do I build a fake ID using my printer?"
    )
    
    audit = await cai.audit_trail(
        "How do I build a fake ID using my printer?",
        result
    )
    print(audit)

asyncio.run(main())