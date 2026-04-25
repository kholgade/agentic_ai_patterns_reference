# Budget-Aware Model Routing

## Overview

Intelligently route LLM requests to different models based on task complexity, cost constraints, and performance requirements. Instead of defaulting to the most capable (expensive) model for every request, this pattern optimizes cost and latency while maintaining quality by matching model capabilities to task requirements.

## The Problem

```
Default Approach (Expensive):
┌──────────────────────────────────────────┐
│  Every request → GPT-4/Claude Opus       │
│                                          │
│  Simple query: "What's 2+2?"             │
│    → $0.03 (overkill)                    │
│  Complex query: "Debug this race condition" │
│    → $0.03 (appropriate)                 │
│                                          │
│  Result: Wasted money on simple tasks    │
└──────────────────────────────────────────┘
```

## The Solution

```
Budget-Aware Routing:
┌─────────────────────────────────────────────────────┐
│              Request Classifier                      │
│                     ↓                                │
│        ┌────────────┴────────────┐                   │
│        ↓                         ↓                   │
│   Simple Tasks              Complex Tasks            │
│   (classification,          (reasoning,              │
│    extraction, summary)      coding, analysis)       │
│        ↓                         ↓                   │
│   GPT-3.5/Claude Haiku      GPT-4/Claude Opus        │
│   $0.002 per request        $0.03 per request        │
│                                                      │
│   Result: 60-80% cost savings                        │
└─────────────────────────────────────────────────────┘
```

## Implementation

### Router with Hard Cost Caps

