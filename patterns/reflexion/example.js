import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

class ReflexionAgent {
    constructor(options = {}) {
        this.maxIterations = options.maxIterations || 5;
        this.reflectionMemory = [];
    }
    
    async actorGenerate(task, context = '', reflectionHistory = '') {
        const prompt = `${reflectionHistory}
${context ? `\n\nContext:\n${context}` : ''}

Task: ${task}

Provide your response:`;
        
        const response = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 2048,
            messages: [{ role: 'user', content: prompt }]
        });
        
        return response.content[0].text;
    }
    
    async criticEvaluate(task, output, criteria = '') {
        const criteriaPrompt = criteria ? `\n\nEvaluation criteria:\n${criteria}` : '';
        
        const prompt = `Critically evaluate this output for the task.

Task: ${task}

Output:
${output}
${criteriaPrompt}

Identify:
1. Strengths
2. Issues/weaknesses
3. Suggested improvements`;
        
        const response = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 1024,
            messages: [{ role: 'user', content: prompt }]
        });
        
        return response.content[0].text;
    }
    
    async reflectorSynthesize(criticism, pastReflections = '') {
        const pastPrompt = pastReflections ? `\n\nPast reflections:\n${pastReflections}` : '';
        
        const prompt = `Synthesize lessons from this criticism.

Criticism:
${criticism}
${pastPrompt}

Summarize:
1. Key issues
2. Actions to take
3. Principles to remember`;
        
        const response = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 512,
            messages: [{ role: 'user', content: prompt }]
        });
        
        return response.content[0].text;
    }
    
    async checkCompletion(task, output) {
        const response = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 256,
            messages: [{
                role: 'user',
                content: `Is this task complete?\n\nTask: ${task}\n\nOutput:\n${output}`
            }]
        });
        
        const result = response.content[0].text;
        return {
            isComplete: result.toUpperCase().includes('COMPLETE'),
            reason: result
        };
    }
    
    async solve(task, criteria = '', context = '') {
        let currentOutput = '';
        const reflections = [];
        
        for (let i = 0; i < this.maxIterations; i++) {
            console.log(`\n--- Iteration ${i + 1} ---`);
            
            let promptContext = context;
            if (this.reflectionMemory.length > 0) {
                const history = this.reflectionMemory
                    .map(r => `Iteration ${r.iteration}: ${r.summary}`)
                    .join('\n');
                promptContext = `${context}\n\nPast learnings:\n${history}`;
            }
            
            currentOutput = await this.actorGenerate(task, promptContext);
            console.log(`Output preview: ${currentOutput.substring(0, 100)}...`);
            
            const { isComplete, reason } = await this.checkCompletion(task, currentOutput);
            if (isComplete) {
                console.log('Task complete!');
                break;
            }
            
            const criticism = await this.criticEvaluate(task, currentOutput, criteria);
            console.log(`Criticism: ${criticism.substring(0, 100)}...`);
            
            const pastSummary = this.reflectionMemory.map(r => r.summary).join('\n');
            const summary = await this.reflectorSynthesize(criticism, pastSummary);
            
            this.reflectionMemory.push({ iteration: i + 1, criticism, summary });
            
            reflections.push({ iteration: i + 1, output: currentOutput, criticism, summary });
        }
        
        return { output: currentOutput, reflections };
    }
}

// Example usage
const agent = new ReflexionAgent({ maxIterations: 3 });

const task = `Write a JavaScript function that validates an email address
using regex. Include edge case handling and documentation.`;

const result = await agent.solve(task, 'Correctness, edge cases, code style');
console.log('\nFinal output:\n', result.output);