import asyncio
from typing import Any, Optional
from dataclasses import dataclass
from collections import deque

@dataclass
class Task:
    id: str
    payload: Any
    result: Optional[Any] = None
    status: str = "pending"

class RoundRobinAgent:
    def __init__(self, name: str):
        self.name = name
        self.completed_tasks: list[Task] = []
    
    async def process(self, task: Task) -> Task:
        await asyncio.sleep(0.1)
        task.result = f"{self.name} processed: {task.payload}"
        task.status = "completed"
        self.completed_tasks.append(task)
        return task

class RoundRobinScheduler:
    def __init__(self):
        self.agents: deque[RoundRobinAgent] = deque()
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.current_index = 0
    
    def add_agent(self, agent: RoundRobinAgent):
        self.agents.append(agent)
    
    def get_next_agent(self) -> RoundRobinAgent:
        if not self.agents:
            raise RuntimeError("No agents available")
        agent = self.agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.agents)
        return agent
    
    async def submit_task(self, task: Task):
        await self.task_queue.put(task)
    
    async def run(self, max_tasks: Optional[int] = None):
        processed = 0
        
        while max_tasks is None or processed < max_tasks:
            try:
                task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                break
            
            agent = self.get_next_agent()
            await agent.process(task)
            processed += 1
        
        return processed
    
    async def process_tasks(self, payloads: list[Any]) -> list[Task]:
        tasks = [Task(id=f"task_{i}", payload=p) for i, p in enumerate(payloads)]
        
        for task in tasks:
            await self.task_queue.put(task)
        
        await self.run(len(tasks))
        
        return tasks

class IterativeRefiner:
    def __init__(self, agents: list[RoundRobinAgent], iterations: int = 3):
        self.scheduler = RoundRobinScheduler()
        for agent in agents:
            self.scheduler.add_agent(agent)
        self.iterations = iterations
    
    async def refine(self, initial_content: str) -> str:
        current = initial_content
        
        for i in range(self.iterations):
            tasks = await self.scheduler.process_tasks([current])
            if tasks and tasks[0].result:
                current = tasks[0].result
        
        return current

agent_a = RoundRobinAgent("Editor")
agent_b = RoundRobinAgent("Reviewer")
agent_c = RoundRobinAgent("Publisher")

scheduler = RoundRobinScheduler()
scheduler.add_agent(agent_a)
scheduler.add_agent(agent_b)
scheduler.add_agent(agent_c)

tasks = await scheduler.process_tasks(["doc1", "doc2", "doc3", "doc4"])