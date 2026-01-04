"""
Quick Start Example: Testing the Binary Quantum Tunneling Endpoint

This example shows how to:
1. Start the FastAPI server
2. Make a request to the binary endpoint
3. Parse the binary response
"""

import requests
import struct
import numpy as np

# Example parameters for quantum tunneling simulation
params = {
    "mass": 1.0,
    "hbar": 1.0,
    "xmin": -6.5,
    "xmax": 6.5,
    "N": 500,
    "momentum": 40.0,
    "sigma": 0.15,
    "x0": -3.0,
    "barrier_start": 0.0,
    "barrier_end": 0.5,
    "dt": 0.001,
    "t_max": 2.0
}

# Make request to the endpoint
print("Sending request to quantum tunneling endpoint...")
response = requests.post(
    "http://localhost:8000/api/quantum-tunneling",
    json=params
)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit(1)

print(f"✅ Response received: {len(response.content)} bytes")
print(f"   Headers: X-Frames={response.headers.get('X-Frames')}, "
      f"X-Grid-Size={response.headers.get('X-Grid-Size')}")

# Parse binary data
binary_data = response.content
offset = 0

# Read header
frame_count = struct.unpack('I', binary_data[offset:offset+4])[0]
offset += 4
grid_size = struct.unpack('I', binary_data[offset:offset+4])[0]
offset += 4

print(f"\n📊 Simulation Info:")
print(f"   Frame count: {frame_count}")
print(f"   Grid size: {grid_size}")

# Read x array
x_bytes = binary_data[offset:offset + grid_size * 4]
x = np.frombuffer(x_bytes, dtype=np.float32)
offset += grid_size * 4

print(f"   X range: [{x[0]:.3f}, {x[-1]:.3f}]")

# Read frames
frames = []
for i in range(frame_count):
    # Read psi_real
    psi_real_bytes = binary_data[offset:offset + grid_size * 4]
    psi_real = np.frombuffer(psi_real_bytes, dtype=np.float32)
    offset += grid_size * 4
    
    # Read psi_imag
    psi_imag_bytes = binary_data[offset:offset + grid_size * 4]
    psi_imag = np.frombuffer(psi_imag_bytes, dtype=np.float32)
    offset += grid_size * 4
    
    # Calculate probability density: |ψ|² = real² + imag²
    probability = psi_real**2 + psi_imag**2
    frames.append(probability)

print(f"\n✅ Parsed {len(frames)} frames successfully")
print(f"   Frame shape: {frames[0].shape}")

# Verify normalization
dx = x[1] - x[0]
sample_frames = [0, frame_count//2, frame_count-1]
print(f"\n🔍 Normalization check (∫|ψ|²dx):")
for i in sample_frames:
    norm = np.sum(frames[i]) * dx
    print(f"   Frame {i}: {norm:.6f}")

print(f"\n✨ Success! Ready to visualize {frame_count} frames.")
print(f"   Total data transferred: {len(binary_data):,} bytes")
print(f"   Single HTTP request - no disk I/O!")

