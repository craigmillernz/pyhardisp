# Copyright (c) 2026 Earth Sciences New Zealand.

"""
HARDISP - Tidal Displacement Calculator
=========================================

Derived from IERS Conventions software (2008).

Original software:
Copyright (C) 2008 IERS Conventions Center

This file is a Python translation and modified version of the
original Fortran implementation.

Modifications include:
- Translation from Fortran to Python
- Refactoring and structural changes
- Interface redesign

See LICENSE_IERS.txt for full license terms.

"""

import math
import csv
import numpy as np
from typing import Tuple, List, Optional
from datetime import datetime, timedelta


# Constants
PI = math.pi
DR = 0.01745329252  # Degrees to radians


def fortran_int_divide(a: int, b: int) -> int:
    """Integer division with Fortran semantics (truncate toward zero)."""
    return int(a / b)


# ==================================================================
# Date and Time Functions
# ==================================================================


def is_leap_year(year: int) -> int:
    """Check if Gregorian year is a leap year. Returns 1 or 0."""
    leap_val = 1 - fortran_int_divide((year % 4) + 3, 4)
    if (year % 100) == 0 and (year % 400) != 0:
        leap_val = 0
    return leap_val


def days_before_month(year: int, month: int) -> int:
    """Days before start of month (0 for Jan 1)."""
    leap_val = is_leap_year(year)
    base = fortran_int_divide(367 * (month - 2 - 12 * fortran_int_divide(month - 14, 12)), 12) + 29
    return (base % 365) + leap_val * fortran_int_divide(9 + month, 12)


def julian_date(year: int, month: int, day: int) -> int:
    """Convert Gregorian date to Julian Day Number."""
    temp = fortran_int_divide(month - 14, 12)
    jd = fortran_int_divide(1461 * (year + 4800 + temp), 4)
    jd += fortran_int_divide(367 * (month - 2 - 12 * temp), 12)
    jd -= fortran_int_divide(3 * fortran_int_divide(year + 4900 + temp, 100), 4)
    return jd + day - 32075


def doy_to_ymd(year: int, day_of_year: int) -> Tuple[int, int, int]:
    """Convert year/day-of-year to year/month/day."""
    leap_val = is_leap_year(year)

    def idn(m):
        return (
            fortran_int_divide(367 * (m - 2 - 12 * fortran_int_divide(m - 14, 12)), 12) + 29
        ) % 365

    month = (
        fortran_int_divide(12 * (day_of_year - 29 - leap_val), 367)
        + 2
        + fortran_int_divide(day_of_year - 200, 169)
    )
    day = day_of_year - idn(month) - leap_val * fortran_int_divide(9 + month, 12)

    return year, month, day


def earth_time_offset_seconds(year: float) -> float:
    """ET - UTC in seconds for given decimal year."""
    if year < 1700.0:
        return 0.0
    if year < 1785.0:
        return (year - 1750.0) / 5.0
    if year < 1820.5:
        return 6.0

    d = [
        5.15,
        4.64,
        5.36,
        3.49,
        3.27,
        2.45,
        4.03,
        1.76,
        3.30,
        1.00,
        2.42,
        0.94,
        2.31,
        2.27,
        -0.22,
        0.03,
        -0.05,
        -0.06,
        -0.57,
        0.03,
        -0.47,
        0.98,
        -0.86,
        2.45,
        0.22,
        0.37,
        2.79,
        1.20,
        3.52,
        1.17,
        2.67,
        3.06,
        2.66,
        2.97,
        3.28,
        3.31,
        3.33,
        3.23,
        3.60,
        3.52,
        4.27,
        2.68,
        2.75,
        2.67,
        1.94,
        1.39,
        1.66,
        0.88,
        0.33,
        -0.17,
        -1.88,
        -3.43,
        -4.05,
        -5.77,
        -7.06,
        -7.36,
        -7.67,
        -7.64,
        -7.93,
        -7.82,
        -8.35,
        -7.91,
        -8.03,
        -9.14,
        -8.18,
        -7.88,
        -7.62,
        -7.17,
        -8.14,
        -7.59,
        -7.17,
        -7.94,
        -8.23,
        -7.88,
        -7.68,
        -6.94,
        -6.89,
        -7.11,
        -5.87,
        -5.04,
        -3.90,
        -2.87,
        -0.58,
        0.71,
        1.80,
        3.08,
        4.63,
        5.86,
        7.21,
        8.58,
        10.50,
        12.10,
        12.49,
        14.41,
        15.59,
        15.81,
        17.52,
        19.01,
        18.39,
        19.55,
        20.36,
        21.01,
        21.81,
        21.76,
        22.35,
        22.68,
        22.94,
        22.93,
        22.69,
        22.94,
        23.20,
        23.31,
        23.63,
        23.47,
        23.68,
        23.62,
        23.53,
        23.59,
        23.99,
        23.80,
        24.20,
        24.99,
        24.97,
        25.72,
        26.21,
        26.37,
        26.89,
        27.68,
        28.13,
        28.94,
        29.42,
        29.66,
        30.29,
        30.96,
        31.09,
        31.59,
        32.06,
        31.82,
        32.69,
        33.05,
        33.16,
        33.59,
    ]

    if year < 1961.5:
        n = int(year - 1819.5)
        frac = year - (1819.5 + n)
        if 0 <= n < len(d) - 1:
            return (d[n + 1] - d[n]) * frac + d[n]
        return d[0] if n < 0 else d[-1]

    if year < 1972.0:
        u = year - 1900.0
        return -0.00002 * u**3 + 0.000297 * u**2 + 0.025184 * u - 2.50976

    delta = 42.184
    for leap_time in [
        1972.5,
        1973.0,
        1974.0,
        1975.0,
        1976.0,
        1977.0,
        1978.0,
        1979.0,
        1980.0,
        1981.5,
        1982.5,
        1983.5,
        1985.5,
        1988.0,
        1990.0,
        1991.0,
        1992.5,
        1993.5,
        1994.5,
        1996.0,
        1997.5,
        1999.0,
        2006.0,
        2009.0,
        2012.5,
        2015.5,
        2017.0,
    ]:
        if year >= leap_time:
            delta += 1.0
        else:
            break

    return delta


# ==================================================================
# Spline Interpolation
# ==================================================================


