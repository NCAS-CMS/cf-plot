"""Integration tests for advanced plot examples (vector, stipple, trajectory, line).

Migrated from cfplot/test/test_examples.py::ExamplesTest
These tests verify that vect(), stipple(), traj(), and lineplot() functions work with real data.
"""

from pathlib import Path
import shutil

import cf
import matplotlib.pyplot as plt
import matplotlib.testing.compare as mpl_compare
import numpy as np
import pytest

import cfplot as cfp


# Path to test data
DATA_DIR = Path(__file__).parent.parent.parent / "docs" / "source" / "example-datasets"
CANARI_DATA_FILE = Path(__file__).parent.parent / "data" / "bnl_tmp_NAEW.nc"
TEST_GEN_DIR = Path(__file__).parent.parent.parent / "generated-example-images"
REF_IMAGE_DIR = Path(__file__).parent.parent / "new_reference-example-images"
#REF_IMAGE_DIR = Path(__file__).parent.parent / "reference-example-images"
TEST_GEN_DIR.mkdir(parents=True, exist_ok=True)


def _is_targeted_example_run(pytestconfig: pytest.Config) -> bool:
    """Return True when pytest was invoked for a narrow subset of tests."""
    args = tuple(str(arg) for arg in pytestconfig.invocation_params.args)
    if any("::" in arg for arg in args):
        return True

    for index, arg in enumerate(args):
        if arg == "-k":
            return index + 1 < len(args) and bool(args[index + 1].strip())
        if arg.startswith("-k"):
            expression = arg[2:]
            return expression.startswith("=") or bool(expression.strip())

    return False


@pytest.fixture(scope="session", autouse=True)
def clean_generated_example_dir(pytestconfig: pytest.Config):
    """Remove stale generated images for broad runs, but preserve targeted runs."""
    if _is_targeted_example_run(pytestconfig):
        return

    for path in TEST_GEN_DIR.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def _configure_example_output(example_id: str) -> None:
    """Route plot output to the expected generated example filename."""
    fname = str(TEST_GEN_DIR / f"gen_fig_{example_id}.png")
    cfp.setvars(file=fname, viewer="matplotlib")


def _assert_reference_match(example_id: str) -> None:
    """Compare generated plot against legacy reference image."""
    ref = REF_IMAGE_DIR / f"ref_fig_{example_id}.png"
    gen = TEST_GEN_DIR / f"gen_fig_{example_id}.png"
    if not ref.exists():
        pytest.skip(f"Missing reference image: {ref}")
    if not gen.exists():
        pytest.fail(f"Generated image missing for example {example_id}: {gen}")
    result = mpl_compare.compare_images(
        str(ref),
        str(gen),
        tol=0.01,
        in_decorator=True,
    )
    if result is not None:
        pytest.fail(f"Image mismatch for example {example_id}: {result}")


@pytest.fixture(autouse=True)
def setup_cfplot():
    """Set up cfplot for each test."""
    plt.close("all")
    cfp.reset()
    yield
    cfp.reset()
    plt.close("all")


@pytest.fixture
def ggap_file():
    """Return GGAP fields keyed by identity."""
    if not (DATA_DIR / "ggap.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ggap.nc'}")
    flds = cf.read(str(DATA_DIR / "ggap.nc"))
    fdict = {f.identity(): f for f in flds}
    return fdict


# ============================================================================
# Vector plot tests (Examples 13-16c)
# ============================================================================

@pytest.mark.integration
def test_example_13_basic_vector_plot(ggap_file):
    """Test Example 13: basic vector plot."""
    u = ggap_file["eastward_wind"]
    v = ggap_file["northward_wind"]

    # Subspace to get values for a specified pressure, here 500 mbar
    u = u.subspace(pressure=500)
    v = v.subspace(pressure=500)

    _configure_example_output("13")
    cfp.vect(u=u, v=v, key_length=10, scale=100, stride=5)
    _assert_reference_match("13")


