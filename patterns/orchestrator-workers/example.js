interface Task {
  id: string;
  description: string;
  workerType: string;
  priority: number;
  result?: string;
  status: 'pending' | 'success' | 'error' | 'timeout';
  error?: string;
}

interface Worker {
  execute(task: Task): Promise<string>;
}

class Orchestrator {
  private client: OpenAI;
  private workers: Map<string, Worker> = new Map();
  private maxConcurrent = 5;

  registerWorker(type: string, worker: Worker): void {
    this.workers.set(type, worker);
  }

  async decompose(input: string): Promise<Task[]> {
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{
        role: 'user',
        content: `Break into tasks: ${input}`
      }]
    });

    const lines = response.choices[0]?.message.content.split('\n');
    return lines?.map((line, i) => {
      const [id, desc, type, priority] = line.split('|');
      return { id: id.trim(), description: desc.trim(), workerType: type.trim(), priority: parseInt(priority), status: 'pending' as const };
    }) ?? [];
  }

  async execute(input: string): Promise<string> {
    const tasks = await this.decompose(input);
    const results = await Promise.all(
      tasks.map(task => this.executeTask(task))
    );

    const aggregation = results
      .filter(t => t.status === 'success')
      .map(t => `Task ${t.id}: ${t.result}`)
      .join('\n\n');

    const final = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: `Combine: ${aggregation}` }]
    });

    return final.choices[0]?.message.content ?? '';
  }

  private async executeTask(task: Task): Promise<Task> {
    const worker = this.workers.get(task.workerType);
    if (!worker) {
      task.status = 'error';
      task.error = 'Unknown worker type';
      return task;
    }

    try {
      task.result = await worker.execute(task);
      task.status = 'success';
    } catch (e) {
      task.status = 'error';
      task.error = String(e);
    }
    return task;
  }
}