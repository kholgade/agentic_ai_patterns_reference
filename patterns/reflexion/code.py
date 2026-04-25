import anthropic
from dataclasses import dataclass, field
from typing import Literal
from collections import deque

@dataclass
class Reflection:
    iteration: int
    original_output: str
    criticism: str
    reflection_summary: str
    improved_output: str | None = None

class ReflexionAgent:
    def __init__(
        self,
        max_iterations: int = 5,
        reflection_memory_size: int = 10
    ):
        self.client = anthropic.Anthropic()
        self.max_iterations = max_iterations
        self.reflection_memory: deque[Reflection] = deque(maxlen=reflection_memory_size)
        
    def actor_generate(
        self,
        task: str,
        context: str = "",
        reflection_history: str = ""
    ) -> str:
        """Actor generates response to the task."""
        
        context_prompt = f"\n\nContext:\n{context}" if context else ""
        reflection_prompt = f"\n\nPrevious reflections to learn from:\n{reflection_history}" if reflection_history else ""
        
        prompt = f"""You are a helpful AI assistant. Complete the following task:

Task: {task}{context_prompt}{reflection_prompt}

Provide your best response:"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def critic_evaluate(
        self,
        task: str,
        output: str,
        criteria: str = ""
    ) -> str:
        """Critic evaluates the output against criteria and task requirements."""
        
        criteria_prompt = f"\n\nEvaluation criteria:\n{criteria}" if criteria else ""
        
        prompt = f"""You are a critical evaluator reviewing AI outputs.

Task: {task}

Output to evaluate:
{output}

{criteria_prompt}

Provide a detailed critique covering:
1. What is done well?
2. What issues or weaknesses exist?
3. How could this be improved?

Be specific and constructive in your feedback."""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def reflector_synthesize(
        self,
        criticism: str,
        past_reflections: str = ""
    ) -> str:
        """Reflector synthesizes lessons from criticism."""
        
        past_prompt = f"\n\nPast reflections:\n{past_reflections}" if past_reflections else ""
        
        prompt = f"""You synthesize lessons from criticism to improve future outputs.

Recent criticism:
{criticism}

{past_prompt}

Create a concise summary of:
1. Key issues identified
2. Actions to take to address these issues
3. General principles to remember

Keep this focused and actionable."""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def check_completion(
        self,
        task: str,
        output: str
    ) -> tuple[bool, str]:
        """Check if the output satisfies the task requirements."""
        
        prompt = f"""Evaluate if this output successfully completes the task.

Task: {task}

Output:
{output}

Is this task complete? Provide:
- Status: COMPLETE or INCOMPLETE
- Reason: Brief explanation
- Remaining issues (if any):"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = response.content[0].text
        
        is_complete = "COMPLETE" in result.upper()
        reason = result
        
        return is_complete, reason
    
    def solve(
        self,
        task: str,
        criteria: str = "",
        context: str = ""
    ) -> tuple[str, list[Reflection]]:
        """
        Solve a task using Reflexion with iterative improvement.
        
        Args:
            task: The task to complete
            criteria: Evaluation criteria for the critic
            context: Additional context for the task
            
        Returns:
            Tuple of (final_output, list of reflections)
        """
        
        current_output = ""
        reflections = []
        
        for iteration in range(self.max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            reflection_history = self._build_reflection_history()
            
            if iteration == 0:
                current_output = self.actor_generate(task, context, "")
            else:
                current_output = self.actor_generate(
                    task,
                    context,
                    reflection_history + f"\n\nCurrent task output to improve:\n{current_output}"
                )
            
            print(f"Actor output (first 200 chars): {current_output[:200]}...")
            
            is_complete, reason = self.check_completion(task, current_output)
            
            if is_complete:
                print(f"Task marked complete: {reason}")
                break
            
            criticism = self.critic_evaluate(task, current_output, criteria)
            print(f"Critic feedback: {criticism[:200]}...")
            
            past_reflections = "\n".join([
                f"Iteration {r.iteration}: {r.reflection_summary}"
                for r in reflections
            ])
            
            reflection_summary = self.reflector_synthesize(criticism, past_reflections)
            print(f"Reflection: {reflection_summary[:200]}...")
            
            reflection = Reflection(
                iteration=iteration + 1,
                original_output=current_output,
                criticism=criticism,
                reflection_summary=reflection_summary
            )
            reflections.append(reflection)
        
        return current_output, reflections
    
    def _build_reflection_history(self) -> str:
        if not self.reflection_memory:
            return ""
        
        history = "=== LEARNED FROM PAST ITERATIONS ===\n"
        for ref in list(self.reflection_memory):
            history += f"\n{chr(10).join([
                f"Iteration {ref.iteration}:",
                f"Issue: {ref.criticism[:200]}...",
                f"Learning: {ref.reflection_summary[:200]}...",
                "---"
            ])}\n"
        
        return history


# Example usage
agent = ReflexionAgent(max_iterations=3)

task = """Write a Python function that:
1. Takes a list of numbers
2. Returns the median value
3. Handles edge cases (empty list, single element, even length)
4. Includes proper documentation
5. Has type hints"""

criteria = """- Function correctness
- Edge case handling
- Code quality and style
- Documentation completeness"""

result, reflections = agent.solve(task, criteria)

print("\n" + "=" * 50)
print("FINAL OUTPUT:")
print(result)