# Data

The input data of the calibration curves. All files are plain CSV (comma-separated, header row,
`.` as decimal separator). The Raman transitions of H<sub>2</sub> are not in `data/`: they are
calculated by ramlab (`../src/h2_raman_imaging/transitions.py`).

## `camera_quantum_efficiency.csv`

Quantum efficiency of the ICCD camera (Andor DH334T-18F-63), normalized.

| Column | Unit | Meaning |
|--------|------|---------|
| `wavelength_nm` | nm | Wavelength |
| `QE_normalized` | – | Quantum efficiency, relative |

## `filters/`

Measured transmission of the interference filters (Section 2.6 of the paper), one file per
filter: `bp550`, `bp560`, `bp580`, `bp589` (10 nm bandpass filters for the rotational lines),
`bp425`, `bp675` (50 nm bandpass filters for the vibrational Stokes and anti-Stokes bands) and
`NOTCH` (the notch filter that rejects the laser light).

Each file has the columns `wavelength_nm` and, for every measured angle of incidence, the
transmission for p-polarized (`p_<angle>deg`) and s-polarized (`s_<angle>deg`) light. The angles
are the filter's rotation angles relative to normal incidence (negative; −0.4° is the closest to
normal incidence). Spectra at angles beyond −12° are not included.

The transmission is relative (1 = full transmission); outside the measured wavelength range
it is not known and is taken as 0.

`filter_parameters.csv` has the centre wavelength `lambda0_nm` and effective refractive index
`n_eff` of the filters that were fitted to the centre wavelength as a function of angle:
λ(θ) = λ<sub>0</sub> (1 − sin²θ / n<sub>eff</sub>²)<sup>1/2</sup>. `fit_rms_nm` is the rms deviation of the fit.

## Origin

`filters/<name>.csv` are the measured, wavelength-corrected transmission spectra of the filters
(`<filter>_WLCORR_.pkl` of the original analysis), on the negative side of the filter rotation up
to −12°, which is the side that the original analysis uses. `n_eff` was fitted per bandpass
filter to the centre wavelength (the middle of the region above half of the maximum
transmission) as a function of angle, over |θ| < 25°. The raw characterisation data are
available from the author on request.

The camera quantum efficiency was digitized from the plot of the quantum efficiency of the
"18F-63" intensifier of the camera (Andor DH334T-18F-63) in the specification sheet of the
manufacturer (Andor, iStar spectroscopy specifications).
