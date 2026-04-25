import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

async function chainOfThought(examples, targetQuestion) {
    let prompt = "Solve the following problems. Show your reasoning step by step.\n\n";
    
    for (const { question, reasoning, answer } of examples) {
        prompt += `Question: ${question}\n`;
        prompt += `Reasoning: ${reasoning}\n`;
        prompt += `Answer: ${answer}\n\n`;
    }
    
    prompt += `Question: ${targetQuestion}\n`;
    prompt += "Reasoning: ";
    
    const message = await client.messages.create({
        model: "claude-sonnet-4-20250514",
        maxTokens: 1024,
        messages: [{ role: "user", content: prompt }]
    });
    
    return message.content[0].text;
}

const mathExamples = [
    {
        question: "A farmer has 15 chickens and buys 3 more. Each chicken lays 2 eggs. How many eggs total?",
        reasoning: "Step 1: Total chickens = 15 + 3 = 18\nStep 2: Total eggs = 18 × 2 = 36\nFinal: 36",
        answer: "36"
    }
];

const question = "There are 4 birds on a tree. 2 more join them. Then half fly away. How many remain?";
const answer = await chainOfThought(mathExamples, question);
console.log(answer);