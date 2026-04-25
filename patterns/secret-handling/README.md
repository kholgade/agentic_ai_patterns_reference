# Secret Handling

## Overview

Secure management of sensitive credentials, API keys, tokens, and other secrets in agentic AI systems. Agents often require access to external services (databases, APIs, cloud resources) that need authentication. This pattern ensures secrets are never exposed in prompts, logs, or agent outputs, and are handled according to security best practices.

## Security Risks

### Secret Exposure Vectors
- **Prompt Leakage**: Secrets accidentally included in LLM context
- **Log Exposure**: Secrets written to application or debug logs
- **Output Leakage**: Agent reveals secrets in responses
- **Memory Inspection**: Secrets accessible in process memory
- **Version Control**: Secrets committed to code repositories
- **Agent Manipulation**: Prompt injection extracts secrets from context

## Core Principles

1. **Never in Prompts**: Secrets should never be passed to LLMs
2. **Least Privilege Access**: Agents get only required credentials
3. **Encryption at Rest**: Secrets encrypted when stored
4. **Rotation**: Regular credential rotation
5. **Audit Access**: All secret access logged and monitored
6. **Separation**: Secrets managed separately from application logic

## Implementation

### Secret Manager Interface

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict
from datetime import datetime, timedelta

class SecretManager(ABC):
    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret by name"""
        pass
    
    @abstractmethod
    def rotate_secret(self, secret_name: str) -> bool:
        """Rotate/refresh a secret"""
        pass
    
    @abstractmethod
    def audit_access(self, secret_name: str, accessed_by: str) -> None:
        """Log secret access for auditing"""
        pass
    
    @abstractmethod
    def validate_secret(self, secret_name: str) -> bool:
        """Check if secret is valid and not expired"""
        pass

class SecureSecretManager(SecretManager):
    def __init__(self, vault_client, encryption_key: bytes):
        self.vault = vault_client  # AWS Secrets Manager, HashiCorp Vault, etc.
        self.encryption_key = encryption_key
        self.access_cache = {}
        self.audit_logger = AuditLogger()
        
    def get_secret(self, secret_name: str, agent_id: str = None) -> str:
        # Validate agent has permission to access this secret
        if not self._check_agent_permission(agent_id, secret_name):
            raise PermissionDeniedError(f"Agent {agent_id} cannot access {secret_name}")
        
        # Check cache first (with TTL)
        cached = self._get_from_cache(secret_name)
        if cached:
            self.audit_access(secret_name, agent_id or "system")
            return cached
        
        # Retrieve from vault
        secret = self.vault.get_secret_value(secret_name)
        
        # Decrypt if needed
        if secret.is_encrypted:
            secret_value = self._decrypt(secret.encrypted_value)
        else:
            secret_value = secret.value
        
        # Cache with TTL
        self._cache_secret(secret_name, secret_value, ttl=secret.ttl)
        
        # Audit access
        self.audit_access(secret_name, agent_id or "system")
        
        return secret_value
    
    def _check_agent_permission(self, agent_id: str, secret_name: str) -> bool:
        # Check agent's allowed secrets list
        allowed_secrets = self._get_agent_allowed_secrets(agent_id)
        return secret_name in allowed_secrets
    
    def _decrypt(self, encrypted_value: bytes) -> str:
        from cryptography.fernet import Fernet
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_value).decode()
    
    def audit_access(self, secret_name: str, accessed_by: str) -> None:
        self.audit_logger.log_event(
            event_type="SECRET_ACCESS",
            secret_name=secret_name,
            accessed_by=accessed_by,
            timestamp=datetime.now().isoformat()
        )
```

### Agent Credential Injection

```python
class CredentialInjector:
    """
    Injects credentials into tool calls without exposing them to the LLM.
    The LLM requests tool usage, but credentials are added by the injector.
    """
    
    def __init__(self, secret_manager: SecretManager):
        self.secret_manager = secret_manager
        self.tool_credentials: Dict[str, List[str]] = {
            "database_query": ["DB_HOST", "DB_USER", "DB_PASSWORD"],
            "send_email": ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"],
            "cloud_api_call": ["AWS_ACCESS_KEY", "AWS_SECRET_KEY"],
            "payment_processor": ["STRIPE_API_KEY"],
        }
    
    def prepare_tool_call(self, tool_name: str, params: Dict, agent_id: str) -> Dict:
        """
        Add required credentials to tool call without exposing to LLM.
        LLM sees only: "I'll query the database"
        Actual execution includes credentials injected here.
        """
        required_secrets = self.tool_credentials.get(tool_name, [])
        
        # Retrieve secrets securely
        credentials = {}
        for secret_name in required_secrets:
            credentials[secret_name] = self.secret_manager.get_secret(
                secret_name, 
                agent_id
            )
        
        # Merge with original params (credentials separate from LLM-visible params)
        return {
            "tool_params": params,
            "credentials": credentials,  # Only visible to tool executor
            "agent_id": agent_id
        }
    
    def execute_secure_tool(self, tool_name: str, prepared_call: Dict) -> Any:
        """Execute tool with credentials, ensuring they're not logged"""
        tool_executor = self._get_tool_executor(tool_name)
        
        # Use secure execution context
        with SecureExecutionContext() as ctx:
            ctx.set_credentials(prepared_call["credentials"])
            result = tool_executor.execute(
                prepared_call["tool_params"],
                ctx.credentials
            )
        
        # Result should be sanitized before returning to LLM
        return self._sanitize_result(result)
    
    def _sanitize_result(self, result: Any) -> Any:
        """Remove any credential leakage from result"""
        if isinstance(result, str):
            # Remove potential credential patterns
            result = re.sub(r'[A-Za-z0-9]{32,}', '[REDACTED]', result)
            result = re.sub(r'password[\'"]?\s*[:=]\s*[\'"][^\'"]+[\'"]', 
                           'password=[REDACTED]', result, flags=re.I)
        return result
