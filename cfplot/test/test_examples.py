"""
Regression testing module for cf-plot.

1. Test standard `levs`, `gvals`, and `lon` and `lat` labelling.
2. Make all the documentation example plots and compare them to
   reference expected plots to ensure they are the same.

"""

import coverage
import faulthandler
import functools
import hashlib
from pprint import pformat
import numpy as np
import os
import unittest

from netCDF4 import Dataset as ncfile
from scipy.interpolate import griddata

import matplotlib.testing.compare as mpl_compare

import cfplot as cfp
import cf


faulthandler.enable()  # to debug seg faults and timeouts


DATA_DIR = "cfplot_data"
TEST_REF_DIR = "./reference-example-images"
TEST_GEN_DIR = "./generated-example-images"
if not os.path.exists(TEST_GEN_DIR):
    os.makedirs(TEST_GEN_DIR)

# Keep track of number of examples including sub-numbering (a, b, etc.)
# as used across the docs and for the ExamplesTest.
NAMED_EXAMPLES = [str(n) for n in range(1, 43)]  # no lettering
# Al lettered examples e.g. 16b
NAMED_EXAMPLES += [
    "16b",
    "16c",
    "19a",
    "19b",
    "21other",
    "22other",
    "23other",
    "42a",
]
# Note: failing so no comparison plots for 16, 24, 25, 26.


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
            f"{TEST_REF_DIR}/ref_fig_{tid}.png",  # expected (reference) plot
            f"{TEST_GEN_DIR}/gen_fig_{tid}.png",  # actual (generated) plot
            tol=0.001,
            in_decorator=True,
        )

        # If the plot image comparison passed, image_cmp_result will be None
        # (see https://matplotlib.org/stable/api/
        # testing_api.html#matplotlib.testing.compare.compare_images)
        msg = f"\nPlot comparison shows differences, see result dict for details."
        _self.assertIsNone(image_cmp_result, msg=msg)

    return wrapper


def compare_arrays(
    ref=None,
    levs_test=None,
    gvals_test=None,
    mapaxis_test=None,
    min=None,
    max=None,
    step=None,
    mult=None,
    type=None,
):
    """
    Compare arrays and return an error string if they don't match.
    """
    plotvar_levs = cfp.plotvars.levels

    anom = 0
    if levs_test:
        cfp.levs(min, max, step)
        if np.size(ref) != np.size(plotvar_levs):
            anom = 1
        else:
            for val in np.arange(np.size(ref)):
                if abs(ref[val] - plotvar_levs[val]) >= 1e-6:
                    anom = 1

        if anom == 1:
            print(
                "***cfp.levs failure***\n"
                f"min, max, step are {min}, {max}, {step}\n"
                "generated levels are:\n"
                f"{plotvar_levs}\n"
                f"expected levels:\n{ref}"
            )
        else:
            pass_str = f"Passed cfp.levs(min={min}, max={max}, step={step})"
            print(pass_str)

    anom = 0
    if gvals_test:
        vals, testmult = cfp._gvals(min, max)
        if np.size(ref) != np.size(vals):
            anom = 1
        else:
            for val in np.arange(np.size(ref)):
                if abs(ref[val] - vals[val]) >= 1e-6:
                    anom = 1
        if mult != testmult:
            anom = 1

        if anom == 1:
            print(
                "***gvals failure***\n"
                f"cfp._gvals({min}, {max})\n\n"
                f"generated values are:{vals}\n"
                f"with a  multiplier of {testmult}\n\n"
                f"expected values:{ref}\n"
                f"with a multiplier of {mult}\n"
            )
        else:
            pass_str = f"Passed cfp._gvals({min}, {max})"
            print(pass_str)

    anom = 0
    if mapaxis_test:
        ref_ticks = ref[0]
        ref_labels = ref[1]
        test_ticks, test_labels = cfp._mapaxis(min=min, max=max, type=type)
        if np.size(test_ticks) != np.size(ref_ticks):
            anom = 1
        else:
            for val in np.arange(np.size(ref_ticks)):
                if abs(ref_ticks[val] - test_ticks[val]) >= 1e-6:
                    anom = 1
                if ref_labels[val] != test_labels[val]:
                    anom = 1

        if anom == 1:
            print(
                "***mapaxis failure***\n\n"
                f"cfp._mapaxis(min={min}, max={max}, type={type})\n"
                f"generated values are:{test_ticks}\n"
                f"with labels:{test_labels}\n\n"
                f"expected ticks:{ref_ticks}\n"
                f"with labels:{ref_labels}\n"
            )
        else:
            pass_str = (
                f"Passed cfp._mapaxis<(min={min}, max={max}, type={type})"
            )
            print(pass_str)