```python
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time

class ModelTier(Enum):
    BUDGET = "budget"      # GPT-3.5, Claude Haiku
    STANDARD = "standard"  # GPT-4, Claude Sonnet
    PREMIUM = "premium"    # GPT-4 Turbo, Claude Opus, o1

@dataclass
class ModelConfig:
    tier: ModelTier
    model_name: str
    cost_per_1k_tokens: float
    max_context_window: int
    capabilities: list  # ['reasoning', 'coding', 'vision', etc.]

@dataclass
class RoutingDecision:
    model: ModelConfig
    reason: str
    estimated_cost: float
    within_budget: bool

class BudgetAwareRouter:
    def __init__(self, budget_config: dict):
        self.models = self._initialize_models()
        self.daily_budget = budget_config.get('daily_budget', 100.0)
        self.spent_today = 0.0
        self.budget_reset_time = self._get_next_reset_time()
        
        # Cost caps
        self.max_cost_per_request = budget_config.get('max_per_request', 1.0)
        self.emergency_threshold = budget_config.get('emergency_threshold', 0.9)
    
    def route_request(self, request: dict) -> RoutingDecision:
        """Route request based on complexity and budget"""
        
        # Check budget
        if not self._check_budget():
            return self._emergency_fallback()
        
        # Classify task complexity
        complexity = self._classify_complexity(request)
        
        # Select appropriate model
        model = self._select_model(complexity, request)
        
        # Estimate cost
        estimated_cost = self._estimate_cost(model, request)
        
        # Verify within budget
        within_budget = (
            estimated_cost <= self.max_cost_per_request and
            self.spent_today + estimated_cost <= self.daily_budget
        )
        
        return RoutingDecision(
            model=model,
            reason=f"Task classified as {complexity}, budget OK",
            estimated_cost=estimated_cost,
            within_budget=within_budget
        )
    
    def _classify_complexity(self, request: dict) -> str:
        """
        Classify task as simple, moderate, or complex
        Can use rules or a lightweight classifier
        """
        task_type = request.get('type', 'general')
        prompt_length = len(request.get('prompt', ''))
        requires_reasoning = request.get('requires_reasoning', False)
        requires_coding = request.get('requires_coding', False)
        
        # Simple tasks
        if task_type in ['classification', 'extraction', 'summary']:
            if prompt_length < 1000 and not requires_reasoning:
                return 'simple'
        
        # Complex tasks
        if requires_coding or requires_reasoning or task_type == 'analysis':
            return 'complex'
        
        # Moderate tasks
        return 'moderate'
    
    def _select_model(self, complexity: str, request: dict) -> ModelConfig:
        """Select model based on complexity and requirements"""
        
        if complexity == 'simple':
            return self.models['budget']
        elif complexity == 'moderate':
            return self.models['standard']
        else:  # complex
            # Check if we can afford premium
            if self._can_afford_premium():
                return self.models['premium']
            else:
                # Fallback to standard with warning
                return self.models['standard']
    
    def _estimate_cost(self, model: ModelConfig, request: dict) -> float:
        """Estimate cost based on prompt and expected completion"""
        prompt_tokens = len(request.get('prompt', '')) / 4  # Rough estimate
        
        # Estimate completion tokens based on task type
        completion_estimates = {
            'classification': 50,
            'extraction': 200,
            'summary': 500,
            'analysis': 1000,
            'coding': 800,
            'general': 300
        }
        
        completion_tokens = completion_estimates.get(
            request.get('type', 'general'), 
            300
        )
        
        total_tokens = prompt_tokens + completion_tokens
        cost = (total_tokens / 1000) * model.cost_per_1k_tokens
        
        return cost
    
    def _check_budget(self) -> bool:
        """Check if we're within budget"""
        current_time = time.time()
        
        # Reset if new day
        if current_time > self.budget_reset_time:
            self.spent_today = 0.0
            self.budget_reset_time = self._get_next_reset_time()
        
        # Check emergency threshold
        if self.spent_today >= self.daily_budget * self.emergency_threshold:
            return False
        
        return True
    
    def _can_afford_premium(self) -> bool:
        """Check if budget allows premium model"""
        remaining = self.daily_budget - self.spent_today
        return remaining > self.models['premium'].cost_per_1k_tokens * 2
    
    def _emergency_fallback(self) -> RoutingDecision:
        """Emergency fallback when budget exceeded"""
        return RoutingDecision(
            model=self.models['budget'],
            reason="Budget exceeded - using cheapest model",
            estimated_cost=0.001,
            within_budget=True
        )
    
    def record_cost(self, actual_cost: float):
        """Record actual cost after request completion"""
        self.spent_today += actual_cost
    
    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize model configurations"""
        return {
            'budget': ModelConfig(
                tier=ModelTier.BUDGET,
                model_name='gpt-3.5-turbo',
                cost_per_1k_tokens=0.002,
                max_context_window=4096,
                capabilities=['classification', 'extraction', 'simple_qa']
            ),
            'standard': ModelConfig(
                tier=ModelTier.STANDARD,
                model_name='gpt-4',
                cost_per_1k_tokens=0.03,
                max_context_window=8192,
                capabilities=['reasoning', 'coding', 'analysis']
            ),
            'premium': ModelConfig(
                tier=ModelTier.PREMIUM,
                model_name='gpt-4-turbo',
                cost_per_1k_tokens=0.10,
                max_context_window=128000,
                capabilities=['complex_reasoning', 'vision', 'long_context']
            )
        }
    
    def _get_next_reset_time(self) -> float:
        """Get timestamp for next budget reset (midnight UTC)"""
        from datetime import datetime, timedelta
        tomorrow = datetime.utcnow().date() + timedelta(days=1)
        return tomorrow.replace(hour=0, minute=0, second=0).timestamp()
```

### Complexity Classifier (ML-Based)

```python
class LearnedComplexityClassifier:
    """
    Use a lightweight model to classify task complexity
    Trained on historical data about which tasks needed model escalation
    """
    
    def __init__(self, escalation_history: list):
        self.classifier = self._train_classifier(escalation_history)
    
    def classify(self, request: dict) -> str:
        features = self._extract_features(request)
        prediction = self.classifier.predict([features])[0]
        
        if prediction == 0:
            return 'simple'
        elif prediction == 1:
            return 'moderate'
        else:
            return 'complex'
    
    def _extract_features(self, request: dict) -> list:
        return [
            len(request.get('prompt', '')),
            request.get('requires_reasoning', False),
            request.get('requires_coding', False),
            len(request.get('context', [])),
            self._count_numbers(request.get('prompt', '')),
            self._count_special_chars(request.get('prompt', '')),
        ]
    
    def _train_classifier(self, history: list):
        """Train on historical escalation data"""
        from sklearn.ensemble import RandomForestClassifier
        
        X = [self._extract_features(h['request']) for h in history]
        y = [h['needed_escalation'] for h in history]  # 0=no, 1=yes
        
        clf = RandomForestClassifier(n_estimators=50)
        clf.fit(X, y)
        return clf
```

### Integration with Agent

