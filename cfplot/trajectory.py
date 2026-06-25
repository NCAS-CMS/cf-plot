from copy import deepcopy

import cartopy.crs as ccrs
import cf
import numpy as np

from .colour import cbar
from .colour import cscale
from .layout_runtime import ensure_runtime_session, finalize_runtime_session, gset
from .map_runtime import (
    _apply_current_map_title,
    _apply_map_axes_with_toggles,
    _apply_map_features,
    _ensure_map_axes,
)
from .state import plotvars
from . import utility


def traj(
    f=None,
    title=None,
    ptype=0,
    linestyle="-",
    linewidth=1.0,
    linecolor="b",
    marker="o",
    markevery=1,
    markersize=5.0,
    markerfacecolor="r",
    markeredgecolor="g",
    markeredgewidth=1.0,
    latmax=None,
    latmin=None,
    axes=True,
    xaxis=True,
    yaxis=True,
    verbose=None,
    legend=False,
    legend_lines=False,
    xlabel=None,
    ylabel=None,
    xticks=None,
    yticks=None,
    xticklabels=None,
    yticklabels=None,
    colorbar=None,
    colorbar_position=None,
    colorbar_orientation="horizontal",
    colorbar_title=None,
    colorbar_text_up_down=False,
    colorbar_text_down_up=False,
    colorbar_drawedges=True,
    colorbar_fraction=None,
    colorbar_thick=None,
    colorbar_anchor=None,
    colorbar_shrink=None,
    colorbar_labels=None,
    vector=False,
    head_width=0.4,
    head_length=1.0,
    fc="k",
    ec="k",
    zorder=None,
):
    """
    | The interface to trajectory plotting in cf-plot.
    |
    | The minimum use is traj(f) where f is a CF field.
    |
    | f - CF data used to make a line plot
    | linestyle='-' - line style
    | linecolor='b' - line colour
    | linewidth=1.0 - line width
    | marker='o' - marker for points along the line
    | markersize=30 - size of the marker
    | markerfacecolor='b' - colour of the marker face
    | markeredgecolor='g' - colour of the marker edge
    | legend=False - plot different colour markers based on a set of user
    |                levels
    | zorder=None - order for plotting
    | verbose=None - Set to True to get a verbose listing of what traj is doing
    |
    | The following parameters override any CF data defaults:
    | title=None - plot title
    | axes=True - plot x and y axes
    | xaxis=True - plot xaxis
    | yaxis=True - plot y axis
    | xlabel=None - x name
    | ylabel=None - y name
    | xticks=None - x ticks
    | xticklabels=None - x tick labels
    | yticks=None - y ticks
    | yticklabels=None - y tick labels
    | colorbar=None - plot a colorbar
    | colorbar_position=None - position of colorbar
    |                          [xmin, ymin, x_extent,y_extent] in normalised
    |                          coordinates. Use when a common colorbar
    |                          is required for a set of plots. A typical set
    |                          of values would be [0.1, 0.05, 0.8, 0.02]
    | colorbar_orientation=None - orientation of the colorbar
    | colorbar_title=None - title for the colorbar
    | colorbar_text_up_down=False - if True horizontal colour bar labels
    |                               alternate above (start) and below the
    |                               colour bar
    | colorbar_text_down_up=False - if True horizontal colour bar labels
    |                               alternate below (start) and above the
    |                               colour bar
    | colorbar_drawedges=True - draw internal divisions in the colorbar
    | colorbar_fraction=None - space for the colorbar - default = 0.21, in
    |                          normalised coordinates
    | colorbar_thick=None - thickness of the colorbar - default = 0.015, in
    |                       normalised coordinates
    | colorbar_anchor=None - default=0.5 - anchor point of colorbar within
    |                        the fraction space. 0.0 = close to plot,
    |                        1.0 = further away
    | colorbar_shrink=None - value to shrink the colorbar by.  If the colorbar
    |                        exceeds the plot area then values of 1.0, 0.55
    |                        or 0.5m ay help it better fit the plot area.
    | colorbar_labels=None - labels for the colorbar. Default is to use the
    |                        levels defined
    |                        using cfp.levs
    | Vector options
    | vector=False - Draw vectors
    | head_width=2.0 - vector head width
    | head_length=2.0 - vector head length
    | fc='k' - vector face colour
    | ec='k' - vector edge colour

    """
    is_1d_data = False
    if f.ndim == 1:
        is_1d_data = True

    is_dsg = False
    if f.DSG or is_1d_data:  # registered as a DSG or if is 1D, assume is DSG
        is_dsg = True

    if verbose:
        print("traj - making a trajectory plot")

    if isinstance(f, cf.FieldList):
        errstr = (
            "\n\ncfp.traj - cannot make a trajectory plot from a field list "
            "- need to pass a field\n\n"
        )
        raise TypeError(errstr)

    # Read in data
    # Find the auxiliary lons and lats if provided
    has_lons = False
    has_lats = False
    for mydim in list(f.auxiliary_coordinates()):
        name = utility.cf_var_name(field=f, dim=mydim)
        if name in ["longitude"]:
            lons = np.squeeze(f.construct(mydim).array)
            has_lons = True
        if name in ["latitude"]:
            lats = np.squeeze(f.construct(mydim).array)
            has_lats = True

    data = f.array

    # Raise an error if lons and lats not found in the input data
    if not has_lons or not has_lats:
        message = "\n\n\ntraj error\n"
        if not has_lons:
            message += "missing longitudes in the field auxiliary data\n"
        if not has_lats:
            message += "missing latitudes in the field auxiliary data\n"
        message += "\n\n\n"
        raise TypeError(message)

    if latmax is not None:
        pts = np.where(lats >= latmax)
        if np.size(pts) > 0:
            lons[pts] = np.nan
            lats[pts] = np.nan

    if latmin is not None:
        pts = np.where(lats <= latmin)
        if np.size(pts) > 0:
            lons[pts] = np.nan
            lats[pts] = np.nan

    # Set potential user axis labels
    user_xlabel = xlabel
    user_ylabel = ylabel

    # Set plotting parameters
    continent_linestyle = plotvars.continent_linestyle or "-"

    ##################
    # Open a new plot if necessary
    ##################
    auto_session = ensure_runtime_session(pos=1)

    # Set up mapping
    if plotvars.user_mapset == 0:
        plotvars.lonmin = -180
        plotvars.lonmax = 180
        plotvars.latmin = -90
        plotvars.latmax = 90

    _ensure_map_axes()
    mymap = plotvars.mymap

    # Set the plot limits
    gset(
        xmin=plotvars.lonmin,
        xmax=plotvars.lonmax,
        ymin=plotvars.latmin,
        ymax=plotvars.latmax,
        user_gset=0,
    )

    # Make lons and lats 2d if they are 1d
    ndim = np.ndim(lons)
    if ndim == 1:
        lons = lons.reshape(1, -1)
        lats = lats.reshape(1, -1)

    ntracks = np.shape(lons)[0]
    if ndim == 1:
        ntracks = 1

    if legend or legend_lines:
        # Check levels are not None
        levs = plotvars.levels
        if plotvars.levels is not None:
            if verbose:
                print(
                    "traj - plotting different colour markers based on a "
                    "user set of levels"
                )
            levs = plotvars.levels

        else:
            # Automatic levels
            if verbose:
                print("traj - generating automatic legend levels")
            dmin = np.nanmin(data)
            dmax = np.nanmax(data)
            levs, mult = utility.gvals(dmin=dmin, dmax=dmax, mod=False)

        # Add extend options to the levels if set
        if plotvars.levels_extend == "min" or plotvars.levels_extend == "both":
            levs = np.append(-1e-30, levs)
        if plotvars.levels_extend == "max" or plotvars.levels_extend == "both":
            levs = np.append(levs, 1e30)

        # Set the default colour scale
        if plotvars.cscale_flag == 0:
            cscale("viridis", ncols=np.size(levs) + 1)
            plotvars.cscale_flag = 0

        # User selected colour map but no mods so fit to levels
        if plotvars.cscale_flag == 1:
            cscale(plotvars.cs_user, ncols=np.size(levs) + 1)
            plotvars.cscale_flag = 1

    ##################################
    # Line, symbol and vector plotting
    ##################################
    for track in np.arange(ntracks):
        xpts = lons[track, :]
        ypts = lats[track, :]
        if is_1d_data:
            data2 = data
        else:
            data2 = data[track, :]

        xpts_orig = deepcopy(xpts)
        xpts = np.mod(xpts + 180, 360) - 180

        # Check if xpts are only within the remapped longitudes above
        if np.min(xpts) < -170 or np.max(xpts) > 170:
            xpts = xpts_orig

            for ix in np.arange(np.size(xpts) - 1):
                diff = xpts[ix + 1] - xpts[ix]
                if diff >= 60:
                    xpts[ix + 1] = xpts[ix + 1] - 360.0
                if diff <= -60:
                    xpts[ix + 1] = xpts[ix + 1] + 360.0

        # Plot lines and markers
        plot_linewidth = linewidth
        plot_markersize = markersize
        if legend:
            plot_markersize = 0.0

        if plot_linewidth > 0.0 or plot_markersize > 0.0:
            if verbose and track == 0 and linewidth > 0.0:
                print("plotting lines")
            if verbose and track == 0 and markersize > 0.0:
                print("plotting markers")

            if legend_lines is False:
                mymap.plot(
                    xpts,
                    ypts,
                    color=linecolor,
                    linewidth=plot_linewidth,
                    linestyle=linestyle,
                    marker=marker,
                    markevery=markevery,
                    markersize=plot_markersize,
                    markerfacecolor=markerfacecolor,
                    markeredgecolor=markeredgecolor,
                    markeredgewidth=markeredgewidth,
                    zorder=zorder,
                    clip_on=True,
                    transform=ccrs.PlateCarree(),
                )
            else:
                line_xpts = xpts.compressed()
                line_ypts = ypts.compressed()
                line_data = data2.compressed()

                for i in np.arange(np.size(line_xpts) - 1):
                    val = (line_data[i] + line_data[i + 1]) / 2.0

                    col = plotvars.cs[np.max(np.where(val > plotvars.levels))]
                    mymap.plot(
                        line_xpts[i : i + 2],
                        line_ypts[i : i + 2],
                        color=col,
                        linewidth=plot_linewidth,
                        linestyle=linestyle,
                        zorder=zorder,
                        clip_on=True,
                        transform=ccrs.PlateCarree(),
                    )

        # Plot vectors
        if vector:
            if verbose and track == 0:
                print("plotting vectors")
            if zorder is None:
                plot_zorder = 101
            else:
                plot_zorder = zorder
            if plotvars.proj == "cyl":
                if isinstance(xpts, np.ma.MaskedArray):
                    pts = np.ma.MaskedArray.count(xpts)
                else:
                    pts = xpts.size

                for pt in np.arange(pts - 1):
                    mymap.arrow(
                        xpts[pt],
                        ypts[pt],
                        xpts[pt + 1] - xpts[pt],
                        ypts[pt + 1] - ypts[pt],
                        head_width=head_width,
                        head_length=head_length,
                        fc=fc,
                        ec=ec,
                        length_includes_head=True,
                        zorder=plot_zorder,
                        clip_on=True,
                        transform=ccrs.PlateCarree(),
                    )

    # Plot different colour markers based on a user set of levels
    if legend:

        # For polar stereographic plots mask any points outside the
        # plotting limb
        if plotvars.proj == "npstere":
            pts = np.where(lats < plotvars.boundinglat)
            if np.size(pts) > 0:
                lats[pts] = np.nan

        if plotvars.proj == "spstere":
            pts = np.where(lats > plotvars.boundinglat)
            if np.size(pts) > 0:
                lats[pts] = np.nan

        for track in np.arange(ntracks):
            xpts = lons[track, :]
            ypts = lats[track, :]
            if is_1d_data:
                data2 = data
            else:
                data2 = data[track, :]

            for i in np.arange(np.size(levs) - 1):
                color = plotvars.cs[i]

                if np.ma.is_masked(data2):
                    pts = np.ma.where(
                        np.logical_and(data2 >= levs[i], data2 <= levs[i + 1])
                    )
                else:
                    pts = np.where(
                        np.logical_and(data2 >= levs[i], data2 <= levs[i + 1])
                    )

                if zorder is None:
                    plot_zorder = 101
                else:
                    plot_zorder = zorder
                if np.size(pts) > 0:

                    # Define the data to plot
                    if is_dsg or is_1d_data:
                        data_colours = [
                            plotvars.cs[np.max(np.where(d > plotvars.levels))]
                            for d in data2[pts]
                        ]
                    else:
                        data_colours = color

                    mymap.scatter(
                        xpts[pts],
                        ypts[pts],
                        s=markersize,
                        c=data_colours,
                        marker=marker,
                        edgecolors=markeredgecolor,
                        linewidths=plot_linewidth,
                        transform=ccrs.PlateCarree(),
                        zorder=plot_zorder,
                    )

    # Axes
    _apply_map_axes_with_toggles(
        axes=axes,
        xaxis=xaxis,
        yaxis=yaxis,
        xticks=xticks,
        xticklabels=xticklabels,
        yticks=yticks,
        yticklabels=yticklabels,
        user_xlabel=user_xlabel,
        user_ylabel=user_ylabel,
    )

    _apply_map_features(
        mymap=mymap,
        continent_color=plotvars.continent_color,
        continent_thickness=plotvars.continent_thickness,
        continent_linestyle=continent_linestyle,
    )

    # Title
    if title is not None:
        _apply_current_map_title(title)

    # Color bar
    plot_colorbar = False
    if colorbar is None and legend:
        plot_colorbar = True
    if colorbar is None and legend_lines:
        plot_colorbar = True
    if colorbar:
        plot_colorbar = True

    if plot_colorbar:
        if colorbar_title is None:
            colorbar_title = "No Name"
            if hasattr(f, "id"):
                colorbar_title = f.id
            nc = f.nc_get_variable(False)
            if nc:
                colorbar_title = f.nc_get_variable()
            if hasattr(f, "short_name"):
                colorbar_title = f.short_name
            if hasattr(f, "long_name"):
                colorbar_title = f.long_name
            if hasattr(f, "standard_name"):
                colorbar_title = f.standard_name

            if hasattr(f, "Units"):
                if str(f.Units) == "":
                    colorbar_title += ""
                else:
                    colorbar_title += f"({utility._supscr(str(f.Units))})"

        levs = plotvars.levels
        if colorbar_labels is not None:
            levs = colorbar_labels
        cbar(
            levs=levs,
            labels=levs,
            orientation=colorbar_orientation,
            position=colorbar_position,
            text_up_down=colorbar_text_up_down,
            text_down_up=colorbar_text_down_up,
            drawedges=colorbar_drawedges,
            fraction=colorbar_fraction,
            thick=colorbar_thick,
            shrink=colorbar_shrink,
            anchor=colorbar_anchor,
            title=colorbar_title,
            verbose=verbose,
        )

    ##########
    # Save plot
    ##########
    finalize_runtime_session(auto_session=auto_session, view=True)
