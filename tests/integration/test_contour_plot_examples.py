"""Integration tests for contour plot examples.

Migrated from cfplot/test/test_examples.py::ExamplesTest
These tests verify that con() plotting functions work with real data.
"""

from pathlib import Path
import shutil

import cf
import matplotlib.pyplot as plt
import matplotlib.testing.compare as mpl_compare
import numpy as np
import pytest

import cfplot as cfp
import cfplot.layout_runtime as layout_runtime


# Path to test data
DATA_DIR = Path(__file__).parent.parent.parent / "docs" / "source" / "example-datasets"
TEST_GEN_DIR = Path(__file__).parent.parent.parent / "generated-example-images"
#REF_IMAGE_DIR = Path(__file__).parent.parent / "reference-example-images"
REF_IMAGE_DIR = Path(__file__).parent.parent / "new_reference-example-images"
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


@pytest.fixture
def ggap_file():
    """Return GGAP fields keyed by identity."""
    if not (DATA_DIR / "ggap.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ggap.nc'}")
    flds = cf.read(str(DATA_DIR / "ggap.nc"))
    fdict = {f.identity(): f for f in flds}
    return fdict

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


@pytest.mark.integration
def test_gclose_view_false_does_not_launch_viewer(monkeypatch):
    """Ensure gclose(view=False) does not trigger display or matplotlib viewer."""
    calls = {"show": 0, "popen": 0}

    def fake_show(*args, **kwargs):
        calls["show"] += 1

    def fake_popen(*args, **kwargs):
        calls["popen"] += 1
        return None

    monkeypatch.setattr(plt, "show", fake_show)
    monkeypatch.setattr(layout_runtime.subprocess, "Popen", fake_popen)

    cfp.setvars(file=None, viewer="display")
    cfp.gopen()
    cfp.gclose(view=False)

    assert calls["show"] == 0
    assert calls["popen"] == 0


@pytest.mark.integration
def test_example_1_basic_cylindrical():
    """Test Example 1: a basic cylindrical projection."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("1")

    # This should not raise
    cfp.con(f.subspace(time=15))
    _assert_reference_match("1")


@pytest.mark.integration
def test_example_2_blockfill():
    """Test Example 2: cylindrical projection with blockfill."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("2")

    # This should not raise (blockfill with filled colors)
    cfp.con(f.subspace(time=15), blockfill=True, lines=False)
    _assert_reference_match("2")


@pytest.mark.integration
def test_example_3_map_limits_and_levels():
    """Test Example 3: altering the map limits and contour levels."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("3")

    cfp.mapset(lonmin=-15, lonmax=3, latmin=48, latmax=60)
    cfp.levs(min=265, max=285, step=1)
    cfp.con(f.subspace(time=15))
    _assert_reference_match("3")


@pytest.mark.integration
def test_example_4_north_pole_stereographic(ggap_file):
    """Test Example 4: north pole polar stereographic projection."""

    f = ggap_file["eastward_wind"]
    assert f.identity() == "eastward_wind"
    _configure_example_output("4")

    cfp.mapset(proj="npstere")
    cfp.con(f.subspace(pressure=500))
    _assert_reference_match("4")


@pytest.mark.integration
def test_example_5_south_pole_with_boundary(ggap_file):
    """Test Example 5: south pole with bounding latitude."""
    if not (DATA_DIR / "ggap.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ggap.nc'}")

    f = ggap_file["eastward_wind"]
    _configure_example_output("5")

    cfp.mapset(proj="spstere", boundinglat=-30, lon_0=180)
    cfp.con(f.subspace(pressure=500))
    _assert_reference_match("5")


@pytest.mark.integration
def test_example_6_latitude_pressure_plot(ggap_file):
    """Test Example 6: latitude-pressure plot."""

    f = ggap_file["geopotential"]
    _configure_example_output("6")

    cfp.con(f.subspace(longitude=0))
    _assert_reference_match("6")


@pytest.mark.integration
def test_example_7_lat_pressure_zonal_mean(ggap_file):
    """Test Example 7: latitude-pressure plot of a zonal mean."""
    if not (DATA_DIR / "ggap.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ggap.nc'}")

    f = ggap_file["eastward_wind"]
    _configure_example_output("7")

    cfp.con(f.collapse("mean", "longitude"))
    _assert_reference_match("7")


@pytest.mark.integration
def test_example_8_log_scale_pressure(ggap_file):
    """Test Example 8: plot showing latitude against log-scale pressure."""
    if not (DATA_DIR / "ggap.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ggap.nc'}")

    f = ggap_file["eastward_wind"]
    _configure_example_output("8")

    cfp.con(f.collapse("mean", "longitude"), ylog=1)
    _assert_reference_match("8")


@pytest.mark.integration
#@pytest.mark.xfail(reason="cf-python issue #799")
def test_example_9_longitude_pressure_plot(ggap_file):
    """Test Example 9: longitude-pressure plot."""

    f = ggap_file["air_temperature"]
    _configure_example_output("9")

    cfp.con(f.collapse("mean", "latitude"))
    _assert_reference_match("9")


@pytest.mark.integration
def test_example_10_latitude_time_hovmuller():
    """Test Example 10: latitude-time Hovmuller plot."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("10")

    cfp.cscale("plasma")
    cfp.con(f.subspace(longitude=0), lines=0)
    _assert_reference_match("10")


