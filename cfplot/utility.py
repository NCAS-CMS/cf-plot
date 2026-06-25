"""Utility functions for plotting.

Pure utility functions with no global state dependencies.
These are designed to be used by any plotting module.
"""

from __future__ import annotations

import os
from copy import deepcopy
from typing import Any

import cartopy.util as cartopy_util
import numpy as np


def to_float_or_none(value: Any) -> float | None:
    """Convert numeric-like metadata values to float, else return None."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def resolve_colour_scale_file(scale: str) -> str:
    """Resolve a named colour scale or explicit file path."""
    package_path = os.path.dirname(__file__)
    file_path = os.path.join(package_path, "colour", "colourmaps", f"{scale}.rgb")
    if os.path.isfile(file_path):
        return file_path
    if os.path.isfile(scale):
        return scale

    errstr = (
        "\ncscale error - colour scale not found:\n"
        f"File {file_path} not found\n"
        f"Scale {scale} not found\n"
    )
    raise Warning(errstr)


def load_colour_scale_rgb(scale: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load RGB channels for a colour scale."""
    with open(resolve_colour_scale_file(scale), "r", encoding="ascii") as handle:
        lines = handle.read().splitlines()

    red: list[int] = []
    green: list[int] = []
    blue: list[int] = []
    for line in lines:
        vals = line.split()
        red.append(int(vals[0]))
        green.append(int(vals[1]))
        blue.append(int(vals[2]))

    return (
        np.asarray(red, dtype=float),
        np.asarray(green, dtype=float),
        np.asarray(blue, dtype=float),
    )


