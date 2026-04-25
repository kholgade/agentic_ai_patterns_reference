from langchain_community.vectorstores import Chroma, FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from sentence_transformers import CrossEncoder
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class AdvancedRAG:
    def __init__(self, embedding_model="sentence-transformers/all-MiniLM-L6-v2"):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

    def build_hybrid_retriever(self, chunks, k=10):
        faiss_index = FAISS.from_texts(chunks, self.embeddings)
        vector_retriever = faiss_index.as_retriever(search_kwargs={"k": k})

        bm25_retriever = BM25Retriever.from_texts(chunks)
        bm25_retriever.k = k

        return vector_retriever, bm25_retriever

    def reciprocal_rank_fusion(self, results_list, k=60):
        fused_scores = {}
        for results in results_list:
            for rank, doc in enumerate(results):
                doc_id = doc.page_content[:50]
                fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (k + rank + 1)

        sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc for doc_id, _ in sorted_docs for results in results_list for doc in results
                if doc.page_content[:50] == doc_id]

    def rerank_documents(self, query, documents, top_k=5):
        reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")
        pairs = [(query, doc.page_content) for doc in documents]
        scores = reranker.predict(pairs)

        doc_scores = list(zip(documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in doc_scores[:top_k]]

    def query_transformation(self, query):
        rewrite_prompt = PromptTemplate.from_template(
            """Rewrite this query to match the vocabulary typically used in technical documentation.
            Query: {query}
            Rewritten query:"""
        )
        chain = rewrite_prompt | self.llm
        return chain.invoke({"query": query})

    def decompose_query(self, query):
        decomp_prompt = PromptTemplate.from_template(
            """Break this complex question into 2-3 simpler sub-questions that can be answered independently.
            Question: {query}
            Sub-questions:"""
        )
        chain = decomp_prompt | self.llm
        return chain.invoke({"query": query})

    def build_qa_chain(self, retriever):
        prompt = PromptTemplate.from_template(
            """Context: {context}
            Question: {question}
            Answer based only on the provided context. If the context is insufficient, say so."""
        )

        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt}
        )

rag = AdvancedRAG()
vector_retriever, bm25_retriever = rag.build_hybrid_retriever(chunks)

original_results = vector_retriever.get_relevant_documents(user_query)
bm25_results = bm25_retriever.get_relevant_documents(user_query)

fused = rag.reciprocal_rank_fusion([original_results, bm25_results])
reranked = rag.rerank_documents(user_query, fused, top_k=5)