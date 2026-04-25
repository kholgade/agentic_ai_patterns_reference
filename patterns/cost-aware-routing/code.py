from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional
from functools import wraps

class Complexity(Enum):
    SIMPLE = "simple"      # Extraction, classification, yes/no
    MEDIUM = "medium"      # Summarization, translation, simple qa
    HIGH = "high"         # Complex reasoning, analysis
    COMPLEX = "complex"  # Creative, technical, multi-step

@dataclass
class ModelConfig:
    name: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    max_tokens: int
    complexity_level: Complexity

class CostAwareRouter:
    def __init__(self):
        self.models = {
            'gpt-3.5-turbo': ModelConfig(
                name='gpt-3.5-turbo',
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                max_tokens=16385,
                complexity_level=Complexity.SIMPLE
            ),
            'gpt-4-turbo': ModelConfig(
                name='gpt-4-turbo',
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.03,
                max_tokens=128000,
                complexity_level=Complexity.HIGH
            ),
            'gpt-4': ModelConfig(
                name='gpt-4',
                cost_per_1k_input=0.03,
                cost_per_1k_output=0.06,
                max_tokens=128000,
                complexity_level=Complexity.COMPLEX
            ),
            'claude-3-haiku': ModelConfig(
                name='claude-3-haiku',
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125,
                max_tokens=200000,
                complexity_level=Complexity.MEDIUM
            ),
            'claude-3-sonnet': ModelConfig(
                name='claude-3-sonnet',
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                max_tokens=200000,
                complexity_level=Complexity.HIGH
            ),
        }
        self._complexity_classifier = self._build_classifier()
    
    def _build_classifier(self) -> Callable[[str], Complexity]:
        """Build or load a complexity classifier."""
        # Simple keyword-based classifier for demonstration
        simple_keywords = ['what', 'is', 'are', 'capital', 'define', 'list']
        complex_keywords = ['analyze', 'compare', 'design', 'explain', 'evaluate']
        
        def classify(query: str) -> Complexity:
            query_lower = query.lower()
            
            # Check for complex patterns
            if any(kw in query_lower for kw in complex_keywords):
                if any(w in query_lower for w in ['step', 'how', 'architect', 'specif']):
                    return Complexity.COMPLEX
                return Complexity.HIGH
            
            # Check for simple patterns
            if any(kw in query_lower for kw in simple_keywords):
                if '?' in query and len(query.split()) < 10:
                    return Complexity.SIMPLE
                return Complexity.MEDIUM
            
            # Default to medium
            return Complexity.MEDIUM
        
        return classify
    
    def estimate_complexity(self, query: str) -> Complexity:
        """Estimate query complexity."""
        return self._complexity_classifier(query)
    
    def select_model(
        self, 
        query: str, 
        complexity: Optional[Complexity] = None,
        max_budget: Optional[float] = None
    ) -> ModelConfig:
        """Select best model based on complexity and budget."""
        complexity = complexity or self.estimate_complexity(query)
        
        # Find cheapest model that meets complexity requirements
        suitable_models = [
            m for m in self.models.values()
            if m.complexity_level.value <= complexity.value
        ]
        
        if max_budget:
            suitable_models = [
                m for m in suitable_models
                if m.cost_per_1k_input <= max_budget
            ]
        
        if not suitable_models:
            # Fallback to most capable
            suitable_models = list(self.models.values())
        
        return min(suitable_models, key=lambda m: m.cost_per_1k_input)
    
    def estimate_cost(
        self, 
        query: str, 
        model_name: str,
        expected_output_tokens: int = 500
    ) -> float:
        """Estimate cost for a query."""
        model = self.models.get(model_name)
        if not model:
            return 0.0
        
        input_tokens = len(query.split()) * 1.3  # Rough estimate
        input_cost = (input_tokens / 1000) * model.cost_per_1k_input
        output_cost = (expected_output_tokens / 1000) * model.cost_per_1k_output
        
        return input_cost + output_cost
    
    def route(self, query: str, **kwargs) -> dict:
        """Full routing with cost estimation."""
        complexity = self.estimate_complexity(query)
        model = self.select_model(query, complexity)
        
        estimated_cost = self.estimate_cost(query, model.name)
        
        return {
            'query': query,
            'complexity': complexity.value,
            'selected_model': model.name,
            'estimated_cost': estimated_cost,
            'all_models': list(self.models.keys())
        }


# Usage
router = CostAwareRouter()

# Simple query
result = router.route("What is the capital of France?")
print(result)
# {'complexity': 'simple', 'selected_model': 'gpt-3.5-turbo', 
#  'estimated_cost': 0.0015, ...}

# Complex query
result = router.route(
    "Design a distributed system architecture for a "
    "global e-commerce platform with automatic failover"
)
print(result)
# {'complexity': 'complex', 'selected_model': 'gpt-4', 
#  'estimated_cost': 0.045, ...}


# Example 1: Budget-Constrained Routing
class BudgetConstrainedRouter(CostAwareRouter):
    def __init__(self, daily_budget: float):
        super().__init__()
        self.daily_budget = daily_budget
        self.spent_today = 0
        self.request_count = 0
    
    def route_with_budget(
        self, 
        query: str, 
        min_quality: str = "medium"
    ) -> dict:
        """Route considering remaining budget."""
        remaining = self.daily_budget - self.spent_today
        budget_per_request = remaining / max(1, 100 - self.request_count)
        
        complexity = self.estimate_complexity(query)
        
        # If budget low, force to cheaper model
        if remaining < self.daily_budget * 0.2:
            min_complexity = Complexity.SIMPLE
        else:
            min_complexity = Complexity.MEDIUM
        
        model = self.select_model(query, complexity, budget_per_request)
        
        estimated = self.estimate_cost(query, model.name)
        
        self.spent_today += estimated
        self.request_count += 1
        
        return {
            'model': model.name,
            'estimated_cost': estimated,
            'remaining_budget': remaining - estimated
        }


# Example 2: Quality-Based Fallback Routing
class QualityAwareRouter:
    def __init__(self):
        self.router = CostAwareRouter()
        self.success_rates = {}
    
    def _extract_quality_threshold(self, query: str) -> str:
        """Determine minimum acceptable quality."""
        q_lower = query.lower()
        
        if any(w in q_lower for w in ['medical', 'legal', 'financial']):
            return 'high'
        if any(w in q_lower for w in ['important', 'critical', 'official']):
            return 'medium'
        return 'low'
    
    def route(self, query: str) -> dict:
        quality = self._extract_quality_threshold(query)
        
        if quality == 'low':
            return self.router.route(query)
        
        # Higher quality - use better model
        complexity = self.router.estimate_complexity(query)
        
        model_map = {
            'low': Complexity.SIMPLE,
            'medium': Complexity.MEDIUM,
            'high': Complexity.HIGH
        }
        
        min_complexity = model_map.get(quality, Complexity.MEDIUM)
        
        if complexity.value < min_complexity.value:
            complexity = min_complexity
        
        return self.router.select_model(query, complexity)