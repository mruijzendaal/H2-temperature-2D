"""Load the input data in `data/` (see data/README.md for the columns)."""

from functools import cache

import numpy as np
import pandas as pd

from h2_raman_imaging import DIR_DATA


@cache
def load_quantum_efficiency() -> pd.DataFrame:
    """Quantum efficiency of the ICCD camera."""
    return pd.read_csv(DIR_DATA / "camera_quantum_efficiency.csv")


@cache
def load_filter_parameters() -> pd.DataFrame:
    """Centre wavelength and effective refractive index of each bandpass filter."""
    return pd.read_csv(DIR_DATA / "filters" / "filter_parameters.csv").set_index("filter")


@cache
def load_filter(name: str) -> dict:
    """Measured transmission spectra of one filter.

    Returns a dict with `wavelength_nm`, `angle_deg` (ascending |angle|; the measurements are at
    negative angles) and the transmissions `p` and `s`, arrays of shape (n_angles, n_wavelengths).
    """
    df = pd.read_csv(DIR_DATA / "filters" / f"{name}.csv")
    angles = [float(c[2:-3]) for c in df.columns if c.startswith("p_")]
    return {
        "wavelength_nm": df["wavelength_nm"].to_numpy(),
        "angle_deg": np.array(angles),
        "p": np.array([df[f"p_{a:.2f}deg"].to_numpy() for a in angles]),
        "s": np.array([df[f"s_{a:.2f}deg"].to_numpy() for a in angles]),
    }
