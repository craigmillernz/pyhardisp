# Copyright (c) 2026 Earth Sciences New Zealand.

#!/usr/bin/env python3
"""
Test suite to verify renamed functions work correctly.
Tests the IERS HARDISP Python conversion with renamed functions for IERS license compliance.
"""

import numpy as np
import pytest
import tempfile
import os
import csv
import pyhardisp
from pyhardisp.core import fortran_int_divide


class TestUtilityFunctions:
    """Test utility and helper functions."""

    def test_fortran_int_divide(self):
        """Test fortran_int_divide() function."""
        # Test basic integer division
        assert fortran_int_divide(7, 2) == 3, "7/2 should be 3"
        assert fortran_int_divide(-7, 2) == -3, "-7/2 should be -3"
        assert fortran_int_divide(10, 3) == 3, "10/3 should be 3"
        assert fortran_int_divide(0, 5) == 0, "0/5 should be 0"

    def test_fortran_int_divide_large_numbers(self):
        """Test fortran_int_divide() with large numbers."""
        assert fortran_int_divide(1000000, 3) == 333333
        assert fortran_int_divide(12345, 67) == 184


class TestDateFunctions:
    """Test date/time conversion functions."""

    def test_is_leap_year(self):
        """Test is_leap_year() function."""
        assert pyhardisp.is_leap_year(2008) == 1, "2008 should be leap year"
        assert pyhardisp.is_leap_year(2009) == 0, "2009 should not be leap year"

    def test_days_before_month(self):
        """Test days_before_month() function."""
        days_may = pyhardisp.days_before_month(2009, 5)
        assert days_may == 120, f"Days before May 2009 should be 120, got {days_may}"

    def test_julian_date(self):
        """Test julian_date() function."""
        jd = pyhardisp.julian_date(2000, 1, 1)
        assert jd == 2451545, f"Julian date for 2000-01-01 should be 2451545, got {jd}"

    def test_doy_to_ymd(self):
        """Test doy_to_ymd() function."""
        y, m, d = pyhardisp.doy_to_ymd(2008, 120)
        assert (y, m, d) == (2008, 4, 29), (
            f"DOY 120 of 2008 should be 2008-04-29, got {y}-{m:02d}-{d:02d}"
        )

    def test_earth_time_offset_seconds(self):
        """Test earth_time_offset_seconds() function."""
        offset = pyhardisp.earth_time_offset_seconds(2009.5)
        assert 64 <= offset <= 68, f"ET-UTC offset for 2009.5 should be ~65-67, got {offset}"


class TestSplineFunctions:
    """Test spline interpolation functions."""

    def test_cublic_spline(self):
        """Test cublic_spline() function."""
        x = np.array([0.0, 1.0, 2.0, 3.0])
        u = np.array([0.0, 1.0, 0.0, 1.0])
        s = pyhardisp.cublic_spline(x, u)
        assert len(s) == len(u), f"Spline coefficients length should match input"

    def test_spline_eval(self):
        """Test spline_eval() function."""
        x = np.array([0.0, 1.0, 2.0, 3.0])
        u = np.array([0.0, 1.0, 0.0, 1.0])
        s = pyhardisp.cublic_spline(x, u)
        y_eval = pyhardisp.spline_eval(0.5, x, u, s)
        assert isinstance(y_eval, (float, np.floating)), f"Spline eval should return float"


class TestTidalFunctions:
    """Test tidal calculation functions."""

    def test_calculate_tidal_arguments(self):
        """Test calculate_tidal_arguments() function."""
        result = pyhardisp.calculate_tidal_arguments(2000, 1, 12, 0, 0)
        # calculate_tidal_arguments() returns None (stores data globally in _tidal)
        assert result is None, f"calculate_tidal_arguments should return None, got {type(result)}"

    def test_tidal_frequency_and_phase(self):
        """Test tidal_frequency_and_phase() function."""
        doodson = np.array([2, 0, 0, 0, 0, 0])  # M2 tide
        freq, phase = pyhardisp.tidal_frequency_and_phase(doodson)
        assert isinstance(freq, (float, np.floating)), "Frequency should be float"
        assert isinstance(phase, (float, np.floating)), "Phase should be float"


