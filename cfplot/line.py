from functools import wraps

import cf
import numpy as np

from . import utility
from .layout_runtime import (
    ensure_runtime_session,
    finalize_runtime_session,
    set_axis_visibility,
)
from .map_runtime import _apply_dim_titles
from .state import plotvars
from .utility import mapaxis


def lineplot(
    f=None,
    x=None,
    y=None,
    fill=True,
    lines=True,
    line_labels=True,
    title=None,
    ptype=0,
    linestyle="-",
    linewidth=1.0,
    color=None,
    xlog=False,
    ylog=False,
    verbose=None,
    swap_xy=False,
    marker=None,
    markersize=5.0,
    markeredgecolor="k",
    markeredgewidth=0.5,
    label=None,
    legend_location="upper right",
    xunits=None,
    yunits=None,
    xlabel=None,
    ylabel=None,
    xticks=None,
    yticks=None,
    xticklabels=None,
    yticklabels=None,
    xname=None,
    yname=None,
    axes=True,
    xaxis=True,
    yaxis=True,
    titles=False,
    zorder=None,
):
    """Create a line (graph) plot.

    The minimum usage is ``lineplot(f)``, where *f* is a CF field.
    If *x* and *y* are provided, appropriate plots can be made, including
    x-versus-data and y-versus-data plots.

    When making a labelled line plot, always provide a label for each line
    and specify the legend location in the final call to ``lineplot``.

    When making a multiple-line plot:
        - Set the axis limits with ``gset`` before plotting the lines.
        - Place any axis overrides described below in the final call to
          ``lineplot``.

    Parameter breakdown (see below for full detail). The following parameters:
        - specify the input data:
            - ``f``, ``x``, ``y``
        - set the verbosity to toggle log level:
            - ``verbose``
        - configure the line appearance and markers:
            - ``linestyle``, ``color``, ``linewidth``, ``marker``,
              ``markersize``, ``markeredgecolor``, ``markeredgewidth``,
              ``zorder``
        - configure the x- and y-axis scales:
            - ``xlog``, ``ylog``
        - configure line labels and the legend:
            - ``label``, ``legend_location``
        - control titles:
            - ``titles``
        - override the defaults derived from CF data:
            - ``title``, ``axes``, ``xunits``, ``yunits``, ``xlabel``,
              ``ylabel``, ``xticks``, ``yticks``, ``xticklabels``,
              ``yticklabels``, ``xaxis``, ``yaxis``
        - specify deprecated parameters:
            - ``xname``, ``yname``

    Args:
        f: CF data used to make a line plot.
        x: x-coordinates of the data in *y*.
        y: y-coordinates of the data in *x*.

        verbose: Set to ``1`` to display a verbose listing of the operations
            performed by ``lineplot``.

        linestyle: Line style. Defaults to ``'-'``.
        color: Line colour. Defaults to Matplotlib's colour scheme unless
            explicitly specified.
        linewidth: Line width. Defaults to ``1.0``.
        marker: Marker style for points along the line. Defaults to ``None``.
        markersize: Marker size. Defaults to ``5.0``.
        markeredgecolor: Colour of the marker edge. Defaults to ``'k'``.
        markeredgewidth: Width of the marker edge. Defaults to ``0.5``.
        zorder: Plotting order. Defaults to ``None``.

        xlog: If ``True``, use a logarithmic x-axis.
        ylog: If ``True``, use a logarithmic y-axis.

        label: Label for the line. Defaults to ``None``.
        legend_location: Location of the legend. Defaults to
            ``'upper right'``. The available options are:

            .. list-table::
               :header-rows: 1

               * - Value
                 - Location
               * - ``'best'``
                 - Best location (automatically determined)
               * - ``'center'``
                 - Centre
               * - ``'center left'``
                 - Centre left
               * - ``'center right'``
                 - Centre right
               * - ``'lower center'``
                 - Lower centre
               * - ``'lower left'``
                 - Lower left
               * - ``'lower right'``
                 - Lower right
               * - ``'right'``
                 - Right
               * - ``'upper center'``
                 - Upper centre
               * - ``'upper left'``
                 - Upper left
               * - ``'upper right'``
                 - Upper right

        titles: If ``True``, display a dimensions title.

        title: Plot title. Defaults to ``None``.
        axes: If ``True``, display the x- and y-axes.

        xunits: x-axis units. Defaults to ``None``.
        yunits: y-axis units. Defaults to ``None``.
        xlabel: x-axis label. Defaults to ``None``.
        ylabel: y-axis label. Defaults to ``None``.
        xticks: x-axis tick positions. Defaults to ``None``.
        yticks: y-axis tick positions. Defaults to ``None``.
        xticklabels: x-axis tick labels. Defaults to ``None``.
        yticklabels: y-axis tick labels.
        xaxis: If ``True``, display the x-axis.
        yaxis: If ``True``, display the y-axis.

        xname: Deprecated keyword.
        yname: Deprecated keyword.

    Returns:
        None.
    """
    if verbose:
        print("lineplot - making a line plot")

    # Catch deprecated keywords
    if xname is not None or yname is not None:
        print(
            "\nlineplot error\n"
            "xname and yname are now deprecated keywords\n"
            "Please use xlabel and ylabel\n"
        )
        return

    ##################
    # Open a new plot if necessary
    ##################
    auto_session = ensure_runtime_session(pos=1)

    ##################
    # Extract required data
    # If a cf-python field
    ##################
    cf_field = False
    if f is not None:
        if isinstance(f, cf.Field):
            cf_field = True

            # Check data is 1D
            ndims = np.squeeze(f.data).ndim
            if ndims != 1:
                errstr = (
                    "\n\ncfp.lineplot error need a 1 dimensonal field to "
                    "make a line\n"
                    f"received {np.squeeze(f.data).ndim} dimensions\n\n"
                )
                raise TypeError(errstr)

            if x is not None:
                if isinstance(x, cf.Field):
                    errstr = (
                        "\n\ncfp.lineplot error - two or more cf-fields "
                        "passed for plotting.\n"
                        "To plot two cf-fields open a graphics plot with "
                        "cfp.gopen(), \n"
                        "plot the two fields separately with cfp.lineplot "
                        "and then close\n"
                        "the graphics plot with cfp.gclose()\n\n"
                    )
                    raise TypeError(errstr)

        elif isinstance(f, cf.FieldList):
            errstr = "\n\ncfp.lineplot - cannot plot a field list\n\n"
            raise TypeError(errstr)

    plot_xlabel = ""
    plot_ylabel = ""
    xlabel_units = ""
    ylabel_units = ""

    if cf_field:
        # Extract data
        if verbose:
            print("lineplot - CF field, extracting data")

        has_count = 0
        for mydim in list(f.dimension_coordinates()):
            if np.size(np.squeeze(f.construct(mydim).array)) > 1:
                has_count = has_count + 1
                x = np.squeeze(f.construct(mydim).array)

                # x label
                xlabel_units = str(getattr(f.construct(mydim), "Units", ""))
                plot_xlabel = f"{utility.cf_var_name(field=f, dim=mydim)} ({xlabel_units})"
                y = np.squeeze(f.array)

                # y label
                if hasattr(f, "id"):
                    plot_ylabel = f.id
                nc = f.nc_get_variable(False)
                if nc:
                    plot_ylabel = f.nc_get_variable()
                if hasattr(f, "short_name"):
                    plot_ylabel = f.short_name
                if hasattr(f, "long_name"):
                    plot_ylabel = f.long_name
                if hasattr(f, "standard_name"):
                    plot_ylabel = f.standard_name

                if hasattr(f, "Units"):
                    ylabel_units = str(f.Units)
                else:
                    ylabel_units = ""
                plot_ylabel += f" ({ylabel_units})"

        if has_count != 1:
            errstr = (
                "\n lineplot error - passed field is not suitable "
                "for plotting as a line\n"
            )
            for mydim in list(f.dimension_coordinates()):
                sn = getattr(f.construct(mydim), "standard_name", False)
                ln = getattr(f.construct(mydim), "long_name", False)
                if sn:
                    errstr += f"{mydim},{sn},{f.construct(mydim).size}\n"
                else:
                    # TODO SLB: replace simple 'else, if' statements such as
                    # this one, with many other examples in codebase, w/ 'elif'
                    if ln:
                        errstr += f"{mydim},{ln},{f.construct(mydim).size}\n"
            raise Warning(errstr)
    else:
        if verbose:
            print("lineplot - not a CF field, using passed data")
        errstr = ""
        if x is None or y is None:
            errstr = "lineplot error- must define both x and y"
        if f is not None:
            errstr += (
                "lineplot error- must define just x and y to make "
                "a lineplot"
            )
        if errstr != "":
            raise Warning(f"\n{errstr}\n")

    # Z on y-axis
    ztype = None
    if xlabel_units in [
        "mb",
        "mbar",
        "millibar",
        "decibar",
        "atmosphere",
        "atm",
        "pascal",
        "Pa",
        "hPa",
    ]:
        ztype = 1
    if xlabel_units in ["meter", "metre", "m", "kilometer", "kilometre", "km"]:
        ztype = 2

    myz = utility.find_z(f)
    if cf_field and f.has_construct(myz):
        z_coord = f.construct(myz)
        if len(z_coord.array) > 1:
            zlabel = ""
            if hasattr(z_coord, "long_name"):
                zlabel = z_coord.long_name
            if hasattr(z_coord, "standard_name"):
                zlabel = z_coord.standard_name
            if zlabel == "atmosphere_hybrid_height_coordinate":
                ztype = 2

    if ztype is not None:
        x, y = y, x
        plot_xlabel, plot_ylabel = plot_ylabel, plot_xlabel

    # Set data values
    if verbose:
        print("lineplot - setting data values")
    xpts = np.squeeze(x)
    ypts = np.squeeze(y)
    minx = np.min(x)
    miny = np.min(y)
    maxx = np.max(x)
    maxy = np.max(y)

    # Use accumulated plot limits if making a multiple line plot
    if plotvars.graph_xmin is None:
        plotvars.graph_xmin = minx
    else:
        if minx < plotvars.graph_xmin:
            plotvars.graph_xmin = minx

    if plotvars.graph_xmax is None:
        plotvars.graph_xmax = maxx
    else:
        if maxx > plotvars.graph_xmax:
            plotvars.graph_xmax = maxx

    if plotvars.graph_ymin is None:
        plotvars.graph_ymin = miny
    else:
        if miny < plotvars.graph_ymin:
            plotvars.graph_ymin = miny

    if plotvars.graph_ymax is None:
        plotvars.graph_ymax = maxy
    else:
        if maxy > plotvars.graph_ymax:
            plotvars.graph_ymax = maxy

    # Reset plot limits based on accumulated plot limits
    minx = plotvars.graph_xmin
    maxx = plotvars.graph_xmax
    miny = plotvars.graph_ymin
    maxy = plotvars.graph_ymax

    if cf_field and f.has_construct("T"):
        taxis = f.construct("T")

    if ztype == 1:
        miny = np.max(y)
        maxy = np.min(y)

    if ztype == 2:
        if cf_field and f.has_construct("Z"):
            if f.construct("Z").positive == "down":
                miny = np.max(y)
                maxy = np.min(y)

    # Use user set values if present
    time_xstr = False
    time_ystr = False
    if plotvars.xmin is not None:
        minx = plotvars.xmin
        miny = plotvars.ymin
        maxx = plotvars.xmax
        maxy = plotvars.ymax

        # Change from date string to a number if strings are passed
        try:
            float(minx)
        except Exception:
            time_xstr = True
        try:
            float(miny)
        except Exception:
            time_ystr = True

        if cf_field and f.has_construct("T"):
            taxis = f.construct("T")
            if time_xstr or time_ystr:
                ref_time = f.construct("T").units
                ref_calendar = f.construct("T").calendar
                time_units = cf.Units(ref_time, ref_calendar)

                if time_xstr:
                    t = cf.Data(cf.dt(minx), units=time_units)
                    minx = t.array
                    t = cf.Data(cf.dt(maxx), units=time_units)
                    maxx = t.array
                    taxis = cf.Data(
                        [cf.dt(plotvars.xmin), cf.dt(plotvars.xmax)],
                        units=time_units,
                    )

                if time_ystr:
                    t = cf.Data(cf.dt(miny), units=time_units)
                    miny = t.array
                    t = cf.Data(cf.dt(maxy), units=time_units)
                    maxy = t.array
                    taxis = cf.Data(
                        [cf.dt(plotvars.ymin), cf.dt(plotvars.ymax)],
                        units=time_units,
                    )

    # Set x and y labelling
    # Retrieve any user defined axis labels
    if plot_xlabel == "" and plotvars.xlabel is not None:
        plot_xlabel = plotvars.xlabel
    if plot_ylabel == "" and plotvars.ylabel is not None:
        plot_ylabel = plotvars.ylabel
    if xticks is None and plotvars.xticks is not None:
        xticks = plotvars.xticks
        if plotvars.xticklabels is not None:
            xticklabels = plotvars.xticklabels
        else:
            xticklabels = list(map(str, xticks))
    if yticks is None and plotvars.yticks is not None:
        yticks = plotvars.yticks
        if plotvars.yticklabels is not None:
            yticklabels = plotvars.yticklabels
        else:
            yticklabels = list(map(str, yticks))

    mod = False
    ymult = 0

    if xticks is None:
        if plot_xlabel[0:3].lower() == "lon":
            xticks, xticklabels = mapaxis(
                min_val=minx,
                max_val=maxx,
                axis_type=1,
                degsym=bool(plotvars.degsym),
            )
        if plot_xlabel[0:3].lower() == "lat":
            xticks, xticklabels = mapaxis(
                min_val=minx,
                max_val=maxx,
                axis_type=2,
                degsym=bool(plotvars.degsym),
            )
    if cf_field:
        if xticks is None:
            if f.has_construct("T"):
                if np.size(f.construct("T").array) > 1:
                    xticks, xticklabels, plot_xlabel = utility.timeaxis(
                        taxis,
                        user_gset=plotvars.user_gset,
                        xmin=plotvars.xmin,
                        xmax=plotvars.xmax,
                        ymin=plotvars.ymin,
                        ymax=plotvars.ymax,
                        tspace_year=plotvars.tspace_year,
                        tspace_hour=plotvars.tspace_hour,
                        tspace_day=plotvars.tspace_day,
                    )
    if xticks is None:
        xticks, ymult = utility.gvals(dmin=minx, dmax=maxx, mod=mod)

        # Fix long floating point numbers if necessary
        utility.fix_floats(xticks)
        xticklabels = xticks
    else:
        if xticklabels is None:
            xticklabels = []
            for val in xticks:
                xticklabels.append(f"{val}")

    if yticks is None:
        if abs(maxy - miny) > 1:
            if miny < maxy:
                yticks, ymult = utility.gvals(dmin=miny, dmax=maxy, mod=mod)
            if maxy < miny:
                yticks, ymult = utility.gvals(dmin=maxy, dmax=miny, mod=mod)

        else:
            yticks, ymult = utility.gvals(dmin=miny, dmax=maxy, mod=mod)

            # Fix long floating point numbers if necessary
            utility.fix_floats(yticks)

    if yticklabels is None:
        yticklabels = []

        for val in yticks:
            yticklabels.append(str(round(val, 9)))

    if xlabel is not None:
        plot_xlabel = xlabel
        if xunits is not None:
            plot_xlabel += f"({xunits})"

    if ylabel is not None:
        plot_ylabel = ylabel
        if yunits is not None:
            plot_ylabel += f"({yunits})"

    if swap_xy:
        if verbose:
            print("lineplot - swapping x and y")

        xpts, ypts = ypts, xpts
        minx, miny = miny, minx
        maxx, maxy = maxy, maxx
        plot_xlabel, plot_ylabel = plot_ylabel, plot_xlabel
        xticks, yticks = yticks, xticks
        xticklabels, yticklabels = yticklabels, xticklabels

    if plotvars.user_gset == 1:
        if time_xstr is False and time_ystr is False:
            minx = plotvars.xmin
            maxx = plotvars.xmax
            miny = plotvars.ymin
            maxy = plotvars.ymax

    if not axes:
        plot_xlabel = ""
        plot_ylabel = ""
    else:
        if xaxis is not True:
            plot_xlabel = ""
        if yaxis is not True:
            plot_ylabel = ""

    # Generate titles if requested
    if titles:
        title_dims = utility.generate_titles(f)

    # Make graph
    if verbose:
        print("lineplot - making graph")

    xlabelalignment = plotvars.xtick_label_align
    ylabelalignment = plotvars.ytick_label_align

    if lines is False:
        linewidth = 0.0

    colorarg = {}
    if color is not None:
        colorarg = {"color": color}

    graph = plotvars.plot

    if plotvars.twinx:
        graph = graph.twinx()
        ylabelalignment = "left"

    if plotvars.twiny:
        graph = graph.twiny()

    # Reset y limits if minx = maxy
    if plotvars.xmin is None:
        if miny == maxy:
            miny = miny - 1.0
            maxy = maxy + 1.0

    graph.axis([minx, maxx, miny, maxy])
    graph.tick_params(direction="out", which="both", right=True, top=True)
    graph.set_xlabel(
        plot_xlabel,
        fontsize=plotvars.axis_label_fontsize,
        fontweight=plotvars.axis_label_fontweight,
    )
    graph.set_ylabel(
        plot_ylabel,
        fontsize=plotvars.axis_label_fontsize,
        fontweight=plotvars.axis_label_fontweight,
    )

    if plotvars.xlog or xlog:
        graph.set_xscale("log")
    if plotvars.ylog or ylog:
        graph.set_yscale("log")

    if xticks is not None:
        graph.set_xticks(xticks)
        graph.set_xticklabels(
            xticklabels,
            rotation=plotvars.xtick_label_rotation,
            horizontalalignment=xlabelalignment,
            fontsize=plotvars.axis_label_fontsize,
            fontweight=plotvars.axis_label_fontweight,
        )
    if yticks is not None:
        graph.set_yticks(yticks)
        graph.set_yticklabels(
            yticklabels,
            rotation=plotvars.ytick_label_rotation,
            horizontalalignment=ylabelalignment,
            fontsize=plotvars.axis_label_fontsize,
            fontweight=plotvars.axis_label_fontweight,
        )

    set_axis_visibility(graph, axes=axes, xaxis=xaxis, yaxis=yaxis)

    graph.plot(
        xpts,
        ypts,
        **colorarg,
        linestyle=linestyle,
        linewidth=linewidth,
        marker=marker,
        markersize=markersize,
        markeredgecolor=markeredgecolor,
        markeredgewidth=markeredgewidth,
        label=label,
        zorder=zorder,
    )

    # Set axis width if required
    if plotvars.axis_width is not None:
        for axis in ["top", "bottom", "left", "right"]:
            plotvars.plot.spines[axis].set_linewidth(plotvars.axis_width)

    # Add a legend if needed
    if label is not None:
        legend_properties = {
            "size": plotvars.legend_text_size,
            "weight": plotvars.legend_text_weight,
        }
        graph.legend(
            loc=legend_location,
            prop=legend_properties,
            frameon=plotvars.legend_frame,
            edgecolor=plotvars.legend_frame_edge_color,
            facecolor=plotvars.legend_frame_face_color,
        )

    # Set title
    if title is not None:
        graph.set_title(
            title,
            fontsize=plotvars.title_fontsize,
            fontweight=plotvars.title_fontweight,
        )

    # Titles for dimensions
    if titles:
        plotvars.plot = graph
        plotvars.plot_type = 0
        _apply_dim_titles(
            plot=plotvars.plot,
            mymap=plotvars.mymap,
            plot_type=plotvars.plot_type,
            proj=plotvars.proj,
            lonmin=plotvars.lonmin,
            lonmax=plotvars.lonmax,
            latmin=plotvars.latmin,
            latmax=plotvars.latmax,
            axis_label_fontsize=plotvars.axis_label_fontsize,
            axis_label_fontweight=plotvars.axis_label_fontweight,
            title=title_dims,
        )

    ##################
    # Save or view plot
    ##################
    if auto_session and verbose:
        print("Saving or viewing plot")
    finalize_runtime_session(auto_session=auto_session, view=True)


@wraps(lineplot)
def scatter(**kwargs):
    """Docs line here overwritten: see below."""
    if "lines" in kwargs:
        raise ValueError(
            "'lines' is not a valid keyword argument for cfp.scatter."
        )

    return lineplot(lines=False, **kwargs)


# Amend the scatter docstring which by 'wraps' inherits the lineplot one, to
# clarify the lines=False setting on 'scatter' onlt
scatter.__doc__ = (
    "Create a scatter plot. Equivalent to `cfp.lineplot(lines=False, ...)`."
    "\n\n"
    "Has the same signature as `cfp.lineplot` except that `lines=False` is\n"
    "set automatically to produce a plot with scatter markers and no lines.\n"
    "Lineplot signature:\n\n"
    + lineplot.__doc__
)
