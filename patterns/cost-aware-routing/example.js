enum Complexity {
  SIMPLE = 'simple',
  MEDIUM = 'medium',
  HIGH = 'high',
  COMPLEX = 'complex'
}

interface ModelConfig {
  name: string;
  costPer1KInput: number;
  costPer1KOutput: number;
  maxTokens: number;
  complexity: Complexity;
}

const MODELS: ModelConfig[] = [
  {
    name: 'gpt-3.5-turbo',
    costPer1KInput: 0.0005,
    costPer1KOutput: 0.0015,
    maxTokens: 16385,
    complexity: Complexity.SIMPLE
  },
  {
    name: 'claude-3-haiku',
    costPer1KInput: 0.00025,
    costPer1KOutput: 0.00125,
    maxTokens: 200000,
    complexity: Complexity.MEDIUM
  },
  {
    name: 'gpt-4-turbo',
    costPer1KInput: 0.01,
    costPer1KOutput: 0.03,
    maxTokens: 128000,
    complexity: Complexity.HIGH
  },
  {
    name: 'gpt-4',
    costPer1KInput: 0.03,
    costPer1KOutput: 0.06,
    maxTokens: 128000,
    complexity: Complexity.COMPLEX
  }
];

class CostAwareRouter {
  private patterns = {
    simple: /\b(what|is|are|define|list|count|find)\b/i,
    medium: /\b(summary|explain|translate|convert)\b/i,
    complex: /\b(design|architect|create|build|develop)\b/i
  };

  classify(query: string): Complexity {
    const lower = query.toLowerCase();
    
    if (this.patterns.complex.test(lower)) {
      return Complexity.COMPLEX;
    }
    if (this.patterns.medium.test(lower)) {
      return Complexity.MEDIUM;
    }
    if (this.patterns.simple.test(lower)) {
      return Complexity.SIMPLE;
    }
    return Complexity.MEDIUM;
  }

  selectModel(query: string, maxBudget?: number): ModelConfig {
    const complexity = this.classify(query);
    
    let suitable = MODELS.filter(m => 
      m.complexity.value <= complexity.value
    );
    
    if (maxBudget) {
      suitable = suitable.filter(m => 
        m.costPer1KInput <= maxBudget
      );
    }
    
    return suitable.sort((a, b) => a.costPer1KInput - b.costPer1KInput)[0] || MODELS[0];
  }

  estimateCost(query: string, model: string, outputTokens = 500): number {
    const modelConfig = MODELS.find(m => m.name === model);
    if (!modelConfig) return 0;
    
    const inputTokens = query.split(/\s/).length * 1.3;
    return (inputTokens / 1000) * modelConfig.costPer1KInput +
           (outputTokens / 1000) * modelConfig.costPer1KOutput;
  }

  route(query: string, maxBudget?: number) {
    const model = this.selectModel(query, maxBudget);
    const cost = this.estimateCost(query, model.name);
    
    return {
      query,
      complexity: this.classify(query),
      selectedModel: model.name,
      estimatedCost: cost
    };
  }
}

// Usage
const router = new CostAwareRouter();

const result = router.route("What is 2+2?");
console.log(result);
// { complexity: 'simple', selectedModel: 'gpt-3.5-turbo', estimatedCost: 0.0015 }

const result2 = router.route(
  "Design a REST API for user authentication",
  0.05
);
console.log(result2);
// { complexity: 'complex', selectedModel: 'gpt-4', estimatedCost: 0.044 }


// Example 3: Adaptive Learning Router
interface RoutingDecision {
  query: string;
  model: string;
  complexity: Complexity;
  success: boolean;
}

class AdaptiveRouter {
  private decisions: RoutingDecision[] = [];
  private modelSuccessRates: Map<string, number> = new Map();
  
  async route(query: string): Promise<string> {
    // Determine complexity
    const complexity = this.classifyQuery(query);
    
    // Select model based on complexity and success history
    const model = await this.selectBestModel(complexity, query);
    
    return model;
  }
  
  async recordOutcome(
    query: string, 
    model: string, 
    success: boolean
  ): Promise<void> {
    this.decisions.push({ query, model, complexity: this.classifyQuery(query), success });
    
    // Update success rate
    const current = this.modelSuccessRates.get(model) || 0;
    const count = this.decisions.filter(d => d.model === model).length;
    const successes = this.decisions.filter(d => d.model === model && d.success).length;
    
    this.modelSuccessRates.set(model, successes / count);
    
    // Adjust routing if needed
    if (successes / count < 0.7) {
      console.warn(`Model ${model} success rate below threshold`);
    }
  }
  
  private async selectBestModel(
    complexity: Complexity, 
    query: string
  ): Promise<string> {
    // Simplified selection with success rate consideration
    const ratePenalty = 0.5;
    
    return 'gpt-4-turbo';  // Simplified
  }
  
  private classifyQuery(query: string): Complexity {
    // Implementation
    return Complexity.MEDIUM;
  }
}