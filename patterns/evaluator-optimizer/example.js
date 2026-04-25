interface EvaluationResult {
  passed: boolean;
  score: number;
  feedback: string;
  issues: string[];
}

class Evaluator {
  constructor(
    private client: OpenAI,
    private criteria: string
  ) {}

  async evaluate(output: string): Promise<EvaluationResult> {
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{
        role: 'user',
        content: `Evaluate against ${this.criteria}:\n${output}`
      }]
    });

    const [status, scoreStr, feedback] = 
      response.choices[0]?.message.content.split('|');
    
    return {
      passed: status.trim().toUpperCase() === 'PASS',
      score: parseFloat(scoreStr),
      feedback: feedback?.trim() ?? '',
      issues: []
    };
  }
}

class Optimizer {
  constructor(private client: OpenAI) {}

  async optimize(output: string, feedback: string): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{
        role: 'user',
        content: `Improve based on feedback:\nOutput: ${output}\nFeedback: ${feedback}`
      }]
    });

    return response.choices[0]?.message.content ?? '';
  }
}

class EvalOptimizerPipeline {
  constructor(
    private client: OpenAI,
    private evaluator: Evaluator,
    private optimizer: Optimizer,
    private generationPrompt: string,
    private maxIterations = 5,
    private minScore = 8.0
  ) {}

  async run(context: string): Promise<{ result: string; iterations: number }> {
    let current = await this.generate(context);

    for (let i = 0; i < this.maxIterations; i++) {
      const evalResult = await this.evaluator.evaluate(current);

      if (evalResult.passed && evalResult.score >= this.minScore) {
        return { result: current, iterations: i + 1 };
      }

      current = await this.optimizer.optimize(current, evalResult.feedback);
    }

    return { result: current, iterations: this.maxIterations };
  }

  private async generate(context: string): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{
        role: 'user',
        content: this.generationPrompt.replace('{context}', context)
      }]
    });

    return response.choices[0]?.message.content ?? '';
  }
}