import random
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Callable, Optional
from collections import defaultdict
from scipy import stats
import numpy as np

@dataclass
class ExperimentVariant:
    """Single variant in an experiment."""
    id: str
    name: str
    config: dict
    weight: float = 1.0

@dataclass
class MetricResult:
    """Result for a single metric."""
    name: str
    values: list[float] = field(default_factory=list)
    
    @property
    def mean(self) -> float:
        return np.mean(self.values) if self.values else 0.0
    
    @property
    def std(self) -> float:
        return np.std(self.values) if self.values else 0.0
    
    @property
    def count(self) -> int:
        return len(self.values)

@dataclass
class ExperimentResult:
    """Complete experiment results."""
    variant_id: str
    metrics: dict[str, MetricResult] = field(default_factory=dict)
    sample_size: int = 0
    
    def add_metric(self, name: str, value: float):
        if name not in self.metrics:
            self.metrics[name] = MetricResult(name)
        self.metrics[name].values.append(value)

class ABTester:
    """A/B testing framework for LLM experiments."""
    
    def __init__(self, experiment_id: str):
        self.experiment_id = experiment_id
        self.variants: dict[str, ExperimentVariant] = {}
        self.results: dict[str, ExperimentResult] = {}
        self._participant_count = 0
    
    def add_variant(
        self, 
        variant_id: str, 
        name: str, 
        config: dict,
        weight: float = 1.0
    ):
        """Add a variant to the experiment."""
        self.variants[variant_id] = ExperimentVariant(
            id=variant_id,
            name=name,
            config=config,
            weight=weight
        )
        self.results[variant_id] = ExperimentResult(variant_id)
    
    def select_variant(self) -> str:
        """Select a variant based on configured weights."""
        if not self.variants:
            raise ValueError("No variants configured")
        
        total_weight = sum(v.weight for v in self.variants.values())
        r = random.random() * total_weight
        
        cumulative = 0
        for variant in self.variants.values():
            cumulative += variant.weight
            if r <= cumulative:
                return variant.id
        
        return list(self.variants.keys())[-1]
    
    def record_result(
        self, 
        variant_id: str, 
        metrics: dict[str, float]
    ):
        """Record results for a variant."""
        if variant_id not in self.results:
            self.results[variant_id] = ExperimentResult(variant_id)
        
        result = self.results[variant_id]
        result.sample_size += 1
        
        for metric_name, value in metrics.items():
            result.add_metric(metric_name, value)
    
    def analyze(self) -> dict:
        """Perform statistical analysis on results."""
        if len(self.variants) < 2:
            return {"error": "Need at least 2 variants"}
        
        analysis = {
            "experiment_id": self.experiment_id,
            "total_samples": self._participant_count,
            "variants": {}
        }
        
        # Get first two variants for comparison
        variant_ids = list(self.results.keys())
        control = self.results[variant_ids[0]]
        treatment = self.results[variant_ids[1]]
        
        # Primary metric analysis
        for metric_name in control.metrics:
            if metric_name not in treatment.metrics:
                continue
            
            control_vals = control.metrics[metric_name].values
            treatment_vals = treatment.metrics[metric_name].values
            
            if len(control_vals) < 10 or len(treatment_vals) < 10:
                continue
            
            # T-test
            t_stat, p_value = stats.ttest_ind(control_vals, treatment_vals)
            
            control_mean = np.mean(control_vals)
            treatment_mean = np.mean(treatment_vals)
            lift = ((treatment_mean - control_mean) / control_mean * 100 
                    if control_mean != 0 else 0)
            
            analysis["variants"][metric_name] = {
                "control_mean": control_mean,
                "treatment_mean": treatment_mean,
                "lift_percent": lift,
                "p_value": p_value,
                "significant": p_value < 0.05,
                "sample_sizes": {
                    "control": len(control_vals),
                    "treatment": len(treatment_vals)
                }
            }
        
        return analysis

def run_ab_test(
    tester: ABTester,
    prompt: str,
    evaluate_fn: Callable[[str], dict],
    n_samples: int = 100
):
    """Run an A/B test."""
    for i in range(n_samples):
        # Select variant
        variant_id = tester.select_variant()
        variant = tester.variants[variant_id]
        
        # Build prompt with variant config
        full_prompt = prompt
        if "prefix" in variant.config:
            full_prompt = variant.config["prefix"] + "\n\n" + prompt
        if "suffix" in variant.config:
            full_prompt = prompt + "\n\n" + variant.config["suffix"]
        
        # Call LLM
        response = call_llm(full_prompt, **variant.config.get("params", {}))
        
        # Evaluate response
        metrics = evaluate_fn(response)
        
        # Record results
        tester.record_result(variant_id, metrics)
        
        # Small delay to avoid rate limits
        time.sleep(0.1)
    
    return tester.analyze()


