from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum
from openai import AsyncOpenAI
import asyncio

class DebateRole(Enum):
    PROPONENT = "proponent"
    SKEPTIC = "skeptic"
    SYNTHESIST = "synthesist"
    MODERATOR = "moderator"

@dataclass
class DebateRound:
    round_number: int
    speaker: str
    content: str
    responds_to: Optional[str] = None

@dataclass
class DebateState:
    topic: str
    rounds: list[DebateRound] = None
    positions: dict[str, str] = None
    
    def __post_init__(self):
        if self.rounds is None:
            self.rounds = []
        if self.positions is None:
            self.positions = {}

class DebateAgent:
    def __init__(self, agent_id: str, role: DebateRole, client: AsyncOpenAI):
        self.agent_id = agent_id
        self.role = role
        self.client = client
    
    def get_system_prompt(self) -> str:
        prompts = {
            DebateRole.PROPONENT: """You are a proponent arguing FOR a position. 
Present strong arguments, address counterarguments, and advocate for your stance.""",
            DebateRole.SKEPTIC: """You are a skeptic challenging arguments.
Identify weaknesses, ask hard questions, and play devil's advocate to strengthen the final position.""",
            DebateRole.SYNTHESIST: """You are a synthesist working to combine insights.
Listen to all arguments, find common ground, and create a balanced synthesis.""",
            DebateRole.MODERATOR: """You are a moderator guiding debate.
Keep discussions focused, ensure all voices heard, and summarize key points."""
        }
        return prompts[self.role]
    
    async def respond(self, state: DebateState, context: str) -> str:
        prompt = f"""{self.get_system_prompt()}

Topic: {state.topic}

Previous positions:
{self._format_positions(state.positions)}

Recent arguments:
{context}

Give your response as {self.role.value}:"""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    def _format_positions(self, positions: dict[str, str]) -> str:
        return "\n".join([f"- {k}: {v}" for k, v in positions.items()])

class DebateModerator:
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.agents: dict[DebateRole, DebateAgent] = {}
    
    def add_agent(self, role: DebateRole):
        self.agents[role] = DebateAgent(
            agent_id=role.value,
            role=role,
            client=self.client
        )
    
    async def run_debate(self, topic: str, num_rounds: int = 3) -> str:
        state = DebateState(topic=topic)
        
        initial_positions = {}
        for role in [DebateRole.PROPONENT, DebateRole.SKEPTIC]:
            pos = await self.agents[role].respond(state, "Present your initial position.")
            initial_positions[role.value] = pos
        state.positions = initial_positions
        
        for round_num in range(num_rounds):
            context = self._build_context(state.rounds)
            
            for role in [DebateRole.PROPONENT, DebateRole.SKEPTIC, DebateRole.SYNTHESIST]:
                if role in self.agents:
                    response = await self.agents[role].respond(state, context)
                    state.rounds.append(DebateRound(
                        round_number=round_num + 1,
                        speaker=role.value,
                        content=response
                    ))
                    state.positions[role.value] = response
        
        return await self._produce_final_synthesis(state)
    
    def _build_context(self, rounds: list[DebateRound]) -> str:
        if not rounds:
            return "No previous arguments."
        return "\n".join([f"Round {r.round_number} - {r.speaker}: {r.content}" for r in rounds[-4:]])
    
    async def _produce_final_synthesis(self, state: DebateState) -> str:
        prompt = f"""Given this debate on "{state.topic}":

{self._build_context(state.rounds)}

Produce a final synthesis that incorporates the best arguments from all sides:"""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

moderator = DebateModerator(client)
moderator.add_agent(DebateRole.PROPONENT)
moderator.add_agent(DebateRole.SKEPTIC)
moderator.add_agent(DebateRole.SYNTHESIST)

result = await moderator.run_debate("Should we adopt AI-assisted code review?")