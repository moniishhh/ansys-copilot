# 🤖 ANSYS Copilot

> AI-powered assistant for ANSYS simulation workflows

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-0.1-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## What It Does

ANSYS Copilot is an AI-powered assistant that helps engineers work faster with ANSYS simulation tools:

- **APDL script generation** from natural language descriptions
- **PyANSYS (PyMAPDL) code generation** for Python-based workflows
- **Convergence troubleshooting** — diagnose and fix solver issues
- **Mesh quality advice** — element size, type, and refinement guidance
- **Element type selection** guidance based on physics and geometry
- **Boundary condition validation** — catch common setup mistakes
- **Analytical solution comparison** — verify FEA results against theory

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Frontend                     │
│            (Chat UI, Mode Selection, Code View)          │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP
┌───────────────────────▼─────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ /chat      │  │/generate-    │  │ /troubleshoot   │  │
│  │ (Q&A)      │  │script (APDL/ │  │ (convergence/   │  │
│  │            │  │ PyMAPDL)     │  │  mesh issues)   │  │
│  └─────┬──────┘  └──────┬───────┘  └────────┬────────┘  │
│        └────────────────┼────────────────────┘           │
│                         │                                │
│  ┌──────────────────────▼────────────────────────────┐   │
│  │              Services Layer                        │   │
│  │  RAG Engine │ LLM Service │ Code Gen │ Troubleshoot│   │
│  └──────────────────────┬────────────────────────────┘   │
│                         │                                │
│  ┌──────────────────────▼────────────────────────────┐   │
│  │           Knowledge Base (ChromaDB)                │   │
│  │     ANSYS Docs │ APDL Reference │ Tutorials        │   │
│  └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | Streamlit                           |
| Backend     | FastAPI + Uvicorn                   |
| AI/LLM      | OpenAI GPT-4o (or compatible)       |
| RAG         | LangChain + ChromaDB                |
| Embeddings  | OpenAI text-embedding-3-small       |
| Config      | pydantic-settings + python-dotenv   |

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/moniishhh/ansys-copilot.git
cd ansys-copilot

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Start the backend
uvicorn backend.main:app --reload --port 8000

# 5. Start the frontend (new terminal)
streamlit run frontend/streamlit_app.py
```

Visit `http://localhost:8501` to open the chat UI, or `http://localhost:8000/docs` for the API docs.

### Docker (optional)

```bash
cp .env.example .env   # add your API key
docker-compose up --build
```

## Project Structure

```
ansys-copilot/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Settings (pydantic-settings)
│   ├── routers/
│   │   ├── chat.py            # /chat endpoint
│   │   ├── scripts.py         # /generate-script endpoint
│   │   └── troubleshoot.py    # /troubleshoot endpoint
│   ├── services/
│   │   ├── rag_engine.py      # LangChain RAG pipeline
│   │   ├── llm_service.py     # LLM abstraction layer
│   │   ├── code_generator.py  # APDL & PyMAPDL generation
│   │   └── troubleshooter.py  # Convergence/mesh diagnostics
│   ├── prompts/
│   │   ├── system_prompts.py
│   │   ├── apdl_gen.py
│   │   ├── pyansys_gen.py
│   │   └── troubleshoot_prompts.py
│   ├── knowledge_base/
│   │   ├── ingest.py
│   │   ├── embeddings.py
│   │   └── data/
│   └── tests/
│       ├── test_chat.py
│       ├── test_code_gen.py
│       └── test_troubleshoot.py
├── frontend/
│   └── streamlit_app.py
├── scripts/
│   ├── scrape_ansys_docs.py
│   ├── process_data.py
│   └── build_vectordb.py
├── examples/
│   ├── apdl_templates/
│   │   ├── static_structural.apdl
│   │   ├── modal_analysis.apdl
│   │   ├── thermal_steady.apdl
│   │   └── parametric_study.apdl
│   └── pymapdl_templates/
│       ├── static_structural.py
│       ├── modal_analysis.py
│       ├── thermal_analysis.py
│       └── parametric_study.py
└── docs/
    ├── ARCHITECTURE.md
    ├── SETUP.md
    └── API.md
```

## Roadmap

### Phase 1 — MVP (current)
- [x] Project structure & configuration
- [x] FastAPI backend with RAG pipeline
- [x] Streamlit chat UI
- [x] APDL & PyMAPDL code generation
- [x] Convergence troubleshooting

### Phase 2 — Knowledge Base
- [ ] Ingest official ANSYS APDL Command Reference
- [ ] Ingest PyANSYS documentation
- [ ] Ingest ANSYS Verification Manual examples
- [ ] Fine-tune retrieval ranking

### Phase 3 — Enhanced Features
- [ ] Multi-turn conversation memory
- [ ] File upload (log files, mesh reports)
- [ ] Result post-processing guidance
- [ ] Integration with ANSYS Mechanical via PyMAPDL

### Phase 4 — Production
- [ ] Authentication & user sessions
- [ ] Usage analytics
- [ ] CI/CD pipeline
- [ ] Cloud deployment (AWS / Azure)

## Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change. Follow PEP 8, add type hints, and include docstrings for all public functions.

## License

MIT © 2026 Monish Saravanan