# Usage
def evaluate_response(response: str) -> dict:
    """Evaluate LLM response with custom metrics."""
    return {
        "latency": random.gauss(1.5, 0.3),  # Simulated
        "accuracy": 1.0 if "10" in response else 0.0,
        "length": len(response)
    }

# Setup experiment
tester = ABTester("prompt-comparison-test")

tester.add_variant(
    "control",
    "No CoT",
    {"prefix": "Answer the question."}
)

tester.add_variant(
    "treatment",
    "With CoT",
    {"prefix": "Let's think step by step.\n\nAnswer the question."}
)

# Run test
results = run_ab_test(
    tester,
    "What is 7+3?",
    evaluate_response,
    n_samples=100
)

print(json.dumps(results, indent=2))


# Example 1: Multi-Variant Prompt Optimization
def prompt_optimization_experiment():
    """Test multiple prompt engineering techniques."""
    
    tester = ABTester("prompt-optimization")
    
    # Variants: baseline, few-shot, cot, structured
    variants = {
        "baseline": "Answer: {question}",
        "fewshot": "Examples: 2+2=4, 5+3=8. Answer: {question}",
        "cot": "Think step by step. {question}\nTherefore:",
        "structured": 'Answer in JSON: {"answer": "number"} Question: {question}'
    }
    
    for vid, template in variants.items():
        tester.add_variant(vid, template, {"template": template})
    
    # Test multiple questions
    questions = [
        "What is 7+3?",
        "What is 12+5?",
        "What is 25+30?"
    ]
    
    results = []
    for question in questions:
        for _ in range(20):
            variant_id = tester.select_variant()
            prompt = variants[variant_id].format(question=question)
            
            response = call_llm(prompt)
            
            is_correct = "10" in response if "7+3" in question else \
                       "17" in response if "12+5" in question else \
                       "55" in response
            
            tester.record_result(variant_id, {"accuracy": float(is_correct)})
    
    return tester.analyze()


# Example 2: Model Selection with Gradual Rollout
class GradualRolloutExperiment:
    """Gradually increase traffic to new model."""
    
    def __init__(self, experiment_id: str):
        self.experiment_id = experiment_id
        self.phases = [
            {"name": "1%", "traffic": 0.01, "duration": 3600},
            {"name": "5%", "traffic": 0.05, "duration": 7200},
            {"name": "25%", "traffic": 0.25, "duration": 14400},
            {"name": "100%", "traffic": 1.0, "duration": None}
        ]
        self.current_phase = 0
        self.champion = "gpt-3.5"
        self.challenger = "gpt-4"
        self.metrics = defaultdict(lambda: defaultdict(list))
    
    def should_serve_challenger(self) -> bool:
        """Determine if challenger should serve this request."""
        if self.current_phase >= len(self.phases):
            return True
        
        phase = self.phases[self.current_phase]
        return random.random() < phase["traffic"]
    
    def record_metrics(self, model: str, latency: float, success: bool):
        """Record and analyze metrics."""
        self.metrics[model]["latency"].append(latency)
        self.metrics[model]["success"].append(success)
        
        # Check if ready to advance
        self._check_progression()
    
    def _check_progression(self):
        """Check if can advance to next phase."""
        if self.current_phase >= len(self.phases) - 1:
            return
        
        champion_latency = np.mean(
            self.metrics[self.champion]["latency"]
        ) if self.metrics[self.champion]["latency"] else 0
        
        challenger_latency = np.mean(
            self.metrics[self.challenger]["latency"]
        ) if self.metrics[self.challenger]["latency"] else 0
        
        champion_success = np.mean(
            self.metrics[self.champion]["success"]
        ) if self.metrics[self.champion]["success"] else 0
        
        challenger_success = np.mean(
            self.metrics[self.challenger]["success"]
        ) if self.metrics[self.challenger]["success"] else 0
        
        # Promote if challenger better on both metrics
        if challenger_latency < champion_latency * 1.5 and \
           challenger_success >= champion_success:
            self.current_phase += 1
            print(f"Advancing to phase: {self.phases[self.current_phase]['name']}")


def call_llm(prompt: str, **kwargs) -> str:
    """Call LLM API"""
    return "10"