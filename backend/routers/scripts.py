"""Router for the /generate-script endpoint — APDL & PyMAPDL code generation."""

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.code_generator import CodeGenerator

router = APIRouter()


class ScriptRequest(BaseModel):
    """Request payload for script generation."""

    description: str
    script_type: Literal["apdl", "pymapdl"] = "apdl"
    analysis_type: str = ""


class ScriptResponse(BaseModel):
    """Response payload containing generated code."""

    code: str
    language: str
    explanation: str


@router.post("", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest) -> ScriptResponse:
    """Generate an APDL or PyMAPDL script from a natural language description.

    Args:
        request: Description of the desired simulation script.

    Returns:
        Generated code, language label, and a plain-English explanation.
    """
    try:
        generator = CodeGenerator()
        if request.script_type == "apdl":
            result = generator.generate_apdl(request.description, request.analysis_type)
        else:
            result = generator.generate_pymapdl(request.description, request.analysis_type)
        return ScriptResponse(
            code=result["code"],
            language=result["language"],
            explanation=result["explanation"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
