from fastapi import APIRouter, HTTPException
from app.models import (
    SimulationRequest, 
    SimulationResponse,
    QuantumSimulationRequest,
    QuantumSimulationResponse
)
from app.physics.calculator import calculate_simulation, quantum_wave_packet_simulation

router = APIRouter()

@router.post("/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    """
    Endpoint to receive simulation data and return calculated results
    """
    try:
        # Calculate physics simulation
        result = calculate_simulation(request.data)
        
        return SimulationResponse(
            result=result,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate")
async def calculate(data: dict):
    """
    Alternative endpoint that accepts raw JSON
    """
    try:
        result = calculate_simulation(data)
        return {
            "result": result,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quantum/simulate", response_model=QuantumSimulationResponse)
async def quantum_simulate(request: QuantumSimulationRequest):
    """
    Quantum wave packet scattering simulation endpoint
    
    Simulates a quantum wave packet scattering off a potential barrier.
    Returns the time evolution of the wavefunction probability density.
    
    The wave packet starts at position x0 and moves toward the barrier.
    You can observe quantum tunneling and reflection effects.
    """
    try:
        result = quantum_wave_packet_simulation(
            mass=request.mass,
            hbar=request.hbar,
            xmin=request.xmin,
            xmax=request.xmax,
            N=request.N,
            momentum=request.momentum,
            sigma=request.sigma,
            x0=request.x0,
            barrier_start=request.barrier_start,
            barrier_end=request.barrier_end,
            dt=request.dt,
            t_max=request.t_max,
            num_time_steps=request.num_time_steps
        )
        
        return QuantumSimulationResponse(
            x=result["x"],
            x_inner=result["x_inner"],
            potential=result["potential"],
            initial_wavefunction=result["initial_wavefunction"],
            time_evolution=result["time_evolution"],
            eigenenergies=result["eigenenergies"],
            barrier_height=result["barrier_height"],
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quantum-tunneling", response_model=QuantumSimulationResponse)
async def quantum_tunneling(request: QuantumSimulationRequest):
    """
    Alias endpoint for quantum simulation (same as /quantum/simulate)
    """
    return await quantum_simulate(request)
