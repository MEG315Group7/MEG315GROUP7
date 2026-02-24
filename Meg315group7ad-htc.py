import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pyromat as pm
from dataclasses import dataclass
from typing import Tuple, Optional

# Initialize thermodynamics libraries
pm.config["unit_pressure"] = "bar"
pm.config["unit_temperature"] = "K"
pm.config["unit_energy"] = "kJ"
air = pm.get("ig.air")
steam = pm.get("mp.H2O")

st.set_page_config(page_title="AD-HTC Advanced Simulator", layout="wide")

@dataclass
class BraytonState:
 """Thermodynamic state for Brayton cycle"""
 p: float  # Pressure (bar)
 T: float  # Temperature (K)
 h: float  # Enthalpy (kJ/kg)
 s: float  # Entropy (kJ/kg·K)
 point_name: str

@dataclass
class RankineState:
 """Thermodynamic state for Rankine cycle"""
 p: float  # Pressure (bar)
 T: float  # Temperature (K)
 h: float  # Enthalpy (kJ/kg)
 s: float  # Entropy (kJ/kg·K)
 x: Optional[float]  # Quality (None for superheated)
 point_name: str

class ThermodynamicError(Exception):
 """Custom exception for thermodynamic calculation errors"""
 pass

def calculate_brayton_cycle(
 p1: float, t1: float, rp: float, 
 eta_c: float, eta_t: float,
 m_air: float, m_fuel: float, biogas_lhv: float
) -> Tuple[list, float, float, float]:
 """
 Calculate Brayton cycle states with fuel enhancement from AD biogas.
 
 Returns:
     states: List of BraytonState objects
     w_comp: Specific compressor work (kJ/kg)
     w_turb: Specific turbine work (kJ/kg)  
     q_in: Specific heat input (kJ/kg)
 """
 states = []
 
 # State 1: Inlet
 h1 = air.h(T=t1, p=p1)[0]
 s1 = air.s(T=t1, p=p1)[0]
 states.append(BraytonState(p1, t1, h1, s1, "1: Compressor Inlet"))
 
 # State 2: Compressor Exit (Isentropic efficiency)
 p2 = p1 * rp
 s2s = s1
 t2s = air.T_s(s=s2s, p=p2)[0]
 h2s = air.h(T=t2s, p=p2)[0]
 h2 = h1 + (h2s - h1) / eta_c
 t2 = air.T_h(h=h2, p=p2)[0]
 s2 = air.s(T=t2, p=p2)[0]
 states.append(BraytonState(p2, t2, h2, s2, "2: Compressor Exit"))
 
 # State 3: Combustor Exit (Energy balance with fuel)
 # m_air*h2 + m_fuel*LHV = (m_air + m_fuel)*h3
 m_total = m_air + m_fuel
 h3 = (m_air * h2 + m_fuel * biogas_lhv) / m_total
 p3 = p2  # Negligible pressure drop
 t3 = air.T_h(h=h3, p=p3)[0]
 s3 = air.s(T=t3, p=p3)[0]
 states.append(BraytonState(p3, t3, h3, s3, "3: Combustor Exit"))
 
 # State 4: Turbine Exit
 p4 = p1
 s4s = s3
 t4s = air.T_s(s=s4s, p=p4)[0]
 h4s = air.h(T=t4s, p=p4)[0]
 h4 = h3 - eta_t * (h3 - h4s)
 t4 = air.T_h(h=h4, p=p4)[0]
 s4 = air.s(T=t4, p=p4)[0]
 states.append(BraytonState(p4, t4, h4, s4, "4: Turbine Exit"))
 
 # Calculate works (per kg of total mass flow)
 w_comp = h2 - h1
 w_turb = h3 - h4
 q_in = h3 - h2
 
 return states, w_comp, w_turb, q_in