@pytest.mark.integration
def test_example_14_vector_with_colour_contour(ggap_file):
    """Test Example 14: vector plot with colour contour map."""
    u = ggap_file["eastward_wind"]
    v = ggap_file["northward_wind"]
    t = ggap_file["air_temperature"]

    # Subspace to get values for a specified pressure, here 500 mbar
    u = u.subspace(pressure=500)
    v = v.subspace(pressure=500)
    t = t.subspace(pressure=500)

    _configure_example_output("14")
    cfp.gopen()
    cfp.mapset(lonmin=10, lonmax=120, latmin=-30, latmax=30)
    cfp.levs(min=254, max=270, step=1)
    cfp.con(t)
    cfp.vect(u=u, v=v, key_length=10, scale=50, stride=2)
    cfp.gclose()

    _assert_reference_match("14")


@pytest.mark.integration
def test_example_15_polar_vector_plot(ggap_file):
    """Test Example 15: polar vector plot."""
    u = ggap_file["eastward_wind"]
    v = ggap_file["northward_wind"]
    u = u.subspace(Z=500)
    v = v.subspace(Z=500)

    _configure_example_output("15")
    cfp.mapset(proj="npstere")

    cfp.gopen(columns=2)
    cfp.vect(
        u=u,
        v=v,
        key_length=10,
        scale=100,
        stride=4,
        title="Polar plot using data grid",
    )
    cfp.gpos(2)
    cfp.vect(
        u=u,
        v=v,
        key_length=10,
        scale=100,
        pts=40,
        title="Polar plot with regular point distribution",
    )
    cfp.gclose()
    _assert_reference_match("15")


@pytest.mark.integration
def test_example_16_zonal_vector_plot_on_contour(ggap_file):
    """Test Example 16a: zonal vector plot."""
    # TODO: The vectors look wrong. Needs investigation and a a comparison file
    u = ggap_file["eastward_wind"]
    v = ggap_file["northward_wind"]

    u = u.collapse("X: mean")
    v = v.collapse("X: mean")

    _configure_example_output("16")
    cfp.gopen()
    cfp.levs(min=-15, max=25, step=5)
    cfp.con(u)
    cfp.vect(u=u, v=v, scale=100, key_length=5, stride=1)
    cfp.gclose()
    _assert_reference_match("16")



@pytest.mark.integration
def test_example_16a_zonal_vector_plot(ggap_file):

    c = cf.read(str(DATA_DIR / "vaAMIPlcd_DJF.nc"))[0]
    c = c.subspace(Y=cf.wi(-60, 60))
    c = c.subspace(X=cf.wi(80, 160))
    c = c.collapse("T: mean X: mean")

    g = cf.read(str(DATA_DIR / "wapAMIPlcd_DJF.nc"))[0]
    g = g.subspace(Y=cf.wi(-60, 60))
    g = g.subspace(X=cf.wi(80, 160))
    g = g.collapse("T: mean X: mean")

    # To avoid a cf-python field bug which would appear if we instead
    # did v = -g, see cf-python Issue #797:
    # https://github.com/NCAS-CMS/cf-python/issues/797
    v = -1 * g

    _configure_example_output("16a")
    cfp.vect(
        u=c,
        v=v,
        key_length=[5, 0.05],
        scale=[20, 0.2],
        title="DJF",
        key_location=[0.95, -0.05],
    )
    _assert_reference_match("16a")

@pytest.mark.integration
def test_example_16b_basic_stream_plot(ggap_file):
    """Test Example 16b: basic stream plot."""
    u = ggap_file["eastward_wind"]
    v = ggap_file["northward_wind"]

    u = u.subspace(pressure=500)
    v = v.subspace(pressure=500)

    u = u.anchor("X", -180)
    v = v.anchor("X", -180)

    _configure_example_output("16b")
    cfp.stream(u=u, v=v, density=2)
    _assert_reference_match("16b")


@pytest.mark.integration
def test_example_16c_enhanced_stream_plot(ggap_file):
    """Test Example 16c: enhanced stream plot."""
    u = ggap_file["eastward_wind"]
    v = ggap_file["northward_wind"]

    u = u.subspace(pressure=500)
    v = v.subspace(pressure=500)

    u = u.anchor("X", -180)
    v = v.anchor("X", -180)

    magnitude = (u**2 + v**2) ** 0.5
    mag = np.squeeze(magnitude.array)

    _configure_example_output("16c")
    cfp.levs(0, 60, 5, extend="max")
    cfp.cscale("viridis", ncols=13)
    cfp.gopen()
    cfp.stream(u=u, v=v, density=2, color=mag)
    cfp.cbar(
        levs=cfp.plotvars.levels,
        position=[0.12, 0.12, 0.8, 0.02],
        title="Wind magnitude",
    )
    cfp.gclose()
   
    _assert_reference_match("16c")


