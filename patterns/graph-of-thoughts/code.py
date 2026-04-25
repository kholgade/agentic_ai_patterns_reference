import anthropic
from dataclasses import dataclass, field
from typing import Literal
from enum import Enum
from collections import defaultdict

class NodeType(Enum):
    GENERATOR = "generator"
    AGGREGATOR = "aggregator"
    CRITIC = "critic"
    FINAL = "final"

@dataclass
class GraphNode:
    id: str
    node_type: NodeType
    content: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    score: float | None = None
    metadata: dict = field(default_factory=dict)

class GraphOfThoughts:
    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[tuple[str, str]] = []
        self.client = anthropic.Anthropic()
        self.node_counter = 0
        
    def create_node(
        self,
        node_type: NodeType,
        content: str,
        inputs: list[str] = None
    ) -> str:
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        
        node = GraphNode(
            id=node_id,
            node_type=node_type,
            content=content,
            inputs=inputs or []
        )
        
        self.nodes[node_id] = node
        
        for input_id in node.inputs:
            self.nodes[input_id].outputs.append(node_id)
            
        return node_id
    
    def get_generators(self) -> list[GraphNode]:
        return [n for n in self.nodes.values() if n.node_type == NodeType.GENERATOR]
    
    def get_ready_nodes(self) -> list[GraphNode]:
        """Get nodes whose inputs have all been processed."""
        ready = []
        for node in self.nodes.values():
            if node.content or node.node_type == NodeType.GENERATOR:
                continue
            if all(
                self.nodes[inp].content 
                for inp in node.inputs
            ):
                ready.append(node)
        return ready
    
    def process_generator(self, node: GraphNode, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": f"{prompt}\n\n{node.metadata.get('source', 'Generate insight')}: {node.content}"}]
        )
        return response.content[0].text
    
    def process_aggregator(self, node: GraphNode, prompt: str) -> str:
        inputs_content = []
        for input_id in node.inputs:
            input_node = self.nodes[input_id]
            inputs_content.append(f"[{input_node.metadata.get('label', 'Input')}]:\n{input_node.content}")
        
        aggregation_prompt = f"""{prompt}

Combine these inputs into a coherent synthesis:

{'=' * 50}
{chr(10).join(inputs_content)}
{'=' * 50}

Synthesis:"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": aggregation_prompt}]
        )
        return response.content[0].text
    
    def process_critic(self, node: GraphNode, evaluation_criteria: str) -> float:
        input_content = ""
        for input_id in node.inputs:
            input_content += f"\n{self.nodes[input_id].content}"
        
        eval_prompt = f"""{evaluation_criteria}

Evaluate the following on a scale of 1-10:

{input_content}

Provide only a number and brief justification."""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=128,
            messages=[{"role": "user", "content": eval_prompt}]
        )
        
        try:
            score = float(response.content[0].text.split()[0])
            score = min(10, max(1, score))
        except:
            score = 5.0
            
        node.score = score
        return score
    
    def add_edge(self, from_id: str, to_id: str):
        self.edges.append((from_id, to_id))
        if to_id in self.nodes:
            self.nodes[to_id].inputs.append(from_id)
        if from_id in self.nodes:
            self.nodes[from_id].outputs.append(to_id)
    
    def solve(
        self,
        sources: list[dict],
        prompt: str,
        evaluation_criteria: str,
        max_iterations: int = 10
    ) -> str:
        # Create generator nodes from sources
        for i, source in enumerate(sources):
            self.create_node(
                NodeType.GENERATOR,
                content=source.get("content", ""),
                inputs=[]
            )
            self.nodes[f"node_{i}"].metadata["source"] = source.get("name", f"Source {i}")
            self.nodes[f"node_{i}"].metadata["label"] = source.get("name", f"Source {i}")
        
        # Create aggregation and critic nodes based on graph design
        generators = self.get_generators()
        if len(generators) > 1:
            # Create first-level aggregator
            gen_ids = [g.id for g in generators]
            agg1_id = self.create_node(
                NodeType.AGGREGATOR,
                content="",
                inputs=gen_ids
            )
            
            # Create critic
            critic_id = self.create_node(
                NodeType.CRITIC,
                content="",
                inputs=[agg1_id]
            )
            self.nodes[critic_id].metadata["evaluates"] = agg1_id
        
        # Process nodes iteratively
        for iteration in range(max_iterations):
            ready_nodes = self.get_ready_nodes()
            
            for node in ready_nodes:
                if node.content:
                    continue
                    
                if node.node_type == NodeType.GENERATOR:
                    node.content = self.process_generator(node, prompt)
                elif node.node_type == NodeType.AGGREGATOR:
                    node.content = self.process_aggregator(node, prompt)
                elif node.node_type == NodeType.CRITIC:
                    node.score = self.process_critic(node, evaluation_criteria)
                    
                    # If score is low, create refined version
                    if node.score and node.score < 6:
                        refined_id = self.create_node(
                            NodeType.GENERATOR,
                            content=f"Refine based on score {node.score}: {node.metadata.get('to_refine', '')}",
                            inputs=node.inputs
                        )
                        self.nodes[refined_id].metadata["is_refinement"] = True
                        self.add_edge(refined_id, node.id)
        
        # Find final output
        final_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.FINAL]
        if not final_nodes:
            # Return the highest-scoring content
            scored = [n for n in self.nodes.values() if n.score is not None]
            if scored:
                return max(scored, key=lambda n: n.score).content
            
        return final_nodes[0].content if final_nodes else ""


# Example usage
sources = [
    {"name": "Financial Report", "content": "Revenue increased 15% YoY, but customer acquisition costs rose 20%"},
    {"name": "Customer Survey", "content": "85% satisfaction rate, but common complaint is about slow customer support"},
    {"name": "Market Analysis", "content": "Competitor X launched similar product at 10% lower price point"},
]

prompt = """Analyze this business data and identify key insights and potential concerns."""

criteria = """Evaluate based on:
- Completeness of analysis
- Actionability of recommendations
- Risk identification"""

got = GraphOfThoughts()
result = got.solve(sources, prompt, criteria)
print(result)