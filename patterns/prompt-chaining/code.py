import asyncio
from typing import Any, Callable
from dataclasses import dataclass

@dataclass
class ChainStep:
    name: str
    prompt_template: str
    transform: Callable[[str], str] | None = None

class PromptChain:
    def __init__(self, client):
        self.client = client
        self.steps: list[ChainStep] = []
        self.checkpoints: dict[str, str] = {}
    
    def add_step(self, name: str, prompt: str, 
                 transform: Callable[[str], str] | None = None) -> "PromptChain":
        self.steps.append(ChainStep(name, prompt, transform))
        return self
    
    async def execute(self, initial_input: str) -> str:
        current = initial_input
        
        for i, step in enumerate(self.steps):
            if step.transform:
                current = step.transform(current)
            
            prompt = step.prompt_template.format(input=current)
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            current = response.choices[0].message.content
            
            self.checkpoints[step.name] = current
        
        return current

async def main():
    chain = PromptChain(client)
    chain.add_step(
        "extract",
        "Extract all names from this text: {input}"
    ).add_step(
        "format",
        "Format these names as a comma-separated list: {input}"
    ).add_step(
        "validate",
        "Verify each name is properly capitalized: {input}"
    )
    
    result = await chain.execute(input_text)
    print(result)

asyncio.run(main())