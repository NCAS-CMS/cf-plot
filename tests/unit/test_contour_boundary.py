import inspect

import numpy as np
import pytest

from cfplot import blockfill
from cfplot import contour
from cfplot import layout_runtime


def test_con_delegates_to_legacy(monkeypatch):
    monkeypatch.setattr("cfplot.contour._can_use_new_xy_path", lambda f, kwargs: False)

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
    monkeypatch.setattr("cfplot.contour._can_use_new_xy_path", lambda f, kwargs: True)
    monkeypatch.setattr(
        "cfplot.contour._render_with_new_xy",
        lambda f, x, y, kwargs: True,
    )

    out = contour.con(f=np.array([[1.0, 2.0], [3.0, 4.0]]))

    assert out is None


def test_con_falls_back_when_new_path_declines(monkeypatch):
    monkeypatch.setattr("cfplot.contour._can_use_new_xy_path", lambda f, kwargs: True)
    monkeypatch.setattr(
        "cfplot.contour._render_with_new_xy",
        lambda f, x, y, kwargs: False,
    )

    with pytest.raises(NotImplementedError, match="not implemented"):
        contour.con(f=np.array([[1.0, 2.0], [3.0, 4.0]]), lines=False)


def test_maybe_autosave_calls_gclose(monkeypatch):
    calls: list[bool] = []

    monkeypatch.setattr(layout_runtime.plotvars, "_contour_session_open", False)
    monkeypatch.setattr(layout_runtime, "gclose", lambda view=True: calls.append(view))

    layout_runtime.maybe_autosave()

    assert calls == [True]


def test_maybe_autosave_skips_when_session_open(monkeypatch):
    calls: list[bool] = []

    monkeypatch.setattr(layout_runtime.plotvars, "_contour_session_open", True)
    monkeypatch.setattr(layout_runtime, "gclose", lambda view=True: calls.append(view))

    layout_runtime.maybe_autosave()

    assert calls == []


def test_blockfill_signature_does_not_advertise_lonlat():
    params = inspect.signature(blockfill._bfill).parameters

    assert "lonlat" not in params