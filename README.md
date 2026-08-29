# Aviation Flight Computer (CRP-5 and ASA CX-3) Digital Emulator

An end-to-end Flight Operations Engineering and navigation calculation platform designed to emulate the mechanical CRP-5 circular slide rule and digital ASA CX-3 flight computer. The platform solves the navigation wind triangle, computes 3° Top-of-Descent (TOD) glide trajectories, calculates Point of Safe Return (PSR) and Critical Points (ETP/CP), and provides aviation unit conversions.

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://scalstein-crp5-cx3-flight-computer.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Operational Context and Problem Statement
In professional flight dispatch, navigation planning, and ATPL flight operations engineering, flight computers like the **Pooley's CRP-5** and **ASA CX-3** are standard operational instruments.

This digital emulator implements their mathematical capabilities:
* **Vector Wind Triangle:** Resolving drift angle (Wind Correction Angle), True Heading ($TH$), and Ground Speed ($GS$) given True Course ($TC$), True Airspeed ($TAS$), and winds aloft vectors.
* **Top of Descent (TOD):** Calculating precise nautical mile distances and required rate of descent ($\text{fpm}$) to transition from cruise flight levels to terminal approach fixes using 3° trigonometric and 3:1 rule-of-thumb formulations.
* **Point of Safe Return (PSR / Radius of Action):** Determining the maximum outbound distance and time before fuel reserves require a 180° turnback to the departure airport.
* **Critical Point (ETP / CP):** Locating the Equal Time Point between two aerodromes accounting for headwind and tailwind asymmetry.
* **Circular Slide-Rule Conversions:** Fuel weight-volume conversions (Specific Gravity 0.80 for Jet-A1), nautical miles to kilometers, and feet to meters.

---

## 2. Mathematical Formulation and Navigation Trigonometry

### A. Navigation Wind Triangle & Heading Solver
$$\sin(\text{WCA}) = \frac{V_{\text{wind}}}{TAS} \cdot \sin(\theta_{\text{wind}} - \theta_{\text{TC}})$$

$$\text{True Heading } (TH) = \theta_{\text{TC}} + \text{WCA}$$

$$\text{Ground Speed } (GS) = TAS \cdot \cos(\text{WCA}) - V_{\text{wind}} \cdot \cos(\theta_{\text{wind}} - \theta_{\text{TC}})$$

### B. Top of Descent (TOD) Profile
$$\Delta H_{\text{descent}} = (\text{FL}_{\text{cruise}} \cdot 100) - H_{\text{target}}$$

$$D_{\text{TOD}} = \frac{\Delta H_{\text{descent}}}{\tan(3^\circ) \cdot 6076.115\text{ ft/NM}}$$

$$\text{Required Rate of Descent (ROD)} = GS \cdot \left(\frac{6076.115}{60}\right) \cdot \tan(3^\circ) \approx GS \cdot 5.3$$

### C. Point of Safe Return (PSR) & Critical Point (CP)
$$T_{\text{out, PSR}} = \frac{E_{\text{safe}} \cdot GS_{\text{home}}}{GS_{\text{out}} + GS_{\text{home}}}$$

$$D_{\text{PSR}} = T_{\text{out, PSR}} \cdot GS_{\text{out}}$$

$$D_{\text{ETP}} = \frac{D_{\text{total}} \cdot GS_{\text{home}}}{GS_{\text{out}} + GS_{\text{home}}}$$

---

## 3. Repository Architecture

```text
crp5-asa-cx3-flight-computer-emulator/
├── app.py                     # Self-contained Streamlit application & vector solver
├── requirements.txt           # Production dependencies
├── .gitignore
├── README.md
└── tests/
    └── test_crp5.py           # Automated pytest verification test suite
