from pathlib import Path

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
