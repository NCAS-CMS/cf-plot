"""
cf-plot: code-light plotting for earth science and aligned research

Documentation is hosted and found at: https://ncas-cms.github.io/cf-plot/
"""

from importlib.metadata import PackageNotFoundError, version as pkg_version
from pathlib import Path

__author__ = "Andy Heaps, Sadie Bartholomew, Bryan Lawrence"
__date__ = "16th May, 2026"


def _version_from_pyproject():
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if not pyproject.exists():
        return None

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

    return None


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

from .colorbar import cbar
from .colour import cscale
from .contour import con
from .contour import levs
from .layout_runtime import gclose, gopen, gset
from .layout_runtime import gpos
from .line import lineplot
from .map_runtime import mapset
from .state import plotvars, setvars
from .stipple import stipple
from .stream import stream
from .trajectory import traj
from .state import reset_runtime_state
from .utility import gvals as _gvals_impl, mapaxis as _mapaxis_impl, regrid
from .vector import vect
from .rotated_runtime import _render_rotated_grid_axes


def reset():
    gset()
    cscale()
    levs()
    mapset()
    setvars()
    reset_runtime_state()


def _gvals(*args, **kwargs):
    return _gvals_impl(*args, **kwargs)


def rgaxes(*, xpole=None, ypole=None, xvec=None, yvec=None, xticks=None, xticklabels=None, yticks=None, yticklabels=None, axes=True, xaxis=True, yaxis=True, xlabel=None, ylabel=None):
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
    return _mapaxis_impl(
        min_val=min,
        max_val=max,
        axis_type=type,
        degsym=bool(plotvars.degsym),
    )


__all__ = [
    "cbar",
    "con",
    "cscale",
    "gclose",
    "gopen",
    "gpos",
    "gset",
    "levs",
    "lineplot",
    "mapset",
    "plotvars",
    "regrid",
    "reset",
    "rgaxes",
    "setvars",
    "stipple",
    "stream",
    "traj",
    "vect",
    "_gvals",
    "_mapaxis",
]
