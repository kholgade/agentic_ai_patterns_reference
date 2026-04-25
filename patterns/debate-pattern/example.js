enum DebateRole {
  PROPONENT = 'proponent',
  SKEPTIC = 'skeptic',
  SYNTHESIST = 'synthesist',
  MODERATOR = 'moderator'
}

interface DebateRound {
  roundNumber: number;
  speaker: string;
  content: string;
}

class DebateAgent {
  constructor(
    private agentId: string,
    private role: DebateRole,
    private client: OpenAI
  ) {}

  private getSystemPrompt(): string {
    const prompts: Record<DebateRole, string> = {
      [DebateRole.PROPONENT]: 'You advocate for a position strongly.',
      [DebateRole.SKEPTIC]: 'You challenge arguments and identify weaknesses.',
      [DebateRole.SYNTHESIST]: 'You combine insights from all sides.',
      [DebateRole.MODERATOR]: 'You guide the discussion fairly.'
    };
    return prompts[this.role];
  }

  async respond(topic: string, positions: Record<string, string>, context: string): Promise<string> {
    const prompt = `${this.getSystemPrompt()}

Topic: ${topic}

Positions:
${Object.entries(positions).map(([k, v]) => `- ${k}: ${v}`).join('\n')}

Context: ${context}

Respond as ${this.role}:`;

    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: prompt }]
    });

    return response.choices[0]?.message.content ?? '';
  }
}

class DebateModerator {
  private agents: Map<DebateRole, DebateAgent> = new Map();

  addAgent(role: DebateRole, client: OpenAI): void {
    this.agents.set(role, new DebateAgent(role.value, role, client));
  }

  async runDebate(topic: string, numRounds: number = 3): Promise<string> {
    const positions: Record<string, string> = {};
    const rounds: DebateRound[] = [];

    const propAgent = this.agents.get(DebateRole.PROPONENT);
    const skepticAgent = this.agents.get(DebateRole.SKEPTIC);
    
    if (propAgent) {
      positions[DebateRole.PROPONENT] = await propAgent.respond(topic, {}, 'Present your position.');
    }
    if (skepticAgent) {
      positions[DebateRole.SKEPTIC] = await skepticAgent.respond(topic, positions, 'Present your counterargument.');
    }

    for (let round = 1; round <= numRounds; round++) {
      const context = rounds.slice(-4).map(r => `Round ${r.roundNumber} - ${r.speaker}: ${r.content}`).join('\n');

      for (const [role, agent] of this.agents) {
        const response = await agent.respond(topic, positions, context);
        rounds.push({ roundNumber: round, speaker: role.value, content: response });
        positions[role.value] = response;
      }
    }

    return this.produceSynthesis(topic, rounds);
  }

  private async produceSynthesis(topic: string, rounds: DebateRound[]): Promise<string> {
    const context = rounds.map(r => `${r.speaker}: ${r.content}`).join('\n\n');
    const prompt = `Debate on "${topic}":\n\n${context}\n\nProvide final synthesis:`;
    
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: prompt }]
    });
    
    return response.choices[0]?.message.content ?? '';
  }
}