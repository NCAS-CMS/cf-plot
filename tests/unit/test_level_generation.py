"""Unit tests for contour level generation functions.

Migrated from cfplot/test/test_examples.py::BasicArrayTest and GvalsArrayTest
"""

import numpy as np
import pytest

import cfplot as cfp


class TestLevsFunction:
    """Tests for cfp.levs() contour level generation."""

    def test_levs_basic_positive(self):
        """Test levs with basic positive range."""
        expected = np.array(
            [
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
        )

        cfp.levs(min=-35, max=65, step=5)
        generated = cfp.plotvars.levels

        assert np.size(expected) == np.size(generated)
        assert np.allclose(expected, generated, atol=1e-6)

    def test_levs_decimal_step(self):
        """Test levs with decimal step size."""
        expected = np.array(
            [-6.0, -4.8, -3.6, -2.4, -1.2, 0.0, 1.2, 2.4, 3.6, 4.8, 6.0]
        )

        cfp.levs(min=-6, max=6, step=1.2)
        generated = cfp.plotvars.levels

        assert np.size(expected) == np.size(generated)
        assert np.allclose(expected, generated, atol=1e-6)

    def test_levs_large_values(self):
        """Test levs with large pressure values."""
        expected = np.array(
            [50000, 51000, 52000, 53000, 54000, 55000, 56000, 57000, 58000, 59000, 60000]
        )

        cfp.levs(min=50000, max=60000, step=1000)
        generated = cfp.plotvars.levels

        assert np.size(expected) == np.size(generated)
        assert np.allclose(expected, generated, atol=1e-6)

    def test_levs_negative_range(self):
        """Test levs with negative range."""
        expected = np.array(
            [-7000, -6500, -6000, -5500, -5000, -4500, -4000, -3500, -3000, -2500, -2000, -1500, -1000, -500]
        )

        cfp.levs(min=-7000, max=-300, step=500)
        generated = cfp.plotvars.levels

        assert np.size(expected) == np.size(generated)
        assert np.allclose(expected, generated, atol=1e-6)


class TestGvalsFunction:
    """Tests for cfp._gvals() automatic contour level generation."""

    def test_gvals_temperature_range(self):
        """Test _gvals with temperature-like range."""
        expected = np.array([281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293])
        expected_mult = 0

        vals, mult = cfp._gvals(dmin=280.50619506835938, dmax=293.48431396484375)

        assert np.size(expected) == np.size(vals)
        assert np.allclose(expected, vals, atol=1e-6)
        assert mult == expected_mult

    def test_gvals_decimal_range(self):
        """Test _gvals with small decimal range."""
        expected = np.array([0.36, 0.38, 0.4, 0.42, 0.44, 0.46, 0.48, 0.5, 0.52, 0.54, 0.56, 0.58, 0.6, 0.62, 0.64, 0.66])
        expected_mult = 0

        vals, mult = cfp._gvals(dmin=0.356, dmax=0.675)

        assert np.size(expected) == np.size(vals)
        assert np.allclose(expected, vals, atol=1e-6)
        assert mult == expected_mult

    def test_gvals_symmetric_range(self):
        """Test _gvals with symmetric around zero."""
        expected = np.array(
            [-45, -40, -35, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        )
        expected_mult = 0

        vals, mult = cfp._gvals(dmin=-49.510975, dmax=53.206604)

        assert np.size(expected) == np.size(vals)
        assert np.allclose(expected, vals, atol=1e-6)
        assert mult == expected_mult

    def test_gvals_pressure_range(self):
        """Test _gvals with large pressure range."""
        expected = np.array(
            [47000, 48000, 49000, 50000, 51000, 52000, 53000, 54000, 55000, 56000, 57000, 58000, 59000, 60000, 61000, 62000, 63000, 64000]
        )
        expected_mult = 0

        vals, mult = cfp._gvals(dmin=46956, dmax=64538)

        assert np.size(expected) == np.size(vals)
        assert np.allclose(expected, vals, atol=1e-6)
        assert mult == expected_mult

    def test_gvals_small_decimal(self):
        """Test _gvals with small decimal range."""
        expected = np.array([-1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1])
        expected_mult = 0

        vals, mult = cfp._gvals(dmin=-1.0, dmax=0.1)

        assert np.size(expected) == np.size(vals)
        assert np.allclose(expected, vals, atol=1e-6)
        assert mult == expected_mult
