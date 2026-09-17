"""Convergence and mesh troubleshooting service."""

from pydantic import BaseModel, Field
from backend.prompts.system_prompts import ANSYS_EXPERT_PROMPT
from backend.prompts.troubleshoot_prompts import CONVERGENCE_PROMPT, MESH_QUALITY_PROMPT
from backend.services.llm_service import LLMService

class TroubleshootResult(BaseModel):
    diagnosis: str = Field(description="Explanation of the root cause of the convergence/mesh issue in 2-3 sentences.")
    solutions: list[str] = Field(description="A list of recommended fixes.")
    recommended_settings: str = Field(description="Specific APDL commands or PyMAPDL calls to apply the fixes.")

class Troubleshooter:
    """Diagnoses ANSYS simulation problems and recommends fixes."""

    def __init__(self) -> None:
        self._llm = LLMService()

    def diagnose(self, problem: str, context: dict) -> dict:
        """Diagnose a simulation problem.

        Args:
            problem: Plain-English description of the issue.
            context: Dictionary with optional keys ``analysis_type``,
                     ``error_message``, and ``current_settings``.

        Returns:
            Dictionary with keys ``diagnosis``, ``solutions``, and
            ``recommended_settings``.
        """
        # Choose prompt template based on keywords in the problem description
        problem_lower = problem.lower()
        if any(kw in problem_lower for kw in ("mesh", "element", "distortion", "skewness", "quality")):
            prompt_template = MESH_QUALITY_PROMPT
        else:
            prompt_template = CONVERGENCE_PROMPT

        prompt = prompt_template.format(
            problem=problem,
            analysis_type=context.get("analysis_type", "unknown"),
            error_message=context.get("error_message", "none"),
            current_settings=context.get("current_settings", "none"),
        )

        result: TroubleshootResult = self._llm.generate_structured(prompt, TroubleshootResult, system_prompt=ANSYS_EXPERT_PROMPT)
        return {
            "diagnosis": result.diagnosis,
            "solutions": result.solutions,
            "recommended_settings": result.recommended_settings,
        }
