from typing import Any, Protocol, Optional
from dataclasses import dataclass, field
from enum import Enum
from openai import AsyncOpenAI
import asyncio

class WorkerStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class WorkerState:
    name: str
    status: WorkerStatus = WorkerStatus.IDLE
    current_task: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None

@dataclass
class Task:
    id: str
    description: str
    assigned_worker: Optional[str] = None
    status: str = "pending"
    result: Optional[str] = None

class WorkerAgent(Protocol):
    async def execute(self, task: Task) -> str:
        ...

class Supervisor:
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.workers: dict[str, WorkerAgent] = {}
        self.worker_states: dict[str, WorkerState] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: dict[str, Task] = {}
        self.max_concurrent = 3
    
    def register_worker(self, name: str, worker: WorkerAgent):
        self.workers[name] = worker
        self.worker_states[name] = WorkerState(name=name)
    
    async def submit_task(self, task: Task):
        await self.task_queue.put(task)
    
    async def assign_task(self, task: Task) -> Optional[str]:
        prompt = f"""Given this task: {task.description}
        
Available workers and their current states:
{self._get_worker_status_summary()}

Select the best worker. Return only the worker name."""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        worker_name = response.choices[0].message.content.strip()
        if worker_name in self.workers:
            return worker_name
        return list(self.workers.keys())[0]
    
    def _get_worker_status_summary(self) -> str:
        return "\n".join([
            f"- {name}: {state.status.value} (current task: {state.current_task or 'none'})"
            for name, state in self.worker_states.items()
        ])
    
    async def execute_worker_task(self, worker_name: str, task: Task):
        self.worker_states[worker_name].status = WorkerStatus.BUSY
        self.worker_states[worker_name].current_task = task.id
        self.active_tasks[task.id] = task
        
        try:
            worker = self.workers[worker_name]
            result = await worker.execute(task)
            task.result = result
            task.status = "completed"
            self.worker_states[worker_name].result = result
            self.worker_states[worker_name].status = WorkerStatus.COMPLETED
        except Exception as e:
            task.status = "failed"
            self.worker_states[worker_name].error = str(e)
            self.worker_states[worker_name].status = WorkerStatus.FAILED
        finally:
            self.worker_states[worker_name].current_task = None
    
    async def run(self):
        workers_available = asyncio.Semaphore(self.max_concurrent)
        
        async def process_task():
            async with workers_available:
                task = await self.task_queue.get()
                worker_name = await self.assign_task(task)
                task.assigned_worker = worker_name
                await self.execute_worker_task(worker_name, task)
                self.task_queue.task_done()
        
        await asyncio.gather(*[process_task() for _ in range(self.max_concurrent)])
    
    async def get_status(self) -> dict:
        return {
            "workers": {name: state.status.value for name, state in self.worker_states.items()},
            "pending_tasks": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks)
        }

class CodeExpert:
    async def execute(self, task: Task) -> str:
        return f"Code analysis complete for: {task.description}"

class ResearchExpert:
    async def execute(self, task: Task) -> str:
        return f"Research complete for: {task.description}"

supervisor = Supervisor(client)
supervisor.register_worker("code_expert", CodeExpert())
supervisor.register_worker("research_expert", ResearchExpert())