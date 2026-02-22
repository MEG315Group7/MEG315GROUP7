import numpy as np
from typing import Dict, Any
import math

class BraytonCycle:
    """
    Gas turbine Brayton cycle analysis for AD-HTC system
    Based on thermodynamic principles with real gas properties
    """
    
    def __init__(self):
        # Air properties (ideal gas approximation)
        self.R_air = 287.0  # J/(kg·K)
        self.cp_air = 1005.0  # J/(kg·K)
        self.gamma_air = 1.4  # Ratio of specific heats for air
        
        # Combustion products properties
        self.cp_exhaust = 1150.0  # J/(kg·K) - typical for combustion products
        self.gamma_exhaust = 1.33  # Typical for combustion products
        self.lhv_biogas = 22.0e6  # J/kg (Lower Heating Value of biogas, ~22 MJ/kg for 65% CH4)
        
        # Reference conditions
        self.T_ref = 288.15  # K (15°C)
        self.P_ref = 101325  # Pa (1 atm)
    
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
        
        Returns:
            Dictionary with cycle performance metrics
        """
        
        # State 1: Compressor inlet
        P1 = self.P_ref
        h1 = self.cp_air * T1
        
        # State 2s: Compressor outlet (isentropic)
        P2 = P1 * P_ratio
        T2s = T1 * (P_ratio ** ((self.gamma_air - 1) / self.gamma_air))
        h2s = self.cp_air * T2s
        
        # State 2: Compressor outlet (actual)
        h2 = h1 + (h2s - h1) / eta_comp
        T2 = h2 / self.cp_air
        W_comp = m_dot_air * (h2 - h1)  # Compressor work input
        
        # State 3: Turbine inlet (after combustion)
        P3 = P2
        h3 = self.cp_exhaust * T3
        
        # State 4s: Turbine outlet (isentropic)
        P4 = P1
        T4s = T3 / (P_ratio ** ((self.gamma_exhaust - 1) / self.gamma_exhaust))
        h4s = self.cp_exhaust * T4s
        
        # State 4: Turbine outlet (actual)
        h4 = h3 - eta_turb * (h3 - h4s)
        T4 = h4 / self.cp_exhaust
        W_turb = m_dot_air * (h3 - h4)  # Turbine work output
        
        # Heat input from combustion
        Q_in = m_dot_air * (h3 - h2)
        
        # Net work output
        W_net = W_turb - W_comp
        
        # Cycle efficiency
        eta_cycle = W_net / Q_in if Q_in > 0 else 0
        
        # Back-work ratio
        BWR = W_comp / W_turb if W_turb > 0 else 0
        
        # Exhaust heat available for recovery
        exhaust_heat = m_dot_air * (h4 - h1)
        
        # Calculate specific work (per kg of air)
        specific_work = W_net / m_dot_air
        
        # Calculate power output for 100MW plant reference
        # Scale factor based on reference air flow
        reference_power = 100000  # kW (100 MW)
        scale_factor = reference_power / (W_net / 1000) if W_net > 0 else 1
        
        return {
            # State conditions
            "T1": T1, "P1": P1/1000,  # kPa
            "T2": T2, "P2": P2/1000,  # kPa
            "T3": T3, "P3": P3/1000,  # kPa
            "T4": T4, "P4": P4/1000,  # kPa
            
            # Energy flows (per kg/s air)
            "compressor_work_kw": W_comp / 1000,  # kW per kg/s air
            "turbine_work_kw": W_turb / 1000,    # kW per kg/s air
            "net_work_kw": W_net / 1000,         # kW per kg/s air
            "heat_input_kw": Q_in / 1000,        # kW per kg/s air
            "exhaust_heat_kw": exhaust_heat / 1000, # kW per kg/s air
            
            # Performance metrics
            "thermal_efficiency": eta_cycle,
            "back_work_ratio": BWR,
            "specific_work_kj_kg": specific_work / 1000,  # kJ/kg
            
            # Scaled to 100MW plant
            "scaled_air_flow_kg_s": scale_factor,
            "scaled_net_power_mw": reference_power / 1000,  # MW
            
            # Component efficiencies
            "compressor_efficiency": eta_comp,
            "turbine_efficiency": eta_turb,
            
            # Derived parameters
            "exhaust_temperature_k": T4,
            "compression_ratio": P_ratio,
            "temperature_ratio": T3/T1
        }
    
    def calculate_with_biogas(self, T1: float, P_ratio: float, T3: float,
                              biogas_energy_input_kw: float,
                              eta_comp: float = 0.85, eta_turb: float = 0.90,
                              m_dot_air: float = 1.0) -> Dict[str, Any]:
        """
        Calculate Brayton cycle performance with biogas as fuel input.
        
        Args:
            T1: Compressor inlet temperature (K)
            P_ratio: Pressure ratio (P2/P1)
            T3: Turbine inlet temperature (K)
            biogas_energy_input_kw: Energy input from biogas (kW)
            eta_comp: Compressor isentropic efficiency
            eta_turb: Turbine isentropic efficiency
            m_dot_air: Air mass flow rate (kg/s)
        
        Returns:
            Dictionary with cycle performance metrics
        """
        
        # State 1: Compressor inlet
        P1 = self.P_ref
        h1 = self.cp_air * T1
        
        # State 2s: Compressor outlet (isentropic)
        P2 = P1 * P_ratio
        T2s = T1 * (P_ratio ** ((self.gamma_air - 1) / self.gamma_air))
        h2s = self.cp_air * T2s
        
        # State 2: Compressor outlet (actual)
        h2 = h1 + (h2s - h1) / eta_comp
        T2 = h2 / self.cp_air
        W_comp = m_dot_air * (h2 - h1)  # Compressor work input
        
        # Determine biogas mass flow rate from energy input
        # biogas_energy_input_kw is in kJ/s, self.lhv_biogas is in J/kg
        m_dot_biogas = biogas_energy_input_kw * 1000 / self.lhv_biogas  # kg/s
        
        m_dot_total_turbine = m_dot_air + m_dot_biogas # Total mass flow through turbine

        # State 3: Turbine inlet (after combustion)
        # Heat added is directly from biogas combustion
        Q_in_actual = biogas_energy_input_kw * 1000 # Convert kW to J/s

        # Assuming constant specific heat for now, T3 is given. We need to check if T3 is achievable
        # with the given biogas energy input for a certain m_dot_air.
        # This simplification assumes T3 is an achievable design parameter with sufficient biogas.
        h3 = self.cp_exhaust * T3
        
        # State 4s: Turbine outlet (isentropic)
        P4 = P1
        T4s = T3 / (P_ratio ** ((self.gamma_exhaust - 1) / self.gamma_exhaust))
        h4s = self.cp_exhaust * T4s
        
        # State 4: Turbine outlet (actual)
        h4 = h3 - eta_turb * (h3 - h4s)
        T4 = h4 / self.cp_exhaust
        # Turbine work output uses total mass flow
        W_turb = m_dot_total_turbine * (h3 - h4)  # Turbine work output
        
        # Net work output
        W_net = W_turb - W_comp
        
        # Cycle efficiency
        eta_cycle = W_net / (Q_in_actual) if Q_in_actual > 0 else 0
        
        # Back-work ratio
        BWR = W_comp / W_turb if W_turb > 0 else 0
        
        # Exhaust heat available for recovery (based on m_dot_total_turbine)
        # Using T_ref as the reference for available heat
        exhaust_heat = m_dot_total_turbine * self.cp_exhaust * (T4 - T1) # Assuming T1 is ambient for exhaust heat calc
        
        # Calculate specific work (per kg of air)
        # This is a bit tricky with varying mass flow, reporting per kg of initial air
        specific_work = W_net / m_dot_air
        
        # Calculate power output for 100MW plant reference (adjusting scale factor)
        reference_power = 100000  # kW (100 MW)
        scale_factor = reference_power / (W_net / 1000) if W_net > 0 else 1
        
        return {
            # State conditions
            "T1": T1, "P1": P1/1000,  # kPa
            "T2": T2, "P2": P2/1000,  # kPa
            "T3": T3, "P3": P3/1000,  # kPa
            "T4": T4, "P4": P4/1000,  # kPa
            
            # Mass flows
            "m_dot_air_kg_s": m_dot_air,
            "m_dot_biogas_kg_s": m_dot_biogas,
            "m_dot_total_turbine_kg_s": m_dot_total_turbine,

            # Energy flows (kW)
            "compressor_work_kw": W_comp / 1000,  # kW
            "turbine_work_kw": W_turb / 1000,    # kW
            "net_work_kw": W_net / 1000,         # kW
            "heat_input_kw": Q_in_actual / 1000, # kW (from biogas)
            "exhaust_heat_kw": exhaust_heat / 1000, # kW (total exhaust heat)
            
            # Performance metrics
            "thermal_efficiency": eta_cycle,
            "back_work_ratio": BWR,
            "specific_work_kj_kg": specific_work / 1000,  # kJ/kg
            
            # Scaled to 100MW plant
            "scaled_air_flow_kg_s": scale_factor,
            "scaled_net_power_mw": reference_power / 1000,  # MW
            
            # Component efficiencies
            "compressor_efficiency": eta_comp,
            "turbine_efficiency": eta_turb,
            
            # Derived parameters
            "exhaust_temperature_k": T4,
            "compression_ratio": P_ratio,
            "temperature_ratio": T3/T1
        }
    
    def calculate_with_heat_recovery(self, T1: float, P_ratio: float, T3: float,
                                     eta_comp: float = 0.85, eta_turb: float = 0.90,
                                     m_dot_air: float = 1.0, T_stack: float = 443.0) -> Dict[str, Any]:
        """
        Calculate Brayton cycle with heat recovery steam generation
        
        Args:
            T_stack: Stack temperature after heat recovery (K)
        """
        
        # Basic cycle calculation
        # This should ideally call calculate_with_biogas if applicable in a real scenario
        basic_results = self.calculate(T1, P_ratio, T3, eta_comp, eta_turb, m_dot_air)
        
        # Calculate heat recovery potential
        T4 = basic_results["T4"]
        # This exhaust heat calculation still uses m_dot_air, should be m_dot_total_turbine
        exhaust_heat_recovered = m_dot_air * self.cp_exhaust * (T4 - T_stack)
        
        # Update results with heat recovery
        results = basic_results.copy()
        results.update({
            "exhaust_heat_recovered_kw": exhaust_heat_recovered / 1000,
            "stack_temperature_k": T_stack,
            "heat_recovery_efficiency": (T4 - T_stack) / (T4 - T1) if (T4 - T1) > 0 else 0,
            "total_thermal_output_kw": (basic_results["net_work_kw"] + exhaust_heat_recovered/1000)
        })
        
        return results
    
    def optimize_pressure_ratio(self, T1: float, T3: float, eta_comp: float = 0.85, 
                               eta_turb: float = 0.90, m_dot_air: float = 1.0) -> Dict[str, Any]:
        """
        Find optimal pressure ratio for maximum efficiency
        """
        
        P_ratios = np.linspace(3, 25, 50)
        efficiencies = []
        net_works = []
        
        for P_ratio in P_ratios:
            # This should ideally call calculate_with_biogas if applicable in a real scenario
            results = self.calculate(T1, P_ratio, T3, eta_comp, eta_turb, m_dot_air)
            efficiencies.append(results["thermal_efficiency"])
            net_works.append(results["net_work_kw"])
        
        max_efficiency_idx = np.argmax(efficiencies)
        optimal_pr = P_ratios[max_efficiency_idx]
        max_efficiency = efficiencies[max_efficiency_idx]
        
        return {
            "optimal_pressure_ratio": optimal_pr,
            "max_efficiency": max_efficiency,
            "corresponding_net_work_kw": net_works[max_efficiency_idx],
            "pressure_ratios": P_ratios.tolist(),
            "efficiencies": efficiencies,
            "net_works": net_works
        }