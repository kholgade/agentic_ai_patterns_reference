import { ChromaClient } from "langchain/vectorstores/chroma";
import { OpenAIEmbeddings } from "langchain/embeddings/openai";
import { ChatOpenAI } from "langchain/chat_models/openai";
import { RetrievalQAChain } from "langchain/chains/retrieval-qa";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";

async function buildBasicRAG(collectionName = "knowledge_base") {
    const embeddings = new OpenAIEmbeddings({
        model: "text-embedding-3-small"
    });

    const vectorStore = await ChromaClient.fromExistingCollection({
        collectionName,
        embeddings
    });

    const llm = new ChatOpenAI({
        modelName: "gpt-4o-mini",
        temperature: 0
    });

    const retriever = vectorStore.asRetriever(5);

    const chain = RetrievalQAChain.fromLLM(llm, retriever);
    return chain;
}

async function indexDocuments(documents, collectionName = "knowledge_base") {
    const embeddings = new OpenAIEmbeddings({
        model: "text-embedding-3-small"
    });

    const textSplitter = new RecursiveCharacterTextSplitter({
        chunkSize: 1000,
        chunkOverlap: 200
    });

    const chunks = await textSplitter.splitTexts(documents);

    const vectorStore = await ChromaClient.fromTexts(
        chunks,
        { id: chunks.map((_, i) => `doc_${i}`) },
        embeddings,
        { collectionName }
    );

    return vectorStore;
}

const chain = await buildBasicRAG("knowledge_base");
const response = await chain.invoke({
    query: "What are the main components of a transformer model?"
});

console.log(response.text);