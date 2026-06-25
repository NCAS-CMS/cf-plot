import cf
import numpy as np

from .map_runtime import _apply_dim_titles
from .layout_runtime import (
    ensure_runtime_session,
    finalize_runtime_session,
    set_axis_visibility,
)
from .state import plotvars
from . import utility
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
    """
    | The interface to line plotting in cf-plot.
    |
    | The minimum use is lineplot(f) where f is a CF field.
    | If x and y are passed then an appropriate plot is made allowing
    | x vs data and y vs data plots.

    | When making a labelled line plot:
    | always have a label for each line
    | always put the legend location as an option to the last call to lineplot
    |
    | f - CF data used to make a line plot
    | x - x locations of data in y
    | y - y locations of data in x
    | linestyle='-' - line style
    | color=None - line color. Defaults to Matplotlib colour scheme
    |              unless specified
    | linewidth=1.0 - line width
    | marker=None - marker for points along the line
    | markersize=5.0 - size of the marker
    | markeredgecolor = 'k' - colour of edge around the marker
    | markeredgewidth = 0.5 - width of edge around the marker
    | xlog=False - log x-axis
    | ylog=False - log y-axis
    | label=None - line label - label for line
    | legend_location='upper right' - default location of legend
    |                 Other options are {'best': 0, 'center': 10,
    |                                    'center left': 6,
    |                                    'center right': 7, 'lower center': 8,
    |                                    'lower left': 3, 'lower right': 4,
    |                                    'right': 5,
    |                                    'upper center': 9, 'upper left': 2,
    |                                    'upper right': 1}
    | titles=False - set to True to have a dimensions title
    | verbose=None - change to 1 to get a verbose listing of what lineplot
    |                is doing
    | zorder=None - plotting order
    |
    | The following parameters override any CF data defaults:
    | title=None - plot title
    | xunits=None - x units
    | yunits=None - y units
    | xlabel=None - x name
    | ylabel=None - y name
    | xname=None - deprecated keyword
    | yname=None - deprecated keyword
    | xticks=None - x ticks
    | xticklabels=None - x tick labels
    | yticks=None - y ticks
    | yticklabels - y tick labels
    | axes=True - plot x and y axes
    | xaxis=True - plot xaxis
    | yaxis=True - plot y axis
    |
    |
    | When making a multiple line plot:
    | a) set the axis limits with gset before plotting the lines
    | b) the last call to lineplot is the one that any of the above
    |    axis overrides should be placed in.
    |
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
                plot_xlabel = (
                    f"{utility.cf_var_name(field=f, dim=mydim)} ({xlabel_units})"
                )
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
