"""Contour-owned map setup/runtime helpers.

This module contains the map-state and map-axes operations used by the
refactored contour renderer so it no longer needs map setup from cfplot.py.
"""

from __future__ import annotations

from typing import Any

import cartopy.crs as ccrs
import numpy as np

from . import utility
from .state import plotvars


def _apply_map_title(
    *,
    mymap: Any,
    title: str,
    proj: str,
    boundinglat: float,
    lon_0: float,
    lonmin: float,
    lonmax: float,
    latmin: float,
    latmax: float,
    title_fontsize: int,
    title_fontweight: str,
) -> Any:
    """Draw a title on a map axes at the geographically correct position."""
    polar_range = 90 - abs(boundinglat)
    myprojs = ["cyl", "robin", "moll", "merc"]

    if proj in myprojs:
        lon_mid = lonmin + (lonmax - lonmin) / 2.0
        projs = [ccrs.PlateCarree, ccrs.Robinson, ccrs.Mollweide, ccrs.Mercator]
        myind = myprojs.index(proj)
        map_proj = projs[myind](central_longitude=lon_mid)
        xpt, ypt = map_proj.transform_point(lon_mid, latmax, ccrs.PlateCarree())
        ypt = ypt + (latmax - latmin) / 40.0
    elif proj == "npstere":
        mylon = lon_0 + 180
        mylat = boundinglat - polar_range / 15.0
        map_proj = ccrs.NorthPolarStereo(central_longitude=lon_0)
        xpt, ypt = map_proj.transform_point(mylon, mylat, ccrs.PlateCarree())
    elif proj == "spstere":
        mylon = lon_0
        mylat = boundinglat + polar_range / 15.0
        map_proj = ccrs.SouthPolarStereo(central_longitude=lon_0)
        xpt, ypt = map_proj.transform_point(mylon, mylat, ccrs.PlateCarree())
    elif proj == "lcc":
        lon_mid = lonmin + (lonmax - lonmin) / 2.0
        lat_0 = 40
        if latmin <= 0 and latmax <= 0:
            lat_0 = 40
        map_proj = ccrs.LambertConformal(
            central_longitude=lon_0,
            central_latitude=lat_0,
            cutoff=latmin,
        )
        xpt, ypt = map_proj.transform_point(lon_mid, latmax, ccrs.PlateCarree())
    else:
        return None

    return mymap.text(
        xpt,
        ypt,
        title,
        va="bottom",
        ha="center",
        rotation="horizontal",
        rotation_mode="anchor",
        fontsize=title_fontsize,
        fontweight=title_fontweight,
    )


def _apply_dim_titles(
    *,
    plot: Any,
    mymap: Any,
    plot_type: int,
    proj: str,
    lonmin: float,
    lonmax: float,
    latmin: float,
    latmax: float,
    axis_label_fontsize: int,
    axis_label_fontweight: str,
    title: str | None = None,
    title2: str | None = None,
    title3: str | None = None,
) -> None:
    """Draw a set of dimension titles on the active contour axes."""
    this_plot = mymap if plot_type == 1 else plot

    left, bottom, width, height = this_plot.get_position().bounds
    valign = "bottom"

    if plot_type == 1 and proj != "cyl":
        left -= 0.1
        myx = 1.25
        myy = 1.0
        valign = "top"
        if title3 is None:
            myx = 1.05
    elif plot_type == 1 and proj == "cyl":
        lonrange = lonmax - lonmin
        latrange = latmax - latmin
        if (lonrange / latrange) > 1.5:
            myx = 0.0
            myy = 1.02
        elif (lonrange / latrange) > 1.2:
            myx = 0.0
            myy = 1.02
            height -= 0.015
        else:
            left -= 0.1
            myx = 1.05
            myy = 1.0
            width -= 0.1
            valign = "top"
    else:
        height -= 0.1
        myx = 0.0
        myy = 1.02

    if title3 is None:
        this_plot.set_position([left, bottom, width, height])

    xspacing = 0.3
    yspacing = 0.0
    if myx in (1.05, 1.25):
        xspacing = 0.0
        yspacing = 0.2

    if title is not None:
        this_plot.text(
            myx,
            myy,
            title,
            va=valign,
            ha="left",
            fontsize=axis_label_fontsize,
            fontweight=axis_label_fontweight,
            transform=this_plot.transAxes,
        )

    if title2 is not None:
        this_plot.text(
            myx + xspacing,
            myy - yspacing,
            title2,
            va=valign,
            ha="left",
            fontsize=axis_label_fontsize,
            fontweight=axis_label_fontweight,
            transform=this_plot.transAxes,
        )

    if title3 is not None:
        this_plot.text(
            myx + xspacing * 2,
            myy - yspacing * 2,
            title3,
            va=valign,
            ha="left",
            fontsize=axis_label_fontsize,
            fontweight=axis_label_fontweight,
            transform=this_plot.transAxes,
        )


