# Tool Permissioning

## Overview

Fine-grained access control for agent tool capabilities. Tool permissioning ensures that agents can only access tools and data appropriate to their role, user context, and operational constraints. This pattern prevents privilege escalation, unauthorized data access, and unintended tool usage.

Unlike simple tool whitelisting, tool permissioning implements dynamic, context-aware policies that consider:
- User identity and permissions
- Agent role and capabilities
- Operational context (time, location, request type)
- Risk level of the requested operation
- Compliance and audit requirements

## Core Components

### 1. Policy Engine
Defines and evaluates access control policies:
```python
class ToolPolicy:
    def __init__(self):
        self.policies = []
        
    def add_policy(self, policy: PolicyRule):
        self.policies.append(policy)
        
    def evaluate(self, context: ToolCallContext) -> PermissionResult:
        for policy in self.policies:
            result = policy.evaluate(context)
            if result.decision != "NOT_APPLICABLE":
                return result
        return PermissionResult.DENY_DEFAULT()
```

### 2. Permission Levels
- **DENY** - Explicitly blocked
- **ALLOW** - Explicitly permitted
- **REQUIRE_APPROVAL** - Needs human authorization
- **ALLOW_WITH_AUDIT** - Permitted but logged
- **NOT_APPLICABLE** - Policy doesn't apply

### 3. Context Attributes
- User identity, roles, groups
- Agent identity and capabilities
- Tool name and parameters
- Time of day, location
- Request history and rate
- Data sensitivity classification

## Implementation

### Policy-Based Access Control

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

class PermissionDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    ALLOW_WITH_AUDIT = "allow_with_audit"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class PermissionResult:
    decision: PermissionDecision
    reason: str
    required_approver: str = None
    conditions: List[str] = None

@dataclass
class ToolCallContext:
    user_id: str
    user_roles: List[str]
    agent_id: str
    tool_name: str
    tool_params: Dict[str, Any]
    timestamp: datetime
    request_id: str
    data_sensitivity: str = "normal"  # normal, confidential, restricted

class PolicyRule:
    def evaluate(self, context: ToolCallContext) -> PermissionResult:
        raise NotImplementedError

class RoleBasedPolicy(PolicyRule):
    def __init__(self, allowed_roles: List[str], tools: List[str]):
        self.allowed_roles = allowed_roles
        self.tools = tools
        
    def evaluate(self, context: ToolCallContext) -> PermissionResult:
        if context.tool_name not in self.tools:
            return PermissionResult(PermissionDecision.NOT_APPLICABLE, "Tool not covered")
            
        if any(role in self.allowed_roles for role in context.user_roles):
            return PermissionResult(PermissionDecision.ALLOW, f"User has role in {self.allowed_roles}")
        else:
            return PermissionResult(PermissionDecision.DENY, f"Requires roles: {self.allowed_roles}")

class SensitiveDataPolicy(PolicyRule):
    def __init__(self, restricted_tools: List[str]):
        self.restricted_tools = restricted_tools
        
    def evaluate(self, context: ToolCallContext) -> PermissionResult:
        if context.tool_name not in self.restricted_tools:
            return PermissionResult(PermissionDecision.NOT_APPLICABLE, "Tool not restricted")
            
        if context.data_sensitivity == "restricted":
            return PermissionResult(
                PermissionDecision.REQUIRE_APPROVAL,
                "Restricted data access requires approval",
                required_approver="security-team"
            )
        elif context.data_sensitivity == "confidential":
            return PermissionResult(
                PermissionDecision.ALLOW_WITH_AUDIT,
                "Confidential data access logged",
                conditions=["audit_log_required"]
            )
        else:
            return PermissionResult(PermissionDecision.ALLOW, "Normal sensitivity")