```

### Secure Context Management

```python
class SecureAgentContext:
    """
    Manages agent context without exposing secrets to the LLM.
    Secrets are used for tool execution but never added to prompt context.
    """
    
    def __init__(self, agent_id: str, secret_manager: SecretManager):
        self.agent_id = agent_id
        self.secret_manager = secret_manager
        self.context_messages = []  # Visible to LLM
        self.secure_state = {}  # Not visible to LLM
        
    def add_to_context(self, message: Dict):
        """Add message to LLM-visible context"""
        # Validate no secrets in message
        self._validate_no_secrets(message)
        self.context_messages.append(message)
        
    def set_secure_state(self, key: str, value: Any):
        """Store data that should not be visible to LLM"""
        self.secure_state[key] = value
        
    def get_secure_state(self, key: str) -> Any:
        return self.secure_state.get(key)
    
    def _validate_no_secrets(self, message: Dict):
        """Ensure message doesn't contain secret patterns"""
        secret_patterns = [
            r'api[_-]?key\s*[:=]\s*[\'"][^\'"]+[\'"]',
            r'password\s*[:=]\s*[\'"][^\'"]+[\'"]',
            r'secret\s*[:=]\s*[\'"][^\'"]+[\'"]',
            r'token\s*[:=]\s*[\'"][^\'"]{20,}[\'"]',
            r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
        ]
        
        message_str = str(message)
        for pattern in secret_patterns:
            if re.search(pattern, message_str, re.I):
                raise SecurityError(
                    f"Potential secret detected in context message. "
                    f"Pattern: {pattern}"
                )
    
    def build_prompt(self) -> str:
        """Build prompt from context messages only (no secrets)"""
        return "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.context_messages
        ])