class BasicArrayTest(unittest.TestCase):
    """Contour levels `levs` array comparison testing."""

    def setup(self):
        """Preparations called immediately before each test method."""
        print(
            "---------------------------------\n"
            "Testing for `levs` contour levels\n"
            "---------------------------------\n"
        )

    def test_arrays_1(self):
        """Test 1 for `levs` contour levels array comparison."""
        ref_answer = [
            -35,
            -30,
            -25,
            -20,
            -15,
            -10,
            -5,
            0,
            5,
            10,
            15,
            20,
            25,
            30,
            35,
            40,
            45,
            50,
            55,
            60,
            65,
        ]
        compare_arrays(ref=ref_answer, levs_test=True, min=-35, max=65, step=5)

        ref_answer = [
            -6.0,
            -4.8,
            -3.6,
            -2.4,
            -1.2,
            0.0,
            1.2,
            2.4,
            3.6,
            4.8,
            6.0,
        ]
        compare_arrays(ref=ref_answer, levs_test=True, min=-6, max=6, step=1.2)

    def test_arrays_2(self):
        """Test 2 for `levs` contour levels array comparison."""
        ref_answer = [
            50000,
            51000,
            52000,
            53000,
            54000,
            55000,
            56000,
            57000,
            58000,
            59000,
            60000,
        ]
        compare_arrays(
            ref=ref_answer, levs_test=True, min=50000, max=60000, step=1000
        )

    def test_arrays_3(self):
        """Test 3 for `levs` contour levels array comparison."""
        ref_answer = [
            -7000,
            -6500,
            -6000,
            -5500,
            -5000,
            -4500,
            -4000,
            -3500,
            -3000,
            -2500,
            -2000,
            -1500,
            -1000,
            -500,
        ]
        compare_arrays(
            ref=ref_answer, levs_test=True, min=-7000, max=-300, step=500
        )


class GvalsArrayTest(unittest.TestCase):
    """Contour levels `gvals` array comparison testing."""

    def setup(self):
        """Preparations called immediately before each test method."""
        print(
            "----------------------------------\n"
            "Testing for `gvals` contour levels\n"
            "----------------------------------\n"
        )

    def test_gvals_1(self):
        """Test 1 for `gvals` contour levels array comparison."""
        ref_answer = [
            281,
            282,
            283,
            284,
            285,
            286,
            287,
            288,
            289,
            290,
            291,
            292,
            293,
        ]
        compare_arrays(
            ref=ref_answer,
            min=280.50619506835938,
            max=293.48431396484375,
            mult=0,
            gvals_test=True,
        )

    def test_gvals_2(self):
        """Test 2 for `gvals` contour levels array comparison."""
        ref_answer = [
            0.356,
            0.385,
            0.414,
            0.443,
            0.472,
            0.501,
            0.53,
            0.559,
            0.588,
            0.617,
            0.646,
            0.675,
        ]
        compare_arrays(
            ref=ref_answer, min=0.356, max=0.675, mult=0, gvals_test=True
        )

    def test_gvals_3(self):
        """Test 3 for `gvals` contour levels array comparison."""
        ref_answer = [
            -45,
            -40,
            -35,
            -30,
            -25,
            -20,
            -15,
            -10,
            -5,
            0,
            5,
            10,
            15,
            20,
            25,
            30,
            35,
            40,
            45,
            50,
        ]
        compare_arrays(
            ref=ref_answer,
            min=-49.510975,
            max=53.206604,
            mult=0,
            gvals_test=True,
        )

    def test_gvals_4(self):
        """Test 4 for `gvals` contour levels array comparison."""
        ref_answer = [
            47000,
            48000,
            49000,
            50000,
            51000,
            52000,
            53000,
            54000,
            55000,
            56000,
            57000,
            58000,
            59000,
            60000,
            61000,
            62000,
            63000,
            64000,
        ]
        compare_arrays(
            ref=ref_answer, min=46956, max=64538, mult=0, gvals_test=True
        )

    def test_gvals_5(self):
        """Test 5 for `gvals` contour levels array comparison."""
        ref_answer = [
            -1.0,
            -0.9,
            -0.8,
            -0.7,
            -0.6,
            -0.5,
            -0.4,
            -0.3,
            -0.2,
            -0.1,
            0.0,
            0.1,
        ]
        compare_arrays(
            ref=ref_answer, min=-1.0, max=0.1, mult=0, gvals_test=True
        )


