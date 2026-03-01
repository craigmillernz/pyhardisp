# Copyright (c) 2026 Earth Sciences New Zealand.

#!/usr/bin/env python3
"""Test the new read_BLQ_from_file function"""

import pyhardisp
import csv
from datetime import datetime, timedelta

# Read the BLQ file
stations = pyhardisp.load_ocean_loading_coefficients(r"./OL_FES2004_gravity_nms2.dat")

print(f"Found {len(stations)} stations: {list(stations.keys())}\n")

# Collect results from all stations
all_results = []
units_str = None

# Process each station
for station_name, (amp_data, phase_data) in stations.items():
    print(f"=== {station_name} ===")

    # Compute ocean loading effects for this station
    computer = pyhardisp.HardispComputer()
    computer.read_blq_format(amp_data, phase_data, units="nm/s2")

    dz, _, _ = computer.compute_ocean_loading(
        year=2018,
        month=4,
        day=5,
        hour=0,
        minute=32,
        second=30,
        num_epochs=10,
        sample_interval=10,
    )
    print(f"  Vertical (gravity): {dz} {computer.units}")

    # Store results for this station
    for i in range(len(dz)):
        all_results.append(
            {
                "station": station_name,
                "dz": dz[i],
                "year": computer.computation_year,
                "month": computer.computation_month,
                "day": computer.computation_day,
                "hour": computer.computation_hour,
                "minute": computer.computation_minute,
                "second": computer.computation_second,
                "sample_interval": computer.sample_interval,
                "epoch_index": i,
            }
        )
    units_str = computer.units

# Save all results to a single CSV file
print("\nSaving all stations to single CSV file...")
output_dir = "."
unit_str_safe = units_str.replace("/", "_").replace(" ", "")
results_file = f"{output_dir}ocean_loading_{unit_str_safe}.csv"

with open(results_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Station", "DateTime", "Vertical (nm/s2)"])

    for result in all_results:
        dt = datetime(
            result["year"],
            result["month"],
            result["day"],
            result["hour"],
            result["minute"],
            result["second"],
        ) + timedelta(seconds=result["epoch_index"] * result["sample_interval"])

        writer.writerow([result["station"], dt.isoformat(), f"{result['dz']:.8e}"])

print(f"✓ Saved: {results_file}")
