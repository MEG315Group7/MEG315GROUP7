"""
System Optimization Module
Multi-objective optimization for AD-HTC integrated system
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class OptimizationMethod(Enum):
    GENETIC = "genetic"
    GRADIENT = "gradient"
    PARETO = "pareto"

@dataclass
class OptimizationConfig:
    """Optimization configuration"""
    objectives: Dict[str, Any]  # {'maximize': ['efficiency'], 'minimize': ['cost']}
    constraints: Optional[Dict[str, Any]] = None
    method: OptimizationMethod = OptimizationMethod.GENETIC
    population_size: int = 50
    generations: int = 100
    mutation_rate: float = 0.1

class SystemOptimizer:
    """
    Multi-objective optimizer for AD-HTC system
    Supports genetic algorithm, gradient descent, and Pareto frontier
    """

    def __init__(self):
        self.bounds = {
            'pressure_ratio': (3.0, 25.0),
            'max_turbine_temp': (800.0, 1600.0),
            'compressor_efficiency': (0.75, 0.95),
            'turbine_efficiency': (0.80, 0.95),
            'ad_retention_time': (10.0, 40.0),
            'htc_temperature': (453.0, 523.0),
            'htc_residence_time': (0.5, 4.0)
        }

        self.reference_power = 100000  # kW
        self.reference_efficiency = 0.35
        self.reference_cost = 1000  # $/kW

    def optimize(self, config: OptimizationConfig) -> Dict[str, Any]:
        """
        Main optimization entry point

        Args:
            config: OptimizationConfig with objectives and method
        """

        if config.method == OptimizationMethod.GENETIC:
            return self._genetic_optimization(config)
        elif config.method == OptimizationMethod.GRADIENT:
            return self._gradient_optimization(config)
        elif config.method == OptimizationMethod.PARETO:
            return self._pareto_optimization(config)
        else:
            raise ValueError(f"Unknown optimization method: {config.method}")

    def _genetic_optimization(self, config: OptimizationConfig) -> Dict[str, Any]:
        """Genetic algorithm optimization"""

        variables = list(self.bounds.keys())
        population = []

        # Initialize population
        for _ in range(config.population_size):
            individual = {}
            for var in variables:
                bounds = self.bounds[var]
                individual[var] = np.random.uniform(bounds[0], bounds[1])
            population.append(individual)

        best_fitness = -np.inf
        best_individual = None
        fitness_history = []

        # Evolution loop
        for generation in range(config.generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_fitness(individual, config.objectives)
                fitness_scores.append(fitness)

                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()

            fitness_history.append(best_fitness)

            # Selection (tournament)
            new_population = []
            for _ in range(config.population_size):
                tournament_idx = np.random.choice(len(population), 3)
                tournament_fitness = [fitness_scores[i] for i in tournament_idx]
                winner_idx = tournament_idx[np.argmax(tournament_fitness)]
                new_population.append(population[winner_idx].copy())

            # Crossover
            for i in range(0, config.population_size - 1, 2):
                if np.random.random() < 0.8:
                    crossover_point = np.random.randint(1, len(variables))
                    parent1 = new_population[i]
                    parent2 = new_population[i + 1]

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
                    new_population[i + 1] = child2

            # Mutation
            for individual in new_population:
                for var in variables:
                    if np.random.random() < config.mutation_rate:
                        bounds = self.bounds[var]
                        mutation = np.random.normal(0, (bounds[1] - bounds[0]) * 0.1)
                        individual[var] = np.clip(individual[var] + mutation, 
                                                 bounds[0], bounds[1])

            population = new_population

        # Final evaluation
        performance = self._evaluate_system_performance(best_individual)

        return {
            "optimized_parameters": best_individual,
            "fitness_score": best_fitness,
            "performance_metrics": performance,
            "optimization_method": "genetic_algorithm",
            "generations": config.generations,
            "population_size": config.population_size,
            "fitness_history": fitness_history,
            "convergence": self._calculate_convergence(fitness_history)
        }

    def _gradient_optimization(self, config: OptimizationConfig) -> Dict[str, Any]:
        """Gradient-based optimization using numerical gradients"""

        # Initial guess
        x0 = np.array([12.0, 1400.0, 0.85, 0.88, 20.0, 473.0, 2.0])

        # Bounds
        bounds = [
            self.bounds['pressure_ratio'],
            self.bounds['max_turbine_temp'],
            self.bounds['compressor_efficiency'],
            self.bounds['turbine_efficiency'],
            self.bounds['ad_retention_time'],
            self.bounds['htc_temperature'],
            self.bounds['htc_residence_time']
        ]

        # Simple gradient descent
        learning_rate = 0.1
        max_iterations = 1000
        tolerance = 1e-6

        x = x0.copy()
        history = []

        for iteration in range(max_iterations):
            # Calculate gradient numerically
            gradient = self._numerical_gradient(x, config.objectives)

            # Update
            x_new = x + learning_rate * gradient

            # Apply bounds
            for i, (lower, upper) in enumerate(bounds):
                x_new[i] = np.clip(x_new[i], lower, upper)

            # Check convergence
            if np.linalg.norm(x_new - x) < tolerance:
                break

            x = x_new

            # Evaluate and store
            params = self._array_to_params(x)
            fitness = self._evaluate_fitness(params, config.objectives)
            history.append(fitness)

        final_params = self._array_to_params(x)
        performance = self._evaluate_system_performance(final_params)

        return {
            "optimized_parameters": final_params,
            "fitness_score": history[-1] if history else 0,
            "performance_metrics": performance,
            "optimization_method": "gradient_descent",
            "iterations": iteration + 1,
            "fitness_history": history,
            "convergence": self._calculate_convergence(history)
        }

    def _pareto_optimization(self, config: OptimizationConfig) -> Dict[str, Any]:
        """Pareto frontier for multi-objective optimization"""

        # Sample points
        n_samples = 50
        pressure_ratios = np.linspace(3, 25, n_samples)
        turbine_temps = np.linspace(800, 1600, n_samples)

        solutions = []

        for pr in pressure_ratios:
            for tt in turbine_temps:
                params = {
                    'pressure_ratio': pr,
                    'max_turbine_temp': tt,
                    'compressor_efficiency': 0.85,
                    'turbine_efficiency': 0.90,
                    'ad_retention_time': 20.0,
                    'htc_temperature': 473.0,
                    'htc_residence_time': 2.0
                }

                performance = self._evaluate_system_performance(params)

                # Check constraints
                if config.constraints and not self._check_constraints(performance, config.constraints):
                    continue

                solutions.append({
                    'parameters': params,
                    'performance': performance,
                    'efficiency': performance.get('overall_efficiency', 0),
                    'power': performance.get('net_power_kw', 0),
                    'cost': performance.get('specific_cost', 1000)
                })

        # Find Pareto frontier
        pareto_frontier = []
        for sol in solutions:
            is_dominated = False
            for other in solutions:
                if (other['efficiency'] >= sol['efficiency'] and 
                    other['power'] >= sol['power'] and
                    other['cost'] <= sol['cost'] and
                    (other['efficiency'] > sol['efficiency'] or 
                     other['power'] > sol['power'] or
                     other['cost'] < sol['cost'])):
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_frontier.append(sol)

        pareto_frontier.sort(key=lambda x: x['efficiency'], reverse=True)

        return {
            "pareto_frontier": pareto_frontier,
            "all_solutions": solutions,
            "optimization_method": "pareto",
            "num_pareto_solutions": len(pareto_frontier)
        }

    def _evaluate_fitness(self, parameters: Dict[str, float], 
                         objectives: Dict[str, Any]) -> float:
        """Evaluate fitness function"""

        performance = self._evaluate_system_performance(parameters)
        fitness = 0.0
        weights = objectives.get('weights', {})

        # Efficiency component
        if 'efficiency' in objectives.get('maximize', []):
            weight = weights.get('efficiency', 1.0)
            fitness += weight * performance.get('overall_efficiency', 0)

        # Power component
        if 'power_output' in objectives.get('maximize', []):
            weight = weights.get('power_output', 1.0)
            normalized_power = performance.get('net_power_kw', 0) / self.reference_power
            fitness += weight * normalized_power

        # Cost component (minimize)
        if 'specific_cost' in objectives.get('minimize', []):
            weight = weights.get('specific_cost', 1.0)
            normalized_cost = performance.get('specific_cost', self.reference_cost) / self.reference_cost
            fitness += weight * (1.0 - normalized_cost)

        # Self-sufficiency
        if 'self_sufficiency' in objectives.get('maximize', []):
            weight = weights.get('self_sufficiency', 1.0)
            fitness += weight * performance.get('self_sufficiency_ratio', 0)

        return fitness

    def _evaluate_system_performance(self, parameters: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate system performance with given parameters"""

        # Simplified performance model
        pr = parameters.get('pressure_ratio', 12.0)
        t3 = parameters.get('max_turbine_temp', 1400.0)
        eta_comp = parameters.get('compressor_efficiency', 0.85)
        eta_turb = parameters.get('turbine_efficiency', 0.88)
        rt = parameters.get('ad_retention_time', 20.0)
        htc_temp = parameters.get('htc_temperature', 473.0)

        # Brayton efficiency
        gamma = 1.4
        ideal_eff = 1 - (1 / pr ** ((gamma - 1) / gamma))
        actual_eff = ideal_eff * eta_comp * eta_turb * (1 - 0.1 * (t3 - 1000) / 1000)

        # Power output
        net_power = 100000 * (actual_eff / 0.35)

        # AD performance
        biogas_yield = 0.8 * (20 / rt) if rt > 0 else 0
        biogas_energy = 50000 * biogas_yield

        # HTC performance
        htc_eff = 0.75 - 0.001 * (htc_temp - 473)
        heat_demand = 20000 / htc_eff if htc_eff > 0 else 0

        # Self-sufficiency
        waste_heat = biogas_energy * 0.6
        self_suff = min(waste_heat / heat_demand, 1.0) if heat_demand > 0 else 0

        # Cost
        specific_cost = 1000 * (1 + 0.1 * (pr - 6) / 6)

        return {
            'overall_efficiency': actual_eff,
            'net_power_kw': net_power,
            'biogas_energy_kw': biogas_energy,
            'htc_heat_demand_kw': heat_demand,
            'waste_heat_available_kw': waste_heat,
            'self_sufficiency_ratio': self_suff,
            'specific_cost': specific_cost
        }

    def _numerical_gradient(self, x: np.ndarray, objectives: Dict[str, Any], 
                           h: float = 1e-5) -> np.ndarray:
        """Calculate numerical gradient"""

        gradient = np.zeros_like(x)

        for i in range(len(x)):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += h
            x_minus[i] -= h

            params_plus = self._array_to_params(x_plus)
            params_minus = self._array_to_params(x_minus)

            fitness_plus = self._evaluate_fitness(params_plus, objectives)
            fitness_minus = self._evaluate_fitness(params_minus, objectives)

            gradient[i] = (fitness_plus - fitness_minus) / (2 * h)

        return gradient

    def _array_to_params(self, x: np.ndarray) -> Dict[str, float]:
        """Convert array to parameter dictionary"""

        return {
            'pressure_ratio': x[0],
            'max_turbine_temp': x[1],
            'compressor_efficiency': x[2],
            'turbine_efficiency': x[3],
            'ad_retention_time': x[4],
            'htc_temperature': x[5],
            'htc_residence_time': x[6]
        }

    def _check_constraints(self, performance: Dict[str, Any], 
                          constraints: Dict[str, Any]) -> bool:
        """Check if performance meets constraints"""

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

    def _calculate_convergence(self, history: List[float]) -> Dict[str, float]:
        """Calculate convergence metrics"""

        if len(history) < 10:
            return {"converged": False, "stability": 0.0}

        # Check if fitness has stabilized
        recent = history[-10:]
        variance = np.var(recent)

        return {
            "converged": variance < 1e-6,
            "stability": 1.0 / (1.0 + variance),
            "final_improvement": (history[-1] - history[0]) / abs(history[0]) if history[0] != 0 else 0
        }