class LonLatTest(unittest.TestCase):
    """Tests for `mapaxis` longitude-latitude labelling."""

    def setup(self):
        """Preparations called immediately before each test method."""
        print("--------------------------------------------------\n")
        print("Testing for `mapaxis` longitude-latitude labelling\n")
        print("--------------------------------------------------\n")

    def test_lonlat_1(self):
        """Test 1 for `mapaxis` longitude-latitude labelling."""
        ref_answer = (
            [-180, -120, -60, 0, 60, 120, 180],
            ["180", "120W", "60W", "0", "60E", "120E", "180"],
        )
        compare_arrays(
            ref=ref_answer, min=-180, max=180, type=1, mapaxis_test=True
        )

    def test_lonlat_2(self):
        """Test 2 for `mapaxis` longitude-latitude labelling."""
        ref_answer = (
            [150, 180, 210, 240, 270],
            ["150E", "180", "150W", "120W", "90W"],
        )
        compare_arrays(
            ref=ref_answer, min=135, max=280, type=1, mapaxis_test=True
        )

    def test_lonlat_3(self):
        """Test 3 for `mapaxis` longitude-latitude labelling."""
        ref_answer = (
            [0, 10, 20, 30, 40, 50, 60, 70, 80, 90],
            [
                "0",
                "10E",
                "20E",
                "30E",
                "40E",
                "50E",
                "60E",
                "70E",
                "80E",
                "90E",
            ],
        )
        compare_arrays(
            ref=ref_answer, min=0, max=90, type=1, mapaxis_test=True
        )

    def test_lonlat_4(self):
        """Test 4 for `mapaxis` longitude-latitude labelling."""
        ref_answer = (
            [-90, -60, -30, 0, 30, 60, 90],
            ["90S", "60S", "30S", "0", "30N", "60N", "90N"],
        )
        compare_arrays(
            ref=ref_answer, min=-90, max=90, type=2, mapaxis_test=True
        )

    def test_lonlat_5(self):
        """Test 5 for `mapaxis` longitude-latitude labelling."""
        ref_answer = (
            [0, 5, 10, 15, 20, 25, 30],
            ["0", "5N", "10N", "15N", "20N", "25N", "30N"],
        )
        compare_arrays(
            ref=ref_answer, min=0, max=30, type=2, mapaxis_test=True
        )


