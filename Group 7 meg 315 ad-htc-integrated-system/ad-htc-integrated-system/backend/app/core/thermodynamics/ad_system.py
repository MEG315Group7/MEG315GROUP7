"""
Anaerobic Digestion System Analysis Module
Enhanced biogas production calculations
"""

import numpy as np
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ADConfig:
    """AD system configuration"""
    feedstock_rate: float  # kg/day
    retention_time: float  # days
    temperature: float  # K
    num_digesters: int = 3
    vs_content: float = 0.60

class ADSystem:
    """
    Anaerobic Digestion system for biogas production
    Based on Buswell equation and empirical models
    """

    def __init__(self):
        # Biogas composition
        self.CH4_fraction = 0.65
        self.CO2_fraction = 0.35

        # Heating values
        self.LHV_CH4 = 35.8  # MJ/m³
        self.biogas_density = 1.15  # kg/m³

        # Process parameters
        self.vs_reduction_efficiency = 0.75
        self.biogas_yield_per_vs = 0.8  # m³/kg VS
        self.heat_recovery_efficiency = 0.65

        # Reference conditions
        self.STP_temp = 273.15
        self.STP_pressure = 101325

    def calculate(self, config: ADConfig) -> Dict[str, Any]:
        """
        Calculate AD system performance

        Args:
            config: ADConfig with system parameters
        """

        # Per-digester calculations
        feedstock_per_digester = config.feedstock_rate / config.num_digesters
        digester_volume = feedstock_per_digester * config.retention_time / 1000

        # Volatile solids
        vs_input_total = config.feedstock_rate * config.vs_content
        vs_input_per_digester = vs_input_total / config.num_digesters

        # Biogas production
        vs_destroyed = vs_input_total * self.vs_reduction_efficiency
        biogas_production = vs_destroyed * self.biogas_yield_per_vs

        # Composition
        ch4_production = biogas_production * self.CH4_fraction
        co2_production = biogas_production * self.CO2_fraction

        # Energy content
        biogas_lhv = self.CH4_fraction * self.LHV_CH4
        biogas_energy = biogas_production * biogas_lhv
        biogas_energy_kw = biogas_energy * 1000 / 86400

        # Mass flows
        ch4_mass_flow = ch4_production * 0.717  # kg/day
        co2_mass_flow = co2_production * 1.977  # kg/day

        # Heat integration
        waste_heat_available = biogas_energy_kw * 0.65

        # Digester heating
        feedstock_temp = 288.0
        digester_temp = config.temperature
        specific_heat = 4.2  # kJ/(kg·K)
        heating_demand = (config.feedstock_rate * specific_heat * 
                         (digester_temp - feedstock_temp) / 86400)

        # Environmental
        carbon_in_ch4 = ch4_mass_flow * 0.75
        carbon_in_co2 = co2_mass_flow * 0.273
        total_carbon = carbon_in_ch4 + carbon_in_co2
        co2_equivalent = co2_mass_flow + ch4_mass_flow * 25

        # Digestate
        digestate_production = config.feedstock_rate - vs_destroyed

        return {
            "config": {
                "feedstock_rate_kg_day": config.feedstock_rate,
                "retention_time_days": config.retention_time,
                "temperature_k": config.temperature,
                "num_digesters": config.num_digesters,
                "vs_content": config.vs_content
            },
            "digester_volume_m3": digester_volume,
            "total_digester_volume_m3": digester_volume * config.num_digesters,

            "biogas_production_m3_day": biogas_production,
            "ch4_production_m3_day": ch4_production,
            "co2_production_m3_day": co2_production,
            "ch4_fraction": self.CH4_fraction,

            "biogas_energy_output_mj_day": biogas_energy,
            "biogas_energy_output_kw": biogas_energy_kw,

            "ch4_mass_flow_kg_day": ch4_mass_flow,
            "co2_mass_flow_kg_day": co2_mass_flow,
            "vs_destroyed_kg_day": vs_destroyed,

            "waste_heat_available_kw": waste_heat_available,
            "digester_heating_demand_kw": heating_demand,
            "net_heat_available_kw": max(0, waste_heat_available - heating_demand),

            "carbon_content_kg_day": total_carbon,
            "co2_equivalent_emissions_kg_day": co2_equivalent,
            "digestate_production_kg_day": digestate_production,

            "biogas_yield_m3_kg_vs": biogas_production / vs_input_total if vs_input_total > 0 else 0,
            "energy_yield_mj_kg_feedstock": biogas_energy / config.feedstock_rate if config.feedstock_rate > 0 else 0
        }

    def calculate_kinetics(self, temperature: float, ph: float = 7.0) -> Dict[str, float]:
        """Calculate AD kinetics"""
        T_ref = 308.0
        Ea = 50000  # J/mol
        R = 8.314

        temp_factor = np.exp((Ea/R) * (1/T_ref - 1/temperature))
        ph_optimum = 7.0
        ph_factor = np.exp(-0.5 * ((ph - ph_optimum) / 0.5)**2)

        overall_factor = temp_factor * ph_factor

        return {
            "temperature_correction_factor": temp_factor,
            "ph_correction_factor": ph_factor,
            "overall_correction_factor": overall_factor,
            "corrected_growth_rate_1_day": 0.2 * overall_factor
        }
