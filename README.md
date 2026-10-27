[![python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Code: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](data/LICENSE)

# 2D Raman imaging for vibrational and rotational temperature mapping in H<sub>2</sub>

Data and code to reproduce the calibration curves of:

> D. Del Cont-Bernard, M.D. Ruijzendaal, T.W.H. Righart, G.J. van Rooij and T.D. Butterworth,
> "2D Raman imaging for vibrational and rotational temperature mapping in H2", Journal of
> Quantitative Spectroscopy and Radiative Transfer **328**, 109145 (2024).

The calibration curves relate the relative signals of a set of bandpass-filtered images to the
rotational and vibrational temperature of H<sub>2</sub>. This repository calculates them from the
H<sub>2</sub> Raman transitions and the measured transmission of the filters.

## Quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run

```bash
uv run reproduce.py
```

uv installs Python 3.13 and the exact package versions in `uv.lock` into a local `.venv`, so the
results do not depend on what is already installed on your machine. Figures are written to
`output/`. The first run takes about 1 minute, because the Raman
transitions of H<sub>2</sub> are calculated with [ramlab](https://github.com/Brightsite-Plasmalab/ramlab)
(about 30 s); the result is kept in `output/cache/`, after which a run takes about 15 s.

Without uv, use Python 3.13 and a virtual environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install .
python reproduce.py
```

This installs the pinned direct dependencies from `pyproject.toml`, but not the exact versions of
indirect ones.

To work with the scripts interactively, open them in VS Code: the `# %%` markers make them run
cell by cell, like a notebook. Select the `.venv` interpreter.

## Contents

| Paper | Script | Output (`output/`) |
|-------|--------|--------------------|
| Fig. 2a, 2b: calibration curves, T<sub>v</sub> = T<sub>r</sub> | `figures/fig02_calibration_curves.py` | `fig2a_calibration_curves_rot.pdf`, `fig2b_calibration_curves_vib.pdf` |
| Fig. 6: angle of incidence dependence (p and s) | `figures/fig06_angle_dependence.py` | `fig6_angle_dependence_rot.pdf` |
| (not in the paper: the same for bp425 and bp675) | `figures/fig06_angle_dependence.py` | `fig6x_angle_dependence_vib.pdf` |
| Fig. 8a, 8b: T<sub>v</sub> ≠ T<sub>r</sub> | `figures/fig08_nonequilibrium.py` | `fig8a_nonequilibrium_rot.pdf`, `fig8b_nonequilibrium_vib.pdf` |

Every figure is also saved as `.png`. The other figures of the paper (measurements, schematics,
and the error that results from assuming a wrong angle of incidence) are not reproduced here.

```
data/          Camera quantum efficiency and filter transmission spectra (CSV);
               see data/README.md
figures/       One script per figure
src/h2_raman_imaging/
    transitions.py   The Raman transitions of H2 and their line strengths (calculated with ramlab)
    data.py          Loading the data
    calibration.py   Line intensities, filter transmission and calibration curves
    plotting.py      Shared plotting functions
reproduce.py   Runs everything
```

## Method

For every filter k, the signal is the sum over the Raman transitions of the line intensity,
weighted by the transmission of the filter, the quantum efficiency of the camera and the
wavelength (to convert power to photon flux):

*S*<sub>k</sub>(T<sub>r</sub>, T<sub>v</sub>, θ) = Σ<sub>lines</sub> *I*(T<sub>r</sub>, T<sub>v</sub>) · *T*<sub>k</sub>(λ, θ) · QE(λ) · λ

The transitions and their line strengths are calculated by ramlab from ab initio matrix
elements of the polarizability (`src/h2_raman_imaging/transitions.py`). The line intensities
follow from these line strengths and Boltzmann distributions over the vibrational and
rotational energy of the initial state. At
every temperature, the signals of the filters of a set (four for rotation, two for vibration)
are normalized to their Euclidean norm. See the supplementary materials of the paper.

The transmission at an angle of incidence θ is interpolated from spectra that were measured
every 1.9° (`data/filters/`): the two spectra on either side of θ are shifted to the centre
wavelength at θ, λ(θ) = λ<sub>0</sub> (1 − sin²θ / n<sub>eff</sub>²)<sup>1/2</sup>, and linearly weighted.
`n_eff` was fitted per filter (`data/filters/filter_parameters.csv`).

## Dependencies

The calculation of the transitions uses ramlab at the tag `2d-h2-raman-imaging-v1.0.0`
(see `[tool.uv.sources]` in `pyproject.toml`). numpy is pinned to 2.2.1, because the matrix
element code of ramlab (`h2_rovib_me`) does not work with numpy 2.4 and later. `cantera` is
listed explicitly, because it is imported by a dependency of ramlab (toddler) without being
declared.

## Data

The input data are described in [data/README.md](data/README.md).

## Citation

If you use this data or code, please cite the article. See [CITATION.cff](CITATION.cff), or use
"Cite this repository" on GitHub.

## License

Code: [MIT](LICENSE). Data (`data/`): [CC BY 4.0](data/LICENSE).
