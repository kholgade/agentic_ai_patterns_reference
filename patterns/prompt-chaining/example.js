interface ChainStep<T = string> {
  name: string;
  prompt: string;
  transform?: (output: string) => string | T;
}

class AsyncPromptChain {
  private steps: ChainStep[] = [];
  private checkpoints: Map<string, string> = new Map();

  constructor(private client: OpenAI) {}

  addStep(step: ChainStep): this {
    this.steps.push(step);
    return this;
  }

  async execute(initialInput: string): Promise<string> {
    let current = initialInput;

    for (const step of this.steps) {
      if (step.transform) {
        current = step.transform(current);
      }

      const prompt = step.prompt.replace('{input}', current);
      const response = await this.client.chat.completions.create({
        model: 'gpt-4o',
        messages: [{ role: 'user', content: prompt }]
      });

      current = response.choices[0]?.message.content || '';
      this.checkpoints.set(step.name, current);
    }

    return current;
  }

  getCheckpoint(name: string): string | undefined {
    return this.checkpoints.get(name);
  }
}

// Usage
const chain = new AsyncPromptChain(client)
  .addStep({
    name: 'extract',
    prompt: 'Extract all dates from this text: {input}'
  })
  .addStep({
    name: 'sort',
    prompt: 'Sort these dates chronologically: {input}'
  });

const result = await chain.execute(inputText);