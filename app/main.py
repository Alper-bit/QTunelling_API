from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.models import QuantumSimulationRequest

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

# Add alias endpoint without /v1 prefix for convenience
@app.post("/api/quantum-tunneling")
async def quantum_tunneling_alias(request: QuantumSimulationRequest):
    """Alias endpoint for quantum tunneling simulation (without /v1)"""
    from app.api.routes import quantum_simulate
    return await quantum_simulate(request)

@app.get("/")
async def root():
    return {"message": "Physics Simulation API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

