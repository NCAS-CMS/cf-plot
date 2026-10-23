import inspect
from pathlib import Path
from types import SimpleNamespace

import cf
import contourpy
import numpy as np
import pytest

from cfplot import blockfill, contour, layout_runtime


def test_con_delegates_to_legacy(monkeypatch):
    monkeypatch.setattr(
        "cfplot.contour._can_use_new_xy_path", lambda f, kwargs: False
    )

    with pytest.raises(NotImplementedError, match="not implemented"):
        contour.con(f=np.array([[1.0, 2.0], [3.0, 4.0]]), lines=False)


def test_colour_scale_label_skip():
    cs = contour.ColourScale(plotvars=object())

    labels = cs.colourbar_labels(
        levels=np.array([0, 1, 2, 3]),
        orientation="horizontal",
        n_columns=1,
        label_skip=2,
        custom_labels=None,
    )

    assert labels == ["0", "", "2", ""]


def test_con_uses_new_path_when_available(monkeypatch):
    monkeypatch.setattr(
        "cfplot.contour._can_use_new_xy_path", lambda f, kwargs: True
    )
    monkeypatch.setattr(
        "cfplot.contour._render_with_new_xy",
        lambda f, x, y, kwargs: True,
    )

    out = contour.con(f=np.array([[1.0, 2.0], [3.0, 4.0]]))

    assert out is None


def test_con_falls_back_when_new_path_declines(monkeypatch):
    monkeypatch.setattr(
        "cfplot.contour._can_use_new_xy_path", lambda f, kwargs: True
    )
    monkeypatch.setattr(
        "cfplot.contour._render_with_new_xy",
        lambda f, x, y, kwargs: False,
    )

    with pytest.raises(NotImplementedError, match="not implemented"):
        contour.con(f=np.array([[1.0, 2.0], [3.0, 4.0]]), lines=False)


def test_maybe_autosave_calls_gclose(monkeypatch):
    calls: list[bool] = []

    monkeypatch.setattr(
        layout_runtime.plotvars, "_contour_session_open", False
    )
    monkeypatch.setattr(
        layout_runtime, "gclose", lambda view=True: calls.append(view)
    )

    layout_runtime.maybe_autosave()

    assert calls == [True]


def test_maybe_autosave_skips_when_session_open(monkeypatch):
    calls: list[bool] = []

    monkeypatch.setattr(layout_runtime.plotvars, "_contour_session_open", True)
    monkeypatch.setattr(
        layout_runtime, "gclose", lambda view=True: calls.append(view)
    )

    layout_runtime.maybe_autosave()

    assert calls == []


def test_blockfill_signature_does_not_advertise_lonlat():
    params = inspect.signature(blockfill._bfill).parameters

    assert "lonlat" not in params


def test_curvilinear_defaults_enable_fast_blockfill_and_disable_lines():
    data = contour.ContourData(
        field=np.ones((3, 4)),
        x=np.ones((3, 4)),
        y=np.ones((3, 4)),
        ptype=1,
    )

    fill, lines, blockfill, blockfill_fast = contour._resolve_curvilinear_render_defaults(
        data=data,
        kwargs={},
        fill=True,
        lines=True,
        blockfill=False,
        blockfill_fast=None,
    )

    assert fill is False
    assert lines is False
    assert blockfill is True
    assert blockfill_fast is True


def test_curvilinear_defaults_respect_explicit_user_choices():
    data = contour.ContourData(
        field=np.ones((3, 4)),
        x=np.ones((3, 4)),
        y=np.ones((3, 4)),
        ptype=1,
    )

    fill, lines, blockfill, blockfill_fast = contour._resolve_curvilinear_render_defaults(
        data=data,
        kwargs={"blockfill": False, "lines": True},
        fill=True,
        lines=True,
        blockfill=False,
        blockfill_fast=None,
    )

    assert fill is True
    assert lines is True
    assert blockfill is False
    assert blockfill_fast is None


@pytest.mark.parametrize("axis", [0, 1])
def test_curvilinear_contours_mask_both_sides_of_seam(axis):
    x = np.tile([178.0, 179.0, -179.0, -178.0], (4, 1))
    if axis == 0:
        x = x.T
    field = np.ma.array(np.ones((4, 4)), mask=False)
    field.mask[0, 0] = True
    data = contour.ContourData(
        field=field, x=x, y=np.ones((4, 4)), ptype=1
    )

    result = contour._mask_curvilinear_contour_seams(data)

    expected = np.zeros((4, 4), dtype=bool)
    if axis == 0:
        expected[1:3, :] = True
    else:
        expected[:, 1:3] = True
    expected[0, 0] = True
    np.testing.assert_array_equal(result.mask, expected)
    np.testing.assert_array_equal(result.data, field.data)
    assert np.ma.count_masked(field) == 1