def interpolate_colour_channels(
    red: np.ndarray,
    green: np.ndarray,
    blue: np.ndarray,
    positions: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Interpolate RGB channels to the requested positions."""
    xpts = np.arange(np.size(red), dtype=float)
    return (
        np.interp(positions, xpts, red),
        np.interp(positions, xpts, green),
        np.interp(positions, xpts, blue),
    )


def ndecs(data: np.ndarray | list) -> int:
    """Find the maximum number of decimal places in an array.
    
    Data with more decimal places will determine the result.
    Used to format colorbar and line labels consistently.
    
    Parameters
    ----------
    data : array-like
        Input array of numeric values
        
    Returns
    -------
    int
        Maximum number of decimal places found
    """
    maxdecs = 0
    for value in data:
        parts = str(value).split(".")
        if len(parts) == 2:
            number_decs = len(parts[1])
            if number_decs > maxdecs:
                maxdecs = number_decs
    return maxdecs


def gvals(
    dmin: float | None = None,
    dmax: float | None = None,
    mystep: float | None = None,
    mod: bool = True,
) -> tuple[np.ndarray, int]:
    """Generate sensible tick values between two limits.
    
    Works out appropriate step size and generates values,
    optionally scaling with a power-of-10 multiplier.
    Used for contour levels and axis labelling.
    
    Parameters
    ----------
    dmin : float
        Minimum value
    dmax : float
        Maximum value
    mystep : float, optional
        Use this step instead of auto-calculating
    mod : bool
        If True, apply multiplier for small/large ranges
        
    Returns
    -------
    vals : ndarray
        Array of tick values
    mult : int
        Multiplier exponent (10^mult) applied to values
    """
    # Copies of inputs as these might be changed
    dmin1 = deepcopy(dmin)
    dmax1 = deepcopy(dmax)

    # Swap if dmin1 > dmax1
    if dmax1 < dmin1:
        dmin1, dmax1 = dmax1, dmin1

    # Data range
    data_range = dmax1 - dmin1

    # field multiplier
    mult = 0
    vals = None

    # Return some values if dmin1 = dmax1
    if dmin1 == dmax1:
        vals = np.array([dmin1 - 1, dmin1, dmin1 + 1])
        mult = 0
        return vals, mult

    # Modify if requested or if out of range 0.001 to 2000000
    if data_range < 0.001:
        while dmax1 <= 3:
            dmin1 = dmin1 * 10.0
            dmax1 = dmax1 * 10.0
            data_range = dmax1 - dmin1
            mult = mult - 1

    if data_range > 2000000:
        while dmax1 > 10:
            dmin1 = dmin1 / 10.0
            dmax1 = dmax1 / 10.0
            data_range = dmax1 - dmin1
            mult = mult + 1

    if data_range >= 0.001 and data_range <= 2000000:
        # Calculate an appropriate step
        step = None
        test_steps = [
            0.0001,
            0.0002,
            0.0005,
            0.001,
            0.002,
            0.005,
            0.01,
            0.02,
            0.05,
            0.1,
            0.2,
            0.5,
            1,
            2,
            5,
            10,
            20,
            50,
            100,
            200,
            500,
            1000,
            2000,
            5000,
            10000,
            20000,
            50000,
            100000,
        ]

        if mystep is not None:
            step = mystep
        else:
            for val in test_steps:
                nvals = data_range / val

                if val < 1:
                    if nvals > 8:
                        step = val
                else:
                    if nvals > 11:
                        step = val

        # Return an error if no step found
        if step is None:
            errstr = "\n\n cfp.gvals - no valid step values found \n\n"
            errstr += "cfp.gvals(" + str(dmin1) + "," + str(dmax1) + ")\n\n"
            raise ValueError(errstr)

        # values  < 0.0
        vals = None
        vals1 = None
        if dmin1 < 0.0:
            vals1 = (np.arange(-dmin1 / step) * -step)[::-1] - step

        # values  >= 0.0
        vals2 = None
        if dmax1 >= 0.0:
            vals2 = np.arange(dmax1 / step + 1) * step

        if vals1 is not None and vals2 is None:
            vals = vals1
        if vals2 is not None and vals1 is None:
            vals = vals2
        if vals1 is not None and vals2 is not None:
            vals = np.concatenate((vals1, vals2))

        # Round off decimal numbers
        if step < 1:
            vals = vals.round(6)

        # Change values to integers for values >= 1
        if step >= 1:
            vals = vals.astype(int)

        pts = np.where(np.logical_and(vals >= dmin1, vals <= dmax1))
        if np.min(pts) > -1:
            vals = vals[pts]

        if mod is False:
            vals = vals * 10**mult
            mult = 0

    # Catch if no values have been defined
    if vals is None:
        vals = np.array([dmin, dmax])

    return (vals, mult)


def mapaxis(
    min_val: float | None = None,
    max_val: float | None = None,
    axis_type: int | None = None,
    degsym: bool = True,
) -> tuple[list, list]:
    """Generate longitude or latitude axis ticks and labels.
    
    Works out sensible tick marks and labels for geographic axes.
    
    Parameters
    ----------
    min_val : float
        Minimum axis value
    max_val : float
        Maximum axis value
    axis_type : int
        1 = longitude, 2 = latitude
    degsym : bool
        If True, use degree symbol in labels
        
    Returns
    -------
    ticks : list
        Tick positions
    labels : list
        Tick labels
    """
    degsym_str = r"$\degree$" if degsym else ""

    if axis_type == 1:
        # Longitude
        lonmin = min_val
        lonmax = max_val
        lonrange = lonmax - lonmin
        lonstep = 60
        if lonrange <= 180:
            lonstep = 30
        if lonrange <= 90:
            lonstep = 10
        if lonrange <= 30:
            lonstep = 5
        if lonrange <= 10:
            lonstep = 2
        if lonrange <= 5:
            lonstep = 1

        lons = np.arange(-720, 720 + lonstep, lonstep)
        lonticks = []
        for lon in lons:
            if lon >= lonmin and lon <= lonmax:
                lonticks.append(lon)

        lonlabels = []
        for lon in lonticks:
            lon2 = np.mod(lon + 180, 360) - 180
            if lon2 < 0 and lon2 > -180:
                if lon != 180:
                    lonlabels.append(str(abs(int(lon2))) + degsym_str + "W")
            if lon2 > 0 and lon2 <= 180:
                lonlabels.append(str(int(lon2)) + degsym_str + "E")
            if lon2 == 0:
                lonlabels.append("0" + degsym_str)
            if lon == 180 or lon == -180:
                lonlabels.append("180" + degsym_str)

        return (lonticks, lonlabels)

    if axis_type == 2:
        # Latitude
        latmin = min_val
        latmax = max_val
        latrange = latmax - latmin
        latstep = 30
        if latrange <= 90:
            latstep = 10
        if latrange <= 30:
            latstep = 5
        if latrange <= 10:
            latstep = 2
        if latrange <= 5:
            latstep = 1

        lats = np.arange(-90, 90 + latstep, latstep)
        latticks = []
        for lat in lats:
            if lat >= latmin and lat <= latmax:
                latticks.append(lat)

        latlabels = []
        for lat in latticks:
            if lat < 0:
                latlabels.append(str(abs(int(lat))) + degsym_str + "S")
            if lat > 0:
                latlabels.append(str(int(lat)) + degsym_str + "N")
            if lat == 0:
                latlabels.append("0" + degsym_str)

        return (latticks, latlabels)

    return ([], [])


def fix_floats(data: list) -> list:
    """Fix numpy rounding issues where e.g. 0.4 becomes 0.3999999999.

    Returns data unchanged if any values contain an exponent ('e').
    """
    has_e = any("e" in str(val) for val in data)
    if has_e:
        return data

    data_ndecs = np.zeros(len(data))
    for i in np.arange(len(data)):
        data_ndecs[i] = len(str(float(data[i])).split(".")[1])

    if max(data_ndecs) >= 10:
        if min(data_ndecs) < 10:
            pts = np.where(data_ndecs >= 10)
            data_ndecs[pts] = 0
            ndecs_max = int(max(data_ndecs))
            for i in np.arange(len(data)):
                data[i] = round(data[i], ndecs_max)
        else:
            nd = 2
            data_range = 0.0
            data_temp = data
            while data_range == 0.0:
                data_temp = deepcopy(data)
                for i in np.arange(len(data_temp)):
                    data_temp[i] = round(data_temp[i], nd)
                data_range = np.max(data_temp) - np.min(data_temp)
                nd = nd + 1
            data = data_temp

    return data


def calculate_levels(
    field: np.ndarray,
    level_spacing: str = "linear",
    levels_step: Any | None = None,
    verbose: bool | None = None,
) -> tuple[np.ndarray, int, float]:
    """Calculate contour levels automatically from field data.

    Parameters
    ----------
    field : ndarray
        The data field to generate levels for.
    level_spacing : str
        One of 'linear', 'outlier', 'inspect', 'log', 'loglike'.
    levels_step : scalar or None
        If given, generate levels with this step size instead of auto.
    verbose : bool or None
        If True, print diagnostic messages.

    Returns
    -------
    clevs : ndarray
        Array of contour levels.
    mult : int
        Multiplier exponent applied (10 ** mult).
    fmult : float
        Inverse multiplier (10 ** -mult).
    """
    dmin = np.nanmin(field)
    dmax = np.nanmax(field)

    tight = True
    field2 = deepcopy(field)
    mult = 0
    fmult = 1.0
    clevs: Any = []

    if levels_step is None:
        if verbose:
            print("calculate_levels - generating automatic contour levels")

        if level_spacing in ("outlier", "inspect"):
            hist = np.histogram(field, 100)[0]
            pts_arr = np.size(field)
            rate = 0.01

            if sum(hist[1:-2]) == 0:
                if hist[0] / hist[-1] < rate:
                    pts = np.where(field == dmin)
                    field2[pts] = dmax
                    dmin = np.nanmin(field2)
                if hist[-1] / hist[0] < rate:
                    pts = np.where(field == dmax)
                    field2[pts] = dmin
                    dmax = np.nanmax(field2)

            clevs, mult = gvals(dmin=dmin, dmax=dmax)
            fmult = 10**-mult
            tight = False

        if level_spacing == "linear":
            if isinstance(np.ma.min(dmin), np.ma.core.MaskedConstant) or isinstance(
                np.ma.min(dmax), np.ma.core.MaskedConstant
            ):
                if verbose:
                    print(
                        "calculate_levels warning - data is entirely masked; "
                        "setting levels to 0 and 0.1"
                    )
                dmin = 0.0
                dmax = 0.1

            clevs, mult = gvals(dmin=dmin, dmax=dmax)
            fmult = 10**-mult
            tight = False

        if level_spacing in ("log", "loglike"):
            if dmin < 0.0 and dmax < 0.0:
                dmin1 = abs(dmax)
                dmax1 = abs(dmin)
            elif dmin > 0.0 and dmax > 0.0:
                dmin1 = abs(dmin)
                dmax1 = abs(dmax)
            else:
                dmax1 = max(abs(dmin), dmax)
                pts_neg = np.where(field < 0.0)
                close_below = np.max(field[pts_neg])
                pts_pos = np.where(field > 0.0)
                close_above = np.min(field[pts_pos])
                dmin1 = min(abs(close_below), close_above)

            if level_spacing == "log":
                clevs = []
                for i in np.arange(31):
                    val = 10 ** (i - 30.0)
                    clevs.append("{:.0e}".format(val))
            else:
                clevs = []
                for i in np.arange(61):
                    val = 10 ** (i - 30.0)
                    clevs.append("{:.0e}".format(val))
                    clevs.append("{:.0e}".format(val * 2))
                    clevs.append("{:.0e}".format(val * 5))

            clevs = np.float64(clevs)
            pts = np.where(np.logical_and(clevs >= abs(dmin1), clevs <= abs(dmax1)))
            clevs = clevs[pts]

            if dmin < 0.0 and dmax < 0.0:
                clevs = -1.0 * clevs[::-1]
            if dmin <= 0.0 and dmax >= 0.0:
                clevs = np.concatenate([-1.0 * clevs[::-1], [0.0], clevs])

    else:
        if verbose:
            print("calculate_levels - using specified step to generate contour levels")

        step = levels_step
        if isinstance(step, int):
            dmin = int(dmin)
            dmax = int(dmax)

        clevs_list = []
        if dmin < 0:
            clevs_list = list((np.arange(-1 * dmin / step + 1) * -step)[::-1])
        if dmax > 0:
            pos = list(np.arange(dmax / step + 1) * step)
            if len(clevs_list) > 0:
                clevs_list = list(clevs_list[:-1]) + pos
            else:
                clevs_list = pos
        clevs = np.array(clevs_list)
        if isinstance(step, int):
            clevs = clevs.astype(int)

    # Remove out-of-range values if tight mode
    if tight:
        pts = np.where(np.logical_and(clevs >= dmin, clevs <= dmax))
        clevs = clevs[pts]

    # Ensure at least two levels
    clevs = list(clevs)
    if len(clevs) < 2:
        clevs.append(clevs[0] + 0.001 if clevs else 0.001)

    # Fix floating-point rounding noise
    if isinstance(clevs[0], float):
        clevs = fix_floats(clevs)

    return (np.asarray(clevs), mult, fmult)


def timeaxis(
    dtimes: Any,
    user_gset: int = 0,
    xmin: Any = None,
    xmax: Any = None,
    ymin: Any = None,
    ymax: Any = None,
    tspace_year: int | None = None,
    tspace_hour: int | None = None,
    tspace_day: int | None = None,
) -> tuple[list, list, str]:
    """Calculate time axis ticks and labels for a CF time coordinate.

    Parameters
    ----------
    dtimes : cf time coordinate
        The time dimension of the CF field.
    user_gset : int
        Non-zero if the user has set axis limits via gset.
    xmin, xmax, ymin, ymax : scalar or str or None
        User-specified axis limits (possibly date strings).
    tspace_year, tspace_hour, tspace_day : int or None
        Override auto-calculated spacing for year/hour/day axes.

    Returns
    -------
    time_ticks : list
    time_labels : list
    axis_label : str
    """
    import cf as _cf

    time_units = dtimes.Units
    time_ticks: list = []
    time_labels: list = []
    axis_label = "Time"

    yearmin = min(dtimes.year.array)
    yearmax = max(dtimes.year.array)
    tmin = min(dtimes.dtarray)
    tmax = max(dtimes.dtarray)
    calendar = getattr(dtimes, "calendar", "standard")

    if user_gset != 0:
        if isinstance(xmin, str):
            t = _cf.Data(_cf.dt(xmin), units=time_units, calendar=calendar)
            yearmin = int(t.year)
            t = _cf.Data(_cf.dt(xmax), units=time_units, calendar=calendar)
            yearmax = int(t.year)
            tmin = _cf.dt(xmin, calendar=calendar)
            tmax = _cf.dt(xmax, calendar=calendar)
        if isinstance(ymin, str):
            t = _cf.Data(_cf.dt(ymin), units=time_units, calendar=calendar)
            yearmin = int(t.year)
            t = _cf.Data(_cf.dt(ymax), units=time_units, calendar=calendar)
            yearmax = int(t.year)
            tmin = _cf.dt(ymin, calendar=calendar)
            tmax = _cf.dt(ymax, calendar=calendar)

    # Years
    span = yearmax - yearmin
    if span > 4 and span < 3000:
        axis_label = "Time (year)"
        if span <= 15:
            step = 1
        elif span <= 30:
            step = 2
        elif span <= 60:
            step = 5
        elif span <= 160:
            step = 10
        elif span <= 300:
            step = 20
        elif span <= 600:
            step = 50
        elif span <= 1300:
            step = 100
        else:
            step = 200

        if tspace_year is not None:
            step = tspace_year

        years = np.arange(yearmax / step + 2) * step
        tvals = years[np.where((years >= yearmin) & (years <= yearmax))]

        if np.size(tvals) < 2:
            tvals = gvals(dmin=yearmin, dmax=yearmax)[0]

        for year in tvals:
            time_ticks.append(
                np.min(
                    _cf.Data(
                        _cf.dt(f"{int(year)}-01-01 00:00:00"),
                        units=time_units,
                        calendar=calendar,
                    ).array
                )
            )
            time_labels.append(str(int(year)))

    # Months
    if yearmax - yearmin <= 4:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        tsteps = 0
        for year in np.arange(yearmax - yearmin + 1) + yearmin:
            for month in np.arange(12):
                mytime = _cf.dt(f"{year}-{month + 1}-01 00:00:00", calendar=calendar)
                if mytime >= tmin and mytime <= tmax:
                    tsteps += 1

        mvals = np.arange(12) if tsteps < 17 else np.arange(4) * 3

        for year in np.arange(yearmax - yearmin + 1) + yearmin:
            for month in mvals:
                mytime = _cf.dt(f"{year}-{month + 1}-01 00:00:00", calendar=calendar)
                if mytime >= tmin and mytime <= tmax:
                    time_ticks.append(
                        np.min(
                            _cf.Data(mytime, units=time_units, calendar=calendar).array
                        )
                    )
                    time_labels.append(str(months[month]) + " " + str(int(year)))

    # Days and hours
    if np.size(time_ticks) <= 2:
        myday = _cf.dt(int(tmin.year), int(tmin.month), int(tmin.day), calendar=calendar)
        not_found = 0
        hour_counter = 0
        span = 0
        while not_found <= 48:
            mydate = _cf.Data(myday, dtimes.Units) + _cf.Data(hour_counter, "hour")
            if mydate >= tmin and mydate <= tmax:
                span += 1
            else:
                not_found += 1
            hour_counter += 1

        step = 1
        if span > 13:
            step = 1
        if span > 13:
            step = 4
        if span > 25:
            step = 6
        if span > 100:
            step = 12
        if span > 200:
            step = 24
        if span > 400:
            step = 48
        if span > 800:
            step = 96
        if tspace_hour is not None:
            step = tspace_hour
        if tspace_day is not None:
            step = tspace_day * 24

        not_found = 0
        hour_counter = 0
        axis_label = "Time (hour)"
        if span >= 24:
            axis_label = "Time"
        time_ticks = []
        time_labels = []

        while not_found <= 48:
            mytime = _cf.Data(myday, dtimes.Units) + _cf.Data(hour_counter, "hour")
            if mytime >= tmin and mytime <= tmax:
                time_ticks.append(np.min(mytime.array))
                label = f"{mytime.year}-{mytime.month}-{mytime.day}"
                if hour_counter / 24 != int(hour_counter / 24):
                    label += f" {mytime.hour}:00:00"
                time_labels.append(label)
            else:
                not_found += 1
            hour_counter += step

    return (time_ticks, time_labels, axis_label)


def _pressure_axis_ticks(ymin: float, ymax: float, ylog: bool) -> list[float] | np.ndarray:
    """Generate pressure-like Y ticks used by ptypes 2 and 3."""
    if ylog:
        ylo = min(ymin, ymax)
        yhi = max(ymin, ymax)
        return [tick for tick in (1000, 100, 10, 1) if ylo <= tick <= yhi]

    ystep = 100.0
    yrange = abs(ymax - ymin)
    if yrange < 1:
        ystep = yrange / 10.0 if yrange != 0 else 0.1
    if yrange > 1:
        ystep = 1.0
    if yrange > 10:
        ystep = 10.0
    if yrange > 100:
        ystep = 100.0
    if yrange > 1000:
        ystep = 200.0
    if yrange > 2000:
        ystep = 500.0
    if yrange > 5000:
        ystep = 1000.0
    if yrange > 15000:
        ystep = 5000.0

    return gvals(
        dmin=min(ymin, ymax),
        dmax=max(ymin, ymax),
        mystep=ystep,
        mod=False,
    )[0]


def compute_xy_ticks(
    *,
    ptype: int,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    ylog: bool,
    degsym: bool,
    xticks: Any,
    yticks: Any,
    xticklabels: Any,
    yticklabels: Any,
    default_xlabel: str,
    default_ylabel: str,
    time_ticks: list | None = None,
    time_labels: list | None = None,
    time_label: str | None = None,
) -> tuple[Any, Any, Any, Any, str, str]:
    """Compute non-map axis ticks/labels for refactored contour rendering.

    Handles ptypes 2-5 plus generic Cartesian fallback used by ptypes 0/7.
    """
    if ptype in (4, 5) and time_ticks is not None and time_labels is not None:
        if ptype == 4:
            lonlat_ticks, lonlat_labels = mapaxis(
                min_val=xmin, max_val=xmax, axis_type=1, degsym=degsym
            )
            default_xlabel = default_xlabel or "Longitude"
        else:
            lonlat_ticks, lonlat_labels = mapaxis(
                min_val=xmin, max_val=xmax, axis_type=2, degsym=degsym
            )
            default_xlabel = default_xlabel or "Latitude"

        default_ylabel = time_label or default_ylabel or "time"

        if xticks is None:
            xticks = lonlat_ticks
            xticklabels = lonlat_labels
        if yticks is None:
            yticks = time_ticks
            yticklabels = time_labels

        return xticks, yticks, xticklabels, yticklabels, default_xlabel, default_ylabel

    if ptype == 2:
        if xticks is None:
            xticks, xticklabels = mapaxis(
                min_val=xmin,
                max_val=xmax,
                axis_type=2,
                degsym=degsym,
            )
        if yticks is None:
            yticks = _pressure_axis_ticks(ymin=ymin, ymax=ymax, ylog=ylog)
    elif ptype == 3:
        if xticks is None:
            xticks, xticklabels = mapaxis(
                min_val=xmin,
                max_val=xmax,
                axis_type=1,
                degsym=degsym,
            )
        if yticks is None:
            yticks = _pressure_axis_ticks(ymin=ymin, ymax=ymax, ylog=ylog)
    else:
        if xticks is None:
            xticks = gvals(dmin=xmin, dmax=xmax, mod=False)[0]
        if yticks is None:
            yticks = gvals(dmin=ymax, dmax=ymin, mod=False)[0]

    return xticks, yticks, xticklabels, yticklabels, default_xlabel, default_ylabel


# ---------------------------------------------------------------------------
# CF field extraction helpers
# ---------------------------------------------------------------------------

def _supscr(text: str) -> str:
    """Format superscript notation for units strings (``**`` and ``^``)."""
    tform = ""
    sup = 0
    for i in text:
        if i == "^":
            sup = 2
        if i == "*":
            sup = sup + 1
        if sup == 0:
            tform = tform + i
        if sup == 1:
            if i not in "*":
                tform = tform + "*" + i
                sup = 0
        if sup == 3:
            if i in "-0123456789":
                tform = tform + i
            else:
                tform = tform + "}$" + i
                sup = 0
        if sup == 2:
            tform = tform + "$^{"
            sup = 3
    if sup == 3:
        tform = tform + "}$"

    tform = tform.replace("m2", "m$^{2}$")
    tform = tform.replace("m3", "m$^{3}$")
    tform = tform.replace("m-2", "m$^{-2}$")
    tform = tform.replace("m-3", "m$^{-3}$")
    tform = tform.replace("s-1", "s$^{-1}$")
    tform = tform.replace("s-2", "s$^{-2}$")
    return tform


def cf_var_name(field: Any, dim: str) -> str:
    """Return the best available name for a CF field dimension coordinate.

    Names are checked in priority order: ncvar, short_name, long_name,
    standard_name.
    """
    # If multiple Z coordinates exist, use the last one
    if dim == "Z":
        z_names = [
            mycoord
            for mycoord in list(field.coords())
            if field.coord(mycoord).Z
        ]
        if len(z_names) > 1:
            dim = z_names[-1]

    construct = field.construct(dim)
    id_ = getattr(construct, "id", False)
    ncvar = construct.nc_get_variable(False)
    short_name = getattr(construct, "short_name", False)
    long_name = getattr(construct, "long_name", False)
    standard_name = getattr(construct, "standard_name", False)

    name = "No Name"
    if id_:
        name = id_
    if ncvar:
        name = ncvar
    if short_name:
        name = short_name
    if long_name:
        name = long_name
    if standard_name:
        name = standard_name
    return name


def cf_var_name_titles(field: Any, dim: str) -> tuple[str | None, str | None]:
    """Return preferred coordinate name/units for dimension-title rendering."""
    name = None
    units = None
    if field.has_construct(dim):
        construct = field.construct(dim)
        id_ = getattr(construct, "id", False)
        ncvar = construct.nc_get_variable(False)
        short_name = getattr(construct, "short_name", False)
        long_name = getattr(construct, "long_name", False)
        standard_name = getattr(construct, "standard_name", False)

        if id_:
            name = id_
        if ncvar:
            name = ncvar
        if short_name:
            name = short_name
        if long_name:
            name = long_name
        if standard_name:
            name = standard_name

        units = getattr(construct, "units", "")
        if len(units) > 0:
            units = f"({units})"
    return name, units


def generate_titles(f: Any = None) -> str:
    """Generate dimension/cell-method title text for plot annotation."""
    import cf

    from .validate import check_well_formed

    mycoords = find_dim_names(f)
    # Preserve legacy side effect/validation behavior.
    check_well_formed(f)

    title_dims = ""
    if isinstance(f, cf.Field):
        for idim in np.arange(len(mycoords)):
            mycoord = mycoords[idim]
            if mycoord == "Z":
                mycoord = find_z(f)

            title, units = cf_var_name_titles(f, mycoord)
            if not f.coord(mycoord).T:
                values = f.construct(mycoord).array
                if len(values) > 1:
                    value = ""
                else:
                    value = str(values)
                title_dims += f"{mycoord}: {title} {value} {units}\n"

            else:
                values = f.construct(mycoord).dtarray
                if len(values) > 1:
                    value = ""
                else:
                    value = str(cf.Data(values).datetime_as_string)
                title_dims += f"{mycoord}: {title} {value}\n"

        if len(f.cell_methods()) > 0:
            title_dims += "cell_methods: "
            i = 0

            for method in f.cell_methods():
                if len(f.cell_methods()[method].get_axes()) > 0:
                    axis = f.cell_methods()[method].get_axes()[0]
                    try:
                        myid = f.constructs.domain_axis_identity(axis)
                    except ValueError:
                        myid = axis

                    value = ""
                    if f.cell_methods()[method].has_method():
                        value = f.cell_methods()[method].get_method()

                    qualifiers = f.cell_methods()[method].qualifiers()
                    qualifier_text = ""
                    if len(qualifiers) > 0:
                        qualifier_text = str(qualifiers)

                    if i > 0:
                        title_dims += ", "

                    title_dims += f"{myid}: {value} {qualifier_text}"
                    i += 1

    return title_dims


def find_dim_names(field: Any) -> list:
    """Return dimension coordinate names in [X, Y, Z, T] order.

    Ignores auxiliary coordinates unless no dimension coordinate is available
    for a given axis.
    """
    daxes = list(field.get_data_axes())
    dcoords = list(field.coords())

    nx = ny = nz = nt = 0
    for coord in dcoords:
        c = field.coord(coord)
        if c.X:
            nx += 1
        if c.Y:
            ny += 1
        if c.Z:
            nz += 1
        if c.T:
            nt += 1

    coords = []
    for axis in daxes:
        chosen = None
        for coord in dcoords:
            try:
                caxes = field.get_data_axes(coord)
            except Exception:
                continue
            if not caxes or caxes[0] != axis:
                continue
            if not str(coord).startswith("auxiliarycoordinate"):
                chosen = coord
                break
            if chosen is None:
                chosen = coord
        if chosen is not None:
            coords.append(chosen)

    mycoords = deepcopy(coords)
    for i in np.arange(len(coords)):
        c = field.coord(coords[i])
        if c.X and nx == 1:
            mycoords[i] = "X"
        if c.Y and ny == 1:
            mycoords[i] = "Y"
        if c.Z and nz == 1:
            mycoords[i] = "Z"
        if c.T and nt == 1:
            mycoords[i] = "T"

    mycoords.reverse()
    return mycoords


def find_z(field: Any) -> str | None:
    """Return the key for the Z coordinate of a CF field, or None."""
    if field is None:
        return None
    mycoords = find_dim_names(field)
    myz = None
    for mycoord in mycoords:
        if field.coord(mycoord).Z:
            myz = mycoord
    return myz


def cf_data_assign(
    f: Any,
    colorbar_title: str | None = None,
    verbose: bool | None = None,
    proj: str = "cyl",
) -> tuple:
    """Extract arrays and metadata from a CF field for contouring.

    This is the refactored, pure version of the legacy ``_cf_data_assign``
    function.  It has no dependency on ``plotvars`` global state; the one
    piece of state it previously read (``plotvars.proj``) is passed explicitly
    via the *proj* parameter.

    Parameters
    ----------
    f : cf.Field
        Input CF field.
    colorbar_title : str or None
        Override colorbar title; if None, derived from field metadata.
    verbose : bool or None
        Print diagnostic information when True.
    proj : str
        Current map projection (default ``'cyl'``).  Used to decide whether
        to look for auxiliary lon/lat coordinates on rotated-pole fields.

    Returns
    -------
    field, x, y, ptype, colorbar_title, xlabel, ylabel, xpole, ypole
    """
    import cf as _cf
    import cartopy.crs as _ccrs

    # Check input data has the correct number of dimensions.
    # Rotated-pole fields may legitimately have extra dimensions.
    ndim = len(f.domain_axes().filter_by_size(_cf.gt(1)))
    if f.ref("grid_mapping_name:rotated_latitude_longitude", default=False) is False:
        if ndim > 2 or ndim < 1:
            if ndim > 2:
                errstr = "cf_data_assign error - data has too many dimensions"
            else:
                errstr = "cf_data_assign error - data has too few dimensions"
            errstr += "\n cf-plot requires one or two dimensional data\n"
            for mydim in list(f.dimension_coordinates()):
                sn = getattr(f.construct(mydim), "standard_name", False)
                ln = getattr(f.construct(mydim), "long_name", False)
                if sn:
                    errstr += f"{mydim},{sn},{f.construct(mydim).size}\n"
                elif ln:
                    errstr += f"{mydim},{ln},{f.construct(mydim).size}\n"
            raise Warning(errstr)

    lons = lats = height = time = None
    has_lons = has_lats = has_height = has_time = False
    xlabel = ylabel = ""
    xpole = ypole = None
    ptype = None
    x = y = None

    myz = find_z(f)

    for mycoord in f.coords():
        c = f.coord(mycoord)
        if c.X:
            lons = np.squeeze(f.construct(mycoord).array)
            if verbose:
                print("lons -", lons)
            if np.size(lons) > 1:
                has_lons = True
        if c.Y:
            lats = np.squeeze(f.construct(mycoord).array)
            if verbose:
                print("lats -", lats)
            if np.size(lats) > 1:
                has_lats = True
        if c.Z:
            height = np.squeeze(f.construct(mycoord).array)
            if verbose:
                print("height -", height)
            if np.size(height) > 1:
                has_height = True
        if c.T:
            time = np.squeeze(f.construct(mycoord).array)
            if verbose:
                print("time -", time)
            if np.size(time) > 1:
                has_time = True

    field = np.squeeze(f.array)

    if str(f.dtype) == "bool":
        print("\n\n\n Warning - boolean data found - converting to integers\n\n\n")
        g = deepcopy(f)
        g.dtype = int
        field = np.squeeze(g.array)

    if has_lons and has_lats:
        ptype = 1
        x = lons
        y = lats

    if has_lats and has_height:
        ptype = 2
        x = lats
        y = height
        xname = cf_var_name(field=f, dim="Y")
        xunits = str(getattr(f.construct("Y"), "Units", ""))
        if xunits == "degrees_north":
            xunits = "degrees"
        xlabel = f"{xname} ({xunits})" if xunits else xname
        yname = cf_var_name(field=f, dim=myz)
        yunits = str(getattr(f.construct(myz), "Units", ""))
        ylabel = f"{yname} ({yunits})" if yunits else yname

    if has_lons and has_height:
        ptype = 3
        x = lons
        y = height
        xname = cf_var_name(field=f, dim="X")
        xunits = str(getattr(f.construct("X"), "Units", ""))
        if xunits == "degrees_east":
            xunits = "degrees"
        xlabel = f"{xname} ({xunits})" if xunits else xname
        yname = cf_var_name(field=f, dim=myz)
        yunits = str(getattr(f.construct(myz), "Units", ""))
        ylabel = f"{yname} ({yunits})" if yunits else yname

    if has_lons and has_time:
        ptype = 4
        x = lons
        y = time
        xname = cf_var_name(field=f, dim="X")
        xunits = str(getattr(f.construct("X"), "Units", ""))
        if xunits == "degrees_east":
            xunits = "degrees"
        xlabel = f"{xname} ({xunits})" if xunits else xname
        yname = cf_var_name(field=f, dim="T")
        yunits = str(getattr(f.construct("T"), "Units", ""))
        ylabel = f"{yname} ({yunits})" if yunits else yname

    if has_lats and has_time:
        ptype = 5
        x = lats
        y = time
        xname = cf_var_name(field=f, dim="Y")
        xunits = str(getattr(f.construct("Y"), "Units", ""))
        if xunits == "degrees_north":
            xunits = "degrees"
        xlabel = f"{xname} ({xunits})" if xunits else xname
        yname = cf_var_name(field=f, dim="T")
        yunits = str(getattr(f.construct("T"), "Units", ""))
        ylabel = f"{yname} ({yunits})" if yunits else yname

    if has_height and has_time:
        ptype = 7
        x = time
        y = height
        xname = cf_var_name(field=f, dim="T")
        xunits = str(getattr(f.construct("T"), "Units", ""))
        xlabel = f"{xname} ({xunits})" if xunits else xname
        yname = cf_var_name(field=f, dim="Z")
        yunits = str(getattr(f.construct("Z"), "Units", ""))
        ylabel = f"{yname} ({yunits})" if yunits else yname
        field = np.flipud(np.rot90(field))

    # Rotated pole
    if f.ref("grid_mapping_name:rotated_latitude_longitude", default=False):
        ptype = 6
        rotated_pole = f.ref("grid_mapping_name:rotated_latitude_longitude")
        xpole = rotated_pole["grid_north_pole_longitude"]
        ypole = rotated_pole["grid_north_pole_latitude"]
        for mydim in list(f.dimension_coordinates()):
            name = cf_var_name(field=f, dim=mydim)
            if name in ["grid_longitude", "longitude", "x"]:
                x = np.squeeze(f.construct(mydim).array)
                xunits = str(getattr(f.construct(mydim), "units", ""))
                xlabel = cf_var_name(field=f, dim=mydim)
            if name in ["grid_latitude", "latitude", "y"]:
                y = np.squeeze(f.construct(mydim).array)
                if y[0] > y[-1]:
                    y = y[::-1]
                    field = np.flipud(field)
                yunits = str(getattr(f.construct(mydim), "Units", ""))
                ylabel = cf_var_name(field=f, dim=mydim) + yunits

    # Auxiliary lon/lat (e.g. ORCA, UGRID)
    if ptype == 1 or ptype is None:
        if proj != "rotated":
            aux_lons = aux_lats = False
            xpts = ypts = None
            for mydim in list(f.auxiliary_coordinates()):
                name = cf_var_name(field=f, dim=mydim)
                if name in ["longitude"]:
                    xpts = np.squeeze(f.construct(mydim).array)
                    aux_lons = True
                if name in ["latitude"]:
                    ypts = np.squeeze(f.construct(mydim).array)
                    aux_lats = True
            if aux_lons and aux_lats:
                x = xpts
                y = ypts
                ptype = 1

    # UKCP transverse mercator
    if f.ref("grid_mapping_name:transverse_mercator", default=False):
        ptype = 1
        field = np.squeeze(f.array)
        has_lons = has_lats = False
        for mydim in list(f.auxiliary_coordinates()):
            name = cf_var_name(field=f, dim=mydim)
            if name in ["longitude"]:
                x = np.squeeze(f.construct(mydim).array)
                has_lons = True
            if name in ["latitude"]:
                y = np.squeeze(f.construct(mydim).array)
                has_lats = True
        if not has_lons or not has_lats:
            xpts = f.construct("X").array
            ypts = f.construct("Y").array
            field = np.squeeze(f.array)
            ref = f.ref("grid_mapping_name:transverse_mercator")
            transform = _ccrs.TransverseMercator(
                false_easting=ref["false_easting"],
                false_northing=ref["false_northing"],
                central_longitude=ref["longitude_of_central_meridian"],
                central_latitude=ref["latitude_of_projection_origin"],
                scale_factor=ref["scale_factor_at_central_meridian"],
            )
            xvals, yvals = np.meshgrid(xpts, ypts)
            points = _ccrs.PlateCarree().transform_points(transform, xvals, yvals)
            x = np.array(points)[:, :, 0]
            y = np.array(points)[:, :, 1]

    # None of the above — fall back to ptype 0
    if ptype is None:
        ptype = 0
        data_axes = f.get_data_axes()
        count = 1
        for d in data_axes:
            try:
                c = f.coordinate(filter_by_axis=[d])
                if np.size(c.array) > 1:
                    if count == 1:
                        y = c
                        mycoord = "dimensioncoordinate" + str(d[-1])
                        yunits = str(getattr(f.coord(mycoord), "Units", ""))
                        yunits_str = f"({yunits})" if yunits else ""
                        ylabel = cf_var_name(field=f, dim=mycoord) + yunits_str
                    elif count == 2:
                        x = c
                        mycoord = "dimensioncoordinate" + str(d[-1])
                        xunits = str(getattr(f.coord(mycoord), "units", ""))
                        xunits_str = f"({xunits})" if xunits else ""
                        xlabel = cf_var_name(field=f, dim=mycoord) + xunits_str
                    count += 1
            except ValueError:
                errstr = (
                    "\n\ncf_data_assign - cannot find data to return\n\n"
                    f"{f.constructs.domain_axis_identity(d)}\n\n"
                )
                raise Warning(errstr)

    # Derive colorbar title from field metadata
    if colorbar_title is None:
        colorbar_title = "No Name"
        if hasattr(f, "id"):
            colorbar_title = f.id
        nc = f.nc_get_variable(None)
        if nc:
            colorbar_title = f.nc_get_variable()
        if hasattr(f, "short_name"):
            colorbar_title = f.short_name
        if hasattr(f, "long_name"):
            colorbar_title = f.long_name
        if hasattr(f, "standard_name"):
            colorbar_title = f.standard_name
        if hasattr(f, "Units"):
            units_str = str(f.Units)
            if units_str:
                colorbar_title = f"{colorbar_title} ({_supscr(units_str)})"

    return (field, x, y, ptype, colorbar_title, xlabel, ylabel, xpole, ypole)


def add_cyclic(field: np.ndarray, lons: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Add a cyclic longitude column if the grid doesn't span the full 360°.
    
    Wraps cartopy_util.add_cyclic_point with float-rounding fallback for
    uneven longitude spacing due to numpy precision.
    """
    try:
        return cartopy_util.add_cyclic_point(field, lons)
    except Exception:
        # Check if spacing is nearly uniform (floating-point precision issue)
        # rather than genuinely unequal. Float32 data often has ~1e-5 artifacts.
        diffs = np.diff(lons)
        mean_diff = np.mean(diffs)
        max_deviation = np.max(np.abs(diffs - mean_diff))
        # If max deviation is < 0.01% of mean spacing, treat as floating-point
        # precision artifact and reconstruct with linspace.
        if max_deviation < 1e-4 * mean_diff:
            lons_reconstructed = np.linspace(
                float(lons[0]), float(lons[-1]), len(lons)
            )
            return cartopy_util.add_cyclic_point(field, lons_reconstructed)
        else:
            # Spacing is genuinely unequal, re-raise the original error
            raise


def stipple_points(
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    pts: int | list | np.ndarray,
    stype: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate regular or offset sampling points over a rectangular domain.

    Parameters
    ----------
    xmin, xmax, ymin, ymax : float
        Domain bounds.
    pts : int or length-2 sequence
        Number of points in x and y directions.
    stype : int
        1 for regular grid rows, 2 for alternating offset rows.
    """
    if np.size(pts) == 1:
        pts_x = int(pts)
        pts_y = int(pts)
    else:
        pts_x = int(pts[0])
        pts_y = int(pts[1])

    xstep = (xmax - xmin) / float(pts_x)
    x1 = [xmin + xstep / 4]
    while (np.nanmax(x1) + xstep) < xmax - xstep / 10:
        x1 = np.append(x1, np.nanmax(x1) + xstep)

    x2 = [xmin + xstep * 3 / 4]
    while (np.nanmax(x2) + xstep) < xmax - xstep / 10:
        x2 = np.append(x2, np.nanmax(x2) + xstep)

    ystep = (ymax - ymin) / float(pts_y)
    y1 = [ymin + ystep / 2]
    while (np.nanmax(y1) + ystep) < ymax - ystep / 10:
        y1 = np.append(y1, np.nanmax(y1) + ystep)

    xnew: list[float] | np.ndarray = []
    ynew: list[float] | np.ndarray = []
    iy = 0
    for y in y1:
        iy += 1
        if stype == 1:
            xnew = np.append(xnew, x1)
            y2 = np.zeros(np.size(x1))
            y2.fill(y)
            ynew = np.append(ynew, y2)
        if stype == 2:
            if iy % 2 == 0:
                xnew = np.append(xnew, x1)
                y2 = np.zeros(np.size(x1))
                y2.fill(y)
                ynew = np.append(ynew, y2)
            if iy % 2 == 1:
                xnew = np.append(xnew, x2)
                y2 = np.zeros(np.size(x2))
                y2.fill(y)
                ynew = np.append(ynew, y2)

    return np.asarray(xnew), np.asarray(ynew)


def _find_pos_in_array(vals: np.ndarray, val: float) -> int:
    """Return lower-bracketing index for *val* in monotonic coordinate *vals*."""
    pos = int(np.searchsorted(vals, val, side="right") - 1)
    return max(0, min(pos, np.size(vals) - 2))


def regrid(
    f: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    xnew: np.ndarray,
    ynew: np.ndarray,
) -> np.ndarray:
    """Bilinearly interpolate a regular 2D field onto scattered target points."""
    regrid_f = deepcopy(f)
    regrid_x = deepcopy(x)
    regrid_y = deepcopy(y)

    if regrid_x[0] > regrid_x[-1]:
        regrid_x = regrid_x[::-1]
        regrid_f = np.fliplr(regrid_f)

    if regrid_y[0] > regrid_y[-1]:
        regrid_y = regrid_y[::-1]
        regrid_f = np.flipud(regrid_f)

    out = np.array([], dtype=float)
    for i in np.arange(np.size(xnew)):
        xval = xnew[i]
        yval = ynew[i]

        ix = _find_pos_in_array(regrid_x, xval)
        iy = _find_pos_in_array(regrid_y, yval)
        ix2 = ix + 1
        iy2 = iy + 1

        dx = regrid_x[ix2] - regrid_x[ix]
        dy = regrid_y[iy2] - regrid_y[iy]
        alpha_x = (xval - regrid_x[ix]) / (dx if dx != 0 else 1e-30)
        alpha_y = (yval - regrid_y[iy]) / (dy if dy != 0 else 1e-30)

        v1 = regrid_f[iy, ix] - (regrid_f[iy, ix] - regrid_f[iy, ix2]) * alpha_x
        v2 = regrid_f[iy2, ix] - (regrid_f[iy2, ix] - regrid_f[iy2, ix2]) * alpha_x
        newval = v1 - (v1 - v2) * alpha_y

        out = np.append(out, newval)

    return out


def polar_regular_grid(
    pts: int = 50,
    proj: str = "npstere",
    boundinglat: float = 0,
    lon_0: float = 0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return lon/lat and projected x/y points over a polar stereographic cap."""
    import cartopy.crs as ccrs

    if proj == "npstere":
        thisproj = ccrs.NorthPolarStereo(central_longitude=lon_0)
    else:
        thisproj = ccrs.SouthPolarStereo(central_longitude=lon_0)

    lons = np.array([lon_0 - 90, lon_0, lon_0 + 90, lon_0 + 180])
    lats = np.array([boundinglat, boundinglat, boundinglat, boundinglat])
    extent = thisproj.transform_points(ccrs.PlateCarree(), lons, lats)

    xmin = np.min(extent[:, 0])
    xmax = np.max(extent[:, 0])
    ymin = np.min(extent[:, 1])
    ymax = np.max(extent[:, 1])

    points_device = stipple_points(
        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, pts=pts, stype=2
    )
    xnew = np.array(points_device)[0, :]
    ynew = np.array(points_device)[1, :]

    points_polar = ccrs.PlateCarree().transform_points(thisproj, xnew, ynew)
    lons = np.array(points_polar)[:, 0]
    lats = np.array(points_polar)[:, 1]

    if proj == "npstere":
        valid = np.where(lats >= boundinglat)
    else:
        valid = np.where(lats <= boundinglat)

    return lons[valid], lats[valid], xnew[valid], ynew[valid]
