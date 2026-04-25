import { ChromaClient } from "langchain/vectorstores/chroma";
import { OpenAIEmbeddings } from "langchain/embeddings/openai";
import { ChatOpenAI } from "langchain/chat_models/openai";

class CorrectiveRAG {
    constructor(vectorStore, webSearchTool = null) {
        this.vectorStore = vectorStore;
        this.webSearch = webSearchTool;
        this.embeddings = new OpenAIEmbeddings();
        this.llm = new ChatOpenAI({ model: "gpt-4o", temperature: 0 });
    }

    async evaluateRelevance(query, docs) {
        const docText = docs.map(d => d.pageContent).join('\n\n');

        const response = await this.llm.invoke(`
            Evaluate document relevance (0-10) to query.
            Query: ${query}
            Documents: ${docText}
            Respond: SCORE: <number>, REASON: <brief explanation>
        `);

        const scoreMatch = response.content.match(/SCORE:\s*(\d+)/);
        return {
            score: scoreMatch ? parseInt(scoreMatch[1]) : 0,
            explanation: response.content
        };
    }

    async verifyClaimSupport(claim, docs) {
        const docText = docs.map(d => d.pageContent).join('\n\n');

        const response = await this.llm.invoke(`
            Does the claim align with documents? Answer YES/PARTIAL/NO.
            Claim: ${claim}
            Documents: ${docText}
        `);

        const content = response.content.toUpperCase();
        const verdict = content.includes('YES') ? 'YES' :
                        content.includes('PARTIAL') ? 'PARTIAL' : 'NO';

        return { verdict, explanation: response.content };
    }

    async correctRetrieval(query, docs, threshold = 5) {
        const relevance = await this.evaluateRelevance(query, docs);

        if (relevance.score >= 7) {
            return { docs, action: 'high' };
        }

        if (relevance.score >= threshold) {
            const expandedQuery = await this.expandQuery(query);
            const newDocs = await this.vectorStore.similaritySearch(expandedQuery, 10);
            return { docs: newDocs, action: 'retry' };
        }

        if (this.webSearch) {
            const webResults = await this.webSearch(query);
            return {
                docs: [{ pageContent: webResults, metadata: { source: 'web' } }],
                action: 'web'
            };
        }

        return { docs: [], action: 'fallback' };
    }

    async expandQuery(query) {
        const response = await this.llm.invoke(
            `Rephrase to improve retrieval: ${query}`
        );
        return response.content;
    }

    async generate(query) {
        const initialDocs = await this.vectorStore.similaritySearch(query, 5);
        const { docs, action } = await this.correctRetrieval(query, initialDocs);

        if (action === 'fallback') {
            return {
                answer: "I don't have sufficient information to answer this.",
                source: 'none',
                action: 'fallback'
            };
        }

        const context = docs.map(d => d.pageContent).join('\n\n');
        const answerResponse = await this.llm.invoke(
            `Context: ${context}\n\nQuestion: ${query}\n\nAnswer only from context.`
        );

        const support = await this.verifyClaimSupport(answerResponse.content, docs);
        const finalAnswer = support.verdict === 'NO'
            ? "I cannot confidently answer this based on available information."
            : answerResponse.content;

        return {
            answer: finalAnswer,
            source: action === 'web' ? 'web_search' : 'vector_store',
            action,
            documentsUsed: docs.length
        };
    }
}

const crag = new CorrectiveRAG(vectorStore, webSearchTool);
const result = await crag.generate("What are the latest AI regulations?");
console.log(result);