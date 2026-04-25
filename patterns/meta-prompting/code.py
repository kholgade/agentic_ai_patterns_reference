import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional

client = instructor.patch(OpenAI())

class PromptAnalysis(BaseModel):
    issues: List[str]
    improvements: List[str]
    refined_prompt: str

class MetaPrompting:
    def __init__(self, base_prompt: str, max_iterations: int = 3):
        self.base_prompt = base_prompt
        self.max_iterations = max_iterations
        self.history: List[dict] = []
    
    def analyze_and_refine(self, task: str, previous_output: str) -> PromptAnalysis:
        analysis_prompt = f"""Analyze this previous attempt at solving the task.
        
Task: {task}

Previous Prompt Used: {self.base_prompt}

Previous Output:
{previous_output}

Provide:
1. Issues or weaknesses in the output
2. Specific improvements for the prompt
3. Refined prompt that addresses these issues"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a prompt engineering expert. Analyze and refine prompts."},
                     {"role": "user", "content": analysis_prompt}],
            response_model=PromptAnalysis
        )
        return response
    
    def execute(self, task: str) -> str:
        current_prompt = self.base_prompt
        
        for i in range(self.max_iterations):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{current_prompt}\n\nTask: {task}"}
                ]
            )
            output = response.choices[0].message.content
            
            if i < self.max_iterations - 1:
                analysis = self.analyze_and_refine(task, output)
                self.history.append({
                    "iteration": i + 1,
                    "prompt": current_prompt,
                    "output": output,
                    "analysis": analysis
                })
                current_prompt = analysis.refined_prompt
            else:
                self.history.append({
                    "iteration": i + 1,
                    "prompt": current_prompt,
                    "output": output
                })
                
        return output

meta_prompter = MetaPrompting(
    base_prompt="Provide a clear, step-by-step explanation of the concept."
)
result = meta_prompter.execute("Explain how neural networks learn through backpropagation")