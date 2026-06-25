import numpy as np

from cfplot import contour


class _FakeConstruct:
    def __init__(self, values, dtvalues=None):
        self.array = np.asarray(values)
        self.dtarray = None if dtvalues is None else np.asarray(dtvalues, dtype=object)


class _FakeField:
    def __init__(self, constructs):
        self._constructs = constructs

    def has_construct(self, key):
        return key in self._constructs

    def construct(self, key):
        return self._constructs[key]


def test_infer_animation_axis_auto_uses_non_ptype_singleton(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "T"])

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36)),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19)),
            "T": _FakeConstruct([1]),
        }
    )

    axis = contour._infer_animation_axis(f=f, axis_spec="auto", ptype=1)

    assert axis == "T"


def test_infer_animation_axis_auto_none_when_non_ptype_not_singleton(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "Z"])

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36)),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19)),
            "Z": _FakeConstruct([1000, 850, 500]),
        }
    )

    axis = contour._infer_animation_axis(f=f, axis_spec="auto", ptype=1)

    assert axis is None


def test_infer_animation_axis_ptype0_fallback_prefers_t(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "T"])

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36)),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19)),
            "T": _FakeConstruct([1]),
        }
    )

    axis = contour._infer_animation_axis(f=f, axis_spec="auto", ptype=0)

    assert axis == "T"


def test_resolve_animation_title_uses_template(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "T"])
    monkeypatch.setattr(contour.utility, "cf_var_name_titles", lambda f, dim: ("time", None))

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36)),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19)),
            "T": _FakeConstruct([1], dtvalues=["2001-01-15 00:00:00"]),
        }
    )

    title = contour._resolve_animation_title(
        f=f,
        base_title="Temperature",
        animation=True,
        animation_axis="auto",
        ptype=1,
        animation_title_template="{title} [{frame}]",
    )

    assert title == "Temperature [time: 2001-01-15 00:00:00]"
