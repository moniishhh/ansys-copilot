"""APDL and PyMAPDL code generation service."""

from backend.prompts.apdl_gen import APDL_GENERATION_PROMPT
from backend.prompts.pyansys_gen import PYMAPDL_GENERATION_PROMPT
from backend.prompts.system_prompts import ANSYS_EXPERT_PROMPT
from backend.services.llm_service import LLMService


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
        raw = self._llm.generate(prompt, system_prompt=ANSYS_EXPERT_PROMPT)
        code, explanation = self._split_code_explanation(raw)
        return {"code": code, "language": "apdl", "explanation": explanation}

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
        raw = self._llm.generate(prompt, system_prompt=ANSYS_EXPERT_PROMPT)
        code, explanation = self._split_code_explanation(raw)
        return {"code": code, "language": "python", "explanation": explanation}

    @staticmethod
    def _split_code_explanation(raw: str) -> tuple[str, str]:
        """Split the LLM output into a code block and an explanation.

        The model is prompted to return a fenced code block followed by a
        plain-English explanation.  This helper extracts both parts.

        Args:
            raw: Raw LLM response text.

        Returns:
            Tuple of (code_string, explanation_string).
        """
        if "```" not in raw:
            return raw.strip(), ""

        parts = raw.split("```")
        # parts[1] contains the fenced block (possibly with language label)
        code_block = parts[1]
        # Strip optional language label on the first line
        code_lines = code_block.splitlines()
        if code_lines and not code_lines[0].strip().startswith("!") and len(code_lines[0].strip()) < 20:
            code_lines = code_lines[1:]
        code = "\n".join(code_lines).strip()

        # Everything after the closing fence is the explanation
        explanation = "".join(parts[2:]).strip()
        return code, explanation
