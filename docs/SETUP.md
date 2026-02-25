# Setup & Installation Guide

## Prerequisites

- **Python 3.10+** (3.11 recommended)
- **pip** or **pipx**
- **Docker & Docker Compose** (optional, for containerised setup)
- An **OpenAI API key** with access to `gpt-4o` and `text-embedding-3-small`

## Step-by-Step Installation

### 1. Clone the repository

```bash
git clone https://github.com/moniishhh/ansys-copilot.git
cd ansys-copilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```
OPENAI_API_KEY=sk-...your-key...
```

All other values have sensible defaults (see `.env.example`).

### 5. (Optional) Build the knowledge base

Add your ANSYS documentation files (`.txt`, `.md`, `.pdf`) to
`backend/knowledge_base/data/`, then run:

```bash
python scripts/process_data.py
python scripts/build_vectordb.py
```

If no documents are added the assistant still works — it answers from the
LLM's parametric knowledge without retrieval context.

## Running the Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Interactive API docs are available at `http://localhost:8000/docs`.

## Running the Frontend

In a second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Open `http://localhost:8501` in your browser.

## Running with Docker

```bash
cp .env.example .env   # add your API key to .env
docker-compose up --build
```

| Service  | URL                    |
|----------|------------------------|
| Backend  | http://localhost:8000  |
| Frontend | http://localhost:8501  |

## Running Tests

```bash
pytest backend/tests/ -v
```

## Troubleshooting Setup

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: backend` | Run commands from the project root, or install the package in editable mode: `pip install -e .` |
| `AuthenticationError` | Check that `OPENAI_API_KEY` is set correctly in `.env` |
| ChromaDB errors on startup | Delete the `chroma_db/` directory and restart — it will be recreated |
| `streamlit: command not found` | Activate your virtual environment |
