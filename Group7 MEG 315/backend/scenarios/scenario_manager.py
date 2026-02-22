from typing import Dict, Any

class ScenarioManager:
    """
    Manages preset scenarios for AD-HTC system analysis
    """
    
    def __init__(self):
        self.scenarios = {
            'base_case': {
                'name': 'Base Case',
                'description': 'Standard configuration with typical operating parameters',
                'parameters': {
                    'ambient_temp': 298.15,  # K
                    'pressure_ratio': 12.0,
                    'max_turbine_temp': 1400,  # K
                    'compressor_efficiency': 0.85,
                    'turbine_efficiency': 0.88,
                    'ad_retention_time': 20,  # days
                    'ad_temperature': 308.15,  # K
                    'htc_reactor_temp': 473.15,  # K (200°C)
                    'htc_residence_time': 2.0,  # hours
                    'biomass_moisture': 0.10,
                    'biomass_rate': 3000,  # kg/day
                    'waste_diversion_rate': 0.85
                },
                'expected_performance': {
                    'net_power': 85000,  # kW
                    'system_efficiency': 0.42,
                    'biogas_yield': 2500,  # m3/day
                    'hydrochar_yield': 300,  # kg/day
                    'self_sufficiency_ratio': 0.75
                }
            },
            
            'optimized': {
                'name': 'Optimized Configuration',
                'description': 'Optimized parameters for maximum efficiency and sustainability',
                'parameters': {
                    'ambient_temp': 298.15,  # K
                    'pressure_ratio': 16.0,
                    'max_turbine_temp': 1500,  # K
                    'compressor_efficiency': 0.88,
                    'turbine_efficiency': 0.91,
                    'ad_retention_time': 15,  # days
                    'ad_temperature': 313.15,  # K
                    'htc_reactor_temp': 493.15,  # K (220°C)
                    'htc_residence_time': 1.5,  # hours
                    'biomass_moisture': 0.08,
                    'biomass_rate': 3500,  # kg/day
                    'waste_diversion_rate': 0.95
                },
                'expected_performance': {
                    'net_power': 105000,  # kW
                    'system_efficiency': 0.48,
                    'biogas_yield': 3200,  # m3/day
                    'hydrochar_yield': 420,  # kg/day
                    'self_sufficiency_ratio': 0.85
                }
            },
            
            'full_cogas': {
                'name': 'Full COGAS Configuration',
                'description': 'Combined cycle with heat recovery steam generator',
                'parameters': {
                    'ambient_temp': 298.15,  # K
                    'pressure_ratio': 18.0,
                    'max_turbine_temp': 1550,  # K
                    'compressor_efficiency': 0.90,
                    'turbine_efficiency': 0.93,
                    'ad_retention_time': 12,  # days
                    'ad_temperature': 318.15,  # K
                    'htc_reactor_temp': 513.15,  # K (240°C)
                    'htc_residence_time': 1.0,  # hours
                    'biomass_moisture': 0.06,
                    'biomass_rate': 4000,  # kg/day
                    'waste_diversion_rate': 0.98,
                    'hrsg_efficiency': 0.85,
                    'steam_turbine_efficiency': 0.88,
                    'steam_pressure': 80,  # bar
                    'steam_temperature': 673.15  # K (400°C)
                },
                'expected_performance': {
                    'net_power': 135000,  # kW (combined cycle)
                    'system_efficiency': 0.58,
                    'biogas_yield': 3800,  # m3/day
                    'hydrochar_yield': 520,  # kg/day
                    'self_sufficiency_ratio': 0.95,
                    'steam_power': 25000  # kW
                }
            },
            
            'minimal_config': {
                'name': 'Minimal Configuration',
                'description': 'Basic configuration with minimal complexity',
                'parameters': {
                    'ambient_temp': 298.15,  # K
                    'pressure_ratio': 8.0,
                    'max_turbine_temp': 1200,  # K
                    'compressor_efficiency': 0.82,
                    'turbine_efficiency': 0.85,
                    'ad_retention_time': 25,  # days
                    'ad_temperature': 303.15,  # K
                    'htc_reactor_temp': 453.15,  # K (180°C)
                    'htc_residence_time': 3.0,  # hours
                    'biomass_moisture': 0.12,
                    'biomass_rate': 2000,  # kg/day
                    'waste_diversion_rate': 0.70
                },
                'expected_performance': {
                    'net_power': 65000,  # kW
                    'system_efficiency': 0.35,
                    'biogas_yield': 1800,  # m3/day
                    'hydrochar_yield': 200,  # kg/day
                    'self_sufficiency_ratio': 0.60
                }
            },
            
            'high_efficiency': {
                'name': 'High Efficiency Focus',
                'description': 'Maximum efficiency with advanced components',
                'parameters': {
                    'ambient_temp': 298.15,  # K
                    'pressure_ratio': 20.0,
                    'max_turbine_temp': 1600,  # K
                    'compressor_efficiency': 0.92,
                    'turbine_efficiency': 0.95,
                    'ad_retention_time': 10,  # days
                    'ad_temperature': 323.15,  # K
                    'htc_reactor_temp': 533.15,  # K (260°C)
                    'htc_residence_time': 0.8,  # hours
                    'biomass_moisture': 0.05,
                    'biomass_rate': 4500,  # kg/day
                    'waste_diversion_rate': 0.99
                },
                'expected_performance': {
                    'net_power': 150000,  # kW
                    'system_efficiency': 0.65,
                    'biogas_yield': 4200,  # m3/day
                    'hydrochar_yield': 630,  # kg/day
                    'self_sufficiency_ratio': 1.05
                }
            }
        }
    
    def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Get a specific scenario by ID"""
        
        if scenario_id not in self.scenarios:
            raise ValueError(f"Scenario '{scenario_id}' not found. Available scenarios: {list(self.scenarios.keys())}")
        
        return self.scenarios[scenario_id].copy()
    
    def get_all_scenarios(self) -> Dict[str, Any]:
        """Get all available scenarios"""
        
        return {
            scenario_id: {
                'name': scenario['name'],
                'description': scenario['description'],
                'expected_performance': scenario['expected_performance']
            }
            for scenario_id, scenario in self.scenarios.items()
        }
    
    def create_custom_scenario(self, name: str, description: str, 
                             parameters: Dict[str, Any], 
                             expected_performance: Dict[str, Any] = None) -> str:
        """Create a custom scenario"""
        
        # Generate unique ID
        import uuid
        scenario_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        self.scenarios[scenario_id] = {
            'name': name,
            'description': description,
            'parameters': parameters,
            'expected_performance': expected_performance or {}
        }
        
        return scenario_id
    
    def compare_scenarios(self, scenario_ids: list) -> Dict[str, Any]:
        """Compare multiple scenarios"""
        
        comparison = {}
        
        for scenario_id in scenario_ids:
            if scenario_id not in self.scenarios:
                continue
            
            scenario = self.scenarios[scenario_id]
            comparison[scenario_id] = {
                'name': scenario['name'],
                'parameters': scenario['parameters'],
                'expected_performance': scenario['expected_performance']
            }
        
        return comparison
    
    def get_parameter_ranges(self) -> Dict[str, Any]:
        """Get acceptable parameter ranges for validation"""
        
        return {
            'ambient_temp': {'min': 273.15, 'max': 323.15, 'unit': 'K'},
            'pressure_ratio': {'min': 5.0, 'max': 25.0, 'unit': ''},
            'max_turbine_temp': {'min': 1000, 'max': 1800, 'unit': 'K'},
            'compressor_efficiency': {'min': 0.75, 'max': 0.95, 'unit': ''},
            'turbine_efficiency': {'min': 0.80, 'max': 0.98, 'unit': ''},
            'ad_retention_time': {'min': 5, 'max': 40, 'unit': 'days'},
            'ad_temperature': {'min': 293.15, 'max': 333.15, 'unit': 'K'},
            'htc_reactor_temp': {'min': 423.15, 'max': 573.15, 'unit': 'K'},
            'htc_residence_time': {'min': 0.5, 'max': 5.0, 'unit': 'hours'},
            'biomass_moisture': {'min': 0.05, 'max': 0.20, 'unit': ''},
            'biomass_rate': {'min': 1000, 'max': 10000, 'unit': 'kg/day'},
            'waste_diversion_rate': {'min': 0.5, 'max': 1.0, 'unit': ''}
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters against acceptable ranges"""
        
        ranges = self.get_parameter_ranges()
        validation_results = {'valid': True, 'errors': [], 'warnings': []}
        
        for param, value in parameters.items():
            if param not in ranges:
                validation_results['warnings'].append(f"Unknown parameter: {param}")
                continue
            
            param_range = ranges[param]
            if value < param_range['min'] or value > param_range['max']:
                validation_results['valid'] = False
                validation_results['errors'].append(
                    f"Parameter {param} = {value} is outside range [{param_range['min']}, {param_range['max']}] {param_range['unit']}"
                )
        
        return validation_results