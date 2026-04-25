interface Pheromone {
  strength: number;
  agentId: string;
  content: any;
  timestamp: number;
}

interface Agent {
  id: string;
  capability: string;
  state: 'exploring' | 'communicating' | 'evaluating' | 'resting';
  memory: any[];
  neighbors: string[];
}

class AgentSwarm {
  private agents: Map<string, Agent> = new Map();
  private pheromones: Pheromone[] = [];
  private sharedMemory: Map<string, any> = new Map();

  addAgent(id: string, capability: string): void {
    this.agents.set(id, {
      id,
      capability,
      state: 'exploring',
      memory: [],
      neighbors: []
    });
  }

  private discoverNeighbors(agent: Agent): void {
    const agentIds = [...this.agents.keys()].filter(a => a !== agent.id);
    const count = Math.min(3, agentIds.length);
    agent.neighbors = this.shuffle(agentIds).slice(0, count);
  }

  private depositPheromone(agentId: string, content: any): void {
    this.pheromones.push({
      strength: 1.0,
      agentId,
      content,
      timestamp: Date.now()
    });
  }

  private sensePheromones(agent: Agent): Pheromone[] {
    this.decayPheromones();
    return this.pheromones
      .filter(p => p.strength > 0.1)
      .sort((a, b) => b.strength - a.strength)
      .slice(0, 5);
  }

  private decayPheromones(): void {
    this.pheromones = this.pheromones
      .map(p => ({ ...p, strength: p.strength * 0.95 }))
      .filter(p => p.strength > 0.01);
  }

  async solve(problem: string, numAgents: number = 5): Promise<any> {
    const agentIds = [...this.agents.keys()].slice(0, numAgents);
    
    const tasks = agentIds.map(id => 
      this.runAgent(this.agents.get(id)!, problem)
    );

    const results = await Promise.all(tasks);
    return this.aggregateResults(results.filter(r => r !== null));
  }

  private async runAgent(agent: Agent, problem: string): Promise<any> {
    agent.state = 'exploring';
    this.discoverNeighbors(agent);

    const localResult = `Agent ${agent.id} explored: ${problem.substring(0, 20)}`;
    agent.memory.push(localResult);

    agent.state = 'communicating';
    this.depositPheromone(agent.id, localResult);

    const pheromones = this.sensePheromones(agent);
    pheromones.forEach(p => agent.memory.push(p.content));

    agent.state = 'evaluating';
    return agent.memory[agent.memory.length - 1];
  }

  private aggregateResults(results: any[]): any {
    return `Aggregated ${results.length} solutions from swarm`;
  }

  private shuffle<T>(array: T[]): T[] {
    return array.sort(() => Math.random() - 0.5);
  }
}