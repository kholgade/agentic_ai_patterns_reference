import neo4j from 'neo4j-driver';
import { ChromaClient } from 'langchain/vectorstores/chroma';

class GraphRAG {
    constructor(uri, user, password) {
        this.driver = neo4j.driver(uri, neo4j.auth.basic(user, password));
        this.embeddings = new OpenAIEmbeddings();
        this.llm = new ChatOpenAI({ model: 'gpt-4o', temperature: 0 });
    }

    async extractEntities(text) {
        const entities = [];
        const regex = /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/g;
        let match;

        while ((match = regex.exec(text)) !== null) {
            entities.push({ name: match[1], type: 'ENTITY' });
        }

        return entities;
    }

    async buildGraph(documents) {
        const session = this.driver.session();

        try {
            for (const doc of documents) {
                const entities = await this.extractEntities(doc.pageContent);

                for (const entity of entities) {
                    await session.run(
                        'MERGE (e:Entity {name: $name, type: $type})',
                        { name: entity.name, type: entity.type }
                    );
                }

                await session.run(
                    'CREATE (d:Document {content: $content, metadata: $metadata})',
                    { content: doc.pageContent, metadata: JSON.stringify(doc.metadata) }
                );
            }
        } finally {
            await session.close();
        }
    }

    async queryGraph(query, maxHops = 2) {
        const session = this.driver.session();
        const entities = await this.extractEntities(query);

        if (entities.length === 0) {
            return { nodes: [], edges: [] };
        }

        const central = entities[0].name;

        try {
            const result = await session.run(`
                MATCH (e:Entity)
                WHERE e.name CONTAINS $name
                OPTIONAL MATCH path = (e)-[r:RELATES*1..${maxHops}]-(connected)
                RETURN nodes(path) as nodes, relationships(path) as rels
            `, { name: central });

            const nodes = new Map();
            const edges = [];

            for (const record of result.records) {
                for (const node of record.get('nodes') || []) {
                    nodes.set(node.properties.name, node.properties);
                }
                for (const rel of record.get('rels') || []) {
                    edges.push({
                        source: rel.start.properties.name,
                        target: rel.end.properties.name,
                        type: rel.type
                    });
                }
            }

            return {
                central,
                nodes: Array.from(nodes.values()),
                edges
            };
        } finally {
            await session.close();
        }
    }

    async answer(query) {
        const graphContext = await this.queryGraph(query);
        const vectorResults = await this.vectorStore.similaritySearch(query, 5);

        const context = `
Knowledge Graph:
Central: ${graphContext.central}
Entities: ${graphContext.nodes.map(n => n.name).join(', ')}
Relationships: ${graphContext.edges.map(e =>
            `${e.source} --(${e.type})--> ${e.target}`).join(', ')}

Documents:
${vectorResults.map(d => d.pageContent).join('\n\n')}
        `;

        const response = await this.llm.invoke(`
Context: ${context}
Question: ${query}
Answer based on the context provided.
        `);

        return response.content;
    }
}

const graphRag = new GraphRAG('bolt://localhost:7687', 'neo4j', 'password');
await graphRag.buildGraph(documents);
const answer = await graphRag.answer("What are the relationships between companies X and Y?");