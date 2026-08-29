"""
Aviation Flight Computer (CRP-5 & ASA CX-3) Digital Emulator
Author: Pascal Ambogo Mudimba (@scalstein)
Flight Operations Engineering & Navigation Physics Systems Suite
"""

import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="CRP-5 & ASA CX-3 Flight Computer Emulator | Flight Ops",
    layout="wide",
    page_icon="🧮",
)

# ---------------------------------------------------------
# 1. NAVIGATION TRIANGLE & WIND VECTOR MATHEMATICS
# ---------------------------------------------------------


def solve_crp5_wind_triangle(
    true_course_deg: float,
    tas_kts: float,
    wind_dir_deg: float,
    wind_spd_kts: float,
) -> dict:
  """Simulates the CRP-5 mechanical wind face / CX-3 digital vector triangle.

  Calculates Wind Correction Angle (WCA), True Heading (TH), and Ground Speed
  (GS).
  """
  tc_rad = math.radians(true_course_deg)
  wd_rad = math.radians(wind_dir_deg)

  alpha = wd_rad - tc_rad
  crosswind = wind_spd_kts * math.sin(alpha)
  headwind = wind_spd_kts * math.cos(alpha)

  sin_wca = crosswind / max(1.0, tas_kts)
  sin_wca = max(-1.0, min(1.0, sin_wca))
  wca_rad = math.asin(sin_wca)
  wca_deg = math.degrees(wca_rad)

  true_heading = (true_course_deg + wca_deg + 360.0) % 360.0
  ground_speed = (tas_kts * math.cos(wca_rad)) - headwind
  ground_speed = max(0.0, ground_speed)

  return {
      "true_course_deg": round(true_course_deg, 1),
      "true_heading_deg": round(true_heading, 1),
      "wca_deg": round(wca_deg, 1),
      "ground_speed_kts": round(ground_speed, 1),
      "headwind_kts": round(headwind, 1),
      "crosswind_kts": round(abs(crosswind), 1),
      "is_tailwind": headwind < 0,
  }


# ---------------------------------------------------------
# 2. TOP-OF-DESCENT & POINT-OF-SAFE-RETURN (PSR / CP)
# ---------------------------------------------------------


def solve_top_of_descent(
    cruise_fl: int,
    target_alt_ft: int,
    ground_speed_kts: float,
    descent_rate_fpm: float = 1800.0,
    descent_angle_deg: float = 3.0,
) -> dict:
  """Calculates Top-of-Descent (TOD) profile using rule-of-thumb and 3-degree trigonometric methods."""
  delta_alt_ft = max(0, (cruise_fl * 100) - target_alt_ft)

  tod_dist_rule_nm = (delta_alt_ft / 1000.0) * 3.0

  gamma_rad = math.radians(descent_angle_deg)
  tod_dist_exact_nm = delta_alt_ft / (math.tan(gamma_rad) * 6076.115)

  time_min = delta_alt_ft / max(100.0, descent_rate_fpm)
  required_rod_fpm = (
      ground_speed_kts * (6076.115 / 60.0) * math.tan(gamma_rad)
  )

  return {
      "altitude_loss_ft": delta_alt_ft,
      "tod_distance_exact_nm": round(tod_dist_exact_nm, 1),
      "tod_distance_rule_nm": round(tod_dist_rule_nm, 1),
      "descent_time_min": round(time_min, 1),
      "required_rod_fpm": round(required_rod_fpm, 0),
  }


def solve_point_of_safe_return(
    safe_endurance_hr: float,
    tas_kts: float,
    wind_comp_kts: float,
    total_dist_nm: float,
) -> dict:
  """Solves Point of Safe Return (PSR) / Radius of Action (ROA) before fuel limits require 180° turnback.

  Formula: T_out = (Endurance * GS_home) / (GS_out + GS_home)
  """
  gs_out = tas_kts + wind_comp_kts
  gs_home = tas_kts - wind_comp_kts

  time_out_hr = (safe_endurance_hr * gs_home) / max(1.0, (gs_out + gs_home))
  time_home_hr = safe_endurance_hr - time_out_hr
  psr_dist_nm = time_out_hr * gs_out

  etp_dist_nm = (total_dist_nm * gs_home) / max(1.0, (gs_out + gs_home))
  etp_time_min = (etp_dist_nm / max(1.0, gs_out)) * 60.0

  return {
      "gs_out_kts": round(gs_out, 1),
      "gs_home_kts": round(gs_home, 1),
      "psr_time_out_min": round(time_out_hr * 60.0, 1),
      "psr_time_home_min": round(time_home_hr * 60.0, 1),
      "psr_distance_nm": round(psr_dist_nm, 1),
      "etp_distance_nm": round(etp_dist_nm, 1),
      "etp_time_min": round(etp_time_min, 1),
  }


