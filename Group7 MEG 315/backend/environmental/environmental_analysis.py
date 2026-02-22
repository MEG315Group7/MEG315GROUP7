import numpy as np
from typing import Dict, Any

class EnvironmentalAnalyzer:
    """Environmental impact analysis for AD-HTC integrated system"""
    
    def __init__(self):
        self.co2_emission_factors = {
            'natural_gas': 0.202,
            'coal': 0.337,
            'grid_electricity': 0.450,
            'biogas': 0.000
        }
        
        self.gwp_factors = {
            'co2': 1.0,
            'ch4': 25.0,
            'n2o': 298.0
        }
    
    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform environmental analysis"""
        net_power = inputs.get('net_power_kw', 100000)
        annual_hours = inputs.get('annual_hours', 8000)
        biomass_rate = inputs.get('biomass_rate_kg_day', 3000)
        hydrochar_rate = inputs.get('hydrochar_rate_kg_day', 300)
        
        # Calculate direct emissions (biogenic CO2 is neutral)
        direct_emissions = 0.0
        
        # Calculate avoided emissions from displaced grid electricity
        daily_generation = net_power * 24
        avoided_grid_emissions = daily_generation * self.co2_emission_factors['grid_electricity']
        
        # Calculate carbon sequestration in hydrochar
        carbon_content_hydrochar = 0.5
        stable_carbon_fraction = 0.2
        carbon_sequestration = hydrochar_rate * carbon_content_hydrochar * stable_carbon_fraction * 3.67
        
        # Net environmental impact
        net_emissions = direct_emissions - avoided_grid_emissions - carbon_sequestration
        
        # Carbon intensity
        annual_generation = net_power * annual_hours
        annual_net_emissions = net_emissions * 365
        carbon_intensity = annual_net_emissions / annual_generation if annual_generation > 0 else 0.0
        
        # Circular economy metrics
        material_recovery = (hydrochar_rate + biomass_rate * 0.3) / biomass_rate if biomass_rate > 0 else 0.0
        
        return {
            'net_emissions_kg_co2_eq_day': net_emissions,
            'net_emissions_ton_co2_eq_year': net_emissions * 365 / 1000,
            'carbon_intensity_kg_co2_eq_kwh': carbon_intensity,
            'avoided_grid_emissions_kg_co2_eq_day': avoided_grid_emissions,
            'carbon_sequestration_kg_co2_eq_day': carbon_sequestration,
            'material_recovery_efficiency': material_recovery,
            'sustainability_score': max(0, 100 - carbon_intensity * 100)
        }