"""Block-fill rendering helpers for contour workflows.

This module hosts contour-specific block-fill logic used by the refactored
contour path so it does not depend on cfplot.py internals.
"""

from __future__ import annotations

from copy import deepcopy

import cartopy.crs as ccrs
import cf
import matplotlib.colors
import matplotlib.patches as mpatches
import numpy as np
import shapely.geometry as sgeom
from matplotlib.collections import PolyCollection

from .colour import get_colour_scale_map
from . import utility
from .state import plotvars


def _bfill(
    f=None,
    x=None,
    y=None,
    clevs=False,
    bound=False,
    alpha=1.0,
    single_fill_color=None,
    white=True,
    zorder=4,
    fast=None,
    transform=False,
    orca=False,
):
    """Block-fill a field with coloured rectangles."""
    _ = (orca,)

    lonlat = plotvars.plot_type == 1

    if single_fill_color is not None:
        white = False

    two_d = False
    if not isinstance(f, cf.Field):
        if np.ndim(x) == 2 and np.ndim(x) == 2:
            two_d = True

    plotargs = {}
    if lonlat:
        plotargs = {"transform": ccrs.PlateCarree()}

    if isinstance(f, cf.Field):
        field = f.array
    else:
        field = f

    levels = np.array(deepcopy(clevs)).astype("float")

    if single_fill_color is None:
        colmap = get_colour_scale_map()
        cmap = matplotlib.colors.ListedColormap(colmap)
        fill_colors = list(colmap)
        if plotvars.levels_extend in ["min", "both"]:
            cmap.set_under(plotvars.cs[0])
        if plotvars.levels_extend in ["max", "both"]:
            cmap.set_over(plotvars.cs[-1])

        under_index = None
        over_index = None
        if plotvars.levels_extend in ["min", "both"]:
            under_index = len(fill_colors)
            fill_colors.append(plotvars.cs[0])
        if plotvars.levels_extend in ["max", "both"]:
            over_index = len(fill_colors)
            fill_colors.append(plotvars.cs[-1])
    else:
        cols = single_fill_color
        cmap = matplotlib.colors.ListedColormap(cols)
        fill_colors = None
        under_index = None
        over_index = None

    colarr = np.zeros([np.shape(field)[0], np.shape(field)[1]]) - 1
    for i in np.arange(np.size(levels) - 1):
        lev = levels[i]
        pts = np.where(np.logical_and(field >= lev, field < levels[i + 1]))
        colarr[pts] = int(i)

    # Keep out-of-range values away from "white" so it is reserved for
    # actual missing/masked values only.
    if np.size(levels) >= 2:
        pts = np.where(field < levels[0])
        if np.size(pts) > 0:
            if under_index is not None:
                colarr[pts] = under_index
            else:
                colarr[pts] = 0

        pts = np.where(field >= levels[-1])
        if np.size(pts) > 0:
            if over_index is not None:
                colarr[pts] = over_index
            else:
                colarr[pts] = np.size(levels) - 2

    if isinstance(field, np.ma.MaskedArray):
        pts = np.ma.where(field.mask)
        if np.size(pts) > 0:
            colarr[pts] = -1

    norm = matplotlib.colors.BoundaryNorm(levels, cmap.N)

    if isinstance(f, cf.Field):
        if f.ref("grid_mapping_name:transverse_mercator", default=False):
            lonlat = True

            ref = f.ref("grid_mapping_name:transverse_mercator")
            false_easting = ref["false_easting"]
            false_northing = ref["false_northing"]
            central_longitude = ref["longitude_of_central_meridian"]
            central_latitude = ref["latitude_of_projection_origin"]
            scale_factor = ref["scale_factor_at_central_meridian"]

            transform = ccrs.TransverseMercator(
                false_easting=false_easting,
                false_northing=false_northing,
                central_longitude=central_longitude,
                central_latitude=central_latitude,
                scale_factor=scale_factor,
            )

            xpts = np.append(
                f.dim("X").bounds.array[:, 0], f.dim("X").bounds.array[-1, 1]
            )
            ypts = np.append(
                f.dim("Y").bounds.array[:, 0], f.dim("Y").bounds.array[-1, 1]
            )
            field = np.squeeze(f.array)
            plotargs = {"transform": transform}

    else:
        if two_d is False:
            if bound:
                xpts = x
                ypts = y
            else:
                xpts = x[0] - (x[1] - x[0]) / 2.0
                for ix in np.arange(np.size(x) - 1):
                    xpts = np.append(xpts, x[ix] + (x[ix + 1] - x[ix]) / 2.0)
                xpts = np.append(xpts, x[ix + 1] + (x[ix + 1] - x[ix]) / 2.0)

                ypts = y[0] - (y[1] - y[0]) / 2.0
                for iy in np.arange(np.size(y) - 1):
                    ypts = np.append(ypts, y[iy] + (y[iy + 1] - y[iy]) / 2.0)
                ypts = np.append(ypts, y[iy + 1] + (y[iy + 1] - y[iy]) / 2.0)

            if lonlat:
                upper_bound = ypts[-1]

                xpts = xpts[0:-1]
                ypts = ypts[0:-1]

                if plotvars.lonmin < np.nanmin(xpts):
                    xpts = xpts - 360
                if plotvars.lonmin > np.nanmax(xpts):
                    xpts = xpts + 360

                lonrange = np.nanmax(xpts) - np.nanmin(xpts)
                if lonrange < 360 and lonrange > 350:
                    field, xpts = utility.add_cyclic(field, xpts)

                right_bound = xpts[-1] + (xpts[-1] - xpts[-2])

                xpts = np.append(xpts, right_bound)
                ypts = np.append(ypts, upper_bound)

        if two_d:
            if fast:
                xpts = x
                ypts = y
            else:
                nx = np.shape(x)[1]
                ny = np.shape(x)[0]

                for ix in np.arange(nx):
                    for iy in np.arange(ny):
                        if ix < nx - 2:
                            xdiff = (x[iy, ix + 1] - x[iy, ix]) / 2
                        else:
                            xdiff = (x[iy, ix] - x[iy, ix - 1]) / 2

                        if iy < ny - 2:
                            ydiff = (y[iy + 1, ix] - y[iy, ix]) / 2
                        else:
                            ydiff = (y[iy, ix] - y[iy - 1, ix]) / 2

                        xpts = [
                            x[iy, ix] - xdiff,
                            x[iy, ix] + xdiff,
                            x[iy, ix] + xdiff,
                            x[iy, ix] - xdiff,
                            x[iy, ix] - xdiff,
                        ]
                        ypts = [
                            y[iy, ix] - ydiff,
                            y[iy, ix] - ydiff,
                            y[iy, ix] + ydiff,
                            y[iy, ix] + ydiff,
                            y[iy, ix] - ydiff,
                        ]

                        plotvars.mymap.add_patch(
                            mpatches.Polygon(
                                [
                                    [xpts[0], ypts[0]],
                                    [xpts[1], ypts[1]],
                                    [xpts[2], ypts[2]],
                                    [xpts[3], ypts[3]],
                                    [xpts[4], ypts[4]],
                                ],
                                facecolor=fill_colors[int(colarr[iy, ix])],
                                zorder=zorder,
                                transform=ccrs.PlateCarree(),
                            )
                        )

                return

    if plotvars.proj == "npstere":
        pts = np.where(ypts < plotvars.boundinglat)
        if np.size(pts) > 0:
            ypts[pts] = plotvars.boundinglat
        pts = np.where(ypts > 90.0)
        if np.size(pts) > 0:
            ypts[pts] = 90.0

    if plotvars.proj == "spstere":
        pts = np.where(ypts > plotvars.boundinglat)
        if np.size(pts) > 0:
            ypts[pts] = plotvars.boundinglat
        pts = np.where(ypts < -90.0)
        if np.size(pts) > 0:
            ypts[pts] = -90.0

    if transform:
        lonlat = True
    else:
        transform = ccrs.PlateCarree()

    if fast:
        if isinstance(clevs, int):
            norm = False

        if two_d:
            fixed_x = x.copy()
            for i, start in enumerate(np.argmax(np.abs(np.diff(x)) > 180, axis=1)):
                fixed_x[i, start + 1 :] += 360
            plotvars.image = plotvars.mymap.pcolormesh(
                fixed_x, y, field, cmap=cmap, transform=transform, norm=norm
            )

        else:
            if lonlat:
                for offset in [0, 360.0]:
                    if isinstance(clevs, int):
                        plotvars.image = plotvars.mymap.pcolormesh(
                            xpts + offset,
                            ypts,
                            field,
                            transform=transform,
                            cmap=cmap,
                        )
                    else:
                        plotvars.image = plotvars.mymap.pcolormesh(
                            xpts + offset,
                            ypts,
                            field,
                            transform=transform,
                            cmap=cmap,
                            norm=norm,
                        )

            else:
                if isinstance(clevs, int):
                    plotvars.image = plotvars.plot.pcolormesh(xpts, ypts, field, cmap=cmap)
                else:
                    plotvars.image = plotvars.plot.pcolormesh(
                        xpts, ypts, field, cmap=cmap, norm=norm
                    )

    else:
        if plotvars.plot_type == 1 and plotvars.proj != "cyl":
            for i in np.unique(colarr[colarr >= 0]).astype(int):
                allverts = []
                xy_stack = np.column_stack(np.where(colarr == i))

                for pt in np.arange(np.shape(xy_stack)[0]):
                    ix = xy_stack[pt][1]
                    iy = xy_stack[pt][0]
                    lons = [xpts[ix], xpts[ix + 1], xpts[ix + 1], xpts[ix], xpts[ix]]
                    lats = [ypts[iy], ypts[iy], ypts[iy + 1], ypts[iy + 1], ypts[iy]]

                    verts = [
                        (lons[0], lats[0]),
                        (lons[1], lats[1]),
                        (lons[2], lats[2]),
                        (lons[3], lats[3]),
                        (lons[4], lats[4]),
                    ]

                    allverts.append(verts)

                if single_fill_color is None:
                    color = fill_colors[i]
                else:
                    color = single_fill_color
                coll = PolyCollection(
                    allverts,
                    facecolor=color,
                    edgecolors=color,
                    alpha=alpha,
                    zorder=zorder,
                    **plotargs,
                )

                if lonlat:
                    plotvars.mymap.add_collection(coll)
                else:
                    plotvars.plot.add_collection(coll)
        else:
            for i in np.unique(colarr[colarr >= 0]).astype(int):
                allverts = []
                xy_stack = np.column_stack(np.where(colarr == i))
                for pt in np.arange(np.shape(xy_stack)[0]):
                    ix = xy_stack[pt][1]
                    iy = xy_stack[pt][0]
                    verts = [
                        (xpts[ix], ypts[iy]),
                        (xpts[ix + 1], ypts[iy]),
                        (xpts[ix + 1], ypts[iy + 1]),
                        (xpts[ix], ypts[iy + 1]),
                        (xpts[ix], ypts[iy]),
                    ]

                    allverts.append(verts)

                if single_fill_color is None:
                    color = fill_colors[i]
                else:
                    color = single_fill_color

                coll = PolyCollection(
                    allverts,
                    facecolor=color,
                    edgecolors=color,
                    alpha=alpha,
                    zorder=zorder,
                    **plotargs,
                )

                if lonlat:
                    plotvars.mymap.add_collection(coll)
                else:
                    plotvars.plot.add_collection(coll)

        if white:
            allverts = []
            xy_stack = np.column_stack(np.where(colarr == -1))
            for pt in np.arange(np.shape(xy_stack)[0]):
                ix = xy_stack[pt][1]
                iy = xy_stack[pt][0]

                verts = [
                    (xpts[ix], ypts[iy]),
                    (xpts[ix + 1], ypts[iy]),
                    (xpts[ix + 1], ypts[iy + 1]),
                    (xpts[ix], ypts[iy + 1]),
                    (xpts[ix], ypts[iy]),
                ]

                allverts.append(verts)

            coll = PolyCollection(
                allverts,
                facecolor="#ffffff",
                edgecolors="#ffffff",
                alpha=alpha,
                zorder=zorder,
                **plotargs,
            )

            if lonlat:
                plotvars.mymap.add_collection(coll)
            else:
                plotvars.plot.add_collection(coll)


