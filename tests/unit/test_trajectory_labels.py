import numpy as np

import cfplot as cfp
import cfplot.trajectory as trajectory_module


def setup_function():
    cfp.reset()


def teardown_function():
    cfp.reset()


class _FakeConstruct:
    def __init__(self, values):
        self.array = np.array(values, dtype=float)

    def nc_get_variable(self, default=False):
        return default


class _FakeField:
    def __init__(self):
        self.ndim = 1
        self.DSG = False
        self.array = np.array([1.0, 2.0, 3.0], dtype=float)
        self._constructs = {
            "lon": _FakeConstruct([0.0, 10.0, 20.0]),
            "lat": _FakeConstruct([40.0, 42.0, 44.0]),
        }

    def auxiliary_coordinates(self):
        return ["lon", "lat"]

    def construct(self, dim):
        return self._constructs[dim]


class _FakeMap:
    def plot(self, *args, **kwargs):
        return None

    def scatter(self, *args, **kwargs):
        return None

    def add_feature(self, *args, **kwargs):
        return None

    def text(self, *args, **kwargs):
        return None

    def arrow(self, *args, **kwargs):
        return None


def test_traj_preserves_user_axis_labels(monkeypatch):
    captured = {}

    monkeypatch.setattr(trajectory_module.cf, "Field", _FakeField)
    monkeypatch.setattr(trajectory_module.cf, "FieldList", tuple)
    monkeypatch.setattr(
        trajectory_module.utility,
        "cf_var_name",
        lambda field, dim: "longitude" if dim == "lon" else "latitude",
    )

    def fake_ensure_map_axes():
        cfp.plotvars.mymap = _FakeMap()

    def fake_apply_map_axes_with_toggles(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        trajectory_module,
        "_ensure_map_axes",
        fake_ensure_map_axes,
    )
    monkeypatch.setattr(
        trajectory_module,
        "_apply_map_axes_with_toggles",
        fake_apply_map_axes_with_toggles,
    )
    monkeypatch.setattr(
        trajectory_module,
        "ensure_runtime_session",
        lambda *a, **k: True,
    )
    monkeypatch.setattr(
        trajectory_module,
        "finalize_runtime_session",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(trajectory_module, "gset", lambda *a, **k: None)

    cfp.traj(_FakeField(), xlabel="Custom X", ylabel="Custom Y")

    assert captured["user_xlabel"] == "Custom X"
    assert captured["user_ylabel"] == "Custom Y"
