# Physics Simulation Backend

FastAPI backend for physics simulation calculations, featuring quantum wave packet scattering simulations.

## Features

- **Quantum Wave Packet Simulation**: Simulate quantum wave packets scattering off potential barriers
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
- `POST /api/v1/simulate` - Generic simulation endpoint with Pydantic validation
- `POST /api/v1/calculate` - Generic calculation endpoint (raw JSON)

### Quantum Simulation

- `POST /api/v1/quantum/simulate` - Quantum wave packet scattering simulation

#### Request Body (all fields optional with defaults):

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

#### Response:

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

## License

[Add your license here]

