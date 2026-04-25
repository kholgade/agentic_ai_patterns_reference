import anthropic
from collections import Counter
import json

client = anthropic.Anthropic()

def self_consistency(
    question: str,
    num_paths: int = 10,
    cot_system_prompt: str = None
) -> tuple[str, dict]:
    """
    Implements Self-Consistency prompting.
    
    Args:
        question: The question to answer
        num_paths: Number of reasoning paths to generate
        cot_system_prompt: Optional system prompt for reasoning style
        
    Returns:
        Tuple of (selected_answer, voting_details)
    """
    
    if cot_system_prompt is None:
        cot_system_prompt = """Think through this problem step by step.
Show your complete reasoning process, then provide your final answer."""
    
    answers = []
    reasoning_paths = []
    
    for i in range(num_paths):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=cot_system_prompt,
                messages=[{"role": "user", "content": question}]
            )
            
            full_response = response.content[0].text
            
            reasoning_paths.append(full_response)
            
            answer = extract_answer(full_response)
            if answer:
                answers.append(normalize_answer(answer))
                
        except Exception as e:
            print(f"Path {i+1} failed: {e}")
            continue
    
    if not answers:
        return "Unable to determine answer", {}
    
    vote_counts = Counter(answers)
    most_common = vote_counts.most_common()
    
    winner = most_common[0][0]
    confidence = most_common[0][1] / len(answers)
    
    return winner, {
        "vote_counts": dict(vote_counts),
        "total_paths": len(answers),
        "confidence": confidence,
        "reasoning_paths": reasoning_paths,
        "winning_votes": most_common[0][1]
    }

def extract_answer(reasoning: str) -> str:
    """Extract the final answer from a reasoning chain."""
    lines = reasoning.strip().split('\n')
    
    for line in reversed(lines):
        line = line.strip()
        if line.startswith(('Answer:', 'Therefore:', 'Final answer:', 'Thus:')):
            return line.split(':', 1)[1].strip()
    
    if lines:
        return lines[-1].strip()
    
    return reasoning.strip()

def normalize_answer(answer: str) -> str:
    """Normalize answers for comparison."""
    answer = answer.lower().strip()
    
    mappings = {
        'yes': 'yes',
        'y': 'yes',
        'true': 'yes',
        'correct': 'yes',
        'no': 'no',
        'n': 'no',
        'false': 'no',
        'incorrect': 'no',
    }
    
    for key, value in mappings.items():
        if key in answer:
            return value
    
    if len(answer) <= 50:
        return answer
    
    return answer[:50]


def self_consistency_with_samples(
    samples: list[tuple[str, str, str]],
    question: str,
    num_paths: int = 10
) -> tuple[str, dict]:
    """
    Self-Consistency with few-shot examples.
    
    Args:
        samples: List of (question, reasoning, answer) examples
        question: Target question
        num_paths: Number of paths to generate
    """
    
    examples_text = "Here are examples of step-by-step reasoning:\n\n"
    for q, r, a in samples:
        examples_text += f"Question: {q}\nReasoning: {r}\nAnswer: {a}\n\n"
    
    examples_text += f"\nNow solve this new question:\nQuestion: {question}\nReasoning:"
    
    answers = []
    reasoning_paths = []
    
    for i in range(num_paths):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": examples_text}]
        )
        
        full_response = response.content[0].text
        reasoning_paths.append(full_response)
        
        answer = extract_answer(full_response)
        if answer:
            answers.append(normalize_answer(answer))
    
    vote_counts = Counter(answers)
    winner = vote_counts.most_common(1)[0][0]
    
    return winner, {
        "vote_counts": dict(vote_counts),
        "total_paths": len(answers),
        "confidence": vote_counts[winner] / len(answers),
        "reasoning_paths": reasoning_paths
    }


# Example usage
question = """A store has 24 items. They receive a new shipment of 3 boxes 
with 8 items each. Then they sell half of all their items. How many items 
do they have left?"""

answer, details = self_consistency(question, num_paths=15)
print(f"Answer: {answer}")
print(f"Confidence: {details['confidence']:.1%}")
print(f"Vote breakdown: {details['vote_counts']}")