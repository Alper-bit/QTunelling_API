"""
Physics calculation module
Add your physics simulation logic here
"""
from typing import Dict, Any, List, Optional
import numpy as np
import struct
from io import BytesIO

def calculate_simulation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main physics calculation function
    
    Args:
        data: Input data dictionary
        
    Returns:
        Dictionary containing calculated results
    """
    # TODO: Implement your physics calculations here
    # Example placeholder:
    result = {
        "calculated": True,
        "input_received": data
    }
    
    return result

def quantum_tunneling_simulation_binary(
    mass: float = 1.0,
    hbar: float = 1.0,
    xmin: float = -6.5,
    xmax: float = 6.5,
    N: int = 1000,
    momentum: float = 40.0,
    sigma: float = 0.15,
    x0: float = -3.0,
    barrier_start: float = 0.0,
    barrier_end: float = 0.5,
    dt: float = 0.001,
    t_max: float = 2.0,
    num_time_steps: Optional[int] = None,
    max_frames: int = 500
) -> bytes:
    """
    Quantum wave packet scattering simulation - returns binary data
    
    Returns the entire simulation as a single binary payload with the format:
    - HEADER: uint32 frame_count, uint32 grid_size (N)
    - DATA: float32 x[N] array
    - FRAMES: For each frame: float32 psi_real[N], float32 psi_imag[N]
    
    Args:
        mass: Particle mass
        hbar: Reduced Planck constant
        xmin, xmax: Spatial grid boundaries
        N: Number of grid points (interior points for wavefunction)
        momentum: Initial momentum
        sigma: Gaussian width
        x0: Initial position (should be left of barrier for scattering)
        barrier_start, barrier_end: Potential barrier boundaries
        dt: Time step
        t_max: Maximum simulation time
        num_time_steps: Number of time steps (if None, calculated from dt and t_max)
        max_frames: Maximum number of frames to output (downsampling)
        
    Returns:
        Binary data (bytes) containing the simulation results
    """
    # Create spatial grid (N+1 points, but we use N interior points)
    x_full = np.linspace(xmin, xmax, N + 1)
    dx = x_full[1] - x_full[0]
    
    # Use interior points for wavefunction (N-1 points)
    x_inner = x_full[1:-1]
    grid_size = len(x_inner)
    
    # Calculate potential barrier height according to the kinetic energy
    V0 = momentum**2 / (2 * mass)
    
    # Create potential array (on interior points)
    V = np.zeros_like(x_inner)
    for i in range(len(V)):
        if x_inner[i] > barrier_start and x_inner[i] < barrier_end:
            V[i] = V0
    
    # Initial wavefunction (Gaussian wave packet)
    Psi0 = (np.exp(-((x_inner - x0)**2) / sigma**2) * 
            np.exp(1j * momentum * (x_inner - x0)))
    
    # Normalize initial wavefunction
    A = np.sum(np.abs(Psi0)**2 * dx)
    Psi0 = Psi0 / np.sqrt(A)
    
    # Construct Hamiltonian matrix (finite difference method)
    H = ((hbar**2 / (mass * dx**2)) * np.diag(np.ones(grid_size)) +
         V * np.diag(np.ones(grid_size)) +
         (-hbar**2 / (2 * mass * dx**2)) * np.diag(np.ones(grid_size - 1), 1) +
         (-hbar**2 / (2 * mass * dx**2)) * np.diag(np.ones(grid_size - 1), -1))
    
    # Solve eigenvalue problem ONCE: H|psi> = E|psi>
    E, psi = np.linalg.eigh(H)
    psi = psi.T  # Transpose so each row is an eigenstate
    
    # Normalize eigenstates
    A = np.sum(np.abs(psi[0])**2 * dx)
    psi = psi / np.sqrt(A)
    
    # Project initial wavefunction onto eigenstates
    c = np.zeros(len(Psi0), dtype=complex)
    for i in range(len(c)):
        c[i] = np.sum(np.conj(psi[i]) * Psi0 * dx)
    
    # Time evolution with downsampling
    if num_time_steps is None:
        num_time_steps = int(t_max / dt)
    
    # Calculate downsampling stride
    if num_time_steps > max_frames:
        downsample_stride = num_time_steps // max_frames
    else:
        downsample_stride = 1
    
    # Collect frames (complex wavefunction)
    frames = []
    for step in range(0, num_time_steps, downsample_stride):
        t = step * dt
        Psi = np.zeros_like(psi[0], dtype=complex)
        
        # Time evolution: Psi(t) = sum(c[i] * psi[i] * exp(-i*E[i]*t/hbar))
        for i in range(len(c)):
            Psi = Psi + c[i] * psi[i] * np.exp(-1j * E[i] * t / hbar)
        
        frames.append(Psi)
        
        # Stop if we've reached max_frames
        if len(frames) >= max_frames:
            break
    
    frame_count = len(frames)
    
    # Write binary data to BytesIO buffer
    buffer = BytesIO()
    
    # Write HEADER
    buffer.write(struct.pack('I', frame_count))  # uint32 frame_count
    buffer.write(struct.pack('I', grid_size))    # uint32 grid_size
    
    # Write DATA: x array (float32)
    x_float32 = x_inner.astype(np.float32)
    buffer.write(x_float32.tobytes())
    
    # Write FRAMES: psi_real[N] and psi_imag[N] for each frame
    for Psi in frames:
        psi_real = np.real(Psi).astype(np.float32)
        psi_imag = np.imag(Psi).astype(np.float32)
        buffer.write(psi_real.tobytes())
        buffer.write(psi_imag.tobytes())
    
    # Get binary data
    binary_data = buffer.getvalue()
    buffer.close()
    
    return binary_data

def quantum_wave_packet_simulation(
    mass: float = 1.0,
    hbar: float = 1.0,
    xmin: float = -6.5,
    xmax: float = 6.5,
    N: int = 1000,
    momentum: float = 40.0,
    sigma: float = 0.15,
    x0: float = -3.0,
    barrier_start: float = 0.0,
    barrier_end: float = 0.5,
    dt: float = 0.001,
    t_max: float = 2.0,
    num_time_steps: Optional[int] = None
) -> Dict[str, Any]:
    """
    Quantum wave packet scattering simulation (legacy JSON endpoint)
    
    This is kept for backward compatibility with the JSON endpoint.
    For the new binary endpoint, use quantum_tunneling_simulation_binary().
    
    Args:
        mass: Particle mass
        hbar: Reduced Planck constant
        xmin, xmax: Spatial grid boundaries
        N: Number of grid points
        momentum: Initial momentum
        sigma: Gaussian width
        x0: Initial position (should be left of barrier for scattering)
        barrier_start, barrier_end: Potential barrier boundaries
        dt: Time step
        t_max: Maximum simulation time
        num_time_steps: Number of time steps (if None, calculated from dt and t_max)
        
    Returns:
        Dictionary with simulation results including time evolution
    """
    # Create spatial grid
    # Divides space to [xmin, xmax] into N + 1 points
    x = np.linspace(xmin, xmax, N + 1)
    dx = x[1] - x[0]
    
    # Calculate potential barrier height according to the kinetic energy
    V0 = momentum**2 / (2 * mass)
    
    # Create potential array
    V = np.zeros_like(x)
    for i in range(len(V)):
        if x[i] > barrier_start and x[i] < barrier_end:
            V[i] = V0
    
    # Initial wavefunction (Gaussian wave packet)
    x_inner = x[1:-1]  # Interior points (N-1 points)
    # Fixed: use (x_inner - x0) for proper Gaussian centering
    Psi0 = (np.exp(-((x_inner - x0)**2) / sigma**2) * 
            np.exp(1j * momentum * (x_inner - x0)))
    
    # Normalize initial wavefunction
    A = np.sum(np.abs(Psi0)**2 * dx)
    Psi0 = Psi0 / np.sqrt(A)
    
    # Construct Hamiltonian matrix (finite difference method)
    H = ((hbar**2 / (mass * dx**2)) * np.diag(np.ones(N - 1)) +
         V[1:-1] * np.diag(np.ones(N - 1)) +
         (-hbar**2 / (2 * mass * dx**2)) * np.diag(np.ones(N - 2), 1) +
         (-hbar**2 / (2 * mass * dx**2)) * np.diag(np.ones(N - 2), -1))
    
    # Solve eigenvalue problem: H|psi> = E|psi>
    E, psi = np.linalg.eigh(H)
    psi = psi.T  # Transpose so each row is an eigenstate
    
    # Normalize eigenstates
    A = np.sum(np.abs(psi[0])**2 * dx)
    psi = psi / np.sqrt(A)
    
    # Project initial wavefunction onto eigenstates
    c = np.zeros(len(Psi0), dtype=complex)
    for i in range(len(c)):
        c[i] = np.sum(np.conj(psi[i]) * Psi0 * dx)
    
    # Time evolution
    if num_time_steps is None:
        num_time_steps = int(t_max / dt)
    
    time_evolution = []
    for step in range(num_time_steps):
        t = step * dt
        Psi = np.zeros_like(psi[0], dtype=complex)
        
        # Time evolution: Psi(t) = sum(c[i] * psi[i] * exp(-i*E[i]*t/hbar))
        for i in range(len(c)):
            Psi = Psi + c[i] * psi[i] * np.exp(-1j * E[i] * t / hbar)
        
        time_evolution.append({
            "time": float(t),
            "wavefunction": np.abs(Psi).tolist()  # Probability density
        })
    
    return {
        "x": x.tolist(),
        "x_inner": x_inner.tolist(),  # For wavefunction data (N-1 points)
        "potential": V.tolist(),
        "initial_wavefunction": np.abs(Psi0).tolist(),
        "time_evolution": time_evolution,
        "eigenenergies": E.tolist(),
        "barrier_height": float(V0)
    }

