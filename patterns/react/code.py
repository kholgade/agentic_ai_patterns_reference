import anthropic
import json
from dataclasses import dataclass
from typing import Literal

@dataclass
class ToolResult:
    success: bool
    result: str
    error: str | None = None

def web_search(query: str) -> ToolResult:
    """Simulated web search tool - replace with actual API call"""
    # In production, use Google Serper API, DuckDuckGo, etc.
    return ToolResult(
        success=True,
        result=f"Search results for: {query}\n[Simulated results would appear here]"
    )

def calculator(expression: str) -> ToolResult:
    """Code execution tool for calculations"""
    try:
        result = eval(expression, {"__builtins__": {}})
        return ToolResult(success=True, result=str(result))
    except Exception as e:
        return ToolResult(success=False, result="", error=str(e))

# Registry of available tools
TOOLS = {
    "search": web_search,
    "calculate": calculator,
}

def react(
    question: str,
    max_iterations: int = 10
) -> str:
    """
    Implements ReAct pattern with tool use.
    
    Args:
        question: The question to answer
        max_iterations: Maximum thought-action-observation cycles
    """
    
    client = anthropic.Anthropic()
    
    system_prompt = """You are a helpful assistant that uses the ReAct pattern.
You have access to tools. For each step, output exactly one Thought/Action/Observation block.

Format each iteration as:
THOUGHT: [Your reasoning about what to do next]
ACTION: [tool_name][input for the tool]
OBSERVATION: [Result from the tool]

When you have enough information to answer, output:
FINAL ANSWER: [Your complete answer]

Available tools: search, calculate
"""
    
    messages = [
        {"role": "user", "content": question},
        {"role": "assistant", "content": system_prompt}
    ]
    
    for iteration in range(max_iterations):
        # Get model's next response
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=messages
        )
        
        model_output = response.content[0].text.strip()
        messages.append({"role": "assistant", "content": model_output})
        
        # Check for final answer
        if "FINAL ANSWER:" in model_output:
            return model_output.split("FINAL ANSWER:")[1].strip()
        
        # Parse and execute action
        action_line = [l for l in model_output.split('\n') if l.startswith('ACTION:')]
        if not action_line:
            continue
            
        action_line = action_line[0].replace('ACTION:', '').strip()
        
        # Parse tool call: tool_name[argument]
        if '[' in action_line and action_line.endswith(']'):
            tool_name, arg = action_line[:-1].split('[', 1)
            tool_name = tool_name.strip()
            
            if tool_name in TOOLS:
                result = TOOLS[tool_name](arg)
                observation = f"Result: {result.result}"
                if result.error:
                    observation += f"\nError: {result.error}"
                messages.append({
                    "role": "user",
                    "content": f"OBSERVATION: {observation}"
                })
    
    return "Could not determine answer within iteration limit"


# Example usage
answer = react(
    "If a train travels 120 miles in 2 hours, and then stops for "
    "30 minutes, then travels another 80 miles in 1.5 hours, what is "
    "the average speed in miles per hour?"
)
print(answer)