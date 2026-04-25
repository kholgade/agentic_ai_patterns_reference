import { OpenAI } from 'openai';

const openai = new OpenAI();

class DynamicFewShotSelector {
    constructor(examples, k = 3) {
        this.examples = examples;
        this.k = k;
        this.exampleEmbeddings = [];
    }

    async getEmbedding(text) {
        const response = await openai.embeddings.create({
            model: "text-embedding-3-small",
            input: text
        });
        return response.data[0].embedding;
    }

    async initialize() {
        this.exampleEmbeddings = await Promise.all(
            this.examples.map(ex => this.getEmbedding(ex.input))
        );
    }

    async selectExamples(query) {
        if (this.exampleEmbeddings.length === 0) {
            await this.initialize();
        }

        const queryEmbedding = await this.getEmbedding(query);

        const similarities = this.exampleEmbeddings.map((exEmb, i) => {
            const similarity = this.dotProduct(queryEmbedding, exEmb);
            return { similarity, index: i };
        });

        similarities.sort((a, b) => b.similarity - a.similarity);

        return similarities
            .slice(0, this.k)
            .map(s => this.examples[s.index]);
    }

    dotProduct(a, b) {
        return a.reduce((sum, val, i) => sum + val * b[i], 0);
    }
}

class FewShotLearner {
    constructor(examples) {
        this.examples = examples;
    }

    buildPrompt(query) {
        const examplesText = this.examples
            .map(ex => `Input: ${ex.input}\nOutput: ${ex.output}`)
            .join('\n\n');

        return `Given the following examples of the desired input-output pattern:

${examplesText}

Now complete this new input:

Input: ${query}
Output:`;
    }

    async complete(query, model = "gpt-4o") {
        const prompt = this.buildPrompt(query);

        const response = await openai.chat.completions.create({
            model,
            messages: [
                { role: "system", content: "You follow the pattern shown in examples exactly." },
                { role: "user", content: prompt }
            ]
        });

        return response.choices[0].message.content;
    }
}

const examples = [
    { input: "hello → spanish", output: "hola" },
    { input: "goodbye → spanish", output: "adiós" },
    { input: "thank you → french", output: "merci" }
];

const learner = new FewShotLearner(examples);
const result = await learner.complete("please → french");