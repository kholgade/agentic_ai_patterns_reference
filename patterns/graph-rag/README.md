---


# Graph RAG
title: "Graph RAG"
description: "RAG leveraging knowledge graphs for entity-based retrieval and multi-hop queries."
complexity: "high"
model_maturity: "advanced"
typical_use_cases: ["Entity-rich domains", "Multi-hop questions", "Knowledge graph systems"]
dependencies: ["basic-rag"]
category: "rag"
---

# Graph RAG



# 32. Graph RAG (Knowledge Graph Based Retrieval)

## Overview

Graph RAG leverages structured knowledge graphs to enhance retrieval by capturing entities, relationships, and semantic connections between concepts. Instead of treating documents as isolated chunks, Graph RAG models the world as a network of interconnected entities—people, places, organizations, concepts—connected by typed relationships like "works_for," "located_in," or "causes." This structural understanding enables more intelligent retrieval: queries about specific entities can traverse the graph to find related information, and answers can be constructed by assembling paths through the knowledge graph.

The knowledge graph serves as both a semantic index and an inference engine. During indexing, named entity recognition and relationship extraction identify entities and their connections from documents, building a graph structure alongside traditional vector embeddings. At query time, the system can either traverse the graph directly (using graph queries like Cypher or SPARQL) or use a hybrid approach where graph context enriches vector search results. Graph RAG excels at multi-hop questions where the answer requires connecting information across multiple documents—questions like "Who was the CEO of the company that acquired X?" or "What proteins interact with disease Y?"

The practical benefits extend beyond query capability. Knowledge graphs provide interpretability—you can trace exactly which entities and relationships contributed to an answer. They support logical inference, enabling the system to deduce new facts from existing knowledge. They handle schema evolution gracefully, adding new entity types or relationships without retraining. However, building and maintaining quality knowledge graphs requires upfront investment in entity extraction, relation classification, and graph curation, making this pattern most valuable for domains with rich entity relationships like biomedical research, legal documents, or enterprise knowledge management.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       GRAPH RAG FLOW                                │
└─────────────────────────────────────────────────────────────────────┘

INDEXING PHASE:
┌─────────────────────────────────────────────────────────────────────┐
│  ┌──────────┐    ┌────────────────┐    ┌──────────────────────────┐ │
│  │  RAW     │───▶│   ENTITY       │───▶│    KNOWLEDGE GRAPH      │ │
│  │ DOCUMENTS│    │   EXTRACTION   │    │  (nodes + edges)        │ │
│  └──────────┘    │  (NER, REL)    │    │                          │ │
│                  └────────────────┘    │    ┌───┐    ┌───┐       │ │
│                                         │   │ A │───▶│ B │       │ │
│  ┌──────────┐    ┌────────────────┐    │   └─┬─┘    └───┘       │ │
│  │  TEXT    │───▶│   VECTOR       │───▶│     │                   │ │
│  │  CHUNKS  │    │   EMBEDDINGS   │    │    ┌┴┐                  │ │
│  └──────────┘    └────────────────┘    │    │ C │◀──────────    │ │
│                                         │    └───┘              │ │
│                                         └──────▲─────────────────┘ │
│                                                │                   │
│                                    ┌───────────┴───────────┐      │
│                                    │  VECTOR STORAGE       │      │
│                                    │  (chunks with entity  │      │
│                                    │   references)        │      │
│                                    └───────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘

QUERY PHASE:
┌─────────────────────────────────────────────────────────────────────┐
│                          USER QUERY                                  │
│                            "..."                                     │
│                             │                                        │
│                    ┌────────▼────────┐                              │
│                    │   GRAPH PARSE   │                              │
│                    │ (entity extract │                              │
│                    │  + intent detect)│                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│            ┌────────────────┼────────────────┐                      │
│            ▼                ▼                ▼                      │
│    ┌────────────┐  ┌──────────────┐  ┌─────────────┐               │
│    │ GRAPH TRAV │  │ VECTOR SEARCH │  │  HYBRID    │               │
│    │(cypher/SPAR│  │(entity-centric│  │  RETRIEVE  │               │
│    │QL query)   │  │  search)      │  │            │               │
│    └─────┬──────┘  └──────┬───────┘  └──────┬──────┘               │
│          │                │                 │                      │
│          └────────────────┴─────────────────┘                      │
│                           │                                         │
│                    ┌───────▼───────┐                                │
│                    │  CONTEXT ASSEMBLY                              │
│                    │ (subgraph + docs + relationships)             │
│                    └───────┬───────┘                                │
│                            │                                        │
│                    ┌───────▼───────┐                                │
│                    │     LLM       │                                │
│                    │ (graph-aware  │                                │
│                    │  generation)  │                                │
│                    └───────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
```

## Code Implementation

### Python (Using Neo4j + LangChain)

### JavaScript

## Examples

### Example 1: Multi-Hop Relationship Query

```
Query: "Who was the doctoral advisor of the person who invented X?"
Graph Traversal:
  1. Find "invention of X" → Person A
  2. Traverse "advisor_of" relationship → Person B
  3. Return Path: Person A ←(student_of)─ Person B
Response: "Person A was supervised by Person B during their PhD at University X."
```

### Example 2: Entity-Centric Document Retrieval

```
Query: "What projects did Company X work on with Company Y?"
Graph Query: Company X --(collaborated_with)--> Company Y
Retrieval: Returns project documents linked to both entities
Response: "Company X collaborated with Company Y on:
  - Project Alpha (2021-2022): Cloud infrastructure
  - Project Beta (2023): AI integration"
```

### Example 3: Relationship Chain Reasoning

```
Query: "Which drugs treat diseases caused by bacteria resistant to antibiotic X?"
Graph Traversal:
  1. Find antibiotic X → Resistance mechanism
  2. Find diseases with this resistance mechanism
  3. Find drugs treating those diseases
Response: "Based on the knowledge graph:
  - Drug A treats Disease B (which shows resistance to antibiotic X)
  - Drug C is in Phase 3 trials for similar resistance mechanisms"
```

## References

- [GraphRAG from Microsoft Research](https://www.microsoft.com/en-us/research/project/graphrag/)
- [Neo4j LangChain Integration](https://python.langchain.com/docs/integrations/graphs/neo4j)
- [Knowledge Graph Construction](https://python.langchain.com/docs/experimental/graph_transformers)
- [Graphrag-py Library](https://github.com/microsoft/graphrag)
- [Entity Extraction with spaCy](https://spacy.io/usage/linguistic-features#named-entities)


From [Yashodhan Kholgade](https://github.com/kholgade/agentic_ai_patterns_reference) (2026)
