import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
from typing import Dict, Any, Optional
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="AD-HTC Power Cycle Analysis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid #2E8B57;
    }
    .stButton>button {
        background: linear-gradient(135deg, #2E8B57 0%, #1a5c3a 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1a5c3a 0%, #2E8B57 100%);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def calculate_performance(params: Dict[str, Any]) -> Optional[Dict]:
    """Call backend calculation API"""
    try:
        response = requests.post(f"{API_URL}/calculate", json=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def optimize_system(objectives, constraints, method, pop_size, generations):
    """Call backend optimization API"""
    try:
        payload = {
            "objectives": objectives,
            "constraints": constraints,
            "method": method,
            "population_size": pop_size,
            "generations": generations
        }
        response = requests.post(f"{API_URL}/optimize", json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Optimization Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Optimization Connection Error: {str(e)}")
        return None

def get_scenarios():
    """Fetch available scenarios"""
    try:
        response = requests.get(f"{API_URL}/scenarios", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def plot_brayton_cycle(results):
    """Plot Brayton cycle T-s diagram"""
    if not results or 'gas_turbine' not in results:
        return None
    
    gt = results['gas_turbine']
    states = gt.get('states', [])
    
    if not states:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract state data
    T_vals = [s['T'] for s in states]
    s_vals = [s['s'] for s in states]
    
    # Plot cycle
    ax.plot(s_vals + [s_vals[0]], T_vals + [T_vals[0]], 'bo-', linewidth=2, markersize=8, label='Brayton Cycle')
    
    # Add state labels
    labels = ['1: Compressor Inlet', '2: Compressor Exit', '3: Turbine Inlet', '4: Turbine Exit']
    for i, (s, T, label) in enumerate(zip(s_vals, T_vals, labels)):
        ax.annotate(label.split(':')[0], (s, T), textcoords="offset points", 
                   xytext=(0,10), ha='center', fontweight='bold')
    
    ax.set_xlabel("Specific Entropy (s) [kJ/kg·K]", fontsize=12)
    ax.set_ylabel("Temperature (T) [K]", fontsize=12)
    ax.set_title(f"Brayton Cycle T-s Diagram\nEfficiency: {gt.get('thermal_efficiency', 0)*100:.1f}%", fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    return fig

def plot_energy_flows(results):
    """Plot energy flow diagram"""
    if not results or 'energy_flows' not in results:
        return None
    
    flows = results['energy_flows']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    categories = ['Biogas Input', 'GT Exhaust', 'AD Waste Heat', 'HTC Heat Demand', 'Net Power']
    values = [
        flows.get('biogas_to_combustor_kw', 0),
        flows.get('gt_exhaust_heat_kw', 0),
        flows.get('ad_waste_heat_kw', 0),
        flows.get('htc_heat_supply_kw', 0),
        flows.get('net_electrical_output_kw', 0)
    ]
    
    colors = ['#228B22', '#FF6347', '#FFD700', '#FF8C00', '#4682B4']
    bars = ax.bar(categories, values, color=colors, alpha=0.8)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
               f'{value:.0f} kW', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel("Power/Heat Rate (kW)", fontsize=12)
    ax.set_title("System Energy Flows", fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=15, ha='right')
    
    plt.tight_layout()
    return fig

# ==================== SIDEBAR ====================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/gas.png", width=80)
    st.title("AD-HTC System")
    st.markdown("---")
    
    # Backend status
    backend_online = check_backend_status()
    if backend_online:
        st.success("🟢 Backend Online")
    else:
        st.error("🔴 Backend Offline")
        st.info("Start backend: `uvicorn main:app --reload`")
    
    st.markdown("---")
    
    # Navigation
    page = st.radio("Navigation", [
        "🏠 Dashboard",
        "🧮 Calculator", 
        "📈 Optimizer",
        "📋 Scenarios",
        "📊 Results"
    ])
    
    st.markdown("---")
    st.markdown("**Group 7** - Process Integration")
    st.markdown("*AD-HTC Power Cycle Analysis*")

# ==================== MAIN CONTENT ====================

if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">AD-HTC Power Cycle Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Integrated Anaerobic Digestion & Hydrothermal Carbonization System</div>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("System Efficiency", "42.5%", "+2.3%")
    with col2:
        st.metric("Power Output", "85.2 MW", "+5.1%")
    with col3:
        st.metric("Carbon Reduction", "12.5 kt", "+8.2%")
    with col4:
        st.metric("Revenue", "$2.4M", "+12.5%")
    
    st.markdown("---")
    
    # System overview
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🔧 Quick Actions")
        
        action_cols = st.columns(2)
        with action_cols[0]:
            if st.button("🧮 Run Calculation", use_container_width=True):
                st.session_state.page = "🧮 Calculator"
                st.rerun()
        with action_cols[1]:
            if st.button("📈 Optimize System", use_container_width=True):
                st.session_state.page = "📈 Optimizer"
                st.rerun()
        
        action_cols2 = st.columns(2)
        with action_cols2[0]:
            if st.button("📋 View Scenarios", use_container_width=True):
                st.session_state.page = "📋 Scenarios"
                st.rerun()
        with action_cols2[1]:
            if st.button("📊 See Results", use_container_width=True):
                st.session_state.page = "📊 Results"
                st.rerun()
    
    with col_right:
        st.subheader("📈 System Status")
        
        # Mock status indicators
        status_data = {
            "Brayton Cycle": "✅ Operational",
            "AD System": "✅ Operational", 
            "HTC System": "✅ Operational",
            "Heat Recovery": "✅ Operational",
            "Optimizer": "✅ Ready"
        }
        
        for system, status in status_data.items():
            st.write(f"**{system}:** {status}")
    
    st.markdown("---")
    
    # Process description
    st.subheader("🔄 Process Overview")
    
    process_html = """
    <div style="background: #f8fafc; padding: 20px; border-radius: 12px; border-left: 4px solid #2E8B57;">
        <h4>Anaerobic Digestion (AD)</h4>
        <p>Organic waste is processed in anaerobic digesters to produce biogas (60-65% methane). 
        Three parallel digesters operate with 20-day retention time at 35°C.</p>
        
        <h4>Gas Turbine (Brayton Cycle)</h4>
        <p>Biogas fuels a gas turbine with 12:1 pressure ratio and 1400K turbine inlet temperature. 
        Compressor and turbine efficiencies at 85% and 88% respectively.</p>
        
        <h4>Hydrothermal Carbonization (HTC)</h4>
        <p>Waste heat from turbine exhaust (639K) drives HTC reactors at 200°C, converting 
        biomass to hydrochar with 45% yield and 28 MJ/kg energy density.</p>
        
        <h4>Heat Integration</h4>
        <p>Self-sufficient heat recovery system achieves 75-85% heat integration efficiency, 
        minimizing external energy input.</p>
    </div>
    """
    st.markdown(process_html, unsafe_allow_html=True)

elif page == "🧮 Calculator":
    st.markdown('<div class="main-header">Thermodynamic Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Calculate system performance with custom parameters</div>', unsafe_allow_html=True)
    
    # Input parameters
    col_inputs, col_results = st.columns([1, 1])
    
    with col_inputs:
        st.subheader("⚙️ Input Parameters")
        
        # Brayton Cycle
        with st.expander("🌀 Brayton Cycle (Gas Turbine)", expanded=True):
            ambient_temp = st.number_input("Ambient Temperature (K)", 273.0, 323.0, 298.15, 0.1)
            pressure_ratio = st.slider("Pressure Ratio", 3.0, 25.0, 12.0, 0.1)
            max_turbine_temp = st.number_input("Max Turbine Temperature (K)", 800.0, 1600.0, 1400.0, 10.0)
            compressor_efficiency = st.slider("Compressor Efficiency", 0.75, 0.95, 0.85, 0.01)
            turbine_efficiency = st.slider("Turbine Efficiency", 0.80, 0.95, 0.88, 0.01)
        
        # AD System
        with st.expander("🌱 Anaerobic Digestion (AD)", expanded=True):
            ad_feedstock_rate = st.number_input("Feedstock Rate (kg/day)", 1000.0, 10000.0, 3000.0, 100.0)
            ad_retention_time = st.slider("Retention Time (days)", 10.0, 40.0, 20.0, 1.0)
        
        # HTC System
        with st.expander("⚡ Hydrothermal Carbonization (HTC)", expanded=True):
            htc_biomass_rate = st.number_input("Biomass Rate (kg/day)", 100.0, 2000.0, 500.0, 50.0)
            htc_temperature = st.slider("Reactor Temperature (K)", 423.0, 573.0, 473.0, 5.0)
        
        # Calculate button
        if st.button("🚀 Calculate Performance", use_container_width=True):
            params = {
                "ambient_temp": ambient_temp,
                "pressure_ratio": pressure_ratio,
                "max_turbine_temp": max_turbine_temp,
                "compressor_efficiency": compressor_efficiency,
                "turbine_efficiency": turbine_efficiency,
                "ad_feedstock_rate": ad_feedstock_rate,
                "ad_retention_time": ad_retention_time,
                "htc_biomass_rate": htc_biomass_rate,
                "htc_temperature": htc_temperature,
                "scenario": "custom"
            }
            
            with st.spinner("Calculating thermodynamic performance..."):
                results = calculate_performance(params)
                if results:
                    st.session_state.calculation_results = results
                    st.success("✅ Calculation completed successfully!")
    
    with col_results:
        st.subheader("📊 Results")
        
        if 'calculation_results' in st.session_state:
            results = st.session_state.calculation_results
            
            # Overall performance
            overall = results.get('overall_performance', {})
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Net Power Output", f"{overall.get('net_power_output_kw', 0):.1f} kW")
            st.metric("Overall Efficiency", f"{overall.get('overall_efficiency', 0)*100:.1f}%")
            st.metric("Self-Sufficiency", f"{overall.get('self_sufficiency_ratio', 0)*100:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed results
            with st.expander("🔍 Detailed Results"):
                st.json(results)
            
            # Visualizations
            st.subheader("📈 Visualizations")
            
            tab1, tab2 = st.tabs(["Brayton Cycle", "Energy Flows"])
            
            with tab1:
                fig = plot_brayton_cycle(results)
                if fig:
                    st.pyplot(fig)
                else:
                    st.info("Brayton cycle plot not available")
            
            with tab2:
                fig2 = plot_energy_flows(results)
                if fig2:
                    st.pyplot(fig2)
                else:
                    st.info("Energy flow plot not available")
        else:
            st.info("👈 Enter parameters and click 'Calculate Performance' to see results")

elif page == "📈 Optimizer":
    st.markdown('<div class="main-header">System Optimizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Find optimal operating parameters using advanced algorithms</div>', unsafe_allow_html=True)
    
    col_opt_inputs, col_opt_results = st.columns([1, 1])
    
    with col_opt_inputs:
        st.subheader("⚙️ Optimization Settings")
        
        # Method selection
        method = st.selectbox("Optimization Method", [
            "genetic",
            "gradient", 
            "pareto"
        ], format_func=lambda x: {
            "genetic": "Genetic Algorithm (Recommended)",
            "gradient": "Gradient Descent (Fast)",
            "pareto": "Pareto Frontier (Multi-objective)"
        }[x])
        
        # Objectives
        st.subheader("🎯 Objectives")
        maximize_efficiency = st.checkbox("Maximize System Efficiency", True)
        maximize_power = st.checkbox("Maximize Power Output", False)
        minimize_cost = st.checkbox("Minimize Specific Cost", False)
        maximize_self_sufficiency = st.checkbox("Maximize Self-Sufficiency", True)
        
        # Constraints
        with st.expander("🔒 Constraints"):
            min_efficiency = st.slider("Min Efficiency", 0.2, 0.6, 0.35, 0.01)
            max_cost = st.number_input("Max Cost ($/kW)", 500, 3000, 1500, 100)
            min_self_sufficiency = st.slider("Min Self-Sufficiency", 0.5, 1.0, 0.70, 0.05)
        
        # Algorithm parameters
        if method == "genetic":
            with st.expander("🔧 Genetic Algorithm Parameters"):
                pop_size = st.slider("Population Size", 10, 200, 50, 10)
                generations = st.slider("Generations", 20, 500, 100, 20)
        else:
            pop_size = 50
            generations = 100
        
        # Optimize button
        if st.button("🚀 Start Optimization", use_container_width=True):
            objectives = {
                "maximize": [],
                "minimize": [],
                "weights": {}
            }
            
            if maximize_efficiency:
                objectives["maximize"].append("efficiency")
                objectives["weights"]["efficiency"] = 1.0
            if maximize_power:
                objectives["maximize"].append("power_output")
                objectives["weights"]["power_output"] = 1.0
            if minimize_cost:
                objectives["minimize"].append("specific_cost")
                objectives["weights"]["specific_cost"] = 1.0
            if maximize_self_sufficiency:
                objectives["maximize"].append("self_sufficiency")
                objectives["weights"]["self_sufficiency"] = 1.0
            
            constraints = {
                "min_efficiency": min_efficiency,
                "max_cost": max_cost,
                "min_self_sufficiency": min_self_sufficiency
            }
            
            with st.spinner(f"Running {method} optimization... This may take a minute."):
                opt_results = optimize_system(objectives, constraints, method, pop_size, generations)
                if opt_results:
                    st.session_state.optimization_results = opt_results
                    st.success("✅ Optimization completed!")
    
    with col_opt_results:
        st.subheader("📊 Optimization Results")
        
        if 'optimization_results' in st.session_state:
            opt = st.session_state.optimization_results
            
            # Fitness and performance
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Fitness Score", f"{opt.get('fitness_score', 0):.3f}")
            
            perf = opt.get('performance_metrics', {})
            st.metric("Optimized Efficiency", f"{perf.get('overall_efficiency', 0)*100:.1f}%")
            st.metric("Optimized Power", f"{perf.get('net_power_kw', 0):.0f} kW")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Optimized parameters
            with st.expander("🔧 Optimized Parameters"):
                params = opt.get('optimized_parameters', {})
                df = pd.DataFrame([
                    {"Parameter": k.replace('_', ' ').title(), "Value": f"{v:.3f}" if isinstance(v, float) else str(v)}
                    for k, v in params.items()
                ])
                st.dataframe(df, use_container_width=True)
            
            # Convergence info
            if 'convergence' in opt:
                with st.expander("📈 Convergence Info"):
                    st.json(opt['convergence'])
        else:
            st.info("👈 Configure objectives and click 'Start Optimization' to see results")

elif page == "📋 Scenarios":
    st.markdown('<div class="main-header">Scenario Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pre-configured system configurations for different optimization goals</div>', unsafe_allow_html=True)
    
    # Fetch scenarios
    scenarios_data = get_scenarios()
    
    if scenarios_data and 'scenarios' in scenarios_data:
        scenarios = scenarios_data['scenarios']
        
        # Display scenarios in grid
        cols = st.columns(2)
        
        for i, (scenario_id, scenario) in enumerate(scenarios.items()):
            with cols[i % 2]:
                with st.expander(f"**{scenario['name']}** ({scenario['category']})", expanded=False):
                    st.write(f"**Description:** {scenario['description']}")
                    
                    # Expected performance
                    perf = scenario.get('expected_performance', {})
                    
                    st.markdown("**Expected Performance:**")
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.metric("Efficiency", f"{perf.get('system_efficiency', 0)*100:.1f}%")
                        st.metric("Power", f"{perf.get('net_power', 0)/1000:.1f} MW")
                    with col_p2:
                        st.metric("LCOE", f"${perf.get('lcoe_usd_kwh', 0):.3f}/kWh")
                        st.metric("Carbon", f"{perf.get('carbon_intensity_g_kwh', 0):.0f} g/kWh")
                    
                    