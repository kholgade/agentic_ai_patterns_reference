import OpenAI from 'openai';

const StreamState = {
  IDLE: 'idle',
  GENERATING: 'generating',
  INTERRUPTED: 'interrupted',
  COMPLETED: 'completed'
};

const InterruptAction = {
  ABORT: 'abort',
  COMPLETE: 'complete',
  REGENERATE: 'regenerate'
};

class StreamingGenerator {
  constructor(client, options = {}) {
    this.client = client;
    this.onToken = options.onToken || (() => {});
    this.onComplete = options.onComplete || (() => {});
    this.onError = options.onError || (() => {});
    
    this.state = StreamState.IDLE;
    this.partialResponse = '';
    this.abortController = null;
    this.messages = [];
  }

  async *streamGenerate(messages, model = 'gpt-4o') {
    this.messages = messages;
    this.state = StreamState.GENERATING;
    this.partialResponse = '';
    this.abortController = new AbortController();
    
    try {
      const response = await this.client.chat.completions.create({
        model,
        messages,
        stream: true,
        max_tokens: 2000,
        stream_options: { include_usage: true }
      }, {
        signal: this.abortController.signal
      });

      for await (const chunk of response) {
        // Check if aborted
        if (this.abortController.signal.aborted) {
          this.state = StreamState.INTERRUPTED;
          yield { text: this.partialResponse, isFinal: false };
          return;
        }

        const delta = chunk.choices[0]?.delta;
        if (delta?.content) {
          this.partialResponse += delta.content;
          this.onToken(delta.content);
          yield { text: delta.content, isFinal: false };
        }

        if (chunk.choices[0]?.finish_reason) {
          this.state = StreamState.COMPLETED;
          this.onComplete(this.partialResponse);
          yield { text: this.partialResponse, isFinal: true };
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        this.state = StreamState.INTERRUPTED;
      } else {
        this.onError(error);
      }
      throw error;
    }
  }

  interrupt(action = InterruptAction.ABORT) {
    if (action === InterruptAction.ABORT) {
      this.abortController?.abort();
      this.state = StreamState.INTERRUPTED;
    } else if (action === InterruptAction.COMPLETE) {
      this.abortController?.abort();
      this.state = StreamState.COMPLETED;
    }
  }

  getPartialResponse() {
    return this.partialResponse;
  }

  getConversationWithPartial() {
    const messages = [...this.messages];
    if (this.partialResponse) {
      messages.push({ role: 'assistant', content: this.partialResponse });
    }
    return messages;
  }
}

class InterruptibleChat {
  constructor() {
    this.client = new OpenAI();
    this.conversation = [];
    this.generator = null;
  }

  async chat(userInput) {
    this.conversation.push({ role: 'user', content: userInput });
    
    this.generator = new StreamingGenerator(this.client, {
      onToken: (token) => process.stdout.write(token),
      onComplete: (response) => console.log('\n[Complete]'),
      onError: (error) => console.error('[Error]', error)
    });

    let fullResponse = '';
    
    for await (const chunk of this.generator.streamGenerate(this.conversation)) {
      fullResponse = chunk.text;
    }

    this.conversation.push({ role: 'assistant', content: fullResponse });
    return fullResponse;
  }

  interrupt(action = InterruptAction.ABORT) {
    if (this.generator) {
      this.generator.interrupt(action);
      
      if (action === InterruptAction.COMPLETE) {
        const partial = this.generator.getPartialResponse();
        this.conversation.push({ 
          role: 'assistant', 
          content: `${partial}[interrupted]` 
        });
      }
    }
  }

  regenerate() {
    if (this.generator) {
      const context = this.generator.getConversationWithPartial();
      this.conversation = context.slice(0, -1);
    }
  }
}