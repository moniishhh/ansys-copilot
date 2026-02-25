"""PyMAPDL steady-state thermal analysis — copper block with temperature BCs."""

import matplotlib.pyplot as plt
import numpy as np
from ansys.mapdl.core import launch_mapdl


def run_thermal_analysis(
    block_length: float = 0.1,
    block_width: float = 0.05,
    block_height: float = 0.05,
    t_hot: float = 100.0,
    t_cold: float = 20.0,
) -> dict:
    """Run a steady-state thermal analysis on a copper block.

    Args:
        block_length: Block dimension in X direction (m).
        block_width: Block dimension in Z direction (m).
        block_height: Block dimension in Y direction (m).
        t_hot: Temperature applied to the hot face x=0 (°C).
        t_cold: Temperature applied to the cold face x=block_length (°C).

    Returns:
        Dictionary with ``max_temp``, ``min_temp``, and ``heat_flux_avg`` values.
    """
    mapdl = launch_mapdl(loglevel="WARNING")
    mapdl.clear()

    # --- Preprocessing ---
    mapdl.prep7()
    mapdl.et(1, "SOLID70")  # 3-D thermal solid
    mapdl.mp("KXX", 1, 385)  # Thermal conductivity — Copper (W/m·K)

    # Geometry
    mapdl.blc4(0, 0, block_length, block_height, block_width)

    # Mesh
    mapdl.esize(block_length / 10)
    mapdl.vmesh("ALL")

    # Hot boundary condition at x = 0
    mapdl.nsel("S", "LOC", "X", 0)
    mapdl.d("ALL", "TEMP", t_hot)

    # Cold boundary condition at x = block_length
    mapdl.nsel("S", "LOC", "X", block_length)
    mapdl.d("ALL", "TEMP", t_cold)

    mapdl.allsel()

    # --- Solution ---
    mapdl.solution()
    mapdl.antype("STEADY")
    mapdl.solve()
    mapdl.finish()

    # --- Post-processing ---
    mapdl.post1()
    mapdl.set("LAST")

    temps = mapdl.post_processing.nodal_temperature()
    heat_flux = mapdl.post_processing.nodal_thermal_strain()  # TF magnitude proxy

    max_temp = float(np.max(temps))
    min_temp = float(np.min(temps))

    # Plot temperature distribution
    mapdl.post_processing.plot_nodal_temperature(
        title="Temperature Distribution (°C)",
        cmap="hot",
        show_edges=True,
    )

    mapdl.exit()
    return {"max_temp": max_temp, "min_temp": min_temp}


if __name__ == "__main__":
    results = run_thermal_analysis()
    print(f"Max temperature: {results['max_temp']:.2f} °C")
    print(f"Min temperature: {results['min_temp']:.2f} °C")
