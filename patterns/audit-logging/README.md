# Audit Logging

## Overview

Comprehensive security event tracking for agentic AI systems. Audit logging provides visibility into agent behavior, tool usage, data access, and security events. Unlike standard application logging, audit logs are immutable, tamper-evident, and designed for security analysis, compliance, and incident investigation.

## What to Audit

### Security-Critical Events
- Authentication and authorization attempts
- Tool invocations and their parameters
- Data access (especially sensitive data)
- Secret/credential usage
- Permission grants and denials
- Configuration changes
- Agent state transitions

### Agent-Specific Events
- Prompt inputs and model outputs
- Reasoning traces (thoughts, plans)
- Tool call decisions and outcomes
- Memory operations (read/write)
- Multi-agent communications
- Human-in-the-loop interactions

### Compliance Events
- Data subject access requests
- Data modifications and deletions
- Policy violations
- Rate limit breaches
- Unusual behavior patterns

## Implementation

### Audit Log Schema

```python
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
import json
import hashlib

class AuditEventType(Enum):
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    
    # Authorization
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ROLE_ASSIGNED = "role_assigned"
    
    # Tool Usage
    TOOL_INVOCATION = "tool_invocation"
    TOOL_EXECUTION_SUCCESS = "tool_execution_success"
    TOOL_EXECUTION_FAILURE = "tool_execution_failure"
    
    # Data Access
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    
    # Secret Management
    SECRET_ACCESS = "secret_access"
    SECRET_ROTATION = "secret_rotation"
    
    # Agent Operations
    AGENT_START = "agent_start"
    AGENT_STOP = "agent_stop"
    AGENT_STATE_CHANGE = "agent_state_change"
    PROMPT_EXECUTED = "prompt_executed"
    MODEL_RESPONSE = "model_response"
    
    # Security Events
    POLICY_VIOLATION = "policy_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    INJECTION_ATTEMPT = "injection_attempt"

@dataclass
class AuditEvent:
    event_id: str
    event_type: AuditEventType
    timestamp: str
    actor_id: str  # User or agent ID
    actor_type: str  # user, agent, system
    resource: str  # What was accessed
    action: str  # What was done
    outcome: str  # success, failure, denied
    details: Dict[str, Any]
    source_ip: Optional[str]
    session_id: Optional[str]
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)
    
    def get_hash(self) -> str:
        """Create hash for integrity verification"""
        return hashlib.sha256(self.to_json().encode()).hexdigest()

class AuditLogger:
    def __init__(self, storage_backend, include_hash_chain: bool = True):
        self.storage = storage_backend  # Database, file, SIEM
        self.include_hash_chain = True
        self.previous_hash = None
        
    def log(self, event: AuditEvent) -> None:
        """Log audit event with integrity protection"""
        
        # Add previous event hash for chain integrity
        if self.include_hash_chain and self.previous_hash:
            event.details['previous_event_hash'] = self.previous_hash
        
        # Serialize event
        event_json = event.to_json()
        
        # Calculate current hash
        current_hash = hashlib.sha256(event_json.encode()).hexdigest()
        event.details['event_hash'] = current_hash
        
        # Store event
        self.storage.store(event_json)
        
        # Update chain
        self.previous_hash = current_hash
        
        # Async: Send to SIEM if configured
        self._send_to_siem(event)
    
    def log_tool_invocation(self, agent_id: str, tool_name: str, 
                           params: Dict, outcome: str) -> None:
        """Convenience method for tool logging"""
        event = AuditEvent(
            event_id=generate_event_id(),
            event_type=AuditEventType.TOOL_INVOCATION,
            timestamp=datetime.now().isoformat(),
            actor_id=agent_id,
            actor_type="agent",
            resource=f"tool:{tool_name}",
            action="invoke",
            outcome=outcome,
            details={
                "tool_name": tool_name,
                "parameters": self._sanitize_params(params),
            },
            source_ip=None,
            session_id=get_current_session()
        )
        self.log(event)
    
    def log_data_access(self, user_id: str, data_type: str, 
                       record_id: str, outcome: str) -> None:
        """Log data access for compliance"""
        event = AuditEvent(
            event_id=generate_event_id(),
            event_type=AuditEventType.DATA_READ,
            timestamp=datetime.now().isoformat(),
            actor_id=user_id,
            actor_type="user",
            resource=f"data:{data_type}:{record_id}",
            action="read",
            outcome=outcome,
            details={
                "data_type": data_type,
                "record_id": record_id,
            },
            source_ip=get_client_ip(),
            session_id=get_current_session()
        )
        self.log(event)
    
    def log_policy_violation(self, actor_id: str, policy_name: str,
                            context: Dict) -> None:
        """Log security policy violations"""
        event = AuditEvent(
            event_id=generate_event_id(),
            event_type=AuditEventType.POLICY_VIOLATION,
            timestamp=datetime.now().isoformat(),
            actor_id=actor_id,
            actor_type="agent",
            resource=f"policy:{policy_name}",
            action="violation",
            outcome="blocked",
            details=context,
            source_ip=None,
            session_id=get_current_session()
        )
        self.log(event)
        # Also trigger alert
        self._trigger_alert(event)
    
    def _sanitize_params(self, params: Dict) -> Dict:
        """Remove sensitive data from logged parameters"""
        sensitive_keys = ['password', 'secret', 'token', 'api_key', 'credential']
        sanitized = {}
        
        for key, value in params.items():
            if any(s in key.lower() for s in sensitive_keys):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _send_to_siem(self, event: AuditEvent) -> None:
        """Forward to SIEM system (async)"""
        pass
    
    def _trigger_alert(self, event: AuditEvent) -> None:
        """Trigger security alert"""
        pass
```

