import { ChatOpenAI } from "langchain/chat_models/openai";
import { AgentExecutor, createOpenAIFunctionsAgent } from "langchain/agents";
import { pullFromHub } from "langchain/hub";
import { TavilySearchResults } from "langchain/tools/tavily_search";
import { Calculator } from "langchain/tools/calculator";

// Define tools
const tools = [
  new TavilySearchResults({ maxResults: 3 }),
  new Calculator()
];

// Create agent with tools
const llm = new ChatOpenAI({ model: "gpt-4o", temperature: 0 });
const prompt = await pullFromHub("hwchase17/openai-functions-agent");
const agent = await createOpenAIFunctionsAgent(llm, tools, prompt);
const agentExecutor = new AgentExecutor({ agent, tools });

// Execute query
const result = await agentExecutor.invoke ({
  input: "What is the temperature in Tokyo divided by 2?"
});

console.log(result.output);
// "The temperature in Tokyo is 25°C, divided by 2 equals 12.5°C."