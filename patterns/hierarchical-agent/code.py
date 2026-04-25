from openai import OpenAI
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

client = OpenAI(api_key="sk-...")

class AgentRole(Enum):
    GENERALIST = "generalist"
    CODER = "coder"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"

@dataclass
class SubAgent:
    role: AgentRole
    system_prompt: str
    tools: List[Dict] = field(default_factory=list)
    
    def get_system_prompt(self) -> str:
        return self.system_prompt

class HierarchicalAgent:
    def __init__(self):
        self.agents = self._create_agents()
        self.parent_prompt = self._create_parent_prompt()
    
    def _create_agents(self) -> Dict[AgentRole, SubAgent]:
        return {
            AgentRole.CODER: SubAgent(
                role=AgentRole.CODER,
                system_prompt="""You are an expert Python developer.
                Write clean, efficient, well-documented code.
                Always handle errors appropriately.
                Return code with brief explanation."""
            ),
            AgentRole.RESEARCHER: SubAgent(
                role=AgentRole.RESEARCHER,
                system_prompt="""You are a research assistant.
                Find accurate, up-to-date information.
                Cite sources when possible.
                Summarize findings clearly."""
            ),
            AgentRole.ANALYST: SubAgent(
                role=AgentRole.ANALYST,
                system_prompt="""You are a data analyst.
                Analyze data thoroughly.
                Provide insights and recommendations.
                Use clear visualizations when helpful."""
            ),
            AgentRole.WRITER: SubAgent(
                role=AgentRole.WRITER,
                system_prompt="""You are a technical writer.
                Write clear, concise content.
                Adapt tone to audience.
                Structure information logically."""
            )
        }
    
    def _create_parent_prompt(self) -> str:
        return """You are a supervisor agent that coordinates sub-agents.
        
Available sub-agents:
- coder: For writing or debugging code
- researcher: For finding information
- analyst: For data analysis
- writer: For creating content

For each task:
1. Analyze what subtasks are needed
2. Assign each subtask to appropriate sub-agent
3. Review results
4. Synthesize final response

If only one sub-agent needed, assign directly.
If multiple sub-agents needed, coordinate them.
Always provide final cohesive response to user."""
    
    def decompose_task(self, task: str) -> List[Dict]:
        """Use LLM to decompose task into subtasks"""
        prompt = f"""Decompose this task into subtasks for specialized agents.
        Task: {task}
        
        Return JSON array of objects with:
        - subtask: description of what to do
        - agent_type: "coder", "researcher", "analyst", or "writer"
        - depends_on: subtask this depends on (null if none)
        
        Return only JSON, no other text."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return [{"subtask": task, "agent_type": "generalist", "depends_on": None}]
    
    def execute_subtask(self, agent_type: str, subtask: str) -> str:
        """Execute a single subtask with appropriate sub-agent"""
        role = AgentRole(agent_type) if agent_type in [r.value for r in AgentRole] else AgentRole.GENERALIST
        agent = self.agents.get(role, SubAgent(AgentRole.GENERALIST, "You are a helpful assistant."))
        
        messages = [
            {"role": "system", "content": agent.system_prompt},
            {"role": "user", "content": subtask}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    def execute_subtasks_parallel(self, subtasks: List[Dict]) -> List[Dict]:
        """Execute independent subtasks in parallel"""
        import concurrent.futures
        
        results = []
        for subtask in subtasks:
            result = self.execute_subtask(subtask["agent_type"], subtask["subtask"])
            results.append({
                "subtask": subtask["subtask"],
                "agent_type": subtask["agent_type"],
                "result": result
            })
        
        return results
    
    def synthesize(self, results: List[Dict], original_task: str) -> str:
        """Combine sub-agent results into final response"""
        combined = "\n\n".join([
            f"Subtask: {r['subtask']}\nResult: {r['result']}"
            for r in results
        ])
        
        prompt = f"""Combine these subtask results into a cohesive response.
        
Original task: {original_task}

Results:
{combined}

Provide a unified final response that addresses the original task."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    def process(self, task: str) -> str:
        """Main entry point - decompose, execute, synthesize"""
        # Step 1: Decompose
        subtasks = self.decompose_task(task)
        
        # Step 2: Execute
        if len(subtasks) == 1:
            # Single subtask - direct execution
            result = self.execute_subtask(
                subtasks[0]["agent_type"], 
                subtasks[0]["subtask"]
            )
            return result
        else:
            # Multiple subtasks - execute and synthesize
            results = self.execute_subtasks_parallel(subtasks)
            return self.synthesize(results, task)


# Usage
agent = HierarchicalAgent()

# Single sub-task
result = agent.process("Write a function to calculate fibonacci")
# → Uses CODER agent directly

# Multi sub-task
result = agent.process("""
Create a report on AI trends:
1. Find latest developments in LLM research
2. Analyze market growth data
3. Write executive summary
""")
# → Uses RESEARCHER, ANALYST, WRITER agents
# → Synthesizes results into final report