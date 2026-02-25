"""Embedding generation and ChromaDB vector store management."""

from pathlib import Path

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from backend.config import settings


def create_embeddings(docs: list[Document]) -> Chroma:
    """Generate embeddings for a list of documents and persist them to ChromaDB.

    Args:
        docs: List of chunked ``Document`` objects to embed.

    Returns:
        Populated ``Chroma`` vector store instance.
    """
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="ansys_knowledge",
        persist_directory=str(persist_dir),
    )
    return vectorstore


def query_similar(query: str, k: int = 5) -> list[Document]:
    """Retrieve the top-k most similar documents for a given query.

    Args:
        query: The search string.
        k: Number of results to return.

    Returns:
        List of the most similar ``Document`` objects.
    """
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )

    vectorstore = Chroma(
        collection_name="ansys_knowledge",
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir,
    )

    return vectorstore.similarity_search(query, k=k)
