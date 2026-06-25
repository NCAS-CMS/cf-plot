"""Stateful colorbar rendering helpers for contour workflows."""

from __future__ import annotations

import matplotlib
import numpy as np

from .colour import get_colour_scale_map
from .state import plotvars


def cbar(
    labels=None,
    orientation=None,
    position=None,
    shrink=None,
    fraction=None,
    title=None,
    fontsize=None,
    fontweight=None,
    text_up_down=None,
    text_down_up=None,
    drawedges=None,
    levs=None,
    thick=None,
    anchor=None,
    extend=None,
    mid=None,
    verbose=None,
):
    """The cf-plot interface to Matplotlib colorbar for contour rendering."""
    if verbose:
        print("con - adding a colour bar")

    if fontsize is None:
        fontsize = plotvars.colorbar_fontsize
    if fontweight is None:
        fontweight = plotvars.colorbar_fontweight
    if thick is None:
        thick = 0.012
        if plotvars.rows == 2:
            thick = 0.008
        if plotvars.rows == 3:
            thick = 0.005
        if plotvars.rows >= 4:
            thick = 0.003
    if drawedges is None:
        drawedges = True
    if orientation is None:
        orientation = "horizontal"
    if fraction is None:
        fraction = 0.12
        if plotvars.rows == 2:
            fraction = 0.08
        if plotvars.rows == 3:
            fraction = 0.06
        if plotvars.rows >= 4:
            fraction = 0.04
    if shrink is None:
        shrink = 1.0
        if plotvars.plot_type == 1 and plotvars.proj in ("npstere", "spstere"):
            shrink = 0.8
    if anchor is None:
        anchor = 0.3
        if plotvars.plot_type > 1:
            anchor = 0.5

    if isinstance(levs, int):
        if plotvars.plot_type == 0:
            myplot = plotvars.mymap
        else:
            myplot = plotvars.plot

        from mpl_toolkits.axes_grid1 import make_axes_locatable

        divider = make_axes_locatable(myplot)
        if orientation == "horizontal":
            if plotvars.plot_type == 1:
                cax = divider.append_axes("bottom", size="2%", pad=0.3, title=title)
            else:
                cax = divider.append_axes("bottom", size="2%", pad=1.0, title=title)
        else:
            cax = divider.append_axes("right", size="2%", pad=0.5, title=title)

        return plotvars.master_plot.colorbar(
            plotvars.image, cax=cax, orientation=orientation
        )

    ax1 = None
    if position is None:
        if plotvars.plot_type == 1 or plotvars.plot_type == 6:
            this_plot = plotvars.mymap
        else:
            this_plot = plotvars.plot

        if plotvars.plot_type == 6 and (
            plotvars.proj == "rotated" or plotvars.proj == "UKCP"
        ):
            this_plot = plotvars.plot

        left, bottom, width, height = this_plot.get_position().bounds

        # Cartopy can occasionally report inverted bounds for some map
        # projections. Normalise to positive sizes so add_axes is valid.
        width = abs(width)
        height = abs(height)
        width = max(width, 1e-6)
        height = max(height, 1e-6)

        if orientation == "horizontal":
            if plotvars.plot_type == 1:
                left, bottom, width, height = this_plot.get_position().bounds
                width = abs(width)
                height = abs(height)
                width = max(width, 1e-6)
                height = max(height, 1e-6)
                if height / width >= 0.9:
                    this_plot.set_position([left, bottom + fraction, width, height - fraction])
                    left, bottom, width, height = this_plot.get_position().bounds
                    width = abs(width)
                    height = abs(height)
                    width = max(width, 1e-6)
                    height = max(height, 1e-6)

                ax1 = plotvars.master_plot.add_axes(
                    [
                        left + width * (1.0 - shrink) / 2.0,
                        bottom + fraction * (anchor - 1.0),
                        max(width * shrink, 1e-6),
                        thick,
                    ]
                )
            else:
                this_plot.set_position([left, bottom + fraction, width, height - fraction])
                ax1 = plotvars.master_plot.add_axes(
                    [
                        left + width * (1.0 - shrink) / 2.0,
                        bottom,
                        max(width * shrink, 1e-6),
                        thick,
                    ]
                )
        else:
            ax1 = plotvars.master_plot.add_axes(
                [
                    left + width + fraction * (anchor - 1),
                    bottom + height * (1.0 - shrink) / 2.0,
                    thick,
                    height * shrink,
                ]
            )
            this_plot.set_position([left, bottom, width - fraction, height])
    else:
        ax1 = plotvars.master_plot.add_axes(position)

    if levs is None:
        if plotvars.levels is not None:
            levs = np.array(plotvars.levels)
        else:
            if labels is None:
                errstr = "\n\ncbar error - No levels or labels supplied \n\n"
                raise TypeError(errstr)
            levs = np.arange(len(labels))

    if labels is None:
        labels = levs

    lbot = levs
    if text_up_down:
        lbot = levs[1:][::2]
        ltop = levs[::2]
    if text_down_up:
        lbot = levs[::2]
        ltop = levs[1:][::2]

    colmap = get_colour_scale_map()
    cmap = matplotlib.colors.ListedColormap(colmap)
    if extend is None:
        extend = plotvars.levels_extend

    ncolors = np.size(levs)
    if extend in ("both", "max"):
        ncolors -= 1

    if mid is not None:
        lbot = [(lbot[i + 1] - lbot[i]) / 2.0 + lbot[i] for i in np.arange(len(labels))]

    if not isinstance(levs, int):
        plotvars.norm = matplotlib.colors.BoundaryNorm(boundaries=levs, ncolors=ncolors)

        boundaries = levs.astype(float)
        if extend in ("both", "min"):
            cmap.set_under(plotvars.cs[0])
            boundaries = np.insert(boundaries, 0, boundaries[0] - 1)
        if extend in ("both", "max"):
            cmap.set_over(plotvars.cs[-1])
            boundaries = np.insert(boundaries, len(boundaries), boundaries[-1] + 1)

        if not isinstance(levs, list):
            lbot = None

        colorbar = matplotlib.colorbar.ColorbarBase(
            ax1,
            cmap=cmap,
            norm=plotvars.norm,
            extend=extend,
            extendfrac="auto",
            boundaries=boundaries,
            ticks=lbot,
            spacing="uniform",
            orientation=orientation,
            drawedges=drawedges,
        )
    else:
        ax1 = plotvars.master_plot.add_axes(position)
        colorbar = matplotlib.colorbar.ColorbarBase(
            ax1,
            cmap=cmap,
            norm=plotvars.norm,
            extend=extend,
            extendfrac="auto",
            boundaries=boundaries,
            ticks=lbot,
            spacing="uniform",
            orientation=orientation,
            drawedges=drawedges,
        )

    colorbar.set_label(title, fontsize=fontsize, fontweight=fontweight)

    if len(labels) > len(levs):
        labels = labels[: len(levs)]

    colorbar.set_ticklabels([str(i) for i in labels])
    if orientation == "horizontal":
        for tick in colorbar.ax.xaxis.get_ticklines():
            tick.set_visible(False)
        for tick_label in colorbar.ax.get_xticklabels():
            tick_label.set_fontsize(fontsize)
            tick_label.set_fontweight(fontweight)
    else:
        for tick in colorbar.ax.yaxis.get_ticklines():
            tick.set_visible(False)
        for tick_label in colorbar.ax.get_yticklabels():
            tick_label.set_fontsize(fontsize)
            tick_label.set_fontweight(fontweight)

    if text_up_down or text_down_up:
        vmin = colorbar.norm.vmin
        vmax = colorbar.norm.vmax

        cbar_extend = colorbar.extend
        if cbar_extend == "min":
            shift_l = 0.05
            scaling = 0.95
        elif cbar_extend == "max":
            shift_l = 0.0
            scaling = 0.95
        elif cbar_extend == "both":
            shift_l = 0.05
            scaling = 0.9
        else:
            shift_l = 0.0
            scaling = 1.0

        colorbar.ax.set_xticklabels(lbot)

        for ii in ltop:
            colorbar.ax.text(
                shift_l + scaling * (ii - vmin) / (vmax - vmin),
                1.5,
                str(ii),
                transform=colorbar.ax.transAxes,
                va="bottom",
                ha="center",
                fontsize=fontsize,
                fontweight=fontweight,
            )

        for tick_label in colorbar.ax.get_xticklabels():
            tick_label.set_fontsize(fontsize)
            tick_label.set_fontweight(fontweight)

    return colorbar
