# AD-HTC Fuel-Enhanced Gas Power Cycle Analysis System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2%2B-61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-3178C6)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A professional-grade process flow analysis system for Anaerobic Digestion (AD) and Hydrothermal Carbonization (HTC) integrated biogas power generation cycles.

## 🌟 Features

### Thermodynamic Analysis
- **Brayton Cycle**: Gas turbine power generation with biogas enhancement
- **AD System**: Biogas production from organic waste with kinetic modeling
- **HTC System**: Biomass conversion to hydrochar with energy densification
- **Heat Integration**: Waste heat recovery and utilization analysis

### Optimization Engine
- **Genetic Algorithm**: Multi-objective optimization for complex parameter spaces
- **Gradient Descent**: Fast convergence for continuous optimization
- **Pareto Frontier**: Trade-off analysis for conflicting objectives
- **Constraints Handling**: Physical and economic feasibility constraints

### Economic Analysis
- **NPV & IRR**: Net present value and internal rate of return calculations
- **LCOE**: Levelized cost of electricity with sensitivity analysis
- **CAPEX/OPEX**: Capital and operating expenditure breakdowns
- **Payback Period**: Investment recovery time analysis

### Environmental Impact
- **Carbon Footprint**: Lifecycle greenhouse gas emissions
- **Carbon Sequestration**: CO₂ capture in hydrochar
- **Avoided Emissions**: Displaced grid electricity impact
- **Sustainability Score**: Overall environmental performance metric

## 🏗️ Architecture

```
ad-htc-integrated-system/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── core/           # Core calculation modules
│   │   │   ├── thermodynamics/   # Brayton, AD, HTC systems
│   │   │   ├── optimization/     # GA, gradient, Pareto
│   │   │   ├── economics/      # NPV, LCOE, CAPEX
│   │   │   └── environmental/  # Carbon, LCA analysis
│   │   └── utils/          # Utilities
│   ├── main.py            # Application entry point
│   └── requirements.txt     # Python dependencies
│
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Calculator.tsx
│   │   │   ├── Optimizer.tsx
│   │   │   ├── Scenarios.tsx
│   │   │   └── ProcessFlow.tsx
│   │   ├── App.tsx        # Main application
│   │   └── main.tsx       # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
├── docker/                 # Docker configurations
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`

### Docker Deployment

```bash
docker-compose up --build
```

## 📊 API Endpoints

### Core Calculation
- `POST /calculate` - Perform thermodynamic calculation
- `POST /optimize` - Run optimization algorithm
- `POST /thermodynamic-charts` - Generate T-s/h-s chart data

### Analysis
- `POST /economic-analysis` - Economic feasibility study
- `POST /environmental-analysis` - Environmental impact assessment
- `POST /compare-scenarios` - Compare multiple scenarios

### Scenarios
- `GET /scenarios` - List all scenarios
- `GET /scenarios/{id}` - Get scenario details
- `POST /scenarios/{id}/calculate` - Calculate scenario performance

### System
- `GET /health` - Health check
- `GET /` - API information

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
APP_NAME=AD-HTC Power Cycle API
DEBUG=false
CORS_ORIGINS=["http://localhost:5173"]
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=AD-HTC Analysis System
```

## 📈 Usage Examples

### Basic Calculation

```python
import requests

response = requests.post("http://localhost:8000/calculate", json={
    "ambient_temp": 298.15,
    "pressure_ratio": 12.0,
    "max_turbine_temp": 1400.0,
    "compressor_efficiency": 0.85,
    "turbine_efficiency": 0.88,
    "ad_feedstock_rate": 3000.0,
    "ad_retention_time": 20.0,
    "htc_biomass_rate": 500.0,
    "htc_temperature": 473.15
})

results = response.json()
print(f"Net Power: {results['overall_performance']['net_power_output_kw']} kW")
print(f"Efficiency: {results['overall_performance']['overall_efficiency']*100:.1f}%")
```

### Optimization

```python
response = requests.post("http://localhost:8000/optimize", json={
    "objectives": {
        "maximize": ["efficiency", "power_output"],
        "minimize": ["specific_cost"],
        "weights": {
            "efficiency": 1.0,
            "power_output": 0.8,
            "specific_cost": 0.6
        }
    },
    "constraints": {
        "min_efficiency": 0.35,
        "max_cost": 1500
    },
    "method": "genetic",
    "population_size": 50,
    "generations": 100
})

optimized = response.json()
print(f"Optimal Parameters: {optimized['optimized_parameters']}")
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) (Swagger UI)
- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guide](CONTRIBUTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Group 7 - Process Integration Team
- University Engineering Department
- Open source thermodynamics libraries

## 📞 Contact

- Email: group7@university.edu
- Issues: [GitHub Issues](https://github.com/yourorg/ad-htc-system/issues)
- Discussions: [GitHub Discussions](https://github.com/yourorg/ad-htc-system/discussions)

---

**Made with ❤️ by Group 7 - Process Integration Team**
