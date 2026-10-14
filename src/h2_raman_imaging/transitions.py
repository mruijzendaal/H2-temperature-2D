"""The Raman transitions of H2, calculated with ramlab.

ramlab (https://github.com/Brightsite-Plasmalab/ramlab) computes the transitions between the
rovibrational states of H2 and their line strengths from ab initio matrix elements of the
polarizability (Raj et al. 2018, via `h2_rovib_me`) and the molecular constants of H2. The
version used is the tag in `pyproject.toml`.
"""

from functools import cache

import numpy as np
import pandas as pd

from h2_raman_imaging import DIR_OUTPUT

LASER_WAVELENGTH_NM = 532.0
# The calculation takes about 30 s; the result is kept here. Delete the file to recalculate.
CACHE = DIR_OUTPUT / "cache" / "transitions_H2_532nm.csv"


@cache
def get_transitions() -> pd.DataFrame:
    """The 735 Raman transitions of H2 for 532 nm excitation (pure rotational, and
    vibrational-rotational with v <= 6), sorted by decreasing Raman shift.

    Columns:
        raman_shift_cm-1   Raman shift (positive for Stokes)
        v_initial, J_initial, v_final, J_final
        degeneracy         degeneracy of the initial state (including nuclear spin)
        E_vib_cm-1         vibrational energy of the initial state
        E_rot_cm-1         rotational energy of the initial state
        line_strength      temperature-independent factor of the line intensity (the Raman
                           cross-section of the transition, polarizations combined)

    The intensity of a line at vibrational and rotational temperature Tv and Tr is
    `line_strength * degeneracy * exp(-hc E_vib / k Tv) * exp(-hc E_rot / k Tr)`, up to a factor
    that depends on the temperatures only.
    """
    if CACHE.exists():
        return pd.read_csv(CACHE)

    from ramlab.molecules import H2
    from ramlab.molecules.calculated_linelist_molecule import CalculatedLinelistMolecule

    M = CalculatedLinelistMolecule(H2)
    tr = M.get_all_transitions(laser_wavelength=LASER_WAVELENGTH_NM * 1e-9, force_recalculate=True)
    tr = tr.sortby("vacuum_wavenumber", ascending=False)
    si, sf = tr.state_initial, tr.state_final
    df = pd.DataFrame({
        "raman_shift_cm-1": np.asarray(tr.vacuum_wavenumber, float),
        "v_initial": np.asarray(si.v, int),
        "J_initial": np.asarray(si.J, int),
        "v_final": np.asarray(sf.v, int),
        "J_final": np.asarray(sf.J, int),
        "degeneracy": np.asarray(si.degeneracy, float),
        "E_vib_cm-1": np.asarray(M.M.E_vib(si.v), float),
        "E_rot_cm-1": np.asarray(M.M.E_rot(si.v, si.J), float),
        "line_strength": np.asarray(
            M.M.get_intensity_constant(tr, LASER_WAVELENGTH_NM * 1e-9, "= + T"), float
        ),
    })
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CACHE, index=False, float_format="%.12g")
    return df
