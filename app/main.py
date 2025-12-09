from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.models import QuantumSimulationRequest, QuantumTunnelingJobResponse
import uuid
import os
import glob
import numpy as np
from datetime import datetime, timedelta
from app.physics.calculator import quantum_wave_packet_simulation

# Determine data directory based on environment
# Render uses /tmp, local development uses data/
DATA_DIR = os.getenv("DATA_DIR", "/tmp" if os.path.exists("/tmp") else "data")

# Batch configuration for efficient frame retrieval
BATCH_SIZE = 100  # Number of frames per batch file

def cleanup_job(job_id: str):
    """Remove all binary files for a specific job (both individual frames and batches)"""
    # Clean up individual frame files
    pattern = os.path.join(DATA_DIR, f"{job_id}_*.bin")
    files = glob.glob(pattern)
    for f in files:
        try:
            os.remove(f)
        except OSError:
            pass  # File might already be deleted

def cleanup_old_jobs(max_age_minutes: int = 5):
    """Clean up jobs older than max_age_minutes"""
    pattern = os.path.join(DATA_DIR, "*_*.bin")
    files = glob.glob(pattern)
    cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
    
    deleted_count = 0
    for file_path in files:
        try:
            # Check file modification time
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if mtime < cutoff_time:
                os.remove(file_path)
                deleted_count += 1
        except (OSError, ValueError):
            pass  # File might be deleted or invalid
    
    return deleted_count

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

# Startup event: Clean up old jobs on server start
@app.on_event("startup")
async def startup_event():
    """Clean up old jobs when server starts"""
    deleted = cleanup_old_jobs(max_age_minutes=5)
    print(f"Startup cleanup: Deleted {deleted} old job files")


@app.post("/api/quantum-tunneling", response_model=QuantumTunnelingJobResponse)
async def quantum_tunneling_alias(request: QuantumSimulationRequest):
    """Quantum tunneling simulation endpoint that saves frames to binary files"""
    print("i am working")
    # Generate unique job ID
    job_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    print(f"Job ID: {job_id}")
    # Calculate number of time steps
    if request.num_time_steps is None:
        num_time_steps = int(request.t_max / request.dt)
    else:
        num_time_steps = request.num_time_steps
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Run simulation and save frames
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
        num_time_steps=num_time_steps
    )
    
    # Save frames in batches for efficient retrieval
    x_inner = np.array(result["x_inner"])
    n = len(x_inner)  # Number of grid points
    total_frames = len(result["time_evolution"])
    
    # Calculate number of batches needed
    num_batches = (total_frames + BATCH_SIZE - 1) // BATCH_SIZE  # Ceiling division
    
    # Save frames in batches
    for batch_idx in range(num_batches):
        start_frame = batch_idx * BATCH_SIZE
        end_frame = min(start_frame + BATCH_SIZE, total_frames)
        
        # Collect all frames in this batch
        batch_frames = []
        for k in range(start_frame, end_frame):
            psi = np.array(result["time_evolution"][k]["wavefunction"], dtype=np.float32)
            batch_frames.append(psi)
        
        # Concatenate all frames in the batch into one array
        batch_array = np.concatenate(batch_frames)
        
        # Save batch file
        batch_file = os.path.join(DATA_DIR, f"{job_id}_batch_{batch_idx}.bin")
        batch_array.tofile(batch_file)
    
    # Return job metadata
    return QuantumTunnelingJobResponse(
        job_id=job_id,
        frame_count=len(result["time_evolution"]),
        n=n,
        dt=request.dt,
        batch_size=BATCH_SIZE
    )

@app.get("/batch/{job_id}/{batch_idx}")
async def get_batch(job_id: str, batch_idx: int, n: int):
    """
    Retrieve a batch of frames from a quantum tunneling simulation
    
    Args:
        job_id: Job identifier
        batch_idx: Batch index (0, 1, 2, ...)
        n: Number of grid points (required to parse frames correctly)
    
    Returns:
        Binary data containing concatenated frames in the batch.
        Each frame is n * 4 bytes (float32 = 4 bytes per value).
        Frontend can parse: frame_size = n * 4, then extract frames[i] = data[i * frame_size : (i+1) * frame_size]
    """
    path = os.path.join(DATA_DIR, f"{job_id}_batch_{batch_idx}.bin")
    
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Batch {batch_idx} not found for job {job_id}")
    
    # Read batch file
    with open(path, "rb") as f:
        data = f.read()
    
    # Calculate how many frames are in this batch
    frame_size = n * 4  # float32 = 4 bytes
    frames_in_batch = len(data) // frame_size
    
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={
            "X-Frame-Count": str(frames_in_batch),
            "X-Grid-Points": str(n),
            "X-Frame-Size": str(frame_size),
            "X-Batch-Index": str(batch_idx),
            "X-Start-Frame": str(batch_idx * BATCH_SIZE)
        }
    )

@app.get("/frame/{job_id}/{k}")
async def get_frame(job_id: str, k: int, n: int):
    """
    Retrieve a specific frame from a quantum tunneling simulation (backward compatibility)
    
    Note: This endpoint extracts a single frame from a batch file.
    For better performance, use /batch/{job_id}/{batch_idx} to get multiple frames at once.
    
    Args:
        job_id: Job identifier
        k: Frame index
        n: Number of grid points (required)
    """
    # Calculate which batch contains this frame
    batch_idx = k // BATCH_SIZE
    frame_in_batch = k % BATCH_SIZE
    
    batch_path = os.path.join(DATA_DIR, f"{job_id}_batch_{batch_idx}.bin")
    
    if not os.path.exists(batch_path):
        raise HTTPException(status_code=404, detail=f"Frame {k} not found for job {job_id}")
    
    # Read the specific frame from the batch
    frame_size = n * 4  # float32 = 4 bytes
    offset = frame_in_batch * frame_size
    
    with open(batch_path, "rb") as f:
        f.seek(offset)
        frame_data = f.read(frame_size)
    
    if len(frame_data) < frame_size:
        raise HTTPException(status_code=404, detail=f"Frame {k} not found for job {job_id}")
    
    return Response(
        content=frame_data,
        media_type="application/octet-stream"
    )

@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """Explicitly delete a job and all its frames"""
    cleanup_job(job_id)
    return {"status": "success", "message": f"Job {job_id} deleted"}

@app.post("/api/cleanup")
async def cleanup_old_jobs_endpoint(max_age_minutes: int = 5):
    """Manually trigger cleanup of old jobs (default: 5 minutes)"""
    deleted = cleanup_old_jobs(max_age_minutes=max_age_minutes)
    return {
        "status": "success", 
        "message": f"Cleaned up {deleted} job files older than {max_age_minutes} minutes"
    }

@app.get("/")
async def root():
    return {"message": "Physics Simulation API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

