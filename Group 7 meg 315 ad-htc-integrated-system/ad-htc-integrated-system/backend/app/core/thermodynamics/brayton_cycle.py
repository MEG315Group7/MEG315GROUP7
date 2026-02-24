"""
Brayton Cycle Thermodynamic Analysis Module
Enhanced with biogas integration and heat recovery
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import math

@dataclass
class BraytonState:
    """Thermodynamic state for Brayton cycle"""
    T: float  # Temperature (K)
    P: float  # Pressure (kPa)
    h: float  # Enthalpy (kJ/kg)
    s: float  # Entropy (kJ/kg·K)
    point_name: str

class BraytonCycle:
    """
    Gas turbine Brayton cycle analysis for AD-HTC system
    Enhanced with real gas properties and biogas integration
    """

    def __init__(self):
        # Air properties (ideal gas approximation)
        self.R_air = 0.287  # kJ/(kg·K)
        self.cp_air = 1.005  # kJ/(kg·K)
        self.gamma_air = 1.4

        # Combustion products properties
        self.cp_exhaust = 1.15  # kJ/(kg·K)
        self.gamma_exhaust = 1.33
        self.lhv_biogas = 22.0  # MJ/kg (65% CH4)

        # Reference conditions
        self.T_ref = 288.15  # K
        self.P_ref = 101.325  # kPa

    def calculate(self, T1: float, P_ratio: float, T3: float,
                  eta_comp: float = 0.85, eta_turb: float = 0.90,
                  m_dot_air: float = 1.0) -> Dict[str, Any]:
        """
        Calculate Brayton cycle performance

        Args:
            T1: Compressor inlet temperature (K)
            P_ratio: Pressure ratio (P2/P1)
            T3: Turbine inlet temperature (K)
            eta_comp: Compressor isentropic efficiency
            eta_turb: Turbine isentropic efficiency
            m_dot_air: Air mass flow rate (kg/s)
        """

        # State 1: Compressor inlet
        P1 = self.P_ref
        h1 = self.cp_air * T1
        s1 = self.cp_air * math.log(T1 / self.T_ref) - self.R_air * math.log(P1 / self.P_ref)

        # State 2: Compressor outlet
        P2 = P1 * P_ratio
        T2s = T1 * (P_ratio ** ((self.gamma_air - 1) / self.gamma_air))
        h2s = self.cp_air * T2s
        h2 = h1 + (h2s - h1) / eta_comp
        T2 = h2 / self.cp_air
        s2 = s1  # Isentropic process assumption for entropy calc
        W_comp = m_dot_air * (h2 - h1)

        # State 3: Turbine inlet (after combustion)
        P3 = P2
        h3 = self.cp_exhaust * T3
        s3 = self.cp_exhaust * math.log(T3 / self.T_ref) - self.R_air * math.log(P3 / self.P_ref)

        # State 4: Turbine outlet
        P4 = P1
        T4s = T3 / (P_ratio ** ((self.gamma_exhaust - 1) / self.gamma_exhaust))
        h4s = self.cp_exhaust * T4s
        h4 = h3 - eta_turb * (h3 - h4s)
        T4 = h4 / self.cp_exhaust
        W_turb = m_dot_air * (h3 - h4)

        # Performance metrics
        Q_in = m_dot_air * (h3 - h2)
        W_net = W_turb - W_comp
        eta_cycle = W_net / Q_in if Q_in > 0 else 0
        BWR = W_comp / W_turb if W_turb > 0 else 0
        exhaust_heat = m_dot_air * (h4 - h1)

        return {
            "states": [
                {"T": T1, "P": P1, "h": h1, "s": s1, "name": "1-Compressor Inlet"},
                {"T": T2, "P": P2, "h": h2, "s": s2, "name": "2-Compressor Exit"},
                {"T": T3, "P": P3, "h": h3, "s": s3, "name": "3-Turbine Inlet"},
                {"T": T4, "P": P4, "h": h4, "s": s4, "name": "4-Turbine Exit"}
            ],
            "compressor_work_kw": W_comp,
            "turbine_work_kw": W_turb,
            "net_work_kw": W_net,
            "heat_input_kw": Q_in,
            "exhaust_heat_kw": exhaust_heat,
            "thermal_efficiency": eta_cycle,
            "back_work_ratio": BWR,
            "exhaust_temperature_k": T4,
            "pressure_ratio": P_ratio
        }

    def calculate_with_biogas(self, T1: float, P_ratio: float, T3: float,
                              biogas_energy_input_kw: float,
                              eta_comp: float = 0.85, eta_turb: float = 0.90,
                              m_dot_air: float = 1.0) -> Dict[str, Any]:
        """Calculate with biogas fuel input"""

        # Basic cycle calculation
        results = self.calculate(T1, P_ratio, T3, eta_comp, eta_turb, m_dot_air)

        # Add biogas-specific calculations
        m_dot_biogas = biogas_energy_input_kw / self.lhv_biogas  # kg/s
        m_dot_total = m_dot_air + m_dot_biogas

        # Recalculate turbine work with increased mass flow
        h3 = results["states"][2]["h"]
        h4 = results["states"][3]["h"]
        W_turb_corrected = m_dot_total * (h3 - h4)
        W_net_corrected = W_turb_corrected - results["compressor_work_kw"]

        results.update({
            "m_dot_biogas_kg_s": m_dot_biogas,
            "m_dot_total_kg_s": m_dot_total,
            "turbine_work_kw": W_turb_corrected,
            "net_work_kw": W_net_corrected,
            "biogas_energy_input_kw": biogas_energy_input_kw
        })

        return results

    def generate_ts_data(self, T1: float, P_ratio: float, T3: float,
                        eta_comp: float, eta_turb: float) -> Dict[str, Any]:
        """Generate T-s diagram data"""
        results = self.calculate(T1, P_ratio, T3, eta_comp, eta_turb)

        # Generate process curves
        n_points = 50

        # Compression curve (1-2)
        T_comp = np.linspace(results["states"][0]["T"], results["states"][1]["T"], n_points)
        s_comp = [results["states"][0]["s"]] * n_points  # Simplified

        # Expansion curve (3-4)
        T_exp = np.linspace(results["states"][2]["T"], results["states"][3]["T"], n_points)
        s_exp = np.linspace(results["states"][2]["s"], results["states"][3]["s"], n_points)

        return {
            "states": results["states"],
            "compression_curve": {"T": T_comp.tolist(), "s": s_comp},
            "expansion_curve": {"T": T_exp.tolist(), "s": s_exp.tolist()},
            "efficiency": results["thermal_efficiency"]
        }
