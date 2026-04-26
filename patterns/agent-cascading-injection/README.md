---
title: "Agent Cascading Injection Defense"
description: "A security pattern for multi-agent systems that prevents malicious instructions from cascading through agent chains by implementing input sanitization, trust boundaries, and message authentication at agent boundaries."
complexity: "high"
model_maturity: "emerging"
typical_use_cases: ["Multi-agent system security", "Prompt injection defense", "Agent chain hardening", "Untrusted agent isolation"]
dependencies: ["Prompt Injection Defense", "Gate Checkpoint"]
category: "security"
---

# Agent Cascading Injection Defense

## Overview

Multi-agent systems enable collaboration and information sharing, but introduce a critical security vulnerability: **Agent Cascading Injection (ACI)**. In such attacks, a compromised agent exploits inter-agent trust to propagate malicious instructions, causing cascading failures across the system.

**Agent Cascading Injection Defense** provides systematic protection against ACI through:

1. **Trust Boundary Enforcement** - Explicit trust zones between agents
2. **Input Sanitization** - Multi-layer filtering at agent boundaries
3. **Message Authentication** - Cryptographic verification of inter-agent messages
4. **Attack Surface Minimization** - Controlled interaction patterns
5. **Runtime Monitoring** - Continuous anomaly detection

## The Attack Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACI Attack Flow                               │
└─────────────────────────────────────────────────────────────────┘

  Attacker ──> [Agent A] ──> [Agent B] ──> [Agent C]
              Compromised   Cascading     Cascading
              via prompt    failure       failure
              injection

  Attack vectors:
  • External inputs (user messages)
  • Agent profile tampering
  • Inter-agent message interception
  • Instruction hijacking
  • Task disruption
  • Information exfiltration
```

## When to Use

Use Agent Cascading Injection Defense when:
- Operating multi-agent systems with 3+ agents
- Agents have different trust levels or origins
- User inputs flow through multiple agent processing stages
- System handles sensitive data or privileged operations
- Agents can invoke tools or external APIs
- Operating in adversarial environments (public-facing systems)

## ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Defense Architecture                            │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   External   │     ┌─────────────────────────────────────────────┐
│    Input     │────▶│           Perimeter Sanitization             │
└──────────────┘     │  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
                     │  │  Input  │ │ Prompt  │ │  Content│        │
                     │  │ Validation│ │ Filtering│ │ Scanning│        │
                     │  └─────────┘ └─────────┘ └─────────┘        │
                     └────────────────────┬──────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Trust Boundaries                           │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Trust Zone A (High Trust - Core Agents)                     │ │
│  │  ┌──────────┐      ┌──────────┐      ┌──────────┐          │ │
│  │  │ Agent A1 │◄────►│ Agent A2 │◄────►│ Agent A3 │          │ │
│  │  └──────────┘      └──────────┘      └──────────┘          │ │
│  │  │                    │                    │               │ │
│  │  │  Signed Messages   │  Signed Messages   │               │ │
│  │  │  + Capability      │  + Capability      │               │ │
│  │  │  Attestation       │  Attestation       │               │ │
│  └────┼────────────────────┼────────────────────┼────────────────┘ │
│       │                    │                    │                  │
│       │ Trust Boundary     │ Trust Boundary     │                  │
│       │ (Gateway)          │ (Gateway)          │                  │
│       │                    │                    │                  │
│  ┌────▼────────────────────▼────────────────────▼────────────────┐ │
│  │  Trust Zone B (Lower Trust - External/Sandboxed Agents)      │ │
│  │  ┌──────────┐      ┌──────────┐      ┌──────────┐            │ │
│  │  │ Agent B1 │◄────►│ Agent B2 │◄────►│ Agent B3 │            │ │
│  │  └──────────┘      └──────────┘      └──────────┘            │ │
│  │  [Isolated execution with capability restrictions]           │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Message Authentication                            │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Message Format:                                             │  │
│  │  {                                                           │  │
│  │    "payload": "<sanitized_content>",                         │  │
│  │    "sender": "agent_id",                                     │  │
│  │    "trust_zone": "A",                                        │  │
│  │    "capabilities": ["read", "write"],                        │  │
│  │    "signature": "hmac_sha256(...)",                          │  │
│  │    "timestamp": 1234567890,                                  │  │
│  │    "ttl": 300                                                │  │
│  │  }                                                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Defense Layers

### Layer 1: Perimeter Sanitization
All external inputs pass through multiple filters:
- **Input Validation**: Schema-based validation
- **Prompt Filtering**: Pattern matching for injection attempts
- **Content Scanning**: Semantic analysis for malicious intent

### Layer 2: Trust Boundaries
Agents are organized into trust zones:
- **High Trust**: Core system agents with minimal privileges
- **Medium Trust**: Standard agents with specific capabilities
- **Low Trust**: External/sandboxed agents with restricted access

### Layer 3: Message Authentication
All inter-agent messages include:
- Cryptographic signatures (HMAC/ECDSA)
- Capability attestations
- Time-to-live (TTL) for replay protection
- Sender verification

### Layer 4: Runtime Monitoring
Continuous detection of:
- Anomalous message patterns
- Privilege escalation attempts
- Unexpected agent behaviors
- Cross-zone communication violations

## Minimal Code (Pseudo)

```python
from dataclasses import dataclass
from typing import List, Set
from hashlib import hmac
import time

