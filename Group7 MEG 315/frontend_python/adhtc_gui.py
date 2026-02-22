#!/usr/bin/env python3
"""
Python-based Frontend for  Group 7 AD-HTC System
Alternative to React frontend for systems without Node.js/React capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import requests
import json
import threading
import time
from datetime import datetime
import math

class ADHTCPythonFrontend:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Group 7 - AD-HTC Fuel-Enhanced Gas Power Cycle")
        self.root.geometry("1400x900")
        self.root.configure(bg='#F0F8FF')
        
        # Color scheme matching React frontend
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
        
        # Component data matching React frontend
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
                    'flow_index': flow_idx,
                    'progress': np.random.random(),
                    'id': f"{flow_idx}-{i}"
                })
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Group 7 - AD-HTC Fuel-Enhanced Gas Power Cycle",
                              fg='white', bg=self.colors['primary'], font=('Arial', 16, 'bold'))
        title_label.pack(pady=5)
        
        subtitle_label = tk.Label(header_frame, text="Professional-grade Process Flow Analysis System",
                                 fg='white', bg=self.colors['primary'], font=('Arial', 10))
        subtitle_label.pack()
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg=self.colors['secondary'], height=30)
        self.status_frame.pack(fill=tk.X, padx=5, pady=2)
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", fg='white', bg=self.colors['secondary'])
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(self.status_frame, text="Time: 0s", fg='white', bg=self.colors['secondary'])
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        control_frame = tk.Frame(main_frame, bg=self.colors['surface'], width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        control_frame.pack_propagate(False)
        
        self.setup_control_panel(control_frame)
        
        # Right panel - Visualization
        viz_frame = tk.Frame(main_frame, bg=self.colors['surface'])
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.setup_visualization_panel(viz_frame)
    
    def setup_control_panel(self, parent):
        """Setup the control panel"""
        # Title
        title_label = tk.Label(parent, text="Controls & Parameters", 
                              font=('Arial', 12, 'bold'), bg=self.colors['surface'])
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scenario tab
        scenario_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(scenario_frame, text="Scenarios")
        self.setup_scenario_tab(scenario_frame)
        
        # Animation tab
        animation_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(animation_frame, text="Animation")
        self.setup_animation_tab(animation_frame)
        
        # Parameters tab
        params_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(params_frame, text="Parameters")
        self.setup_parameters_tab(params_frame)
    
    def setup_scenario_tab(self, parent):
        """Setup scenario selection tab"""
        tk.Label(parent, text="Preset Scenarios:", bg=self.colors['surface']).pack(pady=5)
        
        self.scenario_var = tk.StringVar(value="base_case")
        scenarios = [
            ("Base Case", "base_case"),
            ("Optimized", "optimized"),
            ("Full COGAS", "full_cogas")
        ]
        
        for text, value in scenarios:
            tk.Radiobutton(parent, text=text, variable=self.scenario_var, 
                          value=value, bg=self.colors['surface']).pack(anchor=tk.W, padx=20)
        
        tk.Button(parent, text="Calculate Scenario", command=self.calculate_scenario,
                 bg=self.colors['primary'], fg='white').pack(pady=10)
        
        # Results display
        self.results_text = tk.Text(parent, height=10, width=35, wrap=tk.WORD)
        self.results_text.pack(pady=10, padx=10)
    
    def setup_animation_tab(self, parent):
        """Setup animation controls tab"""
        # Animation controls
        control_frame = tk.Frame(parent, bg=self.colors['surface'])
        control_frame.pack(pady=10)
        
        self.play_pause_btn = tk.Button(control_frame, text="Pause", 
                                       command=self.toggle_animation,
                                       bg=self.colors['danger'], fg='white')
        self.play_pause_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Reset", command=self.reset_simulation,
                 bg=self.colors['warning']).pack(side=tk.LEFT, padx=5)
        
        # Time slider
        tk.Label(parent, text="Simulation Time:", bg=self.colors['surface']).pack(pady=5)
        self.time_slider = tk.Scale(parent, from_=0, to=self.max_simulation_time,
                                   orient=tk.HORIZONTAL, length=250,
                                   command=self.on_time_slider_change)
        self.time_slider.pack(pady=5)
        
        # Speed control
        tk.Label(parent, text="Simulation Speed:", bg=self.colors['surface']).pack(pady=5)
        self.speed_slider = tk.Scale(parent, from_=0.1, to=10.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, length=250,
                                    command=self.on_speed_slider_change)
        self.speed_slider.set(1.0)
        self.speed_slider.pack(pady=5)
        
        self.speed_label = tk.Label(parent, text="1.0x Speed", bg=self.colors['surface'])
        self.speed_label.pack()
    
    def setup_parameters_tab(self, parent):
        """Setup parameters tab"""
        params = [
            ("Ambient Temp (K):", 'ambient_temp', 250, 350),
            ("Pressure Ratio:", 'pressure_ratio', 5, 20),
            ("Max Turbine Temp (K):", 'max_turbine_temp', 1000, 1600),
            ("Compressor Efficiency:", 'compressor_efficiency', 0.7, 0.95),
            ("Turbine Efficiency:", 'turbine_efficiency', 0.7, 0.95),
            ("Biomass Rate (kg/day):", 'biomass_rate', 1000, 5000),
            ("AD Retention Time (days):", 'ad_retention_time', 10, 30),
            ("HTC Temperature (K):", 'htc_temperature', 400, 550)
        ]
        
        self.param_vars = {}
        for label, key, min_val, max_val in params:
            frame = tk.Frame(parent, bg=self.colors['surface'])
            frame.pack(pady=2, padx=10, fill=tk.X)
            
            tk.Label(frame, text=label, bg=self.colors['surface'], width=20).pack(side=tk.LEFT)
            var = tk.DoubleVar(value=self.custom_params[key])
            self.param_vars[key] = var
            
            scale = tk.Scale(frame, from_=min_val, to=max_val, resolution=0.1,
                           orient=tk.HORIZONTAL, length=150, variable=var,
                           command=lambda val, k=key: self.on_param_change(k, float(val)))
            scale.pack(side=tk.RIGHT)
        
        tk.Button(parent, text="Calculate Custom", command=self.calculate_custom,
                 bg=self.colors['secondary'], fg='white').pack(pady=10)
    
    def setup_visualization_panel(self, parent):
        """Setup visualization panel"""
        # Create notebook for different views
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Process Flow Diagram tab
        pfd_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(pfd_frame, text="Process Flow Diagram")
        self.setup_pfd_tab(pfd_frame)
        
        # Performance Charts tab
        charts_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(charts_frame, text="Performance Charts")
        self.setup_charts_tab(charts_frame)
        
        # Analysis tab
        analysis_frame = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(analysis_frame, text="Economic & Environmental")
        self.setup_analysis_tab(analysis_frame)
    
    def setup_pfd_tab(self, parent):
        """Setup Process Flow Diagram tab"""
        # Create canvas for PFD
        self.pfd_canvas = tk.Canvas(parent, width=800, height=500, 
                                   bg='white', scrollregion=(0, 0, 800, 500))
        self.pfd_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        h_scrollbar = tk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.pfd_canvas.xview)
        h_scrollbar.pack(fill=tk.X)
        v_scrollbar = tk.Scrollbar(parent, orient=tk.VERTICAL, command=self.pfd_canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.pfd_canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Bind click events
        self.pfd_canvas.bind("<Button-1>", self.on_pfd_click)
        
        self.draw_pfd()
    
    def setup_charts_tab(self, parent):
        """Setup performance charts tab"""
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_charts()
    
    def setup_analysis_tab(self, parent):
        """Setup economic and environmental analysis tab"""
        # Create text widget for analysis results
        self.analysis_text = tk.Text(parent, wrap=tk.WORD, width=80, height=30)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(parent, command=self.analysis_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.analysis_text.config(yscrollcommand=scrollbar.set)
    
    def draw_pfd(self):
        """Draw the Process Flow Diagram"""
        self.pfd_canvas.delete("all")
        
        # Draw components
        for comp_id, comp in self.components.items():
            x, y = comp['x'], comp['y']
            
            # Different shapes for different component types
            if comp['type'] == 'ad':
                # AD units - rectangles
                self.pfd_canvas.create_rectangle(x, y, x+60, y+60, 
                                                 fill=self.colors['success'], 
                                                 outline='black', width=2,
                                                 tags=f"component_{comp_id}")
                self.pfd_canvas.create_text(x+30, y+30, text="AD", 
                                           font=('Arial', 10, 'bold'))
            elif comp['type'] == 'turbine':
                # Turbine - circle
                self.pfd_canvas.create_oval(x, y, x+60, y+60, 
                                          fill=self.colors['primary'],
                                          outline='black', width=2,
                                          tags=f"component_{comp_id}")
                self.pfd_canvas.create_text(x+30, y+30, text="GT", 
                                           font=('Arial', 10, 'bold'))
            elif comp['type'] == 'generator':
                # Generator - diamond
                points = [x+30, y, x+60, y+30, x+30, y+60, x, y+30]
                self.pfd_canvas.create_polygon(points, 
                                             fill=self.colors['accent'],
                                             outline='black', width=2,
                                             tags=f"component_{comp_id}")
                self.pfd_canvas.create_text(x+30, y+30, text="GEN", 
                                           font=('Arial', 8, 'bold'))
            else:
                # Default - rounded rectangle
                self.pfd_canvas.create_rectangle(x, y, x+60, y+60, 
                                               fill=self.colors['neutral'],
                                               outline='black', width=2,
                                               tags=f"component_{comp_id}")
                self.pfd_canvas.create_text(x+30, y+15, text=comp['name'][:8], 
                                           font=('Arial', 8))
            
            # Component name
            self.pfd_canvas.create_text(x+30, y+75, text=comp['name'], 
                                       font=('Arial', 8))
        
        # Draw flow lines with particles
        self.draw_flow_lines()
    
    def draw_flow_lines(self):
        """Draw flow lines with animated particles"""
        flow_colors = {
            'biogas': self.colors['success'],
            'combustion': self.colors['danger'],
            'shaft': self.colors['neutral'],
            'exhaust': self.colors['warning'],
            'heat': self.colors['accent'],
            'steam': self.colors['secondary']
        }
        
        # Draw flow lines
        for flow_idx, flow in enumerate(self.flows):
            from_comp = self.components[flow['from']]
            to_comp = self.components[flow['to']]
            
            start_x, start_y = from_comp['x'] + 60, from_comp['y'] + 30
            end_x, end_y = to_comp['x'], to_comp['y'] + 30
            
            color = flow_colors.get(flow['type'], self.colors['neutral'])
            
            # Draw line
            self.pfd_canvas.create_line(start_x, start_y, end_x, end_y, 
                                       fill=color, width=3, arrow=tk.LAST)
            
            # Draw label
            mid_x, mid_y = (start_x + end_x) // 2, (start_y + end_y) // 2
            self.pfd_canvas.create_text(mid_x, mid_y - 10, text=flow['label'], 
                                       font=('Arial', 8), fill=color)
            
            # Draw animated particles
            for particle in self.particle_positions:
                if particle['flow_index'] == flow_idx:
                    progress = particle['progress']
                    x = start_x + (end_x - start_x) * progress
                    y = start_y + (end_y - start_y) * progress
                    
                    self.pfd_canvas.create_oval(x-3, y-3, x+3, y+3, 
                                               fill=color, outline=color)
    
    def update_charts(self):
        """Update performance charts"""
        self.fig.clear()
        
        if self.calculation_results:
            # Create subplots
            gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # Power output chart
            ax1 = self.fig.add_subplot(gs[0, 0])
            self.create_power_chart(ax1)
            
            # Efficiency chart
            ax2 = self.fig.add_subplot(gs[0, 1])
            self.create_efficiency_chart(ax2)
            
            # Time series chart
            ax3 = self.fig.add_subplot(gs[1, :])
            self.create_time_series_chart(ax3)
        else:
            # Default empty charts
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available\nCalculate a scenario to see charts', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        self.canvas.draw()
    
    def create_power_chart(self, ax):
        """Create power output chart"""
        if not self.calculation_results:
            return
            
        systems = ['Gas Turbine', 'AD System', 'HTC System']
        power_values = [
            self.calculation_results.get('gas_turbine', {}).get('net_work', 0),
            self.calculation_results.get('ad_system', {}).get('biogas_energy_output', 0),
            self.calculation_results.get('htc_system', {}).get('hydrochar_yield', 0)
        ]
        
        bars = ax.bar(systems, power_values, color=[self.colors['primary'], 
                                                     self.colors['success'], 
                                                     self.colors['accent']])
        ax.set_title('Power Output by System', fontweight='bold')
        ax.set_ylabel('Power (kW)')
        
        # Add value labels on bars
        for bar, value in zip(bars, power_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.0f}', ha='center', va='bottom')
    
    def create_efficiency_chart(self, ax):
        """Create efficiency chart"""
        if not self.calculation_results:
            return
            
        systems = ['Overall', 'Gas Turbine', 'AD System']
        efficiency_values = [
            self.calculation_results.get('overall_performance', {}).get('overall_efficiency', 0) * 100,
            self.calculation_results.get('gas_turbine', {}).get('thermal_efficiency', 0) * 100,
            85.0  # Typical AD efficiency
        ]
        
        bars = ax.bar(systems, efficiency_values, color=[self.colors['secondary'], 
                                                         self.colors['primary'], 
                                                         self.colors['success']])
        ax.set_title('System Efficiency', fontweight='bold')
        ax.set_ylabel('Efficiency (%)')
        
        # Add value labels on bars
        for bar, value in zip(bars, efficiency_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}%', ha='center', va='bottom')
    
    def create_time_series_chart(self, ax):
        """Create time series chart"""
        if not self.calculation_results:
            return
        
        # Generate 24-hour forecast
        hours = np.arange(24)
        current_hour = (self.simulation_time % 86400) // 3600
        
        # Simulate variations based on current time
        base_power = self.calculation_results.get('overall_performance', {}).get('net_power_output_kw', 0)
        base_efficiency = self.calculation_results.get('overall_performance', {}).get('overall_efficiency', 0)
        base_biogas = self.calculation_results.get('ad_system', {}).get('biogas_yield', 0)
        
        power_variation = base_power * (0.85 + 0.3 * np.sin((hours + current_hour/24) * np.pi / 12))
        efficiency_variation = base_efficiency * (0.9 + 0.2 * np.cos((hours + current_hour/24) * np.pi / 8))
        biogas_variation = base_biogas * (0.7 + 0.6 * np.sin((hours + current_hour/24) * np.pi / 6))
        
        # Plot lines
        ax.plot(hours, power_variation, label='Power Output (kW)', 
               color=self.colors['primary'], linewidth=2)
        ax.plot(hours, efficiency_variation * 1000, label='Efficiency (×1000)', 
               color=self.colors['secondary'], linewidth=2)
        ax.plot(hours, biogas_variation, label='Biogas Yield (m³/day)', 
               color=self.colors['success'], linewidth=2)
        
        ax.set_title('24-Hour Performance Forecast', fontweight='bold')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Value')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def update_analysis_tab(self):
        """Update economic and environmental analysis"""
        self.analysis_text.delete(1.0, tk.END)
        
        if not self.calculation_results:
            self.analysis_text.insert(tk.END, "No analysis data available.\nCalculate a scenario to see results.")
            return
        
        # Economic Analysis
        self.analysis_text.insert(tk.END, "ECONOMIC ANALYSIS\n", 'header')
        self.analysis_text.insert(tk.END, "="*50 + "\n\n")
        
        economic = self.calculation_results.get('economic_analysis', {})
        if economic:
            self.analysis_text.insert(tk.END, f"Total CAPEX: ${economic.get('total_capex_usd', 0):,.0f}\n")
            self.analysis_text.insert(tk.END, f"Annual OPEX: ${economic.get('annual_opex_usd', 0):,.0f}\n")
            self.analysis_text.insert(tk.END, f"Annual Revenue: ${economic.get('annual_revenue_usd', 0):,.0f}\n")
            self.analysis_text.insert(tk.END, f"LCOE: ${economic.get('levelized_cost_electricity_usd_kwh', 0):.3f}/kWh\n")
            self.analysis_text.insert(tk.END, f"NPV: ${economic.get('net_present_value_usd', 0):,.0f}\n")
            self.analysis_text.insert(tk.END, f"Payback Period: {economic.get('payback_period_years', 0):.1f} years\n")
        else:
            self.analysis_text.insert(tk.END, "No economic data available.\n")
        
        self.analysis_text.insert(tk.END, "\n")
        
        # Environmental Analysis
        self.analysis_text.insert(tk.END, "ENVIRONMENTAL ANALYSIS\n", 'header')
        self.analysis_text.insert(tk.END, "="*50 + "\n\n")
        
        environmental = self.calculation_results.get('environmental_analysis', {})
        if environmental:
            self.analysis_text.insert(tk.END, f"Net Emissions: {environmental.get('net_emissions_ton_co2_eq_year', 0):,.0f} ton CO2-eq/year\n")
            self.analysis_text.insert(tk.END, f"Carbon Intensity: {environmental.get('carbon_intensity_kg_co2_eq_kwh', 0):.3f} kg CO2-eq/kWh\n")
            self.analysis_text.insert(tk.END, f"Material Recovery: {environmental.get('material_recovery_efficiency', 0):.1%}\n")
            self.analysis_text.insert(tk.END, f"Sustainability Score: {environmental.get('sustainability_score', 0)}/100\n")
        else:
            self.analysis_text.insert(tk.END, "No environmental data available.\n")
        
        # Overall Performance
        self.analysis_text.insert(tk.END, "\n")
        self.analysis_text.insert(tk.END, "OVERALL PERFORMANCE\n", 'header')
        self.analysis_text.insert(tk.END, "="*50 + "\n\n")
        
        overall = self.calculation_results.get('overall_performance', {})
        if overall:
            self.analysis_text.insert(tk.END, f"Net Power Output: {overall.get('net_power_output_kw', 0):,.0f} kW\n")
            self.analysis_text.insert(tk.END, f"Overall Efficiency: {overall.get('overall_efficiency', 0):.1%}\n")
            self.analysis_text.insert(tk.END, f"Self-Sufficiency Ratio: {overall.get('self_sufficiency_ratio', 0):.1%}\n")
        
        # Configure text tags
        self.analysis_text.tag_config('header', font=('Arial', 12, 'bold'), foreground=self.colors['primary'])
    
    def start_simulation_timer(self):
        """Start the simulation timer"""
        def update_timer():
            while True:
                if self.is_animating:
                    self.simulation_time += self.simulation_speed
                    if self.simulation_time >= self.max_simulation_time:
                        self.simulation_time = 0
                    
                    # Update UI
                    self.root.after(0, self.update_simulation_display)
                
                time.sleep(1)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()
    
    def update_simulation_display(self):
        """Update simulation display elements"""
        # Update time label
        hours = int(self.simulation_time // 3600)
        minutes = int((self.simulation_time % 3600) // 60)
        seconds = int(self.simulation_time % 60)
        self.time_label.config(text=f"Time: {hours}h {minutes}m {seconds}s")
        
        # Update time slider
        self.time_slider.set(self.simulation_time)
        
        # Update PFD (redraw particles)
        self.draw_pfd()
        
        # Update charts if we have results
        if self.calculation_results:
            self.update_charts()
    
    def on_time_slider_change(self, value):
        """Handle time slider changes"""
        self.simulation_time = float(value)
        self.update_simulation_display()
    
    def on_speed_slider_change(self, value):
        """Handle speed slider changes"""
        self.simulation_speed = float(value)
        self.speed_label.config(text=f"{value}x Speed")
    
    def on_param_change(self, param_name, value):
        """Handle parameter changes"""
        self.custom_params[param_name] = value
    
    def on_pfd_click(self, event):
        """Handle PFD click events"""
        # Find clicked component
        clicked_items = self.pfd_canvas.find_withtag("current")
        if clicked_items:
            tags = self.pfd_canvas.gettags(clicked_items[0])
            for tag in tags:
                if tag.startswith("component_"):
                    component_id = tag.replace("component_", "")
                    self.show_component_analysis(component_id)
                    break
    
    def show_component_analysis(self, component_id):
        """Show detailed analysis for clicked component"""
        if not self.calculation_results:
            messagebox.showinfo("Component Analysis", "No calculation results available.\nPlease calculate a scenario first.")
            return
        
        comp = self.components[component_id]
        analysis_text = f"Component: {comp['name']}\n\n"
        
        if comp['type'] == 'ad' and self.calculation_results.get('ad_system'):
            ad_data = self.calculation_results['ad_system']
            analysis_text += f"Biogas Yield: {ad_data.get('biogas_yield', 0):,.0f} m³/day\n"
            analysis_text += f"Energy Output: {ad_data.get('biogas_energy_output', 0):,.0f} kW\n"
            analysis_text += f"Methane Content: {ad_data.get('methane_content', 0):.1%}\n"
        elif comp['type'] == 'turbine' and self.calculation_results.get('gas_turbine'):
            gt_data = self.calculation_results['gas_turbine']
            analysis_text += f"Net Work: {gt_data.get('net_work', 0):,.0f} kW\n"
            analysis_text += f"Thermal Efficiency: {gt_data.get('thermal_efficiency', 0):.1%}\n"
            analysis_text += f"Exhaust Temperature: {gt_data.get('exhaust_temp', 0):.0f} K\n"
        elif comp['type'] == 'htc' and self.calculation_results.get('htc_system'):
            htc_data = self.calculation_results['htc_system']
            analysis_text += f"Hydrochar Yield: {htc_data.get('hydrochar_yield', 0):,.0f} kg/day\n"
            analysis_text += f"Heat Demand: {htc_data.get('heat_demand', 0):,.0f} kW\n"
            analysis_text += f"Energy Efficiency: {htc_data.get('energy_efficiency', 0):.1%}\n"
        else:
            analysis_text += "No detailed analysis available for this component."
        
        messagebox.showinfo(f"Component Analysis - {comp['name']}", analysis_text)
    
    def toggle_animation(self):
        """Toggle animation state"""
        self.is_animating = not self.is_animating
        self.play_pause_btn.config(text="Play" if not self.is_animating else "Pause",
                                  bg=self.colors['success'] if not self.is_animating else self.colors['danger'])
    
    def reset_simulation(self):
        """Reset simulation"""
        self.simulation_time = 0
        self.update_simulation_display()
    
    def calculate_scenario(self):
        """Calculate selected scenario"""
        scenario_id = self.scenario_var.get()
        self.perform_calculation(f"http://localhost:8000/scenarios/{scenario_id}/calculate")
    
    def calculate_custom(self):
        """Calculate with custom parameters"""
        payload = {
            'ambient_temp': self.custom_params['ambient_temp'],
            'pressure_ratio': self.custom_params['pressure_ratio'],
            'max_turbine_temp': self.custom_params['max_turbine_temp'],
            'compressor_efficiency': self.custom_params['compressor_efficiency'],
            'turbine_efficiency': self.custom_params['turbine_efficiency'],
            'ad_feedstock_rate': self.custom_params['biomass_rate'],
            'ad_retention_time': self.custom_params['ad_retention_time'],
            'htc_biomass_rate': self.custom_params['biomass_rate'] * 0.3,
            'htc_temperature': self.custom_params['htc_temperature'],
            'scenario': 'custom'
        }
        self.perform_calculation("http://localhost:8000/calculate", payload)
    
    def perform_calculation(self, url, payload=None):
        """Perform calculation with backend"""
        if self.loading:
            return
        
        def calculate():
            self.loading = True
            self.status_label.config(text="Calculating...")
            
            try:
                if payload:
                    response = requests.post(url, json=payload, timeout=30)
                else:
                    response = requests.post(url, timeout=30)
                
                if response.status_code == 200:
                    self.calculation_results = response.json()
                    self.root.after(0, self.on_calculation_success)
                else:
                    error_msg = f"Calculation failed: {response.status_code}"
                    self.root.after(0, lambda: self.on_calculation_error(error_msg))
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Connection error: {str(e)}"
                self.root.after(0, lambda: self.on_calculation_error(error_msg))
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.root.after(0, lambda: self.on_calculation_error(error_msg))
            finally:
                self.loading = False
        
        thread = threading.Thread(target=calculate, daemon=True)
        thread.start()
    
    def on_calculation_success(self):
        """Handle successful calculation"""
        self.status_label.config(text="Calculation completed successfully")
        self.display_results()
        self.update_charts()
        self.update_analysis_tab()
        messagebox.showinfo("Success", "Calculation completed successfully!")
    
    def on_calculation_error(self, error_msg):
        """Handle calculation error"""
        self.status_label.config(text=f"Error: {error_msg}")
        messagebox.showerror("Calculation Error", error_msg)
    
    def display_results(self):
        """Display calculation results"""
        if not self.calculation_results:
            return
        
        self.results_text.delete(1.0, tk.END)
        
        # Overall performance
        overall = self.calculation_results.get('overall_performance', {})
        self.results_text.insert(tk.END, "OVERALL PERFORMANCE\n", 'header')
        self.results_text.insert(tk.END, f"Net Power Output: {overall.get('net_power_output_kw', 0):,.0f} kW\n")
        self.results_text.insert(tk.END, f"Overall Efficiency: {overall.get('overall_efficiency', 0):.1%}\n")
        self.results_text.insert(tk.END, f"Self-Sufficiency: {overall.get('self_sufficiency_ratio', 0):.1%}\n\n")
        
        # Gas turbine
        gt = self.calculation_results.get('gas_turbine', {})
        self.results_text.insert(tk.END, "GAS TURBINE\n", 'header')
        self.results_text.insert(tk.END, f"Net Work: {gt.get('net_work', 0):,.0f} kW\n")
        self.results_text.insert(tk.END, f"Thermal Efficiency: {gt.get('thermal_efficiency', 0):.1%}\n\n")
        
        # AD system
        ad = self.calculation_results.get('ad_system', {})
        self.results_text.insert(tk.END, "AD SYSTEM\n", 'header')
        self.results_text.insert(tk.END, f"Biogas Yield: {ad.get('biogas_yield', 0):,.0f} m³/day\n")
        self.results_text.insert(tk.END, f"Energy Output: {ad.get('biogas_energy_output', 0):,.0f} kW\n\n")
        
        # HTC system
        htc = self.calculation_results.get('htc_system', {})
        self.results_text.insert(tk.END, "HTC SYSTEM\n", 'header')
        self.results_text.insert(tk.END, f"Hydrochar Yield: {htc.get('hydrochar_yield', 0):,.0f} kg/day\n")
        self.results_text.insert(tk.END, f"Heat Demand: {htc.get('heat_demand', 0):,.0f} kW\n")
        
        # Configure text tags
        self.results_text.tag_config('header', font=('Arial', 10, 'bold'), foreground=self.colors['primary'])
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function"""
    # Check requirements first
    try:
        import tkinter
        import matplotlib
        import numpy
        import requests
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages:")
        print("pip install matplotlib numpy requests")
        return
    
    app = ADHTCPythonFrontend()
    app.run()

if __name__ == "__main__":
    main()