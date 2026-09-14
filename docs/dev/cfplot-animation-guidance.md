# cf-plot Animation Hook Guidance

This document is a cf-plot-only implementation guide for animation callbacks.

## Scope

In scope:

- Add callback hooks to the contour animation path.
- Preserve existing contour animation behavior and outputs.
- Keep current frame-writing workflows unchanged.

Out of scope:

- Worker transport protocol details.
- GUI session and playback behavior.
- Any semantic changes to contour logic, level handling, or map behavior.

## Compatibility contract

1. Existing behavior remains the default.
- If no new callback kwargs are provided, output and side effects must match current behavior.

2. Existing file-output workflows remain intact.
- Current options that write frame sequences must continue to do so.
- Callback hooks are additive only and must not disable, reorder, or replace writes.

3. Existing con animation kwargs keep current meaning.
- ptype
- animation
- animation_reference
- reuse_map_background
- clear_previous_frame
- animation_axis
- animation_title_template
- lines

## API additions

Add these optional kwargs to cfp.gopen only:

- animation_session_id
- animation_meta_callback
- animation_frame_callback

No new kwargs are required on cfp.con for v1.

Recommended usage shape:

```python
cfp.gopen(
    file="cfplot.png",
    user_plot=1,
    animation_session_id=session_id,
    animation_frame_callback=on_frame,
    animation_meta_callback=on_meta,
)

cfp.con(
    frame,
    ptype=1,
    animation=True,
    animation_reference=f,
    reuse_map_background=True,
    clear_previous_frame=True,
    animation_axis="auto",
    animation_title_template="{title} [{frame}]",
    lines=False,
)
```

## Callback contracts

### Meta callback

Called once before the first frame callback (or as soon as metadata is known).

Required payload keys:

- session_id: str
- total_frames: int | None
- fps_hint: float | None
- title_template: str | None
- plot_kind: str  # contour
- levels_locked: bool

### Frame callback

Called after each frame has been fully drawn.

Required payload keys:

- session_id: str
- frame_index: int  # 0-based
- frame_value: object | None
- canvas_ready: bool  # true
- timestamp: float

## Callback placement and ordering

Callbacks should be stored in gopen state and used only in the con animation branch.

Required control flow:

1. Enter con.
2. If animation is false, run existing static contour path unchanged.
3. If animation is true:
- Resolve animation frames using existing logic.
- Build metadata once known.
- Invoke animation_meta_callback(meta) once before first frame draw.
4. For each frame:
- Apply existing per-frame state updates.
- Perform existing draw/render.
- Perform existing frame-on-disk write behavior when configured.
- Invoke animation_frame_callback(frame_event).
5. Exit with existing return behavior unchanged.

Hard constraints:

- Meta callback must happen before first frame callback.
- Frame callback must run after draw completes.
- Callback exceptions should be caught and logged so rendering continues.
- Callbacks must not mutate contour internal state.

## Reference pseudocode

```python
import logging
import time

logger = logging.getLogger(__name__)
_ANIMATION_HOOKS = None


def _safe_callback(cb, payload):
    if not callable(cb):
        return
    try:
        cb(payload)
    except Exception:
        logger.exception("animation callback failed")


def gopen(file, **kwargs):
    global _ANIMATION_HOOKS
    _ANIMATION_HOOKS = {
        "session_id": kwargs.get("animation_session_id"),
        "on_meta": kwargs.get("animation_meta_callback"),
        "on_frame": kwargs.get("animation_frame_callback"),
    }
    # existing gopen behavior unchanged


def con(field, **kwargs):
    animation = bool(kwargs.get("animation", False))
    if not animation:
        return _con_static(field, **kwargs)

    hooks = _ANIMATION_HOOKS or {}
    session_id = hooks.get("session_id")
    on_meta = hooks.get("on_meta")
    on_frame = hooks.get("on_frame")

    frames = _resolve_animation_frames(field, kwargs)
    _safe_callback(
        on_meta,
        {
            "session_id": session_id,
            "total_frames": _safe_len_or_none(frames),
            "fps_hint": None,
            "title_template": kwargs.get("animation_title_template"),
            "plot_kind": "contour",
            "levels_locked": _levels_locked_state(),
        },
    )

    for i, frame in enumerate(frames):
        _apply_existing_animation_state(frame, kwargs)
        _draw_frame(frame, kwargs)
        _write_frame_if_configured(frame, kwargs)
        _safe_callback(
            on_frame,
            {
                "session_id": session_id,
                "frame_index": i,
                "frame_value": _frame_value(frame),
                "canvas_ready": True,
                "timestamp": time.time(),
            },
        )

    return _finish_animation()
```

## Implementation checklist

1. Add hook state storage for animation callbacks set by gopen.
2. Add new optional gopen kwargs and store values in hook state.
3. Retrieve hook state inside con animation path.
4. Add a safe callback wrapper with exception logging.
5. Invoke meta callback once before first frame draw.
6. Invoke frame callback after draw and after existing frame output writes.
7. Keep non-animation con path untouched.
8. Update cf-plot docs/changelog to mark these as additive hooks.

## cf-plot test checklist

1. Backward compatibility without callbacks.
2. Meta callback called exactly once and before first frame callback.
3. Frame callback called once per frame with monotonic frame_index.
4. Existing frame-write behavior still occurs when enabled.
5. Callback exceptions are logged and animation continues.
6. Existing kwargs combinations still behave identically with hooks enabled.
7. gopen-registered hooks are visible to subsequent con animation calls.