class TestHarmonics:
    """Test harmonic recursion function."""

    def test_recursion(self):
        """Test recursion() function."""
        n = 5
        hc = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        nf = 2
        om = np.array([0.1, 0.2])
        result = pyhardisp.recursion(n, hc, nf, om)
        assert len(result) == n, f"Result should have length {n}"


class TestOceanLoading:
    """Test ocean loading functions."""

    @pytest.fixture
    def hardisp_computer(self):
        """Create a HardispComputer instance with test coefficients."""
        computer = pyhardisp.HardispComputer()
        amp_data = np.array(
            [
                [
                    0.00352,
                    0.00123,
                    0.00080,
                    0.00032,
                    0.00187,
                    0.00112,
                    0.00063,
                    0.00003,
                    0.00082,
                    0.00044,
                    0.00037,
                ],
                [
                    0.00144,
                    0.00035,
                    0.00035,
                    0.00008,
                    0.00053,
                    0.00049,
                    0.00018,
                    0.00009,
                    0.00012,
                    0.00005,
                    0.00006,
                ],
                [
                    0.00086,
                    0.00023,
                    0.00023,
                    0.00006,
                    0.00029,
                    0.00028,
                    0.00010,
                    0.00007,
                    0.00004,
                    0.00002,
                    0.00001,
                ],
            ]
        )
        phase_data = np.array(
            [
                [-64.7, -52.0, -96.2, -55.2, -58.8, -151.4, -65.6, -138.1, 8.4, 5.2, 2.1],
                [85.5, 114.5, 56.5, 113.6, 99.4, 19.1, 94.1, -10.4, -167.4, -170.0, -177.7],
                [109.5, 147.0, 92.7, 148.8, 50.5, -55.1, 36.4, -170.4, -15.0, 2.3, 5.2],
            ]
        )
        computer.read_blq_format(amp_data, phase_data)
        return computer

    def test_read_blq_format(self, hardisp_computer):
        """Test read_blq_format() function."""
        assert hardisp_computer.units == "m", (
            f"Default units should be 'm', got {hardisp_computer.units}"
        )

    def test_compute_ocean_loading(self, hardisp_computer):
        """Test compute_ocean_loading() function."""
        dz, ds, dw = hardisp_computer.compute_ocean_loading(
            year=2009,
            month=6,
            day=25,
            hour=1,
            minute=10,
            second=45,
            num_epochs=1,
            sample_interval=3600.0,
        )
        assert len(dz) == 1, "Should return 1 epoch"
        assert len(ds) == 1, "Should return 1 epoch"
        assert len(dw) == 1, "Should return 1 epoch"
        assert isinstance(dz[0], (float, np.floating)), "dz should be float"
        # Verify computed values are reasonable ocean loading magnitudes
        assert -0.01 < dz[0] < 0.01, "Vertical displacement should be small"

    def test_read_blq_format_with_units(self):
        """Test read_blq_format() with different unit specifications."""
        computer = pyhardisp.HardispComputer()
        amp_data = np.array(
            [
                [
                    0.00352,
                    0.00123,
                    0.00080,
                    0.00032,
                    0.00187,
                    0.00112,
                    0.00063,
                    0.00003,
                    0.00082,
                    0.00044,
                    0.00037,
                ],
                [
                    0.00144,
                    0.00035,
                    0.00035,
                    0.00008,
                    0.00053,
                    0.00049,
                    0.00018,
                    0.00009,
                    0.00012,
                    0.00005,
                    0.00006,
                ],
                [
                    0.00086,
                    0.00023,
                    0.00023,
                    0.00006,
                    0.00029,
                    0.00028,
                    0.00010,
                    0.00007,
                    0.00004,
                    0.00002,
                    0.00001,
                ],
            ]
        )
        phase_data = np.array(
            [
                [-64.7, -52.0, -96.2, -55.2, -58.8, -151.4, -65.6, -138.1, 8.4, 5.2, 2.1],
                [85.5, 114.5, 56.5, 113.6, 99.4, 19.1, 94.1, -10.4, -167.4, -170.0, -177.7],
                [109.5, 147.0, 92.7, 148.8, 50.5, -55.1, 36.4, -170.4, -15.0, 2.3, 5.2],
            ]
        )
        computer.read_blq_format(amp_data, phase_data, units="nm/s2")
        assert computer.units == "nm/s2", "Units should be nm/s2"

    def test_compute_ocean_loading_multiple_epochs(self, hardisp_computer):
        """Test compute_ocean_loading() with multiple epochs."""
        dz, ds, dw = hardisp_computer.compute_ocean_loading(
            year=2009,
            month=6,
            day=25,
            hour=0,
            minute=0,
            second=0,
            num_epochs=24,
            sample_interval=3600.0,
        )
        assert len(dz) == 24, "Should return 24 epochs"
        assert len(ds) == 24, "Should return 24 epochs"
        assert len(dw) == 24, "Should return 24 epochs"

    def test_save_results(self, hardisp_computer):
        """Test save_results() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Compute some results
            dz, ds, dw = hardisp_computer.compute_ocean_loading(
                year=2009,
                month=6,
                day=25,
                hour=0,
                minute=0,
                second=0,
                num_epochs=2,
                sample_interval=3600.0,
            )

            # Save results
            output_file = hardisp_computer.save_results(
                dz, ds, dw, station_name="TESTSTAT", output_dir=tmpdir, prefix="test"
            )

            # Verify file was created
            assert os.path.exists(output_file), f"Output file {output_file} should exist"

            # Verify CSV content
            with open(output_file, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2, "Should have 2 data rows"
                assert "Station" in rows[0], "Should have Station column"
                assert "Vertical (m)" in rows[0], "Should have Vertical column"


class TestLoadOceanLoadingCoefficients:
    """Test load_ocean_loading_coefficients() function."""

    def test_load_ocean_loading_coefficients_valid_file(self):
        """Test load_ocean_loading_coefficients() with valid BLQ file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".blq", delete=False) as f:
            # Write a valid BLQ format file (phase data must immediately follow amplitude)
            f.write("$$ Test BLQ file\n")
            f.write("TESTSTAT\n")
            f.write(
                "0.0035 0.0012 0.0008 0.0003 0.0019 0.0011 0.0006 0.0000 0.0008 0.0004 0.0004\n"
            )
            f.write(
                "0.0014 0.0004 0.0004 0.0001 0.0005 0.0005 0.0002 0.0001 0.0001 0.0001 0.0001\n"
            )
            f.write(
                "0.0009 0.0002 0.0002 0.0001 0.0003 0.0003 0.0001 0.0001 0.0000 0.0000 0.0000\n"
            )
            f.write("-65.0 -52.0 -96.0 -55.0 -59.0 -151.0 -66.0 -138.0 8.0 5.0 2.0\n")
            f.write("86.0 115.0 57.0 114.0 99.0 19.0 94.0 -10.0 -167.0 -170.0 -178.0\n")
            f.write("110.0 147.0 93.0 149.0 51.0 -55.0 36.0 -170.0 -15.0 2.0 5.0\n")
            f.write("STATION2\n")
            f.write(
                "0.0040 0.0013 0.0009 0.0004 0.0020 0.0012 0.0007 0.0001 0.0009 0.0005 0.0005\n"
            )
            f.write(
                "0.0015 0.0005 0.0005 0.0002 0.0006 0.0006 0.0003 0.0002 0.0002 0.0001 0.0001\n"
            )
            f.write(
                "0.0010 0.0003 0.0003 0.0002 0.0004 0.0004 0.0002 0.0001 0.0001 0.0000 0.0001\n"
            )
            f.write("-60.0 -50.0 -90.0 -50.0 -54.0 -146.0 -61.0 -133.0 3.0 0.0 -3.0\n")
            f.write("91.0 120.0 62.0 119.0 104.0 24.0 99.0 -5.0 -162.0 -165.0 -173.0\n")
            f.write("115.0 152.0 98.0 154.0 56.0 -50.0 41.0 -165.0 -10.0 7.0 10.0\n")
            temp_path = f.name

        try:
            # Load coefficients
            stations = pyhardisp.load_ocean_loading_coefficients(temp_path)

            # Verify structure
            assert "TESTSTAT" in stations, "Should have TESTSTAT"
            assert "STATION2" in stations, "Should have STATION2"
            assert len(stations) == 2, "Should have 2 stations"

            # Verify data shape and values
            amp_data, phase_data = stations["TESTSTAT"]
            assert amp_data.shape == (3, 11), "Amplitude data should be 3x11"
            assert phase_data.shape == (3, 11), "Phase data should be 3x11"
            assert amp_data[0, 0] == pytest.approx(0.0035), "First amplitude value should match"
            assert phase_data[0, 0] == pytest.approx(-65.0), "First phase value should match"
        finally:
            os.unlink(temp_path)

    def test_load_ocean_loading_coefficients_station_names(self):
        """Test that load_ocean_loading_coefficients() correctly extracts station names."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".blq", delete=False) as f:
            f.write("$$ BLQ file with two stations\n")
            f.write("STAT_A\n")
            # Write dummy data (3 amplitude lines, 3 phase lines)
            for _ in range(6):
                f.write(" ".join(["0.001"] * 11) + "\n")
            f.write("STAT_B\n")
            for _ in range(6):
                f.write(" ".join(["0.001"] * 11) + "\n")
            temp_path = f.name

        try:
            stations = pyhardisp.load_ocean_loading_coefficients(temp_path)
            assert "STAT_A" in stations, "Station A should be loaded"
            assert "STAT_B" in stations, "Station B should be loaded"
        finally:
            os.unlink(temp_path)

    def test_load_ocean_loading_coefficients_with_email_header(self):
        """Test that load_ocean_loading_coefficients() skips email-style headers."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".blq", delete=False) as f:
            # Write email header (4 lines + 2 blank lines)
            f.write("To: x.surname@gns.cri.nz\n")
            f.write("Subject: Ocean loading values results\n")
            f.write("From: barre.loading@chalmers.se\n")
            f.write("Content-type: text/plain\n")
            f.write("\n")
            f.write("\n")
            # Normal BLQ content
            f.write("$$ Ocean loading coefficients\n")
            f.write("STAT_A\n")
            for _ in range(6):
                f.write(" ".join(["0.001"] * 11) + "\n")
            temp_path = f.name

        try:
            stations = pyhardisp.load_ocean_loading_coefficients(temp_path)
            assert "STAT_A" in stations, "Station A should be loaded from file with email header"
            amp_data, phase_data = stations["STAT_A"]
            assert amp_data.shape == (3, 11), "Amplitude data should be 3x11"
        finally:
            os.unlink(temp_path)


