import json
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
from openai import OpenAI

client = OpenAI()

class UserProfile(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    roles: List[str] = Field(default_factory=list)
    active: bool = Field(default=True)

def generate_structured_output(prompt: str, schema: type[BaseModel]) -> BaseModel:
    """Generate structured output using OpenAI's structured outputs feature."""
    
    system_prompt = f"""You are a data extraction assistant. 
    Output ONLY valid JSON that matches this schema:
    {schema.model_json_schema()}
    Do not include any explanation or markdown. Only output valid JSON."""
    
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=2000
    )
    
    try:
        return schema.model_validate_json(response.choices[0].message.content)
    except ValidationError as e:
        raise ValueError(f"Output does not match schema: {e}")

# Example: Extract user data from unstructured text
unstructured_text = """
John Doe can be reached at john.doe@example.com. 
His employee ID is emp-12345. He works as a Senior Engineer 
and has access to admin systems.
"""

try:
    profile = generate_structured_output(
        f"Extract user information: {unstructured_text}",
        UserProfile
    )
    print(profile.model_dump())
except ValueError as e:
    print(f"Error: {e}")