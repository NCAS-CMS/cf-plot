"""Contour plotting module.

Provides the refactored contour plotting interface.

Architecture:
- ContourData: Immutable container for arrays and metadata
- ContourLayout: Manages viewport allocation
- ColourScale: Encapsulates colormap/level logic
- ContourRenderer: Base class for rendering strategy
- MapContourRenderer: Renders to map (Cartopy)
- XYContourRenderer: Renders to Cartesian axes

Module Independence:
This module is currently independent at the module level (no module-level
imports from cfplot.py), though functions do import locally from cfplot
for essential utilities like calculate_levels and axis helpers. This keeps
module boundaries clear while preserving functionality during gradual refactoring.

Future work will move more utilities (calculate_levels, _stimeaxis, etc.)
into standalone modules (see utility.py, state.py) and eliminate even the
function-level cfplot imports.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import cf
import cartopy.crs as ccrs
import matplotlib.colors
import numpy as np
from matplotlib.axes import Axes

from . import utility
from .blockfill import _bfill, _bfill_ugrid
from .colour import apply_colour_scale, get_colour_scale_map
from .colorbar import cbar
from .layout_runtime import (
    apply_axes,
    ensure_xy_viewport,
    maybe_autosave,
    set_plot_limits,
)
from .map_runtime import (
    MapSet,
    _apply_dim_titles,
    _apply_map_title,
    _apply_map_features,
    ensure_map_viewport,
)
from .rotated_runtime import _render_ptype6_rotated_pole
from .state import (
    global_blockfill,
    global_fill,
    global_lines,
    plotvars,
)


def _detect_lon_cyclic(f: "cf.Field", x: "np.ndarray | None") -> bool:
    """Return True when the longitude axis closes on itself at 360°.

    Prefers cell bounds from the CF field when available.  Falls back to a
    centre-point heuristic (range + step ≈ 360°) when bounds are absent.
    Returns False for non-1-D or irregular grids (e.g. ORCA).
    """
    try:
        xdim = f.dim("X", default=None)
        if xdim is not None and xdim.has_bounds():
            b = xdim.bounds.data.array
            if b.ndim == 2:
                # Cyclic: right edge of last cell == left edge of first cell + 360°
                return abs(float(b[-1, 1]) - float(b[0, 0]) - 360.0) < 1.0

        # Fallback: centre-point heuristic — only valid for 1-D lon arrays
        if x is not None and x.ndim == 1 and len(x) > 1:
            step = (float(x[-1]) - float(x[0])) / (len(x) - 1)
            return abs((float(x[-1]) - float(x[0]) + step) - 360.0) < 0.5 * abs(step)

    except Exception:
        pass

    return False


@dataclass(frozen=True)
class ContourData:
    """Read-only contour inputs after extraction and validation.
    
    Holds extracted, validated, and pre-processed arrays ready for rendering.
    Immutable by design to prevent unintended state mutations during plotting.
    """

    field: np.ndarray
    x: np.ndarray | None
    y: np.ndarray | None
    ptype: int = 0
    colorbar_title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    levels: np.ndarray | None = None
    mult: int = 0
    fmult: float = 1.0
    irregular: bool = False
    is_ugrid: bool = False
    is_orca: bool = False
    fill: bool = True
    lines: bool = True
    blockfill: bool = False
    xpole: float | None = None
    ypole: float | None = None
    x_is_cyclic: bool = False
    face_lons: np.ndarray | None = None
    face_lats: np.ndarray | None = None
    face_connectivity: np.ndarray | None = None

    @classmethod
    def from_cf_field(
        cls,
        f: cf.Field,
        colorbar_title: str | None,
        verbose: bool | None = None,
        proj: str = "cyl",
    ) -> "ContourData":
        """Extract and prepare CF field for contouring."""
        (
            field,
            x,
            y,
            ptype,
            cbar_title,
            xlabel,
            ylabel,
            xpole,
            ypole,
        ) = utility.cf_data_assign(f, colorbar_title, verbose=verbose, proj=proj)

        if colorbar_title is not None:
            cbar_title = colorbar_title

        x_arr = x if x is None else np.asarray(x)
        x_is_cyclic = _detect_lon_cyclic(f, x_arr)
        irregular = (
            np.asanyarray(field).ndim == 1
            and x_arr is not None
            and y is not None
            and np.ndim(x_arr) == 1
            and np.ndim(y) == 1
            and np.asanyarray(field).size == np.asarray(x_arr).size == np.asarray(y).size
        )

        if irregular and proj == "cyl":
            x_arr = _normalize_longitudes_for_map(x_arr)

        return cls(
            field=np.asanyarray(field),
            x=x_arr,
            y=y if y is None else np.asarray(y),
            ptype=ptype if ptype is not None else 0,
            colorbar_title=cbar_title or "",
            xlabel=xlabel or "",
            ylabel=ylabel or "",
            xpole=utility.to_float_or_none(xpole),
            ypole=utility.to_float_or_none(ypole),
            x_is_cyclic=x_is_cyclic,
            irregular=irregular,
        )

    @classmethod
    def from_arrays(
        cls,
        field: np.ndarray,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
    ) -> "ContourData":
        """Create from raw numpy arrays with validation."""
        field = np.asanyarray(field)
        x = np.asarray(x) if x is not None else np.arange(field.shape[1])
        y = np.asarray(y) if y is not None else np.arange(field.shape[0])

        # Validate array dimensions - support both 1D coordinates and 2D (e.g., ORCA grids)
        if field.ndim not in (1, 2, 3):
            raise ValueError(f"Field must be 1D, 2D, or 3D, got shape {field.shape}")

        return cls(
            field=field,
            x=x,
            y=y,
            ptype=0,
            colorbar_title="",
            xlabel="",
            ylabel="",
        )


class ContourLayout:
    """Manage viewport and annotation geometry for contour plots.
    
    Separates concerns: layout calculates space, rendering uses it.
    Currently still delegates to legacy gopen/gset/gpos system.
    """

    def __init__(self, plotvars: Any):
        self.viewport: Axes | None = None
        self.colorbar_ax: Axes | None = None
        self.title_ax: Axes | None = None
        self._plotvars = plotvars
        self.colorbar_orientation: str = "horizontal"
        self.colorbar_position: list[float] | None = None

    def allocate_xy_viewport(
        self,
        colorbar_orientation: str | None,
        colorbar_position: list[float] | None,
    ) -> "ContourLayout":
        """Reserve viewport for Cartesian/non-map rendering.
        
        Coordinates with plotvars for multi-plot grids.
        """
        # Set colorbar orientation  
        self.colorbar_orientation = colorbar_orientation or "horizontal"
        self.colorbar_position = colorbar_position

        ensure_xy_viewport()

        # Store reference to current axes/map for later use
        self.viewport = self._plotvars.runtime.plot

        return self

    def allocate_map_viewport(
        self,
        colorbar_orientation: str | None,
        colorbar_position: list[float] | None,
    ) -> "ContourLayout":
        """Reserve viewport for map rendering without map-axis operations.

        This intentionally keeps map setup in a dedicated flow where projection
        creation (mapset/_set_map) happens after base viewport selection.
        """
        self.colorbar_orientation = colorbar_orientation or "horizontal"
        self.colorbar_position = colorbar_position

        ensure_map_viewport()

        self.viewport = self._plotvars.runtime.plot

        return self

    def allocate(
        self,
        colorbar_orientation: str | None,
        colorbar_position: list[float] | None,
    ) -> "ContourLayout":
        """Backward-compatible alias for Cartesian viewport allocation."""
        return self.allocate_xy_viewport(colorbar_orientation, colorbar_position)

    def apply_title(
        self,
        title: str | None,
        dims_title: bool,
        fontsize: int | None,
        fontweight: str | None,
    ) -> None:
        """Apply title and dimension titles to plot."""
        pv = self._plotvars
        runtime = pv.runtime
        map_state = pv.map
        dec = pv.decoration

        if title and title != "":
            if runtime.plot_type == 1:
                _apply_map_title(
                    mymap=runtime.mymap,
                    title=title,
                    proj=map_state.proj,
                    boundinglat=map_state.boundinglat,
                    lon_0=map_state.lon_0,
                    lonmin=map_state.lonmin,
                    lonmax=map_state.lonmax,
                    latmin=map_state.latmin,
                    latmax=map_state.latmax,
                    title_fontsize=fontsize or dec.title_fontsize,
                    title_fontweight=fontweight or dec.title_fontweight,
                )
            else:
                if self.viewport:
                    self.viewport.set_title(
                        title,
                        y=1.03,
                        fontsize=fontsize or dec.title_fontsize,
                        fontweight=fontweight or dec.title_fontweight,
                    )

        if dims_title:
            _apply_dim_titles(
                plot=runtime.plot,
                mymap=runtime.mymap,
                plot_type=runtime.plot_type,
                proj=map_state.proj,
                lonmin=map_state.lonmin,
                lonmax=map_state.lonmax,
                latmin=map_state.latmin,
                latmax=map_state.latmax,
                axis_label_fontsize=dec.axis_label_fontsize,
                axis_label_fontweight=dec.axis_label_fontweight,
                title=dims_title if isinstance(dims_title, str) else None,
            )

    def apply_axis_labels(
        self,
        xlabel: str | None,
        ylabel: str | None,
        xticks: Any,
        yticks: Any,
        xticklabels: Any | None = None,
        yticklabels: Any | None = None,
    ) -> None:
        """Apply axis labels and ticks to plot."""
        if self.viewport is None:
            return

        apply_axes(
            plot_type=self._plotvars.runtime.plot_type,
            xticks=xticks,
            yticks=yticks,
            xlabel=xlabel,
            ylabel=ylabel,
            xticklabels=xticklabels,
            yticklabels=yticklabels,
        )


class ColourScale:
    """Encapsulate level fitting, colormap selection, and cbar labels.
    
    Replaces the scattered cscale_flag (0/1/2) branching with explicit methods.
    """

    def __init__(self, plotvars: Any):
        self._plotvars = plotvars
        self._levels: np.ndarray | None = None
        self._includes_zero: bool = False
        self._levels_extend: str = "neither"

    def fit_to_levels(
        self,
        levels: np.ndarray,
        includes_zero: bool,
        levels_extend: str,
    ) -> "ColourScale":
        """Fit color scale to contour levels, handling zero if present."""
        self._levels = np.asarray(levels)
        self._includes_zero = includes_zero
        self._levels_extend = levels_extend
        scale = self._plotvars.scale

        # Replicate legacy cscale_flag == 0 logic (default colour scale).
        # If zero is present in levels, split scale1 around zero so
        # blue shades are strictly below zero and warm shades above.
        if scale.cscale_flag == 0:
            col_zero = 0
            includes_zero = False
            for cval in self._levels:
                if not includes_zero:
                    col_zero += 1
                if cval == 0:
                    includes_zero = True

            if includes_zero:
                cs_below = col_zero
                cs_above = np.size(self._levels) - col_zero + 1
                if scale.levels_extend in ("max", "neither"):
                    cs_below = cs_below - 1
                if scale.levels_extend in ("min", "neither"):
                    cs_above = cs_above - 1
                apply_colour_scale(
                    "scale1",
                    below=cs_below,
                    above=cs_above,
                    uniform=bool(scale.cs_uniform),
                )
            else:
                ncols = np.size(self._levels) + 1
                if scale.levels_extend in ("min", "max"):
                    ncols = ncols - 1
                elif scale.levels_extend == "neither":
                    ncols = ncols - 2
                apply_colour_scale("viridis", ncols=ncols)

            scale.cscale_flag = 0

        # Replicate cscale_flag == 1 logic (user-selected color map, fit to levels)
        if scale.cscale_flag == 1:
            ncols = np.size(self._levels) + 1
            if scale.levels_extend == "min" or scale.levels_extend == "max":
                ncols = ncols - 1
            if scale.levels_extend == "neither":
                ncols = ncols - 2
            apply_colour_scale(scale.cs_user, ncols=ncols)
            scale.cscale_flag = 1

        return self

    def get_cmap(self) -> matplotlib.colors.ListedColormap:
        """Get colormap after fitting to levels."""
        scale = self._plotvars.scale
        colmap = get_colour_scale_map()
        cmap = matplotlib.colors.ListedColormap(colmap)

        if scale.levels_extend == "min" or scale.levels_extend == "both":
            cmap.set_under(scale.cs[0])
        if scale.levels_extend == "max" or scale.levels_extend == "both":
            cmap.set_over(scale.cs[-1])

        return cmap

    def colourbar_labels(
        self,
        levels: np.ndarray,
        orientation: str,
        n_columns: int,
        label_skip: int | None,
        custom_labels: list[str] | None,
    ) -> list[str]:
        """Generate colourbar labels from levels with skip/custom overrides."""
        if custom_labels is not None:
            return custom_labels

        # Legacy default: estimate skip for horizontal colour bars from the
        # total character count, and include fewer labels for readability.
        if label_skip is None:
            if orientation == "horizontal":
                nchars = sum(len(str(level)) for level in levels)
                label_skip = int(nchars / 80 + 1)
                if n_columns > 1:
                    label_skip = int(nchars * n_columns / 80)
            else:
                label_skip = 1

        if label_skip <= 1:
            return [str(level) for level in levels]

        if self._includes_zero:
            zero_positions = np.where(np.asarray(levels) == 0)[0]
            if np.size(zero_positions) > 0:
                zero_pos = int(zero_positions[0])
                labels = [levels[zero_pos]]

                i = zero_pos + label_skip
                while i <= len(levels) - 1:
                    labels = list(np.append(labels, levels[i]))
                    i += label_skip

                i = zero_pos - label_skip
                if i >= 0:
                    while i >= 0:
                        labels = list(np.append([levels[i]], labels))
                        i -= label_skip

                return self._expand_skipped_labels(labels, label_skip)

        labels = [levels[0]]
        i = int(label_skip)
        while i <= len(levels) - 1:
            labels = list(np.append(labels, levels[i]))
            i += label_skip

        return self._expand_skipped_labels(labels, label_skip)

    @staticmethod
    def _expand_skipped_labels(labels: list[Any], label_skip: int) -> list[str]:
        """Interleave skipped colour-bar labels with blank placeholders."""
        clabels: list[str] = []
        for label in labels:
            clabels.append(str(label))
            if label_skip > 1:
                clabels.extend([""] * (label_skip - 1))

        return clabels


class ContourRenderer:
    """Base renderer for shared contour drawing responsibilities."""

    def __init__(
        self,
        layout: ContourLayout,
        data: ContourData,
        colour_scale: ColourScale,
    ):
        self.layout = layout
        self.data = data
        self.cs = colour_scale
        self.frame_artists: list[Any] = []

    def render_filled(
        self, alpha: float, zorder: int, transform_first: bool | None
    ) -> None:
        """Render filled contours. Subclass implements plot-type-specific logic."""
        _ = (alpha, zorder, transform_first)

    def render_blockfill(
        self, fast: bool | None, alpha: float, zorder: int
    ) -> None:
        """Render block-filled contours."""
        _ = (fast, alpha, zorder)

    def render_lines(
        self,
        colors: Any,
        linewidths: Any,
        linestyles: Any,
        line_labels: bool,
        zero_thick: bool | int,
        zorder: int = 1,
    ) -> None:
        """Render contour lines and labels."""
        _ = (colors, linewidths, linestyles, line_labels, zero_thick, zorder)

    def render_colorbar(
        self,
        orientation: str | None,
        shrink: float | None,
        position: list[float] | None,
        fraction: float | None,
        thick: float | None,
        anchor: float | None,
        fontsize: int | None,
        fontweight: str | None,
        text_up_down: bool,
        text_down_up: bool,
        drawedges: bool,
        labels: list[str] | None = None,
        title: str | None = None,
    ) -> Any:
        """Render colorbar for filled contours."""
        _ = (
            orientation,
            shrink,
            position,
            fraction,
            thick,
            anchor,
            fontsize,
            fontweight,
            text_up_down,
            text_down_up,
            drawedges,
            labels,
            title,
        )
        return None


class MapContourRenderer(ContourRenderer):
    """Map renderer specialization for ptype == 1 (lon-lat plots).
    
    Handles Cartopy transformations, coastlines, and polar projections.
    """

    def render_filled(
        self, alpha: float, zorder: int, transform_first: bool | None
    ) -> None:
        """Render filled contours on a map with Cartopy."""
        if self.data.x is None or self.data.y is None or self.data.levels is None:
            return

        lons = self.data.x
        lats = self.data.y

        if self.data.irregular:
            field, lons, lats = _window_irregular_map_data(
                self.data.field * self.data.fmult,
                lons,
                lats,
            )
            runtime = plotvars.runtime
            scale = plotvars.scale
            cmap = self.cs.get_cmap()
            runtime.image = runtime.mymap.tricontourf(
                lons,
                lats,
                field,
                self.data.levels,
                extend=scale.levels_extend,
                cmap=cmap,
                norm=scale.norm,
                alpha=alpha,
                transform=ccrs.PlateCarree(),
                zorder=zorder,
            )
            if hasattr(runtime.image, "collections"):
                self.frame_artists.extend(list(runtime.image.collections))
            return

        if transform_first is None and np.ndim(lons) == 1 and np.ndim(lats) == 1:
            if np.size(lons) >= 400:
                transform_first = True

        if transform_first and np.ndim(lons) == 1 and np.ndim(lats) == 1:
            lons, lats = np.meshgrid(lons, lats)

        cmap = self.cs.get_cmap()
        runtime = plotvars.runtime
        scale = plotvars.scale
        runtime.image = runtime.mymap.contourf(
            lons,
            lats,
            self.data.field * self.data.fmult,
            self.data.levels,
            extend=scale.levels_extend,
            cmap=cmap,
            norm=scale.norm,
            alpha=alpha,
            transform=ccrs.PlateCarree(),
            zorder=zorder,
            transform_first=transform_first,
        )
        if hasattr(runtime.image, "collections"):
            self.frame_artists.extend(list(runtime.image.collections))

    def render_blockfill(
        self, fast: bool | None, alpha: float, zorder: int
    ) -> None:
        """Render block-filled contours on a map."""
        if self.data.levels is None:
            return

        if self.data.is_ugrid:
            if (
                self.data.face_lons is None
                or self.data.face_lats is None
                or self.data.face_connectivity is None
            ):
                return

            _bfill_ugrid(
                f=self.data.field * self.data.fmult,
                face_lons=self.data.face_lons,
                face_lats=self.data.face_lats,
                face_connectivity=self.data.face_connectivity,
                clevs=self.data.levels,
                alpha=alpha,
                zorder=zorder,
            )
            return

        if self.data.x is None or self.data.y is None:
            return

        _bfill(
            f=self.data.field * self.data.fmult,
            x=self.data.x,
            y=self.data.y,
            clevs=self.data.levels,
            bound=0,
            alpha=alpha,
            fast=fast,
            zorder=zorder,
        )

    def render_lines(
        self,
        colors: Any,
        linewidths: Any,
        linestyles: Any,
        line_labels: bool,
        zero_thick: bool | int,
        zorder: int = 1,
    ) -> None:
        """Render contour lines on a map with Cartopy transform."""
        if self.data.x is None or self.data.y is None or self.data.levels is None:
            return

        if self.data.irregular:
            field, lons, lats = _window_irregular_map_data(
                self.data.field * self.data.fmult,
                self.data.x,
                self.data.y,
            )
            runtime = plotvars.runtime
            dec = plotvars.decoration
            cs = runtime.mymap.tricontour(
                lons,
                lats,
                field,
                self.data.levels,
                colors=colors,
                linewidths=linewidths,
                linestyles=linestyles,
                alpha=1.0,
                transform=ccrs.PlateCarree(),
                zorder=zorder,
            )
            if hasattr(cs, "collections"):
                self.frame_artists.extend(list(cs.collections))

            if line_labels and not isinstance(self.data.levels, int):
                nd = utility.ndecs(self.data.levels)
                fmt = "%d"
                if nd != 0:
                    fmt = "%1." + str(nd) + "f"
                runtime.plot.clabel(
                    cs,
                    levels=self.data.levels,
                    fmt=fmt,
                    colors=colors,
                    fontsize=dec.text_fontsize,
                    zorder=zorder,
                )
            return

        runtime = plotvars.runtime
        dec = plotvars.decoration
        cs = runtime.mymap.contour(
            self.data.x,
            self.data.y,
            self.data.field * self.data.fmult,
            self.data.levels,
            colors=colors,
            linewidths=linewidths,
            linestyles=linestyles,
            alpha=1.0,
            transform=ccrs.PlateCarree(),
            zorder=zorder,
        )
        if hasattr(cs, "collections"):
            self.frame_artists.extend(list(cs.collections))

        if line_labels and not isinstance(self.data.levels, int):
            nd = utility.ndecs(self.data.levels)
            fmt = "%d"
            if nd != 0:
                fmt = "%1." + str(nd) + "f"
            runtime.plot.clabel(
                cs,
                levels=self.data.levels,
                fmt=fmt,
                colors=colors,
                fontsize=dec.text_fontsize,
                zorder=zorder,
            )

        if zero_thick:
            cs0 = runtime.mymap.contour(
                self.data.x,
                self.data.y,
                self.data.field * self.data.fmult,
                [-1e-32, 0],
                colors=colors,
                linewidths=zero_thick,
                linestyles=linestyles,
                alpha=1.0,
                transform=ccrs.PlateCarree(),
                zorder=zorder,
            )
            if hasattr(cs0, "collections"):
                self.frame_artists.extend(list(cs0.collections))

    def render_colorbar(
        self,
        orientation: str | None,
        shrink: float | None,
        position: list[float] | None,
        fraction: float | None,
        thick: float | None,
        anchor: float | None,
        fontsize: int | None,
        fontweight: str | None,
        text_up_down: bool,
        text_down_up: bool,
        drawedges: bool,
        labels: list[str] | None = None,
        title: str | None = None,
    ) -> Any:
        """Render colorbar for map contour plots."""
        if self.data.levels is None:
            return None

        return cbar(
            labels=labels,
            orientation=orientation,
            position=position,
            shrink=shrink,
            title=title or self.data.colorbar_title,
            fontsize=fontsize,
            fontweight=fontweight,
            text_up_down=text_up_down,
            text_down_up=text_down_up,
            drawedges=drawedges,
            fraction=fraction,
            thick=thick,
            levs=self.data.levels,
            anchor=anchor,
        )


class XYContourRenderer(ContourRenderer):
    """Cartesian renderer specialization for non-map contour plots.
    
    Handles ptypes 0, 2-7 (simple XY, lat-height, lon-height, Hovmuller, rotated).
    """

    def render_filled(
        self, alpha: float, zorder: int, transform_first: bool | None
    ) -> None:
        """Render filled contours in Cartesian space."""
        _ = transform_first
        if self.data.x is None or self.data.y is None or self.data.levels is None:
            return

        cmap = self.cs.get_cmap()
        runtime = plotvars.runtime
        scale = plotvars.scale
        runtime.image = runtime.plot.contourf(
            self.data.x,
            self.data.y,
            self.data.field * self.data.fmult,
            self.data.levels,
            extend=scale.levels_extend,
            cmap=cmap,
            norm=scale.norm,
            alpha=alpha,
            zorder=zorder,
        )

    def render_blockfill(
        self, fast: bool | None, alpha: float, zorder: int
    ) -> None:
        """Render block-filled contours in Cartesian space."""
        if self.data.x is None or self.data.y is None or self.data.levels is None:
            return

        _bfill(
            f=self.data.field * self.data.fmult,
            x=self.data.x,
            y=self.data.y,
            clevs=self.data.levels,
            bound=0,
            alpha=alpha,
            fast=fast,
            zorder=zorder,
        )

    def render_lines(
        self,
        colors: Any,
        linewidths: Any,
        linestyles: Any,
        line_labels: bool,
        zero_thick: bool | int,
        zorder: int = 1,
    ) -> None:
        """Render contour lines in Cartesian space."""
        if self.data.x is None or self.data.y is None or self.data.levels is None:
            return

        runtime = plotvars.runtime
        dec = plotvars.decoration
        cs = runtime.plot.contour(
            self.data.x,
            self.data.y,
            self.data.field * self.data.fmult,
            self.data.levels,
            colors=colors,
            linewidths=linewidths,
            linestyles=linestyles,
            zorder=zorder,
        )
        if line_labels and not isinstance(self.data.levels, int):
            nd = utility.ndecs(self.data.levels)
            fmt = "%d"
            if nd != 0:
                fmt = "%1." + str(nd) + "f"
            runtime.plot.clabel(
                cs,
                fmt=fmt,
                colors=colors,
                fontsize=dec.text_fontsize,
                zorder=zorder,
            )

        if zero_thick:
            runtime.plot.contour(
                self.data.x,
                self.data.y,
                self.data.field * self.data.fmult,
                [-1e-32, 0],
                colors=colors,
                linewidths=zero_thick,
                linestyles=linestyles,
                alpha=1.0,
                zorder=zorder,
            )

    def render_colorbar(
        self,
        orientation: str | None,
        shrink: float | None,
        position: list[float] | None,
        fraction: float | None,
        thick: float | None,
        anchor: float | None,
        fontsize: int | None,
        fontweight: str | None,
        text_up_down: bool,
        text_down_up: bool,
        drawedges: bool,
        labels: list[str] | None = None,
        title: str | None = None,
    ) -> Any:
        """Render colorbar for Cartesian contour plots."""
        if self.data.levels is None:
            return None

        return cbar(
            labels=labels,
            orientation=orientation,
            position=position,
            shrink=shrink,
            title=title or self.data.colorbar_title,
            fontsize=fontsize,
            fontweight=fontweight,
            text_up_down=text_up_down,
            text_down_up=text_down_up,
            drawedges=drawedges,
            fraction=fraction,
            thick=thick,
            levs=self.data.levels,
            anchor=anchor,
        )


def levs(min=None, max=None, step=None, manual=None, extend="both"):
    """Set or clear the contour levels stored in shared plotting state."""
    scale = plotvars.scale
    runtime = plotvars.runtime

    if all(val is not None for val in [min, max]) and step is None:
        print(
            "\ncfp.levs error: when the min and max are specified "
            "a step also needs to be specified\n"
        )
        return

    if all(val is None for val in [min, max, step, manual]):
        scale.levels = None
        scale.levels_min = None
        scale.levels_max = None
        scale.levels_step = None
        scale.levels_extend = "both"
        scale.norm = None
        runtime.user_levs = 0
        return

    if manual is not None:
        scale.levels = np.array(manual)
        scale.levels_min = None
        scale.levels_max = None
        scale.levels_step = None
        ncolors = np.size(scale.levels)
        if extend == "both" or extend == "max":
            ncolors = ncolors - 1
        scale.norm = matplotlib.colors.BoundaryNorm(
            boundaries=scale.levels, ncolors=ncolors
        )
        runtime.user_levs = 1
    else:
        if all(val is not None for val in [min, max, step]):
            scale.levels_min = min
            scale.levels_max = max
            scale.levels_step = step
            scale.norm = None
            if all(isinstance(item, int) for item in [min, max, step]):
                lstep = step * 1e-10
                levs_arr = np.arange(min, max + lstep, step, dtype=np.float64)
                levs_arr = ((levs_arr * 1e10).astype(np.int64)).astype(np.float64)
                levs_arr = (levs_arr / 1e10).astype(np.int64)
                scale.levels = levs_arr
            else:
                lstep = step * 1e-10
                levs_arr = np.arange(min, max + lstep, step, dtype=np.float64)
                levs_arr = (levs_arr * 1e10).astype(np.int64).astype(np.float64)
                levs_arr = levs_arr / 1e10
                scale.levels = levs_arr
            runtime.user_levs = 1

            for pt in np.arange(np.size(scale.levels)):
                ndecs = str(scale.levels[pt])[::-1].find(".")
                if ndecs > 7:
                    scale.levels[pt] = round(scale.levels[pt], 7)

    if step is not None and all(val is None for val in [min, max]):
        runtime.user_levs = 0
        scale.levels = None
        scale.levels_step = step

    if extend not in ["neither", "min", "max", "both"]:
        errstr = "\n\n extend must be one of 'neither', 'min', 'max', 'both'\n"
        raise TypeError(errstr)
    scale.levels_extend = extend


def _can_use_new_xy_path(f: Any, kwargs: dict[str, Any]) -> bool:
    """Return True when the new XY renderer can safely handle this call."""
    unsupported = (
        "irregular",
        "orca",
        "swap_axes",
        "xlog",
    )
    for key in unsupported:
        if kwargs.get(key):
            return False

    face_kwargs_present = any(
        kwargs.get(key) is not None
        for key in ("face_lons", "face_lats", "face_connectivity")
    )
    if face_kwargs_present and not (isinstance(f, cf.Field) and kwargs.get("blockfill")):
        return False

    ptype = kwargs.get("ptype", 0)
    if not isinstance(f, cf.Field) and ptype not in (0, 1, None):
        return False

    return True


def _clear_animation_artists(plotvars: Any) -> None:
    """Remove artists from previous animation frame if present."""
    artists = getattr(plotvars.runtime, "_contour_animation_artists", None)
    if not artists:
        return
    for artist in artists:
        try:
            artist.remove()
        except Exception:
            continue
    plotvars.runtime._contour_animation_artists = []
    _clear_animation_title_artist(plotvars)


def _clear_animation_title_artist(plotvars: Any) -> None:
    """Remove animation title artist from previous frame if present."""
    title_artist = getattr(plotvars.runtime, "_contour_animation_title_artist", None)
    if title_artist is None:
        return
    try:
        title_artist.remove()
    except Exception:
        pass
    plotvars.runtime._contour_animation_title_artist = None


def _clear_animation_colorbar(plotvars: Any) -> None:
    """Remove animation colorbar from previous frame if present."""
    colorbar_artist = getattr(plotvars.runtime, "_contour_animation_colorbar", None)
    if colorbar_artist is None:
        return

    try:
        colorbar_artist.remove()
    except Exception:
        ax = getattr(colorbar_artist, "ax", None)
        if ax is not None:
            try:
                ax.remove()
            except Exception:
                pass

    plotvars.runtime._contour_animation_colorbar = None


def _ptype_axes(ptype: int | None) -> set[str]:
    """Return logical axes used by each contour plot type."""
    mapping: dict[int, set[str]] = {
        1: {"X", "Y"},
        2: {"Y", "Z"},
        3: {"X", "Z"},
        4: {"X", "T"},
        5: {"Y", "T"},
        6: {"X", "Y"},
        7: {"T", "Z"},
    }
    if ptype is None:
        return set()
    return mapping.get(int(ptype), set())


def _infer_animation_axis(f: Any, axis_spec: Any, ptype: int | None) -> str | None:
    """Infer animation axis from a field and axis specification.

    Parameters
    ----------
    f : Any
        Input field.
    axis_spec : Any
        User axis selection. Supported values are "auto", "T", "Z", "Y", "X".
    """
    if not isinstance(f, cf.Field):
        return None

    if axis_spec is None:
        return None

    axis_text = str(axis_spec).strip()
    if axis_text == "":
        return None

    axis_upper = axis_text.upper()
    valid_axes = ("T", "Z", "Y", "X")

    if axis_upper != "AUTO":
        if axis_upper in valid_axes and f.has_construct(axis_upper):
            return axis_upper
        return None

    try:
        dims = utility.find_dim_names(f)
    except Exception:
        dims = []

    ptype_axes = _ptype_axes(ptype)

    # For known non-zero ptypes, infer frame axis as a singleton axis that
    # is not part of the selected ptype axes.
    if ptype not in (None, 0) and ptype_axes:
        for axis in ("T", "Z", "Y", "X"):
            if axis not in dims or axis in ptype_axes:
                continue
            try:
                values = np.asanyarray(f.construct(axis).array)
            except Exception:
                continue
            if values.size == 1:
                return axis
        return None

    # ptype=0 fallback: prefer temporal slices first, then vertical,
    # then horizontal singleton axes.
    for axis in ("T", "Z", "Y", "X"):
        if axis not in dims:
            continue
        try:
            values = np.asanyarray(f.construct(axis).array)
        except Exception:
            continue
        if values.size == 1:
            return axis

    return None


def _animation_axis_value_text(f: cf.Field, axis: str) -> str | None:
    """Return axis/value text used in animation titles."""
    axis_key = axis
    if axis == "Z":
        try:
            axis_key = utility.find_z(f)
        except Exception:
            axis_key = axis

    try:
        construct = f.construct(axis_key)
    except Exception:
        return None

    try:
        if axis == "T" and getattr(construct, "dtarray", None) is not None:
            values = np.asanyarray(construct.dtarray)
        else:
            values = np.asanyarray(construct.array)
    except Exception:
        return None

    if values.size != 1:
        return None

    value = values.reshape(-1)[0]
    name, units = utility.cf_var_name_titles(f, axis_key)
    axis_name = name or axis
    units_text = f" {units}" if units else ""

    return f"{axis_name}: {value}{units_text}"


def _resolve_animation_title(
    *,
    f: Any,
    base_title: str,
    animation: bool,
    animation_axis: Any,
    ptype: int | None,
    animation_title_template: str | None,
) -> str:
    """Build final title text for animation frames."""
    if not animation:
        return base_title

    axis = _infer_animation_axis(f, animation_axis, ptype)
    if axis is None:
        return base_title

    if not isinstance(f, cf.Field):
        return base_title

    frame_text = _animation_axis_value_text(f, axis)
    if not frame_text:
        return base_title

    if animation_title_template:
        try:
            return str(
                animation_title_template.format(
                    title=base_title,
                    frame=frame_text,
                    axis=axis,
                )
            )
        except Exception:
            pass

    if base_title:
        return f"{base_title} | {frame_text}"
    return frame_text


def _field_has_ugrid_faces(f: cf.Field) -> bool:
    """Return True when a CF field exposes face connectivity for UGRID plots."""
    try:
        return bool(f.domain_topologies()) and f.domain_topology(
            "cell:face", default=None
        ) is not None
    except Exception:
        return False


def _as_array(value: Any) -> np.ndarray:
    """Convert a CF object or array-like to a NumPy array."""
    if isinstance(value, cf.Field):
        return np.asanyarray(value.array)
    return np.asanyarray(value)


def _face_vertex_array(face_values: Any, face_connectivity: Any) -> np.ndarray:
    """Return per-face vertex coordinates from node coordinates and connectivity."""
    try:
        bounds = getattr(face_values, "bounds", None)
        if bounds is not None:
            return np.asanyarray(bounds.array)
    except Exception:
        pass

    values = _as_array(face_values)
    connectivity = np.asanyarray(_as_array(face_connectivity), dtype=int)
    if values.ndim == 1 and connectivity.ndim == 2:
        if connectivity.size and connectivity.min() >= 0 and connectivity.max() < values.size:
            return values[connectivity]
    return values


def _normalize_longitudes_for_map(lons: np.ndarray) -> np.ndarray:
    """Shift longitudes into a continuous [-180, 180] range for map plots."""
    lons = np.asanyarray(lons, dtype=float)
    if lons.ndim != 1 or lons.size == 0:
        return lons

    if np.nanmax(lons) > 180.0 and np.nanmin(lons) >= 0.0:
        lons = np.where(lons > 180.0, lons - 360.0, lons)

    return lons


def _window_irregular_map_data(
    field: np.ndarray, lons: np.ndarray, lats: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Wrap scattered lon/lat data to the current map window.

    This mirrors the legacy irregular_window helper closely enough for the
    global LFRic example: longitudes are shifted into the active map window,
    then a seam column is interpolated at the left edge and duplicated at the
    right edge for a full-globe plot.
    """
    field_irregular = np.asarray(field, dtype=float).copy()
    lons_irregular = np.asarray(lons, dtype=float).copy()
    lats_irregular = np.asarray(lats, dtype=float).copy()

    lonmin = float(plotvars.lonmin)
    lonmax = float(plotvars.lonmax)

    found_lon = False
    lons_offset = 0.0
    for ilon in (-360.0, 0.0, 360.0):
        lons_test = lons_irregular + ilon
        if np.min(lons_test) <= lonmin:
            found_lon = True
            lons_offset = ilon

    if found_lon:
        lons_irregular = lons_irregular + lons_offset
        pts = np.where(lons_irregular < lonmin)
        lons_irregular[pts] = lons_irregular[pts] + 360.0

    # Build a seam line at the left edge of the plot by interpolating the
    # wrapped points nearby in longitude/latitude space.
    delta = 120.0
    pts_left = np.where(lons_irregular >= lonmin + 360.0 - delta)
    lons_left = lons_irregular[pts_left] - 360.0
    lats_left = lats_irregular[pts_left]
    field_left = field_irregular[pts_left]

    field_wrap = np.concatenate([field_irregular, field_left])
    lons_wrap = np.concatenate([lons_irregular, lons_left])
    lats_wrap = np.concatenate([lats_irregular, lats_left])

    try:
        from scipy.interpolate import griddata
    except Exception:
        return field_irregular, lons_irregular, lats_irregular

    lons_new = np.zeros(181) + lonmin
    lats_new = np.arange(181) - 90.0
    field_new = griddata(
        (lons_wrap, lats_wrap),
        field_wrap,
        (lons_new, lats_new),
        method="linear",
    )

    pts = np.where(np.isfinite(field_new))
    field_new = field_new[pts]
    lons_new = lons_new[pts]
    lats_new = lats_new[pts]

    field_irregular = np.concatenate([field_irregular, field_new])
    lons_irregular = np.concatenate([lons_irregular, lons_new])
    lats_irregular = np.concatenate([lats_irregular, lats_new])

    if lonmax - lonmin == 360.0:
        field_irregular = np.concatenate([field_irregular, field_new])
        lons_irregular = np.concatenate([lons_irregular, lons_new + 359.95])
        lats_irregular = np.concatenate([lats_irregular, lats_new])

    return field_irregular, lons_irregular, lats_irregular


