"""
Economic Analysis Module for AD-HTC System
"""

import numpy as np
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class EconomicParams:
    """Economic analysis parameters"""
    net_power_kw: float
    annual_opex_usd: float
    annual_revenue_usd: float
    project_lifetime: int = 20
    discount_rate: float = 0.08
    tax_rate: float = 0.25

class EconomicAnalyzer:
    """
    Economic analysis for AD-HTC integrated system
    NPV, LCOE, and financial metrics
    """

    def __init__(self):
        self.reference_capex_per_kw = 1000  # $/kW
        self.maintenance_rate = 0.02  # 2% of CAPEX annually

    def analyze(self, params: EconomicParams) -> Dict[str, Any]:
        """
        Perform economic analysis

        Args:
            params: EconomicParams with financial data
        """

        # CAPEX estimation
        total_capex = params.net_power_kw * self.reference_capex_per_kw

        # Cash flow calculation
        cash_flows = [-total_capex]

        for year in range(1, params.project_lifetime + 1):
            # Operating costs
            maintenance = total_capex * self.maintenance_rate
            total_opex = params.annual_opex_usd + maintenance

            # Revenue
            revenue = params.annual_revenue_usd

            # Taxable income
            taxable_income = revenue - total_opex
            taxes = taxable_income * params.tax_rate if taxable_income > 0 else 0

            # Net cash flow
            net_cf = taxable_income - taxes
            cash_flows.append(net_cf)

        # NPV calculation
        npv = sum(cf / (1 + params.discount_rate) ** i 
                  for i, cf in enumerate(cash_flows))

        # IRR calculation (simplified)
        irr = self._calculate_irr(cash_flows)

        # Payback period
        payback = self._calculate_payback(cash_flows)

        # LCOE calculation
        annual_generation = params.net_power_kw * 8000  # 8000 hours/year
        total_generation = annual_generation * params.project_lifetime

        if total_generation > 0:
            lcoe = (total_capex + sum(params.annual_opex_usd * 
                    (1 + params.discount_rate) ** -i 
                    for i in range(1, params.project_lifetime + 1))) / total_generation
        else:
            lcoe = 0

        # Profitability index
        pi = (npv + total_capex) / total_capex if total_capex > 0 else 0

        return {
            "financial_metrics": {
                "net_present_value_usd": round(npv, 2),
                "internal_rate_of_return": round(irr, 4),
                "payback_period_years": round(payback, 2),
                "profitability_index": round(pi, 2),
                "levelized_cost_electricity_usd_kwh": round(lcoe, 4)
            },
            "capex_breakdown": {
                "total_capex_usd": round(total_capex, 2),
                "capex_per_kw": round(total_capex / params.net_power_kw, 2) if params.net_power_kw > 0 else 0,
                "equipment_costs": round(total_capex * 0.6, 2),
                "installation_costs": round(total_capex * 0.25, 2),
                "engineering_costs": round(total_capex * 0.1, 2),
                "contingency": round(total_capex * 0.05, 2)
            },
            "opex_breakdown": {
                "annual_opex_usd": round(params.annual_opex_usd, 2),
                "annual_maintenance_usd": round(total_capex * self.maintenance_rate, 2),
                "total_annual_costs_usd": round(params.annual_opex_usd + total_capex * self.maintenance_rate, 2)
            },
            "revenue_analysis": {
                "annual_revenue_usd": round(params.annual_revenue_usd, 2),
                "annual_profit_usd": round(params.annual_revenue_usd - params.annual_opex_usd, 2),
                "profit_margin": round((params.annual_revenue_usd - params.annual_opex_usd) / params.annual_revenue_usd, 4) if params.annual_revenue_usd > 0 else 0
            },
            "cash_flows": [round(cf, 2) for cf in cash_flows],
            "project_lifetime_years": params.project_lifetime,
            "discount_rate": params.discount_rate
        }

    def _calculate_irr(self, cash_flows: list, guess: float = 0.1) -> float:
        """Calculate Internal Rate of Return"""
        try:
            from scipy.optimize import newton

            def npv(rate):
                return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))

            return newton(npv, guess)
        except:
            # Fallback: simple iteration
            for r in np.linspace(-0.5, 1.0, 1000):
                if abs(sum(cf / (1 + r) ** i for i, cf in enumerate(cash_flows))) < 100:
                    return r
            return 0

    def _calculate_payback(self, cash_flows: list) -> float:
        """Calculate payback period"""
        cumulative = 0
        for i, cf in enumerate(cash_flows):
            cumulative += cf
            if cumulative > 0:
                return i - 1 + (cumulative - cf) / cf if cf > 0 else i
        return len(cash_flows)

    def sensitivity_analysis(self, params: EconomicParams, 
                           variable: str, 
                           range_pct: float = 0.2,
                           n_points: int = 10) -> Dict[str, Any]:
        """
        Perform sensitivity analysis

        Args:
            params: Base economic parameters
            variable: Variable to vary ('discount_rate', 'capex', 'opex', 'revenue')
            range_pct: Variation range (+/-)
            n_points: Number of points to evaluate
        """

        base_value = getattr(params, variable, 0)
        variations = np.linspace(base_value * (1 - range_pct), 
                                base_value * (1 + range_pct), 
                                n_points)

        results = []
        for val in variations:
            test_params = EconomicParams(
                net_power_kw=params.net_power_kw,
                annual_opex_usd=params.annual_opex_usd if variable != 'opex' else val,
                annual_revenue_usd=params.annual_revenue_usd if variable != 'revenue' else val,
                project_lifetime=params.project_lifetime,
                discount_rate=params.discount_rate if variable != 'discount_rate' else val,
                tax_rate=params.tax_rate
            )

            result = self.analyze(test_params)
            results.append({
                "variable_value": val,
                "npv": result["financial_metrics"]["net_present_value_usd"],
                "lcoe": result["financial_metrics"]["levelized_cost_electricity_usd_kwh"],
                "irr": result["financial_metrics"]["internal_rate_of_return"]
            })

        return {
            "variable": variable,
            "base_value": base_value,
            "range": [variations[0], variations[-1]],
            "results": results
        }
