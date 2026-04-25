import anthropic
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class PlanStep:
    step_number: int
    name: str
    description: str
    status: Literal["pending", "in_progress", "completed", "skipped"] = "pending"
    output: str | None = None
    dependencies: list[int] = field(default_factory=list)

@dataclass
class Plan:
    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

class PlanAndSolve:
    def __init__(self):
        self.client = anthropic.Anthropic()
        
    def create_plan(self, task: str, context: str = "") -> Plan:
        """Phase 1: Create a detailed plan for the task."""
        
        context_prompt = f"\n\nAdditional context:\n{context}" if context else ""
        
        planning_prompt = f"""You are a strategic planner. Break down this task into clear, executable steps.

Task: {task}{context_prompt}

Create a detailed plan that:
1. Identifies all necessary steps
2. Specifies the order (dependencies)
3. Defines what each step should accomplish
4. Includes validation/checkpoint opportunities

Format your plan as:
STEP [N]: [Step Name]
Description: [What to do]
Dependencies: [List any prerequisite step numbers, or "None" if none]
"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": planning_prompt}]
        )
        
        plan_text = response.content[0].text
        steps = self._parse_plan(plan_text)
        
        return Plan(goal=task, steps=steps)
    
    def _parse_plan(self, plan_text: str) -> list[PlanStep]:
        """Parse the planning response into structured PlanStep objects."""
        steps = []
        current_step = None
        
        for line in plan_text.split('\n'):
            line = line.strip()
            
            if line.startswith('STEP '):
                if current_step:
                    steps.append(current_step)
                
                parts = line.split(':', 1)
                step_num = int(parts[0].replace('STEP ', '').strip())
                step_name = parts[1].strip() if len(parts) > 1 else f"Step {step_num}"
                
                current_step = PlanStep(
                    step_number=step_num,
                    name=step_name,
                    description=""
                )
            
            elif current_step and line.startswith('Description:'):
                current_step.description = line.replace('Description:', '').strip()
            
            elif current_step and line.startswith('Dependencies:'):
                deps_text = line.replace('Dependencies:', '').strip()
                if deps_text.lower() != 'none' and deps_text:
                    current_step.dependencies = [
                        int(d.strip()) for d in deps_text.split(',')
                        if d.strip().isdigit()
                    ]
        
        if current_step:
            steps.append(current_step)
        
        return steps
    
    def execute_step(
        self,
        step: PlanStep,
        task: str,
        previous_outputs: dict[int, str],
        context: str = ""
    ) -> str:
        """Execute a single plan step."""
        
        context_parts = []
        if context:
            context_parts.append(f"Original task context:\n{context}")
        
        if previous_outputs:
            context_parts.append("Results from previous steps:")
            for step_num, output in previous_outputs.items():
                context_parts.append(f"\nStep {step_num}: {output[:300]}...")
        
        full_context = "\n\n".join(context_parts)
        
        execution_prompt = f"""You are executing a step from a larger plan.

Original Task: {task}

Current Step: {step.name}
Description: {step.description}

{full_context}

Execute this step thoroughly. Provide:
1. Your analysis/work
2. Key findings or results
3. Any outputs to pass to subsequent steps"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": execution_prompt}]
        )
        
        return response.content[0].text
    
    def can_execute(self, step: PlanStep, completed_steps: set[int]) -> bool:
        """Check if all dependencies for a step are satisfied."""
        return all(dep in completed_steps for dep in step.dependencies)
    
    def solve(
        self,
        task: str,
        context: str = "",
        validate_steps: bool = False
    ) -> tuple[str, Plan]:
        """
        Solve a task using Plan and Solve pattern.
        
        Args:
            task: The task to complete
            context: Additional context for the task
            validate_steps: Whether to validate step outputs before proceeding
            
        Returns:
            Tuple of (final_output, plan_object)
        """
        
        plan = self.create_plan(task, context)
        
        if not plan.steps:
            return "Failed to create plan", plan
        
        completed_outputs: dict[int, str] = {}
        completed_steps: set[int] = set()
        
        remaining_steps = list(plan.steps)
        max_iterations = len(plan.steps) * 2
        iteration = 0
        
        while remaining_steps and iteration < max_iterations:
            iteration += 1
            
            for step in remaining_steps:
                if not self.can_execute(step, completed_steps):
                    continue
                
                step.status = "in_progress"
                
                output = self.execute_step(
                    step, task, completed_outputs, context
                )
                
                if validate_steps:
                    is_valid = self._validate_step(step, output)
                    if not is_valid:
                        step.status = "pending"
                        continue
                
                step.output = output
                step.status = "completed"
                completed_outputs[step.step_number] = output
                completed_steps.add(step.step_number)
                remaining_steps.remove(step)
        
        final_output = self._synthesize_results(plan)
        
        return final_output, plan
    
    def _validate_step(self, step: PlanStep, output: str) -> bool:
        """Validate that a step produced adequate output."""
        
        validation_prompt = f"""Validate this step's output.

Step: {step.name}
Description: {step.description}

Output:
{output}

Is this step complete and satisfactory? Answer YES or NO with brief justification."""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=128,
            messages=[{"role": "user", "content": validation_prompt}]
        )
        
        return "YES" in response.content[0].text.upper()
    
    def _synthesize_results(self, plan: Plan) -> str:
        """Synthesize final output from all step results."""
        
        steps_text = []
        for step in plan.steps:
            if step.output:
                steps_text.append(f"## Step {step.step_number}: {step.name}\n\n{step.output}")
        
        synthesis_prompt = f"""Synthesize results from all steps into a cohesive final output.

Original Task: {plan.goal}

{'=' * 60}
{chr(10).join(steps_text)}
{'=' * 60}

Provide the final synthesized output that addresses the original task."""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        
        return response.content[0].text


# Example usage
ps = PlanAndSolve()

task = """Create a competitive analysis for a new coffee shop opening
in an urban neighborhood. Include market positioning, pricing strategy,
and a 6-month marketing plan."""

context = """The coffee shop will be located in a mid-size urban area with
moderate foot traffic. Target customers are professionals aged 25-45.
Budget is limited for marketing."""

final_output, plan = ps.solve(task, context)

print("=" * 60)
print("FINAL OUTPUT:")
print(final_output)

print("\n" + "=" * 60)
print("PLAN STRUCTURE:")
for step in plan.steps:
    print(f"  Step {step.step_number}: {step.name} [{step.status}]")