"""
cf-plot: code-light plotting for earth science and aligned research

Documentation is hosted and found at: https://ncas-cms.github.io/cf-plot/
"""

from .colorbar import cbar
from .colour import cscale
from .contour import con, levs
from .layout_runtime import axes, gclose, gfigure, gopen, gpos, gset
from .line import lineplot, scatter
from .map_runtime import mapset
from .rotated_runtime import _render_rotated_grid_axes
from .state import plotvars, reset_runtime_state, setvars
from .stipple import stipple
from .stream import stream
from .trajectory import traj
from .utility import (
    add_cyclic,
    calculate_levels,
    cf_var_name,
    cf_var_name_titles,
    find_dim_names,
    find_z,
    fix_floats,
    generate_titles,
)
from .utility import gvals as _gvals_impl
from .utility import mapaxis as _mapaxis_impl
from .utility import ndecs, polar_regular_grid, regrid, stipple_points
from .validate import check_well_formed, orca_check
from .vector import axes_plot, vect

__author__ = "Andy Heaps, Sadie Bartholomew, Bryan Lawrence"
__maintainer__ = "Sadie Bartholomew"
__date__ = "2026-10-09"


from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path


def _version_from_pyproject():
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if not pyproject.exists():
        return

    in_project = False
    for raw_line in pyproject.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_project = line == "[project]"
            continue
        if in_project and line.startswith("version"):
            _, _, value = line.partition("=")
            return value.strip().strip('"').strip("'")

    return


def _resolve_version():
    # In a source checkout, pyproject.toml is the version source of truth.
    pyproject_version = _version_from_pyproject()
    if pyproject_version:
        return pyproject_version

    # In installed-package contexts, use distribution metadata.
    try:
        return pkg_version("cf-plot")
    except PackageNotFoundError:
        return "0+unknown"


__version__ = _resolve_version()


def reset():
    """Reset plotting state to the default configuration."""
    gset()
    cscale()
    levs()
    mapset()
    setvars()
    reset_runtime_state()


def _gvals(*args, **kwargs):
    """Work out a sensible set of values between two limits."""
    return _gvals_impl(*args, **kwargs)


def rgaxes(
    *,
    xpole=None,
    ypole=None,
    xvec=None,
    yvec=None,
    xticks=None,
    xticklabels=None,
    yticks=None,
    yticklabels=None,
    axes=True,
    xaxis=True,
    yaxis=True,
    xlabel=None,
    ylabel=None,
):
    """Label rotated grid plots."""
    return _render_rotated_grid_axes(
        xpole=xpole,
        ypole=ypole,
        xvec=xvec,
        yvec=yvec,
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


def _mapaxis(min=None, max=None, type=None):
    """Work out a sensible set of lon-lat tick marks and labels."""
    return _mapaxis_impl(
        min_val=min,
        max_val=max,
        axis_type=type,
        degsym=bool(plotvars.degsym),
    )


__all__ = [
    "_gvals",  # Req'd for public API?
    "_mapaxis",  # Req'd for public API?
    "add_cyclic",
    "axes",
    "axes_plot",
    "calculate_levels",
    "cbar",
    "cf_var_name",
    "cf_var_name_titles",
    "check_well_formed",
    "con",
    "cscale",
    "find_dim_names",
    "find_z",
    "fix_floats",
    "gclose",
    "generate_titles",
    "gfigure",
    "gopen",
    "gpos",
    "gset",
    "levs",
    "lineplot",
    "mapset",
    "ndecs",
    "orca_check",
    "plotvars",
    "polar_regular_grid",
    "regrid",
    "reset",
    "rgaxes",
    "scatter",
    "setvars",
    "stipple",
    "stipple_points",
    "stream",
    "traj",
    "vect",
]
