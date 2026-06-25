"""Shared plotting state for cf-plot."""

from __future__ import annotations

import os
import sys
from dataclasses import MISSING, dataclass, field, fields as dc_fields
from typing import Any, ClassVar

import cartopy
import matplotlib
import matplotlib.pyplot as pyplot

from .colour.colourmaps import cscale1


class pvars:
    """Stores plotting variables in `cfp.plotvars`."""

    @dataclass
    class MapState:
        proj: str = "cyl"
        resolution: str = "110m"
        lonmin: float = -180
        lonmax: float = 180
        latmin: float = -90
        latmax: float = 90
        boundinglat: float = 0
        lon_0: float = 0
        lat_0: float = 40
        rotated_grid_spacing: float = 10
        rotated_deg_spacing: float = 0.75
        rotated_continents: bool = True
        rotated_grid: bool = True
        rotated_grid_thickness: float = 1.0
        rotated_labels: bool = True

    @dataclass
    class AxesState:
        xmin: Any = None
        xmax: Any = None
        ymin: Any = None
        ymax: Any = None
        plot_xmin: Any = None
        plot_xmax: Any = None
        plot_ymin: Any = None
        plot_ymax: Any = None
        graph_xmin: Any = None
        graph_xmax: Any = None
        graph_ymin: Any = None
        graph_ymax: Any = None
        xticks: Any = None
        xticklabels: Any = None
        xlabel: Any = None
        yticks: Any = None
        yticklabels: Any = None
        ylabel: Any = None
        xlog: Any = None
        ylog: Any = None
        xstep: Any = None
        ystep: Any = None
        twinx: Any = False
        twiny: Any = False
        xtick_label_rotation: int = 0
        xtick_label_align: str = "center"
        ytick_label_rotation: int = 0
        ytick_label_align: str = "right"
        axis_width: Any = None

    @dataclass
    class DecorationState:
        title: Any = None
        master_title: Any = None
        master_title_location: list[float] = field(
            default_factory=lambda: [0.5, 0.95]
        )
        text_fontsize: int = 11
        axis_label_fontsize: int = 11
        colorbar_fontsize: int = 11
        title_fontsize: int = 15
        master_title_fontsize: int = 30
        legend_text_size: int = 11
        fontweight: str = "normal"
        text_fontweight: str = "normal"
        axis_label_fontweight: str = "normal"
        colorbar_fontweight: str = "normal"
        title_fontweight: str = "normal"
        master_title_fontweight: str = "normal"
        legend_text_weight: str = "normal"
        legend_frame: bool = True
        legend_frame_edge_color: str = "k"
        legend_frame_face_color: Any = None
        grid: bool = False
        grid_x_spacing: float = 60
        grid_y_spacing: float = 30
        grid_zorder: int = 100
        grid_colour: str = "k"
        grid_linestyle: str = "--"
        grid_thickness: float = 1.0
        feature_zorder: int = 999
        land_color: Any = None
        ocean_color: Any = None
        lake_color: Any = None
        continent_color: Any = None
        continent_thickness: Any = None
        continent_linestyle: Any = None
        degsym: bool = False
        titles_con_called: bool = False

    @dataclass
    class LayoutState:
        rows: int = 1
        columns: int = 1
        pos: int = 1
        gpos_called: bool = False
        orientation: str = "landscape"
        aspect: str = "equal"

    @dataclass
    class ScaleState:
        levels: Any = None
        levels_min: Any = None
        levels_max: Any = None
        levels_step: Any = None
        levels_extend: str = "both"
        level_spacing: Any = None
        cs_uniform: bool = True
        cs: Any = None
        cscale_flag: int = 0
        cs_user: str = "cscale1"
        norm: Any = None

    @dataclass
    class RuntimeState:
        plot_type: int = 1
        master_plot: Any = None
        plot: Any = None
        mymap: Any = None
        image: Any = None
        user_mapset: int = 0
        user_gset: int = 0
        user_levs: int = 0
        user_plot: int = 0
        _contour_session_open: bool = False
        _contour_animation_artists: list[Any] = field(default_factory=list)
        _contour_animation_title_artist: Any = None
        _contour_animation_colorbar: Any = None

    @dataclass
    class OutputState:
        global_viewer: str = "display"
        viewer: Any = "display"
        file: Any = None
        dpi: Any = None
        tight: bool = False
        tspace_year: Any = None
        tspace_month: Any = None
        tspace_day: Any = None
        tspace_hour: Any = None

    _SECTION_TYPES: ClassVar[dict[str, type]] = {
        "map": MapState,
        "axes": AxesState,
        "decoration": DecorationState,
        "layout": LayoutState,
        "scale": ScaleState,
        "runtime": RuntimeState,
        "output": OutputState,
    }
    _ATTR_TO_SECTION: ClassVar[dict[str, str]] = {}

    def __init__(self, **kwargs):
        object.__setattr__(self, "map", self.MapState())
        object.__setattr__(self, "axes", self.AxesState())
        object.__setattr__(self, "decoration", self.DecorationState())
        object.__setattr__(self, "layout", self.LayoutState())
        object.__setattr__(self, "scale", self.ScaleState())
        object.__setattr__(self, "runtime", self.RuntimeState())
        object.__setattr__(self, "output", self.OutputState())

        for attr, value in kwargs.items():
            if isinstance(value, (list, dict, set)):
                value = value.copy()
            setattr(self, attr, value)

    def __getattr__(self, attr: str) -> Any:
        section_name = self._ATTR_TO_SECTION.get(attr)
        if section_name is None:
            raise AttributeError(attr)
        return getattr(getattr(self, section_name), attr)

    def __setattr__(self, attr: str, value: Any) -> None:
        section_name = self._ATTR_TO_SECTION.get(attr)
        if section_name is not None:
            setattr(getattr(self, section_name), attr, value)
            return

        if attr in {
            "map",
            "axes",
            "decoration",
            "layout",
            "scale",
            "runtime",
            "output",
        } or attr.startswith("_"):
            object.__setattr__(self, attr, value)
            return

        # Preserve legacy extensibility for ad-hoc state attributes.
        object.__setattr__(self, attr, value)

    def __str__(self):
        out = []
        for a in sorted(self._ATTR_TO_SECTION):
            v = getattr(self, a)
            out.append(f"{a} = {repr(v)}")

        for a, v in self.__dict__.items():
            if a in {
                "map",
                "axes",
                "decoration",
                "layout",
                "scale",
                "runtime",
                "output",
            }:
                continue
            out.append(f"{a} = {repr(v)}")

        return "\n".join(out)


