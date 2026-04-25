import * as tf from '@tensorflow/tfjs';

class SelfRAGModel {
    constructor(apiEndpoint = 'https://api.together.xyz/v1/chat/completions') {
        this.apiEndpoint = apiEndpoint;
        this.apiKey = process.env.TOGETHER_API_KEY;
    }

    parseReflectionTokens(text) {
        const reflections = {
            retrievals: [],
            relevance: [],
            support: [],
            utilities: []
        };

        const regex = /\[(RETRIEVE|ISREL|ISSUP|UTILITY)[^\]]*\]/g;
        let match;

        while ((match = regex.exec(text)) !== null) {
            const token = match[1].toLowerCase();
            if (reflections[token]) {
                reflections[token].push(match[0]);
            }
        }

        return reflections;
    }

    async generate(query, documents = []) {
        const docContext = documents.length > 0
            ? '\n\nRetrieved Documents:\n' + documents.map((d, i) => `[${i}]: ${d}`).join('\n')
            : '';

        const systemPrompt = `You are Self-RAG, a model that uses reflection tokens:
- [RETRIEVE] when you need external knowledge
- [ISREL:relevant] when retrieved content is relevant
- [ISREL:irrelevant] when content doesn't help
- [ISSUP:supported] when evidence supports your claim
- [ISSUP:no support] when evidence contradicts
- [UTILITY:0-5] to rate response quality

Analyze the question and generate a response with appropriate reflection tokens.`;

        const response = await fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'togethercomputer/Reflector-7B',
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: query + docContext }
                ],
                max_tokens: 500,
                temperature: 0.7
            })
        });

        const data = await response.json();
        const text = data.choices[0].message.content;

        return {
            text,
            reflections: this.parseReflectionTokens(text)
        };
    }

    async generateWithRetrieval(query, retriever) {
        const initialResult = await this.generate(query);

        if (initialResult.reflections.retrievals.length > 0) {
            const docs = await retriever.getRelevantDocuments(query);
            return this.generate(query, docs);
        }

        return initialResult;
    }
}

const rag = new SelfRAGModel();
const result = await rag.generateWithRetrieval(
    "What are the main principles of constitutional law?",
    vectorRetriever
);

console.log(`Response:\n${result.text}`);
console.log(`Reflection analysis:`, result.reflections);