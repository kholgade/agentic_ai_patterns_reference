import asyncio
from typing import TypeVar, Callable, Iterable
from dataclasses import dataclass
from openai import AsyncOpenAI

T = TypeVar('T')
R = TypeVar('R')

@dataclass
class MapTask:
    input_data: str
    task_id: str

class ParallelMapper:
    def __init__(self, client: AsyncOpenAI, max_concurrency: int = 10):
        self.client = client
        self.semaphore = asyncio.Semaphore(max_concurrency)
    
    async def map_single(self, prompt: str, task: MapTask) -> dict:
        async with self.semaphore:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt.format(task.input_data)}]
            )
            return {
                "task_id": task.task_id,
                "result": response.choices[0].message.content,
                "status": "success"
            }
    
    async def map_reduce(
        self, 
        tasks: Iterable[MapTask], 
        map_prompt: str,
        reduce_prompt: str
    ) -> str:
        map_tasks = [self.map_single(map_prompt, task) for task in tasks]
        map_results = await asyncio.gather(*map_tasks)
        
        combined = "\n\n".join([
            f"Task {r['task_id']}: {r['result']}" 
            for r in map_results
        ])
        
        reduce_response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": reduce_prompt.format(combined)}]
        )
        
        return reduce_response.choices[0].message.content

async def main():
    client = AsyncOpenAI()
    mapper = ParallelMapper(client, max_concurrency=20)
    
    tasks = [
        MapTask(input_data=f"Document {i} content", task_id=f"doc_{i}")
        for i in range(100)
    ]
    
    result = await mapper.map_reduce(
        tasks,
        map_prompt="Summarize this document in 2 sentences: {0}",
        reduce_prompt="Create a composite report from these summaries:\n{0}"
    )