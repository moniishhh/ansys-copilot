# Architecture

## System Overview

ANSYS Copilot follows a classic three-tier architecture: a **Streamlit** frontend, a **FastAPI** backend, and a **ChromaDB** vector store.

```
┌───────────────────────────────────────────────────────────┐
│                   Streamlit Frontend (port 8501)           │
│   Chat UI · Mode selector · Code viewer · Copy button     │
└──────────────────────────┬────────────────────────────────┘
                           │ HTTP REST (JSON)
┌──────────────────────────▼────────────────────────────────┐
│               FastAPI Backend (port 8000)                  │
│                                                           │
│  Routers                                                  │
│  ┌──────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  /chat   │  │/generate-script│  │  /troubleshoot   │  │
│  └────┬─────┘  └───────┬────────┘  └────────┬─────────┘  │
│       │                │                    │             │
│  Services                                               │
│  ┌────▼──────────┐  ┌──▼──────────────┐  ┌─▼──────────┐  │
│  │  RAGEngine    │  │  CodeGenerator  │  │Troubleshoot│  │
│  │  (LangChain)  │  │ (APDL/PyMAPDL)  │  │   -er      │  │
│  └────┬──────────┘  └──────┬──────────┘  └─────┬──────┘  │
│       │                    │                   │          │
│  ┌────▼────────────────────▼───────────────────▼──────┐   │
│  │                   LLMService                        │   │
│  │              (LangChain + OpenAI)                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Knowledge Base (ChromaDB vector store)           │  │
│  │  ansys_knowledge collection · text-embedding-3-small  │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Streamlit Frontend (`frontend/streamlit_app.py`)
Single-page chat application with four interaction modes. Calls the backend REST API and renders responses with Streamlit's `st.chat_message` and `st.code` widgets.

### FastAPI Backend (`backend/`)
Stateless REST API. Three routers handle different user intents:
- `/chat` — general Q&A via the RAG pipeline
- `/generate-script` — APDL or PyMAPDL code generation
- `/troubleshoot` — convergence and mesh diagnostics

### RAG Engine (`backend/services/rag_engine.py`)
LangChain `RetrievalQA` chain backed by ChromaDB. On each query the five most relevant document chunks are retrieved and injected into the LLM context window.

### LLM Service (`backend/services/llm_service.py`)
Thin wrapper around `langchain_openai.ChatOpenAI`. Accepts a `system_prompt` and a `prompt`, and returns a text response.

### Code Generator (`backend/services/code_generator.py`)
Formats the appropriate prompt template (APDL or PyMAPDL), calls the LLM service, then splits the response into a fenced code block and a plain-English explanation.

### Troubleshooter (`backend/services/troubleshooter.py`)
Selects between the convergence or mesh quality prompt based on keywords in the problem description, calls the LLM, then parses the structured response into `diagnosis`, `solutions`, and `recommended_settings`.

### Knowledge Base (`backend/knowledge_base/`)
- `ingest.py` — loads `.txt`, `.md`, and `.pdf` files and splits them with `RecursiveCharacterTextSplitter`
- `embeddings.py` — generates OpenAI embeddings and persists to ChromaDB

## Data Flow

### Chat Query
```
User → Streamlit → POST /chat
     → RAGEngine.query()
       → ChromaDB similarity search (k=5)
       → LLM with retrieved context
     → response + sources → Streamlit → User
```

### Script Generation
```
User → Streamlit → POST /generate-script
     → CodeGenerator.generate_apdl / generate_pymapdl()
       → Format prompt template
       → LLMService.generate()
       → Split code + explanation
     → ScriptResponse → Streamlit (code block + explanation) → User
```

### Troubleshooting
```
User → Streamlit → POST /troubleshoot
     → Troubleshooter.diagnose()
       → Select prompt (convergence vs mesh)
       → LLMService.generate()
       → Parse structured response
     → TroubleshootResponse → Streamlit → User
```

## Technology Choices

| Choice | Rationale |
|--------|-----------|
| FastAPI | Async, auto-generates OpenAPI docs, excellent Pydantic integration |
| LangChain | Abstracts LLM providers; easy RAG chain construction |
| ChromaDB | Lightweight, file-based vector store — no separate server needed |
| OpenAI GPT-4o | Best-in-class reasoning for technical code generation |
| text-embedding-3-small | High quality, low cost embeddings |
| Streamlit | Zero-boilerplate Python chat UI |
| pydantic-settings | Type-safe environment variable loading |
