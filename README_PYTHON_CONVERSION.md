# PYHARDISP - Python Module Documentation

## Overview

This document describes the Python conversion of the **HARDISP** (Harmonic Displacement) Fortran program from the IERS Conventions software collection. The program computes tidal ocean loading displacements at geodetic stations.

## What is HARDISP?

HARDISP is a scientific program developed by the International Earth Rotation and Reference Systems Service (IERS) for calculating tidal ocean loading effects at geodetic stations. Depending on the coefficients provided by the ocean loading provider, it computes either:
- **Tidal displacements** (vertical, horizontal components) - when displacement coefficients are provided
- **Tidal gravity effects** (gravity disturbances) - when gravity-type coefficients are provided

These effects are critical corrections for:

- GPS and space geodesy
- Satellite laser ranging (SLR)
- Very Long Baseline Interferometry (VLBI)
- Superconducting gravimeter measurements
- Hydrogeodetic measurements

The program is part of the **IERS Conventions 2010** recommendations (Class 1 model) for processing raw space geodetic observations.

## Program Purpose

Given ocean loading coefficients in BLQ format (from the Bos-Scherneck loading service or equivalent providers), HARDISP computes a time series of tidal ocean loading effects in three components:

**Output type depends on the ocean loading provider's coefficients:**
- **Displacement coefficients**: Returns displacements
  - **dU**: Vertical (radial) displacement (meters)
  - **dS**: South (North-South) displacement (meters)
  - **dW**: West (East-West) displacement (meters)

- **Gravity coefficients**: Returns gravity effects
  - **dU**: Vertical gravity effect (nm/s² or equivalent units)
  - **dS**: South gravity tilt effect (nm/s²)
  - **dW**: West gravity tilt effect (nm/s²)

The computation uses **342 tidal constituents** derived by spline interpolation of the tidal admittance, providing approximately 0.1% precision.

HARDISP processes the coefficients as-is, with no automatic conversions between displacement and gravity types.

## Files

The Python conversion consists of:
**core.py** - Main Python module with optimized implementation


Original Fortran files (for reference):
- `HARDISP.F` - Main program
- `ADMINT.F` - Admittance interpolation
- `RECURS.F` - Recursive harmonic evaluation
- `TDFRPH.F` - Tidal frequency and phase calculation
- `SPLINE.F`, `EVAL.F` - Cubic spline interpolation
- `TOYMD.F`, `LEAP.F`, `JULDAT.F`, `MDAY.F` - Date/time utilities
- `ETUTC.F` - ET-UTC offset calculation
- `SHELLS.F` - Shell sort algorithm

## Key Functions Reference

### Date/Time Conversion Functions

```python
import hardisp

# Check if a year is a leap year
is_leap = pyhardisp.is_leap_year(2008)  # Returns 1 for true, 0 for false

# Get days before start of month
days_before_may = pyhardisp.days_before_month(2009, 5)  # Returns 120

# Convert to Julian Day Number
jd = pyhardisp.julian_date(2000, 1, 1)  # Returns 2451545 (J2000.0)

# Convert day-of-year to month/day
y, m, d = pyhardisp.doy_to_ymd(2008, 120)  # Returns (2008, 4, 29)

# Get ET-UTC offset for decimal year
delta = pyhardisp.earth_time_offset_seconds(2009.5)  # Returns difference in seconds
```

### Tidal Calculations

```python
# Set the epoch for tidal calculations
pyhardisp.calculate_tidal_arguments(year=2009, day_of_year=176, hour=0, minute=0, second=0)

# Get frequency and phase of a tidal constituent
import numpy as np
doodson = np.array([2, 0, 0, 0, 0, 0])  # M2 tide
freq, phase = pyhardisp.tidal_frequency_and_phase(doodson)
```

### Main Class: HardispComputer

```python
# Create a computer instance
computer = hardisp.HardispComputer()

# Load BLQ-format ocean loading coefficients
# Two methods:

# Method 1: From numpy arrays (3x11 each)
amp_data = [[0.00352, 0.00123, ...], [0.00144, ...], [0.00086, ...]]
phase_data = [[-64.7, -52.0, ...], [85.5, ...], [109.5, ...]]
computer.read_blq_format(amp_data, phase_data)

# Method 2: From BLQ text file (6 lines)
with open('station.blq', 'r') as f:
    lines = f.readlines()
    computer.read_blq_format(lines[:3], lines[3:])

# Compute ocean loading effects
dz, ds, dw = computer.compute_ocean_loading(
    year=2009, month=6, day=25,
    hour=1, minute=10, second=45,
    num_epochs=24,           # Number of time points
    sample_interval=3600.0   # Seconds between points
)

# Output units depend on input coefficients from the ocean loading provider
# Pass units as metadata to document what you expect (doesn't affect computation)
print(f"Vertical: {dz}")
print(f"South: {ds}")
print(f"West: {dw}")
```

## Usage Examples

