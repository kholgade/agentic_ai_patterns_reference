import { ChromaClient } from "langchain/vectorstores/chroma";
import { OpenAIEmbeddings } from "langchain/embeddings/openai";
import { ChatOpenAI } from "langchain/chat_models/openai";
import { VectorStoreToolkit, createRetrieverTool } from "langchain/tools";
import { BM25 } from "langchain/retrievers/bm25";

class AdvancedRAG {
    constructor() {
        this.embeddings = new OpenAIEmbeddings();
        this.llm = new ChatOpenAI({ model: "gpt-4o", temperature: 0 });
    }

    async reciprocalRankFusion(resultsLists, k = 60) {
        const fusedScores = new Map();

        resultsLists.forEach(results => {
            results.forEach((doc, rank) => {
                const docId = doc.pageContent.substring(0, 50);
                const currentScore = fusedScores.get(docId) || 0;
                fusedScores.set(docId, currentScore + 1 / (k + rank + 1));
            });
        });

        const sorted = Array.from(fusedScores.entries())
            .sort((a, b) => b[1] - a[1]);

        return sorted.map(([id]) =>
            resultsLists.flat().find(doc => doc.pageContent.substring(0, 50) === id)
        );
    }

    async rerank(query, documents, topK = 5) {
        const pairs = documents.map(doc => [query, doc.pageContent]);
        const scores = await this.crossEncoder.predict(pair);

        return documents
            .map((doc, i) => ({ doc, score: scores[i] }))
            .sort((a, b) => b.score - a.score)
            .slice(0, topK)
            .map(r => r.doc);
    }

    async queryRewrite(query) {
        const response = await this.llm.invoke(
            `Rewrite this query to better match technical documentation: ${query}`
        );
        return response.content;
    }

    async decomposeQuery(query) {
        const response = await this.llm.invoke(
            `Break this into simpler sub-questions: ${query}`
        );
        return response.content;
    }
}

const rag = new AdvancedRAG();
const fused = await rag.reciprocalRankFusion([vectorResults, bm25Results]);
const reranked = await rag.rerank(userQuery, fused);