class MapSet:
    """Stateful map setup for contour rendering."""

    def __init__(self, pvars=plotvars):
        self.plotvars = pvars

    def configure(
        self,
        *,
        lonmin: float | None = None,
        lonmax: float | None = None,
        latmin: float | None = None,
        latmax: float | None = None,
        proj: str = "cyl",
        boundinglat: float = 0,
        lon_0: float = 0,
        lat_0: float = 40,
        resolution: str = "110m",
        user_mapset: int = 1,
        aspect: str | float | None = None,
    ) -> None:
        """Set map plotting parameters in shared state."""
        pv = self.plotvars
        pv.resolution = resolution

        if (
            all(val is None for val in [lonmin, lonmax, latmin, latmax, aspect])
            and proj == "cyl"
        ):
            pv.lonmin = -180
            pv.lonmax = 180
            pv.latmin = -90
            pv.latmax = 90
            pv.proj = "cyl"
            pv.user_mapset = 0
            pv.aspect = "equal"
            pv.plot_xmin = None
            pv.plot_xmax = None
            pv.plot_ymin = None
            pv.plot_ymax = None
            return

        if aspect is None:
            aspect = "equal"
        pv.aspect = aspect

        if lonmin is None:
            lonmin = -180
        if lonmax is None:
            lonmax = 180
        if latmin is None:
            latmin = -80 if proj == "merc" else -90
        if latmax is None:
            latmax = 80 if proj == "merc" else 90

        if proj == "moll":
            lonmin = lon_0 - 180
            lonmax = lon_0 + 180

        pv.lonmin = lonmin
        pv.lonmax = lonmax
        pv.latmin = latmin
        pv.latmax = latmax
        pv.proj = proj
        pv.boundinglat = boundinglat
        pv.lon_0 = lon_0
        pv.lat_0 = lat_0
        pv.user_mapset = user_mapset

    def ensure_map_axes(self) -> None:
        """Create map axes in plotvars.mymap when not already present."""
        pv = self.plotvars
        if pv.mymap is not None:
            return

        if pv.plot is None:
            ensure_map_viewport()

        extent = True
        lonmin = pv.lonmin
        lonmax = pv.lonmax
        latmin = pv.latmin
        latmax = pv.latmax
        lon_diff = lonmax - lonmin
        lon_mid = lonmin + lon_diff / 2.0

        vproj = pv.proj

        if vproj in ("cyl", "merc") and lon_diff == 360.0:
            lonmax += 0.01

        if vproj == "cyl":
            proj = ccrs.PlateCarree(central_longitude=lon_mid)
        elif vproj == "merc":
            min_latitude = -80.0
            if lonmin > min_latitude:
                min_latitude = pv.lonmin
            max_latitude = 84.0
            if lonmax < max_latitude:
                max_latitude = pv.lonmax
            proj = ccrs.Mercator(
                central_longitude=pv.lon_0,
                min_latitude=min_latitude,
                max_latitude=max_latitude,
            )
        elif vproj == "npstere":
            proj = ccrs.NorthPolarStereo(central_longitude=pv.lon_0)
            lonmin = pv.lon_0 - 180
            lonmax = pv.lon_0 + 180.01
            latmin = pv.boundinglat
            latmax = 90
        elif vproj == "spstere":
            proj = ccrs.SouthPolarStereo(central_longitude=pv.lon_0)
            lonmin = pv.lon_0 - 180
            lonmax = pv.lon_0 + 180.01
            latmin = -90
            latmax = pv.boundinglat
        elif vproj == "ortho":
            proj = ccrs.Orthographic(
                central_longitude=pv.lon_0, central_latitude=pv.lat_0
            )
            lonmin = pv.lon_0 - 180.0
            lonmax = pv.lon_0 + 180.01
            extent = False
        elif vproj == "moll":
            proj = ccrs.Mollweide(central_longitude=pv.lon_0)
            lonmin = pv.lon_0 - 180.0
            lonmax = pv.lon_0 + 180.01
            extent = False
        elif vproj == "robin":
            proj = ccrs.Robinson(central_longitude=pv.lon_0)
        elif vproj == "lcc":
            lon_0 = lonmin + (lonmax - lonmin) / 2.0
            lat_0 = latmin + (latmax - latmin) / 2.0
            cutoff = -40 if lat_0 > 0 else 40
            standard_parallels = [33, 45]
            if latmin <= 0 and latmax <= 0:
                standard_parallels = [-45, -33]
            proj = ccrs.LambertConformal(
                central_longitude=lon_0,
                central_latitude=lat_0,
                cutoff=cutoff,
                standard_parallels=standard_parallels,
            )
        elif vproj == "rotated":
            proj = ccrs.PlateCarree(central_longitude=lon_mid)
        elif vproj == "OSGB":
            proj = ccrs.OSGB()
        elif vproj == "EuroPP":
            proj = ccrs.EuroPP()
        elif vproj == "UKCP":
            proj = ccrs.TransverseMercator()
        elif vproj == "TransverseMercator":
            proj = ccrs.TransverseMercator()
            lonmin = pv.lon_0 - 180.0
            lonmax = pv.lon_0 + 180.01
            extent = False
        elif vproj == "LambertCylindrical":
            proj = ccrs.LambertCylindrical()
        else:
            proj = ccrs.PlateCarree(central_longitude=lon_mid)

        if pv.plot_xmin:
            delta_x = pv.plot_xmax - pv.plot_xmin
            delta_y = pv.plot_ymax - pv.plot_ymin
            mymap = pv.master_plot.add_axes(
                [pv.plot_xmin, pv.plot_ymin, delta_x, delta_y], projection=proj
            )
        else:
            mymap = pv.master_plot.add_subplot(
                pv.rows, pv.columns, pv.pos, projection=proj
            )

        set_extent = True
        if vproj in ["OSGB", "EuroPP", "UKCP", "robin", "lcc"]:
            set_extent = False
        if extent and set_extent:
            mymap.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

        if vproj == "cyl":
            mymap.set_aspect(pv.aspect)
        elif vproj == "lcc":
            mymap.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())
        elif vproj == "UKCP":
            mymap.set_extent([-11, 3, 49, 61], crs=ccrs.PlateCarree())
        elif vproj == "EuroPP":
            mymap.set_extent([-12, 25, 30, 75], crs=ccrs.PlateCarree())

        if pv.plot is not None:
            pv.plot.set_frame_on(False)
            pv.plot.set_xticks([])
            pv.plot.set_yticks([])

        pv.mymap = mymap

    def draw_grid(self) -> None:
        """Plot a graticule on the active map axes."""
        pv = self.plotvars
        if pv.mymap is None:
            return
        if pv.proj != "cyl":
            return

        lons = np.arange((360 / pv.grid_x_spacing) + 1) * pv.grid_x_spacing
        lons = np.concatenate([lons - 360, lons])
        lats = np.arange((180 / pv.grid_y_spacing) + 1) * pv.grid_y_spacing - 90

        pv.mymap.gridlines(
            color=pv.grid_colour,
            linewidth=pv.grid_thickness,
            linestyle=pv.grid_linestyle,
            xlocs=lons,
            ylocs=lats,
            zorder=pv.grid_zorder,
        )

    def draw_polar_axes(self) -> None:
        """Draw graticule lines and longitude labels for polar stereographic plots.

        Replicates the legacy behaviour: latitude circles, longitude spokes,
        and longitude text labels placed just outside the bounding latitude.
        No latitude labels are drawn (matching legacy output).
        """
        pv = self.plotvars
        if pv.mymap is None:
            return
        vproj = pv.proj
        if vproj not in ("npstere", "spstere"):
            return

        mymap = pv.mymap
        boundinglat = pv.boundinglat
        lon_0 = pv.lon_0
        geodetic = ccrs.Geodetic()

        # --- latitude circles ---
        latvals = np.arange(5) * 30 - 60  # [-60, -30, 0, 30, 60]
        if vproj == "npstere":
            latvals = latvals[latvals >= boundinglat]
        else:
            latvals = latvals[latvals <= boundinglat]

        for lat in latvals:
            if abs(lat - boundinglat) > 1:
                lons_line = np.arange(361, dtype=float)
                lats_line = np.full(361, lat)
                mymap.plot(
                    lons_line, lats_line,
                    color=pv.grid_colour,
                    linewidth=pv.grid_thickness,
                    linestyle=pv.grid_linestyle,
                    transform=geodetic,
                )

        # --- longitude spokes ---
        lonvals = np.arange(7) * 60  # [0, 60, 120, 180, 240, 300, 360]
        for lon in lonvals:
            if vproj == "npstere":
                lats_line = np.arange(90 - boundinglat) + boundinglat
            else:
                lats_line = np.arange(boundinglat + 91) - 90
            lons_line = np.full(lats_line.size, float(lon))
            mymap.plot(
                lons_line, lats_line,
                color=pv.grid_colour,
                linewidth=pv.grid_thickness,
                linestyle=pv.grid_linestyle,
                transform=geodetic,
            )

        # --- longitude labels ---
        if vproj == "npstere":
            polar_proj = ccrs.NorthPolarStereo(central_longitude=lon_0)
            latrange = 90 - abs(boundinglat)
            latpt = boundinglat - latrange / 40.0
        else:
            polar_proj = ccrs.SouthPolarStereo(central_longitude=lon_0)
            latrange = 90 - abs(boundinglat)
            latpt = boundinglat + latrange / 40.0

        axis_label_fontsize = getattr(pv, "axis_label_fontsize", 11)
        axis_label_fontweight = getattr(pv, "axis_label_fontweight", "normal")

        if axis_label_fontsize > 0:
            for lon in lonvals:
                # Build label the same way as legacy _mapaxis
                lon2 = np.mod(lon + 180, 360) - 180
                degsym = r"$\degree$" if getattr(pv, "degsym", False) else ""
                if lon2 < 0 and lon2 > -180:
                    label = str(abs(int(lon2))) + degsym + "W"
                elif lon2 > 0 and lon2 <= 180:
                    label = str(int(lon2)) + degsym + "E"
                elif lon2 == 0:
                    label = "0" + degsym
                else:  # 180
                    label = "180" + degsym

                lonr, latr = polar_proj.transform_point(
                    lon, latpt, ccrs.PlateCarree()
                )

                v_align = "center"
                if lonr < -1:
                    h_align = "right"
                elif lonr > 1:
                    h_align = "left"
                else:
                    h_align = "center"
                    if latr < 0:
                        v_align = "top"
                    else:
                        v_align = "bottom"

                mymap.text(
                    lonr, latr, label,
                    horizontalalignment=h_align,
                    verticalalignment=v_align,
                    fontsize=axis_label_fontsize,
                    fontweight=axis_label_fontweight,
                    zorder=101,
                )

        # Blank off corners to make the plot circular, then draw the bounding
        # latitude circle and adjust axes limits (mirrors legacy behaviour).
        lons_b = np.arange(360, dtype=float)
        lats_b = np.full(360, float(boundinglat))
        device_coords = polar_proj.transform_points(
            ccrs.PlateCarree(), lons_b, lats_b
        )
        xmax_b = np.max(device_coords[:, 0])
        xmin_b = np.min(device_coords[:, 0])

        pts = np.where(device_coords[:, 0] >= 0.0)
        xpts = np.append(
            device_coords[:, 0][pts], np.zeros(np.size(pts)) + xmax_b
        )
        ypts = np.append(
            device_coords[:, 1][pts], device_coords[:, 1][pts][::-1]
        )
        mymap.fill(xpts, ypts, alpha=1.0, color="w", zorder=100)

        xpts = np.append(
            np.zeros(np.size(pts)) + xmin_b, -1.0 * device_coords[:, 0][pts]
        )
        ypts = np.append(
            device_coords[:, 1][pts], device_coords[:, 1][pts][::-1]
        )
        mymap.fill(xpts, ypts, alpha=1.0, color="w", zorder=100)

        mymap.set_frame_on(False)

        # Draw the bounding latitude circle
        lons_circ = np.arange(361, dtype=float)
        lats_circ = np.full(361, float(boundinglat))
        circle_coords = polar_proj.transform_points(
            ccrs.PlateCarree(), lons_circ, lats_circ
        )
        mymap.plot(
            circle_coords[:, 0], circle_coords[:, 1],
            color="k", zorder=100, clip_on=False,
        )

        # Expand axes limits slightly so labels are not clipped
        xmax_ax = np.max(np.abs(mymap.set_xlim(None)))
        mymap.set_xlim((-xmax_ax, xmax_ax), emit=False)
        ymax_ax = np.max(np.abs(mymap.set_ylim(None)))
        mymap.set_ylim((-ymax_ax, ymax_ax), emit=False)