def _bfill_ugrid(
    f=None,
    face_lons=None,
    face_lats=None,
    face_connectivity=None,
    clevs=None,
    alpha=None,
    zorder=None,
):
    """
    | Block fill a irregular field with colour rectangles.
    | This is an internal routine and is not generally used by the user.
    |
    | f=None - field
    | face_lons=None - longitude points for face vertices
    | face_lats=None - latitude points for face verticies
    | face_connectivity=None - connectivity for face verticies
    | clevs=None - levels for filling
    | lonlat=False - lonlat data
    | bound=False - x and y are cf data boundaries
    | alpha=alpha - transparency setting 0 to 1
    | zorder=None - plotting order
    |
     :Returns:
       None
    |
    """

    # Colour faces according to value.
    cols = ["#000000" for _ in range(len(face_connectivity))]

    levs = deepcopy(np.array(clevs))

    if plotvars.levels_extend == "min" or plotvars.levels_extend == "both":
        levs = np.concatenate([[-1e20], levs])
    ilevs_max = np.size(levs)
    if plotvars.levels_extend == "max" or plotvars.levels_extend == "both":
        levs = np.concatenate([levs, [1e20]])
    else:
        ilevs_max = ilevs_max - 1

    for ilev in np.arange(ilevs_max):
        lev = levs[ilev]
        col = plotvars.cs[ilev]
        pts = np.where(f.squeeze() >= lev)[0]

        if len(pts) > 0 and np.min(pts) >= 0:
            for val in np.arange(np.size(pts)):
                pt = pts[val]
                cols[pt] = col

    plotargs = {"transform": ccrs.PlateCarree()}

    coords_all = []

    nfaces = np.shape(face_connectivity)[0]
    for iface in np.arange(nfaces):
        lons = np.array(face_lons[iface, :], copy=True)
        lats = np.array(face_lats[iface, :], copy=True)

        # Wrapping in longitude.
        if (np.max(lons) - np.min(lons)) > 100:
            if np.max(lons) > 180:
                for j in np.arange(len(lons)):
                    lons[j] = (lons[j] + 180) % 360 - 180
            else:
                for j in np.arange(len(lons)):
                    lons[j] = lons[j] % 360

        nverts = len(lons)

        # Add extra vertices if any of the points are at the north or south pole.
        if np.max(lats) == 90 or np.min(lats) == -90:
            geom = sgeom.Polygon([(lons[k], lats[k]) for k in np.arange(nverts)])
            geom_cyl = ccrs.PlateCarree().project_geometry(geom, ccrs.Geodetic())

            # New method for shapely 2.0 +
            poly_mapped = sgeom.mapping(geom_cyl.geoms[0])
            coords = list(poly_mapped["coordinates"][0])
        else:
            coords = [(lons[k], lats[k]) for k in np.arange(nverts)]

        coords_all.append(coords)

    plotvars.mymap.add_collection(
        PolyCollection(
            coords_all,
            facecolors=cols,
            edgecolors=None,
            alpha=alpha,
            zorder=zorder,
            **plotargs,
        )
    )