### Storage Backends

```python
class DatabaseAuditStorage:
    """Store audit logs in database with immutability"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self._create_table()
    
    def _create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                actor_type TEXT NOT NULL,
                resource TEXT,
                action TEXT,
                outcome TEXT,
                details JSONB,
                event_hash TEXT,
                previous_hash TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        # Create index for common queries
        self.db.execute("""
            CREATE INDEX idx_audit_actor_time 
            ON audit_logs(actor_id, timestamp)
        """)
        self.db.execute("""
            CREATE INDEX idx_audit_event_type 
            ON audit_logs(event_type)
        """)
    
    def store(self, event_json: str) -> None:
        event = json.loads(event_json)
        self.db.execute("""
            INSERT INTO audit_logs 
            (id, event_type, timestamp, actor_id, actor_type, 
             resource, action, outcome, details, event_hash, previous_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event['event_id'],
            event['event_type'],
            event['timestamp'],
            event['actor_id'],
            event['actor_type'],
            event['resource'],
            event['action'],
            event['outcome'],
            json.dumps(event['details']),
            event['details'].get('event_hash'),
            event['details'].get('previous_event_hash')
        ))
        self.db.commit()

class ImmutableFileAuditStorage:
    """Append-only file storage with integrity"""
    
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = self._get_current_log_file()
        self.file_handle = open(self.current_file, 'a')
        
    def _get_current_log_file(self) -> Path:
        """Get current log file (rotate daily)"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.log_dir / f"audit_{today}.log"
    
    def store(self, event_json: str) -> None:
        # Append to file
        self.file_handle.write(event_json + '\n')
        self.file_handle.flush()
        
        # Check for rotation
        if self._should_rotate():
            self.file_handle.close()
            self.current_file = self._get_current_log_file()
            self.file_handle = open(self.current_file, 'a')
    
    def _should_rotate(self) -> bool:
        """Check if file should be rotated"""
        if not self.current_file.exists():
            return False
        
        # Rotate if file is too large or date changed
        size = self.current_file.stat().st_size
        return size > 100 * 1024 * 1024  # 100MB
    
    def verify_integrity(self) -> bool:
        """Verify log chain integrity"""
        previous_hash = None
        
        with open(self.current_file, 'r') as f:
            for line in f:
                event = json.loads(line)
                
                # Verify previous hash
                if previous_hash and event['details'].get('previous_event_hash') != previous_hash:
                    return False
                
                # Verify event hash
                event_copy = event.copy()
                stored_hash = event_copy['details'].pop('event_hash', None)
                calculated_hash = hashlib.sha256(
                    json.dumps(event_copy, default=str).encode()
                ).hexdigest()
                
                if stored_hash != calculated_hash:
                    return False
                
                previous_hash = stored_hash
        
        return True
```

### Agent Integration

```python
class AuditableAgent:
    def __init__(self, agent_id: str, audit_logger: AuditLogger):
        self.agent_id = agent_id
        self.audit_logger = audit_logger
        self.tool_executor = SecureToolExecutor()
        
    def execute(self, task: str, user_context: UserContext) -> str:
        # Log agent start
        self.audit_logger.log(AuditEvent(
            event_id=generate_event_id(),
            event_type=AuditEventType.AGENT_START,
            timestamp=datetime.now().isoformat(),
            actor_id=self.agent_id,
            actor_type="agent",
            resource="agent:execution",
            action="start",
            outcome="success",
            details={"task": task[:100]},  # Truncate for log
            source_ip=user_context.ip,
            session_id=user_context.session_id
        ))
        
        try:
            # Execute with auditing
            result = self._execute_with_audit(task, user_context)
            
            # Log success
            self.audit_logger.log(AuditEvent(
                event_id=generate_event_id(),
                event_type=AuditEventType.AGENT_STOP,
                timestamp=datetime.now().isoformat(),
                actor_id=self.agent_id,
                actor_type="agent",
                resource="agent:execution",
                action="complete",
                outcome="success",
                details={"result_length": len(result)},
                source_ip=user_context.ip,
                session_id=user_context.session_id
            ))
            
            return result
            
        except Exception as e:
            # Log failure
            self.audit_logger.log(AuditEvent(
                event_id=generate_event_id(),
                event_type=AuditEventType.AGENT_STOP,
                timestamp=datetime.now().isoformat(),
                actor_id=self.agent_id,
                actor_type="agent",
                resource="agent:execution",
                action="fail",
                outcome="error",
                details={"error": str(e)},
                source_ip=user_context.ip,
                session_id=user_context.session_id
            ))
            raise
    
    def _execute_with_audit(self, task: str, user_context: UserContext) -> str:
        # Execute task with tool call auditing
        for tool_call in self.plan_tools(task):
            self.audit_logger.log_tool_invocation(
                agent_id=self.agent_id,
                tool_name=tool_call.name,
                params=tool_call.params,
                outcome="initiated"
            )
            
            try:
                result = self.tool_executor.execute(tool_call)
                
                self.audit_logger.log_tool_invocation(
                    agent_id=self.agent_id,
                    tool_name=tool_call.name,
                    params=tool_call.params,
                    outcome="success"
                )
                
            except Exception as e:
                self.audit_logger.log_tool_invocation(
                    agent_id=self.agent_id,
                    tool_name=tool_call.name,
                    params=tool_call.params,
                    outcome="failure"
                )
                raise
        
        return self.generate_response()
```

