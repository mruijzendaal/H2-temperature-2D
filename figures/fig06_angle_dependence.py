# %% [markdown]
# # Figure 6: Angle-of-incidence dependence of the calibration curves (Tv = Tr)
# The rotational calibration curves for angles of incidence from 0 to 5 degrees, for p- and
# s-polarized light. The color of the areas gives the angle.
#
# The same analysis for the vibrational filters (bp425 and bp675) is not in the paper; it is
# saved as `fig6x_angle_dependence_vib.pdf`. There, the angle matters little (below 1.5%).
#
# The two polarizations differ only slightly (below 1.4% in the normalized signal).
#
# Output: `output/fig6_angle_dependence_rot.pdf`, `output/fig6x_angle_dependence_vib.pdf`

# %%
import matplotlib.pyplot as plt
import numpy as np

from h2_raman_imaging.calibration import ROT_FILTERS, VIB_FILTERS, angle_family
from h2_raman_imaging.plotting import CMAP, SIZE_COLUMN, fill_family, new_figure, savefig

ANGLES = np.arange(0, 5.01, 0.5)  # degrees
T = np.arange(300, 5000, 5.0)
norm = plt.Normalize(0, 5)

# Positions of the filter labels (data coordinates)
LABELS = {
    "rot": {"bp550": (870, 0.89), "bp560": (2300, 0.80), "bp580": (1000, 0.38), "bp589": (2700, 0.10)},
    "vib": {"bp675": (1500, 0.9), "bp425": (1000, 0.3)},
}

# %%
for key, filters, xlabel in [
    ("rot", ROT_FILTERS, "Temperature [K]"),
    ("vib", VIB_FILTERS, "Vibrational temperature [K]"),
]:
    fig = new_figure(figsize=(SIZE_COLUMN[0], 2.5))
    axes = fig.subplots(1, 2, sharey=True)
    for ax, pol in zip(axes, ["p", "s"]):
        family = angle_family(filters, ANGLES, pol, T)  # (filter, angle, T)
        for curves in family:
            fill_family(ax, T, curves, ANGLES, norm, zorder=2)
        ax.set_xlim(T.min(), T.max())
        ax.set_title(f"{pol}-polarized")
        ax.set_xlabel(xlabel)
    for text, (x, y) in LABELS[key].items():
        axes[0].text(x, y, text, ha="center", va="center")
    axes[0].set_ylabel("Signal per channel [–]")
    # one inset colorbar, in the right panel
    cax = axes[1].inset_axes([0.5, 0.3, 0.42, 0.04] if key == "vib" else [0.22, 0.94, 0.75, 0.03])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm, CMAP), cax=cax, orientation="horizontal", ticks=[0, 2, 4])
    cb.set_label("Angle [°]", labelpad=0)
    cax.xaxis.set_label_position("bottom")
    cb.ax.minorticks_off()
    savefig("fig6_angle_dependence_rot" if key == "rot" else "fig6x_angle_dependence_vib")
    plt.show()
