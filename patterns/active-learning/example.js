import { OpenAI } from 'openai';

const openai = new OpenAI();

class ClarificationRequest {
    constructor(type, question, contextNeeded, priority) {
        this.type = type;
        this.question = question;
        this.contextNeeded = contextNeeded;
        this.priority = priority;
    }
}

class ActiveLearningAgent {
    constructor(confidenceThreshold = 0.7) {
        this.confidenceThreshold = confidenceThreshold;
        this.pendingClarifications = [];
    }

    async assessConfidence(task) {
        const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
                { role: "system", content: "You assess your confidence honestly on a 0-1 scale." },
                { role: "user", content: `Analyze this task and give confidence 0-1:\n\n${task}` }
            ]
        });

        const content = response.choices[0].message.content;
        const match = content.match(/[01](?:\.\d+)?/);
        return match ? parseFloat(match[0]) : 0.5;
    }

    async identifyClarifications(task) {
        const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
                { role: "system", content: "Identify clarification needs." },
                { role: "user", content: `What clarification is needed for:\n\n${task}` }
            ]
        });

        const content = response.choices[0].message.content;
        if (content.trim().toUpperCase() === 'NONE') return [];

        return content.split('\n')
            .filter(line => line.trim())
            .map(line => new ClarificationRequest('ambiguity', line, 'context', 3));
    }

    async executeWithClarification(task, userResponses = null) {
        const confidence = await this.assessConfidence(task);

        if (confidence >= this.confidenceThreshold) {
            return await this.generateOutput(task);
        }

        const clarifications = await this.identifyClarifications(task);
        const pending = clarifications.filter(c => c.priority <= 2);

        if (pending.length > 0 && !userResponses) {
            return {
                status: 'clarification_needed',
                requests: pending,
                confidence
            };
        }

        const augmentedTask = userResponses
            ? `${task}\n\nAdditional context: ${JSON.stringify(userResponses)}`
            : task;

        return await this.generateOutput(augmentedTask);
    }

    async generateOutput(task) {
        const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
                { role: "system", content: "You complete tasks accurately." },
                { role: "user", content: task }
            ]
        });

        return {
            status: 'completed',
            output: response.choices[0].message.content
        };
    }
}

const agent = new ActiveLearningAgent(0.75);
const result = await agent.executeWithClarification("Summarize the project status");