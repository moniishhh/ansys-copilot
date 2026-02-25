"""Build a ChromaDB vector database from the starter knowledge JSON.

Loads backend/knowledge_base/data/starter_knowledge.json, chunks the
documents, generates OpenAI embeddings, and persists a ChromaDB collection.
Runs 5 test queries at the end to verify retrieval.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_openai import OpenAIEmbeddings

load_dotenv()

KNOWLEDGE_FILE = Path("backend/knowledge_base/data/starter_knowledge.json")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

TEST_QUERIES = [
    "What element should I use for a 3D structural analysis?",
    "My nonlinear analysis won't converge, what should I do?",
    "What are the material properties of steel in ANSYS?",
    "How do I set up a modal analysis in APDL?",
    "How do I use PyMAPDL to run a simulation?",
]


def load_knowledge_docs(knowledge_file: Path = KNOWLEDGE_FILE) -> list[Document]:
    """Load and chunk starter knowledge documents.

    Args:
        knowledge_file: Path to the starter_knowledge.json file.

    Returns:
        List of LangChain Document objects ready for embedding.
    """
    with open(knowledge_file, encoding="utf-8") as fh:
        raw_docs = json.load(fh)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )

    documents: list[Document] = []
    for doc in raw_docs:
        chunks = splitter.split_text(doc["content"])
        for idx, chunk in enumerate(chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": doc["id"],
                        "title": doc["title"],
                        "chunk_index": idx,
                    },
                )
            )

    return documents


def build_vectorstore(documents: list[Document]) -> Chroma:
    """Generate embeddings and persist to ChromaDB.

    Args:
        documents: Chunked Document objects to embed.

    Returns:
        Populated Chroma vector store instance.
    """
    persist_dir = Path(CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="ansys_knowledge",
        persist_directory=str(persist_dir),
    )
    return vectorstore


def run_test_queries(vectorstore: Chroma) -> None:
    """Run test queries and print retrieval results.

    Args:
        vectorstore: The populated Chroma vector store.
    """
    print("\n--- Test Queries ---\n")
    for query in TEST_QUERIES:
        results = vectorstore.similarity_search(query, k=1)
        if results:
            top = results[0]
            source = top.metadata.get("source", "unknown")
            preview = top.page_content[:120].replace("\n", " ")
            print(f"Q: {query}")
            print(f"   Top source: {source}")
            print(f"   Preview: {preview}...")
        else:
            print(f"Q: {query}")
            print("   No results found.")
        print()


def main() -> None:
    """Build the starter vector database and run verification queries."""
    if not KNOWLEDGE_FILE.exists():
        print(f"Knowledge file not found: {KNOWLEDGE_FILE}")
        print("Run scripts/create_starter_knowledge.py first.")
        return

    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY is not set. Please set it in .env or environment.")
        return

    print(f"Loading knowledge from {KNOWLEDGE_FILE}...")
    documents = load_knowledge_docs()
    print(f"Created {len(documents)} chunks from starter knowledge.")

    print(f"\nGenerating embeddings with model '{EMBEDDING_MODEL}'...")
    print(f"Persisting to '{CHROMA_PERSIST_DIR}'...")
    vectorstore = build_vectorstore(documents)
    count = vectorstore._collection.count()
    print(f"Vector database built successfully. Collection size: {count} documents.")

    run_test_queries(vectorstore)
    print("Done.")


if __name__ == "__main__":
    main()
