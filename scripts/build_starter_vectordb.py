import json
import os
from pathlib import Path
from dotenv import load_dotenv

from langchain.schema import Document
from backend.knowledge_base.embeddings import create_embeddings

load_dotenv()

DATA_PATH = Path("backend/knowledge_base/data/starter_knowledge.json")

def build_vectordb():
    print("Loading knowledge base...")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)

    docs = []
    for doc in documents:
        docs.append(
            Document(
                page_content=doc["content"],
                metadata={"id": doc["id"], "title": doc["title"]}
            )
        )

    print(f"Loaded {len(docs)} documents")
    print("Creating embeddings and building ChromaDB...")

    vectorstore = create_embeddings(docs)

    print(f"✅ Vector database built successfully.")

if __name__ == "__main__":
    build_vectordb()