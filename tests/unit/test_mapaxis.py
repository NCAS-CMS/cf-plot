"""Unit tests for map axis labelling functions.

Migrated from cfplot/test/test_examples.py::LonLatTest
"""

import numpy as np
import pytest

import cfplot as cfp


class TestMapaxisLongitude:
    """Tests for cfp._mapaxis() longitude labelling (type=1)."""

    def test_mapaxis_lon_full_range(self):
        """Test longitude labelling for full -180 to 180."""
        expected_ticks = [-180, -120, -60, 0, 60, 120, 180]
        expected_labels = ["180", "120W", "60W", "0", "60E", "120E", "180"]

        ticks, labels = cfp._mapaxis(min=-180, max=180, type=1)

        assert np.allclose(ticks, expected_ticks, atol=1e-6)
        assert labels == expected_labels

    def test_mapaxis_lon_eastern_hemisphere(self):
        """Test longitude labelling for eastern 135-280."""
        expected_ticks = [150, 180, 210, 240, 270]
        expected_labels = ["150E", "180", "150W", "120W", "90W"]

        ticks, labels = cfp._mapaxis(min=135, max=280, type=1)

        assert np.allclose(ticks, expected_ticks, atol=1e-6)
        assert labels == expected_labels

    def test_mapaxis_lon_positive(self):
        """Test longitude labelling for positive eastern hemisphere."""
        expected_ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        expected_labels = ["0", "10E", "20E", "30E", "40E", "50E", "60E", "70E", "80E", "90E"]

        ticks, labels = cfp._mapaxis(min=0, max=90, type=1)

        assert np.allclose(ticks, expected_ticks, atol=1e-6)
        assert labels == expected_labels


class TestMapaxisLatitude:
    """Tests for cfp._mapaxis() latitude labelling (type=2)."""

    def test_mapaxis_lat_full_range(self):
        """Test latitude labelling for full -90 to 90."""
        expected_ticks = [-90, -60, -30, 0, 30, 60, 90]
        expected_labels = ["90S", "60S", "30S", "0", "30N", "60N", "90N"]

        ticks, labels = cfp._mapaxis(min=-90, max=90, type=2)

        assert np.allclose(ticks, expected_ticks, atol=1e-6)
        assert labels == expected_labels

    def test_mapaxis_lat_northern_hemisphere(self):
        """Test latitude labelling for northern hemisphere 0-30."""
        expected_ticks = [0, 5, 10, 15, 20, 25, 30]
        expected_labels = ["0", "5N", "10N", "15N", "20N", "25N", "30N"]

        ticks, labels = cfp._mapaxis(min=0, max=30, type=2)

        assert np.allclose(ticks, expected_ticks, atol=1e-6)
        assert labels == expected_labels
