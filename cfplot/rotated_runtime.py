"""Rotated-pole (ptype 6) rendering and grid axes helpers.

This module encapsulates rotated-latitude-longitude coordinate system
rendering, including continent drawing via shapefile, rotated transforms,
and index-space grid line and axis label placement.
"""

from __future__ import annotations

from typing import Any

import cartopy.crs as ccrs
import numpy as np

from . import utility
from .blockfill import _bfill
from .colorbar import cbar
from .layout_runtime import apply_axes, ensure_xy_viewport, set_plot_limits
from .map_runtime import MapSet, _apply_map_title, _apply_map_features
from .state import plotvars


def _rotated_vloc(
    *, lons: np.ndarray, lats: np.ndarray, xvec: np.ndarray, yvec: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Map rotated-grid lon/lat points into plot coordinates.

    This mirrors the legacy location helper but uses safer index lookup so
    empty intersections do not raise during rotated projection plotting.
    """
    if any(val is None for val in [xvec, yvec, lons, lats]):
        errstr = (
            "\nvloc error\n"
            "xvec, yvec, lons, lats all need to be passed to vloc to\n"
            "generate a set of location points\n"
        )
        raise Warning(errstr)

    xvec = np.asarray(xvec, dtype=float).copy()
    yvec = np.asarray(yvec, dtype=float).copy()
    lons = np.asarray(lons, dtype=float).copy()
    lats = np.asarray(lats, dtype=float).copy()

    xarr = np.zeros(np.size(lons))
    yarr = np.zeros(np.size(lats))

    for i in np.arange(np.size(xvec)):
        xvec[i] = ((xvec[i] + 180) % 360) - 180
    for i in np.arange(np.size(lons)):
        lons[i] = ((lons[i] + 180) % 360) - 180

    if np.nanmax(xvec) > 150:
        for i in np.arange(np.size(xvec)):
            xvec[i] = (xvec[i] + 360.0) % 360.0
        pts = np.where(xvec < 0.0)
        xvec[pts] = xvec[pts] + 360.0
        for i in np.arange(np.size(lons)):
            lons[i] = (lons[i] + 360.0) % 360.0
        pts = np.where(lons < 0.0)
        lons[pts] = lons[pts] + 360.0

    for i in np.arange(np.size(lons)):
        if (lons[i] < np.min(xvec)) or (lons[i] > np.max(xvec)):
            xarr[i] = np.nan
        else:
            xpt = int(np.searchsorted(xvec, lons[i], side="right") - 1)
            xpt = max(0, min(xpt, np.size(xvec) - 2))
            xarr[i] = xpt + (lons[i] - xvec[xpt]) / (xvec[xpt + 1] - xvec[xpt])

        if (lats[i] < np.min(yvec)) or (lats[i] > np.max(yvec)):
            yarr[i] = np.nan
        else:
            ypt = int(np.searchsorted(yvec, lats[i], side="right") - 1)
            ypt = max(0, min(ypt, np.size(yvec) - 2))
            yarr[i] = ypt + (lats[i] - yvec[ypt]) / (yvec[ypt + 1] - yvec[ypt])

    return (xarr, yarr)


def _render_rotated_grid_axes(
    *,
    xpole: float,
    ypole: float,
    xvec: np.ndarray,
    yvec: np.ndarray,
    xticks: Any = None,
    xticklabels: Any = None,
    yticks: Any = None,
    yticklabels: Any = None,
    axes: bool = True,
    xaxis: bool = True,
    yaxis: bool = True,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> None:
    """Draw rotated-grid axes and optional graticule labels."""
    import matplotlib.lines

    spacing = plotvars.rotated_grid_spacing
    degspacing = plotvars.rotated_deg_spacing
    continents = plotvars.rotated_continents
    grid = plotvars.rotated_grid
    labels = plotvars.rotated_labels
    grid_thickness = plotvars.rotated_grid_thickness

    yvec = np.asarray(yvec)
    xvec = np.asarray(xvec)
    if yvec[0] > yvec[np.size(yvec) - 1]:
        yvec = yvec[::-1]

    set_plot_limits(
        xmin=0,
        xmax=float(np.size(xvec) - 1),
        ymin=0,
        ymax=float(np.size(yvec) - 1),
        ylog=False,
        user_gset=0,
    )

    # Rotated-grid labels are drawn manually as text; hide the base
    # index-space ticks/labels to avoid a duplicate numeric axis.
    plotvars.plot.set_xticks([])
    plotvars.plot.set_yticks([])
    plotvars.plot.tick_params(
        bottom=False,
        top=False,
        left=False,
        right=False,
        labelbottom=False,
        labeltop=False,
        labelleft=False,
        labelright=False,
    )

    if continents:
        import cartopy.io.shapereader as shpreader
        import shapefile

        shpfilename = shpreader.natural_earth(
            resolution=plotvars.resolution,
            category="physical",
            name="coastline",
        )
        reader = shapefile.Reader(shpfilename)
        shapes = [s.points for s in reader.shapes()]
        for shape in shapes:
            lons, lats = list(zip(*shape))
            lons = np.array(lons)
            lats = np.array(lats)
            rotated_transform = ccrs.RotatedPole(
                pole_latitude=ypole, pole_longitude=xpole
            )
            points = rotated_transform.transform_points(
                ccrs.PlateCarree(), lons, lats
            )
            xout = np.array(points)[:, 0]
            yout = np.array(points)[:, 1]
            xpts, ypts = _rotated_vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)
            plotvars.plot.plot(
                xpts,
                ypts,
                linewidth=plotvars.continent_thickness or 1.5,
                color=plotvars.continent_color or "k",
            )

    if xticks is None:
        lons = -180 + np.arange(360 / spacing + 1) * spacing
    else:
        lons = xticks
    if yticks is None:
        lats = -90 + np.arange(180 / spacing + 1) * spacing
    else:
        lats = yticks

    xlim = plotvars.plot.get_xlim()
    spacing_x = (xlim[1] - xlim[0]) / 20
    ylim = plotvars.plot.get_ylim()
    spacing_y = (ylim[1] - ylim[0]) / 20
    spacing = min(spacing_x, spacing_y)

    rotated_transform = ccrs.RotatedPole(pole_latitude=ypole, pole_longitude=xpole)

    if axes:
        if xaxis:
            for val in np.arange(np.size(lons)):
                ipts = max(2, int(179.0 / degspacing))
                lona = np.zeros(ipts) + lons[val]
                lata = -90 + np.arange(ipts) * degspacing
                points = rotated_transform.transform_points(
                    ccrs.PlateCarree(), lona, lata
                )
                xout = np.array(points)[:, 0]
                yout = np.array(points)[:, 1]
                xpts, ypts = _rotated_vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)
                if grid:
                    plotvars.plot.plot(
                        xpts, ypts, ":", linewidth=grid_thickness, color="k"
                    )

                if labels and np.size(ypts[5:]) > np.sum(np.isnan(ypts[5:])):
                    ymin = np.nanmin(ypts[5:])
                    loc = np.where(ypts == ymin)[0]
                    if np.size(loc) > 1:
                        loc = loc[1]
                    if loc > 0 and np.isfinite(xpts[loc]):
                        xpos = float(np.asarray(xpts[loc]).reshape(-1)[0])
                        line = matplotlib.lines.Line2D(
                            [xpos, xpos], [0, -spacing / 2], color="k"
                        )
                        plotvars.plot.add_line(line)
                        line.set_clip_on(False)
                        xticklabel = (
                            utility.mapaxis(lons[val], lons[val], axis_type=1, degsym=plotvars.degsym)[1][0]
                            if xticklabels is None
                            else xticklabels[val]
                        )
                        plotvars.plot.text(
                            xpos,
                            -spacing,
                            xticklabel,
                            horizontalalignment="center",
                            verticalalignment="top",
                            fontsize=plotvars.text_fontsize,
                            fontweight=plotvars.text_fontweight,
                        )

        if yaxis:
            for val in np.arange(np.size(lats)):
                ipts = max(2, int(359.0 / degspacing))
                lata = np.zeros(ipts) + lats[val]
                lona = -180.0 + np.arange(ipts) * degspacing
                points = rotated_transform.transform_points(
                    ccrs.PlateCarree(), lona, lata
                )
                xout = np.array(points)[:, 0]
                yout = np.array(points)[:, 1]
                xpts, ypts = _rotated_vloc(lons=xout, lats=yout, xvec=xvec, yvec=yvec)

                if grid:
                    plotvars.plot.plot(
                        xpts, ypts, ":", linewidth=grid_thickness, color="k"
                    )

                if labels and np.size(xpts[5:]) > np.sum(np.isnan(xpts[5:])):
                    xmin = np.nanmin(xpts[5:])
                    loc = np.where(xpts == xmin)[0]
                    if np.size(loc) == 1 and loc > 0 and np.isfinite(ypts[loc]):
                        ypos = float(np.asarray(ypts[loc]).reshape(-1)[0])
                        line = matplotlib.lines.Line2D(
                            [0, -spacing / 2], [ypos, ypos], color="k"
                        )
                        plotvars.plot.add_line(line)
                        line.set_clip_on(False)
                        yticklabel = (
                            utility.mapaxis(lats[val], lats[val], axis_type=2, degsym=plotvars.degsym)[1][0]
                            if yticklabels is None
                            else yticklabels[val]
                        )
                        plotvars.plot.text(
                            -spacing,
                            ypos,
                            yticklabel,
                            horizontalalignment="right",
                            verticalalignment="center",
                            fontsize=plotvars.text_fontsize,
                            fontweight=plotvars.text_fontweight,
                        )

    if xlabel:
        plotvars.plot.set_xlabel(
            xlabel,
            fontsize=plotvars.axis_label_fontsize,
            fontweight=plotvars.axis_label_fontweight,
        )
    if ylabel:
        plotvars.plot.set_ylabel(
            ylabel,
            fontsize=plotvars.axis_label_fontsize,
            fontweight=plotvars.axis_label_fontweight,
        )


def _render_ptype6_rotated_pole(
    *,
    f: Any,
    data: Any,
    kwargs: dict[str, Any],
    clevs: np.ndarray,
    cs: Any,
    cbar_labels: list[str] | Any,
    colorbar_title: str,
    fill: bool,
    lines: bool,
    blockfill: bool,
    line_labels: bool,
    zero_thick: bool | int,
    colors: Any,
    linewidths: Any,
    linestyles: Any,
    alpha: float,
    zorder: int,
    finalize_callback: Any,
) -> bool:
    """Render ptype 6 (rotated pole) for cylindrical transformed-map mode."""

    if data.x is None or data.y is None or data.levels is None:
        return False

    if plotvars.user_plot == 0:
        ensure_xy_viewport()

    rotated_pole = f.ref("grid_mapping_name:rotated_latitude_longitude", default=None)
    xpole = ypole = None
    transform = None
    if rotated_pole:
        xpole = utility.to_float_or_none(rotated_pole.get("grid_north_pole_longitude"))
        ypole = utility.to_float_or_none(rotated_pole.get("grid_north_pole_latitude"))

    if plotvars.proj == "rotated":
        xpts = np.arange(np.size(data.x))
        ypts = np.arange(np.size(data.y))
        plotargs: dict[str, Any] = {}
        plot = plotvars.plot
        set_plot_limits(
            xmin=0,
            xmax=float(np.size(xpts) - 1),
            ymin=0,
            ymax=float(np.size(ypts) - 1),
            ylog=False,
            user_gset=plotvars.user_gset,
        )
    elif plotvars.proj == "cyl":
        xpts = data.x
        ypts = data.y

        if not rotated_pole:
            return False
        if xpole is None or ypole is None:
            return False

        transform = ccrs.RotatedPole(pole_latitude=ypole, pole_longitude=xpole)

        map_runtime = MapSet(plotvars)
        if plotvars.user_mapset != 1:
            if np.ndim(xpts) == 1:
                lonpts, latpts = np.meshgrid(xpts, ypts)
            else:
                lonpts = xpts
                latpts = ypts
            points = ccrs.PlateCarree().transform_points(
                transform, lonpts.flatten(), latpts.flatten()
            )
            lons = np.array(points)[:, 0]
            lats = np.array(points)[:, 1]

            map_runtime.configure(
                lonmin=float(np.min(lons)),
                lonmax=float(np.max(lons)),
                latmin=float(np.min(lats)),
                latmax=float(np.max(lats)),
                user_mapset=0,
                resolution=plotvars.resolution,
            )
        map_runtime.ensure_map_axes()

        plotargs = {"transform": transform}
        plot = plotvars.mymap
    else:
        return False

    frame_artists: list[Any] = []

    if fill:
        cmap = cs.get_cmap()
        cset = plot.contourf(
            xpts,
            ypts,
            data.field * data.fmult,
            clevs,
            extend=plotvars.levels_extend,
            cmap=cmap,
            norm=plotvars.norm,
            alpha=alpha,
            zorder=zorder,
            **plotargs,
        )
        if hasattr(cset, "collections"):
            frame_artists.extend(list(cset.collections))

    if blockfill:
        _bfill(
            f=data.field * data.fmult,
            x=xpts,
            y=ypts,
            clevs=clevs,
            bound=0,
            alpha=alpha,
            fast=kwargs.get("blockfill_fast", None),
            zorder=zorder,
            transform=transform,
        )

    if lines:
        cs_lines = plot.contour(
            xpts,
            ypts,
            data.field * data.fmult,
            clevs,
            colors=colors,
            linewidths=linewidths,
            linestyles=linestyles,
            zorder=zorder,
            **plotargs,
        )
        if hasattr(cs_lines, "collections"):
            frame_artists.extend(list(cs_lines.collections))
        if line_labels and not isinstance(clevs, int):
            nd = utility.ndecs(clevs)
            fmt = "%d"
            if nd != 0:
                fmt = "%1." + str(nd) + "f"
            plot.clabel(
                cs_lines,
                fmt=fmt,
                colors=colors,
                zorder=zorder,
                fontsize=plotvars.text_fontsize,
            )
        if zero_thick:
            cs0 = plot.contour(
                xpts,
                ypts,
                data.field * data.fmult,
                [-1e-32, 0],
                colors=colors,
                linewidths=zero_thick,
                linestyles=linestyles,
                alpha=alpha,
                zorder=zorder,
                **plotargs,
            )
            if hasattr(cs0, "collections"):
                frame_artists.extend(list(cs0.collections))

    if kwargs.get("axes", True):
        if plotvars.proj == "cyl":
            apply_axes(
                plot_type=1,
                xticks=kwargs.get("xticks", None),
                yticks=kwargs.get("yticks", None),
                xlabel=kwargs.get("xlabel", None),
                ylabel=kwargs.get("ylabel", None),
                xticklabels=kwargs.get("xticklabels", None),
                yticklabels=kwargs.get("yticklabels", None),
            )
        else:
            _render_rotated_grid_axes(
                xpole=xpole,
                ypole=ypole,
                xvec=data.x,
                yvec=data.y,
                xticks=kwargs.get("xticks", None),
                xticklabels=kwargs.get("xticklabels", None),
                yticks=kwargs.get("yticks", None),
                yticklabels=kwargs.get("yticklabels", None),
                axes=True,
                xaxis=kwargs.get("xaxis", True),
                yaxis=kwargs.get("yaxis", True),
                xlabel=kwargs.get("xlabel", None),
                ylabel=kwargs.get("ylabel", None),
            )

    if plotvars.proj == "cyl" and plotvars.mymap is not None:
        _apply_map_features(
            mymap=plotvars.mymap,
            continent_color=plotvars.continent_color or "k",
            continent_thickness=plotvars.continent_thickness or 1.5,
            continent_linestyle=plotvars.continent_linestyle or "solid",
            kwargs=kwargs,
        )

        if kwargs.get("grid", plotvars.grid):
            MapSet(plotvars).draw_grid()

    if kwargs.get("colorbar", True) and (fill or blockfill):
        cbar(
            labels=cbar_labels,
            orientation=kwargs.get("colorbar_orientation", None) or "horizontal",
            position=kwargs.get("colorbar_position", None),
            shrink=kwargs.get("colorbar_shrink", None),
            title=colorbar_title,
            fontsize=kwargs.get("colorbar_fontsize", None),
            fontweight=kwargs.get("colorbar_fontweight", None),
            text_up_down=kwargs.get("colorbar_text_up_down", False),
            text_down_up=kwargs.get("colorbar_text_down_up", False),
            drawedges=kwargs.get("colorbar_drawedges", True),
            fraction=kwargs.get("colorbar_fraction", None),
            thick=kwargs.get("colorbar_thick", None),
            levs=clevs,
            anchor=kwargs.get("colorbar_anchor", None),
            verbose=kwargs.get("verbose", None),
        )

    title = kwargs.get("title", "") or ""
    if title != "":
        _apply_map_title(
            mymap=plotvars.mymap,
            title=title,
            proj=plotvars.proj,
            boundinglat=plotvars.boundinglat,
            lon_0=plotvars.lon_0,
            lonmin=plotvars.lonmin,
            lonmax=plotvars.lonmax,
            latmin=plotvars.latmin,
            latmax=plotvars.latmax,
            title_fontsize=plotvars.title_fontsize,
            title_fontweight=plotvars.title_fontweight,
        )

    finalize_callback()

    plotvars._contour_animation_artists = frame_artists
    return True
