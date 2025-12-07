from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SimulationRequest(BaseModel):
    """Base model for simulation input data"""
    data: Dict[str, Any]
    
class SimulationResponse(BaseModel):
    """Base model for simulation output data"""
    result: Dict[str, Any]
    status: str = "success"

class QuantumSimulationRequest(BaseModel):
    """Request model for quantum wave packet simulation"""
    mass: float = 1.0
    hbar: float = 1.0
    xmin: float = -6.5
    xmax: float = 6.5
    N: int = 1000
    momentum: float = 40.0
    sigma: float = 0.15
    x0: float = -3.0  # Initial position (left of barrier)
    barrier_start: float = 0.0
    barrier_end: float = 0.5
    dt: float = 0.001
    t_max: float = 2.0
    num_time_steps: Optional[int] = None  # If None, calculate from dt and t_max

class QuantumSimulationResponse(BaseModel):
    """Response model for quantum simulation results"""
    x: List[float]
    x_inner: List[float]  # Interior points for wavefunction
    potential: List[float]
    initial_wavefunction: List[float]
    time_evolution: List[Dict[str, Any]]  # List of {time: float, wavefunction: List[float]}
    eigenenergies: List[float]
    barrier_height: float
    status: str = "success"

