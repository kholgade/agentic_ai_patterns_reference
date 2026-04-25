from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.chains import GraphQAChain
from langchain_core.documents import Document
from typing import List
import spacy

class GraphRAG:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.graph = Neo4jGraph(
            url=neo4j_uri,
            username=neo4j_user,
            password=neo4j_password
        )
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.nlp = spacy.load("en_core_web_sm")

    def extract_entities(self, text: str) -> List[dict]:
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                "name": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        return entities

    def extract_relationships(self, text: str) -> List[dict]:
        doc = self.nlp(text)
        relationships = []
        for token in doc:
            if token.dep_ in ("nsubj", "dobj", "prep"):
                subj = [t for t in token.subtree_ if t.dep_ == "nsubj"]
                obj = [t for t in token.subtree_ if t.dep_ == "dobj"]
                if subj and obj:
                    relationships.append({
                        "source": subj[0].text,
                        "target": obj[0].text,
                        "type": token.lemma_
                    })
        return relationships

    async def build_graph_from_documents(self, documents: List[Document]):
        for doc in documents:
            entities = self.extract_entities(doc.page_content)
            relationships = self.extract_relationships(doc.page_content)

            for entity in entities:
                self.graph.query("""
                    MERGE (e:Entity {name: $name, type: $type})
                """, params={"name": entity["name"], "type": entity["type"]})

            for rel in relationships:
                self.graph.query("""
                    MATCH (s:Entity {name: $source})
                    MATCH (t:Entity {name: $target})
                    MERGE (s)-[r:RELATES {type: $type}]->(t)
                """, params=rel)

            self.graph.query("""
                CREATE (d:Document {
                    content: $content,
                    metadata: $metadata
                })
            """, params={
                "content": doc.page_content,
                "metadata": str(doc.metadata)
            })

    def query_graph(self, query: str, max_hops: int = 2) -> dict:
        central_entities = self.extract_entities(query)

        if not central_entities:
            return {"nodes": [], "edges": [], "paths": []}

        central = central_entities[0]["name"]

        nodes_query = """
            MATCH (e:Entity)
            WHERE e.name CONTAINS $name
            OPTIONAL MATCH path = (e)-[:RELATES*1..%d]-(connected)
            RETURN nodes(path) as nodes, relationships(path) as edges
        """ % max_hops

        result = self.graph.query(nodes_query, params={"name": central})

        nodes = set()
        edges = []
        for record in result:
            for node in record["nodes"] or []:
                nodes.add({"id": node["name"], "type": node.get("type", "UNKNOWN")})
            for edge in record["edges"] or []:
                edges.append({
                    "source": edge["start"]["name"],
                    "target": edge["end"]["name"],
                    "type": edge.get("type", "RELATES")
                })

        return {"nodes": list(nodes), "edges": edges, "central": central}

    def hybrid_retrieve(self, query: str, k: int = 5) -> List[Document]:
        graph_context = self.query_graph(query)

        vector_results = self.vectorstore.similarity_search(query, k=k)

        combined_context = f"Knowledge Graph Context:\n"
        combined_context += f"Central Entity: {graph_context['central']}\n"
        combined_context += "Related Entities: " + ", ".join([
            n["id"] for n in graph_context["nodes"][:10]
        ]) + "\n"
        combined_context += "Relationships: " + ", ".join([
            f"{e['source']} --({e['type']})--> {e['target']}"
            for e in graph_context["edges"][:10]
        ]) + "\n\n"

        for doc in vector_results:
            combined_context += f"\n--- Retrieved Document ---\n{doc.page_content}"

        return combined_context

    def build_qa_chain(self):
        return GraphQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True
        )

    async def answer_question(self, query: str) -> str:
        context = self.hybrid_retrieve(query)

        prompt = f"""Based on the following context from a knowledge graph and retrieved documents,
answer the question thoroughly. Include specific entity names and relationships when relevant.

Context:
{context}

Question: {query}

Answer:"""

        response = await self.llm.ainvoke(prompt)
        return response.content

graph_rag = GraphRAG(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

await graph_rag.build_graph_from_documents(documents)
answer = await graph_rag.answer_question(
    "What companies has the CEO of Acme Corp previously worked for?"
)