# ============================================================================
# Stipple plot tests (Examples 17-18)
# ============================================================================

@pytest.mark.integration
def test_example_17_basic_stipple_plot():
    """Test Example 17: basic stipple plot."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    g = f.subspace(time=15)

    _configure_example_output("17")
    cfp.gopen()
    cfp.cscale("magma")
    cfp.con(g)
    cfp.stipple(f=g, min=220, max=260, size=100, color="#00ff00")
    cfp.stipple(f=g, min=300, max=330, size=50, color="#0000ff", marker="s")
    cfp.gclose()

    _assert_reference_match("17")


@pytest.mark.integration
def test_example_18_polar_stipple_plot():
    """Test Example 18: polar stipple plot."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    g = f.subspace(time=15)

    _configure_example_output("18")
    cfp.gopen()

    cfp.cscale("magma")
    cfp.mapset(proj="npstere")
    cfp.con(g)
    cfp.stipple(f=g, min=265, max=295, size=100, color="#00ff00")
    cfp.gclose()

    _assert_reference_match("18")


# ============================================================================
# Unstructured grid tests (Examples 24a-24c)
# ============================================================================


@pytest.mark.integration
def test_canari_1():
    """Regression test for CANARI rotated-grid plotting case."""
    if not CANARI_DATA_FILE.exists():
        pytest.skip(f"Missing integration dataset: {CANARI_DATA_FILE}")

    _configure_example_output("canari_1")
    flds = cf.read(str(CANARI_DATA_FILE))
    f = flds[0]
    field = f[0, 3, :, :]
    cfp.mapset(proj="rotated")
    cfp.con(field, lines=False)
    _assert_reference_match("canari_1")

@pytest.mark.integration
def test_example_24a_unstructured_grid_basic():
    """Test Example 24a.

    Test example for unstructured grids: LFRic example 1, now
    numbered to become the missing example 24, part (a).

    NOTE, TODO: relative to example from docs, have added
    'blockfill=True' to get well-defined edges on faces, otherwise
    looks very similar to 'gen_fig_unstructured_lfric_3' plot, with
    edges all blurred together.
    """
    if not (DATA_DIR / "lfric_initial.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'lfric_initial .nc'}")
    f = cf.read(str(DATA_DIR / "lfric_initial.nc"))

    # Select the relevant fields for the objects required for the plot,
    # taking the air potential temperature as a variable to choose to view.
    pot = f.select_by_identity("air_potential_temperature")[0]
    lats = f.select_by_identity("latitude")[0]
    lons = f.select_by_identity("longitude")[0]
    faces = f.select_by_identity("cf_role=face_edge_connectivity")[0]

    # Reduce the variable to match the shapes
    pot = pot[4, :]
    _configure_example_output("24a")

    cfp.levs(240, 310, 5)

    cfp.con(
        f=pot,
        face_lons=lons,
        face_lats=lats,
        face_connectivity=faces,
        lines=False,
        blockfill=True,
    )
    _assert_reference_match("24a")


@pytest.mark.integration
def test_example_24b_unstructured_grid_blockfill():
    
    """Test Example 24b.

    Test example for unstructured grids: LFRic example 2, now
    numbered to become the missing example 24, part (b).

    NOTE, TODO: there are 3 'sides' of missing data in the cubed-sphere
    grid, a clear issue. For now the reference plot has this in. An
    issue will be raised to note this and eventually fix it.
    """
    if not (DATA_DIR / "lfric_initial.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'lfric_initial .nc'}")
    f = cf.read(str(DATA_DIR / "lfric_initial.nc"))

    # Select the relevant fields for the objects required for the plot,
    # taking the air potential temperature as a variable to choose to view.
    pot = f.select_by_identity("air_potential_temperature")[0]
    lats = f.select_by_identity("latitude")[0]
    lons = f.select_by_identity("longitude")[0]
    faces = f.select_by_identity("cf_role=face_edge_connectivity")[0]

    # Reduce the variable to match the shapes
    pot = pot[4, :]

    _configure_example_output("24b")
    cfp.levs(240, 310, 5)

    # This time set the projection to a polar one for a different view
    cfp.mapset(proj="npstere")
    cfp.con(
        f=pot,
        face_lons=lons,
        face_lats=lats,
        face_connectivity=faces,
        lines=False,
        blockfill=True,
    )
    _assert_reference_match("24b")