def mapset(
    lonmin: float | None = None,
    lonmax: float | None = None,
    latmin: float | None = None,
    latmax: float | None = None,
    proj: str = "cyl",
    boundinglat: float = 0,
    lon_0: float = 0,
    lat_0: float = 40,
    resolution: str = "110m",
    user_mapset: int = 1,
    aspect: str | float | None = None,
) -> None:
    """Set map plotting parameters in shared state."""
    MapSet(plotvars).configure(
        lonmin=lonmin,
        lonmax=lonmax,
        latmin=latmin,
        latmax=latmax,
        proj=proj,
        boundinglat=boundinglat,
        lon_0=lon_0,
        lat_0=lat_0,
        resolution=resolution,
        user_mapset=user_mapset,
        aspect=aspect,
    )


def ensure_map_viewport() -> None:
    """Ensure a map viewport exists without resetting an existing map axes."""
    if plotvars.mymap is None:
        from .layout_runtime import (
            _open_figure,
            _reset_closed_figure_state,
            _select_position,
        )

        _reset_closed_figure_state()

        if plotvars.master_plot is None:
            _open_figure(user_plot=0)

        if plotvars.plot is None or (plotvars.rows > 1 or plotvars.columns > 1):
            if plotvars.gpos_called is False or plotvars.plot is None:
                _select_position(1)


