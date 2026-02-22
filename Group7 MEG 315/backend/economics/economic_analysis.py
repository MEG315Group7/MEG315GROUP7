import numpy as np
from typing import Dict, Any

class EconomicAnalyzer:
    """Economic analysis for AD-HTC integrated system"""
    
    def __init__(self):
        self.discount_rate = 0.08
        self.project_lifetime = 20
        self.tax_rate = 0.25
        
    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform economic analysis"""
        net_power = inputs.get('net_power_kw', 100000)
        annual_opex = inputs.get('annual_opex_usd', 5000000)
        annual_revenue = inputs.get('annual_revenue_usd', 8000000)
        
        # Simple calculations
        total_capex = net_power * 1000  # $1000/kW
        cash_flows = [-total_capex]
        
        for year in range(1, self.project_lifetime + 1):
            taxable_income = annual_revenue - annual_opex
            taxes = taxable_income * self.tax_rate if taxable_income > 0 else 0
            cash_flows.append(taxable_income - taxes)
        
        # Calculate NPV
        npv = sum(cf / (1 + self.discount_rate) ** i for i, cf in enumerate(cash_flows))
        
        # Simple LCOE calculation
        annual_generation = net_power * 8000  # 8000 hours/year
        total_generation = annual_generation * self.project_lifetime
        
        # Prevent division by zero
        if total_generation > 0:
            lcoe = (total_capex + annual_opex * self.project_lifetime) / total_generation
        else:
            lcoe = 0  # or some default value when no generation
        
        return {
            'net_present_value_usd': npv,
            'levelized_cost_electricity_usd_kwh': lcoe,
            'total_capex_usd': total_capex,
            'annual_opex_usd': annual_opex,
            'annual_revenue_usd': annual_revenue
        }