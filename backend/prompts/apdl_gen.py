"""Prompt templates for APDL code generation."""

APDL_GENERATION_PROMPT = """Generate a complete, working ANSYS APDL script for the following:

Description: {description}
Analysis Type: {analysis_type}

Requirements:
1. Include all three main sections: /PREP7 (preprocessing), /SOLU (solution), /POST1 (post-processing)
2. Define element types with ET command (choose appropriate element for the analysis)
3. Define material properties with MP commands
4. Create or import geometry
5. Mesh the geometry with appropriate element size
6. Apply boundary conditions (D command for DOF constraints)
7. Apply loads (F, SF, BF commands as appropriate)
8. Set solver options and solve
9. Post-process and display results
10. Use FINISH between sections

Use this structure:
```
/TITLE, [Descriptive title]
/PREP7
! Element type definition
ET,1,[ELEMENT_TYPE]
! Material properties
MP,EX,1,[YOUNGS_MODULUS]
MP,PRXY,1,[POISSONS_RATIO]
! ... (geometry, mesh, BCs, loads)
FINISH

/SOLU
! Solution settings
ANTYPE,[ANALYSIS_TYPE]
! ... (BCs, loads, solve)
SOLVE
FINISH

/POST1
! Results post-processing
! ... (plot results, print values)
FINISH
```

After the code block, provide a brief plain-English explanation of what the script does.
"""