def _ensure_map_axes() -> None:
    """Ensure map axes exist on the active plot state."""
    MapSet(plotvars).ensure_map_axes()


def _apply_map_axes_with_toggles(
    *,
    axes: bool = True,
    xaxis: bool = True,
    yaxis: bool = True,
    xticks=None,
    xticklabels=None,
    yticks=None,
    yticklabels=None,
    user_xlabel: str | None = None,
    user_ylabel: str | None = None,
) -> None:
    """Apply map axes while honoring axes/xaxis/yaxis visibility toggles."""
    xlabel = user_xlabel
    ylabel = user_ylabel
    map_xticks = xticks
    map_yticks = yticks
    map_xticklabels = xticklabels
    map_yticklabels = yticklabels

    if not axes:
        map_xticks = []
        map_yticks = []
        xlabel = ""
        ylabel = ""
    else:
        if not xaxis:
            map_xticks = []
            map_xticklabels = []
            xlabel = ""
        if not yaxis:
            map_yticks = []
            map_yticklabels = []
            ylabel = ""

    _apply_map_axes(
        xticks=map_xticks,
        yticks=map_yticks,
        xlabel=xlabel,
        ylabel=ylabel,
        xticklabels=map_xticklabels,
        yticklabels=map_yticklabels,
    )

    if plotvars.proj in ("npstere", "spstere"):
        MapSet(plotvars).draw_polar_axes()


