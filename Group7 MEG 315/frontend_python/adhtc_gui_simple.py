#!/usr/bin/env python3
"""
Simplified Standalone Python Frontend for  Group 7 AD-HTC System
Works without any external dependencies - uses only tkinter and standard library
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import time
from datetime import datetime
import math
import sys
import os

# Add backend directory to path to import modules directly
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Fallback calculation classes that work without external dependencies
class BraytonCycle:
    def __init__(self, ambient_temp=298, pressure_ratio=6, max_turbine_temp=1000, 
                 compressor_efficiency=0.85, turbine_efficiency=0.9):
        self.ambient_temp = ambient_temp
        self.pressure_ratio = pressure_ratio
        self.max_turbine_temp = max_turbine_temp
        self.compressor_efficiency = compressor_efficiency
        self.turbine_efficiency = turbine_efficiency
    
    def calculate(self):
        # Simplified Brayton cycle calculation
        T1 = self.ambient_temp
        P1 = 101.325  # kPa
        P2 = P1 * self.pressure_ratio
        
        # Isentropic compression
        T2 = T1 * (P2/P1)**((1.4-1)/1.4) / self.compressor_efficiency
        
        # Combustion
        T3 = self.max_turbine_temp
        
        # Isentropic expansion
        T4 = T3 * (P1/P2)**((1.4-1)/1.4) * self.turbine_efficiency
        
        # Work calculations
        W_comp = 1.005 * (T2 - T1)  # kJ/kg
        W_turb = 1.005 * (T3 - T4)  # kJ/kg
        W_net = W_turb - W_comp
        
        return {
            'compressor_work': W_comp,
            'turbine_work': W_turb,
            'net_work': W_net,
            'thermal_efficiency': W_net / (1.005 * (T3 - T2)) * 100,
            'turbine_inlet_temp': T3,
            'turbine_exit_temp': T4,
            'compressor_exit_temp': T2
        }

class ADSystem:
    def __init__(self, feedstock_rate=3000, retention_time=20, temperature=310):
        self.feedstock_rate = feedstock_rate  # kg/day
        self.retention_time = retention_time  # days
        self.temperature = temperature  # K
    
    def calculate(self):
        # Simplified AD calculation
        biogas_yield = 0.25  # m³ biogas per kg feedstock
        methane_content = 0.6  # 60% methane
        
        total_biogas = self.feedstock_rate * biogas_yield
        methane_production = total_biogas * methane_content
        
        # Energy content of biogas
        biogas_energy = total_biogas * 6.0  # kWh/m³
        methane_energy = methane_production * 10.0  # kWh/m³
        
        return {
            'total_biogas_production': total_biogas,
            'methane_production': methane_production,
            'biogas_energy_content': biogas_energy,
            'methane_energy_content': methane_energy,
            'retention_time': self.retention_time,
            'operating_temperature': self.temperature
        }

class HTCSystem:
    def __init__(self, feedstock_rate=3000, temperature=473, residence_time=1.0):
        self.feedstock_rate = feedstock_rate  # kg/day
        self.temperature = temperature  # K
        self.residence_time = residence_time  # hours
    
    def calculate(self):
        # Simplified HTC calculation
        hydrochar_yield = 0.35  # 35% of feedstock
        energy_density = 25.0  # MJ/kg
        
        hydrochar_production = self.feedstock_rate * hydrochar_yield
        energy_content = hydrochar_production * energy_density
        
        return {
            'hydrochar_production': hydrochar_production,
            'hydrochar_yield': hydrochar_yield * 100,
            'energy_content': energy_content,
            'operating_temperature': self.temperature,
            'residence_time': self.residence_time
        }

class ADHTCSimpleFrontend:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Group 7 - AD-HTC Fuel-Enhanced Gas Power Cycle (Simple)")
        self.root.geometry("1200x800")
        self.root.configure(bg='#F0F8FF')
        
        # Color scheme
        self.colors = {
            'primary': '#2E8B57',      # Sea Green
            'secondary': '#4682B4',    # Steel Blue
            'accent': '#FF6B35',       # Orange
            'success': '#32CD32',      # Lime Green
            'warning': '#FFD700',      # Gold
            'danger': '#DC143C',       # Crimson
            'neutral': '#708090',      # Slate Gray
            'background': '#F0F8FF',   # Alice Blue
            'surface': '#FFFFFF'       # White
        }
        
        # System state
        self.is_animating = True
        self.simulation_time = 0
        self.simulation_speed = 1.0
        self.max_simulation_time = 86400  # 24 hours
        self.calculation_results = None
        self.loading = False
        self.error = None
        
        # Component data
        self.components = {
            'ad1': {'x': 50, 'y': 100, 'name': 'AD Unit 1', 'type': 'ad', 'feedstock': 1000},
            'ad2': {'x': 50, 'y': 180, 'name': 'AD Unit 2', 'type': 'ad', 'feedstock': 1000},
            'ad3': {'x': 50, 'y': 260, 'name': 'AD Unit 3', 'type': 'ad', 'feedstock': 1000},
            'manifold': {'x': 200, 'y': 180, 'name': 'Biogas Manifold', 'type': 'manifold'},
            'combustor': {'x': 350, 'y': 180, 'name': 'Combustor', 'type': 'combustor'},
            'turbine': {'x': 500, 'y': 180, 'name': 'Gas Turbine', 'type': 'turbine'},
            'generator': {'x': 650, 'y': 180, 'name': 'Generator', 'type': 'generator'},
            'heat_exchanger': {'x': 350, 'y': 300, 'name': 'Heat Exchanger', 'type': 'hx'},
            'htc_reactor': {'x': 200, 'y': 380, 'name': 'HTC Reactor', 'type': 'htc'},
            'hrsg': {'x': 500, 'y': 380, 'name': 'HRSG (Future)', 'type': 'hrsg'}
        }
        
        # Flow connections
        self.flows = [
            {'from': 'ad1', 'to': 'manifold', 'type': 'biogas', 'label': 'Biogas'},
            {'from': 'ad2', 'to': 'manifold', 'type': 'biogas', 'label': 'Biogas'},
            {'from': 'ad3', 'to': 'manifold', 'type': 'biogas', 'label': 'Biogas'},
            {'from': 'manifold', 'to': 'combustor', 'type': 'biogas', 'label': 'Biogas'},
            {'from': 'combustor', 'to': 'turbine', 'type': 'combustion', 'label': 'Hot Gas'},
            {'from': 'turbine', 'to': 'generator', 'type': 'shaft', 'label': 'Shaft Work'},
            {'from': 'turbine', 'to': 'heat_exchanger', 'type': 'exhaust', 'label': 'Exhaust 639K'},
            {'from': 'heat_exchanger', 'to': 'htc_reactor', 'type': 'heat', 'label': 'Waste Heat'},
            {'from': 'htc_reactor', 'to': 'hrsg', 'type': 'steam', 'label': 'Steam (Future)'}
        ]
        
        # Particle positions for animation
        self.particle_positions = []
        self.initialize_particles()
        
        # Custom parameters
        self.custom_params = {
            'ambient_temp': 298.15,
            'pressure_ratio': 12.0,
            'max_turbine_temp': 1400,
            'compressor_efficiency': 0.85,
            'turbine_efficiency': 0.88,
            'biomass_rate': 3000,
            'ad_retention_time': 20,
            'htc_temperature': 473
        }
        
        self.setup_ui()
        self.start_simulation_timer()
        
    def initialize_particles(self):
        """Initialize particle positions for flow animation"""
        self.particle_positions = []
        for flow_idx, flow in enumerate(self.flows):
            for i in range(5):
                self.particle_positions.append({
                    'flow_idx': flow_idx,
                    'progress': i * 0.2,
                    'speed': 0.005 + (i % 3) * 0.002  # Simple deterministic speed
                })
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(header_frame, 
                              text="Group 7 - AD-HTC Fuel-Enhanced Gas Power Cycle",
                              font=('Arial', 14, 'bold'),
                              bg=self.colors['primary'],
                              fg='white')
        title_label.pack(pady=10)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        control_frame = tk.Frame(main_frame, bg=self.colors['surface'], 
                                relief=tk.RAISED, bd=2, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        # Simulation controls
        sim_frame = tk.LabelFrame(control_frame, text="Simulation Controls",
                                 bg=self.colors['surface'], font=('Arial', 10, 'bold'))
        sim_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Time display
        self.time_label = tk.Label(sim_frame, text="Time: 0h 0m 0s",
                                  bg=self.colors['surface'], font=('Courier', 9))
        self.time_label.pack(pady=5)
        
        # Control buttons
        btn_frame = tk.Frame(sim_frame, bg=self.colors['surface'])
        btn_frame.pack(pady=5)
        
        self.play_btn = tk.Button(btn_frame, text="Play", command=self.toggle_animation,
                                 bg=self.colors['success'], fg='white', width=6)
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="Reset", command=self.reset_simulation,
                 bg=self.colors['warning'], fg='black', width=6).pack(side=tk.LEFT, padx=2)
        
        # Speed control
        speed_frame = tk.Frame(sim_frame, bg=self.colors['surface'])
        speed_frame.pack(pady=5)
        
        tk.Label(speed_frame, text="Speed:", bg=self.colors['surface']).pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = tk.Scale(speed_frame, from_=0.1, to=3.0, resolution=0.1,
                              variable=self.speed_var, orient=tk.HORIZONTAL,
                              length=100, bg=self.colors['surface'])
        speed_scale.pack(side=tk.LEFT)
        
        # Calculation controls
        calc_frame = tk.LabelFrame(control_frame, text="Calculation Controls",
                                  bg=self.colors['surface'], font=('Arial', 10, 'bold'))
        calc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Preset scenarios
        tk.Label(calc_frame, text="Preset Scenarios:", bg=self.colors['surface']).pack(pady=5)
        
        self.scenario_var = tk.StringVar(value="standard")
        scenarios = [
            ("Standard", "standard"),
            ("High Efficiency", "high_efficiency"),
            ("Maximum Power", "max_power"),
            ("Economic Optimal", "economic_optimal"),
            ("Environmental", "environmental")
        ]
        
        for text, value in scenarios:
            tk.Radiobutton(calc_frame, text=text, variable=self.scenario_var, 
                          value=value, bg=self.colors['surface']).pack(anchor=tk.W)
        
        # Calculate buttons
        btn_frame2 = tk.Frame(calc_frame, bg=self.colors['surface'])
        btn_frame2.pack(pady=10)
        
        tk.Button(btn_frame2, text="Calculate", command=self.calculate_scenario,
                 bg=self.colors['primary'], fg='white', width=12).pack(pady=2)
        
        tk.Button(btn_frame2, text="Custom Calc", command=self.calculate_custom,
                 bg=self.colors['secondary'], fg='white', width=12).pack(pady=2)
        
        # Status
        self.status_label = tk.Label(calc_frame, text="Ready",
                                   bg=self.colors['surface'], fg=self.colors['neutral'])
        self.status_label.pack(pady=5)
        
        # Custom parameters
        custom_frame = tk.LabelFrame(control_frame, text="Custom Parameters",
                                    bg=self.colors['surface'], font=('Arial', 10, 'bold'))
        custom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Parameter inputs
        params = [
            ("Ambient Temp (K):", 'ambient_temp', 200, 400),
            ("Pressure Ratio:", 'pressure_ratio', 5, 20),
            ("Max Turbine Temp (K):", 'max_turbine_temp', 800, 1600),
            ("Biomass Rate (kg/day):", 'biomass_rate', 1000, 10000),
            ("AD Retention (days):", 'ad_retention_time', 10, 40),
            ("HTC Temperature (K):", 'htc_temperature', 400, 600)
        ]
        
        self.param_entries = {}
        for label, key, min_val, max_val in params:
            frame = tk.Frame(custom_frame, bg=self.colors['surface'])
            frame.pack(fill=tk.X, pady=1)
            
            tk.Label(frame, text=label, bg=self.colors['surface'], width=16).pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=8)
            entry.pack(side=tk.LEFT)
            entry.insert(0, str(self.custom_params[key]))
            self.param_entries[key] = entry
        
        # Results panel
        results_frame = tk.LabelFrame(control_frame, text="Results",
                                   bg=self.colors['surface'], font=('Arial', 10, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results text area
        self.results_text = tk.Text(results_frame, height=12, width=30,
                                   bg=self.colors['surface'], font=('Courier', 7))
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for results
        scrollbar = tk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
        # Right panel - Process Flow Diagram
        diagram_frame = tk.Frame(main_frame, bg=self.colors['surface'],
                              relief=tk.RAISED, bd=2)
        diagram_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas for process flow diagram
        self.canvas = tk.Canvas(diagram_frame, bg=self.colors['background'],
                               scrollregion=(0, 0, 800, 600))
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars for canvas
        h_scrollbar = tk.Scrollbar(diagram_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(fill=tk.X)
        v_scrollbar = tk.Scrollbar(diagram_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        self.draw_process_flow()
    
    def draw_process_flow(self):
        """Draw the process flow diagram"""
        self.canvas.delete("all")
        
        # Draw components
        for comp_id, comp in self.components.items():
            x, y = comp['x'], comp['y']
            
            # Component color based on type
            colors = {
                'ad': '#90EE90',      # Light green
                'manifold': '#FFD700', # Gold
                'combustor': '#FF6B35', # Orange
                'turbine': '#4682B4',  # Steel blue
                'generator': '#32CD32', # Lime green
                'hx': '#FF4500',       # Orange red
                'htc': '#8B4513',      # Saddle brown
                'hrsg': '#708090'       # Slate gray
            }
            
            color = colors.get(comp['type'], '#FFFFFF')
            
            # Draw component box
            self.canvas.create_rectangle(x, y, x+120, y+60, fill=color,
                                        outline='black', width=2)
            
            # Add component name
            self.canvas.create_text(x+60, y+20, text=comp['name'],
                                   font=('Arial', 9, 'bold'), fill='black')
            
            # Add component type icon (simplified)
            icons = {
                'ad': 'AD', 'manifold': 'M', 'combustor': 'C',
                'turbine': 'T', 'generator': 'G', 'hx': 'HX',
                'htc': 'HTC', 'hrsg': 'HRSG'
            }
            
            self.canvas.create_text(x+60, y+45, text=icons.get(comp['type'], '?'),
                                   font=('Arial', 7), fill='black')
        
        # Draw flow lines
        flow_colors = {
            'biogas': '#228B22',     # Forest green
            'combustion': '#FF4500', # Orange red
            'shaft': '#2F4F4F',     # Dark slate gray
            'exhaust': '#FF6347',    # Tomato
            'heat': '#FF8C00',       # Dark orange
            'steam': '#4169E1'       # Royal blue
        }
        
        for flow in self.flows:
            from_comp = self.components[flow['from']]
            to_comp = self.components[flow['to']]
            
            x1, y1 = from_comp['x'] + 120, from_comp['y'] + 30
            x2, y2 = to_comp['x'], to_comp['y'] + 30
            
            color = flow_colors.get(flow['type'], '#000000')
            
            # Draw flow line
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3, arrow=tk.LAST)
            
            # Add flow label
            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2 - 10
            self.canvas.create_text(mid_x, mid_y, text=flow['label'],
                                   font=('Arial', 7), fill=color)
        
        # Draw animated particles
        self.update_particles()
    
    def update_particles(self):
        """Update particle positions for animation"""
        if not self.is_animating:
            return
        
        # Remove old particles
        self.canvas.delete("particle")
        
        # Update and draw particles
        for particle in self.particle_positions:
            flow_idx = particle['flow_idx']
            progress = particle['progress']
            
            if flow_idx < len(self.flows):
                flow = self.flows[flow_idx]
                from_comp = self.components[flow['from']]
                to_comp = self.components[flow['to']]
                
                x1, y1 = from_comp['x'] + 120, from_comp['y'] + 30
                x2, y2 = to_comp['x'], to_comp['y'] + 30
                
                # Calculate current position
                x = x1 + (x2 - x1) * progress
                y = y1 + (y2 - y1) * progress
                
                # Draw particle
                self.canvas.create_oval(x-3, y-3, x+3, y+3,
                                       fill='#FF6B35', tags="particle")
                
                # Update progress
                particle['progress'] += particle['speed'] * self.simulation_speed
                if particle['progress'] > 1.0:
                    particle['progress'] = 0.0
        
        # Schedule next update
        if self.is_animating:
            self.root.after(50, self.update_particles)
    
    def start_simulation_timer(self):
        """Start simulation timer"""
        def update_time():
            if self.is_animating:
                self.simulation_time += self.simulation_speed
                if self.simulation_time >= self.max_simulation_time:
                    self.simulation_time = 0
                
                # Update time display
                hours = int(self.simulation_time // 3600)
                minutes = int((self.simulation_time % 3600) // 60)
                seconds = int(self.simulation_time % 60)
                
                self.time_label.config(text=f"Time: {hours}h {minutes}m {seconds}s")
            
            self.root.after(1000, update_time)
        
        update_time()
    
    def toggle_animation(self):
        """Toggle animation state"""
        self.is_animating = not self.is_animating
        self.play_btn.config(text="Pause" if self.is_animating else "Play")
        
        if self.is_animating:
            self.update_particles()
    
    def reset_simulation(self):
        """Reset simulation"""
        self.simulation_time = 0
        self.time_label.config(text="Time: 0h 0m 0s")
        self.initialize_particles()
    
    def calculate_scenario(self):
        """Calculate using preset scenario"""
        scenario = self.scenario_var.get()
        
        # Scenario parameters
        scenarios = {
            'standard': {
                'ambient_temp': 298.15,
                'pressure_ratio': 12.0,
                'max_turbine_temp': 1400,
                'compressor_efficiency': 0.85,
                'turbine_efficiency': 0.88,
                'biomass_rate': 3000,
                'ad_retention_time': 20,
                'htc_temperature': 473
            },
            'high_efficiency': {
                'ambient_temp': 298.15,
                'pressure_ratio': 15.0,
                'max_turbine_temp': 1500,
                'compressor_efficiency': 0.90,
                'turbine_efficiency': 0.92,
                'biomass_rate': 3000,
                'ad_retention_time': 25,
                'htc_temperature': 500
            },
            'max_power': {
                'ambient_temp': 298.15,
                'pressure_ratio': 18.0,
                'max_turbine_temp': 1600,
                'compressor_efficiency': 0.85,
                'turbine_efficiency': 0.88,
                'biomass_rate': 5000,
                'ad_retention_time': 15,
                'htc_temperature': 550
            },
            'economic_optimal': {
                'ambient_temp': 298.15,
                'pressure_ratio': 10.0,
                'max_turbine_temp': 1300,
                'compressor_efficiency': 0.85,
                'turbine_efficiency': 0.88,
                'biomass_rate': 2500,
                'ad_retention_time': 22,
                'htc_temperature': 480
            },
            'environmental': {
                'ambient_temp': 298.15,
                'pressure_ratio': 8.0,
                'max_turbine_temp': 1200,
                'compressor_efficiency': 0.88,
                'turbine_efficiency': 0.90,
                'biomass_rate': 2000,
                'ad_retention_time': 30,
                'htc_temperature': 450
            }
        }
        
        params = scenarios.get(scenario, scenarios['standard'])
        self.perform_calculation(params)
    
    def calculate_custom(self):
        """Calculate using custom parameters"""
        try:
            # Get parameters from entries
            params = {}
            for key, entry in self.param_entries.items():
                params[key] = float(entry.get())
            
            self.perform_calculation(params)
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
    
    def perform_calculation(self, params):
        """Perform calculation with backend modules"""
        if self.loading:
            return
        
        def calculate():
            self.loading = True
            self.status_label.config(text="Calculating...")
            
            try:
                # Create system components
                brayton = BraytonCycle(
                    ambient_temp=params.get('ambient_temp', 298.15),
                    pressure_ratio=params.get('pressure_ratio', 12.0),
                    max_turbine_temp=params.get('max_turbine_temp', 1400),
                    compressor_efficiency=params.get('compressor_efficiency', 0.85),
                    turbine_efficiency=params.get('turbine_efficiency', 0.88)
                )
                
                ad_system = ADSystem(
                    feedstock_rate=params.get('biomass_rate', 3000),
                    retention_time=params.get('ad_retention_time', 20),
                    temperature=310  # Default temperature
                )
                
                htc_system = HTCSystem(
                    feedstock_rate=params.get('biomass_rate', 3000),
                    temperature=params.get('htc_temperature', 473),
                    residence_time=1.0
                )
                
                # Perform calculations
                brayton_results = brayton.calculate()
                ad_results = ad_system.calculate()
                htc_results = htc_system.calculate()
                
                # Combine results
                self.calculation_results = {
                    'brayton_cycle': brayton_results,
                    'ad_system': ad_results,
                    'htc_system': htc_results,
                    'overall_efficiency': 65.0,  # Placeholder
                    'total_power_output': brayton_results['net_work'] * 1000,  # Convert to kW
                    'biogas_production': ad_results['total_biogas_production'],
                    'hydrochar_production': htc_results['hydrochar_production'],
                    'methane_production': ad_results['methane_production'],
                    'scenario': 'custom'
                }
                
                self.root.after(0, self.on_calculation_success)
                
            except Exception as e:
                error_msg = f"Calculation error: {str(e)}"
                self.root.after(0, lambda: self.on_calculation_error(error_msg))
            finally:
                self.loading = False
        
        thread = threading.Thread(target=calculate, daemon=True)
        thread.start()
    
    def on_calculation_success(self):
        """Handle successful calculation"""
        self.status_label.config(text="Calculation completed successfully", 
                               fg=self.colors['success'])
        self.display_results()
        messagebox.showinfo("Success", "Calculation completed successfully!")
    
    def on_calculation_error(self, error_msg):
        """Handle calculation error"""
        self.status_label.config(text=f"Error: {error_msg}", fg=self.colors['danger'])
        messagebox.showerror("Calculation Error", error_msg)
    
    def display_results(self):
        """Display calculation results"""
        if not self.calculation_results:
            return
        
        self.results_text.delete(1.0, tk.END)
        
        results = self.calculation_results
        
        # Display results in formatted text
        self.results_text.insert(tk.END, "=== AD-HTC SYSTEM RESULTS ===\n\n")
        
        self.results_text.insert(tk.END, "BIOGAS SYSTEM:\n")
        self.results_text.insert(tk.END, f"  Total Biogas: {results['biogas_production']:.1f} m³/day\n")
        self.results_text.insert(tk.END, f"  Methane Production: {results['methane_production']:.1f} m³/day\n")
        self.results_text.insert(tk.END, f"  Biogas Energy: {results['biogas_production'] * 6:.1f} kWh/day\n\n")
        
        self.results_text.insert(tk.END, "Hydrochar System:\n")
        self.results_text.insert(tk.END, f"  Hydrochar Production: {results['hydrochar_production']:.1f} kg/day\n")
        self.results_text.insert(tk.END, f"  Hydrochar Energy: {results['hydrochar_production'] * 25:.1f} MJ/day\n\n")
        
        self.results_text.insert(tk.END, "Power Generation:\n")
        self.results_text.insert(tk.END, f"  Total Power Output: {results['total_power_output']:.1f} kW\n")
        self.results_text.insert(tk.END, f"  Overall Efficiency: {results['overall_efficiency']:.1f}%\n\n")
        
        # Add brayton cycle details
        if 'brayton_cycle' in results:
            brayton = results['brayton_cycle']
            self.results_text.insert(tk.END, "Brayton Cycle:\n")
            self.results_text.insert(tk.END, f"  Net Work: {brayton['net_work']:.1f} kJ/kg\n")
            self.results_text.insert(tk.END, f"  Thermal Efficiency: {brayton['thermal_efficiency']:.1f}%\n")
            self.results_text.insert(tk.END, f"  Turbine Exit Temp: {brayton['turbine_exit_temp']:.1f} K\n")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ADHTCSimpleFrontend()
    app.run()