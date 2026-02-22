from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import numpy as np
import math
from datetime import datetime

# Import calculation modules
try:
    from thermodynamics.brayton_cycle import BraytonCycle
    from thermodynamics.ad_system import ADSystem
    from thermodynamics.htc_system import HTCSystem
    from optimization.optimizer import SystemOptimizer
    from economics.economic_analysis import EconomicAnalyzer
    from environmental.environmental_analysis import EnvironmentalAnalyzer
    from scenarios.scenario_manager import ScenarioManager
except ImportError:
    # Fallback for when running as script
    from .thermodynamics.brayton_cycle import BraytonCycle
    from .thermodynamics.ad_system import ADSystem
    from .thermodynamics.htc_system import HTCSystem
    from .optimization.optimizer import SystemOptimizer
    from .economics.economic_analysis import EconomicAnalyzer
    from .environmental.environmental_analysis import EnvironmentalAnalyzer
    from .scenarios.scenario_manager import ScenarioManager

app = FastAPI(
    title="Group 7 - AD-HTC Fuel-Enhanced Gas Power Cycle Analysis",
    description="Professional-grade process flow analysis system for AD-HTC integrated biogas power cycle",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class CalculationRequest(BaseModel):
    ambient_temp: float = 288.0  # K
    pressure_ratio: float = 6.0
    max_turbine_temp: float = 1000.0  # K
    compressor_efficiency: float = 0.85
    turbine_efficiency: float = 0.90
    
    # AD system inputs - now primary for biogas
    ad_feedstock_rate: float = 3000.0  # kg/day total (3 digesters)
    ad_retention_time: float = 20.0  # days
    
    # HTC system inputs
    htc_biomass_rate: float = 500.0  # kg/day
    htc_temperature: float = 473.0  # K (200°C)
    
    scenario: str = "base_case"

class CalculationResponse(BaseModel):
    timestamp: datetime
    scenario: str
    gas_turbine: Dict[str, Any]
    ad_system: Dict[str, Any]
    htc_system: Dict[str, Any]
    overall_performance: Dict[str, Any]
    energy_flows: Dict[str, Any]

# Initialize calculation engines
brayton_engine = BraytonCycle()
ad_engine = ADSystem()
htc_engine = HTCSystem()
optimizer = SystemOptimizer()
economic_analyzer = EconomicAnalyzer()
environmental_analyzer = EnvironmentalAnalyzer()
scenario_manager = ScenarioManager()

@app.get("/")
async def root():
    return {"message": "Group 7 - AD-HTC Fuel-Enhanced Gas Power Cycle Analysis System"}


# ── Analyze endpoint: h-s chart (HTC steam cycle) + T-Ḣ chart (gas cycle) ──

class AnalyzeRequest(BaseModel):
    # Gas cycle inputs
    ambient_temp: float = 298.15       # K
    pressure_ratio: float = 12.0
    max_turbine_temp: float = 1400.0   # K
    compressor_efficiency: float = 0.85
    turbine_efficiency: float = 0.88
    # HTC steam cycle inputs
    boiler_pressure: float = 10.0      # bar
    condenser_pressure: float = 0.1    # bar
    superheat_temp: float = 523.15     # K (250 °C)
    pump_efficiency: float = 0.80
    steam_turbine_efficiency: float = 0.85
    # AD / biomass - these are for feeding into the AD system model directly now
    ad_feedstock_rate: float = 3000.0  # kg/day
    ad_retention_time: float = 20.0
    htc_biomass_rate: float = 500.0
    htc_temperature: float = 473.0     # K


def _htc_steam_cycle_hs(req: AnalyzeRequest):
    """
    Compute h-s state points for a simplified Rankine-type HTC steam cycle.
    States: 1-pump inlet (sat liq @ P_cond), 2-pump outlet (compressed liq @ P_boil),
            3-boiler outlet (superheated steam @ P_boil), 4-turbine outlet (wet/superheat @ P_cond).
    Returns list of {h, s, label} dicts and the isentropic dome curve.
    """
    P_boil = req.boiler_pressure       # bar
    P_cond = req.condenser_pressure     # bar
    eta_p  = req.pump_efficiency
    eta_t  = req.steam_turbine_efficiency

    # ── Simplified steam property helpers (IAPWS-IF97 lite) ──
    # Saturation temperature (°C) as function of pressure (bar)  –  Antoine-type fit
    def T_sat(P):
        # Rough fit valid 0.01–200 bar
        return 100.0 * (P / 1.01325) ** 0.25  # simplified; close enough for plotting

    # Saturated liquid properties at pressure P (bar)
    def sat_liq(P):
        Ts = T_sat(P)
        hf = 4.18 * Ts                           # kJ/kg
        sf = 4.18 * math.log((Ts + 273.15) / 273.15)  # kJ/(kg·K)
        return {"h": round(hf, 2), "s": round(sf, 4), "T": round(Ts, 2)}

    # Saturated vapour properties at pressure P (bar)
    def sat_vap(P):
        Ts = T_sat(P)
        hfg = 2257.0 * (1 - Ts / 374.0) ** 0.38 if Ts < 374 else 0
        hg = 4.18 * Ts + hfg
        sfg = hfg / (Ts + 273.15)
        sg = 4.18 * math.log((Ts + 273.15) / 273.15) + sfg
        return {"h": round(hg, 2), "s": round(sg, 4), "T": round(Ts, 2), "hfg": round(hfg, 2)}

    # Superheated steam properties (rough cp-based estimate above T_sat)
    def superheated(P, T_K):
        T_C = T_K - 273.15
        sv = sat_vap(P)
        Ts = T_sat(P)
        if T_C <= Ts:
            return sv  # not actually superheated
        cp_steam = 2.08  # kJ/(kg·K) average for low-pressure superheat
        h = sv["h"] + cp_steam * (T_C - Ts)
        s = sv["s"] + cp_steam * math.log((T_C + 273.15) / (Ts + 273.15))
        return {"h": round(h, 2), "s": round(s, 4), "T": round(T_C, 2)}

    # ── State 1: saturated liquid at condenser pressure ──
    s1 = sat_liq(P_cond)
    s1["label"] = "1 – Condenser Exit (sat liq)"

    # ── State 2: compressed liquid after pump ──
    v_f = 0.001  # m³/kg  (liquid specific volume ~ constant)
    w_pump_ideal = v_f * (P_boil - P_cond) * 100  # kJ/kg  (bar→kPa)
    w_pump = w_pump_ideal / eta_p
    s2 = {
        "h": round(s1["h"] + w_pump, 2),
        "s": s1["s"],  # isentropic pump (approx)
        "T": round(s1["T"] + w_pump / 4.18, 2),
        "label": "2 – Pump Exit"
    }

    # ── State 3: superheated steam leaving boiler / HTC reactor ──
    s3 = superheated(P_boil, req.superheat_temp)
    s3["label"] = "3 – Boiler/Reactor Exit (superheated)"

    # ── State 4: turbine exit at condenser pressure ──
    # Isentropic expansion: find h4s at P_cond with s4s = s3["s"]
    sf_cond = sat_liq(P_cond)["s"]
    sg_cond = sat_vap(P_cond)["s"]
    if s3["s"] <= sg_cond:
        # Wet expansion
        x4s = (s3["s"] - sf_cond) / (sg_cond - sf_cond) if sg_cond > sf_cond else 1
        hf_cond = sat_liq(P_cond)["h"]
        hfg_cond = sat_vap(P_cond)["hfg"]
        h4s = hf_cond + x4s * hfg_cond
    else:
        # Superheated exit – approximate
        h4s = sat_vap(P_cond)["h"] + 2.08 * (s3["s"] - sg_cond) * (T_sat(P_cond) + 273.15)

    h4 = s3["h"] - eta_t * (s3["h"] - h4s)
    # Find s4 from h4 at P_cond
    hf_c = sat_liq(P_cond)["h"]
    hg_c = sat_vap(P_cond)["h"]
    if h4 <= hg_c:
        x4 = (h4 - hf_c) / (hg_c - hf_c) if hg_c > hf_c else 1
        s4 = sf_cond + x4 * (sg_cond - sf_cond)
    else:
        s4 = sg_cond + (h4 - hg_c) / (T_sat(P_cond) + 273.15)
    s4_pt = {"h": round(h4, 2), "s": round(s4, 4), "T": round(T_sat(P_cond), 2),
             "label": "4 – Turbine Exit"}

    # ── Isentropic dome curve for reference ──
    dome_pressures = [0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 150.0, 200.0, 220.0]
    dome_liq = [{"h": sat_liq(p)["h"], "s": sat_liq(p)["s"]} for p in dome_pressures]
    dome_vap = [{"h": sat_vap(p)["h"], "s": sat_vap(p)["s"]} for p in dome_pressures]
    dome_curve = dome_liq + dome_vap[::-1]  # closed loop

    # ── Process curves (interpolated paths between states) ──
    def interp(a, b, n=20):
        return [{"h": round(a["h"] + (b["h"] - a["h"]) * t / n, 2),
                 "s": round(a["s"] + (b["s"] - a["s"]) * t / n, 4)}
                for t in range(n + 1)]

    pump_path    = interp(s1, s2)          # 1→2 pump
    boiler_path  = interp(s2, s3, 40)      # 2→3 boiler
    turbine_path = interp(s3, s4_pt, 30)   # 3→4 turbine
    cond_path    = interp(s4_pt, s1, 20)   # 4→1 condenser

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


def _gas_cycle_t_hdot(req: AnalyzeRequest):
    """
    Compute T-Ḣ (temperature vs cumulative heat rate) data for the gas Brayton cycle.
    Processes: 1→2 compression, 2→3 combustion heat addition, 3→4 expansion,
               4→1 exhaust/heat rejection.
    Returns list of {T, H_dot, label} for each process.
    """
    T1 = req.ambient_temp
    rp = req.pressure_ratio
    T3 = req.max_turbine_temp
    eta_c = req.compressor_efficiency
    eta_t = req.turbine_efficiency

    gamma_air = 1.4
    cp_air    = 1.005       # kJ/(kg·K)
    gamma_exh = 1.33
    cp_exh    = 1.15        # kJ/(kg·K)

    # State 2 (compressor outlet)
    T2s = T1 * rp ** ((gamma_air - 1) / gamma_air)
    T2  = T1 + (T2s - T1) / eta_c

    # State 4 (turbine outlet)
    T4s = T3 / rp ** ((gamma_exh - 1) / gamma_exh)
    T4  = T3 - eta_t * (T3 - T4s)

    # Cumulative Ḣ (heat rate per unit mass flow, kW per kg/s = kJ/kg)
    # Process 1→2: compression (work input, no external heat ideally – but temperature rises)
    # Process 2→3: heat addition in combustor
    # Process 3→4: expansion (work output)
    # Process 4→1: heat rejection (exhaust)
    # For T-Ḣ diagram we plot T vs cumulative Q transferred

    n = 25  # points per process
    data = []
    H_cum = 0.0

    # Process 1→2: Compression (adiabatic, Q=0, but we show the T rise at constant Ḣ)
    for i in range(n + 1):
        frac = i / n
        T = T1 + (T2 - T1) * frac
        data.append({"T": round(T, 2), "H_dot": round(H_cum, 2),
                     "process": "1→2 Compression"})

    # Process 2→3: Heat addition in combustion chamber (isobaric)
    q_in = cp_exh * (T3 - T2)  # simplified – mixed cp
    for i in range(n + 1):
        frac = i / n
        T = T2 + (T3 - T2) * frac
        H_cum_local = frac * q_in
        data.append({"T": round(T, 2), "H_dot": round(H_cum + H_cum_local, 2),
                     "process": "2→3 Combustion"})
    H_cum += q_in

    # Process 3→4: Expansion (adiabatic, Q=0)
    for i in range(n + 1):
        frac = i / n
        T = T3 + (T4 - T3) * frac
        data.append({"T": round(T, 2), "H_dot": round(H_cum, 2),
                     "process": "3→4 Expansion"})

    # Process 4→1: Heat rejection (exhaust cooling / HRSG)
    q_out = cp_exh * (T4 - T1)
    for i in range(n + 1):
        frac = i / n
        T = T4 + (T1 - T4) * frac
        H_cum_local = frac * q_out
        data.append({"T": round(T, 2), "H_dot": round(H_cum + H_cum_local, 2),
                     "process": "4→1 Heat Rejection"})

    # Performance summary
    w_comp = cp_air * (T2 - T1)
    w_turb = cp_exh * (T3 - T4)
    w_net  = w_turb - w_comp
    eta    = w_net / q_in if q_in > 0 else 0

    return {
        "data": data,
        "states": [
            {"label": "1 – Compressor Inlet", "T": round(T1, 2), "P_bar": round(1.01325, 2)},
            {"label": "2 – Compressor Exit",  "T": round(T2, 2), "P_bar": round(1.01325 * rp, 2)},
            {"label": "3 – Turbine Inlet",    "T": round(T3, 2), "P_bar": round(1.01325 * rp, 2)},
            {"label": "4 – Turbine Exit",     "T": round(T4, 2), "P_bar": round(1.01325, 2)},
        ],
        "performance": {
            "w_comp_kj_kg": round(w_comp, 2),
            "w_turb_kj_kg": round(w_turb, 2),
            "w_net_kj_kg":  round(w_net, 2),
            "q_in_kj_kg":   round(q_in, 2),
            "eta_brayton":  round(eta, 4)
        }
    }


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """Generate h-s chart data for HTC steam cycle and T-Ḣ chart data for gas cycle."""
    try:
        hs_data  = _htc_steam_cycle_hs(req)
        th_data  = _gas_cycle_t_hdot(req)
        return {
            "htc_steam_hs": hs_data,
            "gas_cycle_th": th_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/calculate", response_model=CalculationResponse)
async def calculate_performance(request: CalculationRequest):
    try:
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
        
        return CalculationResponse(
            timestamp=datetime.now(),
            scenario=request.scenario,
            gas_turbine=gt_results,
            ad_system=ad_results,
            htc_system=htc_results,
            overall_performance=overall,
            energy_flows=energy_flows
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@app.get("/presets")
async def get_presets():
    return {
        "base_case": {
            "name": "Base Case",
            "description": "Standard AD-HTC integration with basic parameters",
            "parameters": {
                "ambient_temp": 288.0,
                "pressure_ratio": 6.0,
                "max_turbine_temp": 1000.0,
                "compressor_efficiency": 0.85,
                "turbine_efficiency": 0.90,
                "biomass_rate": 3000.0,
                "ad_retention_time": 20.0,
                "htc_biomass_rate": 500.0,
                "htc_temperature": 473.0
            }
        },
        "optimized": {
            "name": "Optimized AD-HTC",
            "description": "Enhanced heat recovery with 85% self-sufficiency",
            "parameters": {
                "ambient_temp": 288.0,
                "pressure_ratio": 8.0,
                "max_turbine_temp": 1200.0,
                "compressor_efficiency": 0.88,
                "turbine_efficiency": 0.92,
                "biomass_rate": 3000.0,
                "ad_retention_time": 18.0,
                "htc_biomass_rate": 500.0,
                "htc_temperature": 493.0
            }
        },
        "full_cogas": {
            "name": "Full COGAS Future State",
            "description": "Combined cycle with steam turbine and HRSG",
            "parameters": {
                "ambient_temp": 288.0,
                "pressure_ratio": 12.0,
                "max_turbine_temp": 1400.0,
                "compressor_efficiency": 0.90,
                "turbine_efficiency": 0.93,
                "biomass_rate": 3000.0,
                "ad_retention_time": 15.0,
                "htc_biomass_rate": 500.0,
                "htc_temperature": 513.0
            }
        }
    }

@app.post("/optimize")
async def optimize_parameters(objectives: Dict[str, Any]):
    try:
        optimized_params = optimizer.optimize(objectives)
        return {"optimized_parameters": optimized_params}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@app.post("/economic-analysis")
async def economic_analysis(inputs: Dict[str, Any]):
    try:
        results = economic_analyzer.analyze(inputs)
        return {"economic_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Economic analysis error: {str(e)}")

@app.post("/environmental-analysis")
async def environmental_analysis(inputs: Dict[str, Any]):
    try:
        results = environmental_analyzer.analyze(inputs)
        return {"environmental_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Environmental analysis error: {str(e)}")

@app.get("/scenarios")
async def get_scenarios():
    try:
        scenarios = scenario_manager.get_all_scenarios()
        return {"scenarios": scenarios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario retrieval error: {str(e)}")

@app.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    try:
        scenario = scenario_manager.get_scenario(scenario_id)
        return {"scenario": scenario}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario retrieval error: {str(e)}")

@app.post("/scenarios/{scenario_id}/calculate")
async def calculate_scenario(scenario_id: str):
    try:
        scenario = scenario_manager.get_scenario(scenario_id)
        params = scenario['parameters']
        
        # Calculate gas turbine performance
        gt_results = brayton_engine.calculate(
            T1=params.get('ambient_temp', 298.15),
            P_ratio=params.get('pressure_ratio', 12.0),
            T3=params.get('max_turbine_temp', 1400.0),
            eta_comp=params.get('compressor_efficiency', 0.85),
            eta_turb=params.get('turbine_efficiency', 0.88)
        )
        
        # Calculate AD system performance
        ad_results = ad_engine.calculate(
            feedstock_rate=params.get('biomass_rate', 3000.0),
            retention_time=params.get('ad_retention_time', 20.0)
        )
        
        # Calculate HTC system performance
        htc_results = htc_engine.calculate(
            biomass_rate=params.get('biomass_rate', 3000.0) * 0.3,  # 30% to HTC
            reactor_temp=params.get('htc_reactor_temp', 473.15),
            ambient_temp=params.get('ambient_temp', 298.15),
            moisture_content=params.get('biomass_moisture', 0.10)
        )
        
        # Calculate overall performance
        print(f"DEBUG: About to calculate overall performance")
        print(f"DEBUG: GT results: {gt_results}")
        print(f"DEBUG: AD results: {ad_results}")
        print(f"DEBUG: HTC results: {htc_results}")
        overall = calculate_overall_performance(gt_results, ad_results, htc_results)
        print(f"DEBUG: Overall performance calculated: {overall}")
        energy_flows = calculate_energy_flows(gt_results, ad_results, htc_results)
        
        # Economic analysis
        print(f"DEBUG: About to do economic analysis")
        economic_inputs = {
            'net_power_kw': overall.get('net_power_output_kw', 0),
            'annual_opex_usd': overall.get('net_power_output_kw', 0) * 8000 * 0.02,  # $0.02/kWh OPEX
            'annual_revenue_usd': overall.get('net_power_output_kw', 0) * 8000 * 0.12  # $0.12/kWh revenue
        }
        print(f"DEBUG: Economic inputs: {economic_inputs}")
        economic_results = economic_analyzer.analyze(economic_inputs)
        print(f"DEBUG: Economic analysis completed")
        
        # Environmental analysis
        print(f"DEBUG: About to do environmental analysis")
        environmental_inputs = {
            'net_power_kw': overall.get('net_power_output_kw', 0),
            'annual_hours': 8000,
            'biomass_rate_kg_day': params.get('biomass_rate', 3000.0),
            'hydrochar_rate_kg_day': htc_results.get('hydrochar_yield', 0)
        }
        print(f"DEBUG: Environmental inputs: {environmental_inputs}")
        environmental_results = environmental_analyzer.analyze(environmental_inputs)
        print(f"DEBUG: Environmental analysis completed")
        
        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario['name'],
            "gas_turbine": gt_results,
            "ad_system": ad_results,
            "htc_system": htc_results,
            "overall_performance": overall,
            "energy_flows": energy_flows,
            "economic_analysis": economic_results,
            "environmental_analysis": environmental_results,
            "expected_performance": scenario.get('expected_performance', {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario calculation error: {str(e)}")

def calculate_overall_performance(gt_results, ad_results, htc_results):
    """Calculate overall system performance metrics"""
    print(f"DEBUG calculate_overall_performance:")
    print(f"  GT results: {gt_results}")
    print(f"  AD results: {ad_results}")
    print(f"  HTC results: {htc_results}")
    
    net_power = gt_results.get("net_work_kw", 0)
    biogas_energy = ad_results.get("biogas_energy_output_kw", 0)
    htc_heat_demand = htc_results.get("total_heat_demand_kw", 0)
    
    print(f"  net_power: {net_power}")
    print(f"  biogas_energy: {biogas_energy}")
    print(f"  htc_heat_demand: {htc_heat_demand}")
    
    # Calculate self-sufficiency ratio
    waste_heat_available = ad_results.get("waste_heat_available_kw", 0) + gt_results.get("exhaust_heat_kw", 0)
    self_sufficiency = min(waste_heat_available / htc_heat_demand, 1.0) if htc_heat_demand > 0 else (1.0 if waste_heat_available > 0 else 0.0)
    
    # Calculate overall efficiency
    net_heat_requirement = htc_results.get("net_heat_requirement_kw", 0)
    print(f"  net_heat_requirement: {net_heat_requirement}")
    
    if biogas_energy > 0:
        overall_efficiency = (net_power + net_heat_requirement) / biogas_energy
    else:
        print(f"DEBUG: Division by zero prevented! biogas_energy = {biogas_energy}")
        overall_efficiency = 0
    
    return {
        "net_power_output_kw": net_power,
        "biogas_energy_input_kw": biogas_energy,
        "htc_heat_demand_kw": htc_heat_demand,
        "waste_heat_available_kw": waste_heat_available,
        "self_sufficiency_ratio": self_sufficiency,
        "overall_efficiency": overall_efficiency,
        "primary_energy_saving": calculate_pes(net_power, biogas_energy, htc_heat_demand)
    }

def calculate_energy_flows(gt_results, ad_results, htc_results):
    """Calculate energy flows between subsystems"""
    return {
        "biogas_to_combustor_kw": ad_results.get("biogas_energy_output_kw", 0),
        "gt_exhaust_heat_kw": gt_results.get("exhaust_heat", 0),
        "ad_waste_heat_kw": ad_results.get("waste_heat_available_kw", 0),
        "htc_heat_supply_kw": htc_results.get("total_heat_demand_kw", 0),
        "htc_heat_recovery_kw": htc_results.get("product_heat_recovery_kw", 0),
        "net_electrical_output_kw": gt_results.get("net_work", 0),
        "net_thermal_output_kw": htc_results.get("net_heat_requirement_kw", 0)
    }

def calculate_pes(net_power, biogas_energy, thermal_output):
    """Calculate Primary Energy Saving (PES)"""
    # Reference efficiency for separate production
    eta_ref_power = 0.35  # Reference power generation efficiency
    eta_ref_thermal = 0.85  # Reference thermal production efficiency
    
    # Reference fuel consumption for separate production
    ref_fuel_power = net_power / eta_ref_power if net_power > 0 else 0
    ref_fuel_thermal = thermal_output / eta_ref_thermal if thermal_output > 0 else 0
    ref_fuel_total = ref_fuel_power + ref_fuel_thermal
    
    # Actual fuel consumption (biogas energy)
    actual_fuel = biogas_energy
    
    # Primary Energy Saving
    pes = (ref_fuel_total - actual_fuel) / ref_fuel_total if ref_fuel_total > 0 else 0
    
    return pes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)