class TimeBasedPolicy(PolicyRule):
    def __init__(self, tools: List[str], allowed_hours: tuple):
        self.tools = tools
        self.allowed_hours = allowed_hours  # (start_hour, end_hour)
        
    def evaluate(self, context: ToolCallContext) -> PermissionResult:
        if context.tool_name not in self.tools:
            return PermissionResult(PermissionDecision.NOT_APPLICABLE, "Tool not covered")
            
        current_hour = context.timestamp.hour
        if self.allowed_hours[0] <= current_hour < self.allowed_hours[1]:
            return PermissionResult(PermissionDecision.ALLOW, "Within allowed hours")
        else:
            return PermissionResult(
                PermissionDecision.DENY,
                f"Only allowed between {self.allowed_hours[0]}:00 and {self.allowed_hours[1]}:00"
            )

class RateLimitPolicy(PolicyRule):
    def __init__(self, tools: List[str], max_calls: int, window_seconds: int):
        self.tools = tools
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.call_history = defaultdict(list)
        
    def evaluate(self, context: ToolCallContext) -> PermissionResult:
        if context.tool_name not in self.tools:
            return PermissionResult(PermissionDecision.NOT_APPLICABLE, "Tool not covered")
            
        key = f"{context.user_id}:{context.tool_name}"
        now = context.timestamp.timestamp()
        
        # Clean old entries
        self.call_history[key] = [
            ts for ts in self.call_history[key]
            if now - ts < self.window_seconds
        ]
        
        if len(self.call_history[key]) >= self.max_calls:
            return PermissionResult(
                PermissionDecision.DENY,
                f"Rate limit exceeded: {self.max_calls} calls per {self.window_seconds}s"
            )
            
        self.call_history[key].append(now)
        return PermissionResult(PermissionDecision.ALLOW, "Within rate limit")
```

### Permission Manager

```python
class ToolPermissionManager:
    def __init__(self):
        self.policies: List[PolicyRule] = []
        self.audit_logger = AuditLogger()
        
    def add_policy(self, policy: PolicyRule):
        self.policies.append(policy)
        
    def check_permission(self, context: ToolCallContext) -> PermissionResult:
        # Evaluate all policies
        results = []
        for policy in self.policies:
            result = policy.evaluate(context)
            results.append(result)
            
            # Early return for explicit deny or approval requirement
            if result.decision in [PermissionDecision.DENY, PermissionDecision.REQUIRE_APPROVAL]:
                self.audit_logger.log_permission_check(context, result)
                return result
                
        # If no explicit decision, default to allow with audit
        final_result = PermissionResult(
            PermissionDecision.ALLOW_WITH_AUDIT,
            "Default allow (no matching policies)"
        )
        self.audit_logger.log_permission_check(context, final_result)
        return final_result
    
    def execute_with_permission(self, context: ToolCallContext, tool_executor: callable) -> Any:
        result = self.check_permission(context)
        
        if result.decision == PermissionDecision.DENY:
            raise PermissionDeniedError(f"Tool access denied: {result.reason}")
            
        elif result.decision == PermissionDecision.REQUIRE_APPROVAL:
            approval = self.request_approval(context, result.required_approver)
            if not approval:
                raise PermissionDeniedError("Approval denied")
                
        elif result.decision == PermissionDecision.ALLOW_WITH_AUDIT:
            self.audit_logger.log_tool_execution(context)
            
        # Execute the tool
        return tool_executor(context.tool_name, context.tool_params)
    
    def request_approval(self, context: ToolCallContext, approver: str) -> bool:
        # Send approval request to approver
        # Wait for response (with timeout)
        # Return True if approved, False otherwise
        pass
```

### Tool Capability Registry

```python
class ToolCapability:
    def __init__(self, name: str, sensitivity: str, risk_level: str):
        self.name = name
        self.sensitivity = sensitivity  # public, internal, confidential, restricted
        self.risk_level = risk_level  # low, medium, high, critical
        self.required_roles = []
        self.allowed_user_groups = []
        self.max_rate_limit = None
        
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolCapability] = {}
        
    def register_tool(self, capability: ToolCapability):
        self.tools[capability.name] = capability
        
    def get_tool_capability(self, tool_name: str) -> ToolCapability:
        return self.tools.get(tool_name)
        
    def classify_request(self, tool_name: str, params: Dict) -> str:
        tool = self.tools.get(tool_name)
        if not tool:
            return "unknown"
            
        # Check if params reference sensitive data
        if self.contains_sensitive_data(params):
            return "restricted"
        elif tool.sensitivity == "confidential":
            return "confidential"
        else:
            return "normal"
    
    def contains_sensitive_data(self, params: Dict) -> bool:
        # Check for patterns like SSN, credit cards, passwords, etc.
        sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
            r'password',
            r'secret',
            r'api_key',
        ]
        
        for value in str(params).lower().split():
            for pattern in sensitive_patterns:
                if re.search(pattern, value, re.I):
                    return True
        return False
