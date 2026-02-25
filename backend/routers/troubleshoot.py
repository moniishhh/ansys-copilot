"""Router for the /troubleshoot endpoint — convergence & mesh diagnostics."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.troubleshooter import Troubleshooter

router = APIRouter()


class TroubleshootRequest(BaseModel):
    """Request payload describing a simulation problem."""

    problem: str
    analysis_type: str = ""
    error_message: str = ""
    current_settings: str = ""


class TroubleshootResponse(BaseModel):
    """Diagnostic response with solutions and recommendations."""

    diagnosis: str
    solutions: list[str]
    recommended_settings: str = ""


@router.post("", response_model=TroubleshootResponse)
async def troubleshoot(request: TroubleshootRequest) -> TroubleshootResponse:
    """Diagnose a simulation problem and suggest fixes.

    Args:
        request: Problem description, analysis type, error message, and current settings.

    Returns:
        Diagnosis, list of recommended solutions, and suggested solver settings.
    """
    try:
        troubleshooter = Troubleshooter()
        context = {
            "analysis_type": request.analysis_type,
            "error_message": request.error_message,
            "current_settings": request.current_settings,
        }
        result = troubleshooter.diagnose(request.problem, context)
        return TroubleshootResponse(
            diagnosis=result["diagnosis"],
            solutions=result["solutions"],
            recommended_settings=result.get("recommended_settings", ""),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
