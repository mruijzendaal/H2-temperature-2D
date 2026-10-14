"""Shared plotting helpers, using the `wedme-plots` paper style."""

import matplotlib.pyplot as plt
import numpy as np
import wedme

from h2_raman_imaging import DIR_OUTPUT

# The figures of the paper are one column wide (a single column is 4.77 in wide in this style)
SIZE_COLUMN = (wedme.PAPER_SCW, wedme.PAPER_DH)
CMAP = plt.get_cmap("nipy_spectral")


def new_figure(figsize=SIZE_COLUMN, **kwargs):
    """A new figure in the paper style."""
    return wedme.figure.paper(figsize=figsize, **kwargs)


def savefig(name: str, **kwargs):
    """Save the current figure as `output/<name>.pdf` and `.png`."""
    wedme.savefig(DIR_OUTPUT / name, **kwargs)


def fill_family(ax, x, curves, values, norm, line_first=True, **kwargs):
    """Draw a family of curves as the areas between neighbouring curves.

    `curves` has shape (n, len(x)) (NaN where undefined) and `values` (n) is the parameter that
    the colors encode (here: angle of incidence or Tv - Tr). Each strip gets the color of the
    mean parameter value of its two curves. The first curve is also drawn as a line, so that
    the family has a minimal width.
    """
    for i in range(len(values) - 1):
        ok = np.isfinite(curves[i]) & np.isfinite(curves[i + 1])
        ax.fill_between(x, curves[i], curves[i + 1], where=ok,
                        color=CMAP(norm(0.5 * (values[i] + values[i + 1]))), lw=0.3, **kwargs)
    if line_first:
        ax.plot(x, curves[0], color=CMAP(norm(values[0])), lw=0.6, **kwargs)
