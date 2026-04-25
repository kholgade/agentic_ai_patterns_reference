class ToolOrchestrator {
  constructor(tools) {
    this.tools = tools;
  }

  async sequential(pipeline) {
    let context = {};
    const results = [];
    
    for (const [toolName, argsTemplate] of pipeline) {
      const args = this.resolveArgs(argsTemplate, context);
      const result = await this.execute(toolName, args);
      results.push({ tool: toolName, result });
      
      if (!result.success) break;
      context.lastResult = result.data;
    }
    
    return results;
  }

  async parallel(toolCalls) {
    return Promise.all(
      toolCalls.map(([name, args]) => this.execute(name, args))
    );
  }

  async execute(toolName, args) {
    const tool = this.tools[toolName];
    if (!tool) return { success: false, error: "Tool not found" };
    
    try {
      const data = await tool(args);
      return { success: true, data };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  resolveArgs(template, context) {
    return Object.fromEntries(
      Object.entries(template).map(([k, v]) => [
        k, typeof v === 'string' 
          ? v.replace(/{(\w+)}/, (_, k) => context[k] || v) 
          : v
      ])
    );
  }
}

// Usage
const orchestrator = new ToolOrchestrator({
  search: async ({ query }) => ({ results: [`${query} result 1`, `${query} result 2`] }),
  fetch: async ({ url }) => `Content of ${url}`,
  summarize: async ({ text }) => text.substring(0, 100)
});

const results = await orchestrator.sequential([
  ["search", { query: "AI" }],
  ["fetch", { url: "{lastResult.results[0]}" }],
  ["summarize", { text: "{lastResult}" }]
]);