# API Reference

Base URL: `http://localhost:8000`

Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## GET /health

Health check endpoint.

**Response**

```json
{
  "status": "ok",
  "service": "ansys-copilot-backend"
}
```

---

## POST /chat

Answer an ANSYS-related question using the RAG pipeline.

### Request body

```json
{
  "message": "What element type should I use for a 3-D solid structural analysis?",
  "conversation_history": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ | The user's question |
| `conversation_history` | array | ❌ | Previous message dicts (reserved for future use) |

### Response

```json
{
  "response": "For 3-D solid structural analyses, SOLID185 is the recommended element...",
  "sources": ["apdl_reference.txt"]
}
```

### Example — curl

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I apply a pressure load on a surface in APDL?"}'
```

### Example — Python

```python
import requests
resp = requests.post(
    "http://localhost:8000/chat",
    json={"message": "How do I apply a pressure load on a surface in APDL?"},
)
print(resp.json()["response"])
```

---

## POST /generate-script

Generate an APDL or PyMAPDL simulation script from a natural language description.

### Request body

```json
{
  "description": "Cantilever beam 1 m long made of steel with a 10 kN tip load",
  "script_type": "apdl",
  "analysis_type": "static structural"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `description` | string | ✅ | — | Natural language description of the simulation |
| `script_type` | `"apdl"` \| `"pymapdl"` | ❌ | `"apdl"` | Output script format |
| `analysis_type` | string | ❌ | `""` | Hint for analysis type |

### Response

```json
{
  "code": "/PREP7\nET,1,SOLID185\n...",
  "language": "apdl",
  "explanation": "This script models a cantilever beam using SOLID185 elements..."
}
```

### Example — curl

```bash
curl -X POST http://localhost:8000/generate-script \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Modal analysis of an aluminum plate 500x300x3mm",
    "script_type": "pymapdl",
    "analysis_type": "modal"
  }'
```

---

## POST /troubleshoot

Diagnose a simulation problem and provide recommended fixes.

### Request body

```json
{
  "problem": "My nonlinear static analysis diverges after 3 substeps",
  "analysis_type": "nonlinear static structural",
  "error_message": "*** ERROR *** Convergence not achieved in 26 iterations",
  "current_settings": "NSUBST,5,10,1\nNLGEOM,ON"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `problem` | string | ✅ | Plain-English description of the issue |
| `analysis_type` | string | ❌ | Type of analysis (helps select prompt) |
| `error_message` | string | ❌ | Exact error text from ANSYS output |
| `current_settings` | string | ❌ | Current APDL commands / solver settings |

### Response

```json
{
  "diagnosis": "The solver is diverging because the initial substep size is too large for the nonlinear material response.",
  "solutions": [
    "Increase the minimum number of substeps (NSUBST,20,100,10)",
    "Enable automatic time-stepping (AUTOTS,ON)",
    "Enable line search (LNSRCH,ON)",
    "Check contact stiffness FKN value"
  ],
  "recommended_settings": "NSUBST,20,100,10\nAUTOTS,ON\nLNSRCH,ON\nNEQIT,25"
}
```

### Example — curl

```bash
curl -X POST http://localhost:8000/troubleshoot \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "Highly distorted elements near a fillet radius",
    "analysis_type": "static structural",
    "error_message": "Element shape checking limits exceeded"
  }'
```