@pytest.mark.integration
def test_example_24c_unstructured_grid_version3():
    """Test Example 24c.

    Test example for unstructured grids: LFRic example 3, now
    numbered to become the missing example 24, part (c).

    #TODO Convince ourself this is right. There were some strange polar
    #artifacts in the refactor transition, and it's not obvious what is right or wrong.

    """
    if not (DATA_DIR / "lfric_initial.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'lfric_initial .nc'}")
    f = cf.read(str(DATA_DIR / "lfric_initial.nc"))

    pot = f.select_by_identity("air_potential_temperature")[0]

    g = pot[0,:]   
    _configure_example_output("24c")
    cfp.con(g, lines=False)
    _assert_reference_match("24c")


        

# ============================================================================
# Line/Graph plot tests (Examples 27-30)
# ============================================================================

@pytest.mark.integration
def test_example_27_basic_graph_plot(ggap_file):
    """Test Example 27: basic graph plot."""
    f = ggap_file["eastward_wind"]
    g = f.collapse("X: mean")

    _configure_example_output("27")
    cfp.gopen()
    cfp.lineplot(
        g.subspace(pressure=100),
        marker="o",
        color="blue",
        title="Zonal mean zonal wind at 100mb",
    )
    cfp.gclose()
    _assert_reference_match("27")


@pytest.mark.integration
def test_example_28_line_and_legend_plot(ggap_file):
    """Test Example 28: line and legend plot."""
    f = ggap_file["eastward_wind"]
    g = f.collapse("X: mean")

    xticks = [-90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90]
    xticklabels = [
        "90S", "75S", "60S", "45S", "30S", "15S", "0",
        "15N", "30N", "45N", "60N", "75N", "90N",
    ]
    xpts = [-30, 30, 30, -30, -30]
    ypts = [-8, -8, 5, 5, -8]

    _configure_example_output("28")
    cfp.gset(xmin=-90, xmax=90, ymin=-10, ymax=50)

    cfp.gopen()
    cfp.lineplot(
        g.subspace(pressure=100),
        marker="o",
        color="blue",
        title="Zonal mean zonal wind",
        label="100mb",
    )
    cfp.lineplot(
        g.subspace(pressure=200),
        marker="D",
        color="red",
        label="200mb",
        xticks=xticks,
        xticklabels=xticklabels,
        legend_location="upper right",
    )
    cfp.plotvars.plot.plot(xpts, ypts, linewidth=3.0, color="green")
    cfp.plotvars.plot.text(35, -2, "Region of interest", horizontalalignment="left")
    cfp.gclose()
    _assert_reference_match("28")


