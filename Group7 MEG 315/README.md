# 230404035 Group 7 - AD-HTC Fuel-Enhanced Gas Power Cycle Analysis System

## Overview
This project implements an interactive Process Flow Diagram (PFD) for an AD-HTC (Anaerobic Digestion - Hydrothermal Carbonization) fuel-enhanced gas power cycle analysis system. The system provides both React and Python-based frontends for maximum accessibility.

## System Architecture

### Backend (Python/FastAPI)
- **Location**: `backend/`
- **Technology**: FastAPI with thermodynamic calculation engines
- **API Endpoints**: 
  - `/calculate` - Custom parameter calculations
  - `/scenarios/{scenario_id}/calculate` - Predefined scenario calculations
  - `/presets` - Available parameter presets
  - `/optimize` - Parameter optimization
  - `/economic-analysis` - Economic analysis
  - `/environmental-analysis` - Environmental impact analysis

### Frontend Options

#### 1. React Frontend (Recommended)
- **Location**: `frontend/`
- **Technology**: React with Recharts for visualization
- **Features**: 
  - Interactive PFD with animated flows
  - Real-time simulation controls
  - Time-slider for dynamic analysis
  - Component click analysis
  - Performance charts and metrics

#### 2. Python Frontend (Lecturer-Friendly)
- **Location**: `frontend_python/`
- **Technology**: Tkinter with Matplotlib
- **Features**: 
  - Identical functionality to React frontend
  - No Node.js dependencies required
  - Lightweight and portable
  - Same backend integration

## Quick Start

### Option 1: Universal Launcher (Recommended)
```bash
# Run the interactive launcher
python launcher.py
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### React Frontend
```bash
cd frontend
npm install
npm start
# Opens at http://localhost:3000
```

#### Python Frontend
```bash
cd frontend_python
pip install -r requirements_python_frontend.txt
python adhtc_gui.py
```

## Requirements Checking

### Automatic Requirements Check
```bash
# Check all system requirements
python check_requirements.py

# Or use the launcher for guided setup
python launcher.py
```

### Manual Requirements Check

#### Backend Requirements
- Python 3.7+
- FastAPI
- NumPy
- Pandas
- SciPy
- Uvicorn

#### React Frontend Requirements
- Node.js 14+
- npm or yarn
- React 18+
- Recharts
- Axios

#### Python Frontend Requirements
- Python 3.7+
- Tkinter (usually included)
- Matplotlib
- NumPy
- Requests

## System Features

### Process Flow Diagram (PFD)
- **Animated Flows**: 
  - Green: Biogas flow
  - Blue: Air flow
  - Yellow: Heat flow
- **Interactive Components**: Click any component for detailed analysis
- **Energy Theme**: Color-graded design for sustainability focus

### Scenario Analysis
- **Base Case**: Standard AD-HTC integration
- **Optimized**: Enhanced heat recovery (85% self-sufficiency)
- **Full COGAS**: Combined cycle with steam turbine and HRSG

### Real-Time Simulation
- **Time Control**: Adjustable simulation speed (1x-10x)
- **Time Slider**: Navigate through 24-hour cycles
- **Dynamic Updates**: Real-time parameter adjustment

### Performance Metrics
- **Net Power Output**: kW electrical generation
- **Overall Efficiency**: System-wide energy conversion
- **Self-Sufficiency Ratio**: Waste heat utilization
- **Primary Energy Saving**: Compared to separate production

## API Integration

Both frontends connect to the same backend API for synchronous data exchange:

### Calculation Request Format
```json
{
  "ambient_temp": 288.0,
  "pressure_ratio": 6.0,
  "max_turbine_temp": 1000.0,
  "compressor_efficiency": 0.85,
  "turbine_efficiency": 0.90,
  "ad_feedstock_rate": 3000.0,
  "ad_retention_time": 20.0,
  "htc_biomass_rate": 500.0,
  "htc_temperature": 473.0,
  "scenario": "base_case"
}
```

### Response Format
```json
{
  "timestamp": "2024-01-01T00:00:00",
  "scenario": "base_case",
  "gas_turbine": { /* turbine results */ },
  "ad_system": { /* AD system results */ },
  "htc_system": { /* HTC system results */ },
  "overall_performance": { /* system metrics */ },
  "energy_flows": { /* flow data */ }
}
```

## Usage Instructions

### For Students/Developers
1. Use React frontend for full interactive experience
2. Run `python launcher.py` for guided setup
3. Check `check_requirements.py` for system validation

### For Lecturers/Reviewers
1. Use Python frontend (`python start_python_frontend.py`)
2. No Node.js dependencies required
3. Identical functionality to React version
4. Lightweight and portable

## Troubleshooting

### Common Issues

#### Backend Not Starting
- Check Python version (3.7+ required)
- Verify port 8000 is available
- Check backend requirements installation

#### React Frontend Issues
- Ensure Node.js is installed
- Run `npm install` in frontend directory
- Check for port conflicts (default: 3000)

#### Python Frontend Issues
- Install requirements: `pip install -r frontend_python/requirements_python_frontend.txt`
- Ensure tkinter is available (usually included with Python)
- Check backend is running at http://localhost:8000

### Getting Help
1. Run requirements checker: `python check_requirements.py`
2. Use launcher for guided setup: `python launcher.py`
3. Check backend logs for calculation errors
4. Verify API connectivity with browser: http://localhost:8000/docs

## Project Structure
```
230404035 ASS7/
├── backend/                    # FastAPI backend
│   ├── main.py                # API endpoints
│   ├── requirements.txt       # Backend dependencies
│   └── thermodynamics/        # Calculation engines
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.js            # Main application
│   │   └── components/       # React components
│   └── package.json         # React dependencies
├── frontend_python/           # Python frontend
│   ├── adhtc_gui.py         # Main GUI application
│   └── requirements_python_frontend.txt
├── launcher.py               # Universal launcher
├── start_python_frontend.py  # Python-only launcher
└── check_requirements.py    # Requirements validator
```

## Performance Notes

### Backend Performance
- Calculation time: <100ms for standard scenarios
- Supports concurrent requests from multiple frontends
- Optimized for real-time simulation updates

### Frontend Performance
- **React**: Smooth 60fps animations, responsive design
- **Python**: Lightweight GUI, minimal resource usage
- **Data Sync**: Real-time updates via REST API polling

## Development Notes

### Adding New Scenarios
1. Update `backend/main.py` presets
2. Add scenario to `ScenarioManager` class
3. Update frontend scenario selectors

### Modifying Calculations
1. Edit calculation engines in `backend/thermodynamics/`
2. Update API response models if needed
3. Test with both frontends for compatibility

### Custom Parameters
Both frontends support custom parameter input:
- Ambient temperature (K)
- Pressure ratio
- Maximum turbine temperature (K)
- Compressor/turbine efficiencies
- Biomass feed rates
- Retention times
- Reactor temperatures

## License
This project is part of academic coursework for 230404035 Group 7.