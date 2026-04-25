import anthropic

client = anthropic.Anthropic()

def chain_of_thought(reasoning_examples: list, target_question: str) -> str:
    """
    Implements Chain-of-Thought prompting with few-shot examples.
    
    Args:
        reasoning_examples: List of (question, reasoning, answer) tuples
        target_question: The question to solve
    """
    
    user_message = "Solve the following problems. Show your reasoning step by step.\n\n"
    
    for question, reasoning, answer in reasoning_examples:
        user_message += f"Question: {question}\n"
        user_message += f"Reasoning: {reasoning}\n"
        user_message += f"Answer: {answer}\n\n"
    
    user_message += f"Question: {target_question}\n"
    user_message += "Reasoning: "
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )
    
    return message.content[0].text


# Example usage with mathematical reasoning
math_examples = [
    (
        "A store has 12 apples. They receive a shipment of 8 more apples. "
        "If they sell 5 apples, how many do they have left?",
        "Step 1: Start with initial apples: 12\n"
        "Step 2: Add shipment: 12 + 8 = 20\n"
        "Step 3: Subtract sold apples: 20 - 5 = 15\n"
        "Final answer: 15",
        "15"
    ),
    (
        "Tom has 3 boxes of cookies. Each box contains 4 cookies. "
        "He eats 2 cookies. How many cookies does he have left?",
        "Step 1: Calculate total cookies: 3 × 4 = 12\n"
        "Step 2: Subtract eaten cookies: 12 - 2 = 10\n"
        "Final answer: 10",
        "10"
    )
]

question = ("Sarah has 24 stickers. She gives 1/3 of them to her friend. "
           "Then she buys 6 more stickers. How many stickers does she have?")

answer = chain_of_thought(math_examples, question)
print(answer)