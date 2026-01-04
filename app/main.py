from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.models import QuantumSimulationRequest
from app.physics.calculator import quantum_tunneling_simulation_binary

app = FastAPI(
    title="Physics Simulation API",
    description="Backend API for physics simulation calculations",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["simulation"])


@app.post("/api/quantum-tunneling")
async def quantum_tunneling(request: QuantumSimulationRequest):
    """
    Quantum tunneling simulation endpoint - returns full simulation as binary
    
    Returns the entire simulation in a single HTTP response as binary data.
    No disk I/O, no batches, no separate frame requests.
    
    Binary format:
    - HEADER: uint32 frame_count, uint32 grid_size (N)
    - DATA: float32 x[N] array
    - FRAMES: For each frame: float32 psi_real[N], float32 psi_imag[N]
    
    The frontend can parse this using fixed offsets:
    1. Read header (8 bytes): frame_count, grid_size
    2. Read x array (grid_size * 4 bytes)
    3. For each frame, read psi_real (grid_size * 4) and psi_imag (grid_size * 4)
    """
    try:
        # Calculate number of time steps
        if request.num_time_steps is None:
            num_time_steps = int(request.t_max / request.dt)
        else:
            num_time_steps = request.num_time_steps
        
        # Run simulation and get binary data (all in memory)
        binary_data = quantum_tunneling_simulation_binary(
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
            num_time_steps=num_time_steps,
            max_frames=500  # Downsample to max 500 frames
        )
        
        # Calculate metadata for headers
        # Format: 8 bytes header + N*4 bytes x + frames*(N*4 + N*4) bytes
        import struct
        frame_count = struct.unpack('I', binary_data[0:4])[0]
        grid_size = struct.unpack('I', binary_data[4:8])[0]
        
        return Response(
            content=binary_data,
            media_type="application/octet-stream",
            headers={
                "X-Frames": str(frame_count),
                "X-Grid-Size": str(grid_size),
                "X-Format": "header(uint32 frame_count, uint32 grid_size) + x[N](float32) + frames[psi_real[N], psi_imag[N]](float32)",
                "Content-Length": str(len(binary_data))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Physics Simulation API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