def reset_runtime_state() -> None:
    """Reset shared plotting runtime state back to defaults."""
    plotvars.master_plot = None
    plotvars.plot = None
    plotvars.mymap = None
    plotvars.norm = None
    plotvars.image = None
    plotvars.rows = 1
    plotvars.columns = 1
    plotvars.pos = 1
    plotvars.gpos_called = False
    plotvars.user_plot = 0
    plotvars._contour_session_open = False
    plotvars._contour_animation_artists = []
    plotvars._contour_animation_title_artist = None
    plotvars._contour_animation_colorbar = None
    plotvars.twinx = None
    plotvars.twiny = None
    plotvars.plot_xmin = None
    plotvars.plot_xmax = None
    plotvars.plot_ymin = None
    plotvars.plot_ymax = None
    plotvars.graph_xmin = None
    plotvars.graph_xmax = None
    plotvars.graph_ymin = None
    plotvars.graph_ymax = None
    plotvars.titles_con_called = False


try:
    disp = os.environ["DISPLAY"]
except Exception:
    matplotlib.use("Agg")

try:
    pre_existing_data_dir = os.environ["pre_existing_data_dir"]
    cartopy.config["pre_existing_data_dir"] = pre_existing_data_dir
except KeyError:
    pass

global_fill = True
global_lines = True
global_blockfill = False
global_degsym = False
global_viewer = "display"

