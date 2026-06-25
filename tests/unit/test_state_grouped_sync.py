import cfplot as cfp


def setup_function():
    cfp.reset()


def teardown_function():
    cfp.reset()


def test_grouped_to_legacy_sync():
    cfp.plotvars.map.lonmin = -123
    cfp.plotvars.axes.xmax = 88
    cfp.plotvars.decoration.title_fontsize = 22
    cfp.plotvars.layout.rows = 4
    cfp.plotvars.scale.levels_extend = "min"
    cfp.plotvars.runtime.user_mapset = 1
    cfp.plotvars.output.viewer = "matplotlib"

    assert cfp.plotvars.lonmin == -123
    assert cfp.plotvars.xmax == 88
    assert cfp.plotvars.title_fontsize == 22
    assert cfp.plotvars.rows == 4
    assert cfp.plotvars.levels_extend == "min"
    assert cfp.plotvars.user_mapset == 1
    assert cfp.plotvars.viewer == "matplotlib"


def test_legacy_to_grouped_sync():
    cfp.plotvars.lonmax = 179
    cfp.plotvars.ymin = -50
    cfp.plotvars.axis_label_fontweight = "bold"
    cfp.plotvars.columns = 3
    cfp.plotvars.cs_user = "viridis"
    cfp.plotvars.user_gset = 1
    cfp.plotvars.tspace_day = 5

    assert cfp.plotvars.map.lonmax == 179
    assert cfp.plotvars.axes.ymin == -50
    assert cfp.plotvars.decoration.axis_label_fontweight == "bold"
    assert cfp.plotvars.layout.columns == 3
    assert cfp.plotvars.scale.cs_user == "viridis"
    assert cfp.plotvars.runtime.user_gset == 1
    assert cfp.plotvars.output.tspace_day == 5


def test_levs_updates_grouped_scale_state():
    cfp.levs(min=-2, max=2, step=1, extend="both")

    assert cfp.plotvars.runtime.user_levs == 1
    assert cfp.plotvars.scale.levels is not None
    assert cfp.plotvars.levels_extend == "both"

    cfp.levs()

    assert cfp.plotvars.scale.levels is None
    assert cfp.plotvars.scale.levels_min is None
    assert cfp.plotvars.scale.levels_max is None
    assert cfp.plotvars.scale.levels_step is None
    assert cfp.plotvars.scale.norm is None
    assert cfp.plotvars.runtime.user_levs == 0
