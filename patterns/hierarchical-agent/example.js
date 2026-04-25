class HierarchicalAgent {
  constructor(llm) {
    this.llm = llm;
    this.subAgents = {
      coder: this.createAgent("You write Python code."),
      researcher: this.createAgent("You find information."),
      writer: this.createAgent("You write content.")
    };
  }

  createAgent(systemPrompt) {
    return {
      async run(input) {
        return this.llm.predict(systemPrompt + "\n\n" + input);
      }
    };
  }

  async decompose(task) {
    const prompt = `Decompose: "${task}" 
Return JSON: [{"subtask": "...", "agent": "coder|researcher|writer"}]`;
    const response = await this.llm.predict(prompt);
    return JSON.parse(response);
  }

  async execute(task) {
    const subtasks = await this.decompose(task);
    
    if (subtasks.length === 1) {
      const agent = this.subAgents[subtasks[0].agent];
      return await agent.run(subtasks[0].subtask);
    }
    
    const results = await Promise.all(
      subtasks.map(t => this.subAgents[t.agent].run(t.subtask))
    );
    
    return this.synthesize(task, subtasks, results);
  }

  synthesize(task, subtasks, results) {
    const combined = subtasks.map((t, i) => 
      `${t.subtask}: ${results[i]}`
    ).join("\n\n");
    
    return this.llm.predict(
      `Combine into response for: ${task}\n\n${combined}`
    );
  }
}