import numpy as np
from typing import Dict, Any
import math

class ADSystem:
    """
    Anaerobic Digestion system analysis for biogas production
    Based on Buswell equation and empirical models
    """
    
    def __init__(self):
        # Biogas composition (typical values)
        self.CH4_fraction = 0.65  # 65% methane
        self.CO2_fraction = 0.35  # 35% carbon dioxide
        
        # Heating values (MJ/m³ at STP)
        self.LHV_CH4 = 35.8  # MJ/m³
        self.LHV_CO2 = 0.0   # CO2 has no heating value
        
        # Biogas properties
        self.biogas_density = 1.15  # kg/m³ at STP
        
        # AD operational parameters
        self.vs_reduction_efficiency = 0.75  # Volatile solids reduction
        self.biogas_yield_per_vs = 0.8  # m³ biogas per kg VS destroyed
        
        # Heat recovery efficiency
        self.heat_recovery_efficiency = 0.65
        
        # Reference conditions
        self.STP_temp = 273.15  # K
        self.STP_pressure = 101325  # Pa
    
    def calculate(self, feedstock_rate: float, retention_time: float, 
                  num_digesters: int = 3, vs_content: float = 0.60) -> Dict[str, Any]:
        """
        Calculate AD system performance
        
        Args:
            feedstock_rate: Total feedstock input (kg/day)
            retention_time: Hydraulic retention time (days)
            num_digesters: Number of parallel digesters
            vs_content: Volatile solids content (fraction)
        
        Returns:
            Dictionary with AD performance metrics
        """
        
        # Calculate per-digester parameters
        feedstock_per_digester = feedstock_rate / num_digesters
        digester_volume = feedstock_per_digester * retention_time / 1000  # m³ (assuming 1 kg/L density)
        
        # Calculate volatile solids input
        vs_input_total = feedstock_rate * vs_content  # kg VS/day
        vs_input_per_digester = vs_input_total / num_digesters  # kg VS/day per digester
        
        # Calculate biogas production
        vs_destroyed = vs_input_total * self.vs_reduction_efficiency  # kg VS/day
        biogas_production = vs_destroyed * self.biogas_yield_per_vs  # m³/day
        
        # Calculate biogas composition and energy content
        ch4_production = biogas_production * self.CH4_fraction  # m³/day
        co2_production = biogas_production * self.CO2_fraction  # m³/day
        
        # Calculate energy content
        biogas_lhv = self.CH4_fraction * self.LHV_CH4  # MJ/m³
        biogas_energy = biogas_production * biogas_lhv  # MJ/day
        biogas_energy_kw = biogas_energy * 1000 / 86400  # kW
        
        # Calculate methane mass flow
        ch4_mass_flow = ch4_production * 0.717  # kg/day (CH4 density)
        co2_mass_flow = co2_production * 1.977  # kg/day (CO2 density)
        
        # Calculate waste heat from biogas combustion
        # Assuming 65% of biogas energy becomes waste heat
        waste_heat_available = biogas_energy_kw * 0.65  # kW
        
        # Calculate digester heating requirements
        # Assuming mesophilic conditions (35°C) and ambient feedstock (15°C)
        feedstock_temp = 288.0  # K (15°C)
        digester_temp = 308.0  # K (35°C)
        specific_heat_feedstock = 4200.0  # J/(kg·K) (similar to water)
        
        heating_demand = feedstock_rate * specific_heat_feedstock * (digester_temp - feedstock_temp) / 86400  # kW
        heating_demand = heating_demand / 1000  # Convert to kW
        
        # Calculate biogas flow rates
        biogas_flow_rate = biogas_production / 86400  # m³/s
        ch4_flow_rate = ch4_production / 86400  # m³/s
        co2_flow_rate = co2_production / 86400  # m³/s
        
        # Calculate carbon content for environmental analysis
        carbon_in_ch4 = ch4_mass_flow * 0.75  # kg C/day (CH4 is 75% C by mass)
        carbon_in_co2 = co2_mass_flow * 0.273  # kg C/day (CO2 is 27.3% C by mass)
        total_carbon = carbon_in_ch4 + carbon_in_co2
        
        # Calculate CO2 equivalent emissions
        # CH4 has 25x global warming potential of CO2
        co2_equivalent = co2_mass_flow + ch4_mass_flow * 25  # kg CO2-eq/day
        
        # Calculate digestate production
        digestate_production = feedstock_rate - vs_destroyed  # kg/day
        digestate_volume = digestate_production / 1000  # m³/day (assuming 1 kg/L)
        
        return {
            # Input parameters
            "total_feedstock_rate_kg_day": feedstock_rate,
            "feedstock_per_digester_kg_day": feedstock_per_digester,
            "retention_time_days": retention_time,
            "num_digesters": num_digesters,
            "vs_content_fraction": vs_content,
            
            # Digester sizing
            "digester_volume_m3": digester_volume,
            "total_digester_volume_m3": digester_volume * num_digesters,
            
            # Biogas production
            "biogas_production_m3_day": biogas_production,
            "biogas_flow_rate_m3_s": biogas_flow_rate,
            "ch4_production_m3_day": ch4_production,
            "co2_production_m3_day": co2_production,
            "ch4_flow_rate_m3_s": ch4_flow_rate,
            "co2_flow_rate_m3_s": co2_flow_rate,
            "ch4_fraction": self.CH4_fraction,
            "co2_fraction": self.CO2_fraction,
            
            # Energy content
            "biogas_lhv_mj_m3": biogas_lhv,
            "biogas_energy_output_mj_day": biogas_energy,
            "biogas_energy_output_kw": biogas_energy_kw,
            "ch4_energy_output_kw": ch4_production * self.LHV_CH4 * 1000 / 86400,
            
            # Mass flows
            "ch4_mass_flow_kg_day": ch4_mass_flow,
            "co2_mass_flow_kg_day": co2_mass_flow,
            "vs_destroyed_kg_day": vs_destroyed,
            "vs_reduction_efficiency": self.vs_reduction_efficiency,
            
            # Heat integration
            "waste_heat_available_kw": waste_heat_available,
            "digester_heating_demand_kw": heating_demand,
            "net_heat_available_kw": max(0, waste_heat_available - heating_demand),
            
            # Environmental metrics
            "carbon_content_kg_day": total_carbon,
            "co2_equivalent_emissions_kg_day": co2_equivalent,
            "digestate_production_kg_day": digestate_production,
            "digestate_volume_m3_day": digestate_volume,
            
            # Performance metrics
            "biogas_yield_m3_kg_vs": biogas_production / vs_input_total if vs_input_total > 0 else 0,
            "energy_yield_mj_kg_feedstock": biogas_energy / feedstock_rate if feedstock_rate > 0 else 0,
            "volumetric_biogas_rate_m3_m3_day": biogas_production / digester_volume if digester_volume > 0 else 0
        }
    
    def calculate_buswell_equation(self, substrate_formula: str) -> Dict[str, float]:
        """
        Calculate theoretical biogas yield using Buswell equation
        
        Args:
            substrate_formula: Chemical formula (e.g., 'C6H12O6')
        
        Returns:
            Dictionary with theoretical yields
        """
        # Parse chemical formula (simple implementation)
        # This is a simplified version - in practice, you'd use a proper chemical parser
        
        # Example for glucose (C6H12O6)
        # C6H12O6 → 3CH4 + 3CO2
        # 180 g glucose → 3×22.4 L CH4 + 3×22.4 L CO2 at STP
        
        # Molar masses (g/mol)
        M_C = 12.01
        M_H = 1.008
        M_O = 16.00
        
        # Molar volume at STP (L/mol)
        Vm = 22.4
        
        # Simple parsing (would need proper implementation)
        if substrate_formula == 'C6H12O6':
            # Glucose
            M_substrate = 6*M_C + 12*M_H + 6*M_O  # 180.16 g/mol
            ch4_yield = 3 * Vm / M_substrate * 1000  # L CH4 / kg substrate
            co2_yield = 3 * Vm / M_substrate * 1000  # L CO2 / kg substrate
            
            return {
                "ch4_yield_l_kg": ch4_yield,
                "co2_yield_l_kg": co2_yield,
                "total_biogas_yield_l_kg": ch4_yield + co2_yield,
                "ch4_fraction": 0.5,
                "co2_fraction": 0.5
            }
        
        else:
            # Return default values for unknown substrates
            return {
                "ch4_yield_l_kg": 400,  # Typical for organic waste
                "co2_yield_l_kg": 200,
                "total_biogas_yield_l_kg": 600,
                "ch4_fraction": 0.67,
                "co2_fraction": 0.33
            }
    
    def calculate_kinetics(self, temperature: float, ph: float = 7.0) -> Dict[str, float]:
        """
        Calculate AD kinetics based on temperature and pH
        
        Args:
            temperature: Digester temperature (K)
            ph: Digester pH
        
        Returns:
            Dictionary with kinetic parameters
        """
        
        # Temperature correction using Arrhenius equation
        T_ref = 308.0  # K (35°C reference)
        Ea = 50000  # J/mol (activation energy)
        R = 8.314  # J/(mol·K)
        
        # Temperature correction factor
        temp_factor = np.exp((Ea/R) * (1/T_ref - 1/temperature))
        
        # pH correction (optimum around 7.0)
        ph_optimum = 7.0
        ph_factor = np.exp(-0.5 * ((ph - ph_optimum) / 0.5)**2)  # Gaussian function
        
        # Combined correction
        overall_factor = temp_factor * ph_factor
        
        # Kinetic parameters (base values at 35°C, pH 7.0)
        base_growth_rate = 0.2  # 1/day
        base_decay_rate = 0.05   # 1/day
        base_yield_coeff = 0.1   # g biomass / g substrate
        
        return {
            "temperature_k": temperature,
            "ph": ph,
            "temperature_correction_factor": temp_factor,
            "ph_correction_factor": ph_factor,
            "overall_correction_factor": overall_factor,
            "corrected_growth_rate_1_day": base_growth_rate * overall_factor,
            "corrected_decay_rate_1_day": base_decay_rate * overall_factor,
            "corrected_yield_coefficient": base_yield_coeff * overall_factor
        }