### Example 1: Simple Time Series

```python
import pyhardisp
import numpy as np

# Create computer instance
computer = pyhardisp.HardispComputer()

# Load BLQ ocean loading coefficients
amplitudes = [
    [45.96, 10.98, 6.94, 3.07, 6.00, 1.57, 1.98, 0.91, 1.58, 0.73, 0.41],  # Vertical
    [99.00, 14.68, 21.49, 4.16, 2.67, 2.80, 0.86, 1.03, 0.02, 0.00, 0.01],  # East
    [38.30, 11.46, 8.92, 3.17, 7.47, 4.96, 2.46, 0.97, 1.06, 0.63, 0.52],  # North
]
phases = [
    [53.3, 137.3, 22.4, 135.1, -171.3, 21.5, -170.7, 42.9, -3.6, -8.3, -4.3],
    [140.1, 174.5, 123.5, 159.1, 167.5, 93.9, 168.8, 65.9, -47.8, -49.7, 15.5],
    [-109.9, -78.7, -133.4, -85.9, 28.6, 12.2, 28.1, 16.0, 14.1, 8.0, 1.5],
]

computer.read_blq_format(amplitudes, phases, units="nm/s^2")

# Compute 24 hourly displacements
dz, ds, dw = computer.compute_ocean_loading(
    year=2009, month=6, day=25,
    hour=1, minute=10, second=45,
    num_epochs=24,
    sample_interval=3600.0
)

print("Vertical gravity (nm/s^2):", dz)
print("South tilt (nrad):   ", ds)
print("West tilt (nrad):    ", dw)
```

### Example 2: High-Rate Analysis

```python
# For 1Hz sampling (e.g., seismic or structural monitoring)
dz_high, ds_high, dw_high = computer.compute_ocean_loading(
    year=2009, month=6, day=25,
    hour=1, minute=0, second=0,
    num_epochs=86400,      # Full day at 1Hz
    sample_interval=1.0    # 1 second intervals
)
```

### Example 3: Multi-Day Campaign

```python
# Process multiple days
for day_val in range(1, 8):  # Process days 1-7
    dz, ds, dw = computer.compute_ocean_loading(
        year=2009, month=6, day=day_val,
        num_epochs=1, sample_interval=1
    )
    print(f"June {day_val}: max effect = {max(abs(dz), abs(ds), abs(dw)):.6f}")
```

## Technical Details

### Coordinate System

The output displacements are in a **local geodetic frame** at the station:
- **dU**: Radial (positive upward)
- **dS**: South component (positive southward, i.e., negative latitude direction)
- **dW**: West component (positive westward, i.e., negative longitude direction)

### Tidal Constituents Used

The 11 input harmonics (from BLQ format) represent:
1. M₂ - Principal lunar semi-diurnal (12.42 hours)
2. S₂ - Principal solar semi-diurnal (12.00 hours)
3. N₂ - Lunar elliptic semi-diurnal (12.66 hours)
4. K₂ - Lunisolar semi-diurnal (11.97 hours)
5. K₁ - Lunisolar diurnal (23.93 hours)
6. O₁ - Principal lunar diurnal (25.82 hours)
7. P₁ - Principal solar diurnal (24.07 hours)
8. Q₁ - Larger lunar elliptic diurnal (26.87 hours)
9. Mf - Lunar fortnightly (13.66 days)
10. Mm - Lunar monthly (27.55 days)
11. Ssa - Solar semi-annual (182.6 days)

These are expanded to 342 constituents through spline interpolation for higher precision.

### Recursion Algorithm

The program uses **Chebyshev polynomial recursion** for efficient computation of harmonic series:

Instead of computing: `x(t) = Σ A cos(ωt) + B sin(ωt)`

It uses: `x(j) = 2cos(ω)·x(j-1) - x(j-2)`

This requires only 2-3 operations per harmonic per time point, making it orders of magnitude faster than direct calculations, especially for large numbers of epochs.

## Conversion Notes

### Key Differences from Fortran

1. **Integer Division**: Fortran's division truncates toward zero, while Python's `//` uses floor division. The code uses `fortran_int_divide()` function to maintain Fortran semantics.

2. **Matrix Indexing**: Fortran uses 1-based indexing; Python uses 0-based. Conversions are handled automatically.

3. **Floating Point**: Results may differ slightly due to different floating-point implementations and optimization levels.

4. **Object-Oriented**: The Python version uses a class-based interface (`HardispComputer`) rather than standalone FORTRAN procedures.

## Original Fortran Files (Reference)

The Python code was converted from these 13 Fortran files:

1. `HARDISP.F` (465 lines) - Main program
2. `ADMINT.F` (449 lines) - Ocean loading interpolation
3. `RECURS.F` (180 lines) - Recursive harmonic evaluation
4. `TDFRPH.F` (281 lines) - Frequency and phase calculation
5. `SPLINE.F` (215 lines) - Spline setup
6. `EVAL.F` (197 lines) - Spline evaluation
7. `TOYMD.F` (160 lines) - Date conversion
8. `MDAY.F` (155 lines) - Month/day calculation
9. `LEAP.F` (154 lines) - Leap year check
10. `JULDAT.F` (159 lines) - Julian date
11. `SHELLS.F` (210 lines) - Shell sort
12. `ETUTC.F` (284 lines) - ET-UTC calculation
13. `TOYS.F` - (not in workspace but referenced)


## Function Name Mapping (Original Fortran → New Python)

| Original Fortran | New Python Name | Purpose |
|------------------|-----------------|----------|
| LEAP | is_leap_year | Check leap year status |
| MDAY | days_before_month | Days before month start |
| JULDAT | julian_date | Convert to Julian Day Number |
| TOYMD | doy_to_ymd | Convert day-of-year to month/day |
| ETUTC | earth_time_offset_seconds | ET-UTC offset calculation |
| SPLINE | cublic_spline | Compute cubic spline coefficients |
| EVAL | spline_eval | Evaluate spline at point |
| — | spline_eval_batch | Evaluate spline at multiple points (vectorized) |
| SET_TIDAL_DATE | calculate_tidal_arguments | Initialize tidal calculations |
| TDFRPH | tidal_frequency_and_phase | Get frequency and phase |
| — | tidal_frequency_and_phase_batch | Get frequencies/phases for multiple constituents (vectorized) |
| RECURS | recursion | Recursive harmonic evaluation |
| ADMINT | admittance | Admittance interpolation |
| SHELLS | pyshells | Shell sort array indices |
| int_div (helper) | fortran_int_divide | Fortran-style integer division |

## Features Implemented

### Complete Conversion
- [x] All 342 tidal constituents support
- [x] Recursive harmonic evaluation (efficient)
- [x] Cubic spline interpolation
- [x] Tidal admittance calculation
- [x] BLQ format input/output
- [x] Julian date calculations
- [x] ET-UTC offset (with leap seconds through 2017)
- [x] Doodson number computations
- [x] Delaunay argument calculations

### Additional Features
- [x] Object-oriented design with HardispComputer class
- [x] NumPy integration for high performance
- [x] Comprehensive error handling
- [x] Detailed documentation and docstrings
- [x] Test cases and validation
- [x] Performance optimizations

## Core Components Converted

### 1. Date/Time Functions (7 functions)
```
✓ is_leap_year(year) - Check leap year
✓ days_before_month(year, month) - Days before month start
✓ julian_date(year, month, day) - Convert to Julian date
✓ doy_to_ymd(year, day_of_year) - Convert to month/day
✓ earth_time_offset_seconds(year) - ET-UTC offset calculation
```

### 2. Spline Interpolation (3 functions)
```
✓ cublic_spline(x, u) - Compute cubic spline coefficients
✓ spline_eval(y, x, u, s) - Evaluate spline at point
✓ spline_eval_batch(y_arr, x, u, s) - Evaluate spline at multiple points (vectorized)
```

### 3. Tidal Frequency Calculations (3 functions)
```
✓ calculate_tidal_arguments(year, day, h, m, s) - Initialize tidal calculations
✓ tidal_frequency_and_phase(doodson_number) - Get frequency and phase from Doodson number
✓ tidal_frequency_and_phase_batch(doodson_array) - Get frequencies and phases for multiple constituents (vectorized)
```

### 4. Harmonic Recursion (1 function)
```
✓ recursion(n, hc, nf, om) - Efficient recursive harmonic evaluation
```

### 5. Utility Functions (2 functions)
```
✓ pyshells(x) - Sort array with indices (Shell sort)
✓ fortran_int_divide(a, b) - Fortran-style integer division
```

### 6. Main Class: HardispComputer
```
✓ read_blq_format(amp, phase) - Load ocean loading coefficients
✓ compute_ocean_loading(...) - Main computation engine
```



## References

1. Petit, G. and Luzum, B. (eds.), **IERS Conventions (2010)**, IERS Technical Note No. 36, BKG (2010)
   - Available at: https://www.iers.org/IERS/EN/Publications/TechnicalNotes/tn36.php

2. Agnew, D. C., et al., **HARDISP**: Original algorithm and implementation

3. Scherneck, H.-G., and M. S. Bos, **Ocean Loading Service**: BLQ format specification
   - Available at: http://www.oso.chalmers.se/~loading/

4. Cartwright, D. E., and A. C. Edden, **Tides of the Planet Earth**, Geophys. J. R. Astron. Soc. 65, 615-630, 1981

## License

This Python conversion maintains the same IERS Conventions Software License as the original Fortran code. See copyright notices in source files.

## Contact

For questions or issues with the Fortran original:
- IERS Conventions Center: https://www.iers.org/
- Email: gpetit@bipm.org or brian.luzum@usno.navy.mil

---

*Python conversion completed: 2024*  
*Original Fortran: IERS Conventions 2010*
