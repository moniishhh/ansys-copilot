"""Prompt templates for PyMAPDL (PyANSYS) code generation."""

PYMAPDL_GENERATION_PROMPT = """Generate a complete, working PyMAPDL Python script for the following:

Description: {description}
Analysis Type: {analysis_type}

Requirements:
1. Import ansys.mapdl.core.launch_mapdl
2. Launch MAPDL with launch_mapdl()
3. Perform preprocessing: element types, materials, geometry, mesh
4. Apply boundary conditions and loads
5. Solve the analysis
6. Post-process and display/save results
7. Call mapdl.exit() at the end
8. Add docstrings and inline comments
9. Use type hints for all function arguments and return values

Use this structure:
```python
\"\"\"Module docstring describing the analysis.\"\"\"

from ansys.mapdl.core import launch_mapdl


def main() -> None:
    \"\"\"Run the simulation.\"\"\"
    mapdl = launch_mapdl(loglevel="WARNING")

    # --- Preprocessing ---
    mapdl.clear()
    mapdl.prep7()
    # element types, materials, geometry, mesh ...

    # --- Boundary conditions & loads ---
    mapdl.solution()
    # constraints, forces, solve ...

    # --- Post-processing ---
    mapdl.post1()
    # read results, plot, print ...

    mapdl.exit()


if __name__ == "__main__":
    main()
```

After the code block, provide a brief plain-English explanation of what the script does.
"""
