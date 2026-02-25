"""PyMAPDL modal analysis — natural frequencies of an aluminum plate."""

from ansys.mapdl.core import launch_mapdl


def run_modal_analysis(
    length: float = 0.5,
    width: float = 0.3,
    thickness: float = 0.003,
    n_modes: int = 10,
) -> list[float]:
    """Extract the first n natural frequencies of a simply-supported plate.

    Args:
        length: Plate length in metres.
        width: Plate width in metres.
        thickness: Plate thickness in metres.
        n_modes: Number of modes to extract.

    Returns:
        List of natural frequencies in Hz (length == n_modes).
    """
    mapdl = launch_mapdl(loglevel="WARNING")
    mapdl.clear()

    # --- Preprocessing ---
    mapdl.prep7()
    mapdl.et(1, "SHELL181")
    mapdl.keyopt(1, 3, 2)  # Full integration

    # Shell section (thickness)
    mapdl.sectype(1, "SHELL")
    mapdl.secdata(thickness, 1, 0.0, 3)

    # Aluminum material properties
    mapdl.mp("EX", 1, 70e9)
    mapdl.mp("PRXY", 1, 0.33)
    mapdl.mp("DENS", 1, 2700)

    # Create rectangular plate area
    mapdl.blc4(0, 0, length, width)

    # Mesh
    mapdl.esize(length / 20)
    mapdl.mshkey(0)
    mapdl.amesh("ALL")

    # Simply-supported: constrain out-of-plane on all edges
    mapdl.lsel("S", "LINE", "", "ALL")
    mapdl.dl("ALL", "", "UZ", 0)
    mapdl.allsel()

    # --- Solution ---
    mapdl.solution()
    mapdl.antype("MODAL")
    mapdl.modopt("LANB", n_modes)
    mapdl.mxpand(n_modes)
    mapdl.solve()
    mapdl.finish()

    # --- Post-processing: extract frequencies ---
    mapdl.post1()
    frequencies = []
    for mode in range(1, n_modes + 1):
        mapdl.set(1, mode)
        freq = mapdl.get("FREQ", "ACTIVE", 0, "FREQ")
        frequencies.append(float(freq))

    mapdl.exit()
    return frequencies


if __name__ == "__main__":
    freqs = run_modal_analysis()
    print("Natural frequencies (Hz):")
    for i, f in enumerate(freqs, start=1):
        print(f"  Mode {i:2d}: {f:.3f} Hz")
