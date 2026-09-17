"""APDL and PyMAPDL code generation service."""

from pydantic import BaseModel, Field
from backend.prompts.apdl_gen import APDL_GENERATION_PROMPT
from backend.prompts.pyansys_gen import PYMAPDL_GENERATION_PROMPT
from backend.prompts.system_prompts import ANSYS_EXPERT_PROMPT
from backend.services.llm_service import LLMService

class CodeGenerationResult(BaseModel):
    code: str = Field(description="The generated ANSYS APDL or PyMAPDL script code.")
    explanation: str = Field(description="A brief plain-English explanation of what the script does.")

class CodeGenerator:
    """Generates APDL and PyMAPDL scripts from natural language descriptions."""

    def __init__(self) -> None:
        self._llm = LLMService()

    def generate_apdl(self, description: str, analysis_type: str = "") -> dict:
        """Generate an ANSYS APDL script.

        Args:
            description: Natural language description of the desired simulation.
            analysis_type: Optional hint (e.g., ``"static structural"``).

        Returns:
            Dictionary with keys ``code``, ``language``, and ``explanation``.
        """
        prompt = APDL_GENERATION_PROMPT.format(
            description=description,
            analysis_type=analysis_type or "general",
        )
        result: CodeGenerationResult = self._llm.generate_structured(prompt, CodeGenerationResult, system_prompt=ANSYS_EXPERT_PROMPT)
        return {"code": result.code, "language": "apdl", "explanation": result.explanation}

    def generate_pymapdl(self, description: str, analysis_type: str = "") -> dict:
        """Generate a PyMAPDL Python script.

        Args:
            description: Natural language description of the desired simulation.
            analysis_type: Optional hint (e.g., ``"modal analysis"``).

        Returns:
            Dictionary with keys ``code``, ``language``, and ``explanation``.
        """
        prompt = PYMAPDL_GENERATION_PROMPT.format(
            description=description,
            analysis_type=analysis_type or "general",
        )
        result: CodeGenerationResult = self._llm.generate_structured(prompt, CodeGenerationResult, system_prompt=ANSYS_EXPERT_PROMPT)
        return {"code": result.code, "language": "python", "explanation": result.explanation}