def _apply_current_map_title(title: str | None) -> None:
    """Apply a title using the current global map state values."""
    if title is None or plotvars.mymap is None:
        return

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


def _apply_map_features(
    *,
    mymap: Any,
    continent_color: str | None = None,
    continent_thickness: float | None = None,
    continent_linestyle: str | None = None,
    kwargs: dict[str, Any] | None = None,
) -> None:
    """Apply coastlines and ocean/land/lake feature colors to a map axes.
    
    This centralizes the common map feature colouring logic.
    """
    if mymap is None:
        return
    
    if kwargs is None:
        kwargs = {}

    import cartopy.feature as cfeature

    feature = cfeature.NaturalEarthFeature(
        name="land",
        category="physical",
        scale=plotvars.resolution,
        facecolor="none",
    )
    mymap.add_feature(
        feature,
        edgecolor=continent_color or "k",
        linewidth=continent_thickness or 1.5,
        linestyle=continent_linestyle or "solid",
        zorder=kwargs.get("zorder", 1),
    )

    if plotvars.ocean_color is not None:
        mymap.add_feature(
            cfeature.OCEAN,
            edgecolor="face",
            facecolor=plotvars.ocean_color,
            zorder=plotvars.feature_zorder,
        )
    if plotvars.land_color is not None:
        mymap.add_feature(
            cfeature.LAND,
            edgecolor="face",
            facecolor=plotvars.land_color,
            zorder=plotvars.feature_zorder,
        )
    if plotvars.lake_color is not None:
        mymap.add_feature(
            cfeature.LAKES,
            edgecolor="face",
            facecolor=plotvars.lake_color,
            zorder=plotvars.feature_zorder,
        )