@pytest.mark.integration
def test_example_29_global_average_annual_temperature():
    """Test Example 29: global average annual temperature."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]

    temp = f.subspace(time=cf.wi(cf.dt("1900-01-01"), cf.dt("1980-01-01")))
    temp_annual = temp.collapse("T: mean", group=cf.Y())
    temp_annual_global = temp_annual.collapse("area: mean", weights="area")
    temp_annual_global.Units -= 273.15

    _configure_example_output("29")
    cfp.lineplot(
        temp_annual_global,
        title="Global average annual temperature",
        color="blue",
    )
    _assert_reference_match("29")


@pytest.mark.integration
def test_example_30_two_axis_plotting(ggap_file):
    """Test Example 30: two axis plotting."""
    f_u = ggap_file["eastward_wind"]
    f_t = ggap_file["air_temperature"]

    u = f_u.collapse("X: mean")
    u1 = u.subspace(Y=cf.isclose(-61.12099075))
    u2 = u.subspace(Y=cf.isclose(0.56074494))

    t = f_t.collapse("X: mean")
    t1 = t.subspace(Y=cf.isclose(-61.12099075))
    t2 = t.subspace(Y=cf.isclose(0.56074494))

    _configure_example_output("30")
    cfp.gopen()
    cfp.gset(-30, 30, 1000, 0)
    cfp.lineplot(u1, color="r")
    cfp.lineplot(u2, color="r")
    cfp.gset(190, 300, 1000, 0, twiny=True)
    cfp.lineplot(t1, color="b")
    cfp.lineplot(t2, color="b")
    cfp.gclose()
    _assert_reference_match("30")


# ============================================================================
# Trajectory plot tests (Examples 39-42b)
# ============================================================================

@pytest.mark.integration
def test_example_39_basic_track_plotting_trajectory():
    """Test Example 39: basic track plotting trajectory."""
    if not (DATA_DIR / "ff_trs_pos.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ff_trs_pos.nc'}")

    f = cf.read(str(DATA_DIR / "ff_trs_pos.nc"))[0]

    _configure_example_output("39")
    cfp.traj(f)
    _assert_reference_match("39")


@pytest.mark.integration
def test_example_39b_single_dsg_trajectory_no_dimension():
    """Test Example 39b: single DSG with no trajectory dimension (1D)."""
    if not (DATA_DIR / "dsg_trajectory.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'dsg_trajectory.nc'}")

    f = cf.read(str(DATA_DIR / "dsg_trajectory.nc"))[0]

    # This is over a small part of France so focus in on that area
    cfp.mapset(lonmin=3, lonmax=6, latmin=51, latmax=54, resolution="10m")

    _configure_example_output("39b")
    cfp.traj(f)
    _assert_reference_match("39b")


@pytest.mark.integration
def test_example_40_tracks_polar_stereographic():
    """Test Example 40: tracks in the polar stereographic projection."""
    if not (DATA_DIR / "ff_trs_pos.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ff_trs_pos.nc'}")

    f = cf.read(str(DATA_DIR / "ff_trs_pos.nc"))[0]

    cfp.mapset(proj="npstere")

    _configure_example_output("40")
    cfp.traj(f)
    _assert_reference_match("40")


@pytest.mark.integration
def test_example_41_feature_propagation():
    """Test Example 41: feature propagation over Europe."""
    if not (DATA_DIR / "ff_trs_pos.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ff_trs_pos.nc'}")

    f = cf.read(str(DATA_DIR / "ff_trs_pos.nc"))[0]

    cfp.mapset(lonmin=-20, lonmax=20, latmin=30, latmax=70)

    _configure_example_output("41")
    cfp.traj(f, vector=True, markersize=0.0, fc="b", ec="b")
    _assert_reference_match("41")


@pytest.mark.integration
def test_example_42a_intensity_legend():
    """Test Example 42a: intensity legend."""
    if not (DATA_DIR / "ff_trs_pos.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ff_trs_pos.nc'}")

    f = cf.read(str(DATA_DIR / "ff_trs_pos.nc"))[0]

    cfp.mapset(lonmin=-50, lonmax=50, latmin=20, latmax=80)
    g = f.subspace(time=cf.wi(cf.dt("1979-12-01"), cf.dt("1979-12-10")))
    g = g * 1e5
    cfp.levs(0, 12, 1, extend="max")
    cfp.cscale("scale1", below=0, above=13)

    _configure_example_output("42a")
    cfp.traj(
        g,
        legend=True,
        markersize=40.0,
        colorbar_title="Relative Vorticity (Hz) * 1e5",
    )
    _assert_reference_match("42a")


@pytest.mark.integration
def test_example_42b_intensity_legend_with_lines():
    """Test Example 42b: intensity legend with lines."""
    # TODO I think this is right, even though it is different from legacy.
    # Legacy has 42a and 42b the same, which can't be right.
    if not (DATA_DIR / "ff_trs_pos.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ff_trs_pos.nc'}")

    f = cf.read(str(DATA_DIR / "ff_trs_pos.nc"))[0]

    cfp.mapset(lonmin=-50, lonmax=50, latmin=20, latmax=80)
    g = f.subspace(time=cf.wi(cf.dt("1979-12-01"), cf.dt("1979-12-10")))
    g = g * 1e5
    cfp.levs(0, 12, 1, extend="max")
    cfp.cscale("scale1", below=0, above=13)

    _configure_example_output("42b")
    cfp.traj(
        g,
        legend_lines=True,
        linewidth=2,
        colorbar_title="Relative Vorticity (Hz) * 1e5",
    )
    _assert_reference_match("42b")
