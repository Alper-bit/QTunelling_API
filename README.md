# Physics Simulation Backend

FastAPI backend for physics simulation calculations, featuring quantum wave packet scattering simulations with binary output for high-performance visualization.

## Features

- **Quantum Tunneling Simulation**: High-performance quantum wave packet scattering with binary output
- **In-Memory Processing**: No disk I/O - all simulation data returned in a single HTTP response
- **Efficient Binary Format**: Optimized float32 binary payload for frontend parsing
- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation
- **Type Safety**: Full Pydantic validation for request/response models

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

5. API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### General Endpoints

- `GET /` - Root endpoint (API status)
- `GET /health` - Health check endpoint

### Quantum Simulation

#### Binary Endpoint (Recommended for Production)

- `POST /api/quantum-tunneling` - Quantum tunneling simulation (binary response)

**Returns**: Binary payload with the entire simulation in a single response.

**Request Body** (all fields optional with defaults):

```json
{
  "mass": 1.0,
  "hbar": 1.0,
  "xmin": -6.5,
  "xmax": 6.5,
  "N": 1000,
  "momentum": 40.0,
  "sigma": 0.15,
  "x0": -3.0,
  "barrier_start": 0.0,
  "barrier_end": 0.5,
  "dt": 0.001,
  "t_max": 2.0,
  "num_time_steps": null
}
```

**Binary Response Format**:

```
HEADER (8 bytes):
  - uint32 frame_count (number of time frames)
  - uint32 grid_size (N, number of spatial points)

DATA (grid_size * 4 bytes):
  - float32 x[grid_size] (spatial grid points)

FRAMES (for each frame, sequentially):
  - float32 psi_real[grid_size] (real part of wavefunction)
  - float32 psi_imag[grid_size] (imaginary part of wavefunction)
```

**Response Headers**:
- `Content-Type: application/octet-stream`
- `X-Frames: <frame_count>`
- `X-Grid-Size: <grid_size>`
- `X-Format: <format_description>`

**Frontend Parsing Example (JavaScript)**:

```javascript
const response = await fetch('/api/quantum-tunneling', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(params)
});

const arrayBuffer = await response.arrayBuffer();
const view = new DataView(arrayBuffer);

// Read header
let offset = 0;
const frameCount = view.getUint32(offset, true); offset += 4;
const gridSize = view.getUint32(offset, true); offset += 4;

// Read x array
const x = new Float32Array(arrayBuffer, offset, gridSize);
offset += gridSize * 4;

// Read frames
const frames = [];
for (let i = 0; i < frameCount; i++) {
  const psiReal = new Float32Array(arrayBuffer, offset, gridSize);
  offset += gridSize * 4;
  const psiImag = new Float32Array(arrayBuffer, offset, gridSize);
  offset += gridSize * 4;
  
  // Calculate probability density: |psi|^2 = real^2 + imag^2
  const probability = new Float32Array(gridSize);
  for (let j = 0; j < gridSize; j++) {
    probability[j] = psiReal[j]**2 + psiImag[j]**2;
  }
  
  frames.push(probability);
}
```

#### JSON Endpoint (Legacy)

- `POST /api/v1/quantum/simulate` - Quantum wave packet scattering simulation (JSON response)

**Note**: This endpoint returns the full time evolution in JSON format, which can be memory-intensive for large simulations. Use the binary endpoint for better performance.

**Request Body**: Same as binary endpoint

**Response**:

```json
{
  "x": [...],                    // Full spatial grid (N+1 points)
  "x_inner": [...],              // Interior points for wavefunction (N-1 points)
  "potential": [...],            // Potential energy values
  "initial_wavefunction": [...],  // Initial probability density
  "time_evolution": [            // Time evolution snapshots
    {
      "time": 0.0,
      "wavefunction": [...]
    },
    ...
  ],
  "eigenenergies": [...],        // Energy eigenvalues
  "barrier_height": 800.0,       // Barrier height
  "status": "success"
}
```

## Performance Optimizations

1. **No Disk I/O**: All computation happens in-memory using `io.BytesIO`
2. **Frame Downsampling**: Automatically downsamples to max 500 frames for efficiency
3. **Float32 Precision**: Uses 32-bit floats instead of 64-bit for reduced payload size
4. **Single HTTP Response**: Entire simulation returned in one request (no batching)
5. **Eigenvalue Caching**: Hamiltonian eigenvalues computed only once per simulation

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API routes
│   └── physics/
│       ├── __init__.py
│       └── calculator.py   # Physics calculations
├── data/                    # Empty (no disk I/O)
├── requirements.txt
├── README.md
└── .gitignore
```

## Development

The project uses:
- **FastAPI** for the web framework
- **Pydantic** for data validation
- **NumPy** for numerical computations
- **Uvicorn** as the ASGI server

## Deployment on Render

This backend is optimized for deployment on Render (or similar platforms):

1. No temporary file storage required
2. Stateless architecture - each request is independent
3. Memory-efficient with automatic downsampling
4. Fast response times with binary format

## License

[Add your license here]

