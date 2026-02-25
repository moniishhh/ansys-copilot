"""Build and persist a ChromaDB vector database from processed document chunks.

Reads the chunks.json file produced by process_data.py, generates OpenAI
embeddings, and stores them in ChromaDB.
"""

import json
from pathlib import Path

from langchain.schema import Document

from backend.knowledge_base.embeddings import create_embeddings

CHUNKS_FILE = Path("backend/knowledge_base/data/processed/chunks.json")


def load_chunks(chunks_file: Path = CHUNKS_FILE) -> list[Document]:
    """Load processed chunks from JSON and convert to LangChain Documents.

    Args:
        chunks_file: Path to the JSON file produced by process_data.py.

    Returns:
        List of ``Document`` objects ready for embedding.
    """
    with open(chunks_file, encoding="utf-8") as fh:
        chunks = json.load(fh)

    documents = [
        Document(
            page_content=chunk["text"],
            metadata={"source": chunk["source"], "chunk_id": chunk["chunk_id"]},
        )
        for chunk in chunks
    ]
    print(f"Loaded {len(documents)} chunks from {chunks_file}")
    return documents


def main() -> None:
    """Build the vector database from processed chunks."""
    if not CHUNKS_FILE.exists():
        print(f"Chunks file not found: {CHUNKS_FILE}")
        print("Run scripts/process_data.py first.")
        return

    docs = load_chunks()
    print(f"Generating embeddings for {len(docs)} chunks…")
    vectorstore = create_embeddings(docs)
    print("Vector database built and persisted successfully.")
    print(f"Collection size: {vectorstore._collection.count()} documents")


if __name__ == "__main__":
    main()
