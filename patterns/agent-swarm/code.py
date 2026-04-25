import asyncio
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import time

class AgentState(Enum):
    EXPLORING = "exploring"
    COMMUNICATING = "communicating"
    EVALUATING = "evaluating"
    RESTING = "resting"

@dataclass
class Pheromone:
    strength: float
    agent_id: str
    content: Any
    timestamp: float

@dataclass
class Agent:
    id: str
    capability: str
    state: AgentState = AgentState.EXPLORING
    memory: list[Any] = field(default_factory=list)
    neighbors: list[str] = field(default_factory=list)

class AgentSwarm:
    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.pheromones: list[Pheromone] = []
        self.shared_memory: dict[str, Any] = {}
        self.min_pheromone_strength = 0.1
        self.pheromone_decay = 0.95
    
    def add_agent(self, agent: Agent):
        self.agents[agent.id] = agent
    
    def _discover_neighbors(self, agent: Agent):
        agent.neighbors = random.sample(
            list(self.agents.keys()), 
            min(3, len(self.agents) - 1)
    
    def _deposit_pheromone(self, agent_id: str, content: Any):
        pheromone = Pheromone(
            strength=1.0,
            agent_id=agent_id,
            content=content,
            timestamp=time.time()
        )
        self.pheromones.append(pheromone)
    
    def _sense_pheromones(self, agent: Agent) -> list[Pheromone]:
        self._decay_pheromones()
        relevant = [
            p for p in self.pheromones 
            if p.strength > self.min_pheromone_strength
        ]
        return sorted(relevant, key=lambda p: p.strength, reverse=True)[:5]
    
    def _decay_pheromones(self):
        for p in self.pheromones:
            p.strength *= self.pheromone_decay
        self.pheromones = [p for p in self.pheromones if p.strength > 0.01]
    
    async def run_agent(self, agent: Agent, problem: str, max_iterations: int = 10):
        for iteration in range(max_iterations):
            agent.state = AgentState.EXPLORING
            self._discover_neighbors(agent)
            
            local_result = await self._explore(agent, problem)
            agent.memory.append(local_result)
            
            agent.state = AgentState.COMMUNICATING
            self._deposit_pheromone(agent.id, local_result)
            
            nearby_pheromones = self._sense_pheromones(agent)
            for pheromone in nearby_pheromones:
                if pheromone.agent_id not in agent.neighbors:
                    agent.memory.append(pheromone.content)
            
            agent.state = AgentState.EVALUATING
            best_solution = await self._evaluate_and_merge(agent)
            
            if await self._check_convergence(agent):
                break
            
            agent.state = AgentState.RESTING
            await asyncio.sleep(0.1)
        
        return agent.memory[-1] if agent.memory else None
    
    async def _explore(self, agent: Agent, problem: str) -> Any:
        return f"Agent {agent.id} explored: {problem[:20]}..."
    
    async def _evaluate_and_merge(self, agent: Agent) -> Any:
        return agent.memory[-1]
    
    async def _check_convergence(self, agent: Agent) -> bool:
        return len(agent.memory) >= 3
    
    async def solve(self, problem: str, num_agents: int = 5) -> Any:
        tasks = [
            self.run_agent(self.agents[f"agent_{i}"], problem)
            for i in range(num_agents)
            if f"agent_{i}" in self.agents
        ]
        
        results = await asyncio.gather(*tasks)
        valid_results = [r for r in results if r is not None]
        
        return self._aggregate_results(valid_results)
    
    def _aggregate_results(self, results: list[Any]) -> Any:
        return f"Aggregated {len(results)} solutions from swarm"

swarm = AgentSwarm()
for i in range(5):
    swarm.add_agent(Agent(id=f"agent_{i}", capability=f"skill_{i}"))

result = await swarm.solve("Optimize this routing problem")