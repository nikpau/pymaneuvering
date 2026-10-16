# MMG Dynamics and Abkowitz Model for Ship Maneuvering (v2.0)

This package implementation provides standard models for ship maneuvering:
1.  **MMG Standard Model**: Based on Yasukawa & Yoshimura (2015), suitable for ocean-going vessels with extensions for wind, current, and shallow water.
2.  **Abkowitz-Type Model**: Based on Yang & el Moctar (2024), tailored for inland barges operating in shallow water.

## ⚠️ API Change in Version 2.0
**Important:** Version 2.0 introduces a breaking API change. The package now supports multiple dynamics models. You must instantiate a specific model (MMG or Abkowitz) before calling simulation steps. The old top-level `pstep()` function has been moved to methods within these model classes.

## Installation

Install the package via pip:

```bash
pip install git+https://github.com/nikpau/pymaneuvering
```

## Quick Start

The easiest way to get started is by using the `Vessel` dispatcher with a pre-calibrated vessel type from `VTYPE`.

### 1. MMG Model (Ocean-going)

The MMG model requires propeller revolutions (`nps`) as a control input alongside the rudder angle (`delta`). It supports wind and current disturbances.

```python
import math
from pymaneuvering import Vessel, VTYPE

# 1. Initialize an MMG model (e.g., KVLCC2 Tanker)
vessel_type = VTYPE.KVLCC2_L64 # or KVLCC2_FULL
vessel = Vessel(new_from=vessel_type)

# 2. Set initial state
pos = [0.0, 0.0]        # North, East [m]
psi = 0.0               # Heading [rad]
uvr = [3.85, 0.0, 0.0]  # Surge, Sway, Yaw Rate [m/s, m/s, rad/s]

# 3. Simulate one step (pstep returns updated state)
new_uvr, new_eta = vessel.pstep(
    X=uvr,
    pos=pos,
    dT=1.0,                 # Time step [s]
    nps=4.0,                # Propeller revs [1/s] (REQUIRED for MMG)
    delta=10 * (math.pi/180), # Rudder angle [rad]
    psi=psi,
    water_depth=None,       # Optional: shallow water correction
    w_vel=10.0,             # Optional: Wind speed [m/s]
    beta_w=math.pi,         # Optional: Wind direction [rad]
    fl_vel=None, fl_psi=None # Optional: Current
)

print(f"New Position: {new_eta[0:2]}")
```

### 2. Abkowitz Model (Inland/Shallow Water)

The Abkowitz model for inland barges is designed for shallow water operations. It **does not** use `nps` (propeller RPM). Instead, the vessel's surge velocity (`u`) is the primary longitudinal state. Shallow water effects are integral to this model, so `water_depth` is a **required** parameter.

> **Note on speed behavior (`U_0`)**  
> The Abkowitz formulation is calibrated around a **reference speed** `U_0` (see vessel coefficients). Internally, surge-related terms are evaluated using the deviation `du = u - U_0`, so the model is typically most reliable when the simulated surge speed `u` stays reasonably close to `U_0`.  
> Unlike the MMG model, there is no explicit propulsion control input (`nps`) to command detailed acceleration/deceleration transients directly. As a result, precise speed-up/slow-down maneuvers (as modeled in MMG) are not directly represented in the same way.

```python
import math
from pymaneuvering import Vessel, VTYPE

# 1. Initialize an Abkowitz model (e.g., GMS-like Inland Barge)
vessel_type = VTYPE.GMS_LIKE
vessel = Vessel(new_from=vessel_type)

# 2. Set initial state
pos = [0.0, 0.0]
psi = 0.0
uvr = [2.5, 0.0, 0.0]  # Surge velocity drives the vessel

# 3. Simulate one step
new_uvr, new_eta = vessel.pstep(
    X=uvr,
    pos=pos,
    dT=1.0,
    delta=20 * (math.pi/180), # Rudder angle [rad]
    psi=psi,
    water_depth=3.5,        # Water depth [m] (REQUIRED for Abkowitz)
    # nps is NOT used here
    # w_vel (Wind) is NOT supported here
    fl_vel=0.5,             # Optional: Current speed [m/s]
    fl_psi=math.pi/2        # Optional: Current direction [rad]
)
```

## Comparisons & Capabilities

| Feature | MMG Model | Abkowitz Model |
| :--- | :--- | :--- |
| **Primary Use Case** | Ocean-going vessels (e.g., Tankers) | Inland vessels / Barges |
| **Reference** | Yasukawa & Yoshimura (2015) | Yang & el Moctar (2024) |
| **Propulsion Input** | **Required (`nps`)**. Propeller RPM drives surge. | **Implicit**. Surge velocity (`u`) is the main longitudinal state. |
| **Shallow Water** | Optional correction. | **Required** core component. |
| **Wind** | ✅ Supported (`w_vel`, `beta_w`) | ❌ Not supported |
| **Current** | ✅ Supported (`fl_vel`, `fl_psi`) | ✅ Supported (`fl_vel`, `fl_psi`) |

## Advanced Usage

### Dynamics (`step` vs `pstep`)

*   **`pstep(...)`**: **(Recommended)** "Position Step". inputs current state, position, and controls. Returns **updated state** (new `uvr`) and **updated position** (new `eta`). Handles coordinate transformation (vessel -> earth fixed) internally.
*   **`step(...)`**: "Dynamics Step". inputs current state and controls. Returns **accelerations/derivatives** (`u_dot`, `v_dot`, `r_dot`). Useful if you want to implement your own integration scheme (e.g., Runge-Kutta).

### Custom Calibration

You can calibrate custom MMG vessels using the `mmgdynamics.mmg.dynamics.calibrate` function with a `MinimalVessel` dictionary. See `src/mmg/dynamics.py` for details. Abkowitz models currently rely on pre-defined coefficient sets (like `gms_like_inland_barge`).

## References

*   **MMG:** Yasukawa, H., Yoshimura, Y. (2015). Introduction of MMG standard method for ship maneuvering predictions. *J Mar Sci Technol 20*, 37-52. [DOI](https://doi.org/10.1007/s00773-014-0293-y)
*   **Abkowitz:** Yang, Y., el Moctar, O. (2024). Maneuvering simulation of inland vessels in shallow water. *Ocean Engineering*. [DOI](https://doi.org/10.1016/j.oceaneng.2024.116927)

## License

pymaneuvering is released under the [MIT License](LICENSE). The license covers the source code and the bundled vessel parameter sets, and applies to all versions of the project, including releases published before the LICENSE file was added (e.g. 2.0.0).

Copyright (c) 2022-2026 Niklas Paulig.

Parameter sets derived from published studies should additionally be cited according to the references above.
