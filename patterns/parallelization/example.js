interface MapTask<T = string> {
  id: string;
  input: T;
}

interface MapResult<T = string> {
  taskId: string;
  result: T;
  status: 'success' | 'error';
  error?: string;
}

class ParallelMapper {
  private client: OpenAI;
  private concurrencyLimit: number;

  constructor(client: OpenAI, concurrencyLimit = 10) {
    this.client = client;
    this.concurrencyLimit = concurrencyLimit;
  }

  private async mapSingle<T, R>(
    prompt: (input: T) => string,
    task: MapTask<T>
  ): Promise<MapResult<R>> {
    try {
      const response = await this.client.chat.completions.create({
        model: 'gpt-4o',
        messages: [{ role: 'user', content: prompt(task.input) }]
      });

      return {
        taskId: task.id,
        result: response.choices[0]?.message.content as R,
        status: 'success'
      };
    } catch (error) {
      return {
        taskId: task.id,
        result: '' as R,
        status: 'error',
        error: String(error)
      };
    }
  }

  async mapReduce<T, R>(
    tasks: MapTask<T>[],
    mapFn: (input: T) => string,
    reduceFn: (results: MapResult<R>[]) => string
  ): Promise<R> {
    const promises = tasks.map(task => 
      this.mapSingle(mapFn, task)
    );

    const mapResults = await Promise.all(promises);
    
    const reduceResponse = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: reduceFn(mapResults) }]
    });

    return reduceResponse.choices[0]?.message.content as R;
  }
}

// Usage
const mapper = new ParallelMapper(client, { maxConcurrency: 20 });

const results = await mapper.mapReduce(
  [
    { id: 'doc1', input: 'Content of doc 1...' },
    { id: 'doc2', input: 'Content of doc 2...' },
  ],
  (doc) => `Summarize: ${doc}`,
  (results) => `Create a combined report:\n${results.map(r => r.result).join('\n')}`
);