import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

class TreeOfThoughts {
    constructor(options = {}) {
        this.maxDepth = options.maxDepth || 3;
        this.maxBranches = options.maxBranches || 3;
        this.nodes = new Map();
        this.nodeCounter = 0;
    }
    
    createNode(content, parentId = null) {
        const id = `node_${this.nodeCounter++}`;
        const node = {
            id,
            content,
            parentId,
            children: [],
            depth: parentId ? this.nodes.get(parentId).depth + 1 : 0,
            score: null,
            state: 'pending'
        };
        this.nodes.set(id, node);
        
        if (parentId) {
            this.nodes.get(parentId).children.push(id);
        }
        
        return id;
    }
    
    async expandNode(nodeId, evaluatorPrompt) {
        const node = this.nodes.get(nodeId);
        if (node.depth >= this.maxDepth) return [];
        
        const prompt = `${evaluatorPrompt}

Generate ${this.maxBranches} different approaches for:
"${node.content}"

Format as:
Option 1: [brief description] because [reasoning]`;
        
        const response = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 1024,
            messages: [{ role: 'user', content: prompt }]
        });
        
        const newNodeIds = [];
        const lines = response.content[0].text.split('\n');
        
        for (const line of lines) {
            const match = line.match(/Option \d+:\s*(.+?)\s+because\s+(.+)/);
            if (match) {
                const nodeId = this.createNode(match[2].trim(), nodeId);
                newNodeIds.push(nodeId);
            }
        }
        
        node.state = 'completed';
        return newNodeIds;
    }
    
    async evaluateNode(nodeId) {
        const node = this.nodes.get(nodeId);
        
        const response = await client.messages.create({
            model: 'claude-sonnet-4-20250514',
            maxTokens: 32,
            messages: [{
                role: 'user',
                content: `Rate this thought 1-10: "${node.content}"`
            }]
        });
        
        const score = parseFloat(response.content[0].text) || 5;
        node.score = Math.min(10, Math.max(1, score));
        return node.score;
    }
    
    getBestPath() {
        const leaves = Array.from(this.nodes.values())
            .filter(n => n.children.length === 0);
        
        if (!leaves.length) return [];
        
        const best = leaves.reduce((a, b) => 
            (a.score || 0) > (b.score || 0) ? a : b
        );
        
        const path = [];
        let current = best;
        while (current) {
            path.unshift(current);
            current = current.parentId ? this.nodes.get(current.parentId) : null;
        }
        
        return path;
    }
    
    async solve(problem, evaluatorPrompt) {
        const rootId = this.createNode(problem);
        let frontier = [rootId];
        
        for (let depth = 0; depth < this.maxDepth && frontier.length; depth++) {
            const newFrontier = [];
            for (const nodeId of frontier) {
                const children = await this.expandNode(nodeId, evaluatorPrompt);
                for (const childId of children) {
                    await this.evaluateNode(childId);
                    newFrontier.push(childId);
                }
            }
            frontier = newFrontier;
        }
        
        const path = this.getBestPath();
        return path.map((n, i) => `Step ${i + 1}: ${n.content}`).join('\n');
    }
}

// Example usage
const tot = new TreeOfThoughts({ maxDepth: 3, maxBranches: 2 });
const evaluator = "You are evaluating software architecture options.";
const problem = "How to design a microservices architecture for a startup?";

const solution = await tot.solve(problem, evaluator);
console.log(solution);