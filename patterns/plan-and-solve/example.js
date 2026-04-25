import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

class PlanAndSolve {
    constructor() {
        this.client = new Anthropic();
    }
    
    async createPlan(task, context = '') {
        const contextPrompt = context ? `\n\nContext:\n${context}` : '';
        
        const planningPrompt = `Create a detailed plan for this task:

Task: ${task}${contextPrompt}

Format as:
STEP [N]: [Name]
Description: [What to do]
Dependencies: [Prerequisite step numbers or "None"]`;
        
        const response = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 1024,
            messages: [{ role: 'user', content: planningPrompt }]
        });
        
        return this.parsePlan(response.content[0].text, task);
    }
    
    parsePlan(planText, goal) {
        const steps = [];
        let currentStep = null;
        
        for (const line of planText.split('\n')) {
            const trimmed = line.trim();
            
            if (trimmed.startsWith('STEP ')) {
                if (currentStep) steps.push(currentStep);
                
                const match = trimmed.match(/STEP\s+(\d+):\s*(.+)/);
                if (match) {
                    currentStep = {
                        number: parseInt(match[1]),
                        name: match[2],
                        description: '',
                        dependencies: [],
                        status: 'pending',
                        output: null
                    };
                }
            } else if (currentStep && trimmed.startsWith('Description:')) {
                currentStep.description = trimmed.replace('Description:', '').trim();
            } else if (currentStep && trimmed.startsWith('Dependencies:')) {
                const deps = trimmed.replace('Dependencies:', '').trim();
                if (deps.toLowerCase() !== 'none') {
                    currentStep.dependencies = deps.split(',')
                        .map(d => parseInt(d.trim()))
                        .filter(n => !isNaN(n));
                }
            }
        }
        
        if (currentStep) steps.push(currentStep);
        
        return { goal, steps };
    }
    
    async executeStep(step, task, previousOutputs, context = '') {
        const contextParts = [];
        if (context) contextParts.push(`Context:\n${context}`);
        
        if (Object.keys(previousOutputs).length > 0) {
            contextParts.push('Previous step results:');
            for (const [num, output] of Object.entries(previousOutputs)) {
                contextParts.push(`\nStep ${num}: ${output.substring(0, 300)}...`);
            }
        }
        
        const prompt = `Execute this step:

Task: ${task}

Step: ${step.name}
Description: ${step.description}

${contextParts.join('\n\n')}

Provide thorough execution with findings and outputs.`;
        
        const response = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 2048,
            messages: [{ role: 'user', content: prompt }]
        });
        
        return response.content[0].text;
    }
    
    canExecute(step, completed) {
        return step.dependencies.every(dep => completed.has(dep));
    }
    
    async solve(task, context = '') {
        const plan = await this.createPlan(task, context);
        
        if (plan.steps.length === 0) {
            return { output: 'Failed to create plan', plan };
        }
        
        const completed = new Set();
        const outputs = {};
        
        let remaining = [...plan.steps];
        let iterations = 0;
        
        while (remaining.length > 0 && iterations < plan.steps.length * 2) {
            iterations++;
            
            for (const step of remaining) {
                if (!this.canExecute(step, completed)) continue;
                
                step.status = 'in_progress';
                const output = await this.executeStep(step, task, outputs, context);
                step.output = output;
                step.status = 'completed';
                outputs[step.number] = output;
                completed.add(step.number);
                remaining = remaining.filter(s => s !== step);
            }
        }
        
        const synthesisPrompt = `Synthesize these step results: 

Task: ${task}

${plan.steps.map(s => 
            `## Step ${s.number}: ${s.name}\n\n${s.output}`
         ).join('\n\n')}

Provide the final synthesized output.`;
        
        const finalResponse = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 2048,
            messages: [{ role: 'user', content: synthesisPrompt }]
        });
        
        return {
            output: finalResponse.content[0].text,
            plan
        };
    }
}

// Example usage
const ps = new PlanAndSolve();

const task = 'Research and recommend the best laptop for a computer science student under $1500';
const context = 'Primary use will be programming and light gaming. Needs good battery life for classes.';

const result = await ps.solve(task, context);
console.log(result.output);