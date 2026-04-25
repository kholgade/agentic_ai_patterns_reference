from openai import OpenAI
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

client = OpenAI(api_key="sk-...")

@dataclass
class MemoryEntry:
    id: str
    content: str
    metadata: Dict
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)

class LongTermMemory:
    def __init__(
        self,
        collection_name: str = "agent_memory",
        embedding_model: str = "text-embedding-3-small"
    ):
        self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.embedding_model = embedding_model
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )
    
    def embed(self, text: str) -> List[float]:
        response = client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def add(
        self,
        content: str,
        memory_type: str = "general",
        user_id: Optional[str] = None,
        importance: float = 0.5
    ):
        entry_id = f"{memory_type}_{datetime.now().timestamp()}"
        embedding = self.embed(content)
        metadata = {
            "type": memory_type,
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "user_id": user_id or "default"
        }
        
        self.collection.add(
            ids=[entry_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )
        
        return entry_id
    
    def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 5,
        min_importance: float = 0.0
    ) -> List[Dict]:
        query_embedding = self.embed(query)
        
        where = {}
        if user_id:
            where = {"user_id": user_id}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where if where else None,
            include=["documents", "metadatas", "distances"]
        )
        
        memories = []
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            similarity = 1 - distance
            
            if similarity >= min_importance:
                memories.append({
                    "content": doc,
                    "similarity": similarity,
                    "metadata": metadata,
                    "id": results["ids"][0][i]
                })
        
        return memories
    
    def delete(self, memory_id: str):
        self.collection.delete(ids=[memory_id])
    
    def get_recent(self, user_id: str, limit: int = 10) -> List[Dict]:
        results = self.collection.get(
            where={"user_id": user_id},
            limit=limit,
            include=["documents", "metadatas"]
        )
        
        return [
            {"content": doc, "metadata": meta, "id": id_}
            for id_, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            )
        ]
    
    def update_importance(self, memory_id: str, importance: float):
        self.collection.update(
            ids=[memory_id],
            metadatas=[{"importance": importance}]
        )


class RememberingAgent:
    def __init__(
        self,
        system_prompt: str,
        max_memories: int = 5,
        memory_importance_threshold: float = 0.7
    ):
        self.memory = LongTermMemory()
        self.system_prompt = system_prompt
        self.max_memories = max_memories
        self.threshold = memory_importance_threshold
    
    def chat(self, user_id: str, query: str) -> str:
        # Retrieve relevant memories
        memories = self.memory.search(
            query=query,
            user_id=user_id,
            limit=self.max_memories,
            min_importance=self.threshold
        )
        
        # Build context from memories
        context = self._build_context(memories)
        
        # Create prompt with memory
        messages = [
            {"role": "system", "content": f"{self.system_prompt}\n\n{context}"},
            {"role": "user", "content": query}
        ]
        
        # Get response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        answer = response.choices[0].message.content
        
        # Store important interactions
        self._maybe_store_memory(user_id, query, answer)
        
        return answer
    
    def _build_context(self, memories: List[Dict]) -> str:
        if not memories:
            return "No prior context available."
        
        sections = ["Relevant past context:\n"]
        for i, mem in enumerate(memories, 1):
            sections.append(
                f"{i}. {mem['content']} "
                f"(relevance: {mem['similarity']:.2f})"
            )
        
        return "\n".join(sections)
    
    def _maybe_store_memory(self, user_id: str, query: str, answer: str):
        # Store significant interactions
        if len(query) > 50:
            to_store = f"User asked about: {query[:100]}... | Response: {answer[:100]}..."
            self.memory.add(
                content=to_store,
                memory_type="conversation",
                user_id=user_id,
                importance=0.6
            )


# Usage
agent = RememberingAgent(
    system_prompt="You are a helpful assistant that remembers user preferences."
)

# Session 1
agent.chat("user123", "I prefer concise responses and like discussing AI.")
# "Understood! I'll keep my responses concise."

# Session 2 (new conversation)
response = agent.chat("user123", "What was my preference?")
# "You prefer concise responses and like discussing AI."