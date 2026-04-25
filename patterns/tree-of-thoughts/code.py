import anthropic
from dataclasses import dataclass, field
from typing import Literal
from enum import Enum

class NodeState(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    PRUNED = "pruned"

@dataclass
class ThoughtNode:
    id: str
    content: str
    parent_id: str | None
    children: list[str] = field(default_factory=list)
    state: NodeState = NodeState.PENDING
    score: float | None = None
    depth: int = 0

class TreeOfThoughts:
    def __init__(self, max_depth: int = 3, maxBranches: int = 3):
        self.max_depth = max_depth
        self.maxBranches = maxBranches
        self.nodes: dict[str, ThoughtNode] = {}
        self.client = anthropic.Anthropic()
        self.node_counter = 0
        
    def create_node(self, content: str, parent_id: str | None = None) -> str:
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        
        depth = 0
        if parent_id and parent_id in self.nodes:
            depth = self.nodes[parent_id].depth + 1
            
        self.nodes[node_id] = ThoughtNode(
            id=node_id,
            content=content,
            parent_id=parent_id,
            depth=depth
        )
        
        if parent_id:
            self.nodes[parent_id].children.append(node_id)
            
        return node_id
    
    def expand_node(self, node_id: str, prompt_template: str) -> list[str]:
        """Expand a node by generating multiple thought branches."""
        node = self.nodes[node_id]
        
        if node.depth >= self.max_depth:
            return []
        
        expansion_prompt = f"""{prompt_template}

Current thought: {node.content}

Generate {self.maxBranches} different approaches or continuations for this thought.
For each, provide:
1. A brief description of the approach
2. The reasoning for why this path might be promising

Format as:
Option 1: [description] -> [reasoning]
Option 2: [description] -> [reasoning]
..."""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": expansion_prompt}]
        )
        
        new_node_ids = []
        lines = response.content[0].text.split('\n')
        
        for line in lines:
            if line.startswith('Option '):
                parts = line.split('->', 1)
                if len(parts) == 2:
                    option_id = self.create_node(
                        content=parts[1].strip(),
                        parent_id=node_id
                    )
                    new_node_ids.append(option_id)
                    self.nodes[option_id].state = NodeState.ACTIVE
        
        node.state = NodeState.COMPLETED
        return new_node_ids
    
    def evaluate_node(self, node_id: str, evaluator_prompt: str) -> float:
        """Evaluate the quality of a thought node."""
        node = self.nodes[node_id]
        
        eval_prompt = f"""{evaluator_prompt}

Evaluate this thought on a scale of 1-10:

Thought: {node.content}

Provide only a number from 1 to 10 as your evaluation."""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=64,
            messages=[{"role": "user", "content": eval_prompt}]
        )
        
        try:
            score = float(response.content[0].text.strip().split()[0])
            score = min(10, max(1, score))
        except:
            score = 5.0
            
        node.score = score
        return score
    
    def get_best_path(self) -> list[ThoughtNode]:
        """Get the highest-scoring complete path."""
        leaf_nodes = [
            n for n in self.nodes.values()
            if not n.children or n.state == NodeState.PRUNED
        ]
        
        if not leaf_nodes:
            return []
            
        best_leaf = max(leaf_nodes, key=lambda n: n.score or 0)
        
        path = []
        current = best_leaf
        while current:
            path.insert(0, current)
            current = self.nodes[current.parent_id] if current.parent_id else None
            
        return path
    
    def solve(self, problem: str, evaluator_prompt: str) -> str:
        """Solve a problem using Tree of Thoughts."""
        root_id = self.create_node(content=problem)
        
        frontier = [root_id]
        
        while frontier:
            new_frontier = []
            
            for node_id in frontier:
                children = self.expand_node(node_id, evaluator_prompt)
                new_frontier.extend(children)
            
            frontier = new_frontier
        
        path = self.get_best_path()
        
        return "\n".join([
            f"Step {i+1}: {node.content[:100]}..."
            for i, node in enumerate(path)
        ])


# Example usage
tot = TreeOfThoughts(max_depth=3, maxBranches=2)

evaluator = """You are evaluating business strategies.
Rate each approach on: feasibility, impact, and innovation."""

problem = "How can a small bakery increase revenue by 40% in 6 months?"

solution = tot.solve(problem, evaluator)
print(solution)