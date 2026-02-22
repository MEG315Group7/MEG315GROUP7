# improved_main.py - Enhanced version of main.py with better functionality
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import numpy as np
import math
from datetime import datetime
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import calculation modules with better error handling
try:
    from thermodynamics.brayton_cycle import BraytonCycle
    from thermodynamics.ad_system import ADSystem
    from thermodynamics.htc_system import HTCSystem
    from optimization.optimizer import SystemOptimizer
    from economics.economic_analysis import EconomicAnalyzer
    from environmental.environmental_analysis import EnvironmentalAnalyzer
    from scenarios.scenario_manager import ScenarioManager
except ImportError as e:
    logger.warning(f"Import error: {e}. Using local imports...")
    from brayton_cycle import BraytonCycle
    from ad_system import ADSystem
    from htc_system import HTCSystem
    from optimizer import SystemOptimizer
    from economic_analysis import EconomicAnalyzer
    from environmental_analysis import EnvironmentalAnalyzer
    from scenario_manager import ScenarioManager

# Enhanced FastAPI app with better documentation
app = FastAPI(
    title="AD-HTC Fuel-Enhanced Gas Power Cycle Analysis",
    description="""
    Professional-grade process flow analysis system for AD-HTC integrated biogas power cycle.
    
    ## Features
    
    * **Thermodynamic Analysis**: Brayton cycle, AD system, HTC system calculations
    * **Optimization**: Multi-objective optimization using genetic algorithms, gradient descent, and Pareto frontier
    * **Economic Analysis**: NPV, LCOE, CAPEX/OPEX calculations
    * **Environmental Analysis**: Carbon footprint, emissions, sustainability metrics
    * **Scenario Management**: Predefined and custom scenarios for comparison
    
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
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"]
)

# Request/Response Models with validation
class CalculationRequest(BaseModel):
    ambient_temp: float = Field(288.0, ge=273.0, le=323.0, description="Ambient temperature in Kelvin")
    pressure_ratio: float = Field(6.0, ge=3.0, le=25.0, description="Compressor pressure ratio")
    max_turbine_temp: float = Field(1000.0, ge=800.0, le=1600.0, description="Maximum turbine inlet temperature (K)")
    compressor_efficiency: float = Field(0.85, ge=0.75, le=0.95, description="Compressor isentropic efficiency")
    turbine_efficiency: float = Field(0.90, ge=0.80, le=0.95, description="Turbine isentropic efficiency")
    ad_feedstock_rate: float = Field(3000.0, ge=1000.0, le=10000.0, description="AD feedstock rate (kg/day)")
    ad_retention_time: float = Field(20.0, ge=10.0, le=40.0, description="AD retention time (days)")
    htc_biomass_rate: float = Field(500.0, ge=100.0, le=2000.0, description="HTC biomass rate (kg/day)")
    htc_temperature: float = Field(473.0, ge=423.0, le=573.0, description="HTC reactor temperature (K)")
    scenario: str = Field("base_case", description="Scenario identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "ambient_temp": 298.15,
                "pressure_ratio": 12.0,
                "max_turbine_temp": 1400.0,
                "compressor_efficiency": 0.85,
                "turbine_efficiency": 0.88,
                "ad_feedstock_rate": 3000.0,
                "ad_retention_time": 20.0,
                "htc_biomass_rate": 500.0,
                "htc_temperature": 473.0,
                "scenario": "base_case"
            }
        }

class OptimizationRequest(BaseModel):
    objectives: Dict[str, Any] = Field(..., description="Optimization objectives and weights")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Optional constraints")
    method: str = Field("genetic", pattern="^(genetic|gradient|pareto)$")

class AnalysisResponse(BaseModel):
    timestamp: datetime
    scenario: str
    gas_turbine: Dict[str, Any]
    ad_system: Dict[str, Any]
    htc_system: Dict[str, Any]
    overall_performance: Dict[str, Any]
    energy_flows: Dict[str, Any]
    economic_analysis: Optional[Dict[str, Any]] = None
    environmental_analysis: Optional[Dict[str, Any]] = None

# Initialize calculation engines with caching
class CalculationCache:
    def __init__(self):
        self.cache = {}
        self.max_size = 100
    
    def get_key(self, params: dict) -> str:
        return hash(str(sorted(params.items())))
    
    def get(self, params: dict):
        key = self.get_key(params)
        return self.cache.get(key)
    
    def set(self, params: dict, result: dict):
        key = self.get_key(params)
        if len(self.cache) >= self.max_size:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = result

cache = CalculationCache()
brayton_engine = BraytonCycle()
ad_engine = ADSystem()
htc_engine = HTCSystem()
optimizer = SystemOptimizer()
economic_analyzer = EconomicAnalyzer()
environmental_analyzer = EnvironmentalAnalyzer()
scenario_manager = ScenarioManager()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "2.1.0",
        "components": {
            "brayton_cycle": "ready",
            "ad_system": "ready",
            "htc_system": "ready",
            "optimizer": "ready"
        }
    }

# Root endpoint - serve the HTML frontend
@app.get("/")
async def root():
    return FileResponse("index.html")

# Enhanced calculate endpoint with caching and background processing
@app.post("/calculate", response_model=AnalysisResponse)
async def calculate_performance(request: CalculationRequest, background_tasks: BackgroundTasks):
    start_time = datetime.now()
    
    try:
        # Check cache
        cached = cache.get(request.dict())
        if cached:
            logger.info("Returning cached result")
            return cached
        
        # Calculate gas turbine performance
        gt_results = brayton_engine.calculate(
            T1=request.ambient_temp,
            P_ratio=request.pressure_ratio,
            T3=request.max_turbine_temp,
            eta_comp=request.compressor_efficiency,
            eta_turb=request.turbine_efficiency
        )
        
        # Calculate AD system performance
        ad_results = ad_engine.calculate(
            feedstock_rate=request.ad_feedstock_rate,
            retention_time=request.ad_retention_time,
            num_digesters=3
        )
        
        # Calculate HTC system performance
        htc_results = htc_engine.calculate(
            biomass_rate=request.htc_biomass_rate,
            reactor_temp=request.htc_temperature,
            ambient_temp=request.ambient_temp
        )
        
        # Calculate overall performance
        overall = calculate_overall_performance(gt_results, ad_results, htc_results)
        
        # Calculate energy flows
        energy_flows = calculate_energy_flows(gt_results, ad_results, htc_results)
        
        # Background economic and environmental analysis
        economic_results = None
        environmental_results = None
        
        def run_background_analysis():
            try:
                economic_inputs = {
                    'net_power_kw': overall.get('net_power_output_kw', 0),
                    'annual_opex_usd': overall.get('net_power_output_kw', 0) * 8000 * 0.02,
                    'annual_revenue_usd': overall.get('net_power_output_kw', 0) * 8000 * 0.12
                }
                economic_analyzer.analyze(economic_inputs)
                
                environmental_inputs = {
                    'net_power_kw': overall.get('net_power_output_kw', 0),
                    'annual_hours': 8000,
                    'biomass_rate_kg_day': request.ad_feedstock_rate,
                    'hydrochar_rate_kg_day': htc_results.get('hydrochar_rate_kg_day', 0)
                }
                environmental_analyzer.analyze(environmental_inputs)
            except Exception as e:
                logger.error(f"Background analysis error: {e}")
        
        background_tasks.add_task(run_background_analysis)
        
        response = AnalysisResponse(
            timestamp=datetime.now(),
            scenario=request.scenario,
            gas_turbine=gt_results,
            ad_system=ad_results,
            htc_system=htc_results,
            overall_performance=overall,
            energy_flows=energy_flows,
            economic_analysis=economic_results,
            environmental_analysis=environmental_results
        )
        
        # Cache result
        cache.set(request.dict(), response)
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Calculation completed in {process_time:.3f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

# Enhanced analyze endpoint for thermodynamic charts
@app.post("/analyze")
async def analyze_thermodynamics(request: CalculationRequest):
    """Generate h-s chart data for HTC steam cycle and T-Ḣ chart data for gas cycle."""
    try:
        hs_data = _htc_steam_cycle_hs(request)
        th_data = _gas_cycle_t_hdot(request)
        
        return {
            "htc_steam_hs": hs_data,
            "gas_cycle_th": th_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

# Enhanced presets endpoint
@app.get("/presets")
async def get_presets():
    """Get all available preset scenarios with detailed parameters."""
    return {
        "scenarios": scenario_manager.get_all_scenarios(),
        "categories": {
            "efficiency_focused": ["optimized", "high_efficiency"],
            "power_focused": ["full_cogas", "max_power"],
            "economic": ["base_case", "minimal_config"],
            "environmental": ["environmental", "sustainable"]
        }
    }

# Enhanced optimization endpoint
@app.post("/optimize")
async def optimize_parameters(request: OptimizationRequest):
    """Run multi-objective optimization with specified method and constraints."""
    try:
        logger.info(f"Starting optimization with method: {request.method}")
        
        result = optimizer.optimize(
            objectives=request.objectives,
            constraints=request.constraints,
            method=request.method
        )
        
        # Add metadata
        result["optimization_id"] = f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result["timestamp"] = datetime.now().isoformat()
        result["requested_method"] = request.method
        
        return result
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

# Enhanced scenarios endpoints
@app.get("/scenarios")
async def get_scenarios():
    """Get all available scenarios."""
    try:
        scenarios = scenario_manager.get_all_scenarios()
        return {
            "scenarios": scenarios,
            "count": len(scenarios),
            "categories": list(set(s.get('category', 'general') for s in scenarios.values()))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario retrieval error: {str(e)}")

@app.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get specific scenario details."""
    try:
        scenario = scenario_manager.get_scenario(scenario_id)
        return {
            "scenario": scenario,
            "validation": scenario_manager.validate_parameters(scenario.get('parameters', {}))
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario retrieval error: {str(e)}")

@app.post("/scenarios/{scenario_id}/calculate")
async def calculate_scenario(scenario_id: str, background_tasks: BackgroundTasks):
    """Calculate performance for a specific scenario with full analysis."""
    try:
        scenario = scenario_manager.get_scenario(scenario_id)
        params = scenario['parameters']
        
        # Create calculation request from scenario
        request = CalculationRequest(
            ambient_temp=params.get('ambient_temp', 298.15),
            pressure_ratio=params.get('pressure_ratio', 12.0),
            max_turbine_temp=params.get('max_turbine_temp', 1400.0),
            compressor_efficiency=params.get('compressor_efficiency', 0.85),
            turbine_efficiency=params.get('turbine_efficiency', 0.88),
            ad_feedstock_rate=params.get('biomass_rate', 3000.0),
            ad_retention_time=params.get('ad_retention_time', 20.0),
            htc_biomass_rate=params.get('biomass_rate', 3000.0) * 0.3,
            htc_temperature=params.get('htc_reactor_temp', 473.15),
            scenario=scenario_id
        )
        
        # Run calculation
        result = await calculate_performance(request, background_tasks)
        
        # Add scenario metadata
        return {
            **result.dict(),
            "scenario_metadata": {
                "name": scenario['name'],
                "description": scenario['description'],
                "expected_performance": scenario.get('expected_performance', {})
            }
        }
        
    except Exception as e:
        logger.error(f"Scenario calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Scenario calculation error: {str(e)}")

# Enhanced economic analysis endpoint
@app.post("/economic-analysis")
async def economic_analysis(inputs: Dict[str, Any]):
    """Perform comprehensive economic analysis."""
    try:
        results = economic_analyzer.analyze(inputs)
        
        # Add sensitivity analysis
        sensitivity = {
            "discount_rate_variation": {
                "0.06": economic_analyzer.analyze({**inputs, "discount_rate": 0.06}),
                "0.08": results,
                "0.10": economic_analyzer.analyze({**inputs, "discount_rate": 0.10})
            }
        }
        
        return {
            "economic_results": results,
            "sensitivity_analysis": sensitivity,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Economic analysis error: {str(e)}")

# Enhanced environmental analysis endpoint
@app.post("/environmental-analysis")
async def environmental_analysis(inputs: Dict[str, Any]):
    """Perform comprehensive environmental impact analysis."""
    try:
        results = environmental_analyzer.analyze(inputs)
        
        # Calculate additional metrics
        carbon_footprint = results.get('net_emissions_ton_co2_eq_year', 0)
        power_output = inputs.get('net_power_kw', 0)
        
        if power_output > 0:
            results['carbon_intensity_g_kwh'] = (carbon_footprint * 1000) / (power_output * 8000 / 1000)
        
        return {
            "environmental_results": results,
            "benchmarks": {
                "coal_plant": 820,  # g CO2/kWh
                "natural_gas": 490,  # g CO2/kWh
                "solar_pv": 48,     # g CO2/kWh
                "this_system": results.get('carbon_intensity_g_kwh', 0)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Environmental analysis error: {str(e)}")

# Comparison endpoint
@app.post("/compare")
async def compare_scenarios(scenario_ids: List[str]):
    """Compare multiple scenarios side by side."""
    try:
        comparison = scenario_manager.compare_scenarios(scenario_ids)
        
        # Calculate relative improvements
        if len(scenario_ids) >= 2:
            base = comparison[scenario_ids[0]]['expected_performance']
            for sid in scenario_ids[1:]:
                current = comparison[sid]['expected_performance']
                comparison[sid]['improvements'] = {
                    k: ((current.get(k, 0) - base.get(k, 0)) / base.get(k, 1) * 100) 
                    for k in base.keys() if isinstance(base.get(k), (int, float))
                }
        
        return {
            "comparison": comparison,
            "scenarios_compared": len(scenario_ids),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")

# Helper functions (same as original but with improvements)
def _htc_steam_cycle_hs(req):
    """Compute h-s state points for HTC steam cycle."""
    P_boil = req.boiler_pressure if hasattr(req, 'boiler_pressure') else 10.0
    P_cond = req.condenser_pressure if hasattr(req, 'condenser_pressure') else 0.1
    eta_p = req.pump_efficiency if hasattr(req, 'pump_efficiency') else 0.80
    eta_t = req.steam_turbine_efficiency if hasattr(req, 'steam_turbine_efficiency') else 0.85

    def T_sat(P):
        return 100.0 * (P / 1.01325) ** 0.25

    def sat_liq(P):
        Ts = T_sat(P)
        hf = 4.18 * Ts
        sf = 4.18 * math.log((Ts + 273.15) / 273.15)
        return {"h": round(hf, 2), "s": round(sf, 4), "T": round(Ts, 2)}

    def sat_vap(P):
        Ts = T_sat(P)
        hfg = 2257.0 * (1 - Ts / 374.0) ** 0.38 if Ts < 374 else 0
        hg = 4.18 * Ts + hfg
        sfg = hfg / (Ts + 273.15)
        sg = 4.18 * math.log((Ts + 273.15) / 273.15) + sfg
        return {"h": round(hg, 2), "s": round(sg, 4), "T": round(Ts, 2), "hfg": round(hfg, 2)}

    def superheated(P, T_K):
        T_C = T_K - 273.15
        sv = sat_vap(P)
        Ts = T_sat(P)
        if T_C <= Ts:
            return sv
        cp_steam = 2.08
        h = sv["h"] + cp_steam * (T_C - Ts)
        s = sv["s"] + cp_steam * math.log((T_C + 273.15) / (Ts + 273.15))
        return {"h": round(h, 2), "s": round(s, 4), "T": round(T_C, 2)}

    s1 = sat_liq(P_cond)
    s1["label"] = "1 – Condenser Exit (sat liq)"

    v_f = 0.001
    w_pump_ideal = v_f * (P_boil - P_cond) * 100
    w_pump = w_pump_ideal / eta_p
    s2 = {
        "h": round(s1["h"] + w_pump, 2),
        "s": s1["s"],
        "T": round(s1["T"] + w_pump / 4.18, 2),
        "label": "2 – Pump Exit"
    }

    superheat_temp = req.superheat_temp if hasattr(req, 'superheat_temp') else 523.15
    s3 = superheated(P_boil, superheat_temp)
    s3["label"] = "3 – Boiler/Reactor Exit (superheated)"

    sf_cond = sat_liq(P_cond)["s"]
    sg_cond = sat_vap(P_cond)["s"]
    if s3["s"] <= sg_cond:
        x4s = (s3["s"] - sf_cond) / (sg_cond - sf_cond) if sg_cond > sf_cond else 1
        hf_cond = sat_liq(P_cond)["h"]
        hfg_cond = sat_vap(P_cond)["hfg"]
        h4s = hf_cond + x4s * hfg_cond
    else:
        h4s = sat_vap(P_cond)["h"] + 2.08 * (s3["s"] - sg_cond) * (T_sat(P_cond) + 273.15)

    h4 = s3["h"] - eta_t * (s3["h"] - h4s)
    hf_c = sat_liq(P_cond)["h"]
    hg_c = sat_vap(P_cond)["h"]
    if h4 <= hg_c:
        x4 = (h4 - hf_c) / (hg_c - hf_c) if hg_c > hf_c else 1
        s4 = sf_cond + x4 * (sg_cond - sf_cond)
    else:
        s4 = sg_cond + (h4 - hg_c) / (T_sat(P_cond) + 273.15)
    s4_pt = {"h": round(h4, 2), "s": round(s4, 4), "T": round(T_sat(P_cond), 2),
             "label": "4 – Turbine Exit"}

    dome_pressures = [0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 150.0, 200.0, 220.0]
    dome_liq = [{"h": sat_liq(p)["h"], "s": sat_liq(p)["s"]} for p in dome_pressures]
    dome_vap = [{"h": sat_vap(p)["h"], "s": sat_vap(p)["s"]} for p in dome_pressures]
    dome_curve = dome_liq + dome_vap[::-1]

    def interp(a, b, n=20):
        return [{"h": round(a["h"] + (b["h"] - a["h"]) * t / n, 2),
                 "s": round(a["s"] + (b["s"] - a["s"]) * t / n, 4)}
                for t in range(n + 1)]

    pump_path = interp(s1, s2)
    boiler_path = interp(s2, s3, 40)
    turbine_path = interp(s3, s4_pt, 30)
    cond_path = interp(s4_pt, s1, 20)
    cycle_path = pump_path + boiler_path[1:] + turbine_path[1:] + cond_path[1:]

    w_turbine = s3["h"] - h4
    w_net = w_turbine - w_pump
    q_in = s3["h"] - s2["h"]
    eta_cycle = w_net / q_in if q_in > 0 else 0

    return {
        "states": [s1, s2, s3, s4_pt],
        "cycle_path": cycle_path,
        "dome_curve": dome_curve,
        "performance": {
            "w_pump_kj_kg": round(w_pump, 2),
            "w_turbine_kj_kg": round(w_turbine, 2),
            "w_net_kj_kg": round(w_net, 2),
            "q_in_kj_kg": round(q_in, 2),
            "eta_cycle": round(eta_cycle, 4)
        }
    }

def _gas_cycle_t_hdot(req):
    """Compute T-Ḣ data for gas Brayton cycle."""
    T1 = req.ambient_temp
    rp = req.pressure_ratio
    T3 = req.max_turbine_temp
    eta_c = req.compressor_efficiency
    eta_t = req.turbine_efficiency

    gamma_air = 1.4
    cp_air = 1.005
    gamma_exh = 1.33
    cp_exh = 1.15

    T2s = T1 * rp ** ((gamma_air - 1) / gamma_air)
    T2 = T1 + (T2s - T1) / eta_c

    T4s = T3 / rp ** ((gamma_exh - 1) / gamma_exh)
    T4 = T3 - eta_t * (T3 - T4s)

    n = 25
    data = []
    H_cum = 0.0

    for i in range(n + 1):
        frac = i / n
        T = T1 + (T2 - T1) * frac
        data.append({"T": round(T, 2), "H_dot": round(H_cum, 2), "process": "1→2 Compression"})

    q_in = cp_exh * (T3 - T2)
    for i in range(n + 1):
        frac = i / n
        T = T2 + (T3 - T2) * frac
        H_cum_local = frac * q_in
        data.append({"T": round(T, 2), "H_dot": round(H_cum + H_cum_local, 2), "process": "2→3 Combustion"})
    H_cum += q_in

    for i in range(n + 1):
        frac = i / n
        T = T3 + (T4 - T3) * frac
        data.append({"T": round(T, 2), "H_dot": round(H_cum, 2), "process": "3→4 Expansion"})

    q_out = cp_exh * (T4 - T1)
    for i in range(n + 1):
        frac = i / n
        T = T4 + (T1 - T4) * frac
        H_cum_local = frac * q_out
        data.append({"T": round(T, 2), "H_dot": round(H_cum + H_cum_local, 2), "process": "4→1 Heat Rejection"})

    w_comp = cp_air * (T2 - T1)
    w_turb = cp_exh * (T3 - T4)
    w_net = w_turb - w_comp
    eta = w_net / q_in if q_in > 0 else 0

    return {
        "data": data,
        "states": [
            {"label": "1 – Compressor Inlet", "T": round(T1, 2), "P_bar": round(1.01325, 2)},
            {"label": "2 – Compressor Exit", "T": round(T2, 2), "P_bar": round(1.01325 * rp, 2)},
            {"label": "3 – Turbine Inlet", "T": round(T3, 2), "P_bar": round(1.01325 * rp, 2)},
            {"label": "4 – Turbine Exit", "T": round(T4, 2), "P_bar": round(1.01325, 2)},
        ],
        "performance": {
            "w_comp_kj_kg": round(w_comp, 2),
            "w_turb_kj_kg": round(w_turb, 2),
            "w_net_kj_kg": round(w_net, 2),
            "q_in_kj_kg": round(q_in, 2),
            "eta_brayton": round(eta, 4)
        }
    }

def calculate_overall_performance(gt_results, ad_results, htc_results):
    """Calculate overall system performance metrics with improved error handling."""
    try:
        net_power = gt_results.get("net_work_kw", 0)
        biogas_energy = ad_results.get("biogas_energy_output_kw", 0)
        htc_heat_demand = htc_results.get("total_heat_demand_kw", 0)
        
        waste_heat_available = ad_results.get("waste_heat_available_kw", 0) + gt_results.get("exhaust_heat_kw", 0)
        self_sufficiency = min(waste_heat_available / htc_heat_demand, 1.0) if htc_heat_demand > 0 else (1.0 if waste_heat_available > 0 else 0.0)
        
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
            "primary_energy_saving": calculate_pes(net_power, biogas_energy, htc_heat_demand),
            "heat_integration_efficiency": (waste_heat_available - max(0, waste_heat_available - htc_heat_demand)) / waste_heat_available if waste_heat_available > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error in overall performance calculation: {e}")
        return {
            "net_power_output_kw": 0,
            "biogas_energy_input_kw": 0,
            "htc_heat_demand_kw": 0,
            "waste_heat_available_kw": 0,
            "self_sufficiency_ratio": 0,
            "overall_efficiency": 0,
            "primary_energy_saving": 0,
            "heat_integration_efficiency": 0,
            "error": str(e)
        }

def calculate_energy_flows(gt_results, ad_results, htc_results):
    """Calculate energy flows between subsystems."""
    return {
        "biogas_to_combustor_kw": ad_results.get("biogas_energy_output_kw", 0),
        "gt_exhaust_heat_kw": gt_results.get("exhaust_heat_kw", 0) or gt_results.get("exhaust_heat", 0),
        "ad_waste_heat_kw": ad_results.get("waste_heat_available_kw", 0),
        "htc_heat_supply_kw": htc_results.get("total_heat_demand_kw", 0),
        "htc_heat_recovery_kw": htc_results.get("product_heat_recovery_kw", 0),
        "net_electrical_output_kw": gt_results.get("net_work_kw", 0) or gt_results.get("net_work", 0),
        "net_thermal_output_kw": htc_results.get("net_heat_requirement_kw", 0),
        "total_input_energy_kw": ad_results.get("biogas_energy_output_kw", 0),
        "total_useful_output_kw": (gt_results.get("net_work_kw", 0) or 0) + (htc_results.get("net_heat_requirement_kw", 0) or 0)
    }

def calculate_pes(net_power, biogas_energy, thermal_output):
    """Calculate Primary Energy Saving (PES)."""
    eta_ref_power = 0.35
    eta_ref_thermal = 0.85
    
    ref_fuel_power = net_power / eta_ref_power if net_power > 0 else 0
    ref_fuel_thermal = thermal_output / eta_ref_thermal if thermal_output > 0 else 0
    ref_fuel_total = ref_fuel_power + ref_fuel_thermal
    
    actual_fuel = biogas_energy
    
    pes = (ref_fuel_total - actual_fuel) / ref_fuel_total if ref_fuel_total > 0 else 0
    
    return pes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)