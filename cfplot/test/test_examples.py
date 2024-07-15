"""
Regression testing module for cf-plot.

Test standard `levs`, `gvals`, and `lon` and `lat` labelling.
Make all the gallery plots and use Imagemagick to display them
alongside a reference plot.

"""

import coverage
import faulthandler
import numpy as np
from scipy.interpolate import griddata
import unittest

import cfplot as cfp
import cf


faulthandler.enable()  # to debug seg faults and timeouts


DATA_DIR = "../../cfplot_data"


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
        cfp.compare_arrays(
            ref=ref_answer, levs_test=True, min=-35, max=65, step=5
        )

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
        cfp.compare_arrays(
            ref=ref_answer, levs_test=True, min=-6, max=6, step=1.2
        )

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
        cfp.compare_arrays(
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
        cfp.compare_arrays(
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
        cfp.compare_arrays(
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
        cfp.compare_arrays(
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
        cfp.compare_arrays(
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
        cfp.compare_arrays(
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
        cfp.compare_arrays(
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
        cfp.compare_arrays(
            ref=ref_answer, min=-180, max=180, type=1, mapaxis_test=True
        )

    def test_lonlat_2(self):
        """Test 2 for `mapaxis` longitude-latitude labelling."""
        ref_answer = (
            [150, 180, 210, 240, 270],
            ["150E", "180", "150W", "120W", "90W"],
        )
        cfp.compare_arrays(
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
        cfp.compare_arrays(
            ref=ref_answer, min=0, max=90, type=1, mapaxis_test=True
        )

    def test_lonlat_4(self):
        """Test 4 for `mapaxis` longitude-latitude labelling."""
        ref_answer = (
            [-90, -60, -30, 0, 30, 60, 90],
            ["90S", "60S", "30S", "0", "30N", "60N", "90N"],
        )
        cfp.compare_arrays(
            ref=ref_answer, min=-90, max=90, type=2, mapaxis_test=True
        )

    def test_lonlat_5(self):
        """Test 5 for `mapaxis` longitude-latitude labelling."""
        ref_answer = (
            [0, 5, 10, 15, 20, 25, 30],
            ["0", "5N", "10N", "15N", "20N", "25N", "30N"],
        )
        cfp.compare_arrays(
            ref=ref_answer, min=0, max=30, type=2, mapaxis_test=True
        )


class ExamplesTest(unittest.TestCase):
    """Run through gallery examples and compare to reference plots."""
    data_dir = DATA_DIR

    def setup(self):
        """Preparations called immediately before each test method."""
        cfp.reset()
        print(
            "------------------------------\n"
            "Testing gallery example plots.\n"
            "------------------------------\n"
        )

    def test_example_1(self):
        """Test Example 1."""
        cfp.setvars(file="fig1.png")
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.con(f.subspace(time=15))
        cfp.compare_images(1)

    def test_example_2(self):
        """Test Example 2."""
        cfp.setvars(file="fig2.png")
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.con(f.subspace(time=15), blockfill=True, lines=False)
        cfp.compare_images(2)

    def test_example_3(self):
        """Test Example 3."""
        cfp.setvars(file="fig3.png")
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.mapset(lonmin=-15, lonmax=3, latmin=48, latmax=60)
        cfp.levs(min=265, max=285, step=1)

        cfp.con(f.subspace(time=15))
        cfp.compare_images(3)

    def test_example_4(self):
        """Test Example 4."""
        cfp.setvars(file="fig4.png")
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        cfp.mapset(proj="npstere")

        cfp.con(f.subspace(pressure=500))
        cfp.compare_images(4)

    def test_example_5(self):
        """Test Example 5."""
        cfp.setvars(file="fig5.png")
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        cfp.mapset(proj="spstere", boundinglat=-30, lon_0=180)

        cfp.con(f.subspace(pressure=500))
        cfp.compare_images(5)

    def test_example_6(self):
        """Test Example 6."""
        cfp.setvars(file="fig6.png")
        f = cf.read(f"{self.data_dir}/ggap.nc")[3]

        cfp.con(f.subspace(longitude=0))
        cfp.compare_images(6)

    def test_example_7(self):
        """Test Example 7."""
        cfp.setvars(file="fig7.png")
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        cfp.con(f.collapse("mean", "longitude"))
        cfp.compare_images(7)

    def test_example_8(self):
        """Test Example 8."""
        cfp.setvars(file="fig8.png")
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        cfp.con(f.collapse("mean", "longitude"), ylog=1)
        cfp.compare_images(8)

    def test_example_9(self):
        """Test Example 9."""
        cfp.setvars(file="fig9.png")
        f = cf.read(f"{self.data_dir}/ggap.nc")[0]

        cfp.con(f.collapse("mean", "latitude"))
        cfp.compare_images(9)

    def test_example_10(self):
        """Test Example 10."""
        cfp.setvars(file="fig10.png")
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.cscale("plasma")

        cfp.con(f.subspace(longitude=0), lines=0)
        cfp.compare_images(10)

    def test_example_11(self):
        """Test Example 11."""
        cfp.setvars(file="fig11.png")
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.gset(-30, 30, "1960-1-1", "1980-1-1")
        cfp.levs(min=280, max=305, step=1)
        cfp.cscale("plasma")

        cfp.con(f.subspace(longitude=0), lines=0)
        cfp.compare_images(11)

    def test_example_12(self):
        """Test Example 12."""
        cfp.setvars(file="fig12.png")
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        cfp.cscale("plasma")

        cfp.con(f.subspace(latitude=0), lines=0)
        cfp.compare_images(12)

    def test_example_13(self):
        """Test Example 13."""
        cfp.setvars(file="fig13.png")
        f = cf.read(f"{self.data_dir}/ggap.nc")

        u = f[1].subspace(pressure=500)
        v = f[3].subspace(pressure=500)

        cfp.vect(u=u, v=v, key_length=10, scale=100, stride=5)
        cfp.compare_images(13)

    def test_example_14(self):
        """Test Example 14."""
        cfp.setvars(file="fig14.png")
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

        cfp.compare_images(14)

    def test_example_15(self):
        """Test Example 15."""
        cfp.setvars(file="fig15.png")

        u = cf.read(f"{self.data_dir}/ggap.nc")[1]
        v = cf.read(f"{self.data_dir}/ggap.nc")[3]
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
        cfp.compare_images(15)

    def test_example_16(self):
        """Test Example 16."""
        cfp.setvars(file="fig16.png")

        c = cf.read(f"{self.data_dir}/vaAMIPlcd_DJF.nc")[0]
        c = c.subspace(Y=cf.wi(-60, 60))
        c = c.subspace(X=cf.wi(80, 160))
        c = c.collapse("T: mean X: mean")

        g = cf.read(f"{self.data_dir}/wapAMIPlcd_DJF.nc")[0]
        g = g.subspace(Y=cf.wi(-60, 60))
        g = g.subspace(X=cf.wi(80, 160))
        g = g.collapse("T: mean X: mean")

        cfp.vect(
            u=c,
            v=-g,
            key_length=[5, 0.05],
            scale=[20, 0.2],
            title="DJF",
            key_location=[0.95, -0.05],
        )
        cfp.compare_images(16)

    def test_example_17(self):
        """Test Example 17."""
        cfp.setvars(file="fig17.png")
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

        cfp.compare_images(17)

    def test_example_18(self):
        """Test Example 18."""
        cfp.setvars(file="fig18.png")
        f = cf.read(f"{self.data_dir}/tas_A1.nc")[0]

        g = f.subspace(time=15)

        cfp.gopen()
        cfp.cscale("magma")
        cfp.mapset(proj="npstere")
        cfp.con(g)
        cfp.stipple(f=g, min=265, max=295, size=100, color="#00ff00")
        cfp.gclose()

        cfp.compare_images(18)

    def test_example_19(self):
        """Test Example 19."""
        cfp.reset()
        cfp.setvars(file="fig19.png")
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
        cfp.compare_images(19)

    def test_example_20(self):
        """Test Example 20."""
        cfp.setvars(file="fig20.png")
        f = cf.read(f"{self.data_dir}/Geostropic_Adjustment.nc")[0]

        cfp.con(f.subspace[9])
        cfp.compare_images(20)

    def test_example_21(self):
        """Test Example 21."""
        cfp.setvars(file="fig21.png")
        f = cf.read(f"{self.data_dir}/Geostropic_Adjustment.nc")[0]

        cfp.con(
            f.subspace[9],
            title="test data",
            xticks=np.arange(5) * 100000 + 100000,
            yticks=np.arange(7) * 2000 + 2000,
            xlabel="x-axis",
            ylabel="z-axis",
        )
        cfp.compare_images(21)

    def test_example_22(self):
        """Test Example 22."""
        cfp.setvars(file="fig22.png")
        f = cf.read_field(f"{self.data_dir}/rgp.nc")

        cfp.cscale("gray")

        cfp.con(f)
        cfp.compare_images(22)

    def test_example_23(self):
        """Test Example 23."""
        cfp.setvars(file="fig23.png")
        f = cf.read_field(f"{self.data_dir}/rgp.nc")

        data = f.array
        xvec = f.construct("dim1").array
        yvec = f.construct("dim0").array
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

        cfp.compare_images(23)

    def test_example_24(self):
        """Test Example 24."""
        cfp.setvars(file="fig24.png")

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
        temp_new = griddata(
            lons, lats, temp, lons_new, lats_new, interp="linear"
        )

        cfp.cscale("parula")

        cfp.con(x=lons_new, y=lats_new, f=temp_new, ptype=1)
        cfp.compare_images(24)

    def test_example_25(self):
        """Test Example 25."""
        cfp.setvars(file="fig25.png")

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

        cfp.compare_images(25)

    def test_example_26(self):
        """Test Example 26."""
        cfp.setvars(file="fig26.png")
        from matplotlib.mlab import griddata
        from netCDF4 import Dataset as ncfile

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
        temp_new = griddata(
            lons, lats, temp, lons_new, lats_new, interp="linear"
        )

        cfp.con(x=lons_new, y=lats_new, f=temp_new, ptype=1)
        cfp.compare_images(26)

    def test_example_27(self):
        """Test Example 27."""
        cfp.setvars(file="fig27.png")
        f = cf.read(f"{self.data_dir}/ggap.nc")[1]

        g = f.collapse("X: mean")

        cfp.lineplot(
            g.subspace(pressure=100),
            marker="o",
            color="blue",
            title="Zonal mean zonal wind at 100mb",
        )
        cfp.compare_images(27)

    def test_example_28(self):
        """Test Example 28."""
        cfp.setvars(file="fig28.png")
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

        cfp.compare_images(28)

    def test_example_29(self):
        """Test Example 29."""
        cfp.setvars(file="fig29.png")
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
        cfp.compare_images(29)

    def test_example_31(self):
        """Test Example 31."""
        f = cf.read(f"{self.data_dir}/ukcp_rcm_test.nc")[0]

        cfp.mapset(proj="UKCP", resolution="50m")
        cfp.levs(-3, 7, 0.5)
        cfp.setvars(grid_x_spacing=1, grid_y_spacing=1)

        cfp.con(f, lines=False)


if __name__ == "__main__":
    print(
        "==================\n"
        "Regression testing\n"
        "==================\n"
    )
    cov = coverage.Coverage()
    cov.start()
    unittest.main()

    cov.stop()
    cov.save()

    cov.report()
    print(
        "================\n"
        "Testing complete\n"
        "================\n"
    )