class TestAdmittance:
    """Test admittance interpolation function."""

    def test_admittance(self):
        """Test admittance() function expansion from 11 to 342 constituents."""
        # Test data (11 input constituents)
        ampin = np.array(
            [
                0.00352,
                0.00123,
                0.00080,
                0.00032,
                0.00187,
                0.00112,
                0.00063,
                0.00003,
                0.00082,
                0.00044,
                0.00037,
            ]
        )

        # Doodson numbers for the 11 constituents
        idtin = np.array(
            [
                [2, 0, 0, 0, 0, 0],  # M2
                [2, 2, -2, 0, 0, 0],  # S2
                [2, -1, 0, 1, 0, 0],  # N2
                [2, 2, 0, 0, 0, 0],  # K2
                [1, 1, 0, 0, 0, 0],  # K1
                [1, -1, 0, 0, 0, 0],  # O1
                [1, 1, -2, 0, 0, 0],  # P1
                [1, -2, 0, 1, 0, 0],  # Q1
                [0, 1, 0, 0, 0, 0],  # Mf
                [0, 0, 1, 0, 0, 0],  # Mm
                [0, 2, 0, 0, 0, 0],  # Ssa
            ]
        )

        phin = np.array([-64.7, -52.0, -96.2, -55.2, -58.8, -151.4, -65.6, -138.1, 8.4, 5.2, 2.1])

        amp_out, freq_out, phase_out = pyhardisp.admittance(ampin, idtin, phin)

        assert len(amp_out) == 342, f"Should expand to 342 constituents, got {len(amp_out)}"
        assert len(freq_out) == 342, "freq_out should have 342 elements"
        assert len(phase_out) == 342, "phase_out should have 342 elements"
