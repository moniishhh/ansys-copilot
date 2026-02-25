"""RAG engine using LangChain and ChromaDB for ANSYS knowledge retrieval."""

from pathlib import Path

from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from backend.config import settings


class RAGEngine:
    """Retrieval-Augmented Generation pipeline backed by ChromaDB.

    On first use, if the vector store is empty or absent, queries fall back
    to pure LLM generation without retrieval context.
    """

    def __init__(self) -> None:
        self._qa_chain: RetrievalQA | None = None
        self._vectorstore: Chroma | None = None

    def initialize(self) -> None:
        """Set up the embedding model, vector store, and QA chain."""
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )

        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self._vectorstore = Chroma(
            collection_name="ansys_knowledge",
            embedding_function=embeddings,
            persist_directory=str(persist_dir),
        )

        llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key,
        )

        self._qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self._vectorstore.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
        )

    def query(self, question: str, k: int = 5) -> dict:
        """Run a question through the RAG pipeline.

        Args:
            question: The user's ANSYS-related question.
            k: Number of context documents to retrieve.

        Returns:
            Dictionary with keys ``answer`` and ``sources``.
        """
        if self._qa_chain is None:
            self.initialize()

        result = self._qa_chain.invoke({"query": question})
        sources = [
            doc.metadata.get("source", "")
            for doc in result.get("source_documents", [])
        ]
        return {"answer": result["result"], "sources": sources}
