"""
API showcase of the pymaneuvering library, demonstrating the
simulation of vessel trajectories one for an inland vessel and
one for an ocean vessel.

The trajectories are plotted with rotated transparent ship
footprints to visualize the vessel's orientation and size along the path.

The inland vessel uses the GMS-like model, while the ocean
vessel uses the KVLCC2 L64 model.

Both vessels are subjected to a constant rudder angle of 10° for
800 seconds, and their trajectories are compared in a single plot.

Usage instructions:
1. Ensure you have pymaneuvering installed in your Python environment.
2. Run this script to generate the plot of the vessel trajectories.
3. The plot will be saved as "vessel_trajectories.png" in the current working directory.
"""

import math
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import transforms
from pymaneuvering import Vessel, VTYPE, IntegrationMode


# Load a pre-calibrated vessel
vessel_inland = Vessel(new_from=VTYPE.GMS_LIKE)
vessel_ocean = Vessel(new_from=VTYPE.KVLCC2_L64)

# Let the vessel drive with a rudder angle
# of 10° for 1000 seconds
# -------------------------------------
# Inital position
pos_inland = [0, 0]  # x,y [m]
pos_ocean = [0, 0]  # x,y [m]

# Initial heading
psi_i = 0  # [rad]
psi_o = 0  # [rad]

# Unpack initial values
uvr_i = np.array([2.777, 0, 0.0])  # u,v,r [m/s, m/s, rad/s]
uvr_o = np.array([2.777, 0, 0.0])  # u,v,r [m/s, m/s, rad/s]

positions_i = []
positions_o = []

for _ in range(800):
    # Simulate inland vessel
    uvr_i, eta_i = vessel_inland.pstep(
        X=uvr_i,
        pos=pos_inland,
        dT=1,  # 1 second time step
        delta=10 * (math.pi / 180),  # Convert to radians
        psi=psi_i,  # Heading
        water_depth=15,  # 15 m water depth
        fl_psi=0,  # 0° current angle
        fl_vel=None,  # No current velocity
        mode=IntegrationMode.TRAPEZOIDAL,
    )
    x_i, y_i, psi_i = eta_i  # Unpack new position and heading
    positions_i.append([x_i, y_i, psi_i])  # Store the new position and heading
    pos_inland = [x_i, y_i]  # Update the position

    # Simulate ocean vessel
    uvr_o, eta_o = vessel_ocean.pstep(
        X=uvr_o,
        pos=pos_ocean,
        dT=1,  # 1 second time step
        delta=10 * (math.pi / 180),  # Convert to radians
        psi=psi_o,  # Heading
        nps=5,
        water_depth=15,  # 15 m water depth
        fl_psi=0,  # 0° current angle
        fl_vel=None,  # No current velocity
        w_vel=None,  # No wind velocity
        beta_w=None,  # No wind angle
    )
    x_o, y_o, psi_o = eta_o  # Unpack new position and heading
    positions_o.append([x_o, y_o, psi_o])  # Store the new position and heading
    pos_ocean = [x_o, y_o]  # Update the position

# --------------------------------------------------------
# Plot the trajectories with ship footprints
# --------------------------------------------------------
ps = list(zip(*positions_i))
plt.rcParams.update(
    {
        "figure.dpi": 150,
        "axes.facecolor": "white",
        "axes.edgecolor": "black",
        "axes.linewidth": 1.0,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
    }
)

inland_color = "#1f77b4"
ocean_color = "#d62728"

fig, ax = plt.subplots(figsize=(12, 8))
ax.plot(ps[0], ps[1], color=inland_color, linewidth=2.2, label="Inland trajectory")

# Quick plot of the trajectory for ocean vessel
ps_o = list(zip(*positions_o))
ax.plot(ps_o[0], ps_o[1], color=ocean_color, linewidth=2.2, label="Ocean trajectory")

# Plot ship footprint every n steps
n = 40
x_sub = ps[0][::n]
y_sub = ps[1][::n]
psi_sub = ps[2][::n]
ship_length_i = VTYPE.GMS_LIKE.value["L"]
ship_beam_i = VTYPE.GMS_LIKE.value["B"]

for idx, (x, y, psi) in enumerate(zip(x_sub, y_sub, psi_sub)):
    ship = Rectangle(
        (-ship_length_i / 2, -ship_beam_i / 2),
        ship_length_i,
        ship_beam_i,
        facecolor=inland_color,
        edgecolor="black",
        alpha=0.24,
        linewidth=0.9,
        label="Inland ship footprint" if idx == 0 else None,
    )
    tr = transforms.Affine2D().rotate_around(0, 0, -psi).translate(x, y) + ax.transData
    ship.set_transform(tr)
    ax.add_patch(ship)

x_sub_o = ps_o[0][::n]
y_sub_o = ps_o[1][::n]
psi_sub_o = ps_o[2][::n]
ship_length_o = VTYPE.KVLCC2_L64.value["Lpp"]
ship_beam_o = VTYPE.KVLCC2_L64.value["B"]

for idx, (x, y, psi) in enumerate(zip(x_sub_o, y_sub_o, psi_sub_o)):
    ship = Rectangle(
        (-ship_length_o / 2, -ship_beam_o / 2),
        ship_length_o,
        ship_beam_o,
        facecolor=ocean_color,
        edgecolor="black",
        alpha=0.18,
        linewidth=0.9,
        label="Ocean ship footprint" if idx == 0 else None,
    )
    tr = transforms.Affine2D().rotate_around(0, 0, psi).translate(x, y) + ax.transData
    ship.set_transform(tr)
    ax.add_patch(ship)

# Start and end markers
ax.scatter(
    ps[0][0],
    ps[1][0],
    color=inland_color,
    edgecolors="black",
    marker="o",
    s=52,
    linewidths=0.6,
    label="Inland start",
)
ax.scatter(
    ps[0][-1],
    ps[1][-1],
    color=inland_color,
    edgecolors="black",
    marker="X",
    s=64,
    linewidths=0.7,
    label="Inland end",
)
ax.scatter(
    ps_o[0][0],
    ps_o[1][0],
    color=ocean_color,
    edgecolors="black",
    marker="o",
    s=52,
    linewidths=0.6,
    label="Ocean start",
)
ax.scatter(
    ps_o[0][-1],
    ps_o[1][-1],
    color=ocean_color,
    edgecolors="black",
    marker="X",
    s=64,
    linewidths=0.7,
    label="Ocean end",
)

ax.axis("equal")
ax.set_title("Vessel trajectories with rotated transparent ship footprints")
ax.set_ylabel("East [m]")
ax.set_xlabel("North [m]")
ax.grid(True, linestyle="-", linewidth=0.6, color="#b0b0b0", alpha=0.55)
ax.minorticks_on()
ax.grid(which="minor", linestyle="-", linewidth=0.3, color="#d0d0d0", alpha=0.45)
ax.legend(
    loc="best",
    frameon=True,
    facecolor="white",
    edgecolor="black",
    framealpha=0.96,
    ncol=2,
)
fig.tight_layout()
plt.savefig("vessel_trajectories.png", dpi=300)