def _render_with_new_xy(f: Any, x: Any, y: Any, kwargs: dict[str, Any]) -> bool:
    """Attempt rendering via new XY renderer and return True on success.
    
    Note: Imports from cfplot are local (inside function) to maintain
    module-level independence while preserving current functionality.
    """
    pv_map = plotvars.map
    pv_axes = plotvars.axes
    pv_dec = plotvars.decoration
    pv_layout = plotvars.layout
    pv_scale = plotvars.scale
    pv_runtime = plotvars.runtime
    pv_output = plotvars.output

    if isinstance(f, cf.Field) and (x is not None or y is not None):
        field_arr = np.asanyarray(f.array)
        x_arr = np.asarray(x.array) if isinstance(x, cf.Field) else x
        y_arr = np.asarray(y.array) if isinstance(y, cf.Field) else y
        data = ContourData.from_arrays(
            field=field_arr,
            x=None if x_arr is None else np.asarray(x_arr),
            y=None if y_arr is None else np.asarray(y_arr),
        )
        data = replace(data, ptype=kwargs.get("ptype", 0) or 0)
    elif isinstance(f, cf.Field):
        # Legacy parity: when mapset is user-defined for polar stereographic
        # plots, subset latitude before data extraction and level generation.
        if pv_runtime.user_mapset:
            if pv_map.proj == "npstere":
                f = f.subspace(Y=cf.wi(pv_map.boundinglat, 90.0))
            elif pv_map.proj == "spstere":
                f = f.subspace(Y=cf.wi(-90.0, pv_map.boundinglat))

        data = ContourData.from_cf_field(
            f=f,
            colorbar_title=kwargs.get("colorbar_title", None),
            verbose=kwargs.get("verbose", None),
            proj=pv_map.proj,
        )
        # Implemented CF extraction targets include generic Cartesian (ptype 0),
        # map, and selected non-map ptypes.
        if data.ptype not in (0, 1, 2, 3, 4, 5, 6):
            return False
    else:
        data = ContourData.from_arrays(field=np.asanyarray(f), x=x, y=y)
        data = replace(data, ptype=kwargs.get("ptype", 0) or 0)

    if isinstance(f, cf.Field) and bool(kwargs.get("blockfill")) and _field_has_ugrid_faces(f):
        # Prefer the face metadata embedded in the field, which is the legacy
        # path and is more reliable than the auxiliary coordinate variables
        # supplied by callers.
        face_lons = f.aux("X").bounds.array
        face_lats = f.aux("Y").bounds.array
        face_connectivity = f.domain_topology("cell:face").array

        face_lons = _face_vertex_array(face_lons, face_connectivity)
        face_lats = _face_vertex_array(face_lats, face_connectivity)

        data = replace(
            data,
            is_ugrid=True,
            face_lons=face_lons,
            face_lats=face_lats,
            face_connectivity=face_connectivity,
        )

    # Keep legacy behavior for axis-routing logic by setting active plot type.
    pv_runtime.plot_type = data.ptype

    fill = kwargs.get("fill", global_fill)
    lines = kwargs.get("lines", global_lines)
    blockfill = kwargs.get("blockfill", global_blockfill)
    line_labels = kwargs.get("line_labels", True)
    zero_thick = kwargs.get("zero_thick", False)
    colors = kwargs.get("colors", "k")
    linewidths = kwargs.get("linewidths", None)
    linestyles = kwargs.get("linestyles", None)
    alpha = kwargs.get("alpha", 1.0)
    zorder = kwargs.get("zorder", 1)

    if blockfill:
        fill = False

    colorbar = kwargs.get("colorbar", True)
    if not fill and not blockfill:
        colorbar = False

    if pv_scale.levels is None:
        levels_field = data.field
        if bool(kwargs.get("animation", False)) and kwargs.get("animation_reference") is not None:
            ref = kwargs.get("animation_reference")
            if isinstance(ref, cf.Field):
                levels_field = np.asanyarray(ref.array)
            else:
                levels_field = np.asanyarray(ref)

        clevs, mult, fmult = utility.calculate_levels(
            field=levels_field,
            level_spacing=kwargs.get("level_spacing", "linear"),
            levels_step=pv_scale.levels_step,
            verbose=kwargs.get("verbose", None),
        )
    else:
        clevs = np.asarray(pv_scale.levels)
        mult = 0
        fmult = 1

    cs = ColourScale(plotvars).fit_to_levels(
        levels=np.asarray(clevs),
        includes_zero=bool(np.any(np.asarray(clevs) == 0)),
        levels_extend=pv_scale.levels_extend,
    )

    import matplotlib
    matplotlib.rcParams["contour.negative_linestyle"] = "solid"

    _cb_orient = kwargs.get("colorbar_orientation", None)
    if _cb_orient is None:
        if data.ptype == 1 and pv_map.proj in ("npstere", "spstere"):
            _cb_orient = "vertical"
        else:
            _cb_orient = "horizontal"
    colorbar_orientation = _cb_orient

    clabels = cs.colourbar_labels(
        levels=np.asarray(clevs),
        orientation=colorbar_orientation,
        n_columns=pv_layout.columns,
        label_skip=kwargs.get("colorbar_label_skip", None),
        custom_labels=kwargs.get("colorbar_labels"),
    )
    cbar_labels = clabels

    colorbar_title = kwargs.get("colorbar_title", data.colorbar_title)
    if mult != 0:
        colorbar_title = f"{colorbar_title} *10^{{{mult}}}"

    resolved_title = _resolve_animation_title(
        f=f,
        base_title=kwargs.get("title", "") or "",
        animation=bool(kwargs.get("animation", False)),
        animation_axis=kwargs.get("animation_axis", "auto"),
        ptype=data.ptype,
        animation_title_template=kwargs.get("animation_title_template", None),
    )

    # ptype 6 has its own rendering/axes flow and must bypass generic XY
    # layout to avoid non-map axes state assumptions.
    if data.ptype == 6:
        data = replace(
            data,
            levels=np.asarray(clevs),
            mult=mult,
            fmult=fmult,
            fill=fill,
            lines=lines,
            blockfill=blockfill,
        )
        return _render_ptype6_rotated_pole(
            f=f,
            data=data,
            kwargs=kwargs,
            clevs=np.asarray(clevs),
            cs=cs,
            cbar_labels=cbar_labels,
            colorbar_title=colorbar_title,
            fill=fill,
            lines=lines,
            blockfill=blockfill,
            line_labels=line_labels,
            zero_thick=zero_thick,
            colors=colors,
            linewidths=linewidths,
            linestyles=linestyles,
            alpha=alpha,
            zorder=zorder,
            finalize_callback=maybe_autosave,
        )

    if pv_runtime.user_plot == 0:
        ensure_xy_viewport()

    xmin = kwargs.get("xmin", float(np.nanmin(data.x)))
    xmax = kwargs.get("xmax", float(np.nanmax(data.x)))
    ymin = kwargs.get("ymin", float(np.nanmin(data.y)))
    ymax = kwargs.get("ymax", float(np.nanmax(data.y)))

    # Legacy parity for latitude/longitude/time-pressure plots:
    # pressure-like coordinates are rendered with pressure decreasing upward.
    if data.ptype in (2, 3, 7) and kwargs.get("user_gset", pv_runtime.user_gset) == 0:
        positive = "down"
        if isinstance(f, cf.Field):
            myz = utility.find_z(f)
            if myz is not None and hasattr(f.construct(myz), "positive"):
                positive = f.construct(myz).positive
        if "theta" in (data.ylabel or "").split(" "):
            positive = "up"
        if "height" in (data.ylabel or "").split(" "):
            positive = "up"

        if data.ptype == 2:
            if xmin < -80 and xmin >= -90:
                xmin = -90
            if xmax > 80 and xmax <= 90:
                xmax = 90

        if positive == "down":
            ymin = float(np.nanmax(data.y))
            ymax = float(np.nanmin(data.y))
            if ymax < 10:
                ymax = 0
        else:
            ymin = float(np.nanmin(data.y))
            ymax = float(np.nanmax(data.y))

    # Respect user gset for Hovmuller plots with date-string y limits.
    tmin = None
    tmax = None
    if isinstance(f, cf.Field) and data.ptype in (4, 5):
        if all(
            val is not None
            for val in [pv_axes.xmin, pv_axes.xmax, pv_axes.ymin, pv_axes.ymax]
        ):
            tmin = pv_axes.ymin
            tmax = pv_axes.ymax
            xmin = pv_axes.xmin
            xmax = pv_axes.xmax

            ref_time = f.construct("T").units
            ref_calendar = f.construct("T").calendar
            time_units = cf.Units(ref_time, ref_calendar)
            t = cf.Data(cf.dt(pv_axes.ymin), units=time_units)
            ymin = t.array
            t = cf.Data(cf.dt(pv_axes.ymax), units=time_units)
            ymax = t.array

    if kwargs.get("ylog", False) and ymax == 0:
        ymax = 1
    set_plot_limits(
        xmin=xmin,
        xmax=xmax,
        ymin=ymin,
        ymax=ymax,
        ylog=bool(kwargs.get("ylog", False)),
        user_gset=kwargs.get("user_gset", pv_runtime.user_gset),
    )

    if tmin is not None and tmax is not None:
        pv_axes.ymin = tmin
        pv_axes.ymax = tmax

    xticks = kwargs.get("xticks", None)
    yticks = kwargs.get("yticks", None)
    xticklabels = kwargs.get("xticklabels", None)
    yticklabels = kwargs.get("yticklabels", None)

    default_xlabel = data.xlabel or ""
    default_ylabel = data.ylabel or ""

    if data.ptype == 1:
        map_runtime = MapSet(plotvars)

        animation = bool(kwargs.get("animation", False))
        reuse_map_background = bool(kwargs.get("reuse_map_background", False))
        clear_previous_frame = bool(kwargs.get("clear_previous_frame", False))
        draw_static_map = not (animation and reuse_map_background)

        if clear_previous_frame:
            _clear_animation_artists(plotvars)

        mylonmin = float(np.nanmin(data.x))
        mylonmax = float(np.nanmax(data.x))
        mylatmin = float(np.nanmin(data.y))
        mylatmax = float(np.nanmax(data.y))
        lonrange = mylonmax - mylonmin
        latrange = mylatmax - mylatmin
        if lonrange > 360.0:
            mylonmax = mylonmin + 360.0

        if draw_static_map:
            if not ((lonrange > 350 and latrange > 160) or pv_runtime.user_mapset == 1):
                map_runtime.configure(
                    lonmin=mylonmin,
                    lonmax=mylonmax,
                    latmin=mylatmin,
                    latmax=mylatmax,
                    user_mapset=0,
                    resolution=pv_map.resolution,
                )
            map_runtime.ensure_map_axes()

        # Add a cyclic longitude column when the grid is near-global but
        # doesn't close on itself (no explicit bounds), to avoid a gap at
        # the wrap-around seam in Cartopy.
        # NOTE: For non-cyclic orthographic and polar stereographic grids this
        # can introduce seam artefacts, so skip it there unless the grid is
        # explicitly cyclic.
        if (
            data.x is not None
            and data.y is not None
            and np.ndim(data.x) == 1
            and np.ndim(data.y) == 1
            and not data.irregular
            and not blockfill
            and (
                plotvars.proj not in ("ortho", "npstere", "spstere")
                or data.x_is_cyclic
            )
        ):
            lonrange_data = float(np.nanmax(data.x)) - float(np.nanmin(data.x))
            if 350.0 < lonrange_data < 360.0:
                new_field, new_x = utility.add_cyclic(data.field, data.x)
                data = replace(data, field=new_field, x=new_x)

        # For orthographic plots with a non-cyclic longitude grid, avoid a
        # seam through the center of the visible hemisphere by rolling the
        # array so it starts at ~-180° rather than at 0°.  Cyclic grids
        # (whose bounds close at 360°) are already seamless and must NOT be
        # rolled, or a new artefact appears at ±180° near the poles.
        # Assumes the longitude array is monotonically increasing (standard
        # for CF-convention model output).
        if (
            data.x is not None
            and np.ndim(data.x) == 1
            and plotvars.proj == "ortho"
            and not data.x_is_cyclic
            and not data.irregular
        ):
            split = int(np.searchsorted(data.x, 180.0))
            wrapped_x = np.mod(data.x + 180.0, 360.0) - 180.0
            data = replace(
                data,
                x=np.roll(wrapped_x, -split),
                field=np.roll(data.field, -split, axis=-1),
            )

        if not data.irregular and np.ndim(data.y) == 1 and data.y[0] > data.y[-1]:
            data = replace(data, y=data.y[::-1], field=np.flipud(data.field))

        xticks = kwargs.get("xticks", None)
        yticks = kwargs.get("yticks", None)
        xticklabels = kwargs.get("xticklabels", None)
        yticklabels = kwargs.get("yticklabels", None)

    time_ticks = None
    time_labels = None
    time_label = None
    if isinstance(f, cf.Field) and data.ptype in (4, 5):
        time_ticks, time_labels, time_label = utility.timeaxis(
            dtimes=f.construct("T"),
            user_gset=pv_runtime.user_gset,
            xmin=pv_axes.xmin,
            xmax=pv_axes.xmax,
            ymin=pv_axes.ymin,
            ymax=pv_axes.ymax,
            tspace_year=pv_output.tspace_year,
            tspace_hour=pv_output.tspace_hour,
            tspace_day=pv_output.tspace_day,
        )
    xticks, yticks, xticklabels, yticklabels, default_xlabel, default_ylabel = (
        utility.compute_xy_ticks(
            ptype=data.ptype,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            ylog=bool(kwargs.get("ylog", False)),
            degsym=pv_dec.degsym,
            xticks=xticks,
            yticks=yticks,
            xticklabels=xticklabels,
            yticklabels=yticklabels,
            default_xlabel=default_xlabel,
            default_ylabel=default_ylabel,
            time_ticks=time_ticks,
            time_labels=time_labels,
            time_label=time_label,
        )
    )

    if data.ptype == 1:
        layout = ContourLayout(plotvars).allocate_map_viewport(
            colorbar_orientation=colorbar_orientation,
            colorbar_position=kwargs.get("colorbar_position", None),
        )
    else:
        layout = ContourLayout(plotvars).allocate_xy_viewport(
            colorbar_orientation=colorbar_orientation,
            colorbar_position=kwargs.get("colorbar_position", None),
        )
        layout.apply_axis_labels(
            xlabel=kwargs.get("xlabel", default_xlabel),
            ylabel=kwargs.get("ylabel", default_ylabel),
            xticks=xticks,
            yticks=yticks,
            xticklabels=xticklabels,
            yticklabels=yticklabels,
        )

    data = replace(
        data,
        levels=np.asarray(clevs),
        mult=mult,
        fmult=fmult,
        fill=fill,
        lines=lines,
        blockfill=blockfill,
    )
    if data.ptype == 1:
        renderer = MapContourRenderer(layout=layout, data=data, colour_scale=cs)
    else:
        renderer = XYContourRenderer(layout=layout, data=data, colour_scale=cs)

    transform_first = kwargs.get("transform_first", None)
    if data.ptype == 1 and plotvars.proj in ("npstere", "spstere"):
        # Polar stereographic can show longitude striping when Cartopy
        # pre-transforms dense regular lon/lat grids in data space.
        # Rendering in map space is robust for both cyclic and non-cyclic data.
        transform_first = False
    elif data.ptype == 1 and plotvars.proj == "ortho" and not data.x_is_cyclic:
        # Non-cyclic grids on ortho are prone to clipping artefacts with
        # transform_first=True on near-global dense grids, so force it off.
        # Cyclic grids use the default (True for 1-D arrays) which avoids a
        # visible seam at the 0°/360° boundary.
        transform_first = False

    if fill:
        renderer.render_filled(
            alpha=alpha,
            zorder=zorder,
            transform_first=transform_first,
        )
    if blockfill:
        renderer.render_blockfill(
            fast=kwargs.get("blockfill_fast", None), alpha=alpha, zorder=zorder
        )
    if lines:
        renderer.render_lines(
            colors=colors,
            linewidths=linewidths,
            linestyles=linestyles,
            line_labels=line_labels,
            zero_thick=zero_thick,
            zorder=zorder,
        )

    if data.ptype == 1:
        map_runtime = MapSet(plotvars)

        animation = bool(kwargs.get("animation", False))
        reuse_map_background = bool(kwargs.get("reuse_map_background", False))
        clear_previous_frame = bool(kwargs.get("clear_previous_frame", False))
        draw_static_map = not (animation and reuse_map_background)

        if animation and clear_previous_frame:
            _clear_animation_title_artist(plotvars)
            _clear_animation_colorbar(plotvars)

        if draw_static_map:
            apply_axes(
                plot_type=1,
                xticks=kwargs.get("xticks", None),
                yticks=kwargs.get("yticks", None),
                xlabel=kwargs.get("xlabel", None),
                ylabel=kwargs.get("ylabel", None),
                xticklabels=kwargs.get("xticklabels", None),
                yticklabels=kwargs.get("yticklabels", None),
            )

            _apply_map_features(
                mymap=pv_runtime.mymap,
                continent_color=pv_dec.continent_color or "k",
                continent_thickness=pv_dec.continent_thickness or 1.5,
                continent_linestyle=pv_dec.continent_linestyle or "solid",
                kwargs=kwargs,
            )
            if kwargs.get("grid", pv_dec.grid):
                map_runtime.draw_grid()

            map_runtime.draw_polar_axes()

        # Persist only dynamic contour artists for animation updates.
        pv_runtime._contour_animation_artists = list(renderer.frame_artists)

    if colorbar:
        colorbar_artist = renderer.render_colorbar(
            orientation=colorbar_orientation,
            shrink=kwargs.get("colorbar_shrink", None),
            position=kwargs.get("colorbar_position", None),
            fraction=kwargs.get("colorbar_fraction", None),
            thick=kwargs.get("colorbar_thick", None),
            anchor=kwargs.get("colorbar_anchor", None),
            fontsize=kwargs.get("colorbar_fontsize", None),
            fontweight=kwargs.get("colorbar_fontweight", None),
            text_up_down=kwargs.get("colorbar_text_up_down", False),
            text_down_up=kwargs.get("colorbar_text_down_up", False),
            drawedges=kwargs.get("colorbar_drawedges", True),
            labels=list(cbar_labels),
            title=colorbar_title,
        )
        if bool(kwargs.get("animation", False)):
            pv_runtime._contour_animation_colorbar = colorbar_artist

    if data.ptype == 1:
        title = resolved_title
        animation = bool(kwargs.get("animation", False))

        if title != "":
            title_artist = _apply_map_title(
                mymap=pv_runtime.mymap,
                title=title,
                proj=pv_map.proj,
                boundinglat=pv_map.boundinglat,
                lon_0=pv_map.lon_0,
                lonmin=pv_map.lonmin,
                lonmax=pv_map.lonmax,
                latmin=pv_map.latmin,
                latmax=pv_map.latmax,
                title_fontsize=pv_dec.title_fontsize,
                title_fontweight=pv_dec.title_fontweight,
            )
            if animation:
                pv_runtime._contour_animation_title_artist = title_artist
    else:
        layout.apply_title(
            title=resolved_title,
            dims_title=bool(kwargs.get("titles", False)),
            fontsize=pv_dec.title_fontsize,
            fontweight=pv_dec.title_fontweight,
        )

    maybe_autosave()

    return True


