# %% [markdown]
# # Figure 8: Calibration curves for rotation-vibration non-equilibrium (Tv != Tr)
# The signal of each filter as a function of Tr (8a) or Tv (8b), for Tv - Tr from 0 to 2900 K
# (color). Normal incidence. Data are clipped for Tv and Tr outside [300, 5000] K. The curves
# of 8b start at Tv - Tr = 100 K.
#
# Output: `output/fig8a_nonequilibrium_rot.pdf`, `output/fig8b_nonequilibrium_vib.pdf`

# %%
import matplotlib.pyplot as plt
import numpy as np

from h2_raman_imaging.calibration import ROT_FILTERS, VIB_FILTERS, noneq_family
from h2_raman_imaging.plotting import CMAP, fill_family, new_figure, savefig

T = np.arange(300, 5001, 10.0)
dT = np.arange(0, 3000, 100.0)

# %%
for filters, axis, dT_min, xlabel, labels, name in [
    (ROT_FILTERS, "Tr", 0, "Rotational temperature [K]",
     {"bp550": (870, 0.89), "bp560": (2300, 0.79), "bp580": (1000, 0.38), "bp589": (2700, 0.10)},
     "fig8a_nonequilibrium_rot"),
    (VIB_FILTERS, "Tv", 100, "Vibrational temperature [K]",
     {"bp675": (1500, 0.91), "bp425": (1500, 0.24)},
     "fig8b_nonequilibrium_vib"),
]:
    values = dT[dT >= dT_min]
    family = noneq_family(filters, values, T, axis)  # (filter, dT, T)
    norm = plt.Normalize(values.min(), values.max())
    new_figure()
    for curves in family:
        fill_family(plt.gca(), T, curves, values, norm, zorder=2)
    for text, (x, y) in labels.items():
        plt.text(x, y, text, ha="center", va="center")
    plt.xlim(300, 5000)
    plt.xlabel(xlabel)
    plt.ylabel("Signal per channel [–]")
    ticks = [t for t in range(0, 3000, 500) if t >= dT_min]
    cb = plt.colorbar(plt.cm.ScalarMappable(norm, CMAP), ax=plt.gca(), ticks=ticks)
    cb.set_label("$T_v - T_r$ [K]")
    cb.ax.minorticks_off()
    savefig(name)
    plt.show()
