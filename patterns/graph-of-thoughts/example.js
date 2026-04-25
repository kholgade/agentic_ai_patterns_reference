import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const NodeType = {
    GENERATOR: 'generator',
    AGGREGATOR: 'aggregator',
    CRITIC: 'critic',
    FINAL: 'final'
};

class GraphOfThoughts {
    constructor() {
        this.nodes = new Map();
        this.edges = [];
        this.nodeCounter = 0;
    }
    
    createNode(type, content = '', inputs = []) {
        const id = `node_${this.nodeCounter++}`;
        this.nodes.set(id, {
            id,
            type,
            content,
            inputs,
            outputs: [],
            score: null,
            metadata: {}
        });
        
        for (const inputId of inputs) {
            const inputNode = this.nodes.get(inputId);
            if (inputNode) inputNode.outputs.push(id);
        }
        
        return id;
    }
    
    async processNode(nodeId, systemPrompt, criteria) {
        const node = this.nodes.get(nodeId);
        
        if (node.type === NodeType.GENERATOR) {
            const response = await client.messages.create({
                model: 'claude-sonnet-4-20250514',
                maxTokens: 512,
                messages: [{
                    role: 'user',
                    content: `${systemPrompt}\n\nGenerate insight: ${node.content}`
                }]
            });
            node.content = response.content[0].text;
        }
        else if (node.type === NodeType.AGGREGATOR) {
            const inputsContent = node.inputs
                .map(id => `[${this.nodes.get(id).metadata.label || 'Input'}]: ${this.nodes.get(id).content}`)
                .join('\n');
            
            const response = await client.messages.create({
                model: 'claude-sonnet-4-20250514',
                maxTokens: 512,
                messages: [{
                    role: 'user',
                    content: `${systemPrompt}\n\nSynthesize:\n${inputsContent}`
                }]
            });
            node.content = response.content[0].text;
        }
        else if (node.type === NodeType.CRITIC) {
            const inputContent = node.inputs
                .map(id => this.nodes.get(id).content)
                .join('\n');
            
            const response = await client.messages.create({
                model: 'claude-sonnet-4-20250514',
                maxTokens: 128,
                messages: [{
                    role: 'user',
                    content: `${criteria}\n\nEvaluate:\n${inputContent}`
                }]
            });
            
            const score = parseFloat(response.content[0].text) || 5;
            node.score = Math.min(10, Math.max(1, score));
        }
    }
    
    async solve(sources, prompt, criteria) {
        // Create generator nodes
        for (let i = 0; i < sources.length; i++) {
            const nodeId = this.createNode(
                NodeType.GENERATOR,
                sources[i].content,
                []
            );
            this.nodes.get(nodeId).metadata.label = sources[i].name;
        }
        
        // Create aggregation and critic
        const generators = Array.from(this.nodes.values())
            .filter(n => n.type === NodeType.GENERATOR);
        
        if (generators.length > 1) {
            const genIds = generators.map(n => n.id);
            const aggId = this.createNode(NodeType.AGGREGATOR, '', genIds);
            const criticId = this.createNode(NodeType.CRITIC, '', [aggId]);
            this.nodes.get(criticId).metadata.label = 'Final Evaluation';
        }
        
        // Process nodes
        for (const node of this.nodes.values()) {
            if (!node.content || node.type === NodeType.CRITIC) {
                await this.processNode(node.id, prompt, criteria);
            }
        }
        
        // Return aggregated result
        const aggregator = Array.from(this.nodes.values())
            .find(n => n.type === NodeType.AGGREGATOR);
        
        return aggregator ? aggregator.content : 'No result';
    }
}

// Example usage
const sources = [
    { name: 'Technical Specs', content: 'System handles 10,000 req/s with 50ms latency' },
    { name: 'User Feedback', content: 'App crashes on startup for 5% of users on Android 12' },
    { name: 'Market Research', content: 'Users prefer apps that load in under 3 seconds' }
];

const got = new GraphOfThoughts();
const result = await got.solve(sources, 'Analyze technical performance', 'Rate completeness 1-10');
console.log(result);