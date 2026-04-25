import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// Tool definitions
const tools = {
    search: async (query) => {
        console.log(`[SEARCH] Query: ${query}`);
        return { success: true, result: `Results for: ${query}` };
    },
    calculate: async (expression) => {
        try {
            const result = eval(expression);
            return { success: true, result: String(result) };
        } catch (e) {
            return { success: false, result: '', error: e.message };
        }
    },
};

async function react(question, maxIterations = 10) {
    const messages = [
        { role: 'user', content: question }
    ];
    
    for (let i = 0; i < maxIterations; i++) {
        const response = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 512,
            system: `You use the ReAct pattern. Format:
THOUGHT: [reasoning]
ACTION: [tool_name][argument]
OBSERVATION: [result]

Or when done:
FINAL ANSWER: [answer]

Tools: search, calculate`,
            messages
        });
        
        const output = response.content[0].text;
        messages.push({ role: 'assistant', content: output });
        
        // Check for final answer
        if (output.includes('FINAL ANSWER:')) {
            return output.split('FINAL ANSWER:')[1].trim();
        }
        
        // Execute action
        const actionMatch = output.match(/ACTION:\s*(\w+)\[(.+?)\]/);
        if (actionMatch) {
            const [, toolName, arg] = actionMatch;
            if (tools[toolName]) {
                const result = await tools[toolName](arg);
                const obs = result.success 
                    ? `Result: ${result.result}`
                    : `Error: ${result.error}`;
                messages.push({ role: 'user', content: `OBSERVATION: ${obs}` });
            }
        }
    }
    
    return 'Max iterations reached';
}

// Example usage
const answer = await react(
    'What is the population of the capital city of Australia?'
);
console.log(answer);