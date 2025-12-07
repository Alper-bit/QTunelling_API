from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Physics Simulation API",
    description="Backend API for physics simulation calculations",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1", tags=["simulation"])

@app.get("/")
async def root():
    return {"message": "Physics Simulation API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