@dataclass
class AgentIdentity:
    agent_id: str
    trust_zone: str
    capabilities: Set[str]
    public_key: str

@dataclass
class SecureMessage:
    payload: str
    sender: str
    recipient: str
    trust_zone: str
    capabilities: List[str]
    timestamp: int
    ttl: int
    signature: str

class TrustBoundary:
    """Enforces trust boundaries between agents"""
    
    def __init__(self, zone_a: str, zone_b: str):
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.allowed_capabilities = {
            zone_a: {'read', 'write', 'execute'},
            zone_b: {'read'}  # Lower trust zone
        }
    
    def can_cross(self, message: SecureMessage) -> bool:
        """Check if message can cross boundary"""
        # Check if source zone can send to destination
        if message.trust_zone != self.zone_a:
            return False
        
        # Verify capabilities aren't escalated
        for cap in message.capabilities:
            if cap not in self.allowed_capabilities[self.zone_b]:
                return False
        
        return True

class InputSanitizer:
    """Multi-layer input sanitization"""
    
    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"disregard (all|your) constraints",
        r"you are now .* mode",
        r"system prompt:.*",
        r"\{\{.*\}\}",  # Template injection
        r"<system>.*</system>",
    ]
    
    def __init__(self):
        self.blocked_patterns = self.compile_patterns()
    
    def sanitize(self, input_text: str) -> str:
        """Apply all sanitization layers"""
        # Layer 1: Remove known injection patterns
        cleaned = self.remove_injection_patterns(input_text)
        
        # Layer 2: Content-based filtering
        if self.contains_suspicious_content(cleaned):
            raise SecurityException("Suspicious content detected")
        
        # Layer 3: Rate limiting check
        if self.rate_limit_exceeded(cleaned):
            raise SecurityException("Rate limit exceeded")
        
        return cleaned
    
    def remove_injection_patterns(self, text: str) -> str:
        for pattern in self.blocked_patterns:
            text = pattern.sub("[REMOVED]", text)
        return text
    
    def contains_suspicious_content(self, text: str) -> bool:
        # Semantic analysis for prompt injection
        embeddings = self.get_embeddings(text)
        similarity_to_attack = self.cosine_similarity(
            embeddings, 
            self.attack_embeddings
        )
        return similarity_to_attack > 0.85

class MessageAuthenticator:
    """Cryptographic message authentication"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def sign(self, message: SecureMessage) -> str:
        """Sign message with HMAC"""
        payload = f"{message.payload}:{message.sender}:{message.timestamp}"
        return hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            'sha256'
        ).hexdigest()
    
    def verify(self, message: SecureMessage) -> bool:
        """Verify message signature"""
        expected_signature = self.sign(message)
        return hmac.compare_digest(message.signature, expected_signature)
    
    def verify_freshness(self, message: SecureMessage) -> bool:
        """Check TTL hasn't expired"""
        return time.time() - message.timestamp < message.ttl

