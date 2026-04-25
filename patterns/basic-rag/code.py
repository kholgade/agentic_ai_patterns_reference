from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader

def build_basic_rag(index_dir: str = "./vector_store"):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(persist_directory=index_dir, embedding_function=embeddings)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain

def index_documents(doc_path: str, index_dir: str = "./vector_store"):
    from langchain_community.document_loaders import TextLoader

    loader = DirectoryLoader(doc_path, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=index_dir
    )
    vectorstore.persist()
    return vectorstore

if __name__ == "__main__":
    index_documents("./knowledge_base")
    qa = build_basic_rag("./vector_store")

    question = "What are the main components of a transformer model?"
    result = qa.invoke({"query": question})
    print(f"Answer: {result['result']}")
    for i, doc in enumerate(result['source_documents']):
        print(f"Source {i+1}: {doc.metadata.get('source', 'Unknown')}")