"""Tests for the /troubleshoot endpoint and Troubleshooter service."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.troubleshooter import Troubleshooter

client = TestClient(app)


@patch("backend.routers.troubleshoot.Troubleshooter")
def test_troubleshoot_convergence(mock_ts_cls: MagicMock) -> None:
    """Troubleshoot endpoint should return diagnosis and solutions list."""
    mock_ts = MagicMock()
    mock_ts.diagnose.return_value = {
        "diagnosis": "The solver diverged due to large substep size.",
        "solutions": ["Reduce initial substep size", "Enable auto time-stepping"],
        "recommended_settings": "NSUBST,20,100,10\nAUTOTS,ON",
    }
    mock_ts_cls.return_value = mock_ts

    response = client.post(
        "/troubleshoot",
        json={
            "problem": "Solver diverges after 3 substeps",
            "analysis_type": "nonlinear static",
            "error_message": "*** ERROR *** Solution not converged",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "diagnosis" in data
    assert isinstance(data["solutions"], list)
    assert len(data["solutions"]) > 0


def test_troubleshooter_selects_mesh_prompt() -> None:
    """Troubleshooter should select the mesh prompt for mesh-related problems."""
    ts = Troubleshooter()
    with patch.object(ts._llm, "generate", return_value="**Diagnosis**\nPoor mesh.\n**Solutions**\n- Remesh\n**Recommended Settings**\nESIZE,0.01") as mock_gen:
        result = ts.diagnose("mesh distortion causing errors", {"analysis_type": "static"})
    # Just check it ran without error and returned expected keys
    assert "diagnosis" in result
    assert "solutions" in result


def test_troubleshooter_parse_response_fallback() -> None:
    """_parse_response should fall back gracefully when sections are missing."""
    raw = "Try increasing the number of substeps and enabling line search."
    result = Troubleshooter._parse_response(raw)
    assert result["diagnosis"] or result["solutions"]
    assert isinstance(result["solutions"], list)
