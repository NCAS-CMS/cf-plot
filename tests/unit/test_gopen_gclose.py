from pathlib import Path
import pytest

import cfplot as cfp


def setup_function():
    cfp.reset()


def teardown_function():
    cfp.reset()


def test_gopen_sets_runtime_state(tmp_path: Path):
    outfile = tmp_path / "gopen_state.png"
    cfp.setvars(file=str(outfile), viewer="matplotlib")

    cfp.gopen(rows=2, columns=3)

    assert cfp.plotvars.master_plot is not None
    assert cfp.plotvars.rows == 2
    assert cfp.plotvars.columns == 3
    assert cfp.plotvars.user_plot == 1

    cfp.gclose(view=False)


def test_gclose_clears_runtime_handles(tmp_path: Path):
    outfile = tmp_path / "gclose_state.png"
    cfp.setvars(file=str(outfile), viewer="matplotlib")

    cfp.gopen()
    cfp.gclose(view=False)

    assert cfp.plotvars.master_plot is None
    assert cfp.plotvars.plot is None
    assert cfp.plotvars.mymap is None
    assert cfp.plotvars.gpos_called is False


def test_gfigure_opens_and_closes(tmp_path: Path):
    """Test that the gfigure context manager opens and closes a gfigure."""
    outfile = tmp_path / "gfigure_context.png"
    cfp.setvars(file=str(outfile), viewer="matplotlib")

    with cfp.gfigure(rows=2, columns=3):
        assert cfp.plotvars.master_plot is not None
        assert cfp.plotvars.rows == 2
        assert cfp.plotvars.columns == 3
        assert cfp.plotvars.user_plot == 1

    assert cfp.plotvars.master_plot is None
    assert cfp.plotvars.plot is None
    assert cfp.plotvars.mymap is None


def test_gfigure_closes_after_exception(tmp_path: Path):
    """Test that the gfigure is closed if an exception occurs."""
    outfile = tmp_path / "gfigure_exception.png"
    cfp.setvars(file=str(outfile), viewer="matplotlib")

    with pytest.raises(ValueError, match="Test exception"):
        with cfp.gfigure():
            assert cfp.plotvars.master_plot is not None
            raise ValueError("Test exception")

    assert cfp.plotvars.master_plot is None
    assert cfp.plotvars.plot is None
    assert cfp.plotvars.mymap is None


def test_gfigure_passes_arguments_to_gopen(tmp_path: Path):
    """Test that arguments are passed through to gopen."""
    outfile = tmp_path / "gfigure_arguments.png"
    cfp.setvars(file=str(outfile), viewer="matplotlib")

    with cfp.gfigure(rows=2, columns=3):
        assert cfp.plotvars.rows == 2
        assert cfp.plotvars.columns == 3