def con(f=None, x=None, y=None, **kwargs):
    """Contour entrypoint coordinating through new object architecture.
    
    Gradually extracts logic from legacy _legacy_con into structured classes
    while preserving behavior. Eventually rendering will be split into 
    MapContourRenderer and XYContourRenderer subclasses.
    
    For now, orchestration uses the new classes for data and styling,
    then delegates to legacy renderer.

        Animation title options (map and non-map):
        - animation: bool, enables animation-aware rendering hooks.
        - animation_reference: cf.Field or array-like, optional reference data
            used for automatic level generation across animation frames.
            When supplied and levels are automatic, contour levels are computed
            from this full reference rather than the current frame slice.
        - animation_axis: str, one of "auto", "T", "Z", "Y", "X".
            When "auto" and ptype != 0, the frame axis is inferred as a singleton
            axis not used by that ptype. For ptype == 0, fallback preference is
            singleton T, then Z, then Y, then X.
        - animation_title_template: str, optional template used to construct
            per-frame titles. Available fields are {title}, {frame}, and {axis}.

        Example:
                cfp.con(
                        f,
                        animation=True,
                        reuse_map_background=True,
                        animation_axis="auto",
                        animation_title_template="{title} [{frame}]",
                        title="Air temperature",
                )
    """
    # Refactor mode: unsupported cases should fail explicitly rather than
    # silently routing through legacy code.
    if not _can_use_new_xy_path(f=f, kwargs=kwargs):
        raise NotImplementedError(
            "Contour case not implemented in refactored renderer yet"
        )

    if _render_with_new_xy(f=f, x=x, y=y, kwargs=kwargs):
        return None

    raise NotImplementedError(
        "Contour case not implemented in refactored renderer yet"
    )

