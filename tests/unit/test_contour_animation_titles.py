import numpy as np

from cfplot import contour


class _FakeConstruct:
    def __init__(self, values, dtvalues=None, *, name=None, **flags):
        self.array = np.asarray(values)
        self.dtarray = None if dtvalues is None else np.asarray(dtvalues, dtype=object)
        self.name = name
        self.T = bool(flags.get("T", False))
        self.Z = bool(flags.get("Z", False))
        self.Y = bool(flags.get("Y", False))
        self.X = bool(flags.get("X", False))

    def identity(self, default=None):
        return self.name or default


class _FakeField:
    def __init__(self, constructs):
        self._constructs = constructs

    def has_construct(self, key):
        if key in self._constructs:
            return True
        return any(getattr(construct, "identity", lambda default=None: None)(None) == key for construct in self._constructs.values())

    def construct(self, key):
        if key in self._constructs:
            return self._constructs[key]
        for construct in self._constructs.values():
            identity = getattr(construct, "identity", lambda default=None: None)(None)
            if identity == key:
                return construct
        return self._constructs[key]


def test_infer_animation_axis_auto_uses_non_ptype_singleton(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "T"])

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36), name="longitude", X=True),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19), name="latitude", Y=True),
            "T": _FakeConstruct([1], name="time", T=True),
        }
    )

    axis = contour._infer_animation_axis(f=f, axis_spec="auto", ptype=1)

    assert axis == "time"


def test_infer_animation_axis_auto_none_when_non_ptype_not_singleton(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "Z"])

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36), name="longitude", X=True),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19), name="latitude", Y=True),
            "Z": _FakeConstruct([1000, 850, 500], name="model_level_number", Z=True),
        }
    )

    axis = contour._infer_animation_axis(f=f, axis_spec="auto", ptype=1)

    assert axis is None


def test_infer_animation_axis_ptype0_fallback_prefers_t(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "T"])

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36), name="longitude", X=True),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19), name="latitude", Y=True),
            "T": _FakeConstruct([1], name="time", T=True),
        }
    )

    axis = contour._infer_animation_axis(f=f, axis_spec="auto", ptype=0)

    assert axis == "time"


def test_resolve_animation_title_uses_template(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "T"])
    monkeypatch.setattr(contour.utility, "cf_var_name_titles", lambda f, dim: ("time", None))

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36), name="longitude", X=True),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19), name="latitude", Y=True),
            "T": _FakeConstruct([1], dtvalues=["2001-01-15 00:00:00"], name="time", T=True),
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


def test_infer_animation_axis_accepts_explicit_identity(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)

    f = _FakeField(
        {
            "time": _FakeConstruct([1, 2, 3], name="time", T=True),
            "latitude": _FakeConstruct(np.linspace(-90, 90, 19), name="latitude", Y=True),
            "longitude": _FakeConstruct(np.linspace(0, 350, 36), name="longitude", X=True),
        }
    )

    axis = contour._infer_animation_axis(f=f, axis_spec="time", ptype=1)

    assert axis == "time"