@pytest.mark.integration
def test_example_11_latitude_time_subset_hovmuller():
    """Test Example 11: latitude-time subset Hovmuller plot."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("11")

    cfp.gset(-30, 30, "1960-1-1", "1980-1-1")
    cfp.levs(min=280, max=305, step=1)
    cfp.cscale("plasma")
    cfp.con(f.subspace(longitude=0), lines=0)
    _assert_reference_match("11")


@pytest.mark.integration
def test_example_12_longitude_time_hovmuller():
    """Test Example 12: longitude-time Hovmuller plot."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("12")

    cfp.cscale("plasma")
    cfp.con(f.subspace(latitude=0), lines=0)
    _assert_reference_match("12")


@pytest.mark.integration
def test_example_19_multiple_subplots(ggap_file):
    """Test Example 19: multiple plots as subplots."""
    if not (DATA_DIR / "ggap.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ggap.nc'}")

    f = ggap_file["eastward_wind"]
    _configure_example_output("19")

    cfp.gopen(rows=2, columns=2, bottom=0.2)
    cfp.gpos(1)
    cfp.con(f.subspace(pressure=500), colorbar=None)
    cfp.gpos(2)
    cfp.mapset(proj="moll")
    cfp.con(f.subspace(pressure=500), colorbar=None)
    cfp.gpos(3)
    cfp.mapset(proj="npstere", boundinglat=30, lon_0=180)
    cfp.con(f.subspace(pressure=500), colorbar=None)
    cfp.gpos(4)
    cfp.mapset(proj="spstere", boundinglat=-30, lon_0=180)
    cfp.con(
        f.subspace(pressure=500),
        colorbar_position=[0.1, 0.1, 0.8, 0.02],
        colorbar_orientation="horizontal",
    )
    cfp.gclose()
    _assert_reference_match("19")


@pytest.mark.integration
def test_example_19a_user_positioned_subplots(ggap_file):
    """Test Example 19a: user specified subplot positions."""
    if not (DATA_DIR / "ggap.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ggap.nc'}")

    f = ggap_file["eastward_wind"]
    _configure_example_output("19a")

    cfp.gopen(user_position=True)
    cfp.gpos(xmin=0.1, xmax=0.5, ymin=0.55, ymax=1.0)
    cfp.con(f.subspace(Z=500), title="500mb", lines=False)
    cfp.gpos(xmin=0.55, xmax=0.95, ymin=0.55, ymax=1.0)
    cfp.con(f.subspace(Z=100), title="100mb", lines=False)
    cfp.gpos(xmin=0.3, xmax=0.7, ymin=0.1, ymax=0.55)
    cfp.con(f.subspace(Z=10), title="10mb", lines=False)
    cfp.gclose()
    _assert_reference_match("19a")


@pytest.mark.integration
def test_example_20_rotated_pole_data():
    """Test Example 20: user labelling of axes with rotated pole data."""
    if not (DATA_DIR / "Geostropic_Adjustment.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'Geostropic_Adjustment.nc'}")

    flds = cf.read(str(DATA_DIR / "Geostropic_Adjustment.nc"))
    f = {f.identity(): f for f in flds}["ncvar%v"]
    _configure_example_output("20")

    # Legacy examples contour a 2D slice of this rotated-pole field.
    cfp.con(f.subspace[9])
    _assert_reference_match("20")


