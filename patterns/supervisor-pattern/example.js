interface Task {
  id: string;
  description: string;
  assignedWorker?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  result?: string;
}

interface WorkerState {
  name: string;
  status: 'idle' | 'busy' | 'completed' | 'failed';
  currentTask?: string;
}

interface WorkerAgent {
  execute(task: Task): Promise<string>;
}

class Supervisor {
  private workers: Map<string, WorkerAgent> = new Map();
  private workerStates: Map<string, WorkerState> = new Map();
  private taskQueue: Task[] = [];
  private maxConcurrent = 3;

  registerWorker(name: string, worker: WorkerAgent): void {
    this.workers.set(name, worker);
    this.workerStates.set(name, { name, status: 'idle' });
  }

  async submitTask(task: Task): Promise<void> {
    this.taskQueue.push(task);
    await this.processQueue();
  }

  private async processQueue(): Promise<void> {
    const busyWorkers = [...this.workerStates.values()]
      .filter(s => s.status === 'busy').length;
    
    if (busyWorkers >= this.maxConcurrent) return;

    const availableWorker = [...this.workerStates.entries()]
      .find(([_, s]) => s.status === 'idle');

    if (!availableWorker) return;

    const task = this.taskQueue.shift();
    if (!task) return;

    const [workerName, _] = availableWorker;
    task.assignedWorker = workerName;
    task.status = 'in_progress';
    
    this.workerStates.set(workerName, { 
      name: workerName, 
      status: 'busy', 
      currentTask: task.id 
    });

    try {
      const result = await this.workers.get(workerName)!.execute(task);
      task.result = result;
      task.status = 'completed';
      this.workerStates.set(workerName, { name: workerName, status: 'completed' });
    } catch (error) {
      task.status = 'failed';
      this.workerStates.set(workerName, { name: workerName, status: 'failed' });
    }

    if (this.taskQueue.length > 0) {
      await this.processQueue();
    }
  }

  async getStatus(): Promise<Record<string, string>> {
    const status: Record<string, string> = {};
    this.workerStates.forEach((state, name) => {
      status[name] = state.status;
    });
    return status;
  }
}