# ---------------------------------------------------------
# 3. CONVERSIONS & FUEL BURN SLIDE-RULE
# ---------------------------------------------------------


def execute_slide_rule_conversions(value: float, conversion_type: str) -> dict:
  conversions = {
      "NM to Kilometers (km)": value * 1.852,
      "Kilometers to NM": value / 1.852,
      "Feet (ft) to Meters (m)": value * 0.3048,
      "Meters to Feet (ft)": value / 0.3048,
      "Gallons (US) to Litres (L)": value * 3.78541,
      "Litres to Gallons (US)": value / 3.78541,
      "Jet-A1 Litres to Kilograms (SG 0.80)": value * 0.80,
      "Kilograms to Pounds (lbs)": value * 2.20462,
      "Pounds (lbs) to Kilograms": value / 2.20462,
  }
  res = conversions.get(conversion_type, 0.0)
  return {"converted_value": round(res, 2)}


# ---------------------------------------------------------
# 4. STREAMLIT USER INTERFACE
# ---------------------------------------------------------

st.title("🧮 CRP-5 & ASA CX-3 Flight Computer Digital Emulator")
st.caption(
    "Flight Operations Engineering & Navigation Vector Suite | Circular Slide"
    " Rule, Wind Triangle, TOD & Critical Fuel Solver"
)

t1, t2, t3, t4 = st.tabs([
    "🧭 Wind Triangle & Heading Solver",
    "⛰️ Top of Descent (TOD) Engine",
    "⏱️ Point of Safe Return (PSR / CP)",
    "📐 Aviation Slide-Rule Conversions",
])

with t1:
  st.subheader("CRP-5 Mechanical Wind Face / CX-3 Vector Calculation")

  c1, c2 = st.columns(2)
  with c1:
    tc = st.slider("Planned True Course (°T)", 0, 360, 60, step=1)
    tas = st.slider("True Airspeed (TAS kts)", 100, 520, 420, step=5)
  with c2:
    wdir = st.slider("Wind Direction (°T)", 0, 360, 110, step=5)
    wspd = st.slider("Wind Speed (kts)", 0, 120, 35, step=1)

  w_res = solve_crp5_wind_triangle(tc, tas, wdir, wspd)

  k1, k2, k3, k4 = st.columns(4)
  with k1:
    st.metric(
        "True Heading (TH)",
        f"{w_res['true_heading_deg']:.1f}°",
        delta=f"WCA: {w_res['wca_deg']:+.1f}°",
    )
  with k2:
    st.metric(
        "Ground Speed (GS)",
        f"{w_res['ground_speed_kts']} kts",
        delta=f"TAS: {tas} kts",
    )
  with k3:
    st.metric(
        "Headwind / Tailwind",
        f"{abs(w_res['headwind_kts'])} kts"
        f" {'TW' if w_res['is_tailwind'] else 'HW'}",
    )
  with k4:
    st.metric("Crosswind Component", f"{w_res['crosswind_kts']} kts")

  fig_polar = go.Figure()
  fig_polar.add_trace(
      go.Scatterpolar(
          r=[0, w_res["ground_speed_kts"]],
          theta=[0, tc],
          mode="lines+markers+text",
          text=["", f"GS {w_res['ground_speed_kts']} kts"],
          line=dict(color="#1E3A8A", width=3),
          name=f"Track / Ground Speed ({tc}°)",
      )
  )
  fig_polar.add_trace(
      go.Scatterpolar(
          r=[0, tas],
          theta=[0, w_res["true_heading_deg"]],
          mode="lines+markers+text",
          text=["", f"TH {w_res['true_heading_deg']}°"],
          line=dict(color="#10B981", width=2.5, dash="dash"),
          name=f"Heading Vector ({w_res['true_heading_deg']}°)",
      )
  )
  fig_polar.update_layout(
      polar=dict(angularaxis=dict(direction="clockwise", rotation=90)),
      height=380,
      margin=dict(l=20, r=20, t=30, b=20),
  )
  st.plotly_chart(fig_polar, use_container_width=True)