@pytest.mark.integration
def test_example_21_rotated_pole_custom_ticks():
    """Test Example 21: rotated pole data plot with custom ticks."""
    if not (DATA_DIR / "Geostropic_Adjustment.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'Geostropic_Adjustment.nc'}")

    flds = cf.read(str(DATA_DIR / "Geostropic_Adjustment.nc"))
    f = {f.identity(): f for f in flds}["ncvar%v"]
    _configure_example_output("21")

    cfp.con(
        f.subspace[9],
        title="test data",
        xticks=np.arange(5) * 100000 + 100000,
        yticks=np.arange(7) * 2000 + 2000,
        xlabel="x-axis",
        ylabel="z-axis",
    )


@pytest.mark.integration
def test_example_21other_rgp_plasma():
    """Test Example 21other: RGP data with plasma colorscale."""
    if not (DATA_DIR / "rgp.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'rgp.nc'}")

    f = cf.read(str(DATA_DIR / "rgp.nc"))[0]
    _configure_example_output("21other")

    cfp.cscale("plasma")
    cfp.con(f)
    _assert_reference_match("21other")



@pytest.mark.integration
def test_example_22_rgp_rotated_projection():
    """Test RGP data with rotated projection."""
    if not (DATA_DIR / "rgp.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'rgp.nc'}")

    f = cf.read(str(DATA_DIR / "rgp.nc"))[0]
    _configure_example_output("22")

    cfp.cscale("plasma")
    cfp.mapset(proj="rotated")
    cfp.con(f)
    _assert_reference_match("22")


@pytest.mark.integration
def test_example_23_rotated_grid_axes_overlay():
    """Test Example 23: rotated-grid axes overlay."""
    if not (DATA_DIR / "rgp.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'rgp.nc'}")

    f = cf.read(str(DATA_DIR / "rgp.nc"))[0]
    _configure_example_output("23")

    data = f.array
    xvec = f.construct("ncvar%x").array
    yvec = f.construct("ncvar%y").array
    xpole = 160
    ypole = 30

    cfp.gopen()
    cfp.cscale("plasma")
    xpts = np.arange(np.size(xvec))
    ypts = np.arange(np.size(yvec))
    cfp.gset(xmin=0, xmax=np.size(xvec) - 1, ymin=0, ymax=np.size(yvec) - 1)
    cfp.levs(min=980, max=1035, step=2.5)
    cfp.con(data, xpts, ypts[::-1])
    cfp.rgaxes(xpole=xpole, ypole=ypole, xvec=xvec, yvec=yvec)
    cfp.gclose()
    _assert_reference_match("23")


@pytest.mark.integration
def test_example_23other_incompass_contour_vectors():
    """Test Example 23other: contour + vectors on INCOMPASS data."""
    incompass_file = DATA_DIR / "20160601-05T0000Z_INCOMPASS_km4p4_uv_RH_500.nc"
    if not incompass_file.exists():
        pytest.skip(f"Missing test data: {incompass_file}")

    flds = cf.read(str(incompass_file))
    fdict = {f.identity(): f for f in flds}
    _configure_example_output("23other")

    cfp.mapset(50, 100, 5, 35)
    cfp.levs(0, 90, 15, extend="neither")
    cfp.gopen()
    cfp.con(fdict['long_name=Relative humidity'], lines=False)
    cfp.vect(u=fdict['eastward_wind'], v=fdict['northward_wind'], stride=40, key_length=10)
    cfp.gclose()
    _assert_reference_match("23other")


@pytest.mark.integration
def test_example_31_ukcp_projection():
    """Test Example 31: UKCP projection."""
    ukcp_file = DATA_DIR / "ukcp_rcm_test.nc"
    if not ukcp_file.exists():
        pytest.skip(f"Missing test data: {ukcp_file}")

    f = cf.read(str(ukcp_file))[0]

    fname = str(TEST_GEN_DIR / "gen_fig_31.png")
    cfp.setvars(
        file=fname,
        viewer="matplotlib",
        grid_x_spacing=1,
        grid_y_spacing=1,
    )
    cfp.mapset(proj="UKCP", resolution="50m")
    #TODO The original test set the grid_x_ and _y_spacing to 1, 
    # but this reset all the output, and stopped any output to 
    # file. We need to fix setvars so it doesn't just reset
    # everything. 
    cfp.levs(-3, 7, 0.5)
    cfp.con(f, lines=False)
    _assert_reference_match("31")


