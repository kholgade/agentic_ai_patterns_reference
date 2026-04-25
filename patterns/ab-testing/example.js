interface ExperimentVariant {
  id: string;
  name: string;
  config: Record<string, any>;
  weight: number;
}

interface MetricResult {
  values: number[];
  mean: number;
  std: number;
}

interface ExperimentConfig {
  id: string;
  variants: ExperimentVariant[];
  metrics: string[];
  traffic_split?: number[];
}

class ABTester {
  private experiment: ExperimentConfig;
  private results: Map<string, Map<string, number[]>> = new Map();
  
  constructor(config: ExperimentConfig) {
    this.experiment = config;
    config.variants.forEach(v => 
      this.results.set(v.id, new Map())
    );
  }
  
  selectVariant(): string {
    const variants = this.experiment.variants;
    const weights = variants.map(v => v.weight);
    const total = weights.reduce((a, b) => a + b, 0);
    const rand = Math.random() * total;
    
    let cumulative = 0;
    for (const variant of variants) {
      cumulative += variant.weight;
      if (rand <= cumulative) {
        return variant.id;
      }
    }
    
    return variants[variants.length - 1].id;
  }
  
  recordResult(variantId: string, results: Record<string, number>): void {
    const variantResults = this.results.get(variantId);
    if (!variantResults) return;
    
    for (const [metric, value] of Object.entries(results)) {
      if (!variantResults.has(metric)) {
        variantResults.set(metric, []);
      }
      variantResults.get(metric)!.push(value);
    }
  }
  
  analyze(): Record<string, any> {
    const analysis: Record<string, any> = {
      experiment_id: this.experiment.id,
      variants: {},
      conclusions: []
    };
    
    const variantIds = Array.from(this.results.keys());
    const control = this.results.get(variantIds[0]);
    const treatment = this.results.get(variantIds[1]);
    
    if (!control || !treatment) return analysis;
    
    for (const metric of this.experiment.metrics) {
      const controlVals = control.get(metric) || [];
      const treatmentVals = treatment.get(metric) || [];
      
      if (controlVals.length < 10 || treatmentVals.length < 10) continue;
      
      const controlMean = controlVals.reduce((a, b) => a + b, 0) / controlVals.length;
      const treatmentMean = treatmentVals.reduce((a, b) => a + b, 0) / treatmentVals.length;
      
      // Simple t-test approximation
      const diff = treatmentMean - controlMean;
      const significant = Math.abs(diff) > 0.1;  // Simplified
      
      analysis.variants[metric] = {
        control_mean: controlMean,
        treatment_mean: treatmentMean,
        lift: ((diff / controlMean) * 100).toFixed(2) + '%',
        significant
      };
      
      if (significant) {
        analysis.conclusions.push(
          `${metric} improved by ${Math.abs(diff).toFixed(2)} with ${treatmentVals.length > controlVals.length ? 'treatment' : 'control'}`
        );
      }
    }
    
    return analysis;
  }
  
  toJSON(): string {
    const results: Record<string, any> = {};
    
    for (const [variantId, metrics] of this.experiment) {
      const variantResults: Record<string, any> = {};
      
      for (const [metric, values] of this.results.get(variantId)) {
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        variantResults[metric] = { sample_size: values.length, mean };
      }
      
      results[variantId] = variantResults;
    }
    
    return JSON.stringify(results, null, 2);
  }
}

// Usage
const experiment = new ABTester({
  id: 'cot-comparison',
  variants: [
    { id: 'control', name: 'No CoT', config: { prefix: '' }, weight: 1 },
    { id: 'treatment', name: 'With CoT', config: { prefix: 'Think step by step.\n' }, weight: 1 }
  ],
  metrics: ['accuracy', 'latency']
});

async function runExperiment(n: number): Promise<void> {
  for (let i = 0; i < n; i++) {
    const variantId = experiment.selectVariant();
    const variant = experiment.variants.find(v => v.id === variantId);
    
    const response = await callLLM('What is 7+3?', variant.config);
    const metrics = evaluateResponse(response);
    
    experiment.recordResult(variantId, metrics);
  }
}

function evaluateResponse(response: string): Record<string, number> {
  return {
    accuracy: response.includes('10') ? 1 : 0,
    latency: Math.random() * 2
  };
}


// Example 3: Bayesian Optimization for Hyperparameters
interface HyperparamConfig {
  temperature: number;
  max_tokens: number;
  top_p: number;
}

interface TrialResult {
  config: HyperparamConfig;
  score: number;
}

class BayesianOptimizer {
  private trials: TrialResult[] = [];
  private bestConfig: HyperparamConfig | null = null;
  private bestScore: number = -Infinity;
  
  async optimize(
    objective: (config: HyperparamConfig) => Promise<number>,
    n_trials: number = 20
  ): Promise<HyperparamConfig> {
    const search_space: HyperparamConfig[] = [
      { temperature: 0.0, max_tokens: 100, top_p: 0.9 },
      { temperature: 0.3, max_tokens: 200, top_p: 0.95 },
      { temperature: 0.7, max_tokens: 500, top_p: 1.0 },
      // Grid search + random variations
    ];
    
    for (const config of search_space.slice(0, 5)) {
      const score = await objective(config);
      this.trials.push({ config, score });
      
      if (score > this.bestScore) {
        this.bestScore = score;
        this.bestConfig = config;
      }
    }
    
    // Bayesian optimization loop
    for (let i = 0; i < n_trials - 5; i++) {
      const config = this._selectNextConfig();
      const score = await objective(config);
      
      this.trials.push({ config, score });
      
      if (score > this.bestScore) {
        this.bestScore = score;
        this.bestConfig = config;
      }
    }
    
    return this.bestConfig;
  }
  
  private _selectNextConfig(): HyperparamConfig {
    // Simplified: explore around best config
    return {
      temperature: 0.5 + (Math.random() - 0.5) * 0.3,
      max_tokens: 200 + Math.floor(Math.random() * 300),
      top_p: 0.9 + Math.random() * 0.1
    };
  }
}