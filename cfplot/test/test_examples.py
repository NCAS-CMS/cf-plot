"""
Examples testing of cf-plot.

Run all the documentation example plots and compare them to
reference expected plots to ensure they are the same.

"""

import faulthandler
import functools
import hashlib
import os
from pathlib import Path
from pprint import pformat

import cartopy.crs as ccrs
import cf
import coverage
import matplotlib.testing.compare as mpl_compare
import numpy as np
import pytest
from netCDF4 import Dataset as ncfile
from scipy.interpolate import griddata

import cfplot as cfp

faulthandler.enable()  # to debug seg faults and timeouts

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "docs" / "source" / "example-datasets"
TEST_REF_DIR = REPO_ROOT / "tests" / "reference-example-images"
TEST_GEN_DIR = REPO_ROOT / "generated-example-images"
TEST_GEN_DIR.mkdir(parents=True, exist_ok=True)


def compare_plot_results(test_method):
    """
    Decorator to compare images and cause a test error if they don't match.

    This logic uses 'matplotlib.testing.compare' to handle under-the-hood
    plot image comparison.
    """

    @functools.wraps(test_method)
    def wrapper(_self):
        tid = _self.test_id
        test_name = f"test_example_{tid}"

        # Part A: functional test i.e. does the code run OK
        print(f"\n___Running code for {test_name}___")
        test_method(_self)

        # Part B: plot image comparison test i.e. is the plot output correct
        print(f"___Comparing output images for {test_name}___")
        # TODO add underscore to ref_figX names for consistency
        image_cmp_result = mpl_compare.compare_images(
            str(TEST_REF_DIR / f"ref_fig_{tid}.png"),  # expected plot
            str(TEST_GEN_DIR / f"gen_fig_{tid}.png"),  # actual plot
            tol=0.01,
            in_decorator=True,
        )

        # If the plot image comparison passed, image_cmp_result will be None
        # (see https://matplotlib.org/stable/api/
        # testing_api.html#matplotlib.testing.compare.compare_images)
        msg = "\nPlot comparison shows differences, see result dict for details."
        assert image_cmp_result is None, msg

    return wrapper


