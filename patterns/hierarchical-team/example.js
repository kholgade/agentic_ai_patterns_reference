enum Role {
  EXECUTIVE = 'executive',
  MANAGER = 'manager',
  TEAM_LEAD = 'team_lead',
  WORKER = 'worker'
}

interface Agent {
  id: string;
  role: Role;
  name: string;
  reportsTo?: string;
  team?: string;
}

interface Task {
  id: string;
  description: string;
  assignee?: string;
  status: 'pending' | 'completed';
  result?: string;
}

class HierarchicalTeam {
  private agents: Map<string, Agent> = new Map();
  private taskQueue: Map<string, Task[]> = new Map();

  addAgent(agent: Agent): void {
    this.agents.set(agent.id, agent);
    this.taskQueue.set(agent.id, []);
  }

  getReports(managerId: string): Agent[] {
    return [...this.agents.values()].filter(a => a.reportsTo === managerId);
  }

  async assignTask(task: Task, agentId: string): Promise<void> {
    task.assignee = agentId;
    this.taskQueue.get(agentId)?.push(task);
  }

  async executeTask(agentId: string, task: Task): Promise<string> {
    const agent = this.agents.get(agentId);
    await new Promise(r => setTimeout(r, 100));
    task.result = `${agent?.name} completed: ${task.description}`;
    task.status = 'completed';
    return task.result;
  }

  async processTeam(agentId: string): Promise<string[]> {
    const results: string[] = [];
    const queue = this.taskQueue.get(agentId) ?? [];
    
    while (queue.length > 0) {
      const task = queue.shift()!;
      const result = await this.executeTask(agentId, task);
      results.push(result);
    }
    
    return results;
  }

  async executeHierarchical(directive: string): Promise<string> {
    const executive = [...this.agents.values()].find(a => a.role === Role.EXECUTIVE);
    if (!executive) return 'No executive';

    await this.assignTask({ id: 't1', description: `Plan: ${directive}` }, executive.id);
    await this.processTeam(executive.id);

    for (const manager of this.getReports(executive.id)) {
      await this.assignTask({ id: `${manager.id}_t1`, description: `Coordinate: ${directive}` }, manager.id);
      await this.processTeam(manager.id);

      for (const worker of this.getReports(manager.id)) {
        await this.assignTask({ id: `${worker.id}_t1`, description: `Execute: ${directive}` }, worker.id);
        await this.processTeam(worker.id);
      }
    }

    return `Completed: ${directive}`;
  }
}