"""Runtime layout/axes operations for refactored contour rendering.

These helpers keep stateful calls to legacy cfplot plot orchestration out of
contour.py while preserving behaviour.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any

import matplotlib
import matplotlib.pyplot as plot

from .state import plotvars, reset_runtime_state


def gopen(
    rows: int = 1,
    columns: int = 1,
    user_plot: int = 1,
    file: str = "cfplot.png",
    orientation: str = "landscape",
    figsize: list[float] | tuple[float, float] = (11.7, 8.3),
    dpi: float | None = None,
    user_position: bool = False,
    left: float | None = None,
    right: float | None = None,
    top: float | None = None,
    bottom: float | None = None,
    wspace: float | None = None,
    hspace: float | None = None,
    animation_session_id: str | None = None,
    animation_meta_callback: Any = None,
    animation_frame_callback: Any = None,
) -> None:
    """Open a graphics file to contain plots.

    Parameter breakdown (see below for full detail). The following parameters:
        - configure the plot layout:
            - ``rows``, ``columns``, ``user_plot``
        - configure the output file and figure:
            - ``file``, ``orientation``, ``figsize``, ``dpi``
        - configure figure margins and subplot spacing:
            - ``left``, ``right``, ``top``, ``bottom``, ``wspace``,
              ``hspace``
        - control user-defined plot positioning:
            - ``user_position``
        - configure animation session integration:
            - ``animation_session_id``, ``animation_meta_callback``,
              ``animation_frame_callback``

    Args:
        rows: Number of plot rows on the page.
        columns: Number of plot columns on the page.
        user_plot: Internal plot variable. Do not use.

        file: Default output file name. Defaults to ``'cfplot.png'``.
        orientation: Figure orientation. Options are ``'landscape'`` and
            ``'portrait'``. Defaults to ``'landscape'``.
        figsize: Figure size in inches, specified as a list or tuple of
            two values. Defaults to ``(11.7, 8.3)``.
        dpi: Resolution in dots per inch.

        user_position: If ``True``, allow the plot position to be supplied
            via ``gpos``. Defaults to ``False``.

        left: Left margin in normalised coordinates. Defaults to ``0.12``.
        right: Right margin in normalised coordinates. Defaults to ``0.92``.
        top: Top margin in normalised coordinates. Defaults to ``0.08``.
        bottom: Bottom margin in normalised coordinates. Defaults to
            ``0.08``.
        wspace: Width reserved for blank space between subplots. Defaults
            to ``0.2``.
        hspace: Height reserved for white space between subplots. Defaults
            to ``0.2``.

        animation_session_id: Identifier for the animation session.
        animation_meta_callback: Callback for providing animation metadata.
        animation_frame_callback: Callback for handling animation frames.

    Returns:
        None
    """
    plotvars.rows = rows
    plotvars.columns = columns
    if file != "cfplot.png":
        plotvars.file = file
    plotvars.orientation = orientation

    _open_figure(
        user_plot=user_plot,
        figsize=figsize,
        orientation=orientation,
        left=left,
        right=right,
        top=top,
        bottom=bottom,
        wspace=wspace,
        hspace=hspace,
        dpi=dpi,
        user_position=user_position,
    )

    plotvars.runtime._animation_session_id = (
        "" if animation_session_id is None else str(animation_session_id)
    )
    plotvars.runtime._animation_meta_callback = animation_meta_callback
    plotvars.runtime._animation_frame_callback = animation_frame_callback
    plotvars.runtime._animation_meta_emitted = False
    plotvars.runtime._animation_frame_index = 0

    plotvars._contour_session_open = True


def gclose(view: bool = True) -> None:
    """Close a plot graphics file and save and/or view the output.

    Args:
        view: If ``True``, view the graphics file after saving. Set to
            ``False`` to disable viewing. Defaults to ``True``.

    Returns:
        None
    """
    plotvars.user_plot = 0

    interactive = bool(globals().get("__IPYTHON__", False))

    if matplotlib.is_interactive():
        interactive = True

    saveargs = {}
    if plotvars.tight:
        saveargs = {"bbox_inches": "tight"}

    file = plotvars.file
    figure = plotvars.master_plot or getattr(plotvars.plot, "figure", None)
    if figure is not None and file is not None:
        if os.path.splitext(file)[1].lower() not in (
            ".ps",
            ".eps",
            ".png",
            ".pdf",
        ):
            file = file + ".png"
        figure.savefig(
            file,
            orientation=plotvars.orientation,
            dpi=plotvars.dpi,
            **saveargs,
        )
        plot.close(figure)
    elif figure is not None:
        if view and plotvars.viewer == "display" and not interactive:
            disp = shutil.which("display")
            if disp is not None:
                tfile = "cfplot.png"
                figure.savefig(
                    tfile,
                    orientation=plotvars.orientation,
                    dpi=plotvars.dpi,
                    **saveargs,
                )
                matplotlib.pyplot.ioff()
                subprocess.Popen([disp, tfile])
            else:
                plotvars.viewer = "matplotlib"

        if view and (plotvars.viewer == "matplotlib" or interactive):
            matplotlib.pyplot.ion()
            plot.show()
        elif not view:
            plot.close(figure)

    reset_runtime_state()


def maybe_autosave() -> None:
    """Auto-save/show and close when not inside an explicit gopen/gclose session."""
    session_open = bool(getattr(plotvars, "_contour_session_open", False))
    if not session_open:
        gclose(view=True)


def set_axis_visibility(
    axis: Any,
    *,
    axes: bool = True,
    xaxis: bool = True,
    yaxis: bool = True,
) -> None:
    """Explicitly hide or show axis ticks and tick labels."""
    if axis is None:
        return

    if not axes:
        xaxis = False
        yaxis = False

    if not xaxis:
        axis.set_xticks([])
        axis.set_xticklabels([])
        axis.tick_params(
            bottom=False, top=False, labelbottom=False, labeltop=False
        )

    if not yaxis:
        axis.set_yticks([])
        axis.set_yticklabels([])
        axis.tick_params(
            left=False, right=False, labelleft=False, labelright=False
        )


def ensure_runtime_session(pos: int = 1) -> bool:
    """Ensure an implicit plotting session and default subplot when needed.

    Returns True when a session is implicitly managed by the caller
    (i.e. `gopen` was auto-invoked because `plotvars.user_plot == 0`).
    """
    auto_session = plotvars.user_plot == 0
    if auto_session:
        gopen(user_plot=0)

    if plotvars.rows > 1 or plotvars.columns > 1:
        if plotvars.gpos_called is False:
            gpos(pos)

    return auto_session


def finalize_runtime_session(
    *,
    auto_session: bool,
    reset_limits: bool = False,
    reset_colour_scale: bool = False,
    view: bool = True,
) -> None:
    """Finalize an implicitly managed session.

    When `auto_session` is False this is a no-op so user-managed `gopen/gclose`
    flows are preserved.
    """
    if not auto_session:
        return

    if reset_limits:
        gset()

    if reset_colour_scale:
        from .colour import cscale

        cscale()

    gclose(view=view)


def ensure_xy_viewport() -> None:
    """Ensure a Cartesian viewport exists, matching legacy gopen/gpos behavior."""
    _reset_closed_figure_state()

    if plotvars.master_plot is None:
        _open_figure(user_plot=0)

    if plotvars.plot is None or (plotvars.rows > 1 or plotvars.columns > 1):
        if plotvars.gpos_called is False or plotvars.plot is None:
            _select_position(1)


def set_plot_limits(
    *,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    ylog: bool,
    user_gset: int,
) -> None:
    """Apply graph limits through legacy gset interface."""
    plotvars.user_gset = user_gset
    plotvars.xmin = xmin
    plotvars.xmax = xmax
    plotvars.ymin = ymin
    plotvars.ymax = ymax
    plotvars.ylog = ylog

    time_xstr = False
    time_ystr = False
    try:
        float(xmin)
    except Exception:
        time_xstr = True
    try:
        float(ymin)
    except Exception:
        time_ystr = True

    if plotvars.plot is not None and not time_xstr and not time_ystr:
        plotvars.plot.axis([xmin, xmax, ymin, ymax])

    if ylog and plotvars.plot is not None:
        plotvars.plot.set_yscale("log")


def gset(
    xmin=None,
    xmax=None,
    ymin=None,
    ymax=None,
    xlog=False,
    ylog=False,
    user_gset=1,
    twinx=None,
    twiny=None,
):
    """Set plot limits for non-longitude-latitude plots."""
    plotvars.user_gset = user_gset

    if all(val is None for val in [xmin, xmax, ymin, ymax]):
        plotvars.xmin = None
        plotvars.xmax = None
        plotvars.ymin = None
        plotvars.ymax = None
        plotvars.xlog = False
        plotvars.ylog = False
        plotvars.twinx = False
        plotvars.twiny = False
        plotvars.user_gset = 0
        return

    bcount = 0
    for val in [xmin, xmax, ymin, ymax]:
        if val is None:
            bcount = bcount + 1

    if bcount != 0 and bcount != 4:
        errstr = (
            "gset error\n"
            "xmin, xmax, ymin, ymax all need to be passed to gset\n"
            "to set the plot limits\n"
        )
        raise Warning(errstr)

    plotvars.xmin = xmin
    plotvars.xmax = xmax
    plotvars.ymin = ymin
    plotvars.ymax = ymax
    plotvars.xlog = xlog
    plotvars.ylog = ylog

    time_xstr = False
    time_ystr = False
    try:
        float(xmin)
    except Exception:
        time_xstr = True
    try:
        float(ymin)
    except Exception:
        time_ystr = True

    if plotvars.plot is not None and twinx is None and twiny is None:
        if not time_xstr and not time_ystr:
            plotvars.plot.axis(
                [plotvars.xmin, plotvars.xmax, plotvars.ymin, plotvars.ymax]
            )

        if plotvars.xlog:
            plotvars.plot.set_xscale("log")
        if plotvars.ylog:
            plotvars.plot.set_yscale("log")

    if twinx is not None:
        plotvars.twinx = twinx
    if twiny is not None:
        plotvars.twiny = twiny


def apply_axes(
    *,
    plot_type: int,
    xticks: Any,
    yticks: Any,
    xlabel: str | None,
    ylabel: str | None,
    xticklabels: Any | None,
    yticklabels: Any | None,
) -> None:
    """Apply axis labels/ticks through legacy axes handlers."""
    if plot_type == 1:
        from .map_runtime import _apply_map_axes

        _apply_map_axes(
            xticks=xticks,
            yticks=yticks,
            xlabel=xlabel,
            ylabel=ylabel,
            xticklabels=xticklabels,
            yticklabels=yticklabels,
        )
    else:
        _apply_xy_axes(
            xticks=xticks,
            xticklabels=xticklabels,
            yticks=yticks,
            yticklabels=yticklabels,
            xlabel=xlabel,
            ylabel=ylabel,
        )


def axes(
    xticks=None,
    xticklabels=None,
    yticks=None,
    yticklabels=None,
    xstep=None,
    ystep=None,
    xlabel=None,
    ylabel=None,
    title=None,
):
    """Set axes plotting parameters in shared state."""
    if all(
        val is None
        for val in [
            xticks,
            yticks,
            xticklabels,
            yticklabels,
            xstep,
            ystep,
            xlabel,
            ylabel,
            title,
        ]
    ):
        plotvars.xticks = None
        plotvars.yticks = None
        plotvars.xticklabels = None
        plotvars.yticklabels = None
        plotvars.xstep = None
        plotvars.ystep = None
        plotvars.xlabel = None
        plotvars.ylabel = None
        plotvars.title = None
        return

    plotvars.xticks = xticks
    plotvars.yticks = yticks
    plotvars.xticklabels = xticklabels
    plotvars.yticklabels = yticklabels
    plotvars.xstep = xstep
    plotvars.ystep = ystep
    plotvars.xlabel = xlabel
    plotvars.ylabel = ylabel
    plotvars.title = title


def _open_figure(
    user_plot: int = 0,
    *,
    figsize: list[float] | tuple[float, float] = (11.7, 8.3),
    orientation: str | None = None,
    left: float | None = None,
    right: float | None = None,
    top: float | None = None,
    bottom: float | None = None,
    wspace: float | None = None,
    hspace: float | None = None,
    dpi: float | None = None,
    user_position: bool = False,
) -> None:
    """Open a contour-owned figure and apply legacy-default layout."""
    if orientation is None:
        orientation = plotvars.orientation

    if orientation == "portrait":
        figshape = (figsize[1], figsize[0])
    elif orientation == "landscape":
        figshape = (figsize[0], figsize[1])
    else:
        raise Warning(
            "gopen error\n"
            "orientation incorrectly set\n"
            f"input value was {orientation}\n"
            "Valid options are portrait or landscape\n"
        )

    plotvars.master_plot = plot.figure(figsize=figshape)

    if left is None:
        left = 0.12
    if right is None:
        right = 0.92
    if top is None:
        top = 0.95
    if bottom is None:
        bottom = 0.1 if plotvars.rows >= 3 else 0.08
    if wspace is None:
        wspace = 0.2
    if hspace is None:
        hspace = 0.5 if plotvars.rows >= 3 else 0.2

    plotvars.master_plot.subplots_adjust(
        left=left,
        right=right,
        top=top,
        bottom=bottom,
        wspace=wspace,
        hspace=hspace,
    )

    plotvars.user_plot = user_plot
    plotvars.gpos_called = False
    plotvars.plot_xmin = None
    plotvars.plot_xmax = None
    plotvars.plot_ymin = None
    plotvars.plot_ymax = None

    if dpi is not None:
        plotvars.dpi = dpi

    if not user_position and plotvars.rows == 1 and plotvars.columns == 1:
        _select_position(1)

    if plotvars.columns > 2 or plotvars.rows > 2:
        matplotlib.rcParams["xtick.major.size"] = 2
        matplotlib.rcParams["ytick.major.size"] = 2


def _select_position(pos: int) -> None:
    """Select subplot position in the contour-owned figure state."""
    _reset_closed_figure_state()

    if plotvars.master_plot is None:
        _open_figure(user_plot=0)

    max_pos = plotvars.rows * plotvars.columns
    if pos < 1 or pos > max_pos:
        raise Warning(
            "pos error - pos out of range:\n"
            f" range = 1 - {max_pos}\n"
            f" input pos was {pos}\n"
        )

    user_pos = all(
        value is not None
        for value in [
            plotvars.plot_xmin,
            plotvars.plot_xmax,
            plotvars.plot_ymin,
            plotvars.plot_ymax,
        ]
    )

    if not user_pos:
        plotvars.plot = plotvars.master_plot.add_subplot(
            plotvars.rows, plotvars.columns, pos
        )
    else:
        delta_x = plotvars.plot_xmax - plotvars.plot_xmin
        delta_y = plotvars.plot_ymax - plotvars.plot_ymin
        plotvars.plot = plotvars.master_plot.add_axes(
            [plotvars.plot_xmin, plotvars.plot_ymin, delta_x, delta_y]
        )

    plotvars.plot.tick_params(
        which="both", direction="out", right=True, top=True
    )
    plotvars.pos = pos
    plotvars.gpos_called = True
    plotvars.mymap = None
    plotvars.graph_xmin = None
    plotvars.graph_xmax = None
    plotvars.graph_ymin = None
    plotvars.graph_ymax = None
    plotvars.titles_con_called = False

    if plotvars.user_levs == 0:
        from .contour import levs

        if plotvars.levels_step is None:
            levs()
        else:
            levs(step=plotvars.levels_step)


def _reset_closed_figure_state() -> None:
    """Drop stale figure/axes handles after a window has been closed."""
    figure = plotvars.master_plot
    if figure is None:
        return

    try:
        alive = matplotlib.pyplot.fignum_exists(figure.number)
    except Exception:
        alive = False

    if alive:
        return

    plotvars.master_plot = None
    plotvars.plot = None
    plotvars.mymap = None
    plotvars.gpos_called = False


def gpos(
    pos: int = 1,
    xmin: float | int | None = None,
    xmax: float | int | None = None,
    ymin: float | int | None = None,
    ymax: float | int | None = None,
) -> None:
    """Set subplot position, starting at 1 for the top-left position.

    Plots start at the top left and increase by one for each plot to the
    right. When the end of the row has been reached, the next plot will be
    the leftmost plot on the next row down.

    To obtain full control over the plot position, all of the parameters
    ``xmin``, ``xmax``, ``ymin`` and ``ymax`` can be specified (all four
    are required, if any are given). In addition, ``cfp.gopen`` must
    have the ``user_position=True`` parameter set if these are specified.

    Args:
        pos (int): Plot position, an integer starting at ``1``. For ``1``
            plots at the top left and for the next integer up will plot
            the next subplot to the right, continuing to the next row
            down once the end of the row is reached. Defaults to ``1``.

        xmin (float | int | None, optional): Minimum x-coordinate in
            normalised coordinates. Defaults to ``None``.
        xmax (float | int | None, optional): Maximum x-coordinate in
            normalised coordinates. Defaults to ``None``.
        ymin (float | int | None, optional): Minimum y-coordinate in
            normalised coordinates. Defaults to ``None``.
        ymax (float | int | None, optional): Maximum y-coordinate in
            normalised coordinates. Defaults to ``None``.

    Returns:
        None

    Raises:
        ValueError: If only some of ``xmin``, ``xmax``, ``ymin`` and
            ``ymax`` are specified.
    """
    coord_extrema = [xmin, xmax, ymin, ymax]
    # 'not None' to distinguish None and 0.0 position
    if all(val is not None for val in coord_extrema):
        plotvars.plot_xmin = xmin
        plotvars.plot_xmax = xmax
        plotvars.plot_ymin = ymin
        plotvars.plot_ymax = ymax
    elif any(val is not None for val in coord_extrema):
        raise ValueError(
            "Must specify all four coordinates (xmin, xmax, ymin, ymax) "
            "or leave all four as None. Got values of "
            f"xmin, xmax, ymin, ymax: {xmin, xmax, ymin, ymax}"
        )

    _select_position(pos)


def _apply_xy_axes(
    *,
    xticks: Any,
    xticklabels: Any | None,
    yticks: Any,
    yticklabels: Any | None,
    xlabel: str | None,
    ylabel: str | None,
) -> None:
    """Apply simple Cartesian axes labels and ticks."""
    if plotvars.plot is None:
        return

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

    if xticks is not None:
        plotvars.plot.set_xticks(xticks)
        plotvars.plot.set_xticklabels(
            xticklabels if xticklabels is not None else xticks,
            rotation=plotvars.xtick_label_rotation,
            horizontalalignment=plotvars.xtick_label_align,
        )

    if yticks is not None:
        plotvars.plot.set_yticks(yticks)
        plotvars.plot.set_yticklabels(
            yticklabels if yticklabels is not None else yticks,
            rotation=plotvars.ytick_label_rotation,
            horizontalalignment=plotvars.ytick_label_align,
        )

    for label in plotvars.plot.xaxis.get_ticklabels():
        label.set_fontsize(plotvars.axis_label_fontsize)
        label.set_fontweight(plotvars.axis_label_fontweight)
    for label in plotvars.plot.yaxis.get_ticklabels():
        label.set_fontsize(plotvars.axis_label_fontsize)
        label.set_fontweight(plotvars.axis_label_fontweight)
