import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

async function selfConsistency(question, options = {}) {
    const {
        numPaths = 10,
        systemPrompt = 'Think step by step and show your reasoning.'
    } = options;
    
    const answers = [];
    const reasoningPaths = [];
    
    for (let i = 0; i < numPaths; i++) {
        try {
            const response = await client.messages.create({
                model: 'claude-sonnet-4-20250514',
                maxTokens: 1024,
                system: systemPrompt,
                messages: [{ role: 'user', content: question }]
            });
            
            const fullResponse = response.content[0].text;
            reasoningPaths.push(fullResponse);
            
            const answer = extractAnswer(fullResponse);
            if (answer) {
                answers.push(normalizeAnswer(answer));
            }
        } catch (error) {
            console.error(`Path ${i + 1} failed:`, error);
        }
    }
    
    if (answers.length === 0) {
        return { answer: 'Unable to determine', details: {} };
    }
    
    const voteCounts = {};
    for (const answer of answers) {
        voteCounts[answer] = (voteCounts[answer] || 0) + 1;
    }
    
    const sortedVotes = Object.entries(voteCounts)
        .sort((a, b) => b[1] - a[1]);
    
    const winner = sortedVotes[0][0];
    const confidence = sortedVotes[0][1] / answers.length;
    
    return {
        answer: winner,
        details: {
            voteCounts,
            totalPaths: answers.length,
            confidence,
            reasoningPaths
        }
    };
}

function extractAnswer(reasoning) {
    const lines = reasoning.trim().split('\n');
    
    for (let i = lines.length - 1; i >= 0; i--) {
        const line = lines[i].trim();
        if (line.match(/^(answer|therefore|final answer|thus):/i)) {
            return line.split(':').slice(1).join(':').trim();
        }
    }
    
    return lines[lines.length - 1]?.trim() || reasoning.trim();
}

function normalizeAnswer(answer) {
    answer = answer.toLowerCase().trim();
    
    const yesPatterns = ['yes', 'y', 'true', 'correct', 'affirmative'];
    const noPatterns = ['no', 'n', 'false', 'incorrect', 'negative'];
    
    for (const pattern of yesPatterns) {
        if (answer.includes(pattern)) return 'yes';
    }
    for (const pattern of noPatterns) {
        if (answer.includes(pattern)) return 'no';
    }
    
    return answer.length > 50 ? answer.substring(0, 50) : answer;
}

// Example usage
const question = `If a train leaves at 2:30 PM traveling 60 mph, 
and another train leaves at 3:00 PM traveling 80 mph from the same 
station, when will the second train catch up to the first?`;

const result = await selfConsistency(question, { numPaths: 15 });

console.log(`Answer: ${result.answer}`);
console.log(`Confidence: ${(result.details.confidence * 100).toFixed(1)}%`);
console.log('Vote breakdown:', result.details.voteCounts);