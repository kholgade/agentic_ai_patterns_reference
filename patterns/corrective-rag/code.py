from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from typing import Literal
import json

class CorrectiveRAG:
    def __init__(self, vectorstore, web_search_tool=None):
        self.vectorstore = vectorstore
        self.web_search = web_search_tool
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

        self.relevance_prompt = PromptTemplate.from_template(
            """Evaluate if the retrieved documents are relevant to the query.
            Query: {query}
            Documents: {documents}

            Rate relevance from 0-10 and explain briefly.
            Format: SCORE: <number>, REASON: <explanation>"""
        )

        self.support_prompt = PromptTemplate.from_template(
            """Verify if the retrieved documents support the stated claim.
            Claim: {claim}
            Documents: {documents}

            Is the claim supported by the documents? Answer YES/PARTIAL/NO.
            If partial or no, quote the specific contradicting evidence."""
        )

        self.answer_prompt = PromptTemplate.from_template(
            """Based on the following context, answer the user's question.
            If the context is insufficient, say "I don't know" rather than guessing.

            Context: {context}
            Question: {question}

            Answer:"""
        )

    async def evaluate_relevance(self, query: str, docs: list[Document]) -> dict:
        doc_text = "\n\n".join([d.page_content for d in docs])
        chain = LLMChain(llm=self.llm, prompt=self.relevance_prompt)
        result = await chain.arun({"query": query, "documents": doc_text})

        score = int(result.split("SCORE: ")[1].split(",")[0]) if "SCORE:" in result else 0
        return {"score": score, "explanation": result}

    async def verify_claim_support(self, claim: str, docs: list[Document]) -> dict:
        doc_text = "\n\n".join([d.page_content for d in docs])
        chain = LLMChain(llm=self.llm, prompt=self.support_prompt)
        result = await chain.arun({"claim": claim, "documents": doc_text})

        verdict = "YES" if "YES" in result.upper()[:10] else "PARTIAL" if "PARTIAL" in result.upper()[:10] else "NO"
        return {"verdict": verdict, "explanation": result}

    async def correct_retrieval(
        self, query: str, docs: list[Document], relevance_threshold: int = 5
    ) -> tuple[list[Document], str]:
        relevance = await self.evaluate_relevance(query, docs)

        if relevance["score"] >= 7:
            return docs, "high"

        elif relevance["score"] >= relevance_threshold:
            expanded_query = await self.expand_query(query)
            new_docs = self.vectorstore.similarity_search(expanded_query, k=10)
            return new_docs, "retry"

        elif self.web_search:
            web_results = await self.web_search(query)
            return [Document(page_content=web_results)], "web"

        else:
            return [], "fallback"

    async def expand_query(self, query: str) -> str:
        expand_prompt = PromptTemplate.from_template(
            "Rephrase this query to improve document retrieval:\n{query}"
        )
        chain = LLMChain(llm=self.llm, prompt=expand_prompt)
        return await chain.arun({"query": query})

    async def generate_with_correction(self, query: str) -> dict:
        initial_docs = self.vectorstore.similarity_search(query, k=5)
        docs, action = await self.correct_retrieval(query, initial_docs)

        if action == "fallback":
            return {
                "answer": "I don't have sufficient information to answer this question.",
                "source": "none",
                "corrective_action": "fallback"
            }

        if action == "web":
            source = "web_search"
        else:
            source = "vector_store"

        answer_prompt = PromptTemplate.from_template(
            "Context: {context}\n\nQuestion: {question}\n\nAnswer only from context."
        )
        chain = LLMChain(llm=self.llm, prompt=answer_prompt)
        context = "\n\n".join([d.page_content for d in docs])
        answer = await chain.arun({"context": context, "question": query})

        claim_verification = await self.verify_claim_support(answer, docs)
        if claim_verification["verdict"] == "NO":
            answer = "I cannot confidently answer this based on available information."

        return {
            "answer": answer,
            "source": source,
            "corrective_action": action,
            "relevance_score": docs[0].metadata.get("relevance", "N/A") if docs else "N/A",
            "documents_used": len(docs)
        }

crag = CorrectiveRAG(vectorstore, web_search_tool= TavilySearchResults())
result = await crag.generate_with_correction(
    "What are the latest developments in quantum computing?"
)