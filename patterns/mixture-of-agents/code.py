import asyncio
import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

client = instructor.patch(OpenAI())

class AgentConfig(BaseModel):
    name: str
    system_prompt: str
    model: str = "gpt-4o"
    temperature: float = 0.7

class AgentOutput(BaseModel):
    agent_name: str
    content: str
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
    
    @abstractmethod
    async def process(self, input_data: str) -> AgentOutput:
        pass

class LLMAgent(BaseAgent):
    async def process(self, input_data: str) -> AgentOutput:
        response = await client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": input_data}
            ],
            temperature=self.config.temperature
        )
        
        return AgentOutput(
            agent_name=self.config.name,
            content=response.choices[0].message.content,
            metadata={"model": self.config.model}
        )

class ParallelCombiner:
    def __init__(self, agents: List[BaseAgent], merge_prompt: str):
        self.agents = agents
        self.merge_prompt = merge_prompt
    
    async def execute(self, task: str) -> AgentOutput:
        tasks = [agent.process(task) for agent in self.agents]
        outputs = await asyncio.gather(*tasks)
        
        combined_input = self._format_for_combination(outputs)
        
        merger = LLMAgent(AgentConfig(
            name="Merger",
            system_prompt=self.merge_prompt
        ))
        
        result = await merger.process(combined_input)
        return result
    
    def _format_for_combination(self, outputs: List[AgentOutput]) -> str:
        formatted = "\n\n".join([
            f"Agent: {o.agent_name}\nOutput: {o.content}"
            for o in outputs
        ])
        return f"Combine these outputs into a coherent response:\n\n{formatted}"

class SequentialMoA:
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents
    
    async def execute(self, task: str) -> str:
        current_input = task
        
        for agent in self.agents:
            output = await agent.process(current_input)
            current_input = output.content
        
        return current_input

class VotingCombiner:
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents
    
    async def execute(self, task: str, num_samples: int = 3) -> str:
        tasks = []
        for agent in self.agents:
            tasks.extend([agent.process(task) for _ in range(num_samples)])
        
        outputs = await asyncio.gather(*tasks)
        
        vote_input = f"Select the best response from these options:\n\n" + \
                    "\n\n".join([f"{i+1}. {o.content}" for i, o in enumerate(outputs)])
        
        selector = LLMAgent(AgentConfig(
            name="Selector",
            system_prompt="Select the most accurate and helpful response. Just output the selected response."
        ))
        
        result = await selector.process(vote_input)
        return result.content

async def mixture_example():
    research_agent = LLMAgent(AgentConfig(
        name="Research",
        system_prompt="You are a research expert. Find accurate information."
    ))
    
    analysis_agent = LLMAgent(AgentConfig(
        name="Analysis",
        system_prompt="You are a data analyst. Analyze information critically."
    ))
    
    creative_agent = LLMAgent(AgentConfig(
        name="Creative",
        system_prompt="You are a creative thinker. Generate innovative ideas."
    ))
    
    agents = [research_agent, analysis_agent, creative_agent]
    
    combiner = ParallelCombiner(
        agents=agents,
        merge_prompt="Combine all agent outputs into a single, comprehensive response."
    )
    
    result = await combiner.execute("Explain neural networks")
    return result

async def sequential_moa_example():
    agents = [
        LLMAgent(AgentConfig(
            name="Researcher",
            system_prompt="Research the topic thoroughly."
        )),
        LLMAgent(AgentConfig(
            name="Analyzer",
            system_prompt="Analyze the key points from the research."
        )),
        LLMAgent(AgentConfig(
            name="Writer",
            system_prompt="Write a clear, engaging summary."
        ))
    ]
    
    moa = SequentialMoA(agents)
    return await moa.execute("quantum computing")