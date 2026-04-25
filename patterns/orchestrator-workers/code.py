from typing import Any, Protocol
from dataclasses import dataclass, field
from openai import AsyncOpenAI
import asyncio

@dataclass
class Task:
    id: str
    description: str
    worker_type: str
    priority: int = 0
    result: str | None = None
    status: str = "pending"
    error: str | None = None

class Worker(Protocol):
    async def execute(self, task: Task) -> str:
        ...

class Orchestrator:
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.workers: dict[str, Worker] = {}
        self.max_workers = 5
        self.task_timeout = 60
    
    def register_worker(self, worker_type: str, worker: Worker):
        self.workers[worker_type] = worker
    
    async def decompose(self, input_text: str) -> list[Task]:
        prompt = f"""Break down this request into independent subtasks.
Return format: task_id|description|worker_type|priority

Request: {input_text}

Consider what specialized workers would be needed."""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        tasks = []
        for i, line in enumerate(response.choices[0].message.content.split("\n")):
            if line.strip():
                task_id, desc, worker_type, priority = line.split("|")
                tasks.append(Task(
                    id=task_id.strip(),
                    description=desc.strip(),
                    worker_type=worker_type.strip(),
                    priority=int(priority.strip())
                ))
        
        return sorted(tasks, key=lambda t: t.priority, reverse=True)
    
    async def execute_task(self, task: Task) -> Task:
        if task.worker_type not in self.workers:
            task.status = "error"
            task.error = f"Unknown worker: {task.worker_type}"
            return task
        
        try:
            task.result = await asyncio.wait_for(
                self.workers[task.worker_type].execute(task),
                timeout=self.task_timeout
            )
            task.status = "success"
        except asyncio.TimeoutError:
            task.status = "timeout"
            task.error = f"Task exceeded {self.task_timeout}s"
        except Exception as e:
            task.status = "error"
            task.error = str(e)
        
        return task
    
    async def execute(self, input_text: str) -> str:
        tasks = await self.decompose(input_text)
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def bounded_execute(task: Task):
            async with semaphore:
                return await self.execute_task(task)
        
        results = await asyncio.gather(*[
            bounded_execute(t) for t in tasks
        ], return_exceptions=True)
        
        successful = [r for r in results if isinstance(r, Task) and r.status == "success"]
        failed = [r for r in results if isinstance(r, Task) and r.status != "success"]
        
        if not successful:
            return "All tasks failed"
        
        aggregation_prompt = "Combine these task results into a unified response:\n\n"
        aggregation_prompt += "\n\n".join([
            f"Task {t.id}: {t.result}" for t in successful
        ])
        
        final_response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": aggregation_prompt}]
        )
        
        return final_response.choices[0].message.content

class WebSearchWorker:
    async def execute(self, task: Task) -> str:
        # Specialized search implementation
        return f"Search results for: {task.description}"

class DatabaseWorker:
    async def execute(self, task: Task) -> str:
        # Database query implementation  
        return f"Database results for: {task.description}"

# Usage
orchestrator = Orchestrator(client)
orchestrator.register_worker("search", WebSearchWorker())
orchestrator.register_worker("database", DatabaseWorker())

result = await orchestrator.execute(
    "Research AI trends and check our analytics for relevant metrics"
)