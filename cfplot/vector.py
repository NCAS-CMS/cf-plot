from copy import deepcopy

import cartopy.crs as ccrs
import cf
import numpy as np

from .layout_runtime import (
    apply_axes,
    ensure_runtime_session,
    finalize_runtime_session,
    gset,
    set_axis_visibility,
)
from .map_runtime import (
    _apply_current_map_title,
    _apply_dim_titles,
    _apply_map_axes_with_toggles,
    _apply_map_features,
    _ensure_map_axes,
    mapset,
)
from .rotated_runtime import _render_rotated_grid_axes
from .state import plotvars
from . import utility
from .utility import mapaxis
from .validate import _check_data


def _mapaxis(min=None, max=None, type=None):
    return mapaxis(
        min_val=min,
        max_val=max,
        axis_type=type,
        degsym=bool(plotvars.degsym),
    )




def axes_plot(
    xticks=None,
    xticklabels=None,
    yticks=None,
    yticklabels=None,
    xlabel=None,
    ylabel=None,
    title=None,
    axes=True,
    xaxis=True,
    yaxis=True,
):
    apply_axes(
        plot_type=plotvars.plot_type,
        xticks=xticks,
        yticks=yticks,
        xlabel=xlabel,
        ylabel=ylabel,
        xticklabels=xticklabels,
        yticklabels=yticklabels,
    )

    if title is not None and plotvars.plot is not None:
        plotvars.plot.set_title(
            title,
            y=1.03,
            fontsize=plotvars.title_fontsize,
            fontweight=plotvars.title_fontweight,
        )

    set_axis_visibility(
        plotvars.plot,
        axes=axes,
        xaxis=xaxis,
        yaxis=yaxis,
    )


