from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from openai import AsyncOpenAI
import asyncio

class Role(Enum):
    EXECUTIVE = "executive"
    MANAGER = "manager"
    TEAM_LEAD = "team_lead"
    WORKER = "worker"

@dataclass
class Task:
    id: str
    description: str
    assignee: Optional[str] = None
    status: str = "pending"
    result: Optional[str] = None
    priority: int = 0

@dataclass
class Agent:
    id: str
    role: Role
    name: str
    reports_to: Optional[str] = None
    team: Optional[str] = None
    capabilities: list[str] = field(default_factory=list)

class HierarchicalTeam:
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.agents: dict[str, Agent] = {}
        self.task_queue: dict[str, list[Task]] = {}
    
    def add_agent(self, agent: Agent):
        self.agents[agent.id] = agent
        self.task_queue[agent.id] = []
    
    def get_reports(self, manager_id: str) -> list[Agent]:
        return [a for a in self.agents.values() if a.reports_to == manager_id]
    
    def get_manager_chain(self, agent_id: str) -> list[Agent]:
        chain = []
        current = self.agents.get(agent_id)
        while current and current.reports_to:
            manager = self.agents.get(current.reports_to)
            if manager:
                chain.append(manager)
                current = manager
            else:
                break
        return chain
    
    async def assign_task(self, task: Task, agent_id: str):
        task.assignee = agent_id
        self.task_queue[agent_id].append(task)
    
    async def execute_task(self, agent_id: str, task: Task) -> str:
        agent = self.agents[agent_id]
        await asyncio.sleep(0.1)
        task.result = f"{agent.name} completed: {task.description}"
        task.status = "completed"
        return task.result
    
    async def process_team(self, agent_id: str) -> list[str]:
        results = []
        while self.task_queue[agent_id]:
            task = self.task_queue[agent_id].pop(0)
            result = await self.execute_task(agent_id, task)
            results.append(result)
        return results
    
    async def execute_hierarchical(self, directive: str):
        executive = next((a for a in self.agents.values() if a.role == Role.EXECUTIVE), None)
        if not executive:
            return "No executive agent configured"
        
        executive_tasks = [
            Task(id="t1", description=f"Plan: {directive}", priority=1),
            Task(id="t2", description=f"Allocate resources for: {directive}", priority=2)
        ]
        
        for task in executive_tasks:
            await self.assign_task(task, executive.id)
        
        await self.process_team(executive.id)
        
        for manager in self.get_reports(executive.id):
            manager_tasks = [
                Task(id=f"{manager.id}_t1", description=f"Coordinate: {directive}", priority=1)
            ]
            for task in manager_tasks:
                await self.assign_task(task, manager.id)
            await self.process_team(manager.id)
            
            for worker in self.get_reports(manager.id):
                worker_tasks = [
                    Task(id=f"{worker.id}_t1", description=f"Execute: {directive}", priority=1)
                ]
                for task in worker_tasks:
                    await self.assign_task(task, worker.id)
                await self.process_team(worker.id)
        
        return f"Completed hierarchical execution of: {directive}"

team = HierarchicalTeam(client)

team.add_agent(Agent(id="exec1", role=Role.EXECUTIVE, name="CEO"))
team.add_agent(Agent(id="mgr1", role=Role.MANAGER, name="VP Engineering", reports_to="exec1"))
team.add_agent(Agent(id="mgr2", role=Role.MANAGER, name="VP Product", reports_to="exec1"))
team.add_agent(Agent(id="lead1", role=Role.TEAM_LEAD, name="Backend Lead", reports_to="mgr1", team="backend"))
team.add_agent(Agent(id="lead2", role=Role.TEAM_LEAD, name="Frontend Lead", reports_to="mgr1", team="frontend"))
team.add_agent(Agent(id="worker1", role=Role.WORKER, name="Dev A", reports_to="lead1"))
team.add_agent(Agent(id="worker2", role=Role.WORKER, name="Dev B", reports_to="lead1"))
team.add_agent(Agent(id="worker3", role=Role.WORKER, name="Dev C", reports_to="lead2"))

result = await team.execute_hierarchical("Build new API endpoint")