defaults_file = os.path.expanduser("~") + "/.cfplot_defaults"
if os.path.exists(defaults_file):
    with open(defaults_file) as file:
        for line in file:
            vals = line.split(" ")
            com, val = vals
            v = False
            if val.strip() == "True":
                v = True
            if com == "blockfill":
                global_blockfill = v
            if com == "lines":
                global_lines = v
            if com == "fill":
                global_fill = v
            if com == "degsym":
                global_degsym = v
            if com == "viewer":
                global_viewer = val.strip()


def _dataclass_defaults(dc_type: type) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for fld in dc_fields(dc_type):
        if fld.default_factory is not MISSING:
            defaults[fld.name] = fld.default_factory()
        else:
            defaults[fld.name] = fld.default
    return defaults


def _refresh_state_schemas() -> None:
    attr_to_section: dict[str, str] = {}
    for section, dc_type in pvars._SECTION_TYPES.items():
        for fld in dc_fields(dc_type):
            attr_to_section[fld.name] = section
    pvars._ATTR_TO_SECTION = attr_to_section


def _build_plotvars_defaults() -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for dc_type in pvars._SECTION_TYPES.values():
        defaults.update(_dataclass_defaults(dc_type))

    # Environment and startup-specific overrides.
    defaults["global_viewer"] = global_viewer
    defaults["viewer"] = global_viewer
    defaults["degsym"] = global_degsym
    defaults["cs"] = cscale1
    return defaults


_refresh_state_schemas()
plotvars_defaults = _build_plotvars_defaults()

_SETVARS_KEYS = [
    "viewer",
    "file",
    "dpi",
    "tight",
    "tspace_year",
    "tspace_month",
    "tspace_day",
    "tspace_hour",
    "xtick_label_rotation",
    "xtick_label_align",
    "ytick_label_rotation",
    "ytick_label_align",
    "text_fontsize",
    "axis_label_fontsize",
    "colorbar_fontsize",
    "title_fontsize",
    "master_title_fontsize",
    "legend_text_size",
    "fontweight",
    "text_fontweight",
    "axis_label_fontweight",
    "colorbar_fontweight",
    "title_fontweight",
    "master_title_fontweight",
    "legend_text_weight",
    "master_title",
    "master_title_location",
    "legend_frame",
    "legend_frame_edge_color",
    "legend_frame_face_color",
    "grid",
    "grid_x_spacing",
    "grid_y_spacing",
    "grid_zorder",
    "grid_colour",
    "grid_linestyle",
    "grid_thickness",
    "rotated_grid_spacing",
    "rotated_deg_spacing",
    "rotated_continents",
    "rotated_grid",
    "rotated_grid_thickness",
    "rotated_labels",
    "feature_zorder",
    "land_color",
    "ocean_color",
    "lake_color",
    "continent_color",
    "continent_thickness",
    "continent_linestyle",
    "axis_width",
    "degsym",
    "level_spacing",
    "cs_uniform",
]
setvars_defaults = {key: plotvars_defaults[key] for key in _SETVARS_KEYS}

allvars_defaults = {**setvars_defaults, **plotvars_defaults}
plotvars = pvars(**allvars_defaults)

# Keep shared-state viewer defaults aligned with legacy startup behavior.
is_inline = "inline" in matplotlib.get_backend()
if is_inline:
    plotvars.viewer = None

if sys.platform == "darwin":
    plotvars.global_viewer = "matplotlib"
    plotvars.viewer = "matplotlib"


def setvars(**kwargs: Any) -> None:
    """Set shared plotting variables from defaults plus explicit overrides."""
    for def_var, def_value in setvars_defaults.items():
        setattr(plotvars, def_var, def_value)

    for set_var, set_value in kwargs.items():
        if set_var not in setvars_defaults:
            raise ValueError(
                f"Unrecognised keyword argument for setvars: {set_var}"
            )

        setattr(plotvars, set_var, set_value)

    if "grid" not in kwargs and (
        "grid_x_spacing" in kwargs or "grid_y_spacing" in kwargs
    ):
        plotvars.grid = (
            plotvars.grid_x_spacing != setvars_defaults["grid_x_spacing"]
            or plotvars.grid_y_spacing != setvars_defaults["grid_y_spacing"]
        )

    pyplot.ioff()
