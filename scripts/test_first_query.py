import pickle
import os
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss
import anthropic

load_dotenv()

DB_PATH = Path("backend/knowledge_base/faiss_index")

def search(query, top_k=3):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index(str(DB_PATH / "index.faiss"))
    with open(DB_PATH / "metadata.pkl", "rb") as f:
        data = pickle.load(f)

    query_vec = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vec, top_k)

    results = []
    for i in indices[0]:
        if i != -1:
            results.append({
                "text": data["texts"][i],
                "metadata": data["metadatas"][i]
            })
    return results

def ask_claude(query):
    print(f"\n🔍 Query: {query}")
    print("Searching knowledge base...")

    results = search(query)
    context = "\n\n".join([f"[{r['metadata']['title']}]\n{r['text']}" for r in results])

    print(f"Found {len(results)} relevant documents")
    print("Asking Claude...\n")

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are an ANSYS engineering assistant. Use the context below to answer the question.

Context:
{context}

Question: {query}

Answer clearly and concisely."""
            }
        ]
    )

    print("💬 Claude's Answer:")
    print(message.content[0].text)

if __name__ == "__main__":
    ask_claude("What element types should I use for a structural analysis in ANSYS?")
    ask_claude("How do I troubleshoot convergence issues in ANSYS?")