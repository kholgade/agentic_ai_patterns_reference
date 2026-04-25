class MetaPrompting {
    constructor(basePrompt, maxIterations = 3) {
        this.basePrompt = basePrompt;
        this.maxIterations = maxIterations;
        this.history = [];
    }

    async analyzeAndRefine(task, previousOutput) {
        const analysisPrompt = `Analyze this previous attempt at solving the task.
        
Task: ${task}

Previous Prompt Used: ${this.basePrompt}

Previous Output:
${previousOutput}

Provide:
1. Issues or weaknesses in the output
2. Specific improvements for the prompt
3. Refined prompt that addresses these issues`;

        const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [
                { role: "system", content: "You are a prompt engineering expert." },
                { role: "user", content: analysisPrompt }
            ]
        });

        return this.parseAnalysisResponse(response.choices[0].message.content);
    }

    parseAnalysisResponse(responseText) {
        const sections = responseText.split('\n\n');
        return {
            issues: sections[0]?.split('\n').filter(s => s.trim()) || [],
            improvements: sections[1]?.split('\n').filter(s => s.trim()) || [],
            refinedPrompt: sections[2] || this.basePrompt
        };
    }

    async execute(task) {
        let currentPrompt = this.basePrompt;

        for (let i = 0; i < this.maxIterations; i++) {
            const response = await openai.chat.completions.create({
                model: "gpt-4o",
                messages: [
                    { role: "system", content: "You are a helpful assistant." },
                    { role: "user", content: `${currentPrompt}\n\nTask: ${task}` }
                ]
            });

            const output = response.choices[0].message.content;

            if (i < this.maxIterations - 1) {
                const analysis = await this.analyzeAndRefine(task, output);
                this.history.push({
                    iteration: i + 1,
                    prompt: currentPrompt,
                    output: output,
                    analysis
                });
                currentPrompt = analysis.refinedPrompt;
            } else {
                this.history.push({
                    iteration: i + 1,
                    prompt: currentPrompt,
                    output
                });
            }
        }

        return this.history[this.history.length - 1].output;
    }
}

const metaPrompter = new MetaPrompting(
    "Provide a clear, step-by-step explanation of the concept."
);
const result = await metaPrompter.execute("Explain quantum entanglement");