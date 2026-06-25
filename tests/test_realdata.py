import cf
import cfplot as cfp
from pathlib import Path

# Path to test data
DATA_FILE1 = Path(__file__).parent / "data" / "da193_example.nc"


def test_realdata_contour():
    """Test contour plot with real data."""
    flds = cf.read(str(DATA_FILE1))
    f = flds[0]
    cfp.con(f)


def test_realdata_pstereo():
    """Test pstereo plot with real data."""
    flds = cf.read(str(DATA_FILE1))
    f = flds[0]

    # produces striped output, is wrong
    cfp.mapset(proj="npstere")
    cfp.con(f)

    # squeezing the data then plotting also
    # produces striped output, and is wrong
    # but we don't show that here.
    f0 = f.squeeze()

    # this works correctly, though of course there
    # is an unplotted segment of data
    f1 = f0[:,0:399]
    cfp.con(f1)

    # this goes back to the bad stripes, with
    # an appropriate empty segment
    f1 = f0[:,0:403]
    cfp.con(f1)
