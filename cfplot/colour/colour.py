import subprocess
from typing import Any

import matplotlib
import matplotlib.pyplot as plot
import numpy as np

from .. import utility
from ..state import plotvars


def get_colour_scale_map() -> list[str]:
    """Return the active colour scale trimmed for extend settings."""
    cscale_ncols = len(plotvars.cs)
    if plotvars.levels_extend == "both":
        return plotvars.cs[1 : cscale_ncols - 1]
    if plotvars.levels_extend == "min":
        return plotvars.cs[1:]
    if plotvars.levels_extend == "max":
        return plotvars.cs[: cscale_ncols - 1]
    return plotvars.cs


def apply_colour_scale(
    scale: str | None = None,
    ncols: int | None = None,
    white: Any = None,
    below: int | None = None,
    above: int | None = None,
    reverse: bool = False,
    uniform: bool = False,
) -> None:
    """Apply a colour scale to shared plotting state."""
    if scale is None or scale == "":
        scale = "scale1"

    red, green, blue = utility.load_colour_scale_rgb(scale)

    if reverse:
        red = red[::-1]
        green = green[::-1]
        blue = blue[::-1]

    if ncols is not None:
        positions = np.linspace(0, np.size(red) - 1, num=ncols, endpoint=True)
        red, green, blue = utility.interpolate_colour_channels(
            red, green, blue, positions
        )

    if below is not None or above is not None:
        npoints = np.size(red) // 2

        x_below: np.ndarray | float | list[float] = []
        lower = npoints if below is None else below
        if below is not None and uniform:
            lower = max(above, below)
        if below == 1:
            x_below = 0
        if lower > 1:
            x_below = ((npoints - 1) / float(lower - 1)) * np.arange(lower)

        x_above: np.ndarray | float | list[float] = []
        upper = npoints if above is None else above
        if above is not None and uniform:
            upper = max(above, below)
        if above == 1:
            x_above = npoints * 2 - 1
        if upper > 1:
            x_above = ((npoints - 1) / float(upper - 1)) * np.arange(upper) + npoints

        positions = np.append(x_below, x_above)
        red, green, blue = utility.interpolate_colour_channels(
            red, green, blue, positions
        )

        if uniform:
            midpoint = max(below, above)
            red = red[midpoint - below : midpoint + above]
            green = green[midpoint - below : midpoint + above]
            blue = blue[midpoint - below : midpoint + above]

    hexarr = [
        f"#{int(red[idx]):02x}{int(green[idx]):02x}{int(blue[idx]):02x}"
        for idx in np.arange(np.size(red))
    ]

    if white is not None:
        if np.size(white) == 1:
            hexarr[white] = "#ffffff"
        else:
            for col in white:
                hexarr[col] = "#ffffff"

    plotvars.cs = hexarr


def cscale(
    scale: str | None = None,
    ncols: int | None = None,
    white: Any = None,
    below: int | None = None,
    above: int | None = None,
    reverse: bool = False,
    uniform: bool = False,
) -> None:
    """Choose and manipulate colour maps in shared plotting state."""
    if scale is None:
        plotvars.cscale_flag = 0
        return

    plotvars.cs_user = scale
    plotvars.cscale_flag = 1

    vals = [ncols, white, below, above]
    if any(val is not None for val in vals):
        plotvars.cscale_flag = 2
    if reverse is not False or uniform is not False:
        plotvars.cscale_flag = 2

    apply_colour_scale(
        scale=scale,
        ncols=ncols,
        white=white,
        below=below,
        above=above,
        reverse=reverse,
        uniform=uniform,
    )


def _cscale_get_map():
    """
    | Return colour map for use in contour plots.
    | This is an internal routine and is not used by the user.
    |
    | This depends on the colour bar extensions.
    |
    :Returns:
         colour map
    |
    """
    return get_colour_scale_map()


