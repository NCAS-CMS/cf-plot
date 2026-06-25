"""Integration tests for contour plotting with reference data."""

from pathlib import Path

import cf
import matplotlib.pyplot as plt
import pytest
from netCDF4 import Dataset as ncfile
import cfplot as cfp


# Path to test data
DATA_DIR = Path(__file__).parent.parent.parent / "docs" / "source" / "example-datasets"
REF_IMAGE_DIR = Path(__file__).parent.parent / "reference-example-images"


@pytest.fixture(autouse=True)
def setup_cfplot():
    """Reset cfplot and close figures around each integration test."""
    plt.close("all")
    cfp.reset()
    yield
    cfp.reset()
    plt.close("all")


@pytest.mark.integration
def test_contour_basic_tas():
    """Test basic contour plot with temperature data."""
    if not (DATA_DIR / "tas_A1.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'tas_A1.nc'}")
    
    flds = cf.read(str(DATA_DIR / "tas_A1.nc"))
    f = flds[0]
    
    # Match the known-good example slice for this dataset.
    f_2d = f.subspace(time=15)
    
    # This should not raise
    cfp.con(f_2d)


@pytest.mark.integration
def test_contour_ggap_data():
    """Test contour plot with GGAP dataset."""
    if not (DATA_DIR / "ggap.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'ggap.nc'}")
    
    flds = cf.read(str(DATA_DIR / "ggap.nc"))
    
    # The first two GGAP fields are pressure-level data; take a 2D slice.
    for idx in [0, 1]:
        if idx < len(flds):
            f = flds[idx]
            f_2d = f.subspace(pressure=500) if f.has_construct("Z") else f
            cfp.con(f_2d)


@pytest.mark.integration
def test_orca_direct():

    if not (DATA_DIR / "orca2.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'orca2.nc'}")

    # Use native 2D arrays to exercise map contouring from numpy inputs.
    with ncfile(str(DATA_DIR / "orca2.nc")) as nc:
        lons = nc.variables["longitude"][:]
        lats = nc.variables["latitude"][:]
        temp = nc.variables["sst"][:]

    cfp.con(x=lons, y=lats, f=temp, ptype=1)


@pytest.mark.integration
def test_contour_orca_grid():
    """Test contour plot with ORCA grid (irregular/tripolar)."""
    if not (DATA_DIR / "orca2.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'orca2.nc'}")
    
    flds = cf.read(str(DATA_DIR / "orca2.nc"))
    lons = flds.select_by_identity("ncvar%longitude")[0]
    lats = flds.select_by_identity("ncvar%latitude")[0]
    temp = flds.select_by_identity("ncvar%sst")[0]

    cfp.con(x=lons, y=lats, f=temp, ptype=1)


@pytest.mark.integration
def test_contour_orca_cf_metadata_only():
    """Test ORCA contouring directly from CF metadata (no explicit lon/lat)."""
    if not (DATA_DIR / "orca2.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'orca2.nc'}")

    flds = cf.read(str(DATA_DIR / "orca2.nc"))
    temp = flds.select_by_identity("ncvar%sst")[0].copy()
    lons = flds.select_by_identity("ncvar%longitude")[0]
    lats = flds.select_by_identity("ncvar%latitude")[0]

    # This dataset stores lon/lat as separate fields rather than attached
    # coordinates on sst. Attach them as auxiliary coordinates for CF plotting.
    axes = temp.get_data_axes()
    lon_coord = cf.AuxiliaryCoordinate(
        properties={"standard_name": "longitude", "units": "degrees_east"},
        data=lons.array,
    )
    lat_coord = cf.AuxiliaryCoordinate(
        properties={"standard_name": "latitude", "units": "degrees_north"},
        data=lats.array,
    )
    temp.set_construct(lon_coord, axes=axes)
    temp.set_construct(lat_coord, axes=axes)

    # Plot using the CF field only; metadata is now attached to temp.
    cfp.con(temp)


@pytest.mark.integration
def test_contour_rotated_pole():
    """Test contour plot with rotated pole grid."""
    if not (DATA_DIR / "rgp.nc").exists():
        pytest.skip(f"Missing test data: {DATA_DIR / 'rgp.nc'}")
    
    f = cf.read(str(DATA_DIR / "rgp.nc"))[0]
    cfp.con(f)