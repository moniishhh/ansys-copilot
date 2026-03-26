import json
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

load_dotenv()

DATA_PATH = Path("backend/knowledge_base/data/starter_knowledge.json")
DB_PATH = Path("backend/knowledge_base/faiss_index")

def build_vectordb():
    print("Loading knowledge base...")
    with open(DATA_PATH, "r") as f:
        documents = json.load(f)

    texts = [doc["content"] for doc in documents]
    metadatas = [{"id": doc["id"], "title": doc["title"]} for doc in documents]

    print(f"Loaded {len(texts)} documents")
    print("Loading embedding model (first run downloads ~90MB)...")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Creating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    DB_PATH.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(DB_PATH / "index.faiss"))
    with open(DB_PATH / "metadata.pkl", "wb") as f:
        pickle.dump({"texts": texts, "metadatas": metadatas}, f)

    print(f"✅ Vector database built successfully at {DB_PATH}")
    print(f"   Indexed {index.ntotal} documents")

if __name__ == "__main__":
    build_vectordb()