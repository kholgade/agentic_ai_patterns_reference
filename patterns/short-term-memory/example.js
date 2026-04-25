import { ChatOpenAI } from "langchain/chat_models/openai";
import { BufferMemory } from "langchain/memory";

class ShortTermMemory {
  constructor(options = {}) {
    this.maxTokens = options.maxTokens || 128000;
    this.llm = new ChatOpenAI({ model: "gpt-4o" });
    this.memory = new BufferMemory({
      returnMessages: true,
      memoryKey: "chat_history"
    });
  }

  async chat(input) {
    await this.memory.saveContext(
      { input },
      { output: "" }
    );
    
    const messages = await this.memory.getChatMessages();
    const response = await this.llm.predict(messages);
    
    await this.memory.saveContext(
      { input },
      { output: response }
    );
    
    return response;
  }

  async prune(maxMessages = 10) {
    const messages = await this.memory.getChatMessages();
    if (messages.length > maxMessages) {
      const recent = messages.slice(-maxMessages);
      const summary = await this.summarize(messages.slice(0, -maxMessages));
      
      await this.memory.clear();
      await this.memory.saveContext(
        { summary },
        { output: "" }
      );
      
      for (const msg of recent) {
        await this.memory.saveContext(msg.input, msg.output);
      }
    }
  }

  async summarize(messages) {
    const text = messages.map(m => `${m.role}: ${m.content}`).join("\n");
    const prompt = `Summarize this conversation concisely:\n${text}`;
    return await this.llm.predict(prompt);
  }

  clear() {
    return this.memory.clear();
  }
}

// Usage
const memory = new ShortTermMemory({ maxTokens: 128000 });
const response1 = await memory.chat("My favorite color is blue.");
const response2 = await memory.chat("What's my favorite color?"); // "blue"