```

### Secret Rotation

```python
class SecretRotator:
    def __init__(self, secret_manager: SecretManager):
        self.secret_manager = secret_manager
        self.rotation_schedule = {
            "DB_PASSWORD": timedelta(days=30),
            "API_KEY": timedelta(days=90),
            "JWT_SECRET": timedelta(days=365),
        }
    
    def check_and_rotate(self, secret_name: str) -> bool:
        """Check if secret needs rotation and rotate if needed"""
        last_rotation = self._get_last_rotation(secret_name)
        rotation_period = self.rotation_schedule.get(
            secret_name, 
            timedelta(days=30)
        )
        
        if datetime.now() - last_rotation > rotation_period:
            return self.secret_manager.rotate_secret(secret_name)
        
        return False
    
    def rotate_all_due(self) -> List[str]:
        """Rotate all secrets that are due"""
        rotated = []
        for secret_name in self.rotation_schedule.keys():
            if self.check_and_rotate(secret_name):
                rotated.append(secret_name)
                self._notify_rotation(secret_name)
        return rotated
    
    def _notify_rotation(self, secret_name: str):
        """Notify systems that use this secret to refresh their cache"""
        # Send invalidation message to agent credential caches
        pass
```

### Logging Security

```python
class SecureLogger:
    """Logger that automatically redacts secrets"""
    
    def __init__(self):
        self.redaction_patterns = [
            (r'(api[_-]?key)\s*[:=]\s*[\'"]([^\'"]+)[\'"]', r'\1=[REDACTED]'),
            (r'(password)\s*[:=]\s*[\'"]([^\'"]+)[\'"]', r'\1=[REDACTED]'),
            (r'(secret)\s*[:=]\s*[\'"]([^\'"]+)[\'"]', r'\1=[REDACTED]'),
            (r'(token)\s*[:=]\s*[\'"]([^\'"]{10,})[\'"]', r'\1=[REDACTED]'),
            (r'(-----BEGIN [A-Z ]+ KEY-----)', r'\1[REDACTED]'),
            (r'\b[A-Za-z0-9]{32,}\b', '[REDACTED]'),  # Long alphanumeric strings
        ]
    
    def log(self, level: str, message: str, **kwargs):
        """Log message with automatic redaction"""
        redacted_message = self._redact(message)
        redacted_kwargs = {
            k: self._redact(str(v)) for k, v in kwargs.items()
        }
        
        # Actual logging
        logging.log(level, redacted_message, **redacted_kwargs)
    
    def _redact(self, text: str) -> str:
        """Apply all redaction patterns"""
        for pattern, replacement in self.redaction_patterns:
            text = re.sub(pattern, replacement, text, flags=re.I)
        return text
```

## Best Practices

1. **Use Managed Secret Services**: AWS Secrets Manager, HashiCorp Vault, Azure Key Vault
2. **Environment Variables for Local Dev**: Never hardcode, use .env files (gitignored)
3. **IAM Roles Over Keys**: Use instance roles where possible instead of access keys
4. **Short-Lived Credentials**: Prefer temporary credentials (STS, OAuth tokens)
5. **Secret Scanning**: Use tools like git-secrets, truffleHog to prevent commits
6. **Access Monitoring**: Alert on unusual secret access patterns
7. **Emergency Revocation**: Have process to immediately revoke compromised secrets

## When to Use

- Any agent accessing external APIs or services
- Agents with database access
- Multi-tenant systems with per-tenant credentials
- Compliance-regulated environments
- Production systems (never use real secrets in development)

## When NOT to Use

- Development/testing with mock services
- Single-user local tools (still use .env files)
- Public/demo deployments (use read-only, limited credentials)

## Related Patterns

- [Tool Permissioning](../tool-permissioning/) - Access control for tools
- [Guardrails Pattern](../guardrails-pattern/) - Prevent secret leakage in output
- [Audit Logging](../audit-logging/) - Track secret access
- [Prompt Injection Defense](../prompt-injection-defense/) - Prevent secret extraction

## References

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [12-Factor App: Config](https://12factor.net/config)
- [NIST Guidelines on Authentication and Secrets](https://csrc.nist.gov/publications/detail/sp/800-63b/final)