### Query and Analysis

```python
class AuditQueryEngine:
    def __init__(self, audit_storage):
        self.storage = audit_storage
    
    def get_actor_timeline(self, actor_id: str, 
                          start_time: datetime, 
                          end_time: datetime) -> List[AuditEvent]:
        """Get all events for an actor in time range"""
        return self.storage.query("""
            SELECT * FROM audit_logs
            WHERE actor_id = ?
            AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """, (actor_id, start_time.isoformat(), end_time.isoformat()))
    
    def find_security_events(self, event_types: List[AuditEventType],
                            limit: int = 100) -> List[AuditEvent]:
        """Find specific security events"""
        return self.storage.query("""
            SELECT * FROM audit_logs
            WHERE event_type IN (?)
            ORDER BY timestamp DESC
            LIMIT ?
        """, (event_types, limit))
    
    def detect_anomalies(self, actor_id: str, 
                        window_hours: int = 24) -> List[Dict]:
        """Detect unusual patterns"""
        events = self.get_actor_timeline(
            actor_id,
            datetime.now() - timedelta(hours=window_hours),
            datetime.now()
        )
        
        anomalies = []
        
        # Check for unusual activity volume
        if len(events) > 1000:  # Threshold
            anomalies.append({
                "type": "high_activity_volume",
                "count": len(events),
                "window_hours": window_hours
            })
        
        # Check for permission denials
        denials = [e for e in events if e.outcome == "denied"]
        if len(denials) > 10:
            anomalies.append({
                "type": "multiple_permission_denials",
                "count": len(denials)
            })
        
        # Check for tool usage patterns
        tool_events = [e for e in events if e.event_type == AuditEventType.TOOL_INVOCATION]
        unique_tools = len(set(e.resource for e in tool_events))
        if unique_tools > 20:
            anomalies.append({
                "type": "unusual_tool_diversity",
                "unique_tools": unique_tools
            })
        
        return anomalies
    
    def generate_compliance_report(self, start_date: str, 
                                   end_date: str) -> Dict:
        """Generate compliance report"""
        return {
            "period": {"start": start_date, "end": end_date},
            "total_events": self._count_events(start_date, end_date),
            "events_by_type": self._group_by_type(start_date, end_date),
            "policy_violations": self._count_violations(start_date, end_date),
            "data_access_summary": self._summarize_data_access(start_date, end_date),
            "security_incidents": self._count_incidents(start_date, end_date),
        }
```

## Best Practices

1. **Write-Once Storage**: Audit logs should be immutable
2. **Hash Chain**: Each event references previous for integrity
3. **Separation**: Store audit logs separately from application logs
4. **Retention**: Define and enforce retention policies
5. **Access Control**: Restrict who can view audit logs
6. **Real-time Monitoring**: Alert on critical security events
7. **Regular Review**: Periodic audit log analysis
8. **Compliance Mapping**: Map events to compliance requirements

## When to Use

- All production agentic AI systems
- Compliance-regulated environments (HIPAA, GDPR, SOX, PCI-DSS)
- Multi-tenant systems
- Systems handling sensitive data
- Financial or healthcare applications

## When NOT to Use

- Local development (use simplified logging)
- Personal tools with no sensitive operations

## Related Patterns

- [Guardrails Pattern](../guardrails-pattern/) - Input/output validation
- [Tool Permissioning](../tool-permissioning/) - Access control
- [Secret Handling](../secret-handling/) - Credential security
- [Prompt Injection Defense](../prompt-injection-defense/) - Attack prevention

## References

- [NIST Audit and Accountability Guidelines](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [PCI-DSS Logging Requirements](https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0_1.pdf)
- [GDPR Audit Trail Requirements](https://gdpr.eu/accountability/)
- [HIPAA Audit Controls](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html)