def calculate_rankine_cycle(
 p_cond: float, p_boiler: float, t_boiler: float,
 eta_t: float, eta_p: float,
 gas_exhaust_T: float, gas_exhaust_h: float, 
 gas_mass_flow: float, pinch_approach: float
) -> Tuple[list, float, float, float, float, float]:
 """
 Calculate Rankine cycle with HRSG heat recovery.
 
 Returns:
     states: List of RankineState objects
     w_pump: Specific pump work (kJ/kg)
     w_turb: Specific turbine work (kJ/kg)
     q_in: Specific heat input (kJ/kg)
     q_available: Available heat from gas (kJ/kg)
     hrsg_effectiveness: HRSG effectiveness
 """
 states = []
 
 # State 1: Condenser Exit (Saturated Liquid)
 h1 = steam.h(p=p_cond, x=0)[0]
 s1 = steam.s(p=p_cond, x=0)[0]
 T1 = steam.T_s(s=s1, p=p_cond)[0] if hasattr(steam, 'T_s') else steam.T(p=p_cond, x=0)[0]
 states.append(RankineState(p_cond, T1, h1, s1, 0.0, "1: Pump Inlet"))
 
 # State 2: Pump Exit (Isentropic compression)
 p2 = p_boiler
 # For liquids: h2 - h1 ≈ v*(p2-p1), using incompressible approximation
 v_f = 1 / steam.d(p=p_cond, x=0)[0]  # Specific volume (m³/kg)
 w_pump_s = v_f * (p2 - p_cond) * 100  # Convert bar to kPa (*100)
 w_pump = w_pump_s / eta_p
 h2 = h1 + w_pump
 # For compressed liquid, approximate T using saturation at p2
 T2 = steam.T(p=p2, x=0)[0] if p2 < steam.critical_pressure() else T1 + 10
 s2 = steam.s(p=p2, T=T2)[0] if T2 > steam.T(p=p2, x=0)[0] else s1
 states.append(RankineState(p2, T2, h2, s2, None, "2: Pump Exit"))
 
 # State 3: Boiler Exit (Superheated)
 h3 = steam.h(p=p_boiler, T=t_boiler)[0]
 s3 = steam.s(p=p_boiler, T=t_boiler)[0]
 states.append(RankineState(p_boiler, t_boiler, h3, s3, None, "3: Boiler Exit"))
 
 # State 4: Turbine Exit
 p4 = p_cond
 s4s = s3
 # Check if expansion enters two-phase region
 T_sat = steam.T(p=p_cond)[0]
 s_g = steam.s(p=p_cond, x=1)[0]
 
 if s4s <= s_g:
     # Wet expansion
     x4s = steam.x(s=s4s, p=p_cond)[0]
     h4s = steam.h(p=p_cond, x=x4s)[0]
 else:
     # Superheated expansion (shouldn't happen with typical Rankine)
     T4s = steam.T_s(s=s4s, p=p_cond)[0]
     h4s = steam.h(p=p_cond, T=T4s)[0]
     x4s = None
 
 h4 = h3 - eta_t * (h3 - h4s)
 
 # Determine actual state 4
 if x4s is not None:
     # In two-phase region, find actual quality
     try:
         x4 = steam.x(h=h4, p=p_cond)[0]
         T4 = T_sat
         s4 = steam.s(p=p_cond, x=x4)[0]
     except:
         # If x calculation fails, approximate
         x4 = x4s + (1-eta_t)*(1-x4s) if x4s < 1 else 1
         T4 = T_sat
         s4 = steam.s(p=p_cond, x=min(x4, 1))[0]
 else:
     T4 = steam.T_s(s=s4, p=p_cond)[0] if hasattr(steam, 'T_s') else T_sat
     s4 = steam.s(p=p_cond, T=T4)[0]
     x4 = None
 
 states.append(RankineState(p_cond, T4, h4, s4, x4 if x4 is not None else 0, "4: Turbine Exit"))
 
 # HRSG Analysis
 # Available heat from gas exhaust (cooling to stack temp)
 t_stack_min = max(T2 + pinch_approach, 350)  # Minimum stack temp
 h_stack = air.h(T=t_stack_min, p=1.01)[0]
 q_available = gas_exhaust_h - h_stack  # per kg of gas
 
 # Required heat for steam cycle
 q_in_steam = h3 - h2
 
 # HRSG effectiveness (energy-based)
 q_actual = min(q_in_steam, q_available * gas_mass_flow)  # Limit by available heat
 hrsg_effectiveness = q_actual / q_in_steam if q_in_steam > 0 else 0
 
 w_turb = h3 - h4
 
 return states, w_pump, w_turb, q_in_steam, q_available, hrsg_effectiveness