@pytest.mark.integration
def test_example_33_osgb_and_europp():
    """Test Example 33: OSGB and EuroPP projections."""
    ukcp_file = DATA_DIR / "ukcp_rcm_test.nc"
    if not ukcp_file.exists():
        pytest.skip(f"Missing test data: {ukcp_file}")

    f = cf.read(str(ukcp_file))[0]
    _configure_example_output("33")

    cfp.levs(-3, 7, 0.5)
    cfp.gopen(columns=2)
    cfp.mapset(proj="OSGB", resolution="50m")
    cfp.con(f, lines=False, colorbar_label_skip=2)
    cfp.gpos(2)
    cfp.mapset(proj="EuroPP", resolution="50m")
    cfp.con(f, lines=False, colorbar_label_skip=2)
    cfp.gclose()
    _assert_reference_match("33")


@pytest.mark.integration
def test_example_34_lambert_conformal():
    """Test Example 34: Cropped Lambert conformal projection."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("34")

    cfp.mapset(proj="lcc", lonmin=-50, lonmax=50, latmin=20, latmax=85)
    cfp.con(f.subspace(time=15))
    _assert_reference_match("34")


@pytest.mark.integration
def test_example_35_mollweide_projection():
    """Test Example 35: Mollweide projection."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("35")

    cfp.mapset(proj="moll")
    cfp.con(f.subspace(time=15))
    _assert_reference_match("35")


@pytest.mark.integration
def test_example_36_mercator_projection():
    """Test Example 36: Mercator projection."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("36")

    cfp.mapset(proj="merc")
    cfp.con(f.subspace(time=15))
    _assert_reference_match("36")


@pytest.mark.integration
def test_example_37_orthographic_projection():
    """Test Example 37: Orthographic projection."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("37")

    cfp.mapset(proj="ortho")
    cfp.con(f.subspace(time=15))
    _assert_reference_match("37")


@pytest.mark.integration
def test_example_38_robinson_projection():
    """Test Example 38: Robinson projection."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")

    f = cf.read(str(DATA_DIR / "tas_A1.nc"))[0]
    _configure_example_output("38")

    cfp.mapset(proj="robin")
    cfp.con(f.subspace(time=15))
    _assert_reference_match("38")


@pytest.mark.integration
def test_example_37b_orthographic_full_globe():
    """Test orthographic projection with an explicit full-globe bounding box.

    Exercises the case where lonmin/lonmax/latmin/latmax are all set to the
    full range (-180/180/-90/90), which previously produced rendering artefacts
    (wedge gaps or a seam column through the visible hemisphere).
    """
    data_file = Path(__file__).parent.parent / "data" / "example_ortho_fail.nc"
    if not data_file.exists():
        pytest.skip(f"Missing test data: {data_file}")

    pfld = cf.read(str(data_file))[0]
    _configure_example_output("37b")

    cfp.mapset(
        proj="ortho",
        resolution="110m",
        lonmin=-180.0,
        lonmax=180.0,
        latmin=-90.0,
        latmax=90.0,
        lon_0=0.0,
        lat_0=0.0,
    )
    cfp.con(pfld, fill=True, lines=False, line_labels=False,
            title="time=3080592000.0")
    _assert_reference_match("37b")



@pytest.mark.integration
def test_example_numpy_arrays():
    """Test contour with raw numpy arrays."""
    # Create synthetic 2D data
    x = np.linspace(0, 10, 50)
    y = np.linspace(0, 10, 50)
    X, Y = np.meshgrid(x, y)
    field = np.sin(X) * np.cos(Y)

    fname = str(TEST_GEN_DIR / "gen_fig_numpy.png")
    cfp.setvars(file=fname, viewer="matplotlib")

    # Should accept raw arrays
    cfp.con(f=field, x=x, y=y)
