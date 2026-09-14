import numpy as np

import cfplot as cfp
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


def setup_function():
    cfp.reset()


def teardown_function():
    cfp.reset()


def test_gopen_registers_animation_hooks(tmp_path):
    outfile = tmp_path / "animation_hooks.png"
    cfp.setvars(file=str(outfile), viewer="matplotlib")

    events = []

    cfp.gopen(
        animation_session_id="session-1",
        animation_meta_callback=lambda payload: events.append(("meta", payload)),
        animation_frame_callback=lambda payload: events.append(("frame", payload)),
    )

    runtime = cfp.plotvars.runtime
    assert runtime._animation_session_id == "session-1"
    assert callable(runtime._animation_meta_callback)
    assert callable(runtime._animation_frame_callback)
    assert runtime._animation_meta_emitted is False
    assert runtime._animation_frame_index == 0

    cfp.gclose(view=False)


def test_meta_and_frame_callbacks_emit_in_order(monkeypatch):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "T"])

    runtime = cfp.plotvars.runtime
    runtime._animation_session_id = "session-2"

    events = []
    runtime._animation_meta_callback = lambda payload: events.append(("meta", payload))
    runtime._animation_frame_callback = lambda payload: events.append(("frame", payload))
    runtime._animation_meta_emitted = False
    runtime._animation_frame_index = 0

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36)),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19)),
            "T": _FakeConstruct([1], dtvalues=["2001-01-01 00:00:00"]),
        }
    )

    contour._emit_animation_meta_callback(
        kwargs={
            "animation_reference": np.arange(5),
            "animation_axis": "auto",
            "animation_title_template": "{title} [{frame}]",
        },
        ptype=1,
        levels_locked=False,
    )
    contour._emit_animation_meta_callback(
        kwargs={
            "animation_reference": np.arange(5),
            "animation_axis": "auto",
        },
        ptype=1,
        levels_locked=False,
    )
    contour._emit_animation_frame_callback(
        f=f,
        ptype=1,
        kwargs={"animation_axis": "auto"},
    )

    assert len(events) == 2
    assert events[0][0] == "meta"
    assert events[1][0] == "frame"

    meta_payload = events[0][1]
    assert meta_payload["session_id"] == "session-2"
    assert meta_payload["total_frames"] == 5
    assert meta_payload["plot_kind"] == "contour"
    assert meta_payload["levels_locked"] is False

    frame_payload = events[1][1]
    assert frame_payload["session_id"] == "session-2"
    assert frame_payload["frame_index"] == 0
    assert frame_payload["frame_value"] == "2001-01-01 00:00:00"
    assert frame_payload["canvas_ready"] is True
    assert frame_payload["timestamp"] is not None


def test_callback_exceptions_are_logged_and_frame_index_advances(monkeypatch, caplog):
    monkeypatch.setattr(contour.cf, "Field", _FakeField)
    monkeypatch.setattr(contour.utility, "find_dim_names", lambda f: ["X", "Y", "T"])

    runtime = cfp.plotvars.runtime
    runtime._animation_session_id = "session-3"
    runtime._animation_meta_callback = None
    runtime._animation_frame_callback = lambda payload: (_ for _ in ()).throw(
        RuntimeError("boom")
    )
    runtime._animation_meta_emitted = True
    runtime._animation_frame_index = 0

    f = _FakeField(
        {
            "X": _FakeConstruct(np.linspace(0, 350, 36)),
            "Y": _FakeConstruct(np.linspace(-90, 90, 19)),
            "T": _FakeConstruct([1]),
        }
    )

    with caplog.at_level("ERROR"):
        contour._emit_animation_frame_callback(
            f=f,
            ptype=1,
            kwargs={"animation_axis": "auto"},
        )

    assert "animation callback failed" in caplog.text
    assert runtime._animation_frame_index == 1
