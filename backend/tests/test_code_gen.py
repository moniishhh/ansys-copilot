"""Tests for the /generate-script endpoint and CodeGenerator service."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.code_generator import CodeGenerator

client = TestClient(app)


@patch("backend.routers.scripts.CodeGenerator")
def test_generate_apdl_script(mock_gen_cls: MagicMock) -> None:
    """Script endpoint should return APDL code and explanation."""
    mock_gen = MagicMock()
    mock_gen.generate_apdl.return_value = {
        "code": "/PREP7\nET,1,185\nFINISH",
        "language": "apdl",
        "explanation": "This script sets up a basic structural analysis.",
    }
    mock_gen_cls.return_value = mock_gen

    response = client.post(
        "/generate-script",
        json={"description": "Cantilever beam with tip load", "script_type": "apdl"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "apdl"
    assert "/PREP7" in data["code"]
    assert data["explanation"]


@patch("backend.routers.scripts.CodeGenerator")
def test_generate_pymapdl_script(mock_gen_cls: MagicMock) -> None:
    """Script endpoint should return PyMAPDL Python code."""
    mock_gen = MagicMock()
    mock_gen.generate_pymapdl.return_value = {
        "code": "from ansys.mapdl.core import launch_mapdl\nmapdl = launch_mapdl()",
        "language": "python",
        "explanation": "Launches MAPDL and runs a modal analysis.",
    }
    mock_gen_cls.return_value = mock_gen

    response = client.post(
        "/generate-script",
        json={"description": "Modal analysis of a plate", "script_type": "pymapdl"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "python"


def test_split_code_explanation_with_fence() -> None:
    """_split_code_explanation should correctly separate code from explanation."""
    raw = "```apdl\n/PREP7\nET,1,185\nFINISH\n```\nThis sets up preprocessing."
    code, explanation = CodeGenerator._split_code_explanation(raw)
    assert "/PREP7" in code
    assert "preprocessing" in explanation


def test_split_code_explanation_no_fence() -> None:
    """_split_code_explanation should return full text as code when no fence found."""
    raw = "/PREP7\nET,1,185\nFINISH"
    code, explanation = CodeGenerator._split_code_explanation(raw)
    assert "/PREP7" in code
    assert explanation == ""