def plot_brayton_ts(states: list, eta_c: float, eta_t: float):
 """Generate T-s diagram for Brayton cycle"""
 fig, ax = plt.subplots(figsize=(10, 6))
 
 # Extract values
 T_vals = [s.T for s in states]
 s_vals = [s.s for s in states]
 
 # Plot cycle
 ax.plot(s_vals + [s_vals[0]], T_vals + [T_vals[0]], 'bo-', linewidth=2, markersize=8, label='Actual Cycle')
 
 # Add isobars
 s_range = np.linspace(min(s_vals)*0.95, max(s_vals)*1.05, 100)
 for p in [states[0].p, states[1].p]:
     T_iso = [air.T_s(s=ss, p=p)[0] for ss in s_range]
     ax.plot(s_range, T_iso, 'k--', alpha=0.3, linewidth=1)
     # Label
     mid_idx = len(s_range)//2
     ax.annotate(f'{p:.1f} bar', (s_range[mid_idx], T_iso[mid_idx]), 
                fontsize=8, alpha=0.5)
 
 # Annotations
 labels = ['1', '2', '3', '4']
 for i, (s, T, label) in enumerate(zip(s_vals, T_vals, labels)):
     ax.annotate(label, (s, T), textcoords="offset points", 
                xytext=(0,10), ha='center', fontweight='bold')
 
 ax.set_xlabel("Specific Entropy (s) [kJ/kg·K]", fontsize=12)
 ax.set_ylabel("Temperature (T) [K]", fontsize=12)
 ax.set_title(f"Brayton Cycle T-s Diagram\n(η_comp={eta_c:.0%}, η_turb={eta_t:.0%})", fontsize=14)
 ax.grid(True, alpha=0.3)
 ax.legend()
 
 return fig

def plot_rankine_hs(states: list, eta_t: float):
 """Generate h-s diagram for Rankine cycle with vapor dome"""
 fig, ax = plt.subplots(figsize=(10, 6))
 
 # Plot vapor dome
 p_crit = 220.64  # Critical pressure for water (bar)
 p_range = np.logspace(np.log10(0.05), np.log10(p_crit), 100)
 
 sf_vals, sg_vals = [], []
 hf_vals, hg_vals = [], []
 
 for p in p_range:
     try:
         sf = steam.s(p=p, x=0)[0]
         sg = steam.s(p=p, x=1)[0]
         hf = steam.h(p=p, x=0)[0]
         hg = steam.h(p=p, x=1)[0]
         sf_vals.append(sf)
         sg_vals.append(sg)
         hf_vals.append(hf)
         hg_vals.append(hg)
     except:
         continue
 
 ax.plot(sf_vals, hf_vals, 'k-', linewidth=2, label='Saturated Liquid')
 ax.plot(sg_vals, hg_vals, 'k-', linewidth=2, label='Saturated Vapor')
 ax.fill_betweenx(hf_vals + hg_vals[::-1], sf_vals + sg_vals[::-1], 
                  alpha=0.1, color='blue', label='Vapor Dome')
 
 # Plot cycle
 s_pts = [s.s for s in states] + [states[0].s]
 h_pts = [s.h for s in states] + [states[0].h]
 
 # Different line styles for different processes
 # 1-2: Pump (isentropic-ish)
 ax.plot([s_pts[0], s_pts[1]], [h_pts[0], h_pts[1]], 'g-', linewidth=3, label='Pump')
 # 2-3: Heat addition
 ax.plot([s_pts[1], s_pts[2]], [h_pts[1], h_pts[2]], 'r-', linewidth=3, label='Boiling/Superheat')
 # 3-4: Expansion
 ax.plot([s_pts[2], s_pts[3]], [h_pts[2], h_pts[3]], 'b-', linewidth=3, label='Turbine')
 # 4-1: Condensation
 ax.plot([s_pts[3], s_pts[0]], [h_pts[3], h_pts[0]], 'm-', linewidth=3, label='Condensation')
 
 # Points
 ax.scatter(s_pts[:-1], h_pts[:-1], c='red', s=100, zorder=5)
 labels = ['1', '2', '3', '4']
 for i, (s, h, label) in enumerate(zip(s_pts[:-1], h_pts[:-1], labels)):
     ax.annotate(label, (s, h), textcoords="offset points", 
                xytext=(10,0), ha='left', fontweight='bold', fontsize=12)
 
 ax.set_xlabel("Specific Entropy (s) [kJ/kg·K]", fontsize=12)
 ax.set_ylabel("Specific Enthalpy (h) [kJ/kg]", fontsize=12)
 ax.set_title(f"Rankine Cycle h-s Diagram (η_turb={eta_t:.0%})", fontsize=14)
 ax.legend(loc='upper left')
 ax.grid(True, alpha=0.3)
 
 return fig

