from copy import deepcopy

import numpy as np


def check_well_formed(field):
    """
    Check the coordinates are all of the form X, Y, Z, T.

    returns boolean
    """

    coords = list(field.coords())
    mycoords = deepcopy(coords)

    for i in np.arange(len(coords)):
        c = field.coord(coords[i])
        if c.X:
            mycoords[i] = "X"
        if c.Y:
            mycoords[i] = "Y"
        if c.Z:
            mycoords[i] = "Z"
        if c.T:
            mycoords[i] = "T"

    # Check if the coordtinates are all of the form X, Y, Z, T
    well_formed = True
    dimension_coords = [
        "dimensioncoordinate0",
        "dimensioncoordinate1",
        "dimensioncoordinate2",
        "dimensioncoordinate3",
    ]
    for i in np.arange(4):
        if dimension_coords[i] in mycoords:
            well_formed = False

    return well_formed


def _check_data(field=None, x=None, y=None):
    """
    | Check user input contour data is correct.
    | This is an internal routine and is not used by the user.
    |
    | field=None - field
    | x=None - x points for field
    | y=None - y points for field
    |
    """

    # Input error trapping
    args = True
    if np.size(field) == 1:
        if field is None:
            errstr = (
                "\ncon error - a field for contouring must be "
                "passed with the f= flag\n"
            )
            args = False
    if np.size(x) == 1:
        if x is None:
            x = np.arange(np.shape(field)[1])
    if np.size(y) == 1:
        if y is None:
            y = np.arange(np.shape(field)[0])
    if not args:
        raise Warning(errstr)

    # Check input dimensions look okay.
    # All inputs 2D
    if np.ndim(field) == 2 and np.ndim(x) == 2 and np.ndim(y) == 2:
        xpts = np.shape(field)[1]
        ypts = np.shape(field)[0]
        if xpts != np.shape(x)[1] or xpts != np.shape(y)[1]:
            args = False
        if ypts != np.shape(x)[0] or ypts != np.shape(y)[0]:
            args = False
        if args:
            return

    # Field x and y all 1D
    if np.ndim(field) == 1 and np.ndim(x) == 1 and np.ndim(y) == 1:
        if np.size(x) != np.size(field):
            args = False
        if np.size(y) != np.size(field):
            args = False
        if args:
            return

    # Field 2D, x and y 1D
    if np.ndim(field) != 2:
        args = False
    if np.ndim(x) != 1:
        args = False
    if np.ndim(y) != 1:
        args = False
    if np.ndim(field) == 2:
        if np.size(x) != np.shape(field)[1]:
            args = False
        if np.size(y) != np.shape(field)[0]:
            args = False

    if args is False:
        errstr = (
            "\nInput arguments incorrectly shaped:\n"
            f"x has shape:{np.shape(x)}\n"
            f"y has shape:{np.shape(y)}\n"
            f"field has shape{np.shape(field)}\n\n"
            "Expected x=xpts, y=ypts, field=(ypts,xpts)\n"
            "x=npts, y=npts, field=npts\n"
            "or x=[ypts, xpts], y=[ypts, xpts], field=[ypts, xpts]\n"
        )
        raise Warning(errstr)


def orca_check(x, verbose=False):
    """Check input data to test if it is on an ORCA ocean grid.

    We look for a single discontinuity in longitude where the data changes by
    greater that 120 degrees.
    """

    lons = deepcopy(x)

    # Only check for longitude range > 350 degrees
    if np.max(lons) - np.min(lons) < 350:
        return False

    nvpts = np.shape(lons)[0]

    lons_lower = lons[int(nvpts / 4), :]
    discont_lower_idx = np.where(abs(np.diff(lons_lower)) > 120)

    lons_mid = lons[int(nvpts / 2), :]
    discont_mid_idx = np.where(abs(np.diff(lons_mid)) > 120)

    lons_upper = lons[int(nvpts * 3 / 4), :]
    discont_upper_idx = np.where(abs(np.diff(lons_upper)) > 120)

    # Check for one discontinuity
    retval = False
    if (
        np.size(discont_lower_idx) == 1
        and np.size(discont_mid_idx) == 1
        and np.size(discont_upper_idx) == 1
    ):
        if verbose:
            print("orca_check - one discontinutity")
            print(discont_lower_idx, discont_mid_idx, discont_upper_idx)
        v1 = float(discont_lower_idx[0])
        v2 = float(discont_mid_idx[0])
        v3 = float(discont_upper_idx[0])

        spread = np.max(np.abs(np.diff([v1, v2, v3])))

        if verbose:
            print(
                f"orca_check spread is {np.max(np.abs(np.diff([v1, v2, v3])))}"
            )

        # Check for discontinuity spead of less than 20 places
        if spread <= 20:
            retval = True

    return retval
