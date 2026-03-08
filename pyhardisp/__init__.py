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

from .core import (
    HardispComputer,
    is_leap_year,
    days_before_month,
    julian_date,
    doy_to_ymd,
    earth_time_offset_seconds,
    cublic_spline,
    spline_eval,
    spline_eval_batch,
    calculate_tidal_arguments,
    tidal_frequency_and_phase,
    tidal_frequency_and_phase_batch,
    recursion,
    admittance,
    load_ocean_loading_coefficients,
)

__all__ = [
    "HardispComputer",
    "is_leap_year",
    "days_before_month",
    "julian_date",
    "doy_to_ymd",
    "earth_time_offset_seconds",
    "cublic_spline",
    "spline_eval",
    "spline_eval_batch",
    "calculate_tidal_arguments",
    "tidal_frequency_and_phase",
    "tidal_frequency_and_phase_batch",
    "recursion",
    "admittance",
    "load_ocean_loading_coefficients",
]

__version__ = "0.2.1"
