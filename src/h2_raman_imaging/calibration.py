"""Calibration curves: the signal of each filter as a function of the temperatures.

The signal of filter k is the sum over all Raman lines of the line intensity, weighted by the
transmission of the filter (at the angle of incidence), the quantum efficiency of the camera
and the photon energy (supplementary materials, Section 2):

    signal_k(Tr, Tv) = sum_lines  I_line(Tr, Tv) * T_k(lambda_line) * QE(lambda_line) * lambda_line

The line intensities follow the Boltzmann distributions of the initial states over vibrational
(Tv) and rotational (Tr) energy. The signals of a set of filters are then normalized to their
Euclidean norm at every temperature, because the absolute amplitude is not used.
"""

import numpy as np
from scipy.constants import c, h, k

from h2_raman_imaging.data import load_filter, load_filter_parameters, load_quantum_efficiency
from h2_raman_imaging.transitions import LASER_WAVELENGTH_NM, get_transitions

ROT_FILTERS = ["bp550", "bp560", "bp580", "bp589"]
VIB_FILTERS = ["bp425", "bp675"]
HC_OVER_K = h * c * 100 / k  # K per cm^-1


def line_wavelengths_nm() -> np.ndarray:
    """Wavelength of every transition (Stokes shifts are positive)."""
    shift = get_transitions()["raman_shift_cm-1"].to_numpy()
    return 1e7 / (1e7 / LASER_WAVELENGTH_NM - shift)


def line_intensities(Tv, Tr) -> np.ndarray:
    """Intensity of every transition, shape (n_lines, *broadcast(Tv, Tr).shape).

    Up to a factor that depends on the temperatures only (the partition sum), which cancels in
    the normalized calibration curves.
    """
    t = get_transitions()
    Tv, Tr = np.broadcast_arrays(np.asarray(Tv, float), np.asarray(Tr, float))
    col = (slice(None),) + (None,) * Tv.ndim
    strength = t["line_strength"].to_numpy()[col] * t["degeneracy"].to_numpy()[col]
    return (
        strength
        * np.exp(-HC_OVER_K * t["E_vib_cm-1"].to_numpy()[col] / Tv)
        * np.exp(-HC_OVER_K * t["E_rot_cm-1"].to_numpy()[col] / Tr)
    )


def filter_transmission(name: str, theta_deg: float, pol: str, wavelength_nm: np.ndarray) -> np.ndarray:
    """Transmission of a filter at angle of incidence `theta_deg`, for polarization `pol` ("p" or "s").

    The filter was measured at angles 1.9 deg apart. As in the original analysis, the two
    measured spectra on either side of `theta_deg` are shifted to the centre wavelength at
    `theta_deg`, lambda(theta) = lambda_0 sqrt(1 - sin^2(theta) / n_eff^2), and linearly
    weighted. The transmission is 0 outside the measured wavelength range.
    """
    f = load_filter(name)
    n_eff = load_filter_parameters().loc[name, "n_eff"]
    mag = np.abs(f["angle_deg"])  # ascending
    j = int(np.searchsorted(mag, theta_deg, side="right")) - 1
    if j < 0 or j >= len(mag) - 1:  # closer to normal incidence than any measurement (or beyond the last)
        idx, w = [max(j, 0)], [1.0]
    else:
        frac = (theta_deg - mag[j]) / (mag[j + 1] - mag[j])
        idx, w = [j, j + 1], [1 - frac, frac]

    def shift(angle):  # lambda(theta) / lambda(angle)
        return np.sqrt(1 - np.sin(np.radians(theta_deg)) ** 2 / n_eff**2) / np.sqrt(
            1 - np.sin(np.radians(angle)) ** 2 / n_eff**2
        )

    out = np.zeros_like(wavelength_nm, dtype=float)
    for i, wi in zip(idx, w):
        out += wi * np.interp(
            wavelength_nm, f["wavelength_nm"] * shift(f["angle_deg"][i]), f[pol][i], left=0.0, right=0.0
        )
    return out


def notch_transmission(wavelength_nm: np.ndarray, theta_deg: float = 0.0, pol: str = "p") -> np.ndarray:
    """The notch filter that rejects the laser light, linearly interpolated between the two
    measured angles on either side of `theta_deg`. It only matters near 532 nm."""
    f = load_filter("NOTCH")
    mag = np.abs(f["angle_deg"])
    j = int(np.clip(np.searchsorted(mag, theta_deg, side="right") - 1, 0, len(mag) - 2))
    frac = float(np.clip((theta_deg - mag[j]) / (mag[j + 1] - mag[j]), 0, 1))
    t = (1 - frac) * f[pol][j] + frac * f[pol][j + 1]
    return np.interp(wavelength_nm, f["wavelength_nm"], t, left=0.0, right=0.0)


def filter_weights(names, theta_deg: float = 0.0, pol: str = "p") -> np.ndarray:
    """Weight of every transition in the signal of each filter, shape (n_filters, n_lines)."""
    lam = line_wavelengths_nm()
    qe = load_quantum_efficiency()
    common = np.interp(lam, qe["wavelength_nm"], qe["QE_normalized"], left=0.0, right=0.0)
    common = common * notch_transmission(lam, theta_deg, pol) * lam  # lam: power -> photon flux
    return np.array([filter_transmission(n, theta_deg, pol, lam) * common for n in names])


def signals(names, Tv, Tr, theta_deg: float = 0.0, pol: str = "p") -> np.ndarray:
    """Signal of each filter, shape (n_filters, *broadcast(Tv, Tr).shape)."""
    return np.tensordot(filter_weights(names, theta_deg, pol), line_intensities(Tv, Tr), axes=(1, 0))


def normalize(s: np.ndarray) -> np.ndarray:
    """Normalize to the Euclidean norm over the filter axis (the first)."""
    return s / np.sqrt((s**2).sum(axis=0))


def nominal_curves(names, T=np.arange(300, 5000, 5.0)) -> tuple[np.ndarray, np.ndarray]:
    """Calibration curves for Tv = Tr = T and normal incidence (Figure 2): (T, normalized signals)."""
    return T, normalize(signals(names, T, T))


def noneq_family(names, dT, T=np.arange(300, 5001, 10.0), axis="Tr") -> np.ndarray:
    """Normalized signals for Tv = Tr + dT (Figure 8), shape (n_filters, len(dT), len(T)).

    `T` is the temperature on the x axis: Tr for `axis="Tr"`, Tv for `axis="Tv"`. NaN where Tr or
    Tv is outside [300, 5000] K, the range of the simulation.
    """
    dT = np.asarray(dT, float)[:, None]
    Tr = T[None, :] if axis == "Tr" else T[None, :] - dT
    Tv = Tr + dT
    invalid = (Tr < 300.0) | (Tv > 5000.0)
    out = normalize(signals(names, np.where(invalid, 300.0, Tv), np.where(invalid, 300.0, Tr)))
    out[:, invalid] = np.nan
    return out


def angle_family(names, angles_deg, pol: str, T=np.arange(300, 5000, 5.0)) -> np.ndarray:
    """Normalized signals for Tv = Tr = T at several angles of incidence (Figure 6),
    shape (n_filters, len(angles), len(T))."""
    return np.stack([normalize(signals(names, T, T, a, pol)) for a in angles_deg], axis=1)