@pytest.mark.integration
class TestExamples:
    """Run through gallery examples and compare to reference plots."""

    data_dir = DATA_DIR
    save_gen_dir = TEST_GEN_DIR
    ref_dir = TEST_REF_DIR
    test_id = None

    def setup_method(self, method):
        """Preparations called immediately before each test method."""
        # Get a filename fname with the ID of test_example_X component X
        test_method_name = method.__name__
        self.test_id = test_method_name.rsplit("test_example_")[1]
        fname = str(self.save_gen_dir / f"gen_fig_{self.test_id}.png")

        # At the moment there is no 'getvars' to access the plotting variables
        # defined (see Issue https://github.com/NCAS-CMS/cf-plot/issues/93)
        # so we have to also store these, since any call to setvars(...) in
        # the examples will reset those set here, so we must ensure we set
        # them via inclusion of this self.setvars_dict for use later if needed.
        self.setvars_dict = {
            "file": fname,
            "viewer": "matplotlib",
        }
        cfp.setvars(**self.setvars_dict)

    def teardown_method(self):
        """Preparations called immediately after each test method."""
        cfp.reset()

    @compare_plot_results
    def test_example_1(self):
        """Test Example 1: a basic cylindrical projection."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.con(f.subspace(time=15))

    @compare_plot_results
    def test_example_2(self):
        """Test Example 2: a cylindrical projection with blockfill."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.con(f.subspace(time=15), blockfill=True, lines=False)

    @compare_plot_results
    def test_example_3(self):
        """Test Example 3: altering the map limits and contour levels."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.mapset(lonmin=-15, lonmax=3, latmin=48, latmax=60)
        cfp.levs(min=265, max=285, step=1)

        cfp.con(f.subspace(time=15))

    @compare_plot_results
    def test_example_4(self):
        """Test Example 4: north pole polar stereographic projection."""
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("eastward_wind")[0]

        cfp.mapset(proj="npstere")

        cfp.con(f.subspace(pressure=500))

    @compare_plot_results
    def test_example_5(self):
        """Test Example 5: south pole with a set latitude plot limit.

        South pole polar stereographic projection with 30 degrees
        south being the latitude plot limit.
        """
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("eastward_wind")[0]

        cfp.mapset(proj="spstere", boundinglat=-30, lon_0=180)

        cfp.con(f.subspace(pressure=500))

    @compare_plot_results
    def test_example_6(self):
        """Test Example 6: latitude-pressure plot."""
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("geopotential")[0]

        cfp.con(f.subspace(longitude=0))

    @compare_plot_results
    def test_example_7(self):
        """Test Example 7: latitude-pressure plot of a zonal mean."""
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("eastward_wind")[0]

        cfp.con(f.collapse("mean", "longitude"))

    @compare_plot_results
    def test_example_8(self):
        """Test Example 8: plot showing latitude against log-scale pressure."""
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("eastward_wind")[0]

        cfp.con(f.collapse("mean", "longitude"), ylog=1)

    @compare_plot_results
    def test_example_9(self):
        """Test Example 9: longitude-pressure plot."""
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("air_temperature")[0]

        cfp.con(f.collapse("mean", "latitude"))

    @compare_plot_results
    def test_example_10(self):
        """Test Example 10: latitude-time Hovmuller plot."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.cscale("plasma")

        cfp.con(f.subspace(longitude=0), lines=0)

    @compare_plot_results
    def test_example_11(self):
        """Test Example 11: latitude-time subset Hovmuller plot."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.gset(-30, 30, "1960-1-1", "1980-1-1")
        cfp.levs(min=280, max=305, step=1)
        cfp.cscale("plasma")

        cfp.con(f.subspace(longitude=0), lines=0)

    @compare_plot_results
    def test_example_12(self):
        """Test Example 12: longitude-time Hovmuller plot."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.cscale("plasma")

        cfp.con(f.subspace(latitude=0), lines=0)

    @compare_plot_results
    def test_example_13(self):
        """Test Example 13: basic vector plot."""
        f = cf.read(f"{self.data_dir}/ggap.nc")

        u = f.select_by_identity("eastward_wind")[0]
        v = f.select_by_identity("northward_wind")[0]

        # Subspace to get values for a specified pressure, here 500 mbar
        u = u.subspace(pressure=500)
        v = v.subspace(pressure=500)

        cfp.vect(u=u, v=v, key_length=10, scale=100, stride=5)

    @compare_plot_results
    def test_example_14(self):
        """Test Example 14: vector plot with colour contour map."""
        f = cf.read(f"{self.data_dir}/ggap.nc")

        u = f.select_by_identity("eastward_wind")[0]
        v = f.select_by_identity("northward_wind")[0]
        t = f.select_by_identity("air_temperature")[0]

        # Subspace to get values for a specified pressure, here 500 mbar
        u = u.subspace(pressure=500)
        v = v.subspace(pressure=500)
        t = t.subspace(pressure=500)

        cfp.gopen()
        cfp.mapset(lonmin=10, lonmax=120, latmin=-30, latmax=30)
        cfp.levs(min=254, max=270, step=1)
        cfp.con(t)
        cfp.vect(u=u, v=v, key_length=10, scale=50, stride=2)
        cfp.gclose()

    @compare_plot_results
    def test_example_15(self):
        """Test Example 15: polar vector plot."""
        f = cf.read(f"{self.data_dir}/ggap.nc")

        u = f.select_by_identity("eastward_wind")[0]
        v = f.select_by_identity("northward_wind")[0]
        u = u.subspace(Z=500)
        v = v.subspace(Z=500)

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

    @compare_plot_results
    def test_example_16a(self):
        """Test Example 16a: zonal vector plot."""
        c = cf.read(f"{self.data_dir}/vaAMIPlcd_DJF.nc")[0]
        c = c.subspace(Y=cf.wi(-60, 60))
        c = c.subspace(X=cf.wi(80, 160))
        c = c.collapse("T: mean X: mean")

        g = cf.read(f"{self.data_dir}/wapAMIPlcd_DJF.nc")[0]
        g = g.subspace(Y=cf.wi(-60, 60))
        g = g.subspace(X=cf.wi(80, 160))
        g = g.collapse("T: mean X: mean")

        # To avoid a cf-python field bug which would appear if we instead
        # did v = -g, see cf-python Issue #797:
        # https://github.com/NCAS-CMS/cf-python/issues/797
        v = -1 * g

        cfp.vect(
            u=c,
            v=v,
            key_length=[5, 0.05],
            scale=[20, 0.2],
            title="DJF",
            key_location=[0.95, -0.05],
        )

    @compare_plot_results
    def test_example_16b(self):
        """Test Example 16b: basic stream plot."""
        f = cf.read(f"{self.data_dir}/ggap.nc")

        u = f.select_by_identity("eastward_wind")[0]
        v = f.select_by_identity("northward_wind")[0]

        u = u.subspace(pressure=500)
        v = v.subspace(pressure=500)

        u = u.anchor("X", -180)
        v = v.anchor("X", -180)

        cfp.stream(u=u, v=v, density=2)

    @compare_plot_results
    def test_example_16c(self):
        """Test Example 16c: enhanced stream plot."""
        f = cf.read(f"{self.data_dir}/ggap.nc")

        u = f.select_by_identity("eastward_wind")[0]
        v = f.select_by_identity("northward_wind")[0]

        u = u.subspace(pressure=500)
        v = v.subspace(pressure=500)

        u = u.anchor("X", -180)
        v = v.anchor("X", -180)

        magnitude = (u**2 + v**2) ** 0.5
        mag = np.squeeze(magnitude.array)

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

    @compare_plot_results
    def test_example_17(self):
        """Test Example 17: basic stipple plot."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        g = f.subspace(time=15)

        cfp.gopen()
        cfp.cscale("magma")
        cfp.con(g)
        cfp.stipple(f=g, min=220, max=260, size=100, color="#00ff00")
        cfp.stipple(
            f=g, min=300, max=330, size=50, color="#0000ff", marker="s"
        )
        cfp.gclose()

    @compare_plot_results
    def test_example_18(self):
        """Test Example 18: polar stipple plot."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        g = f.subspace(time=15)

        cfp.gopen()
        cfp.cscale("magma")
        cfp.mapset(proj="npstere")
        cfp.con(g)
        cfp.stipple(f=g, min=265, max=295, size=100, color="#00ff00")
        cfp.gclose()

    @compare_plot_results
    def test_example_19a(self):
        """Test Example 19a: multiple plots as subplots."""
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("eastward_wind")[0]

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

    @compare_plot_results
    def test_example_19b(self):
        """Test Example 19b: multiple plots with user specified positions."""
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("eastward_wind")[0]

        cfp.gopen(user_position=True)

        cfp.gpos(xmin=0.1, xmax=0.5, ymin=0.55, ymax=1.0)
        cfp.con(f.subspace(Z=500), title="500mb", lines=False)

        cfp.gpos(xmin=0.55, xmax=0.95, ymin=0.55, ymax=1.0)
        cfp.con(f.subspace(Z=100), title="100mb", lines=False)

        cfp.gpos(xmin=0.3, xmax=0.7, ymin=0.1, ymax=0.55)
        cfp.con(f.subspace(Z=10), title="10mb", lines=False)

        cfp.gclose()

    @compare_plot_results
    def test_example_19c(self):
        """Test Example 19c: user-specified plot positioning.

        User specified plot position to accomodate more than one color bar.
        """
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("eastward_wind")[0]

        g = f.collapse("X: mean")

        cfp.gopen(user_position=True)

        cfp.gpos(xmin=0.2, ymin=0.2, xmax=0.8, ymax=0.8)
        cfp.lineplot(
            g.subspace(pressure=100),
            marker="o",
            color="blue",
            title="Zonal mean zonal wind at 100mb",
        )

        cfp.cscale("seaice_2", ncols=20)
        levs = np.arange(282, 320, 2)
        cfp.cbar(levs=levs, position=[0.2, 0.1, 0.6, 0.02], title="seaice_2")

        cfp.cscale("topo_15lev", ncols=22)
        levs = np.arange(-100, 2000, 100)
        cfp.cbar(
            levs=levs,
            position=[0.03, 0.2, 0.04, 0.6],
            orientation="vertical",
            title="topo_15lev",
        )

        cfp.gclose()

    @compare_plot_results
    def test_example_20(self):
        """Test Example 20: user labelling of axes."""
        fl = cf.read(f"{self.data_dir}/Geostropic_Adjustment.nc")
        f = fl.select_by_identity("ncvar%v")[0]

        cfp.con(f.subspace[9])

    def test_example_21a(self):
        """Test Example 21a: rotated pole data plot."""
        fl = cf.read(f"{self.data_dir}/Geostropic_Adjustment.nc")
        f = fl.select_by_identity("ncvar%v")[0]

        cfp.con(
            f.subspace[9],
            title="test data",
            xticks=np.arange(5) * 100000 + 100000,
            yticks=np.arange(7) * 2000 + 2000,
            xlabel="x-axis",
            ylabel="z-axis",
        )

    @compare_plot_results
    def test_example_21b(self):
        """Test Example 21b"""
        f = cf.read(f"{self.data_dir}/rgp.nc")[0]

        cfp.cscale("plasma")

        cfp.con(f)

    @compare_plot_results
    def test_example_22other(self):
        """Test Example 22 (other, due to duplicate label of 22)."""
        f = cf.read(f"{self.data_dir}/rgp.nc")[0]

        cfp.cscale("plasma")
        cfp.mapset(proj="rotated")

        cfp.con(f)

    @compare_plot_results
    def test_example_23a(self):
        """Test Example 23a."""
        f = cf.read(f"{self.data_dir}/rgp.nc")[0]

        data = f.array
        xvec = f.construct("ncvar%x").array
        yvec = f.construct("ncvar%y").array
        xpole = 160
        ypole = 30

        cfp.gopen()
        cfp.cscale("plasma")
        xpts = np.arange(np.size(xvec))
        ypts = np.arange(np.size(yvec))
        cfp.gset(
            xmin=0, xmax=np.size(xvec) - 1, ymin=0, ymax=np.size(yvec) - 1
        )
        cfp.levs(min=980, max=1035, step=2.5)
        cfp.con(data, xpts, ypts[::-1])
        cfp.rgaxes(xpole=xpole, ypole=ypole, xvec=xvec, yvec=yvec)
        cfp.gclose()

    @compare_plot_results
    def test_example_23b(self):
        """Test Example 23b."""
        fl = cf.read(
            f"{self.data_dir}/20160601-05T0000Z_INCOMPASS_km4p4_uv_RH_500.nc"
        )
        r = fl.select_by_identity("long_name=Relative humidity")[0]
        u = fl.select_by_identity("eastward_wind")[0]
        v = fl.select_by_identity("northward_wind")[0]

        cfp.mapset(50, 100, 5, 35)
        cfp.levs(0, 90, 15, extend="neither")

        cfp.gopen()
        cfp.con(r, lines=False)
        cfp.vect(u=u, v=v, stride=40, key_length=10)
        cfp.gclose()

    @compare_plot_results
    def test_example_24a(self):
        """Test Example 24a.

        Test example for unstructured grids: LFRic example 1, now
        numbered to become the missing example 24, part (a).

        NOTE, TODO: relative to example from docs, have added
        'blockfill=True' to get well-defined edges on faces, otherwise
        looks very similar to 'gen_fig_unstructured_lfric_3' plot, with
        edges all blurred together.
        """
        f = cf.read(f"{self.data_dir}/lfric_initial.nc")

        # Select the relevant fields for the objects required for the plot,
        # taking the air potential temperature as a variable to choose to view.
        pot = f.select_by_identity("air_potential_temperature")[0]
        lats = f.select_by_identity("latitude")[0]
        lons = f.select_by_identity("longitude")[0]
        faces = f.select_by_identity("cf_role=face_edge_connectivity")[0]

        # Reduce the variable to match the shapes
        pot = pot[4, :]

        cfp.levs(240, 310, 5)

        cfp.con(
            f=pot,
            face_lons=lons,
            face_lats=lats,
            face_connectivity=faces,
            lines=False,
            blockfill=True,
        )

    @compare_plot_results
    def test_example_24b(self):
        """Test Example 24b.

        Test example for unstructured grids: LFRic example 2, now
        numbered to become the missing example 24, part (b).

        NOTE, TODO: there are 3 'sides' of missing data in the cubed-sphere
        grid, a clear issue. For now the reference plot has this in. An
        issue will be raised to note this and eventually fix it.
        """
        f = cf.read(f"{self.data_dir}/lfric_initial.nc")

        # Select the relevant fields for the objects required for the plot,
        # taking the air potential temperature as a variable to choose to view.
        pot = f.select_by_identity("air_potential_temperature")[0]
        lats = f.select_by_identity("latitude")[0]
        lons = f.select_by_identity("longitude")[0]
        faces = f.select_by_identity("cf_role=face_edge_connectivity")[0]

        # Reduce the variable to match the shapes
        pot = pot[4, :]

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

    @compare_plot_results
    def test_example_24c(self):
        """Test Example 24c.

        Test example for unstructured grids: LFRic example 3, now
        numbered to become the missing example 24, part (c).
        """
        f = cf.read(f"{self.data_dir}/lfric_initial.nc")
        pot = f.select_by_identity("air_potential_temperature")[0]

        g = pot[0, :]
        cfp.con(g, lines=False)

    @compare_plot_results
    def test_example_25(self):
        """Test Example 25.

        Test example for unstructured grids: ORCA grid example 1.
        """
        f = cf.read(f"{self.data_dir}/orca2.nc")

        # Get an Orca grid and flatten the arrays
        lons = f.select_by_identity("ncvar%longitude")[0]
        lats = f.select_by_identity("ncvar%latitude")[0]
        temp = f.select_by_identity("ncvar%sst")[0]

        lons.flatten(inplace=True)
        lats.flatten(inplace=True)
        temp.flatten(inplace=True)

        # Note: in this case we can't input the 'temp' field as-is,
        # because it isn't CF-compliant, notably it doesn't have
        # coordinates of any kind set. So we must pull out the array
        # and input that, along with the corresponding lat and lon arrays.
        cfp.con(f=temp.array, x=lons.array, y=lats.array, ptype=1)

    @compare_plot_results
    def test_example_26a(self):
        """Test Example 26a.

        Test example for unstructured grids: station data example 1, now
        numbered to become the missing example 26, part (a).
        """
        # Arrays for data
        lons = []
        lats = []
        pressure = []
        temp = []

        # Read data and make the contour plot
        f = open(f"{self.data_dir}/synop_data.txt")
        lines = f.readlines()
        for line in lines:
            mysplit = line.split()
            lons = np.append(lons, float(mysplit[1]))
            lats = np.append(lats, float(mysplit[2]))
            pressure = np.append(pressure, float(mysplit[3]))
            temp = np.append(temp, float(mysplit[4]))

        cfp.con(
            x=lons, y=lats, f=temp, ptype=1, colorbar_orientation="vertical"
        )

    @compare_plot_results
    def test_example_26b(self):
        """Test Example 26b.

        Test example for unstructured grids: station data example 2, now
        numbered to become the missing example 26, part (b).
        """
        # Arrays for data
        lons = []
        lats = []
        pressure = []
        temp = []

        # Read data and make the contour plot
        f = open(f"{self.data_dir}/synop_data.txt")
        lines = f.readlines()
        for line in lines:
            mysplit = line.split()
            lons = np.append(lons, float(mysplit[1]))
            lats = np.append(lats, float(mysplit[2]))
            pressure = np.append(pressure, float(mysplit[3]))
            temp = np.append(temp, float(mysplit[4]))

        cfp.gopen()
        cfp.con(
            x=lons, y=lats, f=temp, ptype=1, colorbar_orientation="vertical"
        )
        for i in np.arange(len(lines)):
            cfp.plotvars.mymap.text(
                float(lons[i]),
                float(lats[i]),
                str(temp[i]),
                horizontalalignment="center",
                verticalalignment="center",
                transform=ccrs.PlateCarree(),
            )

        cfp.gclose()

    @compare_plot_results
    def test_example_27(self):
        """Test Example 27: basic graph plot."""
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("eastward_wind")[0]

        g = f.collapse("X: mean")

        cfp.gopen()
        cfp.lineplot(
            g.subspace(pressure=100),
            marker="o",
            color="blue",
            title="Zonal mean zonal wind at 100mb",
        )
        cfp.gclose()

    @compare_plot_results
    def test_example_28(self):
        """Test Example 28: line and legend plot."""
        fl = cf.read(f"{self.data_dir}/ggap.nc")
        f = fl.select_by_identity("eastward_wind")[0]

        g = f.collapse("X: mean")

        xticks = [-90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90]
        xticklabels = [
            "90S",
            "75S",
            "60S",
            "45S",
            "30S",
            "15S",
            "0",
            "15N",
            "30N",
            "45N",
            "60N",
            "75N",
            "90N",
        ]
        xpts = [-30, 30, 30, -30, -30]
        ypts = [-8, -8, 5, 5, -8]

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
        cfp.plotvars.plot.text(
            35, -2, "Region of interest", horizontalalignment="left"
        )
        cfp.gclose()

    @compare_plot_results
    def test_example_29(self):
        """Test Example 29: global average annual temperature."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        temp = f.subspace(time=cf.wi(cf.dt("1900-01-01"), cf.dt("1980-01-01")))
        temp_annual = temp.collapse("T: mean", group=cf.Y())
        temp_annual_global = temp_annual.collapse("area: mean", weights="area")
        temp_annual_global.Units -= 273.15

        cfp.lineplot(
            temp_annual_global,
            title="Global average annual temperature",
            color="blue",
        )

    @compare_plot_results
    def test_example_30(self):
        """Test Example 30: two axis plotting."""
        tol = cf.RTOL(1e-5)

        fl = cf.read(f"{self.data_dir}/ggap.nc")

        f = fl.select_by_identity("eastward_wind")[0]
        u = f.collapse("X: mean")
        u1 = u.subspace(Y=cf.isclose(-61.12099075))
        u2 = u.subspace(Y=cf.isclose(0.56074494))

        g = fl.select_by_identity("air_temperature")[0]
        t = g.collapse("X: mean")
        t1 = t.subspace(Y=cf.isclose(-61.12099075))
        t2 = t.subspace(Y=cf.isclose(0.56074494))

        cfp.gopen()
        cfp.gset(-30, 30, 1000, 0)
        cfp.lineplot(u1, color="r")
        cfp.lineplot(u2, color="r")
        cfp.gset(190, 300, 1000, 0, twiny=True)
        cfp.lineplot(t1, color="b")
        cfp.lineplot(t2, color="b")
        cfp.gclose()

    @compare_plot_results
    def test_example_31(self):
        """Test Example 31: UKCP projection.

        NOTE: for docs, remove the '**self.setvars_dict' which relates
        to Issue https://github.com/NCAS-CMS/cf-plot/issues/93.
        """
        f = cf.read(f"{self.data_dir}/ukcp_rcm_test.nc")[0]

        cfp.mapset(proj="UKCP", resolution="50m")
        cfp.levs(-3, 7, 0.5)
        cfp.setvars(grid_x_spacing=1, grid_y_spacing=1, **self.setvars_dict)

        cfp.con(f, lines=False)

    @compare_plot_results
    def test_example_32(self):
        """Test Example 32: UKCP projection with blockfill.

        NOTE, TODO: the code mostly works with a mostly correct
        and reference plot, but there are
        a few issues, namely a patch of unplotted area in the
        Scottish highlands indicating a fill value / masking processing
        issue, perhaps wider than UKCP blockfill, and also the gridlines
        extending out relative to the desired result (see docs image at
        https://ncas-cms.github.io/cf-plot/build/_images/fig32.png).

        NOTE ALSO: for docs, remove the '**self.setvars_dict' which relates
        to Issue https://github.com/NCAS-CMS/cf-plot/issues/93.
        """
        f = cf.read(f"{self.data_dir}/ukcp_rcm_test.nc")[0]

        cfp.mapset(proj="UKCP", resolution="50m")
        cfp.levs(-3, 7, 0.5)
        cfp.setvars(grid_colour="grey", **self.setvars_dict)

        cfp.con(
            f,
            lines=False,
            blockfill=True,
            # Centered over UK region with spacing of 1 each
            xticks=np.arange(14) - 11,
            yticks=np.arange(13) + 49,
        )

    @compare_plot_results
    def test_example_33(self):
        """Test Example 33: OSGB and EuroPP projections."""
        f = cf.read(f"{self.data_dir}/ukcp_rcm_test.nc")[0]

        cfp.levs(-3, 7, 0.5)

        cfp.gopen(columns=2)
        cfp.mapset(proj="OSGB", resolution="50m")
        cfp.con(f, lines=False, colorbar_label_skip=2)
        cfp.gpos(2)
        cfp.mapset(proj="EuroPP", resolution="50m")
        cfp.con(f, lines=False, colorbar_label_skip=2)
        cfp.gclose()

    @compare_plot_results
    def test_example_34(self):
        """Test Example 34: Cropped Lambert conformal projection."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.mapset(proj="lcc", lonmin=-50, lonmax=50, latmin=20, latmax=85)

        cfp.con(f.subspace(time=15))

    @compare_plot_results
    def test_example_35(self):
        """Test Example 35: Mollweide projection."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.mapset(proj="moll")

        cfp.con(f.subspace(time=15))

    @compare_plot_results
    def test_example_36(self):
        """Test Example 36: Mercator projection."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.mapset(proj="merc")

        cfp.con(f.subspace(time=15))

    @compare_plot_results
    def test_example_37(self):
        """Test Example 37: Orthographic projection."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.mapset(proj="ortho")

        cfp.con(f.subspace(time=15))

    @compare_plot_results
    def test_example_38(self):
        """Test Example 38: Robinson projection."""
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.mapset(proj="robin")

        cfp.con(f.subspace(time=15))

    @compare_plot_results
    def test_example_39(self):
        """Test Example 39: basic track plotting trajectory."""
        f = cf.read(f"{self.data_dir}/ff_trs_pos.nc")[0]

        cfp.traj(f)

    @compare_plot_results
    def test_example_39b(self):
        """Test Example 39: single DSG with no trajectory dimension (1D).

        TODO convert 39 to 39a now this is the 'b' example, to keep
        'traj' examples/tests grouped together in order.

        TODO make this a group with the other DSGs from before, namely
        Exs 42a and 42b, but this is simplest so make it 42a and bump
        the other two in number.
        """
        f = cf.read(f"{self.data_dir}/dsg_trajectory.nc")[0]

        # This is over a small part of France so focus in on that
        # area and make the land borders higher-resolution
        cfp.mapset(lonmin=3, lonmax=6, latmin=51, latmax=54, resolution="10m")

        cfp.traj(f)

    @compare_plot_results
    def test_example_40(self):
        """Test Example 40: tracks in the polar stereographic projection."""
        f = cf.read(f"{self.data_dir}/ff_trs_pos.nc")[0]

        cfp.mapset(proj="npstere")

        cfp.traj(f)

    @compare_plot_results
    def test_example_41(self):
        """Test Example 41: feature propagation over Europe."""
        f = cf.read(f"{self.data_dir}/ff_trs_pos.nc")[0]

        cfp.mapset(lonmin=-20, lonmax=20, latmin=30, latmax=70)

        cfp.traj(f, vector=True, markersize=0.0, fc="b", ec="b")

    @compare_plot_results
    def test_example_42a(self):
        """Test Example 42a: intensity legend."""
        f = cf.read(f"{self.data_dir}/ff_trs_pos.nc")[0]

        cfp.mapset(lonmin=-50, lonmax=50, latmin=20, latmax=80)
        g = f.subspace(time=cf.wi(cf.dt("1979-12-01"), cf.dt("1979-12-10")))
        g = g * 1e5
        cfp.levs(0, 12, 1, extend="max")
        cfp.cscale("scale1", below=0, above=13)

        cfp.traj(
            g,
            legend=True,
            markersize=40.0,
            colorbar_title="Relative Vorticity (Hz) * 1e5",
        )

    @compare_plot_results
    def test_example_42b(self):
        """Test Example 42b: intensity legend with lines."""
        f = cf.read(f"{self.data_dir}/ff_trs_pos.nc")[0]

        cfp.mapset(lonmin=-50, lonmax=50, latmin=20, latmax=80)
        g = f.subspace(time=cf.wi(cf.dt("1979-12-01"), cf.dt("1979-12-10")))
        g = g * 1e5
        cfp.levs(0, 12, 1, extend="max")
        cfp.cscale("scale1", below=0, above=13)
        cfp.traj(
            g,
            legend_lines=True,
            linewidth=2,
            colorbar_title="Relative Vorticity (Hz) * 1e5",
        )

    @pytest.mark.skip(reason="WRF test data not available")
    @compare_plot_results
    def test_example_43(self):
        """Test Example 43: plotting WRF data."""
        # TODO add new WRF testing, wherebouts of file used in original
        # test, "wrf2.nc", are not known, so need a new file and one that
        # is not 5GB besides!


if __name__ == "__main__":
    print("==================\nExamples Testing\n==================\n")
    cov = coverage.Coverage()
    cov.start()
    pytest.main(["-v", __file__])

    cov.stop()
    cov.save()

    cov.report()
    print("================\nEnd of Examples Testing\n================\n")
