import numpy as np
from typing import Dict, Any
import math

class HTCSystem:
    """
    Hydrothermal Carbonization system analysis
    Based on thermal processing of biomass in subcritical water
    """
    
    def __init__(self):
        # HTC reaction parameters
        self.reaction_temperature_range = (453, 523)  # K (180-250°C)
        self.reaction_pressure_range = (10, 50)      # bar (1-5 MPa)
        self.residence_time_range = (0.5, 4.0)       # hours
        
        # Product yields (typical ranges)
        self.hydrochar_yield_range = (0.4, 0.7)      # kg hydrochar / kg dry biomass
        self.liquid_yield_range = (0.2, 0.4)         # kg liquid / kg dry biomass
        self.gas_yield_range = (0.05, 0.15)          # kg gas / kg dry biomass
        
        # Energy content (MJ/kg)
        self.biomass_energy_content = 18.0           # MJ/kg (dry basis)
        self.hydrochar_energy_content = 28.0           # MJ/kg (dry basis)
        self.process_water_energy_content = 2.0        # MJ/kg
        
        # Specific heat capacities (J/(kg·K))
        self.cp_biomass = 1500.0                      # J/(kg·K)
        self.cp_water = 4186.0                        # J/(kg·K)
        self.cp_steam = 2100.0                        # J/(kg·K)
        
        # Water properties
        self.water_density = 1000.0                     # kg/m³
        self.latent_heat_vaporization = 2257.0          # kJ/kg
        self.latent_heat_steam = 2200.0                 # kJ/kg
        
        # HTC process parameters
        self.moisture_content_biomass = 0.10            # 10% moisture (dry basis)
        self.water_to_biomass_ratio = 8.0               # kg water / kg dry biomass
        self.heat_recovery_efficiency = 0.75            # Heat recovery from hot products
        
        # Reference conditions
        self.ambient_temp = 298.15                       # K (25°C)
        self.ambient_pressure = 101325                  # Pa (1 atm)
    
    def calculate(self, biomass_rate: float, reactor_temp: float, 
                  ambient_temp: float = 298.15, residence_time: float = 2.0,
                  moisture_content: float = 0.10) -> Dict[str, Any]:
        """
        Calculate HTC system performance
        
        Args:
            biomass_rate: Dry biomass input rate (kg/day)
            reactor_temp: HTC reactor temperature (K)
            ambient_temp: Ambient temperature (K)
            residence_time: Residence time (hours)
            moisture_content: Biomass moisture content (fraction)
        
        Returns:
            Dictionary with HTC performance metrics
        """
        
        # Calculate water requirements
        dry_biomass_rate = biomass_rate * (1 - moisture_content)
        water_input = dry_biomass_rate * self.water_to_biomass_ratio  # kg/day
        total_slurry_rate = dry_biomass_rate + water_input  # kg/day
        
        # Calculate product yields (temperature-dependent)
        temp_factor = (reactor_temp - self.reaction_temperature_range[0]) / \
                     (self.reaction_temperature_range[1] - self.reaction_temperature_range[0])
        
        # Hydrochar yield decreases with temperature
        hydrochar_yield = self.hydrochar_yield_range[1] - temp_factor * 0.3
        hydrochar_yield = max(self.hydrochar_yield_range[0], min(self.hydrochar_yield_range[1], hydrochar_yield))
        
        # Liquid yield increases with temperature
        liquid_yield = self.liquid_yield_range[0] + temp_factor * 0.2
        liquid_yield = max(self.liquid_yield_range[0], min(self.liquid_yield_range[1], liquid_yield))
        
        # Gas yield
        gas_yield = 1.0 - hydrochar_yield - liquid_yield
        gas_yield = max(self.gas_yield_range[0], min(self.gas_yield_range[1], gas_yield))
        
        # Calculate product rates
        hydrochar_rate = dry_biomass_rate * hydrochar_yield  # kg/day
        liquid_rate = dry_biomass_rate * liquid_yield       # kg/day
        gas_rate = dry_biomass_rate * gas_yield             # kg/day
        
        # Calculate energy content of products
        hydrochar_energy = hydrochar_rate * self.hydrochar_energy_content  # MJ/day
        liquid_energy = liquid_rate * self.process_water_energy_content    # MJ/day
        gas_energy = gas_rate * 15.0  # MJ/day (assuming typical HTC gas composition)
        
        # Calculate total energy output
        total_energy_output = hydrochar_energy + liquid_energy + gas_energy  # MJ/day
        total_energy_output_kw = total_energy_output * 1000 / 86400  # kW
        
        # Calculate energy upgrade factor
        input_energy = dry_biomass_rate * self.biomass_energy_content  # MJ/day
        energy_upgrade_factor = hydrochar_energy / input_energy if input_energy > 0 else 0
        
        # Calculate heating requirements
        # 1. Heating biomass from ambient to reactor temperature
        biomass_heating = dry_biomass_rate * self.cp_biomass * (reactor_temp - ambient_temp) / 86400  # kW
        
        # 2. Heating water from ambient to reactor temperature
        water_heating = water_input * self.cp_water * (reactor_temp - ambient_temp) / 86400  # kW
        
        # 3. Reaction heat (endothermic, typically 1-2 MJ/kg dry biomass)
        reaction_heat = dry_biomass_rate * 1.5 * 1000 / 86400  # kW (1.5 MJ/kg)
        
        # Total heat demand
        total_heat_demand = biomass_heating + water_heating + reaction_heat  # kW
        
        # Calculate heat recovery from hot products
        # Assume products leave at reactor temperature
        product_heat_recovery = (hydrochar_rate + liquid_rate) * self.cp_water * \
                                (reactor_temp - ambient_temp) * self.heat_recovery_efficiency / 86400  # kW
        
        # Calculate net heat requirement
        net_heat_requirement = total_heat_demand - product_heat_recovery  # kW
        
        # Calculate reactor sizing
        slurry_density = 1050  # kg/m³ (typical for biomass slurry)
        reactor_volume = total_slurry_rate / slurry_density * residence_time / 24  # m³
        
        # Calculate carbon content and energy densification
        # Assume 50% carbon in dry biomass
        carbon_input = dry_biomass_rate * 0.5  # kg C/day
        carbon_in_hydrochar = hydrochar_rate * 0.75  # kg C/day (hydrochar is 75% C)
        carbon_recovery = carbon_in_hydrochar / carbon_input if carbon_input > 0 else 0
        
        # Energy densification
        energy_densification = self.hydrochar_energy_content / self.biomass_energy_content
        
        # Calculate HTC efficiency
        htc_efficiency = (hydrochar_energy + product_heat_recovery * 86400 / 1000) / input_energy if input_energy > 0 else 0
        
        # Environmental benefits
        # CO2 sequestration in hydrochar (assuming stable carbon)
        co2_sequestered = carbon_in_hydrochar * 44/12  # kg CO2/day (44/12 = CO2/C molecular ratio)
        
        # Energy savings vs fossil fuels (if used for heat)
        fossil_fuel_displacement = net_heat_requirement * 0.8  # kW (assuming 80% boiler efficiency)
        
        return {
            # Input parameters
            "biomass_rate_kg_day": biomass_rate,
            "dry_biomass_rate_kg_day": dry_biomass_rate,
            "water_input_kg_day": water_input,
            "total_slurry_rate_kg_day": total_slurry_rate,
            "reactor_temperature_k": reactor_temp,
            "residence_time_hours": residence_time,
            "moisture_content_fraction": moisture_content,
            
            # Product yields
            "hydrochar_yield_fraction": hydrochar_yield,
            "liquid_yield_fraction": liquid_yield,
            "gas_yield_fraction": gas_yield,
            
            # Product rates
            "hydrochar_rate_kg_day": hydrochar_rate,
            "liquid_rate_kg_day": liquid_rate,
            "gas_rate_kg_day": gas_rate,
            
            # Energy content
            "hydrochar_energy_mj_day": hydrochar_energy,
            "liquid_energy_mj_day": liquid_energy,
            "gas_energy_mj_day": gas_energy,
            "total_energy_output_mj_day": total_energy_output,
            "total_energy_output_kw": total_energy_output_kw,
            
            # Energy analysis
            "input_energy_mj_day": input_energy,
            "energy_upgrade_factor": energy_upgrade_factor,
            "energy_densification": energy_densification,
            "htc_efficiency": htc_efficiency,
            
            # Heat requirements
            "biomass_heating_kw": biomass_heating,
            "water_heating_kw": water_heating,
            "reaction_heat_kw": reaction_heat,
            "total_heat_demand_kw": total_heat_demand,
            "product_heat_recovery_kw": product_heat_recovery,
            "net_heat_requirement_kw": net_heat_requirement,
            
            # Reactor sizing
            "reactor_volume_m3": reactor_volume,
            "slurry_density_kg_m3": slurry_density,
            
            # Carbon analysis
            "carbon_input_kg_day": carbon_input,
            "carbon_in_hydrochar_kg_day": carbon_in_hydrochar,
            "carbon_recovery_fraction": carbon_recovery,
            
            # Environmental benefits
            "co2_sequestered_kg_day": co2_sequestered,
            "fossil_fuel_displacement_kw": fossil_fuel_displacement,
            
            # Process water
            "process_water_rate_kg_day": liquid_rate,
            "process_water_recovery_fraction": 0.9  # 90% can be recycled
        }
    
    def calculate_heat_integration(self, available_heat_sources: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate heat integration with available heat sources
        
        Args:
            available_heat_sources: Dictionary of available heat sources (kW)
                - 'ad_waste_heat': Waste heat from AD system
                - 'gt_exhaust_heat': Exhaust heat from gas turbine
                - 'other_sources': Other available heat sources
        
        Returns:
            Dictionary with heat integration analysis
        """
        
        total_available_heat = sum(available_heat_sources.values())
        
        # Calculate heat integration potential
        # Assume temperature levels are compatible for indirect heating
        heat_integration_efficiency = 0.85  # Heat exchanger efficiency
        available_heat_integrated = total_available_heat * heat_integration_efficiency
        
        # Calculate external heat requirement
        current_heat_demand = self.calculate(500, 473.0)["net_heat_requirement_kw"]  # Reference calculation
        external_heat_needed = max(0, current_heat_demand - available_heat_integrated)
        
        # Calculate self-sufficiency ratio
        self_sufficiency = min(available_heat_integrated / current_heat_demand, 1.0) if current_heat_demand > 0 else 0
        
        # Calculate energy cost savings
        # Assume natural gas cost: $0.04/kWh
        energy_cost_savings = available_heat_integrated * 24 * 0.04  # $/day
        
        # Calculate CO2 emission reduction
        # Natural gas emission factor: 0.2 kg CO2/kWh
        co2_reduction = available_heat_integrated * 24 * 0.2  # kg CO2/day
        
        return {
            "available_heat_sources_kw": available_heat_sources,
            "total_available_heat_kw": total_available_heat,
            "heat_integration_efficiency": heat_integration_efficiency,
            "available_heat_integrated_kw": available_heat_integrated,
            "htc_heat_demand_kw": current_heat_demand,
            "external_heat_needed_kw": external_heat_needed,
            "self_sufficiency_ratio": self_sufficiency,
            "energy_cost_savings_usd_day": energy_cost_savings,
            "co2_emission_reduction_kg_day": co2_reduction,
            "heat_integration_potential": "High" if self_sufficiency > 0.8 else "Medium" if self_sufficiency > 0.5 else "Low"
        }
    
    def optimize_operating_conditions(self, biomass_rate: float, 
                                    available_heat: float = 0) -> Dict[str, Any]:
        """
        Optimize HTC operating conditions for maximum energy efficiency
        
        Args:
            biomass_rate: Biomass input rate (kg/day)
            available_heat: Available heat for HTC (kW)
        
        Returns:
            Dictionary with optimized conditions
        """
        
        # Temperature optimization
        temperatures = np.linspace(453, 523, 10)  # 180-250°C
        efficiencies = []
        heat_demands = []
        
        for temp in temperatures:
            results = self.calculate(biomass_rate, temp)
            efficiencies.append(results["htc_efficiency"])
            heat_demands.append(results["net_heat_requirement_kw"])
        
        # Find optimal temperature considering heat availability
        if available_heat > 0:
            # Find highest temperature within heat availability
            feasible_temps = [temp for temp, demand in zip(temperatures, heat_demands) 
                            if demand <= available_heat]
            if feasible_temps:
                optimal_temp = max(feasible_temps)
            else:
                optimal_temp = temperatures[0]  # Lowest temperature
        else:
            # Find temperature with maximum efficiency
            max_efficiency_idx = np.argmax(efficiencies)
            optimal_temp = temperatures[max_efficiency_idx]
        
        # Get results for optimal conditions
        optimal_results = self.calculate(biomass_rate, optimal_temp)
        
        return {
            "optimal_temperature_k": optimal_temp,
            "optimal_temperature_c": optimal_temp - 273.15,
            "efficiency_at_optimal": optimal_results["htc_efficiency"],
            "heat_demand_at_optimal_kw": optimal_results["net_heat_requirement_kw"],
            "hydrochar_yield_at_optimal": optimal_results["hydrochar_yield_fraction"],
            "energy_upgrade_at_optimal": optimal_results["energy_upgrade_factor"],
            "temperature_range_k": temperatures.tolist(),
            "efficiency_range": efficiencies,
            "heat_demand_range_kw": heat_demands
        }