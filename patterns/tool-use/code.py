from openai import OpenAI
from typing import List, Optional
from pydantic import BaseModel, Field
import json

client = OpenAI(api_key="sk-...")

# Define tool schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "fahrenheit"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "Execute Python code and return output",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

# Tool implementations
def get_weather(location: str, unit: str = "fahrenheit") -> dict:
    # Mock weather API
    weather_db = {
        "San Francisco": {"temp": 68, "condition": "foggy"},
        "New York": {"temp": 75, "condition": "sunny"},
        "London": {"temp": 55, "condition": "rainy"}
    }
    return weather_db.get(location, {"temp": "unknown", "condition": "unknown"})

def execute_code(code: str) -> dict:
    import sys
    from io import StringIO
    stdout = StringIO()
    try:
        old_stdout = sys.stdout
        sys.stdout = stdout
        exec(code, {})
        sys.stdout = old_stdout
        return {"output": stdout.getvalue(), "error": None}
    except Exception as e:
        sys.stdout = old_stdout
        return {"output": None, "error": str(e)}

# Tool execution router
def execute_tool(name: str, args: dict) -> dict:
    tool_map = {"get_weather": get_weather, "execute_code": execute_code}
    return tool_map[name](**args)

# Conversation loop
def chat(query: str, messages: Optional[List[dict]] = None) -> str:
    if messages is None:
        messages = [{"role": "user", "content": query}]
    else:
        messages.append({"role": "user", "content": query})
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    # Check for tool calls
    if message.tool_calls:
        messages.append(message.model_dump())
        for call in message.tool_calls:
            result = execute_tool(call.function.name, 
                             json.loads(call.function.arguments))
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result)
            })
        
        # Get final response with tool results
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content
    
    return message.content

# Usage
response = chat("What's the weather in San Francisco?")
print(response)  # "The current weather in San Francisco is foggy at 68°F."