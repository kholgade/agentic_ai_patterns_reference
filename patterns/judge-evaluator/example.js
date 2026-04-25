interface EvaluationCriteria {
  correctness: number;
  completeness: number;
  safety: number;
  style: number;
}

interface EvaluationResult {
  criteria: EvaluationCriteria;
  passed: boolean;
  feedback: string;
  details: string;
}

class JudgeAgent {
  constructor(private client: OpenAI, private threshold: number = 0.7) {}

  async evaluate(task: string, output: string): Promise<EvaluationResult> {
    const prompt = `Evaluate this output.

Task: ${task}

Output:
${output}

Rate 0-100 for: correctness, completeness, safety, style
Return JSON with scores, feedback, details`;

    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: prompt }],
      response_format: { type: 'json_object' }
    });

    const data = JSON.parse(response.choices[0]?.message.content ?? '{}');
    
    const criteria: EvaluationCriteria = {
      correctness: data.correctness ?? 0,
      completeness: data.completeness ?? 0,
      safety: data.safety ?? 0,
      style: data.style ?? 0
    };

    const weights = { correctness: 0.35, completeness: 0.30, safety: 0.20, style: 0.15 };
    const overallScore = 
      criteria.correctness * weights.correctness +
      criteria.completeness * weights.completeness +
      criteria.safety * weights.safety +
      criteria.style * weights.style;

    return {
      criteria,
      passed: overallScore >= this.threshold,
      feedback: data.feedback ?? '',
      details: data.details ?? ''
    };
  }
}

class ProducerAgent {
  constructor(private client: OpenAI) {}

  async produce(task: string): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: task }]
    });
    return response.choices[0]?.message.content ?? '';
  }
}

class JudgeEvaluatorWorkflow {
  constructor(
    private client: OpenAI,
    private maxAttempts: number = 3
  ) {}

  async execute(task: string): Promise<{ output: string; result: EvaluationResult }> {
    const judge = new JudgeAgent(this.client);
    const producer = new ProducerAgent(this.client);

    for (let attempt = 0; attempt < this.maxAttempts; attempt++) {
      const output = await producer.produce(task);
      const result = await judge.evaluate(task, output);

      if (result.passed) {
        return { output, result };
      }

      if (attempt < this.maxAttempts - 1) {
        task = `${task}\n\nFeedback: ${result.feedback}\nPlease improve.`;
      }
    }

    const output = await producer.produce(task);
    const result = await judge.evaluate(task, output);
    return { output, result };
  }
}