def vect(
    u=None,
    v=None,
    x=None,
    y=None,
    scale=None,
    stride=None,
    pts=None,
    key_length=None,
    key_label=None,
    ptype=None,
    title=None,
    magmin=None,
    width=0.02,
    headwidth=3,
    headlength=5,
    headaxislength=4.5,
    pivot="middle",
    key_location=[0.95, -0.06],
    key_show=True,
    axes=True,
    xaxis=True,
    yaxis=True,
    xticks=None,
    xticklabels=None,
    yticks=None,
    yticklabels=None,
    xlabel=None,
    ylabel=None,
    ylog=False,
    color="k",
    zorder=3,
    titles=None,
    alpha=1.0,
):
    """
    | Plot vectors.
    |
    | u=None - u wind
    | v=None - v wind
    | x=None - x locations of u and v
    | y=None - y locations of u and v
    | scale=None - data units per arrow length unit.  A smaller values gives
    |              a larger vector. Generally takes one value but in the case
    |              of two supplied values the second vector scaling applies to
    |              the v field.
    | stride=None - plot vector every stride points. Can take two values one
    |               for x and one for y.
    | pts=None - use bilinear interpolation to interpolate vectors onto a new
    |            grid - takes one or two values.
    |            If one value is passed then this is used for both the x and
    |            y axes.
    | magmin=None - don't plot any vects with less than this magnitude.
    | key_length=None - length of the key.  Generally takes one value but in
    |                   the case of two supplied values the second vector
    |                   scaling applies to the v field.
    | key_label=None - label for the key. Generally takes one value but in the
    |                  case of two supplied values the second vector scaling
    |                  applies to the v field.
    | key_location=[0.9, -0.06] - location of the vector key relative to the
    |                             plot in normalised coordinates.
    | key_show=True - draw the key.  Set to False if not required.
    | ptype=0 - plot type - not needed for cf fields.
    |                       0 = no specific plot type,
    |                       1 = longitude-latitude,
    |                       2 = latitude - height,
    |                       3 = longitude - height,
    |                       4 = latitude - time,
    |                       5 = longitude - time
    |                       6 = rotated pole
    |
    | title=None - plot title
    | width=0.005 - shaft width in arrow units; default is 0.005 times the
    |               width of the plot
    | headwidth=3 - head width as multiple of shaft width, default is 3
    | headlength=5 - head length as multiple of shaft width, default is 5
    | headaxislength=4.5 - head length at shaft intersection, default is 4.5
    | pivot='middle' - the part of the arrow that is at the grid point; the
    |                  arrow rotates about this point
                       takes 'tail', 'middle', 'tip'
    | axes=True - plot x and y axes
    | xaxis=True - plot xaxis
    | yaxis=True - plot y axis
    | xticks=None - xtick positions
    | xticklabels=None - xtick labels
    | yticks=None - y tick positions
    | yticklabels=None - ytick labels
    | xlabel=None - label for x axis
    | ylabel=None - label for y axis
    | ylog=False - log y axis
    | color='k' - colour for the vectors - default is black.
    | zorder=3 - plotting order
    | titles=None - generate dimension and cell_methods titles for plot
    | alpha=1.0 - transparency setting.  The default is no transparency.
    |
    :Returns:
     None
    |
    """

    # If the vector color is white set the quicker key colour to black
    # so that it can be seen
    qkey_color = color
    if qkey_color == "w" or qkey_color == "white":
        qkey_color = "k"

    colorbar_title = ""
    text_fontsize = plotvars.text_fontsize
    continent_thickness = plotvars.continent_thickness
    continent_color = plotvars.continent_color
    if text_fontsize is None:
        text_fontsize = 11
    if continent_thickness is None:
        continent_thickness = 1.5
    if continent_color is None:
        continent_color = "k"
    # ylog=plotvars.ylog
    title_fontsize = plotvars.title_fontsize
    title_fontweight = plotvars.title_fontweight
    if title_fontsize is None:
        title_fontsize = 15
    resolution_orig = plotvars.resolution

    # Set potential user axis labels
    user_xlabel = xlabel
    user_ylabel = ylabel

    rotated_vect = False
    if isinstance(u, cf.Field):
        if u.ref(
            "grid_mapping_name:rotated_latitude_longitude", default=False
        ):
            rotated_vect = True

    # Extract required data
    # If a cf-python field
    if isinstance(u, cf.Field):

        # Check data is 2D
        ndims = np.squeeze(u.data).ndim
        if ndims != 2:
            errstr = (
                "\n\ncfp.vect error need a 2 dimensonal u field to make "
                "vectors\n"
                f"received {np.squeeze(u.data).ndim}"
            )
            if ndims == 1:
                errstr += " dimension\n\n"
            else:
                errstr += " dimensions\n\n"
            raise TypeError(errstr)

        (
            u_data,
            u_x,
            u_y,
            ptype,
            colorbar_title,
            xlabel,
            ylabel,
            xpole,
            ypole,
        ) = utility.cf_data_assign(
            u, colorbar_title, proj=("rotated" if rotated_vect else plotvars.proj)
        )
    elif isinstance(u, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        # field=f #field data passed in as f
        _check_data(u, x, y)
        u_data = deepcopy(u)
        u_x = deepcopy(x)
        u_y = deepcopy(y)
        xlabel = ""
        ylabel = ""

    if isinstance(v, cf.Field):

        # Check data is 2D
        ndims = np.squeeze(v.data).ndim
        if ndims != 2:
            errstr = (
                "\n\ncfp.vect error need a 2 dimensonal v field to make "
                "vectors\n"
                "received {np.squeeze(v.data).ndim}"
            )
            if ndims == 1:
                errstr += " dimension\n\n"
            else:
                errstr += " dimensions\n\n"
            raise TypeError(errstr)

        (
            v_data,
            v_x,
            v_y,
            ptype,
            colorbar_title,
            xlabel,
            ylabel,
            xpole,
            ypole,
        ) = utility.cf_data_assign(
            v, colorbar_title, proj=("rotated" if rotated_vect else plotvars.proj)
        )
    elif isinstance(v, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        # field=f #field data passed in as f
        _check_data(v, x, y)
        v_data = deepcopy(v)
        v_x = deepcopy(x)
        xlabel = ""
        ylabel = ""

    # If a minimum magnitude is specified mask these data points
    if magmin is not None:
        mag = np.sqrt(u_data**2 + v_data**2)
        invalid = np.where(mag <= magmin)
        if np.size(invalid) > 0:
            u_data[invalid] = np.nan
            v_data[invalid] = np.nan

    # Reset xlabel and ylabel values with user defined labels in specified
    if user_xlabel is not None:
        xlabel = user_xlabel
    if user_ylabel is not None:
        ylabel = user_ylabel

    # Retrieve any user defined axis labels
    if xlabel == "" and plotvars.xlabel is not None:
        xlabel = plotvars.xlabel
    if ylabel == "" and plotvars.ylabel is not None:
        ylabel = plotvars.ylabel
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

    if scale is None:
        scale = np.nanmax(u_data) / 4.0

    if key_length is None:
        key_length = scale

    # Calculate a set of dimension titles if requested
    if titles:
        title_dims = utility.generate_titles(u)
        title_dims = f"u\n{title_dims}"
        title_dims2 = utility.generate_titles(v)
        title_dims2 = f"v\n{title_dims2}"

    # Open a new plot if necessary
    auto_session = ensure_runtime_session(pos=1)

    # Set plot type if user specified
    if ptype is not None:
        plotvars.plot_type = ptype

    lonrange = np.nanmax(u_x) - np.nanmin(u_x)
    latrange = np.nanmax(u_y) - np.nanmin(u_y)

    if plotvars.plot_type == 1:
        # Set up mapping
        if (lonrange > 350 and latrange > 170) or plotvars.user_mapset == 1:
            _ensure_map_axes()
        else:
            mapset(
                lonmin=np.nanmin(u_x),
                lonmax=np.nanmax(u_x),
                latmin=np.nanmin(u_y),
                latmax=np.nanmax(u_y),
                user_mapset=0,
                resolution=resolution_orig,
            )
            _ensure_map_axes()

        mymap = plotvars.mymap

        # u_data, u_x = cartopy_util.add_cyclic_point(u_data, u_x)
        u_data, u_x = utility.add_cyclic(u_data, u_x)
        # v_data, v_x = cartopy_util.add_cyclic_point(v_data, v_x)
        v_data, v_x = utility.add_cyclic(v_data, v_x)

    # stride data points to reduce vector density
    if stride is not None:
        if np.size(stride) == 1:
            xstride = stride
            ystride = stride
        if np.size(stride) == 2:
            xstride = stride[0]
            ystride = stride[1]

        u_x = u_x[0::xstride]
        u_y = u_y[0::ystride]
        u_data = u_data[0::ystride, 0::xstride]
        v_data = v_data[0::ystride, 0::xstride]

    # Map vectors
    if plotvars.plot_type == 1:
        lonmax = plotvars.lonmax
        proj = ccrs.PlateCarree()

        # Fix for high latitude vectors as described at
        # https://github.com/SciTools/cartopy/issues/1179
        if plotvars.proj != "cyl":
            u_src_crs = u_data / np.cos(u_y[:, np.newaxis] / 180 * np.pi)
            v_src_crs = v_data
            magnitude = np.ma.sqrt(u_data**2 + v_data**2)
            magn_src_crs = np.ma.sqrt(u_src_crs**2 + v_src_crs**2)

            u_data = u_src_crs * magnitude / magn_src_crs
            v_data = v_src_crs * magnitude / magn_src_crs

        if pts is None:
            quiv = plotvars.mymap.quiver(
                u_x,
                u_y,
                u_data,
                v_data,
                scale=scale,
                pivot=pivot,
                units="inches",
                width=width,
                headwidth=headwidth,
                headlength=headlength,
                headaxislength=headaxislength,
                color=color,
                transform=proj,
                alpha=alpha,
                zorder=zorder,
            )
        else:
            if plotvars.proj == "cyl":
                # **cartopy 0.16 fix for longitide points in cylindrical
                # projection when regridding to a number of points
                # Make points within the plotting region
                for pt in np.arange(np.size(u_x)):
                    if u_x[pt] > lonmax:
                        u_x[pt] = u_x[pt] - 360

            quiv = plotvars.mymap.quiver(
                u_x,
                u_y,
                u_data,
                v_data,
                scale=scale,
                pivot=pivot,
                units="inches",
                width=width,
                headwidth=headwidth,
                headlength=headlength,
                headaxislength=headaxislength,
                color=color,
                regrid_shape=pts,
                transform=proj,
                alpha=alpha,
                zorder=zorder,
            )

        # Make key_label if none exists
        if key_label is None:
            key_label = str(key_length)
        if isinstance(u, cf.Field):
            key_label = utility._supscr(key_label + u.units)
        if key_show:
            plotvars.mymap.quiverkey(
                quiv,
                key_location[0],
                key_location[1],
                key_length,
                key_label,
                labelpos="W",
                color=qkey_color,
                fontproperties={"size": str(plotvars.axis_label_fontsize)},
                coordinates="axes",
            )

        # axes
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
            continent_linestyle=plotvars.continent_linestyle,
        )

        # Title
        if title is not None:
            _apply_current_map_title(title)

        # Titles for dimensions
        if titles:
            if plotvars.titles_con_called is False:
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
                    title2=title_dims2,
                )
            else:
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
                    title2=title_dims,
                    title3=title_dims2,
                )

    if plotvars.plot_type == 6:
        if u.ref("grid_mapping_name:rotated_latitude_longitude", False):
            proj = ccrs.PlateCarree()

            # Set up mapping
            if (
                lonrange > 350 and latrange > 170
            ) or plotvars.user_mapset == 1:
                _ensure_map_axes()

            else:
                mapset(
                    lonmin=np.nanmin(u_x),
                    lonmax=np.nanmax(u_x),
                    latmin=np.nanmin(u_y),
                    latmax=np.nanmax(u_y),
                    user_mapset=0,
                    resolution=resolution_orig,
                )
                _ensure_map_axes()

            quiv = plotvars.mymap.quiver(
                u_x,
                u_y,
                u_data,
                v_data,
                scale=scale * 10,
                transform=proj,
                pivot=pivot,
                units="inches",
                width=width,
                headwidth=headwidth,
                headlength=headlength,
                headaxislength=headaxislength,
                color=color,
                alpha=alpha,
                zorder=zorder,
            )

            # Make key_label if none exists
            if key_label is None:
                key_label = str(key_length)
            if isinstance(u, cf.Field):
                key_label = utility._supscr(key_label + u.units)

            if key_show:
                plotvars.mymap.quiverkey(
                    quiv,
                    key_location[0],
                    key_location[1],
                    key_length,
                    key_label,
                    labelpos="W",
                    color=qkey_color,
                    fontproperties={"size": str(plotvars.axis_label_fontsize)},
                    coordinates="axes",
                )

            # Axes on the native grid
            if plotvars.plot == "rotated":
                _render_rotated_grid_axes(
                    xpole=xpole,
                    ypole=ypole,
                    xvec=u_x,
                    yvec=u_y,
                    xticks=xticks,
                    xticklabels=xticklabels,
                    yticks=yticks,
                    yticklabels=yticklabels,
                    axes=axes,
                    xaxis=xaxis,
                    yaxis=yaxis,
                    xlabel=xlabel,
                    ylabel=ylabel,
                )

            if plotvars.plot == "cyl":
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

            # Title
            if title is not None:
                _apply_current_map_title(title)

            # Titles for dimensions
            if titles:
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
                    title2=title_dims2,
                )

    ######################################
    # Latitude or longitude vs height plot
    ######################################
    if plotvars.plot_type == 2 or plotvars.plot_type == 3:

        user_gset = plotvars.user_gset
        if user_gset == 0:
            # Program selected data plot limits
            xmin = np.nanmin(u_x)
            xmax = np.nanmax(u_x)
            if plotvars.plot_type == 2:
                if xmin < -80 and xmin >= -90:
                    xmin = -90
                if xmax > 80 and xmax <= 90:
                    xmax = 90
            ymin = np.nanmin(u_y)
            if ymin <= 10:
                ymin = 0
            ymax = np.nanmax(u_y)
        else:
            # User specified plot limits
            xmin = plotvars.xmin
            xmax = plotvars.xmax
            if plotvars.ymin < plotvars.ymax:
                ymin = plotvars.ymin
                ymax = plotvars.ymax
            else:
                ymin = plotvars.ymax
                ymax = plotvars.ymin

        ystep = None
        if ymax == 1000:
            ystep = 100
        if ymax == 100000:
            ystep = 10000

        ytype = 0  # pressure or similar y axis
        if "theta" in ylabel.split(" "):
            ytype = 1
        if "height" in ylabel.split(" "):
            ytype = 1
            ystep = 100
            if (ymax - ymin) > 5000:
                ystep = 500.0
            if (ymax - ymin) > 10000:
                ystep = 1000.0
            if (ymax - ymin) > 50000:
                ystep = 10000.0

        # Set plot limits and draw axes
        if ylog != 1:
            if ytype == 1:
                gset(
                    xmin=xmin,
                    xmax=xmax,
                    ymin=ymin,
                    ymax=ymax,
                    user_gset=user_gset,
                )
            else:
                gset(
                    xmin=xmin,
                    xmax=xmax,
                    ymin=ymax,
                    ymax=ymin,
                    user_gset=user_gset,
                )

            # Set default x-axis labels
            lltype = 1
            if plotvars.plot_type == 2:
                lltype = 2
            llticks, lllabels = _mapaxis(min=xmin, max=xmax, type=lltype)

            heightticks = utility.gvals(
                dmin=ymin, dmax=ymax, mystep=ystep, mod=False
            )[0]
            heightlabels = heightticks

            if axes:
                if xaxis:
                    if xticks is not None:
                        llticks = xticks
                        lllabels = xticks
                        if xticklabels is not None:
                            lllabels = xticklabels
                else:
                    xlabel = ""

                if yaxis:
                    if yticks is not None:
                        heightticks = yticks
                        heightlabels = yticks
                        if yticklabels is not None:
                            heightlabels = yticklabels
                else:
                    ylabel = ""

            else:
                xlabel = ""
                ylabel = ""

            axes_plot(
                xticks=llticks,
                xticklabels=lllabels,
                yticks=heightticks,
                yticklabels=heightlabels,
                xlabel=xlabel,
                ylabel=ylabel,
                axes=axes,
                xaxis=xaxis,
                yaxis=yaxis,
            )

        # Log y axis
        if ylog:
            if ymin == 0:
                ymin = 1  # reset zero mb/height input to a small value
            gset(
                xmin=xmin,
                xmax=xmax,
                ymin=ymax,
                ymax=ymin,
                ylog=1,
                user_gset=user_gset,
            )
            llticks, lllabels = _mapaxis(
                min=xmin, max=xmax, type=plotvars.plot_type
            )

            if axes:
                if xaxis:
                    if xticks is not None:
                        llticks = xticks
                        lllabels = xticks
                        if xticklabels is not None:
                            lllabels = xticklabels
                else:
                    xlabel = ""

                if yaxis:
                    if yticks is not None:
                        heightticks = yticks
                        heightlabels = yticks
                        if yticklabels is not None:
                            heightlabels = yticklabels
                else:
                    ylabel = ""

                if yticks is None:
                    axes_plot(
                        xticks=llticks,
                        xticklabels=lllabels,
                        xlabel=xlabel,
                        ylabel=ylabel,
                        axes=axes,
                        xaxis=xaxis,
                        yaxis=yaxis,
                    )
                else:
                    axes_plot(
                        xticks=llticks,
                        xticklabels=lllabels,
                        yticks=heightticks,
                        yticklabels=heightlabels,
                        xlabel=xlabel,
                        ylabel=ylabel,
                        axes=axes,
                        xaxis=xaxis,
                        yaxis=yaxis,
                    )

        # Regrid the data if requested
        if pts is not None:

            xnew, ynew = utility.stipple_points(
                xmin=np.min(u_x),
                xmax=np.max(u_x),
                ymin=np.min(u_y),
                ymax=np.max(u_y),
                pts=pts,
                stype=1,
            )

            if ytype == 0:
                # Make y interpolation in log space as we have a pressure
                # coordinate
                u_vals = utility.regrid(
                    f=u_data,
                    x=u_x,
                    y=np.log10(u_y),
                    xnew=xnew,
                    ynew=np.log10(ynew),
                )
                v_vals = utility.regrid(
                    f=v_data,
                    x=u_x,
                    y=np.log10(u_y),
                    xnew=xnew,
                    ynew=np.log10(ynew),
                )
            else:
                u_vals = utility.regrid(
                    f=u_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew
                )
                v_vals = utility.regrid(
                    f=v_data, x=u_x, y=u_y, xnew=xnew, ynew=ynew
                )

            u_x = xnew
            u_y = ynew
            u_data = u_vals
            v_data = v_vals

        # set scale and key lengths
        if np.size(scale) == 1:
            scale_u = scale
            scale_v = scale
        else:
            scale_u = scale[0]
            scale_v = scale[1]

        if np.size(key_length) == 2:
            key_length_u = key_length[0]
            key_length_v = key_length[1]
            # scale v data
            v_data = v_data * scale_u / scale_v
        else:
            key_length_u = key_length

        # Plot the vectors
        quiv = plotvars.plot.quiver(
            u_x,
            u_y,
            u_data,
            v_data,
            pivot=pivot,
            units="inches",
            scale=scale_u,
            width=width,
            headwidth=headwidth,
            headlength=headlength,
            headaxislength=headaxislength,
            color=color,
            alpha=alpha,
            zorder=zorder,
        )

        # Plot single key
        if np.size(scale) == 1:
            # Single scale vector
            if key_label is None:
                key_label_u = str(key_length_u)
                if isinstance(u, cf.Field):
                    key_label_u = utility._supscr(f"{key_label_u} ({u.units})")
            else:
                key_label_u = key_label[0]
            if key_show:
                plotvars.plot.quiverkey(
                    quiv,
                    key_location[0],
                    key_location[1],
                    key_length_u,
                    key_label_u,
                    labelpos="W",
                    color=qkey_color,
                    fontproperties={"size": str(plotvars.axis_label_fontsize)},
                )

        # Plot two keys
        if np.size(scale) == 2:
            # translate from normalised units to plot units
            xpos = (
                key_location[0] * (plotvars.xmax - plotvars.xmin)
                + plotvars.xmin
            )
            ypos = (
                key_location[1] * (plotvars.ymax - plotvars.ymin)
                + plotvars.ymin
            )

            # horizontal and vertical spacings for offsetting vector reference
            # text
            xoffset = 0.01 * abs(plotvars.xmax - plotvars.xmin)
            yoffset = 0.01 * abs(plotvars.ymax - plotvars.ymin)

            # Assign key labels if necessary
            if key_label is None:
                key_label_u = str(key_length_u)
                key_label_v = str(key_length_v)
                if isinstance(u, cf.Field):
                    key_label_u = utility._supscr(f"{key_label_u} ({u.units})")
                if isinstance(v, cf.Field):
                    key_label_v = utility._supscr(f"{key_label_v} ({v.units})")
            else:
                key_label_u = utility._supscr(key_label[0])
                key_label_v = utility._supscr(key_label[1])

            # Plot reference vectors and keys
            if key_show:
                plotvars.plot.quiver(
                    xpos,
                    ypos,
                    key_length[0],
                    0,
                    pivot="tail",
                    units="inches",
                    scale=scale[0],
                    headaxislength=headaxislength,
                    width=width,
                    headwidth=headwidth,
                    headlength=headlength,
                    clip_on=False,
                    color=qkey_color,
                )

                plotvars.plot.quiver(
                    xpos,
                    ypos,
                    0,
                    key_length[1],
                    pivot="tail",
                    units="inches",
                    scale=scale[1],
                    headaxislength=headaxislength,
                    width=width,
                    headwidth=headwidth,
                    headlength=headlength,
                    clip_on=False,
                    color=qkey_color,
                )

                plotvars.plot.text(
                    xpos,
                    ypos + yoffset,
                    key_label_u,
                    horizontalalignment="left",
                    verticalalignment="top",
                )
                plotvars.plot.text(
                    xpos - xoffset,
                    ypos,
                    key_label_v,
                    horizontalalignment="right",
                    verticalalignment="bottom",
                )

        if title is not None:
            plotvars.plot.set_title(
                title,
                y=1.03,
                fontsize=plotvars.title_fontsize,
                fontweight=title_fontweight,
            )

            # Titles for dimensions
            if titles:
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
                    title2=title_dims2,
                )

    ##########
    # Save plot
    ##########
    finalize_runtime_session(
        auto_session=auto_session,
        reset_limits=True,
        reset_colour_scale=True,
        view=True,
    )

    if plotvars.user_mapset == 0:
        mapset()
        mapset(resolution=resolution_orig)