def _process_color_scales():
    """
    | Process colour scales to generate images of them for the web
    | documentation and the rst code for inclusion in the
    | colour_scale.rst file.
    |
    |
    | No inputs
    | This is an internal routine and not used by the user
    |
    :Returns:
     None
    """

    # Define scale categories
    uniform = ["viridis", "magma", "inferno", "plasma", "parula", "gray"]

    ncl_large = [
        "amwg256",
        "BkBlAqGrYeOrReViWh200",
        "BlAqGrYeOrRe",
        "BlAqGrYeOrReVi200",
        "BlGrYeOrReVi200",
        "BlRe",
        "BlueRed",
        "BlueRedGray",
        "BlueWhiteOrangeRed",
        "BlueYellowRed",
        "BlWhRe",
        "cmp_b2r",
        "cmp_haxby",
        "detail",
        "extrema",
        "GrayWhiteGray",
        "GreenYellow",
        "helix",
        "helix1",
        "hotres",
        "matlab_hot",
        "matlab_hsv",
        "matlab_jet",
        "matlab_lines",
        "ncl_default",
        "ncview_default",
        "OceanLakeLandSnow",
        "rainbow",
        "rainbow_white_gray",
        "rainbow_white",
        "rainbow_gray",
        "tbr_240_300",
        "tbr_stdev_0_30",
        "tbr_var_0_500",
        "tbrAvg1",
        "tbrStd1",
        "tbrVar1",
        "thelix",
        "ViBlGrWhYeOrRe",
        "wh_bl_gr_ye_re",
        "WhBlGrYeRe",
        "WhBlReWh",
        "WhiteBlue",
        "WhiteBlueGreenYellowRed",
        "WhiteGreen",
        "WhiteYellowOrangeRed",
        "WhViBlGrYeOrRe",
        "WhViBlGrYeOrReWh",
        "wxpEnIR",
        "3gauss",
        "3saw",
        "BrBG",
    ]

    ncl_meteoswiss = [
        "hotcold_18lev",
        "hotcolr_19lev",
        "mch_default",
        "perc2_9lev",
        "percent_11lev",
        "precip2_15lev",
        "precip2_17lev",
        "precip3_16lev",
        "precip4_11lev",
        "precip4_diff_19lev",
        "precip_11lev",
        "precip_diff_12lev",
        "precip_diff_1lev",
        "rh_19lev",
        "spread_15lev",
    ]

    ncl_color_blindness = [
        "StepSeq25",
        "posneg_2",
        "posneg_1",
        "BlueDarkOrange18",
        "BlueDarkRed18",
        "GreenMagenta16",
        "BlueGreen14",
        "BrownBlue12",
        "Cat12",
    ]

    ncl_small = [
        "amwg",
        "amwg_blueyellowred",
        "BlueDarkRed18",
        "BlueDarkOrange18",
        "BlueGreen14",
        "BrownBlue12",
        "Cat12",
        "cmp_flux",
        "cosam12",
        "cosam",
        "GHRSST_anomaly",
        "GreenMagenta16",
        "hotcold_18lev",
        "hotcolr_19lev",
        "mch_default",
        "nrl_sirkes",
        "nrl_sirkes_nowhite",
        "perc2_9lev",
        "percent_11lev",
        "posneg_2",
        "prcp_1",
        "prcp_2",
        "prcp_3",
        "precip_11lev",
        "precip_diff_12lev",
        "precip_diff_1lev",
        "precip2_15lev",
        "precip2_17lev",
        "precip3_16lev",
        "precip4_11lev",
        "precip4_diff_19lev",
        "radar",
        "radar_1",
        "rh_19lev",
        "seaice_1",
        "seaice_2",
        "so4_21",
        "spread_15lev",
        "StepSeq25",
        "sunshine_9lev",
        "sunshine_diff_12lev",
        "temp_19lev",
        "temp_diff_18lev",
        "temp_diff_1lev",
        "topo_15lev",
        "wgne15",
        "wind_17lev",
    ]

    orography = [
        "os250kmetres",
        "wiki_1_0_2",
        "wiki_1_0_3",
        "wiki_2_0",
        "wiki_2_0_reduced",
        "arctic",
    ]

    idl_guide = []
    for i in np.arange(1, 45):
        idl_guide.append("scale" + str(i))

    # TODO SLB improve string formatting below and consolidate
    for category in [
        "uniform",
        "ncl_meteoswiss",
        "ncl_small",
        "ncl_large",
        "ncl_color_blindness",
        "orography",
        "idl_guide",
    ]:
        if category == "uniform":
            scales = uniform
            div = "================== ====="
            chars = 10
            title = (
                "Perceptually uniform colour maps for use with continuous "
                "data"
            )
            print(title)
            print("----------------------------------------------")
            print("")
            print(div)
            print("Name               Scale")
            print(div)

        if category == "ncl_meteoswiss":
            scales = ncl_meteoswiss
            div = "================== ====="
            chars = 19
            print("NCAR Command Language - MeteoSwiss colour maps")
            print("----------------------------------------------")
            print("")
            print(div)
            print("Name               Scale")
            print(div)
        if category == "ncl_small":
            scales = ncl_small
            div = "=================== ====="
            chars = 20
            print("NCAR Command Language - small color maps (<50 colours)")
            print("------------------------------------------------------")
            print("")
            print(div)
            print("Name                Scale")
            print(div)
        if category == "ncl_large":
            scales = ncl_large
            div = "======================= ====="
            chars = 24
            print("NCAR Command Language - large colour maps (>50 colours)")
            print("-------------------------------------------------------")
            print("")
            print(div)
            print("Name                    Scale")
            print(div)
        if category == "ncl_color_blindness":
            scales = ncl_color_blindness
            div = "================ ====="
            chars = 17
            title = (
                "NCAR Command Language - Enhanced to help with colour "
                "blindness"
            )
            print(title)
            title = (
                "-----------------------------------------------------"
                "---------"
            )
            print(title)
            print("")
            print(div)
            print("Name             Scale")
            print(div)
            chars = 17
        if category == "orography":
            scales = orography
            div = "================ ====="
            chars = 17
            print("Orography/bathymetry colour scales")
            print("----------------------------------")
            print("")
            print(div)
            print("Name             Scale")
            print(div)
            chars = 17
        if category == "idl_guide":
            scales = idl_guide
            div = "======= ====="
            chars = 8
            print("IDL guide scales")
            print("----------------")
            print("")
            print(div)
            print("Name    Scale")
            print(div)
            chars = 8

        for scale in scales:
            # Make image of scale
            fig = plot.figure(figsize=(8, 0.5))
            ax1 = fig.add_axes([0.05, 0.1, 0.9, 0.2])
            cscale(scale)
            cmap = matplotlib.colors.ListedColormap(plotvars.cs)
            cb1 = matplotlib.colorbar.ColorbarBase(
                ax1, cmap=cmap, orientation="horizontal", ticks=None
            )
            cb1.set_ticks([0.0, 1.0])
            cb1.set_ticklabels(["", ""])
            # TODO SLB, update path below to non-specific one
            file = (
                "/home/andy/cf-docs/cfplot_sphinx/images/"
                f"colour_scales/{scale}.png"
            )
            plot.savefig(file)
            plot.close()

            # Use convert to trim the png file to remove white space
            subprocess.call(["convert", "-trim", file, file])

            name_pad = scale
            while len(name_pad) < chars:
                name_pad = name_pad + " "
            fn = f"{name_pad}.. image:: images/colour_scales/{scale}.png"
            print(fn)

        print(div)
        print("")
        print("")


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
    """
    | The cf-plot interface to the Matplotlib colorbar routine.
    |
    | labels - colorbar labels
    | orientation - orientation 'horizontal' or 'vertical'
    | position - user specified colorbar position in normalised
    |            plot coordinates [left, bottom, width, height]
    | shrink - default=1.0 - scale colorbar along length
    | fraction - default = 0.12 - space for the colorbar in
    |            normalised plot coordinates
    | title - title for the colorbar
    | fontsize - font size for the colorbar text
    | fontweight - font weight for the colorbar text
    | text_up_down - label division text up and down starting with up
    | text_down_up - label division text down and up starting with down
    | drawedges - Draw internal delimeter lines in colorbar
    | levs - colorbar levels
    | thick - set height of colorbar - default = 0.015,
    |         in normalised plot coordinates
    | anchor - default=0.3 - anchor point of colorbar within the fraction
    |                        space. 0.0 = close to plot, 1.0 = further away
    | extend = None - extensions for colorbar. The default is for
    |                 extensions at both ends.
    | mid = False - label mid points of colours rather than the boundaries
    | verbose = None
    |
    """

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
    if anchor is None:
        anchor = 0.3
        if plotvars.plot_type > 1:
            anchor = 0.5

    # Code for when the user specifies nlevs to the contour command rather than
    # letting cf-plot work out some levels
    if isinstance(levs, int):
        if plotvars.plot_type == 0:
            myplot = plotvars.mymap
        else:
            myplot = plotvars.plot

        from mpl_toolkits.axes_grid1 import make_axes_locatable

        divider = make_axes_locatable(myplot)
        if orientation == "horizontal":
            if plotvars.plot_type == 1:
                cax = divider.append_axes(
                    "bottom", size="2%", pad=0.3, title=title
                )
            else:
                cax = divider.append_axes(
                    "bottom", size="2%", pad=1.0, title=title
                )
        else:
            cax = divider.append_axes("right", size="2%", pad=0.5, title=title)

        plotvars.master_plot.colorbar(
            plotvars.image, cax=cax, orientation=orientation
        )

        return

    # Change plot position based on colorbar location
    ax1 = None  # define next
    if position is None:
        # Work out whether the plot is a map plot or normal plot
        if plotvars.plot_type == 1 or plotvars.plot_type == 6:
            this_plot = plotvars.mymap
        else:
            this_plot = plotvars.plot

        if plotvars.plot_type == 6 and (
            plotvars.proj == "rotated" or plotvars.proj == "UKCP"
        ):
            this_plot = plotvars.plot

        left, bottom, width, height = this_plot.get_position().bounds

        if orientation == "horizontal":
            if plotvars.plot_type == 1:
                # If the plot is too square in terms of aspect ratio, it
                # will push the colour bar down and it can be cut off, so
                # move the plot up in these cases. Use height and width
                # ratio since this represents the matplotlib object
                # position differences, so is the best way to measure.
                left, bottom, width, height = this_plot.get_position().bounds
                # Empirical sweet spot: roughly where plot area is taller
                # than it is wide, including when plot area is roughly square
                if height / width >= 0.9:
                    this_plot.set_position(
                        [left, bottom + fraction, width, height - fraction]
                    )
                    left, bottom, width, height = (
                        this_plot.get_position().bounds
                    )

                ax1 = plotvars.master_plot.add_axes(
                    [
                        left + width * (1.0 - shrink) / 2.0,
                        bottom + fraction * (anchor - 1.0),
                        width * shrink,
                        thick,
                    ]
                )
            else:
                this_plot.set_position(
                    [left, bottom + fraction, width, height - fraction]
                )
                ax1 = plotvars.master_plot.add_axes(
                    [
                        left + width * (1.0 - shrink) / 2.0,
                        bottom,
                        width * shrink,
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
        # Set axes position on coords supplied by the user
        ax1 = plotvars.master_plot.add_axes(position)

    if levs is None:
        if plotvars.levels is not None:
            levs = np.array(plotvars.levels)
        else:
            if labels is None:
                errstr = "\n\ncbar error - No levels or labels supplied \n\n"
                raise TypeError(errstr)
            else:
                levs = np.arange(len(labels))

    if labels is None:
        labels = levs

    # Work out colour bar labeling
    lbot = levs
    if text_up_down:
        lbot = levs[1:][::2]
        ltop = levs[::2]
    if text_down_up:
        lbot = levs[::2]
        ltop = levs[1:][::2]

    # Get the colour map
    colmap = _cscale_get_map()
    cmap = matplotlib.colors.ListedColormap(colmap)
    if extend is None:
        extend = plotvars.levels_extend

    ncolors = np.size(levs)

    if extend in ("both", "max"):
        ncolors -= 1

    if mid is not None:
        lbot = [
            (lbot[i + 1] - lbot[i]) / 2.0 + lbot[i]
            for i in np.arange(len(labels))
        ]

    if not isinstance(levs, int):
        plotvars.norm = matplotlib.colors.BoundaryNorm(
            boundaries=levs, ncolors=ncolors
        )

        # Change boundaries to floats
        boundaries = levs.astype(float)

        # Add colorbar extensions if definded by levs.  Using boundaries[0]-1
        # for the lower and boundaries[-1]+1 is just for the colorbar and
        # has no meaning for the plot.
        if extend in ("both", "min"):
            cmap.set_under(plotvars.cs[0])
            boundaries = np.insert(boundaries, 0, boundaries[0] - 1)
        if extend in ("both", "max"):
            cmap.set_over(plotvars.cs[-1])
            boundaries = np.insert(
                boundaries, len(boundaries), boundaries[-1] + 1
            )

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

    # Bug in Matplotlib colorbar labelling
    # With clevs=[-1, 1, 10000, 20000, 30000, 40000, 50000, 60000]
    # Labels are [0, 2, 10001, 20001, 30001, 40001, 50001, 60001]
    # With a +1 near to the colorbar label

    # Check for an extraneous level compared to the levs
    if len(labels) > len(levs):
        labels = labels[: len(levs)]

    colorbar.set_ticklabels([str(i) for i in labels])
    if orientation == "horizontal":
        for tick in colorbar.ax.xaxis.get_ticklines():
            tick.set_visible(False)
        for t in colorbar.ax.get_xticklabels():
            t.set_fontsize(fontsize)
            t.set_fontweight(fontweight)
    else:
        for tick in colorbar.ax.yaxis.get_ticklines():
            tick.set_visible(False)
        for t in colorbar.ax.get_yticklabels():
            t.set_fontsize(fontsize)
            t.set_fontweight(fontweight)

    # Alternate text top and bottom on a horizontal colorbar if requested
    # Use method described at:
    # https://stackoverflow.com/questions/37161022/matplotlib-colorbar-
    # alternating-top-bottom-labels
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

        # Print bottom tick labels
        colorbar.ax.set_xticklabels(lbot)

        # Print top tick labels
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

        for t in colorbar.ax.get_xticklabels():
            t.set_fontsize(fontsize)
            t.set_fontweight(fontweight)
