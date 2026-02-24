"""
AD-HTC Fuel-Enhanced Gas Power Cycle API
FastAPI backend with comprehensive thermodynamic analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import numpy as np
import math
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import core modules
from app.core.thermodynamics.brayton_cycle import BraytonCycle
from app.core.thermodynamics.ad_system import ADSystem, ADConfig
from app.core.thermodynamics.htc_system import HTCSystem, HTCConfig
from app.core.optimization.optimizer import SystemOptimizer, OptimizationConfig, OptimizationMethod
from app.core.economics.economic_analysis import EconomicAnalyzer, EconomicParams
from app.core.environmental.environmental_analysis import EnvironmentalAnalyzer, EnvironmentalParams
from app.core.optimization.scenario_manager import ScenarioManager

# Initialize FastAPI app
app = FastAPI(
    title="AD-HTC Fuel-Enhanced Gas Power Cycle API",
    description="""
    Professional-grade process flow analysis system for AD-HTC integrated biogas power cycle.

    ## Features

    * **Thermodynamic Analysis**: Brayton cycle, AD system, HTC system
    * **Optimization**: Multi-objective optimization (genetic, gradient, Pareto)
    * **Economic Analysis**: NPV, LCOE, CAPEX/OPEX calculations
    * **Environmental Analysis**: Carbon footprint, emissions, sustainability
    * **Scenario Management**: Presets and custom scenarios

    ## Systems

    1. **Anaerobic Digestion (AD)**: Biogas production from organic waste
    2. **Hydrothermal Carbonization (HTC)**: Biomass conversion to hydrochar
    3. **Gas Turbine**: Brayton cycle power generation
    4. **Heat Recovery**: Integrated heat recovery and utilization
    """,
    version="2.1.0",
    contact={
        "name": "Group 7 - Process Integration Team",
        "email": "group7@university.edu"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
brayton_engine = BraytonCycle()
ad_engine = ADSystem()
htc_engine = HTCSystem()
optimizer = SystemOptimizer()
economic_analyzer = EconomicAnalyzer()
environmental_analyzer = EnvironmentalAnalyzer()
scenario_manager = ScenarioManager()

# ============== Pydantic Models ==============

class CalculationRequest(BaseModel):
    ambient_temp: float = Field(298.15, ge=273.0, le=323.0, description="Ambient temperature (K)")
    pressure_ratio: float = Field(12.0, ge=3.0, le=25.0, description="Compressor pressure ratio")
    max_turbine_temp: float = Field(1400.0, ge=800.0, le=1600.0, description="Turbine inlet temperature (K)")
    compressor_efficiency: float = Field(0.85, ge=0.75, le=0.95, description="Compressor efficiency")
    turbine_efficiency: float = Field(0.88, ge=0.80, le=0.95, description="Turbine efficiency")
    ad_feedstock_rate: float = Field(3000.0, ge=1000.0, le=10000.0, description="AD feedstock rate (kg/day)")
    ad_retention_time: float = Field(20.0, ge=10.0, le=40.0, description="AD retention time (days)")
    htc_biomass_rate: float = Field(500.0, ge=100.0, le=2000.0, description="HTC biomass rate (kg/day)")
    htc_temperature: float = Field(473.0, ge=423.0, le=573.0, description="HTC reactor temperature (K)")
    scenario: str = Field("base_case", description="Scenario identifier")

class OptimizationRequest(BaseModel):
    objectives: Dict[str, Any] = Field(..., description="Optimization objectives")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Optional constraints")
    method: str = Field("genetic", pattern="^(genetic|gradient|pareto)$")
    population_size: int = Field(50, ge=10, le=200)
    generations: int = Field(100, ge=20, le=500)

class EconomicRequest(BaseModel):
    net_power_kw: float = Field(..., gt=0, description="Net power output (kW)")
    annual_opex_usd: float = Field(..., ge=0, description="Annual OPEX (USD)")
    annual_revenue_usd: float = Field(..., ge=0, description="Annual revenue (USD)")
    project_lifetime: int = Field(20, ge=5, le=30)
    discount_rate: float = Field(0.08, ge=0.01, le=0.20)
    tax_rate: float = Field(0.25, ge=0.0, le=0.50)

class EnvironmentalRequest(BaseModel):
    net_power_kw: float = Field(..., gt=0, description="Net power output (kW)")
    annual_hours: float = Field(8000, ge=1000, le=8760)
    biomass_rate_kg_day: float = Field(3000.0, ge=100.0, le=10000.0)
    hydrochar_rate_kg_day: float = Field(300.0, ge=0.0, le=1000.0)
    biogas_production_m3_day: float = Field(0.0, ge=0.0, le=10000.0)

# ============== API Endpoints ==============

@app.get("/")
async def root():
    """API root - health check"""
    return {
        "message": "AD-HTC Fuel-Enhanced Gas Power Cycle API",
        "version": "2.1.0",
        "status": "operational",
        "documentation": "/docs",
        "endpoints": [
            "/calculate",
            "/optimize",
            "/scenarios",
            "/economic-analysis",
            "/environmental-analysis",
            "/thermodynamic-charts"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "brayton_cycle": "ready",
            "ad_system": "ready",
            "htc_system": "ready",
            "optimizer": "ready",
            "economic_analyzer": "ready",
            "environmental_analyzer": "ready",
            "scenario_manager": "ready"
        }
    }

@app.post("/calculate")
async def calculate_performance(request: CalculationRequest):
    """
    Perform comprehensive thermodynamic calculation

    Calculates:
    - Brayton cycle performance
    - AD system biogas production
    - HTC system hydrochar production
    - Overall system integration
    - Energy flows and balances
    """

    try:
        logger.info(f"Starting calculation for scenario: {request.scenario}")

        # Brayton cycle calculation
        gt_results = brayton_engine.calculate(
            T1=request.ambient_temp,
            P_ratio=request.pressure_ratio,
            T3=request.max_turbine_temp,
            eta_comp=request.compressor_efficiency,
            eta_turb=request.turbine_efficiency
        )

        # AD system calculation
        ad_config = ADConfig(
            feedstock_rate=request.ad_feedstock_rate,
            retention_time=request.ad_retention_time,
            temperature=308.15,
            num_digesters=3,
            vs_content=0.60
        )
        ad_results = ad_engine.calculate(ad_config)

        # HTC system calculation
        htc_config = HTCConfig(
            biomass_rate=request.htc_biomass_rate,
            reactor_temp=request.htc_temperature,
            ambient_temp=request.ambient_temp,
            residence_time=2.0,
            moisture_content=0.10
        )
        htc_results = htc_engine.calculate(htc_config)

        # Calculate overall performance
        overall = calculate_overall_performance(gt_results, ad_results, htc_results)

        # Calculate energy flows
        energy_flows = calculate_energy_flows(gt_results, ad_results, htc_results)

        return {
            "timestamp": datetime.now().isoformat(),
            "scenario": request.scenario,
            "gas_turbine": gt_results,
            "ad_system": ad_results,
            "htc_system": htc_results,
            "overall_performance": overall,
            "energy_flows": energy_flows
        }

    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@app.post("/optimize")
async def optimize_system(request: OptimizationRequest):
    """
    Run multi-objective optimization

    Methods:
    - **genetic**: Genetic algorithm (recommended for complex problems)
    - **gradient**: Gradient descent (faster, may find local optima)
    - **pareto**: Pareto frontier (for multi-objective trade-offs)
    """

    try:
        logger.info(f"Starting optimization with method: {request.method}")

        method_map = {
            "genetic": OptimizationMethod.GENETIC,
            "gradient": OptimizationMethod.GRADIENT,
            "pareto": OptimizationMethod.PARETO
        }

        config = OptimizationConfig(
            objectives=request.objectives,
            constraints=request.constraints,
            method=method_map[request.method],
            population_size=request.population_size,
            generations=request.generations
        )

        result = optimizer.optimize(config)

        return {
            "optimization_id": f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            **result
        }

    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@app.get("/scenarios")
async def get_scenarios():
    """Get all available scenarios"""
    return {
        "scenarios": scenario_manager.get_all_scenarios(),
        "categories": {
            "economic": ["base_case", "minimal_config"],
            "efficiency_focused": ["optimized", "high_efficiency"],
            "power_focused": ["full_cogas"],
            "environmental": ["environmental"]
        }
    }

@app.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get specific scenario details"""
    try:
        scenario = scenario_manager.get_scenario(scenario_id)
        validation = scenario_manager.validate_parameters(scenario.parameters)

        return {
            "scenario": {
                "id": scenario.id,
                "name": scenario.name,
                "description": scenario.description,
                "category": scenario.category,
                "version": scenario.version,
                "created_date": scenario.created_date,
                "parameters": scenario.parameters,
                "expected_performance": scenario.expected_performance,
                "constraints": scenario.constraints
            },
            "validation": validation
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/scenarios/{scenario_id}/calculate")
async def calculate_scenario(scenario_id: str):
    """Calculate performance for a specific scenario"""
    try:
        scenario = scenario_manager.get_scenario(scenario_id)
        params = scenario.parameters

        request = CalculationRequest(
            ambient_temp=params.get("ambient_temp", 298.15),
            pressure_ratio=params.get("pressure_ratio", 12.0),
            max_turbine_temp=params.get("max_turbine_temp", 1400.0),
            compressor_efficiency=params.get("compressor_efficiency", 0.85),
            turbine_efficiency=params.get("turbine_efficiency", 0.88),
            ad_feedstock_rate=params.get("biomass_rate", 3000.0),
            ad_retention_time=params.get("ad_retention_time", 20.0),
            htc_biomass_rate=params.get("htc_biomass_rate", 500.0),
            htc_temperature=params.get("htc_reactor_temp", 473.15),
            scenario=scenario_id
        )

        return await calculate_performance(request)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/economic-analysis")
async def economic_analysis(request: EconomicRequest):
    """Perform comprehensive economic analysis"""
    try:
        params = EconomicParams(
            net_power_kw=request.net_power_kw,
            annual_opex_usd=request.annual_opex_usd,
            annual_revenue_usd=request.annual_revenue_usd,
            project_lifetime=request.project_lifetime,
            discount_rate=request.discount_rate,
            tax_rate=request.tax_rate
        )

        results = economic_analyzer.analyze(params)

        return {
            "timestamp": datetime.now().isoformat(),
            **results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Economic analysis error: {str(e)}")

@app.post("/environmental-analysis")
async def environmental_analysis(request: EnvironmentalRequest):
    """Perform environmental impact analysis"""
    try:
        params = EnvironmentalParams(
            net_power_kw=request.net_power_kw,
            annual_hours=request.annual_hours,
            biomass_rate_kg_day=request.biomass_rate_kg_day,
            hydrochar_rate_kg_day=request.hydrochar_rate_kg_day,
            biogas_production_m3_day=request.biogas_production_m3_day
        )

        results = environmental_analyzer.analyze(params)

        return {
            "timestamp": datetime.now().isoformat(),
            **results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Environmental analysis error: {str(e)}")

@app.post("/thermodynamic-charts")
async def generate_thermodynamic_charts(request: CalculationRequest):
    """Generate thermodynamic chart data (T-s, h-s diagrams)"""
    try:
        # Generate T-s data for Brayton cycle
        ts_data = brayton_engine.generate_ts_data(
            T1=request.ambient_temp,
            P_ratio=request.pressure_ratio,
            T3=request.max_turbine_temp,
            eta_comp=request.compressor_efficiency,
            eta_turb=request.turbine_efficiency
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "brayton_ts": ts_data,
            "chart_types": ["temperature_entropy", "pressure_volume"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart generation error: {str(e)}")

@app.post("/compare-scenarios")
async def compare_scenarios(scenario_ids: List[str]):
    """Compare multiple scenarios"""
    try:
        comparison = scenario_manager.compare_scenarios(scenario_ids)
        return {
            "timestamp": datetime.now().isoformat(),
            **comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")

# ============== Helper Functions ==============

def calculate_overall_performance(gt_results, ad_results, htc_results):
    """Calculate overall system performance"""

    net_power = gt_results.get("net_work_kw", 0)
    biogas_energy = ad_results.get("biogas_energy_output_kw", 0)
    htc_heat_demand = htc_results.get("total_heat_demand_kw", 0)

    waste_heat_available = (ad_results.get("waste_heat_available_kw", 0) + 
                           gt_results.get("exhaust_heat_kw", 0))

    self_sufficiency = (min(waste_heat_available / htc_heat_demand, 1.0) 
                      if htc_heat_demand > 0 else 0.0)

    net_heat_requirement = htc_results.get("net_heat_requirement_kw", 0)

    if biogas_energy > 0:
        overall_efficiency = (net_power + net_heat_requirement) / biogas_energy
    else:
        overall_efficiency = 0

    return {
        "net_power_output_kw": net_power,
        "biogas_energy_input_kw": biogas_energy,
        "htc_heat_demand_kw": htc_heat_demand,
        "waste_heat_available_kw": waste_heat_available,
        "self_sufficiency_ratio": self_sufficiency,
        "overall_efficiency": overall_efficiency,
        "heat_integration_efficiency": (waste_heat_available - max(0, waste_heat_available - htc_heat_demand)) / waste_heat_available if waste_heat_available > 0 else 0
    }

def calculate_energy_flows(gt_results, ad_results, htc_results):
    """Calculate energy flows between subsystems"""

    return {
        "biogas_to_combustor_kw": ad_results.get("biogas_energy_output_kw", 0),
        "gt_exhaust_heat_kw": gt_results.get("exhaust_heat_kw", 0),
        "ad_waste_heat_kw": ad_results.get("waste_heat_available_kw", 0),
        "htc_heat_supply_kw": htc_results.get("total_heat_demand_kw", 0),
        "htc_heat_recovery_kw": htc_results.get("product_heat_recovery_kw", 0),
        "net_electrical_output_kw": gt_results.get("net_work_kw", 0),
        "net_thermal_output_kw": htc_results.get("net_heat_requirement_kw", 0),
        "total_input_energy_kw": ad_results.get("biogas_energy_output_kw", 0)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
