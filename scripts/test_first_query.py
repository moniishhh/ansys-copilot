"""Test the full RAG pipeline: retrieve relevant docs and generate answers.

Loads the ChromaDB vector store, builds a RetrievalQA chain backed by an
ANSYS expert system prompt, and runs 3 representative test queries.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chains import RetrievalQA

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    from langchain.prompts import PromptTemplate

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

SYSTEM_PROMPT_TEMPLATE = """You are ANSYS Copilot, an expert ANSYS simulation \
engineer and APDL programmer with deep knowledge of finite element analysis, \
computational fluid dynamics, and multiphysics simulations. You provide \
accurate, practical answers and well-commented APDL or Python code.

Use the following retrieved context to answer the question. If the context \
does not fully cover the question, supplement with your own expert knowledge \
but clearly indicate when you are doing so.

Context:
{context}

Question: {question}

Answer (be detailed and include code examples where relevant):"""

TEST_QUERIES = [
    (
        "Generate APDL code for a static structural analysis of a steel "
        "cantilever beam (100mm x 10mm x 10mm) with a 500N tip load"
    ),
    (
        "My nonlinear contact analysis won't converge. I'm using SOLID185 "
        "elements with large deformation. What should I check?"
    ),
    (
        "Write PyMAPDL code to run a modal analysis of an aluminum plate "
        "and extract the first 5 natural frequencies"
    ),
]


def load_vectorstore() -> Chroma:
    """Load the persisted ChromaDB vector store.

    Returns:
        Chroma vector store instance.
    """
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )
    return Chroma(
        collection_name="ansys_knowledge",
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )


def build_qa_chain(vectorstore: Chroma) -> RetrievalQA:
    """Build a RetrievalQA chain with the ANSYS expert prompt.

    Args:
        vectorstore: Populated Chroma vector store.

    Returns:
        Configured RetrievalQA chain.
    """
    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        openai_api_key=OPENAI_API_KEY,
    )

    prompt = PromptTemplate(
        template=SYSTEM_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return chain


def run_queries(chain: RetrievalQA) -> None:
    """Run test queries and print full responses with sources.

    Args:
        chain: Configured RetrievalQA chain.
    """
    for i, query in enumerate(TEST_QUERIES, start=1):
        print(f"\n{'=' * 70}")
        print(f"Query {i}: {query}")
        print("=" * 70)

        result = chain({"query": query})

        print("\nAnswer:")
        print(result["result"])

        print("\nSource documents used:")
        for doc in result.get("source_documents", []):
            source = doc.metadata.get("source", "unknown")
            title = doc.metadata.get("title", "")
            chunk = doc.metadata.get("chunk_index", 0)
            print(f"  - {source} | {title} | chunk {chunk}")


def main() -> None:
    """Load the vector store, build the QA chain, and run test queries."""
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY is not set. Please set it in .env or environment.")
        return

    persist_path = Path(CHROMA_PERSIST_DIR)
    if not persist_path.exists():
        print(f"ChromaDB directory not found: {CHROMA_PERSIST_DIR}")
        print("Run scripts/build_starter_vectordb.py first.")
        return

    print(f"Loading vector store from '{CHROMA_PERSIST_DIR}'...")
    vectorstore = load_vectorstore()
    count = vectorstore._collection.count()
    print(f"Loaded collection with {count} documents.")

    if count == 0:
        print("Vector store is empty. Run scripts/build_starter_vectordb.py first.")
        return

    print(f"Building QA chain with model '{MODEL_NAME}'...")
    chain = build_qa_chain(vectorstore)

    run_queries(chain)

    print(f"\n{'=' * 70}")
    print("All queries completed.")


if __name__ == "__main__":
    main()