def plot_composite_curves(gas_states: list, steam_states: list, 
                      m_gas: float, m_steam: float,
                      pinch_temp: float):
 """Plot T-H composite curves for HRSG analysis"""
 fig, ax = plt.subplots(figsize=(10, 6))
 
 # Gas side cooling curve
 h_gas = [s.h for s in gas_states]
 T_gas = [s.T for s in gas_states]
 
 # Cumulative heat for gas (cooling from state 4 to stack)
 Q_gas = [0]
 for i in range(len(h_gas)-1):
     Q_gas.append(Q_gas[-1] + m_gas * abs(h_gas[i+1] - h_gas[i]))
 
 # Normalize to actual heat transfer
 Q_max = Q_gas[-1]
 
 # Steam side heating curve
 h_steam = [s.h for s in steam_states]
 T_steam = [s.T for s in steam_states]
 
 Q_steam = [0]
 for i in range(len(h_steam)-1):
     Q_steam.append(Q_steam[-1] + m_steam * (h_steam[i+1] - h_steam[i]))
 
 # Normalize steam curve to match gas curve endpoint (energy balance)
 if Q_steam[-1] > 0:
     scale = Q_max / Q_steam[-1]
     Q_steam = [q * scale for q in Q_steam]
 
 # Plot curves
 ax.plot(Q_gas, T_gas, 'r-', linewidth=3, label='Gas Exhaust (Hot)', marker='o')
 ax.plot(Q_steam, T_steam, 'b-', linewidth=3, label='Steam/Water (Cold)', marker='s')
 
 # Pinch point line
 ax.axhline(y=pinch_temp, color='orange', linestyle='--', 
            label=f'Pinch Temperature ({pinch_temp:.0f} K)')
 
 # Fill between for heat transfer visualization
 ax.fill_between(Q_gas, T_gas, [pinch_temp]*len(Q_gas), 
                 alpha=0.1, color='red', label='Available Heat')
 
 ax.set_xlabel("Cumulative Heat Transfer Rate (Q̇) [kW]", fontsize=12)
 ax.set_ylabel("Temperature (T) [K]", fontsize=12)
 ax.set_title("HRSG Composite Curves (Pinch Analysis)", fontsize=14)
 ax.legend(loc='upper right')
 ax.grid(True, alpha=0.3)
 
 # Add temperature difference annotations
 for qg, tg, qs, ts in zip(Q_gas, T_gas, Q_steam, T_steam):
     if abs(qg - qs) < Q_max * 0.1:  # Near same heat duty
         diff = tg - ts
         if diff > 0:
             ax.annotate(f'ΔT={diff:.0f}K', ((qg+qs)/2, (tg+ts)/2),
                        fontsize=9, ha='center', 
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
 
 return fig

def calculate_exergy(states_brayton: list, states_rankine: list, 
                 t_ambient: float, p_ambient: float) -> dict:
 """Calculate exergy destruction and efficiency"""
 # Simplified exergy analysis
 # Flow exergy: (h - h0) - T0*(s - s0)
 
 h0_air = air.h(T=t_ambient, p=p_ambient)[0]
 s0_air = air.s(T=t_ambient, p=p_ambient)[0]
 
 exergies = {}
 
 # Gas turbine exergy destruction
 ex_in = (states_brayton[2].h - h0_air) - t_ambient * (states_brayton[2].s - s0_air)
 ex_out = (states_brayton[3].h - h0_air) - t_ambient * (states_brayton[3].s - s0_air)
 w_turb = states_brayton[2].h - states_brayton[3].h
 exergies['turbine'] = ex_in - ex_out - w_turb
 
 # Compressor
 ex_in_c = (states_brayton[0].h - h0_air) - t_ambient * (states_brayton[0].s - s0_air)
 ex_out_c = (states_brayton[1].h - h0_air) - t_ambient * (states_brayton[1].s - s0_air)
 w_comp = states_brayton[1].h - states_brayton[0].h
 exergies['compressor'] = ex_in_c - ex_out_c + w_comp  # Work input
 
 return exergies

# ==========================================
# STREAMLIT INTERFACE
# ==========================================

st.title("AD-HTC Fuel-Enhanced Combined Cycle Simulator")
st.markdown("""
### Advanced Thermodynamic Analysis
**Cycle Configuration:** Biogas-enhanced Brayton cycle with Heat Recovery Steam Generator (HRSG) 
powering a Rankine bottoming cycle.

**Key Improvements:**
- Complete Rankine cycle (including pump work)
- Pinch analysis for HRSG design
- Exergy destruction analysis
- Proper thermodynamic state validation
- Interactive composite curves
""")

# --- Sidebar Inputs ---
with st.sidebar:
 st.header("⚡ System Configuration")
 
 col1, col2 = st.columns(2)
 with col1:
     m_air = st.number_input("Air Flow (kg/s)", value=15.0, min_value=1.0)
 with col2:
     m_fuel = st.number_input("Biogas Flow (kg/s)", value=0.5, min_value=0.1, step=0.1)
 
 st.header("🔥 AD-HTC Feedstock")
 biogas_lhv = st.number_input("Biogas LHV (kJ/kg)", value=20000.0, min_value=10000.0)
 
 st.header("🌀 Brayton Cycle (Gas Turbine)")
 p1 = st.number_input("Inlet Pressure (bar)", value=1.013)
 t1 = st.number_input("Inlet Temperature (K)", value=288.15, min_value=250.0)
 rp = st.slider("Pressure Ratio", 5.0, 30.0, 12.0, 0.5)
 eta_c = st.slider("Compressor Isentropic Efficiency", 0.7, 0.95, 0.85, 0.01)
 eta_t_gas = st.slider("Turbine Isentropic Efficiency", 0.7, 0.95, 0.88, 0.01)
 
 st.header("💧 Rankine Cycle (Steam)")
 p_cond = st.number_input("Condenser Pressure (bar)", value=0.08, min_value=0.05, max_value=1.0, format="%.3f")
 p_boiler = st.number_input("HRSG Pressure (bar)", value=60.0, min_value=10.0, max_value=200.0)
 t_boiler = st.number_input("Steam Temperature (K)", value=773.15, min_value=500.0, max_value=900.0)
 eta_t_steam = st.slider("Steam Turbine Efficiency", 0.7, 0.95, 0.85, 0.01)
 eta_pump = st.slider("Pump Efficiency", 0.7, 0.95, 0.8, 0.01)
 
 st.header("🔄 Heat Recovery")
 pinch_approach = st.slider("Pinch Point ΔT (K)", 5.0, 50.0, 20.0, 1.0)
 t_ambient = st.number_input("Ambient Temperature (K)", value=298.15)

# --- Main Analysis ---
if st.button("🔍 RUN THERMODYNAMIC ANALYSIS", type="primary"):
 try:
     progress_bar = st.progress(0)
     status_text = st.empty()
     
     # Step 1: Brayton Cycle
     status_text.text("Calculating Brayton cycle...")
     brayton_states, w_comp_sp, w_turb_sp, q_in_brayton = calculate_brayton_cycle(
         p1, t1, rp, eta_c, eta_t_gas,
         m_air, m_fuel, biogas_lhv
     )
     progress_bar.progress(33)
     
     # Step 2: Rankine Cycle with HRSG
     status_text.text("Optimizing Rankine cycle and HRSG...")
     m_total = m_air + m_fuel
     rankine_states, w_pump_sp, w_turb_steam_sp, q_in_steam, q_avail, hrsg_eff = calculate_rankine_cycle(
         p_cond, p_boiler, t_boiler,
         eta_t_steam, eta_pump,
         brayton_states[3].T, brayton_states[3].h,
         m_total, pinch_approach
     )
     progress_bar.progress(66)
     
     # Step 3: System Integration
     status_text.text("Calculating system performance...")
     
     # Mass flow calculations
     # Steam mass flow determined by energy balance in HRSG
     # Q_available * m_gas = Q_required * m_steam
     if q_in_steam > 0 and q_avail > 0:
         m_steam = (q_avail * m_total * hrsg_eff) / q_in_steam
     else:
         m_steam = 0
     
     # Power calculations
     P_gas_turb = m_total * w_turb_sp
     P_gas_comp = m_total * w_comp_sp
     P_gas_net = P_gas_turb - P_gas_comp
     
     P_steam_turb = m_steam * w_turb_steam_sp if m_steam > 0 else 0
     P_pump = m_steam * w_pump_sp if m_steam > 0 else 0
     P_steam_net = P_steam_turb - P_pump
     
     P_total = P_gas_net + P_steam_net
     
     # Heat inputs
     Q_fuel = m_fuel * biogas_lhv
     Q_recovered = m_steam * q_in_steam if m_steam > 0 else 0
     
     # Efficiencies
     eta_brayton = P_gas_net / Q_fuel if Q_fuel > 0 else 0
     eta_rankine = P_steam_net / Q_recovered if Q_recovered > 0 else 0
     eta_combined = P_total / Q_fuel if Q_fuel > 0 else 0
     
     # Exergy analysis
     exergy_results = calculate_exergy(brayton_states, rankine_states, t_ambient, p1)
     
     progress_bar.progress(100)
     status_text.empty()
     progress_bar.empty()
     
     # ==========================================
     # RESULTS DISPLAY
     # ==========================================
     
     st.header("📊 System Performance Summary")
     
     # Top metrics
     col1, col2, col3, col4 = st.columns(4)
     col1.metric("Total Power Output", f"{P_total/1000:.2f}", "MW")
     col2.metric("Combined Efficiency", f"{eta_combined:.1%}", 
                f"{eta_combined*100:.1f}%")
     col3.metric("Brayton Efficiency", f"{eta_brayton:.1%}")
     col4.metric("Rankine Efficiency", f"{eta_rankine:.1%}")
     
     # Detailed breakdown
     st.subheader("Power Balance")
     col1, col2 = st.columns(2)
     
     with col1:
         st.markdown("**Gas Turbine Cycle**")
         st.write(f"• Turbine Power: {P_gas_turb/1000:.2f} MW")
         st.write(f"• Compressor Power: {P_gas_comp/1000:.2f} MW")
         st.write(f"• Net Power: **{P_gas_net/1000:.2f} MW**")
         st.write(f"• Heat Input: {Q_fuel/1000:.2f} MW")
         st.write(f"• Exhaust Temperature: {brayton_states[3].T:.1f} K")
     
     with col2:
         st.markdown("**Steam Bottoming Cycle**")
         st.write(f"• Steam Mass Flow: {m_steam:.2f} kg/s")
         st.write(f"• Turbine Power: {P_steam_turb/1000:.2f} MW")
         st.write(f"• Pump Power: {P_pump/1000:.2f} MW")
         st.write(f"• Net Power: **{P_steam_net/1000:.2f} MW**")
         st.write(f"• HRSG Effectiveness: {hrsg_eff:.1%}")
     
     # State tables
     st.subheader("Thermodynamic States")
     col1, col2 = st.columns(2)
     
     with col1:
         st.markdown("**Brayton Cycle States**")
         brayton_data = {
             'Point': [s.point_name for s in brayton_states],
             'P (bar)': [f"{s.p:.2f}" for s in brayton_states],
             'T (K)': [f"{s.T:.1f}" for s in brayton_states],
             'h (kJ/kg)': [f"{s.h:.1f}" for s in brayton_states],
             's (kJ/kg·K)': [f"{s.s:.3f}" for s in brayton_states]
         }
         st.dataframe(brayton_data, use_container_width=True)
     
     with col2:
         st.markdown("**Rankine Cycle States**")
         rankine_data = {
             'Point': [s.point_name for s in rankine_states],
             'P (bar)': [f"{s.p:.2f}" for s in rankine_states],
             'T (K)': [f"{s.T:.1f}" for s in rankine_states],
             'h (kJ/kg)': [f"{s.h:.1f}" for s in rankine_states],
             's (kJ/kg·K)': [f"{s.s:.3f}" for s in rankine_states],
             'Quality': [f"{s.x:.3f}" if s.x is not None else "Superheated" for s in rankine_states]
         }
         st.dataframe(rankine_data, use_container_width=True)
     
     # Thermodynamic diagrams
     st.subheader("Thermodynamic Diagrams")
     col1, col2 = st.columns(2)
     
     with col1:
         fig_brayton = plot_brayton_ts(brayton_states, eta_c, eta_t_gas)
         st.pyplot(fig_brayton)
     
     with col2:
         fig_rankine = plot_rankine_hs(rankine_states, eta_t_steam)
         st.pyplot(fig_rankine)
     
     # HRSG Composite curves
     st.subheader("Heat Recovery Analysis")
     pinch_temp = rankine_states[1].T + pinch_approach
     fig_composite = plot_composite_curves(
         brayton_states, rankine_states, 
         m_total, m_steam, pinch_temp
     )
     st.pyplot(fig_c)
