"""PyMAPDL parametric study — cantilever beam tip displacement vs height."""

import matplotlib.pyplot as plt
import numpy as np
from ansys.mapdl.core import launch_mapdl


def run_parametric_study(
    length: float = 1.0,
    width: float = 0.05,
    heights: list[float] | None = None,
    tip_load: float = -5000.0,
) -> dict:
    """Parametric study varying beam height and recording tip displacement.

    Args:
        length: Beam length in metres.
        width: Beam width in metres.
        heights: List of beam heights to evaluate. Defaults to 4 values
                 from 0.05 m to 0.20 m.
        tip_load: Applied tip force in the Y direction (N).

    Returns:
        Dictionary with lists ``heights``, ``displacements``, and ``stresses``.
    """
    if heights is None:
        heights = list(np.linspace(0.05, 0.20, 4))

    displacements: list[float] = []
    stresses: list[float] = []

    for h in heights:
        mapdl = launch_mapdl(loglevel="WARNING")
        mapdl.clear()

        # --- Preprocessing ---
        mapdl.prep7()
        mapdl.et(1, "SOLID185")
        mapdl.mp("EX", 1, 200e9)
        mapdl.mp("PRXY", 1, 0.3)
        mapdl.blc4(0, 0, length, h, width)
        mapdl.esize(h / 4)
        mapdl.vmesh("ALL")

        mapdl.nsel("S", "LOC", "X", 0)
        mapdl.d("ALL", "ALL", 0)
        mapdl.allsel()

        mapdl.nsel("S", "LOC", "X", length)
        n_tip = max(mapdl.mesh.n_node, 1)
        mapdl.f("ALL", "FY", tip_load / n_tip)
        mapdl.allsel()

        # --- Solution ---
        mapdl.solution()
        mapdl.antype("STATIC")
        mapdl.solve()
        mapdl.finish()

        # --- Post-processing ---
        mapdl.post1()
        mapdl.set("LAST")
        disp = mapdl.post_processing.nodal_displacement("Y").min()
        stress = mapdl.post_processing.nodal_eqv_stress().max()

        displacements.append(float(disp))
        stresses.append(float(stress))
        mapdl.exit()

    # Plot results
    _plot_results(heights, displacements, stresses)

    return {"heights": heights, "displacements": displacements, "stresses": stresses}


def _plot_results(
    heights: list[float],
    displacements: list[float],
    stresses: list[float],
) -> None:
    """Generate a two-panel plot of displacement and stress vs beam height.

    Args:
        heights: Beam heights evaluated (m).
        displacements: Corresponding tip displacements (m).
        stresses: Corresponding maximum von Mises stresses (Pa).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.plot(heights, [abs(d) * 1e3 for d in displacements], "bo-")
    ax1.set_xlabel("Beam Height (m)")
    ax1.set_ylabel("Tip Displacement (mm)")
    ax1.set_title("Tip Displacement vs Height")
    ax1.grid(True)

    ax2.plot(heights, [s / 1e6 for s in stresses], "rs-")
    ax2.set_xlabel("Beam Height (m)")
    ax2.set_ylabel("Max von Mises Stress (MPa)")
    ax2.set_title("Max Stress vs Height")
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig("parametric_study_results.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    results = run_parametric_study()
    print("\nParametric Study Results:")
    print(f"{'Height (m)':<12} {'Displacement (mm)':<20} {'Max Stress (MPa)'}")
    print("-" * 50)
    for h, d, s in zip(results["heights"], results["displacements"], results["stresses"]):
        print(f"{h:<12.3f} {abs(d)*1e3:<20.4f} {s/1e6:.2f}")