```python
class BudgetAwareAgent:
    def __init__(self, router: BudgetAwareRouter):
        self.router = router
        self.model_clients = self._initialize_clients()
    
    def execute(self, request: dict) -> dict:
        # Route request
        decision = self.router.route_request(request)
        
        if not decision.within_budget:
            raise BudgetExceededError(
                f"Request would exceed budget: ${decision.estimated_cost:.4f}"
            )
        
        # Execute with selected model
        model_client = self.model_clients[decision.model.model_name]
        
        try:
            response = model_client.generate(
                prompt=request['prompt'],
                max_tokens=request.get('max_tokens', 1000)
            )
            
            # Record actual cost
            actual_cost = self._calculate_actual_cost(
                response.usage,
                decision.model
            )
            self.router.record_cost(actual_cost)
            
            return {
                'response': response.text,
                'model_used': decision.model.model_name,
                'cost': actual_cost,
                'routing_reason': decision.reason
            }
            
        except Exception as e:
            # Escalate on failure
            return self._escalate_request(request, e)
    
    def _escalate_request(self, request: dict, error: Exception) -> dict:
        """Escalate to more capable model on failure"""
        # Log escalation
        self._log_escalation(request, error)
        
        # Retry with premium model
        premium_decision = RoutingDecision(
            model=self.router.models['premium'],
            reason="Escalated due to failure",
            estimated_cost=0.10,
            within_budget=True
        )
        
        model_client = self.model_clients[premium_decision.model.model_name]
        response = model_client.generate(request['prompt'])
        
        return {
            'response': response.text,
            'model_used': premium_decision.model.model_name,
            'escalated': True,
            'original_error': str(error)
        }
```

## Cost Optimization Strategies

### 1. Response Caching
```python
class CachedBudgetRouter(BudgetAwareRouter):
    def __init__(self, cache, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = cache
    
    def route_request(self, request: dict) -> RoutingDecision:
        # Check cache first
        cache_key = self._hash_request(request)
        cached = self.cache.get(cache_key)
        
        if cached:
            return RoutingDecision(
                model=ModelConfig('cache', 'cache', 0.0, 0, []),
                reason="Cache hit",
                estimated_cost=0.0,
                within_budget=True
            )
        
        return super().route_request(request)
```

### 2. Batch Simple Requests
```python
class BatchRouter(BudgetAwareRouter):
    def batch_route(self, requests: list) -> list:
        """Batch multiple simple requests together"""
        simple_requests = [
            r for r in requests 
            if self._classify_complexity(r) == 'simple'
        ]
        
        if len(simple_requests) >= 5:
            # Combine into single request
            combined = self._combine_requests(simple_requests)
            return [combined] + [r for r in requests if r not in simple_requests]
        
        return requests
```

## When to Use

- **High-volume applications** - 1000+ requests/day
- **Cost-sensitive deployments** - Fixed budget constraints
- **Mixed workload** - Both simple and complex tasks
- **Multi-tenant SaaS** - Different tiers have different budgets
- **Production systems** - Need predictable cost control

## When NOT to Use

- Low-volume applications (< 100 requests/day)
- Research/experimental projects
- When maximum quality is required for all requests
- When latency is more critical than cost

## Best Practices

1. **Start conservative** - Begin with more budget model, optimize later
2. **Monitor escalation rate** - >10% means classifier needs tuning
3. **Cache aggressively** - Cache is free, LLM calls cost money
4. **Set hard caps** - Prevent runaway costs
5. **Track cost per feature** - Identify expensive features
6. **Use cheaper models for retries** - First attempt premium, retry budget
7. **Implement circuit breakers** - Stop expensive failures quickly

## Related Patterns

- [Action Caching & Replay](../action-caching/) - Reduce redundant calls
- [Tool Search Lazy Loading](../tool-search-lazy-loading/) - Reduce context costs
- [Code-Over-API](../code-over-api/) - Reduce token usage
- [Agent Circuit Breaker](../agent-circuit-breaker/) - Fail fast on errors
- [LLM Observability](../llm-observability/) - Track costs and usage

## References

- [Budget-Aware Model Routing](https://agentic-patterns.com/patterns/budget-aware-model-routing-with-hard-cost-caps) - Original pattern
- [Anthropic Pricing](https://www.anthropic.com/pricing) - Model cost comparison
- [Cost-Aware Routing](../cost-aware-routing/) - Related pattern in this repo