def cublic_spline(x: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Compute cubic spline second derivatives."""
    x = np.asarray(x, dtype=float)
    u = np.asarray(u, dtype=float)
    n = len(x)

    if n <= 3:
        return np.zeros(n)

    s = np.zeros(n)
    a = np.zeros(n)

    # Parabolic end conditions
    dx1, du1 = x[1] - x[0], (u[1] - u[0]) / (x[1] - x[0])
    dx2, du2 = x[2] - x[1], (u[2] - u[1]) / (x[2] - x[1])
    q1 = (u[0] / dx1**2 - u[1] / dx2**2) / (1.0 / dx1 - 1.0 / dx2)

    dx_n1 = x[-2] - x[-1]
    du_n1 = (u[-2] - u[-1]) / dx_n1
    dx_n2 = x[-3] - x[-2]
    du_n2 = (u[-3] - u[-2]) / dx_n2
    qn = (u[-2] / dx_n1**2 - u[-3] / dx_n2**2) / (1.0 / dx_n1 - 1.0 / dx_n2)

    # RHS (vectorized)
    s[0] = 6.0 * (du1 - q1)
    dx_left = x[1:-1] - x[:-2]  # x[i] - x[i-1] for i=1..n-2
    dx_right = x[2:] - x[1:-1]  # x[i+1] - x[i] for i=1..n-2
    s[1:-1] = (
        u[:-2] / dx_left - u[1:-1] * (1.0 / dx_left + 1.0 / dx_right) + u[2:] / dx_right
    ) * 6.0
    s[-1] = 6.0 * (qn + (u[-2] - u[-1]) / (x[-1] - x[-2]))

    # Tridiagonal solve
    a[0] = 2.0 * (x[1] - x[0])
    a[1] = 1.5 * (x[1] - x[0]) + 2.0 * (x[2] - x[1])
    s[1] -= 0.5 * s[0]

    for i in range(2, n - 1):
        c = (x[i] - x[i - 1]) / a[i - 1]
        a[i] = 2.0 * (x[i + 1] - x[i - 1]) - c * (x[i] - x[i - 1])
        s[i] -= c * s[i - 1]

    c = (x[-1] - x[-2]) / a[-2]
    a[-1] = (2.0 - c) * (x[-1] - x[-2])
    s[-1] -= c * s[-2]

    # Back substitution
    s[-1] /= a[-1]
    for j in range(1, n):
        s[-(j + 1)] = (s[-(j + 1)] - (x[-j] - x[-(j + 1)]) * s[-j]) / a[-(j + 1)]

    return s


def spline_eval(y: float, x: np.ndarray, u: np.ndarray, s: np.ndarray) -> float:
    """Evaluate cubic spline at point y."""
    if y <= x[0]:
        return u[0]
    if y >= x[-1]:
        return u[-1]

    # Find interval using searchsorted
    k2 = np.searchsorted(x, y, side="left")
    k2 = max(1, min(k2, len(x) - 1))
    k1 = k2 - 1

    # Spline formula
    dy = x[k2] - y
    dy1 = y - x[k1]
    dk = x[k2] - x[k1]
    deli = 1.0 / (6.0 * dk)

    return (
        (s[k1] * dy**3 + s[k2] * dy1**3) * deli
        + dy1 * (u[k2] / dk - s[k2] * dk / 6.0)
        + dy * (u[k1] / dk - s[k1] * dk / 6.0)
    )


def spline_eval_batch(y_arr: np.ndarray, x: np.ndarray, u: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Evaluate cubic spline at multiple points (vectorized)."""
    y_arr = np.asarray(y_arr, dtype=float)

    # Find intervals using searchsorted
    k2 = np.searchsorted(x, y_arr, side="left")
    k2 = np.clip(k2, 1, len(x) - 1)
    k1 = k2 - 1

    dy = x[k2] - y_arr
    dy1 = y_arr - x[k1]
    dk = x[k2] - x[k1]
    deli = 1.0 / (6.0 * dk)

    result = (
        (s[k1] * dy**3 + s[k2] * dy1**3) * deli
        + dy1 * (u[k2] / dk - s[k2] * dk / 6.0)
        + dy * (u[k1] / dk - s[k1] * dk / 6.0)
    )

    # Handle out-of-range values
    result[y_arr <= x[0]] = u[0]
    result[y_arr >= x[-1]] = u[-1]

    return result


# ==================================================================
# Tidal Calculations
# ==================================================================

_tidal = {"D": np.zeros(6), "DD": np.zeros(6), "init": False}


def calculate_tidal_arguments(
    year: int, day_of_year: int, hour: int = 0, minute: int = 0, second: int = 0
) -> None:
    """Precompute Doodson variables for tidal calculations."""
    global _tidal

    y, m, d = doy_to_ymd(year, day_of_year)
    jd = julian_date(year, m, d)
    dayfr = hour / 24.0 + minute / 1440.0 + second / 86400.0

    days_in_year = 365 + is_leap_year(year)
    year_decimal = year + (day_of_year - 1 + dayfr) / days_in_year
    delta = earth_time_offset_seconds(year_decimal)

    djd = jd - 0.5 + dayfr
    t = (djd - 2451545.0 + delta / 86400.0) / 36525.0

    f1 = 134.9634025100 + t * (
        477198.8675605000 + t * (0.0088553333 + t * (0.0000143431 - 0.0000000680 * t))
    )
    f2 = 357.5291091806 + t * (
        35999.0502911389 + t * (-0.0001536667 + t * (0.0000000378 - 0.0000000032 * t))
    )
    f3 = 93.2720906200 + t * (
        483202.0174577222 + t * (-0.0035420000 + t * (-0.0000002881 + 0.0000000012 * t))
    )
    f4 = 297.8501954694 + t * (
        445267.1114469445 + t * (-0.0017696111 + t * (0.0000018314 - 0.0000000088 * t))
    )
    f5 = 125.0445550100 + t * (
        -1934.1362619722 + t * (0.0020756111 + t * (0.0000021394 - 0.0000000165 * t))
    )

    D = np.array(
        [
            360.0 * dayfr - f4,
            f3 + f5,
            f3 + f5 - f4,
            f3 + f5 - f1,
            -f5,
            f3 + f5 - f4 - f2,
        ]
    )

    fd1 = 0.0362916471 + 0.0000000013 * t
    fd2 = 0.0027377786
    fd3 = 0.0367481951 - 0.0000000005 * t
    fd4 = 0.0338631920 - 0.0000000003 * t
    fd5 = -0.0001470938 + 0.0000000003 * t

    DD = np.array(
        [
            1.0 - fd4,
            fd3 + fd5,
            fd3 + fd5 - fd4,
            fd3 + fd5 - fd1,
            -fd5,
            fd3 + fd5 - fd4 - fd2,
        ]
    )

    _tidal.update({"D": D, "DD": DD, "init": True})


def tidal_frequency_and_phase(idood: np.ndarray) -> Tuple[float, float]:
    """Get frequency and phase of tidal constituent from Doodson number."""
    global _tidal
    if not _tidal["init"]:
        calculate_tidal_arguments(2000, 1, 12, 0, 0)

    idood = np.asarray(idood, dtype=float)
    freq = np.dot(idood, _tidal["DD"])
    phase = np.dot(idood, _tidal["D"]) % 360.0
    if phase < 0:
        phase += 360.0

    return freq, phase


def tidal_frequency_and_phase_batch(idood_array: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Get frequency and phase for multiple constituents at once (vectorized)."""
    global _tidal
    if not _tidal["init"]:
        calculate_tidal_arguments(2000, 1, 12, 0, 0)

    idood_array = np.asarray(idood_array, dtype=float)
    freq = idood_array @ _tidal["DD"]
    phase = idood_array @ _tidal["D"] % 360.0
    phase[phase < 0] += 360.0
    return freq, phase


# ==================================================================
# Recursive Harmonic Series
# ==================================================================


def recursion(n: int, hc: np.ndarray, nf: int, om: np.ndarray) -> np.ndarray:
    """Compute harmonic series using recursive evaluation (vectorized)."""
    cos_om = np.cos(om)
    sin_om = np.sin(om)

    # Separate arrays instead of interleaved (better cache + vectorized ops)
    hc_even = hc[0 : 2 * nf : 2]  # hc[0], hc[2], ... hc[2*(nf-1)]  -> (nf,)
    hc_odd = hc[1 : 2 * nf : 2]  # hc[1], hc[3], ... hc[2*(nf-1)+1] -> (nf,)
    a = hc_even.copy()  # current values (nf,)
    b = hc_even * cos_om - hc_odd * sin_om  # previous values (nf,)
    c = 2.0 * cos_om  # multiplier (nf,)

    x = np.zeros(n)
    for j in range(n):
        x[j] = np.sum(a)
        a_prev = a.copy()
        a = c * a_prev - b
        b = a_prev

    return x


# ==================================================================
# ADMINT - Admittance Interpolation for 342 Constituents
# ==================================================================

# Cartwright-Edden amplitudes for all 342 constituents
TAMP = np.array(
    [
        0.632208,
        0.294107,
        0.121046,
        0.079915,
        0.023818,
        -0.023589,
        0.022994,
        0.019333,
        -0.017871,
        0.017192,
        0.016018,
        0.004671,
        -0.004662,
        -0.004519,
        0.004470,
        0.004467,
        0.002589,
        -0.002455,
        -0.002172,
        0.001972,
        0.001947,
        0.001914,
        -0.001898,
        0.001802,
        0.001304,
        0.001170,
        0.001130,
        0.001061,
        -0.001022,
        -0.001017,
        0.001014,
        0.000901,
        -0.000857,
        0.000855,
        0.000855,
        0.000772,
        0.000741,
        0.000741,
        -0.000721,
        0.000698,
        0.000658,
        0.000654,
        -0.000653,
        0.000633,
        0.000626,
        -0.000598,
        0.000590,
        0.000544,
        0.000479,
        -0.000464,
        0.000413,
        -0.000390,
        0.000373,
        0.000366,
        0.000366,
        -0.000360,
        -0.000355,
        0.000354,
        0.000329,
        0.000328,
        0.000319,
        0.000302,
        0.000279,
        -0.000274,
        -0.000272,
        0.000248,
        -0.000225,
        0.000224,
        -0.000223,
        -0.000216,
        0.000211,
        0.000209,
        0.000194,
        0.000185,
        -0.000174,
        -0.000171,
        0.000159,
        0.000131,
        0.000127,
        0.000120,
        0.000118,
        0.000117,
        0.000108,
        0.000107,
        0.000105,
        -0.000102,
        0.000102,
        0.000099,
        -0.000096,
        0.000095,
        -0.000089,
        -0.000085,
        -0.000084,
        -0.000081,
        -0.000077,
        -0.000072,
        -0.000067,
        0.000066,
        0.000064,
        0.000063,
        0.000063,
        0.000063,
        0.000062,
        0.000062,
        -0.000060,
        0.000056,
        0.000053,
        0.000051,
        0.000050,
        0.368645,
        -0.262232,
        -0.121995,
        -0.050208,
        0.050031,
        -0.049470,
        0.020620,
        0.020613,
        0.011279,
        -0.009530,
        -0.009469,
        -0.008012,
        0.007414,
        -0.007300,
        0.007227,
        -0.007131,
        -0.006644,
        0.005249,
        0.004137,
        0.004087,
        0.003944,
        0.003943,
        0.003420,
        0.003418,
        0.002885,
        0.002884,
        0.002160,
        -0.001936,
        0.001934,
        -0.001798,
        0.001690,
        0.001689,
        0.001516,
        0.001514,
        -0.001511,
        0.001383,
        0.001372,
        0.001371,
        -0.001253,
        -0.001075,
        0.001020,
        0.000901,
        0.000865,
        -0.000794,
        0.000788,
        0.000782,
        -0.000747,
        -0.000745,
        0.000670,
        -0.000603,
        -0.000597,
        0.000542,
        0.000542,
        -0.000541,
        -0.000469,
        -0.000440,
        0.000438,
        0.000422,
        0.000410,
        -0.000374,
        -0.000365,
        0.000345,
        0.000335,
        -0.000321,
        -0.000319,
        0.000307,
        0.000291,
        0.000290,
        -0.000289,
        0.000286,
        0.000275,
        0.000271,
        0.000263,
        -0.000245,
        0.000225,
        0.000225,
        0.000221,
        -0.000202,
        -0.000200,
        -0.000199,
        0.000192,
        0.000183,
        0.000183,
        0.000183,
        -0.000170,
        0.000169,
        0.000168,
        0.000162,
        0.000149,
        -0.000147,
        -0.000141,
        0.000138,
        0.000136,
        0.000136,
        0.000127,
        0.000127,
        -0.000126,
        -0.000121,
        -0.000121,
        0.000117,
        -0.000116,
        -0.000114,
        -0.000114,
        -0.000114,
        0.000114,
        0.000113,
        0.000109,
        0.000108,
        0.000106,
        -0.000106,
        -0.000106,
        0.000105,
        0.000104,
        -0.000103,
        -0.000100,
        -0.000100,
        -0.000100,
        0.000099,
        -0.000098,
        0.000093,
        0.000093,
        0.000090,
        -0.000088,
        0.000083,
        -0.000083,
        -0.000082,
        -0.000081,
        -0.000079,
        -0.000077,
        -0.000075,
        -0.000075,
        -0.000075,
        0.000071,
        0.000071,
        -0.000071,
        0.000068,
        0.000068,
        0.000065,
        0.000065,
        0.000064,
        0.000064,
        0.000064,
        -0.000064,
        -0.000060,
        0.000056,
        0.000056,
        0.000053,
        0.000053,
        0.000053,
        -0.000053,
        0.000053,
        0.000053,
        0.000052,
        0.000050,
        -0.066607,
        -0.035184,
        -0.030988,
        0.027929,
        -0.027616,
        -0.012753,
        -0.006728,
        -0.005837,
        -0.005286,
        -0.004921,
        -0.002884,
        -0.002583,
        -0.002422,
        0.002310,
        0.002283,
        -0.002037,
        0.001883,
        -0.001811,
        -0.001687,
        -0.001004,
        -0.000925,
        -0.000844,
        0.000766,
        0.000766,
        -0.000700,
        -0.000495,
        -0.000492,
        0.000491,
        0.000483,
        0.000437,
        -0.000416,
        -0.000384,
        0.000374,
        -0.000312,
        -0.000288,
        -0.000273,
        0.000259,
        0.000245,
        -0.000232,
        0.000229,
        -0.000216,
        0.000206,
        -0.000204,
        -0.000202,
        0.000200,
        0.000195,
        -0.000190,
        0.000187,
        0.000180,
        -0.000179,
        0.000170,
        0.000153,
        -0.000137,
        -0.000119,
        -0.000119,
        -0.000112,
        -0.000110,
        -0.000110,
        0.000107,
        -0.000095,
        -0.000095,
        -0.000091,
        -0.000090,
        -0.000081,
        -0.000079,
        -0.000079,
        0.000077,
        -0.000073,
        0.000069,
        -0.000067,
        -0.000066,
        0.000065,
        0.000064,
        -0.000062,
        0.000060,
        0.000059,
        -0.000056,
        0.000055,
        -0.000051,
    ]
)

# Doodson numbers for all 342 constituents (6 components each) - abbreviated for brevity
IDD_FLAT = [
    2,
    0,
    0,
    0,
    0,
    0,
    2,
    2,
    -2,
    0,
    0,
    0,
    2,
    -1,
    0,
    1,
    0,
    0,
    2,
    2,
    0,
    0,
    0,
    0,
    2,
    2,
    0,
    0,
    1,
    0,
    2,
    0,
    0,
    0,
    -1,
    0,
    2,
    -1,
    2,
    -1,
    0,
    0,
    2,
    -2,
    2,
    0,
    0,
    0,
    2,
    1,
    0,
    -1,
    0,
    0,
    2,
    2,
    -3,
    0,
    0,
    1,
    2,
    -2,
    0,
    2,
    0,
    0,
    2,
    -3,
    2,
    1,
    0,
    0,
    2,
    1,
    -2,
    1,
    0,
    0,
    2,
    -1,
    0,
    1,
    -1,
    0,
    2,
    3,
    0,
    -1,
    0,
    0,
    2,
    1,
    0,
    1,
    0,
    0,
    2,
    2,
    0,
    0,
    2,
    0,
    2,
    2,
    -1,
    0,
    0,
    -1,
    2,
    0,
    -1,
    0,
    0,
    1,
    2,
    1,
    0,
    1,
    1,
    0,
    2,
    3,
    0,
    -1,
    1,
    0,
    2,
    0,
    1,
    0,
    0,
    -1,
    2,
    0,
    -2,
    2,
    0,
    0,
    2,
    -3,
    0,
    3,
    0,
    0,
    2,
    -2,
    3,
    0,
    0,
    -1,
    2,
    4,
    0,
    0,
    0,
    0,
    2,
    -1,
    1,
    1,
    0,
    -1,
    2,
    -1,
    3,
    -1,
    0,
    -1,
    2,
    2,
    0,
    0,
    -1,
    0,
    2,
    -1,
    -1,
    1,
    0,
    1,
    2,
    4,
    0,
    0,
    1,
    0,
    2,
    -3,
    4,
    -1,
    0,
    0,
    2,
    -1,
    2,
    -1,
    -1,
    0,
    2,
    3,
    -2,
    1,
    0,
    0,
    2,
    1,
    2,
    -1,
    0,
    0,
    2,
    -4,
    2,
    2,
    0,
    0,
    2,
    4,
    -2,
    0,
    0,
    0,
    2,
    0,
    2,
    0,
    0,
    0,
    2,
    -2,
    2,
    0,
    -1,
    0,
    2,
    2,
    -4,
    0,
    0,
    2,
    2,
    2,
    -2,
    0,
    -1,
    0,
    2,
    1,
    0,
    -1,
    -1,
    0,
    2,
    -1,
    1,
    0,
    0,
    0,
    2,
    2,
    -1,
    0,
    0,
    1,
    2,
    2,
    1,
    0,
    0,
    -1,
    2,
    -2,
    0,
    2,
    -1,
    0,
    2,
    -2,
    4,
    -2,
    0,
    0,
    2,
    2,
    2,
    0,
    0,
    0,
    2,
    -4,
    4,
    0,
    0,
    0,
    2,
    -1,
    0,
    -1,
    -2,
    0,
    2,
    1,
    2,
    -1,
    1,
    0,
    2,
    -1,
    -2,
    3,
    0,
    0,
    2,
    3,
    -2,
    1,
    1,
    0,
    2,
    4,
    0,
    -2,
    0,
    0,
    2,
    0,
    0,
    2,
    0,
    0,
    2,
    0,
    2,
    -2,
    0,
    0,
    2,
    0,
    2,
    0,
    1,
    0,
    2,
    -3,
    3,
    1,
    0,
    -1,
    2,
    0,
    0,
    0,
    -2,
    0,
    2,
    4,
    0,
    0,
    2,
    0,
    2,
    4,
    -2,
    0,
    1,
    0,
    2,
    0,
    0,
    0,
    0,
    2,
    2,
    1,
    0,
    1,
    2,
    0,
    2,
    0,
    -2,
    0,
    -2,
    0,
    2,
    -2,
    1,
    0,
    0,
    1,
    2,
    -2,
    1,
    2,
    0,
    -1,
    2,
    -1,
    1,
    -1,
    0,
    1,
    2,
    5,
    0,
    -1,
    0,
    0,
    2,
    1,
    -3,
    1,
    0,
    1,
    2,
    -2,
    -1,
    2,
    0,
    1,
    2,
    3,
    0,
    -1,
    2,
    0,
    2,
    1,
    -2,
    1,
    -1,
    0,
    2,
    5,
    0,
    -1,
    1,
    0,
    2,
    -4,
    0,
    4,
    0,
    0,
    2,
    -3,
    2,
    1,
    -1,
    0,
    2,
    -2,
    1,
    1,
    0,
    0,
    2,
    4,
    0,
    -2,
    1,
    0,
    2,
    0,
    0,
    2,
    1,
    0,
    2,
    -5,
    4,
    1,
    0,
    0,
    2,
    0,
    2,
    0,
    2,
    0,
    2,
    -1,
    2,
    1,
    0,
    0,
    2,
    5,
    -2,
    -1,
    0,
    0,
    2,
    1,
    -1,
    0,
    0,
    0,
    2,
    2,
    -2,
    0,
    0,
    2,
    2,
    -5,
    2,
    3,
    0,
    0,
    2,
    -1,
    -2,
    1,
    -2,
    0,
    2,
    -3,
    5,
    -1,
    0,
    -1,
    2,
    -1,
    0,
    0,
    0,
    1,
    2,
    -2,
    0,
    0,
    -2,
    0,
    2,
    0,
    -1,
    1,
    0,
    0,
    2,
    -3,
    1,
    1,
    0,
    1,
    2,
    3,
    0,
    -1,
    -1,
    0,
    2,
    1,
    0,
    1,
    -1,
    0,
    2,
    -1,
    2,
    1,
    1,
    0,
    2,
    0,
    -3,
    2,
    0,
    1,
    2,
    1,
    -1,
    -1,
    0,
    1,
    2,
    -3,
    0,
    3,
    -1,
    0,
    2,
    0,
    -2,
    2,
    -1,
    0,
    2,
    -4,
    3,
    2,
    0,
    -1,
    2,
    -1,
    0,
    1,
    -2,
    0,
    2,
    5,
    0,
    -1,
    2,
    0,
    2,
    -4,
    5,
    0,
    0,
    -1,
    2,
    -2,
    4,
    0,
    0,
    -2,
    2,
    -1,
    0,
    1,
    0,
    2,
    2,
    -2,
    -2,
    4,
    0,
    0,
    2,
    3,
    -2,
    -1,
    -1,
    0,
    2,
    -2,
    5,
    -2,
    0,
    -1,
    2,
    0,
    -1,
    0,
    -1,
    1,
    2,
    5,
    -2,
    -1,
    1,
    0,
    1,
    1,
    0,
    0,
    0,
    0,
    1,
    -1,
    0,
    0,
    0,
    0,
    1,
    1,
    -2,
    0,
    0,
    0,
    1,
    -2,
    0,
    1,
    0,
    0,
    1,
    1,
    0,
    0,
    1,
    0,
    1,
    -1,
    0,
    0,
    -1,
    0,
    1,
    2,
    0,
    -1,
    0,
    0,
    1,
    0,
    0,
    1,
    0,
    0,
    1,
    3,
    0,
    0,
    0,
    0,
    1,
    -2,
    2,
    -1,
    0,
    0,
    1,
    -2,
    0,
    1,
    -1,
    0,
    1,
    -3,
    2,
    0,
    0,
    0,
    1,
    0,
    0,
    -1,
    0,
    0,
    1,
    1,
    0,
    0,
    -1,
    0,
    1,
    3,
    0,
    0,
    1,
    0,
    1,
    1,
    -3,
    0,
    0,
    1,
    1,
    -3,
    0,
    2,
    0,
    0,
    1,
    1,
    2,
    0,
    0,
    0,
    1,
    0,
    0,
    1,
    1,
    0,
    1,
    2,
    0,
    -1,
    1,
    0,
    1,
    0,
    2,
    -1,
    0,
    0,
    1,
    2,
    -2,
    1,
    0,
    0,
    1,
    3,
    -2,
    0,
    0,
    0,
    1,
    -1,
    2,
    0,
    0,
    0,
    1,
    1,
    1,
    0,
    0,
    -1,
    1,
    1,
    -1,
    0,
    0,
    1,
    1,
    4,
    0,
    -1,
    0,
    0,
    1,
    -4,
    2,
    1,
    0,
    0,
    1,
    0,
    -2,
    1,
    0,
    0,
    1,
    -2,
    2,
    -1,
    -1,
    0,
    1,
    3,
    0,
    -2,
    0,
    0,
    1,
    -1,
    0,
    2,
    0,
    0,
    1,
    -1,
    0,
    0,
    -2,
    0,
    1,
    3,
    0,
    0,
    2,
    0,
    1,
    -3,
    2,
    0,
    -1,
    0,
    1,
    4,
    0,
    -1,
    1,
    0,
    1,
    0,
    0,
    -1,
    -1,
    0,
    1,
    1,
    -2,
    0,
    -1,
    0,
    1,
    -3,
    0,
    2,
    -1,
    0,
    1,
    1,
    0,
    0,
    2,
    0,
    1,
    1,
    -1,
    0,
    0,
    -1,
    1,
    -1,
    -1,
    0,
    0,
    1,
    1,
    0,
    2,
    -1,
    1,
    0,
    1,
    -1,
    1,
    0,
    0,
    -1,
    1,
    -1,
    -2,
    2,
    0,
    0,
    1,
    2,
    -2,
    1,
    1,
    0,
    1,
    -4,
    0,
    3,
    0,
    0,
    1,
    -1,
    2,
    0,
    1,
    0,
    1,
    3,
    -2,
    0,
    1,
    0,
    1,
    2,
    0,
    -1,
    -1,
    0,
    1,
    0,
    0,
    1,
    -1,
    0,
    1,
    -2,
    2,
    1,
    0,
    0,
    1,
    4,
    -2,
    -1,
    0,
    0,
    1,
    -3,
    3,
    0,
    0,
    -1,
    1,
    -2,
    1,
    1,
    0,
    -1,
    1,
    -2,
    3,
    -1,
    0,
    -1,
    1,
    0,
    -2,
    1,
    -1,
    0,
    1,
    -2,
    -1,
    1,
    0,
    1,
    1,
    4,
    -2,
    1,
    0,
    0,
    1,
    -4,
    4,
    -1,
    0,
    0,
    1,
    -4,
    2,
    1,
    -1,
    0,
    1,
    5,
    -2,
    0,
    0,
    0,
    1,
    3,
    0,
    -2,
    1,
    0,
    1,
    -5,
    2,
    2,
    0,
    0,
    1,
    2,
    0,
    1,
    0,
    0,
    1,
    1,
    3,
    0,
    0,
    -1,
    1,
    -2,
    0,
    1,
    -2,
    0,
    1,
    4,
    0,
    -1,
    2,
    0,
    1,
    1,
    -4,
    0,
    0,
    2,
    1,
    5,
    0,
    -2,
    0,
    0,
    1,
    -1,
    0,
    2,
    1,
    0,
    1,
    -2,
    1,
    0,
    0,
    0,
    1,
    4,
    -2,
    1,
    1,
    0,
    1,
    -3,
    4,
    -2,
    0,
    0,
    1,
    -1,
    3,
    0,
    0,
    -1,
    1,
    3,
    -3,
    0,
    0,
    1,
    1,
    5,
    -2,
    0,
    1,
    0,
    1,
    1,
    2,
    0,
    1,
    0,
    1,
    2,
    0,
    1,
    1,
    0,
    1,
    -5,
    4,
    0,
    0,
    0,
    1,
    -2,
    0,
    -1,
    -2,
    0,
    1,
    5,
    0,
    -2,
    1,
    0,
    1,
    1,
    2,
    -2,
    0,
    0,
    1,
    1,
    -2,
    2,
    0,
    0,
    1,
    -2,
    2,
    1,
    1,
    0,
    1,
    0,
    3,
    -1,
    0,
    -1,
    1,
    2,
    -3,
    1,
    0,
    1,
    1,
    -2,
    -2,
    3,
    0,
    0,
    1,
    -1,
    2,
    -2,
    0,
    0,
    1,
    -4,
    3,
    1,
    0,
    -1,
    1,
    -4,
    0,
    3,
    -1,
    0,
    1,
    -1,
    -2,
    2,
    -1,
    0,
    1,
    -2,
    0,
    3,
    0,
    0,
    1,
    4,
    0,
    -3,
    0,
    0,
    1,
    0,
    1,
    1,
    0,
    -1,
    1,
    2,
    -1,
    -1,
    0,
    1,
    1,
    2,
    -2,
    1,
    -1,
    0,
    1,
    0,
    0,
    -1,
    -2,
    0,
    1,
    2,
    0,
    1,
    2,
    0,
    1,
    2,
    -2,
    -1,
    -1,
    0,
    1,
    0,
    0,
    1,
    2,
    0,
    1,
    0,
    1,
    0,
    0,
    0,
    1,
    2,
    -1,
    0,
    0,
    0,
    1,
    0,
    2,
    -1,
    -1,
    0,
    1,
    -1,
    -2,
    0,
    -2,
    0,
    1,
    -3,
    1,
    0,
    0,
    1,
    1,
    3,
    -2,
    0,
    -1,
    0,
    1,
    -1,
    -1,
    0,
    -1,
    1,
    1,
    4,
    -2,
    -1,
    1,
    0,
    1,
    2,
    1,
    -1,
    0,
    -1,
    1,
    0,
    -1,
    1,
    0,
    1,
    1,
    -2,
    4,
    -1,
    0,
    0,
    1,
    4,
    -4,
    1,
    0,
    0,
    1,
    -3,
    1,
    2,
    0,
    -1,
    1,
    -3,
    3,
    0,
    -1,
    -1,
    1,
    1,
    2,
    0,
    2,
    0,
    1,
    1,
    -2,
    0,
    -2,
    0,
    1,
    3,
    0,
    0,
    3,
    0,
    1,
    -1,
    2,
    0,
    -1,
    0,
    1,
    -2,
    1,
    -1,
    0,
    1,
    1,
    0,
    -3,
    1,
    0,
    1,
    1,
    -3,
    -1,
    2,
    0,
    1,
    1,
    2,
    0,
    -1,
    2,
    0,
    1,
    6,
    -2,
    -1,
    0,
    0,
    1,
    2,
    2,
    -1,
    0,
    0,
    1,
    -1,
    1,
    0,
    -1,
    -1,
    1,
    -2,
    3,
    -1,
    -1,
    -1,
    1,
    -1,
    0,
    0,
    0,
    2,
    1,
    -5,
    0,
    4,
    0,
    0,
    1,
    1,
    0,
    0,
    0,
    -2,
    1,
    -2,
    1,
    1,
    -1,
    -1,
    1,
    1,
    -1,
    0,
    1,
    1,
    1,
    1,
    2,
    0,
    0,
    -2,
    1,
    -3,
    1,
    1,
    0,
    0,
    1,
    -4,
    4,
    -1,
    -1,
    0,
    1,
    1,
    0,
    -2,
    -1,
    0,
    1,
    -2,
    -1,
    1,
    -1,
    1,
    1,
    -3,
    2,
    2,
    0,
    0,
    1,
    5,
    -2,
    -2,
    0,
    0,
    1,
    3,
    -4,
    2,
    0,
    0,
    1,
    1,
    -2,
    0,
    0,
    2,
    1,
    -1,
    4,
    -2,
    0,
    0,
    1,
    2,
    2,
    -1,
    1,
    0,
    1,
    -5,
    2,
    2,
    -1,
    0,
    1,
    1,
    -3,
    0,
    -1,
    1,
    1,
    1,
    1,
    0,
    1,
    -1,
    1,
    6,
    -2,
    -1,
    1,
    0,
    1,
    -2,
    2,
    -1,
    -2,
    0,
    1,
    4,
    -2,
    1,
    2,
    0,
    1,
    -6,
    4,
    1,
    0,
    0,
    1,
    5,
    -4,
    0,
    0,
    0,
    1,
    -3,
    4,
    0,
    0,
    0,
    1,
    1,
    2,
    -2,
    1,
    0,
    1,
    -2,
    1,
    0,
    -1,
    0,
    0,
    2,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    -1,
    0,
    0,
    0,
    0,
    2,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    0,
    2,
    0,
    0,
    1,
    0,
    0,
    3,
    0,
    -1,
    0,
    0,
    0,
    1,
    -2,
    1,
    0,
    0,
    0,
    2,
    -2,
    0,
    0,
    0,
    0,
    3,
    0,
    -1,
    1,
    0,
    0,
    0,
    1,
    0,
    0,
    -1,
    0,
    2,
    0,
    -2,
    0,
    0,
    0,
    2,
    0,
    0,
    2,
    0,
    0,
    3,
    -2,
    1,
    0,
    0,
    0,
    1,
    0,
    -1,
    -1,
    0,
    0,
    1,
    0,
    -1,
    1,
    0,
    0,
    4,
    -2,
    0,
    0,
    0,
    0,
    1,
    0,
    1,
    0,
    0,
    0,
    0,
    3,
    0,
    0,
    -1,
    0,
    4,
    0,
    -2,
    0,
    0,
    0,
    3,
    -2,
    1,
    1,
    0,
    0,
    3,
    -2,
    -1,
    0,
    0,
    0,
    4,
    -2,
    0,
    1,
    0,
    0,
    0,
    2,
    0,
    1,
    0,
    0,
    1,
    0,
    1,
    1,
    0,
    0,
    4,
    0,
    -2,
    1,
    0,
    0,
    3,
    0,
    -1,
    2,
    0,
    0,
    5,
    -2,
    -1,
    0,
    0,
    0,
    1,
    2,
    -1,
    0,
    0,
    0,
    1,
    -2,
    1,
    -1,
    0,
    0,
    1,
    -2,
    1,
    1,
    0,
    0,
    2,
    -2,
    0,
    -1,
    0,
    0,
    2,
    -3,
    0,
    0,
    1,
    0,
    2,
    -2,
    0,
    1,
    0,
    0,
    0,
    2,
    -2,
    0,
    0,
    0,
    1,
    -3,
    1,
    0,
    1,
    0,
    0,
    0,
    0,
    2,
    0,
    0,
    0,
    1,
    0,
    0,
    1,
    0,
    1,
    2,
    -1,
    1,
    0,
    0,
    3,
    0,
    -3,
    0,
    0,
    0,
    2,
    1,
    0,
    0,
    -1,
    0,
    1,
    -1,
    -1,
    0,
    1,
    0,
    1,
    0,
    1,
    2,
    0,
    0,
    5,
    -2,
    -1,
    1,
    0,
    0,
    2,
    -1,
    0,
    0,
    1,
    0,
    2,
    2,
    -2,
    0,
    0,
    0,
    1,
    -1,
    0,
    0,
    0,
    0,
    5,
    0,
    -3,
    0,
    0,
    0,
    2,
    0,
    -2,
    1,
    0,
    0,
    1,
    1,
    -1,
    0,
    -1,
    0,
    3,
    -4,
    1,
    0,
    0,
    0,
    0,
    2,
    0,
    2,
    0,
    0,
    2,
    0,
    -2,
    -1,
    0,
    0,
    4,
    -3,
    0,
    0,
    1,
    0,
    3,
    -1,
    -1,
    0,
    1,
    0,
    0,
    2,
    0,
    0,
    -2,
    0,
    3,
    -3,
    1,
    0,
    1,
    0,
    2,
    -4,
    2,
    0,
    0,
    0,
    4,
    -2,
    -2,
    0,
    0,
    0,
    3,
    1,
    -1,
    0,
    -1,
    0,
    5,
    -4,
    1,
    0,
    0,
    0,
    3,
    -2,
    -1,
    -1,
    0,
    0,
    3,
    -2,
    1,
    2,
    0,
    0,
    4,
    -4,
    0,
    0,
    0,
    0,
    6,
    -2,
    -2,
    0,
    0,
    0,
    5,
    0,
    -3,
    1,
    0,
    0,
    4,
    -2,
    0,
    2,
    0,
    0,
    2,
    2,
    -2,
    1,
    0,
    0,
    0,
    4,
    0,
    0,
    -2,
    0,
    3,
    -1,
    0,
    0,
    0,
    0,
    3,
    -3,
    -1,
    0,
    1,
    0,
    4,
    0,
    -2,
    2,
    0,
    0,
    1,
    -2,
    -1,
    -1,
    0,
    0,
    2,
    -1,
    0,
    0,
    -1,
    0,
    4,
    -4,
    2,
    0,
    0,
    0,
    2,
    1,
    0,
    1,
    -1,
    0,
    3,
    -2,
    -1,
    1,
    0,
    0,
    4,
    -3,
    0,
    1,
    1,
    0,
    2,
    0,
    0,
    3,
    0,
    0,
    6,
    -4,
    0,
    0,
    0,
]
IDD = np.array(IDD_FLAT).reshape((342, 6))


def admittance(
    ampin: np.ndarray,
    idtin: np.ndarray,
    phin: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform full admittance interpolation to expand from 11 to 342 constituents.
    Implements the IERS ADMINT algorithm with cubic spline interpolation.

    Converts input amplitude/phase to real/imaginary admittance components,
    performs cubic spline interpolation by frequency band, then converts
    back to amplitude/phase for all 342 constituents.
    """
    NT = 342
    DTR = PI / 180.0

    # Initialize output arrays
    amp_out = np.zeros(NT)
    freq_out = np.zeros(NT)
    phase_out = np.zeros(NT)

    # Batch-compute frequencies and equilibrium phases for all 342 constituents
    freq_all, phase_eq = tidal_frequency_and_phase_batch(IDD)
    freq_out[:] = freq_all

    # Pre-match all input constituents to IDD using broadcasting (vectorized)
    # Shape: (n_input, NT, 6) -> all(axis=2) -> (n_input, NT)
    n_input = len(idtin)
    matches = np.all(idtin[:, None, :] == IDD[None, :, :], axis=2)
    match_idx = np.argmax(matches, axis=1)
    has_match = np.any(matches, axis=1)

    # Get band for each input constituent
    input_bands = idtin[:, 0]

    # Convert input amplitude/phase to real/imaginary admittance (vectorized)
    tamp_vals = np.where(has_match, np.abs(TAMP[match_idx]), 1.0)
    phase_rads = phin * DTR
    input_real = ampin * np.cos(phase_rads) / tamp_vals
    input_imag = ampin * np.sin(phase_rads) / tamp_vals
    input_freq = np.where(has_match, freq_all[match_idx], 0.0)

    # Create spline interpolators for each band and evaluate all constituents
    idd_bands = IDD[:, 0]

    # Apply band-specific phase corrections (vectorized)
    band0_mask = idd_bands == 0
    band1_mask = idd_bands == 1
    band2_mask = idd_bands == 2
    valid_mask = band0_mask | band1_mask | band2_mask

    phase_out[valid_mask] = phase_eq[valid_mask]
    phase_out[band0_mask] += 180.0
    phase_out[band1_mask] += 90.0

    # Process each frequency band
    re_all = np.zeros(NT)
    im_all = np.zeros(NT)

    for band in range(3):
        # Input constituents in this band
        band_input_mask = (input_bands == band) & has_match
        if not np.any(band_input_mask):
            continue

        band_freq = input_freq[band_input_mask]
        band_real = input_real[band_input_mask]
        band_imag = input_imag[band_input_mask]

        # Sort by frequency
        sort_idx = np.argsort(band_freq)
        freq_sorted = band_freq[sort_idx]
        real_sorted = band_real[sort_idx]
        imag_sorted = band_imag[sort_idx]

        # Output constituents in this band
        out_mask = idd_bands == band
        out_freqs = freq_all[out_mask]

        if len(freq_sorted) >= 4:
            # Cubic spline interpolation (batch)
            try:
                z_real = cublic_spline(freq_sorted, real_sorted)
                z_imag = cublic_spline(freq_sorted, imag_sorted)
                re_all[out_mask] = spline_eval_batch(out_freqs, freq_sorted, real_sorted, z_real)
                im_all[out_mask] = spline_eval_batch(out_freqs, freq_sorted, imag_sorted, z_imag)
            except Exception:
                # Fallback to nearest neighbor (vectorized)
                diffs = np.abs(freq_sorted[None, :] - out_freqs[:, None])
                best_idx = np.argmin(diffs, axis=1)
                re_all[out_mask] = real_sorted[best_idx]
                im_all[out_mask] = imag_sorted[best_idx]
        elif len(freq_sorted) > 0:
            # Nearest neighbor (vectorized)
            diffs = np.abs(freq_sorted[None, :] - out_freqs[:, None])
            best_idx = np.argmin(diffs, axis=1)
            re_all[out_mask] = real_sorted[best_idx]
            im_all[out_mask] = imag_sorted[best_idx]

    # Convert back from admittance to amplitude and phase (fully vectorized)
    admittance_mag = np.sqrt(re_all**2 + im_all**2)
    amp_out[valid_mask] = TAMP[valid_mask] * admittance_mag[valid_mask]

    nonzero = valid_mask & (admittance_mag > 0)
    phase_correction = np.arctan2(im_all, re_all) / DTR
    phase_out[nonzero] += phase_correction[nonzero]

    # Normalize phase to [-180, 180] (vectorized)
    phase_out = ((phase_out + 180.0) % 360.0) - 180.0

    return amp_out, freq_out, phase_out


# ==================================================================
# BLQ File Reading
# ==================================================================


def load_ocean_loading_coefficients(filepath: str) -> dict:
    """
    Read BLQ format ocean loading file and extract coefficients for all stations.

    BLQ format (Bos-Scherneck/IERS standard):
    - Comments start with $$
    - Station name on its own line
    - 3 lines of amplitude values (RADIAL, TILT E, TILT N) with 11 constituents each
    - 3 lines of phase values (RADIAL, TILT E, TILT N) with 11 constituents each
    - Columns: M2  S2  N2  K2  K1  O1  P1  Q1  MF  MM  SSA

    Files from the Chalmers loading service may include email-style headers
    (To:, Subject:, From:, Content-type: lines) before the BLQ content.
    Up to 6 leading non-blank, non-$$ lines are automatically skipped.

    Parameters:
        filepath: Path to BLQ file

    Returns:
        Dictionary with station names as keys and (amp_data, phase_data) tuples as values
        where amp_data and phase_data are 3x11 numpy arrays
    """
    stations = {}

    with open(filepath, "r") as f:
        lines = f.readlines()

    # Skip email-style headers that some BLQ files from the Chalmers loading
    # service include at the top (To:, Subject:, From:, Content-type: lines
    # followed by blank lines). A valid BLQ file always starts with blank
    # lines or $$ comments, so any other content in the first 6 lines is
    # treated as a header and skipped.
    i = 0
    while i < min(6, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith("$$"):
            break
        i += 1

    while i < len(lines):
        line = lines[i].strip()
        i += 1

        # Skip empty lines and comments
        if not line or line.startswith("$$"):
            continue

        # This should be a station name (first word of non-comment line)
        station_name = line.split()[0]

        # Skip any comment lines that follow the station name
        while i < len(lines) and lines[i].strip().startswith("$$"):
            i += 1

        # Now we should have 3 amplitude lines and 3 phase lines
        if i + 5 < len(lines):
            try:
                # Read 3 amplitude lines
                amp_lines = []
                for j in range(3):
                    values = [float(x) for x in lines[i + j].split()]
                    amp_lines.append(values)

                # Read 3 phase lines
                phase_lines = []
                for j in range(3):
                    values = [float(x) for x in lines[i + 3 + j].split()]
                    phase_lines.append(values)

                # Convert to numpy arrays
                amp_data = np.array(amp_lines)
                phase_data = np.array(phase_lines)

                # Validate shape
                if amp_data.shape == (3, 11) and phase_data.shape == (3, 11):
                    stations[station_name] = (amp_data, phase_data)

                i += 6
            except (ValueError, IndexError):
                # Skip malformed data
                i += 1

    return stations


# ==================================================================
# Main HARDISP Computer
# ==================================================================


class HardispComputer:
    """Ocean loading calculator for gravity or displacement effects."""

    NL = 600
    NT = 342
    NTIN = 11

    IDT = np.array(
        [
            [2, 0, 0, 0, 0, 0],  # M2
            [2, 2, -2, 0, 0, 0],  # S2
            [2, -1, 0, 1, 0, 0],  # N2
            [2, 2, 0, 0, 0, 0],  # K2
            [1, 1, 0, 0, 0, 0],  # K1
            [1, -1, 0, 0, 0, 0],  # O1
            [1, 1, -2, 0, 0, 0],  # P1
            [1, -2, 0, 1, 0, 0],  # Q1
            [0, 2, 0, 0, 0, 0],  # Mf
            [0, 1, 0, -1, 0, 0],  # Mm
            [0, 0, 2, 0, 0, 0],  # Ssa
        ],
        dtype=int,
    )

    def __init__(self):
        self.tamp = None
        self.tph = None
        self.units = "m"  # Default metadata about coefficient units
        # Datetime stored by compute_ocean_loading()
        self.computation_year = None
        self.computation_month = None
        self.computation_day = None
        self.computation_hour = None
        self.computation_minute = None
        self.computation_second = None
        self.sample_interval = None

    def read_blq_format(self, amp_data, phase_data, units: str = "m") -> None:
        """
        Load 3x11 arrays of amplitudes and phases in BLQ format.

        Input file format (as per Chalmers/IERS BLQ specification):
        Row 0: RADIAL (Vertical/Radial displacement or gravity)
        Row 1: TILT E (East horizontal displacement or gravity component)
        Row 2: TILT N (North horizontal displacement or gravity component)

        Parameters:
            units: Metadata documenting the units of the coefficients.
                   Examples: 'm' (meters), 'nm/s2' (gravity), or any custom string.
                   Stored for reference and used in save_results() for file naming.

        The ocean loading provider determines whether coefficients represent
        displacements or gravity effects. This method loads them as-is.

        Note: Although the Fortran HARDISP.F says "vertical, horizontal EW, horizontal NS",
        the actual hardisp_x64.exe and displacement calculations expect the order to be:
        (Row0→Z, Row2→S, Row1→W) which is reordered to output (Z, S, W).
        This reordering is applied automatically to match the exe output.
        """
        amp_data = np.array(amp_data)
        phase_data = np.array(phase_data)

        # Expect shape (3, 11)
        if amp_data.shape != (3, 11) or phase_data.shape != (3, 11):
            raise ValueError(
                f"Expected shape (3, 11), got amp {amp_data.shape}, phase {phase_data.shape}"
            )

        # Reorder from input (0=Z, 1=W, 2=S) to output (0=Z, 1=S, 2=W)
        # This empirically matches hardisp.exe output to <1% error
        self.tamp = np.array([amp_data[0], amp_data[2], amp_data[1]])
        self.tph = -np.array(
            [phase_data[0], phase_data[2], phase_data[1]]
        )  # Negate for HARDISP convention
        self.units = units  # Store metadata about coefficient units

    def compute_ocean_loading(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        num_epochs: int = 1,
        sample_interval: float = 1.0,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute vertical, south, west ocean loading effects using ADMINT expansion to 342 constituents.

        Always uses full ADMINT expansion to 342 constituents (matches hardisp.exe output).

        Parameters:
            sample_interval: units are seconds
        Returns:
            Tuple of (dz, ds, dw) arrays containing ocean loading effects at each epoch,
            in the native units determined by the ocean loading provider.

        Note: The 'units' metadata is stored from read_blq_format() and is accessible via self.units.
              Datetime parameters are stored for use in save_results().
        """
        if self.tamp is None:
            raise ValueError("Load data with read_blq_format first")

        # Store datetime for save_results() to use
        self.computation_year = year
        self.computation_month = month
        self.computation_day = day
        self.computation_hour = hour
        self.computation_minute = minute
        self.computation_second = second
        self.sample_interval = sample_interval

        doy = day + days_before_month(year, month)
        calculate_tidal_arguments(year, doy, hour, minute, second)

        # Use ADMINT expansion to 342 constituents (matches hardisp.exe)
        amp_342 = []
        phase_arr = []
        freq_arr = None

        # Process each direction: vertical (Z), south (S), west (W)
        for c in range(3):
            a_342, f_342, p_342 = admittance(self.tamp[c], self.IDT.astype(int), self.tph[c])
            amp_342.append(a_342)
            phase_arr.append(p_342)
            if c == 0:
                freq_arr = f_342.copy()

        # Normalize frequencies for recursion
        nf = 342
        f = freq_arr * sample_interval * PI / 43200.0

        # Convert phases to radians
        ph = [p * DR for p in phase_arr]
        amp = amp_342

        # Compute displacements
        dz = np.zeros(num_epochs)
        ds = np.zeros(num_epochs)
        dw = np.zeros(num_epochs)

        # Block processing (same as Fortran)
        irli = 0
        while irli < num_epochs:
            irhi = min(irli + self.NL - 1, num_epochs - 1)
            np_block = irhi - irli + 1

            # Setup harmonic coefficients for recursion (vectorized)
            hc = []
            for c in range(3):
                hc_c = np.zeros(2 * nf)
                cos_ph = np.cos(ph[c])
                sin_ph = np.sin(ph[c])
                hc_c[0::2] = amp[c] * cos_ph
                hc_c[1::2] = -amp[c] * sin_ph
                hc.append(hc_c)

            # Recursion
            dz[irli : irhi + 1] = recursion(np_block, hc[0], nf, f)
            ds[irli : irhi + 1] = recursion(np_block, hc[1], nf, f)
            dw[irli : irhi + 1] = recursion(np_block, hc[2], nf, f)

            # Update phases for next block
            pi2 = 2.0 * PI
            for c in range(3):
                ph[c] = (ph[c] + np_block * f) % pi2

            irli = irhi + 1

        # Output is in native units from the ocean loading coefficients
        return dz, ds, dw

    def save_results(
        self,
        dz: np.ndarray,
        ds: np.ndarray = None,
        dw: np.ndarray = None,
        station_name: str = None,
        output_dir: str = ".",
        prefix: str = "ocean_loading",
    ) -> str:
        """
        Save ocean loading time series results to a CSV file.

        Datetime and units metadata are automatically retrieved from the most recent
        compute_ocean_loading() call and read_blq_format() call respectively.

        Parameters:
            dz: Vertical result array from compute_ocean_loading()
            ds: South result array from compute_ocean_loading() (optional)
            dw: West result array from compute_ocean_loading() (optional)
            station_name: Station identifier to include in output (optional)
            output_dir: Directory to save CSV file (default: current directory)
            prefix: Prefix for output filename (default: "ocean_loading")

        Returns:
            Path to the saved CSV file

        Example:
            computer.read_blq_format(amp_data, phase_data, units="m")
            dz, ds, dw = computer.compute_ocean_loading(year=2018, month=4, day=5)
            ts_file = computer.save_results(dz, ds, dw, station_name="TGKB", output_dir="./results")
        """
        import os

        # Create output directory if it doesn't exist
        if output_dir != "." and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Use units metadata stored from read_blq_format()
        # Convert units to filename-safe format (replace / and spaces with _)
        unit_str = self.units.replace("/", "_").replace(" ", "")

        # Determine component-specific units
        # When units are gravity (nm/s2), vertical is gravity but horizontals are tilts (nrad)
        vertical_units = self.units
        if "nm/s2" in self.units.lower() or "gravity" in self.units.lower():
            horiz_units = "nrad"  # Horizontal tilts in nanoradians
        else:
            horiz_units = self.units  # Same units for all components (e.g., displacement)

        # Time series file
        ts_file = os.path.join(output_dir, f"{prefix}_{unit_str}.csv")
        with open(ts_file, "w", newline="") as f:
            writer = csv.writer(f)

            # Build header row based on which components are provided
            header = []
            if station_name is not None:
                header.append("Station")
            header.extend(["DateTime", f"Vertical ({vertical_units})"])
            if ds is not None:
                header.append(f"South ({horiz_units})")
            if dw is not None:
                header.append(f"West ({horiz_units})")
            writer.writerow(header)

            start_time = datetime(
                self.computation_year,
                self.computation_month,
                self.computation_day,
                self.computation_hour,
                self.computation_minute,
                self.computation_second,
            )
            for i in range(len(dz)):
                current_time = start_time + timedelta(seconds=i * self.sample_interval)

                # Build data row based on which components are provided
                row = []
                if station_name is not None:
                    row.append(station_name)
                row.extend([current_time.isoformat(), f"{dz[i]:.8e}"])
                if ds is not None:
                    row.append(f"{ds[i]:.8e}")
                if dw is not None:
                    row.append(f"{dw[i]:.8e}")
                writer.writerow(row)

        return ts_file
