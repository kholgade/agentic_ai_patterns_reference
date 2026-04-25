import { WebClient } from '@slack/web-api';

enum ApprovalStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  MODIFIED = 'modified'
}

interface ReviewRequest {
  id: string;
  content: string;
  context: Record<string, unknown>;
  status: ApprovalStatus;
  requestedAt: Date;
  reviewerComment?: string;
  modifiedContent?: string;
}

interface Reviewer {
  requestReview(request: ReviewRequest): Promise<ReviewRequest>;
}

class HitlWorkflow {
  constructor(
    private client: OpenAI,
    private reviewer: Reviewer,
    private alwaysRequireReview = false,
    private triggers: ((output: string) => boolean)[] = []
  ) {}

  private shouldReview(output: string): boolean {
    if (this.alwaysRequireReview) return true;
    return this.triggers.some(trigger => trigger(output));
  }

  async generate(prompt: string): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: prompt }]
    });
    return response.choices[0]?.message.content ?? '';
  }

  async execute(prompt: string, context: Record<string, unknown> = {}): Promise<{ output: string; review?: ReviewRequest }> {
    const output = await this.generate(prompt);
    
    if (!this.shouldReview(output)) {
      return { output };
    }

    const review = await this.reviewer.requestReview({
      id: crypto.randomUUID(),
      content: output,
      context,
      status: ApprovalStatus.PENDING,
      requestedAt: new Date()
    });

    return {
      output: review.status === ApprovalStatus.MODIFIED 
        ? review.modifiedContent ?? output 
        : output,
      review
    };
  }
}

class SlackReviewer implements Reviewer {
  constructor(private slack: WebClient, private channel: string) {}

  async requestReview(request: ReviewRequest): Promise<ReviewRequest> {
    await this.slack.chat.postMessage({
      channel: this.channel,
      text: `Review: ${request.id}`,
      blocks: [
        { type: 'section', text: { type: 'mrkdwn', text: `\`\`\`${request.content}\`\`\`` }},
        { type: 'actions', elements: [
          { type: 'button', text: { type: 'plain_text', text: 'Approve' }, style: 'primary' },
          { type: 'button', text: { type: 'plain_text', text: 'Reject' } }
        ]}
      ]
    });
    // Real implementation: wait for callback
    return request;
  }
}