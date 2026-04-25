import { Pinecone } from "@pinecone-database/pinecone";
import { OpenAIEmbeddings } from "@langchain/embeddings";

class LongTermMemory {
  constructor(options = {}) {
    this.indexName = options.indexName || "agent-memory";
    this.embeddings = new OpenAIEmbeddings({ 
      model: "text-embedding-3-small" 
    });
    this.pinecone = new Pinecone();
    this.index = this.pinecone.Index(this.indexName);
  }

  async add(content, metadata = {}) {
    const vector = await this.embeddings.embedQuery(content);
    const id = `${Date.now()}`;
    
    await this.index.upsert([{
      id,
      values: vector,
      metadata: { content, ...metadata }
    }]);
    
    return id;
  }

  async search(query, options = {}) {
    const { limit = 5, filter = {} } = options;
    const vector = await this.embeddings.embedQuery(query);
    
    const results = await this.index.query({
      vector,
      topK: limit,
      filter,
      includeMetadata: true
    });
    
    return results.matches.map(match => ({
      id: match.id,
      content: match.metadata.content,
      score: match.score,
      metadata: match.metadata
    }));
  }
}

// Usage
const memory = new LongTermMemory({ indexName: "my-agent" });

// Store knowledge
await memory.add(
  "User Yashodhan prefers brief responses about technical topics",
  { type: "preference", user: "yashodhan" }
);

// Retrieve
const relevant = await memory.search("what does user prefer", {
  limit: 3,
  filter: { user: "yashodhan" }
});