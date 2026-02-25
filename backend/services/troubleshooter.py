"""Convergence and mesh troubleshooting service."""

from backend.prompts.system_prompts import ANSYS_EXPERT_PROMPT
from backend.prompts.troubleshoot_prompts import CONVERGENCE_PROMPT, MESH_QUALITY_PROMPT
from backend.services.llm_service import LLMService


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

        raw = self._llm.generate(prompt, system_prompt=ANSYS_EXPERT_PROMPT)
        return self._parse_response(raw)

    @staticmethod
    def _parse_response(raw: str) -> dict:
        """Parse the structured LLM response into a result dictionary.

        The model is prompted to return sections labelled **Diagnosis**,
        **Solutions**, and **Recommended Settings**.

        Args:
            raw: Raw LLM response text.

        Returns:
            Parsed dictionary with ``diagnosis``, ``solutions``, and
            ``recommended_settings`` keys.
        """
        diagnosis = ""
        solutions: list[str] = []
        recommended_settings = ""

        section = None
        for line in raw.splitlines():
            stripped = line.strip()
            lower = stripped.lower()
            if "diagnosis" in lower and stripped.startswith("**"):
                section = "diagnosis"
                continue
            if "solution" in lower and stripped.startswith("**"):
                section = "solutions"
                continue
            if "recommended" in lower and stripped.startswith("**"):
                section = "settings"
                continue

            if section == "diagnosis" and stripped:
                diagnosis += stripped + " "
            elif section == "solutions" and stripped.startswith(("-", "*", "•")):
                solutions.append(stripped.lstrip("-*• "))
            elif section == "settings" and stripped:
                recommended_settings += stripped + "\n"

        # Fallback: return whole response as diagnosis if parsing found nothing
        if not diagnosis and not solutions:
            diagnosis = raw.strip()

        return {
            "diagnosis": diagnosis.strip(),
            "solutions": solutions or [raw.strip()],
            "recommended_settings": recommended_settings.strip(),
        }
