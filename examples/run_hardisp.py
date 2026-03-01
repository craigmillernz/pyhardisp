# Copyright (c) 2026 Earth Sciences New Zealand.

import pyhardisp
import numpy as np

# Load BLQ ocean loading coefficients
# From TGM01_nms2.dat Te Maari
# units are in nm/s^2, nrad, nrad for amplitudes and degrees for phases
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


computer = pyhardisp.HardispComputer()
computer.read_blq_format(amplitudes, phases, units="nm/s2")

# Ocean loading effects (using ADMINT, 342 constituents)
dz, ds, dw = computer.compute_ocean_loading(
    year=2018,
    month=4,
    day=5,
    hour=0,
    minute=32,
    second=30,
    num_epochs=10,
    sample_interval=10,
)

# Ocean loading gravity in nm/s^2
# %%
print(f"Vertical: {dz[0]:.5f} nm/s^2")  # Output: -44.7 nm/s^2
print(f"South: {ds[0]:.5f} nrad")  # Output: -294.2 nm/s^2
print(f"West: {dw[0]:.5f} nrad")  # Output: 496.8 nm/s^2


# %%
# Save results to CSV file using the built-in method
print("\nSaving results to CSV file...")
results_file = computer.save_results(
    dz,
    ds,
    dw,
    output_dir=".",
    prefix="ocean_loading",
)

print(f"✓ Saved: {results_file}")

# %%