def _apply_map_axes(
    *,
    xticks,
    yticks,
    xlabel,
    ylabel,
    xticklabels,
    yticklabels,
) -> None:
    """Apply map axes labels/ticks without using legacy cfplot map helpers."""
    map_ax = plotvars.mymap
    if map_ax is None:
        return
    axes = True
    xaxis = True
    yaxis = True

    if plotvars.proj == "cyl":
        lon_ticks = xticks
        lon_labels = xticklabels
        lat_ticks = yticks
        lat_labels = yticklabels
        lonrange = plotvars.lonmax - plotvars.lonmin
        lon_mid = plotvars.lonmin + lonrange / 2.0
        xticklen = (plotvars.lonmax - plotvars.lonmin) * 0.007
        yticklen = (plotvars.latmax - plotvars.latmin) * 0.014

        if lon_ticks is None:
            lon_ticks, lon_labels = utility.mapaxis(
                min_val=plotvars.lonmin,
                max_val=plotvars.lonmax,
                axis_type=1,
                degsym=bool(plotvars.degsym),
            )
        if lat_ticks is None:
            lat_ticks, lat_labels = utility.mapaxis(
                min_val=plotvars.latmin,
                max_val=plotvars.latmax,
                axis_type=2,
                degsym=bool(plotvars.degsym),
            )

        if lon_ticks is not None:
            lon_ticks_new = list(lon_ticks)
            # Avoid wrapped endpoint labels overlapping for global ranges.
            if lonrange >= 360 and len(lon_ticks_new) >= 2:
                lon_ticks_new[0] = lon_ticks_new[0] + 0.01
                lon_ticks_new[-1] = lon_ticks_new[-1] - 0.01

            map_ax.set_xticks(lon_ticks_new, crs=ccrs.PlateCarree())
            map_ax.set_xticklabels(
                lon_labels if lon_labels is not None else lon_ticks_new,
                rotation=plotvars.xtick_label_rotation,
                horizontalalignment=plotvars.xtick_label_align,
            )

            # Match legacy behavior: draw top-edge major tick marks manually.
            if plotvars.plot_type == 1:
                proj = ccrs.PlateCarree(central_longitude=lon_mid)
                for xval in lon_ticks_new:
                    xpt, ypt = proj.transform_point(
                        xval, plotvars.latmax, ccrs.PlateCarree()
                    )
                    ypt2 = ypt + yticklen
                    map_ax.plot(
                        [xpt, xpt],
                        [ypt, ypt2],
                        color="k",
                        linewidth=0.8,
                        clip_on=False,
                    )
        if lat_ticks is not None:
            map_ax.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
            map_ax.set_yticklabels(
                lat_labels if lat_labels is not None else lat_ticks,
                rotation=plotvars.ytick_label_rotation,
                horizontalalignment=plotvars.ytick_label_align,
            )

            # Match legacy behavior: draw right-edge major tick marks manually.
            if plotvars.plot_type == 1:
                proj = ccrs.PlateCarree(central_longitude=lon_mid)
                for ytick in lat_ticks:
                    xpt, ypt = proj.transform_point(
                        plotvars.lonmax - 0.001, ytick, ccrs.PlateCarree()
                    )
                    xpt2 = xpt + xticklen
                    map_ax.plot(
                        [xpt, xpt2],
                        [ypt, ypt],
                        color="k",
                        linewidth=0.8,
                        clip_on=False,
                    )

        for label in map_ax.xaxis.get_ticklabels():
            label.set_fontsize(plotvars.axis_label_fontsize)
            label.set_fontweight(plotvars.axis_label_fontweight)
        for label in map_ax.yaxis.get_ticklabels():
            label.set_fontsize(plotvars.axis_label_fontsize)
            label.set_fontweight(plotvars.axis_label_fontweight)

    if plotvars.proj == "lcc":
        lonmin = plotvars.lonmin
        lonmax = plotvars.lonmax
        latmin = plotvars.latmin
        latmax = plotvars.latmax
        lon_0 = lonmin + (lonmax - lonmin) / 2.0
        lat_0 = latmin + (latmax - latmin) / 2.0
        standard_parallels = [33, 45]
        if latmin <= 0 and latmax <= 0:
            standard_parallels = [-45, -33]

        proj = ccrs.LambertConformal(
            central_longitude=lon_0,
            central_latitude=lat_0,
            cutoff=40,
            standard_parallels=standard_parallels,
        )

        ymin, ymax = map_ax.set_ylim(None)
        map_ax.set_ylim(ymin * 1.05, ymax, emit=False)
        map_ax.set_ylim(None)

        lons = np.arange(lonmax - lonmin + 1) + lonmin
        lats = np.arange(latmax - latmin + 1) + latmin

        # Mask left and right of plot
        lons_lr = np.zeros(np.size(lats)) + lonmin
        device_coords = proj.transform_points(ccrs.PlateCarree(), lons_lr, lats)
        xmin = np.min(device_coords[:, 0])
        xmax = np.max(device_coords[:, 0])
        if lat_0 > 0:
            ymin_lr = np.min(device_coords[:, 1])
            ymax_lr = np.max(device_coords[:, 1])
        else:
            ymin_lr = np.max(device_coords[:, 1])
            ymax_lr = np.min(device_coords[:, 1])

        map_ax.fill(
            [xmin, xmin, xmax, xmin],
            [ymin_lr, ymax_lr, ymax_lr, ymin_lr],
            alpha=1.0,
            color="w",
            zorder=100,
        )
        map_ax.plot(
            [xmin, xmax], [ymin_lr, ymax_lr], color="k", zorder=101, clip_on=False
        )

        map_ax.fill(
            [-xmin, -xmin, -xmax, -xmin],
            [ymin_lr, ymax_lr, ymax_lr, ymin_lr],
            alpha=1.0,
            color="w",
            zorder=100,
        )
        map_ax.plot(
            [-xmin, -xmax], [ymin_lr, ymax_lr], color="k", zorder=101, clip_on=False
        )

        # Upper mask/boundary
        lats_top = np.zeros(np.size(lons)) + latmax
        device_coords = proj.transform_points(ccrs.PlateCarree(), lons, lats_top)
        ymax_top = np.max(device_coords[:, 1])
        xpts = np.append(device_coords[:, 0], device_coords[:, 0][::-1])
        ypts = np.append(device_coords[:, 1], np.zeros(np.size(lons)) + ymax_top)
        map_ax.fill(xpts, ypts, alpha=1.0, color="w", zorder=100)
        map_ax.plot(
            device_coords[:, 0], device_coords[:, 1], color="k", zorder=101, clip_on=False
        )

        # Lower mask/boundary
        lats_bottom = np.zeros(np.size(lons)) + latmin
        device_coords = proj.transform_points(
            ccrs.PlateCarree(), lons, lats_bottom
        )
        ymin_bottom = np.min(device_coords[:, 1]) * 1.05
        xpts = np.append(device_coords[:, 0], device_coords[:, 0][::-1])
        ypts = np.append(device_coords[:, 1], np.zeros(np.size(lons)) + ymin_bottom)
        map_ax.fill(xpts, ypts, alpha=1.0, color="w", zorder=100)
        map_ax.plot(
            device_coords[:, 0], device_coords[:, 1], color="k", zorder=101, clip_on=False
        )

        map_ax.set_frame_on(False)

        if axes and xaxis:
            if xticks is None:
                map_xticks, map_xticklabels = utility.mapaxis(
                    min_val=plotvars.lonmin,
                    max_val=plotvars.lonmax,
                    axis_type=1,
                    degsym=bool(plotvars.degsym),
                )
            else:
                map_xticks = xticks
                map_xticklabels = xticks if xticklabels is None else xticklabels

            lats_x = np.arange(latmax - latmin + 1) + latmin
            for tick, tick_label in zip(map_xticks, map_xticklabels):
                lons_x = np.zeros(np.size(lats_x)) + tick
                device_coords = proj.transform_points(
                    ccrs.PlateCarree(), lons_x, lats_x
                )
                map_ax.plot(
                    device_coords[:, 0],
                    device_coords[:, 1],
                    linewidth=plotvars.grid_thickness,
                    linestyle=plotvars.grid_linestyle,
                    color=plotvars.grid_colour,
                    zorder=101,
                )

                latpt = latmin - 3
                if lat_0 < 0:
                    latpt = latmax + 1
                dpt = proj.transform_point(tick, latpt, ccrs.PlateCarree())
                map_ax.text(
                    dpt[0],
                    dpt[1],
                    tick_label,
                    horizontalalignment="center",
                    fontsize=plotvars.axis_label_fontsize,
                    fontweight=plotvars.axis_label_fontweight,
                    zorder=101,
                )

        if axes and yaxis:
            if yticks is None:
                map_yticks, map_yticklabels = utility.mapaxis(
                    min_val=plotvars.latmin,
                    max_val=plotvars.latmax,
                    axis_type=2,
                    degsym=bool(plotvars.degsym),
                )
            else:
                map_yticks = yticks
                map_yticklabels = yticks if yticklabels is None else yticklabels

            lons_y = np.arange(lonmax - lonmin + 1) + lonmin
            for tick, tick_label in zip(map_yticks, map_yticklabels):
                lats_y = np.zeros(np.size(lons_y)) + tick
                device_coords = proj.transform_points(
                    ccrs.PlateCarree(), lons_y, lats_y
                )
                map_ax.plot(
                    device_coords[:, 0],
                    device_coords[:, 1],
                    linewidth=plotvars.grid_thickness,
                    linestyle=plotvars.grid_linestyle,
                    color=plotvars.grid_colour,
                    zorder=101,
                )

                dpt_l = proj.transform_point(lonmin - 1, tick, ccrs.PlateCarree())
                map_ax.text(
                    dpt_l[0],
                    dpt_l[1],
                    tick_label,
                    horizontalalignment="right",
                    verticalalignment="center",
                    fontsize=plotvars.axis_label_fontsize,
                    fontweight=plotvars.axis_label_fontweight,
                    zorder=101,
                )

                dpt_r = proj.transform_point(lonmax + 1, tick, ccrs.PlateCarree())
                map_ax.text(
                    dpt_r[0],
                    dpt_r[1],
                    tick_label,
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=plotvars.axis_label_fontsize,
                    fontweight=plotvars.axis_label_fontweight,
                    zorder=101,
                )

    if plotvars.proj == "UKCP" and plotvars.grid:
        lons = (
            np.arange((360 / plotvars.grid_x_spacing) + 1)
            * plotvars.grid_x_spacing
        )
        lons = np.concatenate([lons - 360, lons])
        lats = (
            np.arange((180 / plotvars.grid_y_spacing) + 1)
            * plotvars.grid_y_spacing
            - 90
        )

        map_ax.gridlines(
            color=plotvars.grid_colour,
            linewidth=plotvars.grid_thickness,
            linestyle=plotvars.grid_linestyle,
            xlocs=lons,
            ylocs=lats,
            zorder=plotvars.grid_zorder,
        )

    if xlabel:
        map_ax.text(
            0.5,
            -0.10,
            xlabel,
            va="bottom",
            ha="center",
            rotation="horizontal",
            rotation_mode="anchor",
            transform=map_ax.transAxes,
            fontsize=plotvars.axis_label_fontsize,
            fontweight=plotvars.axis_label_fontweight,
        )
    if ylabel:
        map_ax.text(
            -0.05,
            0.50,
            ylabel,
            va="bottom",
            ha="center",
            rotation="vertical",
            rotation_mode="anchor",
            transform=map_ax.transAxes,
            fontsize=plotvars.axis_label_fontsize,
            fontweight=plotvars.axis_label_fontweight,
        )
