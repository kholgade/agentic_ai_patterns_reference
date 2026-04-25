interface Task {
  id: string;
  payload: any;
  result?: any;
  status: 'pending' | 'completed' | 'failed';
}

class RoundRobinAgent {
  name: string;
  completedTasks: Task[] = [];

  constructor(name: string) {
    this.name = name;
  }

  async process(task: Task): Promise<Task> {
    await new Promise(resolve => setTimeout(resolve, 100));
    task.result = `${this.name} processed: ${task.payload}`;
    task.status = 'completed';
    this.completedTasks.push(task);
    return task;
  }
}

class RoundRobinScheduler {
  private agents: RoundRobinAgent[] = [];
  private taskQueue: Task[] = [];
  private currentIndex = 0;

  addAgent(agent: RoundRobinAgent): void {
    this.agents.push(agent);
  }

  private getNextAgent(): RoundRobinAgent {
    if (this.agents.length === 0) {
      throw new Error("No agents available");
    }
    const agent = this.agents[this.currentIndex];
    this.currentIndex = (this.currentIndex + 1) % this.agents.length;
    return agent;
  }

  async submitTask(task: Task): Promise<void> {
    this.taskQueue.push(task);
  }

  async run(maxTasks?: number): Promise<number> {
    let processed = 0;
    
    while (maxTasks === undefined || processed < maxTasks) {
      const task = this.taskQueue.shift();
      if (!task) break;

      const agent = this.getNextAgent();
      await agent.process(task);
      processed++;
    }

    return processed;
  }

  async processTasks(payloads: any[]): Promise<Task[]> {
    const tasks = payloads.map((p, i) => ({
      id: `task_${i}`,
      payload: p,
      status: 'pending' as const
    }));

    for (const task of tasks) {
      await this.submitTask(task);
    }

    await this.run(tasks.length);
    return tasks;
  }
}