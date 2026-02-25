"""Prompt templates for simulation troubleshooting."""

CONVERGENCE_PROMPT = """You are diagnosing an ANSYS simulation convergence problem.

Problem description: {problem}
Analysis type: {analysis_type}
Error message: {error_message}
Current settings: {current_settings}

Please provide a structured response with exactly these sections:

**Diagnosis**
[Explain the root cause of the convergence issue in 2–3 sentences]

**Solutions**
- [First recommended fix]
- [Second recommended fix]
- [Third recommended fix]
- [Additional fixes as needed]

**Recommended Settings**
[Specific APDL commands or PyMAPDL calls to apply the fixes, e.g.
NSUBST,20,100,10
AUTOTS,ON
LNSRCH,ON
NEQIT,25]

Common causes to consider:
- Too large initial substep size (increase NSUBST minimum substeps)
- Contact issues (KEYOPT settings, contact stiffness)
- Material nonlinearity requiring stabilization (STABILIZE command)
- Geometric nonlinearity (NLGEOM,ON)
- Poor mesh quality causing element distortion
- Insufficient constraint — rigid body motion
- Solver divergence from large load steps
"""

MESH_QUALITY_PROMPT = """You are advising on ANSYS mesh quality issues.

Problem description: {problem}
Analysis type: {analysis_type}
Error message: {error_message}
Current settings: {current_settings}

Please provide a structured response with exactly these sections:

**Diagnosis**
[Identify the mesh quality issue and its effect on results in 2–3 sentences]

**Solutions**
- [First meshing recommendation]
- [Second meshing recommendation]
- [Third meshing recommendation]
- [Additional recommendations as needed]

**Recommended Settings**
[Specific APDL MESH commands or PyMAPDL meshing calls, e.g.
ESIZE,0.01
MSHAPE,1,3D
MSHKEY,0
SMRTSIZE,4]

Common issues to consider:
- High aspect ratio elements (use uniform mesh sizing)
- Skewed / distorted elements near curved geometry (increase divisions)
- Insufficient through-thickness layers for thin shells
- Element size too large near stress concentrations (use SMRTSIZE or local sizing)
- Incompatible mesh across contact pairs
- Mixed element types causing incompatible DOFs
"""
