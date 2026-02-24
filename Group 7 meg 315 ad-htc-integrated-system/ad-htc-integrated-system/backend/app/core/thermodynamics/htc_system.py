"""
Hydrothermal Carbonization System Analysis Module
"""

import numpy as np
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class HTCConfig:
    """HTC system configuration"""
    biomass_rate: float  # kg/day
    reactor_temp: float  # K
    ambient_temp: float = 298.15
    residence_time: float = 2.0
    moisture_content: float = 0.10

class HTCSystem:
    """
    Hydrothermal Carbonization system
    Biomass conversion to hydrochar
    """

    def __init__(self):
        # Process parameters
        self.reaction_temp_range = (453, 523)
        self.reaction_pressure_range = (10, 50)
        self.residence_time_range = (0.5, 4.0)

        # Yields
        self.hydrochar_yield_range = (0.4, 0.7)
        self.liquid_yield_range = (0.2, 0.4)
        self.gas_yield_range = (0.05, 0.15)

        # Energy content (MJ/kg)
        self.biomass_energy = 18.0
        self.hydrochar_energy = 28.0
        self.process_water_energy = 2.0

        # Heat capacities (kJ/(kg·K))
        self.cp_biomass = 1.5
        self.cp_water = 4.186

        # Process parameters
        self.water_to_biomass_ratio = 8.0
        self.heat_recovery_efficiency = 0.75

        self.ambient_temp = 298.15

    def calculate(self, config: HTCConfig) -> Dict[str, Any]:
        """Calculate HTC system performance"""

        # Water requirements
        dry_biomass = config.biomass_rate * (1 - config.moisture_content)
        water_input = dry_biomass * self.water_to_biomass_ratio
        total_slurry = dry_biomass + water_input

        # Temperature-dependent yields
        temp_factor = ((config.reactor_temp - self.reaction_temp_range[0]) / 
                      (self.reaction_temp_range[1] - self.reaction_temp_range[0]))

        hydrochar_yield = self.hydrochar_yield_range[1] - temp_factor * 0.3
        hydrochar_yield = max(self.hydrochar_yield_range[0], 
                             min(self.hydrochar_yield_range[1], hydrochar_yield))

        liquid_yield = self.liquid_yield_range[0] + temp_factor * 0.2
        liquid_yield = max(self.liquid_yield_range[0],
                          min(self.liquid_yield_range[1], liquid_yield))

        gas_yield = 1.0 - hydrochar_yield - liquid_yield

        # Product rates
        hydrochar_rate = dry_biomass * hydrochar_yield
        liquid_rate = dry_biomass * liquid_yield
        gas_rate = dry_biomass * gas_yield

        # Energy content
        hydrochar_energy = hydrochar_rate * self.hydrochar_energy
        liquid_energy = liquid_rate * self.process_water_energy
        gas_energy = gas_rate * 15.0
        total_energy = hydrochar_energy + liquid_energy + gas_energy

        # Energy upgrade
        input_energy = dry_biomass * self.biomass_energy
        energy_upgrade = hydrochar_energy / input_energy if input_energy > 0 else 0

        # Heat requirements
        biomass_heating = (dry_biomass * self.cp_biomass * 
                          (config.reactor_temp - config.ambient_temp) / 86400)
        water_heating = (water_input * self.cp_water * 
                        (config.reactor_temp - config.ambient_temp) / 86400)
        reaction_heat = dry_biomass * 1.5 / 86400  # MJ to kW

        total_heat_demand = biomass_heating + water_heating + reaction_heat

        # Heat recovery
        product_heat_recovery = ((hydrochar_rate + liquid_rate) * self.cp_water *
                                (config.reactor_temp - config.ambient_temp) * 
                                self.heat_recovery_efficiency / 86400)

        net_heat_requirement = total_heat_demand - product_heat_recovery

        # Reactor sizing
        slurry_density = 1050
        reactor_volume = total_slurry / slurry_density * config.residence_time / 24

        # Carbon analysis
        carbon_input = dry_biomass * 0.5
        carbon_in_hydrochar = hydrochar_rate * 0.75
        carbon_recovery = carbon_in_hydrochar / carbon_input if carbon_input > 0 else 0

        # Environmental
        co2_sequestered = carbon_in_hydrochar * 44/12
        fossil_displacement = net_heat_requirement * 0.8

        return {
            "config": {
                "biomass_rate_kg_day": config.biomass_rate,
                "dry_biomass_rate_kg_day": dry_biomass,
                "reactor_temp_k": config.reactor_temp,
                "residence_time_hours": config.residence_time,
                "moisture_content": config.moisture_content
            },

            "water_input_kg_day": water_input,
            "total_slurry_rate_kg_day": total_slurry,

            "hydrochar_yield_fraction": hydrochar_yield,
            "liquid_yield_fraction": liquid_yield,
            "gas_yield_fraction": gas_yield,

            "hydrochar_rate_kg_day": hydrochar_rate,
            "liquid_rate_kg_day": liquid_rate,
            "gas_rate_kg_day": gas_rate,

            "hydrochar_energy_mj_day": hydrochar_energy,
            "total_energy_output_mj_day": total_energy,
            "total_energy_output_kw": total_energy * 1000 / 86400,

            "input_energy_mj_day": input_energy,
            "energy_upgrade_factor": energy_upgrade,
            "energy_densification": self.hydrochar_energy / self.biomass_energy,

            "total_heat_demand_kw": total_heat_demand,
            "product_heat_recovery_kw": product_heat_recovery,
            "net_heat_requirement_kw": net_heat_requirement,

            "reactor_volume_m3": reactor_volume,

            "carbon_input_kg_day": carbon_input,
            "carbon_recovery_fraction": carbon_recovery,
            "co2_sequestered_kg_day": co2_sequestered,
            "fossil_fuel_displacement_kw": fossil_displacement
        }

    def optimize_temperature(self, config: HTCConfig, available_heat: float = 0) -> Dict[str, Any]:
        """Optimize operating temperature"""

        temperatures = np.linspace(453, 523, 10)
        best_temp = config.reactor_temp
        best_efficiency = 0

        for temp in temperatures:
            test_config = HTCConfig(
                biomass_rate=config.biomass_rate,
                reactor_temp=temp,
                ambient_temp=config.ambient_temp,
                residence_time=config.residence_time,
                moisture_content=config.moisture_content
            )
            results = self.calculate(test_config)

            efficiency = results["energy_upgrade_factor"]
            heat_demand = results["net_heat_requirement_kw"]

            if available_heat > 0 and heat_demand > available_heat:
                continue

            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_temp = temp

        return {
            "optimal_temperature_k": best_temp,
            "optimal_temperature_c": best_temp - 273.15,
            "max_efficiency": best_efficiency
        }
