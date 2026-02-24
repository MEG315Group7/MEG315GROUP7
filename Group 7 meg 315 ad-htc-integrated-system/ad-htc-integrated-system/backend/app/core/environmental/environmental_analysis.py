"""
Environmental Impact Analysis Module
"""

import numpy as np
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class EnvironmentalParams:
    """Environmental analysis parameters"""
    net_power_kw: float
    annual_hours: float = 8000
    biomass_rate_kg_day: float = 3000
    hydrochar_rate_kg_day: float = 300
    biogas_production_m3_day: float = 0

class EnvironmentalAnalyzer:
    """
    Environmental impact analysis for AD-HTC system
    Carbon footprint, emissions, sustainability metrics
    """

    def __init__(self):
        # Emission factors (kg CO2/kWh)
        self.emission_factors = {
            'natural_gas': 0.202,
            'coal': 0.337,
            'grid_electricity': 0.450,
            'biogas': 0.000,  # Biogenic CO2 is neutral
            'diesel': 0.267
        }

        # Global warming potentials
        self.gwp = {
            'co2': 1.0,
            'ch4': 25.0,
            'n2o': 298.0
        }

        # Carbon sequestration factors
        self.hydrochar_carbon_content = 0.75
        self.stable_carbon_fraction = 0.8

    def analyze(self, params: EnvironmentalParams) -> Dict[str, Any]:
        """
        Perform environmental analysis

        Args:
            params: EnvironmentalParams with system data
        """

        # Daily generation
        daily_generation = params.net_power_kw * 24  # kWh/day
        annual_generation = params.net_power_kw * params.annual_hours

        # Direct emissions (biogenic CO2 from biogas is carbon neutral)
        direct_emissions = 0.0

        # Avoided emissions from displaced grid electricity
        avoided_grid_emissions = daily_generation * self.emission_factors['grid_electricity']

        # Carbon sequestration in hydrochar
        carbon_in_hydrochar = params.hydrochar_rate_kg_day * self.hydrochar_carbon_content
        stable_carbon = carbon_in_hydrochar * self.stable_carbon_fraction
        carbon_sequestration = stable_carbon * 44/12  # Convert C to CO2

        # Methane emissions from AD (fugitive emissions)
        # Assume 1% fugitive methane
        methane_fugitive = params.biogas_production_m3_day * 0.65 * 0.01  # 1% of CH4
        methane_co2eq = methane_fugitive * self.gwp['ch4'] * 0.717  # kg CO2-eq/day

        # Net emissions
        net_emissions = (direct_emissions + methane_co2eq - 
                        avoided_grid_emissions - carbon_sequestration)

        # Carbon intensity
        carbon_intensity = (net_emissions * 365) / (annual_generation / 1000) if annual_generation > 0 else 0

        # Material recovery efficiency
        total_outputs = params.hydrochar_rate_kg_day + params.biomass_rate_kg_day * 0.3
        material_recovery = total_outputs / params.biomass_rate_kg_day if params.biomass_rate_kg_day > 0 else 0

        # Waste diversion
        waste_diversion = params.biomass_rate_kg_day * 0.85  # 85% diversion rate

        # Water usage
        water_usage = params.biomass_rate_kg_day * 8  # 8 kg water per kg biomass

        # Land use (simplified)
        land_use = params.biomass_rate_kg_day * 0.001  # m² per kg feedstock

        return {
            "emissions": {
                "direct_emissions_kg_co2_day": round(direct_emissions, 2),
                "avoided_grid_emissions_kg_co2_day": round(avoided_grid_emissions, 2),
                "carbon_sequestration_kg_co2_day": round(carbon_sequestration, 2),
                "methane_fugitive_kg_ch4_day": round(methane_fugitive, 2),
                "methane_co2_equivalent_kg_day": round(methane_co2eq, 2),
                "net_emissions_kg_co2_eq_day": round(net_emissions, 2),
                "net_emissions_ton_co2_eq_year": round(net_emissions * 365 / 1000, 2)
            },
            "carbon_intensity": {
                "carbon_intensity_g_co2_kwh": round(carbon_intensity, 2),
                "carbon_intensity_vs_grid": round(carbon_intensity / (self.emission_factors['grid_electricity'] * 1000), 4),
                "carbon_intensity_vs_natural_gas": round(carbon_intensity / (self.emission_factors['natural_gas'] * 1000), 4)
            },
            "resource_efficiency": {
                "material_recovery_efficiency": round(material_recovery, 4),
                "waste_diversion_kg_day": round(waste_diversion, 2),
                "water_usage_kg_day": round(water_usage, 2),
                "land_use_m2": round(land_use, 2)
            },
            "sustainability_metrics": {
                "sustainability_score": max(0, min(100, 100 - carbon_intensity / 10)),
                "carbon_negative": net_emissions < 0,
                "renewable_energy_fraction": 1.0,  # 100% renewable
                "circular_economy_index": round(material_recovery * 0.8 + 0.2, 4)
            },
            "benchmarks": {
                "coal_plant_g_co2_kwh": 820,
                "natural_gas_plant_g_co2_kwh": 490,
                "solar_pv_g_co2_kwh": 48,
                "this_system_g_co2_kwh": round(carbon_intensity, 2)
            }
        }

    def lifecycle_assessment(self, params: EnvironmentalParams, 
                           lifetime_years: int = 20) -> Dict[str, Any]:
        """
        Simplified Life Cycle Assessment

        Args:
            params: Environmental parameters
            lifetime_years: System lifetime
        """

        annual_results = self.analyze(params)

        # Scale to lifetime
        lifetime_emissions = annual_results["emissions"]["net_emissions_ton_co2_eq_year"] * lifetime_years

        # Embodied emissions (simplified estimate)
        embodied_emissions = params.net_power_kw * 0.05 * lifetime_years  # 50 kg CO2/kW/year

        total_lifecycle_emissions = lifetime_emissions + embodied_emissions

        total_generation = params.net_power_kw * params.annual_hours * lifetime_years / 1000  # MWh

        lifecycle_carbon_intensity = (total_lifecycle_emissions * 1000) / total_generation if total_generation > 0 else 0

        return {
            "lifetime_years": lifetime_years,
            "operational_emissions_ton_co2": round(lifetime_emissions, 2),
            "embodied_emissions_ton_co2": round(embodied_emissions, 2),
            "total_lifecycle_emissions_ton_co2": round(total_lifecycle_emissions, 2),
            "total_generation_mwh": round(total_generation, 2),
            "lifecycle_carbon_intensity_g_co2_kwh": round(lifecycle_carbon_intensity, 2),
            "net_carbon_benefit_ton_co2": round(-lifetime_emissions, 2)  # Negative = benefit
        }
