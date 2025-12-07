"""
Physics calculation module
Add your physics simulation logic here
"""
from typing import Dict, Any, List, Optional
import numpy as np

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
    Quantum wave packet scattering simulation
    
    Simulates a quantum wave packet scattering off a potential barrier.
    This is the backend version that returns data instead of visualizing.
    
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
    x = np.linspace(xmin, xmax, N + 1)
    dx = x[1] - x[0]
    
    # Calculate potential barrier height
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

