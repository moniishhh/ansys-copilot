"""PyMAPDL static structural analysis — cantilever beam with tip load."""

from ansys.mapdl.core import launch_mapdl


def run_static_structural(
    length: float = 1.0,
    width: float = 0.05,
    height: float = 0.1,
    tip_load: float = -10000.0,
) -> dict:
    """Run a static structural analysis of a cantilever beam.

    Args:
        length: Beam length in metres.
        width: Beam width in metres.
        height: Beam height in metres.
        tip_load: Applied tip force in the Y direction (N).

    Returns:
        Dictionary with ``max_displacement`` (m) and ``max_von_mises`` (Pa).
    """
    mapdl = launch_mapdl(loglevel="WARNING")
    mapdl.clear()

    # --- Preprocessing ---
    mapdl.prep7()
    mapdl.et(1, "SOLID185")  # 3-D structural solid
    mapdl.mp("EX", 1, 200e9)   # Young's modulus — Steel (Pa)
    mapdl.mp("PRXY", 1, 0.3)   # Poisson's ratio

    # Create beam geometry (block)
    mapdl.blc4(0, 0, length, height, width)

    # Mesh
    mapdl.esize(height / 4)
    mapdl.vmesh("ALL")

    # Fixed support at x = 0
    mapdl.nsel("S", "LOC", "X", 0)
    mapdl.d("ALL", "ALL", 0)
    mapdl.allsel()

    # Distribute tip load at x = length
    mapdl.nsel("S", "LOC", "X", length)
    n_tip = mapdl.mesh.n_node  # number of selected nodes
    mapdl.f("ALL", "FY", tip_load / max(n_tip, 1))
    mapdl.allsel()

    # --- Solution ---
    mapdl.solution()
    mapdl.antype("STATIC")
    mapdl.solve()
    mapdl.finish()

    # --- Post-processing ---
    mapdl.post1()
    mapdl.set("LAST")

    max_disp = mapdl.post_processing.nodal_displacement("Y").min()  # tip deflects in -Y
    max_stress = mapdl.post_processing.nodal_eqv_stress().max()

    mapdl.exit()
    return {"max_displacement": float(max_disp), "max_von_mises": float(max_stress)}


if __name__ == "__main__":
    results = run_static_structural()
    print(f"Max Y-displacement : {results['max_displacement']:.6f} m")
    print(f"Max von Mises stress: {results['max_von_mises']:.2f} Pa")
