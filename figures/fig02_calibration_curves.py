# %% [markdown]
# # Figure 2: Calibration curves (Tv = Tr, normal incidence)
# The normalized signal of each filter as a function of temperature, for the four filters that
# select rotational Raman lines (2a) and the two filters that select the vibrational Stokes and
# anti-Stokes bands (2b).
#
# Output: `output/fig2a_calibration_curves_rot.pdf`, `output/fig2b_calibration_curves_vib.pdf`

# %%
import matplotlib.pyplot as plt

from h2_raman_imaging.calibration import ROT_FILTERS, VIB_FILTERS, nominal_curves
from h2_raman_imaging.plotting import new_figure, savefig

# %%
for filters, xlabel, name in [
    (ROT_FILTERS, "Rotational temperature [K]", "fig2a_calibration_curves_rot"),
    (VIB_FILTERS, "Vibrational temperature [K]", "fig2b_calibration_curves_vib"),
]:
    T, signal = nominal_curves(filters)
    new_figure()
    for label, y in zip(filters, signal):
        plt.plot(T, y, label=label)
    plt.xlim(T.min(), T.max())
    plt.ylim(0, 1)
    plt.xlabel(xlabel)
    plt.ylabel("Signal per channel [–]")
    plt.legend(loc="lower right", ncols=2)
    savefig(name)
    plt.show()
