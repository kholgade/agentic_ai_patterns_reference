# Policy-Gated Tool Proxy

## Overview

Insert a transparent proxy between agents and tool servers that evaluates every tool call against a policy engine before forwarding, producing an immutable audit trail of all decisions. This pattern enforces security policies, compliance rules, and access control at the tool call level.

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│   Agent     │───▶│ Policy Proxy    │───▶│   Tool      │
│             │    │                  │    │   Server    │
└─────────────┘    │ 1. Intercept     │    └─────────────┘
                   │ 2. Evaluate      │
                   │ 3. Log           │
                   │ 4. Forward/Block │
                   └──────────────────┘
```

## Implementation

```python
from enum import Enum
from typing import Dict, Any

class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    MODIFY = "modify"  # Modify parameters before forwarding

class PolicyGatedProxy:
    def __init__(self, policy_engine, audit_logger):
        self.policy_engine = policy_engine
        self.audit = audit_logger
        self.tool_servers = {}
    
    def handle_tool_call(self, agent_id: str, tool_name: str, 
                         params: Dict) -> Any:
        """Intercept and evaluate tool call"""
        
        # Create evaluation context
        context = {
            'agent_id': agent_id,
            'tool_name': tool_name,
            'params': params,
            'timestamp': datetime.now().isoformat(),
            'request_id': generate_request_id()
        }
        
        # Evaluate against policies
        decision = self.policy_engine.evaluate(context)
        
        # Log decision (immutable audit trail)
        self.audit.log({
            'event': 'tool_call_evaluation',
            'context': context,
            'decision': decision,
            'policies_matched': decision['matched_policies']
        })
        
        # Enforce decision
        if decision['action'] == PolicyDecision.DENY:
            raise PolicyDeniedError(
                f"Tool call blocked: {decision['reason']}"
            )
        
        elif decision['action'] == PolicyDecision.REQUIRE_APPROVAL:
            approval = self._request_approval(context, decision)
            if not approval:
                raise PolicyDeniedError("Approval denied")
        
        elif decision['action'] == PolicyDecision.MODIFY:
            # Modify parameters per policy
            params = decision['modified_params']
        
        # Forward to tool server
        result = self._forward_to_tool(tool_name, params)
        
        # Log successful execution
        self.audit.log({
            'event': 'tool_call_completed',
            'request_id': context['request_id'],
            'result_summary': self._summarize_result(result)
        })
        
        return result
    
    def _request_approval(self, context: dict, decision: dict) -> bool:
        """Request human approval for policy exception"""
        # Send to approval system (Slack, email, dashboard)
        # Wait for response (with timeout)
        # Return True if approved
        pass
```

## Policy Examples

```python
class ToolCallPolicy:
    def evaluate(self, context: dict) -> PolicyDecision:
        # Example: Block database writes after hours
        if context['tool_name'] == 'database_write':
            hour = datetime.now().hour
            if hour < 6 or hour > 22:
                return PolicyDecision.DENY(
                    reason="Database writes only allowed 6AM-10PM"
                )
        
        # Example: Require approval for large financial transactions
        if context['tool_name'] == 'transfer_funds':
            amount = context['params'].get('amount', 0)
            if amount > 10000:
                return PolicyDecision.REQUIRE_APPROVAL(
                    reason=f"Transaction ${amount} requires approval"
                )
        
        # Example: Redact PII from tool parameters
        if context['tool_name'] == 'send_email':
            params = context['params'].copy()
            if 'body' in params:
                params['body'] = self._redact_pii(params['body'])
            return PolicyDecision.MODIFY(modified_params=params)
        
        return PolicyDecision.ALLOW()
```

## When to Use

- Enterprise environments with compliance requirements
- Multi-tenant systems with different access policies
- Financial/healthcare applications (regulated industries)
- When audit trail is required
- Centralized policy enforcement across many agents

## Related Patterns

- [Tool Permissioning](../tool-permissioning/) - Access control
- [Audit Logging](../audit-logging/) - Immutable audit trail
- [Human in the Loop](../human-in-the-loop/) - Approval workflows

## References

- [Policy-Gated Tool Proxy](https://agentic-patterns.com/patterns/policy-gated-tool-proxy)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [NIST Access Control Guidelines](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)