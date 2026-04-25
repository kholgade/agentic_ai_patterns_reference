import asyncio
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

client = OpenAI(api_key="sk-...")

@dataclass
class ToolResult:
    tool: str
    success: bool
    result: Any
    error: Optional[str] = None

# Define orchestrator tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_articles",
            "description": "Search for relevant articles",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_article_content",
            "description": "Fetch full article content by URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_text",
            "description": "Generate a summary of text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "max_length": {"type": "integer", "default": 100}
                },
                "required": ["text"]
            }
        }
    }
]

# Tool implementations
def search_articles(query: str) -> List[Dict]:
    # Mock search
    return [{"url": f"https://example.com/{i}", "title": f"Result {i}"} 
            for i in range(3)]

def fetch_article_content(url: str) -> str:
    return f"Full content from {url}. This article discusses..."

def summarize_text(text: str, max_length: int = 100) -> str:
    words = text.split()
    return " ".join(words[:max_length]) + "..."

class Orchestrator:
    def __init__(self):
        self.tool_map = {
            "search_articles": search_articles,
            "fetch_article_content": fetch_article_content,
            "summarize_text": summarize_text
        }
    
    def execute_tool(self, name: str, args: dict) -> ToolResult:
        try:
            result = self.tool_map[name](**args)
            return ToolResult(tool=name, success=True, result=result)
        except Exception as e:
            return ToolResult(tool=name, success=False, result=None, error=str(e))
    
    def sequential_workflow(self, steps: List[tuple]) -> List[ToolResult]:
        """Execute tools sequentially, passing output as input"""
        context = {}
        results = []
        
        for tool_name, arg_template in steps:
            args = {k: v.format(**context) if isinstance(v, str) else v 
                   for k, v in arg_template.items()}
            
            result = self.execute_tool(tool_name, args)
            results.append(result)
            
            if not result.success:
                break
            
            # Pass result to context for next step
            context["last_result"] = result.result
            
            if isinstance(result.result, list):
                context["first_item"] = result.result[0]
            elif isinstance(result.result, dict):
                context.update(result.result)
        
        return results
    
    def parallel_workflow(self, tools: List[tuple]) -> List[ToolResult]:
        """Execute independent tools in parallel"""
        def run_tool(tool_name, args):
            return self.execute_tool(tool_name, args)
        
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(run_tool, name, args) 
                     for name, args in tools]
            return [f.result() for f in futures]
    
    def conditional_workflow(self, rules: List, initial_context: dict) -> List[ToolResult]:
        """Execute tools based on conditions"""
        results = []
        context = initial_context
        
        for condition, action in rules:
            if self._evaluate_condition(condition, context):
                result = self.execute_tool(action["tool"], action["args"])
                results.append(result)
                if result.success:
                    context.update({"last_result": result.result})
        
        return results
    
    def _evaluate_condition(self, condition: dict, context: dict) -> bool:
        # Simple condition evaluation
        if "has_key" in condition:
            return condition["has_key"] in context
        if "not_empty" in condition:
            return bool(context.get(condition["not_empty"]))
        return True

# Usage - Sequential: Search → Fetch → Summarize
orchestrator = Orchestrator()
results = orchestrator.sequential_workflow([
    ("search_articles", {"query": "AI trends 2024"}),
    ("fetch_article_content", {"url": "{first_item[url]}"}),
    ("summarize_text", {"text": "{last_result}", "max_length": 50})
])

# Usage - Parallel: Get multiple data sources
results = orchestrator.parallel_workflow([
    ("search_articles", {"query": "weather"}),
    ("search_articles", {"query": "sports"}),
    ("search_articles", {"query": "technology"})
])