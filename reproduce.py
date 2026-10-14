"""Reproduce the calibration curves of the paper.

    uv run reproduce.py

Results are written to `output/`.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FIGURES = [
    "figures/fig02_calibration_curves.py",
    "figures/fig06_angle_dependence.py",
    "figures/fig08_nonequilibrium.py",
]


def run(script):
    print(f"Running {script}...", flush=True)
    t0 = time.time()
    # Render without a display; `plt.show()` in the scripts is then a no-op
    env = os.environ | {"MPLBACKEND": "Agg", "PYTHONWARNINGS": "ignore:FigureCanvasAgg is non-interactive:UserWarning"}
    subprocess.run([sys.executable, ROOT / script], cwd=ROOT, env=env, check=True)
    print(f"  done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    for script in FIGURES:
        run(script)
    print(f"All results are in {ROOT / 'output'}")
