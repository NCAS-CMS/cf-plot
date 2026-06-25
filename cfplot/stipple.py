import cartopy.crs as ccrs
import cf
import numpy as np

from .state import plotvars
from . import utility
from .validate import _check_data


def stipple(
    f=None,
    x=None,
    y=None,
    min=None,
    max=None,
    size=80,
    color="k",
    pts=50,
    marker=".",
    edgecolors="k",
    alpha=1.0,
    ylog=False,
    zorder=1,
):
    """
    | Put markers on a plot to indicate value of interest.
    |
    | f=None - cf field or field
    | x=None - x points for field
    | y=None - y points for field
    | min=None - minimum threshold for stipple
    | max=None - maximum threshold for stipple
    | size=80 - default size for stipples
    | color='k' - default colour for stipples
    | pts=50 - number of points in the x direction
    | marker='.' - default marker for stipples
    | edegecolors='k' - outline colour
    | alpha=1.0 - transparency setting - default is off
    | ylog=False - set to True if a log pressure stipple plot
    |              is required
    | zorder=2 - plotting order
    |
    :Returns:
       None
    |
    """

    if plotvars.plot_type not in [1, 2, 3]:
        errstr = (
            "\n stipple error - only X-Y, X-Z and Y-Z \n"
            "stipple supported at the present time\n"
            "Please raise a feature request if you see this error.\n"
        )
        raise Warning(errstr)

    # Extract required data for contouring
    # If a cf-python field
    if isinstance(f, cf.Field):
        colorbar_title = ""
        (
            field,
            xpts,
            ypts,
            ptype,
            colorbar_title,
            xlabel,
            ylabel,
            xpole,
            ypole,
        ) = utility.cf_data_assign(f, colorbar_title, proj=plotvars.proj)
    elif isinstance(f, cf.FieldList):
        raise TypeError("Can't plot a field list")
    else:
        field = f  # field data passed in as f
        _check_data(field, x, y)
        xpts = x
        ypts = y

    if plotvars.plot_type == 1:
        # Cylindrical projection
        # Add cyclic information if missing.
        lonrange = np.nanmax(xpts) - np.nanmin(xpts)
        if lonrange < 360:
            # field, xpts = cartopy_util.add_cyclic_point(field, xpts)
            field, xpts = utility.add_cyclic(field, xpts)

        # if plotvars.proj == 'cyl':
        if plotvars.proj in ["cyl", "robin", "merc", "ortho", "moll"]:
            # Calculate interpolation points
            xnew, ynew = utility.stipple_points(
                xmin=np.nanmin(xpts),
                xmax=np.nanmax(xpts),
                ymin=np.nanmin(ypts),
                ymax=np.nanmax(ypts),
                pts=pts,
                stype=2,
            )

            # Calculate points in map space
            xnew_map = xnew
            ynew_map = ynew

        if plotvars.proj == "npstere" or plotvars.proj == "spstere":
            # Calculate interpolation points
            xnew, ynew, xnew_map, ynew_map = utility.polar_regular_grid(
                pts=pts,
                proj=plotvars.proj,
                boundinglat=plotvars.boundinglat,
                lon_0=plotvars.lon_0,
            )
            # Convert longitudes to be 0 to 360
            # negative longitudes are incorrectly regridded in polar
            # stereographic projection
            xnew = np.mod(xnew + 360.0, 360.0)

    if plotvars.plot_type >= 2 and plotvars.plot_type <= 3:

        # Flip data if a lat-height plot and lats start at the north pole
        if plotvars.plot_type == 2:
            if xpts[0] > xpts[-1]:
                xpts = xpts[::-1]
                field = np.fliplr(field)

        # Calculate interpolation points
        ymin = np.nanmin(ypts)
        ymax = np.nanmax(ypts)
        if ylog:
            ymin = np.log10(ymin)
            ymax = np.log10(ymax)

        xnew, ynew = utility.stipple_points(
            xmin=np.nanmin(xpts),
            xmax=np.nanmax(xpts),
            ymin=ymin,
            ymax=ymax,
            pts=pts,
            stype=2,
        )

        if ylog:
            ynew = 10**ynew

    # Get values at the new points
    vals = utility.regrid(f=field, x=xpts, y=ypts, xnew=xnew, ynew=ynew)

    # Work out which of the points are valid
    valid_points = np.array([], dtype="int64")
    for i in np.arange(np.size(vals)):
        if vals[i] >= min and vals[i] <= max:
            valid_points = np.append(valid_points, i)

    if plotvars.plot_type == 1:
        proj = ccrs.PlateCarree()

        if np.size(valid_points) > 0:
            plotvars.mymap.scatter(
                xnew[valid_points],
                ynew[valid_points],
                s=size,
                c=color,
                marker=marker,
                edgecolors=edgecolors,
                alpha=alpha,
                transform=proj,
                zorder=zorder,
            )

    if plotvars.plot_type >= 2 and plotvars.plot_type <= 3:
        plotvars.plot.scatter(
            xnew[valid_points],
            ynew[valid_points],
            s=size,
            c=color,
            marker=marker,
            edgecolors=edgecolors,
            alpha=alpha,
            zorder=zorder,
        )
