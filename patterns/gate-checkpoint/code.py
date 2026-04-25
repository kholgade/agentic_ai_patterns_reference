from enum import Enum
from dataclasses import dataclass
from typing import Callable, Awaitable
from abc import ABC, abstractmethod

class GateResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"

@dataclass
class GateCheck:
    name: str
    result: GateResult
    message: str
    score: float | None = None
    retry_allowed: bool = True

class Gate(ABC):
    @abstractmethod
    async def check(self, output: str, context: dict) -> GateCheck:
        pass

class QualityGate(Gate):
    def __init__(self, client, min_score: float = 7.0):
        self.client = client
        self.min_score = min_score
    
    async def check(self, output: str, context: dict) -> GateCheck:
        prompt = f"""Rate the quality of this output (0-10).
Output: {output[:500]}

Return format: score|reason"""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content
        score = float(content.split("|")[0])
        
        return GateCheck(
            name="quality",
            result=GateResult.PASS if score >= self.min_score else GateResult.FAIL,
            message=f"Score: {score}",
            score=score
        )

class SafetyGate(Gate):
    def __init__(self, client, blocked_terms: list[str] = None):
        self.client = client
        self.blocked_terms = blocked_terms or []
    
    async def check(self, output: str, context: dict) -> GateCheck:
        output_lower = output.lower()
        violations = [term for term in self.blocked_terms if term in output_lower]
        
        if violations:
            return GateCheck(
                name="safety",
                result=GateResult.FAIL,
                message=f"Blocked terms found: {violations}",
                retry_allowed=False
            )
        
        return GateCheck(
            name="safety",
            result=GateResult.PASS,
            message="No safety violations"
        )

class FormatGate(Gate):
    def __init__(self, required_elements: list[str]):
        self.required_elements = required_elements
    
    async def check(self, output: str, context: dict) -> GateCheck:
        missing = [
            elem for elem in self.required_elements 
            if elem not in output
        ]
        
        return GateCheck(
            name="format",
            result=GateResult.PASS if not missing else GateResult.FAIL,
            message=f"Missing elements: {missing}" if missing else "Format valid"
        )

class GatedWorkflow:
    def __init__(self, client):
        self.client = client
        self.stages: list[tuple[str, list[Gate]]] = []
        self.max_retries = 3
    
    def add_stage(self, name: str, prompt: str, gates: list[Gate] = None):
        self.stages.append((name, gates or []))
        return self
    
    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    async def check_gates(self, output: str, gates: list[Gate], context: dict) -> list[GateCheck]:
        results = []
        for gate in gates:
            check = await gate.check(output, context)
            results.append(check)
        return results
    
    async def execute(self, initial_prompt: str, context: dict = None) -> tuple[str, list[GateCheck]]:
        context = context or {}
        results = []
        
        for stage_idx, (stage_name, gates) in enumerate(self.stages):
            prompt = initial_prompt if stage_idx == 0 else None
            
            for attempt in range(self.max_retries):
                if stage_idx == 0:
                    output = await self.generate(initial_prompt)
                else:
                    output = await self.generate(f"Refine: {results[-1] if results else initial_prompt}")
                
                if gates:
                    gate_results = await self.check_gates(output, gates, context)
                    all_passed = all(g.result == GateResult.PASS for g in gate_results)
                    
                    if all_passed:
                        results.extend(gate_results)
                        break
                    
                    if attempt == self.max_retries - 1:
                        raise RuntimeError(f"Failed gates at stage {stage_name}")
                else:
                    results.append(GateCheck(name=stage_name, result=GateResult.PASS, message="No gates"))
                    break
        
        return output, results

# Usage
workflow = GatedWorkflow(client)
workflow.add_stage(
    "generate", 
    "Create a product description: {prompt}",
    gates=[QualityGate(client, min_score=7.0), SafetyGate(client)]
).add_stage(
    "refine", 
    "Enhance the description",
    gates=[FormatGate(required_elements=["features", "benefits"])]
)

output, checks = await workflow.execute("Wireless bluetooth headphones")