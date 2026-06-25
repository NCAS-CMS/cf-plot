"""Integration tests for contour animation behavior with real datasets."""

from pathlib import Path

import cf
import matplotlib.pyplot as plt
import numpy as np
import pytest

import cfplot as cfp


DATA_DIR = Path(__file__).parent.parent.parent / "docs" / "source" / "example-datasets"
TEST_GEN_DIR = Path(__file__).parent.parent.parent / "generated-example-images"
ANIM_GEN_DIR = TEST_GEN_DIR / "animation"


@pytest.fixture(autouse=True)
def setup_cfplot():
    """Reset plotting state around each integration test."""
    plt.close("all")
    cfp.reset()
    yield
    cfp.reset()
    plt.close("all")


@pytest.mark.integration
def test_ptype1_animation_first_five_tas_timesteps_updates_titles():
    """Animate first five tas_A1 frames and verify per-frame title updates."""
    data_file = DATA_DIR / "tas_A1.nc"
    if not data_file.exists():
        pytest.skip(f"Missing test data: {data_file}")

    f = cf.read(str(data_file))[0]
    frame_titles: list[str] = []

    cfp.gopen()
    try:
        for frame_idx in range(5):
            frame = f[frame_idx, :, :]
            reuse_map_background = frame_idx > 0

            cfp.con(
                frame,
                ptype=1,
                animation=True,
                reuse_map_background=reuse_map_background,
                clear_previous_frame=reuse_map_background,
                title="tas",
                animation_axis="auto",
                animation_title_template="{title} [{frame}]",
                lines=False,
            )

            if reuse_map_background:
                title_artist = cfp.plotvars.runtime._contour_animation_title_artist
                assert title_artist is not None
                frame_title = title_artist.get_text()
                assert frame_title.startswith("tas [")
                assert "time:" in frame_title.lower()
                frame_titles.append(frame_title)

        # Frames 1-4 should each have a distinct time-stamped title.
        assert len(frame_titles) == 4
        assert len(set(frame_titles)) == 4
    finally:
        cfp.gclose(view=False)


@pytest.mark.integration
def test_ptype1_animation_first_five_tas_timesteps_writes_png_frames():
    """Render five animation frames and save each frame as a PNG file."""
    data_file = DATA_DIR / "tas_A1.nc"
    if not data_file.exists():
        pytest.skip(f"Missing test data: {data_file}")

    f = cf.read(str(data_file))[0]
    ANIM_GEN_DIR.mkdir(parents=True, exist_ok=True)

    for old_frame in ANIM_GEN_DIR.glob("tas_ptype1_frame_*.png"):
        old_frame.unlink()

    written_frames: list[Path] = []
    expected_axes_count: int | None = None
    expected_boundaries: np.ndarray | None = None

    cfp.gopen()
    try:
        for frame_idx in range(5):
            frame = f[frame_idx, :, :]
            # For exported standalone frames, redraw the map each frame so
            # each PNG contains complete map context on its own.
            reuse_map_background = False

            cfp.con(
                frame,
                ptype=1,
                animation=True,
                animation_reference=f,
                reuse_map_background=reuse_map_background,
                clear_previous_frame=True,
                title="tas",
                animation_axis="auto",
                animation_title_template="{title} [{frame}]",
                lines=False,
            )

            fig = cfp.plotvars.runtime.master_plot
            if fig is None and cfp.plotvars.runtime.plot is not None:
                fig = cfp.plotvars.runtime.plot.figure
            assert fig is not None

            if expected_axes_count is None:
                expected_axes_count = len(fig.axes)
            else:
                assert len(fig.axes) == expected_axes_count

            colorbar = cfp.plotvars.runtime._contour_animation_colorbar
            assert colorbar is not None
            boundaries = np.asarray(colorbar.boundaries, dtype=float)
            if expected_boundaries is None:
                expected_boundaries = boundaries
            else:
                assert np.allclose(boundaries, expected_boundaries)

            frame_path = ANIM_GEN_DIR / f"tas_ptype1_frame_{frame_idx:02d}.png"
            fig.savefig(frame_path, dpi=100)
            written_frames.append(frame_path)

        assert len(written_frames) == 5
        for frame_path in written_frames:
            assert frame_path.exists()
            assert frame_path.stat().st_size > 0
    finally:
        cfp.gclose(view=False)