with t2:
  st.subheader("Top of Descent (TOD) Profile & 3° Descent Geometry")

  col_td1, col_td2 = st.columns(2)
  with col_td1:
    cruise_fl = st.slider("Cruise Flight Level (FL)", 150, 430, 370, step=10)
    target_alt = st.slider(
        "Target Arrival Altitude (ft MSL)", 0, 10000, 5330, step=100
    )
  with col_td2:
    descent_gs = st.slider("Descent Ground Speed (kts)", 180, 480, 360, step=10)
    descent_angle = st.slider("Descent Path Angle (°)", 2.5, 4.0, 3.0, step=0.1)

  tod_res = solve_top_of_descent(
      cruise_fl, target_alt, descent_gs, descent_angle_deg=descent_angle
  )

  c_m1, c_m2, c_m3 = st.columns(3)
  with c_m1:
    st.metric(
        "Required TOD Distance",
        f"{tod_res['tod_distance_exact_nm']} NM",
        delta=f"Rule of 3: {tod_res['tod_distance_rule_nm']} NM",
    )
  with c_m2:
    st.metric(
        "Descent Time to Target", f"{tod_res['descent_time_min']:.1f} min"
    )
  with c_m3:
    st.metric(
        f"Target Rate of Descent ({descent_angle}°)",
        f"{tod_res['required_rod_fpm']:,.0f} fpm",
    )

  fig_tod = go.Figure()
  fig_tod.add_trace(
      go.Scatter(
          x=[tod_res["tod_distance_exact_nm"], 0],
          y=[cruise_fl * 100, target_alt],
          mode="lines+markers+text",
          text=["TOD Fix", f"Level-Off ({target_alt} ft)"],
          textposition="top right",
          line=dict(color="#1E3A8A", width=3),
          name="3° Glide Profile",
      )
  )
  fig_tod.update_layout(
      title="Top of Descent Trajectory (NM vs Altitude)",
      xaxis_title="Distance from Waypoint / Airport (NM)",
      yaxis_title="Altitude (ft MSL)",
      height=320,
      margin=dict(l=0, r=0, t=30, b=0),
  )
  st.plotly_chart(fig_tod, use_container_width=True)

with t3:
  st.subheader(
      "Point of Safe Return (PSR) & Critical Point (CP / ETP) Solver"
  )

  col_p1, col_p2 = st.columns(2)
  with col_p1:
    safe_endurance = st.slider(
        "Safe Usable Fuel Endurance (Hours)", 1.5, 8.0, 4.5, step=0.1
    )
    route_dist = st.slider("Total Route Distance (NM)", 200, 3500, 1200, step=50)
  with col_p2:
    psr_tas = st.slider("True Airspeed (TAS kts) ", 150, 500, 430, step=10)
    psr_wind = st.slider(
        "En-Route Wind Component (kts) [Negative = HW]",
        -60,
        60,
        -20,
        step=5,
    )

  psr_res = solve_point_of_safe_return(
      safe_endurance, psr_tas, psr_wind, route_dist
  )

  kp1, kp2, kp3, kp4 = st.columns(4)
  with kp1:
    st.metric(
        "Point of Safe Return (PSR)",
        f"{psr_res['psr_distance_nm']} NM",
        delta=f"{psr_res['psr_time_out_min']} min out",
    )
  with kp2:
    st.metric(
        "Return Flight Time",
        f"{psr_res['psr_time_home_min']} min",
        delta=f"GS Home: {psr_res['gs_home_kts']} kts",
    )
  with kp3:
    st.metric(
        "Critical Point (ETP)",
        f"{psr_res['etp_distance_nm']} NM",
        delta=f"{psr_res['etp_time_min']:.1f} min out",
    )
  with kp4:
    st.metric("Outbound Ground Speed", f"{psr_res['gs_out_kts']} kts")

with t4:
  st.subheader("CRP-5 Circular Slide-Rule Engineering Unit Conversions")

  col_u1, col_u2 = st.columns(2)
  conv_list = [
      "NM to Kilometers (km)",
      "Kilometers to NM",
      "Feet (ft) to Meters (m)",
      "Meters to Feet (ft)",
      "Gallons (US) to Litres (L)",
      "Litres to Gallons (US)",
      "Jet-A1 Litres to Kilograms (SG 0.80)",
      "Kilograms to Pounds (lbs)",
      "Pounds (lbs) to Kilograms",
  ]
  with col_u1:
    sel_conv = st.selectbox("Select Conversion Metric", conv_list)
    val_input = st.number_input("Input Quantity", value=1000.0, step=10.0)
  with col_u2:
    converted = execute_slide_rule_conversions(val_input, sel_conv)
    st.metric("Converted Engineering Value", f"{converted['converted_value']:,}")
    st.caption(
        "Calibrated against standard ICAO Annex 5 and CRP-5 slide-rule circular"
        " ratios."
    )
