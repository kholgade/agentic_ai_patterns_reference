from enum import Enum
from dataclasses import dataclass
from typing import Callable, Awaitable
from datetime import datetime
import uuid

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"

@dataclass
class ReviewRequest:
    id: str
    content: str
    context: dict
    status: ApprovalStatus
    requested_at: datetime
    reviewed_at: datetime | None = None
    reviewer_comment: str | None = None
    modified_content: str | None = None

class HumanReviewer(Protocol):
    async def request_review(self, request: ReviewRequest) -> ReviewRequest:
        ...

class HitlWorkflow:
    def __init__(
        self,
        llm_client,
        reviewer: HumanReviewer,
        trigger_conditions: list[Callable[[str], bool]] | None = None,
        always_require_review: bool = False
    ):
        self.llm_client = llm_client
        self.reviewer = reviewer
        self.trigger_conditions = trigger_conditions or []
        self.always_require_review = always_require_review
    
    def should_review(self, output: str) -> bool:
        if self.always_require_review:
            return True
        return any(condition(output) for condition in self.trigger_conditions)
    
    async def generate(self, prompt: str) -> str:
        response = await self.llm_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    async def execute(self, prompt: str, context: dict = None) -> tuple[str, ReviewRequest]:
        output = await self.generate(prompt)
        
        if not self.should_review(output):
            return output, None
        
        review_request = ReviewRequest(
            id=str(uuid.uuid4()),
            content=output,
            context=context or {},
            status=ApprovalStatus.PENDING,
            requested_at=datetime.now()
        )
        
        reviewed = await self.reviewer.request_review(review_request)
        
        if reviewed.status == ApprovalStatus.APPROVED:
            return output, reviewed
        
        if reviewed.status == ApprovalStatus.MODIFIED:
            return reviewed.modified_content, reviewed
        
        return await self.execute(prompt, context)

class SlackReviewer:
    def __init__(self, slack_client, channel_id: str):
        self.slack_client = slack_client
        self.channel_id = channel_id
    
    async def request_review(self, request: ReviewRequest) -> ReviewRequest:
        await self.slack_client.chat.postMessage(
            channel=self.channel_id,
            text=f"Review requested for: {request.id}",
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"```{request.content[:1500]}```"}
                },
                {
                    "type": "actions",
                    "block_id": request.id,
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Approve"},
                            "action_id": "approve",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Reject"},
                            "action_id": "reject"
                        }
                    ]
                }
            ]
        )
        # Wait for webhook callback with approval decision
        # This is simplified - real implementation needs async wait

# Usage
workflow = HitlWorkflow(
    llm_client=client,
    reviewer=SlackReviewer(slack, "#reviews"),
    trigger_conditions=[
        lambda o: "legal" in o.lower(),
        lambda o: "public" in o.lower(),
    ],
    always_require_review=False
)

final_output, review = await workflow.execute(
    "Generate a public announcement about our Q4 results"
)