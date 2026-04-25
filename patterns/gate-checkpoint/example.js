enum GateResult {
  PASS = 'pass',
  FAIL = 'fail',
  CONDITIONAL = 'conditional'
}

interface GateCheck {
  name: string;
  result: GateResult;
  message: string;
  score?: number;
}

interface Gate {
  check(output: string, context: Record<string, unknown>): Promise<GateCheck>;
}

class QualityGate implements Gate {
  constructor(
    private client: OpenAI,
    private minScore = 7.0
  ) {}

  async check(output: string): Promise<GateCheck> {
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: `Rate quality 0-10: ${output}` }]
    });

    const score = parseFloat(response.choices[0]?.message.content ?? '0');
    return {
      name: 'quality',
      result: score >= this.minScore ? GateResult.PASS : GateResult.FAIL,
      message: `Score: ${score}`,
      score
    };
  }
}

class SafetyGate implements Gate {
  constructor(
    private client: OpenAI,
    private blocked: string[] = []
  ) {}

  async check(output: string): Promise<GateCheck> {
    const violations = this.blocked.filter(term => 
      output.toLowerCase().includes(term.toLowerCase())
    );

    return {
      name: 'safety',
      result: violations.length ? GateResult.FAIL : GateResult.PASS,
      message: violations.length ? `Blocked: ${violations}` : 'Passed'
    };
  }
}

class GatedWorkflow {
  private stages: { name: string; prompt: string; gates: Gate[] }[] = [];

  addStage(name: string, prompt: string, gates: Gate[] = []): this {
    this.stages.push({ name, prompt, gates });
    return this;
  }

  async execute(input: string): Promise<{ output: string; checks: GateCheck[] }> {
    let current = input;
    const allChecks: GateCheck[] = [];

    for (const stage of this.stages) {
      const prompt = stage.prompt.replace('{input}', current);
      const response = await this.client.chat.completions.create({
        model: 'gpt-4o',
        messages: [{ role: 'user', content: prompt }]
      });

      current = response.choices[0]?.message.content ?? '';
      const checks = await Promise.all(
        stage.gates.map(gate => gate.check(current, {}))
      );

      const failed = checks.filter(c => c.result === GateResult.FAIL);
      if (failed.length) {
        throw new Error(`Gates failed: ${failed.map(f => f.message)}`);
      }

      allChecks.push(...checks);
    }

    return { output: current, checks: allChecks };
  }
}