class ExamplesTest(unittest.TestCase):
    """Run through gallery examples and compare to reference plots."""

    data_dir = DATA_DIR
    save_gen_dir = TEST_GEN_DIR
    ref_dir = TEST_REF_DIR
    test_id = None

    def setUp(self):
        """Preparations called immediately before each test method."""
        # Get a filename fname with the ID of test_example_X component X
        test_method_name = unittest.TestCase.id(self).split(".")[-1]
        self.test_id = test_method_name.rsplit("test_example_")[1]
        fname = f"{self.save_gen_dir}/" f"gen_fig_{self.test_id}.png"
        cfp.setvars(
            file=fname,
            viewer="matplotlib",
        )

    def tearDown(self):
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
        # Traceback (most recent call last):
        #   File "/home/slb93/git-repos/cf-plot/cfplot/test/test_examples.py", line 498, in test_example_2
        #     cfp.con(f.subspace(time=15), blockfill=True, lines=False)
        #   File "/home/slb93/git-repos/cf-plot/cfplot/cfplot.py", line 3349, in con
        #     raise TypeError(errstr)
        # TypeError:

        # cfp.con - blockfill error
        # need to match number of colours and contour intervals
        # Don't forget to take account of the colorbar extensions

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
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        cfp.mapset(proj="npstere")

        cfp.con(f.subspace(pressure=500))

    @compare_plot_results
    def test_example_5(self):
        """Test Example 5: south pole with a set latitude plot limit.

        South pole polar stereographic projection with 30 degrees
        south being the latitude plot limit.
        """
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        cfp.mapset(proj="spstere", boundinglat=-30, lon_0=180)

        cfp.con(f.subspace(pressure=500))

    @compare_plot_results
    def test_example_6(self):
        """Test Example 6: latitude-pressure plot."""
        f = cf.read(f"{self.data_dir}/ggap.nc")[3]

        cfp.con(f.subspace(longitude=0))

    @compare_plot_results
    def test_example_7(self):
        """Test Example 7: latitude-pressure plot of a zonal mean."""
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        cfp.con(f.collapse("mean", "longitude"))

    @compare_plot_results
    def test_example_8(self):
        """Test Example 8: plot showing latitude against log-scale pressure."""
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        cfp.con(f.collapse("mean", "longitude"), ylog=1)

    @unittest.expectedFailure  # works standalone, test suite gives IndexError
    @compare_plot_results
    def test_example_9(self):
        """Test Example 9: longitude-pressure plot."""
        # TODO SLB, flaky/bad test alert! This works in interactive Python
        # but in test suite it fails with:
        # Traceback (most recent call last):
        # File "/home/slb93/git-repos/cf-plot/cfplot/test/test_examples.py", line 551, in test_example_9
        #   cfp.con(lat_mean)
        # File "/home/slb93/git-repos/cf-plot/cfplot/cfplot.py", line 3262, in con
        #   f = f.subspace(Y=cf.wi(-90.0, plotvars.boundinglat))
        #       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # File "/home/slb93/git-repos/cf-python/cf/subspacefield.py", line 353, in __call__
        #   raise error
        # File "/home/slb93/git-repos/cf-python/cf/subspacefield.py", line 348, in __call__
        #   out = field[indices]
        #         ~~~~~^^^^^^^^^
        # File "/home/slb93/git-repos/cf-python/cf/field.py", line 450, in __getitem__
        #   raise IndexError(
        # IndexError: Indices [slice(None, None, None), slice(None, None, None),
        # array([], dtype=int64), slice(None, None, None)] result in a
        # subspaced shape of (1, 23, 0, 320), but can't create a subspace
        # of Field that has a size 0 axis

        f = cf.read(f"{self.data_dir}/ggap.nc")[0]

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

        u = f[1].subspace(pressure=500)
        v = f[3].subspace(pressure=500)

        cfp.vect(u=u, v=v, key_length=10, scale=100, stride=5)

    @compare_plot_results
    def test_example_14(self):
        """Test Example 14: vector plot with colour contour map."""
        f = cf.read(f"{self.data_dir}/ggap.nc")

        u = f[1].subspace(pressure=500)
        v = f[3].subspace(pressure=500)
        t = f[0].subspace(pressure=500)

        cfp.gopen()
        cfp.mapset(lonmin=10, lonmax=120, latmin=-30, latmax=30)
        cfp.levs(min=254, max=270, step=1)
        cfp.con(t)
        cfp.vect(u=u, v=v, key_length=10, scale=50, stride=2)
        cfp.gclose()

    @compare_plot_results
    def test_example_15(self):
        """Test Example 15: polar vector plot."""
        # TODO avoiding repeated reads, incorporate into docs too
        f = cf.read(f"{self.data_dir}/ggap.nc")
        u = f[1]
        v = f[3]
        u = u.subspace(Z=500)
        v = v.subspace(Z=500)

        cfp.mapset(proj="npstere")

        cfp.vect(
            u=u,
            v=v,
            key_length=10,
            scale=100,
            pts=40,
            title="Polar plot with regular point distribution",
        )

    @unittest.expectedFailure  # errors due to cf-python Issue #797
    @compare_plot_results
    def test_example_16(self):
        """Test Example 16: zonal vector plot."""
        c = cf.read(f"{self.data_dir}/vaAMIPlcd_DJF.nc")[0]
        c = c.subspace(Y=cf.wi(-60, 60))
        c = c.subspace(X=cf.wi(80, 160))
        c = c.collapse("T: mean X: mean")

        g = cf.read(f"{self.data_dir}/wapAMIPlcd_DJF.nc")[0]
        g = g.subspace(Y=cf.wi(-60, 60))
        g = g.subspace(X=cf.wi(80, 160))
        g = g.collapse("T: mean X: mean")

        # This fails due to a cf-python field bug, see cf-python Issue #797:
        # https://github.com/NCAS-CMS/cf-python/issues/797
        cfp.vect(
            u=c,
            v=-g,
            key_length=[5, 0.05],
            scale=[20, 0.2],
            title="DJF",
            key_location=[0.95, -0.05],
        )

    @compare_plot_results
    def test_example_16b(self):
        """Test Example 16b: basic stream plot."""
        f = cf.read(f"{self.data_dir}/ggap.nc")
        u = f[1].subspace(pressure=500)
        v = f[2].subspace(pressure=500)

        u = u.anchor("X", -180)
        v = v.anchor("X", -180)

        cfp.stream(u=u, v=v, density=2)

    @compare_plot_results
    def test_example_16c(self):
        """Test Example 16c: enhanced stream plot."""
        f = cf.read(f"{self.data_dir}/ggap.nc")

        u = f[1].subspace(pressure=500)
        v = f[2].subspace(pressure=500)
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
    def test_example_19(self):
        """Test Example 19: multiple plots as subplots."""
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]
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
    def test_example_19a(self):
        """Test Example 19a: multiple plots with user specified positions."""
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        cfp.gopen(user_position=True)

        cfp.gpos(xmin=0.1, xmax=0.5, ymin=0.55, ymax=1.0)
        cfp.con(f.subspace(Z=500), title="500mb", lines=False)

        cfp.gpos(xmin=0.55, xmax=0.95, ymin=0.55, ymax=1.0)
        cfp.con(f.subspace(Z=100), title="100mb", lines=False)

        cfp.gpos(xmin=0.3, xmax=0.7, ymin=0.1, ymax=0.55)
        cfp.con(f.subspace(Z=10), title="10mb", lines=False)

        cfp.gclose()

    @compare_plot_results
    def test_example_19b(self):
        """Test Example 19b: user-specified plot positioning.

        User specified plot position to accomodate more than one color bar.
        """
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]
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
        f = cf.read(f"{self.data_dir}/Geostropic_Adjustment.nc")[0]

        cfp.con(f.subspace[9])

    def test_example_21(self):
        """Test Example 21: rotated pole data plot."""
        f = cf.read(f"{self.data_dir}/Geostropic_Adjustment.nc")[0]

        cfp.con(
            f.subspace[9],
            title="test data",
            xticks=np.arange(5) * 100000 + 100000,
            yticks=np.arange(7) * 2000 + 2000,
            xlabel="x-axis",
            ylabel="z-axis",
        )

    @compare_plot_results
    def test_example_21other(self):
        """Test Example 21 (other, due to duplicate label of 21)."""
        f = cf.read(f"{self.data_dir}/rgp.nc")[0]

        cfp.cscale("plasma")
        cfp.con(f)

    @compare_plot_results
    def test_example_22(self):
        """Test Example 22:"""
        f = cf.read(f"{self.data_dir}/rgp.nc")[0]

        cfp.cscale("gray")

        cfp.con(f)

    @compare_plot_results
    def test_example_22other(self):
        """Test Example 22 (other, due to duplicate label of 22)."""
        f = cf.read(f"{self.data_dir}/rgp.nc")[0]

        cfp.cscale("plasma")
        cfp.mapset(proj="rotated")

        cfp.con(f)

    @compare_plot_results
    def test_example_23(self):
        """Test Example 23."""
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
    def test_example_23other(self):
        """Test Example 23 (other, due to duplicate label of 23)."""
        f = cf.read(
            f"{self.data_dir}/20160601-05T0000Z_INCOMPASS_km4p4_uv_RH_500.nc"
        )
        cfp.mapset(50, 100, 5, 35)
        cfp.levs(0, 90, 15, extend="neither")

        cfp.gopen()
        cfp.con(f[0], lines=False)
        cfp.vect(u=f[1], v=f[2], stride=40, key_length=10)
        cfp.gclose()

    @unittest.expectedFailure  # IndexError after griddata API conformance
    def test_example_24(self):
        """Test Example 24."""
        # Arrays for data
        lons = []
        lats = []
        pressure = []
        temp = []

        f = open(f"{self.data_dir}/synop_data.txt")

        lines = f.readlines()
        for line in lines:
            mysplit = line.split()
            lons = np.append(lons, float(mysplit[1]))
            lats = np.append(lats, float(mysplit[2]))
            pressure = np.append(pressure, float(mysplit[3]))
            temp = np.append(temp, float(mysplit[4]))

        # Linearly interpolate data to a regular grid
        lons_new = np.arange(140) * 0.1 - 11.0
        lats_new = np.arange(140) * 0.1 + 49.0
        # TODO SLB needs fixing, fails on an IndexError
        temp_new = griddata(
            points=(lons, lats),
            values=temp,
            xi=(lons_new, lats_new),
            method="linear",
        )

        cfp.cscale("parula")

        cfp.con(x=lons_new, y=lats_new, f=temp_new, ptype=1)

    @unittest.expectedFailure  # IndexError after griddata API conformance
    @compare_plot_results
    def test_example_25(self):
        """Test Example 25."""
        # Note the block of code until '---' is shared with example 24.
        # Arrays for data
        lons = []
        lats = []
        pressure = []
        temp = []

        f = open(f"{self.data_dir}/synop_data.txt")

        lines = f.readlines()
        for line in lines:
            mysplit = line.split()
            lons = np.append(lons, float(mysplit[1]))
            lats = np.append(lats, float(mysplit[2]))
            pressure = np.append(pressure, float(mysplit[3]))
            temp = np.append(temp, float(mysplit[4]))

        # Linearly interpolate data to a regular grid
        lons_new = np.arange(140) * 0.1 - 11.0
        lats_new = np.arange(140) * 0.1 + 49.0
        # TODO SLB needs fixing, fails on an IndexError
        temp_new = griddata(
            points=(lons, lats),
            values=temp,
            xi=(lons_new, lats_new),
            method="linear",
        )
        # ---

        cfp.gopen()

        cfp.con(x=lons_new, y=lats_new, f=temp_new, ptype=1)
        for i in np.arange(len(lines)):
            cfp.plotvars.plot.text(
                float(lons[i]),
                float(lats[i]),
                str(temp[i]),
                horizontalalignment="center",
                verticalalignment="center",
            )

        cfp.gclose()

    @unittest.expectedFailure  # ValueError after griddata API conformance
    @compare_plot_results
    def test_example_26(self):
        """Test Example 26."""
        # Get an Orca grid and flatten the arrays
        nc = ncfile(f"{self.data_dir}/orca2.nc")
        lons = np.array(nc.variables["longitude"])
        lats = np.array(nc.variables["latitude"])
        temp = np.array(nc.variables["sst"])
        lons = lons.flatten()
        lats = lats.flatten()
        temp = temp.flatten()

        # Add wrap around at both longitude limits
        pts = np.squeeze(np.where(lons < -150))
        lons = np.append(lons, lons[pts] + 360)
        lats = np.append(lats, lats[pts])
        temp = np.append(temp, temp[pts])

        pts = np.squeeze(np.where(lons > 150))
        lons = np.append(lons, lons[pts] - 360)
        lats = np.append(lats, lats[pts])
        temp = np.append(temp, temp[pts])

        lons_new = np.arange(181 * 8) * 0.25 - 180.0
        lats_new = np.arange(91 * 8) * 0.25 - 90.0
        # TODO SLB needs fixing, fails on a ValueError
        temp_new = griddata(
            points=(lons, lats),
            values=temp,
            xi=(lons_new, lats_new),
            method="linear",
        )

        cfp.con(x=lons_new, y=lats_new, f=temp_new, ptype=1)

    @compare_plot_results
    def test_example_27(self):
        """Test Example 27: basic graph plot."""
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

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
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

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

        # TODO avoiding repeated reads, incorporate into docs too
        f_list = cf.read(f"{self.data_dir}/ggap.nc")
        f = f_list[1]

        u = f.collapse("X: mean")
        u1 = u.subspace(Y=-61.12099075)
        u2 = u.subspace(Y=0.56074494)

        g = f_list[0]
        t = g.collapse("X: mean")
        t1 = t.subspace(Y=-61.12099075)
        t2 = t.subspace(Y=0.56074494)

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
        """Test Example 31: UKCP projection."""
        f = cf.read(f"{self.data_dir}/ukcp_rcm_test.nc")[0]

        cfp.mapset(proj="UKCP", resolution="50m")
        cfp.levs(-3, 7, 0.5)
        cfp.setvars(grid_x_spacing=1, grid_y_spacing=1)

        cfp.con(f, lines=False)

    @unittest.expectedFailure  # errors, issue TBC
    @compare_plot_results
    def test_example_32(self):
        """Test Example 32: UKCP projection with blockfill."""
        # Traceback (most recent call last):
        #   File "/home/slb93/git-repos/cf-plot/cfplot/test/gen-plot.py", line 25, in <module>
        #     cfp.con(
        #   File "/home/slb93/git-repos/cf-plot/cfplot/cfplot.py", line 3871, in con
        #     _bfill(
        #   File "/home/slb93/git-repos/cf-plot/cfplot/cfplot.py", line 1833, in _bfill
        #     colarr[pts] = int(i)
        #     ~~~~~~^^^^^
        # IndexError: too many indices for array: array is 2-dimensional, but 4 were indexed
        f = cf.read(f"{self.data_dir}/ukcp_rcm_test.nc")[0]

        cfp.mapset(proj="UKCP", resolution="50m")
        cfp.levs(-3, 7, 0.5)
        cfp.setvars(grid_colour="grey")

        cfp.con(
            f,
            lines=False,
            blockfill=True,
            xticks=np.arange(14) - 11,
            yticks=np.arange(13) + 49,
        )

    @unittest.expectedFailure  # errors, issue TBC
    @compare_plot_results
    def test_example_33(self):
        """Test Example 33: OSGB and EuroPP projections."""
        # Traceback (most recent call last):
        #   File "/home/slb93/git-repos/cf-plot/cfplot/test/gen-plot.py", line 23, in <module>
        #     cfp.con(f, lines=False, colorbar_label_skip=2)
        #   File "/home/slb93/git-repos/cf-plot/cfplot/cfplot.py", line 4100, in con
        #     cbar(
        #   File "/home/slb93/git-repos/cf-plot/cfplot/cfplot.py", line 10056, in cbar
        #     ax1,
        #     ^^^
        # UnboundLocalError: cannot access local variable 'ax1' where it is not associated with a value
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
    def test_example_42(self):
        """Test Example 42: intensity legend."""
        f = cf.read(f"{self.data_dir}/ff_trs_pos.nc")[0]

        cfp.mapset(lonmin=-50, lonmax=50, latmin=20, latmax=80)
        g = f.subspace(time=cf.wi(cf.dt("1979-12-01"), cf.dt("1979-12-10")))
        g = g * 1e5
        cfp.levs(0, 12, 1, extend="max")
        cfp.cscale("scale1", below=0, above=13)

        cfp.traj(
            g,
            legend=True,
            linewidth=2,
            colorbar_title="Relative Vorticity (Hz) * 1e5",
        )

    @compare_plot_results
    def test_example_42a(self):
        """Test Example 42a: intensity legend with lines."""
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

    @unittest.expectedFailure  # needs data file adding to datasets
    @compare_plot_results
    def test_example_43(self):
        """Test Example 43: plotting WRF data."""
        f = cf.read(f"{self.data_dir}/wrf2.nc")[0]  # TODO missing dataset

        t2 = f.subspace(time=cf.dt("2016-12-25"))
        t2.units = "degC"

        cfp.con(t2, lines=False)

    # TODO SLB: add rest of examples from current docs, which aren't
    # numbered but should be assigned numbers, here.
    # E.g. the UGRID examples (see:
    # https://ncas-cms.github.io/cf-plot/build/unstructured.html#unstructured)


if __name__ == "__main__":
    print("==================\n" "Regression testing\n" "==================\n")
    cov = coverage.Coverage()
    cov.start()
    unittest.main()

    cov.stop()
    cov.save()

    cov.report()
    print("================\n" "Testing complete\n" "================\n")
