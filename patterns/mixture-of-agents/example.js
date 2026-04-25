import { OpenAI } from 'openai';

const openai = new OpenAI();

class AgentConfig {
    constructor(name, systemPrompt, model = "gpt-4o", temperature = 0.7) {
        this.name = name;
        this.systemPrompt = systemPrompt;
        this.model = model;
        this.temperature = temperature;
    }
}

class LLMAgent {
    constructor(config) {
        this.config = config;
    }

    async process(inputData) {
        const response = await openai.chat.completions.create({
            model: this.config.model,
            messages: [
                { role: "system", content: this.config.systemPrompt },
                { role: "user", content: inputData }
            ],
            temperature: this.config.temperature
        });

        return {
            agentName: this.config.name,
            content: response.choices[0].message.content,
            metadata: { model: this.config.model }
        };
    }
}

class ParallelMixtureOfAgents {
    constructor(agents, mergePrompt) {
        this.agents = agents;
        this.mergePrompt = mergePrompt;
    }

    async execute(task) {
        const tasks = this.agents.map(agent => agent.process(task));
        const outputs = await Promise.all(tasks);

        const combinedInput = outputs
            .map(o => `Agent: ${o.agentName}\nOutput: ${o.content}`)
            .join('\n\n');

        const merger = new LLMAgent(new AgentConfig(
            'Merger',
            this.mergePrompt
        ));

        const result = await merger.process(
            `Combine: \n\n${combinedInput}`
        );

        return result;
    }
}

class SequentialMoA {
    constructor(agents) {
        this.agents = agents;
    }

    async execute(task) {
        let currentInput = task;

        for (const agent of this.agents) {
            const output = await agent.process(currentInput);
            currentInput = output.content;
        }

        return currentInput;
    }
}

class VotingMoA {
    constructor(agents, numSamples = 2) {
        this.agents = agents;
        this.numSamples = numSamples;
    }

    async execute(task) {
        const tasks = [];
        for (const agent of this.agents) {
            for (let i = 0; i < this.numSamples; i++) {
                tasks.push(agent.process(task));
            }
        }

        const outputs = await Promise.all(tasks);

        const voteInput = outputs
            .map((o, i) => `${i + 1}. ${o.content}`)
            .join('\n\n');

        const selector = new LLMAgent(new AgentConfig(
            'Selector',
            'Pick the best response.'
        ));

        const result = await selector.process(
            `Select best:\n\n${voteInput}`
        );

        return result.content;
    }
}

const researchAgent = new LLMAgent(new AgentConfig(
    'Research',
    'Research thoroughly and find accurate information.'
));

const analysisAgent = new LLMAgent(new AgentConfig(
    'Analysis',
    'Analyze information critically and identify key insights.'
));

const creativeAgent = new LLMAgent(new AgentConfig(
    'Creative',
    'Generate innovative and creative ideas.'
));

const moa = new ParallelMixtureOfAgents(
    [researchAgent, analysisAgent, creativeAgent],
    'Combine outputs into one comprehensive response.'
);

const result = await moa.execute('Explain artificial intelligence');