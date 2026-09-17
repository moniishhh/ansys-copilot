"""RAG engine using LangChain, HuggingFace embeddings, and ChromaDB for ANSYS knowledge retrieval."""

import json
from operator import itemgetter
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings

from backend.config import settings
from backend.services.llm_service import create_chat_model

RAG_PROMPT_TEMPLATE = """You are an expert ANSYS simulation engineer.
Use the following retrieved context and conversation history to answer the question.
If the context doesn't contain enough information, rely on your general ANSYS knowledge.

Context:
{context}

Conversation History:
{history}

Question: {question}

Answer:"""


def _format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

def _format_history(history: list[dict] | None) -> str:
    if not history:
        return "No prior conversation history."
    formatted = []
    for msg in history:
        role = "User" if msg.get("role") == "user" else "Assistant"
        formatted.append(f"{role}: {msg.get('content')}")
    return "\n".join(formatted)


class RAGEngine:
    """Retrieval-Augmented Generation pipeline backed by ChromaDB.

    On first use, if the vector store is empty or absent, queries fall back
    to pure LLM generation without retrieval context.

    Embeddings are computed locally using a HuggingFace sentence-transformers
    model (all-MiniLM-L6-v2 by default) — no embedding API key required.
    """

    def __init__(self) -> None:
        self._chain = None
        self._vectorstore: Chroma | None = None
        self._retriever = None

    def initialize(self) -> None:
        """Set up the embedding model, vector store, and RAG chain."""
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
        )

        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self._vectorstore = Chroma(
            collection_name="ansys_knowledge",
            embedding_function=embeddings,
            persist_directory=str(persist_dir),
        )

        # Populate a fresh cloud instance from the bundled starter knowledge.
        if self._vectorstore._collection.count() == 0:
            starter_file = Path("backend/knowledge_base/data/starter_knowledge.json")
            if starter_file.exists():
                records = json.loads(starter_file.read_text(encoding="utf-8"))
                self._vectorstore.add_documents([
                    Document(
                        page_content=record["content"],
                        metadata={"source": record["title"], "document_id": record["id"]},
                    )
                    for record in records
                ])

        llm = create_chat_model()

        prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        self._retriever = self._vectorstore.as_retriever(search_kwargs={"k": 5})

        self._chain = (
            {
                "context": itemgetter("question") | self._retriever | _format_docs,
                "question": itemgetter("question"),
                "history": itemgetter("history"),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

    def query(self, question: str, history: list[dict] | None = None, k: int = 5) -> dict:
        """Run a question through the RAG pipeline.

        Args:
            question: The user's ANSYS-related question.
            history: Optional list of previous chat messages.
            k: Number of context documents to retrieve.

        Returns:
            Dictionary with keys ``answer`` and ``sources``.
        """
        if self._chain is None:
            self.initialize()

        answer = self._chain.invoke({
            "question": question,
            "history": _format_history(history)
        })

        # Retrieve source metadata separately
        sources = []
        if self._retriever:
            docs = self._retriever.invoke(question)
            sources = [doc.metadata.get("source", "") for doc in docs]

        return {"answer": answer, "sources": sources}