```

## Policy Configuration Example

```python
def setup_default_policies(permission_manager: ToolPermissionManager):
    # Admin tools - only for admin roles
    permission_manager.add_policy(
        RoleBasedPolicy(
            allowed_roles=["admin", "security-admin"],
            tools=["delete_user", "export_all_data", "modify_permissions"]
        )
    )
    
    # Financial tools - require approval for large amounts
    permission_manager.add_policy(
        FinancialTransactionPolicy(
            tools=["transfer_funds", "process_payment"],
            approval_threshold=10000  # $10,000
        )
    )
    
    # Data export - time restricted
    permission_manager.add_policy(
        TimeBasedPolicy(
            tools=["export_data", "bulk_download"],
            allowed_hours=(9, 18)  # 9 AM to 6 PM only
        )
    )
    
    # Rate limiting on search
    permission_manager.add_policy(
        RateLimitPolicy(
            tools=["search_database", "query_api"],
            max_calls=100,
            window_seconds=60
        )
    )
    
    # Sensitive data access
    permission_manager.add_policy(
        SensitiveDataPolicy(
            restricted_tools=["access_pii", "view_financial_records", "read_health_data"]
        )
    )
```

## Integration with Agent Systems

```python
class SecureAgent:
    def __init__(self, permission_manager: ToolPermissionManager):
        self.permission_manager = permission_manager
        self.tool_executor = ToolExecutor()
        
    def execute_tool(self, tool_name: str, params: Dict, user_context: UserContext) -> Any:
        context = ToolCallContext(
            user_id=user_context.user_id,
            user_roles=user_context.roles,
            agent_id=self.agent_id,
            tool_name=tool_name,
            tool_params=params,
            timestamp=datetime.now(),
            request_id=generate_request_id(),
            data_sensitivity=self.permission_manager.classify_request(tool_name, params)
        )
        
        return self.permission_manager.execute_with_permission(
            context,
            lambda name, p: self.tool_executor.execute(name, p)
        )
```

## Best Practices

1. **Principle of Least Privilege** - Grant minimum necessary permissions
2. **Explicit Deny by Default** - Unknown tools should be blocked
3. **Separation of Duties** - Critical operations require multiple approvers
4. **Audit All Access** - Log every tool access attempt
5. **Regular Policy Review** - Audit and update policies periodically
6. **Dynamic Policies** - Adapt permissions based on context
7. **Fail Secure** - On errors, deny access rather than allow

## When to Use

- Agents with access to sensitive data or critical systems
- Multi-tenant systems with different user permission levels
- Compliance-regulated environments (HIPAA, GDPR, SOX)
- Financial or healthcare applications
- Systems with irreversible or high-risk operations

## When NOT to Use

- Single-user personal tools with no sensitive operations
- Read-only agents with no modification capabilities
- Fully isolated test environments

## Related Patterns

- [Guardrails Pattern](../guardrails-pattern/) - Input/output validation
- [Gate Checkpoint](../gate-checkpoint/) - Automated approval gates
- [Human in the Loop](../human-in-the-loop/) - Human approval workflows
- [Audit Logging](../audit-logging/) - Security event tracking
- [Tool Use](../tool-use/) - Tool integration patterns

## References

- [NIST Access Control Guidelines](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [Role-Based Access Control (RBAC)](https://en.wikipedia.org/wiki/Role-based_access_control)
- [Attribute-Based Access Control (ABAC)](https://en.wikipedia.org/wiki/Attribute-based_access_control)
- [Principle of Least Privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege)