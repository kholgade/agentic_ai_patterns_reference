import { ChromaClient } from "langchain/vectorstores/chroma";
import { OpenAIEmbeddings } from "langchain/embeddings/openai";
import { ChatOpenAI } from "langchain/chat_models/openai";
import { createFFmpeg } from "@ffmpeg/ffmpeg";

class MultimodalRAG {
    constructor() {
        this.embeddings = new OpenAIEmbeddings();
        this.vectorStore = new ChromaClient({ collectionName: "multimodal" });
        this.llm = new ChatOpenAI({ model: "gpt-4o", temperature: 0 });
    }

    async transcribeAudio(audioPath) {
        const response = await fetch("/api/transcribe", {
            method: "POST",
            body: JSON.stringify({ audioPath })
        });
        return (await response.json()).transcription;
    }

    async embedImage(imagePath) {
        const response = await fetch("/api/embed/image", {
            method: "POST",
            body: JSON.stringify({ imagePath })
        });
        return (await response.json()).embedding;
    }

    async indexDocument(content, modality, sourcePath = null, metadata = {}) {
        const embedding = await this.embeddings.embedQuery(content);

        const doc = {
            pageContent: content,
            metadata: {
                modality,
                sourcePath,
                ...metadata
            }
        };

        await this.vectorStore.addDocuments([doc], [embedding]);
    }

    async indexFile(filePath) {
        const ext = filePath.split(".").pop().toLowerCase();

        if (["txt", "md", "json"].includes(ext)) {
            const content = await this.readFile(filePath);
            await this.indexDocument(content, "text", filePath);
        }

        else if (["jpg", "jpeg", "png", "gif"].includes(ext)) {
            const embedding = await this.embedImage(filePath);
            const doc = {
                pageContent: `Image: ${filePath}`,
                metadata: { modality: "image", sourcePath: filePath }
            };
            await this.vectorStore.addDocuments([doc], [embedding]);
        }

        else if (["mp3", "wav", "m4a"].includes(ext)) {
            const transcription = await this.transcribeAudio(filePath);
            await this.indexDocument(transcription, "audio", filePath);
        }
    }

    async retrieve(query, k = 5) {
        const queryEmbedding = await this.embeddings.embedQuery(query);
        return this.vectorStore.similaritySearchByVector(queryEmbedding, k);
    }

    async answer(query) {
        const docs = await this.retrieve(query, 5);

        const context = docs.map((doc, i) => {
            const modality = doc.metadata?.modality || "unknown";
            return `[${i + 1}] ${modality.toUpperCase()}:\n${doc.pageContent}\nSource: ${doc.metadata?.sourcePath || "N/A"}`;
        }).join("\n\n");

        const prompt = `
Based on the following retrieved context from multiple modalities, answer thoroughly.

Context:
${context}

Question: ${query}

Answer:
        `;

        const response = await this.llm.invoke(prompt);
        return response.content;
    }
}

const mmrag = new MultimodalRAG();
await mmrag.indexFile("./documents/report.pdf");
await mmrag.indexFile("./images/diagram.png");
await mmrag.indexFile("./audio/meeting.mp3");

const answer = await mmrag.answer("What are the key findings from the report?");
console.log(answer);