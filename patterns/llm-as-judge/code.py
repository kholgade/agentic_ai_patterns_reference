from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

client = OpenAI()

class QualityDimension(str, Enum):
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COHERENCE = "coherence"
    HELPFULNESS = "helpfulness"
    SAFETY = "safety"

class EvaluationScore(BaseModel):
    dimension: QualityDimension
    score: int = Field(..., ge=1, le=10)
    reasoning: str

class JudgeResult(BaseModel):
    overall_score: int = Field(..., ge=1, le=10)
    dimension_scores: List[EvaluationScore]
    summary: str
    improvement_suggestions: List[str] = Field(default_factory=list)

def create_judge_prompt(
    evaluee_output: str,
    criteria: str,
    context: Optional[str] = None,
    with_reasoning: bool = True
) -> str:
    """Create a detailed judge prompt with evaluation criteria."""
    
    reasoning_instruction = (
        "Before scoring, provide step-by-step reasoning for your evaluation."
        if with_reasoning else ""
    )
    
    return f"""You are an expert evaluator judging AI system outputs.

## Output to Evaluate:
{evaluee_output}

## Evaluation Context:
{context or "No additional context provided."}

## Evaluation Criteria:
{criteria}

{reasoning_instruction}

## Scoring Rubric:
- 1-3: Poor - Significant issues present
- 4-6: Average - Some issues, acceptable quality
- 7-8: Good - Minor issues, solid quality
- 9-10: Excellent - No significant issues

## Output Format:
Provide your evaluation in this JSON format:
{{
  "overall_score": <number>,
  "dimension_scores": [
    {{"dimension": "<dimension>", "score": <number>, "reasoning": "<reasoning>"}}
  ],
  "summary": "<brief summary>",
  "improvement_suggestions": ["<suggestion1>", "<suggestion2>"]
}}

Ensure scores are integers between 1 and 10."""

def judge_output(
    output_to_judge: str,
    criteria: str,
    context: Optional[str] = None,
    model: str = "gpt-4o",
    with_cot: bool = True
) -> JudgeResult:
    """Use LLM as judge to evaluate an output."""
    
    prompt = create_judge_prompt(output_to_judge, criteria, context, with_cot)
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=2000
    )
    
    result_data = response.choices[0].message.content
    return JudgeResult.model_validate_json(result_data)

def multi_perspective_judge(
    output_to_judge: str,
    criteria: str,
    num_judges: int = 3,
    model: str = "gpt-4o"
) -> dict:
    """Use multiple judge prompts for more reliable evaluation."""
    
    perspectives = [
        "Strict evaluator focusing on correctness and safety",
        "Helpful assistant focusing on user benefit and clarity", 
        "Technical expert focusing on precision and completeness"
    ]
    
    scores = []
    for perspective in perspectives[:num_judges]:
        prompt = create_judge_prompt(
            output_to_judge,
            f"{criteria}\n\nYour perspective: {perspective}",
            with_reasoning=True
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2000
        )
        
        result = JudgeResult.model_validate_json(response.choices[0].message.content)
        scores.append(result.overall_score)
    
    avg_score = sum(scores) / len(scores)
    return {
        "scores": scores,
        "average": round(avg_score, 2),
        "agreement": max(scores) - min(scores)  # Lower is better
    }