@pytest.mark.parametrize("curvilinear", [False, True])
def test_contour_seam_mask_preserves_continuous_grids(curvilinear):
    field = np.arange(12.0).reshape(3, 4)
    x, y = np.arange(4.0), np.arange(3.0)
    if curvilinear:
        x, y = np.meshgrid(x, y)
    data = contour.ContourData(field=field, x=x, y=y, ptype=1)

    result = contour._mask_curvilinear_contour_seams(data)

    np.testing.assert_array_equal(result, field)
    assert np.ma.count_masked(result) == 0


def test_map_renderers_use_seam_mask_for_fill_lines_and_zero(monkeypatch):
    calls = []

    def record(x, y, field, levels, **kwargs):
        calls.append(field)
        return SimpleNamespace()

    monkeypatch.setattr(
        contour.plotvars.runtime,
        "mymap",
        SimpleNamespace(contourf=record, contour=record),
    )
    data = contour.ContourData(
        field=np.ones((3, 4)),
        x=np.tile([178.0, 179.0, -179.0, -178.0], (3, 1)),
        y=np.tile(np.arange(3.0)[:, None], (1, 4)),
        ptype=1,
        levels=np.array([-1.0, 0.0, 1.0]),
        fmult=2,
    )
    renderer = contour.MapContourRenderer(
        layout=None,
        data=data,
        colour_scale=SimpleNamespace(get_cmap=lambda: None),
    )

    renderer.render_filled(alpha=1, zorder=1, transform_first=False)
    renderer.render_lines(
        colors="k",
        linewidths=None,
        linestyles=None,
        line_labels=False,
        zero_thick=3,
    )

    assert len(calls) == 3
    for field in calls:
        np.testing.assert_array_equal(field.mask[:, 1:3], True)
        np.testing.assert_array_equal(field.compressed(), 2.0)
    assert np.ma.count_masked(data.field) == 0


def test_map_blockfill_does_not_apply_contour_seam_mask(monkeypatch):
    calls = []
    monkeypatch.setattr(
        contour, "_bfill", lambda **kwargs: calls.append(kwargs["f"])
    )
    data = contour.ContourData(
        field=np.ones((3, 4)),
        x=np.tile([178.0, 179.0, -179.0, -178.0], (3, 1)),
        y=np.ones((3, 4)),
        ptype=1,
        levels=np.array([0.0, 1.0]),
    )
    renderer = contour.MapContourRenderer(
        layout=None, data=data, colour_scale=None
    )

    renderer.render_blockfill(fast=True, alpha=1, zorder=1)

    assert len(calls) == 1
    assert np.ma.count_masked(calls[0]) == 0
    np.testing.assert_array_equal(calls[0], data.field)


@pytest.mark.parametrize("filled", [False, True])
def test_nemo_contours_do_not_interpolate_across_longitude_seam(filled):
    path = Path(__file__).parents[1] / "data" / "nemo_eg260916.nc"
    data = contour.ContourData.from_cf_field(cf.read(str(path))[0], None)
    field = contour._mask_curvilinear_contour_seams(data)
    levels = np.array([0.5, 1.5, 2.5, 3.5]) * 1e-4

    def longest_edge(values):
        generator = contourpy.contour_generator(
            x=data.x, y=data.y, z=values, corner_mask=True
        )
        if filled:
            paths = []
            for lower, upper in zip(levels[:-1], levels[1:]):
                vertices, offsets = generator.filled(lower, upper)
                for points, boundaries in zip(vertices, offsets):
                    paths.extend(
                        points[start:end]
                        for start, end in zip(
                            boundaries[:-1], boundaries[1:]
                        )
                    )
        else:
            paths = [
                path for level in levels for path in generator.lines(level)
            ]
        return max(
            np.max(np.abs(np.diff(path[:, 0])))
            for path in paths
            if len(path) > 1
        )

    assert longest_edge(data.field) > 300.0
    assert longest_edge(field) < 180.0
