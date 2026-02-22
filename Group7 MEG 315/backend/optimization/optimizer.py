import numpy as np
from typing import Dict, Any, List
from scipy.optimize import minimize
import json

class SystemOptimizer:
    """
    Multi-objective optimization for AD-HTC integrated system
    Uses genetic algorithm and gradient descent methods
    """
    
    def __init__(self):
        self.optimization_methods = ['genetic', 'gradient', 'pareto']
        self.default_bounds = {
            'pressure_ratio': (3, 25),
            'max_turbine_temp': (800, 1500),
            'compressor_efficiency': (0.75, 0.95),
            'turbine_efficiency': (0.80, 0.95),
            'ad_retention_time': (10, 30),
            'htc_temperature': (453, 523),
            'htc_residence_time': (0.5, 4.0)
        }
        
        # Reference values for normalization
        self.reference_power = 100000  # kW (100 MW)
        self.reference_efficiency = 0.35  # 35%
        self.reference_cost = 1000  # $/kW
    
    def optimize(self, objectives: Dict[str, Any], 
                constraints: Dict[str, Any] = None,
                method: str = 'genetic') -> Dict[str, Any]:
        """
        Main optimization function
        
        Args:
            objectives: Dictionary with optimization objectives
                - 'maximize': List of parameters to maximize
                - 'minimize': List of parameters to minimize
                - 'weights': Weights for multi-objective optimization
            constraints: Optional constraints dictionary
            method: Optimization method ('genetic', 'gradient', 'pareto')
        
        Returns:
            Dictionary with optimized parameters and performance
        """
        
        if method == 'genetic':
            return self._genetic_optimization(objectives, constraints)
        elif method == 'gradient':
            return self._gradient_optimization(objectives, constraints)
        elif method == 'pareto':
            return self._pareto_optimization(objectives, constraints)
        else:
            raise ValueError(f"Unknown optimization method: {method}")
    
    def _genetic_optimization(self, objectives: Dict[str, Any], 
                               constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Genetic algorithm optimization
        """
        
        # Define optimization variables
        variables = ['pressure_ratio', 'max_turbine_temp', 'compressor_efficiency', 
                    'turbine_efficiency', 'ad_retention_time', 'htc_temperature']
        
        # Create initial population
        population_size = 50
        generations = 100
        mutation_rate = 0.1
        
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = {}
            for var in variables:
                bounds = self.default_bounds[var]
                individual[var] = np.random.uniform(bounds[0], bounds[1])
            population.append(individual)
        
        # Evolution loop
        best_fitness = -np.inf
        best_individual = None
        fitness_history = []
        
        for generation in range(generations):
            # Evaluate fitness for each individual
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_fitness(individual, objectives)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
            
            fitness_history.append(best_fitness)
            
            # Selection (tournament selection)
            new_population = []
            for _ in range(population_size):
                tournament_size = 3
                tournament_indices = np.random.choice(len(population), tournament_size)
                tournament_fitness = [fitness_scores[i] for i in tournament_indices]
                winner_idx = tournament_indices[np.argmax(tournament_fitness)]
                new_population.append(population[winner_idx].copy())
            
            # Crossover
            for i in range(0, population_size-1, 2):
                if np.random.random() < 0.8:  # Crossover probability
                    crossover_point = np.random.randint(1, len(variables))
                    parent1 = new_population[i]
                    parent2 = new_population[i+1]
                    
                    child1 = {}
                    child2 = {}
                    for j, var in enumerate(variables):
                        if j < crossover_point:
                            child1[var] = parent1[var]
                            child2[var] = parent2[var]
                        else:
                            child1[var] = parent2[var]
                            child2[var] = parent1[var]
                    
                    new_population[i] = child1
                    new_population[i+1] = child2
            
            # Mutation
            for individual in new_population:
                for var in variables:
                    if np.random.random() < mutation_rate:
                        bounds = self.default_bounds[var]
                        mutation = np.random.normal(0, (bounds[1] - bounds[0]) * 0.1)
                        individual[var] = np.clip(individual[var] + mutation, bounds[0], bounds[1])
            
            population = new_population
        
        # Evaluate final performance
        final_performance = self._evaluate_system_performance(best_individual)
        
        return {
            "optimized_parameters": best_individual,
            "fitness_score": best_fitness,
            "performance_metrics": final_performance,
            "optimization_method": "genetic_algorithm",
            "generations": generations,
            "population_size": population_size,
            "fitness_history": fitness_history
        }
    
    def _gradient_optimization(self, objectives: Dict[str, Any], 
                               constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Gradient-based optimization using scipy minimize
        """
        
        # Define initial guess
        x0 = [8.0, 1200.0, 0.85, 0.90, 20.0, 473.0]  # Initial values
        
        # Define bounds
        bounds = [
            self.default_bounds['pressure_ratio'],
            self.default_bounds['max_turbine_temp'],
            self.default_bounds['compressor_efficiency'],
            self.default_bounds['turbine_efficiency'],
            self.default_bounds['ad_retention_time'],
            self.default_bounds['htc_temperature']
        ]
        
        # Define objective function (negative for maximization)
        def objective_function(x):
            params = {
                'pressure_ratio': x[0],
                'max_turbine_temp': x[1],
                'compressor_efficiency': x[2],
                'turbine_efficiency': x[3],
                'ad_retention_time': x[4],
                'htc_temperature': x[5]
            }
            return -self._evaluate_fitness(params, objectives)
        
        # Run optimization
        result = minimize(objective_function, x0, method='L-BFGS-B', bounds=bounds)
        
        # Extract optimized parameters
        optimized_params = {
            'pressure_ratio': result.x[0],
            'max_turbine_temp': result.x[1],
            'compressor_efficiency': result.x[2],
            'turbine_efficiency': result.x[3],
            'ad_retention_time': result.x[4],
            'htc_temperature': result.x[5]
        }
        
        # Evaluate final performance
        final_performance = self._evaluate_system_performance(optimized_params)
        
        return {
            "optimized_parameters": optimized_params,
            "fitness_score": -result.fun,
            "performance_metrics": final_performance,
            "optimization_method": "gradient_descent",
            "optimization_result": result
        }
    
    def _pareto_optimization(self, objectives: Dict[str, Any], 
                              constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Pareto frontier optimization for multi-objective problems
        """
        
        # Generate sample points
        n_samples = 100
        pressure_ratios = np.linspace(3, 25, n_samples)
        turbine_temps = np.linspace(800, 1500, n_samples)
        
        # Evaluate all combinations
        pareto_solutions = []
        
        for pr in pressure_ratios:
            for tt in turbine_temps:
                params = {
                    'pressure_ratio': pr,
                    'max_turbine_temp': tt,
                    'compressor_efficiency': 0.85,
                    'turbine_efficiency': 0.90,
                    'ad_retention_time': 20.0,
                    'htc_temperature': 473.0
                }
                
                performance = self._evaluate_system_performance(params)
                
                # Check if solution is feasible (constraints)
                if constraints and not self._check_constraints(performance, constraints):
                    continue
                
                pareto_solutions.append({
                    'parameters': params,
                    'performance': performance,
                    'efficiency': performance.get('overall_efficiency', 0),
                    'cost': performance.get('specific_cost', 0)
                })
        
        # Find Pareto frontier
        pareto_frontier = []
        for solution in pareto_solutions:
            is_dominated = False
            for other in pareto_solutions:
                if (other['efficiency'] >= solution['efficiency'] and 
                    other['cost'] <= solution['cost'] and
                    (other['efficiency'] > solution['efficiency'] or 
                     other['cost'] < solution['cost'])):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_frontier.append(solution)
        
        # Sort by efficiency
        pareto_frontier.sort(key=lambda x: x['efficiency'], reverse=True)
        
        return {
            "pareto_frontier": pareto_frontier,
            "all_solutions": pareto_solutions,
            "optimization_method": "pareto",
            "num_pareto_solutions": len(pareto_frontier)
        }
    
    def _evaluate_fitness(self, parameters: Dict[str, float], 
                         objectives: Dict[str, Any]) -> float:
        """
        Evaluate fitness function for optimization
        """
        
        # Get system performance
        performance = self._evaluate_system_performance(parameters)
        
        # Calculate fitness based on objectives
        fitness = 0.0
        weights = objectives.get('weights', {})
        
        # Efficiency component
        if 'efficiency' in objectives.get('maximize', []):
            weight = weights.get('efficiency', 1.0)
            fitness += weight * performance.get('overall_efficiency', 0)
        
        # Power output component
        if 'power_output' in objectives.get('maximize', []):
            weight = weights.get('power_output', 1.0)
            normalized_power = performance.get('net_power_kw', 0) / self.reference_power
            fitness += weight * normalized_power
        
        # Cost component
        if 'specific_cost' in objectives.get('minimize', []):
            weight = weights.get('specific_cost', 1.0)
            normalized_cost = performance.get('specific_cost', self.reference_cost) / self.reference_cost
            fitness += weight * (1.0 - normalized_cost)  # Minimize cost
        
        # Self-sufficiency component
        if 'self_sufficiency' in objectives.get('maximize', []):
            weight = weights.get('self_sufficiency', 1.0)
            fitness += weight * performance.get('self_sufficiency_ratio', 0)
        
        return fitness
    
    def _evaluate_system_performance(self, parameters: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluate system performance with given parameters
        """
        
        # Simulate system performance (simplified model)
        # In practice, this would call the thermodynamic models
        
        pr = parameters['pressure_ratio']
        t3 = parameters['max_turbine_temp']
        eta_comp = parameters['compressor_efficiency']
        eta_turb = parameters['turbine_efficiency']
        rt = parameters['ad_retention_time']
        htc_temp = parameters['htc_temperature']
        
        # Simplified performance model
        # Brayton cycle efficiency
        gamma = 1.4
        ideal_efficiency = 1 - (1 / pr**((gamma-1)/gamma))
        actual_efficiency = ideal_efficiency * eta_comp * eta_turb * (1 - 0.1 * (t3 - 1000) / 1000)
        
        # Power output (scaled)
        net_power = 100000 * (actual_efficiency / 0.35)  # Reference: 100MW at 35% efficiency
        
        # AD performance
        biogas_yield = 0.8 * (20 / rt)  # Higher yield with shorter retention time
        biogas_energy = 50000 * biogas_yield  # kW (reference)
        
        # HTC performance
        htc_efficiency = 0.75 - 0.001 * (htc_temp - 473)  # Efficiency decreases with temperature
        heat_demand = 20000 / htc_efficiency  # kW
        
        # Self-sufficiency
        waste_heat_available = biogas_energy * 0.6  # 60% of biogas energy as waste heat
        self_sufficiency = min(waste_heat_available / heat_demand, 1.0) if heat_demand > 0 else 0
        
        # Cost estimation (simplified)
        specific_cost = 1000 * (1 + 0.1 * (pr - 6) / 6)  # $/kW
        
        return {
            'overall_efficiency': actual_efficiency,
            'net_power_kw': net_power,
            'biogas_energy_kw': biogas_energy,
            'htc_heat_demand_kw': heat_demand,
            'waste_heat_available_kw': waste_heat_available,
            'self_sufficiency_ratio': self_sufficiency,
            'specific_cost': specific_cost
        }
    
    def _check_constraints(self, performance: Dict[str, Any], 
                          constraints: Dict[str, Any]) -> bool:
        """
        Check if performance meets constraints
        """
        
        if 'min_efficiency' in constraints:
            if performance.get('overall_efficiency', 0) < constraints['min_efficiency']:
                return False
        
        if 'max_cost' in constraints:
            if performance.get('specific_cost', 0) > constraints['max_cost']:
                return False
        
        if 'min_self_sufficiency' in constraints:
            if performance.get('self_sufficiency_ratio', 0) < constraints['min_self_sufficiency']:
                return False
        
        return True