class ACIDefense:
    """Complete ACI defense system"""
    
    def __init__(self):
        self.sanitizer = InputSanitizer()
        self.authenticator = MessageAuthenticator(secret_key)
        self.trust_boundaries = {}
        self.agent_identities = {}
    
    def register_agent(self, identity: AgentIdentity):
        """Register agent with defense system"""
        self.agent_identities[identity.agent_id] = identity
    
    def process_external_input(self, input_text: str) -> str:
        """Process user/external input through perimeter"""
        return self.sanitizer.sanitize(input_text)
    
    def send_message(self, 
                     sender_id: str, 
                     recipient_id: str, 
                     payload: str) -> SecureMessage:
        """Send secure message between agents"""
        sender = self.agent_identities[sender_id]
        recipient = self.agent_identities[recipient_id]
        
        # Check trust boundary
        boundary = self.get_trust_boundary(
            sender.trust_zone, 
            recipient.trust_zone
        )
        
        # Sanitize payload
        clean_payload = self.sanitizer.sanitize(payload)
        
        # Create message
        message = SecureMessage(
            payload=clean_payload,
            sender=sender_id,
            recipient=recipient_id,
            trust_zone=sender.trust_zone,
            capabilities=list(sender.capabilities),
            timestamp=int(time.time()),
            ttl=300,
            signature=""
        )
        
        # Sign message
        message.signature = self.authenticator.sign(message)
        
        # Check boundary crossing
        if not boundary.can_cross(message):
            raise SecurityException(
                f"Message cannot cross from {sender.trust_zone} "
                f"to {recipient.trust_zone}"
            )
        
        return message
    
    def receive_message(self, message: SecureMessage) -> str:
        """Receive and validate secure message"""
        # Verify signature
        if not self.authenticator.verify(message):
            raise SecurityException("Invalid message signature")
        
        # Check freshness
        if not self.authenticator.verify_freshness(message):
            raise SecurityException("Message expired (replay attack?)")
        
        # Additional validation
        sender = self.agent_identities.get(message.sender)
        if not sender:
            raise SecurityException("Unknown sender")
        
        if sender.trust_zone != message.trust_zone:
            raise SecurityException("Trust zone mismatch")
        
        return message.payload

# Usage
ac = ACIDefense()

# Register agents
ac.register_agent(AgentIdentity(
    agent_id="agent_a",
    trust_zone="high",
    capabilities={"read", "write", "execute"},
    public_key="..."
))

ac.register_agent(AgentIdentity(
    agent_id="agent_b",
    trust_zone="low",
    capabilities={"read"},
    public_key="..."
))

# Send secure message
msg = ac.send_message("agent_a", "agent_b", "Process this data")
payload = ac.receive_message(msg)
```

## Comparison with Existing Patterns

| Aspect | ACI Defense | Prompt Injection Defense | Gate Checkpoint |
|--------|-------------|-------------------------|-----------------|
| **Scope** | Multi-agent chains | Single agent | Quality gates |
| **Attack Type** | Cascading propagation | Direct injection | Output quality |
| **Mechanism** | Trust boundaries + auth | Pattern filtering | Evaluation |
| **Granularity** | Per-message | Per-input | Per-output |
| **Best For** | Multi-agent systems | Single agent setup | Content validation |

## Academic References

1. **An, H., et al.** (2026). "ACIArena: Toward Unified Evaluation for Agent Cascading Injection" - *ACL 2026*
   - Comprehensive framework for ACI evaluation
   - 1,356 test cases across 6 MAS implementations
   - Reveals that topology-only evaluation is insufficient

## Related Patterns

- **Prompt Injection Defense**: ACI Defense extends this to multi-agent chains
- **Gate Checkpoint**: Can be combined for additional output validation
- **Circuit Breaker**: Use for isolating compromised agents

## When NOT to Use

- **Single-agent systems** (use Prompt Injection Defense instead)
- **Trusted, closed environments** where overhead isn't justified
- **High-performance requirements** where signature verification adds latency
- **Simple sequential pipelines** without branching/interaction

## Trade-offs

| Benefit | Cost |
|---------|------|
| Prevents cascading failures | Significant complexity overhead |
| Fine-grained capability control | Latency from cryptographic operations |
| Trust zone isolation | Complex trust modeling required |
| Replay attack prevention | Message size overhead |
| Audit trail | Additional storage requirements |


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
