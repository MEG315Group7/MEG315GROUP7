# improved_scenario_manager.py - Enhanced scenario management
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import json

class EnhancedScenarioManager:
    """
    Enhanced scenario management with versioning, comparison, and validation
    """
    
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
        self.custom_scenarios = {}
        self.version_history = {}
    
    def _initialize_scenarios(self) -> Dict[str, Any]:
        """Initialize built-in scenarios with complete parameter sets."""
        return {
            'base_case': {
                'id': 'base_case',
                'name': 'Base Case',
                'description': 'Standard configuration with typical operating parameters for AD-HTC integration',
                'category': 'economic',
                'version': '1.0',
                'created_date': '2024-01-01',
                'parameters': {
                    'ambient_temp': 298.15,
                    'pressure_ratio': 12.0,
                    'max_turbine_temp': 1400.0,
                    'compressor_efficiency': 0.85,
                    'turbine_efficiency': 0.88,
                    'ad_retention_time': 20.0,
                    'ad_temperature': 308.15,
                    'htc_reactor_temp': 473.15,
                    'htc_residence_time': 2.0,
                    'biomass_moisture': 0.10,
                    'biomass_rate': 3000.0,
                    'waste_diversion_rate': 0.85,
                    'htc_biomass_rate': 500.0,
                    'heat_recovery_efficiency': 0.75
                },
                'expected_performance': {
                    'net_power': 85000,
                    'system_efficiency': 0.42,
                    'biogas_yield': 2500,
                    'hydrochar_yield': 300,
                    'self_sufficiency_ratio': 0.75,
                    'lcoe_usd_kwh': 0.08,
                    'carbon_intensity_g_kwh': 120
                },
                'constraints': {
                    'min_efficiency': 0.35,
                    'max_cost_per_kw': 1200,
                    'min_self_sufficiency': 0.70
                }
            },
            
            'optimized': {
                'id': 'optimized',
                'name': 'Optimized Configuration',
                'description': 'Optimized parameters for maximum efficiency and sustainability',
                'category': 'efficiency_focused',
                'version': '1.0',
                'created_date': '2024-01-01',
                'parameters': {
                    'ambient_temp': 298.15,
                    'pressure_ratio': 16.0,
                    'max_turbine_temp': 1500.0,
                    'compressor_efficiency': 0.88,
                    'turbine_efficiency': 0.91,
                    'ad_retention_time': 15.0,
                    'ad_temperature': 313.15,
                    'htc_reactor_temp': 493.15,
                    'htc_residence_time': 1.5,
                    'biomass_moisture': 0.08,
                    'biomass_rate': 3500.0,
                    'waste_diversion_rate': 0.95,
                    'htc_biomass_rate': 600.0,
                    'heat_recovery_efficiency': 0.85
                },
                'expected_performance': {
                    'net_power': 105000,
                    'system_efficiency': 0.48,
                    'biogas_yield': 3200,
                    'hydrochar_yield': 420,
                    'self_sufficiency_ratio': 0.85,
                    'lcoe_usd_kwh': 0.075,
                    'carbon_intensity_g_kwh': 95
                },
                'constraints': {
                    'min_efficiency': 0.45,
                    'max_cost_per_kw': 1500,
                    'min_self_sufficiency': 0.80
                }
            },
            
            'full_cogas': {
                'id': 'full_cogas',
                'name': 'Full COGAS Configuration',
                'description': 'Combined cycle with heat recovery steam generator for maximum output',
                'category': 'power_focused',
                'version': '1.0',
                'created_date': '2024-01-01',
                'parameters': {
                    'ambient_temp': 298.15,
                    'pressure_ratio': 18.0,
                    'max_turbine_temp': 1550.0,
                    'compressor_efficiency': 0.90,
                    'turbine_efficiency': 0.93,
                    'ad_retention_time': 12.0,
                    'ad_temperature': 318.15,
                    'htc_reactor_temp': 513.15,
                    'htc_residence_time': 1.0,
                    'biomass_moisture': 0.06,
                    'biomass_rate': 4000.0,
                    'waste_diversion_rate': 0.98,
                    'htc_biomass_rate': 700.0,
                    'heat_recovery_efficiency': 0.90,
                    'hrsg_efficiency': 0.85,
                    'steam_turbine_efficiency': 0.88,
                    'steam_pressure': 80.0,
                    'steam_temperature': 673.15
                },
                'expected_performance': {
                    'net_power': 135000,
                    'system_efficiency': 0.58,
                    'biogas_yield': 3800,
                    'hydrochar_yield': 520,
                    'self_sufficiency_ratio': 0.95,
                    'steam_power': 25000,
                    'lcoe_usd_kwh': 0.065,
                    'carbon_intensity_g_kwh': 75
                },
                'constraints': {
                    'min_efficiency': 0.55,
                    'max_cost_per_kw': 2000,
                    'min_self_sufficiency': 0.90
                }
            },
            
            'minimal_config': {
                'id': 'minimal_config',
                'name': 'Minimal Configuration',
                'description': 'Basic configuration with minimal complexity and lower capital cost',
                'category': 'economic',
                'version': '1.0',
                'created_date': '2024-01-01',
                'parameters': {
                    'ambient_temp': 298.15,
                    'pressure_ratio': 8.0,
                    'max_turbine_temp': 1200.0,
                    'compressor_efficiency': 0.82,
                    'turbine_efficiency': 0.85,
                    'ad_retention_time': 25.0,
                    'ad_temperature': 303.15,
                    'htc_reactor_temp': 453.15,
                    'htc_residence_time': 3.0,
                    'biomass_moisture': 0.12,
                    'biomass_rate': 2000.0,
                    'waste_diversion_rate': 0.70,
                    'htc_biomass_rate': 300.0,
                    'heat_recovery_efficiency': 0.65
                },
                'expected_performance': {
                    'net_power': 65000,
                    'system_efficiency': 0.35,
                    'biogas_yield': 1800,
                    'hydrochar_yield': 200,
                    'self_sufficiency_ratio': 0.60,
                    'lcoe_usd_kwh': 0.095,
                    'carbon_intensity_g_kwh': 150
                },
                'constraints': {
                    'min_efficiency': 0.30,
                    'max_cost_per_kw': 800,
                    'min_self_sufficiency': 0.50
                }
            },
            
            'high_efficiency': {
                'id': 'high_efficiency',
                'name': 'High Efficiency Focus',
                'description': 'Maximum efficiency with advanced components and optimized integration',
                'category': 'efficiency_focused',
                'version': '1.0',
                'created_date': '2024-01-01',
                'parameters': {
                    'ambient_temp': 298.15,
                    'pressure_ratio': 20.0,
                    'max_turbine_temp': 1600.0,
                    'compressor_efficiency': 0.92,
                    'turbine_efficiency': 0.95,
                    'ad_retention_time': 10.0,
                    'ad_temperature': 323.15,
                    'htc_reactor_temp': 533.15,
                    'htc_residence_time': 0.8,
                    'biomass_moisture': 0.05,
                    'biomass_rate': 4500.0,
                    'waste_diversion_rate': 0.99,
                    'htc_biomass_rate': 800.0,
                    'heat_recovery_efficiency': 0.95
                },
                'expected_performance': {
                    'net_power': 150000,
                    'system_efficiency': 0.65,
                    'biogas_yield': 4200,
                    'hydrochar_yield': 630,
                    'self_sufficiency_ratio': 1.05,
                    'lcoe_usd_kwh': 0.06,
                    'carbon_intensity_g_kwh': 50
                },
                'constraints': {
                    'min_efficiency': 0.60,
                    'max_cost_per_kw': 2500,
                    'min_self_sufficiency': 1.0
                }
            },
            
            'environmental': {
                'id': 'environmental',
                'name': 'Environmental Priority',
                'description': 'Configuration optimized for minimal environmental impact',
                'category': 'environmental',
                'version': '1.0',
                'created_date': '2024-01-01',
                'parameters': {
                    'ambient_temp': 298.15,
                    'pressure_ratio': 10.0,
                    'max_turbine_temp': 1300.0,
                    'compressor_efficiency': 0.88,
                    'turbine_efficiency': 0.90,
                    'ad_retention_time': 30.0,
                    'ad_temperature': 308.15,
                    'htc_reactor_temp': 463.15,
                    'htc_residence_time': 2.5,
                    'biomass_moisture': 0.08,
                    'biomass_rate': 2500.0,
                    'waste_diversion_rate': 0.95,
                    'htc_biomass_rate': 400.0,
                    'heat_recovery_efficiency': 0.90,
                    'carbon_capture_enabled': True
                },
                'expected_performance': {
                    'net_power': 75000,
                    'system_efficiency': 0.40,
                    'biogas_yield': 2800,
                    'hydrochar_yield': 350,
                    'self_sufficiency_ratio': 0.90,
                    'lcoe_usd_kwh': 0.09,
                    'carbon_intensity_g_kwh': 20,
                    'carbon_sequestered_ton_year': 500
                },
                'constraints': {
                    'min_efficiency': 0.35,
                    'max_cost_per_kw': 1800,
                    'min_self_sufficiency': 0.85,
                    'max_carbon_intensity': 50
                }
            }
        }
    
    def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Get a specific scenario by ID with full details."""
        if scenario_id in self.custom_scenarios:
            return self.custom_scenarios[scenario_id].copy()
        if scenario_id in self.scenarios:
            return self.scenarios[scenario_id].copy()
        raise ValueError(f"Scenario '{scenario_id}' not found. Available: {self.get_available_ids()}")
    
    def get_all_scenarios(self) -> Dict[str, Any]:
        """Get all available scenarios with summary information."""
        all_scenarios = {**self.scenarios, **self.custom_scenarios}
        return {
            scenario_id: {
                'id': scenario_id,
                'name': scenario['name'],
                'description': scenario['description'],
                'category': scenario.get('category', 'general'),
                'version': scenario.get('version', '1.0'),
                'expected_performance': scenario['expected_performance']
            }
            for scenario_id, scenario in all_scenarios.items()
        }
    
    def get_available_ids(self) -> List[str]:
        """Get list of all available scenario IDs."""
        return list(self.scenarios.keys()) + list(self.custom_scenarios.keys())
    
    def create_custom_scenario(self, name: str, description: str, 
                             parameters: Dict[str, Any], 
                             expected_performance: Dict[str, Any] = None,
                             base_scenario: str = None) -> str:
        """Create a custom scenario, optionally based on an existing one."""
        
        if base_scenario and base_scenario in self.scenarios:
            base = self.scenarios[base_scenario].copy()
            base['parameters'].update(parameters)
            if expected_performance:
                base['expected_performance'].update(expected_performance)
            parameters = base['parameters']
            expected_performance = base['expected_performance']
        
        scenario_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        self.custom_scenarios[scenario_id] = {
            'id': scenario_id,
            'name': name,
            'description': description,
            'category': 'custom',
            'version': '1.0',
            'created_date': datetime.now().isoformat(),
            'parameters': parameters,
            'expected_performance': expected_performance or {},
            'is_custom': True
        }
        
        # Save to history
        self.version_history[scenario_id] = [self.custom_scenarios[scenario_id].copy()]
        
        return scenario_id
    
    def update_scenario(self, scenario_id: str, updates: Dict[str, Any]) -> str:
        """Update an existing custom scenario, creating a new version."""
        if scenario_id not in self.custom_scenarios:
            raise ValueError(f"Cannot update built-in scenario '{scenario_id}'")
        
        current = self.custom_scenarios[scenario_id]
        new_version = current.copy()
        
        if 'parameters' in updates:
            new_version['parameters'].update(updates['parameters'])
        if 'expected_performance' in updates:
            new_version['expected_performance'].update(updates['expected_performance'])
        if 'name' in updates:
            new_version['name'] = updates['name']
        if 'description' in updates:
            new_version['description'] = updates['description']
        
        new_version['version'] = str(float(current['version']) + 0.1)
        new_version['last_modified'] = datetime.now().isoformat()
        
        self.custom_scenarios[scenario_id] = new_version
        
        # Add to version history
        if scenario_id not in self.version_history:
            self.version_history[scenario_id] = []
        self.version_history[scenario_id].append(new_version.copy())
        
        return scenario_id
    
    def compare_scenarios(self, scenario_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple scenarios with detailed analysis."""
        comparison = {
            'scenarios': {},
            'differences': {},
            'rankings': {}
        }
        
        valid_ids = [sid for sid in scenario_ids if sid in self.scenarios or sid in self.custom_scenarios]
        
        for scenario_id in valid_ids:
            scenario = self.get_scenario(scenario_id)
            comparison['scenarios'][scenario_id] = {
                'name': scenario['name'],
                'parameters': scenario['parameters'],
                'expected_performance': scenario['expected_performance'],
                'constraints': scenario.get('constraints', {})
            }
        
        # Calculate differences if 2+ scenarios
        if len(valid_ids) >= 2:
            base = comparison['scenarios'][valid_ids[0]]
            for sid in valid_ids[1:]:
                current = comparison['scenarios'][sid]
                comparison['differences'][sid] = {
                    'vs_' + valid_ids[0]: {
                        'parameter_changes': {
                            k: {'from': base['parameters'].get(k), 'to': v}
                            for k, v in current['parameters'].items()
                            if base['parameters'].get(k) != v
                        },
                        'performance_changes': {
                            k: {
                                'absolute': current['expected_performance'].get(k, 0) - base['expected_performance'].get(k, 0),
                                'percent': ((current['expected_performance'].get(k, 0) / base['expected_performance'].get(k, 1) - 1) * 100) if base['expected_performance'].get(k, 0) != 0 else 0
                            }
                            for k in set(base['expected_performance'].keys()) | set(current['expected_performance'].keys())
                            if base['expected_performance'].get(k) != current['expected_performance'].get(k)
                        }
                    }
                }
        
        # Rankings
        metrics = ['system_efficiency', 'net_power', 'self_sufficiency_ratio', 'lcoe_usd_kwh']
        for metric in metrics:
            sorted_scenarios = sorted(
                [(sid, data['expected_performance'].get(metric, 0)) 
                 for sid, data in comparison['scenarios'].items()],
                key=lambda x: x[1],
                reverse=(metric != 'lcoe_usd_kwh')  # Lower LCOE is better
            )
            comparison['rankings'][metric] = [
                {'rank': i+1, 'scenario_id': sid, 'value': val}
                for i, (sid, val) in enumerate(sorted_scenarios)
            ]
        
        return comparison
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters against acceptable ranges."""
        ranges = self.get_parameter_ranges()
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        for param, value in parameters.items():
            if param not in ranges:
                validation_results['warnings'].append(f"Unknown parameter: {param}")
                continue
            
            param_range = ranges[param]
            min_val, max_val = param_range['min'], param_range['max']
            
            if value < min_val or value > max_val:
                validation_results['valid'] = False
                validation_results['errors'].append({
                    'parameter': param,
                    'value': value,
                    'allowed_range': [min_val, max_val],
                    'unit': param_range['unit']
                })
            elif value < min_val + (max_val - min_val) * 0.1 or value > max_val - (max_val - min_val) * 0.1:
                validation_results['warnings'].append({
                    'parameter': param,
                    'value': value,
                    'message': f"Value near boundary of acceptable range [{min_val}, {max_val}]"
                })
            
            # Optimization suggestions
            if param == 'pressure_ratio' and value < 10:
                validation_results['suggestions'].append({
                    'parameter': param,
                    'suggestion': 'Consider increasing pressure ratio for better efficiency',
                    'potential_improvement': '+5-10% efficiency'
                })
            elif param == 'compressor_efficiency' and value < 0.85:
                validation_results['suggestions'].append({
                    'parameter': param,
                    'suggestion': 'Higher compressor efficiency available with advanced designs',
                    'potential_improvement': '+3-5% overall efficiency'
                })
        
        return validation_results
    
    def get_parameter_ranges(self) -> Dict[str, Any]:
        """Get acceptable parameter ranges for validation."""
        return {
            'ambient_temp': {'min': 273.15, 'max': 323.15, 'unit': 'K', 'description': 'Ambient temperature'},
            'pressure_ratio': {'min': 3.0, 'max': 25.0, 'unit': '', 'description': 'Compressor pressure ratio'},
            'max_turbine_temp': {'min': 800, 'max': 1800, 'unit': 'K', 'description': 'Maximum turbine inlet temperature'},
            'compressor_efficiency': {'min': 0.75, 'max': 0.95, 'unit': '', 'description': 'Compressor isentropic efficiency'},
            'turbine_efficiency': {'min': 0.80, 'max': 0.98, 'unit': '', 'description': 'Turbine isentropic efficiency'},
            'ad_retention_time': {'min': 5, 'max': 40, 'unit': 'days', 'description': 'AD hydraulic retention time'},
            'ad_temperature': {'min': 293.15, 'max': 333.15, 'unit': 'K', 'description': 'AD operating temperature'},
            'htc_reactor_temp': {'min': 423.15, 'max': 573.15, 'unit': 'K', 'description': 'HTC reactor temperature'},
            'htc_residence_time': {'min': 0.5, 'max': 5.0, 'unit': 'hours', 'description': 'HTC residence time'},
            'biomass_moisture': {'min': 0.05, 'max': 0.20, 'unit': '', 'description': 'Biomass moisture content'},
            'biomass_rate': {'min': 1000, 'max': 10000, 'unit': 'kg/day', 'description': 'Biomass feed rate'},
            'waste_diversion_rate': {'min': 0.5, 'max': 1.0, 'unit': '', 'description': 'Waste diversion rate'},
            'heat_recovery_efficiency': {'min': 0.5, 'max': 0.98, 'unit': '', 'description': 'Heat recovery efficiency'}
        }
    
    def export_scenario(self, scenario_id: str, format: str = 'json') -> str:
        """Export scenario to JSON or other formats."""
        scenario = self.get_scenario(scenario_id)
        
        if format == 'json':
            return json.dumps(scenario, indent=2)
        elif format == 'csv':
            # Flatten parameters for CSV
            lines = ['Parameter,Value,Unit']
            for k, v in scenario['parameters'].items():
                unit = self.get_parameter_ranges().get(k, {}).get('unit', '')
                lines.append(f"{k},{v},{unit}")
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_scenario(self, data: str, format: str = 'json') -> str:
        """Import scenario from external format."""
        if format == 'json':
            scenario_data = json.loads(data)
            return self.create_custom_scenario(
                name=scenario_data.get('name', 'Imported Scenario'),
                description=scenario_data.get('description', 'Imported from external source'),
                parameters=scenario_data.get('parameters', {}),
                expected_performance=scenario_data.get('expected_performance', {})
            )
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_recommendations(self, goals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get scenario recommendations based on goals."""
        recommendations = []
        
        all_scenarios = self.get_all_scenarios()
        
        for scenario_id, scenario in all_scenarios.items():
            score = 0
            reasons = []
            
            if goals.get('maximize_efficiency'):
                eff = scenario['expected_performance'].get('system_efficiency', 0)
                score += eff * 100
                reasons.append(f"Efficiency: {eff*100:.1f}%")
            
            if goals.get('maximize_power'):
                power = scenario['expected_performance'].get('net_power', 0)
                score += power / 1000  # Normalize
                reasons.append(f"Power: {power/1000:.1f} MW")
            
            if goals.get('minimize_cost'):
                lcoe = scenario['expected_performance'].get('lcoe_usd_kwh', 0.1)
                score += (0.15 - lcoe) * 100  # Lower is better
                reasons.append(f"LCOE: ${lcoe:.3f}/kWh")
            
            if goals.get('environmental'):
                carbon = scenario['expected_performance'].get('carbon_intensity_g_kwh', 200)
                score += (200 - carbon) / 2  # Lower is better
                reasons.append(f"Carbon: {carbon:.0f} g/kWh")
            
            recommendations.append({
                'scenario_id': scenario_id,
                'name': scenario['name'],
                'score': score,
                'reasons': reasons,
                'category': scenario.get('category', 'general')
            })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]  # Top 5 recommendations